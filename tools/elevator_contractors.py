#!/usr/bin/env python3
"""Chicago elevator contractors: the buyer count for the elevator citations list (Todd, Oct 22, 2026, live chat,
decision 3: "Elevator: run the buyer-count probe only. No build.").

Question: how many independent elevator companies could buy a $99 a month list of elevator citations? Every elevator
equipment permit names its elevator contractor, so the distinct contractors on those permits are the market. Counts
only: names are read and counted in the runner and never written. National firms are matched on Otis, Schindler,
TK Elevator or thyssenkrupp, KONE and Mitsubishi; everything else is an independent.

Runs in GitHub Actions (.github/workflows/elevator-contractors.yml); the cloud agents cannot reach data.cityofchicago.org.
Source: Building Permits (ydr8-5enu), permit_type PERMIT - ELEVATOR EQUIPMENT, every contact_N whose type is
CONTRACTOR-ELEVATOR. Writes probes/elevator-contractors-<date>.json.

Usage: python3 tools/elevator_contractors.py             counts (Actions)
       python3 tools/elevator_contractors.py --selftest  offline: planted names
"""
import collections
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WINDOWS = (90, 365)
MIN_PERMITS = 5          # Todd's cut: an independent that pulled 5 or more permits in the window
NATIONAL = {"otis": r"\bOTIS\b", "schindler": r"\bSCHINDLER\b", "tk_elevator": r"\bTK\s*ELEVATOR\b|\bTHYSSEN\s*KRUPP\b|\bTHYSSENKRUPP\b",
            "kone": r"\bKONE\b", "mitsubishi": r"\bMITSUBISHI\b"}
SUFFIX = re.compile(r"\b(?:THE|INC|INCORPORATED|LLC|L L C|CO|COMPANY|CORP|CORPORATION|LTD|LP|LLP)\b")


def norm(name):
    """One firm, one key: upper case, no punctuation, no legal suffix. 'Otis Elevator Co.' and 'OTIS ELEVATOR COMPANY'
    both give 'OTIS ELEVATOR'."""
    n = re.sub(r"[^A-Z0-9& ]+", " ", (name or "").upper())
    n = SUFFIX.sub(" ", n)
    return re.sub(r"\s+", " ", n).strip()


def brand(key):
    return next((b for b, rx in NATIONAL.items() if re.search(rx, key)), None)


def contractors(row):
    """The normalized elevator contractor keys on one permit row (any contact_N of type CONTRACTOR-ELEVATOR)."""
    out = set()
    for k, v in row.items():
        m = re.match(r"^contact_(\d+)_type$", k)
        if m and str(v or "").strip().upper() == "CONTRACTOR-ELEVATOR":
            key = norm(row.get(f"contact_{m.group(1)}_name"))
            if key:
                out.add(key)
    return out


def count(rows, days, today):
    """Counts for permits issued in the last `days` days. Returns a dict of numbers only."""
    since = (today - dt.timedelta(days=days)).isoformat()
    per = collections.Counter()
    permits, no_contractor = 0, 0
    for r in rows:
        if (r.get("issue_date") or "")[:10] < since:
            continue
        permits += 1
        cs = contractors(r)
        if not cs:
            no_contractor += 1
        for c in cs:
            per[c] += 1
    nat = {c: n for c, n in per.items() if brand(c)}
    ind = {c: n for c, n in per.items() if not brand(c)}
    return {"days": days, "permits": permits, "permitsWithoutContractor": no_contractor, "contractors": len(per),
            "nationalFirms": len(nat), "nationalBrands": len({brand(c) for c in nat}),
            "nationalBrandsByKey": dict(collections.Counter(brand(c) for c in nat)),
            "independents": len(ind), f"independentsWith{MIN_PERMITS}OrMorePermits": sum(1 for n in ind.values() if n >= MIN_PERMITS),
            "permitContractorPairsNational": sum(nat.values()), "permitContractorPairsIndependent": sum(ind.values()),
            "independentPermitsMedian": sorted(ind.values())[len(ind) // 2] if ind else 0}


def selftest():
    bad = []
    for raw, want in (("Otis Elevator Co.", "OTIS ELEVATOR"), ("OTIS ELEVATOR COMPANY", "OTIS ELEVATOR"),
                      ("TK Elevator Corporation", "TK ELEVATOR"), ("Acme Lift Service, L.L.C.", "ACME LIFT SERVICE")):
        if norm(raw) != want:
            bad.append((raw, norm(raw), want))
    for key, want in (("OTIS ELEVATOR", "otis"), ("SCHINDLER ELEVATOR", "schindler"), ("THYSSENKRUPP ELEVATOR", "tk_elevator"),
                      ("THYSSEN KRUPP ELEVATOR AMERICAS", "tk_elevator"), ("TK ELEVATOR", "tk_elevator"), ("KONE", "kone"),
                      ("MITSUBISHI ELECTRIC US", "mitsubishi"), ("ACME LIFT SERVICE", None), ("KONEKT LIFTS", None)):
        if brand(key) != want:
            bad.append((key, brand(key), want))
    today = dt.date(2026, 10, 22)
    rows = ([{"issue_date": "2026-10-01", "contact_1_type": "CONTRACTOR-ELEVATOR", "contact_1_name": "Acme Lift Service LLC",
              "contact_2_type": "OWNER", "contact_2_name": "Somebody"}] * 5
            + [{"issue_date": "2026-09-01", "contact_1_type": "CONTRACTOR-ELEVATOR", "contact_1_name": "Otis Elevator Co"},
               {"issue_date": "2026-09-02", "contact_3_type": "CONTRACTOR-ELEVATOR", "contact_3_name": "OTIS ELEVATOR COMPANY"},
               {"issue_date": "2026-09-03", "contact_1_type": "CONTRACTOR-ELEVATOR", "contact_1_name": "Beta Elevator Inc"},
               {"issue_date": "2025-01-01", "contact_1_type": "CONTRACTOR-ELEVATOR", "contact_1_name": "Gamma Lifts"},
               {"issue_date": "2026-10-02", "contact_1_type": "ARCHITECT", "contact_1_name": "Not A Contractor"}])
    c = count(rows, 90, today)
    want = {"permits": 9, "contractors": 3, "nationalFirms": 1, "independents": 2, "independentsWith5OrMorePermits": 1,
            "permitsWithoutContractor": 1}
    for k, v in want.items():
        if c[k] != v:
            bad.append((k, c[k], v))
    if "Acme" in json.dumps(c) or "ACME" in json.dumps(c):
        bad.append(("a name was written", "", ""))
    for b in bad:
        print("FAIL", b)
    print(f"selftest {'FAIL' if bad else 'ok'}: {len(bad)} wrong")
    return not bad


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    from exterior_chicago import PORTAL, TODAY, get   # network only in the runner
    since = (TODAY - dt.timedelta(days=max(WINDOWS))).isoformat()
    rows = get(f"{PORTAL}/resource/ydr8-5enu.json", {"$where": f"permit_type='PERMIT - ELEVATOR EQUIPMENT' AND issue_date>='{since}'",
                                                     "$limit": 50000})
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "source": "ydr8-5enu",
           "note": "Counts only. Contractor names are normalized (case, punctuation, legal suffix) and counted in the runner, never written.",
           "rowsFetched": len(rows)}
    for d in WINDOWS:
        out[f"days{d}"] = count(rows, d, TODAY)
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"elevator-contractors-{TODAY.isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(path, json.dumps({k: v for k, v in out.items() if k.startswith("days")}))


if __name__ == "__main__":
    main()
