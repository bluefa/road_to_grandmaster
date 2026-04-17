#!/usr/bin/env python3
"""Refresh the vendored Codeforces problemset cache.

Fetches `problemset.problems` from the Codeforces public API and writes the
`result` payload to `data/codeforces/problemset.json`. No authentication is
required; the `/api/*` endpoints are not behind Cloudflare.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "data" / "codeforces" / "problemset.json"
API_URL = "https://codeforces.com/api/problemset.problems"


def fetch(url: str, timeout: float) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "road-to-grandmaster/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Refresh Codeforces problemset cache")
    p.add_argument("--out", type=Path, default=DEFAULT_OUT, help="output JSON path")
    p.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout seconds")
    p.add_argument("--quiet", action="store_true", help="suppress stdout summary")
    return p


def main() -> int:
    args = build_parser().parse_args()
    out: Path = args.out.resolve()

    try:
        payload = fetch(API_URL, args.timeout)
    except urllib.error.URLError as exc:
        print(f"[refresh_cf] network error: {exc}", file=sys.stderr)
        return 2

    if payload.get("status") != "OK":
        print(f"[refresh_cf] CF API returned non-OK: {payload}", file=sys.stderr)
        return 3

    result = payload["result"]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(result, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8",
    )

    if not args.quiet:
        problems = result.get("problems", [])
        rated = sum(1 for p in problems if p.get("rating") is not None)
        print(
            f"[refresh_cf] cached {len(problems)} problems "
            f"({rated} rated) -> {out}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
