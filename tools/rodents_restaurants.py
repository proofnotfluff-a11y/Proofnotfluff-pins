#!/usr/bin/env python3
"""Restaurant pest and ventilation index: the counts behind the extra map metric on /chicago-rat-complaints/ (Todd,
Oct 27, 2026, "Let's do them all", coo/DECISIONS-2026-10-27.md, R10 item 13). Counts only, never a restaurant name.

Runs in GitHub Actions (.github/workflows/rodents-chicago.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Food Inspections (dataset 4ijn-s7e5). The inspection
workflows commit no counts by community area (only named, sealed or sample files), so this file makes its own.

What is read, in the runner only: inspection date, facility type, result, the violations field and the latitude and
longitude. The point is placed in one of the 77 community areas (site/geo/chicago-community-areas.json) and then
dropped; names, license numbers, addresses, inspector notes and points never leave the runner.

What is counted, over the last 12 whole weeks (7-day buckets ending the day before the pull, as on the rat page):
- inspections: Food Inspections rows whose facility type names a restaurant and whose result is Pass, Pass w/
  Conditions or Fail (the City's "Out of Business", "No Entry" and "Not Ready" visits are not inspections of a kitchen);
- pest: those whose violations cite violation 38 (the City's code; its title is read from the rows and written out);
- vent: those that cite violation 56 with an inspector note naming a hood, filter, exhaust, ventilation, a vent or a
  fan (56 also covers lighting and designated areas, so a note about those alone does not count).
One inspection counts once in each column, however many items it cites. A place inspected twice counts twice.

Usage: python3 tools/rodents_restaurants.py            pull and write permits/rodents-chicago/restaurants.json
       python3 tools/rodents_restaurants.py --selftest  planted rows, no network
"""
import argparse, collections, datetime as dt, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rodents_chicago as R  # noqa: E402  (areas, windows, weeks)

OUT = os.path.join(ROOT, "permits", "rodents-chicago", "restaurants.json")
GEO = os.path.join(ROOT, "site", "geo", "chicago-community-areas.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "4ijn-s7e5"
DATASET_PAGE = f"{PORTAL}/Health-Human-Services/Food-Inspections/{DATASET}"
PEST, VENT = 38, 56
RESULTS = {"PASS", "PASS W/ CONDITIONS", "FAIL"}
VENT_WORDS = re.compile(r"\bHOODS?\b|FILTER|EXHAUST|VENTILAT|\bVENTS?\b|\bFANS?\b")
VIOLATION = re.compile(r"^\s*(\d{1,2})\.\s*(.*?)(?:\s+-\s+Comments:\s*(.*))?$", re.S)


def split_violations(text):
    """[(code, title, note)] from the City's violations field ('38. TITLE - Comments: ... | 41. ...')."""
    out = []
    for part in (text or "").split(" | "):
        m = VIOLATION.match(part.strip())
        if m:
            out.append((int(m.group(1)), m.group(2).strip(), (m.group(3) or "").upper()))
    return out


def classify(violations):
    """(pest, vent, {code: title}) for one inspection."""
    pest = vent = False
    titles = {}
    for code, title, note in split_violations(violations):
        if code == PEST:
            pest = True
            titles[PEST] = title
        if code == VENT:
            titles[VENT] = title
            if VENT_WORDS.search(note):
                vent = True
    return pest, vent, titles


def counted(r):
    return "RESTAURANT" in (r.get("facility_type") or "").upper() and (r.get("results") or "").strip().upper() in RESULTS


# ---------------------------------------------------------------- point in community area
def _in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i in range(len(ring)):
        xi, yi = ring[i]
        xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def locator(geo):
    """A function (lon, lat) -> community area number, or 0 outside every area. Holes are respected."""
    shapes = []
    for a in geo["areas"]:
        for poly in a["polys"]:
            xs = [p[0] for p in poly[0]]
            ys = [p[1] for p in poly[0]]
            shapes.append((a["n"], (min(xs), min(ys), max(xs), max(ys)), poly))

    def find(lon, lat):
        for n, (x0, y0, x1, y1), poly in shapes:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and _in_ring(lon, lat, poly[0]) and not any(_in_ring(lon, lat, h) for h in poly[1:]):
                return n
        return 0
    return find


def area_of(r, find):
    try:
        lat, lon = float(r.get("latitude")), float(r.get("longitude"))
    except (TypeError, ValueError):
        return 0
    return find(lon, lat)


# ---------------------------------------------------------------- the counts
def week_index(day, w):
    """0..11 for the 12 weeks ending w["to"] (oldest first), or None outside them."""
    k = (w["to"] - dt.datetime.combine(day, dt.time(0))).days
    if not 1 <= k <= 84:
        return None
    return 11 - (k - 1) // 7


def build(rows, w, find, fetched):
    blank = lambda: [[0, 0, 0] for _ in range(12)]
    per = collections.defaultdict(blank)           # area -> 12 x [inspections, pest, vent]
    titles = collections.defaultdict(collections.Counter)
    for r in rows:
        if not counted(r):
            continue
        try:
            day = dt.date.fromisoformat((r.get("inspection_date") or "")[:10])
        except ValueError:
            continue
        i = week_index(day, w)
        if i is None:
            continue
        pest, vent, t = classify(r.get("violations"))
        for code, title in t.items():
            titles[code][title] += 1
        cell = per[area_of(r, find)][i]
        cell[0] += 1
        cell[1] += pest
        cell[2] += vent
    weeks = []
    for i in range(12):
        a = w["to"] - dt.timedelta(days=7 * (12 - i))
        tot = [sum(per[k][i][j] for k in per) for j in range(3)]
        weeks.append({"from": a.strftime("%Y-%m-%d"), "to": (a + dt.timedelta(days=6)).strftime("%Y-%m-%d"),
                      "inspections": tot[0], "pest": tot[1], "vent": tot[2]})
    areas = []
    for k in sorted(R.AREAS):
        wk = per.get(k) or blank()
        areas.append({"n": k, "name": R.AREAS[k], "inspections": sum(x[0] for x in wk), "pest": sum(x[1] for x in wk),
                      "vent": sum(x[2] for x in wk), "weeks": wk})
    s = lambda j: sum(x[j] for x in weeks)
    title = lambda c: titles[c].most_common(1)[0][0] if titles[c] else None
    return {"about": "Counts only: City of Chicago food inspections of restaurants by community area and week. No name, license, address, point or inspector note is kept. Built by tools/rodents_restaurants.py.",
            "source": {"name": "Food Inspections", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched},
            "window": {"from": weeks[0]["from"], "to": weeks[-1]["to"]},
            "codes": {"pest": {"code": PEST, "title": title(PEST)}, "vent": {"code": VENT, "title": title(VENT)}},
            "counts": {"inspections": s("inspections"), "pest": s("pest"), "vent": s("vent"),
                       "noArea": sum(x[0] for x in (per.get(0) or blank()))},
            "weeks": weeks, "areas": areas}


def pull():
    from permits_chicago import get
    now = dt.datetime.now(R.CHI)
    w = R.windows(now.date())
    where = (f"inspection_date >= '{R.soql_time(w['from12w'])}' AND inspection_date < '{R.soql_time(w['to'])}' "
             "AND upper(facility_type) like '%RESTAURANT%'")
    rows, off = [], 0
    while True:
        page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": "inspection_date, facility_type, results, violations, latitude, longitude",
                                                         "$where": where, "$order": "inspection_date", "$limit": 5000, "$offset": off})
        rows += page
        if len(page) < 5000:
            break
        off += 5000
    geo = json.load(open(GEO, encoding="utf-8"))
    d = build(rows, w, locator(geo), now.strftime("%Y-%m-%dT%H:%M:%S%z"))
    del rows
    c = d["counts"]
    if c["inspections"] < 300 or not d["codes"]["pest"]["title"] or not d["codes"]["vent"]["title"]:
        raise SystemExit(f"restaurants: {c['inspections']} inspections or a missing violation title; the query or the dataset changed; not writing")
    if sum(a["inspections"] for a in d["areas"]) + c["noArea"] != c["inspections"]:
        raise SystemExit("restaurants: areas do not add up to the city total; not writing")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(d, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"restaurants: {c['inspections']} inspections in 12 weeks, pest {c['pest']}, vent {c['vent']}, no area {c['noArea']}; "
          f"38 = {d['codes']['pest']['title']!r}, 56 = {d['codes']['vent']['title']!r}")


def selftest():
    p, v, t = classify("38. INSECTS, RODENTS, & ANIMALS NOT PRESENT - Comments: MOUSE DROPPINGS | 56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED - Comments: CLEAN THE HOOD FILTERS")
    assert (p, v) == (True, True) and t[38].startswith("INSECTS") and t[56].startswith("ADEQUATE"), (p, v, t)
    assert classify("56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED - Comments: REPLACE BURNT OUT LIGHT BULB")[:2] == (False, False)
    assert classify("56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED")[:2] == (False, False), "56 with no note is not counted"
    assert classify("55. PHYSICAL FACILITIES - Comments: MICE SEEN | 41. WIPING CLOTHS - Comments: HOOD")[:2] == (False, False), "codes only"
    assert classify("")[:2] == (False, False)
    assert counted({"facility_type": "Restaurant", "results": "Pass w/ Conditions"}) and counted({"facility_type": "GAS STATION/RESTAURANT", "results": "Fail"})
    assert not counted({"facility_type": "School", "results": "Fail"}) and not counted({"facility_type": "Restaurant", "results": "Out of Business"})
    sq = {"areas": [{"n": 6, "name": "Lake View", "polys": [[[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]], [[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]]},
                    {"n": 24, "name": "West Town", "polys": [[[[4, 4], [6, 4], [6, 6], [4, 6], [4, 4]]]]}]}
    f = locator(sq)
    assert (f(1, 1), f(5, 5), f(20, 20)) == (6, 24, 0), "inside, inside the hole's own area, outside"
    w = R.windows(dt.date(2026, 10, 26))
    assert week_index(dt.date(2026, 10, 25), w) == 11 and week_index(dt.date(2026, 10, 19), w) == 11 and week_index(dt.date(2026, 10, 18), w) == 10
    assert week_index(dt.date(2026, 8, 3), w) == 0 and week_index(dt.date(2026, 8, 2), w) is None and week_index(dt.date(2026, 10, 26), w) is None
    mk = lambda day, lon, lat, viol, ft="Restaurant", res="Fail": {"inspection_date": f"{day}T00:00:00.000", "facility_type": ft, "results": res,
                                                                     "violations": viol, "latitude": str(lat), "longitude": str(lon),
                                                                     "dba_name": "PLANTED NAME", "address": "1 PLANTED ST"}
    pest = "38. INSECTS, RODENTS, & ANIMALS NOT PRESENT - Comments: ROACHES"
    hood = "56. ADEQUATE VENTILATION & LIGHTING; DESIGNATED AREAS USED - Comments: GREASY HOOD"
    rows = [mk("2026-10-25", 1, 1, pest + " | " + hood), mk("2026-10-24", 1, 1, ""), mk("2026-10-20", 5, 5, hood, res="Pass"),
            mk("2026-10-20", 50, 50, pest), mk("2026-10-20", 1, 1, pest, ft="School"), mk("2026-10-20", 1, 1, pest, res="No Entry"),
            mk("2026-08-03", 1, 1, pest), mk("2026-10-26", 1, 1, pest), {"inspection_date": "2026-10-21T00:00:00", "facility_type": "Restaurant", "results": "Pass", "violations": ""}]
    d = build(rows, w, f, "t")
    c = d["counts"]
    assert (c["inspections"], c["pest"], c["vent"], c["noArea"]) == (6, 3, 2, 2), c
    lv = next(a for a in d["areas"] if a["n"] == 6)
    assert (lv["inspections"], lv["pest"], lv["vent"], lv["weeks"][-1], lv["weeks"][0]) == (3, 2, 1, [2, 1, 1], [1, 1, 0]), lv
    assert d["weeks"][-1] == {"from": "2026-10-19", "to": "2026-10-25", "inspections": 5, "pest": 2, "vent": 2}, d["weeks"][-1]
    assert d["codes"]["pest"]["title"] == "INSECTS, RODENTS, & ANIMALS NOT PRESENT" and len(d["areas"]) == 77
    blob = json.dumps(d)
    assert "PLANTED" not in blob and "ROACHES" not in blob and "latitude" not in blob, "counts only: no name, address, note or point"
    print("rodents_restaurants selftest: ok (codes from the rows, 56 needs a vent note, restaurants only, completed inspections, "
          "point in area with holes, 12 weeks, counts only)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    selftest() if ap.parse_args().selftest else pull()
