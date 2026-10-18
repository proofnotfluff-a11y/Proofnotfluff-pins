#!/usr/bin/env python3
"""Chicago Construction Cleaning Leads: the paid weekly workbook (A1 pre-sale, email/A1-OUTREACH.md).

Input: the full list tools/permits_chicago.py writes with --full (the permits workflow keeps it out of the
repo, because it is the paid product).
Output: one Excel workbook that also opens in Google Sheets, built to design/WORKBOOK_STANDARD.md v3
(canvas, cards, stat tiles, numbered tabs) after the design director's review of Oct 17, 2026.

Tabs: Start Here, 1 Near finish, 2 New this week, 3 All projects, 4 Builders, 5 Pitch kit, Terms.
Only public, business-level permit fields go in (no owner names, phones or emails), and the City of
Chicago data disclaimer its Terms of Use require goes on Start Here and Terms word for word.

Usage: python3 tools/leads_xlsx.py chicago-full.json out.xlsx [--prev last-week.json]
       python3 tools/leads_xlsx.py --selftest
"""
import argparse, collections, datetime as dt, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wb_style as S  # noqa: E402
import pnf_dash as D  # noqa: E402
from openpyxl.cell.rich_text import CellRichText, TextBlock  # noqa: E402
from openpyxl.cell.text import InlineFont  # noqa: E402
from openpyxl.styles import Alignment, Border  # noqa: E402
from openpyxl.utils import get_column_letter as gl  # noqa: E402
import leads_cities as LC  # noqa: E402  (per-city words, Oct 18, 2026: one code base for Chicago and Austin)

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
NEAR = ("OCCUPANCY PENDING", "PARTIAL OCCUPANCY")
STAGE_ORDER = {"Partial occupancy approved": 0, "Inspections under way": 1, "Permit issued": 2}
# one status color system across the workbook, the free page and the members' page (design director, Oct 17)
CHIP = {"Partial occupancy approved": ("2E6B66", "E3EFED"), "Inspections under way": ("2F5F9E", "E6EDF6"),
        "Permit issued": ("3A4152", "ECE6DA")}
# The pitch kit, shared with the members' page (tools/leads_page.py). [Brackets] are the parts to fill in.
CAPABILITY_SHEET = [
    ("Top line", "Company name, phone, email and website."),
    ("What you clean", "Rough clean, final clean, touch-up or punch clean, windows, floors, pressure washing."),
    ("Crew and speed", "Crew size, how fast you can start, and the largest job you have done (square feet or units)."),
    ("Insurance", "General liability and workers' compensation limits. Builders usually ask for a certificate of insurance."),
    ("Equipment", "What you bring, such as lifts, HEPA vacuums or floor machines."),
    ("References", "Two references from builders or property managers, with permission to share them."),
]
BUILDER_EMAIL = [
    "Subject: Final clean for [address]",
    "Hi [name], thanks for the time on the phone today. We do post-construction cleaning in Chicago, from rough clean "
    "through final and touch-up. We would like to quote the final clean at [address] (permit [number]). Our capability "
    "sheet is attached: [crew size], insured for [limits], and we can start within [days]. Who should I send a quote to?",
    "[Your name], [company], [phone]",
]

SCOPE_MAX = 120
MONEY_SHORT = '[>=1000000000]"$"0.0,,," billion";[>=1000000]"$"0.0,,"M";"$"#,##0'
BILLION = '"$"0.0,,," billion"'
ROW_H = 30
C = LC.CHICAGO   # the city being built; use() switches it


def use(c):
    """Point this module at one city's settings (tools/leads_cities.py). Chicago's are the defaults, the exact words the
    Chicago workbook shipped with."""
    global C, PRODUCT, CITY_DISCLAIMER, OUR_NOTICE, STAGE_ORDER, CHIP, NEAR, MONEY_SHORT, BILLION
    C = LC.city(c) if isinstance(c, str) else c
    PRODUCT, CITY_DISCLAIMER, OUR_NOTICE, NEAR = C["product"], C["disclaimer"], C["notice"], C["nearMatch"]
    BILLION = '"$"0.00,,," billion"' if C.get("bil2") else '"$"0.0,,," billion"'
    MONEY_SHORT = f'[>=1000000000]{BILLION};[>=1000000]"$"0.0,,"M";"$"#,##0'
    st = C["stages"]
    STAGE_ORDER = {x: i for i, x in enumerate(st)}
    CHIP = {st[0]: ("2E6B66", "E3EFED"), st[1]: ("2F5F9E", "E6EDF6"), st[2]: ("3A4152", "ECE6DA")}
    BUILDER_EMAIL[1] = BUILDER_EMAIL[1].replace("cleaning in Chicago", f"cleaning in {C['city']}").replace("cleaning in Austin", f"cleaning in {C['city']}")
    return C


TABS = {"near": "1 Near finish", "new": "2 New this week", "all": "3 All projects", "builders": "4 Builders", "pitch": "5 Pitch kit"}


def stage(m):
    if (m or "") in C["stages"]:          # Austin's list carries the stage itself
        return m
    u = (m or "").upper()
    if any(x in u for x in NEAR):
        return "Partial occupancy approved"
    if "INSPECTION" in u:
        return "Inspections under way"
    if "ISSUED" in u or not u:
        return "Permit issued"
    return (m or "").strip()


def sort_key(p):
    """Closest to a final clean first, then the biggest job (design director, Oct 17)."""
    return (STAGE_ORDER.get(p.get("stage"), 3), -(p.get("cost") or 0), p.get("communityArea") or "~", p.get("issued", ""))


def cut(text, n=SCOPE_MAX):
    """Whole words, never inside parentheses, one ellipsis at the end."""
    t = re.sub(r"\.{3}$", "\u2026", (text or "").strip())
    if len(t) <= n:
        return t
    t = t[:n].rsplit(" ", 1)[0]
    if t.count("(") > t.count(")"):
        t = t[:t.rfind("(")]
    return t.rstrip(" ,;:-&/.") + "…"


def prep(p, prev_ids=None):
    q = dict(p)
    q["stage"] = stage(p.get("milestone"))
    q["gcText"] = "; ".join(p.get("gc") or [])
    new = p.get("newThisWeek") if prev_ids is None else (str(p.get("permit")) not in prev_ids)
    q["new"] = bool(new)
    q["newText"] = "New" if new else ""
    try:
        q["issuedDate"] = dt.date.fromisoformat(p.get("issued", "")[:10])
    except ValueError:
        q["issuedDate"] = None
    return q


def rich(parts):
    """[(text, bold, color)] as one rich-text cell value."""
    return CellRichText(*[TextBlock(InlineFont(rFont=D.FONT, sz=10, b=b, color=D.T.get(c, c)), t) for t, b, c in parts])


# ---------------------------------------------------------------- project tabs
PROJECT_COLS = [  # key, heading, width, align, fmt
    ("address", "Address", 27, "left", None),
    ("cost", "Reported cost", 15, "right", "usd0"),
    ("gcText", "Builder", 30, "left", None),
    ("communityArea", "Community area", 18, "left", None),
    ("stage", "Stage", 25, "center", None),
    ("type", "Type", 16, "left", None),
    ("units", "Homes", 8, "right", "int"),
    ("sleeping", "Sleeping units", 10, "right", "int"),   # shelters and group homes: never counted as homes (holdout round 6)
    ("issued", "Issued", 14, "left", "date"),
    ("permit", "Permit", 12, "left", None),
    ("scope", "What the permit covers", 60, "left", None),
]


AUSTIN_COLS = [
    ("address", "Address", 27, "left", None),
    ("cost", "Valuation", 15, "right", "usd0"),
    ("gcText", "Builder", 34, "left", None),
    ("communityArea", "ZIP code", 11, "left", None),
    ("stage", "Stage", 22, "center", None),
    ("type", "Type", 18, "left", None),
    ("units", "Homes", 8, "right", "int"),
    ("buildings", "Building permits", 11, "right", "int"),
    ("issued", "First issued", 14, "left", "date"),
    ("permit", "Master permit", 20, "left", None),
    ("scope", "What the permits cover", 60, "left", None),
]


def project_sheet(wb, key, tagline, rows, list_date, tab, drop=(), stats=None):
    ws = wb.create_sheet(TABS[key])
    cols = [c for c in (PROJECT_COLS if C["key"] == "chicago" else AUSTIN_COLS) if c[0] not in drop]
    letters = [gl(i + 3) for i in range(len(cols))]          # A gutter, B pad, data from C
    pad_r, gut_r = gl(len(cols) + 3), gl(len(cols) + 4)
    S.set_widths(ws, {"A": 3, "B": 2, **{l: c[2] for l, c in zip(letters, cols)}, pad_r: 2, gut_r: 3})
    D.page_header(ws, TABS[key].split(" ", 1)[1], tagline, list_date, span=("B", pad_r), side_cols=3)
    # one-line stat strip card (rows 6 to 9), numbers by formula from the table so they never drift
    top = 10
    first, last = top + 2, top + 2 + max(len(rows), 1) - 1
    col = {c[0]: l for l, c in zip(letters, cols)}
    rng = lambda k: f"{col[k]}{first}:{col[k]}{last}"
    D.h(ws, 6, 10)
    stats_ = [("Projects", f'=COUNTIF({rng("cost")},">0")', S.FMT["int"]), (C["cost"], f'=SUM({rng("cost")})', MONEY_SHORT)]
    if key == "all" and "units" in col:
        stats_.append(("Homes in them", f'=SUM({rng("units")})', S.FMT["int"]))
        stats_.append(("Near finish", f'=COUNTIF({rng("stage")},"{C["stages"][0]}")', S.FMT["int"]))
    else:
        stats_.append(("Biggest single job", f'=MAX({rng("cost")})', MONEY_SHORT))
    # spread the numbers across the whole card, the description column taking the last share
    groups, k = [], len(stats_)
    widths = [c[2] for c in cols]          # split the card into k equal widths, so the numbers sit evenly across it
    total, acc, cuts = sum(widths), 0, []
    for i, w in enumerate(widths):
        acc += w
        cuts.append(acc)
    starts = [0] + [min(range(len(cuts)), key=lambda j: abs(cuts[j] - total * i / k)) + 1 for i in range(1, k)]
    for i in range(k):
        a = letters[starts[i]]
        z = letters[starts[i + 1] - 1] if i < k - 1 else letters[-1]
        groups.append(f"{a}:{z}")
    D.stat_strip(ws, 7, [(g, e, f_, fmt) for g, (e, f_, fmt) in zip(groups, stats_)])
    D.h(ws, 9, 10)
    D.frame(ws, 6, 9, "B", pad_r)
    # the table card
    spec = []
    for l, (k, head, w, align, fmt) in zip(letters, cols):
        vals = [(p["issuedDate"] if k == "issued" else (cut(p.get(k)) if k == "scope" else
                 ", ".join(p["masters"]) if k == "permit" and len(p.get("masters") or []) > 1 else p.get(k))) for p in rows]
        spec.append({"col": l, "head": head, "kind": "text", "values": [None if v in ("", None) else v for v in vals],
                     "align": align, "fmt": "mmm d, yyyy" if fmt == "date" else (S.FMT[fmt] if fmt else None),
                     "bold": k in ("address", "cost")})
    f1, f2, end = D.table_card(ws, top, "B", pad_r, spec, max(len(rows), 1), row_height=ROW_H)
    head = f1 - 1
    D.h(ws, head, 24)
    for l, (k, head_, w, align, fmt) in zip(letters, cols):
        ws[f"{l}{head}"].alignment = Alignment(horizontal=align, vertical="center", wrap_text=True,
                                               indent=1 if (fmt in ("int", "usd0") or k in ("issued", "gcText", "type")) else 0)
    if not rows:
        ws[f"{letters[0]}{f1}"] = "None this week."
        ws[f"{letters[0]}{f1}"].font = D.f(10, False, "muted")
    for i, p in enumerate(rows):
        r = f1 + i
        for l, (k, head_, w, align, fmt) in zip(letters, cols):
            c = ws[f"{l}{r}"]
            c.alignment = Alignment(horizontal=align, vertical="center", wrap_text=k in ("scope", "gcText", "address") or (k == "permit" and C["key"] == "austin"),
                                    indent=1 if (fmt in ("int", "usd0") or k in ("issued", "gcText", "type")) else 0)
            if k == "stage" and p.get("stage") in CHIP:
                fg, bg = CHIP[p["stage"]]
                c.fill = D.fill(bg); c.font = D.f(9, True, fg)
                c.border = Border(bottom=D.side("hair"))
            elif k == "scope":
                c.font = D.f(9, False, "ink2")
            elif k in ("permit", "issued", "communityArea", "type"):
                c.font = D.f(10, False, "ink2")
    if rows:
        ws.auto_filter.ref = f"{letters[0]}{head}:{letters[-1]}{f2}"
    D.paint_canvas(ws, end + 1, gl(len(cols) + 6))
    S.finish_sheet(ws, PRODUCT, end, span=("A", gut_r), freeze=f"{letters[1]}{f1}", protect=False,
                   footer_notice=f"Public {C['records']}. See the Terms tab.", tab_color=tab,
                   canvas_cols=gl(len(cols) + 6))
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_LEGAL
    ws.page_setup.fitToWidth = 1
    ws.page_margins.left = ws.page_margins.right = 0.3
    ws.print_title_rows = f"{head}:{head}"
    return ws


# ---------------------------------------------------------------- builders tab
def builders_sheet(wb, rows, list_date):
    ws = wb.create_sheet(TABS["builders"])
    S.set_widths(ws, {"A": 3, "B": 2, "C": 40, "D": 11, "E": 18, "F": 15, "G": 11, "H": 10, "I": 2, "J": 42, "K": 2, "L": 3})
    aus = C["key"] == "austin"
    unit = "project" if aus else "permit"
    D.page_header(ws, "Builders with the most open work",
                  f"One call to a builder's main office can cover many projects. A {unit} with two builders counts for each.",
                  list_date, span=("B", "K"), side_cols=3)
    from permits_chicago import entity_key, entity_names
    agg, names = collections.OrderedDict(), entity_names(rows)
    for p in rows:
        for g in (p.get("gc") or []):
            a = agg.setdefault(names[entity_key(g)], {"n": 0, "cost": 0, "near": 0, "new": 0, "areas": collections.Counter()})
            a["n"] += 1; a["cost"] += p.get("cost") or 0
            a["near"] += p["stage"] == C["stages"][0]; a["new"] += p["new"]
            if p.get("communityArea"):
                a["areas"][p["communityArea"]] += 1
    items = sorted(agg.items(), key=lambda kv: (-kv[1]["n"], -kv[1]["cost"]))
    top = 10
    first, last = top + 2, top + 2 + max(len(items), 1) - 1
    D.h(ws, 6, 10)
    D.stat_strip(ws, 7, [
        ("C:C", "Builders with open work", f'=COUNTIF(C{first}:C{last},"?*")', S.FMT["int"]),
        ("D:G", "With 2 or more projects" if aus else "With 2 or more open permits", f'=COUNTIF(D{first}:D{last},">=2")', S.FMT["int"]),
        ("H:J", "Builder-projects (two builders count twice)" if aus else "Builder-permits (two builders count twice)", f"=SUM(D{first}:D{last})", S.FMT["int"]),
    ])
    D.h(ws, 9, 10)
    D.frame(ws, 6, 9, "B", "K")
    biggest = max([a["n"] for _, a in items] or [1])
    spec = [
        {"col": "C", "head": "Builder", "kind": "text", "values": [g for g, _ in items]},
        {"col": "D", "head": "Projects" if aus else "Open permits", "kind": "text", "values": [a["n"] for _, a in items], "align": "right", "fmt": S.FMT["int"]},
        {"col": "E", "head": "", "kind": "calc", "formula": lambda r: f'=IF(D{r}>=2,IFERROR(REPT("{D.BAR_CHAR}",MAX(0,ROUND(D{r}/{biggest}*16,0))),""),"")'},
        {"col": "F", "head": C["cost"], "kind": "text", "values": [a["cost"] for _, a in items], "align": "right", "fmt": S.FMT["usd0"]},
        {"col": "G", "head": "Near finish", "kind": "text", "values": [a["near"] for _, a in items], "align": "right", "fmt": S.FMT["int"]},
        {"col": "H", "head": "New", "kind": "text", "values": [a["new"] for _, a in items], "align": "right", "fmt": S.FMT["int"]},
        {"col": "I", "head": "", "kind": "text", "values": []},
        {"col": "J", "head": "Where most of them are", "kind": "text",
         "values": [", ".join(k for k, _ in a["areas"].most_common(3)) for _, a in items]},
    ]
    f1, f2, end = D.table_card(ws, top, "B", "K", spec, max(len(items), 1), row_height=24)
    D.h(ws, f1 - 1, 24)
    for i, (g, a) in enumerate(items):
        r = f1 + i
        ws[f"C{r}"].font = D.f(10, i < 10)
        ws[f"C{r}"].alignment = Alignment(vertical="center", wrap_text=True)
        ws[f"E{r}"].font = D.f(9, False, "teal"); ws[f"E{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
        for c in "DGH":
            ws[f"{c}{r}"].alignment = Alignment(horizontal="right", vertical="center", indent=1)
            if not ws[f"{c}{r}"].value:
                ws[f"{c}{r}"].value = 0; ws[f"{c}{r}"].font = D.f(9, False, "muted")
        ws[f"F{r}"].alignment = Alignment(horizontal="right", vertical="center", indent=1)
        ws[f"J{r}"].font = D.f(10, False, "ink2"); ws[f"J{r}"].alignment = Alignment(vertical="center", wrap_text=True)
    for c in "CDEFGHIJ":
        hc = ws[f"{c}{f1 - 1}"]
        hc.alignment = Alignment(horizontal="right" if c in "DFGH" else "left", vertical="bottom", indent=1 if c in "DFGH" else 0, wrap_text=True)
    if items:
        ws.auto_filter.ref = f"C{f1 - 1}:J{f2}"
    D.paint_canvas(ws, end + 1, "N")
    S.finish_sheet(ws, PRODUCT, end, span=("A", "L"), freeze=f"D{f1}", protect=False,
                   footer_notice=f"Public {C['records']}. See the Terms tab.", tab_color="purple", canvas_cols="N")
    ws.page_setup.orientation = "landscape"
    ws.print_title_rows = f"{f1 - 1}:{f1 - 1}"
    return ws


# ---------------------------------------------------------------- one-column card tabs (Start Here, Pitch kit, Terms)
GRID = {"A": 3, "B": 1, "C": 21, "D": 1, "E": 2, "F": 1, "G": 21, "H": 1, "I": 2, "J": 1, "K": 21, "L": 1, "M": 2, "N": 1,
        "O": 21, "P": 1, "Q": 3}          # four stat tiles with gaps on top, one-column cards (C to O) below
TEXT_W = sum(GRID[c] for c in "CDEFGHIJKLMNO")
INNER = "CDEFGHIJKLMNO"


def card(ws, top, title, rows, eyebrow=None, bg="card", line="frame"):
    """rows: [(kind, value)] kind in para, note, num (n, text), lead (lead-in, text), link (text, url), rich (parts)."""
    r = top
    D.h(ws, r, 14); r += 1
    if eyebrow:
        e = ws[f"C{r}"]; e.value = eyebrow; e.font = D.f(8, True, "muted"); ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, 16); r += 1
    if title:
        t = ws[f"C{r}"]; t.value = title; t.font = D.f(12, True); t.alignment = Alignment(vertical="center")
        ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, 24); r += 1
        D.h(ws, r, 6); r += 1
    for kind, val in rows:
        if kind == "num":
            n, text = val
            c = ws[f"C{r}"]
            c.value = CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=16, b=True, color=D.T["accent"]), f"{n}   "),
                                   TextBlock(InlineFont(rFont=D.FONT, sz=10, color=D.T["ink"]), text))
            c.alignment = Alignment(vertical="center", wrap_text=True)
            ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, max(S.text_height(text, TEXT_W, 10) + 12, 30))
        elif kind == "lead":
            lead, text = val
            L = ws[f"C{r}"]; L.value = lead; L.font = D.f(10, True); L.alignment = Alignment(vertical="top", wrap_text=True)
            c = ws[f"E{r}"]; c.value = text; c.font = D.f(10); c.alignment = Alignment(vertical="top", wrap_text=True)
            ws.merge_cells(f"E{r}:O{r}"); D.h(ws, r, max(S.text_height(text, TEXT_W - 16, 10) + 6, 22))
            for k in INNER:
                ws[f"{k}{r}"].border = Border(bottom=D.side("hair"))
        elif kind == "link":
            text, url = val
            c = ws[f"C{r}"]; c.value = text; c.hyperlink = url; c.font = D.f(10, False, "blue", underline="single")
            c.alignment = Alignment(vertical="center", wrap_text=True); ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, 22)
        elif kind == "rich":
            text = "".join(t for t, _, _ in val)
            c = ws[f"C{r}"]; c.value = rich(val); c.alignment = Alignment(vertical="top", wrap_text=True)
            ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, S.text_height(text, TEXT_W + 8, 10) + 6)
        else:
            size, color = (9, "muted") if kind == "note" else (10, "ink")
            c = ws[f"C{r}"]; c.value = val; c.font = D.f(size, False, color); c.alignment = Alignment(vertical="top", wrap_text=True)
            ws.merge_cells(f"C{r}:O{r}"); D.h(ws, r, S.text_height(val, TEXT_W + 3, size) + 16 if kind == "paragap" else S.text_height(val, TEXT_W + 8, size) + 6)
        r += 1
    D.h(ws, r, 14)
    D.frame(ws, top, r, "B", "P", bg=bg, line=line)
    return r + 2


def card_sheet(wb, name, title, tagline, list_date, tab, position=None):
    ws = wb.create_sheet(name, position) if position is not None else wb.create_sheet(name)
    S.set_widths(ws, GRID)
    D.page_header(ws, title, tagline, list_date, span=("B", "P"), side_cols=4)
    return ws


def finish_card_sheet(ws, r, tab):
    D.paint_canvas(ws, r, "S")
    S.finish_sheet(ws, PRODUCT, r - 1, span=("A", "Q"), protect=False, canvas_cols="S",
                   footer_notice=f"Public {C['records']}. See the Terms tab.", tab_color=tab)


def start_here(wb, rows, near, new, src, list_date, addresses):
    aus = C["key"] == "austin"
    ws = card_sheet(wb, "Start Here", PRODUCT, "Open commercial and apartment projects valued at $500,000 or more, and their builders." if aus
                    else "Open apartment and commercial permits of $500,000 or more, and their builders.", list_date, "teal", position=0)
    allr = f"'{TABS['all']}'!"
    n = max(len(rows), 1)
    c_rng, s_rng = f"{allr}D12:D{11 + n}", f"{allr}G12:G{11 + n}"
    newr = f"'{TABS['new']}'!D12:D{11 + max(len(new), 1)}"
    tiles = [("B", "D", "OPEN BIG PROJECTS", f'=COUNTIF({c_rng},">0")', S.FMT["int"], (f"projects, {sum(p.get('buildings') or 0 for p in rows):,} building permits" if aus else f"permits, at {addresses:,} addresses"), True),
             ("F", "H", "VALUATION" if aus else "REPORTED COST", f"=SUM({c_rng})", BILLION,
              "largest on each project's open permits" if aus else "filed with the permits", False),
             ("J", "L", "NEAR FINISH", f'=COUNTIF({s_rng},"{C["stages"][0]}")', S.FMT["int"], C["stages"][0].lower(), False),
             ("N", "P", "NEW THIS WEEK", f'=COUNTIF({newr},">0")', S.FMT["int"], "issued in the last 7 days", False)]
    D.h(ws, 6, 10)
    for left, right, eb, fml, fmt, sub, dark in tiles:
        D.tile(ws, 7, left, right, eb, fml, fmt, sub, dark=dark, value_size=28 if dark else 20)
    r = 12
    r = card(ws, r, "Three steps", [
        ("num", (1, f"Start with {TABS['near']}. Those {'projects' if aus else 'buildings'} are closest to a final clean.")),
        ("num", (2, f"Use {TABS['builders']} to find general contractors with several open jobs. One relationship can cover many projects.")),
        ("num", (3, f"Call the builder's office with the address and {C['permitLower']} number. Ask who buys cleaning, then send your capability sheet."
                    if aus else "Call the builder's office with the address and permit. Ask who buys cleaning, then send your capability sheet.")),
    ])
    if aus:
        how = [("para", src.get("modified", "")),
               ("lead", ("Projects", "Austin issues a building permit for each building, and often one for each floor of finish-out. The list "
                                     "groups them by the City's master permit, so one row is one project.")),
               ("lead", ("Homes", "The City's housing units on residential buildings and on finish-outs or remodels of homes. When the "
                                  "permits of a project repeat the same number, it counts once (fourplexes add up). Blank on non-residential work.")),
               ("lead", ("Stages", "From the City's own permit fields. Permit issued is early. Work under way means the City has pushed a "
                                   "permit's expiry date past the first 180 days, which it does when an inspection passes or an extension is "
                                   "granted. Some permits finaled means part of the project is marked Final while the rest is open.")),
               ("lead", ("Valuation", "Austin repeats a development's valuation on its building permits, so each project shows the largest "
                                      "valuation on its open building permits on the list, counted once. Finaled, shell and garage permits "
                                      "do not count. It is a size signal, not a budget.")),
               ("lead", ("Order", f"{TABS['all']} lists the projects closest to a final clean first, then the biggest. Every table has filter "
                                  "arrows on its header row, so you can pick one ZIP code or sort by valuation.")),
               ("lead", ("Builders", "The general contractor the City lists on the project's open building permits. When they name more than "
                                     "one, the one on the most permits comes first.")),
               ("lead", ("Wording", "Descriptions are the City's own text, shortened, with typos left as filed.")),
               ("link", (f"Source: {C['sourceLabel']}", src.get("url", "")))]
    else:
        how = [("para", src.get("modified", "")),
               ("lead", ("Stages", "From the City's permit milestone. Permit issued is early, Inspections under way means work is moving, and "
                                   "Partial occupancy approved means the City has cleared parts of the building for use.")),
               ("lead", ("Order", f"{TABS['all']} lists the projects closest to a final clean first, then the biggest. Every table has filter "
                                  "arrows on its header row, so you can pick one community area or sort by cost.")),
               ("lead", ("Builders", "When a permit names two general contractors, the builder comes first and a trade contractor "
                                     "(heating, electrical and similar) second.")),
               ("lead", ("Wording", "Descriptions are the City's own text, shortened, with typos left as filed.")),
               ("link", ("Source: City of Chicago Data Portal, Building Permits", src.get("url", "")))]
    r = card(ws, r, "How the list is made", how)
    r = card(ws, r, "Before you rely on it", [
        ("note", "For general information and planning only. This is not legal, tax, financial or other professional advice, and using it "
                 f"doesn't create a professional relationship. Figures come from {C['cityName']} records as of {list_date[8:]} and can change. "
                 "See the Terms tab before you rely on anything here."),
        ("note", OUR_NOTICE), ("note", CITY_DISCLAIMER)])
    finish_card_sheet(ws, r, "teal")
    return ws


def pitch_kit(wb, list_date):
    ws = card_sheet(wb, TABS["pitch"], "Pitch kit", "Adapt these to your company. Keep every claim true.", list_date, "teal")
    r = card(ws, 6, "Your one-page capability sheet", [("lead", x) for x in CAPABILITY_SHEET])

    def blue(line):   # [brackets] in bold blue, the rest plain
        return [(part, part.startswith("["), "input_text" if part.startswith("[") else "ink") for part in re.split(r"(\[[^\]]+\])", line) if part]
    r = card(ws, r, "An email to a builder (send it after you call)", [("rich", blue(line)) for line in BUILDER_EMAIL],
             eyebrow="COPY, THEN FILL IN THE BLUE PARTS", bg="input_fill", line="input_line")
    finish_card_sheet(ws, r, "teal")
    return ws


def terms_text(date):
    """The Terms of Use from the clause library, adapted for a monthly membership (Legal desk, Oct 17, 2026; version 2 for builder
    contacts and the map, Legal desk round 2, Fix 3). One source: the workbook's Terms tab and the members' app's #/terms view
    (tools/leads_app.py) are both built from this list. Austin's version 1 (Oct 18, 2026) is the same text for the City of Austin,
    with no builder contacts and its valuation wording."""
    if C["key"] == "austin":
        return [
            f"ProofNotFluff | {PRODUCT} | {C['termsVersion']}, {date}",
            "License. Your membership gives you a license to use this list for one business you own, for its own sales prospecting. You may edit "
            "it and print it for that use. You may not resell, share, give away, upload or redistribute it, in original or edited form, or use it "
            "to make a competing product.",
            "Ownership. The selection, layout, text and formulas belong to ProofNotFluff. The permit records themselves are public City of Austin "
            "data from the City of Austin, Austin Development Services (data.austintexas.gov), used under the City of Austin Open Data Terms of "
            "Use. Buying a membership doesn't transfer ownership.",
            "Businesses only. The list is for contacting the businesses named on it about work on their projects. The City of Austin's Open Data "
            "Terms of Use require that you not use the data to identify or contact individual people, and not combine it with other data to "
            "re-identify anyone. Use it only to reach businesses.",
            "Accuracy. The list is built from City of Austin permit records as of the date above. City data can be late, incomplete or wrong, and "
            "permits change. Confirm anything you rely on with the builder or the City. Valuation is the largest valuation filed on a project's "
            "open City building permits on the list, not a contract value. Map pins come from the City's coordinates or, where the City gives none, from the US "
            "Census Bureau's public geocoder, and can be off. A listed builder is not an invitation to bid.",
            "No promise of results. Valuations, stages and counts are figures from City records, not contract values or forecasts. Nothing "
            "here promises any work, contract, income or outcome.",
            "Availability. The list depends on the City of Austin publishing its permit data. The City may stop or change its data feed at any "
            "time, or require any use of it to end. If that happens the list may pause or end, and future charges will stop. The map uses OpenStreetMap's free public map service, "
            "which can limit or stop access at any time; the list and downloads work without it. Map data © OpenStreetMap contributors.",
            "No warranty. The product is provided \"as is\", without warranties of any kind, to the extent the law allows.",
            "Limit of liability. To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on this "
            "product, and its total liability for any claim is limited to the amount you paid for the most recent month of your membership. "
            "Nothing here limits rights you have under consumer protection laws that can't be waived.",
            "Trademarks. Microsoft Excel, Google Sheets, Google Maps, OpenStreetMap and Gumroad are trademarks of their owners. ProofNotFluff "
            "isn't affiliated with, sponsored or endorsed by them, by the City of Austin, or by any builder listed.",
            "AI assistance. This product was made with AI assistance and reviewed and tested by the shop owner.",
            "Help and cancelling. If the file won't open or something looks wrong, reply to your Gumroad receipt and it will be fixed. Cancel any "
            "time from your Gumroad receipt or library; cancelling stops future charges.",
        ]
    return [
        f"ProofNotFluff | {PRODUCT} | Version 2, {date}",
        "License. Your membership gives you a license to use this list for one business you own, for its own sales prospecting. You may edit "
        "it and print it for that use. You may not resell, share, give away, upload or redistribute it, in original or edited form, or use it "
        "to make a competing product.",
        "Ownership. The selection, layout, text and formulas belong to ProofNotFluff. The permit records themselves are public City of Chicago "
        "data. Buying a membership doesn't transfer ownership.",
        "Accuracy. The list is built from City of Chicago permit records as of the date above. City data can be late, incomplete or wrong, and "
        "permits change. Confirm anything you rely on with the builder or the City. Builder office phone numbers, general email addresses "
        "and websites are not City data. We read them on each builder's own website on the date shown with each one, and builders change "
        "them. A listed contact is not an invitation to bid.",
        "No promise of results. Reported costs, stages and counts are figures from City records, not contract values or forecasts. Nothing "
        "here promises any work, contract, income or outcome.",
        "Availability. The list depends on the City of Chicago publishing its permit data. If the City stops or changes that data, or asks us "
        "to stop using it, the list may pause or end, and future charges will stop. The map uses OpenStreetMap's free public map service, "
        "which can limit or stop access at any time; the list, contacts and downloads work without it. Map data © OpenStreetMap "
        "contributors.",
        "No warranty. The product is provided \"as is\", without warranties of any kind, to the extent the law allows.",
        "Limit of liability. To the extent the law allows, ProofNotFluff is not liable for any loss or damage from using or relying on this "
        "product, and its total liability for any claim is limited to the amount you paid for the most recent month of your membership. "
        "Nothing here limits rights you have under consumer protection laws that can't be waived.",
        "Trademarks. Microsoft Excel, Google Sheets, Google Maps, OpenStreetMap and Gumroad are trademarks of their owners. ProofNotFluff "
        "isn't affiliated with, sponsored or endorsed by them, by the City of Chicago, or by any builder listed.",
        "AI assistance. This product was made with AI assistance and reviewed and tested by the shop owner.",
        "Help and cancelling. If the file won't open or something looks wrong, reply to your Gumroad receipt and it will be fixed. Cancel any "
        "time from your Gumroad receipt or library; cancelling stops future charges.",
    ]


def terms(wb, src, list_date):
    ws = card_sheet(wb, "Terms", "Terms of Use", f"{PRODUCT}. Read this before you rely on the list.", list_date, "note")
    r = card(ws, 6, f"{C['cityName']} data", [("para", CITY_DISCLAIMER), ("link", (C["termsLabel"], src.get("terms", "") or C["termsUrl"]))])
    kind = "paragap" if C["key"] == "austin" else "para"   # Austin: an even gap after every paragraph (design director, Oct 18)
    r = card(ws, r, "ProofNotFluff", [(kind, OUR_NOTICE)] + [(kind, t) for t in terms_text(list_date[8:])])
    finish_card_sheet(ws, r, "note")
    return ws


def build(data, out, prev=None, city=None):
    use(city or LC.for_source(data.get("source")))
    prev_ids = {str(p.get("permit")) for p in prev["projects"]} if prev else None
    rows = [prep(p, prev_ids) for p in data["projects"]]
    rows.sort(key=sort_key)
    addresses = len({p.get("address") for p in rows})
    near = [p for p in rows if p["stage"] == C["stages"][0]]
    new = [p for p in rows if p["new"]]
    src = data["source"]
    from permits_chicago import list_day
    fetched = list_day(src["fetchedAt"])
    list_date = f"List of {fetched.strftime('%b')} {fetched.day}, {fetched.year}"
    wb = S.new_workbook(PRODUCT)
    project_sheet(wb, "near", "Some permits finaled: part of the project is marked Final while the rest is open. Biggest first."
                  if C["key"] == "austin" else "Partial occupancy approved: the City has cleared part of the building for use. Biggest first.",
                  near, list_date, "accent", drop=("stage",) + absent(near))
    project_sheet(wb, "new", "Permits issued in the last 7 days. Closest to a final clean first, then biggest.",
                  new, list_date, None, drop=absent(new))
    project_sheet(wb, "all", f"Every open {'project' if C['key'] == 'austin' else 'permit'} that passed the filter, closest to a final clean first, then biggest.",
                  rows, list_date, None, drop=tuple(k for k in absent(rows) if k == "sleeping"))
    builders_sheet(wb, rows, list_date)
    pitch_kit(wb, list_date)
    terms(wb, src, list_date)
    start_here(wb, rows, near, new, src, list_date, addresses)
    wb.active = 0
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                v = str(c.value) if c.value is not None else ""
                if "—" in v:
                    raise SystemExit(f"em dash in {ws.title}!{c.coordinate}")
    wb.save(out)
    cache_values(out)
    return {"projects": len(rows), "near": len(near), "new": len(new), "addresses": addresses,
            "builders": len({__import__("permits_chicago").entity_key(g) for p in rows for g in (p.get("gc") or [])})}


def absent(rows):
    """The count columns no row on a tab fills (Homes, Sleeping units), left off that tab."""
    return tuple(k for k in ("units", "sleeping") if not any(p.get(k) for p in rows))


# ---------------------------------------------------------------- cached formula values
# openpyxl writes formulas with no stored result, so a viewer that does not recalculate (a phone preview, Google Drive's
# viewer, Quick Look) shows the summary cells blank (holdout round 6). cache_values() works out every formula this file
# writes from the cells it reads and stores the result in the file; Excel still recalculates on open.
_FUNCS = {}


def _flat(a):
    for x in a:
        if isinstance(x, list):
            yield from _flat(x)
        else:
            yield x


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _countif(rng, crit):
    vals = list(_flat(rng))
    m = re.fullmatch(r"(>=|<=|<>|>|<|=)?(.*)", crit)
    op, rhs = m.group(1) or "=", m.group(2)
    if rhs == "?*":
        return sum(1 for v in vals if isinstance(v, str) and len(v) >= 1)
    try:
        r = float(rhs)
        test = {">": lambda v: v > r, ">=": lambda v: v >= r, "<": lambda v: v < r, "<=": lambda v: v <= r,
                "=": lambda v: v == r, "<>": lambda v: v != r}[op]
        return sum(1 for v in vals if _num(v) and test(v))
    except ValueError:
        return sum(1 for v in vals if isinstance(v, str) and (v.lower() == rhs.lower()) == (op != "<>"))


def _round(x, n=0):
    q = 10 ** int(n)
    return (1 if x >= 0 else -1) * int(abs(x) * q + 0.5) / q   # Excel rounds half away from zero


class _Err(Exception):
    pass


_FUNCS.update(COUNTIF=_countif, SUM=lambda *a: sum(v for v in _flat(a) if _num(v)), MAX=lambda *a: max([v for v in _flat(a) if _num(v)] or [0]),
              MIN=lambda *a: min([v for v in _flat(a) if _num(v)] or [0]), ROUND=_round, REPT=lambda t, n: t * int(n),
              IF=lambda c, a, b="": a if c else b, IFERROR=lambda x, alt: alt if isinstance(x, _Err) else x)


def formula_value(wb, ws, f):
    """The value of one formula of the kinds this workbook writes (COUNTIF, SUM, MAX, MIN, IF, IFERROR, REPT, ROUND, + - * /, comparisons)."""
    parts = re.split(r'("(?:[^"]|"")*")', f[1:])
    out = []
    for i, part in enumerate(parts):
        if i % 2:
            out.append(repr(part[1:-1].replace('""', '"')))
            continue
        part = re.sub(r"(?:'((?:[^']|'')+)'!)?\$?\b([A-Z]{1,3})\$?(\d+)(?::\$?([A-Z]{1,3})\$?(\d+))?\b",
                      lambda m: f"_R({(m.group(1) or '').replace(chr(39) * 2, chr(39))!r},{m.group(2)!r},{m.group(3)},{(m.group(4) or '')!r},{m.group(5) or 0})", part)
        part = part.replace("<>", "!=")
        part = re.sub(r"(?<![<>!=])=(?!=)", "==", part)
        out.append(part)
    expr = "".join(out)

    def _R(sheet, c1, r1, c2, r2):
        sh = wb[sheet] if sheet else ws
        if not c2:
            v = sh[f"{c1}{r1}"].value
            if isinstance(v, str) and v.startswith("="):
                raise SystemExit(f"formula refers to formula cell {c1}{r1}: not supported")
            return 0 if v is None else v   # a blank cell is 0 in Excel arithmetic
        return [[c.value for c in row] for row in sh[f"{c1}{r1}:{c2}{r2}"]]

    env = dict(_FUNCS, _R=_R, _try=_try, __builtins__={})
    expr = _close_try(re.sub(r"IFERROR\(", "IFERROR(_try(lambda: ", expr))
    try:
        return eval(expr, env)
    except (ZeroDivisionError, TypeError, ValueError) as e:
        return _Err(str(e))


def _try(fn):
    try:
        return fn()
    except (_Err, ZeroDivisionError, TypeError, ValueError) as e:
        return e if isinstance(e, _Err) else _Err(str(e))


def _close_try(expr):
    """IFERROR(_try(lambda: X, alt)  ->  IFERROR(_try(lambda: X), alt): close the lambda at IFERROR's first top-level comma."""
    out, i = "", 0
    key = "IFERROR(_try(lambda: "
    while True:
        j = expr.find(key, i)
        if j < 0:
            return out + expr[i:]
        out += expr[i:j + len(key)]
        k, depth, q = j + len(key), 0, None
        while k < len(expr):
            ch = expr[k]
            if q:
                if ch == q and expr[k - 1] != "\\":
                    q = None
            elif ch in "'\"":
                q = ch
            elif ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "," and depth == 0:
                break
            k += 1
        out += _close_try(expr[j + len(key):k]) + ")"
        i = k


def cache_values(path):
    """Store every formula's result in the saved file, so the numbers show without a recalculation."""
    import zipfile, html as _html
    from openpyxl import load_workbook
    wb = load_workbook(path)
    zf = zipfile.ZipFile(path)
    names = zf.namelist()
    wbxml = zf.read("xl/workbook.xml").decode()
    rels = zf.read("xl/_rels/workbook.xml.rels").decode()
    target = {m.group(1): m.group(2) for m in re.finditer(r'<Relationship[^>]*Id="([^"]+)"[^>]*Target="([^"]+)"', rels)}
    target.update({m.group(2): m.group(1) for m in re.finditer(r'<Relationship[^>]*Target="([^"]+)"[^>]*Id="([^"]+)"', rels)})
    sheet_file = {}
    for m in re.finditer(r'<sheet [^>]*name="([^"]+)"[^>]*r:id="([^"]+)"', wbxml):
        t = target[m.group(2)].lstrip("/")
        sheet_file[_html.unescape(m.group(1))] = t if t.startswith("xl/") else "xl/" + t
    patched = {}
    for ws in wb.worksheets:
        vals = {}
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    v = formula_value(wb, ws, c.value)
                    if isinstance(v, _Err):
                        raise SystemExit(f"{ws.title}!{c.coordinate} {c.value}: {v}")
                    vals[c.coordinate] = v
        if not vals:
            continue
        fn = sheet_file[ws.title]
        xml = zf.read(fn).decode()

        def put(m):
            coord = re.search(r'\br="([A-Z]+\d+)"', m.group(1)).group(1)
            if coord not in vals:
                return m.group(0)
            v, head = vals[coord], m.group(1)
            if isinstance(v, str):
                head = re.sub(r'\st="[^"]*"', "", head)[:-1] + ' t="str">'
                return f"{head}{m.group(2)}<v>{_html.escape(v, quote=False)}</v></c>"
            if isinstance(v, bool):
                v = int(v)
            num = repr(float(v)) if isinstance(v, float) and not float(v).is_integer() else str(int(v))
            return f"{head}{m.group(2)}<v>{num}</v></c>"
        xml = re.sub(r"(<c [^>]*>)(<f>[^<]*</f>)(?:<v\s*/>|<v>[^<]*</v>)?</c>", put, xml)
        patched[fn] = xml
    tmp = path + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as out:
        for n in names:
            out.writestr(zf.getinfo(n), patched.get(n, zf.read(n)))
    zf.close()
    os.replace(tmp, path)


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
    assert wb.sheetnames == ["Start Here", TABS["near"], TABS["new"], TABS["all"], TABS["builders"], TABS["pitch"], "Terms"], wb.sheetnames
    assert res["near"] == len(sample["nearFinish"]), res
    assert res["new"] == 1, res
    allp = wb[TABS["all"]]
    assert [allp[f"{c}11"].value for c in "CDE"] == ["ADDRESS", "REPORTED COST", "BUILDER"], [allp[f"{c}11"].value for c in "CDE"]
    stages = [allp[f"G{r}"].value for r in range(12, 12 + res["projects"])]
    assert stages == sorted(stages, key=lambda s: STAGE_ORDER.get(s, 3)), "All projects not closest-to-clean first"
    assert "C12" in allp.auto_filter.ref or allp.auto_filter.ref.startswith("C11"), allp.auto_filter.ref
    assert any(CITY_DISCLAIMER == c.value for row in wb["Terms"].iter_rows() for c in row)
    # every formula cell carries its stored result (holdout round 6: blank in viewers that do not recalculate)
    cached = load_workbook(out, data_only=True)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for c in row:
                if isinstance(c.value, str) and c.value.startswith("="):
                    v, want = cached[ws.title][c.coordinate].value, formula_value(wb, ws, c.value)
                    assert (v if v is not None else "") == want, f"stored value {v!r} != {want!r}: {ws.title}!{c.coordinate} {c.value}"
    assert cached["Start Here"]["C8"].value == res["projects"], cached["Start Here"]["C8"].value
    assert formula_value(wb, allp, '=IF(5>=2,IFERROR(REPT("x",MAX(0,ROUND(5/10*16,0))),""),"")') == "x" * 8
    assert formula_value(wb, allp, '=IFERROR(1/0,"none")') == "none"
    assert _round(2.5) == 3 and _round(-2.5) == -3
    assert cut("a" * 50 + " (bb cc) " + "d" * 80).endswith("…") and "(" not in cut("x " * 40 + "(one two three four five six seven" + " y" * 30)
    # Austin: the same code with the City of Austin's words (tools/leads_cities.py); built from the public free sample
    au = json.load(open(os.path.join(here, "permits", "austin", "sample.json")))
    ids = {q["permit"] for q in au["projects"]}
    adata = {"source": au["source"], "window": au["window"], "counts": au["counts"],
             "projects": au["projects"] + [q for q in au["nearFinish"] if q["permit"] not in ids]}
    out2 = os.path.join(tempfile.mkdtemp(), "a.xlsx")
    res2 = build(adata, out2)
    wa = load_workbook(out2)
    assert PRODUCT == "Austin Construction Cleaning Leads" and wa.sheetnames == wb.sheetnames
    assert [wa[TABS["all"]][f"{c}11"].value for c in "CDEF"] == ["ADDRESS", "VALUATION", "BUILDER", "ZIP CODE"]
    cells = [str(c.value) for ws in wa.worksheets for row in ws.iter_rows() for c in row if c.value is not None]
    assert LC.AUSTIN["disclaimer"] in cells and not any("Chicago" in c for c in cells), [c for c in cells if "Chicago" in c][:3]
    assert res2["near"] == len(au["nearFinish"]), res2
    use("chicago")
    print("selftest ok", res, "austin", res2)


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
