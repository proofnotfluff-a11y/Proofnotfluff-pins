#!/usr/bin/env python3
"""Live check of the downstream pipeline's join keys (runs in .github/workflows/data-probe.yml; the cloud cannot reach the
portals). Writes probes/join-keys-<date>.json with counts and column names only: no business or person names.

It answers, from the City's own APIs:
  1. Chicago ydr8-5enu: how many permits sit in each downstream permit_milestone (730 days, $500,000 and up).
  2. Chicago 4ijn-s7e5: License and License Re-Inspection rows in the last 120 days, and how many of their
     address_key values equal a downstream permit's address_key (the permit-to-health join).
  3. Austin 3syk-w9eu: the values of certificate_of_occupancy on commercial building permits (the permit-to-CO key).
  4. Austin ecmv-9xxi: whether the food inspection dataset and its address column exist, the address value's shape,
     and the permit-to-health join hit count.
Exit 0 when every probe answered; 1 when any source failed (the file still records which).
"""
import collections
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402
from socrata import Socrata, SocrataError, in_list  # noqa: E402


def main():
    today = dt.date.today()
    since = (today - dt.timedelta(days=730)).isoformat()
    look = (today - dt.timedelta(days=120)).isoformat()
    chi, aus = Socrata("https://data.cityofchicago.org"), Socrata("https://data.austintexas.gov")
    out, failed = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "since": since, "lookback": look}, []

    try:
        ms = chi.rows("ydr8-5enu", select="permit_milestone,count(*) AS n",
                      where=f"issue_date >= '{since}' AND reported_cost >= 500000 AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')",
                      group="permit_milestone", order="n DESC", limit=50)
        out["chicagoMilestones"] = {r.get("permit_milestone") or "": int(r["n"]) for r in ms}
        down = chi.pull("ydr8-5enu", select="street_number,street_direction,street_name",
                        where=f"issue_date >= '{since}' AND reported_cost >= 500000 AND permit_milestone in{in_list(sorted(R.CHICAGO_MILESTONES))}")
        pkeys = {R.address_key(" ".join(x for x in (r.get("street_number"), r.get("street_direction"), r.get("street_name")) if x)) for r in down}
        food = chi.pull("4ijn-s7e5", select="address,inspection_type",
                        where=f"inspection_date >= '{look}' AND inspection_type in('License','License Re-Inspection')")
        fkeys = {R.address_key(r.get("address")) for r in food}
        out["chicagoJoin"] = {"downstreamPermits": len(down), "permitKeys": len(pkeys - {""}), "licenseInspections": len(food),
                              "foodKeys": len(fkeys - {""}), "keyMatches": len((pkeys & fkeys) - {""})}
    except SocrataError as e:
        failed.append(f"chicago: {e}")

    try:
        co = aus.rows("3syk-w9eu", select="certificate_of_occupancy,count(*) AS n",
                      where=f"issue_date >= '{since}' AND permittype='BP' AND permit_class_mapped='Commercial'",
                      group="certificate_of_occupancy", order="n DESC", limit=20)
        out["austinCoValues"] = {str(r.get("certificate_of_occupancy")): int(r["n"]) for r in co}
    except SocrataError as e:
        failed.append(f"austin permits: {e}")

    try:
        cols = aus.columns("ecmv-9xxi")
        out["austinFoodColumns"] = cols
        sample = aus.rows("ecmv-9xxi", select="address,inspection_date", where=f"inspection_date >= '{look}'", limit=3)
        out["austinFoodAddressShape"] = [type(r.get("address")).__name__ + ":" + ",".join(sorted(r["address"].keys()) if isinstance(r.get("address"), dict) else []) for r in sample]
        n = aus.count("ecmv-9xxi", where=f"inspection_date >= '{look}'")
        out["austinFoodRows"] = n
        food = aus.pull("ecmv-9xxi", select="address", where=f"inspection_date >= '{look}'")
        fkeys = set()
        for r in food:
            a = r.get("address")
            if isinstance(a, dict):
                try:
                    a = json.loads(a.get("human_address") or "{}").get("address") or ""
                except ValueError:
                    a = ""
            fkeys.add(R.address_key(a))
        pr = aus.pull("3syk-w9eu", select="original_address1",
                      where=f"issue_date >= '{since}' AND permittype='BP' AND permit_class_mapped='Commercial' AND total_job_valuation >= 500000")
        pkeys = {R.address_key(r.get("original_address1")) for r in pr}
        out["austinJoin"] = {"permitKeys": len(pkeys - {""}), "foodKeys": len(fkeys - {""}), "keyMatches": len((pkeys & fkeys) - {""})}
    except SocrataError as e:
        failed.append(f"austin food: {e}")

    out["failed"] = failed
    os.makedirs("probes", exist_ok=True)
    path = os.path.join("probes", f"join-keys-{today.isoformat()}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print(path, "FAILED: " + "; ".join(failed) if failed else "ok")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
