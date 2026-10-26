#!/usr/bin/env python3
"""Chicago Construction Cleaning Leads, area seats (Todd, live chat, Oct 26, 2026: "an exclusive-area version of Chicago
Construction Cleaning Leads. One cleaning company per area of Chicago; no other subscriber sees that area's leads";
coo/DECISIONS-2026-10-26.md, launches/chicago-cleaning-area-seats.md).

The territories live in site/area_seats.json: six groups of the City's 77 community areas, drawn from
permits/chicago/area_counts.json (tools/exclusive_areas.py) so each averages 10 or more new qualifying projects a month
and is one connected piece. This file is the one place that reads them:

  territory_of(area)          the territory slug for a community area name ("" when none)
  split(projects, cfg)        {slug: [projects]} for the seat lists, every project placed once
  shared(projects, cfg)       the projects the shared $29 list, the free page and outreach may show: every territory
                              whose seat is not held (held slugs in cfg["held"]); nothing changes while held is empty
  stats(cfg)                  per territory: 12-month total, monthly average, low and high month, months under 10,
                              open projects now, community areas (all from the committed counts)
  svg(cfg)                    the territory map (inline SVG, colours by territory, no tiles, no names of businesses)
  held_numbers(cfg)           the City's community area numbers inside held territories (tools/ingest_downstream.py
                              leaves those permits out of the public downstream leads file the cleaning emails draw on)
  password(key, slug)         a seat's members' password, derived from one secret (the AREA_SEAT_KEY Actions secret)
  city_for(t)                 the members' app and workbook settings for one seat (tools/leads_cities.py CHICAGO plus
                              the seat's name, its areas, its own storage key and the seat clause in the Terms)

Usage: python3 tools/area_seats.py --stats                    print the table
       python3 tools/area_seats.py --svg OUT.svg              write the map
       python3 tools/area_seats.py --shared IN OUT            the weekly full list without held territories (the $29 list)
       python3 tools/area_seats.py --shared-sample PATH       the free sample file, in place, without held territories
       python3 tools/area_seats.py --week-counts IN           permits/chicago/area_week.json: this week's counts per seat
       AREA_SEAT_KEY=... LEADS_PASSWORD=... python3 tools/area_seats.py --build IN
                                                              one members' app per seat, docs/chicago-cleaning-area-members/<slug>/
       python3 tools/area_seats.py --passwords                each seat's password from AREA_SEAT_KEY (the build session only;
                                                              never printed in a workflow or a log)
       python3 tools/area_seats.py --selftest
"""
import base64, datetime as dt, hashlib, hmac, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, "site", "area_seats.json")
COUNTS = os.path.join(ROOT, "permits", "chicago", "area_counts.json")
GEO = os.path.join(ROOT, "permits", "chicago", "community_areas.json")
WEEK = os.path.join(ROOT, "permits", "chicago", "area_week.json")
MEMBERS = os.path.join(ROOT, "docs", "chicago-cleaning-area-members")
OFFER_URL = "https://proofnotfluff.com/chicago-construction-cleaning-leads/#areas"


def load(path=CFG):
    return json.load(open(path))


def territory_of(area, cfg):
    for t in cfg["territories"]:
        if area in t["areas"]:
            return t["slug"]
    return ""


def check(cfg, geo):
    """Every community area in exactly one territory, each territory connected. Returns a list of problems."""
    names = {a["name"] for a in geo["areas"]}
    nb = {a["name"]: set(a["neighbours"]) for a in geo["areas"]}
    seen, bad = {}, []
    for t in cfg["territories"]:
        for a in t["areas"]:
            if a not in names:
                bad.append(f"{t['slug']}: {a} is not a City community area")
            if a in seen:
                bad.append(f"{a} is in {seen[a]} and {t['slug']}")
            seen[a] = t["slug"]
        mem = set(t["areas"]) & names
        if mem:
            start = sorted(mem)[0]; reach, stack = {start}, [start]
            while stack:
                x = stack.pop()
                for y in nb[x] & mem - reach:
                    reach.add(y); stack.append(y)
            if reach != mem:
                bad.append(f"{t['slug']} is not one connected piece ({len(reach)} of {len(mem)})")
    for a in sorted(names - set(seen)):
        bad.append(f"{a} is in no territory")
    for h in cfg.get("held", []):
        if h not in {t["slug"] for t in cfg["territories"]}:
            bad.append(f"held seat {h} is not a territory")
    return bad


def split(projects, cfg):
    out = {t["slug"]: [] for t in cfg["territories"]}
    for p in projects:
        s = territory_of(p.get("communityArea") or "", cfg)
        if s:
            out[s].append(p)
    return out


def shared(projects, cfg):
    """The shared list keeps a project unless its territory's seat is held. A project with no community area on the City
    record stays shared (it belongs to no seat)."""
    held = set(cfg.get("held", []))
    return [p for p in projects if territory_of(p.get("communityArea") or "", cfg) not in held]


def stats(cfg, counts=None):
    counts = counts or json.load(open(COUNTS))
    months = counts["months"]
    out = []
    for t in cfg["territories"]:
        ms = [sum(counts["areas"].get(a, {}).get("byMonth", {}).get(m, 0) for a in t["areas"]) for m in months]
        out.append({"slug": t["slug"], "name": t["name"], "total12": sum(ms), "avg": round(sum(ms) / len(ms), 1),
                    "low": min(ms), "high": max(ms), "under10": sum(1 for x in ms if x < 10), "byMonth": ms,
                    "openNow": sum(counts["openNow"]["byArea"].get(a, 0) for a in t["areas"]), "areas": len(t["areas"]),
                    "held": t["slug"] in set(cfg.get("held", []))})
    return {"months": months, "from": months[0], "to": months[-1], "ranAt": counts["ranAt"],
            "citywide12": counts["qualifying"], "openNow": counts["openNow"]["total"], "territories": out}


# ------------------------------------------------------------------------------------------------ the map
def _proj(geo, width):
    xs = [x for a in geo["areas"] for r in a["rings"] for x, _ in r]
    ys = [y for a in geo["areas"] for r in a["rings"] for _, y in r]
    lat0 = (min(ys) + max(ys)) / 2
    k = math.cos(math.radians(lat0))
    w = (max(xs) - min(xs)) * k
    s = width / w
    h = (max(ys) - min(ys)) * s
    return (lambda x, y: (round((x - min(xs)) * k * s, 1), round((max(ys) - y) * s, 1))), width, round(h, 1)


def svg(cfg, geo=None, st=None, width=420, title="Chicago cleaning lead areas"):
    """The territory map: each community area filled with its territory's colour token (CSS variables --t1 to --t6 with
    fallbacks), territory outlines drawn heavier, a numbered marker at each territory's centre. The page around it
    carries the legend in text, so the map is decorative to a screen reader beyond its title and description."""
    geo = geo or json.load(open(GEO))
    st = st or stats(cfg)
    f, w, h = _proj(geo, width)
    order = {t["slug"]: i for i, t in enumerate(cfg["territories"])}
    fills = ["#2f5f9e", "#c2603a", "#3d8a6b", "#8a5aa6", "#b38a1e", "#4f7f8f"]
    parts = []
    for a in geo["areas"]:
        s = territory_of(a["name"], cfg)
        i = order.get(s, -1)
        d = " ".join("M" + " L".join(f"{px},{py}" for px, py in (f(x, y) for x, y in r)) + " Z" for r in a["rings"])
        held = s in set(cfg.get("held", []))
        parts.append(f'<path d="{d}" fill="var(--t{i + 1},{fills[i] if i >= 0 else "#999"})" fill-opacity="{0.28 if held else 0.78}" '
                     f'stroke="var(--map-line,#fff)" stroke-width="0.6"><title>{a["name"]}</title></path>')
    # markers at the centre of each territory's busiest area
    counts = json.load(open(COUNTS))
    for t in cfg["territories"]:
        i = order[t["slug"]]
        busiest = max(t["areas"], key=lambda n: counts["areas"].get(n, {}).get("total12", 0))
        cx, cy = next(a["centre"] for a in geo["areas"] if a["name"] == t.get("marker", busiest))
        px, py = f(cx, cy)
        parts.append(f'<g aria-hidden="true"><circle cx="{px}" cy="{py}" r="10" fill="var(--map-pin,#14213d)" stroke="var(--map-line,#fff)" stroke-width="1.5"/>'
                     f'<text x="{px}" y="{round(py + 4.2, 1)}" text-anchor="middle" font-size="12" font-weight="700" fill="var(--map-pin-ink,#fff)" '
                     f'font-family="system-ui,sans-serif">{i + 1}</text></g>')
    desc = "; ".join(f"{i + 1} {t['name']}: about {s['avg']:g} new projects a month, {s['openNow']} open now"
                     for i, (t, s) in enumerate(zip(cfg["territories"], st["territories"])))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-labelledby="amap-t amap-d">'
            f'<title id="amap-t">{title}</title><desc id="amap-d">{desc}</desc>' + "".join(parts) + "</svg>")


def held_numbers(cfg, geo=None):
    geo = geo or json.load(open(GEO))
    held = set(cfg.get("held", []))
    names = {a for t in cfg["territories"] if t["slug"] in held for a in t["areas"]}
    return {str(a["number"]) for a in geo["areas"] if a["name"] in names and a.get("number")}


# ------------------------------------------------------------------------------------------------ the seat lists
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"     # no 0, 1, i, l, o: easy to read off a receipt


def password(key, slug):
    """Four groups of four from HMAC-SHA256(key, "area-seat:" + slug). A new key changes every seat's password; swapping one
    seat's password alone means adding a "rotation" number to that territory (its slug then becomes slug + ":" + n)."""
    d = hmac.new(key.encode(), f"area-seat:{slug}".encode(), hashlib.sha256).digest()
    n = int.from_bytes(d, "big")
    out = []
    for _ in range(16):
        n, r = divmod(n, len(ALPHABET))
        out.append(ALPHABET[r])
    return "-".join("".join(out[i:i + 4]) for i in range(0, 16, 4))


def seat_slug(t):
    return t["slug"] + (f":{t['rotation']}" if t.get("rotation") else "")


def city_for(t, geo=None):
    """The Chicago settings with this seat's words. The product, storage key, file name and map centre change; the City's
    disclaimer and every Chicago term stay word for word; the Terms gain the seat clause (tools/leads_xlsx.py terms_text)."""
    import leads_cities as LC
    geo = geo or json.load(open(GEO))
    pts = [a["centre"] for a in geo["areas"] if a["name"] in t["areas"]]
    lon = sum(p[0] for p in pts) / len(pts)
    lat = sum(p[1] for p in pts) / len(pts)
    areas = ", ".join(t["areas"])
    c = dict(LC.CHICAGO)
    c.update({
        "product": f"{t['name']} seat, Chicago Construction Cleaning Leads",
        "slug": f"chicago-cleaning-{t['slug']}-seat",
        "members": f"chicago-cleaning-area-members/{t['slug']}",
        "freePage": OFFER_URL,
        "csvPrefix": f"chicago-{t['slug']}-seat",
        "storageKey": f"pnf-cas-{t['slug']}-v1",
        "center": [round(lat, 4), round(lon, 4)], "zoom": 13 if len(t["areas"]) <= 2 else (11 if len(t["areas"]) > 20 else 12),
        "gateSub": (f"Your seat: {t['name']}. Projects close to a final clean in your area, the builder on each, and the builder's "
                    "office phone or email where their own website lists one."),
        "legal": LC.CHICAGO["legal"].replace(
            "Licensed to one business for its own prospecting;",
            f"Licensed to one business, the only seat holder for {t['name']}, for its own prospecting;"),
        "seatName": t["name"], "seatAreas": areas,
        "seatClause": (f"Your seat. Your membership is the only seat for {t['name']}: the City of Chicago community areas "
                       f"{areas}. While your membership is active, ProofNotFluff sells this area's list to no other business, "
                       "and leaves this area's projects out of its shared Chicago list, its free sample page and the examples in "
                       "its emails to other cleaning companies, starting with the first weekly list after you join. The permits "
                       "are public City of Chicago records: anyone can read them on the City's site, and other companies may "
                       "sell lists made from the same records. Exclusive means ProofNotFluff sells this area's list to you only."),
    })
    return c


def week_counts(full):
    """Counts only, per seat, from this week's full list: open projects, new in the last 7 days, near finish, builders.
    Standard library only: it runs before the workflow installs openpyxl."""
    cfg = load()
    by = split(full["projects"], cfg)
    near = ("OCCUPANCY PENDING", "PARTIAL OCCUPANCY")
    out = []
    for t in cfg["territories"]:
        ps = by[t["slug"]]
        out.append({"slug": t["slug"], "open": len(ps), "newWeek": sum(1 for p in ps if p.get("newThisWeek")),
                    "nearFinish": sum(1 for p in ps if any(k in (p.get("milestone") or "").upper() for k in near)),
                    "builders": len({g for p in ps for g in (p.get("gc") or [])[:1]})})
    return {"schema": "pnf.areaweek.v1", "fetchedAt": full["source"]["fetchedAt"], "window": full.get("window"),
            "openCitywide": len(full["projects"]), "territories": out}


def build_members(full, key, out_root=MEMBERS):
    """One members' app per seat (tools/leads_app.py, the $29 list's own app) with only that seat's projects and the seat's
    own password. Builder contacts decrypt with LEADS_PASSWORD from the environment, as in the weekly build."""
    import tempfile
    import leads_app, leads_xlsx
    from permits_chicago import list_day
    cfg = load()
    geo = json.load(open(GEO))
    by = split(full["projects"], cfg)
    fetched = list_day(full["source"]["fetchedAt"])
    report = []
    for t in cfg["territories"]:
        c = city_for(t, geo)
        sub = dict(full, projects=by[t["slug"]])
        tmp = tempfile.mkdtemp()
        xlsx = os.path.join(tmp, "seat.xlsx")
        leads_xlsx.build(sub, xlsx, city=c)
        leads_app.use(c)
        rows = [leads_app.prep(p) for p in sub["projects"]]
        html = leads_app.build_html(rows, fetched, open(xlsx, "rb").read(), password(key, seat_slug(t)),
                                    full["source"].get("terms") or c["termsUrl"], city=c)
        d = os.path.join(out_root, t["slug"])
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(html)
        report.append({"slug": t["slug"], "projects": len(rows), "bytes": len(html)})
    return report


def selftest():
    geo = {"areas": [
        {"name": "A", "neighbours": ["B"], "centre": [0.5, 0.5], "rings": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]},
        {"name": "B", "neighbours": ["A", "C"], "centre": [1.5, 0.5], "rings": [[[1, 0], [2, 0], [2, 1], [1, 1], [1, 0]]]},
        {"name": "C", "neighbours": ["B"], "centre": [2.5, 0.5], "rings": [[[2, 0], [3, 0], [3, 1], [2, 1], [2, 0]]]}]}
    good = {"territories": [{"slug": "one", "name": "One", "areas": ["A", "B"]}, {"slug": "two", "name": "Two", "areas": ["C"]}], "held": []}
    assert check(good, geo) == [], check(good, geo)
    gap = {"territories": [{"slug": "one", "name": "One", "areas": ["A", "C"]}, {"slug": "two", "name": "Two", "areas": ["B"]}], "held": []}
    assert any("not one connected" in x for x in check(gap, geo))
    dup = {"territories": [{"slug": "one", "name": "One", "areas": ["A", "B"]}, {"slug": "two", "name": "Two", "areas": ["B", "C"]}], "held": []}
    assert any("is in one and two" in x for x in check(dup, geo))
    miss = {"territories": [{"slug": "one", "name": "One", "areas": ["A", "B"]}], "held": []}
    assert check(miss, geo) == ["C is in no territory"]
    typo = {"territories": [{"slug": "one", "name": "One", "areas": ["A", "B", "C", "Lopo"]}], "held": ["zzz"]}
    assert len(check(typo, geo)) == 2
    ps = [{"permit": "1", "communityArea": "A"}, {"permit": "2", "communityArea": "C"}, {"permit": "3", "communityArea": ""}]
    sp = split(ps, good)
    assert [p["permit"] for p in sp["one"]] == ["1"] and [p["permit"] for p in sp["two"]] == ["2"]
    assert [p["permit"] for p in shared(ps, good)] == ["1", "2", "3"]          # nothing held: the shared list is unchanged
    held = dict(good, held=["one"])
    assert [p["permit"] for p in shared(ps, held)] == ["2", "3"]              # a held seat leaves the shared list
    assert territory_of("B", good) == "one" and territory_of("Z", good) == ""
    geo2 = {"areas": [dict(a, number=i + 1) for i, a in enumerate(geo["areas"])]}
    assert held_numbers(good, geo2) == set() and held_numbers(held, geo2) == {"1", "2"}
    p1, p2 = password("k", "loop"), password("k", "west")
    assert p1 != p2 and p1 == password("k", "loop") and p1 != password("k2", "loop") and len(p1) == 19
    assert all(ch in ALPHABET + "-" for ch in p1)
    assert seat_slug({"slug": "loop"}) == "loop" and seat_slug({"slug": "loop", "rotation": 2}) == "loop:2"
    c = city_for({"slug": "one", "name": "One", "areas": ["A", "B"]}, geo)
    assert "the only seat holder for One" in c["legal"] and "Licensed to one business for its own prospecting;" not in c["legal"]
    assert c["disclaimer"].startswith("This site provides applications") and c["storageKey"] == "pnf-cas-one-v1"
    assert "sells this area's list to no other business" in c["seatClause"] and "A, B" in c["seatClause"]
    print("area_seats selftest ok (17 planted cases)")
    real = load()
    bad = check(real, json.load(open(GEO)))
    if bad:
        raise SystemExit("area_seats: territories FAIL: " + "; ".join(bad))
    st = stats(real)
    low = [t for t in st["territories"] if t["avg"] < 10]
    if low:
        raise SystemExit("area_seats: territories under 10 a month: " + ", ".join(f"{t['name']} {t['avg']}" for t in low))
    print(f"area_seats territories ok ({len(real['territories'])} territories, 77 areas once each, all connected, "
          f"all {min(t['avg'] for t in st['territories'])} or more a month)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif sys.argv[1:2] == ["--svg"]:
        open(sys.argv[2], "w").write(svg(load()))
    elif sys.argv[1:2] == ["--shared"]:
        full = json.load(open(sys.argv[2]))
        before = len(full["projects"])
        full["projects"] = shared(full["projects"], load())
        json.dump(full, open(sys.argv[3], "w"))
        print(f"shared list: {len(full['projects'])} of {before} projects (held: {', '.join(load().get('held', [])) or 'none'})")
    elif sys.argv[1:2] == ["--shared-sample"]:
        sm = json.load(open(sys.argv[2]))
        cfg = load()
        for k in ("projects", "nearFinish"):
            sm[k] = shared(sm.get(k) or [], cfg)
        json.dump(sm, open(sys.argv[2], "w"), indent=1)
    elif sys.argv[1:2] == ["--week-counts"]:
        json.dump(week_counts(json.load(open(sys.argv[2]))), open(WEEK, "w"), indent=1)
    elif sys.argv[1:2] == ["--build"]:
        key = os.environ.get("AREA_SEAT_KEY", "")
        if not key:
            print("no AREA_SEAT_KEY secret yet; seat pages not built")
        else:
            for r in build_members(json.load(open(sys.argv[2])), key):
                print(f"seat {r['slug']}: {r['projects']} projects, {r['bytes']:,} bytes")
    elif sys.argv[1:] == ["--passwords"]:
        key = os.environ.get("AREA_SEAT_KEY", "")
        if not key or os.environ.get("GITHUB_ACTIONS"):
            raise SystemExit("--passwords runs only in the build session with AREA_SEAT_KEY set, never in a workflow")
        for t in load()["territories"]:
            print(f"{t['name']}: {password(key, seat_slug(t))}")
    else:
        print(json.dumps(stats(load()), indent=1))
