#!/usr/bin/env python3
"""Chicago exterior repair violations at business buildings (growth-research Phase B, Oct 22, 2026): the sample count.

Signal: the City's Department of Buildings cites a building for an exterior defect (wall, parapet, lintels, cornice,
chimney, porch, exterior stairs, windows, roof, eaves, fence). Buyers: small masonry and tuckpointing, porch, window,
roofing and fence contractors. Business-level only: a building counts only when an active City business license sits
at the same street address, so homes and plain apartment buildings stay out. Counts only: no address, business or
person name is written.

Runs in GitHub Actions (.github/workflows/exterior-chicago.yml); the cloud agents cannot reach data.cityofchicago.org.
Sources: Building Violations (22u3-xenr, bureau CONSERVATION), Business Licenses (r5kz-chrr, status AAI, not expired).
Writes probes/exterior-chicago-<date>.json.

Usage: python3 tools/exterior_chicago.py             counts (Actions)
       python3 tools/exterior_chicago.py --selftest  offline: planted descriptions and addresses
"""
import datetime as dt
import json
import os
import re
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "ProofNotFluff exterior probe (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
PORTAL = "https://data.cityofchicago.org"
TODAY = dt.date.today()

# The City's descriptions are short and often cut off ("REPLCE WINDOW PANES, PLEXGLAS"); matched on whole words.
EXTERIOR = {
    "masonry": r"\b(exterior wall|parapet|lintels?|cornice|chimney|masonry|tuckpoint\w*|coping|brick\w*)\b",
    "porch_stairs": r"\b(porch\w*|exterior stair\w*|exterior stairs|fire escape\w*|balcon\w*)\b",
    "windows_doors": r"\b(window\w*|exterior door\w*|screens?|screen outer)\b",
    "roof": r"\b(roof\w*|eaves|gutter\w*|downspout\w*|flashing)\b",
    "fence": r"\b(fence\w*)\b",
}
UNIT_TAIL = re.compile(r"\s+(?:#|UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|RM|ROOM|STRFRNT|STOREFRONT|BSMT|BASEMENT|REAR|FRONT|\d+(?:ST|ND|RD|TH))\b.*$")
SUFFIX = {"STREET": "ST", "AVENUE": "AVE", "BOULEVARD": "BLVD", "ROAD": "RD", "DRIVE": "DR", "PLACE": "PL", "PARKWAY": "PKWY",
          "COURT": "CT", "LANE": "LN", "TERRACE": "TER", "AV": "AVE"}


def trades(description):
    d = (description or "").lower()
    return [k for k, rx in EXTERIOR.items() if re.search(rx, d)]


def norm_address(a):
    """'1800-1802 W Pershing Rd 1st' and '1800 W PERSHING ROAD' both give '1800 W PERSHING RD'. None when there is no
    house number."""
    a = re.sub(r"[.,]", " ", (a or "").upper()).strip()
    a = re.sub(r"\s+", " ", a)
    m = re.match(r"^(\d+)(?:-\d+)?[A-Z]?\s+(.*)$", a)
    if not m:
        return None
    rest = UNIT_TAIL.sub("", m.group(2))
    words = [SUFFIX.get(w, w) for w in rest.split()]
    types = set(SUFFIX.values())
    last = max((i for i, w in enumerate(words) if w in types and i >= 1), default=None)
    if last is not None:
        words = words[:last + 1]            # anything after the last street type is a unit or floor
    else:
        while len(words) > 1 and re.search(r"\d", words[-1]):
            words = words[:-1]              # "N BROADWAY 2 P105" gives "N BROADWAY"
    return f"{m.group(1)} {' '.join(words)}".strip()


def get(url, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def active_license_addresses():
    rows = get(f"{PORTAL}/resource/r5kz-chrr.json", {"$select": "address", "$where": f"license_status='AAI' AND expiration_date>='{TODAY}'",
                                                     "$group": "address", "$limit": 200000})
    return {n for n in (norm_address(r.get("address")) for r in rows) if n}


def counts(days, biz):
    since = (TODAY - dt.timedelta(days=days)).isoformat()
    rows = get(f"{PORTAL}/resource/22u3-xenr.json", {
        "$select": "address,violation_description,violation_status,inspection_category",
        "$where": f"department_bureau='CONSERVATION' AND violation_date>='{since}'", "$limit": 100000})
    by_trade, bld, bld_biz, open_biz, cat = {}, set(), set(), set(), {}
    for r in rows:
        ts = trades(r.get("violation_description"))
        if not ts:
            continue
        a = norm_address(r.get("address"))
        if not a:
            continue
        bld.add(a)
        if a in biz:
            bld_biz.add(a)
            if (r.get("violation_status") or "").upper() == "OPEN":
                open_biz.add(a)
            c = r.get("inspection_category") or "?"
            cat[c] = cat.get(c, 0) + 1
            for t in ts:
                by_trade.setdefault(t, set()).add(a)
    return {"days": days, "conservationRows": len(rows), "exteriorBuildings": len(bld), "atBusinessBuildings": len(bld_biz),
            "openAtBusinessBuildings": len(open_biz), "businessBuildingsByTrade": {k: len(v) for k, v in sorted(by_trade.items())},
            "businessViolationsByCategory": cat}


def selftest():
    bad = []
    for d, want in [("REPAIR EXTERIOR WALL", ["masonry"]), ("PARAPET", ["masonry"]), ("REPAIR LINTELS", ["masonry"]),
                    ("REPAIR PORCH SYSTEM", ["porch_stairs"]), ("REPAIR EXTERIOR STAIR", ["porch_stairs"]),
                    ("REPLCE WINDOW PANES, PLEXGLAS", ["windows_doors"]), ("REPAIR ROOF", ["roof"]), ("REPAIR EAVES", ["roof"]),
                    ("REPAIR FENCE", ["fence"]), ("REPAIR INTERIOR WALLS/CEILING", []), ("INSTALL SMOKE DETECTORS", []),
                    ("ARRANGE PREMISE INSPECTION", [])]:
        if trades(d) != want:
            bad.append((d, trades(d), want))
    for a, want in [("1800-1802 W Pershing Rd 1st", "1800 W PERSHING RD"), ("1800 W PERSHING ROAD", "1800 W PERSHING RD"),
                    ("2459 S Christiana Ave Strfrnt", "2459 S CHRISTIANA AVE"), ("3047 N Lincoln Ave 4 412", "3047 N LINCOLN AVE"),
                    ("8 S Michigan Ave 8th 801", "8 S MICHIGAN AVE"), ("100 W RANDOLPH ST", "100 W RANDOLPH ST"),
                    ("1410 W Taylor St 1 101", "1410 W TAYLOR ST"), ("W LAKE ST", None), ("10000 W Ohare St", "10000 W OHARE ST"),
                    ("3509 S Dr Martin Luther King Jr Dr 2 2b Off. A", "3509 S DR MARTIN LUTHER KING JR DR"),
                    ("4753 N Broadway 2 P105", "4753 N BROADWAY")]:
        if norm_address(a) != want:
            bad.append((a, norm_address(a), want))
    for b in bad:
        print("FAIL", b)
    print(f"selftest {'FAIL' if bad else 'ok'}: {23 - len(bad)} of 23 planted cases right")
    return not bad


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    biz = active_license_addresses()
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "activeLicenseSites": len(biz),
           "d30": counts(30, biz), "d90": counts(90, biz)}
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"exterior-chicago-{TODAY.isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(path, json.dumps(out["d30"]))


if __name__ == "__main__":
    main()
