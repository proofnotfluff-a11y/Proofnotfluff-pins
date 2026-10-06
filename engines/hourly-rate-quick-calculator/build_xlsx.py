#!/usr/bin/env python3
"""#20 Hourly Rate Quick Calculator, version 3 (dashboard design, Oct 6, 2026).

Same inputs, same maths and same worked example as versions 1 and 2:
$60,000 take-home, 25% tax set-aside, $6,000 expenses, 48 weeks x 40 hours, 60% billable
-> $74.65 minimum rate ($75 rounded), a $40 rate keeps $15.66 per hour worked, quote $1,072.50.

Usage: python3 engines/hourly-rate-quick-calculator/build_xlsx.py out.xlsx
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import wb_style as S  # noqa: E402
import pnf_dash as D  # noqa: E402
import re  # noqa: E402
from openpyxl.cell.rich_text import CellRichText, TextBlock  # noqa: E402
from openpyxl.cell.text import InlineFont  # noqa: E402
from openpyxl.styles import Alignment  # noqa: E402

PRODUCT = "Hourly Rate Quick Calculator"
AS_OF = "Figures checked Oct 6, 2026"
OUT = sys.argv[1] if len(sys.argv) > 1 else "Hourly-Rate-Quick-Calculator.xlsx"
USD0, USD2, PCT, INT, NUM1 = S.FMT["usd0"], S.FMT["usd2"], S.FMT["pct"], S.FMT["int"], S.FMT["num1"]

wb = S.new_workbook(PRODUCT, version="3")

# =====================================================================  Calculator
ws = wb.create_sheet("Calculator")
S.set_widths(ws, {"A": 3, "B": 2, "C": 31, "D": 14, "E": 2, "F": 3, "G": 2, "H": 24, "I": 12, "J": 17, "K": 2, "L": 3})
r = D.page_header(ws, PRODUCT, "Find the hourly rate that pays you the take-home you want, then test any rate against it.", AS_OF)

# ---- the cards are laid out first so the tiles can point at real cells
TOP = 11
# Left column: Your numbers
A = D.Card(ws, TOP, "B", "C", "D", "E", wb=wb)
A.title("Your numbers", "Type over the yellow cells. Every other number updates.")
A.eyebrow("WHAT YOU WANT TO TAKE HOME")
TH = A.input("Take-home pay you want per year", 60000, USD0, name="TakeHome", validation=("decimal", 0, None),
             prompt="What you want left after tax for the whole year, in dollars. Example: 60000.")
TX = A.input("Tax set-aside rate", 0.25, PCT, name="TaxRate", validation=("decimal", 0, 0.9),
             prompt="Share of profit you set aside for tax. Type a percent, for example 25%. See Notes and sources below.")
EX = A.input("Business expenses per year", 6000, USD0, name="Expenses", validation=("decimal", 0, None),
             prompt="Software, insurance, equipment, phone, fees, mileage, training: everything the business pays for in a year.")
A.eyebrow("YOUR WORKING TIME")
WK = A.input("Weeks you work per year", 48, INT, name="WeeksPerYear", validation=("decimal", 1, 52),
             prompt="52 minus holidays, sick days and time off. Example: 48.")
HW = A.input("Hours you work per week", 40, INT, name="HoursPerWeek", validation=("decimal", 1, 100),
             prompt="All hours, including admin, quoting, marketing and travel. Example: 40.")
BS = A.input("Share of hours a client pays for", 0.6, PCT, name="BillableShare", validation=("decimal", 0.05, 1),
             prompt="Only hours a client pays for. Admin, quotes, marketing and travel are not billable. Example: 60%.")
A.close()

# Right column: How your rate is built
B = D.Card(ws, TOP, "G", "H", "I", "K", extra="J", wb=wb)
B.title("How your rate is built", "Your target, grossed up for tax and costs, spread over the hours you bill.")
b_take = B.calc("Take-home you want", f"=$D${TH}", USD0)
b_tax = B.calc("Plus tax set-aside", f'=IFERROR($D${TH}/(1-$D${TX})-$D${TH},"")', USD0)
b_exp = B.calc("Plus business expenses", f"=$D${EX}", USD0)
b_rev = B.calc("Revenue you need", f'=IFERROR(SUM(I{b_take}:I{b_exp}),"")', USD0, total=True)
B.eyebrow("SPREAD OVER YOUR BILLABLE HOURS")
b_work = B.calc("Hours you work per year", f"=$D${WK}*$D${HW}", INT)
b_bill = B.calc("Hours a client pays for", f"=I{b_work}*$D${BS}", INT)
b_rate = B.calc("Minimum hourly rate", f'=IFERROR(I{b_rev}/I{b_bill},"")', USD2, total=True, tint="total_tint")
B.eyebrow("WHERE EACH BILLABLE HOUR GOES")
s1 = B.r; s3 = B.r + 2
mx = f"MAX($I${s1}:$I${s3})"
B.bar("Your take-home", f'=IFERROR($D${TH}/I{b_bill},"")', USD2, mx, "teal")
B.bar("Tax set-aside", f'=IFERROR(I{b_tax}/I{b_bill},"")', USD2, mx, "accent")
B.bar("Business expenses", f'=IFERROR($D${EX}/I{b_bill},"")', USD2, mx, "gold")
B.close()

# Left column, second card: Check a rate
C = D.Card(ws, A.end + 2, "B", "C", "D", "E", wb=wb)
C.title("Check a rate you are considering", "What a rate really pays you once costs and tax come out.")
RC = C.input("Hourly rate to check", 40, USD0, name="RateToCheck", validation=("decimal", 0, None),
             prompt="Any hourly rate you charge now or are thinking of. Example: 40.")
c_rev = C.calc("Revenue at this rate", f"=$D${RC}*$I${b_bill}", USD0)
c_exp = C.calc("Less business expenses", f"=-$D${EX}", USD0)
c_tax = C.calc("Less tax set-aside", f"=-MAX(0,D{c_rev}+D{c_exp})*$D${TX}", USD0)
c_take = C.calc("Take-home at this rate", f"=SUM(D{c_rev}:D{c_tax})", USD0, total=True)
c_hr = C.calc("Per hour you actually work", f'=IFERROR(D{c_take}/$I${b_work},"")', USD2, bold=True)
GAP = f"($D${c_take}-$D${TH})"
c_pill = C.text(f'=IF(OR($D${TH}="",$D${RC}=""),"",IF({GAP}<0,"Short of your take-home goal by "&TEXT(-{GAP},"$#,##0")&" a year",'
                f'"Above your take-home goal by "&TEXT({GAP},"$#,##0")&" a year"))', size=10, color="ink", bold=True)
ws[f"C{c_pill}"].alignment = Alignment(horizontal="center", vertical="center")
C.close()
D.status_rule(ws, f"C{c_pill}:D{c_pill}", f"{GAP}<0")

# Right column, second card: billable share
E = D.Card(ws, B.end + 2, "G", "H", "I", "K", extra="J", wb=wb)
E.title("Bill more of your week", "Same goal, tax and costs: the rate you need at each billable share.")
e1 = E.r; e4 = E.r + 3
emx = f"MAX($I${e1}:$I${e4})"
for share in (0.5, 0.6, 0.7, 0.8):
    rr = E.bar(f"{int(share * 100)}% of your hours billed", f'=IFERROR($I${b_rev}/($I${b_work}*{share}),"")', USD2, emx, "blue")
    D.highlight_rule(ws, f"H{rr}:I{rr}", f"ROUND($D${BS},2)={share}")
E.text("The row in yellow matches your own billable share. Billing one more hour a day lowers the rate you need; "
       "it does not lower what you keep.", height=D.GRID_ROW * 2)
E.close()

# ---- hero tiles (rows 6 to 9), now that every cell exists
RATE = f"$I${b_rate}"
D.tile(ws, 6, "B", "E", "YOUR MINIMUM HOURLY RATE", f"={RATE}", USD2,
       f'=IFERROR("Rounded up for your rate card: "&TEXT(CEILING({RATE},5),"$#,##0")&" an hour","")', dark=True)
v, sub, _ = D.tile(ws, 6, "G", "K", f'="CHARGE "&TEXT($D${RC},"$#,##0")&" AN HOUR AND YOU REALLY KEEP"',
                   f"=$D${c_hr}", USD2,
                   f'=IF(OR($D${TH}="",$D${RC}=""),"",IF({GAP}<0,"per hour worked, "&TEXT(-{GAP},"$#,##0")&" a year short of your goal",'
                   f'"per hour worked, "&TEXT({GAP},"$#,##0")&" a year above your goal"))')
D.status_rule(ws, v.coordinate, f"{GAP}<0", fill_tint=False)
h10 = 14
ws.row_dimensions[10].height = h10

# ---- full-width card: Quick quote
q_top = max(C.end, E.end) + 2
for rr in range(q_top, q_top + 8):
    D.h(ws, rr, D.GRID_ROW)
r = q_top + 1
t = ws[f"C{r}"]; t.value = "Quick quote"; t.font = D.f(12, True); ws.merge_cells(f"C{r}:J{r}"); r += 1
t = ws[f"C{r}"]; t.value = "Turn your rate-card rate into a price for one job."; t.font = D.f(9, False, "muted")
t.alignment = Alignment(vertical="top")
ws.merge_cells(f"C{r}:J{r}"); r += 1
QK = D.Card.__new__(D.Card)  # reuse the row helpers for both halves without opening a new frame
QK.ws, QK.wb, QK.left, QK.label, QK.value, QK.right, QK.extra = ws, wb, "B", "C", "D", "E", None
QK.r = r
JH = QK.input("Billable hours for the job", 12, NUM1, name="JobHours", validation=("decimal", 0, None),
              prompt="Your best estimate of billable hours on this job, for example 12 or 2.5.")
JM = QK.input("Materials and other job costs", 150, USD0, name="Materials", validation=("decimal", 0, None),
              prompt="Parts, supplies, subcontractors, permits or travel you want the client to cover.")
MU = QK.input("Markup on materials", 0.15, PCT, name="Markup", validation=("decimal", 0, 5),
              prompt="Covers the time and cash tied up buying materials. Type 0% to pass costs through.")
QR = D.Card.__new__(D.Card)
QR.ws, QR.wb, QR.left, QR.label, QR.value, QR.right, QR.extra = ws, wb, "G", "H", "I", "K", "J"
QR.r = r
q_lab = QR.calc("Labor", f'=IFERROR($D${JH}*CEILING({RATE},5),"")', USD2)
ws[f"H{q_lab}"] = f'=IFERROR("Labor at "&TEXT(CEILING({RATE},5),"$#,##0")&" an hour","Labor")'
q_mat = QR.calc("Materials with markup", f"=$D${JM}*(1+$D${MU})", USD2)
q_tot = QR.calc("Quote total", f'=IFERROR(I{q_lab}+I{q_mat},"")', USD2, total=True, tint="total_tint")
ws[f"I{q_tot}"].font = D.f(12, True)
q_end = r + 3
D.frame(ws, q_top, q_end, "B", "K")
S.page_break_before(ws, q_top)

# ---- full-width card: Notes and sources
n_top = q_end + 2
NOTES = [
    ("Tax set-aside", "US self-employment tax alone is 15.3% (12.4% Social Security plus 2.9% Medicare), generally on 92.35% of net "
     "earnings, per IRS Topic 554 (irs.gov/taxtopics/tc554, page updated Sep 24, 2026, checked Oct 6, 2026). Federal and state "
     "income tax come on top, so the example uses 25% as a starting point. It is not advice: set your own rate or ask a tax professional."),
    ("Billable hours", "Admin, quoting, marketing and travel are hours no client pays for. Count every one: the share you bill moves "
     "your rate more than any other number here."),
    ("Any currency", "The maths works in any currency. To change the symbol, select the money cells and pick yours under Format, Number."),
    ("Before you rely on a number", "For general information and planning only. This is not legal, tax, financial, medical or other "
     "professional advice, and using it doesn't create a professional relationship. Results are estimates based on the numbers you "
     "enter. Figures were checked on Oct 6, 2026 and can change. See the Terms of Use tab before you rely on anything here."),
]
r = n_top
D.h(ws, r, 12); r += 1
t = ws[f"C{r}"]; t.value = "Notes and sources"; t.font = D.f(12, True); ws.merge_cells(f"C{r}:J{r}"); D.h(ws, r, 24); r += 1
D.h(ws, r, 6); r += 1
width = sum(S.width_of(ws, k) for k in "CDEFGHIJ")
for head, body in NOTES:
    cell = ws[f"C{r}"]
    from openpyxl.cell.rich_text import CellRichText, TextBlock
    from openpyxl.cell.text import InlineFont
    cell.value = CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=9, b=True, color=D.T["ink"]), head + ". "),
                              TextBlock(InlineFont(rFont=D.FONT, sz=9, color=D.T["ink2"]), body))
    cell.alignment = Alignment(vertical="top", wrap_text=True)
    ws.merge_cells(f"C{r}:J{r}")
    D.h(ws, r, S.text_height(head + ". " + body, width, 9) + 4); r += 1
D.h(ws, r, 12)
n_end = r
D.frame(ws, n_top, n_end, "B", "K")
LAST = n_end + 1
D.h(ws, LAST, 14)

D.paint_canvas(ws, LAST, "Z")
S.finish_sheet(ws, PRODUCT, LAST, span=("A", "L"), freeze="A11", tab_color="accent")


# =====================================================================  Start Here
sh = wb.create_sheet("Start Here", 0)
S.set_widths(sh, {"A": 3, "B": 2, "C": 8, "D": 62, "E": 18, "F": 2, "G": 3})
D.page_header(sh, PRODUCT, "Start here. One tab, nine yellow cells, two minutes.", "Checked Oct 6, 2026", span=("B", "F"), side_cols=2)
W = S.width_of(sh, "D") + S.width_of(sh, "E")


def sh_card(top, title, rows):
    """rows: list of (left, text, kind) with kind 'num' | 'chip-in' | 'chip-calc' | 'chip-key' | 'para' | 'link'."""
    r = top
    D.h(sh, r, 12); r += 1
    t = sh[f"C{r}"]; t.value = title; t.font = D.f(12, True); sh.merge_cells(f"C{r}:E{r}"); D.h(sh, r, 24); r += 1
    for left, text, kind in rows:
        full = kind in ("para", "link", "note")
        c = sh[f"C{r}"] if full else sh[f"D{r}"]
        if kind == "link":
            c.value = text[0]; c.hyperlink = text[1]; c.font = D.f(10, False, "blue", underline="single"); body = text[0]
        else:
            c.value = text; c.font = D.f(9 if kind == "note" else 10, False, "muted" if kind == "note" else "ink"); body = text
            m = re.match(r"^([A-Z][A-Za-z ]{1,28})\. (.*)$", text, re.S) if kind == "para" else None
            if m:
                c.value = CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=10, b=True, color=D.T["ink"]), m.group(1) + ". "),
                                       TextBlock(InlineFont(rFont=D.FONT, sz=10, color=D.T["ink"]), m.group(2)))
        c.alignment = Alignment(vertical="center", wrap_text=True)
        if full:
            sh.merge_cells(f"C{r}:E{r}")
            ht = S.text_height(body, W + 8, 10) + 8
        else:
            sh.merge_cells(f"D{r}:E{r}")
            ht = max(S.text_height(body, W, 10) + 10, 30)
        L = sh[f"C{r}"]
        if kind == "num":
            L.value = left; L.font = D.f(18, True, "accent"); L.alignment = Alignment(horizontal="center", vertical="center")
        elif kind.startswith("chip"):
            L.value = left[0]; L.number_format = left[1]; L.alignment = Alignment(horizontal="center", vertical="center")
            if kind == "chip-in":
                L.fill = D.fill("input_fill"); L.font = D.f(9, True, "input_text")
                L.border = D.Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
            elif kind == "chip-calc":
                L.font = D.f(9, False, "ink"); L.border = D.Border(bottom=D.side("hair"))
            else:
                L.fill = D.fill("ink"); L.font = D.f(9, True, "on_ink")
        D.h(sh, r, ht); r += 1
    D.h(sh, r, 12)
    D.frame(sh, top, r, "B", "F")
    return r + 2


r = 6
r = sh_card(r, "What it does", [(None,
    "Type the take-home pay you want, a tax set-aside rate, your yearly business costs and the hours you really work. "
    "The Calculator tab turns them into the minimum hourly rate you must charge, shows what any rate you are considering "
    "really pays you per hour worked, and turns your rate into a quick job quote.", "para")])
r = sh_card(r, "Three steps", [
    (1, "Open the Calculator tab. The example is already filled in, so you can see how every number is made.", "num"),
    (2, "Type over the nine yellow cells with your own numbers. Each one shows a hint when you select it.", "num"),
    (3, "Read your minimum rate in the dark tile at the top, then test any rate in Check a rate and price a job in Quick quote.", "num"),
])
r = sh_card(r, "How to read the cells", [
    ((60000, USD0), "Yellow cells with blue numbers are yours to change. Type over the example.", "chip-in"),
    ((1152, INT), "Plain numbers are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((74.65, USD2), "Dark tiles are your answers. The main one sits at the top of the Calculator tab and stays on screen as you scroll.", "chip-key"),
    (None, "Each tab is protected without a password. To change anything else, use Review, Unprotect Sheet in Excel, or Data, "
           "Protect sheets and ranges in Google Sheets.", "note"),
])
S.page_break_before(sh, r)
r = sh_card(r, "The example", [(None,
    "A $60,000 take-home goal, 25% set aside for tax and $6,000 of yearly costs needs $86,000 of revenue. At 48 weeks of "
    "40 hours with 60% billable, that is 1,152 billable hours, so the minimum rate is $74.65 an hour, or $75 rounded. "
    "Charge $40 instead and you keep $15.66 for every hour you work, $29,940 a year short of the goal.", "para")])
r = sh_card(r, "Good to know", [
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. Every formula is a plain "
           "formula that works in Excel, Google Sheets, Numbers and LibreOffice. No macros, no add-ons, no sign-up.", "para"),
    (None, "More tools. The Terms of Use tab links the full Service Business Pricing Calculator and the Cleaning "
           "Business Starter Kit.", "para"),
])
r = sh_card(r, "Before you rely on a number", [(None,
    "For general information and planning only. This is not legal, tax, financial, medical or other professional advice, and "
    "using it doesn't create a professional relationship. Results are estimates based on the numbers you enter. Figures were "
    "checked on Oct 6, 2026 and can change. See the Terms of Use page before you rely on anything here.", "note")])
SH_LAST = r - 1
D.paint_canvas(sh, SH_LAST, "Z")
S.finish_sheet(sh, PRODUCT, SH_LAST, span=("A", "G"), tab_color="teal")

# =====================================================================  Terms
tm = wb.create_sheet("Terms")
S.set_widths(tm, {"A": 3, "B": 2, "C": 8, "D": 62, "E": 18, "F": 2, "G": 3})
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version 3. Read this before you rely on a number.", "Checked Oct 6, 2026", span=("B", "F"), side_cols=2)
LICENSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "LICENSE-AND-DISCLAIMER.txt")
paras = open(LICENSE, encoding="utf-8").read().strip().split("\n\n")[1:]
sh, _save = tm, sh  # reuse sh_card on this tab
r = 6
r = sh_card(r, "The full versions of this calculator", [
    (None, ("Service Business Pricing Calculator: hourly rate, overhead by category, job quotes, presets for 7 trades",
            "https://www.etsy.com/listing/4587962930"), "link"),
    (None, ("Cleaning Business Starter Kit: pricing calculator, client intake, checklists", "https://www.etsy.com/listing/4588330888"), "link"),
    (None, ("Everything in the shop: etsy.com/shop/ProofNotFluff", "https://www.etsy.com/shop/ProofNotFluff"), "link"),
])
S.page_break_before(tm, r)
r = sh_card(r, "Terms of Use and disclaimer", [(None, p, "para") for p in paras])
r = sh_card(r, "A small ask", [
    (None, "If this calculator earned its $3, a review on Etsy helps other freelancers find it. Thank you.", "para"),
    (None, "If a file won't open or something looks wrong, message the shop on Etsy and it will be fixed.", "para"),
])
TM_LAST = r - 1
D.paint_canvas(tm, TM_LAST, "Z")
S.finish_sheet(tm, PRODUCT, TM_LAST, span=("A", "G"), tab_color="note")
sh = _save

wb.active = 0
problems = [p for p in S.audit(wb) if "input without validation" not in p]
if problems:
    print("AUDIT:", *problems, sep="\n  ")
wb.save(OUT)
print("saved", OUT, {"TH": TH, "rate": b_rate, "check": c_hr, "quote": q_tot})
