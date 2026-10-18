#!/usr/bin/env python3
"""Domain availability checker for the namesmith skill.

Four rules this script exists to enforce.

1. Never bare DNS for availability. A registered-but-unhosted domain returns
   NXDOMAIN and would misreport as free. DNS is used here only as a one-way
   TAKEN proof: NS records present means registered, full stop. Absence of NS
   proves nothing and is never reported as free.

2. A 404 from a resolver that has no RDAP service for that TLD is not an
   answer. rdap.org returns a bare, bodyless 404 both for "domain not found"
   and for "I have no server for .io" -- indistinguishable. v1 of this script
   read that as FREE, which silently reported every .io and .co candidate as
   available. This version resolves the TLD to a verified registry RDAP
   endpoint and never treats an unmapped TLD as free.

3. When RDAP is missing or throttled, fall through to port-43 WHOIS with the
   server discovered from whois.iana.org. .pl RDAP hard-429s from outside a
   registrar; .co and .eu publish no RDAP at all. All three answer WHOIS
   cleanly. Without this layer a third of a European sweep is unanswerable.

4. Anything unresolved is UNVERIFIED or UNSUPPORTED, and the process exits
   non-zero. A caller must not be able to mistake an incomplete sweep for a
   clean one.

Ladder per domain:  DNS NS  ->  registry RDAP  ->  port-43 WHOIS  ->  UNVERIFIED

Usage:
    python check_domains.py --names ritka karbia zyla --tlds com pl io ai
    python check_domains.py --names ritka --tlds com pl io ai co eu app dev \
        --csv out.csv --json out.json
    python check_domains.py --tld-report --tlds com pl io co eu de me au com.au
"""

import argparse
import csv
import json
import os
import re
import socket
import ssl
import sys
import threading
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IANA_BOOTSTRAP = "https://data.iana.org/rdap/dns.json"
CACHE_PATH = os.path.join(HERE, ".rdap-bootstrap.json")
WHOIS_CACHE = os.path.join(HERE, ".whois-servers.json")
CACHE_MAX_AGE = 7 * 24 * 3600  # a week; the registry moves slowly

# ccTLDs the IANA bootstrap does not carry. Every entry was probed against a
# known-registered and a known-free domain before being added: taken -> 200,
# free -> 404. Do not add a TLD here on documentation alone -- verify both
# directions, or leave it out and let the WHOIS layer handle it.
RDAP_EXTRAS = {
    "io": "https://rdap.identitydigital.services/rdap",   # github.io 200 / free 404
    "me": "https://rdap.identitydigital.services/rdap",   # about.me 200
    "sh": "https://rdap.identitydigital.services/rdap",   # nic.sh 200
    "ac": "https://rdap.identitydigital.services/rdap",
    "de": "https://rdap.denic.de",                        # denic.de 200
}

# Registries whose RDAP is present but unusable from a normal IP. Skip straight
# to WHOIS rather than burning three retries and a minute of backoff.
RDAP_SKIP = {"pl"}  # rdap.dns.pl hard-429s every request from outside a registrar

# Verified port-43 servers. Anything not listed is discovered from IANA.
WHOIS_EXTRAS = {
    "co": "whois.registry.co",   # whois.nic.co does not resolve
}

FREE, TAKEN, UNVERIFIED, UNSUPPORTED = "FREE", "taken", "UNVERIFIED", "UNSUPPORTED"

# Case-insensitive substrings that mean "this domain is not registered".
NOT_FOUND = [
    "no match", "not found", "no data found", "no entries found",
    "no object found", "nothing found", "does not exist",
    "no information available about domain name",
    "status: available", "status:      available", "status: free",
    "available for registration", "not registered", "no such domain",
    "domain status: no object found",
]
# Substrings that mean the server refused rather than answered.
THROTTLED = [
    "rate limit", "quota exceeded", "exceeded", "too many requests",
    "try again later", "access denied", "connection refused by",
]
# Fields that cannot appear unless a registration exists. Checked BEFORE the
# not-found list, so a stray "not found" inside a registrar disclaimer can
# never turn a live domain into a FREE result.
STRONG_REGISTERED = [
    "creation date:", "registry domain id:", "registrar iana id:",
    "registry expiry date:", "expiration date:", "registered:", "created:",
]
# Weaker markers -- a record shape, but only trusted after the not-found pass.
WEAK_REGISTERED = [
    "domain name:", "domain:", "registrar:", "nameservers:", "name servers:",
    "registrant type:", "sponsoring registrar",
]

_ctx = ssl.create_default_context()
_UA = {"User-Agent": "namesmith/2.0", "Accept": "application/rdap+json"}


# --------------------------------------------------------------------------
# TLD -> endpoint resolution

def _load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_json(path, obj):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1)
    except Exception:
        pass


def load_bootstrap(refresh=False):
    """Return {tld: rdap_base_url} from the IANA bootstrap, cached weekly."""
    fresh = (os.path.exists(CACHE_PATH)
             and (time.time() - os.path.getmtime(CACHE_PATH)) < CACHE_MAX_AGE)
    if refresh or not fresh:
        try:
            req = urllib.request.Request(IANA_BOOTSTRAP, headers=_UA)
            with urllib.request.urlopen(req, timeout=30, context=_ctx) as r:
                data = r.read()
            with open(CACHE_PATH, "wb") as fh:
                fh.write(data)
        except Exception as e:
            if not os.path.exists(CACHE_PATH):
                print(f"! IANA bootstrap unreachable ({e}); RDAP limited to "
                      f"the built-in map", file=sys.stderr)
                return {}
            print(f"! bootstrap refresh failed ({e}); using cache",
                  file=sys.stderr)

    doc = _load_json(CACHE_PATH)
    out = {}
    for entry in doc.get("services", []):
        tlds, urls = entry[0], entry[1]
        base = next((u for u in urls if u.startswith("https://")), urls[0])
        for t in tlds:
            out[t.lower().lstrip(".")] = base.rstrip("/")
    return out


def resolve_rdap(tld, bootstrap):
    """RDAP base for a TLD, honouring multi-label TLDs like com.au."""
    tld = tld.lower().lstrip(".")
    for cand in (tld, tld.split(".")[-1]):
        if cand in RDAP_SKIP:
            return None
        if cand in RDAP_EXTRAS:
            return RDAP_EXTRAS[cand]
        if cand in bootstrap:
            return bootstrap[cand]
    return None


def resolve_whois(tld, cache):
    """Port-43 server for a TLD, discovered from whois.iana.org and cached."""
    root = tld.lower().lstrip(".").split(".")[-1]
    if root in WHOIS_EXTRAS:
        return WHOIS_EXTRAS[root]
    if root in cache:
        return cache[root] or None
    reply = whois_query("whois.iana.org", root, timeout=12)
    # [ \t]* not \s*: an empty "whois:" line (.app, .dev) must not capture the
    # next line's "status:" as a server name
    m = re.search(r"^whois:[ \t]*(\S+)", reply or "", re.M)
    server = m.group(1) if m else None
    cache[root] = server or ""
    _save_json(WHOIS_CACHE, cache)
    return server


# --------------------------------------------------------------------------
# probes

_warned_no_dns = False


def dns_has_ns(domain):
    """True only if the domain demonstrably has NS records -> registered."""
    global _warned_no_dns
    try:
        import dns.resolver
    except ImportError:
        # a fresh machine without dnspython loses this rung; say so once
        if not _warned_no_dns:
            _warned_no_dns = True
            print("! dnspython not installed; skipping the DNS rung "
                  "(pip install dnspython)", file=sys.stderr)
        return False
    try:
        return len(dns.resolver.resolve(domain, "NS", lifetime=5)) > 0
    except Exception:
        return False


def rdap_probe(base, domain, timeout=20):
    url = f"{base}/domain/{domain}"
    req = urllib.request.Request(url, headers=_UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_ctx) as r:
            return r.status, r.read(4096)
    except urllib.error.HTTPError as e:
        try:
            return e.code, e.read(2048)
        except Exception:
            return e.code, b""
    except Exception as e:
        return type(e).__name__, b""


def whois_query(server, query, timeout=15):
    try:
        s = socket.create_connection((server, 43), timeout=timeout)
        s.sendall((query + "\r\n").encode())
        chunks = []
        while True:
            d = s.recv(8192)
            if not d:
                break
            chunks.append(d)
        s.close()
        return b"".join(chunks).decode("utf-8", "replace")
    except Exception:
        return None


def read_whois(text):
    """Classify a WHOIS body. Returns (status, detail).

    Order matters and is the whole safety argument: throttling first (a refusal
    is not an answer), then fields that can only exist on a live registration,
    then the not-found vocabulary, then weak record shape. Reversing the middle
    two turns a disclaimer containing "not found" into a false FREE.
    """
    if text is None:
        return UNVERIFIED, "whois unreachable"
    low = text.lower()
    # strip server comments/disclaimers before looking for record fields
    body = "\n".join(l for l in text.splitlines()
                     if l.strip() and not l.lstrip().startswith(("%", "#", ">>>")))
    blow = body.lower()

    for pat in THROTTLED:
        if pat in low:
            return UNVERIFIED, f"whois throttled: '{pat}'"
    for pat in STRONG_REGISTERED:
        if pat in blow:
            return TAKEN, f"whois: '{pat}'"
    for pat in NOT_FOUND:
        if pat in blow:
            return FREE, f"whois: '{pat}'"
    for pat in NOT_FOUND:            # some servers answer only in a comment
        if pat in low:
            return FREE, f"whois comment: '{pat}'"
    for pat in WEAK_REGISTERED:
        if pat in blow:
            return TAKEN, "whois record present"
    return UNVERIFIED, "whois reply unparsed"


# --------------------------------------------------------------------------
# the ladder

def check_one(domain, tld, rdap_base, whois_server, attempts=2, base_sleep=5.0):
    if dns_has_ns(domain):
        return TAKEN, "NS records present", "dns"

    if rdap_base:
        last = None
        for attempt in range(attempts):
            code, body = rdap_probe(rdap_base, domain)
            last = code
            if code == 404:
                return FREE, "rdap 404", "rdap"
            if code == 200:
                if b'"errorCode"' in body and b"404" in body:
                    return FREE, "rdap 200/errorCode 404", "rdap"
                return TAKEN, "rdap 200", "rdap"
            if code in (400, 422):
                break  # malformed for this registry; try whois
            if attempt < attempts - 1:
                time.sleep(base_sleep * (attempt + 1))
        rdap_note = f"rdap inconclusive ({last})"
    else:
        rdap_note = "no rdap"

    if whois_server:
        status, detail = read_whois(whois_query(whois_server, domain))
        if status in (FREE, TAKEN):
            return status, f"{detail} [{rdap_note}]", "whois"
        return UNVERIFIED, f"{detail} [{rdap_note}]", "whois"

    if not rdap_base:
        return UNSUPPORTED, "no rdap endpoint and no whois server", "none"
    return UNVERIFIED, rdap_note, "rdap"


def run(jobs, per_host_sleep, attempts):
    """One worker per endpoint host: registries run in parallel, none hammered."""
    by_host, results, lock = {}, [], threading.Lock()
    for job in jobs:
        host = (re.sub(r"^https?://([^/]+).*$", r"\1", job["rdap"])
                if job["rdap"] else (job["whois"] or "none"))
        by_host.setdefault(host, []).append(job)

    def worker(items):
        for i, job in enumerate(items):
            status, detail, source = check_one(
                job["domain"], job["tld"], job["rdap"], job["whois"],
                attempts=attempts)
            job.update(status=status, detail=detail, source=source)
            with lock:
                results.append(job)
                flag = "*" if status == FREE else " "
                print(f"{flag} {job['domain']:<26} {status:<12} {source:<6} "
                      f"{detail}", flush=True)
            if source in ("rdap", "whois") and i < len(items) - 1:
                time.sleep(per_host_sleep)

    threads = [threading.Thread(target=worker, args=(it,), daemon=True)
               for it in by_host.values()]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return results


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--names", nargs="+", help="candidate names, bare")
    ap.add_argument("--tlds", nargs="+", default=["com"], help="TLDs to check")
    ap.add_argument("--sleep", type=float, default=2.0,
                    help="seconds between calls to the SAME endpoint")
    ap.add_argument("--attempts", type=int, default=2)
    ap.add_argument("--csv")
    ap.add_argument("--json", dest="json_path")
    ap.add_argument("--refresh-bootstrap", action="store_true")
    ap.add_argument("--tld-report", action="store_true",
                    help="show how each TLD will be resolved, then exit")
    args = ap.parse_args()

    bootstrap = load_bootstrap(refresh=args.refresh_bootstrap)
    wcache = _load_json(WHOIS_CACHE)

    if args.tld_report:
        print(f"{'tld':<10} {'rdap':<48} whois")
        for tld in args.tlds:
            print(f"{tld:<10} {str(resolve_rdap(tld, bootstrap) or '-'):<48} "
                  f"{resolve_whois(tld, wcache) or '-'}")
        return 0

    if not args.names:
        ap.error("--names is required unless --tld-report is used")

    jobs = [{"name": n, "tld": t, "domain": f"{n}.{t}",
             "rdap": resolve_rdap(t, bootstrap),
             "whois": resolve_whois(t, wcache)}
            for n in args.names for t in args.tlds]

    blind = sorted({j["tld"] for j in jobs if not j["rdap"] and not j["whois"]})
    if blind:
        print(f"! no endpoint at all for: {', '.join(blind)} -- these report "
              f"UNSUPPORTED, never FREE. Check them at a registrar by hand.\n")

    t0 = time.time()
    results = run(jobs, args.sleep, args.attempts)
    results.sort(key=lambda r: (args.names.index(r["name"]),
                                args.tlds.index(r["tld"])))

    free = [r["domain"] for r in results if r["status"] == FREE]
    unver = [r["domain"] for r in results if r["status"] == UNVERIFIED]
    unsup = [r["domain"] for r in results if r["status"] == UNSUPPORTED]

    print(f"\n--- summary ({len(results)} lookups in {time.time() - t0:.0f}s) ---")
    print(f"FREE ({len(free)}): {', '.join(free) or 'none'}")
    if unver:
        print(f"UNVERIFIED ({len(unver)}): {', '.join(unver)}")
        print("  ^ NOT available. Re-run before reporting.")
    if unsup:
        print(f"UNSUPPORTED ({len(unsup)}): {', '.join(unsup)}")
        print("  ^ no endpoint for that TLD. NOT a free result.")

    if args.csv:
        with open(args.csv, "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, extrasaction="ignore",
                               fieldnames=["name", "tld", "domain", "status",
                                           "source", "detail"])
            w.writeheader()
            w.writerows(results)
        print(f"\nwrote {args.csv}")
    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as fh:
            json.dump(results, fh, indent=2)
        print(f"wrote {args.json_path}")

    return 1 if (unver or unsup) else 0


if __name__ == "__main__":
    sys.exit(main())
