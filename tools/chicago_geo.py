#!/usr/bin/env python3
"""Chicago community area outlines for the free and paid maps (Todd, live chat, Oct 27, 2026: "Interactive maps. This
should be available for both free and paid products").

Runs in GitHub Actions (.github/workflows/chicago-geo.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Boundaries - Community Areas (dataset igwz-8jzy), the same
77 areas tools/rodents_chicago.py and tools/inspections_chicago.py already use. Writes site/geo/chicago-community-areas.json:
area number, name and outline rings rounded to 5 decimals (about 1 meter) after a light Douglas-Peucker pass. Public
boundaries only; no person, address or record is in the file. The page builders (tools/geo_map.py) project and
simplify it further for each map.

Usage: python3 tools/chicago_geo.py            pull and write the file
       python3 tools/chicago_geo.py --selftest  planted shapes, no network
"""
import datetime as dt, json, os, sys, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "site", "geo", "chicago-community-areas.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "igwz-8jzy"
DATASET_PAGE = f"{PORTAL}/Facilities-Geographic-Boundaries/Boundaries-Community-Areas-current-/{DATASET}"
TOL = 0.00003     # degrees, about 3 meters: keeps every corner a map at city scale can show
UA = {"User-Agent": "ProofNotFluff maps (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}


def dp(pts, tol):
    """Douglas-Peucker on one ring (first point equals last). Keeps the end points."""
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = (dx * dx + dy * dy) ** 0.5
        best, at = -1.0, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            if d > best:
                best, at = d, i
        if at > 0 and best > tol:
            keep[at] = True
            stack += [(a, at), (at, b)]
    return [p for p, k in zip(pts, keep) if k]


def clean(gj):
    """GeoJSON FeatureCollection from the portal to {n: {"name", "polys": [[ring, hole...], ...]}}."""
    import rodents_chicago as R    # the 77 names, already checked against this dataset on Oct 26
    out = {}
    for f in gj.get("features", []):
        pr = f.get("properties") or {}
        try:
            n = int(float(pr.get("area_numbe") or pr.get("area_num_1") or pr.get("area_number") or 0))
        except (TypeError, ValueError):
            n = 0
        if n not in R.AREAS:
            raise SystemExit(f"unexpected community area number {pr.get('area_numbe')!r}")
        g = f.get("geometry") or {}
        polys = g.get("coordinates") or []
        if g.get("type") == "Polygon":
            polys = [polys]
        elif g.get("type") != "MultiPolygon":
            raise SystemExit(f"area {n}: geometry {g.get('type')!r}")
        kept = []
        for poly in polys:
            rings = [[[round(x, 5), round(y, 5)] for x, y in dp([tuple(p[:2]) for p in ring], TOL)] for ring in poly]
            rings = [r for r in rings if len(r) >= 4]
            if rings:
                kept.append(rings)
        out[n] = {"name": R.AREAS[n], "polys": kept}
    missing = sorted(set(R.AREAS) - set(out))
    if missing:
        raise SystemExit(f"community areas missing from the City file: {missing}")
    return out


def write(areas, fetched):
    doc = {"about": "Outlines of Chicago's 77 community areas, public City boundaries only. Built by tools/chicago_geo.py.",
           "source": {"name": "Boundaries - Community Areas", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched},
           "areas": [{"n": n, "name": a["name"], "polys": a["polys"]} for n, a in sorted(areas.items())]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    tmp = OUT + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, separators=(",", ":"))
    os.replace(tmp, OUT)
    return doc


def pull():
    req = urllib.request.Request(f"{PORTAL}/resource/{DATASET}.geojson?$limit=200", headers=UA)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def selftest():
    sys.path.insert(0, HERE)
    import rodents_chicago as R
    sq = [[0, 0], [0.5, 0.000001], [1, 0], [1, 1], [0, 1], [0, 0]]
    assert dp([tuple(p) for p in sq], 0.001) == [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)], "a near-straight point goes"
    feats = [{"properties": {"area_numbe": str(n), "community": nm.upper()},
              "geometry": {"type": "MultiPolygon" if n == 76 else "Polygon",
                           "coordinates": ([[sq]] if n == 76 else [sq])}} for n, nm in R.AREAS.items()]
    a = clean({"features": feats})
    assert len(a) == 77 and a[9]["name"] == "Edison Park" and len(a[76]["polys"]) == 1, "77 areas, names from our list"
    try:
        clean({"features": feats[:-1]})
        raise AssertionError("a missing area must stop the run")
    except SystemExit:
        pass
    try:
        clean({"features": feats + [{"properties": {"area_numbe": "99"}, "geometry": {"type": "Polygon", "coordinates": [sq]}}]})
        raise AssertionError("an unknown area number must stop the run")
    except SystemExit:
        pass
    print("chicago_geo selftest: ok")


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    if "--selftest" in sys.argv:
        selftest()
    else:
        doc = write(clean(pull()), dt.datetime.now(ZoneInfo("America/Chicago")).strftime("%Y-%m-%dT%H:%M:%S%z"))
        pts = sum(len(r) for a in doc["areas"] for p in a["polys"] for r in p)
        print(f"wrote {OUT}: {len(doc['areas'])} areas, {pts} points, {os.path.getsize(OUT):,} bytes")
