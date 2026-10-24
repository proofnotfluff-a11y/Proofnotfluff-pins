#!/usr/bin/env python3
"""Approved cold email templates, for the standing send rule (coo/CONSTITUTION.md section 2, Todd, Oct 24, 2026).

A batch may send without Todd's per-batch word only when every draft uses a template Todd approved in a live chat and
that template's subject and body are byte for byte what he approved. This tool keeps that record.

    python3 tools/approved_templates.py --status
        lists every template block in the outreach files and whether it is approved, changed since approval or new.
    python3 tools/approved_templates.py --check-drafts DRAFTS.json --file FILE
        exit 0 only if every draft's 'variant' (its template id, T2-B) is approved in FILE and unchanged.
    python3 tools/approved_templates.py --record FILE --ids T1-A T1-B ... --note "Todd's words and date"
        live chat only, after Todd's yes in that chat: records the current text of those templates as approved.
    python3 tools/approved_templates.py --selftest

The record is email/approved_templates.json. A template is identified by its file and id (T<n>-<Variant>, a missing
Variant line is A); its fingerprint is a sha256 of its Subject line and fenced body. Editing a template's wording
changes the fingerprint, so the edited template needs Todd's yes again before any batch on it sends without him.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECORD = os.path.join(ROOT, "email", "approved_templates.json")
FILES = (".claude/skills/outreach-drafter/templates.md", "email/L1-OUTREACH.md", "email/P1-PEST-SEAT.md", "email/L2-COMMISSION.md")
BLOCK = re.compile(r"^### (T(\d+)[^\n]*)\n(.*?)(?=^### |^## |\Z)", re.S | re.M)


def blocks(path):
    """{template id: fingerprint} for every '### T<n>' block with a Subject line and a fenced body."""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in BLOCK.finditer(text):
        num, chunk = m.group(2), m.group(3)
        subj = re.search(r"^Subject:\s*(.+)$", chunk, re.M)
        body = re.search(r"```(?:text)?\n(.*?)```", chunk, re.S)
        if not (subj and body):
            continue
        var = re.search(r"^Variant:\s*(.*)$", chunk, re.M)
        tid = f"T{num}-{(var.group(1).strip() if var else '') or 'A'}"
        out[tid] = hashlib.sha256((subj.group(1).strip() + "\n" + body.group(1).strip("\n")).encode("utf-8")).hexdigest()
    return out


def load(record=RECORD):
    if not os.path.isfile(record):
        return {"schema": "pnf.approved_templates.v1", "templates": {}}
    return json.load(open(record, encoding="utf-8"))


def rel(path):
    p = os.path.abspath(path if os.path.isabs(path) else os.path.join(ROOT, path))
    return os.path.relpath(p, ROOT)


def check_ids(file, ids, record=RECORD):
    """Problems for templates in FILE that are not approved or changed since approval (empty list = all clear)."""
    f = rel(file)
    now = blocks(os.path.join(ROOT, f))
    rec = load(record)["templates"]
    probs = []
    for tid in ids:
        key = f"{f}#{tid}"
        if tid not in now:
            probs.append(f"{key}: no such template in the file")
        elif key not in rec:
            probs.append(f"{key}: not approved by Todd yet (first batch on it goes to him)")
        elif rec[key]["sha256"] != now[tid]:
            probs.append(f"{key}: wording changed since Todd approved it on {rec[key].get('approvedOn', '?')}")
    return probs


def check_drafts(drafts_path, file, record=RECORD):
    ds = json.load(open(drafts_path, encoding="utf-8")).get("drafts", [])
    if not ds:
        return ["no drafts in the file"]
    ids = sorted({str(d.get("variant") or "") for d in ds})
    probs = [f"draft {d.get('prospect_id')}: no template id" for d in ds if not d.get("variant")]
    return probs + check_ids(file, [i for i in ids if i], record)


def record_ids(file, ids, note, day, record=RECORD):
    f = rel(file)
    now = blocks(os.path.join(ROOT, f))
    missing = [t for t in ids if t not in now]
    if missing:
        raise SystemExit(f"not in {f}: {', '.join(missing)}")
    if not note.strip():
        raise SystemExit("--note must carry Todd's words and the date")
    data = load(record)
    for tid in ids:
        data["templates"][f"{f}#{tid}"] = {"sha256": now[tid], "approvedOn": day, "note": note.strip()}
    data["templates"] = dict(sorted(data["templates"].items()))
    with open(record, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def status(record=RECORD):
    rec = load(record)["templates"]
    rows = []
    for f in FILES:
        for tid, sha in blocks(os.path.join(ROOT, f)).items():
            key = f"{f}#{tid}"
            st = "approved" if key in rec and rec[key]["sha256"] == sha else ("CHANGED" if key in rec else "new")
            rows.append(f"{st:8} {key}" + (f" ({rec[key]['approvedOn']})" if key in rec else ""))
    return rows


def selftest():
    global ROOT
    old = ROOT
    with tempfile.TemporaryDirectory() as d:
        ROOT = d
        os.makedirs(os.path.join(d, "email"))
        tf = os.path.join(d, "email", "X.md")
        open(tf, "w").write("# X\n\n### T1 one\nSubject: Hi {first}\n```text\nBody one\n```\n\n### T1 one, B\nVariant: B\n"
                            "Subject: Hi\n```text\nBody B\n```\n\n## Other\n")
        rec = os.path.join(d, "email", "rec.json")
        assert set(blocks(tf)) == {"T1-A", "T1-B"}, blocks(tf)
        assert check_ids("email/X.md", ["T1-A"], rec), "an unapproved template must fail"
        record_ids("email/X.md", ["T1-A"], "Todd, test", "2026-10-24", rec)
        assert check_ids("email/X.md", ["T1-A"], rec) == [], "an approved, unchanged template must pass"
        assert check_ids("email/X.md", ["T1-B"], rec), "B was never approved"
        dr = os.path.join(d, "drafts.json")
        json.dump({"drafts": [{"prospect_id": "p1", "variant": "T1-A"}, {"prospect_id": "p2", "variant": "T1-B"}]}, open(dr, "w"))
        assert check_drafts(dr, "email/X.md", rec), "a batch with one unapproved template must fail"
        json.dump({"drafts": [{"prospect_id": "p1", "variant": "T1-A"}]}, open(dr, "w"))
        assert check_drafts(dr, "email/X.md", rec) == [], "an all-approved batch must pass"
        json.dump({"drafts": [{"prospect_id": "p1"}]}, open(dr, "w"))
        assert check_drafts(dr, "email/X.md", rec), "a draft without a template id must fail"
        open(tf, "w").write(open(tf).read().replace("Body one", "Body one, edited"))
        assert check_ids("email/X.md", ["T1-A"], rec), "an edited template must fail"
        try:
            record_ids("email/X.md", ["T1-A"], " ", "2026-10-24", rec)
            raise AssertionError("an empty note must be refused")
        except SystemExit:
            pass
    ROOT = old
    print("approved_templates selftest: 7 planted cases right")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--check-drafts")
    ap.add_argument("--file")
    ap.add_argument("--record")
    ap.add_argument("--ids", nargs="*")
    ap.add_argument("--note", default="")
    ap.add_argument("--day")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return 0
    if a.status:
        print("\n".join(status()))
        return 0
    if a.check_drafts:
        if not a.file:
            ap.error("--check-drafts needs --file")
        probs = check_drafts(a.check_drafts, a.file)
        print("\n".join(probs) if probs else "approved_templates: every draft uses an approved, unchanged template")
        return 1 if probs else 0
    if a.record:
        if not (a.ids and a.day):
            ap.error("--record needs --ids and --day (YYYY-MM-DD, from bash)")
        record_ids(a.record, a.ids, a.note, a.day)
        print(f"recorded {len(a.ids)} template(s) in {rel(RECORD)}")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
