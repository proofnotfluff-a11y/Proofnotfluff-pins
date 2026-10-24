#!/usr/bin/env python3
"""CRM prospects (the ArtifactData listing a run saved with out_dir) into the validated Entity B file plus the stored
matches, with no model in between.

A run lists the CRM's prospects collection with ArtifactData (out_dir=data/crm) and then runs this script. It keeps only
prospects that carry a named decision-maker, have never had a first email (no firstSentAt) (contactFirstName, contactLastName, contactTitle and a contact email that
passes the Inbox Gate), drops doNotEmail, replied, customer, opted-out and bounced records, and writes:
  data/prospects/prospects.json   schema pnf.prospect.v1 (eligible for drafting)
  data/prospects/followups.json   schema pnf.prospect.v1: emailed, no reply, fewer than two follow-ups, one due, address valid
  data/prospects/verify.json      named owners whose site address (emailStatus unverified) waits for its Bouncer check;
                                  the outreach run checks them first and writes emailStatus deliverable or bounced-precheck
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
# "monday": said yes to the free Monday email (email/M1-MONDAY.md, Todd Oct 22): no more cold emails or follow-ups
CLOSED = {"replied", "customer", "opted-out", "bounced", "bounced-precheck", "skipped", "sent", "followed-up", "monday"}
# Todd, Oct 22, 2026: the Oct 19 and Oct 20 batches (a link in every email, sent to role inboxes) get no follow-up, ever
LEGACY_BATCHES = {"2026-10-19", "2026-10-20"}


def legacy_batch(d):
    """True for a prospect first emailed in the Oct 19 or Oct 20 batch, by its batch field or its first send date."""
    return str(d.get("batch") or "")[:10] in LEGACY_BATCHES or str(d.get("firstSentAt") or "")[:10] in LEGACY_BATCHES


CITY = {"chicago-construction": "chicago", "chicago-restaurant": "chicago", "austin-construction": "austin", "chicago-licenses": "chicago"}


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
        "owner_source": d.get("ownerSource") or "",
        "area": d.get("area") or "",
        "trade_vertical": d.get("tradeVertical") or R.TRADE_DEFAULT,
        "do_not_email": bool(d.get("doNotEmail")),
        "status": d.get("status") or "",
        "matched_lead_id": d.get("matchedLeadId") or "",
        "first_example": d.get("firstExample") or "",
        "sender": d.get("sender") or "",
        "variant": d.get("variant") or "",
        "followup_examples": [str(x) for x in (d.get("followupExamples") or [])],
        "checked_at": d.get("checkedAt") or "",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("listing")
    ap.add_argument("--products", default="austin-construction,chicago-construction",
                    help="the construction products only: the templates are construction emails")
    ap.add_argument("--gc", default=os.path.join(ROOT, "permits", "downstream", "gc_leads.json"))
    ap.add_argument("--prefix", default="", help="file name prefix for the outputs: 'lic_' for the license count emails "
                    "(python3 tools/crm_prospects.py data/crm --products chicago-licenses --trades pos_merchant,commercial_insurance --prefix lic_)")
    ap.add_argument("--trades", default="", help="keep only these trade verticals")
    ap.add_argument("--crm-trade", default="", help="keep only CRM records whose trade field is one of these, e.g. 'pest control' "
                    "for the pest seat emails (python3 tools/crm_prospects.py data/crm --products chicago-restaurant "
                    "--crm-trade 'pest control' --prefix pest_)")
    a = ap.parse_args()
    if not os.path.exists(a.listing):
        print(f"ERROR crm: {a.listing} does not exist (list the CRM prospects with ArtifactData out_dir first)")
        sys.exit(1)
    want = {p for p in a.products.split(",") if p}
    eligible, ineligible, followups, verify = [], [], [], []
    seen = set()
    today = __import__("datetime").date.today().isoformat()
    for pid, d in docs_from(a.listing):
        if pid in seen or not pid:
            continue
        seen.add(pid)
        p = to_prospect(pid, d)
        if want and p["product"] not in want:
            continue
        if a.trades and R.trade_of(p) not in a.trades.split(","):
            continue
        if a.crm_trade and (d.get("trade") or "").strip().lower() not in {t.strip().lower() for t in a.crm_trade.split(",") if t.strip()}:
            continue
        named = [w.split(": ", 1)[-1] for w in R.validate_prospect(p)]
        if d.get("contactType") != "email":
            named.append("contact form only")
        # follow-up candidates: emailed, nothing back, due, and a named address that still passes every gate
        if legacy_batch(d):
            ineligible.append({"prospect_id": pid, "reasons": ["legacy Oct 19 or 20 batch: no follow-up under the Oct 22 rules"]})
            continue
        # Todd, Oct 22, 2026, live chat: up to two follow-ups (pnf_rules.MAX_FOLLOWUPS), each due 5 business days after the last
        sent_fu = int(d.get("followupCount") or (1 if d.get("followupSentAt") else 0))
        if (p["status"] in ("sent", "followed-up") and d.get("firstSentAt") and not d.get("repliedAt") and not p["do_not_email"]
                and (d.get("followupDueAt") or "9999") <= today and sent_fu < R.MAX_FOLLOWUPS):
            if named:
                ineligible.append({"prospect_id": pid, "reasons": sorted(set(["follow-up blocked"] + named))})
            else:
                followups.append(p)
            continue
        why = list(named)
        # a named owner whose site address waits for its Bouncer check (enrichment ladder, Oct 22)
        if (p["email_status"] == R.PENDING_STATUS and not d.get("firstSentAt") and not p["do_not_email"]
                and p["status"] not in CLOSED and not R.validate_prospect(p, pending=True)):
            verify.append(p)
            ineligible.append({"prospect_id": pid, "reasons": ["waiting for its Bouncer check (data/prospects/verify.json)"]})
            continue
        if p["do_not_email"] or p["status"] in CLOSED:
            why.append(f"closed ({p['status'] or 'doNotEmail'})")
        if d.get("firstSentAt"):
            why.append("already emailed (firstSentAt set; never a second first email)")
        (ineligible.append({"prospect_id": pid, "reasons": sorted(set(why))}) if why else eligible.append(p))

    # file-level rules move records aside instead of stopping the whole Monday: one decision-maker per business and
    # address, catch-all at most 10% of the batch
    kept, emails, biz = [], set(), set()
    for p in sorted(eligible, key=lambda x: x["prospect_id"]):
        key = (p["product"], p["website_domain"])
        if p["email"] in emails or key in biz:
            ineligible.append({"prospect_id": p["prospect_id"], "reasons": ["duplicate address or business"]})
            continue
        emails.add(p["email"]); biz.add(key); kept.append(p)
    ca = [p for p in kept if p["email_status"] in R.CATCH_ALL]
    allowed = len(kept) // 10
    for p in ca[allowed:]:
        kept.remove(p)
        ineligible.append({"prospect_id": p["prospect_id"], "reasons": ["catch-all over the 10% batch cap; next week"]})
    eligible = kept
    doc = {"schema": "pnf.prospect.v1", "prospects": eligible}
    probs = R.validate_prospect_file(doc) + R.validate_prospect_file({"schema": "pnf.prospect.v1", "prospects": followups})
    if probs:
        for x in probs[:20]:
            print(f"ERROR crm: {x}")
        sys.exit(1)
    os.makedirs(os.path.join(ROOT, "data", "prospects"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "data", "work"), exist_ok=True)
    json.dump(doc, open(os.path.join(ROOT, "data", "prospects", a.prefix + "prospects.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"schema": "pnf.prospect.v1", "prospects": followups},
              open(os.path.join(ROOT, "data", "prospects", a.prefix + "followups.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"schema": "pnf.prospect.v1", "prospects": [], "pending": verify},
              open(os.path.join(ROOT, "data", "prospects", a.prefix + "verify.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"ineligible": ineligible}, open(os.path.join(ROOT, "data", "prospects", a.prefix + "ineligible.json"), "w", encoding="utf-8"), indent=1)

    leads = {}
    if os.path.exists(a.gc):
        leads = {x["lead_id"]: x for x in json.load(open(a.gc, encoding="utf-8")).get("leads", [])}
    # a stored match is kept only when the lead is still current and the prospect's trade vertical may use its stage
    matches = [{"prospect_id": p["prospect_id"], "lead_id": p["matched_lead_id"], "reason": "stored match from the CRM"}
               for p in eligible if p["matched_lead_id"] in leads and p["matched_lead_id"] != p["first_example"]
               and not R.trade_problems(p["product"], R.trade_of(p), leads[p["matched_lead_id"]])]
    json.dump({"schema": "pnf.match.v1", "matches": matches},
              open(os.path.join(ROOT, "data", "work", a.prefix + "matches.json"), "w", encoding="utf-8"), indent=1)
    role = sum(1 for x in ineligible if any("role-based" in r for r in x["reasons"]))
    print(f"OK crm: {len(eligible)} eligible named decision-makers, {len(ineligible)} ineligible ({role} role inboxes), "
          f"{len(matches)} stored matches still current, {len(followups)} follow-ups due, {len(verify)} addresses to check with Bouncer")
    sys.exit(0)


if __name__ == "__main__":
    main()
