#!/usr/bin/env python3
"""Chicago repair demand by trade: the data layer for the free page /chicago-repair-demand/ (site/pages.json kind
"datapage", module tools/dp_repairs.py). Todd's go, Oct 27, 2026 ("Let's do them all", coo/PARALLEL_BUILDS.md,
build B8; research_notes/kimi-2026-10-27-r10.md item 14).

Runs in GitHub Actions (.github/workflows/dp_repairs.yml), because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Building Violations (dataset 22u3-xenr). Each violation the
Department of Buildings records is sorted into a trade with the published hand mapping
site/datapages/dp_repairs/trade-map.json (violation code first, then the City's code series), and counted by the month
of its violation date and its community area.

The dataset has no community area column, so the runner places each violation's map point inside the City's
community area outlines (site/geo/chicago-community-areas.json). Points, addresses and codes stay on the runner: only
counts per trade, area and month, and counts per violation code citywide, are written. No address, location,
inspector, comment or property detail is ever kept.

Each daily run pulls the last 3 months again and keeps the older months from the committed file; the 1st of each
month, a missing file, a changed mapping or --full pulls everything again.

Usage: python3 tools/dp_repairs_data.py            pull and write site/datapages/dp_repairs/monthly.json
       python3 tools/dp_repairs_data.py --full
       python3 tools/dp_repairs_data.py --selftest  planted shapes and rows, no network
"""
import argparse, datetime as dt, hashlib, json, os, sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "site", "datapages", "dp_repairs")
OUT = os.path.join(DIR, "monthly.json")
MAPF = os.path.join(DIR, "trade-map.json")
GEO = os.path.join(ROOT, "site", "geo", "chicago-community-areas.json")
PORTAL = "https://data.cityofchicago.org"
DATASET = "22u3-xenr"
DATASET_PAGE = f"{PORTAL}/Buildings/Building-Violations/{DATASET}"
CHI = ZoneInfo("America/Chicago")
YEARS = 4          # months kept: the last 4 calendar years and this one
REPULL = 3
PAGE = 50000


def month_list(first, last):
    y, m = map(int, first.split("-"))
    out = []
    while f"{y:04d}-{m:02d}" <= last:
        out.append(f"{y:04d}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def next_month(ym):
    y, m = map(int, ym.split("-"))
    return f"{y + 1:04d}-01" if m == 12 else f"{y:04d}-{m + 1:02d}"


def load_map(path=MAPF):
    m = json.load(open(path, encoding="utf-8"))
    m["_hash"] = hashlib.sha256(json.dumps({k: m[k] for k in ("trades", "codes", "prefixes")}, sort_keys=True).encode()).hexdigest()[:12]
    return m


def trade_of(m, code):
    """The published mapping: a violation code listed in it wins, then the City code series the code starts with
    (EV elevator, BR boiler, VT ventilation, RF refrigeration, PL plumbing, EL electrical); anything else is "other"."""
    c = (code or "").strip().upper()
    if c in m["codes"]:
        return m["codes"][c]["trade"]
    for p, v in m["prefixes"].items():
        if c.startswith(p):
            return v["trade"]
    return "other"


class Areas:
    """Point in community area, with a bounding box first. Outer ring in, holes out."""

    def __init__(self, geo):
        self.shapes = []
        for a in geo["areas"]:
            for poly in a["polys"]:
                xs = [p[0] for p in poly[0]]
                ys = [p[1] for p in poly[0]]
                self.shapes.append((a["n"], (min(xs), min(ys), max(xs), max(ys)), poly))

    @staticmethod
    def _in(x, y, r):
        c = False
        for i in range(len(r)):
            (x1, y1), (x2, y2) = r[i], r[i - 1]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
                c = not c
        return c

    def find(self, lon, lat):
        for n, (x0, y0, x1, y1), poly in self.shapes:
            if x0 <= lon <= x1 and y0 <= lat <= y1 and self._in(lon, lat, poly[0]) and not any(self._in(lon, lat, h) for h in poly[1:]):
                return n
        return 0


def fold(rows, m, areas):
    """Grouped rows (violation_code, violation_description, latitude, longitude, n) -> {trade: {area: n}}, {code: n},
    {code: the City's description}."""
    out, codes, desc = {}, {}, {}
    for r in rows:
        n = int(float(r.get("n") or 0))
        t = trade_of(m, r.get("violation_code"))
        try:
            k = areas.find(float(r["longitude"]), float(r["latitude"]))
        except (KeyError, TypeError, ValueError):
            k = 0          # no map point on the record
        out.setdefault(t, {})
        out[t][k] = out[t].get(k, 0) + n
        c = (r.get("violation_code") or "").strip().upper()
        codes[c] = codes.get(c, 0) + n
        if r.get("violation_description"):
            desc.setdefault(c, r["violation_description"].strip())
    return out, codes, desc


def assemble(per, months, through, fetched, m):
    trades = [t["key"] for t in m["trades"]] + ["other"]
    out = {"about": "Counts only: City of Chicago building violations by trade (published mapping trade-map.json), community area and month. "
                    "No address, location, inspector, comment or property detail is kept. Built by tools/dp_repairs_data.py.",
           "source": {"name": "Building Violations", "dataset": DATASET, "url": DATASET_PAGE, "fetchedAt": fetched, "dateField": "violation_date"},
           "mapping": m["_hash"], "months": months, "through": through, "series": {}, "codes": {}, "desc": {}}
    for t in trades:
        area = {str(n): [] for n in range(1, 78)}
        city, noarea = [], []
        for ym in months:
            a = per.get(ym, ({}, {}, {}))[0].get(t, {})
            for n in range(1, 78):
                area[str(n)].append(a.get(n, 0))
            city.append(sum(a.values()))
            noarea.append(a.get(0, 0))
        out["series"][t] = {"area": area, "city": city, "noArea": noarea}
    for ym in months:
        tr, cs, ds = per.get(ym, ({}, {}, {}))
        for c, n in cs.items():
            out["codes"].setdefault(c, [0] * len(months))[months.index(ym)] += n
        for c, t in ds.items():
            out["desc"].setdefault(c, t)
    out["codes"] = dict(sorted(out["codes"].items()))
    out["desc"] = {c: out["desc"][c] for c in sorted(out["desc"])}
    return out


def unpack(old, months):
    per = {}
    if not old:
        return per
    for i, ym in enumerate(old["months"]):
        if ym not in months:
            continue
        tr = {}
        for t, s in old["series"].items():
            a = {int(n): v[i] for n, v in s["area"].items() if v[i]}
            if s["noArea"][i]:
                a[0] = s["noArea"][i]
            if a:
                tr[t] = a
        per[ym] = (tr, {c: v[i] for c, v in old["codes"].items() if v[i]}, {c: old["desc"][c] for c, v in old["codes"].items() if v[i] and c in old.get("desc", {})})
    return per


def pull(full=False):
    sys.path.insert(0, HERE)
    from permits_chicago import get
    m = load_map()
    areas = Areas(json.load(open(GEO, encoding="utf-8")))
    now = dt.datetime.now(CHI)
    today = now.date()
    last_day = today - dt.timedelta(days=1)
    months = month_list(f"{today.year - YEARS}-01", last_day.isoformat()[:7])
    old = None
    if os.path.isfile(OUT) and not full and today.day != 1:
        old = json.load(open(OUT, encoding="utf-8"))
        if old.get("mapping") != m["_hash"]:
            old = None
    per = unpack(old, months)
    redo = [ym for ym in months if ym not in per] + [ym for ym in months[-REPULL:] if ym in per]
    api = f"{PORTAL}/resource/{DATASET}.json"
    for ym in sorted(set(redo)):
        a, b = ym + "-01", min(next_month(ym) + "-01", today.isoformat())
        rows, off = [], 0
        while True:
            page = get(api, {"$select": "violation_code, violation_description, latitude, longitude, count(*) AS n",
                             "$where": f"violation_date >= '{a}T00:00:00' AND violation_date < '{b}T00:00:00'",
                             "$group": "violation_code, violation_description, latitude, longitude",
                             "$order": "violation_code, violation_description, latitude, longitude", "$limit": PAGE, "$offset": off})
            rows += page
            if len(page) < PAGE:
                break
            off += PAGE
        per[ym] = fold(rows, m, areas)
    d = assemble(per, months, last_day.isoformat(), now.strftime("%Y-%m-%dT%H:%M:%S%z"), m)
    tot12 = sum(sum(s["city"][-13:-1]) for s in d["series"].values())
    if tot12 < 20000:
        raise SystemExit(f"only {tot12} violations in 12 months: the query or the dataset changed; not writing")
    json.dump(d, open(OUT, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
    print(f"repairs: {months[0]} to {months[-1]} (pulled {len(set(redo))} months), through {d['through']}, 12 months {tot12:,}, "
          f"other share {sum(d['series']['other']['city'][-13:-1]) / tot12:.1%}, no area {sum(sum(s['noArea'][-13:-1]) for s in d['series'].values()):,}")


def selftest():
    m = {"trades": [{"key": "masonry"}, {"key": "hvac"}], "codes": {"CN061014": {"trade": "masonry"}, "BR2010": {"trade": "other"}},
         "prefixes": {"BR": {"trade": "hvac"}}, "_hash": "x"}
    assert trade_of(m, " cn061014 ") == "masonry" and trade_of(m, "BR3055") == "hvac" and trade_of(m, "BR2010") == "other" and trade_of(m, "") == "other"
    sq = lambda x, y: [[x, y], [x + 1, y], [x + 1, y + 1], [x, y + 1], [x, y]]
    hole = [[0.4, 0.4], [0.6, 0.4], [0.6, 0.6], [0.4, 0.6], [0.4, 0.4]]
    geo = {"areas": [{"n": 6, "name": "Lake View", "polys": [[sq(0, 0), hole]]}, {"n": 7, "name": "Lincoln Park", "polys": [[sq(1, 0)]]}]}
    A = Areas(geo)
    assert A.find(0.2, 0.2) == 6 and A.find(1.5, 0.5) == 7 and A.find(0.5, 0.5) == 0 and A.find(5, 5) == 0, "inside, hole, outside"
    rows = [{"violation_code": "CN061014", "violation_description": "REPAIR EXTERIOR WALL", "latitude": "0.2", "longitude": "0.2", "n": "3"},
            {"violation_code": "BR3055", "violation_description": "REPLACE", "latitude": "0.5", "longitude": "1.5", "n": "2"},
            {"violation_code": "ZZ", "n": "4"}]
    tr, codes, desc = fold(rows, m, A)
    assert tr == {"masonry": {6: 3}, "hvac": {7: 2}, "other": {0: 4}} and codes == {"CN061014": 3, "BR3055": 2, "ZZ": 4}, (tr, codes)
    assert desc == {"CN061014": "REPAIR EXTERIOR WALL", "BR3055": "REPLACE"}
    per = {"2026-09": (tr, codes, desc)}
    d = assemble(per, ["2026-09", "2026-10"], "2026-10-26", "x", m)
    assert d["series"]["masonry"]["area"]["6"] == [3, 0] and d["series"]["other"]["noArea"] == [4, 0] and d["codes"]["BR3055"] == [2, 0]
    assert unpack(d, ["2026-09", "2026-10"])["2026-09"] == (tr, codes, desc), "round trip"
    assert "2025-01" not in unpack(d, ["2026-10"]), "months that fall out of the window are dropped"
    assert month_list("2022-11", "2023-02") == ["2022-11", "2022-12", "2023-01", "2023-02"]
    js = json.dumps({k: v for k, v in d.items() if k != "about"})
    assert all(x not in js for x in ("address", "latitude", "longitude", "inspector", "comments")), "counts only"
    real = load_map()
    keys = {t["key"] for t in real["trades"]} | {"other"}
    assert all(v["trade"] in keys for v in real["codes"].values()) and all(v["trade"] in keys for v in real["prefixes"].values()), "mapping names known trades"
    assert trade_of(real, "CN070024") == "carpentry" and trade_of(real, "EV1110") == "elevator" and trade_of(real, "VT1010") == "other"
    print("dp_repairs_data selftest: ok (mapping, point in area with holes, fold, assemble, round trip, counts only)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--full", action="store_true")
    x = ap.parse_args()
    selftest() if x.selftest else pull(x.full)
