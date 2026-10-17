#!/usr/bin/env python3
"""Chicago Construction Cleaning Leads: the paid weekly workbook (A1 pre-sale, email/A1-OUTREACH.md).

Input: the full list tools/permits_chicago.py writes with --full (the permits workflow uploads it as the
3-day run artifact "chicago-full"; it is never committed, because it is the paid product).
Output: one Excel workbook that also opens in Google Sheets.

Tabs: Start Here, Near finish, New this week, All projects, Builders, Pitch kit, Terms.
Only public, business-level permit fields go in (no owner names, phones or emails), and the City of
Chicago data disclaimer its Terms of Use require goes on Start Here and Terms word for word.

Usage: python3 tools/leads_xlsx.py chicago-full.json out.xlsx [--prev last-week.json]
       python3 tools/leads_xlsx.py --selftest
"""
import argparse, collections, datetime as dt, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wb_style as S  # noqa: E402
from openpyxl.styles import Alignment, Border, Side  # noqa: E402
from openpyxl.utils import get_column_letter  # noqa: E402

PRODUCT = "Chicago Construction Cleaning Leads"
CITY_DISCLAIMER = ("This site provides applications using data that has been modified for use from its original source, "
                   "www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims "
                   "as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The "
                   "data provided at this site is subject to change at any time. It is understood that the data provided at "
                   "this site is being used at one's own risk.")
OUR_NOTICE = ("For general business information only. Projects appear because their permits are public City of Chicago "
              "records; no builder listed here has endorsed or works with ProofNotFluff, and a listing is not an "
              "invitation to bid. Reported cost is the figure the applicant filed for the permit, not a contract value. "
              "You make your own calls and emails, and you are responsible for following the law when you do. "
              "ProofNotFluff never contacts builders or anyone else on your behalf.")
COLS = [  # (heading, key, width, format)
    ("Stage", "stage", 24, None),
    ("Address", "address", 26, None),
    ("Community area", "communityArea", 18, None),
    ("Type", "type", 15, None),
    ("What the permit covers", "scope", 58, None),
    ("Reported cost", "cost", 15, "usd0"),
    ("Homes", "units", 8, "int"),
    ("Issued", "issued", 12, "date"),
    ("General contractor", "gcText", 32, None),
    ("Permit", "permit", 12, None),
    ("New", "newText", 14, None),
]
NEAR = ("OCCUPANCY PENDING", "PARTIAL OCCUPANCY")


def stage(m):
    u = (m or "").upper()
    if any(x in u for x in NEAR):
        return "Partial occupancy approved"
    if "INSPECTION" in u:
        return "Inspections under way"
    if "ISSUED" in u or not u:
        return "Permit issued"
    return (m or "").strip()


def prep(p, prev_ids=None):
    q = dict(p)
    q["stage"] = stage(p.get("milestone"))
    q["gcText"] = ", ".join(p.get("gc") or [])
    new = p.get("newThisWeek") if prev_ids is None else (str(p.get("permit")) not in prev_ids)
    q["new"] = bool(new)
    q["newText"] = "New" if new else ""
    try:
        q["issuedDate"] = dt.date.fromisoformat(p.get("issued", "")[:10])
    except ValueError:
        q["issuedDate"] = None
    return q


def project_sheet(wb, title, subtitle, rows, as_of, tab):
    ws = wb.create_sheet(title)
    widths = {"A": 2}
    for i, (_, _, w, _) in enumerate(COLS):
        widths[get_column_letter(i + 2)] = w
    widths[get_column_letter(len(COLS) + 2)] = 2
    S.set_widths(ws, widths)
    first, last = "B", get_column_letter(len(COLS) + 1)
    r = S.title_block(ws, title, f"{subtitle} {as_of}.", span=(first, last))
    hdr = r
    S.table_header(ws, r, {get_column_letter(i + 2): h for i, (h, _, _, _) in enumerate(COLS)})
    for i in range(len(COLS)):
        ws[f"{get_column_letter(i + 2)}{r}"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
    r += 1
    line = Side(style="thin", color=S.PALETTE["line"])
    if not rows:
        S.paragraph(ws, f"B{r}", "None this week.", span=(first, last), color="note"); r += 1
    for p in rows:
        for i, (_, key, w, fmt) in enumerate(COLS):
            c = ws[f"{get_column_letter(i + 2)}{r}"]
            v = p["issuedDate"] if key == "issued" else p.get(key)
            c.value = v if v not in ("", None) else None
            c.font = S.font(S.SIZE["value"], bold=(key in ("address",)), color="accent" if key == "newText" else "ink")
            c.alignment = Alignment(vertical="top", wrap_text=key in ("scope", "gcText", "address", "stage"),
                                    horizontal="right" if fmt in ("usd0", "int") else "left")
            if fmt == "date":
                c.number_format = "mmm d, yyyy"
            elif fmt:
                c.number_format = S.FMT[fmt]
            c.border = Border(bottom=line)
        h = max(S.text_height(str(p.get("scope") or ""), COLS[4][2], S.SIZE["value"], min_height=18),
                S.text_height(p.get("gcText") or "", COLS[8][2], S.SIZE["value"], min_height=18))
        S.set_height(ws, r, h)
        r += 1
    if rows:
        ws.auto_filter.ref = f"B{hdr}:{last}{r - 1}"
    S.finish_sheet(ws, PRODUCT, r, span=("A", get_column_letter(len(COLS) + 2)), freeze=f"C{hdr + 1}",
                   protect=False, footer_notice="Public City of Chicago permit records. See the Terms tab.", tab_color=tab)
    ws.page_setup.orientation = "landscape"
    ws.print_title_rows = f"{hdr}:{hdr}"
    return ws


def builders_sheet(wb, rows, as_of):
    ws = wb.create_sheet("Builders")
    S.set_widths(ws, {"A": 2, "B": 38, "C": 12, "D": 18, "E": 14, "F": 12, "G": 40, "H": 2})
    r = S.title_block(ws, "Builders with the most open work",
                      "One call to a builder's main office can cover many projects. Ask who buys cleaning for the job you name.",
                      span=("B", "G"), as_of=as_of)
    agg = collections.OrderedDict()
    for p in rows:
        for g in (p.get("gc") or [])[:1]:
            a = agg.setdefault(g, {"n": 0, "cost": 0, "near": 0, "new": 0, "areas": collections.Counter()})
            a["n"] += 1; a["cost"] += p.get("cost") or 0
            a["near"] += p["stage"] == "Partial occupancy approved"; a["new"] += p["new"]
            if p.get("communityArea"):
                a["areas"][p["communityArea"]] += 1
    hdr = r
    S.table_header(ws, r, {"B": "General contractor", "C": "Open projects", "D": "Reported cost", "E": "Near finish",
                           "F": "New", "G": "Where most of them are"})
    r += 1
    line = Side(style="thin", color=S.PALETTE["line"])
    for g, a in sorted(agg.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["cost"])):
        vals = [g, a["n"], a["cost"], a["near"] or None, a["new"] or None, ", ".join(k for k, _ in a["areas"].most_common(3))]
        for col, v, fmt in zip("BCDEFG", vals, (None, "int", "usd0", "int", "int", None)):
            c = ws[f"{col}{r}"]; c.value = v
            c.font = S.font(S.SIZE["value"], bold=col == "B")
            c.alignment = Alignment(vertical="top", wrap_text=col in "BG", horizontal="right" if fmt else "left")
            if fmt:
                c.number_format = S.FMT[fmt]
            c.border = Border(bottom=line)
        S.set_height(ws, r, max(S.text_height(g, 38, S.SIZE["value"], min_height=18), S.text_height(vals[-1], 40, S.SIZE["value"], min_height=18)))
        r += 1
    if agg:
        ws.auto_filter.ref = f"B{hdr}:G{r - 1}"
    S.finish_sheet(ws, PRODUCT, r, span=("A", "H"), freeze=f"C{hdr + 1}", protect=False,
                   footer_notice="Public City of Chicago permit records. See the Terms tab.", tab_color="purple")
    return ws


def text_sheet(wb, title, subtitle, sections, tab, position=None):
    ws = wb.create_sheet(title, position) if position is not None else wb.create_sheet(title)
    S.set_widths(ws, {"A": 2, "B": 86, "C": 22, "D": 2})
    r = S.title_block(ws, title if title != "Start Here" else PRODUCT, subtitle, span=("B", "C"))
    for heading, paras in sections:
        r = S.section_header(ws, r, heading, span=("B", "C")); r = S.spacer(ws, r, 6)
        for p in paras:
            if isinstance(p, tuple):
                S.hyperlink(ws, f"B{r}", p[1], p[2], span=("B", "C"))
            else:
                S.paragraph(ws, f"B{r}", p, span=("B", "C"))
            r += 1; S.set_height(ws, r, 4); r += 1
        r = S.spacer(ws, r)
    S.finish_sheet(ws, PRODUCT, r, span=("A", "D"), protect=False,
                   footer_notice="Public City of Chicago permit records. See the Terms tab.", tab_color=tab)
    return ws


def build(data, out, prev=None):
    prev_ids = {str(p.get("permit")) for p in prev["projects"]} if prev else None
    rows = [prep(p, prev_ids) for p in data["projects"]]
    rows.sort(key=lambda p: (-(p.get("cost") or 0), p.get("issued", "")))
    near = [p for p in rows if p["stage"] == "Partial occupancy approved"]
    new = [p for p in rows if p["new"]]
    src = data["source"]
    fetched = dt.datetime.fromisoformat(src["fetchedAt"]).date()
    as_of = f"City data as of {fetched.strftime('%b')} {fetched.day}, {fetched.year}"
    total_cost = sum(p.get("cost") or 0 for p in rows)
    wb = S.new_workbook(PRODUCT)
    text_sheet(wb, "Start Here", f"The open apartment and commercial projects in Chicago over $500,000 and the builders on them. {as_of}.", [
        ("This week", [f"{len(rows):,} open projects with about ${total_cost / 1e9:.1f} billion of reported cost. "
                       f"{len(near)} {'has' if len(near) == 1 else 'have'} partial occupancy approved, so the building is close to done. "
                       f"{len(new)} {'is' if len(new) == 1 else 'are'} new since last week."]),
        ("Three steps", [
            "1. Start with the Near finish tab. Those buildings are closest to a final clean.",
            "2. Use the Builders tab to find general contractors with several open jobs. One relationship can cover many projects.",
            "3. Call the builder's main office, name the address and permit number, and ask who buys cleaning for that job. "
            "Send your one-page capability sheet the same day (Pitch kit tab).",
        ]),
        ("How the list is made", [
            src.get("modified", ""),
            "Stages come from the City's permit milestone: Permit issued is early, Inspections under way means work is moving, "
            "and Partial occupancy approved means the City has cleared parts of the building for use.",
            "The tables have filters on the header row, so you can sort by cost or pick one community area.",
            ("link", "Source: City of Chicago Data Portal, Building Permits", src.get("url", "")),
        ]),
        ("Before you rely on it", [OUR_NOTICE, CITY_DISCLAIMER]),
    ], "teal", position=0)
    project_sheet(wb, "Near finish", "Partial occupancy approved: the City has cleared part of the building for use.", near, as_of, "accent")
    project_sheet(wb, "New this week", "Permits that were not on last week's list.", new, as_of, "gold")
    project_sheet(wb, "All projects", "Every open project that passed the filter, biggest reported cost first.", rows, as_of, "blue")
    builders_sheet(wb, rows, as_of)
    text_sheet(wb, "Pitch kit", "Adapt these to your company. Keep every claim true.", [
        ("Your one-page capability sheet", [
            "Company name, phone, email and website at the top.",
            "What you clean after construction: rough clean, final clean, touch-up or punch clean, windows, floors, pressure washing.",
            "Crew size, how fast you can start, and the largest job you have done (square feet or units).",
            "Insurance: general liability and workers' compensation limits. Builders usually ask for a certificate of insurance.",
            "Equipment you bring, such as lifts, HEPA vacuums or floor machines.",
            "Two references from builders or property managers, with permission to share them.",
        ]),
        ("An email to a builder (send after you call)", [
            "Subject: Final clean for [address]",
            "Hi [name], thanks for the time on the phone today. We do post-construction cleaning in Chicago, from rough clean "
            "through final and touch-up. We would like to quote the final clean at [address] (permit [number]). Our capability "
            "sheet is attached: [crew size], insured for [limits], and we can start within [days]. Who should I send a quote to?",
            "[Your name], [company], [phone]",
        ]),
    ], "teal")
    text_sheet(wb, "Terms", f"{PRODUCT}. Read this before you rely on the list.", [
        ("City of Chicago data", [CITY_DISCLAIMER, ("link", "City of Chicago Data Terms of Use", src.get("terms", ""))]),
        ("ProofNotFluff", [OUR_NOTICE, "Licensed to one business for its own prospecting. Please don't resell or republish the list."]),
    ], "note")
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and "—" in c.value:
                    raise SystemExit(f"em dash in {ws.title}!{c.coordinate}")
    wb.save(out)
    return {"projects": len(rows), "near": len(near), "new": len(new), "builders": len({(p.get('gc') or [''])[0] for p in rows})}


def selftest():
    import tempfile
    from openpyxl import load_workbook
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample = json.load(open(os.path.join(here, "permits", "chicago", "sample.json")))
    data = {"source": sample["source"], "window": sample["window"], "counts": sample["counts"],
            "projects": sample["projects"] + [p for p in sample["nearFinish"] if p["permit"] not in {q["permit"] for q in sample["projects"]}]}
    data["projects"][0] = dict(data["projects"][0], newThisWeek=True)
    out = os.path.join(tempfile.mkdtemp(), "t.xlsx")
    res = build(data, out)
    wb = load_workbook(out)
    assert wb.sheetnames == ["Start Here", "Near finish", "New this week", "All projects", "Builders", "Pitch kit", "Terms"], wb.sheetnames
    assert res["near"] == len(sample["nearFinish"]), res
    assert res["new"] == 1, res
    allp = wb["All projects"]
    vals = [c.value for c in allp[allp.auto_filter.ref.split(":")[0][1:] and int(allp.auto_filter.ref.split(":")[0][1:])]]
    assert "Reported cost" in vals, vals
    assert any(CITY_DISCLAIMER == c.value for row in wb["Terms"].iter_rows() for c in row)
    print("selftest ok", res)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--prev")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        prev = json.load(open(a.prev)) if a.prev else None
        print(build(json.load(open(a.src)), a.out, prev))
