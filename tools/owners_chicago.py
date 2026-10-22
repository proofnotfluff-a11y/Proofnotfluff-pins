#!/usr/bin/env python3
"""Owner names for Chicago prospects from the City's own records (rung 1 of the enrichment ladder, Todd, Oct 22, 2026).

Runs inside GitHub Actions only (tools/enrich_ci.py), because the cloud sandbox cannot reach data.cityofchicago.org.
Two public datasets on the City of Chicago Data Portal:
  r5kz-chrr  Business Licenses: legal_name, doing_business_as_name, account_number, license_status
  ezma-pppn  Business Owners:   account_number, owner_first_name, owner_last_name, owner_title (one row per owner)
A business from prospects/businesses.json matches a license account only when its name, normalized (case, punctuation,
"and", corporate suffixes), equals the account's legal or doing-business-as name exactly. No fuzzy match: a wrong owner
is worse than none. The owner is the first person (not a company) whose title is a decision-maker role, in TITLE_RANK
order. Names are personal data: they stay in the runner and leave it only inside the sealed box; nothing is printed.

Usage as a library: owners_chicago.find(businesses) -> {website_domain: {"first_name", "last_name", "title", "account"}}
       python3 tools/owners_chicago.py --selftest
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

PORTAL = "https://data.cityofchicago.org"
LICENSES, OWNERS = "r5kz-chrr", "ezma-pppn"
SUFFIX = re.compile(r"\b(?:INC|INCORPORATED|LLC|L L C|LTD|CO|CORP|CORPORATION|COMPANY|THE|PLLC|LLP|LP|ENTERPRISES?)\b")
STOP = {"CLEANING", "SERVICES", "SERVICE", "CHICAGO", "COMMERCIAL", "JANITORIAL", "MAIDS", "MAID", "AND", "OF", "GROUP",
        "SOLUTIONS", "BUILDING", "THE", "PRO", "PROS", "CLEAN", "CLEANERS", "COMPANY"}
# City titles, best first, and the title we store (it must pass pnf_rules.DECISION_TITLE)
TITLE_RANK = [("SOLE PROPRIETOR", "Owner"), ("OWNER", "Owner"), ("PRESIDENT", "President"), ("CEO", "CEO"),
              ("CHIEF EXECUTIVE OFFICER", "CEO"), ("MANAGING MEMBER", "Managing Member"), ("MANAGING PARTNER", "Managing Partner"),
              ("PARTNER", "Partner"), ("PRINCIPAL", "Principal"), ("MEMBER", "Owner")]


def norm(name):
    s = (name or "").upper().replace("&", " AND ")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    s = SUFFIX.sub(" ", s)
    return re.sub(r"\s+", " ", s).strip()


def key_token(name):
    """The longest distinctive word of the name, used only to narrow the portal query."""
    words = [w for w in norm(name).split() if w not in STOP and len(w) >= 3]
    return max(words, key=len) if words else ""


def title_of(raw):
    t = re.sub(r"\s+", " ", (raw or "").upper()).strip()
    for city, ours in TITLE_RANK:
        if t == city:
            return ours
    return ""


def pick_owner(rows):
    """The best person among one account's owner rows, or None."""
    best = None
    for r in rows:
        first = (r.get("owner_first_name") or "").strip().title()
        last = (r.get("owner_last_name") or "").strip().title()
        raw = re.sub(r"\s+", " ", (r.get("owner_title") or "").upper()).strip()
        title = title_of(raw)
        if not (first and last and title) or not R.NAME_RE.match(first) or not R.NAME_RE.match(last):
            continue
        rank = next(i for i, (city, _) in enumerate(TITLE_RANK) if city == raw)
        if best is None or rank < best[0]:
            best = (rank, {"first_name": first, "last_name": last, "title": title, "account": r.get("account_number")})
    return best[1] if best else None


def match_accounts(business_name, license_rows):
    """Account numbers whose legal or DBA name normalizes to the business's name. Issued licenses (AAI) first."""
    want = norm(business_name)
    if not want:
        return []
    hits = [r for r in license_rows if want in (norm(r.get("legal_name")), norm(r.get("doing_business_as_name")))]
    hits.sort(key=lambda r: (r.get("license_status") != "AAI", r.get("account_number") or ""))
    out = []
    for r in hits:
        if r.get("account_number") and r["account_number"] not in out:
            out.append(r["account_number"])
    return out


def find(businesses, client=None):
    """{website_domain: owner} for the Chicago businesses whose City license account names a decision-maker."""
    from socrata import Socrata, quote, in_list
    chi = client or Socrata(PORTAL)
    found = {}
    for b in businesses:
        if R.PRODUCTS.get(b.get("product")) != "chicago":
            continue
        tok = key_token(b.get("business"))
        if not tok:
            continue
        like = quote(f"%{tok}%")
        lic = chi.rows(LICENSES, select="account_number,legal_name,doing_business_as_name,license_status",
                       where=f"upper(legal_name) like {like} OR upper(doing_business_as_name) like {like}", limit=2000)
        accounts = match_accounts(b.get("business"), lic)
        for acct in accounts[:3]:
            rows = chi.rows(OWNERS, select="account_number,owner_first_name,owner_last_name,owner_title",
                            where=f"account_number = {quote(acct)}", limit=50)
            owner = pick_owner(rows)
            if owner:
                found[R.domain_of(b.get("website"))] = owner
                break
    return found


def selftest():
    bad = []

    def check(name, got, want):
        if got != want:
            bad.append(f"{name}: got {got!r}, want {want!r}")

    check("norm drops suffix and punctuation", norm("Done Just Right, Inc."), "DONE JUST RIGHT")
    check("norm reads & as and", norm("Smith & Sons Cleaning LLC"), "SMITH AND SONS CLEANING")
    check("token skips trade words", key_token("Skyline Commercial Cleaning"), "SKYLINE")
    lic = [{"account_number": "1", "legal_name": "SKYLINE COMMERCIAL CLEANING INC", "doing_business_as_name": "", "license_status": "AAI"},
           {"account_number": "2", "legal_name": "SKYLINE ROOFING LLC", "doing_business_as_name": "SKYLINE ROOFING", "license_status": "AAI"},
           {"account_number": "3", "legal_name": "X LLC", "doing_business_as_name": "SKYLINE COMMERCIAL CLEANING", "license_status": "AAC"}]
    check("exact normalized match only, issued first", match_accounts("Skyline Commercial Cleaning", lic), ["1", "3"])
    check("no partial match", match_accounts("Skyline", lic), [])
    owners = [{"account_number": "1", "owner_first_name": "ACME HOLDINGS", "owner_last_name": "", "owner_title": "MEMBER"},
              {"account_number": "1", "owner_first_name": "DANA", "owner_last_name": "REYES", "owner_title": "SECRETARY"},
              {"account_number": "1", "owner_first_name": "SAM", "owner_last_name": "OKAFOR", "owner_title": "MEMBER"},
              {"account_number": "1", "owner_first_name": "LEE", "owner_last_name": "PARK", "owner_title": "PRESIDENT"}]
    check("president beats member, secretary and companies skipped", pick_owner(owners),
          {"first_name": "Lee", "last_name": "Park", "title": "President", "account": "1"})
    check("no decision-maker, no owner", pick_owner(owners[:2]), None)
    check("stored titles pass the decision-title rule", all(R.DECISION_TITLE.search(o) for _, o in TITLE_RANK), True)
    if bad:
        for b in bad:
            print(f"ERROR owners_chicago selftest: {b}")
        sys.exit(1)
    print("owners_chicago selftest: PASS 8 checks")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(__doc__)
