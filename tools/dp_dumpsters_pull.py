#!/usr/bin/env python3
"""Chicago dumpster permits: the data layer for the free page /chicago-dumpster-permits/ (site/pages.json kind
"datapage", module dp_dumpsters). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md,
research_notes/kimi-2026-10-27-r10.md item 10).

Runs in GitHub Actions (.github/workflows/dp_dumpsters.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Transportation Department Permits (dataset pubx-yq2d),
permit type DOT_DMPSTR (dumpster placement in the public way), issued permits only.

Privacy at ingest: the query asks the City for six fields only (KEEP below): issue date, status, latitude, longitude,
the record key used for paging and the permit number, which is used in memory to count a permit once (the City lists a
permit with several locations as several rows) and is never written. No primarycontact column (names, streets, cities, ZIPs of applicants), no
emergency contact, street address, project name or comment is ever requested, and any that arrived anyway are dropped
before a row is read (drop_people). Each point is joined to one of the 77 community areas by its latitude and longitude
(site/geo/chicago-community-areas.json) and only counts are written: site/datapages/dp_dumpsters/counts.json.

Usage: python3 tools/dp_dumpsters_pull.py            pull and write counts.json
       python3 tools/dp_dumpsters_pull.py --selftest  planted rows, no network
"""
import datetime as dt, json, os, sys, time, urllib.parse, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "datapages", "dp_dumpsters", "counts.json")
GEO = os.path.join(ROOT, "site", "geo", "chicago-community-areas.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "pubx-yq2d"
DATASET_PAGE = f"{PORTAL}/Transportation/Transportation-Department-Permits/{DATASET}"
TYPE = "DOT_DMPSTR"
KEEP = ["uniquekey", "applicationnumber", "applicationissueddate", "applicationstatus", "latitude", "longitude"]
CHI = ZoneInfo("America/Chicago")
UA = {"User-Agent": "ProofNotFluff data pages (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
PAGE = 50000


def drop_people(row):
    """Only the KEEP fields survive; anything about a person (primarycontact*, emergencycontactname, street fields,
    applicationname, comments) is dropped before the row is used."""
    return {k: row[k] for k in KEEP if k in row}


def soql(params):
    url = f"{PORTAL}/resource/{DATASET}.json?" + urllib.parse.urlencode(params)
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                return json.load(r)
        except Exception as e:   # noqa: BLE001
            print(f"try {i + 1}: {e}", file=sys.stderr)
            time.sleep(5 * (i + 1))
    raise SystemExit(f"the City's permit data did not answer: {url}")


def ts(t):
    return t.strftime("%Y-%m-%dT%H:%M:%S")


def windows(today):
    """Whole days ending at the start of `today` (the pull day is left out as incomplete)."""
    end = dt.datetime.combine(today, dt.time(0))
    yr = lambda t: t.replace(year=t.year - 1) if not (t.month == 2 and t.day == 29) else t.replace(year=t.year - 1, day=28)
    first = dt.datetime(today.year - 2, today.month, 1)          # 24 whole months before this one, plus this one
    return {"to": end, "from90": end - dt.timedelta(days=90), "prev90From": end - dt.timedelta(days=180),
            "yr90From": yr(end - dt.timedelta(days=90)), "yr90To": yr(end), "fromMonths": first}


def load_geo(path=GEO):
    g = json.load(open(path, encoding="utf-8"))
    areas = []
    for a in g["areas"]:
        rings = [r for poly in a["polys"] for r in poly]
        xs = [p[0] for r in rings for p in r]
        ys = [p[1] for r in rings for p in r]
        areas.append((a["n"], a["name"], rings, (min(xs), min(ys), max(xs), max(ys))))
    return areas, g["source"]


def inside(x, y, rings):
    c = False
    for r in rings:
        for i in range(len(r)):
            (x1, y1), (x2, y2) = r[i], r[i - 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
                c = not c
    return c


def area_of(lat, lon, areas):
    try:
        y, x = float(lat), float(lon)
    except (TypeError, ValueError):
        return 0
    for n, _, rings, (x0, y0, x1, y1) in areas:
        if x0 <= x <= x1 and y0 <= y <= y1 and inside(x, y, rings):
            return n
    return 0


def build(rows, areas, w, fetched, src_geo, statuses):
    """Distinct permits, not rows: the City lists a permit with several locations as several rows. A permit counts once
    citywide, and once in each community area where it has a location; one with no location inside any area counts only
    citywide (noArea)."""
    names = {n: name for n, name, _, _ in areas}
    city, by_area, where = {}, {}, {}          # bucket -> set of permit ids; permit id -> set of areas
    def add(bag, key, pid):
        bag.setdefault(key, set()).add(pid)
    for r in rows:
        r = drop_people(r)
        pid = r.get("applicationnumber") or ("row:" + str(r.get("uniquekey")))
        t = dt.datetime.fromisoformat(r["applicationissueddate"][:19])
        k = area_of(r.get("latitude"), r.get("longitude"), areas)
        where.setdefault(pid, set())
        if k:
            where[pid].add(k)
        keys = []
        if w["fromMonths"] <= t < w["to"]:
            keys.append("m" + t.strftime("%Y-%m"))
        for lo, hi, key in ((w["from90"], w["to"], "d90"), (w["prev90From"], w["from90"], "prev90"), (w["yr90From"], w["yr90To"], "yr90")):
            if lo <= t < hi:
                keys.append(key)
        for key in keys:
            add(city, key, pid)
            if k:
                add(by_area.setdefault(k, {}), key, pid)
    n_of = lambda bag, key: len(bag.get(key, ()))
    no_area = {"months": sum(1 for key, ids in city.items() if key.startswith("m") for pid in ids if not where[pid]),
               "d90": sum(1 for pid in city.get("d90", ()) if not where[pid])}
    multi90 = sum(1 for pid in city.get("d90", ()) if len(where[pid]) > 1)
    mlist = []
    m = w["fromMonths"]
    while m < w["to"]:
        mlist.append(m.strftime("%Y-%m"))
        m = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    out_areas = []
    for n in sorted(names):
        g = by_area.get(n, {})
        out_areas.append({"n": n, "name": names[n], "d90": n_of(g, "d90"), "prev90": n_of(g, "prev90"), "yr90": n_of(g, "yr90"),
                          "months": [n_of(g, "m" + x) for x in mlist]})
    for a in out_areas:   # rank 1 = most permits in the last 90 days; ties share a rank
        a["rank"] = 1 + sum(1 for b in out_areas if b["d90"] > a["d90"])
    return {"about": "Issued CDOT dumpster permits (DOT_DMPSTR), each permit counted once, by community area. Counts only; no name, address or record.",
            "source": {"name": "Transportation Department Permits", "dataset": DATASET, "url": DATASET_PAGE,
                       "type": TYPE, "issuedOnly": True, "fetchedAt": fetched, "join": "latitude and longitude to community area outlines",
                       "geo": src_geo, "statusesCounted": statuses, "unit": "distinct permit numbers", "rows": len(rows)},
            "window": {k: ts(v)[:10] for k, v in w.items()},
            "monthLabels": mlist, "partialMonth": mlist[-1] if w["to"].day != 1 else None,
            "city": {"months": [n_of(city, "m" + x) for x in mlist], "d90": n_of(city, "d90"), "prev90": n_of(city, "prev90"),
                     "yr90": n_of(city, "yr90"), "noArea": no_area, "multiArea90": multi90},
            "areas": out_areas}


def main():
    now = dt.datetime.now(CHI)
    w = windows(now.date())
    areas, src_geo = load_geo()
    lo = min(w["fromMonths"], w["yr90From"])
    base = f"applicationtype = '{TYPE}' AND applicationissueddate IS NOT NULL"
    span = f" AND applicationissueddate >= '{ts(lo)}' AND applicationissueddate < '{ts(w['to'])}'"
    st = soql({"$select": "applicationstatus, count(*) AS n", "$where": base + span, "$group": "applicationstatus", "$limit": 100})
    statuses = {(x.get("applicationstatus") or "(blank)"): int(float(x["n"])) for x in st}
    probe = soql({"$select": "applicationtype, applicationdescription, worktype, worktypedescription, count(*) AS n",
                  "$where": "upper(applicationdescription) like '%DUMPSTER%' OR applicationtype like '%DMP%' OR worktype like '%DMP%'",
                  "$group": "applicationtype, applicationdescription, worktype, worktypedescription", "$limit": 100})
    rows, off = [], 0
    while True:
        page = soql({"$select": ", ".join(KEEP), "$where": base + span, "$order": "uniquekey", "$limit": PAGE, "$offset": off})
        rows += [drop_people(r) for r in page]
        if len(page) < PAGE:
            break
        off += PAGE
    expect = sum(statuses.values())
    if len(rows) != expect:
        raise SystemExit(f"paging gave {len(rows)} rows, the City's count is {expect}")
    d = build(rows, areas, w, now.strftime("%Y-%m-%dT%H:%M:%S%z"), src_geo, statuses)
    d["source"]["typeProbe"] = probe   # permit type and sub-type labels with counts (no rows), to confirm the filter
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1)
    print(json.dumps({"rows": len(rows), "statuses": statuses, "city": d["city"], "months": d["monthLabels"][-3:]}, indent=1))


def selftest():
    sq = [[[-87.70, 41.90], [-87.60, 41.90], [-87.60, 41.95], [-87.70, 41.95], [-87.70, 41.90]]]
    areas = [(6, "Lake View", sq, (-87.70, 41.90, -87.60, 41.95))]
    assert area_of("41.92", "-87.65", areas) == 6 and area_of("41.80", "-87.65", areas) == 0 and area_of(None, None, areas) == 0
    row = {"uniquekey": "1", "applicationnumber": "P1", "applicationissueddate": "2026-10-20T09:00:00.000", "applicationstatus": "Open",
           "latitude": "41.92", "longitude": "-87.65", "primarycontactlast": "SMITH", "primarycontactfirst": "JO",
           "primarycontactstreet": "1 MAIN ST", "emergencycontactname": "X", "streetname": "MAIN", "comments": "hi"}
    kept = drop_people(row)
    assert set(kept) <= set(KEEP) and not any(k.startswith("primarycontact") for k in kept), "people dropped at ingest"
    assert not any(k.startswith("primarycontact") or k in ("emergencycontactname", "comments", "applicationname") for k in KEEP)
    w = windows(dt.date(2026, 10, 27))
    rows = [row, dict(row, uniquekey="1b"),   # the same permit at a second location: counted once
            dict(row, applicationnumber="P2", applicationissueddate="2025-10-20T09:00:00.000"),
            dict(row, applicationnumber="P3", applicationissueddate="2026-06-01T09:00:00.000"),
            dict(row, applicationnumber="P4", latitude="41.0", applicationissueddate="2026-10-01T09:00:00.000")]
    d = build(rows, areas, w, "2026-10-27T06:00:00-0500", {}, {"Open": 4})
    a = d["areas"][0]
    assert (a["d90"], a["yr90"], a["prev90"], a["rank"]) == (1, 1, 1, 1), a
    assert d["city"]["d90"] == 2 and d["city"]["noArea"]["d90"] == 1, d["city"]
    assert d["monthLabels"][0] == "2024-10" and d["monthLabels"][-1] == "2026-10" and d["partialMonth"] == "2026-10"
    assert sum(a["months"]) == 3 and sum(d["city"]["months"]) == 4
    s = json.dumps(d)
    assert "SMITH" not in s and "MAIN" not in s and "uniquekey" not in s and "P1" not in s, "counts only, no permit number"
    print("dp_dumpsters_pull selftest: ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
