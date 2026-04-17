#!/usr/bin/env python3
"""Initialize a problem workspace from an AtCoder or Codeforces URL.

Usage:
    ./scripts/init_problem.py <url> [flags]

Idempotent: re-running on an existing problem directory never overwrites user
files (main.cpp, notes.md, attempts/, review/). Missing pieces are filled in.
See `plan-problem-intake.md` for the full policy.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Optional

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates"
PROBLEMS = REPO_ROOT / "problems"
SESSIONS = REPO_ROOT / "sessions"
SCRIPTS = REPO_ROOT / "scripts"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)


# ---------------------------------------------------------------------------
# URL parsing
# ---------------------------------------------------------------------------


@dataclass
class ParsedURL:
    platform: str
    contest_id: str
    problem_id: str
    index: Optional[str]
    slug: str
    canonical_url: str


def parse_url(url: str) -> ParsedURL:
    url = url.strip()
    m = re.match(r"https?://atcoder\.jp/contests/([^/]+)/tasks/([^/?#]+)", url)
    if m:
        contest, task = m.group(1), m.group(2)
        return ParsedURL(
            platform="atc",
            contest_id=contest,
            problem_id=task,
            index=None,
            slug=f"atc-{task}",
            canonical_url=f"https://atcoder.jp/contests/{contest}/tasks/{task}",
        )

    m = re.match(r"https?://codeforces\.com/contest/(\d+)/problem/([A-Za-z0-9]+)", url)
    if not m:
        m = re.match(r"https?://codeforces\.com/problemset/problem/(\d+)/([A-Za-z0-9]+)", url)
    if m:
        cid, idx = m.group(1), m.group(2).upper()
        return ParsedURL(
            platform="cf",
            contest_id=cid,
            problem_id=f"{cid}_{idx.lower()}",
            index=idx,
            slug=f"cf-{cid}_{idx.lower()}",
            canonical_url=f"https://codeforces.com/problemset/problem/{cid}/{idx}",
        )

    raise ValueError(
        "Unsupported URL. Expected AtCoder "
        "(https://atcoder.jp/contests/<c>/tasks/<task>) or Codeforces "
        "(https://codeforces.com/contest/<n>/problem/<i>)."
    )


# ---------------------------------------------------------------------------
# HTML fetch + sample/limit extraction
# ---------------------------------------------------------------------------


@dataclass
class ProblemData:
    name: Optional[str] = None
    time_limit_ms: Optional[int] = None
    memory_limit_mb: Optional[int] = None
    tests: list[tuple[str, str]] = field(default_factory=list)


def fetch_html(url: str, timeout: float = 20.0) -> str:
    """Fetch a URL. Uses urllib first; if it returns 403 (Codeforces bot
    protection is sensitive to urllib's TCP/TLS fingerprint), falls back to
    invoking `curl` which gets through reliably on macOS."""

    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code != 403:
            raise
        raw = _fetch_via_curl(url, timeout)

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("latin-1", errors="replace")


def _fetch_via_curl(url: str, timeout: float) -> bytes:
    result = subprocess.run(
        [
            "curl", "-sSL", "--fail",
            "--max-time", str(int(timeout)),
            "-A", USER_AGENT,
            "-H", "Accept-Language: en-US,en;q=0.9",
            url,
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise urllib.error.URLError(
            f"curl fallback failed (exit {result.returncode}): "
            f"{result.stderr.decode('utf-8', 'replace').strip()}"
        )
    return result.stdout


def _clean_pre(text: str) -> str:
    # Strip leading/trailing whitespace then ensure a single trailing newline.
    stripped = text.strip("\r\n")
    return stripped + "\n" if stripped else ""


def parse_atcoder(html_text: str) -> ProblemData:
    data = ProblemData()

    # Modern AtCoder uses <title>A - Foo</title>; the old <span class="h2"> is gone.
    m = re.search(r'<span class="h2">\s*([^<]+?)\s*</span>', html_text)
    if not m:
        m = re.search(r"<title>\s*([^<]+?)\s*</title>", html_text)
    if m:
        data.name = html.unescape(m.group(1)).strip()

    m = re.search(r"Time Limit:\s*(\d+(?:\.\d+)?)\s*sec", html_text)
    if m:
        data.time_limit_ms = int(round(float(m.group(1)) * 1000))
    # AtCoder writes either "MB" or "MiB"; treat both as MB for our purposes.
    m = re.search(r"Memory Limit:\s*(\d+)\s*Mi?B", html_text)
    if m:
        data.memory_limit_mb = int(m.group(1))

    # Prefer the English section if present.
    en = re.search(
        r'<span class="lang-en">(.*?)</span>\s*(?:<span class="lang-ja">|$)',
        html_text,
        re.DOTALL,
    )
    scope = en.group(1) if en else html_text

    inputs: dict[int, str] = {}
    outputs: dict[int, str] = {}
    for m in re.finditer(
        r"Sample Input\s*(\d+)\s*</h3>\s*<pre[^>]*>(.*?)</pre>",
        scope,
        re.DOTALL,
    ):
        inputs[int(m.group(1))] = _clean_pre(html.unescape(m.group(2)))
    for m in re.finditer(
        r"Sample Output\s*(\d+)\s*</h3>\s*<pre[^>]*>(.*?)</pre>",
        scope,
        re.DOTALL,
    ):
        outputs[int(m.group(1))] = _clean_pre(html.unescape(m.group(2)))

    for n in sorted(set(inputs) & set(outputs)):
        data.tests.append((inputs[n], outputs[n]))
    return data


def _flatten_cf_pre(pre_inner: str) -> str:
    # CF wraps each input line in <div class="test-example-line">line</div>.
    lines = re.findall(
        r'<div[^>]*class="[^"]*test-example-line[^"]*"[^>]*>(.*?)</div>',
        pre_inner,
        re.DOTALL,
    )
    if lines:
        body = "\n".join(html.unescape(_strip_tags(line)) for line in lines)
    else:
        body = html.unescape(_strip_tags(pre_inner))
    return _clean_pre(body)


def _strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def parse_codeforces(html_text: str) -> ProblemData:
    data = ProblemData()

    # Preferred: "<div class='title'>C. Name</div>" inside the problem header.
    m = re.search(r'<div class="title">\s*([A-Z0-9]+\.\s*[^<]+?)\s*</div>', html_text)
    if not m:
        # Fallback: the document <title> is usually "Problem - 1168C - Codeforces".
        t = re.search(r"<title>\s*([^<]+?)\s*</title>", html_text)
        if t:
            data.name = html.unescape(t.group(1)).strip()
    else:
        data.name = html.unescape(m.group(1)).strip()

    m = re.search(
        r'<div class="time-limit">.*?</div>\s*(\d+(?:\.\d+)?)\s*second',
        html_text,
        re.DOTALL,
    )
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)\s*seconds?\s*</div>", html_text)
    if m:
        data.time_limit_ms = int(round(float(m.group(1)) * 1000))
    m = re.search(r"(\d+)\s*megabytes\s*</div>", html_text)
    if m:
        data.memory_limit_mb = int(m.group(1))

    sample_block = re.search(
        r'<div class="sample-test">(.*?)</div>\s*(?:<div class="note"|</div>)',
        html_text,
        re.DOTALL,
    )
    scope = sample_block.group(1) if sample_block else html_text

    inputs = [
        _flatten_cf_pre(m.group(1))
        for m in re.finditer(
            r'<div class="input">.*?<pre[^>]*>(.*?)</pre>', scope, re.DOTALL
        )
    ]
    outputs = [
        _flatten_cf_pre(m.group(1))
        for m in re.finditer(
            r'<div class="output">.*?<pre[^>]*>(.*?)</pre>', scope, re.DOTALL
        )
    ]
    for a, b in zip(inputs, outputs):
        data.tests.append((a, b))
    return data


def fetch_problem(parsed: ParsedURL) -> ProblemData:
    html_text = fetch_html(parsed.canonical_url)
    if parsed.platform == "atc":
        return parse_atcoder(html_text)
    if parsed.platform == "cf":
        return parse_codeforces(html_text)
    raise AssertionError(parsed.platform)


# ---------------------------------------------------------------------------
# Difficulty / tag lookup via sibling scripts
# ---------------------------------------------------------------------------


@dataclass
class Difficulty:
    source: Optional[str] = None
    value: Optional[int] = None
    tags: list[str] = field(default_factory=list)


def lookup_difficulty(parsed: ParsedURL) -> Difficulty:
    if parsed.platform == "atc":
        script = SCRIPTS / "lookup_atcoder_difficulty.py"
        try:
            out = subprocess.check_output(
                [sys.executable, str(script), parsed.problem_id],
                text=True,
            )
            payload = json.loads(out)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            print(f"[init] atcoder lookup failed: {exc}", file=sys.stderr)
            return Difficulty()
        if payload.get("found") and payload.get("difficulty") is not None:
            return Difficulty(
                source="kenkoooo-local",
                value=int(round(payload["difficulty"])),
            )
        return Difficulty()

    if parsed.platform == "cf":
        script = SCRIPTS / "lookup_codeforces_difficulty.py"
        try:
            out = subprocess.check_output(
                [sys.executable, str(script), parsed.contest_id, parsed.index or ""],
                text=True,
            )
            payload = json.loads(out)
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            print(f"[init] codeforces lookup failed: {exc}", file=sys.stderr)
            return Difficulty()
        return Difficulty(
            source="codeforces-api" if payload.get("found") else None,
            value=payload.get("rating"),
            tags=payload.get("tags") or [],
        )

    return Difficulty()


# ---------------------------------------------------------------------------
# File materialization
# ---------------------------------------------------------------------------


@dataclass
class InitOptions:
    refresh_testcases: bool = False
    refresh_metadata: bool = False
    force_references: bool = False
    force_statement: bool = False
    add_to_session: bool = False
    dry_run: bool = False


def _render(template: Path, mapping: dict[str, str]) -> str:
    text = template.read_text(encoding="utf-8")
    for k, v in mapping.items():
        text = text.replace("{{" + k + "}}", v)
        text = text.replace("__" + k + "__", v)
    return text


def _is_effectively_empty(path: Path) -> bool:
    if not path.exists():
        return True
    content = path.read_text(encoding="utf-8", errors="replace").strip()
    return content == ""


def _write(path: Path, content: str, actions: list[str], label: str, dry: bool) -> None:
    if dry:
        actions.append(f"would write {label}: {path.relative_to(REPO_ROOT)}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    actions.append(f"{label}: {path.relative_to(REPO_ROOT)}")


def build_problem_yaml(
    parsed: ParsedURL,
    problem: ProblemData,
    difficulty: Difficulty,
    existing: Optional[dict] = None,
    refresh_metadata: bool = False,
) -> dict:
    """Build the problem.yaml dict. If `existing` is provided, merge
    (existing values win unless the field is empty/null), except when
    `refresh_metadata` is True, where difficulty/limits are always refreshed.
    """

    title = problem.name or (existing or {}).get("problem", {}).get("title") or ""

    base = {
        "schema_version": 1,
        "problem": {
            "platform": parsed.platform,
            "contest_id": parsed.contest_id,
            "problem_id": parsed.problem_id,
            "slug": parsed.slug,
            "title": title,
            "url": parsed.canonical_url,
            "tags": list(difficulty.tags),
            "difficulty": {
                "source": difficulty.source,
                "value": difficulty.value,
            },
            "time_limit_ms": problem.time_limit_ms,
            "memory_limit_mb": problem.memory_limit_mb,
        },
        "status": {
            "state": "not_started",
            "first_started_at": None,
            "last_touched_at": None,
            "solved_at": None,
            "current_attempt_id": None,
            "canonical_solution_path": None,
        },
        "workflow": {
            "language": "cpp17",
            "workspace_entry": "workspace/main.cpp",
            "review_required": True,
        },
        "references": {
            "editorial": {"status": "pending", "path": "references/editorial.md"},
            "ranker": {"status": "pending", "path": "references/ranker.md"},
        },
        "review": {"status": "pending", "path": "review/review.md"},
    }

    if existing is None:
        return base

    merged = _deep_merge_preserving(existing, base)

    if refresh_metadata:
        # Plan: --refresh-metadata only touches difficulty, time_limit, memory_limit.
        # Tags are left to the normal merge path (filled only if existing is empty).
        prob = merged.setdefault("problem", {})
        if problem.time_limit_ms is not None:
            prob["time_limit_ms"] = problem.time_limit_ms
        if problem.memory_limit_mb is not None:
            prob["memory_limit_mb"] = problem.memory_limit_mb
        if difficulty.value is not None:
            prob.setdefault("difficulty", {})
            prob["difficulty"]["source"] = difficulty.source
            prob["difficulty"]["value"] = difficulty.value
    return merged


def _deep_merge_preserving(existing, new):
    """Return a dict where existing non-empty values win; empty/None slots get
    filled from new. Lists: existing wins unless empty.
    """
    if isinstance(existing, dict) and isinstance(new, dict):
        out = dict(existing)
        for k, nv in new.items():
            if k not in out:
                out[k] = nv
            else:
                out[k] = _deep_merge_preserving(out[k], nv)
        return out
    # Scalars and lists: existing wins unless it's None/empty.
    if existing is None:
        return new
    if isinstance(existing, str) and existing.strip() == "":
        return new
    if isinstance(existing, list) and len(existing) == 0:
        return new
    return existing


def dump_yaml(data: dict) -> str:
    return yaml.safe_dump(
        data,
        sort_keys=False,
        allow_unicode=True,
        default_flow_style=False,
    )


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------


def init_problem(parsed: ParsedURL, problem: ProblemData, difficulty: Difficulty,
                 opts: InitOptions) -> tuple[Path, list[str]]:
    problem_root = PROBLEMS / parsed.platform / parsed.slug
    actions: list[str] = []
    existed = problem_root.exists()

    if existed:
        actions.append(f"existing problem detected: {problem_root.relative_to(REPO_ROOT)}")
    else:
        actions.append(f"creating new problem: {problem_root.relative_to(REPO_ROOT)}")

    # 1. Create directory tree (no-op if already present).
    for sub in ("workspace/testcases", "references", "attempts", "review"):
        (problem_root / sub).mkdir(parents=True, exist_ok=True) if not opts.dry_run else None

    # 2. problem.yaml — merge if exists.
    pyaml_path = problem_root / "problem.yaml"
    existing_yaml = None
    if pyaml_path.exists():
        try:
            existing_yaml = yaml.safe_load(pyaml_path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            print(f"[init] warning: could not parse existing problem.yaml: {exc}", file=sys.stderr)

    rendered = build_problem_yaml(
        parsed, problem, difficulty,
        existing=existing_yaml,
        refresh_metadata=opts.refresh_metadata,
    )
    if existing_yaml is None:
        _write(pyaml_path, dump_yaml(rendered), actions, "problem.yaml", opts.dry_run)
    elif rendered != existing_yaml or opts.refresh_metadata:
        _write(pyaml_path, dump_yaml(rendered), actions,
               "problem.yaml (merged)" if not opts.refresh_metadata else "problem.yaml (refreshed)",
               opts.dry_run)
    else:
        actions.append("problem.yaml: unchanged")

    # 3. workspace/main.cpp — NEVER overwrite.
    main_cpp = problem_root / "workspace" / "main.cpp"
    if main_cpp.exists():
        actions.append("workspace/main.cpp: skip (user file)")
    else:
        _write(main_cpp,
               (TEMPLATES / "workspace-main.cpp").read_text(encoding="utf-8"),
               actions, "workspace/main.cpp", opts.dry_run)

    # 4. workspace/notes.md — NEVER overwrite.
    notes = problem_root / "workspace" / "notes.md"
    if notes.exists():
        actions.append("workspace/notes.md: skip (user file)")
    else:
        _write(notes,
               (TEMPLATES / "workspace.notes.md").read_text(encoding="utf-8"),
               actions, "workspace/notes.md", opts.dry_run)

    # 5. testcases — add missing, optionally refresh all.
    tc_dir = problem_root / "workspace" / "testcases"
    if opts.refresh_testcases and not opts.dry_run:
        for f in tc_dir.glob("sample_*"):
            f.unlink()
    existing_inputs = {int(m.group(1)) for f in tc_dir.glob("sample_input_*.txt")
                       if (m := re.match(r"sample_input_(\d+)\.txt$", f.name))}
    added = 0
    kept = 0
    for i, (inp, outp) in enumerate(problem.tests, start=1):
        in_path = tc_dir / f"sample_input_{i}.txt"
        out_path = tc_dir / f"sample_output_{i}.txt"
        if (i in existing_inputs) and not opts.refresh_testcases:
            kept += 1
            continue
        _write(in_path, inp, actions, f"testcase input {i}", opts.dry_run)
        _write(out_path, outp, actions, f"testcase output {i}", opts.dry_run)
        added += 1
    actions.append(f"testcases: {kept} existing kept, {added} written (total now "
                   f"{kept + added})")

    # 6. statement.md — only if empty/missing or forced.
    stmt_path = problem_root / "statement.md"
    if opts.force_statement or _is_effectively_empty(stmt_path):
        content = _render(TEMPLATES / "statement.md", {
            "TITLE": problem.name or parsed.slug,
            "URL": parsed.canonical_url,
        })
        _write(stmt_path, content, actions, "statement.md", opts.dry_run)
    else:
        actions.append("statement.md: skip (non-empty)")

    # 7. README.md — always regenerate (volatile status file).
    readme_path = problem_root / "README.md"
    state = (existing_yaml or {}).get("status", {}).get("state") or "not_started"
    attempt = (existing_yaml or {}).get("status", {}).get("current_attempt_id") or "none"
    readme_content = _render(TEMPLATES / "problem.README.md", {
        "TITLE": problem.name or parsed.slug,
        "PLATFORM": parsed.platform,
        "PROBLEM_ID": parsed.problem_id,
        "PROBLEM_SLUG": parsed.slug,
        "STATE": str(state),
        "CURRENT_ATTEMPT_ID": str(attempt),
    })
    _write(readme_path, readme_content, actions, "README.md", opts.dry_run)

    # 8. references/* — only if empty/missing or forced.
    for name, tpl in (
        ("editorial.md", TEMPLATES / "editorial.md"),
        ("ranker.md", TEMPLATES / "ranker.md"),
        ("references.yaml", TEMPLATES / "references.yaml"),
    ):
        dst = problem_root / "references" / name
        if opts.force_references or _is_effectively_empty(dst):
            _write(dst, tpl.read_text(encoding="utf-8"), actions, f"references/{name}", opts.dry_run)
        else:
            actions.append(f"references/{name}: skip (non-empty)")

    # 9. review/* — skeleton only if missing/empty. Never overwrite user work.
    for name, tpl in (
        ("review.md", TEMPLATES / "review.md"),
        ("review.yaml", TEMPLATES / "review.yaml"),
    ):
        dst = problem_root / "review" / name
        if _is_effectively_empty(dst):
            _write(dst, tpl.read_text(encoding="utf-8"), actions, f"review/{name}", opts.dry_run)
        else:
            actions.append(f"review/{name}: skip (user file)")

    # 10. attempts/.gitkeep so the empty directory is tracked by git.
    gitkeep = problem_root / "attempts" / ".gitkeep"
    if not gitkeep.exists() and not any((problem_root / "attempts").glob("*")):
        _write(gitkeep, "", actions, "attempts/.gitkeep", opts.dry_run)

    return problem_root, actions


def register_session(slug: str, dry_run: bool, actions: list[str]) -> None:
    today = date.today().isoformat()
    session_path = SESSIONS / f"{today}.yaml"
    if session_path.exists():
        try:
            data = yaml.safe_load(session_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            data = {}
    else:
        data = {
            "schema_version": 1,
            "session": {"date": today},
            "log": [],
            "next_actions": [],
        }
    queue = data.setdefault("log", [])
    if any((entry or {}).get("slug") == slug for entry in queue if isinstance(entry, dict)):
        actions.append(f"session {today}: slug already present")
        return
    queue.append({"slug": slug, "status": "queued"})
    if dry_run:
        actions.append(f"would register in sessions/{today}.yaml")
        return
    session_path.parent.mkdir(parents=True, exist_ok=True)
    session_path.write_text(
        yaml.safe_dump(data, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    actions.append(f"session: registered in sessions/{today}.yaml")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Initialize a problem workspace from a URL")
    p.add_argument("url", help="Problem URL (AtCoder or Codeforces)")
    p.add_argument("--refresh-testcases", action="store_true",
                   help="delete existing sample_* files and re-download")
    p.add_argument("--refresh-metadata", action="store_true",
                   help="overwrite difficulty, time/memory limits in problem.yaml")
    p.add_argument("--force-references", action="store_true",
                   help="reset references/* to templates")
    p.add_argument("--force-statement", action="store_true",
                   help="reset statement.md to template")
    p.add_argument("--session", action="store_true",
                   help="register the slug in today's sessions/{yyyy-mm-dd}.yaml")
    p.add_argument("--dry-run", action="store_true", help="show actions without writing")
    p.add_argument("--no-fetch", action="store_true",
                   help="skip HTTP fetch; useful when offline and only merging metadata "
                        "(limits/samples will be None and no testcases added)")
    return p


def main() -> int:
    args = build_parser().parse_args()
    try:
        parsed = parse_url(args.url)
    except ValueError as exc:
        print(f"[init] {exc}", file=sys.stderr)
        return 2

    if args.no_fetch:
        problem = ProblemData()
    else:
        try:
            problem = fetch_problem(parsed)
        except urllib.error.URLError as exc:
            print(f"[init] network error fetching {parsed.canonical_url}: {exc}", file=sys.stderr)
            return 3
        except FileNotFoundError:
            print("[init] curl fallback needed but `curl` is not on PATH", file=sys.stderr)
            return 3
        except (re.error, ValueError, AttributeError, KeyError) as exc:
            print(
                f"[init] failed to parse problem page ({type(exc).__name__}: {exc})",
                file=sys.stderr,
            )
            return 4

    # If fetch returned nothing usable and the problem directory doesn't
    # already exist, the URL is almost certainly wrong (typo, removed
    # problem, etc.). Refuse rather than leaving a hollow directory.
    problem_root = PROBLEMS / parsed.platform / parsed.slug
    if (not problem_root.exists()
            and not args.no_fetch
            and problem.name is None
            and not problem.tests
            and problem.time_limit_ms is None):
        print(
            f"[init] page fetched but no title/samples/limits recognized; "
            f"aborting to avoid creating an empty directory. "
            f"Double-check the URL, or pass --no-fetch to create the skeleton anyway.",
            file=sys.stderr,
        )
        return 5

    difficulty = lookup_difficulty(parsed)

    opts = InitOptions(
        refresh_testcases=args.refresh_testcases,
        refresh_metadata=args.refresh_metadata,
        force_references=args.force_references,
        force_statement=args.force_statement,
        add_to_session=args.session,
        dry_run=args.dry_run,
    )

    problem_root, actions = init_problem(parsed, problem, difficulty, opts)

    if args.session:
        register_session(parsed.slug, args.dry_run, actions)

    print(f"[init] {parsed.platform} {parsed.slug} -> {problem_root.relative_to(REPO_ROOT)}")
    print(f"[init] title: {problem.name or '(unknown)'}")
    print(f"[init] limits: {problem.time_limit_ms} ms / {problem.memory_limit_mb} MB")
    print(f"[init] difficulty: {difficulty.value} ({difficulty.source or 'none'})")
    if difficulty.tags:
        print(f"[init] tags: {', '.join(difficulty.tags)}")
    print(f"[init] samples: {len(problem.tests)}")
    for a in actions:
        print(f"  - {a}")
    if args.dry_run:
        print("[init] dry-run: no files written")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
