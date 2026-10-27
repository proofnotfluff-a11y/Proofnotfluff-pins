#!/usr/bin/env python3
"""Chicago Public Way Permit Cost Calculator: the free page /chicago-public-way-permit-costs/ (site/pages.json kind
"datapage", module dp_cdot_fees; tools/make_site.py calls page_html here). The owner's go, Oct 27, 2026, 12:17 pm ("Let's
do them all", coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 6).

Source, and the only source: the City's CDOT 2026 Permit Fee Schedule ("Effective January 1, 2026"). The shop owner downloaded
the PDF in his own browser on Oct 27, 2026 (the runner could not); tools/dp_cdot_fees_pull.py --from-file extracted its
text to site/datapages/dp_cdot_fees/ (fee-schedule.layout.txt, source.json with the PDF's sha256). The degradation fee
box on page 11 is an image in the PDF, so it is typed into degradation-page11.json and checked by eye.

Every fee below is typed from that text. selftest() finds each table row in fee-schedule.layout.txt and checks its
amounts, in order, on the row's own line, so a changed schedule fails the build (and the monthly Action) instead of
showing an old fee. The calculator runs in the visitor's browser; nothing typed is sent anywhere.

Usage: python3 tools/dp_cdot_fees.py --selftest
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "site", "datapages", "dp_cdot_fees")
DUMPSTER_SLUG = "chicago-dumpster-permits"

META = {"h1": "Chicago Public Way Permit Cost Calculator",
        "card": "What a CDOT permit costs in 2026: dumpster placement, work vehicles and equipment, sidewalk and street closures, and openings, from the City's fee schedule.",
        "keywords": "Chicago dumpster permit cost, CDOT permit fee, Chicago public way permit, sidewalk closure permit Chicago, street opening permit Chicago, Chicago work vehicle permit, moratorium street degradation fee"}

# ---- The 2026 schedule, typed from fee-schedule.layout.txt (page numbers are the schedule's own, "Page n of 12") ----
APP = {   # application fees by closure type: (CBD, outside CBD residential street, outside CBD arterial street)
    "dumpster": {"page": 2, "full": (92.63, 22.60, 56.51), "partial": (92.63, 22.60, 56.51)},
    "occupy": {"page": 6, "full": (316.49, 158.25, 158.25), "partial": (22.60, 22.60, 22.60)},
}
# Dumpster usage, page 2: placement -> Class A outside (1-3 days, month), A inside, B outside, B inside
DUMP_ROWS = ["Alley", "Curb Lane", "Parkway", "Sidewalk"]
DUMP = {"A": {"out": (50.00, 100.00), "in": (100.00, 200.00)}, "B": {"out": (100.00, 200.00), "in": (200.00, 400.00)}}
# Openings, page 2: placement -> fee, unit
OPEN = [("ADA Ramp installation", 389.26, "opening"), ("Street / Alley", 778.54, "opening"), ("Sidewalk", 778.54, "opening"),
        ("Parkway", 389.26, "opening"), ("Soil Borings - Street", 778.54, "opening"), ("Soil Borings - Parkway", 389.26, "block"),
        ("Well Monitoring", 778.54, "opening")]
# Vehicles, equipment and other items, page 7: (group, placement as printed, outside CBD, inside CBD, unit)
#   units: day_vehicle, vehicle, foot, foot_month, driveway
ITEMS = [
    ("Parking vehicles", "Parking Moving Van", 30.00, 60.00, "day_vehicle"),
    ("Parking vehicles", "Citywide (Annual)", 600.00, 600.00, "vehicle"),
    ("Parking vehicles", "Residential (Annual)", 100.00, 100.00, "vehicle"),
    ("Parking vehicles", "Work Vehicle Daily-Alley", 30.00, 60.00, "day_vehicle"),
    ("Parking vehicles", "Work Vehicle Daily-Curb Lane", 30.00, 60.00, "day_vehicle"),
    ("Parking vehicles", "Work Vehicle Daily-Curb/Traffic Lane", 30.00, 60.00, "day_vehicle"),
    ("Parking vehicles", "Work Vehicle Daily-Traffic Lane", 30.00, 60.00, "day_vehicle"),
    ("Parking vehicles", "Work Vehicle - Alley (if a lane of at least 10 feet is left unobstructed)", 6.00, 12.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Alley (if a lane of at least 10 feet is not left unobstructed)", 12.00, 24.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Bicycle Lane", 5.00, 10.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Curb Lane", 12.00, 24.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Traffic Lane", 24.00, 48.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Sidewalk or parkway partial closure", 2.50, 5.00, "foot"),
    ("Parking vehicles", "Work Vehicle - Sidewalk or parkway total closure", 5.00, 10.00, "foot"),
    ("Parking vehicles", "Parking / Various Locations (Monthly)", 20.00, 100.00, "vehicle"),
    ("Parking vehicles", "Parking / Various Locations (Semi-Annual)", 100.00, 500.00, "vehicle"),
    ("Operating equipment", "Alley (if a lane of at least 10 feet is left unobstructed)", 3.00, 6.00, "foot"),
    ("Operating equipment", "Alley (if a lane of at least 10 feet is not left unobstructed)", 6.00, 12.00, "foot"),
    ("Operating equipment", "Bicycle Lane", 2.50, 5.00, "foot"),
    ("Operating equipment", "Curb Lane", 6.00, 12.00, "foot"),
    ("Operating equipment", "Sidewalk or parkway partial closure", 1.25, 2.50, "foot"),
    ("Operating equipment", "Sidewalk or parkway total closure", 2.50, 5.00, "foot"),
    ("Operating equipment", "Traffic Lane", 12.00, 24.00, "foot"),
    ("Other", "Barricade - Sidewalk or parkway closure", 2.50, 5.00, "foot_month"),
    ("Other", "Temporary Driveway", 100.00, 100.00, "driveway"),
]
# Monthly usage fees (Types I, II and III), page 9. CBD amounts; outside the CBD the fees are one-half.
# Each row: A (per foot) and B (minimum monthly fee) for the columns
#   1 to 3 days (all types) | Types I & III: 4-180, 181-360, 361-540, 541-720, 721+ | Type II: 4-540, 541+
# "C" and "D" in the 721+ column: previous monthly fee + $4.00 (C) or $8.00 (D) x length.
USAGE = [
    ("Sidewalk or parkway - partial closure", [2.50, 5.00, 10.00, 14.00, 19.00, "C", 5.00, 10.00],
     [48.00, 96.00, 192.00, 288.00, 384.00, 384.00, 96.00, 192.00]),
    ("Sidewalk or parkway - total closure", [5.00, 10.00, 19.00, 29.00, 38.00, "D", 10.00, 19.00],
     [96.00, 192.00, 384.00, 576.00, 768.00, 768.00, 192.00, 384.00]),
    ("Bicycle lane - total closure", [5.00, 10.00, 19.00, 29.00, 38.00, 38.00, 10.00, 19.00],
     [96.00, 192.00, 384.00, 576.00, 768.00, 768.00, 192.00, 384.00]),
    ("Street lane containing parking spaces", [12.00, 24.00, 48.00, 72.00, 96.00, 96.00, 24.00, 48.00],
     [240.00, 480.00, 960.00, 1440.00, 1920.00, 1920.00, 480.00, 960.00]),
    ("Street lane normally used for vehicular traffic, including a bus lane", [24.00, 48.00, 96.00, 144.00, 192.00, 192.00, 48.00, 96.00],
     [480.00, 960.00, 1920.00, 2880.00, 3840.00, 3840.00, 960.00, 1920.00]),
    ("Alley - if a lane of at least 10 feet is left unobstructed", [6.00, 12.00, 24.00, 36.00, 48.00, 48.00, 12.00, 24.00],
     [120.00, 240.00, 480.00, 720.00, 960.00, 960.00, 240.00, 480.00]),
    ("Alley - if a lane of at least 10 feet is not left unobstructed", [12.00, 24.00, 48.00, 72.00, 96.00, 96.00, 24.00, 48.00],
     [240.00, 480.00, 960.00, 1440.00, 1920.00, 1920.00, 480.00, 960.00]),
]
STEP = {"C": 4.00, "D": 8.00}


def load_source():
    f = os.path.join(DIR, "source.json")
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def load_degradation():
    return json.load(open(os.path.join(DIR, "degradation-page11.json"), encoding="utf-8"))


def lastmod(p):
    s = load_source()
    return s["fetchedAt"][:10] if s else None


# ---- The maths, mirrored exactly by the page's script (selftest compares them on planted cases) ----
def usage_fee(row, typ, cbd, days, feet):
    """Total occupy usage fee for one placement: 1 to 3 days is one charge; longer, every 30-day block (MCC: "All
    Occupy permits are issued for 30-day increments") is charged at the column for the days it falls in, at the per-foot
    rate times the length or the minimum monthly fee, whichever is more. Outside the CBD everything is one-half.
    Returns (total, [(first day, last day, fee)])."""
    name, A, B = USAGE[row]
    if days <= 0 or feet <= 0:
        return 0.0, []
    half = 1.0 if cbd else 0.5
    if days <= 3:
        f = max(A[0] * feet, B[0])
        return round(f * half, 2), [(1, days, round(f * half, 2))]
    blocks, prev, total = [], 0.0, 0.0
    for k in range((days + 29) // 30):
        s = 30 * k + 1
        if typ == "II":
            col = 6 if s <= 540 else 7
        else:
            col = 1 if s <= 180 else 2 if s <= 360 else 3 if s <= 540 else 4 if s <= 720 else 5
        a, b = A[col], B[col]
        f = max(prev + STEP[a] * feet, b) if isinstance(a, str) else max(a * feet, b)
        prev = f
        blocks.append((s, min(s + 29, days), round(f * half, 2)))
        total += f * half
    return round(total, 2), blocks


def degradation(age_months, trench_feet=None):
    d = load_degradation()
    p = next((m["P"] for m in d["multiplier"] if age_months <= m["maxMonths"]), None)
    if p is None or age_months <= 0:
        return 0.0
    ol = d["overallLengthForCuts"] if trench_feet is None else max(trench_feet, d["trenchMinimumFeet"])
    return p * (ol / 200) * d["baseRate"]


def money(x):
    return f"${x:,.2f}"


CSS = ("<style>"
       ".pf-pick{display:flex;flex-wrap:wrap;gap:8px;border:0;margin:0 0 16px;padding:0}"
       ".pf-pick legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 8px;padding:0;width:100%}"
       ".pf-pick label{position:relative;display:inline-flex;align-items:center;min-height:44px;padding:0 15px;border:1px solid var(--line);border-radius:999px;"
       "font-size:15px;font-weight:600;color:var(--ink2);cursor:pointer;background:var(--card)}"
       ".pf-pick input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}"
       ".pf-pick label:has(input:checked){background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".pf-pick label:has(input:focus-visible){outline:3px solid var(--focus,var(--accent));outline-offset:2px}"
       ".pf-sec[hidden]{display:none}.pf-out[hidden]{display:none}"
       ".pf .row.pick{grid-template-columns:1fr}.pf .row.pick .field select{text-align:left}"
       ".pf .help{margin:6px 0 0;font-size:13.5px;color:var(--muted)}"
       ".pf-src{margin:10px 0 0;font-size:14px;color:var(--muted)}"
       ".pf-blocks{margin:10px 0 0;font-size:14px}.pf-blocks summary{cursor:pointer;font-weight:600;min-height:44px;display:flex;align-items:center}"
       ".pf-blocks ol{margin:6px 0 0;padding-left:20px}.pf-blocks li{margin:3px 0;font-variant-numeric:tabular-nums}"
       ".pf-tw{overflow-x:auto;margin:12px 0 4px;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".pf-tw:focus-visible{outline:3px solid var(--focus,var(--accent));outline-offset:2px}"
       ".pf-t{width:100%;border-collapse:collapse;font-size:14.5px}.pf-t th,.pf-t td{padding:8px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums;vertical-align:top}"
       ".pf-t th:first-child,.pf-t td:first-child{text-align:left}.pf-t thead th{font-size:13px;color:var(--muted);font-weight:700}"
       ".pf-t tbody th{font-weight:600;color:var(--ink);text-align:left}.pf-t tr:last-child>*{border-bottom:0}"
       ".pf-ref h3{margin:22px 0 4px;font-size:17px}.pf-ref .asof{margin-top:4px}"
       ".pf-eff{display:flex;flex-wrap:wrap;gap:6px 16px;margin:14px 0 20px;font-size:14.5px;color:var(--ink2)}.pf-eff b{color:var(--ink)}"
       "#pf-res .pf-tiles{grid-template-columns:1fr}#pf-res .tile.key .val{font-size:40px}"
       ".ld-heroact .st-btn2{min-height:50px;display:inline-flex;align-items:center;justify-content:center}.pf-ref h3{text-wrap:pretty}"
       ".ld-cta .ld-buybtn{margin-top:18px}.pf .calc-reset{border-top:0;padding-top:4px}"
       ".pf .row.pick select{appearance:none;-webkit-appearance:none;padding-right:40px}.pf .row.pick .field{position:relative}"
       ".pf .row.pick .field::after{content:'';position:absolute;right:16px;top:50%;width:8px;height:8px;border-right:2px solid var(--input-ink);border-bottom:2px solid var(--input-ink);transform:translateY(-70%) rotate(45deg);pointer-events:none}"
       ".pf-ref .asof,.pf-ref .pf-note{font-size:14.5px;color:var(--muted);margin:4px 0 0;max-width:72ch}"
       "@media(min-width:760px){.pf-ref .pf-tw:not(.wide-tw),.pf-more,.pf-how details{max-width:860px}}"
       ".pf-how>p b{color:var(--ink)}.pf-how details{margin:10px 0 0}.pf-how summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".pf-how details{border:0;background:none;border-radius:0}.pf-how details[open] summary{margin-bottom:8px}"
       "#calc{scroll-margin-top:96px}#fees{scroll-margin-top:96px}"
       ".pf-pick{display:grid;grid-template-columns:1fr 1fr}.pf-pick legend{grid-column:1/-1}.pf-pick label{justify-content:center;text-align:center;min-height:48px;border-radius:12px;padding:6px 12px;line-height:1.25}"
       ".pf-t.wide{min-width:820px}.pf-t.wide th:first-child,.pf-t.wide td:first-child{position:sticky;left:0;background:var(--card);min-width:190px;z-index:1}"
       ".pf-swipe{display:none;margin:8px 0 0;font-size:13.5px;color:var(--muted)}"
       ".pf-more{margin:10px 0 0}.pf-more>summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".pf-more{border:0;background:none;border-radius:0}.pf-more[open]>summary{margin-bottom:6px}"
       "@media(max-width:599px){.pf-t{font-size:13.5px}.pf-t th,.pf-t td{padding:8px 8px}.pf-swipe{display:block}#pf-res .tile.key .val{font-size:34px}"
       ".pf-t.app tbody th{white-space:nowrap}.pf-t thead th:not(:first-child){white-space:nowrap}.ld-heroact{display:grid;grid-template-columns:1fr 1fr;gap:10px}.ld-heroact .btn,.ld-heroact .st-btn2{width:100%}"
       ".pf-eff span:last-child{flex-basis:100%;font-size:13.5px;color:var(--muted)}}"
       "</style>")


def _opts(pairs, val=None):
    import html
    return "".join(f'<option value="{html.escape(str(v))}"{" selected" if str(v) == str(val) else ""}>{html.escape(t)}</option>' for v, t in pairs)


def _sel(key, label, hint, pairs, val=None):
    import html
    return (f'<div class="row pick"><label for="{key}">{html.escape(label)}{f"<small>{html.escape(hint)}</small>" if hint else ""}</label>'
            f'<div class="field"><select id="{key}">{_opts(pairs, val)}</select></div></div>')


def _num(key, label, value, hint="", suf=""):
    import html
    return (f'<div class="row"><label for="{key}">{html.escape(label)}{f"<small>{html.escape(hint)}</small>" if hint else ""}</label>'
            f'<div class="field{" has-suf" if suf else ""}"><input id="{key}" type="text" inputmode="numeric" value="{value}" autocomplete="off">'
            + (f'<span class="suf">{html.escape(suf)}</span>' if suf else "") + "</div></div>")


WHERE = [("cbd", "Inside the CBD"), ("res", "Outside the CBD, residential street"), ("art", "Outside the CBD, arterial street")]


def form_html():
    sec_pick = ('<fieldset class="pf-pick"><legend>What are you pricing?</legend>'
                + "".join(f'<label><input type="radio" name="pf-what" value="{v}"{" checked" if i == 0 else ""}>{t}</label>'
                          for i, (v, t) in enumerate([("dump", "Dumpster"), ("occ", "Vehicle, equipment or barricade"),
                                                      ("use", "Sidewalk or street closure"), ("open", "Opening or cut")]))
                + "</fieldset>")
    dump = ('<fieldset class="pf-sec" data-sec="dump"><legend>Dumpster in the public way</legend>'
            + _sel("d-where", "Where it goes", "The CBD's boundaries are in Municipal Code section 9-4-010", WHERE, "res")
            + _sel("d-class", "Dumpster size", "", [("A", "Class A, 30 cubic yards or less"), ("B", "Class B, more than 30 cubic yards")], "A")
            + _sel("d-place", "Placement", "The fee is the same for each placement", [(x, x) for x in DUMP_ROWS], "Curb Lane")
            + _sel("d-time", "How long", "", [("3", "1 to 3 days"), ("m", "By the month")], "3")
            + _num("d-months", "Months", 1)
            + "</fieldset>")
    import html as _h
    groups = []
    for i, (g, n, *_r) in enumerate(ITEMS):
        if not groups or groups[-1][0] != g:
            groups.append((g, []))
        groups[-1][1].append((i, n))
    item_sel = ('<div class="row pick"><label for="o-item">What you are placing<small>Names as the City\'s schedule prints them</small></label>'
                '<div class="field"><select id="o-item">'
                + "".join(f'<optgroup label="{_h.escape(g)}">' + "".join(f'<option value="{i}"{" selected" if i == 4 else ""}>{_h.escape(n)}</option>' for i, n in xs) + "</optgroup>" for g, xs in groups)
                + "</select></div></div>")
    occ = ('<fieldset class="pf-sec" data-sec="occ"><legend>Work vehicle, equipment or barricade</legend>'
           + _sel("o-where", "Where it goes", "The CBD's boundaries are in Municipal Code section 9-4-010", WHERE, "res")
           + _sel("o-close", "Full or partial closure", "Sets the application fee", [("full", "Full closure"), ("partial", "Partial closure")], "partial")
           + item_sel
           + _num("o-days", "Days", 3) + _num("o-count", "Vehicles", 1) + _num("o-feet", "Length", 40, "", "ft")
           + _num("o-months", "Months", 1)
           + "</fieldset>")
    use = ('<fieldset class="pf-sec" data-sec="use"><legend>Sidewalk or street closure for building work</legend>'
           + _sel("u-cbd", "Where it is", "Outside the CBD the fees are one-half", [("1", "Inside the CBD"), ("0", "Outside the CBD")], "0")
           + _sel("u-type", "Type of work", "", [("I", "Type I: alterations, facade repair, tuckpointing or demolition"), ("II", "Type II: building a new building"),
                                                 ("III", "Type III: routine maintenance in the CBD, like painting or window washing")], "I")
           + _sel("u-row", "What you close", "", [(str(i), r[0]) for i, r in enumerate(USAGE)], "0")
           + _num("u-feet", "Length of frontage closed", 50, "Each foot of frontage", "ft")
           + _num("u-days", "Days it stays in place", 60)
           + "</fieldset>")
    opn = ('<fieldset class="pf-sec" data-sec="open"><legend>Opening or cut in the public way</legend>'
           + _sel("p-place", "Placement", "", [(str(i), n) for i, (n, _f, _u) in enumerate(OPEN)], "1")
           + _num("p-count", "Openings", 1, "Count blocks instead for parkway soil borings")
           + _sel("p-mor", "Moratorium street?", "Newly paved streets and others CDOT protects. Check the ChiStreetWork map", [("0", "No"), ("1", "Yes")], "0")
           + _sel("p-age", "Pavement age", "Moratorium streets only",
                  [(str(m["maxMonths"]), m["label"]) for m in load_degradation()["multiplier"]], "6")
           + _sel("p-kind", "Cut or trench", "Moratorium streets only", [("cut", "A cut"), ("trench", "A trench")], "cut")
           + _num("p-trench", "Trench length", 250, "Trenches only; we read the schedule as at least 200 feet", "ft")
           + "</fieldset>")
    return (f'<form class="card pf" id="pf" novalidate>{sec_pick}{dump}{occ}{use}{opn}'
            '<div class="calc-reset"><button type="reset" class="st-btn2">Reset to the example</button></div></form>')


RESULTS = """<div class="sticky"><div class="card" aria-live="polite" id="pf-res">
<div class="tiles pf-tiles"><div class="tile key"><div class="lab">Estimated CDOT fees</div><div class="val" id="r-total">$0.00</div><div class="sub" id="r-sub">From the 2026 fee schedule</div></div></div>
<ul class="lines" id="r-lines"></ul>
<div id="r-blocks"></div>
<div class="callout warn" id="r-warn" hidden></div>
<div class="callout" id="r-note" hidden></div>
<p class="pf-src">Fees can change; confirm with CDOT before you apply.</p>
</div></div>
<div class="mbar" aria-hidden="true"><span>Estimated CDOT fees</span><b id="m-total">$0.00</b></div>"""


def reference_html(E):
    """Every fee the calculator uses, as the City prints it, so the page reads fully without scripts."""
    def tbl(label, head, rows, wide=False, cls=""):
        return (f'<div class="pf-tw{" wide-tw" if wide else ""}" role="region" aria-label="{E(label)}" tabindex="0"><table class="pf-t{" wide" if wide else ""}{" " + cls if cls else ""}"><thead><tr>'
                + "".join(f'<th scope="col">{E(h)}</th>' for h in head) + "</tr></thead><tbody>"
                + "".join("<tr>" + f'<th scope="row">{E(r[0])}</th>' + "".join(f"<td>{E(c)}</td>" for c in r[1:]) + "</tr>" for r in rows)
                + "</tbody></table></div>")
    d = load_degradation()
    out = ['<section class="block pf-ref" id="fees"><h2>The 2026 fees this calculator uses</h2>'
           '<p>Typed from CDOT\'s 2026 Permit Fee Schedule, with the schedule\'s own page numbers. CBD is the Central Business District.</p>']
    out.append("<h3>Dumpster permits: application fee (page 2)</h3><p class=\"pf-note\">Residential and arterial streets are outside the CBD.</p>"
               + tbl("Dumpster application fees", ["Closure", "CBD", "Residential", "Arterial"],
                     [[k.capitalize() + " closure"] + [money(x) for x in APP["dumpster"][k]] for k in ("full", "partial")], cls="app"))
    out.append("<h3>Dumpster placement usage fee (page 2)</h3><p class=\"asof\">The same for alley, curb lane, parkway and sidewalk.</p>"
               + tbl("Dumpster usage fees", ["Size and location", "1 to 3 days", "Per month"],
                     [[f'Class {c} ({"30 cubic yards or less" if c == "A" else "more than 30 cubic yards"}), {"inside" if w == "in" else "outside"} the CBD',
                       money(DUMP[c][w][0]), money(DUMP[c][w][1])] for c in ("A", "B") for w in ("out", "in")]))
    out.append("<h3>Occupy the public right of way: application fee (page 6)</h3>"
               "<p class=\"asof\">The schedule applies it to work vehicles, temporary driveways, barricades and operating equipment. Residential and arterial streets are outside the CBD.</p>"
               + tbl("Occupy application fees", ["Closure", "CBD", "Residential", "Arterial"],
                     [[k.capitalize() + " closure"] + [money(x) for x in APP["occupy"][k]] for k in ("full", "partial")], cls="app"))
    unit = {"day_vehicle": "per day per vehicle", "vehicle": "per vehicle", "foot": "per foot", "foot_month": "per foot per month", "driveway": "per month for every 25 feet"}
    out.append("<h3>Vehicles, equipment and other items (page 7)</h3><p class=\"asof\">Names as the City's schedule prints them.</p>"
               + f'<details class="pf-more"><summary>Show the {len(ITEMS)} items the calculator prices</summary>'
               + tbl("Vehicle and equipment fees", ["Item", "Outside CBD", "Inside CBD"],
                     [[f"{g}: {n}", f"{money(o)} {unit[u]}", f"{money(i)} {unit[u]}"] for g, n, o, i, u in ITEMS]) + "</details>")
    cols = ["1 to 3 days", "4 to 180", "181 to 360", "361 to 540", "541 to 720", "721 or more", "Type II, 4 to 540", "Type II, 541 or more"]
    rows = []
    for n, A, B in USAGE:
        rows.append([f"{n}: per foot"] + [money(a) if not isinstance(a, str) else a for a in A])
        rows.append([f"{n}: minimum a month"] + [money(b) for b in B])
    out.append("<h3>Monthly usage fees for Types I, II and III (pages 8 and 9)</h3>"
               "<p class=\"asof\">Amounts for the CBD; outside the CBD the fees are one-half. Columns are days in place: 1 to 3 days is for all three types, the next five for Types I and III, the last two for Type II. "
               "The schedule says these fees are subject to a yearly CPI increase of up to 2.5%.</p>"
               + f'<details class="pf-more"><summary>Show all {len(USAGE)} placements</summary>'
               + tbl("Monthly usage fees", ["Placement"] + cols, rows, wide=True)
               + '<p class="pf-swipe">Swipe sideways for all eight columns.</p>'
               + f'<p class="asof">C: the previous monthly fee plus {money(STEP["C"])} times the length. D: the previous monthly fee plus {money(STEP["D"])} times the length.</p></details>')
    out.append("<h3>Openings in the public way (page 2)</h3><p class=\"asof\">Fees double, and a degradation fee is added, on moratorium streets.</p>"
               + tbl("Opening fees", ["Placement", "Fee"], [[n, f"{money(f)} per {u}"] for n, f, u in OPEN]))
    out.append("<h3>Degradation fee on moratorium streets (page 11)</h3>"
               f"<p class=\"pf-note\">Fee = P times (length divided by 200) times {money(d['baseRate'])}, where P is the multiplier for the pavement's age in the table below. For a cut the length is set to 200 feet; for a trench the schedule says a minimum of 200 foot increments, which we read as at least 200 feet, prorated above that. "
               "Residential homeowners are exempt on repairs to existing sewer and water services. Moratorium streets are on CDOT's <a href=\"https://chistreetwork.chicago.gov/map\" rel=\"noopener\">ChiStreetWork map</a>.</p>"
               + tbl("Degradation multiplier", ["Age of the pavement", "Multiplier (P)"], [[m["label"], f'{m["P"]:g}'] for m in d["multiplier"]]))
    out.append("</section>")
    return "".join(out)


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    src = load_source()
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Free Chicago data", "chicago-data/"), (p["h1"], None)])
    faq = p.get("faq") or []
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": p["h1"], "url": url, "applicationCategory": "BusinessApplication",
              "operatingSystem": "Any", "isAccessibleForFree": True, "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP,
                                    ld=M.ld_tags(*[x for x in (crumb_ld, app_ld, faq_ld if faq else None)]) + CSS,
                                    bodycls=' class="ld-page has-mbar"', robots=rb, analytics=M.analytics_tag())
    if not src:
        body = f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The fee schedule is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    dump_live = any(x.get("slug") == DUMPSTER_SLUG for x in M.PAGES_LIVE)
    eff = ('<p class="pf-eff"><span>Fees from <b>CDOT\'s 2026 Permit Fee Schedule</b>, effective <b>January 1, 2026</b></span>'
           f'<span><a href="{E(src["url"])}" rel="noopener">Open the City\'s fee schedule (PDF)</a></span>'
           '<span>Fees can change; confirm with CDOT.</span></p>')
    data = {"app": APP, "dump": DUMP, "open": OPEN, "items": [[g, n, o, i, u] for g, n, o, i, u in ITEMS],
            "usage": [[n, A, B] for n, A, B in USAGE], "step": STEP, "deg": load_degradation()}
    js = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    calc = (f'<section class="block" id="calc"><h2>Price your permit</h2><div class="grid">{form_html()}{RESULTS}</div></section>')
    def lead(x):
        k, sep, rest = x.partition(": ")
        return f"<p><b>{E(k)}:</b> {E(rest)}</p>" if sep and len(k) < 45 else f"<p>{E(x)}</p>"
    meth = p["method"]
    how = ('<section class="block pf-how"><h2>How the calculator reads the schedule</h2>' + lead(meth[0])
           + (f'<details><summary>How each permit type is priced</summary>{"".join(lead(x) for x in meth[1:])}</details>' if len(meth) > 1 else "")
           + "</section>")
    nxt = p.get("next") or {}
    links = ('<section class="block"><div class="cta ld-cta"><div>'
             + (f'<h2>{E(nxt["title"])}</h2><p>{E(nxt["text"])}</p><p class="ld-buybtn"><a class="btn" href="{rel}{DUMPSTER_SLUG}/">{E(nxt["button"])}</a></p>' if dump_live and nxt else
                f'<h2>Apply with CDOT</h2><p>Permits are applied for and paid through CDOT. This page only estimates the fee.</p>')
             + "</div></div></section>")
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>{eff}'
            '<div class="ld-heroact rl-act"><a class="btn" href="#calc">Price a permit</a><a class="st-btn2" href="#fees">See the fee tables</a></div></div>'
            f'{calc}{reference_html(E)}{how}{links}{M.faq_block(faq) if faq else ""}')
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Department of Transportation, <a href="{E(src["url"])}">2026 Permit Fee Schedule</a>, effective January 1, 2026; '
            f'fees checked {E(M.nice_date(src["fetchedAt"][:10]))}. CDOT says permit fees may change year to year and that permittees should review the '
            'schedule before applying.</p>'
            "<p>Estimates for planning only, from the numbers you enter. Not legal, tax or financial advice; CDOT decides the fee on each permit, so check with the agency before you apply. "
            "The calculator runs in your browser; nothing you type is sent anywhere.</p>"
            f"<p>{E(M.CITY_DISCLAIMER['Chicago'])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>"
            "<p>Made by ProofNotFluff with AI assistance from the City's published fee schedule. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p>"
            f'</div></footer>\n<script type="application/json" id="pf-data">{js}</script>\n<script>{JS}</script>\n</body></html>')
    return head(robots) + body + foot


JS = r"""(function(){
var D=JSON.parse(document.getElementById("pf-data").textContent),f=document.getElementById("pf");if(!f)return;
var $=function(id){return document.getElementById(id)};
var num=function(id){var v=parseFloat(String(($(id)||{}).value||"").replace(/[^0-9.]/g,""));return isFinite(v)&&v>0?v:0};
var whole=function(id){return Math.floor(num(id))};
var m=function(x){return "$"+x.toLocaleString("en-US",{minimumFractionDigits:2,maximumFractionDigits:2})};
var col=function(w){return w==="cbd"?0:w==="res"?1:2};
var rowVis=function(id,on){var e=$(id);if(!e)return;var r=e.closest(".row");if(r)r.hidden=!on};
function usage(row,typ,cbd,days,feet){var u=D.usage[row],A=u[1],B=u[2],half=cbd?1:.5,out=[],prev=0,t=0;
 if(days<=0||feet<=0)return[0,out];
 if(days<=3){var f=Math.max(A[0]*feet,B[0])*half;return[f,[[1,days,f]]]}
 for(var k=0;k<Math.ceil(days/30);k++){var s=30*k+1,c=typ==="II"?(s<=540?6:7):(s<=180?1:s<=360?2:s<=540?3:s<=720?4:5),a=A[c],b=B[c];
  var g=typeof a==="string"?Math.max(prev+D.step[a]*feet,b):Math.max(a*feet,b);prev=g;out.push([s,Math.min(s+29,days),g*half]);t+=g*half}
 return[t,out]}
function deg(age,trench){var P=null;D.deg.multiplier.forEach(function(x){if(P===null&&age<=x.maxMonths)P=x.P});if(P===null)return 0;
 var ol=trench===null?D.deg.overallLengthForCuts:Math.max(trench,D.deg.trenchMinimumFeet);return P*(ol/200)*D.deg.baseRate}
window.PF={usage:usage,deg:deg};
function draw(){var what=(f.querySelector("input[name=pf-what]:checked")||{}).value||"dump",L=[],W=[],N=[],total=0,sub="",blocks="";
 f.querySelectorAll(".pf-sec").forEach(function(s){s.hidden=s.getAttribute("data-sec")!==what});
 if(what==="dump"){var w=$("d-where").value,cl=$("d-class").value,inn=w==="cbd"?"in":"out",byM=$("d-time").value==="m",mo=whole("d-months");
  rowVis("d-months",byM);var app=D.app.dumpster.full[col(w)],r=D.dump[cl][inn],use=byM?r[1]*mo:r[0];
  L.push(["Application fee",app]);L.push([byM?"Usage, "+mo+" month"+(mo===1?"":"s")+" at "+m(r[1]):"Usage, 1 to 3 days",use]);total=app+use;
  if(byM&&!mo)W.push("Type how many months the dumpster stays.");sub="Application fee plus usage";
  N.push("The schedule lists a 1 to 3 day fee and a per month fee. Ask CDOT how a stay of 4 days to a month is charged.")}
 if(what==="occ"){var w2=$("o-where").value,it=D.items[+$("o-item").value],u=it[4],rate=w2==="cbd"?it[3]:it[2],app2=D.app.occupy[$("o-close").value][col(w2)];
  var dy=whole("o-days"),ct=whole("o-count"),ft=num("o-feet"),mo2=whole("o-months"),use2=0,lab="";
  rowVis("o-days",u==="day_vehicle");rowVis("o-count",u==="day_vehicle"||u==="vehicle");rowVis("o-feet",u==="foot"||u==="foot_month"||u==="driveway");rowVis("o-months",u==="foot_month"||u==="driveway");
  if(u==="day_vehicle"){use2=rate*dy*ct;lab=dy+" day"+(dy===1?"":"s")+" x "+ct+" vehicle"+(ct===1?"":"s")+" at "+m(rate)}
  if(u==="vehicle"){use2=rate*ct;lab=ct+" vehicle"+(ct===1?"":"s")+" at "+m(rate)}
  if(u==="foot"){use2=rate*ft;lab=ft+" ft at "+m(rate)+" a foot";N.push("The schedule prices this item per foot and does not say over what period. Ask CDOT how long one charge covers.")}
  if(u==="foot_month"){use2=rate*ft*mo2;lab=ft+" ft x "+mo2+" month"+(mo2===1?"":"s")+" at "+m(rate)}
  if(u==="driveway"){var inc=Math.ceil(ft/25);use2=rate*inc*mo2;lab=inc+" x 25 ft x "+mo2+" month"+(mo2===1?"":"s")+" at "+m(rate);N.push("We count a part of 25 feet as a full increment; ask CDOT.")}
  L.push(["Application fee",app2]);L.push(["Usage, "+lab,use2]);total=app2+use2;sub="Application fee plus usage";
  N.push("The schedule applies this application fee to work vehicles, temporary driveways, barricades and operating equipment; ask CDOT whether it applies to your item.");
  if(!use2)W.push("Type the days, vehicles, length or months for this item.")}
 if(what==="use"){var cbd=$("u-cbd").value==="1",ty=$("u-type").value,ft2=num("u-feet"),dy2=whole("u-days"),R=usage(+$("u-row").value,ty,cbd,dy2,ft2);
  total=R[0];L.push(["Usage for "+dy2+" day"+(dy2===1?"":"s")+", "+ft2+" ft"+(cbd?"":" (one-half outside the CBD)"),R[0]]);sub=R[1].length>1?R[1].length+" blocks of 30 days":"One charge";
  if(ty==="III"&&!cbd)W.push("The schedule defines Type III as routine maintenance inside the CBD. Outside it, ask CDOT which type applies.");
  if(!ft2||!dy2)W.push("Type the length closed and the days it stays.");
  if(R[1].length>1)blocks='<details class="pf-blocks"><summary>See each 30-day block</summary><ol>'+R[1].map(function(b){return"<li>Days "+b[0]+" to "+b[1]+": "+m(b[2])+"</li>"}).join("")+"</ol></details>";
  N.push("Our reading: each 30-day block is the per-foot rate times the length or the minimum monthly fee, whichever is more. CDOT may price the whole permit at one column; ask CDOT. If your closure makes metered spaces unusable, CDOT charges for those too; this part of the schedule gives no amount and points to Municipal Code section 9-68-080.")}
 if(what==="open"){var o=D.open[+$("p-place").value],n=whole("p-count"),mor=$("p-mor").value==="1",tr=$("p-kind").value==="trench";
  rowVis("p-age",mor);rowVis("p-kind",mor);rowVis("p-trench",mor&&tr);
  var fee=o[1]*n*(mor?2:1);L.push([n+" "+o[2]+(n===1?"":"s")+" at "+m(o[1])+(mor?", doubled on a moratorium street":""),fee]);total=fee;
  if(mor){var dg=deg(+$("p-age").value,tr?num("p-trench"):null)*(tr?1:n);L.push([tr?"Degradation fee, one trench":"Degradation fee, "+n+" cut"+(n===1?"":"s"),dg]);total+=dg;
   N.push(tr?"We read the schedule as charging a trench on at least 200 feet, prorated above that; ask CDOT.":"We show the degradation fee for each cut; ask CDOT how it charges several cuts.");
   N.push("The schedule says residential homeowners are exempt from the degradation fee on repairs to existing sewer and water services. CDOT decides who qualifies.")}
  N.push("The schedule says to contact 811 Chicago two business days before you dig.");sub=mor?"Permit fees plus degradation fee":"Permit fees";if(!n)W.push("Type how many openings.")}
 $("r-total").textContent=m(total);var mt=$("m-total");if(mt)mt.textContent=m(total);$("r-sub").textContent=sub;
 $("r-lines").innerHTML=L.map(function(x){return"<li><span>"+x[0]+"</span><span>"+m(x[1])+"</span></li>"}).join("")+'<li class="total"><span>Total</span><span>'+m(total)+"</span></li>";
 $("r-blocks").innerHTML=blocks;var wv=$("r-warn"),nv=$("r-note");wv.hidden=!W.length;wv.textContent=W.join(" ");nv.hidden=!N.length;nv.textContent=N.join(" ")}
f.addEventListener("input",draw);f.addEventListener("change",draw);f.addEventListener("reset",function(){setTimeout(draw,0)});f.addEventListener("submit",function(e){e.preventDefault()});draw()})();"""


# ---- Selftest: every fee against the City's text, and the maths on planted cases ----
def _nums(line):
    return [float(x.replace(",", "")) for x in re.findall(r"\d[\d,]*\.\d\d", line)]


def _find(lines, label, values, near=6):
    """True when a line within `near` lines of the line holding `label` carries exactly `values` (money amounts, in order)."""
    key = label.lower()
    hits = [i for i, l in enumerate(lines) if key in l.lower()]
    for i in hits:
        for j in range(max(0, i - near), min(len(lines), i + near + 1)):
            if _nums(lines[j]) == list(values):
                return True
    return False


def selftest():
    lines = open(os.path.join(DIR, "fee-schedule.layout.txt"), encoding="utf-8").read().splitlines()
    text = "\n".join(lines)
    src = load_source()
    assert src and src["sha256"] == "009061e5936dd3335048de2e8b5ccceb216a2504c1b568e12c7dad2209fcd9b7", "the PDF this page was typed from"
    assert "Effective January 1, 2026" in text and "2026 Permit Fee Schedule" in text, "effective date"
    bad = []
    chk = lambda ok, what: ok or bad.append(what)
    for k in ("full", "partial"):   # dumpster application row, then the occupy one (the first and second matching lines)
        rows = [l for l in lines if l.strip().lower().startswith(k + " closure")]
        chk(any(_nums(l) == list(APP["dumpster"][k]) for l in rows), f"dumpster app {k}")
        chk(any(_nums(l) == list(APP["occupy"][k]) for l in rows), f"occupy app {k}")
    for r in DUMP_ROWS:
        want = [DUMP["A"]["out"][0], DUMP["A"]["out"][1], DUMP["A"]["in"][0], DUMP["A"]["in"][1],
                DUMP["B"]["out"][0], DUMP["B"]["out"][1], DUMP["B"]["in"][0], DUMP["B"]["in"][1]]
        chk(any(l.strip().startswith(r) and _nums(l) == want for l in lines), f"dumpster usage {r}")
    for n, fee, u in OPEN:
        chk(_find(lines, n, [fee], 0) and f"{fee:.2f} per {u}" in text, f"opening {n}")
    seen = {}
    for g, n, o, i, u in ITEMS:
        label = n.split(" (if")[0] if "(if" in n else n
        ok = _find(lines, label[:30], [o, i] if u != "driveway" else [o], 7)   # long labels wrap; the amounts sit up to 6 lines below
        chk(ok, f"item {n}")
        seen[n] = ok
    for n, A, B in USAGE:
        a = [x for x in A if not isinstance(x, str)]
        chk(_find(lines, n[:22], a, 3), f"usage A {n}")
        chk(_find(lines, n[:22], B, 3), f"usage B {n}")
    chk("C = Previous monthly fee + $4.00 X length" in text and "D = Previous monthly fee + $8.00 X length" in text, "C and D")
    chk("one-half of the amounts" in text, "outside the CBD is one-half")
    chk("All Occupy permits are issued for 30-day increments" in text, "30-day increments")
    chk("Fees double and a degradation fee" in text, "moratorium doubling")
    assert not bad, "not in the City's text: " + "; ".join(bad)
    # the maths: planted cases worked by hand from the table
    assert usage_fee(0, "I", True, 3, 10) == (48.0, [(1, 3, 48.0)]), "1 to 3 days, the minimum wins"
    assert usage_fee(0, "I", True, 30, 50)[0] == 250.0, "4 to 180: $5.00 x 50 ft beats $96"
    assert usage_fee(0, "I", False, 30, 50)[0] == 125.0, "outside the CBD, one-half"
    t, b = usage_fee(0, "I", True, 210, 10)
    assert [x[2] for x in b] == [96.0] * 6 + [192.0] and t == 768.0, "days 181 to 210 move to the next column"
    t, b = usage_fee(0, "I", True, 750, 100)
    assert b[23][2] == 1900.0 and b[24][2] == 2300.0, "721 or more: previous month plus $4.00 x length (C)"
    assert usage_fee(4, "II", True, 600, 20)[1][-1][2] == 1920.0, "Type II 541 or more: minimum $1,920"
    assert degradation(6) == 20000 and degradation(54, 250) == 3125, "the schedule's two worked examples"
    assert degradation(6, 100) == 20000, "a trench is charged on at least 200 feet"
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("module") == "dp_cdot_fees"][0]
    html = page_html(spec)
    assert html.count("<h1>") == 1 and "\u2014" not in html and "\u2013" not in html, "one h1, no dashes"
    assert "January 1, 2026" in html and "Fees can change; confirm with CDOT" in html and src["url"] in html, "effective date, link, caution"
    assert all(money(x) in html for x in (92.63, 22.60, 56.51, 316.49, 158.25, 778.54, 389.26, 3840.00)), "the reference tables"
    assert isinstance(META["keywords"], str)
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html and 'id="m-total"' in html and 'type="reset"' in html, "City disclaimer, phone bar, reset"
    print("dp_cdot_fees selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
