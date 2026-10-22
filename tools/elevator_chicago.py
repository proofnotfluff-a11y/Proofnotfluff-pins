#!/usr/bin/env python3
"""Chicago elevator violations and elevator permits (growth-research Phase B, Oct 22, 2026): the sample count.

Signal: the City's Elevator bureau cites a building's elevator (most often "maintain or repair" an electric or hydraulic
elevator), or the City issues an elevator equipment permit. Buyers: independent elevator service and repair companies,
for whom one building is a service contract. Buildings with elevators are commercial or large residential buildings,
almost never a home. Counts only: no address, business or person name is written.

Runs in GitHub Actions (.github/workflows/elevator-chicago.yml); the cloud agents cannot reach data.cityofchicago.org.
Sources: Building Violations (22u3-xenr, department_bureau ELEVATOR), Building Permits (ydr8-5enu, PERMIT - ELEVATOR
EQUIPMENT), Business Licenses (r5kz-chrr, active) to count how many cited buildings also hold a business license.
Writes probes/elevator-chicago-<date>.json.

Usage: python3 tools/elevator_chicago.py             counts (Actions)
       python3 tools/elevator_chicago.py --selftest  offline: planted descriptions
"""
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exterior_chicago import PORTAL, TODAY, active_license_addresses, get, norm_address  # noqa: E402

# The City's elevator descriptions are cut off at 30 characters ("MAINTAIN OR REPAIR ELECT ELEVA").
KIND = {"repair_electric": r"\belect\w*\s+eleva", "repair_hydraulic": r"\bhydro\w*\s+eleva", "inspection_admin": r"\b(arrange|inspection|certificate|test)\b"}


def kind(description):
    d = (description or "").lower()
    return next((k for k, rx in KIND.items() if re.search(rx, d)), "other")


def violations(days, biz):
    since = (TODAY - dt.timedelta(days=days)).isoformat()
    rows = get(f"{PORTAL}/resource/22u3-xenr.json", {"$select": "address,violation_description,violation_status,inspection_category",
                                                     "$where": f"department_bureau='ELEVATOR' AND violation_date>='{since}'", "$limit": 100000})
    bld, open_b, kinds, cats = set(), set(), {}, {}
    for r in rows:
        a = norm_address(r.get("address"))
        if not a:
            continue
        bld.add(a)
        if (r.get("violation_status") or "").upper() == "OPEN":
            open_b.add(a)
        k = kind(r.get("violation_description"))
        kinds[k] = kinds.get(k, 0) + 1
        c = r.get("inspection_category") or "?"
        cats[c] = cats.get(c, 0) + 1
    return {"days": days, "violations": len(rows), "buildings": len(bld), "buildingsOpen": len(open_b),
            "buildingsWithBusinessLicense": len(bld & biz), "byKind": kinds, "byCategory": cats}, bld


def permits(days):
    since = (TODAY - dt.timedelta(days=days)).isoformat()
    rows = get(f"{PORTAL}/resource/ydr8-5enu.json", {"$select": "street_number,street_direction,street_name,contact_1_type,reported_cost",
                                                     "$where": f"permit_type='PERMIT - ELEVATOR EQUIPMENT' AND issue_date>='{since}'",
                                                     "$limit": 50000})
    bld, c1 = set(), {}
    for r in rows:
        a = norm_address(f"{r.get('street_number') or ''} {r.get('street_direction') or ''} {r.get('street_name') or ''}")
        if a:
            bld.add(a)
        t = r.get("contact_1_type") or "?"
        c1[t] = c1.get(t, 0) + 1
    return {"days": days, "permits": len(rows), "buildings": len(bld), "byContact1Type": c1}, bld


def selftest():
    cases = [("MAINTAIN OR REPAIR ELECT ELEVA", "repair_electric"), ("MAINTAIN OR REPAIR HYDRO ELEVA", "repair_hydraulic"),
             ("ARRANGE FOR INSPECTION", "inspection_admin"), ("REPAIR STAIRS", "other")]
    bad = [(d, kind(d), w) for d, w in cases if kind(d) != w]
    for b in bad:
        print("FAIL", b)
    print(f"selftest {'FAIL' if bad else 'ok'}: {len(cases) - len(bad)} of {len(cases)} planted descriptions right")
    return not bad


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    biz = active_license_addresses()
    v30, vb = violations(30, biz)
    v90, _ = violations(90, biz)
    p30, pb = permits(30)
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "violations30": v30, "violations90": v90,
           "permits30": p30, "buildingsCitedAndPermitted30": len(vb & pb)}
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"elevator-chicago-{TODAY.isoformat()}.json")
    json.dump(out, open(path, "w"), indent=1)
    print(path, json.dumps(v30))


if __name__ == "__main__":
    main()
