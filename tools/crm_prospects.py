#!/usr/bin/env python3
"""CRM prospects (the ArtifactData listing a run saved with out_dir) into the validated Entity B file plus the stored
matches, with no model in between.

A run lists the CRM's prospects collection with ArtifactData (out_dir=data/crm) and then runs this script. It keeps only
prospects that carry a named decision-maker, have never had a first email (no firstSentAt) (contactFirstName, contactLastName, contactTitle and a contact email that
passes the Inbox Gate), drops doNotEmail, replied, customer, opted-out and bounced records, and writes:
  data/prospects/prospects.json   schema pnf.prospect.v1 (eligible for drafting)
  data/prospects/ineligible.json  every other prospect id with the reason (role inbox, no name, contact form ...)
  data/work/matches.json          schema pnf.match.v1 from each eligible prospect's matchedLeadId, kept only when that lead
                                  is in this week's permits/downstream/gc_leads.json
Exit 0 when the files were written (even with zero eligible prospects, so the inbox part of a run can go on);
exit 1 when the listing cannot be read or the written prospect file fails validation.

Usage: python3 tools/crm_prospects.py data/crm [--products austin-construction,chicago-construction]
"""
import argparse
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOSED = {"replied", "customer", "opted-out", "bounced", "bounced-precheck", "skipped"}
CITY = {"chicago-construction": "chicago", "chicago-restaurant": "chicago", "austin-construction": "austin"}


def docs_from(path):
    files = [path] if os.path.isfile(path) else sorted(glob.glob(os.path.join(path, "**", "*.json"), recursive=True))
    out = []
    for f in files:
        try:
            d = json.load(open(f, encoding="utf-8"))
        except ValueError as e:
            raise SystemExit(f"ERROR crm: {f} is not JSON ({e})")
        items = d if isinstance(d, list) else d.get("documents") or d.get("docs") or d.get("items") or [d]
        for it in items:
            if not isinstance(it, dict):
                continue
            data = it.get("data") if isinstance(it.get("data"), dict) else it
            pid = it.get("id") or it.get("doc_id") or data.get("id") or os.path.splitext(os.path.basename(f))[0]
            pid = str(pid).split("/")[-1]
            out.append((pid, data))
    return out


def to_prospect(pid, d):
    return {
        "prospect_id": pid,
        "product": d.get("product"),
        "business": d.get("business") or "",
        "website_domain": R.domain_of(d.get("website") or ""),
        "city": CITY.get(d.get("product"), ""),
        "first_name": (d.get("contactFirstName") or "").strip(),
        "last_name": (d.get("contactLastName") or "").strip(),
        "title": (d.get("contactTitle") or "").strip(),
        "email": (d.get("contact") or "").strip().lower() if d.get("contactType") == "email" else "",
        "email_source": d.get("emailSource") or "",
        "email_status": d.get("emailStatus") or "",
        "area": d.get("area") or "",
        "do_not_email": bool(d.get("doNotEmail")),
        "status": d.get("status") or "",
        "matched_lead_id": d.get("matchedLeadId") or "",
        "first_example": d.get("firstExample") or "",
        "sender": d.get("sender") or "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listing")
    ap.add_argument("--products", default="")
    ap.add_argument("--gc", default=os.path.join(ROOT, "permits", "downstream", "gc_leads.json"))
    a = ap.parse_args()
    if not os.path.exists(a.listing):
        print(f"ERROR crm: {a.listing} does not exist (list the CRM prospects with ArtifactData out_dir first)")
        sys.exit(1)
    want = {p for p in a.products.split(",") if p}
    eligible, ineligible = [], []
    seen = set()
    for pid, d in docs_from(a.listing):
        if pid in seen or not pid:
            continue
        seen.add(pid)
        p = to_prospect(pid, d)
        if want and p["product"] not in want:
            continue
        why = []
        if p["do_not_email"] or p["status"] in CLOSED:
            why.append(f"closed ({p['status'] or 'doNotEmail'})")
        if d.get("firstSentAt"):
            why.append("already emailed (firstSentAt set; follow-ups run from the CRM, never a second first email)")
        if d.get("contactType") != "email":
            why.append("contact form only")
        why += [w.split(": ", 1)[-1] for w in R.validate_prospect(p)]
        (ineligible.append({"prospect_id": pid, "reasons": sorted(set(why))}) if why else eligible.append(p))

    doc = {"schema": "pnf.prospect.v1", "prospects": eligible}
    probs = R.validate_prospect_file(doc)
    if probs:
        for x in probs[:20]:
            print(f"ERROR crm: {x}")
        sys.exit(1)
    os.makedirs(os.path.join(ROOT, "data", "prospects"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "data", "work"), exist_ok=True)
    json.dump(doc, open(os.path.join(ROOT, "data", "prospects", "prospects.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"ineligible": ineligible}, open(os.path.join(ROOT, "data", "prospects", "ineligible.json"), "w", encoding="utf-8"), indent=1)

    leads = set()
    if os.path.exists(a.gc):
        leads = {x["lead_id"] for x in json.load(open(a.gc, encoding="utf-8")).get("leads", [])}
    matches = [{"prospect_id": p["prospect_id"], "lead_id": p["matched_lead_id"], "reason": "stored match from the CRM"}
               for p in eligible if p["matched_lead_id"] in leads and p["matched_lead_id"] != p["first_example"]]
    json.dump({"schema": "pnf.match.v1", "matches": matches},
              open(os.path.join(ROOT, "data", "work", "matches.json"), "w", encoding="utf-8"), indent=1)
    role = sum(1 for x in ineligible if any("role-based" in r for r in x["reasons"]))
    print(f"OK crm: {len(eligible)} eligible named decision-makers, {len(ineligible)} ineligible ({role} role inboxes), "
          f"{len(matches)} stored matches still current")
    sys.exit(0)


if __name__ == "__main__":
    main()
