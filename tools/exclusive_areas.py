#!/usr/bin/env python3
"""Exclusive-area counts (Todd, live chat, Oct 26, 2026: "Count from our own permit data how many new qualifying projects
each area gets a month, and draw the areas so each has 10 or more"; coo/DECISIONS-2026-10-26.md).

Runs in GitHub Actions (.github/workflows/exclusive-areas.yml) because the cloud agents cannot reach data.cityofchicago.org.
Writes counts only, never a business or person's name:

  permits/chicago/area_counts.json          qualifying construction cleaning projects by community area and issue month,
                                            the same rules as the weekly list (tools/permits_chicago.py decide, builders,
                                            dedupe), every City status, so a month counts the jobs that started in it;
                                            plus the open jobs the list holds today, by area
  permits/licenses-chicago/area_counts.json new business licenses by community area and month (tools/licenses_chicago.py
                                            build and its buildings check), all trades and street-level storefronts
  permits/chicago/community_areas.json      the City's 77 community areas: simplified outline, centre and neighbours,
                                            for drawing territories and the map (public City boundaries)

Usage: python3 tools/exclusive_areas.py [--months 12]
       python3 tools/exclusive_areas.py --selftest
"""
import argparse, collections, datetime as dt, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import permits_chicago as pc  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PERMIT_OUT = os.path.join(ROOT, "permits", "chicago", "area_counts.json")
LIC_OUT = os.path.join(ROOT, "permits", "licenses-chicago", "area_counts.json")
GEO_OUT = os.path.join(ROOT, "permits", "chicago", "community_areas.json")

# A unit that puts a business above the street: a floor 2 or higher, or a suite or unit numbered 200 or more ("STE 1200",
# "20TH 2021", "FL 3"). A blank unit, "1ST FL", "STORE 2", "UNIT C" or "STE 101" stays street level.
UPPER_UNIT = re.compile(r"\b([2-9]|[1-9]\d)(?:ST|ND|RD|TH)?\s*(?:FL|FLR|FLOOR)\b|\b(?:FL|FLR|FLOOR)\s*([2-9]|[1-9]\d)\b|"
                        r"(?:\b(?:STE|SUITE|SUIT|UNIT|RM|ROOM)|#)\s*#?\s*([2-9]\d\d+|[1-9]\d{3,})\b|^([2-9]\d\d|[1-9]\d{3,})$|"
                        r"\b([2-9]|[1-9]\d)(?:ST|ND|RD|TH)\b", re.I)
STREET_SEGMENTS = {"food", "beauty", "auto", "venue", "retail", "care"}


def months_back(today, n):
    """The n whole months before today's month, oldest first, as YYYY-MM, plus today's month (partial)."""
    y, m = today.year, today.month
    out = []
    for _ in range(n):
        m -= 1
        if m == 0:
            y, m = y - 1, 12
        out.append(f"{y:04d}-{m:02d}")
    return sorted(out), f"{today.year:04d}-{today.month:02d}"


def street_level(unit):
    return not UPPER_UNIT.search((unit or "").strip())


# ------------------------------------------------------------------------------------------- geometry
def simplify(ring, tol):
    """Douglas-Peucker on [lon, lat] points (degrees); keeps the first and last point."""
    if len(ring) < 4:
        return ring
    def dist(p, a, b):
        (x, y), (x1, y1), (x2, y2) = p, a, b
        dx, dy = x2 - x1, y2 - y1
        if dx == 0 and dy == 0:
            return math.hypot(x - x1, y - y1)
        t = max(0, min(1, ((x - x1) * dx + (y - y1) * dy) / (dx * dx + dy * dy)))
        return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))
    keep = [False] * len(ring)
    keep[0] = keep[-1] = True
    stack = [(0, len(ring) - 1)]
    while stack:
        i, j = stack.pop()
        best, k = 0, None
        for n in range(i + 1, j):
            d = dist(ring[n], ring[i], ring[j])
            if d > best:
                best, k = d, n
        if k is not None and best > tol:
            keep[k] = True
            stack += [(i, k), (k, j)]
    return [p for p, f in zip(ring, keep) if f]


def ring_area_centroid(ring):
    a = cx = cy = 0.0
    for i in range(len(ring)):
        x1, y1 = ring[i - 1]
        x2, y2 = ring[i]
        c = x1 * y2 - x2 * y1
        a += c; cx += (x1 + x2) * c; cy += (y1 + y2) * c
    if not a:
        return 0.0, ring[0]
    return a / 2, (cx / (3 * a), cy / (3 * a))


def neighbours(areas, places=5):
    """{name: sorted names}: two areas are neighbours when their outlines share two or more points (the City's boundary file
    draws shared edges with the same points)."""
    pts = {n: {(round(x, places), round(y, places)) for ring in rings for x, y in ring} for n, rings in areas}
    out = {n: [] for n, _ in areas}
    names = [n for n, _ in areas]
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if len(pts[a] & pts[b]) >= 2:
                out[a].append(b); out[b].append(a)
    return {k: sorted(v) for k, v in out.items()}


def geo(areas_full, numbers):
    nb = neighbours(areas_full)
    out = []
    for name, rings in areas_full:
        big = max(rings, key=lambda r: abs(ring_area_centroid(r)[0])) if rings else []
        _, (cx, cy) = ring_area_centroid(big) if big else (0, (0, 0))
        out.append({"name": name, "number": numbers.get(name), "centre": [round(cx, 5), round(cy, 5)],
                    "neighbours": nb.get(name, []),
                    "rings": [[[round(x, 5), round(y, 5)] for x, y in simplify(r, 0.0006)] for r in rings]})
    return sorted(out, key=lambda a: a["number"] or 999)


# ------------------------------------------------------------------------------------------- permits
def permit_records(rows, area_name):
    """The weekly list's rules (decide, a business as general contractor, a revision counted once) on every City row, open or
    closed. Returns kept dicts with issued, communityArea and open."""
    kept = []
    for r in rows:
        desc = (r.get("work_description") or "").upper().replace("¿", " ")
        ok, _ = pc.decide(desc, r.get("permit_type") or "")
        if not ok:
            continue
        names = [r.get(f"contact_{n}_name") or "" for n in range(1, 16)
                 if "GENERAL CONTRACTOR" in (r.get(f"contact_{n}_type") or "").upper()
                 and "OWNER" not in (r.get(f"contact_{n}_type") or "").upper()]
        if not pc.builders(names):
            continue
        rev, ref = pc.refs(desc)
        kept.append({"permit": r.get("permit_") or r.get("id"), "issued": (r.get("issue_date") or "")[:10],
                     "address": pc.street(r), "cost": float(r.get("reported_cost") or 0), "_rev": rev, "_ref": ref,
                     "communityArea": area_name(r), "open": pc.is_open(r.get("permit_status"))})
    kept, _ = pc.dedupe(kept)
    return kept


def tally(recs, months, now_month, key=lambda r: True):
    by = collections.defaultdict(collections.Counter)
    for r in recs:
        if key(r):
            by[r["communityArea"] or "(no area on the City record)"][r["issued"][:7]] += 1
    out = {}
    for a, c in by.items():
        full = [c.get(m, 0) for m in months]
        out[a] = {"byMonth": {m: c.get(m, 0) for m in months + [now_month]}, "total12": sum(full),
                  "avg": round(sum(full) / len(months), 2), "low": min(full), "monthsUnder10": sum(1 for x in full if x < 10)}
    return dict(sorted(out.items(), key=lambda kv: -kv[1]["total12"]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--months", type=int, default=12)
    a = ap.parse_args()
    import licenses_chicago as lc
    from inspections_chicago import load_areas, area_of
    now = lc.chicago_now()
    today = now.date()
    months, now_month = months_back(today, a.months)
    since = months[0] + "-01"
    areas_full = load_areas()
    if len(areas_full) < 70:
        raise SystemExit(f"community areas did not load ({len(areas_full)})")
    numbers = {}
    try:
        for r in pc.get(f"{pc.PORTAL}/resource/{pc.AREAS}.json", {"$select": "area_numbe,community", "$limit": 200}):
            nm = (r.get("community") or "").title()
            numbers[pc.AREA_NAMES.get(nm, nm)] = int(float(r.get("area_numbe") or 0))
    except SystemExit:
        pass
    by_number = {str(v): k for k, v in numbers.items()}

    def area_name(r):
        ca = str(r.get("community_area") or "").split(".")[0]
        return by_number.get(ca) or area_of(r.get("latitude"), r.get("longitude"), areas_full)

    # permits: the weekly list's query from the first day of the first month
    where = (f"issue_date >= '{since}T00:00:00' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION') "
             f"AND reported_cost >= 500000")
    rows, off = [], 0
    while True:
        page = pc.get(f"{pc.PORTAL}/resource/{pc.DATASET}.json", {"$where": where, "$order": "issue_date DESC", "$limit": 5000, "$offset": off})
        rows += page
        if len(page) < 5000:
            break
        off += 5000
    recs = permit_records(rows, area_name)
    window_open = pc.window_start(dt.datetime.now(dt.timezone.utc))[:10]
    # open jobs the 24-month list holds today, by area (a second pull: the weekly list's own window)
    w24 = (f"issue_date >= '{window_open}T00:00:00' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION') "
           f"AND reported_cost >= 500000")
    rows24, off = [], 0
    while True:
        page = pc.get(f"{pc.PORTAL}/resource/{pc.DATASET}.json", {"$where": w24, "$order": "issue_date DESC", "$limit": 5000, "$offset": off})
        rows24 += page
        if len(page) < 5000:
            break
        off += 5000
    open24 = collections.Counter(r["communityArea"] or "(no area on the City record)"
                                 for r in permit_records(rows24, area_name) if r["open"])
    permits = {"schema": "pnf.areacounts.v1", "ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "source": pc.DATASET_PAGE, "months": months, "partialMonth": now_month,
               "rule": ("Qualifying projects as the weekly Chicago Construction Cleaning Leads list keeps them (new construction or "
                        "renovation, reported cost $500,000 or more, apartment buildings of 4+ units or commercial work, interior "
                        "finish or a new building, a business as general contractor, a revision counted once), counted by the "
                        "month the City issued the permit, whatever its status today. Community area from the City record, "
                        "else from its point."),
               "fetched": len(rows), "qualifying": sum(1 for r in recs if r["issued"][:7] in months),
               "areas": tally(recs, months, now_month),
               "openNow": {"windowFrom": window_open, "total": sum(open24.values()), "byArea": dict(open24.most_common())}}
    json.dump(permits, open(PERMIT_OUT, "w"), indent=1)

    # licenses: build() over the same months plus the buildings check (home and mail-drop addresses)
    lrows = lc.pull(since)
    lrecs, reasons = lc.build(lrows, areas_full, today, days=(today - dt.date.fromisoformat(since)).days)
    try:
        home, virtual = lc.fetch_buildings()
        drop = lc.flagged_buildings(lrecs, home, virtual)
        lrecs = [r for r in lrecs if r["license"] not in drop]
        bcheck = True
    except SystemExit:
        bcheck = False
    for r in lrecs:
        r["street"] = r["segment"] in STREET_SEGMENTS and street_level(lc.split_address(r.get("address"))[1])
    lic = {"schema": "pnf.areacounts.v1", "ranAt": permits["ranAt"], "source": lc.DATASET_PAGE, "months": months,
           "partialMonth": now_month, "buildingsCheck": bcheck,
           "rule": ("New business licenses as the weekly Chicago New Business Licenses list keeps them (tools/licenses_chicago.py "
                    "build: a new license at a business site, no person-named, home, mailbox, event or one-person licenses, one "
                    "row per site) plus its buildings check; the business-history check (it drops a handful of renewals a "
                    "month) is not run here. streetLevel: a site whose unit is not a floor 2+ or a suite 200+."),
           "fetched": len(lrows), "kept": len(lrecs),
           "bySegment": dict(collections.Counter(r["segment"] for r in lrecs if r["issued"][:7] in months)),
           "areasAll": tally(lrecs, months, now_month),
           "areasStreetLevel": tally(lrecs, months, now_month, key=lambda r: r["street"]),
           "areasStorefront": tally(lrecs, months, now_month, key=lambda r: r["street"] and r["segment"] in {"food", "beauty", "auto", "retail"})}
    json.dump(lic, open(LIC_OUT, "w"), indent=1)

    json.dump({"schema": "pnf.communityareas.v1", "source": f"{pc.PORTAL}/resource/{pc.AREAS}", "areas": geo(areas_full, numbers)},
              open(GEO_OUT, "w"), separators=(",", ":"))
    print(json.dumps({"permits": permits["qualifying"], "licenses": len(lrecs), "areas": len(areas_full)}))


def selftest():
    m, now = months_back(dt.date(2026, 10, 26), 12)
    assert m[0] == "2025-10" and m[-1] == "2026-09" and now == "2026-10" and len(m) == 12, m
    m, now = months_back(dt.date(2027, 1, 3), 2)
    assert m == ["2026-11", "2026-12"] and now == "2027-01", m
    for unit, want in [("", True), ("1ST FL", True), ("STORE 2", True), ("UNIT C", True), ("STE 101", True), ("1", True),
                       ("STE 1200", False), ("20TH 2021", False), ("FL 3", False), ("2ND FL", False), ("SUITE 450", False),
                       ("# 300", False), ("1500", False), ("B", True), ("REAR", True)]:
        assert street_level(unit) is want, (unit, want)
    sq = [[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]
    a, c = ring_area_centroid(sq)
    assert abs(abs(a) - 1) < 1e-9 and abs(c[0] - 0.5) < 1e-9 and abs(c[1] - 0.5) < 1e-9
    line = [[0, 0], [0.5, 0.00001], [1, 0], [1, 1], [0, 1], [0, 0]]
    assert [0.5, 0.00001] not in simplify(line, 0.001) and [1, 1] in simplify(line, 0.001)
    nb = neighbours([("A", [sq]), ("B", [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]), ("C", [[[5, 5], [6, 5], [6, 6], [5, 5]]])])
    assert nb == {"A": ["B"], "B": ["A"], "C": []}, nb
    recs = [{"communityArea": "Loop", "issued": "2025-10-03"}, {"communityArea": "Loop", "issued": "2026-10-01"},
            {"communityArea": "", "issued": "2026-01-09"}]
    t = tally(recs, ["2025-10", "2026-01"], "2026-10")
    assert t["Loop"]["total12"] == 1 and t["Loop"]["byMonth"]["2026-10"] == 1 and t["Loop"]["low"] == 0
    assert t["(no area on the City record)"]["total12"] == 1
    print("exclusive_areas selftest ok (22 planted cases)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
