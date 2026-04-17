#!/usr/bin/env python3
"""Lookup Codeforces problem difficulty and tags from the vendored cache.

Reads `data/codeforces/problemset.json`. If the cache is missing or older than
`--max-age-seconds` (default 24h), automatically invokes
`refresh_codeforces_problems.py` before reading. Prints a compact JSON object.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CACHE = REPO_ROOT / "data" / "codeforces" / "problemset.json"
REFRESH_SCRIPT = Path(__file__).with_name("refresh_codeforces_problems.py")
DEFAULT_MAX_AGE = 24 * 60 * 60  # 1 day


def cache_is_stale(path: Path, max_age: float) -> bool:
    if not path.exists():
        return True
    return (time.time() - path.stat().st_mtime) > max_age


def refresh_cache(cache: Path) -> None:
    subprocess.run(
        [sys.executable, str(REFRESH_SCRIPT), "--out", str(cache), "--quiet"],
        check=True,
    )


def find_problem(data: dict[str, Any], contest_id: int, index: str) -> dict | None:
    idx = index.upper()
    for p in data.get("problems", []):
        if p.get("contestId") == contest_id and p.get("index") == idx:
            return p
    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Lookup Codeforces difficulty/tags from the local vendored cache"
    )
    p.add_argument("contest_id", type=int, help="Codeforces contest id, e.g. 1168")
    p.add_argument("index", help="Problem index within the contest, e.g. C or E1")
    p.add_argument("--cache", type=Path, default=DEFAULT_CACHE)
    p.add_argument(
        "--max-age-seconds",
        type=float,
        default=DEFAULT_MAX_AGE,
        help="refresh cache if older than this (default: 86400)",
    )
    p.add_argument(
        "--no-refresh",
        action="store_true",
        help="never trigger a network refresh, even if the cache is stale",
    )
    p.add_argument(
        "--value-only",
        action="store_true",
        help="print only the rating integer or 'null'",
    )
    return p


def main() -> int:
    args = build_parser().parse_args()
    cache: Path = args.cache.resolve()

    if cache_is_stale(cache, args.max_age_seconds) and not args.no_refresh:
        try:
            refresh_cache(cache)
        except subprocess.CalledProcessError as exc:
            if not cache.exists():
                print(f"[lookup_cf] refresh failed and no cache present: {exc}", file=sys.stderr)
                return 2
            print(f"[lookup_cf] refresh failed, using stale cache: {exc}", file=sys.stderr)

    if not cache.exists():
        print(f"[lookup_cf] cache not found: {cache}", file=sys.stderr)
        return 2

    data = json.loads(cache.read_text(encoding="utf-8"))
    problem = find_problem(data, args.contest_id, args.index)

    if args.value_only:
        rating = None if problem is None else problem.get("rating")
        print("null" if rating is None else rating)
        return 0

    result = {
        "contest_id": args.contest_id,
        "index": args.index.upper(),
        "found": problem is not None,
        "rating": None if problem is None else problem.get("rating"),
        "tags": [] if problem is None else problem.get("tags", []),
        "name": None if problem is None else problem.get("name"),
        "source": "codeforces-api",
        "cache_path": str(cache),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
