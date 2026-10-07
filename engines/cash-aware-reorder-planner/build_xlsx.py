#!/usr/bin/env python3
"""#6 Cash-Aware Reorder Planner, version 3 (dashboard design, Oct 7, 2026).

Same inputs, the same fictional sample shop (Maple & Moss Goods, 16 SKUs, 3 suppliers, $1,500 of
usable cash) and the same formulas as the live version 1 (Sep 29, 2026), rebuilt to
design/WORKBOOK_STANDARD.md section 0. tools/compare_xlsx.py with compare_map.json proves the
answers match.

Restructured for the dashboard: the old Setup and Dashboard tabs are one tab, 1 Your Shop (inputs on
the left, the inventory glance on the right, then suppliers, SKUs by status and where the cash is);
the purchase-order blocks moved from the Reorder Planner to their own tab, 4 Purchase Orders, two
per row. Every formula is the v1 formula with new cell addresses, except the fixes below.

Fixes in v3 (declared under "intended" in compare_map.json):
  - Priority score: a SKU with 0 days of stock left (sold out) scored 0 and ranked last, so 5 Cash
    Check funded it after everything else. Days of stock now count as at least half a day, so a
    sold-out SKU ranks by its profit per day. Identical for every SKU with half a day or more.
  - Blank as-of date: days since last sale showed about -46,000 and the stockout date showed a
    date in 1900. Both now stay blank until the as-of date is typed.
  - Purchase orders: a SKU to order with no supplier showed "0" as its supplier and sat on no
    purchase order with no warning. It now shows blank, and 4 Purchase Orders counts the lines with
    no listed supplier so none is missed.
  - Cash verdict and dead-stock recommendations are written in sentence case (v1 was all capitals).
  - Text: the dashboard's unsourced "small shops land at 4 to 20 turns" benchmark is gone; the
    where-to-find-your-sales note now cites Etsy's Help Center (Shop Manager, Stats, checked Oct 7,
    2026) and says Etsy counts orders, not units; the Amazon and eBay menu paths, which could not
    be checked at the source, are replaced by a general line; "take the write-off" (a tax claim)
    is gone. Added: Start Here, full Terms of Use tab, the short notice and the money tier clause.

Usage: python3 engines/cash-aware-reorder-planner/build_xlsx.py out.xlsx
"""
import os
import re
import sys
import datetime as dt

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
import wb_style as S  # noqa: E402
import pnf_dash as D  # noqa: E402
from openpyxl.cell.rich_text import CellRichText, TextBlock  # noqa: E402
from openpyxl.cell.text import InlineFont  # noqa: E402
from openpyxl.formatting.rule import FormulaRule  # noqa: E402
from openpyxl.styles import Alignment, Border, Font, PatternFill  # noqa: E402
from openpyxl.worksheet.cell_range import MultiCellRange  # noqa: E402

PRODUCT = "Cash-Aware Reorder Planner"
VERSION = "3"
CHECKED = "Oct 7, 2026"
AS_OF = f"Figures checked {CHECKED}"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "Cash-Aware-Reorder-Planner.xlsx"
USD0, USD2, PCT, INT, DATE = (S.FMT[k] for k in ("usd0", "usd2", "pct", "int", "date"))
USD2Z = '"$"#,##0.00;-"$"#,##0.00;""'      # hides a zero (rows with nothing to show)
NUM1 = "#,##0.0"
NUM2 = "#,##0.00"
SALES = "#,##0.0#"
TREND = '+0%;-0%;0%'
SHOP_URL = "https://proofnotfluff.etsy.com"
N = 30          # SKU rows
N_SUP = 6       # supplier slots
N_LINES = 10    # lines per purchase order

# ---------------------------------------------------------------- the v1 sample shop (fictional, unchanged)
EX = dict(shop="Maple & Moss Goods", as_of=dt.datetime(2026, 9, 28), cash=1800, bills=300, safety=0.20, cycle=14,
          trend=0.0, dead=90, over=120, small=30, lead=14)
SUPPLIERS = ["Northwind Ceramics", "Fieldstone Textiles", "Harbor Wholesale", None, None, None]
SKUS = [  # SKU, product, supplier, unit cost, sell price, fees, lead, on hand, on order, daily sales, last sale
    ("SKU-001", "Speckled Ceramic Mug 12 oz", 0, 6.5, 24, 3.1, 21, 48, 0, 1.4, (2026, 9, 27)),
    ("SKU-002", "Stoneware Bud Vase", 0, 7.2, 22, 2.9, 21, 30, 0, 1.8, (2026, 9, 28)),
    ("SKU-003", "Ceramic Ring Dish", 0, 3.1, 14, 1.95, 21, 30, 0, 0.6, (2026, 9, 25)),
    ("SKU-004", "Large Serving Bowl", 0, 16, 58, 6.9, 28, 12, 0, 0.8, (2026, 9, 26)),
    ("SKU-005", "Espresso Cup Set (2)", 0, 17, 32, 4, 21, 6, 0, 0, (2026, 5, 20)),
    ("SKU-006", "Linen Tea Towel", 1, 4.8, 18, 2.4, 10, 60, 0, 2.2, (2026, 9, 28)),
    ("SKU-007", "Canvas Tote Bag", 1, 9.5, 28, 3.6, 10, 24, 0, 3.2, (2026, 9, 28)),
    ("SKU-008", "Embroidered Patch Set", 1, 3.2, 12, 1.7, 10, 28, 0, 2.5, (2026, 9, 27)),
    ("SKU-009", "Quilted Pot Holder (pair)", 1, 5.1, 20, 2.6, 10, 130, 0, 0.9, (2026, 9, 24)),
    ("SKU-010", "Waxed Canvas Apron", 1, 14, 38, 4.7, 14, 26, 0, 1.8, (2026, 9, 27)),
    ("SKU-011", "Soy Candle 8 oz", 2, 5.6, 22, 2.9, 7, 24, 48, 3.5, (2026, 9, 28)),
    ("SKU-012", "Goat Milk Soap Bar", 2, 2.6, 9, 1.35, 7, 46, 0, 6, (2026, 9, 28)),
    ("SKU-013", "Greeting Card 6-Pack", 2, 3.4, 16, 2.15, 7, 28, 0, 3, (2026, 9, 27)),
    ("SKU-014", "Beeswax Wrap Set", 2, 8.4, 24, 3.1, 7, 24, 0, 3, (2026, 9, 28)),
    ("SKU-015", "Holiday Ornament 2025", 2, 4.5, 15, 2, 14, 5, 0, 0, (2026, 1, 4)),
    ("SKU-016", "Cotton Napkin Set (4)", 1, 6.2, 26, 3.3, 10, 40, 0, 1.1, (2026, 9, 26)),
]
STATUSES = ["OK", "OVERSTOCK", "REORDER", "STOCKOUT RISK", "DEAD", "NO SALES"]
STATUS_LOOK = {  # word: (font color, tint)
    "OK": ("teal", "teal_tint"), "OVERSTOCK": ("blue", "E3ECF7"), "REORDER": ("A87C1F", "FFF6D6"),
    "STOCKOUT RISK": ("accent", "accent_tint"), "DEAD": ("ink", "E6E3DD"), "NO SALES": ("muted", "F3F1EC"),
}


def pad(vals, n):
    return list(vals) + [None] * (n - len(vals))


wb = S.new_workbook(PRODUCT, version=VERSION)
GRID = {"A": 3, "B": 2, "C": 31, "D": 14, "E": 2, "F": 3, "G": 2, "H": 24, "I": 15, "J": 14, "K": 2, "L": 3}


def notes_card(ws, top, notes, span=("C", "J"), frame_span=("B", "K"), title="Notes and sources"):
    r = top
    D.h(ws, r, 12); r += 1
    t = ws[f"{span[0]}{r}"]; t.value = title; t.font = D.f(12, True)
    ws.merge_cells(f"{span[0]}{r}:{span[1]}{r}"); D.h(ws, r, 24); r += 1
    D.h(ws, r, 6); r += 1
    width = sum(S.width_of(ws, k) for k in D.cols(*span))
    for head, body in notes:
        cell = ws[f"{span[0]}{r}"]
        cell.value = CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=9, b=True, color=D.T["ink"]), head + ". "),
                                  TextBlock(InlineFont(rFont=D.FONT, sz=9, color=D.T["ink2"]), body))
        cell.alignment = Alignment(vertical="top", wrap_text=True)
        ws.merge_cells(f"{span[0]}{r}:{span[1]}{r}")
        D.h(ws, r, S.text_height(head + ". " + body, width, 9) + 4); r += 1
    D.h(ws, r, 12)
    D.frame(ws, top, r, *frame_span)
    return r


def total_row(ws, row, span, label_col, label, cells):
    """Turn the last body row of a table card into its total row: ink rule on top, bold, locked, no inputs."""
    for k in span:
        c = ws[f"{k}{row}"]
        c.value = None
        c.fill = D.fill("total_tint")
        c.font = D.f(10, True)
        c.protection = c.protection.copy(locked=True)
        c.border = Border(top=D.side("ink"), bottom=D.side("hair"))
        c.alignment = Alignment(horizontal="right", vertical="center")
    lab = ws[f"{label_col}{row}"]; lab.value = label; lab.alignment = Alignment(horizontal="left", vertical="center")
    for col, (formula, fmt) in cells.items():
        c = ws[f"{col}{row}"]; c.value = formula; c.number_format = fmt


def trim_validations(ws, last_body):
    for dv in ws.data_validations.dataValidation:
        new = []
        for rng in str(dv.sqref).split():
            a, _, b = rng.partition(":")
            if b:
                col = "".join(ch for ch in b if ch.isalpha())
                row = int("".join(ch for ch in b if ch.isdigit()))
                if row > last_body:
                    b = f"{col}{last_body}"
                new.append(f"{a}:{b}")
            else:
                new.append(rng)
        dv.sqref = MultiCellRange(" ".join(new))


def finish(ws, last, span, freeze, tab_color, print_last=None):
    for rr in range(1, last + 1):
        if ws.row_dimensions[rr].height is None:
            D.h(ws, rr, D.GRID_ROW)
    D.paint_canvas(ws, last, "Z")
    S.finish_sheet(ws, PRODUCT, last, span=span, freeze=freeze, tab_color=tab_color)
    if print_last:
        ws.print_area = f"{span[0]}1:{span[1]}{print_last}"


def status_colors(ws, rng, words=STATUSES):
    first = rng.split(":")[0]
    col = "".join(ch for ch in first if ch.isalpha()); row = "".join(ch for ch in first if ch.isdigit())
    for w in words:
        color, tint = STATUS_LOOK[w]
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'${col}{row}="{w}"'], stopIfTrue=True,
                                      font=Font(color=D.T.get(color, color), bold=True),
                                      fill=PatternFill("solid", bgColor=D.T.get(tint, tint))))


def word_colors(ws, rng, pairs):
    first = rng.split(":")[0]
    col = "".join(ch for ch in first if ch.isalpha()); row = "".join(ch for ch in first if ch.isdigit())
    for w, (color, tint) in pairs.items():
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'${col}{row}="{w}"'], stopIfTrue=True,
                                      font=Font(color=D.T.get(color, color), bold=True),
                                      fill=PatternFill("solid", bgColor=D.T.get(tint, tint)) if tint else None))


def set_error(ws, cell, text):
    for dv in ws.data_validations.dataValidation:
        if cell in str(dv.sqref).split():
            dv.error = text
            return
    raise KeyError(cell)


def left_align(ws, col, first, last, indent=1):
    for r in range(first, last + 1):
        ws[f"{col}{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=indent)


# =====================================================================  1 Your Shop: the inputs (built first, every tab reads them)
ys = wb.create_sheet("1 Your Shop")
S.set_widths(ys, GRID)
D.page_header(ys, "Your Shop", "Your cash, your reorder rules and your suppliers. Every other tab reads from here.", AS_OF)
TOP = 11
A = D.Card(ys, TOP, "B", "C", "D", "E", wb=wb)
A.title("Your shop and your rules", "Type over the yellow cells. Every tab updates.")
A.eyebrow("THE SHOP")
SN = A.input("Shop name", EX["shop"], "@", name="ShopName", validation=("textLength", 0, 40),
             prompt="Shows on the purchase orders. Up to 40 characters.", prompt_title="Shop name", allow_blank=True)
ys[f"D{SN}"].alignment = Alignment(horizontal="left", vertical="center", shrink_to_fit=True)
ys[f"D{SN}"].font = D.f(9, True, "input_text")
AD = A.input("As-of date (today)", EX["as_of"], DATE, name="AsOfDate", validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"),
             prompt="The day you sit down to reorder, for example 9/28/2026. Every days figure counts from it. A typed date, "
                    "not TODAY(), so numbers don't drift while you work.", prompt_title="As-of date")
A.eyebrow("YOUR CASH")
CA = A.input("Cash available for stock", EX["cash"], USD0, name="CashAvailable", validation=("decimal", 0, None),
             prompt="What you could send to suppliers this week, in dollars: not your bank balance, the part you'd spend "
                    "on stock. Example: 1800.", prompt_title="Cash available for stock")
BD = A.input("Bills due before stock lands", EX["bills"], USD0, name="BillsDue", validation=("decimal", 0, None),
             prompt="Rent, software, ads, a loan payment: anything leaving the same account before the order arrives, "
                    "in dollars. Example: 300.", prompt_title="Bills due before stock lands")
UC = A.calc("Usable cash for this order", f"=MAX(0,D{CA}-D{BD})", USD2, total=True, tint="total_tint")
A.eyebrow("YOUR REORDER RULES")
SS = A.input("Safety stock, % of lead-time sales", EX["safety"], PCT, name="SafetyStock", validation=("decimal", 0, 2),
             prompt="Cushion on top of what you expect to sell while an order is in transit. Type a percent, 0% to 200%, "
                    "for example 20%. Raise it for suppliers that run late.", prompt_title="Safety stock")
OC = A.input("Days between your orders", EX["cycle"], INT, name="OrderCycleDays",
             validation=("whole", 1, 365),
             prompt="Whole days, 1 to 365. Order weekly: 7. Every two weeks: 14. Monthly: 30. Longer cycles mean bigger orders.",
             prompt_title="Days between your orders")
TR = A.input("Sales trend for the weeks ahead", EX["trend"], TREND, name="SalesTrend", validation=("decimal", -0.9, 5),
             prompt="Scales every SKU's daily sales. Type a percent from -90% to 500%: +30% for a busier month ahead, "
                    "-20% for a slow one, 0% to trust the last 30 days.", prompt_title="Sales trend")
DDY = A.input("Dead stock: days with no sale", EX["dead"], INT, name="DeadStockDays", validation=("whole", 1, 365),
              prompt="Whole days, 1 to 365. A SKU with no sales that last sold this many days ago or more is DEAD. Example: 90.",
              prompt_title="Dead stock: days with no sale")
OD = A.input("Overstock: days of stock on hand", EX["over"], INT, name="OverstockDays", validation=("whole", 1, 365),
             prompt="Whole days, 1 to 365. A SKU with this many days of stock or more is OVERSTOCK: stop reordering it. "
                    "Example: 120.", prompt_title="Overstock: days of stock")
SL = A.input("Small lot: donate under", EX["small"], USD0, name="SmallLot", validation=("decimal", 0, None),
             prompt="In dollars at cost. Dead stock worth this or less isn't worth a clearance push; 6 Dead Stock says "
                    "donate or write it off. Example: 30.", prompt_title="Small lot: donate under")
DL = A.input("Default lead time, days", EX["lead"], INT, name="DefaultLeadTime", validation=("whole", 1, 365),
             prompt="Whole days, 1 to 365. Used for any SKU whose lead time is blank on 2 SKU List. Example: 14.",
             prompt_title="Default lead time")
A.close()
set_error(ys, f"D{SN}", "Type up to 40 characters.")
set_error(ys, f"D{AD}", "Enter a date from 2000 to 2100, for example 9/28/2026.")
set_error(ys, f"D{CA}", "Enter 0 or more dollars, for example 1800.")
set_error(ys, f"D{BD}", "Enter 0 or more dollars, for example 300.")
set_error(ys, f"D{SS}", "Enter a percent from 0% to 200%, for example 20%.")
set_error(ys, f"D{OC}", "Enter whole days from 1 to 365, for example 14.")
set_error(ys, f"D{TR}", "Enter a percent from -90% to 500%, for example 30%.")
set_error(ys, f"D{DDY}", "Enter whole days from 1 to 365, for example 90.")
set_error(ys, f"D{OD}", "Enter whole days from 1 to 365, for example 120.")
set_error(ys, f"D{SL}", "Enter 0 or more dollars, for example 30.")
set_error(ys, f"D{DL}", "Enter whole days from 1 to 365, for example 14.")
P1 = "'1 Your Shop'!"
ADr, UCr, SSr, OCr, TRr, DDr, ODr, SLr, DLr, SNr = (f"{P1}$D${x}" for x in (AD, UC, SS, OC, TR, DDY, OD, SL, DL, SN))

# Suppliers card, left column under the rules
SUP = D.Card(ys, A.end + 2, "B", "C", "D", "E", wb=wb)
SUP.title("Your suppliers", "Up to 6. They feed the pick list on 2 SKU List.")
SUP_ROWS = []
for i in range(N_SUP):
    rr = SUP.input(f"Supplier {i + 1}", SUPPLIERS[i], "@", validation=("textLength", 0, 40),
                   prompt="A supplier name, up to 40 characters. It appears in the Supplier pick list and heads its own "
                          "purchase order on 4 Purchase Orders.", prompt_title=f"Supplier {i + 1}", allow_blank=True)
    ys[f"D{rr}"].alignment = Alignment(horizontal="left", vertical="center", shrink_to_fit=True)
    ys[f"D{rr}"].font = D.f(9, True, "input_text")
    set_error(ys, f"D{rr}", "Type up to 40 characters.")
    SUP_ROWS.append(rr)
SUP.text("Renamed one? Pick it again on 2 SKU List.")
SUPr = [f"{P1}$D${x}" for x in SUP_ROWS]
SUP_LIST = f"{P1}$D${SUP_ROWS[0]}:$D${SUP_ROWS[-1]}"

# =====================================================================  2 SKU List
sk = wb.create_sheet("2 SKU List")
SK_W = {"A": 3, "B": 2, "C": 10, "D": 27, "E": 20, "F": 9, "G": 9, "H": 10, "I": 8, "J": 8, "K": 8, "L": 10, "M": 12,
        "N": 9, "O": 9, "P": 9, "Q": 10, "R": 10, "S": 9, "T": 18, "U": 10, "V": 12, "W": 9, "X": 12, "Y": 12, "Z": 2, "AA": 3}
S.set_widths(sk, SK_W)
D.page_header(sk, "SKU List", "One row per SKU. Type the yellow columns; the rest calculates and Status says what to do.",
              AS_OF, span=("B", "Z"), side_cols=4)
SK_TOP = 11
sk_first = SK_TOP + 5
sk_last = sk_first + N - 1
sk_tot = sk_last + 1


def skf(kind):
    def fn(r):
        LT = f'IF(I{r}="",{DLr},I{r})'
        return {
            "adj": f'=IF(C{r}="","",L{r}*(1+{TRr}))',
            "margin": f'=IF(C{r}="","",G{r}-F{r}-H{r})',
            "days": f'=IF(C{r}="","",IF(N{r}>0,J{r}/N{r},"no sales"))',
            "rop": f'=IF(C{r}="","",IF(N{r}>0,N{r}*{LT}*(1+{SSr}),0))',
            "out": f'=IF(C{r}="","",IF(N{r}>0,N{r}*({LT}+{OCr})*(1+{SSr}),0))',
            "since": f'=IF(C{r}="","",IF(OR(M{r}="",{ADr}=""),"",{ADr}-M{r}))',
            "status": (f'=IF(C{r}="","",IF(N{r}=0,IF(AND(S{r}<>"",S{r}>={DDr}),"DEAD","NO SALES"),'
                       f'IF(AND(P{r}<{LT},K{r}=0),"STOCKOUT RISK",IF(J{r}+K{r}<=Q{r},"REORDER",'
                       f'IF(P{r}>={ODr},"OVERSTOCK","OK")))))'),
            "value": f'=IF(C{r}="","",J{r}*F{r})',
            "stockout": f'=IF(C{r}="","",IF(AND(N{r}>0,{ADr}<>""),{ADr}+J{r}/N{r},""))',
            "until": f'=IF(C{r}="","",IF(N{r}>0,(J{r}+K{r}-Q{r})/N{r},""))',
            "due30": (f'=IF(C{r}="","",IF(OR(T{r}="REORDER",T{r}="STOCKOUT RISK"),MAX(0,ROUNDUP(R{r}-J{r}-K{r},0))*F{r},'
                      f'IF(AND(ISNUMBER(W{r}),W{r}<=30),ROUNDUP(R{r}-Q{r},0)*F{r},0)))'),
            "cogs": f'=IF(C{r}="","",N{r}*F{r}*365)',
        }[kind]
    return fn


col_vals = list(zip(*[(s[0], s[1], SUPPLIERS[s[2]], s[3], s[4], s[5], s[6], s[7], s[8], s[9], dt.datetime(*s[10])) for s in SKUS]))
cols_sk = [
    dict(col="C", head="SKU", kind="input", values=pad(col_vals[0], N + 1), validation=("textLength", 0, 20),
         prompt="Your SKU code, up to 20 characters. A row only calculates once it has a SKU.", error="Up to 20 characters."),
    dict(col="D", head="Product", kind="input", values=pad(col_vals[1], N + 1), validation=("textLength", 0, 60),
         prompt="The product name, up to 60 characters.", error="Up to 60 characters."),
    dict(col="E", head="Supplier", kind="input", values=pad(col_vals[2], N + 1), validation=("list_range", SUP_LIST),
         prompt="Pick a supplier from your list on 1 Your Shop.", error="Pick a supplier from the list. Add new ones on 1 Your Shop."),
    dict(col="F", head="Unit cost", kind="input", fmt=USD2, align="right", values=pad(col_vals[3], N + 1),
         validation=("decimal", 0, None), prompt="What you pay the supplier per unit, in dollars. Example: 6.50.",
         error="Enter 0 or more, for example 6.50."),
    dict(col="G", head="Sell price", kind="input", fmt=USD2, align="right", values=pad(col_vals[4], N + 1),
         validation=("decimal", 0, None), prompt="Your selling price per unit, in dollars. Example: 24.",
         error="Enter 0 or more, for example 24."),
    dict(col="H", head="Fees and costs per unit", kind="input", fmt=USD2, align="right", values=pad(col_vals[5], N + 1),
         validation=("decimal", 0, None), prompt="Marketplace and payment fees, packaging: anything else that comes out of "
                                                 "each sale, in dollars. Example: 3.10.", error="Enter 0 or more, for example 3.10."),
    dict(col="I", head="Lead time, days", kind="input", fmt=INT, align="right", values=pad(col_vals[6], N + 1),
         validation=("whole", 0, 365), prompt="Whole days from placing an order to having stock to sell, 0 to 365. Blank uses "
                                              "the default on 1 Your Shop.", error="Enter whole days from 0 to 365, or leave it blank."),
    dict(col="J", head="On hand", kind="input", fmt=INT, align="right", values=pad(col_vals[7], N + 1),
         validation=("whole", 0, None), prompt="Units you have now, whole number.", error="Enter a whole number of 0 or more."),
    dict(col="K", head="On order", kind="input", fmt=INT, align="right", values=pad(col_vals[8], N + 1),
         validation=("whole", 0, None), prompt="Units ordered and not yet arrived, whole number. 0 if none.",
         error="Enter a whole number of 0 or more."),
    dict(col="L", head="Daily sales, last 30 days", kind="input", fmt=SALES, align="right", values=pad(col_vals[9], N + 1),
         validation=("decimal", 0, None), prompt="Units sold in the last 30 days divided by 30. Example: 42 sold is 1.4. "
                                                 "See Notes and sources for where Etsy shows it.", error="Enter 0 or more, for example 1.4."),
    dict(col="M", head="Last sale date", kind="input", fmt=DATE, align="right", values=pad(col_vals[10], N + 1),
         validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), prompt="The last date this SKU sold, for example 9/27/2026.",
         error="Enter a date from 2000 on, for example 9/27/2026."),
    dict(col="N", head="Daily sales, with trend", kind="calc", fmt=NUM2, align="right", formula=skf("adj")),
    dict(col="O", head="Margin per unit", kind="calc", fmt=USD2, align="right", formula=skf("margin")),
    dict(col="P", head="Days of stock", kind="calc", fmt=NUM1, align="right", formula=skf("days")),
    dict(col="Q", head="Reorder point, units", kind="calc", fmt=NUM1, align="right", formula=skf("rop")),
    dict(col="R", head="Order up to, units", kind="calc", fmt=NUM1, align="right", formula=skf("out")),
    dict(col="S", head="Days since last sale", kind="calc", fmt=INT, align="right", formula=skf("since")),
    dict(col="T", head="Status", kind="calc", align="left", bold=True, formula=skf("status")),
    dict(col="U", head="Stock value at cost", kind="calc", fmt=USD2, align="right", formula=skf("value")),
    dict(col="V", head="Runs out on", kind="calc", fmt=DATE, align="right", formula=skf("stockout")),
    dict(col="W", head="Days until reorder", kind="calc", fmt=NUM1, align="right", formula=skf("until")),
    dict(col="X", head="Order cost due in 30 days", kind="calc", fmt=USD2, align="right", formula=skf("due30")),
    dict(col="Y", head="Cost of goods a year at this pace", kind="calc", fmt=USD0, align="right", formula=skf("cogs")),
]
f1, l1, sk_end = D.table_card(sk, SK_TOP, "B", "Z", cols_sk, N + 1, title="Your SKUs",
                              sub="Yellow columns are yours. Status: STOCKOUT RISK and REORDER need an order now; "
                                  "OVERSTOCK means stop reordering; DEAD goes to 6 Dead Stock.")
assert (f1, l1) == (sk_first, sk_tot), (f1, l1)
D.h(sk, sk_first - 1, 44)
total_row(sk, sk_tot, D.cols("C", "Y"), "C", "All SKUs", {
    "U": (f"=SUM(U{sk_first}:U{sk_last})", USD2),
    "X": (f"=SUM(X{sk_first}:X{sk_last})", USD2),
    "Y": (f"=SUM(Y{sk_first}:Y{sk_last})", USD0),
})
trim_validations(sk, sk_last)
for c in "CDE":
    left_align(sk, c, sk_first, sk_last)
left_align(sk, "T", sk_first, sk_last)
status_colors(sk, f"T{sk_first}:T{sk_last}")
sk.conditional_formatting.add(f"P{sk_first}:P{sk_last}", FormulaRule(
    formula=[f'AND(ISNUMBER(P{sk_first}),P{sk_first}<IF(I{sk_first}="",{DLr},I{sk_first}))'],
    font=Font(color=D.T["accent"], bold=True)))
TS = f"T{sk_first}:T{sk_last}"
D.h(sk, 6, 10)
D.stat_strip(sk, 7, [
    ("C:D", "SKUs listed", f'=COUNTIF(C{sk_first}:C{sk_last},"?*")', INT),
    ("E:H", "Need an order now", f'=COUNTIF({TS},"REORDER")+COUNTIF({TS},"STOCKOUT RISK")', INT),
    ("I:M", "Overstock or dead", f'=COUNTIF({TS},"OVERSTOCK")+COUNTIF({TS},"DEAD")', INT),
    ("N:R", "Stock value at cost", f"=U{sk_tot}", USD2),
    ("S:V", "Order cost due in 30 days", f"=X{sk_tot}", USD2),
])
D.status_rule(sk, "E8", "$E$8>0", fill_tint=False)
D.h(sk, 9, 10)
D.frame(sk, 6, 9, "B", "Z")
D.h(sk, 10, 14)
SK_NOTES = [
    ("How Status is decided, in this order", "DEAD: no daily sales, and the last sale was at least the dead-stock days on 1 Your "
     "Shop before the as-of date. NO SALES: no daily sales and not dead yet (or no last sale date). STOCKOUT RISK: days of stock "
     "are fewer than the lead time and nothing is on order, so a new order can't land in time. REORDER: on hand plus on order is "
     "at or below the reorder point. OVERSTOCK: days of stock at or above the overstock days. Otherwise OK. Days of stock turn "
     "orange when they are shorter than the lead time."),
    ("Where to find daily sales", f"On Etsy: Shop Manager, then Stats; each listing shows its orders for the period you pick "
     f"(Etsy Help Center, How to Use Etsy Stats for Your Shop, checked {CHECKED}). Etsy counts orders, and an order can hold "
     "more than one unit, so check quantities in your Orders list for your best sellers. On other platforms, use the sales "
     "report that lists units sold per item. Units in the last 30 days divided by 30 is the daily figure."),
    ("The maths", "Reorder point = daily sales x lead time x (1 + safety stock). Order up to = daily sales x (lead time + days "
     "between your orders) x (1 + safety stock). Runs out on = the as-of date plus days of stock. Days until reorder = (on hand "
     "+ on order - reorder point) / daily sales; below 0 means the reorder point is already behind you."),
    ("Order cost due in 30 days", "For SKUs that need an order now, the cost of topping them up to the order-up-to level. For "
     "other SKUs that will reach their reorder point within 30 days, the cost of one normal order (order up to minus reorder "
     "point). A cash forecast for the month, not an invoice."),
    ("More than 30 SKUs", "Unprotect the tab (Review, Unprotect Sheet in Excel), copy the last SKU row with its formulas and "
     "insert it above the total row, then do the same on 3 Reorder Plan, 5 Cash Check and 6 Dead Stock. Or keep your top 30 "
     "sellers here."),
]
sk_n_end = notes_card(sk, sk_end + 2, SK_NOTES, span=("C", "Y"), frame_span=("B", "Z"))
S.page_break_before(sk, sk_end + 2)
finish(sk, sk_n_end + 1, ("A", "AA"), f"A{sk_first}", "accent")
sk.page_setup.orientation = "landscape"
sk.page_setup.fitToHeight = 0
SK = "'2 SKU List'!"


def skr(col):
    return f"{SK}${col}${sk_first}:${col}${sk_last}"


# =====================================================================  3 Reorder Plan
rp = wb.create_sheet("3 Reorder Plan")
S.set_widths(rp, {"A": 3, "B": 2, "C": 10, "D": 25, "E": 20, "F": 18, "G": 8, "H": 8, "I": 9, "J": 9, "K": 11, "L": 9,
                  "M": 11, "N": 9, "O": 9, "P": 9, "Q": 7, "R": 9, "S": 21, "T": 2, "U": 3})
D.page_header(rp, "Reorder Plan", "Nothing to type. Every SKU that needs an order gets a quantity, a cost and a priority.",
              AS_OF, span=("B", "T"), side_cols=4)
RP_TOP = 11
rp_first = RP_TOP + 5
rp_last = rp_first + N - 1
rp_tot = rp_last + 1


def rpf(kind):
    def fn(r):
        i = r - rp_first + sk_first
        A_ = f"{SK}C{i}"
        blank = f'IF({A_}="",""'
        return {
            "sku": f'={blank},{SK}C{i})',
            "prod": f'={blank},{SK}D{i})',
            "sup": f'={blank},IF({SK}E{i}="","",{SK}E{i}))',
            "status": f'={blank},{SK}T{i})',
            "onhand": f'={blank},{SK}J{i})',
            "onorder": f'={blank},{SK}K{i})',
            "rop": f'={blank},{SK}Q{i})',
            "out": f'={blank},{SK}R{i})',
            "qty": f'={blank},IF(OR(F{r}="REORDER",F{r}="STOCKOUT RISK"),MAX(0,ROUNDUP(J{r}-G{r}-H{r},0)),0))',
            "cost": f'={blank},{SK}F{i})',
            "ocost": f'={blank},K{r}*L{r})',
            "days": f'={blank},{SK}P{i})',
            "ppd": f'={blank},{SK}O{i}*{SK}N{i})',
            "prio": f'=IF({A_}="",0,IF(AND(K{r}>0,ISNUMBER(N{r})),O{r}/MAX(N{r},0.5),0))',
            "rank": f'={blank},IF(K{r}>0,RANK(P{r},$P${rp_first}:$P${rp_last},0)+COUNTIF($P${rp_first}:P{r},P{r})-1,""))',
            "cover": f'={blank},IF(K{r}>0,MAX(0,ROUNDUP(I{r}-G{r}-H{r},0)),0))',
            "key": f'={blank},IF(K{r}>0,E{r}&"|"&COUNTIFS($E${rp_first}:E{r},E{r},$K${rp_first}:K{r},">0"),""))',
        }[kind]
    return fn


cols_rp = [
    dict(col="C", head="SKU", kind="calc", formula=rpf("sku")),
    dict(col="D", head="Product", kind="calc", formula=rpf("prod")),
    dict(col="E", head="Supplier", kind="calc", formula=rpf("sup")),
    dict(col="F", head="Status", kind="calc", bold=True, formula=rpf("status")),
    dict(col="G", head="On hand", kind="calc", fmt=INT, align="right", formula=rpf("onhand")),
    dict(col="H", head="On order", kind="calc", fmt=INT, align="right", formula=rpf("onorder")),
    dict(col="I", head="Reorder point", kind="calc", fmt=NUM1, align="right", formula=rpf("rop")),
    dict(col="J", head="Order up to", kind="calc", fmt=NUM1, align="right", formula=rpf("out")),
    dict(col="K", head="Qty to order", kind="calc", fmt="#,##0;-#,##0;\"\"", align="right", bold=True, formula=rpf("qty")),
    dict(col="L", head="Unit cost", kind="calc", fmt=USD2, align="right", formula=rpf("cost")),
    dict(col="M", head="Order cost", kind="calc", fmt=USD2Z, align="right", bold=True, formula=rpf("ocost")),
    dict(col="N", head="Days of stock", kind="calc", fmt=NUM1, align="right", formula=rpf("days")),
    dict(col="O", head="Profit per day", kind="calc", fmt=USD2, align="right", formula=rpf("ppd")),
    dict(col="P", head="Priority score", kind="calc", fmt='#,##0.00;-#,##0.00;""', align="right", formula=rpf("prio")),
    dict(col="Q", head="Rank", kind="calc", fmt=INT, align="right", formula=rpf("rank")),
    dict(col="R", head="Cover qty", kind="calc", fmt="#,##0;-#,##0;\"\"", align="right", formula=rpf("cover")),
    dict(col="S", head="Supplier line (helper)", kind="calc", muted=True, formula=rpf("key")),
]
f1, l1, rp_end = D.table_card(rp, RP_TOP, "B", "T", cols_rp, N + 1, title="What to order", row_height=19,
                              sub="Qty to order tops a SKU up to its order-up-to level. Cover qty only gets it back to its "
                                  "reorder point; 5 Cash Check funds that first when cash is short.")
assert (f1, l1) == (rp_first, rp_tot), (f1, l1)
D.h(rp, rp_first - 1, 44)
for r in range(rp_first, rp_last + 1):
    rp[f"S{r}"].font = D.f(9, False, "muted")
total_row(rp, rp_tot, D.cols("C", "S"), "C", "All orders", {
    "K": (f"=SUM(K{rp_first}:K{rp_last})", INT),
    "M": (f"=SUM(M{rp_first}:M{rp_last})", USD2),
})
for c in "CDEFS":
    left_align(rp, c, rp_first, rp_last, indent=1 if c != "S" else 1)
status_colors(rp, f"F{rp_first}:F{rp_last}")
rp.conditional_formatting.add(f"K{rp_first}:K{rp_last}", FormulaRule(formula=[f"AND(ISNUMBER(K{rp_first}),K{rp_first}>0)"],
                              font=Font(color=D.T["accent"], bold=True), fill=PatternFill("solid", bgColor=D.T["accent_tint"])))
RP_TOTAL = f"M{rp_tot}"
D.h(rp, 6, 10)
D.stat_strip(rp, 7, [
    ("C:D", "Total recommended order", f"=SUM(M{rp_first}:M{rp_last})", USD2),
    ("E:H", "SKUs to order", f'=COUNTIF(K{rp_first}:K{rp_last},">0")', INT),
    ("I:M", "Usable cash", f"={UCr}", USD2),
    ("N:S", "Affordable?", f'=IF(C8=0,"Nothing to order",IF(C8<=I8,"YES","NO: see 5 Cash Check"))', "@"),
])
word_colors(rp, "N8", {"YES": ("teal", None), "NO: see 5 Cash Check": ("accent", None)})
D.h(rp, 9, 10)
D.frame(rp, 6, 9, "B", "T")
D.h(rp, 10, 14)
RP_NOTES = [
    ("Qty to order", "Order up to minus on hand minus on order, rounded up to a whole unit, for SKUs marked REORDER or "
     "STOCKOUT RISK. Check your supplier's minimum order and price breaks before you send it, and round up when a minimum is close."),
    ("Priority", "Profit per day (margin per unit x daily sales) divided by days of stock left, so what earns most and runs out "
     "first ranks highest. Days of stock count as at least half a day, so a sold-out SKU still ranks by what it earns."),
    ("Supplier line", "The helper column numbers each supplier's lines so 4 Purchase Orders can list them. Leave it as is."),
]
rp_n_end = notes_card(rp, rp_end + 2, RP_NOTES, span=("C", "S"), frame_span=("B", "T"))
S.page_break_before(rp, rp_end + 2)
finish(rp, rp_n_end + 1, ("A", "U"), f"A{rp_first}", "gold")
rp.page_setup.orientation = "landscape"
RP = "'3 Reorder Plan'!"


def rpr(col):
    return f"{RP}${col}${rp_first}:${col}${rp_last}"


# =====================================================================  4 Purchase Orders
po = wb.create_sheet("4 Purchase Orders")
S.set_widths(po, {"A": 3, "B": 2, "C": 10, "D": 27, "E": 7, "F": 10, "G": 11, "H": 2, "I": 3, "J": 2, "K": 10, "L": 27,
                  "M": 7, "N": 10, "O": 11, "P": 2, "Q": 3})
D.page_header(po, "Purchase Orders", "One block per supplier, filled from 3 Reorder Plan. Send each block as its own order.",
              AS_OF, span=("B", "P"), side_cols=4)
po["B2"].value = f'=IF({SNr}="","Purchase Orders","Purchase Orders: "&{SNr})'
PO_TOP = 11
PO_ROWS = 1 + 1 + 1 + 1 + 1 + N_LINES + 1 + 1   # pad, title, sub, gap, head, lines, total, pad
PO_TOTALS, PO_FIRST_LINES = [], []


def po_block(slot, top, c0):
    cs = D.cols(c0, chr(ord(c0) + 4))           # SKU, Product, Qty, Unit cost, Cost
    left, right = chr(ord(c0) - 1), chr(ord(c0) + 5)
    sup = SUPr[slot]
    r = top
    D.h(po, r, 12); r += 1
    t = po[f"{cs[0]}{r}"]
    t.value = f'=IF({sup}="","Supplier {slot + 1}: not set",{sup})'
    t.font = D.f(12, True); t.alignment = Alignment(vertical="center")
    po.merge_cells(f"{cs[0]}{r}:{cs[-1]}{r}"); D.h(po, r, 24); r += 1
    s = po[f"{cs[0]}{r}"]
    cnt = f'COUNTIFS({rpr("E")},{sup},{rpr("K")},">0")'
    s.value = (f'=IF({sup}="","Add a supplier on 1 Your Shop to use this block.",IF({cnt}>10,"More than 10 lines: see 3 Reorder Plan for the rest.",'
               f'IF({cnt}=0,"Nothing to order from this supplier this cycle.",{cnt}&IF({cnt}=1," line"," lines")&" to order.")))')
    s.font = D.f(9, False, "muted"); s.alignment = Alignment(vertical="top")
    po.merge_cells(f"{cs[0]}{r}:{cs[-1]}{r}"); D.h(po, r, 18); r += 1
    D.h(po, r, 6); r += 1
    for k, head in zip(cs, ("SKU", "PRODUCT", "QTY", "UNIT COST", "COST")):
        c = po[f"{k}{r}"]; c.value = head; c.font = D.f(8, True, "muted")
        c.alignment = Alignment(horizontal="left" if head in ("SKU", "PRODUCT") else "right", vertical="bottom")
        c.border = Border(bottom=D.side("ink"))
    D.h(po, r, 24); r += 1
    first = r
    src = {0: "C", 1: "D", 2: "K", 3: "L", 4: "M"}
    fmts = {0: "@", 1: "@", 2: INT, 3: USD2, 4: USD2}
    for line in range(1, N_LINES + 1):
        for j, k in enumerate(cs):
            c = po[f"{k}{r}"]
            c.value = (f'=IF({sup}="","",IFERROR(INDEX({rpr(src[j])},MATCH({sup}&"|"&{line},{rpr("S")},0)),""))')
            c.number_format = fmts[j]; c.font = D.f(10, j == 4)
            c.alignment = Alignment(horizontal="left" if j < 2 else "right", vertical="center", indent=1 if j == 0 else 0)
            c.border = Border(bottom=D.side("hair"))
        D.h(po, r, D.GRID_ROW); r += 1
    for k in cs:
        c = po[f"{k}{r}"]; c.fill = D.fill("total_tint"); c.font = D.f(10, True)
        c.border = Border(top=D.side("ink")); c.alignment = Alignment(horizontal="right", vertical="center")
    po[f"{cs[0]}{r}"].value = "Order total"; po[f"{cs[0]}{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    po[f"{cs[-1]}{r}"].value = f"=SUM({cs[-1]}{first}:{cs[-1]}{r - 1})"; po[f"{cs[-1]}{r}"].number_format = USD2
    tot = r
    D.h(po, r, D.GRID_ROW); r += 1
    D.h(po, r, 12)
    D.frame(po, top, r, left, right)
    PO_TOTALS.append(f"{cs[-1]}{tot}"); PO_FIRST_LINES.append((first, cs))
    return r


r = PO_TOP
for pair in range(N_SUP // 2):
    e1 = po_block(pair * 2, r, "C")
    e2 = po_block(pair * 2 + 1, r, "K")
    assert e1 == e2
    if pair:
        S.page_break_before(po, r)
    r = e1 + 2
po_cards_end = r - 2
counted = "+".join(f'IF({s}="",0,COUNTIFS({rpr("E")},{s},{rpr("K")},">0"))' for s in SUPr)
D.h(po, 6, 10)
D.stat_strip(po, 7, [
    ("C:D", "Lines to order", f'=COUNTIF({rpr("K")},">0")', INT),
    ("E:G", "Suppliers with an order", "=" + "+".join(f"({t}>0)" for t in PO_TOTALS), INT),
    ("K:L", "All purchase orders", "=" + "+".join(PO_TOTALS), USD2),
    ("M:O", "Lines with no listed supplier", f'=COUNTIF({rpr("K")},">0")-({counted})', INT),
])
D.status_rule(po, "M8", "$M$8>0", fill_tint=False)
D.h(po, 9, 10)
D.frame(po, 6, 9, "B", "P")
D.h(po, 10, 14)
PO_NOTES = [
    ("No listed supplier", "A line to order whose supplier is blank, or isn't one of the six names on 1 Your Shop, can't go "
     "on a purchase order here. When the count above is more than 0, pick the supplier for that SKU on 2 SKU List."),
    ("Before you send", "Check minimum order quantities, price breaks, shipping and lead times with each supplier. The block "
     "totals are at your unit cost, before shipping and tax."),
]
po_n_end = notes_card(po, po_cards_end + 2, PO_NOTES, span=("C", "O"), frame_span=("B", "P"))
finish(po, po_n_end + 1, ("A", "Q"), "A11", "blue")
PO = "'4 Purchase Orders'!"


# =====================================================================  5 Cash Check
cc = wb.create_sheet("5 Cash Check")
# decision columns first so the answer sits next to the product; the working columns follow
X = dict(rank="C", sku="D", prod="E", status="F", dec="G", nowq="H", nowc="I", defq="J", defc="K", sup="L", days="M",
         prio="N", cost="O", full="P", cover="Q", top="R", coverf="S", topf="T", cov="U", topd="V")
S.set_widths(cc, {"A": 3, "B": 2, "C": 6, "D": 10, "E": 24, "F": 18, "G": 14, "H": 9, "I": 11, "J": 9, "K": 11, "L": 19,
                  "M": 8, "N": 9, "O": 9, "P": 8, "Q": 8, "R": 8, "S": 9, "T": 9, "U": 10, "V": 10, "W": 2, "X": 3})
D.page_header(cc, "Cash Check", "Can you afford the order? If not, what to buy now and what to defer to the next cycle.",
              AS_OF, span=("B", "W"), side_cols=4)
CC_TOP = 11
cc_first = CC_TOP + 5
cc_last = cc_first + N - 1
cc_tot = cc_last + 1
USABLE = UCr


def ccf(kind):
    def fn(r):
        c = {k: f"{v}{r}" for k, v in X.items()}
        M_ = f"MATCH(${X['rank']}{r},{rpr('Q')},0)"
        look = lambda col: f'=IFERROR(INDEX({rpr(col)},{M_}),"")'  # noqa: E731
        U, V = X["cov"], X["topd"]
        prev_u = "0" if r == cc_first else f"SUM(${U}${cc_first}:{U}{r - 1})"
        prev_v = "0" if r == cc_first else f"SUM(${V}${cc_first}:{V}{r - 1})"
        b = f'=IF({c["sku"]}=""'
        return {
            "sku": look("C"), "prod": look("D"), "sup": look("E"), "status": look("F"), "days": look("N"),
            "prio": look("P"), "cost": look("L"), "full": look("K"),
            "cover": f'{b},"",MIN({c["full"]},IFERROR(INDEX({rpr("R")},{M_}),0)))',
            "top": f'{b},"",{c["full"]}-{c["cover"]})',
            "coverf": f'{b},"",IF({c["cost"]}>0,MIN({c["cover"]},INT(MAX(0,{USABLE}-{prev_u})/{c["cost"]})),{c["cover"]}))',
            "topf": (f'{b},"",IF({c["cost"]}>0,MIN({c["top"]},INT(MAX(0,{USABLE}-SUM(${U}${cc_first}:${U}${cc_last})-{prev_v})/{c["cost"]})),{c["top"]}))'),
            "nowq": f'{b},"",{c["coverf"]}+{c["topf"]})',
            "nowc": f'{b},"",{c["nowq"]}*{c["cost"]})',
            "defq": f'{b},"",{c["full"]}-{c["nowq"]})',
            "defc": f'{b},"",{c["defq"]}*{c["cost"]})',
            "dec": f'{b},"",IF({c["nowq"]}=0,"DEFER",IF({c["defq"]}>0,"PARTIAL","ORDER NOW")))',
            "cov": f'{b},0,{c["coverf"]}*{c["cost"]})',
            "topd": f'{b},0,{c["topf"]}*{c["cost"]})',
        }[kind]
    return fn


HEADS = dict(sku=("SKU", None, "left"), prod=("Product", None, "left"), status=("Status", None, "left"),
             dec=("Decision", None, "left"), nowq=("Order now qty", INT, "right"), nowc=("Order now cost", USD2, "right"),
             defq=("Deferred qty", INT, "right"), defc=("Deferred cost", USD2, "right"), sup=("Supplier", None, "left"),
             days=("Days of stock", NUM1, "right"), prio=("Priority score", NUM2, "right"), cost=("Unit cost", USD2, "right"),
             full=("Full qty", INT, "right"), cover=("Cover qty", INT, "right"), top=("Top-up qty", INT, "right"),
             coverf=("Cover funded", INT, "right"), topf=("Top-up funded", INT, "right"),
             cov=("Cover $ funded", USD2Z, "right"), topd=("Top-up $ funded", USD2Z, "right"))
BOLD = {"status", "dec", "nowq", "nowc"}
cols_cc = [dict(col=X["rank"], head="Rank", kind="text", fmt=INT, align="right", values=list(range(1, N + 1)) + [None])]
for k in ("sku", "prod", "status", "dec", "nowq", "nowc", "defq", "defc", "sup", "days", "prio", "cost", "full", "cover",
          "top", "coverf", "topf", "cov", "topd"):
    head, fmt, al = HEADS[k]
    d = dict(col=X[k], head=head, kind="calc", align=al, bold=k in BOLD, formula=ccf(k))
    if fmt:
        d["fmt"] = fmt
    cols_cc.append(d)
f1, l1, cc_end = D.table_card(cc, CC_TOP, "B", "W", cols_cc, N + 1, title="What to buy now", sub="placeholder")
assert (f1, l1) == (cc_first, cc_tot), (f1, l1)
D.h(cc, cc_first - 1, 44)
for r in range(cc_first, cc_last + 1):
    for k in ("cov", "topd"):
        cc[f"{X[k]}{r}"].font = D.f(9, False, "muted")
    cc[f"{X['rank']}{r}"].font = D.f(10, False, "muted")
total_row(cc, cc_tot, D.cols("C", "V"), "D", "Totals", {
    X["nowq"]: (f"=SUM({X['nowq']}{cc_first}:{X['nowq']}{cc_last})", INT),
    X["nowc"]: (f"=SUM({X['nowc']}{cc_first}:{X['nowc']}{cc_last})", USD2),
    X["defq"]: (f"=SUM({X['defq']}{cc_first}:{X['defq']}{cc_last})", INT),
    X["defc"]: (f"=SUM({X['defc']}{cc_first}:{X['defc']}{cc_last})", USD2),
})
for k in ("sku", "prod", "status", "dec", "sup"):
    left_align(cc, X[k], cc_first, cc_last)
status_colors(cc, f"{X['status']}{cc_first}:{X['status']}{cc_last}", ["REORDER", "STOCKOUT RISK"])
word_colors(cc, f"{X['dec']}{cc_first}:{X['dec']}{cc_last}", {"ORDER NOW": ("teal", "teal_tint"), "PARTIAL": ("A87C1F", "FFF6D6"),
                                                               "DEFER": ("accent", "accent_tint")})
REC = f"={RP}{RP_TOTAL}"
NOWC = f"{X['nowc']}{cc_first}:{X['nowc']}{cc_last}"
DEFC = f"{X['defc']}{cc_first}:{X['defc']}{cc_last}"
D.h(cc, 6, 10)
D.stat_strip(cc, 7, [
    ("C:E", "Recommended order", REC, USD2),
    ("F:F", "Usable cash", f"={USABLE}", USD2),
    ("G:H", "Order now, funded", f"=SUM({NOWC})", USD2),
    ("I:L", "Deferred to next cycle", f"=SUM({DEFC})", USD2),
    ("M:O", "Shortfall", "=MAX(0,C8-F8)", USD2),
    ("P:V", "Cash left after ordering", "=F8-G8", USD2),
])
D.status_rule(cc, "M8", "$M$8>0", fill_tint=False)
D.status_rule(cc, "I8", "$I$8>0", fill_tint=False)
D.h(cc, 9, 10)
D.frame(cc, 6, 9, "B", "W")
D.h(cc, 10, 14)
VERDICT_ROW = CC_TOP + 2
cc[f"C{VERDICT_ROW}"].value = ('=IF(C8=0,"Nothing to order this cycle.",IF(C8<=F8,"You can afford this order. Send every purchase order.",'
                               'IF(G8=0,"You are "&TEXT(M8,"$#,##0.00")&" short and no row can be funded yet. Every row waits for the next cycle.",'
                               '"You are "&TEXT(M8,"$#,##0.00")&" short. Order the ORDER NOW and PARTIAL rows and defer the rest.")))')
cc[f"C{VERDICT_ROW}"].font = D.f(10, True)
cc.conditional_formatting.add(f"C{VERDICT_ROW}", FormulaRule(formula=["$C$8>$F$8"], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
cc.conditional_formatting.add(f"C{VERDICT_ROW}", FormulaRule(formula=["$C$8<=$F$8"], font=Font(color=D.T["teal"], bold=True), stopIfTrue=True))
CC_NOTES = [
    ("How the cut works when cash is short", "Pass 1: every SKU that needs an order gets its cover qty (enough to reach its "
     "reorder point), in priority order, as far as the cash goes. Pass 2: whatever is left tops SKUs up to their full "
     "recommended qty, highest priority first. Part orders are allowed, so an expensive SKU can't block cheaper ones below it. "
     "The columns right of Deferred cost show each pass."),
    ("Decision", "ORDER NOW: the full qty is funded. PARTIAL: some of it is funded; the rest waits. DEFER: nothing is funded "
     "this cycle. Don't stretch to fund deferred rows with money promised to a bill: the bill arrives before the stock does."),
    ("Usable cash", "Cash available for stock minus bills due before the stock lands, both on 1 Your Shop."),
]
cc_n_end = notes_card(cc, cc_end + 2, CC_NOTES, span=("C", "V"), frame_span=("B", "W"))
S.page_break_before(cc, cc_end + 2)
finish(cc, cc_n_end + 1, ("A", "X"), f"A{cc_first}", "teal")
cc.page_setup.orientation = "landscape"
CC = "'5 Cash Check'!"

# =====================================================================  6 Dead Stock
ds = wb.create_sheet("6 Dead Stock")
# the flag, the cash and the recommendation sit next to the product; the markdown ladder follows
Y = dict(sku="C", prod="D", flag="E", trap="F", rec="G", sup="H", onhand="I", cost="J", price="K", since="L", days="M",
         p10="N", b10="O", p25="P", b25="Q", p50="R", b50="S")
S.set_widths(ds, {"A": 3, "B": 2, "C": 10, "D": 26, "E": 9, "F": 11, "G": 34, "H": 20, "I": 8, "J": 9, "K": 9, "L": 9,
                  "M": 9, "N": 9, "O": 10, "P": 9, "Q": 10, "R": 9, "S": 10, "T": 2, "U": 3})
D.page_header(ds, "Dead Stock", "Cash sitting in stock that isn't moving, and a markdown ladder to get some of it back.",
              AS_OF, span=("B", "T"), side_cols=4)
DS_TOP = 11
ds_first = DS_TOP + 5
ds_last = ds_first + N - 1
ds_tot = ds_last + 1


def dsf(kind):
    def fn(r):
        i = r - ds_first + sk_first
        c = {k: f"{v}{r}" for k, v in Y.items()}
        b = f'=IF({SK}C{i}="",""'
        return {
            "sku": f"{b},{SK}C{i})", "prod": f"{b},{SK}D{i})", "sup": f'{b},IF({SK}E{i}="","",{SK}E{i}))',
            "onhand": f"{b},{SK}J{i})", "cost": f"{b},{SK}F{i})", "price": f"{b},{SK}G{i})", "since": f"{b},{SK}S{i})",
            "days": f"{b},{SK}P{i})",
            "flag": f'{b},IF({SK}T{i}="DEAD","DEAD",IF({SK}T{i}="OVERSTOCK","SLOW","")))',
            "trap": f'{b},IF({c["flag"]}="",0,{c["onhand"]}*{c["cost"]}))',
            "p10": f'{b},IF({c["flag"]}="","",{c["price"]}*(1-0.1)))', "b10": f'{b},IF({c["flag"]}="",0,{c["onhand"]}*{c["p10"]}))',
            "p25": f'{b},IF({c["flag"]}="","",{c["price"]}*(1-0.25)))', "b25": f'{b},IF({c["flag"]}="",0,{c["onhand"]}*{c["p25"]}))',
            "p50": f'{b},IF({c["flag"]}="","",{c["price"]}*(1-0.5)))', "b50": f'{b},IF({c["flag"]}="",0,{c["onhand"]}*{c["p50"]}))',
            "rec": (f'{b},IF({c["flag"]}="","",IF({c["flag"]}="SLOW","Stop reordering. 10% off to move it",IF({c["trap"]}<={SLr},"Donate or write off",'
                    f'IF({c["p50"]}>={c["cost"]},"Liquidate: up to 50% off",IF({c["p25"]}>={c["cost"]},"Bundle with a mover at 25% off","Bundle or donate"))))))'),
        }[kind]
    return fn


DHEADS = dict(sku=("SKU", None, "left", False), prod=("Product", None, "left", False), flag=("Flag", None, "left", True),
              trap=("Cash trapped", USD2Z, "right", True), rec=("Recommendation", None, "left", True),
              sup=("Supplier", None, "left", False), onhand=("On hand", INT, "right", False), cost=("Unit cost", USD2, "right", False),
              price=("Sell price", USD2, "right", False), since=("Days since last sale", INT, "right", False),
              days=("Days of stock", NUM1, "right", False), p10=("Price at 10% off", USD2, "right", False),
              b10=("Brings in at 10% off", USD2Z, "right", False), p25=("Price at 25% off", USD2, "right", False),
              b25=("Brings in at 25% off", USD2Z, "right", False), p50=("Price at 50% off", USD2, "right", False),
              b50=("Brings in at 50% off", USD2Z, "right", False))
cols_ds = []
for k, (head, fmt, al, bold) in DHEADS.items():
    d = dict(col=Y[k], head=head, kind="calc", align=al, bold=bold, formula=dsf(k))
    if fmt:
        d["fmt"] = fmt
    cols_ds.append(d)
f1, l1, ds_end = D.table_card(ds, DS_TOP, "B", "T", cols_ds, N + 1, title="Dead and slow stock",
                              sub="DEAD: no sale for the dead-stock days on 1 Your Shop. SLOW: still selling, but overstocked.")
assert (f1, l1) == (ds_first, ds_tot), (f1, l1)
D.h(ds, ds_first - 1, 44)
total_row(ds, ds_tot, D.cols("C", "S"), "C", "Flagged stock", {
    Y["trap"]: (f"=SUM({Y['trap']}{ds_first}:{Y['trap']}{ds_last})", USD2),
    Y["b10"]: (f"=SUM({Y['b10']}{ds_first}:{Y['b10']}{ds_last})", USD2),
    Y["b25"]: (f"=SUM({Y['b25']}{ds_first}:{Y['b25']}{ds_last})", USD2),
    Y["b50"]: (f"=SUM({Y['b50']}{ds_first}:{Y['b50']}{ds_last})", USD2),
})
for k in ("sku", "prod", "flag", "rec", "sup"):
    left_align(ds, Y[k], ds_first, ds_last)
word_colors(ds, f"{Y['flag']}{ds_first}:{Y['flag']}{ds_last}", {"DEAD": ("ink", "E6E3DD"), "SLOW": ("blue", "E3ECF7")})
ds.conditional_formatting.add(f"{Y['rec']}{ds_first}:{Y['rec']}{ds_last}", FormulaRule(formula=[f'{Y["rec"]}{ds_first}<>""'],
                              font=Font(color=D.T["accent"], bold=True)))
for pc in ("p10", "p25", "p50"):
    col = Y[pc]
    ds.conditional_formatting.add(f"{col}{ds_first}:{col}{ds_last}", FormulaRule(
        formula=[f'AND(ISNUMBER({col}{ds_first}),{col}{ds_first}<${Y["cost"]}{ds_first})'], font=Font(color=D.T["accent"])))
KD = f"{Y['flag']}{ds_first}:{Y['flag']}{ds_last}"


def dsum(word, key):
    return f'=SUMIF({KD},"{word}",{Y[key]}{ds_first}:{Y[key]}{ds_last})'


D.h(ds, 6, 10)
D.stat_strip(ds, 7, [
    ("C:D", "Cash trapped in dead stock", dsum("DEAD", "trap"), USD2),
    ("E:F", "Tied up in slow movers", dsum("SLOW", "trap"), USD2),
    ("G:G", "Dead stock back at 25% off", dsum("DEAD", "b25"), USD2),
    ("H:L", "Dead stock back at 50% off", dsum("DEAD", "b50"), USD2),
])
D.h(ds, 9, 10)
D.frame(ds, 6, 9, "B", "T")
D.h(ds, 10, 14)
DS_NOTES = [
    ("Recommendation, in this order", "SLOW: stop reordering and try 10% off. DEAD and worth no more than the small-lot figure on "
     "1 Your Shop at cost: donate it or write it off, as it isn't worth a clearance push. DEAD where half price still covers "
     "what you paid: liquidate, up to 50% off. DEAD where 25% off still covers cost: bundle it with a SKU that sells. "
     "Otherwise bundle or donate."),
    ("Brings in", "On hand x the marked-down price, before fees and shipping. Marked-down prices below your unit cost turn "
     "orange. Money already spent on dead stock doesn't come back on its own; pick one action per SKU this week."),
]
ds_n_end = notes_card(ds, ds_end + 2, DS_NOTES, span=("C", "S"), frame_span=("B", "T"))
S.page_break_before(ds, ds_end + 2)
finish(ds, ds_n_end + 1, ("A", "U"), f"A{ds_first}", "purple")
ds.page_setup.orientation = "landscape"
DS = "'6 Dead Stock'!"


# =====================================================================  1 Your Shop: glance, status, where the cash is, tiles
B = D.Card(ys, TOP, "G", "H", "I", "K", extra="J", wb=wb)
B.title("Your inventory at a glance", "From the other tabs. Change a yellow cell and these move.")
B.eyebrow("CASH ON THE SHELF")
g_inv = B.calc("Stock value at cost", f"=SUM({skr('U')})", USD2, bold=True)
g_dead = B.calc("Trapped in dead stock", f"={DS}C8", USD2)
g_slow = B.calc("Tied up in slow movers", f"={DS}E8", USD2)
B.eyebrow("THIS ORDER")
g_rec = B.calc("Recommended order", f"={RP}{RP_TOTAL}", USD2)
g_use = B.calc("Usable cash", f"=$D${UC}", USD2)
g_short = B.calc("Shortfall", f"=MAX(0,I{g_rec}-I{g_use})", USD2)
g_now = B.calc("Order now, funded", f"={CC}G8", USD2, bold=True)
g_def = B.calc("Deferred to next cycle", f"={CC}I8", USD2)
g_30 = B.calc("Order cost due in 30 days", f"=SUM({skr('X')})", USD2)
B.eyebrow("TURNOVER")
g_cogs = B.calc("Yearly cost of goods sold", f"=SUM({skr('Y')})", USD0)
g_turn = B.calc("Inventory turns a year", f"=IF(I{g_inv}>0,I{g_cogs}/I{g_inv},0)", NUM1, bold=True)
g_days = B.calc("Days to sell through stock", f"=IF(I{g_turn}>0,365/I{g_turn},0)", INT)
B.close()
D.status_rule(ys, f"I{g_dead}", f"$I${g_dead}>0", fill_tint=False)
D.status_rule(ys, f"I{g_def}", f"$I${g_def}>0", fill_tint=False)
D.status_rule(ys, f"I{g_short}", f"$I${g_short}>0", fill_tint=False)
assert A.end == B.end, (A.end, B.end)

# SKUs by status, right column beside the suppliers
ST = D.Card(ys, B.end + 2, "G", "H", "I", "K", extra="J", wb=wb)
ST.title("SKUs by status", "How many SKUs, and their stock value at cost.")
st_rows = []
for w in STATUSES:
    rr = ST.calc(w, f'=COUNTIF({skr("T")},"{w}")', INT)
    v = ys[f"J{rr}"]; v.value = f'=SUMIF({skr("T")},"{w}",{skr("U")})'; v.number_format = USD2
    v.font = D.f(10); v.alignment = Alignment(horizontal="right", vertical="center")
    color, tint = STATUS_LOOK[w]
    ys[f"H{rr}"].font = D.f(9, True, color)
    st_rows.append(rr)
st_tot = ST.calc("All SKUs", f"=SUM(I{st_rows[0]}:I{st_rows[-1]})", INT, total=True)
v = ys[f"J{st_tot}"]; v.value = f"=SUM(J{st_rows[0]}:J{st_rows[-1]})"; v.number_format = USD2
v.font = D.f(10, True); v.alignment = Alignment(horizontal="right", vertical="center")
while SUP.r < ST.r:
    SUP._row()
while ST.r < SUP.r:
    ST._row()
SUP.close(); ST.close()
assert SUP.end == ST.end, (SUP.end, ST.end)

# Where the cash is: top 5 by stock value (keys in the helper block at the bottom of this tab)
W_TOP = SUP.end + 2
HELP_TOP = None   # filled below
w_rows = []
r = W_TOP
D.h(ys, r, 12); r += 1
t = ys[f"C{r}"]; t.value = "Where the cash is"; t.font = D.f(12, True); ys.merge_cells(f"C{r}:J{r}"); D.h(ys, r, 24); r += 1
t = ys[f"C{r}"]; t.value = "Your five SKUs with the most stock value at cost. Overstocked ones are cash you could free up."
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top"); ys.merge_cells(f"C{r}:J{r}"); D.h(ys, r, 18); r += 1
for k, head, al in (("C", "PRODUCT", "left"), ("D", "SKU", "left"), ("H", "STATUS", "left"), ("I", "STOCK VALUE", "right")):
    c = ys[f"{k}{r}"]; c.value = head; c.font = D.f(8, True, "muted"); c.alignment = Alignment(horizontal=al, vertical="bottom")
for k in D.cols("C", "J"):
    ys[f"{k}{r}"].border = Border(bottom=D.side("ink"))
D.h(ys, r, 22); r += 1
w_first = r
for k in range(5):
    w_rows.append(r); D.h(ys, r, D.GRID_ROW)
    for col in D.cols("C", "J"):
        ys[f"{col}{r}"].border = Border(bottom=D.side("hair"))
    r += 1
D.h(ys, r, 12)
W_END = r
D.frame(ys, W_TOP, W_END, "B", "K")
YS_NOTES = [
    ("As-of date", "Every days figure counts from it: days since last sale, runs out on, days until reorder. Update it, the on-hand "
     "and on-order counts and the daily sales each time you sit down to reorder; about ten minutes once the SKUs are in."),
    ("Safety stock and days between orders", "Safety stock is a cushion on top of the sales you expect while an order is in "
     "transit; 20% is the sample's starting point, not a rule. Days between your orders sets how much cover each order buys, "
     "so a longer cycle means bigger, less frequent orders."),
    ("Sales trend", "The forecast is your last 30 days of sales. If your demand is seasonal, set the trend before every order: "
     "+30% scales every SKU's daily sales up by 30%."),
    ("Turnover", "Inventory turns = cost of goods a year at your current pace divided by the stock value at cost. Read the "
     "direction over time rather than the number: falling turns with rising stock value means cash is piling up on shelves."),
    ("The sample", "Maple & Moss Goods, its products, suppliers and numbers are fictional. Clear the yellow cells on 2 SKU List "
     "to start your own."),
    ("Before you rely on a number", S.SHORT_NOTICE.format(date=CHECKED).replace("Terms of Use page", "Terms tab") + " "
     "Calculations are estimates for planning and depend on your inputs. They aren't accounting, tax or financial advice. Check "
     "fees, rates and interest against your own statements and the provider's current terms."),
]
ys_n_end = notes_card(ys, W_END + 2, YS_NOTES)
S.page_break_before(ys, W_END + 2)
S.page_break_before(ys, A.end + 2)

# helper block: one ranking key per SKU row (v1's sort key), below the printed area
HELP_TOP = ys_n_end + 3
hh = ys[f"C{HELP_TOP}"]; hh.value = "Helper: ranking keys for Where the cash is (leave as is)"; hh.font = D.f(9, True, "muted")
D.h(ys, HELP_TOP, 20)
key_first = HELP_TOP + 1
for i in range(N):
    rr = key_first + i
    src = sk_first + i
    lab = ys[f"C{rr}"]; lab.value = f"2 SKU List row {src}"; lab.font = D.f(8, False, "muted")
    kc = ys[f"D{rr}"]; kc.value = f'=IF({SK}C{src}="",-1,{SK}U{src}+ROW({SK}C{src})/100000)'
    kc.number_format = "#,##0.00000"; kc.font = D.f(8, False, "muted")
    D.h(ys, rr, 14)
key_last = key_first + N - 1
KEY = f"$D${key_first}:$D${key_last}"
for k, rr in enumerate(w_rows, 1):
    big = f"LARGE({KEY},{k})"
    for col, src, fmt in (("C", "D", "@"), ("D", "C", "@"), ("H", "T", "@"), ("I", "U", USD2)):
        c = ys[f"{col}{rr}"]
        c.value = f'=IFERROR(IF({big}<0,"",INDEX({skr(src)},MATCH({big},{KEY},0))),"")'
        c.number_format = fmt; c.font = D.f(10, col == "I")
        c.alignment = Alignment(horizontal="right" if col == "I" else "left", vertical="center")
    bar = ys[f"J{rr}"]
    bar.value = f'=IFERROR(REPT("{D.BAR_CHAR}",MAX(0,ROUND(I{rr}/MAX($I${w_rows[0]}:$I${w_rows[-1]})*11,0))),"")'
    bar.font = D.f(9, False, "blue"); bar.alignment = Alignment(horizontal="left", vertical="center", indent=1)
status_colors(ys, f"H{w_rows[0]}:H{w_rows[-1]}")

# hero tiles (rows 6 to 9)
D.tile(ys, 6, "B", "E", "USABLE CASH FOR THIS ORDER", f"=$D${UC}", USD2,
       f'=IF($D${CA}="","Type the cash you could send to suppliers","Cash "&TEXT($D${CA},"$#,##0")&" less "&TEXT(N($D${BD}),"$#,##0")'
       f'&" of bills due before the stock lands")', dark=True)
v, sub, _ = D.tile(ys, 6, "G", "K", "THE PLANNER RECOMMENDS ORDERING", f"=$I${g_rec}", USD2,
                   f'=IF($I${g_rec}=0,"Nothing to order this cycle",IF($I${g_rec}<=$D${UC},"You can afford it: send every purchase order",'
                   f'TEXT($I${g_rec}-$D${UC},"$#,##0.00")&" more than your usable cash. 5 Cash Check splits it."))')
D.status_rule(ys, v.coordinate, f"$I${g_rec}>$D${UC}", fill_tint=False)
D.h(ys, 10, 14)
finish(ys, key_last, ("A", "L"), "A11", "accent", print_last=ys_n_end + 1)

# order the working tabs 1 to 6
wb._sheets = [wb[n] for n in ("1 Your Shop", "2 SKU List", "3 Reorder Plan", "4 Purchase Orders", "5 Cash Check", "6 Dead Stock")]

# =====================================================================  Start Here and Terms (card style, from #13 and #9)
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
            m = re.match(r"^([A-Z0-9][A-Za-z0-9 ,+&\-]{1,40})\. (.*)$", text, re.S) if kind in ("para", "num", "bullet") else None
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
        elif kind == "bullet":
            L.value = "•"; L.font = D.f(12, True, "teal"); L.alignment = Alignment(horizontal="center", vertical="center")
        elif kind.startswith("chip"):
            L.value = left[0]; L.number_format = left[1]; L.alignment = Alignment(horizontal="center", vertical="center")
            if kind == "chip-in":
                L.fill = D.fill("input_fill"); L.font = D.f(9, True, "input_text")
                L.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
            elif kind == "chip-calc":
                L.font = D.f(9, False, "ink"); L.border = Border(bottom=D.side("hair"))
            elif kind == "chip-status":
                L.font = D.f(8, True, "accent"); L.fill = D.fill("accent_tint")
            else:
                L.fill = D.fill("ink"); L.font = D.f(9, True, "on_ink")
        D.h(sh, r, ht); r += 1
    D.h(sh, r, 12)
    D.frame(sh, top, r, "B", "F")
    return r + 2


sh = wb.create_sheet("Start Here", 0)
S.set_widths(sh, SH_GRID)
D.page_header(sh, PRODUCT, "Start here. Run your first reorder in about 30 minutes.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
r = 6
r = sh_card(sh, r, "What it does", [(None,
    "Most reorder sheets tell you what to buy. This one also asks whether you can pay for it. Type your SKUs, your cash and "
    "the bills due before the stock lands. The workbook flags every SKU (OK, REORDER, STOCKOUT RISK, OVERSTOCK, DEAD), "
    "works out how many to order, ranks the orders by profit per day and days left, decides what to buy now and what to "
    "defer when cash is short, writes a purchase order per supplier and shows the cash trapped in stock that isn't moving.",
    "para")])
r = sh_card(sh, r, "Six steps", [
    (1, "Your Shop. Today's date, the cash you could send to suppliers, bills due first, your reorder rules and suppliers.", "num"),
    (2, "SKU List. One row per SKU: cost, price, fees, lead time, on hand, on order, daily sales, last sale date.", "num"),
    (3, "Reorder Plan. Nothing to type. Every SKU that needs an order gets a quantity, a cost and a rank.", "num"),
    (4, "Purchase Orders. One block per supplier, ready to copy into an email or a supplier's order form.", "num"),
    (5, "Cash Check. Can you afford it? If not, order the ORDER NOW and PARTIAL rows and defer the rest.", "num"),
    (6, "Dead Stock. Cash trapped in DEAD and SLOW stock, a 10%, 25% and 50% markdown ladder and one action each.", "num"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "How to read the cells", [
    ((EX["cash"], USD0), "Yellow cells with blue numbers are yours to change. Type over the example. Each one shows a hint when you select it.", "chip-in"),
    ((34.3, NUM1), "Plain numbers are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((1500, USD0), "Dark tiles and bold numbers are your answers. The tiles sit at the top of 1 Your Shop.", "chip-key"),
    (("REORDER", "@"), "Status words are coloured: orange needs an order now, gold soon, blue overstock, grey dead, green OK.", "chip-status"),
    (None, "Each tab is protected without a password. To change anything else, use Review, Unprotect Sheet in Excel, or Data, "
           "Protect sheets and ranges in Google Sheets.", "note"),
])
r = sh_card(sh, r, "The example", [(None,
    "Maple & Moss Goods, a fictional shop with 16 SKUs and 3 suppliers, has $1,800 for stock and $300 of bills due first, so "
    "$1,500 of usable cash. The planner wants $2,793.90 of stock across 7 SKUs: $1,293.90 more than the cash. 5 Cash Check "
    "funds every at-risk SKU's cover quantity first ($603.90), then tops up the canvas tote bags in full, 45 of 50 "
    "beeswax wraps and one soap bar: $1,497.50 now, $1,296.40 deferred to the next cycle. Two dead SKUs hold $124.50, and the overstocked "
    "pot holders hold $663.", "para")])
r = sh_card(sh, r, "Try it on the example", [
    (None, "Cash. On 1 Your Shop, change the cash from $1,800 to $3,300. Usable cash becomes $3,000, the verdict on 5 Cash "
           "Check says you can afford it and every row turns to ORDER NOW. Put it back.", "bullet"),
    (None, "On order. On 2 SKU List, set the soy candles' on-order count from 48 to 0. They flip from OK to STOCKOUT RISK: 24 "
           "candles at 3.5 a day last under 7 days, less than the 7-day lead time. Put it back.", "bullet"),
    (None, "Trend. Set the sales trend to +30%. Eight SKUs now need an order instead of seven, and the recommended order grows from $2,793.90 to $4,282.00. Put it back to 0%.",
     "bullet"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "What each sample SKU shows", [
    (None, "Mug, SKU-001. OK: 34 days of stock against a 21-day lead time.", "bullet"),
    (None, "Bud vase, SKU-002. STOCKOUT RISK: 17 days of stock, a 21-day lead time and nothing on order. Ordered today, it still "
           "runs out for a few days.", "bullet"),
    (None, "Serving bowl, SKU-004. STOCKOUT RISK with the best margin in the shop. 5 Cash Check funds its cover quantity first.", "bullet"),
    (None, "Espresso cups, SKU-005. DEAD: no sale since May. Half price would bring in less than cost; 25% off still covers it, "
           "so the advice is to bundle them with a SKU that sells.", "bullet"),
    (None, "Tote bag, SKU-007. STOCKOUT RISK and the best profit per day. Rank 1, funded in full.", "bullet"),
    (None, "Pot holders, SKU-009. OVERSTOCK: 130 on hand at 0.9 a day is 144 days of stock. Stop reordering.", "bullet"),
    (None, "Soy candle, SKU-011. OK only because 48 are on order. Take that away and it turns STOCKOUT RISK.", "bullet"),
    (None, "Soap bar, SKU-012. REORDER: 6 a day on a 7-day lead time; small margin, big quantity.", "bullet"),
    (None, "Greeting cards, SKU-013. OK, but less than a day from its reorder point. Watch it next cycle.", "bullet"),
    (None, "Beeswax wraps, SKU-014. REORDER with the second-best profit per day; topped up with the cash left over.", "bullet"),
    (None, "Ornaments, SKU-015. DEAD: a $22.50 lot under the $30 small-lot line, so the advice is donate or write off.", "bullet"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "Good to know", [
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. Every formula is a plain "
           "formula that works in Excel, Google Sheets, Numbers and LibreOffice. No macros, no add-ons, no sign-up.", "para"),
    (None, "Clear the sample. Select only the yellow cells on 2 SKU List and press Delete, then type your suppliers on 1 Your "
           "Shop. Don't delete whole rows: the formula columns go blank on their own when a row has no SKU.", "para"),
    (None, "Supplier minimums. The planner doesn't know your suppliers' minimum orders or price breaks. Check them before you "
           "send a purchase order, and round up when a minimum is close.", "para"),
    (None, "More than 30 SKUs. See the note at the bottom of 2 SKU List, or keep your top 30 sellers here.", "para"),
])
r = sh_card(sh, r, "Before you rely on a number", [(None,
    S.SHORT_NOTICE.format(date=CHECKED).replace("Terms of Use page", "Terms tab") + " "
    "Calculations are estimates for planning and depend on your inputs. They aren't accounting, tax or financial advice. Check "
    "fees, rates and interest against your own statements and the provider's current terms.", "note")])
D.paint_canvas(sh, r - 1, "Z")
S.finish_sheet(sh, PRODUCT, r - 1, span=("A", "G"), tab_color="teal")

tm = wb.create_sheet("Terms")
S.set_widths(tm, SH_GRID)
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version {VERSION}. Read this before you rely on a number.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
paras = open(os.path.join(HERE, "LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().strip().split("\n\n")[1:]
r = 6
r = sh_card(tm, r, "More from the shop", [
    (None, ("Etsy True Profit System: what you really keep on each sale", "https://www.etsy.com/listing/4584721212"), "link"),
    (None, ("Shipping True-Cost Calculator: price shipping without losing money", "https://www.etsy.com/listing/4585097496"), "link"),
    (None, ("Everything in the shop: proofnotfluff.etsy.com", SHOP_URL), "link"),
])
S.page_break_before(tm, r)
r = sh_card(tm, r, "Terms of Use and disclaimer", [(None, p, "para") for p in paras])
r = sh_card(tm, r, "A small ask", [
    (None, "If this planner helped you order with confidence, a short review on Etsy helps other shop owners find it. Thank you.", "para"),
])
D.paint_canvas(tm, r - 1, "Z")
S.finish_sheet(tm, PRODUCT, r - 1, span=("A", "G"), tab_color="note")

wb.active = 0
problems = S.audit(wb)
if problems:
    print("AUDIT:", *problems, sep="\n  ")
wb.save(OUT)
print("saved", OUT)
print({"ys": dict(SN=SN, AD=AD, CA=CA, BD=BD, UC=UC, SS=SS, OC=OC, TR=TR, DD=DDY, OD=OD, SL=SL, DL=DL, SUP=SUP_ROWS,
                  g_inv=g_inv, g_dead=g_dead, g_slow=g_slow, g_rec=g_rec, g_use=g_use, g_short=g_short, g_now=g_now, g_def=g_def, g_30=g_30,
                  g_cogs=g_cogs, g_turn=g_turn, g_days=g_days, st_rows=st_rows, st_tot=st_tot, w_rows=w_rows),
       "sk": dict(first=sk_first, tot=sk_tot), "rp": dict(first=rp_first, tot=rp_tot), "po": PO_FIRST_LINES, "po_tot": PO_TOTALS,
       "cc": dict(first=cc_first, tot=cc_tot, verdict=VERDICT_ROW), "ds": dict(first=ds_first, tot=ds_tot)})
