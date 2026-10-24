#!/usr/bin/env python3
"""Sender DNS check (Todd's go, Oct 24, 2026, coo/DECISIONS-2026-10-24.md item 3): checkdmarc (Apache-2.0) on both sender
domains, plus a DKIM lookup, run weekly by .github/workflows/sender-dns.yml. Fails loudly: every problem is an ERROR
line and a GitHub error annotation, and the run exits 1.

ERROR: SPF missing or invalid, DMARC missing or invalid, no MX host, a nameserver error, or an expected DKIM selector
       with no key (or a revoked, empty p=).
WARN:  checkdmarc warnings, and DMARC at p=none (monitoring only; tightening it is a DNS change for Todd).

  python3 tools/sender_dns.py                 check both domains (needs DNS; the cloud sandbox has none, GitHub's runner does)
  python3 tools/sender_dns.py --selftest      planted bad results (no DMARC, broken SPF, no MX, missing or revoked DKIM)
                                              are each caught, and a good result passes; no network
  python3 tools/sender_dns.py --selftest-live a domain that cannot exist and a DKIM selector that does not exist, checked
                                              for real through checkdmarc and DNS, must both fail
"""
import argparse, base64, binascii, os, sys

# Selectors: proofnotfluff.com signs through Kit (cka, cka2: email/KIT-SETUP.md, Oct 17). getproofnotfluff.com sends from
# Google Workspace through the Apps Script sender (email/SEND_RULES.md); Workspace's default selector is "google".
DOMAINS = {"proofnotfluff.com": ["cka", "cka2"], "getproofnotfluff.com": ["google"]}
PROBE = ["google", "cka", "cka2", "default", "selector1", "selector2", "k1", "s1", "mail"]
GH = os.environ.get("GITHUB_ACTIONS") == "true"
lines = []


def say(level, name, detail=""):
    text = f"{level} {name}" + (f": {detail}" if detail else "")
    lines.append(text)
    print(text)
    if GH and level == "ERROR":
        print(f"::error title=Sender DNS::{name}: {detail}")


def judge(domain, r, dkim):
    """r: checkdmarc's result for one domain. dkim: {selector: TXT string or None}. Returns the number of errors."""
    n = 0
    def bad(part, why):
        nonlocal n
        n += 1
        say("ERROR", f"{domain} {part}", why)
    ns = r.get("ns") or {}
    if ns.get("error"):
        bad("ns", ns["error"])
    spf = r.get("spf") or {}
    if not spf.get("valid"):
        bad("spf", spf.get("error") or "no valid SPF record")
    dmarc = r.get("dmarc") or {}
    if not dmarc.get("valid"):
        bad("dmarc", dmarc.get("error") or "no valid DMARC record")
    else:
        p = ((dmarc.get("tags") or {}).get("p") or {}).get("value")
        if p == "none":
            say("WARN", f"{domain} dmarc", "policy p=none (reports only, nothing is quarantined or rejected)")
    mx = r.get("mx") or {}
    if mx.get("error") or not mx.get("hosts"):
        bad("mx", mx.get("error") or "no MX host")
    for part in ("spf", "dmarc", "mx"):
        for w in (r.get(part) or {}).get("warnings") or []:
            say("WARN", f"{domain} {part}", str(w)[:300])
    for sel, txt in dkim.items():
        if not txt:
            bad(f"dkim {sel}", f"no TXT record at {sel}._domainkey.{domain}")
            continue
        tags = dict(t.strip().split("=", 1) for t in txt.split(";") if "=" in t)
        key = tags.get("p", "").replace(" ", "")
        if not key:
            bad(f"dkim {sel}", "key is empty (p= revoked)")
            continue
        try:
            raw = base64.b64decode(key, validate=True)
        except (binascii.Error, ValueError):
            bad(f"dkim {sel}", "key is not base64")
            continue
        if tags.get("k", "rsa").strip() == "rsa" and len(raw) < 140:
            bad(f"dkim {sel}", f"RSA key under 1024 bits ({len(raw)} bytes)")
    if n == 0:
        sels = ", ".join(dkim) or "none"
        say("OK", domain, f"SPF, DMARC and MX valid; DKIM {sels}")
    return n


def dkim_lookup(domain, selectors, resolver=None):
    import dns.resolver
    res = resolver or dns.resolver.Resolver()
    res.lifetime = 10
    out = {}
    for sel in selectors:
        try:
            ans = res.resolve(f"{sel}._domainkey.{domain}", "TXT")
            out[sel] = " ".join(b"".join(r.strings).decode("utf-8", "replace") for r in ans)
        except Exception:   # NXDOMAIN, NoAnswer, timeout: no key
            out[sel] = None
    return out


def check(domains):
    import checkdmarc
    errors = 0
    for d, sels in domains.items():
        try:
            r = checkdmarc.check_domains([d], timeout=6.0, retries=2)
        except Exception as e:   # checkdmarc gave up on the domain: every part counts as missing
            say("WARN", f"{d} checkdmarc", f"{type(e).__name__}: {str(e)[:200]}")
            r = {}
        if isinstance(r, list):
            r = r[0]
        errors += judge(d, r, dkim_lookup(d, sels))
        extra = [s for s, t in dkim_lookup(d, [s for s in PROBE if s not in sels]).items() if t]
        if extra:
            say("WARN", f"{d} dkim", f"keys also published at selectors {', '.join(extra)} (not checked as required)")
    return errors


GOOD_KEY = base64.b64encode(bytes(range(256)) + bytes(38)).decode()   # 294 bytes, the size of a 2048-bit RSA public key
GOOD = {"ns": {"hostnames": ["a.ns"]}, "spf": {"valid": True, "record": "v=spf1 include:_spf.example ~all", "warnings": []},
        "dmarc": {"valid": True, "record": "v=DMARC1; p=quarantine", "tags": {"p": {"value": "quarantine"}}, "warnings": []},
        "mx": {"hosts": [{"hostname": "mx.example", "preference": 10}], "warnings": []}}


def selftest():
    import copy
    good_dkim = {"cka": f"v=DKIM1; k=rsa; p={GOOD_KEY}"}
    cases = []
    def case(name, mutate=None, dkim=None, want_errors=1):
        r = copy.deepcopy(GOOD)
        if mutate:
            mutate(r)
        cases.append((name, r, good_dkim if dkim is None else dkim, want_errors))
    case("a good domain passes", want_errors=0)
    case("p=none is a warning, not an error", lambda r: r["dmarc"]["tags"]["p"].update(value="none"), want_errors=0)
    case("no DMARC record", lambda r: r.update(dmarc={"valid": False, "error": "A DMARC record does not exist", "warnings": []}))
    case("broken SPF", lambda r: r.update(spf={"valid": False, "error": "too many DNS lookups", "warnings": []}))
    case("no SPF key at all", lambda r: r.pop("spf"))
    case("no MX host", lambda r: r.update(mx={"hosts": [], "warnings": []}))
    case("MX lookup error", lambda r: r.update(mx={"error": "NXDOMAIN", "hosts": []}))
    case("nameserver error", lambda r: r.update(ns={"error": "no nameservers"}))
    case("DKIM selector missing", dkim={"cka": None})
    case("DKIM key revoked", dkim={"cka": "v=DKIM1; k=rsa; p="})
    case("DKIM key not base64", dkim={"cka": "v=DKIM1; k=rsa; p=@@@@"})
    case("DKIM key too short", dkim={"cka": "v=DKIM1; k=rsa; p=" + base64.b64encode(bytes(60)).decode()})
    case("two failures count twice", lambda r: r.update(spf={"valid": False}, dmarc={"valid": False}), want_errors=2)
    wrong = []
    global lines
    saved, lines = lines, []
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        for name, r, dkim, want in cases:
            if judge("planted.example", r, dkim) != want:
                wrong.append(name)
    lines = saved
    if wrong:
        say("ERROR", "sender-dns-selftest", "wrong verdict on: " + "; ".join(wrong))
        return 1
    say("OK", "sender-dns-selftest", f"{len(cases)} planted results judged right ({sum(1 for c in cases if c[3])} failures caught)")
    return 0


def selftest_live():
    import io, contextlib
    global lines
    saved, lines = lines, []
    with contextlib.redirect_stdout(io.StringIO()):
        e1 = check({"pnf-planted-nonexistent.invalid": []})
        e2 = judge("proofnotfluff.com", GOOD, dkim_lookup("proofnotfluff.com", ["pnf-planted-missing"]))
        e3 = judge("proofnotfluff.com", GOOD, dkim_lookup("proofnotfluff.com", ["cka"]))   # control: a real key passes
    lines = saved
    if e1 < 2 or e2 != 1 or e3 != 0:
        say("ERROR", "sender-dns-selftest-live", f"planted bad domain {e1} errors (want 2 or more), missing selector {e2} "
            f"(want 1), real Kit key {e3} (want 0; if this fails, DNS is not answering and nothing below can be trusted)")
        return 1
    say("OK", "sender-dns-selftest-live", f"live checkdmarc failed the planted domain ({e1} errors) and the missing DKIM "
        "selector, and passed the real Kit key")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--selftest-live", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.selftest_live:
        sys.exit(selftest_live())
    errors = check(DOMAINS)
    print(f"sender_dns: {errors} errors")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
