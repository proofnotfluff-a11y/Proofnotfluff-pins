#!/usr/bin/env python3
"""Addresses a business publishes on its own website (rung 2 of the enrichment ladder, Todd, Oct 22, 2026).

Runs inside GitHub Actions (tools/enrich_ci.py). Reads a handful of the business's own pages (home, contact, about),
collects mailto links, plain addresses and Cloudflare-protected addresses, and keeps only addresses on the business's
own domain. choose() then picks the address for a named owner, in this order:
  1. a published address whose local part carries the owner's name (dana@, dreyes@, dana.reyes@)
  2. a published owner-read inbox (info@, office@ ... pnf_rules.OWNER_READ_ROLES), allowed only for an owner named
     by the City's owner record or the business's own site (pnf_rules.owner_read_inbox)
  3. nothing: a guessed address is never stored, it would cost a Bouncer credit for a likely bounce
Every address chosen here leaves with email_status "unverified"; the outreach run checks it with Bouncer before any
draft. Nothing is printed except counts.

Usage as a library: site_emails.collect(domain) -> sorted list of addresses; site_emails.choose(addresses, domain, owner)
       python3 tools/site_emails.py --selftest
"""
import os
import re
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

PATHS = ("", "contact", "contact-us", "about", "about-us")
UA = {"User-Agent": "Mozilla/5.0 (compatible; ProofNotFluff prospect check; one visit per page)"}
ADDR = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
CF = re.compile(r'data-cfemail="([0-9a-fA-F]+)"|/cdn-cgi/l/email-protection#([0-9a-fA-F]+)')
ROLE_ORDER = ["info", "office", "contact", "hello", "admin", "mail", "general", "inquiries", "inquiry", "sales", "team"]
JUNK = re.compile(r"\.(?:png|jpe?g|gif|webp|svg|css|js)$|^(?:example|email|name|your|you|user)@|sentry|wixpress|godaddy", re.I)


def cf_decode(hexstr):
    try:
        key = int(hexstr[:2], 16)
        return "".join(chr(int(hexstr[i:i + 2], 16) ^ key) for i in range(2, len(hexstr), 2))
    except ValueError:
        return ""


def extract(html, domain):
    """On-domain addresses in one page's HTML."""
    found = set(ADDR.findall(html or ""))
    for a, b in CF.findall(html or ""):
        found.add(cf_decode(a or b))
    out = set()
    for e in found:
        e = e.strip().strip(".").lower()
        if not R.EMAIL_RE.match(e) or JUNK.search(e):
            continue
        dom = e.split("@", 1)[1]
        if dom == domain or dom.endswith("." + domain):
            out.add(e)
    return out


def collect(domain, opener=None, pause=1.0, timeout=20):
    opener = opener or urllib.request.urlopen
    out = set()
    for path in PATHS:
        url = f"https://{domain}/{path}"
        try:
            with opener(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                out |= extract(r.read(600000).decode("utf-8", "replace"), domain)
        except Exception:
            pass   # a missing page is normal; the business simply has fewer pages
        time.sleep(pause)
    return sorted(out)


def choose(addresses, domain, owner, owner_source):
    """(address, kind) for the named owner, or (None, reason)."""
    first, last = owner.get("first_name", ""), owner.get("last_name", "")
    personal = [e for e in addresses if not R.inbox_problems(e, domain, first, last)]
    if personal:
        return personal[0], "personal"
    roles = [e for e in addresses if R.owner_read_inbox(e, owner_source, "site")
             and not R.inbox_problems(e, domain, first, last, owner_source, "site")]
    roles.sort(key=lambda e: ROLE_ORDER.index(e.split("@")[0]) if e.split("@")[0] in ROLE_ORDER else 99)
    if roles:
        return roles[0], "owner-read inbox"
    return None, "no usable address on the site"


def selftest():
    bad = []

    def check(name, got, want):
        if got != want:
            bad.append(f"{name}: got {got!r}, want {want!r}")

    html = ('<a href="mailto:Dana@SparkleCo.example">x</a> info@sparkleco.example jobs@sparkleco.example '
            'logo@2x.png someone@gmail.com x@other.example <span data-cfemail="0f6b6e616e4f7c7f6e7d64636a6c60216a776e627f636a"></span>')
    got = extract(html, "sparkleco.example")
    check("on-domain only, junk and other domains dropped", sorted(got),
          ["dana@sparkleco.example", "info@sparkleco.example", "jobs@sparkleco.example"])
    check("cloudflare-only address found", extract('<a href="/cdn-cgi/l/email-protection#0f6b6e616e4f7c7f6e7d64636a6c60216a776e627f636a">',
                                                   "sparkleco.example"), {"dana@sparkleco.example"})
    check("cloudflare address decoded", cf_decode("0f6b6e616e4f7c7f6e7d64636a6c60216a776e627f636a"), "dana@sparkleco.example")
    owner = {"first_name": "Dana", "last_name": "Reyes"}
    check("personal address wins", choose(["dana@sparkleco.example", "info@sparkleco.example"], "sparkleco.example", owner,
                                          "city_owner_record"), ("dana@sparkleco.example", "personal"))
    check("owner-read inbox for a City-named owner", choose(["info@sparkleco.example", "jobs@sparkleco.example"], "sparkleco.example",
                                                           owner, "city_owner_record"), ("info@sparkleco.example", "owner-read inbox"))
    check("no owner-read inbox for a Hunter-named owner", choose(["info@sparkleco.example"], "sparkleco.example", owner, "hunter")[0], None)
    check("jobs@ is never an owner's inbox", choose(["jobs@sparkleco.example"], "sparkleco.example", owner, "city_owner_record")[0], None)
    check("someone else's address is not the owner's", choose(["sam@sparkleco.example"], "sparkleco.example", owner, "site_about")[0], None)
    if bad:
        for b in bad:
            print(f"ERROR site_emails selftest: {b}")
        sys.exit(1)
    print("site_emails selftest: PASS 8 checks")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(__doc__)
