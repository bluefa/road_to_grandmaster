#!/usr/bin/env python3
"""Import Codeforces / AtCoder cookies from a local browser into oj's cookie jar.

Why this exists:
    Both platforms sit behind Cloudflare challenges that oj cannot defeat with
    password or Selenium modes reliably. Copying cookies from a real browser
    (where the user has already solved the challenge manually) gives oj a valid
    session. Subsequent `oj submit` works normally.

Usage:
    pip3 install --user browser-cookie3   # one-time
    ./scripts/import_browser_cookies.py codeforces
    ./scripts/import_browser_cookies.py atcoder --browser safari
    oj login --check https://codeforces.com/
"""

from __future__ import annotations

import argparse
import http.cookiejar
import sys
from pathlib import Path

OJ_JAR = Path.home() / "Library/Application Support/online-judge-tools/cookie.jar"

PLATFORMS = {
    "codeforces": {
        "domain": "codeforces.com",
        "check_url": "https://codeforces.com/",
    },
    "atcoder": {
        "domain": "atcoder.jp",
        "check_url": "https://atcoder.jp/",
    },
}


def _import_browser_cookie3():
    try:
        import browser_cookie3  # type: ignore
        return browser_cookie3
    except ImportError:
        sys.exit(
            "browser-cookie3 is not installed.\n"
            "Install with:  pip3 install --user browser-cookie3"
        )


def fetch_browser_cookies(browser: str, domain: str):
    bc3 = _import_browser_cookie3()
    loader = {
        "chrome":  bc3.chrome,
        "firefox": bc3.firefox,
        "safari":  bc3.safari,
        "edge":    bc3.edge,
        "brave":   bc3.brave,
    }.get(browser)
    if loader is None:
        sys.exit(
            f"unsupported browser: {browser!r}. "
            "Supported: chrome, firefox, safari, edge, brave"
        )
    try:
        return list(loader(domain_name=domain))
    except Exception as exc:
        sys.exit(
            f"failed to read {browser} cookies for {domain}: {exc}\n"
            "Common causes:\n"
            "  - macOS Keychain denied access (accept the prompt and retry)\n"
            "  - the browser is not installed or you are not logged in there\n"
            "  - Chrome profile is locked (quit all Chrome windows and retry)"
        )


def domain_matches(cookie_domain: str, target: str) -> bool:
    """Match 'codeforces.com' and '.codeforces.com' but not 'codeforces.com.evil.net'."""
    d = cookie_domain.lstrip(".")
    return d == target or d.endswith("." + target)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Import browser session cookies into oj's cookie jar",
    )
    ap.add_argument("platform", choices=sorted(PLATFORMS.keys()))
    ap.add_argument("--browser", default="chrome",
                    help="source browser (default: chrome)")
    ap.add_argument("--jar", type=Path, default=OJ_JAR,
                    help="destination oj cookie jar (default: macOS oj location)")
    ap.add_argument("--dry-run", action="store_true",
                    help="show what would be imported, do not write")
    args = ap.parse_args()

    conf = PLATFORMS[args.platform]
    target_domain = conf["domain"]

    browser_cookies = fetch_browser_cookies(args.browser, target_domain)
    relevant = [c for c in browser_cookies if domain_matches(c.domain, target_domain)]

    if not relevant:
        print(
            f"[import] no {args.platform} cookies found in {args.browser}. "
            f"Are you logged in at {conf['check_url']} there?",
            file=sys.stderr,
        )
        return 1

    # Load the existing oj jar (may contain cookies for other platforms).
    oj_jar = http.cookiejar.LWPCookieJar(str(args.jar))
    if args.jar.exists():
        try:
            oj_jar.load(ignore_discard=True, ignore_expires=True)
        except Exception as exc:
            print(f"[import] warning: could not parse existing jar ({exc}); starting fresh",
                  file=sys.stderr)

    # Build a fresh jar: keep cookies for *other* domains, replace ours entirely.
    fresh = http.cookiejar.LWPCookieJar(str(args.jar))
    kept = 0
    for c in oj_jar:
        if not domain_matches(c.domain, target_domain):
            fresh.set_cookie(c)
            kept += 1

    # Add the browser cookies for our platform.
    for c in relevant:
        fresh.set_cookie(c)

    print(
        f"[import] source: {args.browser}  target: {args.platform} ({target_domain})\n"
        f"[import] kept {kept} cookies from other domains, "
        f"replacing {args.platform} cookies with {len(relevant)} from browser"
    )

    if args.dry_run:
        for c in relevant:
            expiry = c.expires or "session"
            print(f"  + {c.name}={c.value[:18]}... domain={c.domain} expires={expiry}")
        print("[import] dry-run: nothing written")
        return 0

    args.jar.parent.mkdir(parents=True, exist_ok=True)
    fresh.save(ignore_discard=True, ignore_expires=True)
    print(f"[import] wrote {args.jar}")
    print(f"[import] verify: oj login --check {conf['check_url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
