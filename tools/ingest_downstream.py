#!/usr/bin/env python3
"""Downstream GC leads (Entity A): City building permits in a completion stage, joined in code to the adjacent public
datasets that confirm an imminent handover, filtered by the Timing Moat Gate and written to permits/downstream/.

Runs in GitHub Actions (.github/workflows/downstream-leads.yml): the cloud sandbox cannot reach the City portals.
Every fetch goes through tools/socrata.py (paged, counted, retried). Any fetch failure on a required source, any changed
column, or any record that fails tools/pnf_rules.validate_gc_lead exits 1 and nothing is written.

Sources and join keys (verified against the live columns by tools/data_probe.py; see permits/downstream/README.md):
  Chicago Building Permits ydr8-5enu
      stage   = permit_milestone (City text) mapped by pnf_rules.CHICAGO_MILESTONES
      CO      = the same milestone: "CERTIFICATE OF OCCUPANCY PENDING (...)" gives co_pending,
                "INSPECTIONS (CERTIFICATE OF OCCUPANCY REQUIRED)" gives co_required
      key     = address_key(street_number + street_direction + street_name)
  Chicago Food Inspections 4ijn-s7e5
      health  = inspection_type License or License Re-Inspection in the last LOOKBACK days
      key     = address_key(address); joined on (city, address_key)
  Austin Issued Construction Permits 3syk-w9eu (projects from tools/permits_austin.py, grouped by masterpermitnum)
      stage   = the derived stage, mapped by pnf_rules.AUSTIN_STAGES
      CO      = certificate_of_occupancy column on the project's building permits (co_flag when the City marks it)
      key     = address_key(original_address1)
  Austin Food Establishment Inspection Scores ecmv-9xxi
      health  = any inspection in the last LOOKBACK days at the same address_key (a new food business inspected
                inside a building that is still under City inspection is an opening signal)

Usage: python3 tools/ingest_downstream.py [--out permits/downstream/gc_leads.json] [--days 730] [--lookback 120]
       python3 tools/ingest_downstream.py --selftest
"""
import argparse
import collections
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402
from socrata import Socrata, SocrataError, in_list  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
CHI = "https://data.cityofchicago.org"
AUS = "https://data.austintexas.gov"
CHI_PERMITS, CHI_FOOD = "ydr8-5enu", "4ijn-s7e5"
AUS_PERMITS, AUS_FOOD = "3syk-w9eu", "ecmv-9xxi"
MIN_COST = 500000
CHI_NEED = {"id", "permit_", "permit_status", "permit_milestone", "permit_type", "issue_date", "street_number",
            "street_direction", "street_name", "work_description", "reported_cost"}
CHI_FOOD_NEED = {"inspection_id", "dba_name", "address", "inspection_date", "inspection_type", "results"}
AUS_FOOD_NEED = {"restaurant_name", "inspection_date", "address", "facility_id"}


def today_central(now):
    from zoneinfo import ZoneInfo
    return now.astimezone(ZoneInfo("America/Chicago")).date()


def scope_text(s, limit=200):
    s = re.sub(r"\s+", " ", (s or "")).strip()
    s = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", s)
    s = re.sub(r"\(?\b\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}\b", "", s)
    return (s[:limit - 3].rsplit(" ", 1)[0] + "...") if len(s) > limit else s


# ------------------------------------------------------------------ Chicago
def chicago_permits(api, since):
    import permits_chicago as P
    api.require_columns(CHI_PERMITS, CHI_NEED)
    stages = sorted(R.CHICAGO_MILESTONES)
    where = (f"issue_date >= '{since}' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION') "
             f"AND reported_cost >= {MIN_COST} AND permit_milestone in{in_list(stages)}")
    rows = api.pull(CHI_PERMITS, where=where, order=":id")
    out, reasons, seen = [], collections.Counter(), set()
    for r in rows:
        if not P.in_window(r, since):
            reasons["permit not open in the City record"] += 1
            continue
        if r.get("permit_") in seen:
            reasons["second row of the same permit"] += 1
            continue
        seen.add(r.get("permit_"))
        ms = (r.get("permit_milestone") or "").strip().upper()
        stage = R.CHICAGO_MILESTONES.get(ms)
        if not stage:
            reasons[f"unmapped milestone {ms[:40]}"] += 1
            continue
        ok, why = P.decide((r.get("work_description") or "").upper(), r.get("permit_type") or "")
        if not ok:
            reasons[why] += 1
            continue
        names = [r.get(f"contact_{n}_name") or "" for n in range(1, 16)
                 if "GENERAL CONTRACTOR" in (r.get(f"contact_{n}_type") or "").upper()
                 and "OWNER" not in (r.get(f"contact_{n}_type") or "").upper()]
        gcs = P.builders(names)
        if not gcs:
            reasons["no business listed as general contractor"] += 1
            continue
        addr = P.street(r)
        sigs = []
        if ms.startswith("CERTIFICATE OF OCCUPANCY PENDING"):
            sigs.append({"type": "co_pending", "dataset": CHI_PERMITS, "record_id": str(r.get("id") or r.get("permit_")),
                         "date": None, "detail": (r.get("permit_milestone") or "").title()})
        elif "CERTIFICATE OF OCCUPANCY REQUIRED" in ms:
            sigs.append({"type": "co_required", "dataset": CHI_PERMITS, "record_id": str(r.get("id") or r.get("permit_")),
                         "date": None, "detail": (r.get("permit_milestone") or "").title()})
        out.append({
            "lead_id": f"chi-{r.get('permit_')}",
            "city": "chicago",
            "permit_id": str(r.get("permit_")),
            "master_permit_id": None,
            "stage": stage,
            "stage_source": (r.get("permit_milestone") or "").strip(),
            "issue_date": (r.get("issue_date") or "")[:10],
            "address": addr,
            "address_key": R.address_key(addr),
            "zip": None,
            "valuation": round(float(r.get("reported_cost") or 0)),
            "work_type": "New construction" if "NEW CONSTRUCTION" in (r.get("permit_type") or "") else "Renovation",
            "scope": scope_text(P.clean_scope(r.get("work_description"), limit=400, whole=True)),
            "gc_company": gcs[0],
            "site_contact": None,
            "signals": sigs,
            "source_url": f"{CHI}/resource/{CHI_PERMITS}.json?permit_={r.get('permit_')}",
            "_rev": [], "_ref": [], "_ca": str(r.get("community_area") or "").split(".")[0],
        })
        if hasattr(P, "refs"):
            out[-1]["_rev"], out[-1]["_ref"] = P.refs((r.get("work_description") or "").upper())
        reasons["candidate"] += 1
    # each job once: a revision of a listed permit, or two permits at one address where one names the other
    # (permits_chicago.dedupe, the same rule the paid list uses)
    view = [{"permit": x["permit_id"], "address": x["address"], "cost": x["valuation"], "_rev": x["_rev"], "_ref": x["_ref"]} for x in out]
    _left, dropped = P.dedupe(view)
    reasons["revision or repeat of a listed job"] += len(dropped)
    out = [x for x in out if x["permit_id"] not in set(dropped)]
    # area seats (site/area_seats.json; Todd, Oct 26, 2026): a held seat's projects never reach this public file, so no email
    # to another cleaning company names one
    held = held_area_numbers()
    if held:
        reasons["in an area held by a seat"] += sum(1 for x in out if x["_ca"] in held)
        out = [x for x in out if x["_ca"] not in held]
    for x in out:
        x.pop("_rev", None)
        x.pop("_ref", None)
        x.pop("_ca", None)
    return out, reasons, len(rows)


def held_area_numbers():
    try:
        import area_seats
        return area_seats.held_numbers(area_seats.load())
    except (OSError, ValueError, KeyError):
        return set()


def chicago_health(api, lookback_since):
    api.require_columns(CHI_FOOD, CHI_FOOD_NEED)
    where = f"inspection_date >= '{lookback_since}' AND inspection_type in('License','License Re-Inspection')"
    rows = api.pull(CHI_FOOD, where=where, select="inspection_id,address,inspection_date,inspection_type,results", order=":id")
    idx = collections.defaultdict(list)
    for r in rows:
        k = R.address_key(r.get("address"))
        if k:
            idx[k].append(r)
    return idx, len(rows)


# ------------------------------------------------------------------ Austin
def austin_projects(api, now, days):
    import permits_austin as A
    since, _where, rows = A.fetch(now, days)
    projects, _reasons, _pre = A.build_lists(rows, now, since, days)
    by_master = collections.defaultdict(list)
    for r in rows:
        by_master[r.get("masterpermitnum") or ("P" + str(r.get("permit_number")))].append(r)
    return projects, by_master, len(rows)


def austin_co_flags(api, permit_numbers):
    """certificate_of_occupancy per permit_number, read in chunks (the project rows from permits_austin do not carry it)."""
    cols = api.columns(AUS_PERMITS)
    if "certificate_of_occupancy" not in cols:
        raise SocrataError(f"{AUS_PERMITS}: certificate_of_occupancy column is gone")
    flags = {}
    nums = sorted({str(n) for n in permit_numbers if n})
    for i in range(0, len(nums), 80):
        chunk = nums[i:i + 80]
        for r in api.pull(AUS_PERMITS, where=f"permit_number in{in_list(chunk)}",
                          select="permit_number,certificate_of_occupancy", order="permit_number", key="permit_number"):
            flags[str(r.get("permit_number"))] = (r.get("certificate_of_occupancy") or "").strip()
    return flags


def co_flag_on(value):
    return (value or "").strip().upper() in ("YES", "Y", "TRUE", "1", "REQUIRED", "ISSUED", "PENDING")


def austin_health(api, lookback_since):
    api.require_columns(AUS_FOOD, AUS_FOOD_NEED)
    rows = api.pull(AUS_FOOD, where=f"inspection_date >= '{lookback_since}'",
                    select="facility_id,address,inspection_date,process_description", order=":id")
    idx = collections.defaultdict(list)
    for r in rows:
        a = r.get("address")
        if isinstance(a, dict):
            try:
                a = json.loads(a.get("human_address") or "{}").get("address") or ""
            except ValueError:
                a = ""
        k = R.address_key(a)
        if k:
            idx[k].append(dict(r, address=a))
    return idx, len(rows)


def austin_leads(projects, by_master, flags):
    out, reasons = [], collections.Counter()
    for pj in projects:
        stage = R.AUSTIN_STAGES.get(pj.get("milestone"))
        if not stage:
            reasons[f"upstream stage {pj.get('milestone')}"] += 1
            continue
        addr = re.sub(r"\s*\(\+\d+ more\)$", "", pj.get("address") or "")
        sigs = []
        for r in by_master.get(pj["permit"], []):
            v = flags.get(str(r.get("permit_number")), "")
            if co_flag_on(v):
                sigs.append({"type": "co_flag", "dataset": AUS_PERMITS, "record_id": str(r.get("permit_number")),
                             "date": None, "detail": f"certificate_of_occupancy={v}"})
                break
        detail = f"{pj.get('buildingsFinal', 0)} of {pj.get('buildings', 0) + pj.get('buildingsFinal', 0)} building permits finaled"
        out.append({
            "lead_id": f"aus-{pj['permit']}",
            "city": "austin",
            "permit_id": str(pj["permits"][0]["n"]) if pj.get("permits") else str(pj["permit"]),
            "master_permit_id": str(pj["permit"]),
            "stage": stage,
            "stage_source": f"{pj.get('milestone')} ({detail})",
            "issue_date": pj.get("issued"),
            "address": addr,
            "address_key": R.address_key(addr),
            "zip": pj.get("communityArea") or None,
            "valuation": int(pj.get("cost") or 0),
            "work_type": pj.get("type"),
            "scope": scope_text(pj.get("scope")),
            "gc_company": (pj.get("gc") or [""])[0],
            "site_contact": None,
            "signals": sigs,
            "source_url": f"{AUS}/resource/{AUS_PERMITS}.json?masterpermitnum={pj['permit']}",
        })
        reasons["candidate"] += 1
    return out, reasons


# ------------------------------------------------------------------ the join and the gate
def attach_health(leads, idx, dataset, kind_detail):
    hits = 0
    for ld in leads:
        rows = idx.get(ld["address_key"]) or []
        if rows:
            r = sorted(rows, key=lambda x: x.get("inspection_date") or "", reverse=True)[0]
            ld["signals"].append({"type": "health_license_inspection", "dataset": dataset,
                                  "record_id": str(r.get("inspection_id") or r.get("facility_id")),
                                  "date": (r.get("inspection_date") or "")[:10], "detail": kind_detail(r)})
            hits += 1
    return hits


def moat(leads):
    kept, rejected = [], collections.Counter()
    for ld in leads:
        probs = R.validate_gc_lead(ld)
        if probs:
            rejected["no adjacent CO or health signal" if any("no adjacent" in p for p in probs) else probs[0].split(": ", 1)[-1]] += 1
        else:
            kept.append(ld)
    return kept, rejected


def run(api_chi, api_aus, now, days, lookback):
    today = today_central(now)
    since = (today - dt.timedelta(days=days)).isoformat() + "T00:00:00"
    look = (today - dt.timedelta(days=lookback)).isoformat() + "T00:00:00"
    report = {"cities": {}}

    chi, chi_reasons, chi_rows = chicago_permits(api_chi, since)
    chi_idx, chi_food_rows = chicago_health(api_chi, look)
    chi_hits = attach_health(chi, chi_idx, CHI_FOOD, lambda r: f"{r.get('inspection_type')} inspection, {r.get('results')}")
    chi_kept, chi_rej = moat(chi)
    report["cities"]["chicago"] = {"permitRows": chi_rows, "foodRows": chi_food_rows, "healthJoins": chi_hits,
                                   "candidates": len(chi), "kept": len(chi_kept), "filtered": dict(chi_reasons),
                                   "rejectedByMoat": dict(chi_rej)}

    projects, by_master, aus_rows = austin_projects(api_aus, now, days)
    nums = [r.get("permit_number") for pj in projects for r in by_master.get(pj["permit"], [])]
    flags = austin_co_flags(api_aus, nums)
    aus, aus_reasons = austin_leads(projects, by_master, flags)
    aus_idx, aus_food_rows = austin_health(api_aus, look)
    aus_hits = attach_health(aus, aus_idx, AUS_FOOD, lambda r: f"food establishment inspection, {r.get('process_description') or 'routine'}")
    aus_kept, aus_rej = moat(aus)
    report["cities"]["austin"] = {"permitRows": aus_rows, "foodRows": aus_food_rows, "healthJoins": aus_hits,
                                  "coFlagValues": dict(collections.Counter(flags.values()).most_common(12)),
                                  "candidates": len(aus), "kept": len(aus_kept), "filtered": dict(aus_reasons),
                                  "rejectedByMoat": dict(aus_rej)}

    leads = sorted(chi_kept + aus_kept, key=lambda x: (x["city"], R.DOWNSTREAM.index(x["stage"]), -x["valuation"], x["lead_id"]))
    doc = {
        "schema": "pnf.gc_lead.v1",
        "generatedAt": now.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "window": {"issuedSince": since[:10], "signalLookbackSince": look[:10], "minValuation": MIN_COST},
        "sources": {"chicagoPermits": CHI_PERMITS, "chicagoFood": CHI_FOOD, "austinPermits": AUS_PERMITS, "austinFood": AUS_FOOD},
        "joinKeys": {"permitToCo": "same permit record (Chicago permit_milestone; Austin certificate_of_occupancy by permit_number)",
                     "permitToHealth": "(city, tools/pnf_rules.address_key(address))"},
        "report": report,
        "leads": leads,
    }
    return doc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--days", type=int, default=730)
    ap.add_argument("--lookback", type=int, default=120)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    try:
        doc = run(Socrata(CHI), Socrata(AUS), dt.datetime.now(dt.timezone.utc), a.days, a.lookback)
    except (SocrataError, SystemExit) as e:  # permits_austin and permits_chicago raise SystemExit on a failed fetch
        print(f"ERROR ingest: {e}")
        sys.exit(1)
    probs = R.validate_gc_file(doc)
    if probs:
        for p in probs[:30]:
            print(f"ERROR gc-lead: {p}")
        sys.exit(1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    tmp = a.out + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")
    os.replace(tmp, a.out)
    c = doc["report"]["cities"]
    print(f"OK ingest: {len(doc['leads'])} downstream GC leads (chicago {c['chicago']['kept']}, austin {c['austin']['kept']}) -> "
          f"{os.path.relpath(a.out, ROOT)}")
    sys.exit(0)


# ------------------------------------------------------------------ offline selftest (no network)
def selftest():
    fails = []

    def check(name, cond):
        if not cond:
            fails.append(name)

    check("address key range and suite", R.address_key("1234-40 West Madison Street, Suite 2") == "1234 W MADISON ST")
    check("address key plain", R.address_key("1234 W MADISON ST") == "1234 W MADISON ST")
    check("address key no number", R.address_key("W MADISON ST") == "")
    check("austin address", R.address_key("2915 E Cesar Chavez St") == "2915 E CESAR CHAVEZ ST")
    base = {"lead_id": "chi-1", "city": "chicago", "permit_id": "1", "stage": "Partial Occupancy Approved",
            "stage_source": "CERTIFICATE OF OCCUPANCY PENDING (TEMPORARY OR PARTIAL OCCUPANCY APPROVED)", "issue_date": "2026-01-02",
            "address": "1234 W Madison St", "address_key": "1234 W MADISON ST", "valuation": 4500000, "gc_company": "Example Builders",
            "signals": [{"type": "co_pending", "dataset": CHI_PERMITS, "record_id": "9", "date": None, "detail": "x"}],
            "source_url": "u", "site_contact": None, "scope": "New school"}
    check("good lead passes", R.validate_gc_lead(base) == [])
    check("no signal fails", R.validate_gc_lead(dict(base, signals=[])) != [])
    check("upstream stage fails", R.validate_gc_lead(dict(base, stage="Permit Issued", stage_source="PERMIT ISSUED (FEE DUE)")) != [])
    check("past handover fails", R.validate_gc_lead(dict(base, stage_source="CERTIFICATE OF OCCUPANCY ISSUED")) != [])
    check("site contact in public file fails", R.validate_gc_lead(dict(base, site_contact={"name": "x"})) != [])
    check("phone in scope fails", R.validate_gc_lead(dict(base, scope="call 312-555-1212")) != [])
    leads = [dict(base, signals=[]), dict(base, lead_id="chi-2", address_key="99 N STATE ST", signals=[])]
    hits = attach_health(leads, {"1234 W MADISON ST": [{"inspection_id": "77", "inspection_date": "2026-09-01", "inspection_type": "License", "results": "Pass"}]},
                         CHI_FOOD, lambda r: "License")
    kept, rej = moat(leads)
    check("health join attaches by address key", hits == 1 and [k["lead_id"] for k in kept] == ["chi-1"])
    check("unjoined lead rejected by moat", rej.get("no adjacent CO or health signal") == 1)
    check("austin stage map", R.AUSTIN_STAGES.get("Permit issued") is None and R.AUSTIN_STAGES["Near finish"] == "Inspections Under Way")
    check("co flag reading", co_flag_on("Yes") and not co_flag_on("No") and not co_flag_on(""))
    if fails:
        for f in fails:
            print(f"FAIL {f}")
        print(f"ingest_downstream selftest: {len(fails)} failed")
        sys.exit(1)
    print("ingest_downstream selftest: PASS 15 checks")
    sys.exit(0)


if __name__ == "__main__":
    main()
