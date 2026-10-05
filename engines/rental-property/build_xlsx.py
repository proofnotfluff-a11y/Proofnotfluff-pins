#!/usr/bin/env python3
"""Builds the 1 to 10 Door Rental Property Spreadsheet (ProofNotFluff). Usage: build_xlsx.py out.xlsx [--blank]"""
import sys, datetime as dt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, Protection
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter as L

OUT = sys.argv[1]; BLANK = "--blank" in sys.argv
CHECKED = "October 5, 2026"
INK, PAPER, ACC, LINE, SOFT = "1D2433", "F5F2EC", "C8502F", "D9D3C7", "FBF9F5"
INPUT = "FFF4D6"  # pale yellow = type here
F = "Calibri"
def font(sz=11, b=False, c=INK, i=False): return Font(name=F, size=sz, bold=b, color=c, italic=i)
def fill(c): return PatternFill("solid", fgColor=c)
thin = Side(style="thin", color=LINE); box = Border(left=thin, right=thin, top=thin, bottom=thin)
MONEY = '$#,##0.00;[Red]($#,##0.00);"-"'
MONEY0 = '$#,##0;[Red]($#,##0);"-"'
NOTICE = "Estimates only. Not professional advice. See the Terms tab."
LOGMAX = 5000  # formulas read Log rows 6 to 5000, so added rows keep counting

wb = Workbook()

def title(ws, text, sub, width_cols):
    ws.sheet_view.showGridLines = False
    ws["A1"] = text; ws["A1"].font = Font(name=F, size=18, bold=True, color=INK)
    ws["A2"] = sub; ws["A2"].font = font(10, c="5A6070")
    ws["A3"] = NOTICE; ws["A3"].font = font(9, i=True, c=ACC)
    for c in range(1, width_cols + 1): ws.cell(1, c).fill = fill(PAPER); ws.cell(2, c).fill = fill(PAPER); ws.cell(3, c).fill = fill(PAPER)
    ws.row_dimensions[1].height = 30

def header(ws, row, labels, widths=None):
    for i, t in enumerate(labels, 1):
        c = ws.cell(row, i, t); c.font = font(10, True, "FFFFFF"); c.fill = fill(INK)
        c.alignment = Alignment(wrap_text=True, vertical="center"); c.border = box
    ws.row_dimensions[row].height = 32
    if widths:
        for i, w in enumerate(widths, 1): ws.column_dimensions[L(i)].width = w

# ---------------- Categories ----------------
CATS = [  # name, kind, Schedule E line, note
    ("Rent", "Income", "Line 3, Rents received", "Monthly rent you collected."),
    ("Other rental income", "Income", "Line 3, Rents received", "Late fees, pet rent, a kept deposit. Confirm with your preparer."),
    ("Advertising", "Expense", "Line 5, Advertising", "Listing sites, signs."),
    ("Auto and travel", "Expense", "Line 6, Auto and travel", "Trips to the property. The IRS instructions set the rules."),
    ("Cleaning and maintenance", "Expense", "Line 7, Cleaning and maintenance", "Turnover cleaning, lawn, snow."),
    ("Commissions", "Expense", "Line 8, Commissions", "Leasing agent commissions."),
    ("Insurance", "Expense", "Line 9, Insurance", "Landlord or rental dwelling policy."),
    ("Legal and other professional fees", "Expense", "Line 10, Legal and other professional fees", "Lease review, tax prep share."),
    ("Management fees", "Expense", "Line 11, Management fees", "Property manager."),
    ("Mortgage interest", "Expense", "Line 12, Mortgage interest paid to banks, etc.", "Interest only. Principal goes on its own row."),
    ("Other interest", "Expense", "Line 13, Other interest", "Interest on other loans for the rental."),
    ("Repairs", "Expense", "Line 14, Repairs", "Keeps the place in working order. Upgrades are improvements."),
    ("Supplies", "Expense", "Line 15, Supplies", "Light bulbs, filters, smoke detector batteries."),
    ("Taxes", "Expense", "Line 16, Taxes", "Property tax for the rental."),
    ("Utilities", "Expense", "Line 17, Utilities", "Utilities you pay, not the tenant."),
    ("Other expenses", "Expense", "Line 19, Other (list)", "Bank fees, HOA dues, software. Ask your preparer."),
    ("Mortgage principal", "Cash only", "Not an expense line", "Counts in cash flow, not in profit."),
    ("Capital improvement", "Cash only", "Not an expense line (depreciated)", "New roof, water heater. Your preparer handles depreciation."),
    ("Security deposit received", "Deposit", "Not income if you plan to return it", "Held for the tenant. IRS Pub. 527."),
    ("Security deposit returned", "Deposit", "Not an expense line", "Money you gave back."),
]
cat = wb.active; cat.title = "Categories"
title(cat, "Categories", "The list behind the Category dropdown, with the IRS Schedule E (Form 1040) Part I line each one lines up with.", 4)
header(cat, 5, ["Category", "Kind", "Schedule E line (tax year 2025 form)", "What goes here"], [32, 12, 40, 62])
for r, row in enumerate(CATS, 6):
    for c, v in enumerate(row, 1):
        x = cat.cell(r, c, v); x.font = font(10); x.border = box; x.alignment = Alignment(wrap_text=True, vertical="top")
        if r % 2: x.fill = fill(SOFT)
CAT_FIRST, CAT_LAST = 6, 6 + len(CATS) - 1
EXP_FIRST, EXP_LAST = 8, 21  # Advertising .. Other expenses
r = CAT_LAST + 2
notes = [
    "For organizing only. The line names match the 2025 Schedule E form; your tax preparer decides what goes where on your return.",
    "Line 18 (depreciation) is left out on purpose. Improvements and the building itself are depreciated over years, and that math belongs to your preparer.",
    "Sources, checked " + CHECKED + ":",
    "IRS, Schedule E (Form 1040) 2025, Part I lines 3 to 19: https://www.irs.gov/pub/irs-pdf/f1040se.pdf",
    "IRS, Instructions for Schedule E, line 14 (repairs vs. improvements): https://www.irs.gov/instructions/i1040se",
    "IRS, Publication 527 (security deposits and advance rent): https://www.irs.gov/publications/p527",
]
for t in notes:
    cat.cell(r, 1, t).font = font(9, c="5A6070"); r += 1
cat.freeze_panes = "A6"

# ---------------- Setup ----------------
st = wb.create_sheet("Setup", 0)
title(st, "Setup (step 1 of 2)", "Type your properties and doors once. Yellow cells are yours to type in. Up to 10 properties and 10 doors.", 11)
st["A5"] = "Properties"; st["A5"].font = font(12, True, ACC)
header(st, 6, ["Property name (short)", "Address or note"], None)
st["A6"].alignment = Alignment(wrap_text=True)
props = [("Maple Duplex", "Sample: 2 units, 1 mortgage"), ("Oak Street House", "Sample: single family")]
for i in range(10):
    r = 7 + i
    for c in (1, 2):
        x = st.cell(r, c); x.fill = fill(INPUT); x.border = box; x.font = font(10)
    if not BLANK and i < len(props): st.cell(r, 1, props[i][0]); st.cell(r, 2, props[i][1])
PROP_RANGE = "Setup!$A$7:$A$16"
st["D5"] = "Doors (one row per rentable unit)"; st["D5"].font = font(12, True, ACC)
dh = ["Door ID", "Property", "Tenant", "Monthly rent", "Rent due day (1 to 31)", "Grace days", "Lease end", "Deposit held"]
for i, t in enumerate(dh):
    c = st.cell(6, 4 + i, t); c.font = font(10, True, "FFFFFF"); c.fill = fill(INK); c.border = box
    c.alignment = Alignment(wrap_text=True, vertical="center")
st.row_dimensions[6].height = 32
for col, w in zip("ABCDEFGHIJK", [24, 30, 3, 13, 20, 16, 12, 13, 10, 13, 13]): st.column_dimensions[col].width = w
doors = [("MAPLE-A", "Maple Duplex", "Tenant A", 1150, 1, 5, dt.date(2027, 5, 31), 1150),
         ("MAPLE-B", "Maple Duplex", "Tenant B", 1100, 1, 5, dt.date(2026, 11, 30), 1100),
         ("OAK", "Oak Street House", "Tenant C", 1650, 1, 3, dt.date(2027, 7, 31), 1650)]
for i in range(10):
    r = 7 + i
    for c in range(4, 12):
        x = st.cell(r, c); x.fill = fill(INPUT); x.border = box; x.font = font(10)
    st.cell(r, 7).number_format = MONEY; st.cell(r, 11).number_format = MONEY; st.cell(r, 10).number_format = "mmm d, yyyy"
    if not BLANK and i < len(doors):
        for c, v in enumerate(doors[i], 4): st.cell(r, c, v)
DOOR_RANGE = "Setup!$D$7:$D$16"
dv_p = DataValidation(type="list", formula1="=" + PROP_RANGE.replace("Setup!", "Setup!"), allow_blank=True)
st.add_data_validation(dv_p); dv_p.add("E7:E16")
dv_day = DataValidation(type="whole", operator="between", formula1="1", formula2="31", allow_blank=True,
                        error="Type a day from 1 to 31.", showErrorMessage=True); st.add_data_validation(dv_day); dv_day.add("H7:H16")
st["A19"] = "Tips"; st["A19"].font = font(12, True, ACC)
tips = ["Door ID is any short name you will recognize in a dropdown, like MAPLE-A or 12-ELM.",
        "A single-family house is one property with one door. A duplex is one property with two doors.",
        "Rent due day 1 with 5 grace days means rent shows LATE from the 7th if not fully paid.",
        "Lease end shows a heads-up on the Rent Roll 60 days ahead.",
        "To start fresh: delete the sample rows here and on the Log tab (select the cells, press Delete). Every formula keeps working. Dropdowns and yellow cells cover the first 1,000 Log rows; formulas read down to row 5,000."]
for i, t in enumerate(tips): st.cell(20 + i, 1, "- " + t).font = font(10)
st.freeze_panes = "A7"

# ---------------- Log ----------------
lg = wb.create_sheet("Log", 1)
title(lg, "Log (step 2 of 2)", "Every dollar in or out, one row each. Pick the property, door and category from the dropdowns. Amounts are always positive.", 7)
header(lg, 5, ["Date", "Property", "Door (needed for rent)", "Category", "Amount", "Paid to or from", "Note"], [13, 22, 16, 30, 13, 24, 36])
lg.freeze_panes = "A6"
dv1 = DataValidation(type="list", formula1="=" + PROP_RANGE, allow_blank=True, error="Pick a property from Setup.", showErrorMessage=True)
dv2 = DataValidation(type="list", formula1="=" + DOOR_RANGE, allow_blank=True, error="Pick a door from Setup.", showErrorMessage=True)
dv3 = DataValidation(type="list", formula1=f"=Categories!$A${CAT_FIRST}:$A${CAT_LAST}", allow_blank=True, error="Pick a category from the list.", showErrorMessage=True)
dv4 = DataValidation(type="decimal", operator="greaterThanOrEqual", formula1="0", allow_blank=True, error="Amounts are positive. The category says whether money came in or went out.", showErrorMessage=True)
dv5 = DataValidation(type="date", operator="greaterThan", formula1="36526", allow_blank=True, error="Type a date, like 10/1/2026.", showErrorMessage=True)
for d in (dv1, dv2, dv3, dv4, dv5): lg.add_data_validation(d)
ROWS = 1000
dv1.add("B6:B5000"); dv2.add("C6:C5000"); dv3.add("D6:D5000"); dv4.add("E6:E5000"); dv5.add("A6:A5000")
for r in range(6, ROWS + 6):
    for c in range(1, 8):
        x = lg.cell(r, c); x.font = font(10); x.fill = fill(INPUT); x.border = Border(bottom=Side(style="hair", color=LINE))
    lg.cell(r, 1).number_format = "mm/dd/yyyy"; lg.cell(r, 5).number_format = MONEY
lg.conditional_formatting.add(f"C6:C{ROWS+5}", FormulaRule(formula=['AND($D6="Rent",$C6="")'], fill=fill("F6C9BC")))
lg.conditional_formatting.add(f"B6:B{ROWS+5}", FormulaRule(formula=['AND($E6<>"",$B6="")'], fill=fill("F6C9BC")))

log = []
if not BLANK:
    D = dt.date
    for m in range(1, 11):
        for door, prop, rent, day in (("MAPLE-A", "Maple Duplex", 1150, 1), ("MAPLE-B", "Maple Duplex", 1100, 2), ("OAK", "Oak Street House", 1650, 1)):
            if m == 10 and door == "OAK": continue           # October: not paid yet
            amt = 600 if (m == 10 and door == "MAPLE-B") else rent  # October: partial
            log.append((D(2026, m, day), prop, door, "Rent", amt, "Tenant", "Partial, rest promised Friday" if amt == 600 else ""))
    for m in range(1, 10):
        log.append((D(2026, m, 5), "Maple Duplex", "", "Mortgage interest", 612, "Lender", "From the monthly statement"))
        log.append((D(2026, m, 5), "Maple Duplex", "", "Mortgage principal", 288, "Lender", "From the monthly statement"))
        log.append((D(2026, m, 5), "Oak Street House", "", "Mortgage interest", 534, "Lender", ""))
        log.append((D(2026, m, 5), "Oak Street House", "", "Mortgage principal", 316, "Lender", ""))
        log.append((D(2026, m, 20), "Maple Duplex", "", "Utilities", 138, "City water", "Water and sewer, both units"))
    log += [
        (D(2026, 3, 2), "Maple Duplex", "", "Insurance", 1380, "Insurer", "Annual landlord policy"),
        (D(2026, 6, 1), "Oak Street House", "", "Insurance", 1140, "Insurer", "Annual landlord policy"),
        (D(2026, 6, 15), "Maple Duplex", "", "Taxes", 2140, "County treasurer", "First installment"),
        (D(2026, 9, 14), "Maple Duplex", "", "Taxes", 2140, "County treasurer", "Second installment"),
        (D(2026, 6, 15), "Oak Street House", "", "Taxes", 1860, "County treasurer", "First installment"),
        (D(2026, 9, 14), "Oak Street House", "", "Taxes", 1860, "County treasurer", "Second installment"),
        (D(2026, 2, 11), "Maple Duplex", "MAPLE-B", "Repairs", 185, "Plumber", "Kitchen drain"),
        (D(2026, 4, 22), "Oak Street House", "OAK", "Repairs", 240, "Handyman", "Back door lock and frame"),
        (D(2026, 7, 9), "Oak Street House", "OAK", "Capital improvement", 1450, "Plumber", "New water heater"),
        (D(2026, 5, 3), "Maple Duplex", "", "Cleaning and maintenance", 320, "Lawn service", "Spring cleanup"),
        (D(2026, 8, 3), "Maple Duplex", "", "Cleaning and maintenance", 160, "Lawn service", "Summer mowing"),
        (D(2026, 3, 18), "Oak Street House", "OAK", "Supplies", 62, "Hardware store", "Filters and smoke detector batteries"),
        (D(2026, 1, 30), "Maple Duplex", "", "Legal and other professional fees", 250, "Tax preparer", "Rental share of prep fee"),
        (D(2026, 4, 8), "Oak Street House", "", "Auto and travel", 38, "", "Trips to the property, see IRS rules"),
        (D(2026, 9, 2), "Maple Duplex", "MAPLE-A", "Other rental income", 50, "Tenant", "Pet rent, September"),
    ]
    log.sort(key=lambda x: x[0])
    for i, row in enumerate(log):
        for c, v in enumerate(row, 1):
            if v != "": lg.cell(6 + i, c, v)

def rng(col): return f"Log!${col}$6:${col}${LOGMAX}"
A, B, C, Dd, E = rng("A"), rng("B"), rng("C"), rng("D"), rng("E")
EXPLIST = f"Categories!$A${EXP_FIRST}:$A${EXP_LAST}"

# ---------------- Rent Roll ----------------
rr = wb.create_sheet("Rent Roll", 2)
title(rr, "Rent Roll", "Who has paid this month. Change the month in the yellow cell. LATE uses today's date, your due day and grace days.", 10)
rr["A5"] = "Month to check (type any date in the month):"; rr["A5"].font = font(11, True)
rr["E5"] = dt.date(2026, 10, 1) if not BLANK else None
if BLANK: rr["E5"] = "=DATE(YEAR(TODAY()),MONTH(TODAY()),1)"
rr["E5"].number_format = "mmmm yyyy"; rr["E5"].fill = fill(INPUT); rr["E5"].border = box; rr["E5"].font = font(12, True)
rr["F5"] = "Today:"; rr["F5"].font = font(10, c="5A6070"); rr["F5"].alignment = Alignment(horizontal="right")
rr["G5"] = "=TODAY()"; rr["G5"].number_format = "mmm d, yyyy"; rr["G5"].font = font(10, c="5A6070")
header(rr, 7, ["Door", "Property", "Tenant", "Rent due", "Received this month", "Still owed", "Due date", "Status", "Lease", "Deposit held"],
       [12, 20, 13, 12, 14, 12, 13, 11, 22, 13])
MS = "DATE(YEAR($E$5),MONTH($E$5),1)"; ME = "EOMONTH($E$5,0)"
for i in range(10):
    r = 8 + i; s = 7 + i
    f = {
        1: f'=IF(Setup!$D${s}="","",Setup!$D${s})',
        2: f'=IF($A{r}="","",Setup!$E${s})',
        3: f'=IF($A{r}="","",Setup!$F${s})',
        4: f'=IF($A{r}="","",N(Setup!$G${s}))',
        5: f'=IF($A{r}="","",SUMIFS({E},{C},$A{r},{Dd},Categories!$A$6,{A},">="&{MS},{A},"<="&{ME}))',
        6: f'=IF($A{r}="","",MAX(0,D{r}-E{r}))',
        7: f'=IF($A{r}="","",DATE(YEAR($E$5),MONTH($E$5),MIN(MAX(1,N(Setup!$H${s})),DAY({ME}))))',
        8: f'=IF($A{r}="","",IF(F{r}<=0,"Paid",IF(TODAY()>G{r}+N(Setup!$I${s}),"LATE",IF(E{r}>0,"Partial","Due"))))',
        9: f'=IF(OR($A{r}="",Setup!$J${s}=""),"",IF(Setup!$J${s}<TODAY(),"Lease ended",IF(Setup!$J${s}-TODAY()<=60,"Ends in "&(Setup!$J${s}-TODAY())&" days","Ends "&TEXT(Setup!$J${s},"mmm d, yyyy"))))',
        10: f'=IF($A{r}="","",N(Setup!$K${s}))',
    }
    for c, v in f.items():
        x = rr.cell(r, c, v); x.font = font(10); x.border = box
    for c in (4, 5, 6, 10): rr.cell(r, c).number_format = MONEY
    rr.cell(r, 7).number_format = "mmm d"
    rr.cell(r, 8).font = font(10, True); rr.cell(r, 8).alignment = Alignment(horizontal="center")
rr.conditional_formatting.add("H8:H17", FormulaRule(formula=['$H8="LATE"'], fill=fill(ACC), font=Font(name=F, color="FFFFFF", bold=True)))
rr.conditional_formatting.add("H8:H17", FormulaRule(formula=['$H8="Paid"'], fill=fill("DCEBDD")))
rr.conditional_formatting.add("H8:H17", FormulaRule(formula=['$H8="Partial"'], fill=fill("FBE3B0")))
rr.conditional_formatting.add("I8:I17", FormulaRule(formula=['LEFT($I8,7)="Ends in"'], font=Font(name=F, color=ACC, bold=True)))
rr["A18"] = "Totals"; rr["A18"].font = font(10, True)
for c, col in ((4, "D"), (5, "E"), (6, "F"), (10, "J")):
    x = rr.cell(18, c, f"=SUM({col}8:{col}17)"); x.number_format = MONEY; x.font = font(10, True); x.border = Border(top=Side(style="medium", color=INK))
rr["A20"] = '=IF(COUNTIF(H8:H17,"LATE")=0,"No late rent for this month.",COUNTIF(H8:H17,"LATE")&" door(s) LATE. Total still owed this month: "&TEXT(F18,"$#,##0.00"))'
rr["A20"].font = font(12, True, ACC)
rr["A22"] = "Rent counts only when the Log row has the Rent category and a Door picked. Partial payments add up. Late fees go under Other rental income."
rr["A22"].font = font(9, c="5A6070")
rr.freeze_panes = "A8"

# ---------------- Property P&L ----------------
pl = wb.create_sheet("Property P&L", 3)
title(pl, "Property P&L and Cash Flow", "One column per property for the year in the yellow cell. Fills itself from the Log.", 15)
pl["A5"] = "Year:"; pl["A5"].font = font(11, True)
pl["B5"] = 2026 if not BLANK else "=YEAR(TODAY())"
pl["B5"].fill = fill(INPUT); pl["B5"].border = box; pl["B5"].font = font(12, True); pl["B5"].number_format = "0"; pl["B5"].alignment = Alignment(horizontal="left")
pl["D5"] = "Check one property:"; pl["D5"].font = font(11, True); pl["D5"].alignment = Alignment(horizontal="right")
pl["E5"] = "Maple Duplex" if not BLANK else None
pl["E5"].fill = fill(INPUT); pl["E5"].border = box; pl["E5"].font = font(11, True)
dvy = DataValidation(type="whole", operator="between", formula1="2000", formula2="2100", error="Type a four-digit year.", showErrorMessage=True); pl.add_data_validation(dvy); dvy.add("B5")
dvp = DataValidation(type="list", formula1="=" + PROP_RANGE, allow_blank=True); pl.add_data_validation(dvp); dvp.add("E5")
YS, YE = "DATE($B$5,1,1)", "DATE($B$5,12,31)"
pl.cell(7, 1, "Category").font = font(10, True, "FFFFFF")
pl.cell(7, 2, "Schedule E line").font = font(10, True, "FFFFFF")
for c in range(1, 15):
    pl.cell(7, c).fill = fill(INK); pl.cell(7, c).border = box; pl.cell(7, c).alignment = Alignment(wrap_text=True, vertical="center")
pl.row_dimensions[7].height = 34
for i in range(10):
    c = 3 + i
    x = pl.cell(7, c, f'=IF(Setup!$A${7+i}="","",Setup!$A${7+i})'); x.font = font(10, True, "FFFFFF")
x = pl.cell(7, 13, "All properties"); x.font = font(10, True, "FFFFFF")
x = pl.cell(7, 14, '=IF($E$5="","Selected property",$E$5)'); x.font = font(10, True, ACC); x.fill = fill(INK)
pl.column_dimensions["A"].width = 32; pl.column_dimensions["B"].width = 44
for c in range(3, 15): pl.column_dimensions[L(c)].width = 13
pl.column_dimensions["M"].width = 14; pl.column_dimensions["N"].width = 16

def sumcat(catcell, col):
    return f'=IF({col}$7="",0,SUMIFS({E},{B},{col}$7,{Dd},{catcell},{A},">="&{YS},{A},"<="&{YE}))'
row = 8
def section(label):
    global row
    x = pl.cell(row, 1, label); x.font = font(10, True, ACC); row += 1
def line(label, eline, formula_for_col, bold=False, top=False, fmt=MONEY):
    global row
    pl.cell(row, 1, label).font = font(10, bold); pl.cell(row, 2, eline).font = font(9, c="5A6070")
    for c in range(3, 13):
        col = L(c); x = pl.cell(row, c, formula_for_col(col)); x.number_format = fmt; x.font = font(10, bold)
    x = pl.cell(row, 13, f"=SUM(C{row}:L{row})"); x.number_format = fmt; x.font = font(10, True)
    x = pl.cell(row, 14, f'=SUMIF($C$7:$L$7,$E$5,C{row}:L{row})'); x.number_format = fmt; x.font = font(10, True); x.fill = fill(SOFT)
    for c in range(1, 15):
        pl.cell(row, c).border = Border(bottom=Side(style="hair", color=LINE), top=Side(style="medium", color=INK) if top else None)
    row += 1; return row - 1
section("Money in")
inc_rows = []
for k in (6, 7):
    inc_rows.append(line(CATS[k-6][0], CATS[k-6][2], lambda col, k=k: sumcat(f"Categories!$A${k}", col)))
r_inc = line("Total money in", "Line 3", lambda col: f"=SUM({col}{inc_rows[0]}:{col}{inc_rows[-1]})", True, True)
section("Expenses (Schedule E lines)")
exp_rows = []
for k in range(EXP_FIRST, EXP_LAST + 1):
    exp_rows.append(line(CATS[k-6][0], CATS[k-6][2], lambda col, k=k: sumcat(f"Categories!$A${k}", col)))
r_exp = line("Total expenses", "Lines 5 to 19 added", lambda col: f"=SUM({col}{exp_rows[0]}:{col}{exp_rows[-1]})", True, True)
r_net = line("Profit before depreciation", "Line 3 minus expenses", lambda col: f"={col}{r_inc}-{col}{r_exp}", True, True)
section("Cash items (not expenses)")
r_pr = line("Mortgage principal", "Not on Schedule E", lambda col: sumcat("Categories!$A$22", col))
r_ci = line("Capital improvement", "Depreciated, ask your preparer", lambda col: sumcat("Categories!$A$23", col))
r_cf = line("Cash flow (what you kept)", "Profit minus principal and improvements", lambda col: f"={col}{r_net}-{col}{r_pr}-{col}{r_ci}", True, True)
section("Deposits (held for tenants)")
r_dr = line("Security deposits received", "Not income if you plan to return it", lambda col: sumcat("Categories!$A$24", col))
r_dt = line("Security deposits returned", "", lambda col: sumcat("Categories!$A$25", col))
row += 1
pl.cell(row, 1, "Unlabeled rows:").font = font(9, True, c="5A6070")
pl.cell(row, 2, f'=COUNTIFS({E},">0",{B},"")+COUNTIFS({E},">0",{Dd},"")').font = font(9, True, c=ACC)
pl.cell(row, 3, "Log rows with an amount but no property or no category are not counted anywhere. Fix any shown here.").font = font(9, c="5A6070")
row += 1
pl.cell(row, 1, "Profit here is before depreciation (Schedule E line 18), which your preparer works out. For organizing, not a tax return.").font = font(9, c="5A6070")
pl.freeze_panes = "C8"
for rr_ in (r_net, r_cf):
    pl.conditional_formatting.add(f"C{rr_}:N{rr_}", FormulaRule(formula=[f"C{rr_}<0"], font=Font(name=F, color=ACC, bold=True)))

# ---------------- Monthly ----------------
mo = wb.create_sheet("Monthly", 4)
title(mo, "Monthly Summary", "Month by month for the year on the Property P&L tab. Pick one property or leave it on All.", 14)
mo["A5"] = "Show:"; mo["A5"].font = font(11, True)
mo["B5"] = "All properties"; mo["B5"].fill = fill(INPUT); mo["B5"].border = box; mo["B5"].font = font(11, True)
mo["D5"] = "Year:"; mo["D5"].font = font(10, c="5A6070"); mo["E5"] = "='Property P&L'!$B$5"; mo["E5"].number_format = "0"; mo["E5"].font = font(11, True)
mo["F5"] = "(change it on the Property P&L tab)"; mo["F5"].font = font(9, c="5A6070")
# dropdown: All properties + property list. Use the property range; "All properties" typed as default is allowed (allow free text by not erroring)
dvm = DataValidation(type="list", formula1="=" + PROP_RANGE, allow_blank=True, showErrorMessage=False); mo.add_data_validation(dvm); dvm.add("B5")
mo["B6"] = 'Clear this cell or type "All properties" to see everything.'; mo["B6"].font = font(8, c="5A6070")
PC = 'IF(OR($B$5="",$B$5="All properties"),"*",$B$5)'
header(mo, 8, ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Year"], [30] + [11] * 12 + [13])
def msum(cats_expr, m, arr=False):
    s, e = f"DATE($E$5,{m},1)", f"EOMONTH(DATE($E$5,{m},1),0)"
    if arr: return f"SUMPRODUCT(SUMIFS({E},{Dd},{cats_expr},{B},{PC},{A},\">=\"&{s},{A},\"<=\"&{e}))"
    return f"SUMIFS({E},{Dd},{cats_expr},{B},{PC},{A},\">=\"&{s},{A},\"<=\"&{e})"
rows = [
    ("Money in", lambda m: f"={msum('Categories!$A$6:$A$7', m, True)}"),
    ("Expenses", lambda m: f"={msum(EXPLIST, m, True)}"),
    ("Profit before depreciation", lambda m: f"={L(m+1)}9-{L(m+1)}10"),
    ("Principal and improvements", lambda m: f"={msum('Categories!$A$22:$A$23', m, True)}"),
    ("Cash flow", lambda m: f"={L(m+1)}11-{L(m+1)}12"),
    ("Running cash flow", lambda m: f"={L(m+1)}13" if m == 1 else f"={L(m)}14+{L(m+1)}13"),
]
for i, (lab, fn) in enumerate(rows):
    r = 9 + i; bold = lab in ("Profit before depreciation", "Cash flow")
    mo.cell(r, 1, lab).font = font(10, bold)
    for m in range(1, 13):
        x = mo.cell(r, m + 1, fn(m)); x.number_format = MONEY0; x.font = font(10, bold); x.border = Border(bottom=Side(style="hair", color=LINE))
    if lab != "Running cash flow":
        x = mo.cell(r, 14, f"=SUM(B{r}:M{r})"); x.number_format = MONEY0; x.font = font(10, True)
    else:
        x = mo.cell(r, 14, "=M14"); x.number_format = MONEY0; x.font = font(10, True)
    mo.cell(r, 1).border = Border(bottom=Side(style="hair", color=LINE))
mo.conditional_formatting.add("B9:N14", FormulaRule(formula=["B9<0"], font=Font(name=F, color=ACC, bold=True)))
mo["A16"] = "Months after today show 0 until you log them. Deposits are left out because they belong to the tenant."
mo["A16"].font = font(9, c="5A6070")
mo.freeze_panes = "B9"

# ---------------- Start Here ----------------
sh = wb.create_sheet("Start Here", 0)
sh.sheet_view.showGridLines = False
sh.column_dimensions["A"].width = 3; sh.column_dimensions["B"].width = 92
for r in range(1, 50):
    for c in (1, 2, 3): sh.cell(r, c).fill = fill(PAPER)
lines = [
    ("Rental Property Spreadsheet for 1 to 10 Doors", 20, True, INK),
    ("ProofNotFluff | Version 1, " + CHECKED, 10, False, "5A6070"),
    ("", 6, False, INK),
    ("For general information and planning only. This is not legal, tax, financial, medical or other professional advice, and using it doesn't create a professional relationship. Results are estimates based on the numbers you enter. Figures were checked on " + CHECKED + " and can change. See the Terms tab before you rely on anything here.", 9, False, ACC),
    ("Calculations are estimates for planning and depend on your inputs. They aren't accounting, tax or financial advice. Check fees, rates and interest against your own statements and the provider's current terms.", 9, False, ACC),
    ("", 6, False, INK),
    ("Which file to open", 13, True, ACC),
    ("Computer with Excel: double-click the .xlsx file. Computer without Excel: go to sheets.google.com, open a blank sheet, then File > Import > Upload, pick the .xlsx and choose Replace spreadsheet. It uses only functions Google Sheets supports.", 11, False, INK),
    ("Phone: the Etsy app can't download files. Sign in at etsy.com in your phone's browser, go to Your account > Purchases > Download Files, save the zip to your Files app, tap it to unzip, then open the .xlsx in the free Excel or Google Sheets app. Setup is easier on a computer.", 11, False, INK),
    ("", 6, False, INK),
    ("Five-minute setup", 13, True, ACC),
    ("1. Setup tab: type each property once (a short name), then one row per door with rent, due day, grace days, lease end and deposit.", 11, False, INK),
    ("2. Log tab: one row per payment or bill. Pick property, door (needed for rent) and category from the dropdowns. Amounts are always positive.", 11, False, INK),
    ("3. Rent Roll tab: type the month you want to check. Each door shows Paid, Partial, Due or LATE, plus leases ending within 60 days.", 11, False, INK),
    ("4. Property P&L tab: type the year. One column per property, expenses on the IRS Schedule E line names, profit and cash flow.", 11, False, INK),
    ("5. Monthly tab: money in, expenses and cash flow by month, for all properties or one.", 11, False, INK),
    ("", 6, False, INK),
    ("The sample data", 13, True, ACC),
    ("The file opens with a worked example: a duplex and a single-family house, January to October 2026. On the Rent Roll for October, one door is Paid, one paid $600 of $1,100, and one has paid nothing. Status and the lease countdown use today's date, so both unpaid sample doors may show LATE when you open it. To start fresh, delete the sample rows on Setup and Log. Every formula keeps working on a blank file.", 11, False, INK),
    ("", 6, False, INK),
    ("Good to know", 13, True, ACC),
    ("Yellow cells, including every row of the Log, are for typing. White cells on Rent Roll, Property P&L and Monthly are formulas and are locked so they can't be typed over by accident (Review > Unprotect Sheet if you want to change them; no password).", 11, False, INK),
    ("Formulas read Log rows down to row 5,000, so keep adding rows below the last one. Sorting the Log by date is fine.", 11, False, INK),
    ("Mortgage interest is an expense. Principal and capital improvements are not expenses; they lower cash flow only. Depreciation (Schedule E line 18) is left to your tax preparer.", 11, False, INK),
    ("Security deposits are tracked on their own rows and left out of income. IRS Publication 527: don't include a deposit in income if you plan to return it.", 11, False, INK),
    ("", 6, False, INK),
    ("Tabs: Start Here, Setup, Log, Rent Roll, Property P&L, Monthly, Categories, Terms, Thank You.", 10, False, "5A6070"),
]
for i, (t, sz, b, c) in enumerate(lines, 2):
    x = sh.cell(i, 2, t); x.font = Font(name=F, size=sz, bold=b, color=c); x.alignment = Alignment(wrap_text=True, vertical="top")
    if len(t) > 85: sh.row_dimensions[i].height = 15.5 * (len(t) // 80 + 1) * (sz / 11)

# ---------------- Terms ----------------
tm = wb.create_sheet("Terms")
tm.sheet_view.showGridLines = False; tm.column_dimensions["A"].width = 110
TERMS = open(sys.path[0] + "/LICENSE-AND-DISCLAIMER.txt", encoding="utf-8").read().split("\n")
for i, t in enumerate(TERMS, 1):
    x = tm.cell(i, 1, t); x.alignment = Alignment(wrap_text=True, vertical="top")
    x.font = font(14 if i == 1 else 10, i <= 2)
    if len(t) > 110: tm.row_dimensions[i].height = 14 * (len(t) // 105 + 1)

# ---------------- Thank you ----------------
ty = wb.create_sheet("Thank You")
ty.sheet_view.showGridLines = False; ty.column_dimensions["A"].width = 3; ty.column_dimensions["B"].width = 90
for r in range(1, 12):
    for c in (1, 2, 3): ty.cell(r, c).fill = fill(PAPER)
ty["B2"] = "Thank you for buying from ProofNotFluff"; ty["B2"].font = Font(name=F, size=16, bold=True, color=INK)
ty["B4"] = "If this spreadsheet helps you keep track of your rentals, a short review on Etsy helps other landlords find it."
ty["B5"] = "Message me on Etsy if anything doesn't open or a formula looks wrong, and I'll fix it."
for c in ("B4", "B5"): ty[c].font = font(11); ty[c].alignment = Alignment(wrap_text=True)

# protection on formula tabs (no password); input cells unlocked
for ws, inputs in ((rr, ["E5"]), (pl, ["B5", "E5"]), (mo, ["B5"])):
    for c in inputs: ws[c].protection = Protection(locked=False)
    ws.protection.sheet = True
    ws.protection.formatCells = False; ws.protection.formatColumns = False; ws.protection.formatRows = False

for ws in wb.worksheets:
    ws.oddFooter.center.text = "Estimates only. Not professional advice. ProofNotFluff"
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
wb.properties.creator = "ProofNotFluff"; wb.properties.lastModifiedBy = "ProofNotFluff"; wb.properties.company = None
wb.properties.title = "Rental Property Spreadsheet for 1 to 10 Doors"
wb.active = 0
wb.save(OUT)
print("saved", OUT, "log rows", len(log))
