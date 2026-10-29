#!/usr/bin/env python3
"""Chicago's big building jobs by how far along they are: the data layer for the free page /chicago-construction-pipeline/
(tools/dp_pipeline.py). Todd's go, Oct 29, 2026, 3:56 pm: "Yes, please do. Go with your recommendations for everything"
(the counts-only page planned after the cfongai read and Kimi's review; research_notes/stage-timing-2026-10-29.md).

Runs in GitHub Actions on the weekly permit wait pull (.github/workflows/dp_permit_wait.yml), because the cloud agents
cannot reach data.cityofchicago.org. Source: City of Chicago Data Portal, Building Permits (dataset ydr8-5enu).

What it counts: new construction and renovation permits with a reported cost of $500,000 or more, issued since Jan 1, 2021,
whose City milestone puts them on the certificate of occupancy (CO) path. Open jobs are grouped by community area and by
months since the permit was issued; issue-year cohorts show how many have their CO today.

What leaves the runner: counts only, in site/datapages/dp_pipeline/data.json. The query asks the City for seven columns
(KEEP); no contact, address, coordinate or description column is ever requested. Permit numbers are used for one thing:
the weekly stage tracker, which keeps last week's permit number and milestone pairs sealed with tools/data_box.py
(PNF_DATA_KEY) in state.sealed.json, so the page can say how many jobs moved stage, never which ones. Without the key the
tracker is skipped and the page simply has no moves line.

Usage: python3 tools/dp_pipeline_data.py            pull and write the data file
       python3 tools/dp_pipeline_data.py --selftest  planted rows, no network
"""
import argparse, datetime as dt, json, os, sys, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "site", "datapages", "dp_pipeline")
OUT = os.path.join(OUT_DIR, "data.json")
STATE = os.path.join(OUT_DIR, "state.sealed.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "ydr8-5enu"
DATASET_PAGE = f"{PORTAL}/Buildings/Building-Permits/{DATASET}"
CHI = ZoneInfo("America/Chicago")
UA = {"User-Agent": "ProofNotFluff data page (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
KEEP = ("permit_", "permit_type", "permit_status", "permit_milestone", "issue_date", "reported_cost", "community_area")
SINCE = "2021-01-01"
MIN_COST = 500000
TYPES = {"PERMIT - NEW CONSTRUCTION": "new", "PERMIT - RENOVATION/ALTERATION": "reno"}
CO_REQ = "INSPECTIONS (CERTIFICATE OF OCCUPANCY REQUIRED)"
CO_PEND = "CERTIFICATE OF OCCUPANCY PENDING"
CO_PART = "CERTIFICATE OF OCCUPANCY PENDING (TEMPORARY OR PARTIAL OCCUPANCY APPROVED)"
CO_DONE = "CERTIFICATE OF OCCUPANCY ISSUED"
OPEN = (CO_REQ, CO_PEND, CO_PART)
CO_PATH = OPEN + (CO_DONE,)
DEAD = ("SUSPENDED", "EXPIRED", "CANCELLED", "REVOKED")   # permit_status values that are not live jobs
BUCKETS = [(0, 183, "b0"), (183, 365, "b1"), (365, 730, "b2"), (730, 10 ** 6, "b3")]   # days since the permit was issued
HISTORY_WEEKS = 52


def strip(r):
    """Keep the seven columns this page counts; anything else on a row (contacts, address, location) is dropped here."""
    return {k: r.get(k) for k in KEEP}


def parse_day(s):
    try:
        return dt.date.fromisoformat((s or "")[:10])
    except ValueError:
        return None


def area_of(v):
    try:
        k = int(float(v))
    except (TypeError, ValueError):
        return 0
    return k if 1 <= k <= 77 else 0


def bucket(days):
    return next(key for lo, hi, key in BUCKETS if lo <= days < hi)


def empty():
    return {"open": 0, "b0": 0, "b1": 0, "b2": 0, "b3": 0, "partial": 0, "new": 0, "reno": 0}


def build(rows, today, fetched, rows_updated, names, prev_state=None, history=None):
    """rows: City rows (any columns; strip() keeps KEEP). Returns (data, state) where state maps permit number to milestone
    for every CO path permit, for next week's moves."""
    recs = []
    for r in map(strip, rows):
        typ, iss = TYPES.get((r["permit_type"] or "").strip().upper()), parse_day(r["issue_date"])
        try:
            cost = float(r["reported_cost"] or 0)
        except ValueError:
            cost = 0
        ms = (r["permit_milestone"] or "").strip().upper()
        if not typ or not iss or iss < dt.date.fromisoformat(SINCE) or iss > today or cost < MIN_COST or ms not in CO_PATH:
            continue
        recs.append({"p": (r["permit_"] or "").strip(), "t": typ, "iss": iss, "ms": ms, "a": area_of(r["community_area"]),
                     "dead": (r["permit_status"] or "").strip().upper() in DEAD})
    city, no_area, dead = empty(), 0, 0
    areas = {k: empty() for k in names}
    for x in recs:
        if x["ms"] == CO_DONE:
            continue
        if x["dead"]:
            dead += 1
            continue
        for tgt in [city] + ([areas[x["a"]]] if x["a"] in areas else []):
            tgt["open"] += 1
            tgt[x["t"]] += 1
            if x["ms"] == CO_PART:
                tgt["partial"] += 1
            else:
                tgt[bucket((today - x["iss"]).days)] += 1
        if x["a"] not in areas:
            no_area += 1
    cohorts = []
    for y in range(int(SINCE[:4]), today.year + 1):
        row = {"year": y}
        for t in ("new", "reno"):
            path = [x for x in recs if x["t"] == t and x["iss"].year == y]
            done = sum(1 for x in path if x["ms"] == CO_DONE)
            row[t] = {"path": len(path), "co": done, "share": round(done / len(path) * 100) if path else None}
        cohorts.append(row)
    state = {x["p"]: x["ms"] for x in recs if x["p"]}
    moves = None
    if prev_state is not None:
        moves = {"gotCo": 0, "toPartial": 0, "newOnPath": 0}
        for p, ms in state.items():
            was = prev_state.get(p)
            if was is None:
                moves["newOnPath"] += 1
            elif was != ms and ms == CO_DONE:
                moves["gotCo"] += 1
            elif was != ms and ms == CO_PART:
                moves["toPartial"] += 1
    week = (today - dt.timedelta(days=today.weekday())).isoformat()   # the Monday of this week
    hist = [h for h in (history or []) if h.get("week") != week]
    hist.append({"week": week, "open": city["open"], "b0": city["b0"], "b1": city["b1"], "b2": city["b2"], "b3": city["b3"],
                 "partial": city["partial"], "moves": moves})
    hist = sorted(hist, key=lambda h: h["week"])[-HISTORY_WEEKS:]
    data = {"schema": "pnf.dp_pipeline.v1",
            "source": {"dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched, "rowsUpdatedAt": rows_updated,
                       "since": SINCE, "minCost": MIN_COST},
            "asOf": today.isoformat(), "week": week,
            "city": dict(city, noArea=no_area, deadLeftOut=dead),
            "areas": [dict(areas[k], n=k, name=names[k]) for k in sorted(names)],
            "cohorts": cohorts, "history": hist}
    return data, state


def get(url, params):
    q = urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(f"{url}?{q}", headers=UA), timeout=180) as r:
        return json.load(r)


def fetch():
    where = (f"issue_date >= '{SINCE}T00:00:00' AND reported_cost >= {MIN_COST} AND "
             "permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')")
    rows, off = [], 0
    while True:
        page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": ",".join(KEEP), "$where": where, "$order": "permit_",
                                                          "$limit": 50000, "$offset": off})
        rows += page
        if len(page) < 50000:
            return rows
        off += 50000


def area_names():
    g = json.load(open(os.path.join(ROOT, "site", "geo", "chicago-community-areas.json"), encoding="utf-8"))
    return {int(a["n"]): a["name"] for a in g["areas"]}


def seal_state(state, key):
    sys.path.insert(0, HERE)
    import data_box
    return data_box.seal(json.dumps(state, sort_keys=True).encode("utf-8"), key)


def open_state(path, key):
    if not (key and os.path.isfile(path)):
        return None
    sys.path.insert(0, HERE)
    import data_box
    try:
        return json.loads(data_box.unseal(json.load(open(path, encoding="utf-8")), key).decode("utf-8"))
    except Exception as e:   # a damaged box or a rotated key: start the tracker again, say so in the log
        print(f"stage tracker: could not open last week's state ({type(e).__name__}); starting fresh")
        return None


def main():
    now = dt.datetime.now(CHI)
    meta = get(f"{PORTAL}/api/views/{DATASET}.json", {})
    rows_updated = dt.datetime.fromtimestamp(meta.get("rowsUpdatedAt", 0), CHI).isoformat(timespec="seconds")
    rows = fetch()
    key = os.environ.get("PNF_DATA_KEY", "")
    prev = open_state(STATE, key)
    old = json.load(open(OUT, encoding="utf-8")) if os.path.isfile(OUT) else {}
    data, state = build(rows, now.date(), now.isoformat(timespec="seconds"), rows_updated, area_names(), prev, old.get("history"))
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
        f.write("\n")
    if key:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(seal_state(state, key), f)
    c = data["city"]
    print(f"dp_pipeline: {len(rows):,} rows read, {c['open']:,} open CO path jobs ({c['partial']} partial occupancy), "
          f"{c['deadLeftOut']} suspended or expired left out, tracker {'on' if key else 'off (no PNF_DATA_KEY)'}, "
          f"moves {data['history'][-1]['moves']}")


def selftest():
    names = {6: "Lake View", 24: "West Town"}
    today = dt.date(2026, 10, 29)
    r = lambda p, t, ms, iss, cost="900000", a="6", st="ACTIVE", **kw: dict({"permit_": p, "permit_type": t, "permit_milestone": ms,
                                                                            "issue_date": iss + "T00:00:00.000", "reported_cost": cost,
                                                                            "community_area": a, "permit_status": st}, **kw)
    N, R = "PERMIT - NEW CONSTRUCTION", "PERMIT - RENOVATION/ALTERATION"
    rows = [r("1", N, CO_REQ, "2026-08-01", contact_1_name="PLANTED PERSON", street_name="PLANTED ST"),   # b0
            r("2", N, CO_REQ, "2026-01-15"),                       # b1 (287 days)
            r("3", R, CO_REQ, "2025-03-01", a="24"),               # b2
            r("4", N, CO_REQ, "2023-02-01"),                       # b3
            r("5", N, CO_PART, "2024-05-01", a="24"),              # partial
            r("6", N, CO_DONE, "2024-04-01"),                      # done, cohort 2024
            r("7", N, CO_REQ, "2024-06-01", st="EXPIRED"),         # dead: left out of open, still in cohort path
            r("8", N, "INSPECTIONS", "2026-02-01"),                # not on the CO path
            r("9", N, CO_REQ, "2026-03-01", cost="400000"),        # under $500,000
            r("10", "PERMIT - SIGNS", CO_REQ, "2026-03-01"),       # wrong type
            r("11", N, CO_REQ, "2026-05-01", a=None),              # no community area: city total only
            r("12", N, CO_REQ, "2020-12-31")]                      # before the window
    d, state = build(rows, today, "2026-10-29T07:00:00-05:00", "2026-10-28T06:00:00-05:00", names)
    c = d["city"]
    assert (c["open"], c["b0"], c["b1"], c["b2"], c["b3"], c["partial"]) == (6, 2, 1, 1, 1, 1), c
    assert c["noArea"] == 1 and c["deadLeftOut"] == 1 and c["new"] == 5 and c["reno"] == 1, c
    lv = next(a for a in d["areas"] if a["n"] == 6)
    wt = next(a for a in d["areas"] if a["n"] == 24)
    assert (lv["open"], wt["open"], wt["partial"]) == (3, 2, 1), (lv, wt)
    co24 = next(x for x in d["cohorts"] if x["year"] == 2024)["new"]
    assert co24 == {"path": 3, "co": 1, "share": 33}, co24
    assert "PLANTED" not in json.dumps(d) and '"permit_"' not in json.dumps(d) and '"1"' not in json.dumps(d["areas"]), "counts only"
    assert d["history"][-1]["moves"] is None and d["history"][-1]["week"] == "2026-10-26"
    rows2 = [dict(x) for x in rows]
    rows2[0]["permit_milestone"] = CO_PART      # 1 moved to partial occupancy
    rows2[1]["permit_milestone"] = CO_DONE      # 2 got its CO
    rows2.append(r("13", R, CO_REQ, "2026-10-20"))   # new on the path
    d2, _ = build(rows2, today + dt.timedelta(days=7), "x", "y", names, state, d["history"])
    assert d2["history"][-1]["moves"] == {"gotCo": 1, "toPartial": 1, "newOnPath": 1}, d2["history"][-1]
    assert [h["week"] for h in d2["history"]] == ["2026-10-26", "2026-11-02"], "one dated snapshot per week"
    d3, _ = build(rows2, today + dt.timedelta(days=8), "x", "y", names, state, d2["history"])
    assert len(d3["history"]) == 2, "a second run in the same week replaces that week's snapshot"
    print("dp_pipeline_data selftest: ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    if ap.parse_args().selftest:
        selftest()
    else:
        main()
