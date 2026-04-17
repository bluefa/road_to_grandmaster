---
name: problem-intake
description: Create a new competitive programming problem workspace for AtCoder or Codeforces from a URL. Wraps scripts/init_problem.py, which handles URL parsing, sample testcase download, difficulty lookup, and idempotent file materialization.
---

# Problem Intake

Initialize (or top up) a problem under `problems/{platform}/{problem_slug}/` from an AtCoder or Codeforces URL.

The heavy lifting lives in `../../scripts/init_problem.py`. This skill is a thin wrapper: collect the URL, call the script, interpret the output, and confirm optional follow-ups with the user.

## Scope
- Supported platforms: **AtCoder** (`atcoder.jp/contests/<c>/tasks/<task>`), **Codeforces** (`codeforces.com/contest/<n>/problem/<i>` or `/problemset/problem/<n>/<i>`).
- Unsupported URLs raise an error; do not attempt to handle BOJ, CF gym, AtCoder heuristic contests, etc.

## Main Workspace Rule
- Canonical workspace root: `/Users/study/road_to_grandmaster`.
- If the current session is running inside a worktree or any path other than the canonical root, call the script from the canonical root (e.g. `/Users/study/road_to_grandmaster/scripts/init_problem.py`).
- Relative paths shown to the user should be canonical-root-relative.

## Inputs
- `url` (required)
- optional: user asked to register the slug in today's session
- optional: user asked to refresh testcases or difficulty/limits on an existing problem

## Workflow
1. Ask for the URL if not provided. Do **not** guess a platform from a slug alone.
2. Invoke the script with the minimal flag set:
   ```bash
   /Users/study/road_to_grandmaster/scripts/init_problem.py <url> [flags]
   ```
   Flags to use only when the user asks:
   - `--session` — register today's session entry
   - `--refresh-testcases` — re-download samples (on an existing problem)
   - `--refresh-metadata` — overwrite difficulty/time/memory in problem.yaml
   - `--force-references` / `--force-statement` — reset those files to templates
   - `--dry-run` — preview actions without writing
3. Read the script's stdout. It already prints title, limits, difficulty, tags, samples, and a per-file action log. Summarize that back to the user; do not re-derive the paths manually.
4. On non-zero exit:
   - `2` → URL not supported. Ask the user for the correct URL form.
   - `3` → network / curl error. Suggest checking connectivity; do not retry silently more than once.
   - `4` → parse failure. The platform's HTML likely drifted; report the problem, do not patch the scraper from within the skill.
   - `5` → guard tripped (no title/samples/limits). Very likely a bad URL. Confirm with the user before any `--no-fetch` retry.
5. If the user asked to register the attempt in today's session but didn't add `--session`, re-run with the flag (idempotent — the script is a no-op if the slug is already present).

## Guardrails
- Do not solve the problem.
- Do not generate hints or editorial summaries.
- Do not read or summarize `references/editorial.md` or `references/ranker.md` during intake.
- Do not bypass the script by creating files directly, **except** when the script fails with exit 4 and the user explicitly asks for a manual skeleton — in that case prefer `--no-fetch` to let the script still handle the directory layout and metadata merge.
- Never pass `--refresh-testcases`, `--refresh-metadata`, `--force-references`, or `--force-statement` without explicit user consent — they are destructive on already-curated content.
- The script protects `workspace/main.cpp`, `workspace/notes.md`, `attempts/`, and `review/` under all flag combinations. Do not attempt to circumvent this protection.

## What the script does under the hood (for reference)
- Parses the URL into `(platform, contest_id, problem_id, slug)`.
- Fetches the problem page (urllib first, `curl` fallback on 403 — Codeforces requires this).
- Extracts sample inputs/outputs, time limit, memory limit, and title from the HTML.
- Calls `scripts/lookup_atcoder_difficulty.py` or `scripts/lookup_codeforces_difficulty.py` for difficulty and tags; the CF cache is auto-refreshed if older than 24h.
- Writes the problem tree from `templates/*`, merging `problem.yaml` if it already exists (existing non-empty fields win).
