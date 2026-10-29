#!/usr/bin/env python3
"""Stage timing probe: how close to move-in is each Chicago permit milestone? (Todd, Oct 29, 2026: "Go with your
recommendations for everything", the timing check Kimi asked for before any page or video says "weeks before move-in".)

Runs in GitHub Actions (.github/workflows/stage-timing.yml) because the cloud agents cannot reach the City portal.
Reads Chicago Building Permits (ydr8-5enu) with Socrata's row system fields (:created_at, :updated_at) and writes only
aggregate day counts to probes/stage-timing-<date>.json: no addresses, no business or person names.

What it measures, per milestone, for big jobs (new construction or renovation, reported cost $500,000 or more):
- age: days from the permit's issue date to today, for permits still open
- finish: days from issue date to the row's last update, for permits whose milestone says the CO was issued or the
  job is complete (the last update is our proxy for when that milestone was reached; the probe reports how many
  rows share one update day, so a bulk refresh that stamps every row shows up as a warning instead of a fake answer)
"""
import datetime as dt, json, os, statistics, sys, urllib.parse, urllib.request
from collections import Counter

UA = {"User-Agent": "ProofNotFluff data probe (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
URL = "https://data.cityofchicago.org/resource/ydr8-5enu.json"
WHERE = ("issue_date >= '2021-01-01T00:00:00' AND reported_cost >= 500000 AND "
         "permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')")
SELECT = "permit_,permit_type,permit_status,permit_milestone,issue_date,:created_at,:updated_at"
TODAY = dt.date.today()


def fetch():
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({"$select": SELECT, "$where": WHERE, "$order": "permit_", "$limit": 50000, "$offset": offset})
        with urllib.request.urlopen(urllib.request.Request(f"{URL}?{q}", headers=UA), timeout=120) as r:
            page = json.load(r)
        rows += page
        if len(page) < 50000:
            return rows
        offset += 50000


def day(s):
    return dt.date.fromisoformat(s[:10]) if s else None


def pct(xs):
    if not xs:
        return None
    xs = sorted(xs)
    q = lambda p: xs[min(len(xs) - 1, int(p * (len(xs) - 1) + 0.5))]
    return {"n": len(xs), "p10": q(.1), "p25": q(.25), "median": q(.5), "p75": q(.75), "p90": q(.9),
            "mean": round(statistics.mean(xs))}


def main():
    rows = fetch()
    by_ms = {}
    upd_days = Counter()
    for r in rows:
        iss, upd = day(r.get("issue_date")), day(r.get(":updated_at"))
        if not iss:
            continue
        ms = r.get("permit_milestone") or "(blank)"
        typ = "new" if "NEW" in (r.get("permit_type") or "") else "reno"
        b = by_ms.setdefault(ms, {"new": {"age": [], "finish": []}, "reno": {"age": [], "finish": []}})
        b[typ]["age"].append((TODAY - iss).days)
        if upd:
            b[typ]["finish"].append((upd - iss).days)
            upd_days[upd.isoformat()] += 1
    out = {"probe": "stage-timing", "ranAt": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z", "dataset": "ydr8-5enu",
           "where": WHERE, "rows": len(rows),
           "updateDaysTop": upd_days.most_common(8), "distinctUpdateDays": len(upd_days),
           "milestones": {ms: {t: {"ageDays": pct(v["age"]), "issueToLastUpdateDays": pct(v["finish"])} for t, v in d.items()}
                          for ms, d in sorted(by_ms.items())}}
    os.makedirs("probes", exist_ok=True)
    path = f"probes/stage-timing-{TODAY.isoformat()}.json"
    with open(path, "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))
    print("WROTE", path)


if __name__ == "__main__":
    sys.exit(main())
