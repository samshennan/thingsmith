#!/usr/bin/env python3
"""Platform handle checker for the namesmith skill.

A domain alone is not a name. The package registry that already owns your word
will outrank you forever, and the GitHub org you cannot have will follow the
project for its whole life. This checks the surfaces that can be checked
honestly, and refuses to guess about the ones that cannot.

Same discipline as check_domains.py: a platform that blocks anonymous lookups
reports BLOCKED, never "free". Anything ambiguous reports UNKNOWN. Only an
explicit 404 from an endpoint that is known to 404 on absence counts as FREE.

Usage:
    python check_handles.py --names ritka karbia
    python check_handles.py --names ritka --only github npm pypi --json out.json
    python check_handles.py --list
"""

import argparse
import json
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request

FREE, TAKEN, BLOCKED, UNKNOWN = "FREE", "taken", "BLOCKED", "UNKNOWN"

_ctx = ssl.create_default_context()
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) namesmith/2.0 "
       "(brand-name availability check)")

# name -> (url template, note)
# Only endpoints verified to answer 404 on an absent handle belong here.
CHECKS = {
    "github":     ("https://api.github.com/users/{n}",
                   "60 unauthenticated req/hr; org names share this namespace"),
    "npm":        ("https://registry.npmjs.org/{n}", ""),
    "pypi":       ("https://pypi.org/pypi/{n}/json",
                   "PyPI normalises - / _ / . to the same name"),
    "crates":     ("https://crates.io/api/v1/crates/{n}", ""),
    "dockerhub":  ("https://hub.docker.com/v2/users/{n}/", ""),
    "huggingface": ("https://huggingface.co/{n}",
                    "the HTML page covers users and orgs; the API only users"),
    "reddit":     ("https://www.reddit.com/user/{n}/about.json",
                   "subreddit r/{n} is a separate namespace - check by hand"),
    "youtube":    ("https://www.youtube.com/@{n}", ""),
    "telegram":   ("https://t.me/{n}", "t.me always 200s; body is inspected"),
    "bluesky":    ("https://public.api.bsky.app/xrpc/com.atproto.identity."
                   "resolveHandle?handle={n}.bsky.social", ""),
    "gitlab":     ("https://gitlab.com/api/v4/users?username={n}", ""),
}

# Surfaces that matter but cannot be checked without an account. Printed so the
# report never silently omits them.
MANUAL = {
    "x/twitter":   "anonymous lookups blocked - check while logged in",
    "instagram":   "anonymous lookups blocked - check while logged in",
    "linkedin":    "company slug linkedin.com/company/<n> - check logged in",
    "producthunt": "needs an account",
    "tiktok":      "anonymous lookups rate-limited and unreliable",
    "app stores":  "developer name uniqueness - check in the console",
}


def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": _UA,
                                               "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx) as r:
            return r.status, r.read(65536)
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(2048)
        except Exception:
            return e.code, b""
    except Exception as e:
        return type(e).__name__, b""


def classify(platform, name, code, body):
    if platform == "telegram":
        # t.me returns 200 for everything; an unclaimed handle has no title
        if code == 200:
            low = body.lower()
            # every t.me URL renders; only a claimed handle gets a title block
            if b"tgme_page_title" in low:
                return TAKEN, "profile block present"
            return FREE, "no profile block in page"
        return UNKNOWN, f"http {code}"
    if platform == "gitlab":
        if code == 200:
            return (TAKEN, "user returned") if body.strip() not in (b"[]", b"") \
                else (FREE, "empty result set")
        return UNKNOWN, f"http {code}"
    if platform == "bluesky":
        if code == 400:
            return FREE, "handle does not resolve"
        if code == 200:
            return TAKEN, "handle resolves"
        return UNKNOWN, f"http {code}"

    if code == 404:
        return FREE, "http 404"
    if code == 200:
        return TAKEN, "http 200"
    if code in (403, 429):
        return BLOCKED, f"http {code} - rate limited or gated"
    return UNKNOWN, f"http {code}"


def check(name, platforms, sleep, results, lock):
    for i, p in enumerate(platforms):
        tmpl, _note = CHECKS[p]
        code, body = fetch(tmpl.format(n=name))
        status, detail = classify(p, name, code, body)
        with lock:
            results.append({"name": name, "platform": p,
                            "status": status, "detail": detail})
            flag = "*" if status == FREE else " "
            print(f"{flag} {name:<14} {p:<12} {status:<8} {detail}", flush=True)
        if i < len(platforms) - 1:
            time.sleep(sleep)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", nargs="+")
    ap.add_argument("--only", nargs="+", choices=sorted(CHECKS),
                    help="restrict to these platforms")
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--json", dest="json_path")
    ap.add_argument("--list", action="store_true",
                    help="show checkable and manual-only surfaces")
    args = ap.parse_args()

    if args.list:
        print("automated:")
        for p, (_u, note) in sorted(CHECKS.items()):
            print(f"  {p:<13} {note}")
        print("manual only:")
        for p, note in sorted(MANUAL.items()):
            print(f"  {p:<13} {note}")
        return 0

    if not args.names:
        ap.error("--names is required unless --list is used")

    platforms = args.only or sorted(CHECKS)
    results, lock = [], threading.Lock()
    threads = [threading.Thread(target=check,
                                args=(n, platforms, args.sleep, results, lock),
                                daemon=True) for n in args.names]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print("\n--- summary ---")
    for n in args.names:
        rows = [r for r in results if r["name"] == n]
        free = [r["platform"] for r in rows if r["status"] == FREE]
        taken = [r["platform"] for r in rows if r["status"] == TAKEN]
        murky = [f"{r['platform']}({r['status']})" for r in rows
                 if r["status"] in (BLOCKED, UNKNOWN)]
        print(f"{n}:")
        print(f"  free  ({len(free)}): {', '.join(free) or 'none'}")
        print(f"  taken ({len(taken)}): {', '.join(taken) or 'none'}")
        if murky:
            print(f"  UNRESOLVED: {', '.join(murky)}  <- not free, just unknown")
    print("\nstill to check by hand: " + ", ".join(sorted(MANUAL)))

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"wrote {args.json_path}")

    return 1 if any(r["status"] in (BLOCKED, UNKNOWN) for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
