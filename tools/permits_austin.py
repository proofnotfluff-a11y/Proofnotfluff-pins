#!/usr/bin/env python3
"""Austin Construction Cleaning Leads (product #2 on the permit engine; Todd, Oct 17, 2026: "let's test multiple areas").

Runs in GitHub Actions (.github/workflows/permits-austin.yml) because the cloud agents cannot reach data.austintexas.gov.
Source: City of Austin, Issued Construction Permits (dataset 3syk-w9eu), Public Domain U.S. Government.

How Austin differs from Chicago (probes/2026-10-17.json and probes/austin-descriptions.json, read Oct 17):
- One building permit per building. A multi-building development carries the WHOLE project's valuation on every building
  permit (one Lake View East master permit has 77 building permits each showing $830,000,000), so the lead is the project:
  building permits grouped by masterpermitnum, valued once.
- Remodels carry their value in total_valuation_remodel, not total_job_valuation.
- There is no inspection milestone. A project with some buildings Final and others still Active is the near-finish signal.
- Area: ZIP code (the dataset has no neighborhood).

Kept: Commercial building permits (permittype BP) issued in the last 365 days, project valuation $500,000 or more, at least one
building still open, work class New, Addition, Addition and Remodel or Remodel, building types that get a construction clean
(class 329 structures other than buildings, such as dumpster enclosures and pergolas, and 321 parking garages left out;
three and four family buildings need 4+ homes), and no trade-only, roof, site, demolition or equipment work.
Builder: contractor_company_name only when it is a business. Never kept: contractor_full_name, any phone, applicant names.
"""
import argparse, collections, datetime as dt, json, os, re, sys, time, urllib.parse, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import permits_chicago as P  # noqa: E402  (clean_scope, gc_filter, the trade and site rules)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "austin")
PORTAL = "https://data.austintexas.gov"
DATASET = "3syk-w9eu"
DATASET_PAGE = f"{PORTAL}/d/{DATASET}"
TERMS_VIEW = "ranj-cccq"          # City of Austin Open Data Terms of Use (catalog.data.gov lists it)
UA = {"User-Agent": "ProofNotFluff permit leads (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
CLOSED = {"FINAL", "EXPIRED", "VOID", "WITHDRAWN", "CANCELLED", "CANCELED", "CLOSED", "REVOKED"}
KEEP_WORK = {"NEW", "ADDITION", "ADDITION AND REMODEL", "REMODEL"}
SKIP_CLASS = re.compile(r"\b(?:329|321)\b")       # structures other than buildings; parking garages
SMALL_CLASS = re.compile(r"\b(?:103|104)\b")      # two family; three and four family
FIELDS = ("permit_number,masterpermitnum,permittype,permit_class_mapped,permit_class,work_class,description,status_current,"
          "issue_date,total_job_valuation,total_valuation_remodel,housing_units,original_address1,original_zip,"
          "contractor_trade,contractor_company_name,link")
AUSTIN_PREFIX = re.compile(r"^\s*(?:e-?plan\s*[:-]?\s*)?(?:BAUS\s*[-:]?\s*(?:review\s*[-:]?\s*)?(?:airport project\s*:\s*)?)?"
                           r"(?:[A-Z][A-Za-z ]{0,40}\breview\b\s*[-:]?\s*)?(?:\[[^\]]{1,40}\]\s*)*", re.I)
NOT_CLEAN = re.compile(r"RE-?ROOF|ROOF (?:OVERLAY|REPLACEMENT|TEAR)|TPO|RESKIN|DUMPSTER|TRASH ENCLOSURE|PERGOLA|CARPORT|RETAINING WALL|"
                       r"\bFENCE\b|SIGNAGE|\bSIGNS?\b|GENERATOR|GEN ?SET|CATWALK|FUEL (?:TANK|INFRASTRUCTURE|SYSTEM)|HYDRANT FUEL|SCRUBBER|COOLING TOWER|CHILLER|SHADE STRUCTURE|CANOPY ONLY|"
                       r"INTERIOR (?:NON[- ]?STRUCTURAL )?DEMO|DEMOLITION ONLY|FOUNDATION ONLY|SITE WORK ONLY|SHELL ONLY|POOL\b(?! HOUSE| PAVIL)")


def get(url, params=None, tries=3, as_text=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                body = r.read().decode("utf-8", "replace")
                return body if as_text else json.loads(body)
        except Exception as e:
            last = e
            time.sleep(5 * (i + 1))
    raise SystemExit(f"fetch failed: {url[:160]} ({last})")


def money_of(r):
    return max(float(r.get("total_job_valuation") or 0), float(r.get("total_valuation_remodel") or 0))


MAIN_TAG = re.compile(r"\s*[\[(]?\**\s*MAIN\s*\**[\])]?\s*$", re.I)   # "***Main***", "(Main)", "*Main*" office tags in builder names
OPEN_TAG = re.compile(r"^\s*\[(?:APPROVED|CONCURRENT|SMART HOUSING|AE GREEN BUILDING|GREEN BUILDING)\]?\s*", re.I)


def builder_name(nm):
    nm = MAIN_TAG.sub("", (nm or "").strip()).strip(" *,")
    return P.gc_filter(nm) if nm and P.BUSINESS.search(nm.upper()) else None


def austin_scope(desc):
    d = OPEN_TAG.sub("", AUSTIN_PREFIX.sub("", (desc or "").strip()))
    return P.clean_scope(d)


def keep_row(r):
    """(keep?, reason) for one building permit."""
    work = (r.get("work_class") or "").upper()
    cls = r.get("permit_class") or ""
    d = (r.get("description") or "").upper()
    if (r.get("permit_class_mapped") or "") != "Commercial":
        return False, "not commercial"
    if work not in KEEP_WORK:
        return False, f"work class {work.title() or 'blank'} (shell, demolition or repair)"
    if SKIP_CLASS.search(cls):
        return False, "structure that is not a building, or a parking garage"
    try:
        units = int(float(r.get("housing_units") or 0))
    except ValueError:
        units = 0
    if SMALL_CLASS.search(cls) and units < 4:
        return False, "two to three homes"
    if NOT_CLEAN.search(d):
        return False, "no construction clean (roof, site, equipment, demolition or shell only)"
    main = P.scope_start(AUSTIN_PREFIX.sub("", d))
    if P.ONLY_TRADE.search(d) or P.STRUCTURE_ONLY.search(main) or P.TRADE_WORK.search(main) or P.TRADE_ONLY_WORK.search(main):
        return False, "no construction clean (roof, site, equipment, demolition or shell only)"
    return True, "kept"


def group_projects(rows, min_cost):
    """Building permits grouped into projects by master permit number; the project is valued once (the largest valuation
    on any of its permits, since Austin repeats the project valuation on each building)."""
    groups = collections.OrderedDict()
    for r in rows:
        key = r.get("masterpermitnum") or r.get("permit_number")
        groups.setdefault(key, []).append(r)
    projects, reasons = [], collections.Counter()
    for key, rs in groups.items():
        open_rs = [r for r in rs if (r.get("status_current") or "").upper() not in CLOSED]
        if not open_rs:
            reasons["every building permit closed"] += 1
            continue
        kept = [r for r in open_rs if keep_row(r)[0]]
        if not kept:
            reasons[keep_row(open_rs[0])[1]] += 1
            continue
        cost = max(money_of(r) for r in rs)
        if cost < min_cost:
            reasons["project valuation under the floor"] += 1
            continue
        gcs = []
        for r in kept:
            g = builder_name(r.get("contractor_company_name"))
            if g and P.gc_key(g) not in [P.gc_key(x) for x in gcs]:
                gcs.append(g)
        if not gcs:
            reasons["no business listed as contractor"] += 1
            continue
        finals = sum(1 for r in rs if (r.get("status_current") or "").upper() == "FINAL")
        units = 0   # Austin repeats project-level numbers on each building permit, so homes are the largest count on any one permit (a floor)
        for r in kept:
            if re.search(r"\b(?:104|105|106)\b", r.get("permit_class") or ""):
                try:
                    units = max(units, int(float(r.get("housing_units") or 0)))
                except ValueError:
                    pass
        first = sorted(kept, key=lambda r: r.get("issue_date") or "")[0]
        addrs = sorted({(r.get("original_address1") or "").strip().title() for r in kept if r.get("original_address1")})
        new_build = any((r.get("work_class") or "").upper() in ("NEW", "ADDITION") for r in kept)
        projects.append({
            "permit": key,
            "issued": (first.get("issue_date") or "")[:10],
            "type": "New construction" if new_build else "Renovation",
            "scope": austin_scope(first.get("description")),
            "units": units or None,
            "cost": round(cost),
            "address": addrs[0] + (f" (+{len(addrs) - 1} more)" if len(addrs) > 1 else "") if addrs else "",
            "communityArea": (first.get("original_zip") or "").strip()[:5],
            "status": "Active",
            "milestone": "Some buildings finaled" if finals else "Permit active",
            "buildings": len(kept),
            "buildingsFinal": finals,
            "gc": gcs[:2],
        })
        reasons["kept"] += 1
    return projects, reasons


def terms_text():
    try:
        meta = get(f"{PORTAL}/api/views/{TERMS_VIEW}.json")
    except SystemExit as e:
        return f"Could not fetch the City of Austin Open Data Terms of Use ({TERMS_VIEW}): {e}\n"
    parts = [f"Source: {PORTAL}/d/{TERMS_VIEW}", f"Fetched: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}", "",
             f"Name: {meta.get('name', '')}", "", meta.get("description") or ""]
    for k in ("attribution", "attributionLink", "license", "metadata"):
        if meta.get(k):
            parts.append(f"{k}: {json.dumps(meta.get(k))[:4000]}")
    return "\n".join(parts) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--min-cost", type=int, default=500000)
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--full", default="")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)
    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    upd = meta.get("rowsUpdatedAt") or meta.get("viewLastModified")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    since = (now - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT00:00:00")
    where = (f"issue_date >= '{since}' AND permittype='BP' AND permit_class_mapped='Commercial' AND "
             f"(total_job_valuation >= {a.min_cost} OR total_valuation_remodel >= {a.min_cost})")
    rows, offset = [], 0
    while True:
        page = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": FIELDS, "$where": where, "$order": "issue_date DESC",
                                                          "$limit": 5000, "$offset": offset})
        rows += page
        if len(page) < 5000 or offset > 50000:
            break
        offset += 5000
    # Final siblings of open projects decide "some buildings finaled", so the masters' closed permits come in too
    masters = sorted({r.get("masterpermitnum") for r in rows if r.get("masterpermitnum")})
    for i in range(0, len(masters), 40):
        chunk = ",".join(f"'{m}'" for m in masters[i:i + 40])
        extra = get(f"{PORTAL}/resource/{DATASET}.json", {"$select": FIELDS, "$where": f"masterpermitnum in({chunk}) AND permittype='BP'",
                                                           "$limit": 5000})
        seen = {r.get("permit_number") for r in rows}
        rows += [r for r in extra if r.get("permit_number") not in seen]
    projects, reasons = group_projects(rows, a.min_cost)
    projects.sort(key=lambda x: (-x["cost"], x["issued"]))
    near = [x for x in projects if x["milestone"] == "Some buildings finaled"]
    by_zip = collections.Counter(x["communityArea"] for x in projects if x["communityArea"])
    gc_n, gc_cost, gc_name = collections.Counter(), collections.Counter(), {}
    for x in projects:
        for g in x["gc"]:
            key = P.gc_key(g); gc_n[key] += 1; gc_cost[key] += x["cost"]; gc_name.setdefault(key, g)
    top_gcs = [{"name": gc_name[k], "projects": n, "cost": gc_cost[k]} for k, n in sorted(gc_n.items(), key=lambda kv: (-kv[1], -gc_cost[kv[0]]))[:12]]
    sample = {
        "source": {
            "name": "City of Austin, Issued Construction Permits", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
            "fetchedAt": now.isoformat(timespec="seconds"), "license": (meta.get("license") or {}).get("name", ""),
            "attribution": meta.get("attribution", ""),
            "modified": (f"Filtered by ProofNotFluff: commercial building permits issued in the last {a.days} days, grouped into projects "
                         f"by master permit, project valuation ${a.min_cost:,} or more, at least one building still open; dumpster "
                         "enclosures, pergolas, parking garages, roofs, demolition, shell-only and equipment work left out; homes of "
                         "two or three units left out; only project-level and business fields kept."),
            "terms": f"{PORTAL}/d/{TERMS_VIEW}",
        },
        "window": {"from": since[:10], "to": now.strftime("%Y-%m-%d")},
        "counts": {"fetched": len(rows), "kept": len(projects), "excluded": dict(reasons),
                   "keptByType": dict(collections.Counter(x["type"] for x in projects)),
                   # a development's valuation repeats across its master permits: counted once per (valuation, builder, ZIP)
                   "keptCost": sum(v for v, *_ in {(x["cost"], P.gc_key(x["gc"][0]), x["communityArea"]) for x in projects}),
                   "keptUnits": sum(x["units"] or 0 for x in projects if x["type"] == "New construction"),
                   "topAreas": by_zip.most_common(8), "topGCs": top_gcs, "nearFinish": len(near)},
        "projects": projects[: a.top],
        "nearFinish": near[:10],
    }
    profile = {"fetchedAt": sample["source"]["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": [c.get("fieldName") for c in meta.get("columns", [])],
               "workClasses": dict(collections.Counter(r.get("work_class") for r in rows)),
               "statuses": dict(collections.Counter(r.get("status_current") for r in rows)),
               "classes": dict(collections.Counter(r.get("permit_class") for r in rows).most_common(30)),
               "license": sample["source"]["license"], "where": where}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    if a.full:
        week = (now - dt.timedelta(days=7)).strftime("%Y-%m-%d")
        for x in projects:
            x["newThisWeek"] = x["issued"] >= week
        review = [{"permit": r.get("permit_number"), "master": r.get("masterpermitnum"), "raw": r.get("description") or "",
                   "cost": money_of(r), "work": r.get("work_class"), "class": r.get("permit_class"), "status": r.get("status_current"),
                   "units": r.get("housing_units"), "issued": (r.get("issue_date") or "")[:10], "address": r.get("original_address1"),
                   "zip": r.get("original_zip"), "gcRaw": [r.get("contractor_company_name")]} for r in rows]
        json.dump({"source": sample["source"], "window": sample["window"], "counts": sample["counts"], "projects": projects, "review": review},
                  open(a.full, "w"), indent=1)
    print(json.dumps({"fetched": len(rows), "kept": len(projects), "near": len(near), "excluded": dict(reasons)}))


ROW_CASES = [  # real Austin wording (probes/austin-descriptions.json, Oct 17): (row fields, keep?)
    ({"permit_class": "C- 105 Five or More Family Bldgs", "work_class": "New", "housing_units": "30",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction of New Apartments with Private Garages (38520 SF)."}, True),
    ({"permit_class": "C- 329 Com Structures Other Than Bldg", "work_class": "New", "housing_units": "1",
      "description": "ePlan: Commercial Expedited Review - [SMART HOUSING] New Construction of Dumpster Enclosure."}, False),
    ({"permit_class": "C- 321 Pkg Garage Bldg & Open Deck", "work_class": "New", "housing_units": "1",
      "description": "ePlan: Commercial Expedited Review - [CONCURRENT] New Construction of New Detached Garage (1667 SF)."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "housing_units": "0",
      "description": "TPO Roof Overlay. Adding 1/2 Coverboard and TPO Membrane over Existing Roof. Existing warehouse."}, False),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Remodel", "housing_units": "0",
      "description": "ePlan: Expedited Review - First Time Tenant Finish-Out to create Restaurant with Mezzanine (10643 SF)"}, True),
    ({"permit_class": "C-1000 Commercial Remodel", "work_class": "Interior Demo Non-Structural", "housing_units": "2",
      "description": "Interior Non-Structural Demolition"}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Addition and Remodel", "housing_units": "1",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] Addition and Remodel to Existing Exterior Hospital Services. Work to include replacing existing Generator and Fuel Tank."}, False),
    ({"permit_class": "C- 104 Three & Four Family Bldgs", "work_class": "New", "housing_units": "3",
      "description": "ePlan: Expedited Review - New Construction of Multi Family Townhouse Building."}, False),
    ({"permit_class": "C- 104 Three & Four Family Bldgs", "work_class": "New", "housing_units": "4",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction of Multi Family Buildings with Private Garages (8781 SF)."}, True),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "housing_units": "1",
      "description": "ePlan: Commercial Expedited Review - [APPROVED] New Construction of New club Building- Also Contains Leasing Mail Finess and Co- Work (8953 SF)."}, True),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "housing_units": "1",
      "description": "BAUS - Airport Project: Install Necessary Fuel Infrastructure and Equipment to Support a Future Concourse hydrant fuel system"}, False),
    ({"permit_class": "C- 328 Commercial Other Nonresident Bldg", "work_class": "New", "housing_units": "1",
      "description": "ePlan: Commercial Expedited Review - New Gen Set and Catwalk. (400 SF)"}, False),
    ({"permit_class": "C- 437 Addn, Alter, Convn-NonRes", "work_class": "Shell", "housing_units": "0",
      "description": "ePlan: Commercial Expedited Review - New Construction of Shell Building"}, False),
]


def selftest():
    bad = []
    for fields, want in ROW_CASES:
        r = dict(fields, permit_class_mapped="Commercial")
        if keep_row(r)[0] != want:
            bad.append((fields["description"][:80], want, keep_row(r)))
    s = austin_scope("ePlan: Commercial Expedited Review - [SMART HOUSING] [APPROVED] New Construction of New Apartments with Private Garages (38520 SF).")
    if not s.startswith("New Construction of New Apartments"):
        bad.append(("scope prefix", s))
    # grouping: a project repeats its valuation on each building; it counts once and a Final sibling marks it near finish
    rows = [dict(ROW_CASES[0][0], permit_class_mapped="Commercial", permit_number=str(i), masterpermitnum="M1", status_current=st,
                 total_job_valuation="245000000", contractor_company_name="EXAMPLE BUILDERS LLC", original_address1="1 Main St",
                 original_zip="78701", issue_date="2026-05-01") for i, st in enumerate(["Active", "Active", "Final"])]
    projects, _ = group_projects(rows, 500000)
    if builder_name("HARVEY-CLEARY BUILDERS ***MAIN***") != "Harvey-Cleary Builders" or builder_name("CM CONSTRUCTORS *MAIN*") != "CM Constructors":
        bad.append(("main tag", builder_name("HARVEY-CLEARY BUILDERS ***MAIN***"), builder_name("CM CONSTRUCTORS *MAIN*")))
    if not austin_scope("[APPROVED New Construction of Behavior Health Hospital").startswith("New Construction of Behavior"):
        bad.append(("open tag", austin_scope("[APPROVED New Construction of Behavior Health Hospital")))
    if len(projects) != 1 or projects[0]["cost"] != 245000000 or projects[0]["milestone"] != "Some buildings finaled" or projects[0]["units"] != 30:
        bad.append(("grouping", projects))
    if bad:
        raise SystemExit("austin selftest FAIL: " + json.dumps(bad)[:1200])
    print(f"austin selftest ok ({len(ROW_CASES)} planted rows, grouping)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        main()
