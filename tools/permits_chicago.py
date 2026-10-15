#!/usr/bin/env python3
"""Chicago permit leads pilot (Todd approved Oct 14, 2026; coo/OPPORTUNITIES.md Case 4).

Runs in GitHub Actions (.github/workflows/permits-chicago.yml) because the cloud agents' network
cannot reach data.cityofchicago.org. Pulls the City of Chicago Building Permits dataset, keeps big
commercial and apartment projects with a business listed as general contractor, and writes only
public, business-level fields to permits/chicago/:

  sample.json        the projects the free sample page shows, plus counts and the source line
  profile.json       column names, permit and contact type counts (tunes the filters; no names)
  source-terms.txt   the City's data terms page as text, for the Legal desk

Never written: owner names, any contact that is not a business acting as general contractor,
phone numbers, emails. Subscribers do their own outreach; the crew never contacts anyone.

Usage: python3 tools/permits_chicago.py [--days 365] [--min-cost 500000] [--top 25]
"""
import argparse, collections, datetime as dt, html.parser, json, os, re, sys, time, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "chicago")
DATASET = "ydr8-5enu"
PORTAL = "https://data.cityofchicago.org"
DATASET_PAGE = f"{PORTAL}/Buildings/Building-Permits/{DATASET}"
TERMS_URL = "https://www.chicago.gov/city/en/narr/foia/data_disclaimer.html"
AREAS = "igwz-8jzy"   # Boundaries - Community Areas (area number to name)
CLOSED = {"COMPLETE", "COMPLETED", "SUSPENDED", "CANCELLED", "CANCELED", "REVOKED", "EXPIRED", "VOID", "WITHDRAWN", "CLOSED"}
UA = {"User-Agent": "ProofNotFluff permit pilot (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}

BUSINESS = re.compile(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LP|LLP|PLLC|GROUP|BUILDERS?|"
                      r"CONSTRUCTION|CONSTRUCTORS|CONTRACTING|CONTRACTORS?|DEVELOPMENT|DEVELOPERS|ENTERPRISES?|SERVICES|"
                      r"PARTNERS|HOLDINGS|MANAGEMENT|RESTORATION|RENOVATIONS?|INTERIORS|BUILDING|HOMES|REALTY|PROPERTIES|"
                      r"ASSOCIATES|INDUSTRIES|SOLUTIONS|SYSTEMS|BUILD)\b\.?")
RESIDENTIAL_SMALL = re.compile(r"SINGLE[- ]FAMILY|\bSFR\b|\bS\.F\.R\b|TWO[- ]FLAT|\b2[- ]FLAT|THREE[- ]FLAT|\b3[- ]FLAT|COACH HOUSE|"
                               r"\b(1|2|3|ONE|TWO|THREE)[- ]?(DWELLING UNITS?|DU|D\.U\.?|UNITS?)\b")
UNITS = re.compile(r"(\d{1,4})\s*[- ]?\s*(?:RESIDENTIAL\s+)?(?:DWELLING UNITS?|D\.?U\.?S?\b|UNITS?\b|APARTMENTS?\b)")
COMMERCIAL = re.compile(r"RETAIL|COMMERCIAL|OFFICE|RESTAURANT|HOTEL|SCHOOL|WAREHOUSE|INDUSTRIAL|MIXED[- ]USE|MEDICAL|"
                        r"CLINIC|HOSPITAL|CHURCH|FITNESS|\bGYM\b|\bSTORE\b|\bBANK\b|\bLAB\b|LABORATORY|DATA CENTER|TENANT|"
                        r"BUILD[- ]?OUT|CAFE|\bBAR\b|THEATER|THEATRE|UNIVERSITY|COLLEGE|LIBRARY|DAY ?CARE|MANUFACTURING|"
                        r"DISTRIBUTION|SENIOR|ASSISTED LIVING|DORMITORY|STUDENT HOUSING|APARTMENT|MULTI[- ]?FAMILY|"
                        r"\bMF\b|CONDOMINIUM|HIGH[- ]RISE|MID[- ]RISE")


def get(url, params=None, tries=3, as_text=False):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    last = None
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                body = r.read().decode("utf-8", "replace")
                return body if as_text else json.loads(body)
        except Exception as e:  # network hiccup or 5xx: wait and retry
            last = e
            time.sleep(5 * (i + 1))
    raise SystemExit(f"fetch failed: {url[:160]} ({last})")


class Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "nav", "header", "footer"): self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "br", "div", "tr"): self.parts.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "nav", "header", "footer") and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.parts.append(data)


def terms_text():
    raw = get(TERMS_URL, as_text=True)
    t = Text(); t.feed(raw)
    lines = [re.sub(r"\s+", " ", x).strip() for x in "".join(t.parts).split("\n")]
    lines = [x for x in lines if len(x) > 2]
    return f"Source: {TERMS_URL}\nFetched: {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')}\n\n" + "\n".join(lines)


PREFIX = re.compile(r"^(?:(?:DDS|DIRECT DEVELOPER SERVICES|SELF[- ]CERT(?:IFICATION)?|SC|SPR|STANDARD PLAN REVIEW|EPR|"
                    r"EXPRESS PERMIT|EASY PERMIT|2019|CBC|CBRC|CHICAGO BUILDING (?:REHABILITATION )?CODE)[\s/,.:-]*)+", re.I)


def clean_scope(desc, limit=150):
    d = re.sub(r"\s+", " ", (desc or "")).strip().rstrip(".")
    d = PREFIX.sub("", d).strip(" :-/.,")
    d = d[:1].upper() + d[1:].lower() if d.isupper() or d[:1].islower() else d
    d = re.sub(r"\b(\d+)\s*du\b", r"\1 dwelling units", d)
    return d if len(d) <= limit else d[:limit].rsplit(" ", 1)[0] + "..."


KEEP_UP = {"LLC", "LP", "LLP", "PLLC", "USA", "II", "III", "IV", "JV", "HVAC", "MEP", "GC", "DBA"}


def title_name(n):
    out = []
    for w in re.sub(r"\s+", " ", n).strip().split(" "):
        bare = re.sub(r"[^A-Za-z]", "", w).upper()
        if bare in KEEP_UP or re.fullmatch(r"(?:[A-Za-z]\.){2,}", w.strip(",")) or (1 < len(bare) <= 3 and not re.search(r"[AEIOUY]", bare)):
            out.append(w.upper())
        else:
            w = re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), w.lower())
            out.append(re.sub(r"\bMc([a-z])", lambda m: "Mc" + m.group(1).upper(), w))
    return re.sub(r"\s+,", ",", " ".join(out))


def street(r):
    name = re.sub(r"[A-Za-z]+", lambda m: m.group(0).capitalize(), (r.get("street_name") or "").lower())
    name = re.sub(r"(\d)(St|Nd|Rd|Th)\b", lambda m: m.group(1) + m.group(2).lower(), name)
    return " ".join(x for x in [r.get("street_number", ""), r.get("street_direction", ""), name] if x).strip()


def gc_key(n):
    return re.sub(r"[^A-Z0-9]", "", re.sub(r"\b(LLC|L\.L\.C|INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD)\b\.?", "", n.upper()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=365)
    ap.add_argument("--min-cost", type=int, default=500000)
    ap.add_argument("--top", type=int, default=25)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    now = dt.datetime.now(dt.timezone.utc)

    meta = get(f"{PORTAL}/api/views/{DATASET}.json")
    cols = [c.get("fieldName") for c in meta.get("columns", [])]
    upd = meta.get("rowsUpdatedAt") or meta.get("viewLastModified")
    upd_iso = dt.datetime.fromtimestamp(upd, dt.timezone.utc).isoformat(timespec="seconds") if upd else ""
    need = {"issue_date", "permit_type", "work_description"}
    missing = sorted(need - set(cols))
    if missing:
        raise SystemExit(f"dataset columns changed, missing {missing}; columns: {cols}")
    cost_col = "reported_cost" if "reported_cost" in cols else None

    since = (now - dt.timedelta(days=a.days)).strftime("%Y-%m-%dT00:00:00")
    where = (f"issue_date >= '{since}' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')"
             + (f" AND {cost_col} >= {a.min_cost}" if cost_col else ""))
    def pull(w):
        out, offset = [], 0
        while True:
            page = get(f"{PORTAL}/resource/{DATASET}.json", {"$where": w, "$order": "issue_date DESC", "$limit": 5000, "$offset": offset})
            out += page
            if len(page) < 5000 or offset > 50000:
                return out
            offset += 5000

    try:
        rows = pull(where)
    except SystemExit:
        # reported_cost stored as text in some vintages: pull without the cost test and apply it here
        where = f"issue_date >= '{since}' AND permit_type in('PERMIT - NEW CONSTRUCTION','PERMIT - RENOVATION/ALTERATION')"
        rows = [r for r in pull(where) if cost_col and float(r.get(cost_col) or 0) >= a.min_cost]

    areas = {}
    for params in ({"$select": "area_numbe,community", "$limit": 200}, {"$limit": 200}):
        try:
            areas = {str(int(float(r.get("area_numbe") or r.get("area_num_1") or 0))): (r.get("community") or "").title()
                     for r in get(f"{PORTAL}/resource/{AREAS}.json", params, tries=2)}
            break
        except SystemExit:
            continue

    ctype = collections.Counter(); ptype = collections.Counter(); reasons = collections.Counter()
    kept = []
    status = collections.Counter(); milestone = collections.Counter()
    for r in rows:
        ptype[r.get("permit_type", "")] += 1
        status[r.get("permit_status") or ""] += 1
        milestone[r.get("permit_milestone") or ""] += 1
        if (r.get("permit_status") or "").upper() in CLOSED:
            reasons["closed, complete or suspended"] += 1; continue
        desc = (r.get("work_description") or "").upper()
        units = [int(m.group(1)) for m in UNITS.finditer(desc)]
        maxu = max(units) if units else 0
        if maxu and maxu < 4:
            reasons["1 to 3 homes"] += 1; continue
        if not maxu and RESIDENTIAL_SMALL.search(desc):
            reasons["house or 2 to 3 flat"] += 1; continue
        if not maxu and not COMMERCIAL.search(desc):
            reasons["no commercial or apartment wording"] += 1; continue
        gcs = []
        for n in range(1, 16):
            t = (r.get(f"contact_{n}_type") or "").upper()
            nm = (r.get(f"contact_{n}_name") or "").strip()
            if t:
                ctype[t] += 1
            if "GENERAL CONTRACTOR" in t and "OWNER" not in t and nm and BUSINESS.search(nm.upper()):
                if gc_key(nm) not in [gc_key(g) for g in gcs]:
                    gcs.append(title_name(nm))
        if not gcs:
            reasons["no business listed as general contractor"] += 1; continue
        addr = street(r)
        ca = str(r.get("community_area") or "").split(".")[0]
        cost = float(r.get(cost_col) or 0) if cost_col else 0
        kept.append({
            "permit": r.get("permit_") or r.get("permit_number") or r.get("id"),
            "issued": (r.get("issue_date") or "")[:10],
            "type": "New construction" if "NEW CONSTRUCTION" in (r.get("permit_type") or "") else "Renovation",
            "scope": clean_scope(r.get("work_description")),
            "units": maxu or None,
            "cost": round(cost),
            "address": addr,
            "communityArea": areas.get(ca, ""),
            "status": (r.get("permit_status") or "").title(),
            "milestone": (r.get("permit_milestone") or "").title(),
            "gc": gcs[:2],
        })
    kept.sort(key=lambda x: (-x["cost"], x["issued"]))
    by_area = collections.Counter(k["communityArea"] for k in kept if k["communityArea"])
    gc_n, gc_cost, gc_name = collections.Counter(), collections.Counter(), {}
    for k in kept:
        g = k["gc"][0]; key = gc_key(g)
        gc_n[key] += 1; gc_cost[key] += k["cost"]; gc_name.setdefault(key, g)
    top_gcs = [{"name": gc_name[key], "projects": n, "cost": gc_cost[key]} for key, n in
               sorted(gc_n.items(), key=lambda kv: (-kv[1], -gc_cost[kv[0]]))[:12]]
    sample = {
        "source": {
            "name": "City of Chicago Data Portal, Building Permits", "url": DATASET_PAGE, "rowsUpdatedAt": upd_iso,
            "fetchedAt": now.isoformat(timespec="seconds"),
            "modified": (f"Filtered by ProofNotFluff: permits issued in the last {a.days} days, new construction or renovation, "
                         f"reported cost ${a.min_cost:,} or more, still open (not complete, suspended, revoked or expired), "
                         "apartment buildings of 4+ units or commercial work, with a business listed as general contractor; "
                         "only project-level and business fields kept."),
            "terms": TERMS_URL,
        },
        "window": {"from": since[:10], "to": now.strftime("%Y-%m-%d")},
        "counts": {"fetched": len(rows), "kept": len(kept), "excluded": dict(reasons),
                   "keptByType": dict(collections.Counter(k["type"] for k in kept)),
                   "keptCost": sum(k["cost"] for k in kept), "keptUnits": sum(k["units"] or 0 for k in kept if k["type"] == "New construction"),
                   "topAreas": by_area.most_common(8), "topGCs": top_gcs,
                   "nearFinish": sum(1 for k in kept if "OCCUPANCY PENDING" in k["milestone"].upper() or "PARTIAL OCCUPANCY" in k["milestone"].upper())},
        "projects": kept[: a.top],
        "nearFinish": [k for k in kept if "OCCUPANCY PENDING" in k["milestone"].upper() or "PARTIAL OCCUPANCY" in k["milestone"].upper()][:10],
    }
    profile = {"fetchedAt": sample["source"]["fetchedAt"], "rowsUpdatedAt": upd_iso, "columns": cols,
               "permitTypes": dict(ptype), "contactTypes": dict(ctype.most_common(40)),
               "statuses": dict(status.most_common()), "milestones": dict(milestone.most_common(30)),
               "license": (meta.get("license") or {}).get("name", ""), "attribution": meta.get("attribution", ""),
               "where": where}
    json.dump(sample, open(os.path.join(OUT, "sample.json"), "w"), indent=1)
    json.dump(profile, open(os.path.join(OUT, "profile.json"), "w"), indent=1)
    try:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(terms_text())
    except SystemExit as e:
        open(os.path.join(OUT, "source-terms.txt"), "w").write(f"Could not fetch {TERMS_URL}: {e}\n")
    print(json.dumps({"fetched": len(rows), "kept": len(kept), "excluded": dict(reasons), "top3": [(k["cost"], k["type"], k["communityArea"]) for k in kept[:3]]}))


if __name__ == "__main__":
    main()
