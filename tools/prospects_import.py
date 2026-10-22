#!/usr/bin/env python3
"""Cleaning prospects (Entity B) from enrichment exports into one validated file.

Reads Apollo, Hunter or Clay CSV exports (or our own CSV with the same headers) and writes data/prospects/prospects.json
in schema pnf.prospect.v1. data/ is gitignored: named decision-makers are personal data and never enter this public repo.
The Inbox Gate (tools/pnf_rules.inbox_problems) runs on every row: role-based inboxes (info@, contact@, office@,
estimating@ ...), free-mail addresses and addresses off the business's own domain are rejected with the reason, never
silently kept. The CRM's existing role-inbox prospects stay where they are and are simply not eligible for drafting.

Usage: python3 tools/prospects_import.py --product austin-construction --source apollo export.csv [more.csv ...]
           [--out data/prospects/prospects.json] [--do-not-email data/prospects/do_not_email.txt]
Exit 0 when at least one prospect passed and the written file validates; 1 otherwise. Rejections are listed in
data/prospects/rejected.json (gitignored) with the reason for each row.
"""
import argparse
import csv
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "prospects", "prospects.json")

# header aliases, compared lower case with spaces and punctuation removed
ALIASES = {
    "first_name": ("firstname", "first", "givenname", "contactfirstname"),
    "last_name": ("lastname", "last", "surname", "familyname", "contactlastname"),
    "title": ("title", "jobtitle", "position", "role", "seniortitle"),
    "email": ("email", "emailaddress", "workemail", "value", "personemail", "contactemail"),
    "email_status": ("emailstatus", "verificationstatus", "status", "emailverification", "result", "verification"),
    "business": ("company", "companyname", "organization", "organizationname", "accountname", "business"),
    "website": ("website", "companywebsite", "domain", "companydomain", "websiteurl", "url"),
    "city": ("city", "companycity", "personcity", "locationcity"),
    "source_url": ("linkedinurl", "personlinkedinurl", "sourceurl", "source"),
}
STATUS_MAP = {"verified": "verified", "valid": "valid", "deliverable": "deliverable", "ok": "valid",
              "accept_all": "accept_all", "acceptall": "accept_all", "catchall": "catch_all", "catch_all": "catch_all",
              "catch-all": "catch_all", "likely to engage": "valid", "guessed": "unverified", "unverified": "unverified",
              "invalid": "invalid", "undeliverable": "invalid", "risky": "risky", "unknown": "unknown", "": "unknown"}
CITY_OF = {"chicago-construction": "chicago", "chicago-restaurant": "chicago", "austin-construction": "austin"}
PREFIX = {"chicago-construction": "cc", "chicago-restaurant": "cr", "austin-construction": "ac"}


def norm_header(h):
    return re.sub(r"[^a-z0-9]", "", (h or "").lower())


def map_row(row):
    by = {norm_header(k): (v or "").strip() for k, v in row.items() if k}
    out = {}
    for field, names in ALIASES.items():
        for n in names:
            if by.get(n):
                out[field] = by[n]
                break
    return out


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def to_prospect(m, product, source):
    domain = R.domain_of(m.get("website") or (m.get("email", "").split("@", 1)[1] if "@" in m.get("email", "") else ""))
    status = STATUS_MAP.get((m.get("email_status") or "").strip().lower(), "unknown")
    return {
        "prospect_id": f"{PREFIX[product]}-{slug(domain)}",
        "product": product,
        "business": re.sub(r"\s+", " ", m.get("business") or "").strip(),
        "website_domain": domain,
        "city": CITY_OF[product],
        "first_name": (m.get("first_name") or "").strip().title(),
        "last_name": (m.get("last_name") or "").strip().title(),
        "title": (m.get("title") or "").strip(),
        "email": (m.get("email") or "").strip().lower(),
        "email_source": source,
        "email_status": status,
        "source_url": m.get("source_url") or "",
        "do_not_email": False,
        "status": "ready",
        "importedAt": dt.date.today().isoformat(),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", nargs="+")
    ap.add_argument("--product", required=True, choices=sorted(CITY_OF))
    ap.add_argument("--source", required=True, choices=sorted(R.SOURCES))
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--do-not-email", default=os.path.join(ROOT, "data", "prospects", "do_not_email.txt"))
    a = ap.parse_args()

    blocked = set()
    if os.path.exists(a.do_not_email):
        blocked = {l.strip().lower() for l in open(a.do_not_email, encoding="utf-8") if l.strip() and not l.startswith("#")}

    existing = {"schema": "pnf.prospect.v1", "prospects": []}
    if os.path.exists(a.out):
        existing = json.load(open(a.out, encoding="utf-8"))
    keep = {x["prospect_id"]: x for x in existing.get("prospects", [])}
    rejected = []
    for path in a.csv:
        with open(path, newline="", encoding="utf-8-sig") as f:
            for i, row in enumerate(csv.DictReader(f), 2):
                p = to_prospect(map_row(row), a.product, a.source)
                why = R.validate_prospect(p)
                dom = p["website_domain"]
                if p["email"] in blocked or dom in blocked:
                    why.append("on the do-not-email list")
                if p["prospect_id"] in keep and keep[p["prospect_id"]]["email"] != p["email"]:
                    why.append("this business already has a decision-maker in the file (one per business)")
                if why:
                    rejected.append({"file": os.path.basename(path), "line": i, "business": p["business"], "reasons": why})
                else:
                    keep[p["prospect_id"]] = p

    doc = {"schema": "pnf.prospect.v1", "updatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
           "prospects": sorted(keep.values(), key=lambda x: x["prospect_id"])}
    problems = R.validate_prospect_file(doc)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(os.path.join(os.path.dirname(a.out), "rejected.json"), "w", encoding="utf-8") as f:
        json.dump({"rejected": rejected}, f, indent=1)
    if problems:
        for p in problems[:30]:
            print(f"ERROR prospects: {p}")
        sys.exit(1)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1)
        f.write("\n")
    print(f"{'OK' if doc['prospects'] else 'ERROR'} prospects: {len(doc['prospects'])} named decision-makers kept, "
          f"{len(rejected)} rows rejected (see {os.path.relpath(os.path.join(os.path.dirname(a.out), 'rejected.json'), ROOT)})")
    sys.exit(0 if doc["prospects"] else 1)


if __name__ == "__main__":
    main()
