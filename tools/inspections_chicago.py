#!/usr/bin/env python3
"""Chicago Restaurant Inspection Leads (product #3, Oct 17, 2026): the weekly data layer.

Runs in GitHub Actions (.github/workflows/inspections-chicago.yml) because the cloud agents cannot reach
data.cityofchicago.org. Source: City of Chicago Data Portal, Food Inspections (dataset 4ijn-s7e5).

Buyers: pest control, commercial kitchen hood cleaning and grease trap companies. Every row is a licensed
food business; inspector names and inspection comments are never kept or published. Comments are read only
in the runner to set category labels, and travel onward only inside the encrypted review set (--full).

Usage: python3 tools/inspections_chicago.py --probe       violation codes, titles and keyword counts only
       python3 tools/inspections_chicago.py [--full PATH] the weekly sample (and the full list for members)
       python3 tools/inspections_chicago.py --selftest
"""
import argparse, collections, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from permits_chicago import get, terms_text, title_name  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "permits", "inspections-chicago")
PORTAL = "https://data.cityofchicago.org"
DATASET = "4ijn-s7e5"
DATASET_PAGE = f"{PORTAL}/Health-Human-Services/Food-Inspections/{DATASET}"
AREAS = "igwz-8jzy"

VIOLATION = re.compile(r"^\s*(\d{1,2})\.\s*(.*?)(?:\s+-\s+Comments:\s*(.*))?$", re.S)
KEYWORDS = {
    "rodent": r"\bRODENT|\bMICE\b|\bMOUSE\b|\bRAT\b|\bRATS\b|GNAW",
    "droppings": r"DROPPING",
    "roach": r"ROACH",
    "flies": r"\bFLIES\b|\bFLY\b|FRUIT FLIES|GNATS",
    "insect": r"INSECT",
    "hood": r"\bHOOD",
    "filter": r"FILTER",
    "grease": r"GREASE",
    "grease_trap": r"GREASE TRAP|GREASE INTERCEPTOR|INTERCEPTOR",
    "exhaust": r"EXHAUST|VENTILATION",
    "plumbing": r"PLUMB|LEAK|DRAIN|BACKFLOW|SEWAGE",
}


def split_violations(text):
    """[(code, title, comments)] from the City's violations field ('38. TITLE - Comments: ... | 41. ...')."""
    out = []
    for part in (text or "").split(" | "):
        m = VIOLATION.match(part.strip())
        if m:
            out.append((int(m.group(1)), m.group(2).strip().upper(), (m.group(3) or "").upper()))
    return out


def pull(where, select=None, order="inspection_date DESC"):
    rows, offset = [], 0
    while True:
        params = {"$where": where, "$order": order, "$limit": 5000, "$offset": offset}
        if select:
            params["$select"] = select
        page = get(f"{PORTAL}/resource/{DATASET}.json", params)
        rows += page
        if len(page) < 5000 or offset > 50000:
            return rows
        offset += 5000


def probe():
    """Violation codes and titles with counts, and keyword hit counts per code. No business names, no comments."""
    since = (dt.date.today() - dt.timedelta(days=42)).isoformat()
    rows = pull(f"inspection_date >= '{since}'", select="inspection_type,results,facility_type,violations")
    titles, hits, by_result = collections.Counter(), collections.defaultdict(collections.Counter), collections.Counter()
    ftypes = collections.Counter()
    for r in rows:
        by_result[(r.get("results") or "", r.get("inspection_type") or "")] += 1
        ftypes[r.get("facility_type") or ""] += 1
        for code, title, comments in split_violations(r.get("violations")):
            titles[(code, title)] += 1
            for k, pat in KEYWORDS.items():
                if re.search(pat, comments):
                    hits[code][k] += 1
    out = {"ranAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "since": since, "inspections": len(rows),
           "codes": [{"code": c, "title": t, "count": n, "keywordHits": dict(hits[c])} for (c, t), n in sorted(titles.items())],
           "results": [{"result": a, "type": b, "count": n} for (a, b), n in by_result.most_common()],
           "facilityTypes": ftypes.most_common(40)}
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(os.path.join(OUT, "violation-codes.json"), "w"), indent=1)
    print(json.dumps({"inspections": len(rows), "codes": len(titles)}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    if a.probe:
        probe()
