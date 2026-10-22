#!/usr/bin/env python3
"""Handle availability checker for the namesmith skill.

Three rules this script exists to enforce.

1. A domain alone is not a name. A candidate whose GitHub org, npm package
   and YouTube handle are all held by strangers is a candidate with a
   permanent search problem, whatever its .com says.

2. Every platform is read by its own positive signal. "The request didn't
   fail" is not "free". Each probe below names the exact response that means
   TAKEN and the exact response that means FREE; anything else -- a 403, a
   429, a consent redirect, a page shape we do not recognise -- is UNVERIFIED.

3. Platforms that cannot be checked without logging in, or whose terms forbid
   scripted lookups, are listed as MANUAL and printed as MANUAL. They are
   never silently skipped and never reported as clear. The process exits
   non-zero while anything is UNVERIFIED, so a partial sweep cannot be handed
   over as a clean one.

Usage:
    python check_handles.py --names ritka karbia
    python check_handles.py --names ritka --json handles.json
    python check_handles.py --names ritka --only github npm pypi
    python check_handles.py --list
"""

import argparse
import json
import re
import ssl
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

UA = "namesmith-handle-check/1.0 (+https://github.com/; availability research)"

# Older Python/OpenSSL builds ship a CA store that predates newer Let's
# Encrypt chains (Docker Hub fails verification on OpenSSL 1.1.1n while the
# cert is valid). Prefer certifi's bundle when it is installed.
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()

TAKEN, FREE, UNVERIFIED, INVALID = "taken", "FREE", "UNVERIFIED", "INVALID"


def fetch(url, timeout=20, accept="application/json"):
    """Return (status, final_url, body). Network failure -> (None, url, str(err))."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            return r.status, r.geturl(), r.read(400_000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            body = e.read(50_000).decode("utf-8", "replace")
        except Exception:
            body = ""
        return e.code, url, body
    except Exception as e:  # timeout, DNS, TLS
        return None, url, f"{type(e).__name__}: {e}"


def by_status(status, taken=(200,), free=(404,)):
    if status in taken:
        return TAKEN, ""
    if status in free:
        return FREE, ""
    return UNVERIFIED, f"HTTP {status}" if status else "no response"


# --- probes: each returns (status, note) ----------------------------------

def p_github(n):
    # Users and orgs share one namespace; /users/ answers for both.
    s, _, _ = fetch(f"https://api.github.com/users/{n}")
    st, note = by_status(s)
    if s == 403:
        note = "rate-limited (60/h unauthenticated)"
    return st, note


def p_npm(n):
    s, _, _ = fetch(f"https://registry.npmjs.org/{n.lower()}")
    st, note = by_status(s)
    if st == FREE:
        note = "npm also blocks names too similar to existing ones; FREE here is not a publish guarantee"
    return st, note


def p_pypi(n):
    norm = re.sub(r"[-_.]+", "-", n).lower()  # PEP 503
    s, _, _ = fetch(f"https://pypi.org/pypi/{norm}/json")
    st, note = by_status(s)
    if st == FREE:
        note = "PyPI may still refuse names that collide after normalisation or are prohibited"
    return st, note


def p_crates(n):
    s, _, _ = fetch(f"https://crates.io/api/v1/crates/{n.lower()}")
    return by_status(s)


def p_dockerhub(n):
    s, _, _ = fetch(f"https://hub.docker.com/v2/users/{n.lower()}/")
    if s == 200:
        return TAKEN, "user"
    if s in (301, 308):  # Docker Hub redirects /users/<org> to /orgs/<org>
        return TAKEN, "organisation"
    if s != 404:
        return by_status(s)
    s2, _, _ = fetch(f"https://hub.docker.com/v2/orgs/{n.lower()}/")
    if s2 == 200:
        return TAKEN, "organisation"
    if s2 == 404:
        return FREE, ""
    return UNVERIFIED, f"user 404, org lookup HTTP {s2}"


def p_huggingface(n):
    s, _, _ = fetch(f"https://huggingface.co/api/users/{n}/overview")
    if s == 200:
        return TAKEN, "user"
    s2, _, _ = fetch(f"https://huggingface.co/api/organizations/{n}/overview")
    if s2 == 200:
        return TAKEN, "organisation"
    if s in (404,) and s2 in (404,):
        return FREE, ""
    return UNVERIFIED, f"user HTTP {s}, org HTTP {s2}"


def p_youtube(n):
    s, final, body = fetch(f"https://www.youtube.com/@{n}", accept="text/html")
    if "consent." in (final or ""):
        return UNVERIFIED, "redirected to cookie consent (EU); check manually"
    if s == 200:
        return TAKEN, ""
    if s == 404:
        return FREE, ""
    return by_status(s)


def p_telegram(n):
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{4,31}", n):
        return INVALID, "Telegram usernames are 5-32 chars, start with a letter"
    s, _, body = fetch(f"https://t.me/{n}", accept="text/html")
    if s != 200:
        return by_status(s)
    # t.me answers 200 for everything. An existing user/channel/bot renders
    # a title block; a free name renders the bare "contact" landing page.
    if 'class="tgme_page_title"' in body:
        return TAKEN, ""
    if "tgme_page" in body:
        return FREE, "no public profile; a private account could still hold it"
    return UNVERIFIED, "unrecognised page shape"


def p_bluesky(n):
    handle = f"{n.lower()}.bsky.social"
    q = urllib.parse.urlencode({"handle": handle})
    s, _, body = fetch(f"https://public.api.bsky.app/xrpc/com.atproto.identity.resolveHandle?{q}")
    if s == 200:
        return TAKEN, handle
    if s == 400 and "resolve handle" in body.lower():
        return FREE, handle
    return UNVERIFIED, f"HTTP {s}"


def p_gitlab(n):
    s, _, body = fetch(f"https://gitlab.com/api/v4/users?username={urllib.parse.quote(n)}")
    if s != 200:
        return by_status(s)
    try:
        if json.loads(body):
            return TAKEN, "user"
    except ValueError:
        return UNVERIFIED, "unparseable user response"
    s2, _, _ = fetch(f"https://gitlab.com/api/v4/groups/{urllib.parse.quote(n)}")
    if s2 == 200:
        return TAKEN, "group"
    if s2 == 404:
        return FREE, "no user or public group; a private group could still hold it"
    return UNVERIFIED, f"group lookup HTTP {s2}"


def p_reddit_user(n):
    s, _, _ = fetch(f"https://www.reddit.com/user/{n}/about.json")
    st, note = by_status(s)
    if s in (403, 429):
        note = "Reddit blocks unauthenticated scripts often; check manually"
    return st, note


def p_subreddit(n):
    s, final, body = fetch(f"https://www.reddit.com/r/{n}/about.json")
    if s == 200 and '"kind": "t5"' in body.replace('":"', '": "'):
        return TAKEN, ""
    if s == 404 or (s == 200 and "search" in (final or "")):
        return FREE, ""
    st, note = by_status(s)
    if s in (403, 429):
        note = "Reddit blocks unauthenticated scripts often; check manually"
    return st, note


PROBES = {
    "github": ("GitHub user/org", p_github),
    "npm": ("npm package", p_npm),
    "pypi": ("PyPI package", p_pypi),
    "crates": ("crates.io crate", p_crates),
    "dockerhub": ("Docker Hub namespace", p_dockerhub),
    "huggingface": ("Hugging Face user/org", p_huggingface),
    "youtube": ("YouTube @handle", p_youtube),
    "telegram": ("Telegram username", p_telegram),
    "bluesky": ("Bluesky .bsky.social", p_bluesky),
    "gitlab": ("GitLab user/group", p_gitlab),
    "reddit": ("Reddit user", p_reddit_user),
    "subreddit": ("Reddit r/", p_subreddit),
}

# Login walls, or terms that forbid scripted lookups. Printed, never skipped.
MANUAL = {
    "x": "x.com/<name> -- login wall; check in a browser",
    "instagram": "instagram.com/<name> -- login wall",
    "tiktok": "tiktok.com/@<name> -- bot protection",
    "linkedin": "linkedin.com/company/<name> -- login wall; the company slug is first-come",
    "producthunt": "producthunt.com/@<name> and /products/<name>",
    "appstore": "App Store / Google Play developer and app name -- search both stores",
    "threads": "threads.net/@<name> -- tied to the Instagram handle",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", nargs="+")
    ap.add_argument("--only", nargs="+", choices=sorted(PROBES), help="subset of platforms")
    ap.add_argument("--json", help="write results to this file")
    ap.add_argument("--sleep", type=float, default=1.0, help="pause between calls to one platform")
    ap.add_argument("--list", action="store_true", help="show automated vs manual platforms")
    a = ap.parse_args()

    if a.list:
        print("AUTOMATED")
        for k, (label, _) in PROBES.items():
            print(f"  {k:<12} {label}")
        print("MANUAL (always printed in the report as MANUAL, never as clear)")
        for k, v in MANUAL.items():
            print(f"  {k:<12} {v}")
        return 0
    if not a.names:
        ap.error("--names is required (or use --list)")

    platforms = a.only or list(PROBES)
    results = {n: {} for n in a.names}
    lock = threading.Lock()

    def worker(platform):
        fn = PROBES[platform][1]
        for i, n in enumerate(a.names):
            if i:
                time.sleep(a.sleep)
            try:
                st, note = fn(n)
            except Exception as e:  # a probe bug must not read as FREE
                st, note = UNVERIFIED, f"probe error: {type(e).__name__}: {e}"
            with lock:
                results[n][platform] = {"status": st, "note": note}

    # One thread per platform: parallel across hosts, polite within each.
    threads = [threading.Thread(target=worker, args=(p,)) for p in platforms]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    unresolved = 0
    for n in a.names:
        row = results[n]
        free = sum(1 for p in platforms if row[p]["status"] == FREE)
        print(f"\n{n}   {free}/{len(platforms)} automated handles free")
        for p in platforms:
            r = row[p]
            if r["status"] == UNVERIFIED:
                unresolved += 1
            note = f"  ({r['note']})" if r["note"] else ""
            print(f"  {PROBES[p][0]:<24} {r['status']}{note}")
        for k, v in MANUAL.items():
            print(f"  {k:<24} MANUAL  {v.replace('<name>', n)}")
        row["_manual"] = {k: v.replace("<name>", n) for k, v in MANUAL.items()}

    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

    if unresolved:
        print(f"\n{unresolved} check(s) UNVERIFIED -- this sweep is not complete.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
