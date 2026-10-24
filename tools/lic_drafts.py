#!/usr/bin/env python3
"""First-email drafts for the license count emails (email/L2-COMMISSION.md), with no model in between.

Reads data/prospects/lic_prospects.json (written by tools/crm_prospects.py --products chicago-licenses --trades
pos_merchant,commercial_insurance --prefix lic_), puts POS and merchant services resellers first, then commercial
insurance agents (Todd, Oct 24, 2026), oldest checkedAt first inside each, fills the trade's first template with this
Monday's counts, and writes data/work/lic_drafts.json (schema pnf.lic_draft.v1, sender sales@ on every draft). The
copy gate (copy_gate.py --lic) then checks every draft. Nothing here sends anything.

Usage: python3 tools/lic_drafts.py [--max 25]
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import copy_gate as C  # noqa: E402
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORDER = ("pos_merchant", "commercial_insurance")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=25)
    ap.add_argument("--prospects", default=C.LIC_PROSPECTS)
    ap.add_argument("--out", default=C.LIC_DRAFTS)
    ap.add_argument("--pending", default="", help="also draft the addresses still waiting for Bouncer (data/prospects/lic_verify.json), "
                    "for Todd's review only; they cannot send before the check")
    a = ap.parse_args()
    pdoc = json.load(open(a.prospects, encoding="utf-8"))
    pros = list(pdoc["prospects"])
    if a.pending:
        pend = json.load(open(a.pending, encoding="utf-8")).get("pending") or []
        pros += pend
        pdoc["pending"] = pend
        json.dump(pdoc, open(a.prospects, "w", encoding="utf-8"), indent=1)   # the gate reads both lists from one file
    lic, insp = json.load(open(C.LIC_SAMPLE, encoding="utf-8")), json.load(open(C.INSP_SAMPLE, encoding="utf-8"))
    first = {t["trade"]: t for t in C.signal_templates(C.LIC_FILE) if t["step"] == "first" and t["letter"] == "A"}
    pros = [p for p in pros if R.trade_of(p) in ORDER and not p.get("first_example") and not p.get("do_not_email")]
    pros.sort(key=lambda p: (ORDER.index(R.trade_of(p)), p.get("checked_at") or "", p["prospect_id"]))
    drafts = []
    for p in pros[:a.max]:
        t = first[R.trade_of(p)]
        subj, body = C.lic_fill(t, lic, insp, p["first_name"])
        drafts.append({"prospect_id": p["prospect_id"], "to": p["email"], "subject": subj, "body": body, "variant": t["id"],
                       "sender": R.SALES_SENDER, "trade": R.trade_of(p), "window_from": lic["window"]["from"],
                       "emailStatus": p.get("email_status") or ""})
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"schema": "pnf.lic_draft.v1", "drafts": drafts}, open(a.out, "w", encoding="utf-8"), indent=1)
    by = {tr: sum(1 for d in drafts if d["trade"] == tr) for tr in ORDER}
    print(f"OK lic drafts: {len(drafts)} written ({', '.join(f'{k} {v}' for k, v in by.items())}), "
          f"window {lic['window']['from']} to {lic['window']['to']}, sender {R.SALES_SENDER}")


if __name__ == "__main__":
    main()
