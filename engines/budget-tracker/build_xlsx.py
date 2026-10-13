#!/usr/bin/env python3
"""Budget Tracker Spreadsheet, version 1 (v3 dashboard design, Oct 13, 2026).

A spend-first budget tracker for Excel and Google Sheets. You type each purchase once:
  1 Budget        one list of categories (income, bills, spending, savings) with a monthly budget each.
  2 Transactions  one row per money in or money out: date, what, category from the list, amount.
  3 Month         pick a month: left to spend, every category's budget, spent and left, in words and bars.
  4 Year          twelve months of every category side by side, and out against the budget by month.

Different from the shop's Budget Planner (#29), which plans pay schedules and takes one typed actual per line
per month: here every purchase is its own row and the totals build themselves from the log.

Built to design/WORKBOOK_STANDARD.md section 0 with tools/pnf_dash.py and tools/wb_style.py.
Only SUMIFS, COUNTIFS, SUMPRODUCT, INDEX, MATCH, DATE, TODAY, REPT, IF and IFERROR: no macros, no scripts,
no charts, no locked-for-good ranges, so it works in the Google Sheets phone app too.

  python3 build_xlsx.py Budget-Tracker-EXAMPLE.xlsx           (the worked example, July to September 2026)
  python3 build_xlsx.py Budget-Tracker.xlsx --blank           (category names kept, no amounts, no transactions)
"""
import datetime as dt
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

PRODUCT = "Budget Tracker Spreadsheet"
VERSION = "1"
CHECKED = "Oct 13, 2026"
AS_OF = f"Checked {CHECKED}"
HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[1:]
BLANK = "--blank" in args
args = [a for a in args if a != "--blank"]
OUT = args[0] if args else "Budget-Tracker-EXAMPLE.xlsx"
MONEY = '"$"#,##0.00;-"$"#,##0.00;"$"0.00'
MONEY_T = '"$"#,##0.00;-"$"#,##0.00;"-"'     # tables: a dash for zero so empty rows stay quiet
USD0 = '"$"#,##0;-"$"#,##0;"-"'
PCT = '0%;-0%;0%'
INT = S.FMT["int"]
DATE = S.FMT["date"]
HIDE = ";;;"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
               "October", "November", "December"]
ARR_MON = "{" + ",".join(f'"{m}"' for m in MONTHS) + "}"
ARR_NAME = "{" + ",".join(f'"{m}"' for m in MONTH_NAMES) + "}"

# ---------------------------------------------------------------- categories (group fixed by position)
GROUP_ORDER = [("Income", "INCOME", 4), ("Bills", "BILLS", 10), ("Spending", "EVERYDAY SPENDING", 14),
               ("Savings", "SAVINGS AND EXTRA DEBT PAYMENTS", 4)]
_BUDGET = {
    "Income": [("Paycheck", 4200), ("Side income", 300)],
    "Bills": [("Rent", 1450), ("Car insurance", 120), ("Streaming", 25), ("Electric", 95), ("Internet", 65),
              ("Phone", 55), ("Student loan", 210)],
    "Spending": [("Groceries", 550), ("Eating out", 200), ("Gas", 160), ("Household", 80), ("Personal care", 60),
                 ("Fun", 120), ("Clothing", 75), ("Gifts", 50), ("Other", 100)],
    "Savings": [("Emergency fund", 400), ("Vacation fund", 150)],
}
CATS = []          # (group, name, monthly budget)
for g, _, n in GROUP_ORDER:
    items = _BUDGET[g] + [("", None)] * (n - len(_BUDGET[g]))
    CATS += [(g, nm or None, amt) for nm, amt in items]
N_CATS = len(CATS)

# ---------------------------------------------------------------- the example: a made-up household, July to September 2026
d = dt.datetime
TX = []  # (date, what, category, amount, paid with)


def add(m, day, what, cat, amt, paid="Debit card"):
    TX.append((d(2026, m, day), what, cat, amt, paid))


MONTH_DATA = {
    7: dict(side=280.00, electric=112.40,
            groceries=[(4, 128.45), (11, 142.30), (18, 119.86), (25, 151.22)],
            eating=[(3, 38.60), (10, 24.15), (17, 61.80), (24, 29.40)],
            gas=[(6, 51.30), (16, 48.75), (27, 55.10)],
            household=[(8, 39.95), (21, 26.40)], personal=[(13, 42.15)], fun=[(4, 64.00), (19, 38.50)],
            clothing=[(23, 59.99)], gifts=[(29, 40.00)], other=[(14, 31.25), (30, 18.60)]),
    8: dict(side=345.00, electric=118.75,
            groceries=[(1, 137.90), (8, 126.15), (15, 148.72), (22, 133.41), (29, 96.80)],
            eating=[(2, 44.25), (9, 31.70), (16, 22.90), (23, 57.35), (30, 35.10)],
            gas=[(5, 49.85), (14, 53.20), (24, 50.65)],
            household=[(11, 58.30)], personal=[(20, 36.40)], fun=[(8, 45.00), (22, 72.00)],
            clothing=[(15, 84.50)], gifts=[(26, 30.00)], other=[(12, 22.75), (27, 48.10)]),
    9: dict(side=260.00, electric=91.30,
            groceries=[(5, 132.18), (12, 118.64), (19, 141.07), (26, 109.53)],
            eating=[(4, 42.80), (11, 18.65), (18, 64.25), (24, 31.90), (27, 56.40)],
            gas=[(3, 48.20), (14, 52.75), (25, 51.10)],
            household=[(7, 46.32), (21, 22.18)], personal=[(16, 38.99)], fun=[(6, 45.00), (20, 62.50)],
            clothing=[(10, 79.99), (17, -34.99)], gifts=[(23, 35.00)], other=[(9, 27.45), (29, 41.20)]),
}
WHAT = {"groceries": ("Groceries", "Grocery store"), "eating": ("Eating out", "Takeout and cafes"),
        "gas": ("Gas", "Gas station"), "household": ("Household", "Household supplies"),
        "personal": ("Personal care", "Pharmacy and haircare"), "fun": ("Fun", "Movies, games, outings"),
        "clothing": ("Clothing", "Clothes"), "gifts": ("Gifts", "Birthday gift"), "other": ("Other", "Odds and ends")}
for m, md in MONTH_DATA.items():
    add(m, 1, "Paycheck", "Paycheck", 2100.00, "Deposit")
    add(m, 1, "Rent", "Rent", 1450.00, "Bank transfer")
    add(m, 2, "Emergency fund transfer", "Emergency fund", 400.00, "Bank transfer")
    add(m, 9, "Streaming", "Streaming", 25.00, "Credit card")
    add(m, 12, "Car insurance", "Car insurance", 120.00, "Credit card")
    add(m, 15, "Paycheck", "Paycheck", 2100.00, "Deposit")
    add(m, 16, "Vacation fund transfer", "Vacation fund", 150.00, "Bank transfer")
    add(m, 18, "Electric bill", "Electric", md["electric"], "Bank transfer")
    add(m, 20, "Weekend dog walking", "Side income", md["side"], "Deposit")
    add(m, 22, "Internet", "Internet", 65.00, "Credit card")
    add(m, 25, "Phone", "Phone", 55.00, "Credit card")
    add(m, 28, "Student loan", "Student loan", 210.00, "Bank transfer")
    for key, (cat, what) in WHAT.items():
        for day, amt in md[key]:
            w = "Returned jacket (refund)" if amt < 0 else what
            add(m, day, w, cat, amt, "Credit card" if key in ("eating", "fun", "clothing") else "Debit card")
TX.sort(key=lambda t: (t[0], t[2]))
EX_YEAR, EX_MONTH = 2026, 9


def ex_numbers(m):
    grp = {c[1]: c[0] for c in CATS if c[1]}
    bud = {c[1]: c[2] for c in CATS if c[1]}
    act = {n: round(sum(t[3] for t in TX if t[2] == n and t[0].month == m), 2) for n in bud}
    out_b = sum(v for n, v in bud.items() if grp[n] != "Income")
    out_a = round(sum(v for n, v in act.items() if grp[n] != "Income"), 2)
    inc_a = round(sum(v for n, v in act.items() if grp[n] == "Income"), 2)
    over = [n for n in bud if grp[n] in ("Bills", "Spending") and act[n] > bud[n] + 1e-9]
    return dict(act=act, out_b=out_b, out_a=out_a, inc_b=sum(v for n, v in bud.items() if grp[n] == "Income"),
                inc_a=inc_a, left=round(out_b - out_a, 2), net=round(inc_a - out_a, 2), over=over,
                spend_a=round(sum(v for n, v in act.items() if grp[n] == "Spending"), 2))


EXAMPLE = {m: ex_numbers(m) for m in (7, 8, 9)}
EXM = EXAMPLE[EX_MONTH]
# the Start Here example and the listing quote these; fail the build if the data ever drifts
assert (EXM["inc_b"], EXM["out_b"]) == (4500, 3965), EXM
assert (EXM["out_a"], EXM["left"], EXM["net"], EXM["over"]) == (3797.41, 167.59, 662.59, ["Eating out"]), EXM
N_TX = len(TX)
if BLANK:
    CATS = [(g, n, None) for g, n, _ in CATS]
    TX = []

BUD_N, TX_N, MON_N, YR_N = "1 Budget", "2 Transactions", "3 Month", "4 Year"
BUD, TXS, MON, YR = (f"'{n}'" for n in (BUD_N, TX_N, MON_N, YR_N))


def rich(head, body, size=9):
    return CellRichText(TextBlock(InlineFont(rFont=D.FONT, sz=size, b=True, color=D.T["ink"]), head + ". "),
                        TextBlock(InlineFont(rFont=D.FONT, sz=size, color=D.T["ink2"]), body))


def sign_rule(ws, ref):
    ws.conditional_formatting.add(ref, FormulaRule(formula=[f'AND(ISNUMBER({ref}),{ref}<0)'], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
    ws.conditional_formatting.add(ref, FormulaRule(formula=[f'AND(ISNUMBER({ref}),{ref}>0)'], font=Font(color=D.T["teal"], bold=True), stopIfTrue=True))


def notes_card(ws, top, left, right, c0, c1, notes, title="Notes"):
    r = top
    D.h(ws, r, 12); r += 1
    t = ws[f"{c0}{r}"]; t.value = title; t.font = D.f(12, True); ws.merge_cells(f"{c0}{r}:{c1}{r}"); D.h(ws, r, 24); r += 1
    width = sum(S.width_of(ws, k) for k in D.cols(c0, c1))
    for head, body in notes:
        cell = ws[f"{c0}{r}"]; cell.value = rich(head, body)
        cell.alignment = Alignment(vertical="top", wrap_text=True); ws.merge_cells(f"{c0}{r}:{c1}{r}")
        D.h(ws, r, S.text_height(head + ". " + body, width, 9) + 4); r += 1
    D.h(ws, r, 12)
    D.frame(ws, top, r, left, right)
    return r


def fill_heights(ws, last):
    for rr in range(1, last + 1):
        if ws.row_dimensions[rr].height is None:
            D.h(ws, rr, D.GRID_ROW)


def head_row(ws, row, spec, span):
    for k, txt, al in spec:
        c = ws[f"{k}{row}"]; c.value = txt; c.font = D.f(8, True, "muted")
        c.alignment = Alignment(horizontal=al, vertical="bottom", wrap_text=True, indent=1 if al == "left" and k != span[0] else 0)
    for k in D.cols(*span):
        ws[f"{k}{row}"].border = Border(bottom=D.side("ink"))
    D.h(ws, row, 24)


wb = S.new_workbook(PRODUCT, version=VERSION)
GRID = {"A": 3, "B": 2, "C": 30, "D": 16, "E": 15, "F": 2, "G": 2, "H": 15, "I": 12, "J": 24, "K": 2, "L": 3}

# =====================================================================  1 Budget
bu = wb.create_sheet(BUD_N)
S.set_widths(bu, GRID)
D.page_header(bu, "Your budget", "One list of categories with a monthly budget each. The other tabs follow this list.",
              AS_OF, span=("B", "K"), side_cols=3)
B_TOP = 23
cols_b = [
    dict(col="C", head="Category", kind="input", values=[c[1] for c in CATS], validation=("textLength", 0, 40),
         prompt="A short name, up to 40 characters, for example Groceries. Clear it to drop the line. Each name once.",
         error="Up to 40 characters."),
    dict(col="D", head="Group", kind="muted", values=[c[0] for c in CATS]),
    dict(col="E", head="Monthly budget", kind="input", fmt=MONEY, align="right", values=[c[2] for c in CATS],
         validation=("decimal", 0, 10000000), error="Type an amount from 0 to 10,000,000, as a positive number.",
         prompt="What you plan for this category in a month, for example 550. For income, what you expect to come in."),
    dict(col="H", head="Per year", kind="calc", fmt=MONEY_T, align="right",
         formula=lambda rr: f'=IF(C{rr}="",0,N(E{rr})*12)'),
    dict(col="I", head="Of income", kind="calc", fmt=PCT, align="right",
         formula=lambda rr: f'=IF(OR(C{rr}="",N(E{rr})=0,$E$__INC__=0,D{rr}="Income"),"",E{rr}/$E$__INC__)'),
    dict(col="J", head="", kind="calc", formula=lambda rr: f'=IF(I{rr}="","",REPT("{D.BAR_CHAR}",MIN(18,MAX(1,ROUND(I{rr}*16,0)))))'),
]
CF, CL, B_END = D.table_card(bu, B_TOP, "B", "K", cols_b, N_CATS, title="Your categories",
                             sub="Yellow cells are yours: rename, clear or add a line in any group, and type its monthly budget.")
NAMES = f"{BUD}!$C${CF}:$C${CL}"
GRPS = f"{BUD}!$D${CF}:$D${CL}"
BUDS = f"{BUD}!$E${CF}:$E${CL}"
ROW_OF = {i: CF + i for i in range(N_CATS)}
GROUP_ROWS = {}
i0 = 0
for g, _, n in GROUP_ORDER:
    GROUP_ROWS[g] = (CF + i0, CF + i0 + n - 1)
    i0 += n
for rr in range(CF, CL + 1):
    bu[f"D{rr}"].font = D.f(9, True, "muted"); bu[f"J{rr}"].font = D.f(9, False, "blue")
    bu[f"J{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    bu[f"C{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
for g, (a, b) in GROUP_ROWS.items():       # an ink rule between groups
    if a != CF:
        for k in D.cols("C", "J"):
            bu[f"{k}{a}"].border = Border(top=D.side("ink2"), bottom=D.side("hair"))

# cards above the table, rows 11 to 21
K = D.Card(bu, 11, "B", "C", "E", "F", wb=wb)
K.title("Budget totals", "A month, from the list below.")
GSUM = {}
for g, label in (("Income", "Income"), ("Bills", "Bills"), ("Spending", "Everyday spending"), ("Savings", "Savings")):
    GSUM[g] = K.calc(label, f'=SUMIFS($E${CF}:$E${CL},$D${CF}:$D${CL},"{g}",$C${CF}:$C${CL},"<>")', MONEY,
                     bold=g == "Income")
r_bout = K.calc("Everything out", f"=E{GSUM['Bills']}+E{GSUM['Spending']}+E{GSUM['Savings']}", MONEY, total=True)
r_bleft = K.calc("Left to budget", f"=E{GSUM['Income']}-E{r_bout}", MONEY, bold=True, tint="total_tint")
sign_rule(bu, f"E{r_bleft}")
K.close()
for rr in range(CF, CL + 1):
    for k in ("I", "J"):
        bu[f"{k}{rr}"].value = bu[f"{k}{rr}"].value.replace("$E$__INC__", f"$E${GSUM['Income']}")

G = D.Card(bu, 11, "G", "H", "I", "K", extra="J", wb=wb)
G.title("Where each dollar goes", "Each group as a share of budgeted income.")
GB = {}
for g, color, label in (("Bills", "ink", "Bills"), ("Spending", "blue", "Spending"), ("Savings", "gold", "Savings")):
    GB[g] = G.calc(label, f'=IF($E${GSUM["Income"]}=0,"",$E${GSUM[g]}/$E${GSUM["Income"]})', PCT)
    bu[f"J{GB[g]}"].value = f'=IF(I{GB[g]}="","",REPT("{D.BAR_CHAR}",MIN(16,MAX(1,ROUND(I{GB[g]}*14,0)))))'
    bu[f"J{GB[g]}"].font = D.f(9, False, color); bu[f"J{GB[g]}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
GB["left"] = G.calc("Left to budget", f'=IF($E${GSUM["Income"]}=0,"",$E${r_bleft}/$E${GSUM["Income"]})', PCT, bold=True)
bu[f"J{GB['left']}"].value = f'=IF(OR(I{GB["left"]}="",I{GB["left"]}<=0),"",REPT("{D.BAR_CHAR}",MIN(16,MAX(1,ROUND(I{GB["left"]}*14,0)))))'
bu[f"J{GB['left']}"].font = D.f(9, False, "teal"); bu[f"J{GB['left']}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
sign_rule(bu, f"I{GB['left']}")
r_dup = G.calc("Names used twice", f'=SUMPRODUCT(($C${CF}:$C${CL}<>"")*(COUNTIF($C${CF}:$C${CL},$C${CF}:$C${CL})>1))', INT)
D.status_rule(bu, f"I{r_dup}", f"$I${r_dup}>0", fill_tint=False)
G.text(f'=IF($I${r_dup}>0,"Give each category its own name so its spending is counted once","Every name is used once")',
       size=9, color="ink2")
G.close()
assert max(K.end, G.end) < B_TOP, (K.end, G.end)

# tiles, rows 6 to 9
D.tile(bu, 6, "B", "F", "LEFT TO BUDGET EACH MONTH", f"=$E${r_bleft}", MONEY,
       f'=IF($E${GSUM["Income"]}=0,"Type your monthly income below to start",IF($E${r_bleft}<0,"Your budget is more than your income. Trim a line below.",'
       f'IF($E${r_bleft}=0,"Every dollar has a job","Income with no job yet. Give it one, or leave it as a cushion.")))', dark=True)
v_b, s_b, _ = D.tile(bu, 6, "G", "K", "BUDGETED OUT EACH MONTH", f"=$E${r_bout}", MONEY,
                     f'="Bills, everyday spending and savings, from "&COUNTIFS($C${CF}:$C${CL},"<>",$D${CF}:$D${CL},"<>Income")&" categories"')
D.h(bu, 10, 14)
BN_TOP = B_END + 2
bn_end = notes_card(bu, BN_TOP, "B", "K", "C", "J", [
    ("Groups", "Each line belongs to the group printed beside it: income, bills, everyday spending or savings. Use the empty "
     "lines in a group to add categories. Extra debt payments go under savings."),
    ("Renaming", "Rename a category here and the Transactions dropdown follows. Rows already typed with the old name show up "
     "as Not on the list on the Transactions tab until you pick the new name."),
    ("A cost that comes once a year", "Budget a twelfth of it each month, for example $20 a month for a $240 car registration, "
     "and log the payment in the month it is paid."),
])
BU_LAST = bn_end + 1
D.h(bu, BU_LAST, 14)
fill_heights(bu, BU_LAST)
D.paint_canvas(bu, BU_LAST, "Z")
S.finish_sheet(bu, PRODUCT, BU_LAST, span=("A", "L"), freeze="A11", tab_color="gold")
S.page_break_before(bu, B_TOP)
S.page_break_before(bu, BN_TOP)

# =====================================================================  2 Transactions
N_ROWS = 1000
tx = wb.create_sheet(TX_N)
S.set_widths(tx, {"A": 3, "B": 2, "C": 13, "D": 30, "E": 24, "F": 13, "G": 16, "H": 26, "I": 18, "J": 2, "K": 3})
D.page_header(tx, "Transactions", "One row per money in or money out. Type it once; every total builds itself from this log.",
              "Example rows: type over them" if not BLANK else "Type your first row in row 16", span=("B", "J"), side_cols=3)
T_TOP = 11
T_FIRST = T_TOP + 5
T_LAST = T_FIRST + N_ROWS - 1


def counts_as(r):
    return (f'=IF(F{r}="","",IF(E{r}="","Needs a category",IF(C{r}="","Needs a date",'
            f'IFERROR(INDEX({GRPS},MATCH(E{r},{NAMES},0)),"Not on the list"))))')


cols_t = [
    dict(col="C", head="Date", kind="input", fmt=DATE, values=[t[0] for t in TX],
         validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"),
         prompt="The day the money moved, for example 9/14/2026. It shows the month by name so you can check it.",
         error="Type a real date between 2000 and 2100, for example 9/14/2026."),
    dict(col="D", head="What it was", kind="input", values=[t[1] for t in TX], validation=("textLength", 0, 80),
         prompt="A few words you will recognise later, for example Grocery store. Optional.", error="Up to 80 characters."),
    dict(col="E", head="Category (pick)", kind="input", values=[t[2] for t in TX], validation=("list_range", NAMES),
         prompt="Choose a category from the list. The list comes from the 1 Budget tab; rename or add categories there.",
         error="Choose a category from the list. To add one, type it on the 1 Budget tab first."),
    dict(col="F", head="Amount", kind="input", fmt=MONEY, align="right", values=[t[3] for t in TX],
         validation=("decimal", -10000000, 10000000),
         prompt="A positive number, for example 54.20. The category decides if it is money in or out. A refund is a minus amount in the same category.",
         error="Type an amount from -10,000,000 to 10,000,000. Use a minus only for a refund."),
    dict(col="G", head="Paid with", kind="input", values=[t[4] for t in TX], validation=("textLength", 0, 30),
         prompt="Optional: debit card, credit card, cash, deposit.", error="Up to 30 characters."),
    dict(col="H", head="Notes", kind="input", values=[], validation=("textLength", 0, 120),
         prompt="Anything worth remembering about this row. Optional.", error="Up to 120 characters."),
    dict(col="I", head="Counts as", kind="calc", formula=counts_as),
]
f1, f2, t_end = D.table_card(tx, T_TOP, "B", "J", cols_t, N_ROWS, title="Your transactions",
                             sub=f"Yellow columns are yours. Counts as fills in on its own. {N_ROWS:,} rows; the totals read every row.")
assert (f1, f2) == (T_FIRST, T_LAST), (f1, f2)
for rr in range(T_FIRST, T_LAST + 1):
    tx[f"I{rr}"].font = D.f(9, False, "ink2"); tx[f"I{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    for k in ("D", "E", "G", "H"):
        tx[f"{k}{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
tx.conditional_formatting.add(f"C{T_FIRST}:E{T_LAST}", FormulaRule(
    formula=[f'AND($F{T_FIRST}<>"",OR($C{T_FIRST}="",$E{T_FIRST}=""))'], fill=PatternFill("solid", bgColor=D.T["accent_tint"])))
for word, color in (("Needs", "accent"), ("Not on", "accent")):
    tx.conditional_formatting.add(f"I{T_FIRST}:I{T_LAST}", FormulaRule(
        formula=[f'LEFT($I{T_FIRST},{len(word)})="{word}"'], font=Font(color=D.T[color], bold=True), stopIfTrue=True))
TA = f"{TXS}!$F${T_FIRST}:$F${T_LAST}"
TC = f"{TXS}!$E${T_FIRST}:$E${T_LAST}"
TD = f"{TXS}!$C${T_FIRST}:$C${T_LAST}"
FIX = (f'SUMPRODUCT(({TA}<>"")*((({TC}="")+({TD}="")+(({TC}<>"")*(COUNTIF({NAMES},{TC})=0)))>0))')

# =====================================================================  3 Month
mo = wb.create_sheet(MON_N)
S.set_widths(mo, GRID)
D.page_header(mo, "Your month", "Pick a month. See what is left to spend and every category against its budget.",
              AS_OF, span=("B", "K"), side_cols=3)
K = D.Card(mo, 11, "B", "C", "E", "F", wb=wb)
K.title("The month", "Leave both blank to see this month.")
r_m = K.input("Month to show", None if BLANK else MONTHS[EX_MONTH - 1], "@", name="MonthShown", validation=("list", MONTHS),
              allow_blank=True, prompt_title="Month",
              prompt="Pick a month from the list. Leave blank for this month.",
              error="Pick a month from the list: Jan to Dec.")
mo[f"E{r_m}"].alignment = Alignment(horizontal="center", vertical="center")
r_y = K.input("Year", None if BLANK else EX_YEAR, "0", name="YearShown", validation=("whole", 2000, 2100),
              allow_blank=True, prompt_title="Year",
              prompt="Type a year, for example 2026. Leave blank for this year (it changes on its own on January 1).",
              error="Type a year from 2000 to 2100, or leave the cell blank for this year.")
mo[f"E{r_y}"].alignment = Alignment(horizontal="center", vertical="center")
M = f"$F${r_m}"
Y = f"$F${r_y}"
hm = mo[f"F{r_m}"]; hm.value = f'=IF($E${r_m}="",MONTH(TODAY()),IFERROR(MATCH($E${r_m},{ARR_MON},0),MONTH(TODAY())))'
hm.number_format = HIDE
hy = mo[f"F{r_y}"]; hy.value = f'=IF($E${r_y}="",YEAR(TODAY()),$E${r_y})'; hy.number_format = HIDE
START, NEXT = f"DATE({Y},{M},1)", f"DATE({Y},{M}+1,1)"


def spent(name_ref):
    return (f'SUMIFS({TXS}!$F:$F,{TXS}!$E:$E,{name_ref},{TXS}!$C:$C,">="&{START},{TXS}!$C:$C,"<"&{NEXT})')


r_show = K.calc("Showing", f'=INDEX({ARR_NAME},{M})&" "&{Y}', "@")
mo[f"E{r_show}"].alignment = Alignment(horizontal="right", vertical="center")
r_ib = K.calc("Income, budgeted", f"={BUD}!$E${GSUM['Income']}", MONEY)
r_ia = K.calc("Income, came in", "=0", MONEY)            # filled after the table
r_ob = K.calc("Out, budgeted", f"={BUD}!$E${r_bout}", MONEY)
r_oa = K.calc("Out so far", "=0", MONEY, total=True)     # filled after the table
K.close()

G = D.Card(mo, 11, "G", "H", "I", "K", extra="J", wb=wb)
G.title("Spent of budget", "Each group's spending as a share of its budget.")
GROW = {}
for g, color, label in (("Bills", "ink", "Bills"), ("Spending", "blue", "Spending"), ("Savings", "gold", "Savings")):
    GROW[g] = G.calc(label, "=0", PCT)
    mo[f"J{GROW[g]}"].font = D.f(9, False, color); mo[f"J{GROW[g]}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
GROW["all"] = G.calc("Everything out", f'=IF($E${r_ob}=0,"",$E${r_oa}/$E${r_ob})', PCT, bold=True)
mo[f"J{GROW['all']}"].font = D.f(9, False, "teal"); mo[f"J{GROW['all']}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
G.text("A full bar is 100% of the budget. Red means over it.", size=9, color="muted")
G.close()

# ---- category by category
L_TOP = max(K.end, G.end) + 2
r = L_TOP
D.h(mo, r, 12); r += 1
t = mo[f"C{r}"]; t.value = f'="Category by category, "&INDEX({ARR_NAME},{M})&" "&{Y}'; t.font = D.f(12, True); mo.merge_cells(f"C{r}:J{r}")
D.h(mo, r, 24); r += 1
t = mo[f"C{r}"]; t.value = "Budget from the 1 Budget tab, actual from the Transactions tab. Left is budget minus actual; a minus means over."
t.font = D.f(9, False, "muted"); mo.merge_cells(f"C{r}:J{r}"); D.h(mo, r, 18); r += 1
D.h(mo, r, 6); r += 1
head_row(mo, r, [("C", "CATEGORY", "left"), ("D", "BUDGET", "right"), ("E", "ACTUAL", "right"), ("H", "LEFT", "right"),
                 ("I", "USED", "right"), ("J", "STATUS", "left")], ("C", "J"))
r += 1
LTOT = {}
LINE_RANGES = {}


def l_eyebrow(text):
    global r
    c = mo[f"C{r}"]; c.value = text; c.font = D.f(8, True, "muted"); c.alignment = Alignment(vertical="bottom")
    for k in D.cols("C", "J"):
        mo[f"{k}{r}"].border = Border(bottom=D.side("hair"))
    D.h(mo, r, D.GRID_ROW); r += 1


def status_formula(g, rr):
    if g == "Income":
        return (f'=IF(C{rr}="","",IF(E{rr}=0,"Nothing in yet",IF(E{rr}>=D{rr},"Came in",'
                f'REPT("{D.BAR_CHAR}",MIN(14,MAX(1,ROUND(E{rr}/D{rr}*14,0)))))))')
    over = "Saved more than planned" if g == "Savings" else "Over budget"
    done = {"Savings": "Saved", "Bills": "Paid"}.get(g)
    bar = f'IF(E{rr}<0,"Refund",IF(E{rr}=0,"Nothing yet",REPT("{D.BAR_CHAR}",MIN(14,MAX(1,ROUND(E{rr}/D{rr}*14,0))))))'
    if done:
        bar = f'IF(AND(D{rr}>0,E{rr}=D{rr}),"{done}",{bar})'
    return f'=IF(C{rr}="","",IF(AND(D{rr}=0,E{rr}>0),"Not budgeted",IF(E{rr}>D{rr},"{over}",{bar})))'


def l_row(name, budget, actual, g=None, total=False, tint=None):
    global r
    c = mo[f"C{r}"]; c.value = name; c.font = D.f(10, total); c.alignment = Alignment(vertical="center")
    for k, v in (("D", budget), ("E", actual)):
        cell = mo[f"{k}{r}"]; cell.value = v; cell.number_format = MONEY_T; cell.font = D.f(10, total, "ink2" if k == "D" else "ink")
        cell.alignment = Alignment(horizontal="right", vertical="center")
    lf = mo[f"H{r}"]; lf.value = f'=IF(C{r}="","",D{r}-E{r})'; lf.number_format = MONEY_T; lf.font = D.f(10, True)
    lf.alignment = Alignment(horizontal="right", vertical="center")
    if g in ("Bills", "Spending", None):
        sign_rule(mo, f"H{r}")
    us = mo[f"I{r}"]; us.value = f'=IF(OR(C{r}="",D{r}=0),"",E{r}/D{r})'; us.number_format = PCT; us.font = D.f(9, False, "ink2")
    us.alignment = Alignment(horizontal="right", vertical="center")
    sw = mo[f"J{r}"]
    sw.value = status_formula(g or "Spending", r) if not total else status_formula(g or "Spending", r)
    sw.font = D.f(9, total, {"Savings": "gold", "Income": "teal"}.get(g, "teal"))
    sw.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    mo.conditional_formatting.add(f"J{r}", FormulaRule(formula=[f'OR($J{r}="Over budget",$J{r}="Not budgeted")'],
                                                      font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
    mo.conditional_formatting.add(f"J{r}", FormulaRule(formula=[f'OR($J{r}="Nothing yet",$J{r}="Nothing in yet")'],
                                                      font=Font(color=D.T["muted"]), stopIfTrue=True))
    mo.conditional_formatting.add(f"J{r}", FormulaRule(formula=[f'OR($J{r}="Came in",$J{r}="Saved more than planned",$J{r}="Paid",$J{r}="Saved")'],
                                                      font=Font(color=D.T["teal"], bold=True), stopIfTrue=True))
    for k in D.cols("C", "J"):
        cell = mo[f"{k}{r}"]
        cell.border = Border(top=D.side("ink") if total else None, bottom=D.side("hair"))
        if tint:
            cell.fill = D.fill(tint)
    D.h(mo, r, D.GRID_ROW)
    out = r; r += 1
    return out


TOTAL_LABEL = {"Income": "Total income", "Bills": "Total bills", "Spending": "Total everyday spending", "Savings": "Total savings"}
for g, eyebrow, n in GROUP_ORDER:
    l_eyebrow(eyebrow)
    a, b = GROUP_ROWS[g]
    first = r
    for br in range(a, b + 1):
        l_row(f'=IF({BUD}!$C${br}="","",{BUD}!$C${br})', f'=IF({BUD}!$C${br}="","",N({BUD}!$E${br}))',
              f'=IF({BUD}!$C${br}="","",{spent(f"{BUD}!$C${br}")})', g=g)
    last = r - 1
    LINE_RANGES[g] = (first, last)
    LTOT[g] = l_row(TOTAL_LABEL[g], f"=SUM(D{first}:D{last})", f"=SUM(E{first}:E{last})", g=g, total=True)
L_ALL = l_row("Everything out", f"=D{LTOT['Bills']}+D{LTOT['Spending']}+D{LTOT['Savings']}",
              f"=E{LTOT['Bills']}+E{LTOT['Spending']}+E{LTOT['Savings']}", g=None, total=True, tint="total_tint")
D.h(mo, r, 12)
L_END = r
D.frame(mo, L_TOP, L_END, "B", "K")
S.page_break_before(mo, L_TOP)

# fill the cards from the table
mo[f"E{r_ia}"].value = f"=E{LTOT['Income']}"
mo[f"E{r_oa}"].value = f"=E{L_ALL}"
for g in ("Bills", "Spending", "Savings"):
    rr = GROW[g]
    mo[f"I{rr}"].value = f'=IF(D{LTOT[g]}=0,"",E{LTOT[g]}/D{LTOT[g]})'
for g, rr in GROW.items():
    mo[f"I{rr}"].number_format = '0.0%;-0.0%;0.0%'
    mo[f"J{rr}"].value = f'=IF(OR(I{rr}="",I{rr}<=0),"",REPT("{D.BAR_CHAR}",MIN(16,MAX(1,ROUND(I{rr}*14,0)))))'
    if g != "Savings":
        mo.conditional_formatting.add(f"J{rr}", FormulaRule(formula=[f'AND(ISNUMBER($I{rr}),$I{rr}>1)'], font=Font(color=D.T["accent"]), stopIfTrue=True))
        D.status_rule(mo, f"I{rr}", f"$I${rr}>1", fill_tint=False)
N_OVER = "(" + "+".join(f'COUNTIF($J${LINE_RANGES[g][0]}:$J${LINE_RANGES[g][1]},"Over budget")'
                        f'+COUNTIF($J${LINE_RANGES[g][0]}:$J${LINE_RANGES[g][1]},"Not budgeted")'
                        for g in ("Bills", "Spending")) + ")"
N_MONTH = f'COUNTIFS({TD},">="&{START},{TD},"<"&{NEXT},{TA},"<>")'
MONTH_NAME = f"INDEX({ARR_NAME},{M})"

# ---- the biggest single spends of the month (top 5 by amount)
P_TOP = L_END + 2
r = P_TOP
D.h(mo, r, 12); r += 1
t = mo[f"C{r}"]; t.value = f'="Biggest everyday spends, "&{MONTH_NAME}'; t.font = D.f(12, True); mo.merge_cells(f"C{r}:J{r}")
D.h(mo, r, 24); r += 1
t = mo[f"C{r}"]; t.value = "Everyday spending only, so you see the choices, not the rent. Each line is one row of the Transactions tab."
t.font = D.f(9, False, "muted"); mo.merge_cells(f"C{r}:J{r}"); D.h(mo, r, 18); r += 1
D.h(mo, r, 6); r += 1
head_row(mo, r, [("C", "WHAT IT WAS", "left"), ("D", "DATE", "right"), ("E", "AMOUNT", "right"), ("H", "CATEGORY", "left")], ("C", "J"))
r += 1
SP_ROWS = []
HK = f"{TXS}!$J${T_FIRST}:$J${T_LAST}"     # helper keys on the Transactions tab (everyday spends in the month shown)
for n in range(1, 6):
    key = f"$I${r}"
    kc = mo[f"I{r}"]; kc.value = f'=IFERROR(LARGE({HK},{n}),"")'; kc.number_format = HIDE
    pos = f"MATCH({key},{HK},0)"
    vals = {
        "C": f'=IF({key}="","",INDEX({TXS}!$D${T_FIRST}:$D${T_LAST},{pos}))',
        "D": f'=IF({key}="","",INDEX({TD},{pos}))',
        "E": f'=IF({key}="","",INDEX({TA},{pos}))',
        "H": f'=IF({key}="","",INDEX({TC},{pos}))',
    }
    for k, v in vals.items():
        c = mo[f"{k}{r}"]; c.value = v
        c.font = D.f(10, False, "ink2" if k in "DH" else "ink")
        c.alignment = Alignment(horizontal="left" if k in "CH" else "right", vertical="center", indent=1 if k == "H" else 0)
    mo[f"D{r}"].number_format = DATE; mo[f"E{r}"].number_format = MONEY_T
    for k in D.cols("C", "J"):
        mo[f"{k}{r}"].border = Border(bottom=D.side("hair"))
    D.h(mo, r, D.GRID_ROW)
    SP_ROWS.append(r); r += 1
c = mo[f"C{r}"]
c.value = (f'=IF(E{LTOT["Spending"]}<=0,"No everyday spending logged for "&{MONTH_NAME}&" yet",'
           f'"These five come to "&ROUND(SUM(E{SP_ROWS[0]}:E{SP_ROWS[-1]})/E{LTOT["Spending"]}*100,0)&"% of everyday spending this month")')
c.font = D.f(10, True, "ink2"); c.alignment = Alignment(vertical="center"); mo.merge_cells(f"C{r}:J{r}"); D.h(mo, r, D.GRID_ROW + 4)
r += 1
D.h(mo, r, 12)
P_END = r
D.frame(mo, P_TOP, P_END, "B", "K")

# ---- tiles (rows 6 to 9)
D.tile(mo, 6, "B", "F", f'="LEFT TO SPEND, "&UPPER({MONTH_NAME})&" "&{Y}', f"=$E${r_ob}-$E${r_oa}", MONEY,
       f'=IF($E${r_ob}=0,"Type your monthly budget on the 1 Budget tab first",IF({N_MONTH}=0,"Nothing logged for "&{MONTH_NAME}&" yet: add it on the Transactions tab",'
       f'IF($E${r_oa}>$E${r_ob},"Over the budget. Spent "&ROUND($E${r_oa}/$E${r_ob}*100,0)&"% of it.",'
       f'"Spent "&MAX(0,ROUND($E${r_oa}/$E${r_ob}*100,0))&"% of the budget so far")))', dark=True)
v_r, s_r, _ = D.tile(mo, 6, "G", "K", "MONEY IN LESS MONEY OUT", f"=$E${r_ia}-$E${r_oa}", MONEY,
                     f'=IF(AND($E${r_ia}=0,$E${r_oa}=0),"Nothing logged for "&{MONTH_NAME}&" yet",IF($E${r_ob}=0,"No budget set yet on the 1 Budget tab",IF($E${r_ia}=0,"No income logged for this month yet",'
                     f'IF({N_OVER}=0,"Every category within its budget",{N_OVER}&IF({N_OVER}=1," category over its budget"," categories over their budget")))))')
sign_rule(mo, v_r.coordinate)
mo.conditional_formatting.add(s_r.coordinate, FormulaRule(formula=[f"{N_OVER}>0"], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
D.h(mo, 10, 14)

MN_TOP = P_END + 2
mn_end = notes_card(mo, MN_TOP, "B", "K", "C", "J", [
    ("Left to spend", "Budgeted out for the month (bills, everyday spending and savings from the 1 Budget tab) minus what the "
     "Transactions tab shows went out in that month. A minus means the month went over the budget."),
    ("Money in less money out", "Income logged for the month minus everything that went out. Savings count as out."),
    ("Not budgeted", "A category with no budget but money logged against it. Give it a budget on the 1 Budget tab if it comes back."),
    ("Rows not counted", "A row needs a date, an amount and a category from the list to count. The Transactions tab marks any "
     "row with an amount that is missing a date or category, or uses a name not on the list."),
    ("Before you rely on a number", S.SHORT_NOTICE.format(date=CHECKED).replace("Terms of Use page", "Terms tab")
     + " " + S.MONEY_TIER_CLAUSE),
], title="How the numbers work")
MO_LAST = mn_end + 1
D.h(mo, MO_LAST, 14)
fill_heights(mo, MO_LAST)
D.paint_canvas(mo, MO_LAST, "Z")
S.finish_sheet(mo, PRODUCT, MO_LAST, span=("A", "L"), freeze="A11", tab_color="accent")
S.page_break_before(mo, P_TOP)
_lines_pt = sum(mo.row_dimensions[rr].height or D.GRID_ROW for rr in range(L_TOP, L_END + 1))
mo.sheet_properties.pageSetUpPr.fitToPage = False
mo.page_setup.scale = max(40, min(100, int(680 / _lines_pt * 100)))

# ---- Transactions helper keys: amount plus a row-sized fraction, for everyday spends in the month shown
for rr in range(T_FIRST, T_LAST + 1):
    hc = tx[f"J{rr}"]
    hc.value = (f'=IF(AND(I{rr}="Spending",N(F{rr})>0,N(C{rr})>=DATE({MON}!{Y},{MON}!{M},1),'
                f'N(C{rr})<DATE({MON}!{Y},{MON}!{M}+1,1)),F{rr}+ROW()/1000000000,"")')
    hc.number_format = HIDE

# ---- Transactions stat strip (needs the Month tab's month)
D.h(tx, 6, 10)
D.stat_strip(tx, 7, [
    ("C:D", "Shown on the Month tab", f"={MON}!$E${r_show}", "@"),
    ("E:E", "Money in that month", f"={MON}!$E${r_ia}", MONEY),
    ("F:G", "Money out that month", f"={MON}!$E${r_oa}", MONEY),
    ("H:I", "Rows to fix", f"={FIX}", INT),
])
D.h(tx, 9, 10)
D.frame(tx, 6, 9, "B", "J")
D.status_rule(tx, "H8", "$H$8>0", fill_tint=False)
D.h(tx, 10, 14)
D.paint_canvas(tx, t_end + 1, "Z")
S.finish_sheet(tx, PRODUCT, t_end + 1, span=("A", "K"), freeze=f"A{T_FIRST}", tab_color="teal")
tx.page_setup.orientation = "landscape"
tx.print_title_rows = f"{T_FIRST - 1}:{T_FIRST - 1}"
tx.print_area = f"A1:K{T_FIRST + 399}"  # print the first 400 rows, not 1,000 bare ones

# =====================================================================  4 Year
yr = wb.create_sheet(YR_N)
MC = D.cols("D", "O")
S.set_widths(yr, {"A": 3, "B": 2, "C": 22, **{k: 9.5 for k in MC}, "P": 11, "Q": 11, "R": 11, "S": 2, "T": 3})
D.page_header(yr, "Your year", "Every category, month by month, for the year picked on the Month tab.", AS_OF,
              span=("B", "S"), side_cols=4)
YY = f"{MON}!{Y}"


def ycell(name_ref, m):
    return (f'SUMIFS({TXS}!$F:$F,{TXS}!$E:$E,{name_ref},{TXS}!$C:$C,">="&DATE({YY},{m},1),{TXS}!$C:$C,"<"&DATE({YY},{m + 1},1))')


Y_TOP = 11
r = Y_TOP
D.h(yr, r, 12); r += 1
t = yr[f"C{r}"]; t.value = f'="Month by month, "&{YY}'; t.font = D.f(12, True); yr.merge_cells(f"C{r}:R{r}"); D.h(yr, r, 24); r += 1
t = yr[f"C{r}"]; t.value = "Actual amounts from the Transactions tab. Budget to date is the monthly budget times the months that have entries; Left is budget minus actual."
t.font = D.f(9, False, "muted"); yr.merge_cells(f"C{r}:R{r}"); D.h(yr, r, 18); r += 1
D.h(yr, r, 6); r += 1
Y_HEAD = r
head_row(yr, r, [("C", "CATEGORY", "left"), *[(k, MONTHS[i].upper(), "right") for i, k in enumerate(MC)],
                 ("P", "YEAR", "right"), ("Q", "BUDGET TO DATE", "right"), ("R", "LEFT", "right")], ("C", "R"))
r += 1
YTOT = {}


def y_eyebrow(text):
    global r
    c = yr[f"C{r}"]; c.value = text; c.font = D.f(8, True, "muted"); c.alignment = Alignment(vertical="bottom")
    for k in D.cols("C", "R"):
        yr[f"{k}{r}"].border = Border(bottom=D.side("hair"))
    D.h(yr, r, D.GRID_ROW); r += 1


def y_row(label, month_fn, budget, bold=False, tint=None, signed=False, top_rule=False):
    global r
    c = yr[f"C{r}"]; c.value = label; c.font = D.f(10, bold); c.alignment = Alignment(vertical="center")
    for m, k in enumerate(MC, 1):
        v = yr[f"{k}{r}"]; v.value = month_fn(m, k); v.number_format = USD0; v.font = D.f(9 if not bold else 10, bold)
        v.alignment = Alignment(horizontal="right", vertical="center")
        if signed:
            sign_rule(yr, f"{k}{r}")
    p = yr[f"P{r}"]; p.value = f'=IF(C{r}="","",SUM(D{r}:O{r}))'; p.number_format = USD0; p.font = D.f(10, True)
    q = yr[f"Q{r}"]; q.value = budget; q.number_format = USD0; q.font = D.f(10, bold, "ink2")
    lft = yr[f"R{r}"]; lft.value = f'=IF(OR(C{r}="",Q{r}=""),"",Q{r}-P{r})'; lft.number_format = USD0; lft.font = D.f(10, True)
    for k in "PQR":
        yr[f"{k}{r}"].alignment = Alignment(horizontal="right", vertical="center")
    if signed:
        sign_rule(yr, f"P{r}")
    for k in D.cols("C", "R"):
        cell = yr[f"{k}{r}"]
        cell.border = Border(top=D.side("ink") if (bold or top_rule) else None, bottom=D.side("hair"))
        if tint:
            cell.fill = D.fill(tint)
    D.h(yr, r, D.GRID_ROW)
    out = r; r += 1
    return out


for g, eyebrow, n in GROUP_ORDER:
    y_eyebrow(eyebrow)
    a, b = GROUP_ROWS[g]
    first = r
    for br in range(a, b + 1):
        rr = y_row(f'=IF({BUD}!$C${br}="","",{BUD}!$C${br})',
                   lambda m, k, br=br: f'=IF({BUD}!$C${br}="","",{ycell(f"{BUD}!$C${br}", m)})',
                   f'=IF({BUD}!$C${br}="","",N({BUD}!$E${br})*__NM__)')
        if g in ("Bills", "Spending"):
            sign_rule(yr, f"R{rr}")
    last = r - 1
    YTOT[g] = y_row(TOTAL_LABEL[g], lambda m, k, a=first, b=last: f"=SUM({k}{a}:{k}{b})", f"=SUM(Q{first}:Q{last})", bold=True)
    if g in ("Bills", "Spending"):
        sign_rule(yr, f"R{YTOT[g]}")
Y_OUT = y_row("Everything out", lambda m, k: f"={k}{YTOT['Bills']}+{k}{YTOT['Spending']}+{k}{YTOT['Savings']}",
              f"=Q{YTOT['Bills']}+Q{YTOT['Spending']}+Q{YTOT['Savings']}", bold=True)
sign_rule(yr, f"R{Y_OUT}")
Y_NET = y_row("Money in less money out", lambda m, k: f"={k}{YTOT['Income']}-{k}{Y_OUT}",
              f"=Q{YTOT['Income']}-Q{Y_OUT}", bold=True, tint="total_tint", signed=True)
yr[f"R{Y_NET}"].value = None
D.h(yr, r, 12)
Y_END = r
D.frame(yr, Y_TOP, Y_END, "B", "S")

# ---- out against the budget, month by month
O_TOP = Y_END + 2
r = O_TOP
D.h(yr, r, 12); r += 1
t = yr[f"C{r}"]; t.value = "Out against the budget"; t.font = D.f(12, True); yr.merge_cells(f"C{r}:R{r}"); D.h(yr, r, 24); r += 1
t = yr[f"C{r}"]; t.value = "Bills, everyday spending and savings for each month. Teal bars are under the budget, accent bars over it. Months with nothing logged stay empty."
t.font = D.f(9, False, "muted"); yr.merge_cells(f"C{r}:R{r}"); D.h(yr, r, 18); r += 1
D.h(yr, r, 6); r += 1
head_row(yr, r, [("C", "MONTH", "left"), ("E", "OUT", "right"), ("G", "BUDGET", "right"), ("I", "LEFT", "right"),
                 ("J", "UNDER OR OVER", "left")], ("C", "R"))
r += 1
O1 = r
SCALE = f"MAX(MAX($I${O1}:$I${O1 + 11}),-MIN($I${O1}:$I${O1 + 11}),1)"
for m, k in enumerate(MC):
    has = f"COUNTIFS({TD},\">=\"&DATE({YY},{m + 1},1),{TD},\"<\"&DATE({YY},{m + 2},1),{TA},\"<>\")>0"
    vals = {
        "C": MONTH_NAMES[m],
        "E": f'=IF({has},{k}{Y_OUT},"")',
        "G": f'=IF({has},{BUD}!$E${r_bout},"")',
        "I": f'=IF(E{r}="","",G{r}-E{r})',
        "J": f'=IF(OR(I{r}="",I{r}=0),"",REPT("{D.BAR_CHAR}",MAX(1,ROUND(ABS(I{r})/{SCALE}*30,0))))',
    }
    for kk, v in vals.items():
        c = yr[f"{kk}{r}"]; c.value = v
        if kk in "EGI":
            c.number_format = MONEY_T; c.alignment = Alignment(horizontal="right", vertical="center")
            c.font = D.f(10, kk == "I", "ink2" if kk == "G" else "ink")
        else:
            c.alignment = Alignment(horizontal="left", vertical="center", indent=1 if kk == "J" else 0)
            c.font = D.f(10) if kk == "C" else D.f(9, False, "teal")
    for kk in D.cols("C", "R"):
        yr[f"{kk}{r}"].border = Border(bottom=D.side("hair"))
    sign_rule(yr, f"I{r}")
    yr.conditional_formatting.add(f"J{r}", FormulaRule(formula=[f'AND(ISNUMBER($I{r}),$I{r}<0)'], font=Font(color=D.T["accent"]), stopIfTrue=True))
    D.h(yr, r, D.GRID_ROW)
    r += 1
OL = r - 1
NM = f"COUNT($E${O1}:$E${OL})"
for row in yr.iter_rows(min_col=17, max_col=17):
    for c in row:
        if isinstance(c.value, str) and "__NM__" in c.value:
            c.value = c.value.replace("__NM__", NM)
D.h(yr, r, 12)
O_END = r
D.frame(yr, O_TOP, O_END, "B", "S")
S.page_break_before(yr, O_TOP)

OVERM = f'COUNTIF($I${O1}:$I${OL},"<0")'
D.stat_strip(yr, 7, [
    ("C:E", "Money in", f"=$P${YTOT['Income']}", USD0),
    ("F:I", "Money out", f"=$P${Y_OUT}", USD0),
    ("J:M", "In less out", f"=$P${Y_NET}", USD0),
    ("N:R", "Months over budget", f"={OVERM}", INT),
])
D.h(yr, 9, 10)
D.frame(yr, 6, 9, "B", "S")
sign_rule(yr, "J8")
D.status_rule(yr, "N8", "$N$8>0", fill_tint=False)
D.h(yr, 10, 14)
YN_TOP = O_END + 2
yn_end = notes_card(yr, YN_TOP, "B", "S", "C", "R", [
    ("The year shown", "The year picked on the 3 Month tab (blank there means this year). Type a different year there to look back."),
    ("Budget to date", "The monthly budget times the number of months that have at least one transaction, so a year that "
     "started in July compares three months with three months. For income, Left is what was expected but did not come in."),
    ("Out against the budget", "A month counts once it has at least one transaction. Savings count as out, so a month can be "
     "under the budget and still have saved what was planned."),
])
YR_LAST = yn_end + 1
D.h(yr, YR_LAST, 14)
fill_heights(yr, YR_LAST)
D.paint_canvas(yr, YR_LAST, "Z")
S.finish_sheet(yr, PRODUCT, YR_LAST, span=("A", "T"), freeze="D11", tab_color="blue")
yr.page_setup.orientation = "landscape"
yr.print_title_rows = f"{Y_HEAD}:{Y_HEAD}"

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
            mm = re.match(r"^([A-Z][A-Za-z ,'0-9]{1,40})\. (.*)$", text, re.S) if kind in ("para", "num") else None
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
D.page_header(sh, PRODUCT, "Start here. Type each purchase once on Transactions; read the Month tab.", AS_OF,
              span=("B", "F"), side_cols=2)
r = 6
r = sh_card(sh, r, "What it does", [(None,
    "A spend-first budget tracker. Set a monthly budget for each category once on the 1 Budget tab. Then type each purchase, "
    "bill and paycheck as one row on the Transactions tab: date, what it was, category, amount. The 3 Month tab shows what is "
    "left to spend, every category against its budget, and your biggest everyday spends. The 4 Year tab lines up all twelve "
    "months.", "para")])
r = sh_card(sh, r, "Before you rely on a number", [
    (None, S.SHORT_NOTICE.format(date=CHECKED).replace("Terms of Use page", "Terms tab") + " " + S.MONEY_TIER_CLAUSE, "para"),
])
r = sh_card(sh, r, "Three steps", [
    (1, "Set your budget. On the 1 Budget tab, type a monthly budget beside each category. Rename or add categories in any group.", "num"),
    (2, "Log each purchase. On the 2 Transactions tab, one row for each money in or money out: date, what it was, category from the list, amount.", "num"),
    (3, "Read the month. On the 3 Month tab, pick the month (blank shows this month). Read Left to spend in the dark tile and check any category marked Over budget.", "num"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "How to read the cells", [
    ((550, MONEY), "Yellow cells with blue numbers are yours to type in. Each one shows a hint when you select it.", "chip-in"),
    ((3965, MONEY), "Plain numbers are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((EXM["left"], MONEY),
     "Dark tiles are your answers. The main one sits at the top of the 3 Month tab and stays on screen as you scroll.", "chip-key"),
    (None, "Nothing is locked for good: each tab is protected without a password, so you can still change anything. To edit a "
           "formula cell, use Review, Unprotect Sheet in Excel, or Data, Protect sheets and ranges in Google Sheets.", "note"),
])
ex_text = (f"Budget-Tracker-EXAMPLE.xlsx holds July to September 2026 for a made-up household, {N_TX} transactions in all. "
           f"Income is budgeted at {money(EXM['inc_b'])} a month and bills, everyday spending and savings at {money(EXM['out_b'])}. "
           f"In September {money(EXM['out_a'])} went out, so the 3 Month tab shows {money(EXM['left'])} left to spend and "
           f"{money(EXM['net'])} of money in less money out. Eating out came to {money(EXM['act']['Eating out'])} against a "
           f"$200.00 budget, so it shows Over budget. A $34.99 jacket return is typed as a minus amount under Clothing.")
r = sh_card(sh, r, "The example", [(None, ex_text, "para")])
r = sh_card(sh, r, "Which file to open", [
    (None, "Excel on a computer. Double-click Budget-Tracker.xlsx. If Excel shows a yellow Protected View bar, click Enable Editing.", "para"),
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. No macros, no add-ons, no sign-up.", "para"),
    (None, "Mac, iPad or phone. Unzip on a computer first (phones often can't open a .zip), then upload the .xlsx to Google Drive "
           "and open it in the Google Sheets app, or open it in Excel for Mac or iPad.", "para"),
    (None, "See it filled in first. Open Budget-Tracker-EXAMPLE.xlsx. Budget-Tracker.xlsx has the same category names with every "
           "amount empty and no transactions, so there is no sample data to clear.", "para"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "Good to know", [
    (None, f"Room for a busy year. The Transactions tab has {N_ROWS:,} rows and every total reads the whole column. Rows can go "
           "in any order; the date decides the month. Printing the Transactions tab prints the first 400 rows; to print "
           "more, select the rows and print the selection.", "para"),
    (None, "Refunds. Type a refund as a minus amount in the same category, for example -34.99 under Clothing.", "para"),
    (None, "Moving money between your own accounts. Leave it out, unless it is money going into savings: then log it under its "
           "savings category.", "para"),
    (None, "On a phone. Every formula is a plain sum or count with no scripts or add-ons, so the totals work in the Google Sheets app too.", "para"),
    (None, "Start a fresh copy each year. Save the file under a new name in January and clear the Transactions tab.", "para"),
])
SH_LAST = r - 1
D.paint_canvas(sh, SH_LAST, "Z")
S.finish_sheet(sh, PRODUCT, SH_LAST, span=("A", "G"), tab_color="teal",
               footer_notice="Estimates only. Not professional advice. See the Terms tab or LICENSE-AND-DISCLAIMER.txt.")

tm = wb.create_sheet("Terms")
S.set_widths(tm, SH_GRID)
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version {VERSION}. Read this before you rely on a number.", AS_OF,
              span=("B", "F"), side_cols=2)
paras = open(os.path.join(HERE, "LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().strip().split("\n\n")[1:]
r = 6
r = sh_card(tm, r, "More tools from the shop", [
    (None, ("Budget Planner Spreadsheet: plan each month by pay schedule and bill due dates", "https://www.etsy.com/listing/4592917337"), "link"),
    (None, ("Everything in the shop: etsy.com/shop/ProofNotFluff", "https://www.etsy.com/shop/ProofNotFluff"), "link"),
])
S.page_break_before(tm, r)
r = sh_card(tm, r, "Terms of Use and disclaimer", [(None, p, "para") for p in paras])
r = sh_card(tm, r, "A small ask", [
    (None, "If this tracker helps you keep your month on budget, a short review on Etsy helps other people find it. Thank you.", "para"),
    (None, "Message me on Etsy if anything doesn't open or looks wrong, and it will be fixed.", "para"),
])
TM_LAST = r - 1
D.paint_canvas(tm, TM_LAST, "Z")
S.finish_sheet(tm, PRODUCT, TM_LAST, span=("A", "G"), tab_color="note")

wb.active = 0
problems = [p for p in S.audit(wb)]
if problems:
    print("AUDIT:", *problems[:40], sep="\n  ")
wb.save(OUT)
print("saved", OUT, wb.sheetnames)
print({"budget": (CF, CL), "gsum": GSUM, "r_bout": r_bout, "r_bleft": r_bleft, "tx": (T_FIRST, T_LAST),
       "month": {"r_m": r_m, "r_y": r_y, "r_ib": r_ib, "r_ia": r_ia, "r_ob": r_ob, "r_oa": r_oa, "L_TOP": L_TOP,
                 "ltot": LTOT, "all": L_ALL, "sp": SP_ROWS}, "year": {"ytot": YTOT, "out": Y_OUT, "net": Y_NET, "o1": O1}})
print("example Sep:", {k: v for k, v in EXM.items() if k != "act"}, "n_tx:", N_TX)
print("eating out Sep:", EXM["act"]["Eating out"], "spend:", EXM["spend_a"])
