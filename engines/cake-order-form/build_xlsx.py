#!/usr/bin/env python3
"""Cake Order Form and Order Tracker Workbook for home bakers, version 1 (v3 dashboard design, Oct 9, 2026).

Three working tabs:
  1 Price List   your price per serving (buttercream and fondant), minimum cake price, deposit, rush
                 and delivery fees, sales tax, the cake size table (servings per size from Wilton's
                 serving guide, editable) and your extras price list. Plus cups to millilitres.
  2 Order Form   one order: customer and date, serving style, finish, up to 4 tier sizes picked from
                 the list, extras with quantities, delivery miles. Servings, cake price, extras,
                 delivery, rush fee, tax, total, deposit and balance fill in on their own. Page 2 of
                 the tab is the customer's one-page order summary.
  3 Order Log    one row per order: dates, customer, cake, total, deposit and final payment. Balance,
                 days to go and a plain-words status fill in; the strip counts what is due this week
                 and what is still owed.

Every lookup reads fixed row ranges (sizes rows 41 to 70, extras rows 78 to 97, log rows 22 to 521),
never a whole column. Formulas sit only in locked white cells: clearing the yellow example cells never
removes a formula. Blank inputs give blank or zero results, never an error value. No TEXT() format
strings, no macros, no tables, no dynamic arrays: same results in Excel and Google Sheets.

Built to design/WORKBOOK_STANDARD.md section 0 with tools/pnf_dash.py and tools/wb_style.py.

  python3 build_xlsx.py Cake-Order-Form-EXAMPLE.xlsx           (the worked example)
  python3 build_xlsx.py Cake-Order-Form.xlsx --blank           (blank)
"""
import datetime as dt
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import wb_style as S  # noqa: E402
import pnf_dash as D  # noqa: E402
from openpyxl.cell.rich_text import CellRichText, TextBlock  # noqa: E402
from openpyxl.cell.text import InlineFont  # noqa: E402
from openpyxl.formatting.rule import FormulaRule  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill  # noqa: E402
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

PRODUCT = "Cake Order Form"
LONG_NAME = "Cake Order Form and Order Tracker Workbook for Home Bakers"
VERSION = "1"
CHECKED = "Oct 9, 2026"
CHECKED_LONG = "October 9, 2026"
AS_OF = f"Version {VERSION}, {CHECKED}"
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
BLANK = "--blank" in args
args = [a for a in args if a != "--blank"]
OUT = args[0] if args else "Cake-Order-Form-EXAMPLE.xlsx"
USD2, INT, DATE = S.FMT["usd2"], S.FMT["int"], S.FMT["date"]
QTY = '#,##0.##;-#,##0.##;0'
PCTIN = '0%'
ML = '#,##0.0 "ml"'
FLOZ = '#,##0.00 "fl oz"'
d = dt.datetime

# ---------------------------------------------------------------- the serving table (Wilton cake serving guide, checked Oct 9, 2026)
# size label, shape, party servings (slices about 1.5 x 2 in), wedding servings (slices about 1 x 2 in); 2-layer, 4 in high cakes
SIZES = [
    ("6 in round", "Round", 12, 12), ("8 in round", "Round", 20, 24), ("9 in round", "Round", 24, 32),
    ("10 in round", "Round", 28, 38), ("12 in round", "Round", 40, 56), ("14 in round", "Round", 63, 78),
    ("16 in round", "Round", 77, 100),
    ("6 in square", "Square", 12, 18), ("8 in square", "Square", 20, 32), ("10 in square", "Square", 30, 50),
    ("12 in square", "Square", 48, 72), ("14 in square", "Square", 63, 98), ("16 in square", "Square", 80, 128),
    ("7 x 11 in sheet", "Sheet", 24, 32), ("9 x 13 in sheet", "Sheet", 36, 50), ("11 x 15 in sheet", "Sheet", 54, 74),
    ("12 x 18 in sheet", "Sheet", 72, 98),
    ("6 in heart", "Heart", 8, 14), ("8 in heart", "Heart", 18, 22), ("9 in heart", "Heart", 20, 28),
    ("10 in heart", "Heart", 24, 38), ("12 in heart", "Heart", 24, 56), ("14 in heart", "Heart", 48, 72),
    ("16 in heart", "Heart", 64, 94),
]
SHAPES = ["Round", "Square", "Sheet", "Heart", "Other"]
# the baker's extras price list (example prices, all editable)
EXTRAS = [
    ("Fondant finish, per tier", 15.00, "Per tier", None), ("Sugar flowers", 6.00, "Each", "About 1 hour each"),
    ("Fresh flowers arranged", 20.00, "Per cake", "Customer's flowers"), ("Custom cake topper", 25.00, "Each", None),
    ("Hand-painted detail", 30.00, "Per tier", None), ("Edible image print", 15.00, "Each", None),
    ("Gold leaf accent", 20.00, "Per cake", None), ("Extra filling flavor", 5.00, "Per tier", None),
    ("Cupcakes", 36.00, "Per dozen", "Matching the cake"), ("Cake box and board", 6.00, "Per cake", None),
    ("Setup at the venue", 25.00, "Per cake", None), ("Cake stand loan", 15.00, "Per cake", "Refunded on return"),
]
PER = ["Each", "Per cake", "Per tier", "Per dozen"]
# US measuring units (NIST Handbook 44, Appendix C, 2023 edition): 1 fl oz = 29.5735 ml; 1 cup = 8 fl oz; 1 tbsp = 1/2 fl oz; 1 tsp = 1/3 tbsp
FLOZ_ML = 29.5735
MEASURES = [("1 cup", 8), ("3/4 cup", 6), ("2/3 cup", 16 / 3), ("1/2 cup", 4), ("1/3 cup", 8 / 3), ("1/4 cup", 2),
            ("1 tablespoon", 0.5), ("1 teaspoon", 1 / 6)]

# ---------------------------------------------------------------- the worked example (a made-up home bakery; names are placeholders)
PRICING = dict(bakery="Maple Lane Cakes (example)", pps_bc=4.50, pps_fd=6.00, min_cake=60.00, deposit=0.50, rush_days=7,
               rush_pct=0.20, deliv_base=10.00, deliv_mile=1.00, tax=0.0,
               terms="Deposit holds the date. Balance due at pickup or delivery.")
ORDER = dict(customer="Casey L. (sample)", contact="555-0134 (sample)", event=d(2026, 11, 14), ordered=d(2026, 10, 9),
             method="Delivery", miles=18, occasion="Wedding, 70 guests", style="Wedding", finish="Fondant",
             override=None, tiers=["10 in round", "8 in round", "6 in round", None], flavor="Vanilla bean",
             filling="Raspberry", design="Ivory fondant, soft ruffles on the bottom tier, sugar flowers cascading down one side")
ORDER_EXTRAS = [("Sugar flowers", 12, "Blush and ivory"), ("Fresh flowers arranged", 1, "Florist delivers to the venue"),
                ("Cake box and board", 1, None)]
LOG = [  # order date, customer, event date, cake, servings, total, deposit paid, final paid, done, note
    (d(2026, 9, 20), "Jordan K. (sample)", d(2026, 10, 3), "9 x 13 in sheet, chocolate, buttercream", 36, 162.00, 81.00, 81.00, "Yes", "Picked up"),
    (d(2026, 9, 28), "Riley T. (sample)", d(2026, 10, 4), "10 in round, lemon, buttercream", 28, 126.00, 63.00, None, None, "Balance not yet paid"),
    (d(2026, 10, 1), "Taylor M. (sample)", d(2026, 10, 11), "8 in round, vanilla, buttercream", 20, 110.00, 55.00, None, None, None),
    (d(2026, 10, 2), "Dakota F. (sample)", d(2026, 10, 10), "Cupcakes, 3 dozen, mixed", 36, 108.00, 108.00, None, None, "Paid up front"),
    (d(2026, 10, 5), "Sam P. (sample)", d(2026, 10, 24), "2 tiers, 8 + 6 in round, fondant", 32, 232.00, 116.00, None, None, None),
    (d(2026, 10, 7), "Morgan D. (sample)", d(2026, 10, 17), "6 in round smash cake", 12, 60.00, None, None, None, "Waiting on the deposit"),
    (d(2026, 10, 8), "Avery B. (sample)", d(2026, 12, 5), "12 in square, winter theme, buttercream", 48, 288.00, 144.00, None, None, None),
    (d(2026, 10, 9), "Casey L. (sample)", d(2026, 11, 14), "3 tiers, 10 + 8 + 6 in round, fondant", 74, 570.00, 285.00, None, None, "See the Order Form tab"),
]
ASOF_DATE = d(2026, 10, 9)


def expected():
    sz = {s[0]: s for s in SIZES}
    ex = {e[0]: e for e in EXTRAS}
    servings = [sz[t][3 if ORDER["style"] == "Wedding" else 2] if t else 0 for t in ORDER["tiers"]]
    tot_serv = sum(servings)
    pps = ORDER["override"] or (PRICING["pps_fd"] if ORDER["finish"] == "Fondant" else PRICING["pps_bc"])
    cake = max(PRICING["min_cake"], tot_serv * pps) if tot_serv else 0
    extras = sum(q * ex[n][1] for n, q, _ in ORDER_EXTRAS)
    deliv = PRICING["deliv_base"] + ORDER["miles"] * PRICING["deliv_mile"] if ORDER["method"] == "Delivery" else 0
    days = (ORDER["event"] - ORDER["ordered"]).days
    rush = round(PRICING["rush_pct"] * (cake + extras), 2) if days < PRICING["rush_days"] else 0
    sub = cake + extras + deliv + rush
    tax = round(sub * PRICING["tax"], 2)
    total = sub + tax
    dep = round(total * PRICING["deposit"], 2)
    asof = ASOF_DATE
    bal_owed = sum((r[5] - (r[6] or 0) - (r[7] or 0)) for r in LOG if r[8] != "Yes")
    due7 = sum(1 for r in LOG if r[8] != "Yes" and 0 <= (r[2] - asof).days <= 7)
    deposits = sum((r[6] or 0) for r in LOG)
    return dict(servings=servings, tot_serv=tot_serv, pps=pps, cake=cake, extras=extras, deliv=deliv, rush=rush, days=days,
                sub=sub, tax=tax, total=total, dep=dep, bal=total - dep, log_n=len(LOG), due7=due7, deposits=deposits,
                bal_owed=bal_owed)


EX = expected()
if BLANK:
    ORDER = dict(customer=None, contact=None, event=None, ordered=None, method=None, miles=None, occasion=None, style="Party",
                 finish="Buttercream", override=None, tiers=[None] * 4, flavor=None, filling=None, design=None)
    ORDER_EXTRAS, LOG = [], []
    PRICING["bakery"] = None

# ---------------------------------------------------------------- fixed addresses
PL_N, OF_N, OL_N = "1 Price List", "2 Order Form", "3 Order Log"
PL, OF, OL = (f"'{n}'" for n in (PL_N, OF_N, OL_N))
N_SIZES, N_EXTRAS, N_LOG = 30, 20, int(os.environ.get("PNF_LOG_ROWS", "500"))
SHIP_LOG = 500
SZ_TOP = 36  # checked by an assert once the cards above are built
SZ_FIRST = SZ_TOP + 5
SZ_LAST = SZ_FIRST + N_SIZES - 1
EX_TOP = SZ_LAST + 3
EX_FIRST = EX_TOP + 5
EX_LAST = EX_FIRST + N_EXTRAS - 1
L_TOP = 17
L_FIRST = L_TOP + 5
L_LAST = L_FIRST + N_LOG - 1
GRID = {"A": 3, "B": 2, "C": 31, "D": 14, "E": 2, "F": 3, "G": 2, "H": 24, "I": 12, "J": 17, "K": 2, "L": 3}


def szr(col):
    return f"{PL}!${col}${SZ_FIRST}:${col}${SZ_LAST}"


def exr(col):
    return f"{PL}!${col}${EX_FIRST}:${col}${EX_LAST}"


def lr(col):
    return f"{OL}!${col}${L_FIRST}:${col}${L_LAST}"


SIZE_NAMES, SIZE_PARTY, SIZE_WED = szr("C"), szr("H"), szr("I")
EXTRA_NAMES, EXTRA_PRICES, EXTRA_PER = exr("C"), exr("D"), exr("H")


def rich(head, body, size=9):
    return CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=size, b=True, color=D.T["ink"]), head + ". "),
                        TextBlock(InlineFont(rFont=D.FONT, sz=size, color=D.T["ink2"]), body))


wb = S.new_workbook(PRODUCT, version=VERSION)

# =====================================================================  1 Price List
pl = wb.create_sheet(PL_N)
S.set_widths(pl, GRID)
D.page_header(pl, "Price list", "Your prices, fees, sizes and extras. The Order Form reads everything here.",
              f"Figures checked {CHECKED}", span=("B", "K"), side_cols=3)
D.h(pl, 6, 10)
D.stat_strip(pl, 7, [
    ("C:D", "Cake sizes on the list", f'=COUNTIF({SIZE_NAMES},"?*")', INT),
    ("H:I", "Extras on the list", f'=COUNTIF({EXTRA_NAMES},"?*")', INT),
    ("J:J", "Rows to fix", "=0", INT),
])
D.h(pl, 9, 10)
D.frame(pl, 6, 9, "B", "K")
D.status_rule(pl, "J8", "$J$8>0", fill_tint=False)
D.h(pl, 10, 14)

P = D.Card(pl, 11, "B", "C", "D", "E", wb=wb)
P.title("Your pricing", "Per-serving prices and fees. Example prices: type over them." if not BLANK else "Per-serving prices and fees. Type yours in the yellow cells.")
P.eyebrow("PER SERVING")
r_bc = P.input("Buttercream, per serving", PRICING["pps_bc"], USD2, name="PriceButtercream", validation=("decimal", 0, 1000),
               prompt="What you charge per serving for a buttercream cake, for example 4.50.", prompt_title="Buttercream per serving")
r_fd = P.input("Fondant, per serving", PRICING["pps_fd"], USD2, name="PriceFondant", validation=("decimal", 0, 1000),
               prompt="What you charge per serving for a fondant-covered cake, for example 6.00.", prompt_title="Fondant per serving")
r_min = P.input("Minimum cake price", PRICING["min_cake"], USD2, name="MinimumCake", validation=("decimal", 0, 100000), allow_blank=True,
                prompt="The least you charge for any cake, for example 60. Small cakes price up to this. Blank or 0 means no minimum.",
                prompt_title="Minimum cake price")
P.eyebrow("FEES")
r_dep = P.input("Deposit to book, % of total", PRICING["deposit"], PCTIN, name="DepositRate", validation=("decimal", 0, 1),
                prompt="The share of the total you ask for to hold the date, for example 50%. Type 0% for no deposit.",
                prompt_title="Deposit to book", error="Type a percent from 0% to 100%, for example 50%.")
r_rdays = P.input("Rush when fewer days than", PRICING["rush_days"], INT, name="RushDays", validation=("whole", 0, 365),
                  prompt="An order with fewer days than this between the order date and the event gets the rush fee, for example 7. Type 0 to turn rush fees off.",
                  prompt_title="Rush days")
r_rpct = P.input("Rush fee, % of cake + extras", PRICING["rush_pct"], PCTIN, name="RushRate", validation=("decimal", 0, 2),
                 prompt="Added to the cake and extras on a rush order, for example 20%.", prompt_title="Rush fee", error="Type a percent from 0% to 200%, for example 20%.")
r_db = P.input("Delivery, base fee", PRICING["deliv_base"], USD2, name="DeliveryBase", validation=("decimal", 0, 10000),
               prompt="What you charge for any delivery before mileage, for example 10. Type 0 if you only charge per mile.",
               prompt_title="Delivery base fee")
r_dm = P.input("Delivery, per mile", PRICING["deliv_mile"], USD2, name="DeliveryPerMile", validation=("decimal", 0, 1000),
               prompt="Added for every mile typed on the Order Form, for example 1.00. Type 0 for a flat fee.", prompt_title="Delivery per mile")
r_tax = P.input("Sales tax rate, if charged", PRICING["tax"], '0.0%', name="SalesTaxRate", validation=("decimal", 0, 0.5),
                prompt="Type a percent, for example 8.25%, or 0% if you don't charge sales tax. Check your own state and local rules.",
                prompt_title="Sales tax rate", error="Type a percent from 0% to 50%, for example 8.25%.")
P.close()
PPS_BC, PPS_FD, MIN_CAKE, DEP, RUSH_DAYS, RUSH_PCT, DELIV_BASE, DELIV_MILE, TAX = (
    f"{PL}!$D${r}" for r in (r_bc, r_fd, r_min, r_dep, r_rdays, r_rpct, r_db, r_dm, r_tax))

M = D.Card(pl, 11, "G", "H", "I", "K", extra="J", wb=wb)
M.title("Cups to millilitres", "NIST Handbook 44, Appendix C (2023), checked Oct 9, 2026.")
M.eyebrow("MEASURE  |  MILLILITRES  |  FLUID OUNCES")
m_first = M.r
for name, floz in MEASURES:
    rr = M.calc(name, f"=ROUND({floz}*{FLOZ_ML},1)", ML)
    pl[f"J{rr}"].value = f"=ROUND({floz},2)"; pl[f"J{rr}"].number_format = FLOZ
    pl[f"J{rr}"].font = D.f(10, False, "ink2"); pl[f"J{rr}"].alignment = Alignment(horizontal="right", vertical="center")
M.eyebrow("YOUR OWN AMOUNT")
r_cups = M.input("Cups", 1.5, QTY, name="CupsToConvert", validation=("decimal", 0, 1000), allow_blank=True,
                 prompt="Type an amount in US cups, for example 1.5, and read the millilitres on the next row.", prompt_title="Cups")
r_cml = M.calc("Millilitres", f'=IF(I{r_cups}="","",ROUND(I{r_cups}*8*{FLOZ_ML},0))', ML, bold=True)
pl[f"J{r_cml}"].value = f'=IF(I{r_cups}="","",ROUND(I{r_cups}*8,2))'; pl[f"J{r_cml}"].number_format = FLOZ
pl[f"J{r_cml}"].font = D.f(10, False, "ink2"); pl[f"J{r_cml}"].alignment = Alignment(horizontal="right", vertical="center")
M.text("1 US cup is 8 fluid ounces and 1 fluid ounce is 29.5735 ml, so a cup is about 236.6 ml. A UK metric cup is 250 ml.", size=9, color="ink2")
M.close()
O = D.Card(pl, max(P.end, M.end) + 2, "B", "C", "D", "K", extra="J", wb=wb)
O.title("On the order form", "Two lines of your own text. Long text runs across the row here and prints in full on the order summary.")
r_bak = O.input("Your bakery name", PRICING["bakery"], S.FMT["text"], name="BakeryName", validation=("textLength", 0, 60), allow_blank=True,
                prompt="Prints at the top of the customer's order summary, for example Maple Lane Cakes.", prompt_title="Your bakery name", error="Up to 60 characters.")
r_terms = O.input("Order terms line", PRICING["terms"], S.FMT["text"], name="OrderTerms", validation=("textLength", 0, 250), allow_blank=True,
                  prompt="One or two sentences that print under the totals: deposit, balance and change rules in your own words.",
                  prompt_title="Order terms line", error="Up to 250 characters.")
O.close()
for rr in (r_bak, r_terms):
    of_cell = pl[f"D{rr}"]; of_cell.alignment = Alignment(horizontal="left", vertical="center", indent=1, wrap_text=False)
    for k in D.cols("E", "J"):
        pl[f"{k}{rr}"].border = Border(bottom=D.side("hair"))
BAKERY, TERMS = f"{PL}!$D${r_bak}", f"{PL}!$D${r_terms}"
assert O.end + 2 == SZ_TOP, (O.end, SZ_TOP)

# ---- cake sizes table
cols_sz = [
    dict(col="C", head="Size", kind="input", values=[s[0] for s in SIZES], validation=("textLength", 1, 30),
         prompt="How you name the size, for example 8 in round or 9 x 13 in sheet. The Order Form picks from this column.",
         error="1 to 30 characters, and different for every row."),
    dict(col="D", head="Shape (pick)", kind="input", values=[s[1] for s in SIZES], validation=("list", SHAPES),
         prompt="Round, Square, Sheet, Heart or Other.", error="Pick a shape from the list."),
    dict(col="H", head="Party servings", kind="input", fmt=INT, align="right", values=[s[2] for s in SIZES], validation=("whole", 0, 1000),
         prompt="Slices about 1.5 x 2 in from a 2-layer cake, per Wilton. Change it to match how you cut.",
         error="Type a whole number from 0 to 1,000."),
    dict(col="I", head="Wedding servings", kind="input", fmt=INT, align="right", values=[s[3] for s in SIZES], validation=("whole", 0, 1000),
         prompt="Slices about 1 x 2 in from a 2-layer cake, per Wilton. Change it to match how you cut.",
         error="Type a whole number from 0 to 1,000."),
    dict(col="J", head="Your note", kind="input", values=[None] * len(SIZES), validation=("textLength", 0, 60),
         prompt="Pan you use, bake time, anything else. Optional.", error="Up to 60 characters."),
]
s1, s2, sz_end = D.table_card(pl, SZ_TOP, "B", "K", cols_sz, N_SIZES, title="Cake sizes and servings",
                              sub="Per Wilton's serving guide, 2-layer cakes (wilton.com, checked Oct 9, 2026): party slice 1.5 x 2 in, wedding 1 x 2 in.")
assert (s1, s2) == (SZ_FIRST, SZ_LAST), (s1, s2)
for rr in range(SZ_FIRST, SZ_LAST + 1):
    for k in ("C", "D", "J"):
        pl[f"{k}{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
S.page_break_before(pl, SZ_TOP)

# ---- extras table
cols_ex = [
    dict(col="C", head="Extra", kind="input", values=[e[0] for e in EXTRAS], validation=("textLength", 1, 40),
         prompt="What the add-on is called, for example Sugar flowers. The Order Form picks from this column.",
         error="1 to 40 characters, and different for every row."),
    dict(col="D", head="Price", kind="input", fmt=USD2, align="right", values=[e[1] for e in EXTRAS], validation=("decimal", 0, 100000),
         prompt="Your price for one of this extra, for example 6.00.", error="Type an amount from 0 to 100,000."),
    dict(col="H", head="Charged per (pick)", kind="input", values=[e[2] for e in EXTRAS], validation=("list", PER),
         prompt="Each, Per cake, Per tier or Per dozen. The Order Form multiplies the price by the quantity you type there.",
         error="Pick one from the list."),
    dict(col="J", head="Your note", kind="input", values=[e[3] for e in EXTRAS], validation=("textLength", 0, 60),
         prompt="Anything worth remembering. Optional.", error="Up to 60 characters."),
]
e1, e2, ex_end = D.table_card(pl, EX_TOP, "B", "K", cols_ex, N_EXTRAS, title="Extras price list",
                              sub="Add-ons the Order Form can pick, with your price for one. Example prices: type over them.")
assert (e1, e2) == (EX_FIRST, EX_LAST), (e1, e2)
for rr in range(EX_FIRST, EX_LAST + 1):
    for k in ("C", "H", "J"):
        pl[f"{k}{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
S.page_break_before(pl, EX_TOP)
for rng_first, rng_last in ((SZ_FIRST, SZ_LAST), (EX_FIRST, EX_LAST)):
    pl.conditional_formatting.add(f"C{rng_first}:C{rng_last}", FormulaRule(
        formula=[f'AND(C{rng_first}<>"",COUNTIF($C${rng_first}:$C${rng_last},C{rng_first})>1)'],
        font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
pl["J8"].value = (f'=SUMPRODUCT(--({SIZE_NAMES}<>""),--(COUNTIF({SIZE_NAMES},{SIZE_NAMES})>1))'
                  f'+SUMPRODUCT(--({EXTRA_NAMES}<>""),--(COUNTIF({EXTRA_NAMES},{EXTRA_NAMES})>1))')
PL_LAST = ex_end + 1
D.h(pl, PL_LAST, 14)
D.paint_canvas(pl, PL_LAST, "Z")
S.finish_sheet(pl, PRODUCT, PL_LAST, span=("A", "L"), freeze="A11", tab_color="gold")
pl.print_area = f"A1:L{PL_LAST}"

# =====================================================================  2 Order Form
of = wb.create_sheet(OF_N)
S.set_widths(of, GRID)
D.page_header(of, "Order form", "Pick the tier sizes and extras; the quote, deposit and balance fill in on their own.",
              "Example order: type over it" if not BLANK else "Type the order in the yellow cells", span=("B", "K"), side_cols=3)

# ---- left: customer and date
A = D.Card(of, 11, "B", "C", "D", "E", wb=wb)
A.title("Customer and date", "Who it is for and when. Prints on the order summary.")
r_cust = A.input("Customer name", ORDER["customer"], S.FMT["text"], name="CustomerName", validation=("textLength", 0, 60), allow_blank=True,
                 prompt="Who the cake is for, for example Casey L.", prompt_title="Customer name", error="Up to 60 characters.")
r_cont = A.input("Phone or email", ORDER["contact"], S.FMT["text"], validation=("textLength", 0, 60), allow_blank=True,
                 prompt="How you reach them. Optional.", prompt_title="Phone or email", error="Up to 60 characters.")
r_evt = A.input("Event date", ORDER["event"], DATE, name="EventDate", validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), allow_blank=True,
                prompt="The day the cake is needed, for example 11/14/2026.", prompt_title="Event date", error="Type a real date between 2000 and 2100, for example 11/14/2026.")
r_ord = A.input("Order date", ORDER["ordered"], DATE, name="OrderDate", validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), allow_blank=True,
                prompt="The day you took the order, for example 10/9/2026. Used with the event date for the rush fee. Leave blank for no rush check.",
                prompt_title="Order date", error="Type a real date between 2000 and 2100, for example 10/9/2026.")
r_meth = A.input("Pickup or delivery (pick)", ORDER["method"], S.FMT["text"], name="PickupOrDelivery", validation=("list", ["Pickup", "Delivery"]), allow_blank=True,
                 prompt="Delivery adds the base fee plus the miles below.", prompt_title="Pickup or delivery")
r_miles = A.input("Delivery miles, one way", ORDER["miles"], QTY, name="DeliveryMiles", validation=("decimal", 0, 1000), allow_blank=True,
                  prompt="Miles from your kitchen to the venue, for example 18. Only used when Delivery is picked.", prompt_title="Delivery miles")
r_occ = A.input("Occasion", ORDER["occasion"], S.FMT["text"], validation=("textLength", 0, 60), allow_blank=True,
                prompt="For example Wedding, 70 guests, or 1st birthday. Optional.", prompt_title="Occasion", error="Up to 60 characters.")
A.close()
for rr in (r_cust, r_cont, r_meth, r_occ):
    of[f"D{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)

# ---- left: the cake
B = D.Card(of, A.end + 2, "B", "C", "D", "E", wb=wb)
B.title("The cake", "Sizes come from the Price List tab, biggest tier first.")
B.eyebrow("SERVINGS AND FINISH")
r_style = B.input("Serving style (pick)", ORDER["style"], S.FMT["text"], name="ServingStyle", validation=("list", ["Party", "Wedding"]),
                  prompt="Party slices are about 1.5 x 2 in; wedding slices about 1 x 2 in, so a wedding cake serves more.", prompt_title="Serving style")
r_fin = B.input("Finish (pick)", ORDER["finish"], S.FMT["text"], name="Finish", validation=("list", ["Buttercream", "Fondant"]),
                prompt="Sets which price per serving is used from the Price List.", prompt_title="Finish")
r_ovr = B.input("Price per serving override", ORDER["override"], USD2, name="PriceOverride", validation=("decimal", 0, 1000), allow_blank=True,
                prompt="Leave blank to use the Price List price. Type a price, for example 5.25, to use it for this order only.",
                prompt_title="Price per serving override")
B.eyebrow("TIERS (PICK A SIZE)")
TIER_ROWS = []
for i in range(4):
    rr = B.input(f"Tier {i + 1}", ORDER["tiers"][i], S.FMT["text"], allow_blank=True)
    dv = DataValidation(type="list", formula1=SIZE_NAMES, allow_blank=True)
    dv.showErrorMessage = True; dv.errorStyle = "stop"; dv.errorTitle = "Check this cell"
    dv.error = "Pick a size from the list on the Price List tab, or leave blank."
    dv.showInputMessage = True; dv.promptTitle = f"Tier {i + 1} size"
    dv.prompt = "Pick a size from the Price List. Leave blank for no tier." if i else "Pick the bottom tier's size from the Price List."
    of.add_data_validation(dv); dv.add(f"D{rr}")
    TIER_ROWS.append(rr)
B.eyebrow("FLAVORS AND DESIGN")
r_flav = B.input("Flavor", ORDER["flavor"], S.FMT["text"], validation=("textLength", 0, 60), allow_blank=True,
                 prompt="Cake flavor, for example Vanilla bean. Optional.", prompt_title="Flavor", error="Up to 60 characters.")
r_fill = B.input("Filling", ORDER["filling"], S.FMT["text"], validation=("textLength", 0, 60), allow_blank=True,
                 prompt="Filling or frosting flavor, for example Raspberry. Optional.", prompt_title="Filling", error="Up to 60 characters.")
r_des = B.input("Design notes", ORDER["design"], S.FMT["text"], validation=("textLength", 0, 250), allow_blank=True,
                prompt="Colors, theme, inspiration. Prints in full on the order summary. Optional.", prompt_title="Design notes", error="Up to 250 characters.")
B.close()
for rr in (r_style, r_fin, r_flav, r_fill, r_des) + tuple(TIER_ROWS):
    of[f"D{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
LEFT_END = B.end

# ---- right: how it's built
R = D.Card(of, 11, "G", "H", "I", "K", extra="J", wb=wb)
R.title("How it's built", "Every line reads the cells on the left and the Price List.")
R.eyebrow("CAKE")
# the tiers card (built after this one) holds the per-tier servings that feed "Servings in total"
def f_serv(tier_row):
    return (f'=IF($D${tier_row}="","",IFERROR(IF({OF}!$D${r_style}="Wedding",INDEX({SIZE_WED},MATCH($D${tier_row},{SIZE_NAMES},0)),'
            f'INDEX({SIZE_PARTY},MATCH($D${tier_row},{SIZE_NAMES},0))),0))')


r_serv = R.calc("Servings in total", "=0", INT)  # filled after the tiers card exists
r_pps = R.calc("Price per serving used", f'=IF($D${r_ovr}<>"",$D${r_ovr},IF($D${r_fin}="Fondant",{PPS_FD},{PPS_BC}))', USD2)
r_cake = R.calc("Cake price", f'=IF(N(I{r_serv})=0,0,MAX(N({MIN_CAKE}),I{r_serv}*N(I{r_pps})))', USD2, bold=True)
r_minnote = R.text(f'=IF(N(I{r_serv})=0,"Pick at least one tier size",IF(I{r_cake}>I{r_serv}*N(I{r_pps}),"Priced up to your minimum cake price",'
                   f'I{r_serv}&" servings at the per-serving price"))', size=9, color="ink2")
R.eyebrow("ADD-ONS")
r_ext = R.calc("Extras (table below)", "=0", USD2)  # filled after the extras table exists
r_del = R.calc("Delivery", f'=IF($D${r_meth}="Delivery",N({DELIV_BASE})+N($D${r_miles})*N({DELIV_MILE}),0)', USD2)
r_rush = R.calc("Rush fee", f'=IF(AND($D${r_ord}<>"",$D${r_evt}<>"",N({RUSH_DAYS})>0,$D${r_evt}-$D${r_ord}<N({RUSH_DAYS})),'
                            f'ROUND(N({RUSH_PCT})*(I{r_cake}+I{r_ext}),2),0)', USD2)
r_sub = R.calc("Subtotal", f"=I{r_cake}+I{r_ext}+I{r_del}+I{r_rush}", USD2, total=True)
r_tax = R.calc("Sales tax", f"=ROUND(I{r_sub}*N({TAX}),2)", USD2)
r_tot = R.calc("Total", f"=I{r_sub}+I{r_tax}", USD2, total=True, tint="total_tint")
R.eyebrow("PAYMENT")
r_dep2 = R.calc("Deposit to book", f"=ROUND(I{r_tot}*N({DEP}),2)", USD2)
r_bal = R.calc("Balance due at the event", f"=I{r_tot}-I{r_dep2}", USD2, bold=True)
r_rpill = R.text(f'=IF(OR($D${r_evt}="",$D${r_ord}=""),"Add the order and event dates for the rush check",'
                 f'IF($D${r_evt}<$D${r_ord},"The event date is before the order date",'
                 f'IF(I{r_rush}>0,"Rush fee applied: "&($D${r_evt}-$D${r_ord})&" days to the event",'
                 f'"No rush fee: "&($D${r_evt}-$D${r_ord})&" days to the event")))', size=9, color="ink2", bold=True)
R.close()
D.status_rule(of, f"H{r_rpill}", f'OR($D${r_evt}<$D${r_ord},I{r_rush}>0)', fill_tint=False)

# ---- right: servings by tier
T = D.Card(of, R.end + 2, "G", "H", "I", "K", extra="J", wb=wb)
T.title("Servings by tier", "From the size table on the Price List, in the serving style picked.")
tier_calc_rows = []
for i, tr in enumerate(TIER_ROWS):
    rr = T.bar(f'=IF($D${tr}="","Tier {i + 1}: none",$D${tr})', f_serv(tr), INT, f"MAX($I${R.end + 5}:$I${R.end + 8})", "teal")
    tier_calc_rows.append(rr)
assert tier_calc_rows[0] == R.end + 5 and tier_calc_rows[-1] == R.end + 8, tier_calc_rows
T.text(f'=IF(N(I{r_serv})=0,"",IF($D${r_style}="Wedding","Wedding slices, about 1 x 2 in","Party slices, about 1.5 x 2 in")&", 2-layer cakes 4 in high")',
       size=9, color="ink2")
T.close()
of[f"I{r_serv}"].value = f"=SUM(I{tier_calc_rows[0]}:I{tier_calc_rows[-1]})"
for rr in tier_calc_rows:
    of[f"H{rr}"].font = D.f(10, False, "ink"); of[f"H{rr}"].alignment = Alignment(horizontal="left", vertical="center")
RIGHT_END = T.end
CARDS_END = max(LEFT_END, RIGHT_END)
for rr in range(11, CARDS_END + 1):
    if of.row_dimensions[rr].height is None:
        D.h(of, rr, D.GRID_ROW)

# ---- extras table (full width)
X_TOP = CARDS_END + 2
X_FIRST = X_TOP + 5
N_X = 6
X_LAST = X_FIRST + N_X - 1
ex_vals = ORDER_EXTRAS + [(None, None, None)] * (N_X - len(ORDER_EXTRAS))


def f_xprice(r):
    return f'=IF($C{r}="","",IFERROR(INDEX({EXTRA_PRICES},MATCH($C{r},{EXTRA_NAMES},0)),""))'


def f_xper(r):
    return f'=IF($C{r}="","",IFERROR(INDEX({EXTRA_PER},MATCH($C{r},{EXTRA_NAMES},0)),"Not on the Price List"))'


def f_xline(r):
    return f'=IF(OR($C{r}="",$D{r}="",I{r}=""),"",$D{r}*I{r})'


cols_x = [
    dict(col="C", head="Extra (pick from the Price List)", kind="input", values=[e[0] for e in ex_vals], validation=("list_range", EXTRA_NAMES),
         prompt="Pick an add-on from the Price List. Add new ones there first.", error="Pick an extra from the list on the Price List tab."),
    dict(col="D", head="Quantity", kind="input", fmt=QTY, align="right", values=[e[1] for e in ex_vals], validation=("decimal", 0, 10000),
         prompt="How many: flowers, tiers, dozens or cakes, as the Price List says it is charged. For example 12.",
         error="Type a quantity of 0 or more."),
    dict(col="H", head="Charged per", kind="calc", formula=f_xper),
    dict(col="I", head="Price each", kind="calc", fmt=USD2, align="right", formula=f_xprice),
    dict(col="J", head="Line total", kind="calc", fmt=USD2, align="right", formula=f_xline, bold=True),
]
x1, x2, x_end = D.table_card(of, X_TOP, "B", "K", cols_x, N_X, title="Extras on this order",
                             sub="Up to 6 add-ons. Price each comes from the Price List; the line total is price times quantity.")
assert (x1, x2) == (X_FIRST, X_LAST), (x1, x2)
for rr in range(X_FIRST, X_LAST + 1):
    of[f"C{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    of[f"H{rr}"].font = D.f(10, False, "muted"); of[f"H{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
of[f"I{r_ext}"].value = f"=SUM(J{X_FIRST}:J{X_LAST})"
of.conditional_formatting.add(f"H{X_FIRST}:H{X_LAST}", FormulaRule(formula=[f'$H{X_FIRST}="Not on the Price List"'],
                              font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))

# ---- tiles
D.tile(of, 6, "B", "E", "QUOTE TOTAL", f"=I{r_tot}", USD2,
       f'=IF(I{r_tot}=0,"Pick a tier size on the left to start the quote",'
       f'"Deposit of "&ROUND(N({DEP})*100,0)&"% to book, balance due on the event date")', dark=True)
v2, _, _ = D.tile(of, 6, "G", "K", "SERVINGS", f"=N(I{r_serv})", INT,
                  f'=IF(N(I{r_serv})=0,"No tier sizes picked yet",COUNTA($D${TIER_ROWS[0]}:$D${TIER_ROWS[-1]})&IF(COUNTA($D${TIER_ROWS[0]}:$D${TIER_ROWS[-1]})=1," tier, "," tiers, ")'
                  f'&IF($D${r_style}="","",LOWER($D${r_style})&" slices")&IF(AND($D${r_style}<>"",$D${r_fin}<>""),", ","")&LOWER($D${r_fin}))', dark=False)
D.status_rule(of, v2.coordinate, f"{v2.coordinate}=0", fill_tint=False)
D.h(of, 10, 14)

# ---- the customer's order summary (page 2 when printed)
S_TOP = x_end + 2
Q = D.Card(of, S_TOP, "B", "C", "D", "K", extra="J", wb=wb)
Q.title("Order summary", "Your order at a glance.")
r_bak2 = Q.text(f'=IF({BAKERY}="","Order summary",{BAKERY}&": order summary")', size=12, color="ink", bold=True)
Q.eyebrow("WHO AND WHEN")
Q.text(f'=IF($D${r_cust}="","Customer: (none yet)","Customer: "&$D${r_cust}&IF($D${r_cont}<>"",", "&$D${r_cont},""))', size=10, color="ink")
q_evt = Q.calc("Event date", f'=IF($D${r_evt}="","",$D${r_evt})', DATE)
q_ord = Q.calc("Order date", f'=IF($D${r_ord}="","",$D${r_ord})', DATE)
Q.text(f'=IF($D${r_meth}="","Pickup or delivery: not picked yet",$D${r_meth}&IF($D${r_meth}="Delivery",", "&N($D${r_miles})&" miles one way",""))'
       f'&IF($D${r_occ}<>"",". "&$D${r_occ},"")', size=10, color="ink")
Q.eyebrow("THE CAKE")
Q.text(f'=IF(N(I{r_serv})=0,"Tiers: none picked yet","Tiers: "&$D${TIER_ROWS[0]}'
       + "".join(f'&IF($D${tr}<>""," + "&$D${tr},"")' for tr in TIER_ROWS[1:]) + ')', size=10, color="ink")
Q.text(f'=IF(N(I{r_serv})=0,"",N(I{r_serv})&" "&LOWER($D${r_style})&" servings, "&LOWER($D${r_fin})&" finish")', size=10, color="ink")
Q.text(f'=IF(AND($D${r_flav}="",$D${r_fill}=""),"",IF($D${r_flav}<>"","Flavor: "&$D${r_flav},"")&IF(AND($D${r_flav}<>"",$D${r_fill}<>""),". ","")'
       f'&IF($D${r_fill}<>"","Filling: "&$D${r_fill},""))', size=10, color="ink")
q_des = Q.text(f'=IF($D${r_des}="","","Design: "&$D${r_des})', size=10, color="ink")
Q.eyebrow("WHAT IT COSTS")
q_cake = Q.calc("Cake", f"=I{r_cake}", USD2)
q_ext = Q.calc("Extras", f"=I{r_ext}", USD2)
q_del = Q.calc("Delivery", f"=I{r_del}", USD2)
q_rush = Q.calc("Rush fee", f"=I{r_rush}", USD2)
q_tax = Q.calc("Sales tax", f"=I{r_tax}", USD2)
q_tot = Q.calc("Total", f"=I{r_tot}", USD2, total=True, tint="total_tint")
q_dep = Q.calc("Deposit to book", f"=I{r_dep2}", USD2)
q_bal = Q.calc("Balance due on the event date", f"=I{r_bal}", USD2, bold=True)
q_terms = Q.text(f'=IF({TERMS}="","",{TERMS})', size=9, color="ink2")
Q.close()
D.h(of, q_des, 42); of[f"C{q_des}"].alignment = Alignment(vertical="center", wrap_text=True)
D.h(of, q_terms, 32)
for rr in (q_evt, q_ord):
    of[f"D{rr}"].alignment = Alignment(horizontal="left", vertical="center")
S.page_break_before(of, X_TOP)
OF_LAST = Q.end + 1
D.h(of, OF_LAST, 14)
D.paint_canvas(of, OF_LAST, "Z")
S.finish_sheet(of, PRODUCT, OF_LAST, span=("A", "L"), freeze="A11", tab_color="accent")
of.print_area = f"A1:L{OF_LAST}"
of.sheet_properties.pageSetUpPr.fitToPage = True
of.page_setup.fitToWidth = 1
of.page_setup.fitToHeight = 2

# =====================================================================  3 Order Log
ol = wb.create_sheet(OL_N)
S.set_widths(ol, {"A": 3, "B": 2, "C": 13, "D": 22, "E": 13, "F": 40, "G": 10, "H": 11, "I": 11, "J": 11, "K": 11, "L": 10,
                  "M": 25, "N": 8, "O": 24, "P": 2, "Q": 3})
D.page_header(ol, "Order log", "One row per order. Balance, days to go and status fill in on their own.",
              "Example rows: type over them" if not BLANK else f"Type your first order in row {L_FIRST}", span=("B", "P"), side_cols=4)
D.h(ol, 6, 10)
ASOF_CELL = "$E$14"
ASOF = f'IF({ASOF_CELL}="",TODAY(),{ASOF_CELL})'
D.stat_strip(ol, 7, [
    ("C:D", "Orders logged", f'=COUNTIF({lr("D")},"?*")', INT),
    ("E:F", "Due in the next 7 days", f'=COUNTIFS({lr("L")},">=0",{lr("L")},"<=7",{lr("N")},"<>Yes")', INT),
    ("G:H", "Deposits received", f'=SUM({lr("I")})', USD2),
    ("I:K", "Balance still owed", f'=SUMIF({lr("N")},"<>Yes",{lr("K")})', USD2),
    ("L:M", "Rows to fix", f'=COUNTIF({lr("M")},"Needs*")', INT),
])
D.h(ol, 9, 10)
D.frame(ol, 6, 9, "B", "P")
D.status_rule(ol, "I8", "$I$8>0", fill_tint=False)
D.status_rule(ol, "L8", "$L$8>0", fill_tint=False)
D.h(ol, 10, 14)
W = D.Card(ol, 11, "B", "D", "E", "G", extra="F", wb=wb)
W.title("Counting from", "Days to go and the 7-day count read this date; blank means today.")
r_asof = W.input("Count from", ASOF_DATE if not BLANK else None, DATE, name="CountFromDate",
                 validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), allow_blank=True,
                 prompt="Leave blank and the log counts from today's date. Type a date, for example 10/9/2026, to look at the log as of that day.",
                 prompt_title="Count from", error="Type a real date between 2000 and 2100, or leave blank.")
W.close()
assert r_asof == 14 and W.end < L_TOP, (r_asof, W.end)


def f_bal(r):
    return f'=IF($H{r}="","",$H{r}-N($I{r})-N($J{r}))'


def f_days(r):
    return f'=IF($E{r}="","",$E{r}-{ASOF})'


def f_status(r):
    return (f'=IF(COUNTA($C{r}:$J{r})=0,"",IF($D{r}="","Needs a customer",IF($E{r}="","Needs an event date",'
            f'IF($H{r}="","Needs a total",IF($N{r}="Yes","Done",IF(K{r}<=0,"Paid in full",IF(L{r}<0,"Past date, balance owed",'
            f'IF(L{r}<=7,"Due this week, balance owed",IF(N($I{r})>0,"Booked, deposit in","Quoted, no deposit yet")))))))))')


cols_lg = [
    dict(col="C", head="Order date", kind="input", fmt=DATE, values=[x[0] for x in LOG], validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"),
         prompt="The day you took the order, for example 10/9/2026.", error="Type a real date between 2000 and 2100."),
    dict(col="D", head="Customer", kind="input", values=[x[1] for x in LOG], validation=("textLength", 0, 40),
         prompt="Who the cake is for.", error="Up to 40 characters."),
    dict(col="E", head="Event date", kind="input", fmt=DATE, values=[x[2] for x in LOG], validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"),
         prompt="The day the cake is needed, for example 11/14/2026.", error="Type a real date between 2000 and 2100."),
    dict(col="F", head="Cake", kind="input", values=[x[3] for x in LOG], validation=("textLength", 0, 80),
         prompt="Sizes, flavor, finish, in a few words. Copy it from the Order Form.", error="Up to 80 characters."),
    dict(col="G", head="Servings", kind="input", fmt=INT, align="right", values=[x[4] for x in LOG], validation=("whole", 0, 10000),
         prompt="Servings in total, from the Order Form. Optional.", error="Type a whole number of 0 or more."),
    dict(col="H", head="Quote total", kind="input", fmt=USD2, align="right", values=[x[5] for x in LOG], validation=("decimal", 0, 1000000),
         prompt="The total from the Order Form, for example 570.00.", error="Type an amount of 0 or more."),
    dict(col="I", head="Deposit paid", kind="input", fmt=USD2, align="right", values=[x[6] for x in LOG], validation=("decimal", 0, 1000000),
         prompt="What the customer has paid to book, for example 285.00. Blank means nothing yet.", error="Type an amount of 0 or more, or leave blank."),
    dict(col="J", head="Final payment", kind="input", fmt=USD2, align="right", values=[x[7] for x in LOG], validation=("decimal", 0, 1000000),
         prompt="The balance payment when it arrives. Blank means not yet.", error="Type an amount of 0 or more, or leave blank."),
    dict(col="K", head="Balance", kind="calc", fmt=USD2, align="right", formula=f_bal, bold=True),
    dict(col="L", head="Days to go", kind="calc", fmt='#,##0;-#,##0;0', align="right", formula=f_days),
    dict(col="M", head="Status", kind="calc", formula=f_status),
    dict(col="N", head="Done (pick)", kind="input", values=[x[8] for x in LOG], validation=("list", ["Yes"]),
         prompt="Pick Yes once the cake is delivered or picked up. Done orders drop out of the due and owed counts.",
         error="Pick Yes, or clear the cell."),
    dict(col="O", head="Note", kind="input", values=[x[9] for x in LOG], validation=("textLength", 0, 120),
         prompt="Anything worth remembering. Optional.", error="Up to 120 characters."),
]
g1, g2, lg_end = D.table_card(ol, L_TOP, "B", "P", cols_lg, N_LOG, title="Your orders",
                              sub=f"Yellow columns are yours; white columns fill in on their own. {SHIP_LOG} rows, all read by the totals.")
assert (g1, g2) == (L_FIRST, L_LAST), (g1, g2)
for rr in range(L_FIRST, L_LAST + 1):
    for k in ("D", "F", "N", "O"):
        ol[f"{k}{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ol[f"M{rr}"].font = D.f(9, True, "ink2"); ol[f"M{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
ol.conditional_formatting.add(f"L{L_FIRST}:L{L_LAST}", FormulaRule(formula=[f'AND(L{L_FIRST}<>"",L{L_FIRST}<0,$N{L_FIRST}<>"Yes")'],
                              font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
for word, color in (("Needs", "accent"), ("Past", "accent"), ("Due this", "gold"), ("Quoted", "gold"), ("Booked", "ink2"),
                    ("Paid", "teal"), ("Done", "muted")):
    ol.conditional_formatting.add(f"M{L_FIRST}:M{L_LAST}", FormulaRule(
        formula=[f'LEFT($M{L_FIRST},{len(word)})="{word}"'], font=Font(color=D.T[color], bold=color != "muted"),
        fill=PatternFill("solid", bgColor=D.T["accent_tint"]) if color == "accent" else None, stopIfTrue=True))
D.paint_canvas(ol, lg_end + 1, "Z")
S.finish_sheet(ol, PRODUCT, lg_end + 1, span=("A", "Q"), freeze=f"A{L_FIRST}", tab_color="blue")
ol.page_setup.orientation = "landscape"
ol.print_title_rows = f"{L_FIRST - 1}:{L_FIRST - 1}"
ol.print_area = f"A1:Q{L_FIRST + 59}"
ol[f"O{L_FIRST - 1}"].alignment = Alignment(horizontal="left", vertical="bottom", wrap_text=True, indent=1)

# =====================================================================  Start Here and Terms
SH_GRID = {"A": 3, "B": 2, "C": 8, "D": 62, "E": 18, "F": 2, "G": 3}


def sh_card(sh, top, title, rows):
    W = S.width_of(sh, "D") + S.width_of(sh, "E")
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
            mm = re.match(r"^([A-Z][A-Za-z0-9 ,]{1,34})\. (.*)$", text, re.S) if kind in ("para", "num") else None
            if mm:
                c.value = CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=10, b=True, color=D.T["ink"]), mm.group(1) + ". "),
                                       TextBlock(InlineFont(rFont=D.FONT, sz=10, color=D.T["ink"]), mm.group(2)))
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
                L.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
            elif kind == "chip-calc":
                L.font = D.f(9, False, "ink"); L.border = Border(bottom=D.side("hair"))
            else:
                L.fill = D.fill("ink"); L.font = D.f(9, True, "on_ink")
        D.h(sh, r, ht); r += 1
    D.h(sh, r, 12)
    D.frame(sh, top, r, "B", "F")
    return r + 2


def money(x):
    return ("-" if x < 0 else "") + f"${abs(x):,.2f}"


sh = wb.create_sheet("Start Here", 0)
S.set_widths(sh, SH_GRID)
D.page_header(sh, "Cake Order Form", "Set your prices once, quote each cake on the Order Form, keep every order in the log.",
              f"Version {VERSION}, {CHECKED}", span=("B", "F"), side_cols=2)
r = 6
r = sh_card(sh, r, "What it does", [(None,
    "A quoting and order-tracking workbook for home bakers and small cake businesses. Type your price per serving, deposit, "
    "rush and delivery fees once on the Price List. On the Order Form, pick up to four tier sizes and any extras: the servings, "
    "cake price, extras, delivery, rush fee, tax, total, deposit and balance fill in on their own, and page 2 of the tab is a "
    "clean order summary to print or save as a PDF for the customer. The Order Log keeps every order with its balance, days to "
    "go and a plain-words status.", "para")])
r = sh_card(sh, r, "Three steps", [
    (1, "Price List tab. Type your price per serving for buttercream and fondant, your minimum, deposit, rush and delivery fees, "
        "and your extras. The size table already holds servings for 24 sizes; change any number to match how you cut.", "num"),
    (2, "Order Form tab. Type the customer and dates, pick the serving style, finish and tier sizes, add extras with quantities. "
        "Read the total, deposit and balance in the tiles. Print the tab: page 2 is the extras table and the customer's order summary.", "num"),
    (3, "Order Log tab. Add one row per order with the total and the deposit as it arrives. The strip shows what is due in the "
        "next 7 days and what is still owed; pick Yes under Done when the cake goes out.", "num"),
])
r = sh_card(sh, r, "How to read the cells", [
    ((6.00, USD2), "Yellow cells with blue numbers are yours to type in. Each one shows a hint when you select it.", "chip-in"),
    ((EX["cake"], USD2), "Numbers on white are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((EX["total"], USD2),
     "Dark tiles are your answers. The quote total sits at the top of the Order Form and stays on screen as you scroll.", "chip-key"),
    (None, "Each tab is protected without a password, so you can still change anything. To edit a locked cell, use Review, "
           "Unprotect Sheet in Excel, or Data, Protect sheets and ranges in Google Sheets.", "note"),
])
S.page_break_before(sh, r)
ex_text = (f"Cake-Order-Form-EXAMPLE.xlsx holds a made-up home bakery (the names are placeholders). The open order is a three-tier "
           f"wedding cake, 10 in, 8 in and 6 in round, in fondant: {EX['tot_serv']} wedding servings at {money(EX['pps'])} a serving is "
           f"{money(EX['cake'])}; 12 sugar flowers, fresh flowers arranged and a box and board add {money(EX['extras'])}; delivery "
           f"18 miles one way is {money(EX['deliv'])}; the event is {EX['days']} days out, so no rush fee. Total {money(EX['total'])}, "
           f"deposit {money(EX['dep'])} to book, balance {money(EX['bal'])} on the event date. The Order Log holds {EX['log_n']} orders "
           f"as of {CHECKED}: {EX['due7']} due in the next 7 days, {money(EX['deposits'])} of deposits received and "
           f"{money(EX['bal_owed'])} still owed.")
r = sh_card(sh, r, "The example", [(None, ex_text, "para")])
r = sh_card(sh, r, "Which file to open", [
    (None, "Excel on a computer. Double-click Cake-Order-Form.xlsx. If Excel shows a yellow Protected View bar, click Enable Editing.", "para"),
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. No macros, no add-ons, no sign-up.", "para"),
    (None, "Mac, iPad or phone. Unzip on a computer first (phones often can't open a .zip), then upload the .xlsx to Google Drive "
           "and open it in the Google Sheets app, or open it in Excel for Mac or iPad.", "para"),
    (None, "See it filled in first. Open Cake-Order-Form-EXAMPLE.xlsx, then use the blank Cake-Order-Form.xlsx for your own orders.", "para"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "Good to know", [
    (None, "Printing the order form. On the Order Form tab choose File, Print. Page 1 is your working view, page 2 is the customer's "
           "extras table and order summary (every line reads the cells above; nothing to type there). To send it, print to PDF and attach page 2, or take a screenshot of the summary card.", "para"),
    (None, "One order at a time. The Order Form holds the order you are quoting now. When it is booked, add a row to the Order Log "
           "(customer, dates, cake, total, deposit), then type the next order over the form. Keep a PDF of each summary if you want a record.", "para"),
    (None, "Clearing the example. Select the yellow cells and press Delete. Formulas live only in the white cells, so every total "
           "keeps working. Or start from the blank file.", "para"),
    (None, "Your own sizes and extras. Add rows at the bottom of each Price List table, in the yellow cells. The Order Form's drop-downs "
           f"read all {N_SIZES} size rows and all {N_EXTRAS} extras rows.", "para"),
    (None, "Minimum cake price. A small cake prices up to your minimum when servings times the per-serving price comes out lower. "
           "The Order Form says when that happened.", "para"),
    (None, "Cups to millilitres. The Price List carries a conversion card for US measuring cups, tablespoons and teaspoons, with a "
           "cell for your own amount.", "para"),
    (None, "Any currency. The maths works in any currency. Select the money cells and pick your symbol under Format, Number.", "para"),
    (None, "Any language setting. The formulas use no text-format codes, so they work the same in Excel set to other languages "
           "and in Google Sheets.", "para"),
])
r = sh_card(sh, r, "Before you rely on a number", [
    (None, S.SHORT_NOTICE.format(date=CHECKED).replace("Terms of Use page", "Terms tab"), "note"),
    (None, "Selling food from home is regulated (cottage food laws, permits, labels, sales tax). This workbook prices and tracks orders; "
           "it does not cover those rules. Check your state and local requirements.", "note"),
])
SH_LAST = r - 1
D.paint_canvas(sh, SH_LAST, "Z")
S.finish_sheet(sh, PRODUCT, SH_LAST, span=("A", "G"), tab_color="teal",
               footer_notice="Estimates only. Not professional advice. See the Terms tab or LICENSE-AND-DISCLAIMER.txt.")

tm = wb.create_sheet("Terms")
S.set_widths(tm, SH_GRID)
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version {VERSION}. Read this before you rely on a number.", f"Version {VERSION}, {CHECKED}",
              span=("B", "F"), side_cols=2)
paras = open(os.path.join(HERE, "LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().strip().split("\n\n")[1:]
r = 6
r = sh_card(tm, r, "More tools from the shop", [
    (None, ("Craft Fair Profit Calculator: booth fee break-even for makers and bakers at markets", "https://www.etsy.com/listing/4586813952"),
     "link"),
    (None, ("Hourly Rate Quick Calculator: the hourly rate your take-home goal needs", "https://www.etsy.com/listing/4589695837"), "link"),
    (None, ("Everything in the shop: etsy.com/shop/ProofNotFluff", "https://www.etsy.com/shop/ProofNotFluff"), "link"),
])
r = sh_card(tm, r, "Terms of Use and disclaimer", [(None, p, "para") for p in paras])
r = sh_card(tm, r, "A small ask", [
    (None, "If this workbook saves you time, a short review on Etsy helps other bakers find it. Thank you.", "para"),
    (None, "If a file won't open or something looks wrong, message the shop on Etsy and it will be fixed.", "para"),
])
TM_LAST = r - 1
D.paint_canvas(tm, TM_LAST, "Z")
S.finish_sheet(tm, PRODUCT, TM_LAST, span=("A", "G"), tab_color="note")

wb.active = 0
problems = [p for p in S.audit(wb) if "input without validation" not in p]
if problems:
    print("AUDIT:", *problems[:20], sep="\n  ")
wb.save(OUT)
print("saved", OUT, wb.sheetnames)
print(json.dumps({"price_list": dict(bc=r_bc, fd=r_fd, min=r_min, dep=r_dep, rush_days=r_rdays, rush_pct=r_rpct, db=r_db, dm=r_dm, tax=r_tax,
                                     bakery=r_bak, terms=r_terms, cups=r_cups, sizes=(SZ_FIRST, SZ_LAST), extras=(EX_FIRST, EX_LAST)),
                  "order_form": dict(cust=r_cust, evt=r_evt, ord=r_ord, meth=r_meth, miles=r_miles, style=r_style, fin=r_fin, ovr=r_ovr,
                                     tiers=TIER_ROWS, serv=r_serv, pps=r_pps, cake=r_cake, ext=r_ext, deliv=r_del, rush=r_rush, sub=r_sub,
                                     tax=r_tax, tot=r_tot, dep=r_dep2, bal=r_bal, extras=(X_FIRST, X_LAST), summary=(S_TOP, Q.end)),
                  "order_log": dict(asof=r_asof, rows=(L_FIRST, L_LAST), n=len(LOG))}))
print("example:", json.dumps(EX))
