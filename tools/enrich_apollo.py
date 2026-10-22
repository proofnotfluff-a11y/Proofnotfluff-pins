#!/usr/bin/env python3
"""Find one named decision-maker per cleaning business with the Apollo.io API (People Search, then People Match to
reveal the work email). Same output shape as tools/enrich_hunter.py, read by tools/prospects_import.py (--source apollo).

Deterministic: for each domain it asks for people at that organization with an owner, founder, president, partner,
director or general manager title, keeps the first one whose revealed email is on the business's own domain, passes
the Inbox Gate and comes back "verified", and writes nothing it could not verify. Personal emails are never requested.

Needs APOLLO_API_KEY (a GitHub Actions secret in prospect-enrichment.yml; never printed, logged or committed).
Apollo charges credits per revealed email on most plans: --limit caps the businesses per run.

Usage: APOLLO_API_KEY=... python3 tools/enrich_apollo.py businesses.csv --out data/prospects/apollo.csv [--limit 50]
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

API = "https://api.apollo.io/api/v1"
HEAD = ["First name", "Last name", "Position", "Email", "Email status", "Company", "Website", "Source"]
TITLES = ["owner", "co-owner", "founder", "co-founder", "president", "ceo", "principal", "partner", "general manager",
          "operations manager", "director of operations"]
SENIORITIES = ["owner", "founder", "c_suite", "partner", "vp", "head", "director"]


def post(path, body, key, tries=3):
    data = json.dumps(body).encode("utf-8")
    last = None
    for i in range(tries):
        req = urllib.request.Request(f"{API}/{path}", data=data, method="POST",
                                     headers={"Content-Type": "application/json", "Cache-Control": "no-cache",
                                              "X-Api-Key": key, "User-Agent": "ProofNotFluff"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8", "replace"))
        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise SystemExit("ERROR apollo: the API key was refused or the plan lacks API access (HTTP %d)" % e.code)
            if e.code == 429:
                time.sleep(15 * (i + 1))
                last = "HTTP 429"
                continue
            last = f"HTTP {e.code}"
            break
        except Exception as e:
            last = type(e).__name__
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"{path} failed: {last}")


def candidates(people, domain):
    out = []
    for p in people or []:
        if not (p.get("first_name") and p.get("last_name")):
            continue
        if not R.DECISION_TITLE.search(p.get("title") or ""):
            continue
        out.append(p)
    return out


def enrich(rows, key, pause=1.0):
    """rows: dicts with business and website. Returns (found rows in HEAD shape, misses)."""
    found, misses = [], 0
    for r in rows:
        domain = R.domain_of(r.get("website") or r.get("domain") or "")
        if not domain:
            misses += 1
            continue
        res = post("mixed_people/search", {"q_organization_domains_list": [domain], "person_titles": TITLES,
                                           "person_seniorities": SENIORITIES, "page": 1, "per_page": 10}, key)
        pick = None
        for p in candidates(res.get("people"), domain):
            m = post("people/match", {"id": p.get("id"), "reveal_personal_emails": False}, key)
            person = m.get("person") or {}
            email = (person.get("email") or "").lower()
            status = (person.get("email_status") or "").lower()
            if not email or "not_unlocked" in email or status != "verified":
                continue
            if R.inbox_problems(email, domain, p.get("first_name"), p.get("last_name")):
                continue
            pick = (p, email, status)
            break
        if not pick:
            misses += 1
            continue
        p, email, status = pick
        found.append({"First name": p.get("first_name"), "Last name": p.get("last_name"), "Position": p.get("title"),
                      "Email": email, "Email status": status, "Company": r.get("business") or "",
                      "Website": domain, "Source": "apollo"})
        time.sleep(pause)
    return found, misses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("businesses")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--pause", type=float, default=1.0)
    a = ap.parse_args()
    key = os.environ.get("APOLLO_API_KEY", "")
    if not key:
        print("ERROR apollo: APOLLO_API_KEY is not set in this environment")
        sys.exit(1)
    rows = list(csv.DictReader(open(a.businesses, newline="", encoding="utf-8-sig")))[: a.limit]
    try:
        found, misses = enrich(rows, key, a.pause)
    except RuntimeError as e:
        print(f"ERROR apollo: {e}")
        sys.exit(1)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEAD)
        w.writeheader()
        w.writerows(found)
    print(f"{'OK' if found else 'ERROR'} apollo: {len(found)} verified decision-makers from {len(rows)} businesses, {misses} without one")
    sys.exit(0 if found else 1)


if __name__ == "__main__":
    main()
