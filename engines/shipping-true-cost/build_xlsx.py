#!/usr/bin/env python3
"""#7 Shipping True-Cost Calculator, version 3 (dashboard design, Oct 7, 2026).

Same inputs, rate tables, formulas and sample shop as version 1 (Sep 29, 2026), rebuilt to
design/WORKBOOK_STANDARD.md section 0. tools/compare_xlsx.py with compare_map.json proves the
answers match. Changes in v3, each declared in the compare map:
  - a product row with a blank zone no longer reads a whole rate row (v1 fed zone 0 to INDEX);
    it now waits for a zone, like any other missing input;
  - picking "Your quote A" or "Your quote B" with no quote typed no longer counts postage as
    $0 (v1 then called the row covered); it now says "Enter postage";
  - status words in sentence case ("Under-recovered", not "UNDER-RECOVERED");
  - new: an optional switch adds the USPS temporary holiday prices (Oct 4, 2026 to
    Jan 17, 2027) to the three USPS columns. It ships set to "No", so every v1 answer holds;
  - the dimension-rounding note now says what each carrier publishes (v1 said every carrier
    rounds up; USPS and FedEx say nearest inch);
  - the Dashboard chart is replaced by stat tiles (standard section 12);
  - every tab protected without a password; full Terms of Use tab.

Usage: python3 engines/shipping-true-cost/build_xlsx.py out.xlsx
"""
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

PRODUCT = "Shipping True-Cost Calculator"
VERSION = "3"
CHECKED = "Oct 7, 2026"
AS_OF = f"Figures checked {CHECKED}"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "Shipping-True-Cost-Calculator.xlsx"
USD0, USD2, PCT, INT, NUM1 = (S.FMT[k] for k in ("usd0", "usd2", "pct", "int", "num1"))
PCT1 = "0.0%"
NUM2 = "#,##0.00"
LB = '#,##0.0# "lb"'
N = 30  # product rows
TROW = 17  # product table rows: 30 rows and the header print on one landscape page

# ---------------------------------------------------------------- sample shop (v1, unchanged)
# name, sale price, shipping charged, zone, service, box, filler, tape, label, packing minutes
PRODUCTS = [
    ("Ceramic Mug 12 oz", 19, 4.95, 5, "Cheapest", 0.85, 0.45, 0.08, 0.06, 6),
    ("Graphic T-Shirt", 28, 4.95, 3, "Cheapest", 0.22, 0, 0, 0.06, 3),
    ("Framed Print 11x14", 65, 12, 6, "Cheapest", 2.4, 1.1, 0.15, 0.06, 12),
    ("Sterling Silver Earrings", 42, 0, 8, "Cheapest", 0.3, 0.1, 0, 0.06, 3),
    ("Soy Candle 8 oz", 22, 8.95, 4, "Cheapest", 0.7, 0.4, 0.08, 0.06, 5),
    ("Grapevine Wreath 16 in", 58, 14.95, 5, "Cheapest", 3.2, 0.6, 0.2, 0.06, 10),
    ("Canvas Tote Bag", 30, 6.95, 2, "Cheapest", 0.25, 0, 0, 0.06, 3),
    ("Handmade Soap Set (3)", 26, 9.95, 5, "Cheapest", 0.55, 0.2, 0.05, 0.06, 4),
    ("Wooden Puzzle", 34, 12.95, 4, "Cheapest", 0.95, 0.3, 0.08, 0.06, 5),
    ("Board Game", 48, 17.95, 5, "Cheapest", 1.4, 0.35, 0.1, 0.06, 7),
]
DIMS = [(8, 6, 6, 18), (10, 13, 1, 7), (18, 14, 3, 52), (6, 9, 1, 2), (6, 6, 6, 20), (16, 16, 8, 40),
        (12, 15, 1, 9), (7, 5, 3, 14), (10, 8, 2, 30), (12, 12, 3, 60)]
FEES = [(0.095, 8.5), (0.095, 12), (0.095, 22), (0.095, 11), (0.095, 5.6), (0.095, 18), (0.095, 9.5),
        (0.095, 6), (0.095, 9), (0.095, 16)]
SERVICES = ["Cheapest", "USPS GA Commercial", "USPS GA Retail", "USPS Priority Commercial", "UPS Ground Saver",
            "Your quote A", "Your quote B"]
HOURLY = 18
USPS_DIV, USPS_THRESH, UPS_DIV = 139, 1728, 139
UPS_FUEL = 0.295
FIXED_FEE = 0.45
FS = dict(aov=48, ship=6.5, margin=0.45, lift=0.15, thresholds=(35, 50, 75), shares=(0.55, 0.3, 0.12), avg=(50, 64, 92))
# USPS temporary holiday price increases, Oct 4, 2026 to Jan 17, 2027 (USPS news release Aug 25, 2026):
# rows 0-3 lb, 4-10 lb, 11-25 lb; columns GA commercial z1-4, z5-9, GA retail z1-4, z5-9, Priority commercial z1-4, z5-9
HOLIDAY = [("Up to 3 lb", 0.40, 0.55, 0.50, 0.75, 0.40, 0.85),
           ("4 to 10 lb", 0.65, 1.05, 0.80, 1.40, 0.65, 1.75),
           ("11 to 25 lb", 1.05, 1.75, 1.25, 2.75, 1.05, 3.85)]

# Rate tables (USPS Notice 123 effective July 12, 2026; UPS Ground Saver 2026 daily rates, Dec 22, 2025)
GA_COM = [(0, "Under 1 lb", [6.93, 6.94, 7.3, 7.46, 7.69, 7.86, 8.07, 8.4, 8.4]),
          (1, "1 lb", [7.61, 7.68, 8, 8.15, 8.74, 9.63, 9.98, 10.67, 10.67]),
          (2, "2 lb", [7.99, 8.08, 8.26, 8.51, 9.95, 11.58, 12, 12.87, 12.87]),
          (3, "3 lb", [8.64, 8.66, 9.14, 9.67, 11.57, 13.59, 14.36, 15.75, 15.75]),
          (4, "4 lb", [9.28, 9.34, 9.7, 10.65, 12.84, 15.16, 16.19, 18.01, 18.01]),
          (5, "5 lb", [9.7, 9.76, 10.14, 11.02, 13.48, 15.89, 17.12, 19.19, 19.19]),
          (6, "6 lb", [9.87, 9.94, 10.36, 11.55, 14.28, 16.89, 18.31, 20.68, 20.68]),
          (7, "7 lb", [9.96, 10.02, 10.62, 11.9, 14.9, 17.65, 19.23, 21.83, 21.83]),
          (8, "8 lb", [10.1, 10.27, 11.49, 12.43, 15.49, 18.34, 20.08, 22.9, 22.9]),
          (9, "9 lb", [11.01, 11.25, 12.39, 13.65, 16.11, 19.13, 21.01, 24.09, 24.09]),
          (10, "10 lb", [11.91, 12.26, 13.18, 14.44, 16.76, 19.94, 21.97, 25.34, 25.34]),
          (11, "11 lb", [12.75, 12.94, 14, 15.18, 18.12, 21.28, 23.68, 27.37, 27.37]),
          (12, "12 lb", [13.49, 13.85, 14.63, 15.89, 18.86, 22.2, 24.78, 28.73, 28.73]),
          (13, "13 lb", [14.15, 14.48, 15.25, 16.53, 19.62, 23.16, 25.87, 30.11, 30.11]),
          (14, "14 lb", [14.73, 15.07, 15.81, 17.13, 20.38, 24.14, 26.99, 31.53, 31.53]),
          (15, "15 lb", [15.23, 15.53, 16.31, 17.67, 21.15, 25.13, 28.11, 32.91, 32.91]),
          (16, "16 lb", [15.64, 15.91, 16.73, 17.94, 21.89, 26.09, 29.22, 34.29, 34.29]),
          (17, "17 lb", [15.97, 16.29, 17.15, 18.41, 22.51, 26.85, 30.11, 35.42, 35.42]),
          (18, "18 lb", [16.21, 16.46, 17.61, 18.94, 23.16, 27.7, 31.09, 36.64, 36.64]),
          (19, "19 lb", [16.38, 16.82, 17.81, 19.36, 23.79, 28.52, 32.07, 37.84, 37.84]),
          (20, "20 lb", [16.46, 17.06, 18.03, 19.66, 24.93, 30.32, 34.67, 40.39, 40.39])]
GA_RET = [(0.5, "1 to 8 oz", [7.9, 8.05, 8.15, 8.3, 8.6, 8.75, 8.95, 9.45, 9.45]),
          (0.99, "9 to 15.99 oz", [9.55, 9.95, 10.2, 10.6, 10.95, 11.35, 11.95, 12.9, 12.9]),
          (1, "1 lb", [9.55, 9.95, 10.2, 10.6, 10.95, 11.35, 11.95, 12.9, 12.9]),
          (2, "2 lb", [10.8, 11.5, 12.2, 13, 14.1, 15.1, 16.45, 19.05, 19.05]),
          (3, "3 lb", [11.3, 12, 12.65, 13.7, 14.95, 16.45, 18.95, 22.4, 22.4]),
          (4, "4 lb", [12.25, 12.75, 13.65, 14.85, 16.4, 18.3, 20.9, 24.25, 24.25]),
          (5, "5 lb", [12.95, 13.55, 14.55, 15.8, 17.45, 19.6, 22.4, 26.05, 26.05]),
          (6, "6 lb", [13.5, 13.9, 14.85, 16.35, 18.4, 21.05, 24.35, 28.35, 28.35]),
          (7, "7 lb", [14, 14.4, 15.4, 17.1, 19.45, 22.55, 26.25, 30.6, 30.6]),
          (8, "8 lb", [14.6, 14.85, 15.8, 17.65, 20.4, 24.1, 28.45, 33.15, 33.15]),
          (9, "9 lb", [15.1, 15.4, 16.25, 18.3, 21.4, 25.55, 30.75, 35.7, 35.7]),
          (10, "10 lb", [15.95, 16.3, 17.25, 19.4, 22.85, 27.5, 33.3, 39.45, 39.45]),
          (11, "11 lb", [16.75, 17.3, 18.15, 20.4, 24.2, 29.45, 35.95, 43.3, 43.3]),
          (12, "12 lb", [17.45, 17.85, 18.65, 21.3, 25.4, 31.25, 38.65, 46.5, 46.5]),
          (13, "13 lb", [18.2, 18.5, 19.15, 21.75, 26.4, 33.1, 41.7, 51, 51]),
          (14, "14 lb", [18.95, 19.05, 19.65, 22.55, 27.8, 35.25, 44.8, 54.9, 54.9]),
          (15, "15 lb", [19.65, 19.75, 20.4, 23.2, 28.95, 36.75, 46.65, 57.35, 57.35]),
          (16, "16 lb", [20.4, 20.55, 21.2, 24.3, 30.2, 38.25, 48.5, 59.9, 59.9]),
          (17, "17 lb", [21.15, 21.4, 21.9, 25.4, 31.45, 39.95, 50.8, 62.85, 62.85]),
          (18, "18 lb", [21.85, 22.1, 22.65, 25.95, 32.8, 41.75, 53.15, 65.85, 65.85]),
          (19, "19 lb", [22.3, 22.55, 23.6, 26.4, 33.8, 42.8, 54.1, 68, 68]),
          (20, "20 lb", [22.75, 22.95, 24.45, 27.3, 35.15, 44.25, 55.5, 69.4, 69.4])]
PRI_COM = [(1, "1 lb", [9.04, 9.32, 9.71, 10.4, 12.97, 14.47, 15.08, 15.22, 32.48]),
           (2, "2 lb", [9.1, 9.39, 9.78, 10.79, 13.17, 15.34, 16.31, 16.37, 34.94]),
           (3, "3 lb", [9.45, 9.71, 10.75, 12.68, 16.56, 18.86, 20.51, 20.57, 43.91]),
           (4, "4 lb", [10.97, 11.22, 12.52, 14.96, 19.88, 24.51, 26.76, 26.82, 57.23]),
           (5, "5 lb", [11.39, 11.56, 13.02, 15.72, 21.52, 26.35, 29.1, 29.18, 62.27]),
           (6, "6 lb", [11.77, 11.84, 13.44, 16.46, 23.07, 28.16, 31.35, 31.9, 68.08]),
           (7, "7 lb", [12.19, 12.38, 13.96, 17.46, 24.89, 30.28, 33.99, 34.97, 74.63]),
           (8, "8 lb", [12.48, 12.6, 14.91, 17.97, 25.91, 31.5, 35.6, 37.15, 79.28]),
           (9, "9 lb", [13.5, 13.63, 15.84, 18.78, 26.84, 32.63, 37.1, 39.25, 83.75]),
           (10, "10 lb", [14.5, 14.63, 16.66, 19.62, 27.78, 33.74, 38.57, 41.28, 88.1]),
           (11, "11 lb", [15.43, 15.56, 17.52, 20.43, 29.45, 35.4, 40.78, 44.05, 94.01]),
           (12, "12 lb", [16.28, 16.39, 18.21, 21.25, 30.62, 36.76, 42.54, 46.25, 98.69]),
           (13, "13 lb", [17.03, 17.15, 18.93, 22.1, 31.99, 38.3, 44.45, 48.54, 103.58]),
           (14, "14 lb", [17.74, 17.87, 19.65, 22.96, 33.51, 40.02, 46.59, 51, 108.83]),
           (15, "15 lb", [18.39, 18.52, 20.37, 23.91, 35.25, 41.99, 48.97, 53.6, 114.39]),
           (16, "16 lb", [19.01, 19.13, 21.1, 24.68, 37.23, 44.19, 51.61, 56.4, 120.37]),
           (17, "17 lb", [19.56, 19.69, 21.93, 25.82, 39.36, 46.5, 54.4, 59.22, 126.38]),
           (18, "18 lb", [20.09, 20.21, 22.93, 27.17, 41.89, 49.26, 57.68, 62.42, 133.22]),
           (19, "19 lb", [20.36, 20.48, 23.19, 27.75, 43.03, 50.58, 59.36, 64.47, 137.58]),
           (20, "20 lb", [20.56, 20.69, 23.54, 28.29, 44.81, 53.02, 62.83, 68.06, 145.25])]
UPS_GS = [(1, "1 lb", [13, 13, 13.51, 14.68, 15.31, 15.82, 15.99, 16.26]),
          (2, "2 lb", [13.99, 13.99, 15.37, 16.71, 17.07, 17.78, 18.43, 18.73]),
          (3, "3 lb", [14.54, 14.54, 16.14, 17.42, 18.27, 19.01, 19.62, 20.56]),
          (4, "4 lb", [14.94, 14.94, 16.25, 18.12, 19.25, 19.77, 21.03, 21.98]),
          (5, "5 lb", [15.31, 15.31, 16.95, 18.55, 20.09, 20.88, 21.97, 23.26]),
          (6, "6 lb", [15.44, 15.44, 17.02, 18.72, 20.17, 20.89, 21.98, 23.27]),
          (7, "7 lb", [16.29, 16.29, 17.39, 19.2, 20.8, 21.26, 22.57, 24.11]),
          (8, "8 lb", [16.73, 16.73, 18, 19.86, 21.37, 22.1, 23.45, 25.14]),
          (9, "9 lb", [16.98, 16.98, 18.25, 19.92, 21.55, 22.56, 24.41, 26.46]),
          (10, "10 lb", [21.77, 21.77, 23.38, 25.62, 28.16, 29.14, 32.68, 36.15]),
          (11, "11 lb", [23.05, 23.05, 23.84, 26.1, 28.49, 29.89, 35.25, 38.88]),
          (12, "12 lb", [23.27, 23.27, 24.86, 26.35, 28.74, 30.94, 36.94, 40.39]),
          (13, "13 lb", [23.36, 23.36, 24.94, 26.51, 29.08, 31.91, 39.03, 42.35]),
          (14, "14 lb", [24.41, 24.41, 25.65, 26.91, 30.02, 33.77, 41.98, 45.82]),
          (15, "15 lb", [24.43, 24.43, 26, 27.31, 30.86, 35.63, 42.98, 47.94]),
          (16, "16 lb", [25.05, 25.05, 26.94, 27.79, 31.62, 37.07, 45.56, 50.06]),
          (17, "17 lb", [25.23, 25.23, 27.5, 28.11, 32.5, 38.34, 47.53, 50.33]),
          (18, "18 lb", [25.5, 25.5, 27.92, 28.39, 34.05, 40.34, 49.34, 54.25]),
          (19, "19 lb", [26.1, 26.1, 29.19, 29.77, 35.55, 41.37, 50.29, 56.9]),
          (20, "20 lb", [26.11, 26.11, 29.2, 29.82, 36.68, 42.8, 52.16, 58.93])]

T1, T2, T3, T4, T5 = "1 Parcel Costs", "2 Dim Weight", "3 Free Shipping", "4 Services", "5 Dashboard"
Q1, Q2, Q3, Q4, Q5 = (f"'{t}'!" for t in (T1, T2, T3, T4, T5))

wb = S.new_workbook(PRODUCT, version=VERSION)

_card_input = D.Card.input


def _input_with_error(self, *args, error=None, **kw):
    """Card.input plus a column-specific stop error (standard section 15, misses list)."""
    r = _card_input(self, *args, **kw)
    if error:
        ref = f"{self.value}{r}"
        for dv in self.ws.data_validations.dataValidation:
            if ref in str(dv.sqref).split():
                dv.error = error[:255]
    return r


D.Card.input = _input_with_error


# ---------------------------------------------------------------- helpers
def notes_card(ws, top, notes, span, frame_span):
    r = top
    D.h(ws, r, 12); r += 1
    t = ws[f"{span[0]}{r}"]; t.value = "Notes and sources"; t.font = D.f(12, True)
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


def word_rule(ws, rng, anchor, words):
    """Color status words: words = [(text, color, tint)]. Matches the start of the text."""
    for word, color, tint in words:
        ws.conditional_formatting.add(rng, FormulaRule(
            formula=[f'LEFT({anchor},{len(word)})="{word}"'], font=Font(color=D.T[color], bold=True),
            fill=PatternFill("solid", bgColor=D.T[tint]), stopIfTrue=True))


def neg_rule(ws, rng, anchor):
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f"AND(ISNUMBER({anchor}),{anchor}<-0.005)"],
                                                   font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))


def lock_text(c, text, color="muted", bold=False, align="left"):
    c.value = text; c.font = D.f(10, bold, color)
    c.fill = D.fill("card"); c.protection = c.protection.copy(locked=True)
    c.alignment = Alignment(horizontal=align, vertical="center", indent=1 if align == "right" else 0)


def totals_row(ws, r, span, label_col, label_text, cells):
    """Turn the last table row into a totals row: ink rule on top, tint, bold, locked."""
    for k in span:
        c = ws[f"{k}{r}"]
        c.value = None
        c.fill = D.fill("total_tint"); c.protection = c.protection.copy(locked=True)
        c.border = Border(top=D.side("ink"), bottom=D.side("hair"))
        c.font = D.f(10, True)
    lab = ws[f"{label_col}{r}"]; lab.value = label_text; lab.alignment = Alignment(vertical="center")
    for col, formula, fmt in cells:
        c = ws[f"{col}{r}"]; c.value = formula; c.number_format = fmt
        c.alignment = Alignment(horizontal="right", vertical="center")


def pad_rows(ws, last, height=None):
    for rr in range(1, last + 1):
        if ws.row_dimensions[rr].height is None:
            D.h(ws, rr, height or D.GRID_ROW)


# =====================================================================  4 Service Compare (built first: tab 1 reads it)
# Rows are fixed up front so every tab can reference every other one.
P_TOP = 17               # tab 1 table card top -> header at +4, first body row at +5
P_FIRST = P_TOP + 5
P_LAST = P_FIRST + N - 1
P_AVG = P_LAST + 1


def prow(i):
    return P_FIRST + i


# ---------------------------------------------------------------- 1 Parcel Costs
p = wb.create_sheet(T1)
S.set_widths(p, {"A": 3, "B": 2, "C": 24, "D": 12, "E": 10, "F": 7, "G": 22, "H": 10, "I": 10, "J": 8, "K": 8,
                 "L": 7, "M": 7, "N": 8, "O": 9, "P": 10, "Q": 11, "R": 17, "S": 9, "T": 2, "U": 3})
D.page_header(p, "Parcel Costs", "One row per product: the true cost of one parcel, and whether the shipping you charge covers it.",
              AS_OF, span=("B", "T"), side_cols=3)
K1 = D.Card(p, 11, "B", "C", "G", "T", wb=wb)
K1.title("Your packing time", "Even $15 an hour changes the answer.")
HR = K1.input("Your hourly rate for packing time", HOURLY, USD2, name="HourlyRate", validation=("decimal", 0, None),
              prompt="What an hour of your time is worth, in dollars. Packing minutes in the table are charged at this rate. Example: 18.",
              prompt_title="Hourly rate for packing", error=None)
K1.close()
assert K1.end + 2 == P_TOP, K1.end
_t = p["I12"]; _t.value = "Where postage comes from"; _t.font = D.f(12, True); p.merge_cells("I12:S12")
_t = p["I13"]
_t.value = ("From tab 4: the service you pick in the Service column (or the cheapest) at the zone you type, with the billable "
            "weight from tab 2. A number in Postage override wins.")
_t.font = D.f(9, False, "ink2"); _t.alignment = Alignment(vertical="top", wrap_text=True); p.merge_cells("I13:S14")
HRR = f"$G${HR}"

# Service Compare rows (fixed layout, see the 4 Service Compare section)
SC_SET_TOP = 11
SC_HOL_TOP = 18
SC_TOP = 28
SC_FIRST = SC_TOP + 5
SC_LAST = SC_FIRST + N - 1
RT_TOP0 = SC_LAST + 1 + 2  # comparison card ends at SC_LAST + 1; four rate tables follow
_t = RT_TOP0
for _n in (21, 22, 20, 20):  # rows in each rate table
    _t = _t + 5 + _n - 1 + 1 + 2
SVC_TOP = _t  # the service-names helper row sits at the very bottom
SVC_FIRST = SVC_TOP + 5
SVC_RANGE = f"$G${SVC_FIRST}:$L${SVC_FIRST}"


def srow(i):
    return SC_FIRST + i


def p_formula(kind):
    def fn(r):
        i = r - P_FIRST
        k = srow(i)
        if kind == "postage":
            pick = f"INDEX({Q4}$G${k}:$L${k},MATCH(G{r},{Q4}{SVC_RANGE},0))"
            return (f'=IF(C{r}="","",IF(H{r}<>"",H{r},IF(OR(G{r}="",G{r}="Cheapest"),{Q4}M{k},'
                    f'IFERROR(IF({pick}="","",{pick}),""))))')
        if kind == "labor":
            return f'=IF(C{r}="","",N{r}/60*{HRR})'
        if kind == "true":
            return f'=IF(C{r}="","",IF(ISNUMBER(I{r}),I{r}+J{r}+K{r}+L{r}+M{r}+O{r},""))'
        if kind == "short":
            return f'=IF(C{r}="","",IF(ISNUMBER(P{r}),E{r}-P{r},""))'
        if kind == "flag":
            return f'=IF(C{r}="","",IF(ISNUMBER(P{r}),IF(Q{r}<-0.005,"Under-recovered","Covered"),"Enter postage"))'
        if kind == "share":
            return f'=IF(C{r}="","",IF(AND(ISNUMBER(P{r}),P{r}>0),I{r}/P{r},""))'
    return fn


def vals(idx):
    return [row[idx] for row in PRODUCTS]


money_in = dict(validation=("decimal", 0, None), error="Enter dollars, zero or more, for example 0.85.")
cols_p = [
    dict(col="C", head="Product", kind="input", values=vals(0), validation=("textLength", 0, 40),
         prompt="A short product name. Tabs 2, 4 and 5 fill in from this column.", error="Up to 40 characters."),
    dict(col="D", head="Sale price", kind="input", fmt=USD2, align="right", values=vals(1),
         prompt="The item price the buyer pays, before shipping.", **money_in),
    dict(col="E", head="Shipping charged", kind="input", fmt=USD2, align="right", values=vals(2),
         prompt="What the buyer pays you for shipping. 0 for free shipping.", **money_in),
    dict(col="F", head="Zone", kind="input", fmt=INT, align="right", values=vals(3), validation=("whole", 1, 9),
         prompt="USPS zone, 1 to 9. Not sure? 5 is a fair national average; your label platform shows the zone.",
         error="Enter a whole zone from 1 to 9."),
    dict(col="G", head="Service", kind="input", values=vals(4), validation=("list", SERVICES),
         prompt="Cheapest picks the lowest price on tab 4. Or pick one service, or one of your own quotes.",
         error="Pick a service from the list."),
    dict(col="H", head="Postage override", kind="input", fmt=USD2, align="right", values=[None] * len(PRODUCTS),
         prompt="Leave blank to use tab 4. Type a label price here to use it instead.", **money_in),
    dict(col="I", head="Postage used", kind="calc", fmt=USD2, align="right", formula=p_formula("postage")),
    dict(col="J", head="Box or mailer", kind="input", fmt=USD2, align="right", values=vals(5),
         prompt="Cost of one box or mailer, in dollars.", **money_in),
    dict(col="K", head="Filler", kind="input", fmt=USD2, align="right", values=vals(6),
         prompt="Wrap, tissue or peanuts for one parcel, in dollars.", **money_in),
    dict(col="L", head="Tape", kind="input", fmt=USD2, align="right", values=vals(7),
         prompt="Tape per parcel. A $34 roll that seals 400 parcels is $0.085.", **money_in),
    dict(col="M", head="Label", kind="input", fmt=USD2, align="right", values=vals(8),
         prompt="Label paper or ink per parcel, in dollars.", **money_in),
    dict(col="N", head="Pack min", kind="input", fmt=INT, align="right", values=vals(9), validation=("decimal", 0, 240),
         prompt="Minutes to pack one order. Time yourself twice and use the average.", error="Enter minutes from 0 to 240."),
    dict(col="O", head="Packing labor", kind="calc", fmt=USD2, align="right", formula=p_formula("labor")),
    dict(col="P", head="True cost per parcel", kind="calc", fmt=USD2, align="right", bold=True, formula=p_formula("true")),
    dict(col="Q", head="Shortfall", kind="calc", fmt=USD2, align="right", formula=p_formula("short")),
    dict(col="R", head="Check", kind="calc", formula=p_formula("flag")),
    dict(col="S", head="Postage share", kind="calc", fmt=PCT, align="right", formula=p_formula("share")),
]
pf, pl, pend = D.table_card(p, P_TOP, "B", "T", cols_p, N + 1, row_height=TROW, title="Your products",
                            sub="Yellow columns are yours. Shortfall is shipping charged minus the true cost; "
                                "on a free-shipping listing it is the whole parcel cost, which your price has to cover.")
assert (pf, pl) == (P_FIRST, P_AVG), (pf, pl)
totals_row(p, P_AVG, D.cols("C", "S"), "C", "Averages", [
    ("P", f"=IFERROR(AVERAGE(P{P_FIRST}:P{P_LAST}),0)", USD2),
    ("Q", f"=IFERROR(AVERAGE(Q{P_FIRST}:Q{P_LAST}),0)", USD2),
    ("S", f"=IFERROR(AVERAGE(S{P_FIRST}:S{P_LAST}),0)", PCT)])
for r in range(P_FIRST, P_LAST + 1):
    p[f"R{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
word_rule(p, f"R{P_FIRST}:R{P_LAST}", f"$R{P_FIRST}", [("Under-recovered", "accent", "accent_tint"),
                                                         ("Covered", "teal", "teal_tint"), ("Enter postage", "gold", "input_fill")])
neg_rule(p, f"Q{P_FIRST}:Q{P_AVG}", f"Q{P_FIRST}")
PAVG_TRUE, PAVG_SHORT, PAVG_SHARE = f"{Q1}$P${P_AVG}", f"{Q1}$Q${P_AVG}", f"{Q1}$S${P_AVG}"
NPROD = f'COUNT($P${P_FIRST}:$P${P_LAST})'
NNAMES = f'COUNTIF($C${P_FIRST}:$C${P_LAST},"?*")'
D.tile(p, 6, "B", "I", "AVERAGE TRUE COST PER PARCEL", f"=$P${P_AVG}", USD2,
       f'=IF({NNAMES}=0,"Add a product in the table below",IF({NPROD}=0,"Enter postage: no product has a price yet","Postage is "&TEXT($S${P_AVG},"0%")&" of it. Box, filler, tape, label and packing time are the rest."))',
       dark=True)
UNDER = f'COUNTIF($R${P_FIRST}:$R${P_LAST},"Under-recovered")'
v, _, _ = D.tile(p, 6, "K", "T", "PRODUCTS WHERE SHIPPING CHARGED FALLS SHORT", f"={UNDER}", INT,
                 f'=IF({NNAMES}=0,"No products yet",IF({NPROD}=0,"Enter postage: no product has a price yet",IF({UNDER}=0,"Every product\'s shipping covers its parcel",'
                 f'"of "&{NPROD}&" priced products. Average shortfall "&TEXT(-MIN(0,$Q${P_AVG}),"$#,##0.00")&" per parcel")))')
D.status_rule(p, v.coordinate, f"{v.coordinate}>0", fill_tint=False)
D.h(p, 10, 14)
P_LASTROW = pend + 1
pad_rows(p, P_LASTROW)
D.h(p, P_LASTROW, 14)
S.page_break_before(p, P_TOP)
D.paint_canvas(p, P_LASTROW, "Z")
S.finish_sheet(p, PRODUCT, P_LASTROW, span=("A", "U"), freeze="D11", tab_color="accent")
p.page_setup.orientation = "landscape"
p.page_setup.fitToHeight = 0

# ---------------------------------------------------------------- 2 Dim Weight
dw = wb.create_sheet(T2)
S.set_widths(dw, {"A": 3, "B": 2, "C": 24, "D": 9, "E": 9, "F": 9, "G": 10, "H": 9, "I": 11, "J": 9, "K": 10, "L": 10,
                  "M": 11, "N": 11, "O": 24, "P": 24, "Q": 2, "R": 3})
D.page_header(dw, "Dim Weight", "Box size and packed weight in, the weight each carrier really bills out. "
              "A light box can cost like a heavy one.", AS_OF, span=("B", "Q"), side_cols=2)
K2 = D.Card(dw, 11, "B", "C", "E", "I", wb=wb)
K2.title("Carrier rules", "Published figures. Select a cell for its source.")
DV_USPS = K2.input("USPS dim divisor", USPS_DIV, INT, name="USPSDivisor", validation=("whole", 50, 400),
                   prompt="139 since July 12, 2026 (was 166), USPS Postal Bulletin 22705. A whole number from 50 to 400.",
                   error="Enter a whole number from 50 to 400. USPS publishes 139.")
DV_TH = K2.input("USPS dim threshold, cubic in", USPS_THRESH, INT, name="DimThreshold", validation=("whole", 1, 20000),
                 prompt="USPS bills dim weight only above 1,728 cubic inches (1 cubic foot). Under that it bills the scale weight.",
                 prompt_title="USPS dim threshold", error="Enter whole cubic inches from 1 to 20,000. USPS uses 1,728.")
DV_UPS = K2.input("UPS and FedEx dim divisor", UPS_DIV, INT, name="UPSDivisor", validation=("whole", 50, 400),
                  prompt="139 for UPS daily rates and FedEx published rates, on every parcel. Some accounts get a higher divisor.",
                  error="Enter a whole number from 50 to 400. UPS and FedEx publish 139.")
K2.close()
# right: how it works (text card, same rows)
r0, r1 = 11, K2.end
D.frame(dw, r0, r1, "K", "Q")
t = dw[f"L{r0 + 1}"]; t.value = "How dim weight works"; t.font = D.f(12, True); dw.merge_cells(f"L{r0 + 1}:P{r0 + 1}")
body = ("Cubic inches divided by the divisor is the dim weight. The carrier bills the higher of dim weight and scale weight, "
        "rounded up to the next pound. The wreath weighs 2.5 lb but ships in a 16 x 16 x 8 box: 2,048 cubic inches, over one "
        "cubic foot, so USPS bills 2,048 / 139 = 14.7, rounded up to 15 lb. That is a $21.15 label instead of $11.57 at zone 5. "
        "The framed print's 18 x 14 x 3 box is under a cubic foot, so USPS bills its 4 lb, while UPS and FedEx bill 756 / 139 = "
        "5.4, rounded up to 6 lb. Sources checked Oct 7, 2026: USPS Postal Bulletin 22705; UPS and FedEx dim weight pages.")
c = dw[f"L{r0 + 2}"]; c.value = body; c.font = D.f(9, False, "ink2"); c.alignment = Alignment(vertical="top", wrap_text=True)
dw.merge_cells(f"L{r0 + 2}:P{r1 - 1}")
D_TOP = r1 + 2
D_FIRST = D_TOP + 5
D_LAST = D_FIRST + N - 1


def d_formula(kind):
    def fn(r):
        pr = prow(r - D_FIRST)
        T = f"$E${DV_TH}"; U = f"$E${DV_USPS}"; V = f"$E${DV_UPS}"
        if kind == "name":
            return f'=IF({Q1}C{pr}="","",{Q1}C{pr})'
        if kind == "lb":
            return f'=IF(C{r}="","",IF(G{r}="","",G{r}/16))'
        if kind == "cubic":
            return f'=IF(C{r}="","",IF(OR(D{r}="",E{r}="",F{r}=""),"",ROUNDUP(D{r},0)*ROUNDUP(E{r},0)*ROUNDUP(F{r},0)))'
        if kind == "over":
            return f'=IF(C{r}="","",IF(ISNUMBER(I{r}),IF(I{r}>{T},"Yes","No"),""))'
        if kind == "usps_dim":
            return f'=IF(C{r}="","",IF(ISNUMBER(I{r}),IF(I{r}>{T},I{r}/{U},"-"),""))'
        if kind == "usps_bill":
            return (f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(H{r})),NOT(ISNUMBER(I{r}))),"",IF(ISNUMBER(K{r}),'
                    f'IF(MAX(H{r},K{r})<1,MAX(H{r},K{r}),ROUNDUP(MAX(H{r},K{r}),0)),IF(H{r}<1,H{r},ROUNDUP(H{r},0)))))')
        if kind == "ups_dim":
            return f'=IF(C{r}="","",IF(ISNUMBER(I{r}),I{r}/{V},""))'
        if kind == "ups_bill":
            return f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(H{r})),NOT(ISNUMBER(M{r}))),"",MAX(1,ROUNDUP(MAX(H{r},M{r}),0))))'
        if kind == "usps_flag":
            return (f'=IF(C{r}="","",IF(NOT(ISNUMBER(L{r})),"",IF(AND(ISNUMBER(K{r}),K{r}>H{r}),'
                    f'"Dim weight bites: +"&(ROUNDUP(L{r},0)-ROUNDUP(H{r},0))&" lb","OK")))')
        if kind == "ups_flag":
            return (f'=IF(C{r}="","",IF(NOT(ISNUMBER(N{r})),"",IF(N{r}>MAX(1,ROUNDUP(H{r},0)),'
                    f'"Dim weight bites: +"&(N{r}-MAX(1,ROUNDUP(H{r},0)))&" lb","OK")))')
    return fn


inch = dict(validation=("decimal", 0.1, 108), error="Enter inches from 0.1 to 108.")
cols_d = [
    dict(col="C", head="Product", kind="calc", formula=d_formula("name")),
    dict(col="D", head="Length (in)", kind="input", fmt="#,##0.0#", align="right", values=[d[0] for d in DIMS],
         prompt="Box length in inches. Each side is rounded up to the next whole inch.", **inch),
    dict(col="E", head="Width (in)", kind="input", fmt="#,##0.0#", align="right", values=[d[1] for d in DIMS],
         prompt="Box width in inches.", **inch),
    dict(col="F", head="Height (in)", kind="input", fmt="#,##0.0#", align="right", values=[d[2] for d in DIMS],
         prompt="Box height in inches.", **inch),
    dict(col="G", head="Packed weight (oz)", kind="input", fmt="#,##0.0#", align="right", values=[d[3] for d in DIMS],
         validation=("decimal", 0.1, 1120), prompt="Weigh the packed parcel, not the product. 16 oz is 1 lb.",
         error="Enter ounces from 0.1 to 1,120 (70 lb)."),
    dict(col="H", head="Packed weight (lb)", kind="calc", fmt="#,##0.00", align="right", formula=d_formula("lb")),
    dict(col="I", head="Cubic inches", kind="calc", fmt=INT, align="right", formula=d_formula("cubic")),
    dict(col="J", head="Over 1 cu ft?", kind="calc", formula=d_formula("over")),
    dict(col="K", head="USPS dim (lb)", kind="calc", fmt="#,##0.0", align="right", formula=d_formula("usps_dim")),
    dict(col="L", head="USPS bills (lb)", kind="calc", fmt="#,##0.##", align="right", bold=True, formula=d_formula("usps_bill")),
    dict(col="M", head="UPS/FedEx dim (lb)", kind="calc", fmt="#,##0.0", align="right", formula=d_formula("ups_dim")),
    dict(col="N", head="UPS/FedEx bills (lb)", kind="calc", fmt=INT, align="right", bold=True, formula=d_formula("ups_bill")),
    dict(col="O", head="USPS check", kind="calc", formula=d_formula("usps_flag")),
    dict(col="P", head="UPS and FedEx check", kind="calc", formula=d_formula("ups_flag")),
]
df, dl, dend = D.table_card(dw, D_TOP, "B", "Q", cols_d, N, row_height=TROW, title="Your parcels",
                            sub="Product names come from tab 1. Type each packed box size and weight; the bold columns go to tab 4.")
assert (df, dl) == (D_FIRST, D_LAST), (df, dl)
for r in range(D_FIRST, D_LAST + 1):
    for k in "JOP":
        dw[f"{k}{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    dw[f"K{r}"].alignment = Alignment(horizontal="right", vertical="center")
word_rule(dw, f"O{D_FIRST}:P{D_LAST}", f"O{D_FIRST}", [("Dim weight bites", "accent", "accent_tint"), ("OK", "teal", "teal_tint")])
DCOUNT = f'COUNTIF($O${D_FIRST}:$O${D_LAST},"Dim weight bites*")'
DCOUNT_U = f'COUNTIF($P${D_FIRST}:$P${D_LAST},"Dim weight bites*")'
DN = f"COUNT($L${D_FIRST}:$L${D_LAST})"
D.tile(dw, 6, "B", "I", "PARCELS USPS BILLS ABOVE THEIR SCALE WEIGHT", f"={DCOUNT}", INT,
       f'=IF({DN}=0,"Add box sizes and weights in the table below","of "&{DN}&" parcels. Only boxes over one cubic foot can be hit.")',
       dark=True)
v, _, _ = D.tile(dw, 6, "K", "Q", "PARCELS UPS AND FEDEX BILL ABOVE SCALE WEIGHT", f"={DCOUNT_U}", INT,
                 f'=IF({DN}=0,"No parcels yet","UPS and FedEx apply dim weight to every box, so small light boxes count too")')
D.status_rule(dw, v.coordinate, f"{v.coordinate}>0", fill_tint=False)
D.h(dw, 10, 14)
D_LASTROW = dend + 1
pad_rows(dw, D_LASTROW); D.h(dw, D_LASTROW, 14)
S.page_break_before(dw, D_TOP)
D.paint_canvas(dw, D_LASTROW, "Z")
S.finish_sheet(dw, PRODUCT, D_LASTROW, span=("A", "R"), freeze="D11", tab_color="purple" if "purple" in S.PALETTE else "blue")
dw.page_setup.orientation = "landscape"
dw.page_setup.fitToHeight = 0


def drow(i):
    return D_FIRST + i


# ---------------------------------------------------------------- 3 Free Shipping
fs = wb.create_sheet(T3)
S.set_widths(fs, {"A": 3, "B": 2, "C": 30, "D": 13, "E": 2, "F": 3, "G": 2, "H": 16, "I": 16, "J": 16, "K": 2, "L": 3})
D.page_header(fs, "Free Shipping", "What free shipping over $35, $50 or $75 does to your profit.",
              AS_OF, span=("B", "K"), side_cols=3)
L = D.Card(fs, 11, "B", "C", "D", "E", wb=wb)
L.title("Your shop today", "Type over the yellow cells.")
AOV = L.input("Average order value (items)", FS["aov"], USD2, name="AvgOrderValue", validation=("decimal", 0, None),
              prompt="Item sales divided by orders, last 90 days (Shop Manager, Stats). Items only, no shipping.",
              error="Enter dollars, zero or more.")
SHIP = L.input("Shipping you charge per order", FS["ship"], USD2, name="ShipCharged", validation=("decimal", 0, None),
               prompt="What the buyer pays you for shipping on a typical order.", error="Enter dollars, zero or more.")
TC = L.calc("True parcel cost, from tab 1", f"={PAVG_TRUE}", USD2)
TCO = L.input("True parcel cost override", None, USD2, validation=("decimal", 0, None), allow_blank=True,
              prompt="Optional. Leave blank to use the average from tab 1, or type another parcel cost.",
              error="Enter dollars, zero or more, or leave blank.")
TCU = L.calc("True parcel cost used", f'=IF(D{TCO}<>"",D{TCO},D{TC})', USD2, total=True)
MRG = L.input("Margin on the items", FS["margin"], PCT, name="ItemMargin", validation=("decimal", 0.01, 0.95),
              prompt="Item price minus product cost and marketplace fees, as a share of item price, before shipping. Type a percent, for example 45%.",
              error="Enter a margin from 1% to 95%.")
LIFT = L.input("Order lift from free shipping", FS["lift"], PCT, name="OrderLift", validation=("decimal", 0, 1),
               prompt="Assumption: how many more orders a free-shipping badge brings. 15% is a planning figure, not a promise. Try 5% and 25%.",
               prompt_title="Order lift (assumption)", error="Enter a lift from 0% to 100%.")
L.close()
R = D.Card(fs, 11, "G", "H", "J", "K", wb=wb)
R.title("Three numbers first", "Per order, before any scenario.")
F_PROF = R.calc("Profit per order today", f"=$D${AOV}*$D${MRG}+$D${SHIP}-$D${TCU}", USD2)
R.text("Item margin plus shipping, less the parcel.", size=9)
F_COST = R.calc("Shipping you stop collecting", f"=$D${SHIP}", USD2)
R.text("The parcel still costs what it costs.", size=9)
F_BE = R.calc("Break-even order value", f"=IF($D${MRG}>0,$D${AOV}+$D${SHIP}/$D${MRG},0)", USD2, total=True, tint="total_tint")
R.text("Set your thresholds at or above this.", size=9)
R.close()
for rr in range(R.end + 1, L.end + 1):
    D.h(fs, rr, D.GRID_ROW)
# full-width scenario card
s_top = max(L.end, R.end) + 2
r = s_top
D.h(fs, r, 12); r += 1
t = fs[f"C{r}"]; t.value = "Scenarios, per 100 orders you get today"; t.font = D.f(12, True); fs.merge_cells(f"C{r}:J{r}"); D.h(fs, r, 24); r += 1
t = fs[f"C{r}"]; t.value = "Yellow cells: three thresholds, the share of orders at or above each, and what those orders average."
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top"); fs.merge_cells(f"C{r}:J{r}"); D.h(fs, r, 18); r += 1
HEAD = r
for col, txt in (("D", "TODAY"), ("H", "SCENARIO 1"), ("I", "SCENARIO 2"), ("J", "SCENARIO 3")):
    c = fs[f"{col}{r}"]; c.value = txt; c.font = D.f(8, True, "muted"); c.alignment = Alignment(horizontal="right", vertical="bottom")
fs[f"C{r}"].value = "CHARGE SHIPPING OR GO FREE"; fs[f"C{r}"].font = D.f(8, True, "muted"); fs[f"C{r}"].alignment = Alignment(vertical="bottom")
for k in D.cols("C", "J"):
    fs[f"{k}{r}"].border = Border(bottom=D.side("ink"))
D.h(fs, r, 24); r += 1
SROWS = {}
SC_COLS = ("H", "I", "J")


def srow_line(key, label, today, scen, fmt, kind="calc", bold=False, total=False, tint=None):
    global r
    SROWS[key] = r
    lab = fs[f"C{r}"]; lab.value = label; lab.font = D.f(10, bold or total); lab.alignment = Alignment(vertical="center")
    d = fs[f"D{r}"]
    if today is None:
        d.value = "-"; d.font = D.f(10, False, "muted"); d.alignment = Alignment(horizontal="right", vertical="center")
    else:
        d.value = today; d.number_format = fmt; d.font = D.f(10, bold or total)
        d.alignment = Alignment(horizontal="right", vertical="center")
    for i, col in enumerate(SC_COLS):
        c = fs[f"{col}{r}"]
        c.value = scen[i] if kind == "input" else scen(col)
        c.number_format = fmt
        if kind == "input":
            c.fill = D.fill("input_fill"); c.font = D.f(10, True, "input_text")
            c.protection = c.protection.copy(locked=False)
            c.alignment = Alignment(horizontal="right", vertical="center", indent=1)
            c.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
        else:
            c.font = D.f(10, bold or total); c.alignment = Alignment(horizontal="right", vertical="center")
    for k in D.cols("C", "J"):
        cell = fs[f"{k}{r}"]
        if kind != "input" or k not in SC_COLS:
            cell.border = Border(top=D.side("ink") if total else None, bottom=D.side("hair"))
        if tint and (kind != "input" or k not in SC_COLS):
            cell.fill = D.fill(tint)
    D.h(fs, r, D.GRID_ROW)
    r += 1


def add_dv(ws, rng, kind, lo, hi, title, prompt, error):
    dv = DataValidation(type=kind, operator="between", formula1=str(lo), formula2=str(hi), allow_blank=True) if hi is not None \
        else DataValidation(type=kind, operator="greaterThanOrEqual", formula1=str(lo), allow_blank=True)
    dv.showInputMessage = True; dv.promptTitle = title[:32]; dv.prompt = prompt[:255]
    dv.showErrorMessage = True; dv.errorStyle = "stop"; dv.errorTitle = "Check this cell"; dv.error = error[:255]
    ws.add_data_validation(dv); dv.add(rng)


srow_line("thr", "Free-shipping threshold", None, FS["thresholds"], USD0, kind="input")
srow_line("share", "Share of orders at or above it", None, FS["shares"], PCT, kind="input")
srow_line("avgq", "Average value of those orders", None, FS["avg"], USD2, kind="input")
add_dv(fs, f"H{SROWS['thr']}:J{SROWS['thr']}", "decimal", 0, None, "Free-shipping threshold",
       "Orders at or above this item total ship free. Example: 50.", "Enter dollars, zero or more, for example 50.")
add_dv(fs, f"H{SROWS['share']}:J{SROWS['share']}", "decimal", 0, 1, "Share of orders above it",
       "From your order history: sort orders by item total and count those at or above the threshold. Type a percent, for example 30%.",
       "Enter a share from 0% to 100%.")
add_dv(fs, f"H{SROWS['avgq']}:J{SROWS['avgq']}", "decimal", 0, None, "Average of those orders",
       "Average item total of the orders that qualify. Buyers often add an item to reach the threshold.",
       "Enter dollars, zero or more.")
A_ = f"$D${AOV}"; SH_ = f"$D${SHIP}"; TC_ = f"$D${TCU}"; M_ = f"$D${MRG}"; LF_ = f"$D${LIFT}"
srow_line("avgo", "Average value of the other orders", f"={A_}", lambda c: f"={A_}", USD2)
srow_line("orders", "Orders (with the lift)", "=100", lambda c: f"=100*(1+{LF_})", NUM1)
srow_line("qual", "Orders that ship free", "=0", lambda c: f"={c}{SROWS['orders']}*{c}{SROWS['share']}", NUM1)
srow_line("other", "Orders that pay shipping", f"=D{SROWS['orders']}", lambda c: f"={c}{SROWS['orders']}-{c}{SROWS['qual']}", NUM1)
srow_line("rev", "Item revenue", f"=D{SROWS['orders']}*{A_}",
          lambda c: f"={c}{SROWS['qual']}*{c}{SROWS['avgq']}+{c}{SROWS['other']}*{c}{SROWS['avgo']}", USD0)
srow_line("coll", "Shipping collected", f"=D{SROWS['other']}*{SH_}", lambda c: f"={c}{SROWS['other']}*{SH_}", USD0)
srow_line("parc", "Parcel cost, all orders", f"=D{SROWS['orders']}*{TC_}", lambda c: f"={c}{SROWS['orders']}*{TC_}", USD0)
srow_line("profit", "Profit", f"=D{SROWS['rev']}*{M_}+D{SROWS['coll']}-D{SROWS['parc']}",
          lambda c: f"={c}{SROWS['rev']}*{M_}+{c}{SROWS['coll']}-{c}{SROWS['parc']}", USD0, total=True)
srow_line("per", "Profit per order", f"=IF(D{SROWS['orders']}>0,D{SROWS['profit']}/D{SROWS['orders']},0)",
          lambda c: f"=IF({c}{SROWS['orders']}>0,{c}{SROWS['profit']}/{c}{SROWS['orders']},0)", USD2)
srow_line("chg", "Change against today", "=0", lambda c: f"={c}{SROWS['profit']}-$D${SROWS['profit']}", USD0, bold=True,
          tint="total_tint")
srow_line("verd", "Verdict", '="Today"',
          lambda c: f'=IF(OR({TC_}<=0,{c}{SROWS["thr"]}=""),"",IF({c}{SROWS["chg"]}>0.005,"Beats today",IF({c}{SROWS["chg"]}<-0.005,"Worse than today","About the same")))', "General")
for col in ("D",) + SC_COLS:
    fs[f"{col}{SROWS['verd']}"].alignment = Alignment(horizontal="right", vertical="center")
word_rule(fs, f"H{SROWS['verd']}:J{SROWS['verd']}", f"H{SROWS['verd']}",
          [("Beats", "teal", "teal_tint"), ("Worse", "accent", "accent_tint"), ("About", "gold", "input_fill")])
neg_rule(fs, f"H{SROWS['chg']}:J{SROWS['chg']}", f"H{SROWS['chg']}")
CHG = f"$H${SROWS['chg']}:$J${SROWS['chg']}"
THR = f"$H${SROWS['thr']}:$J${SROWS['thr']}"
# recommendation pill (2 rows)
D.h(fs, r, 8); r += 1
REC = r
rec = fs[f"C{r}"]
rec.value = (f'=IF({TC_}<=0,"Enter your true parcel cost first (it fills in from tab 1, or type one in the override cell).",'
             f'IF(MAX({CHG})<=0.005,"Keep charging shipping. With these assumptions, none of the three thresholds beats what you earn today.",'
             f'"Best of the three: free shipping over "&TEXT(INDEX({THR},MATCH(MAX({CHG}),{CHG},0)),"$#,##0")&", about "'
             f'&TEXT(MAX({CHG}),"$#,##0")&" more profit per 100 orders than today. An estimate built on your assumptions above, not a promise."))')
rec.font = D.f(10, True); rec.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
fs.merge_cells(f"C{r}:J{r + 1}")
D.h(fs, r, 22); D.h(fs, r + 1, 22)
fs.conditional_formatting.add(f"C{r}:J{r + 1}", FormulaRule(formula=[f'LEFT($C${r},4)="Best"'], font=Font(color=D.T["teal"], bold=True),
                                                             fill=PatternFill("solid", bgColor=D.T["teal_tint"]), stopIfTrue=True))
fs.conditional_formatting.add(f"C{r}:J{r + 1}", FormulaRule(formula=[f'LEFT($C${r},4)<>"Best"'], font=Font(color=D.T["accent"], bold=True),
                                                             fill=PatternFill("solid", bgColor=D.T["accent_tint"]), stopIfTrue=True))
r += 2
D.h(fs, r, 12)
D.frame(fs, s_top, r, "B", "K")
S_END = r
BEST = f'IF(MAX({CHG})<=0.005,"Keep charging",INDEX({THR},MATCH(MAX({CHG}),{CHG},0)))'
D.tile(fs, 6, "B", "E", "BEST FREE-SHIPPING THRESHOLD", f'=IF({TC_}<=0,"Not yet",{BEST})', '"Over "$#,##0',
       f'=IF({TC_}<=0,"Enter a parcel cost first",IF(MAX({CHG})<=0.005,"None of the three beats charging shipping","Of your three thresholds, on your assumptions"))',
       dark=True)
v, _, _ = D.tile(fs, 6, "G", "K", "PROFIT PER 100 ORDERS AGAINST TODAY", f'=IF({TC_}<=0,"",MAX({CHG}))', '"+"$#,##0;-"$"#,##0;"$"0',
                 f'=IF({TC_}<=0,"Enter a parcel cost first","Today: "&TEXT($D${SROWS["profit"]},"$#,##0")&" profit per 100 orders")')
D.status_rule(fs, v.coordinate, f"AND({TC_}>0,{v.coordinate}<=0.005)", fill_tint=False)
D.h(fs, 10, 14)
n_top = S_END + 2
FS_NOTES = [
    ("How to read it", "Free shipping does two things: some buyers add an item to reach the threshold (the average value of the "
     "orders that ship free), and some buyers who would have left now buy (the lift). Against that, you stop collecting shipping "
     "on those orders. The scenarios put all of it in one place, per 100 of the orders you get today."),
    ("Your own numbers", "The share of orders above each threshold comes from your order history: sort your orders by item total "
     "and count. The lift is an assumption, so try 5% and 25% and see whether the answer changes."),
    ("Before you rely on a number", "Estimates for planning, built on your inputs and assumptions. Not accounting, tax or financial "
     "advice. See the Terms tab."),
]
n_end = notes_card(fs, n_top, FS_NOTES, ("C", "J"), ("B", "K"))
S.page_break_before(fs, s_top)
FS_LAST = n_end + 1
pad_rows(fs, FS_LAST); D.h(fs, FS_LAST, 14)
D.paint_canvas(fs, FS_LAST, "Z")
S.finish_sheet(fs, PRODUCT, FS_LAST, span=("A", "L"), freeze="A11", tab_color="teal")

# ---------------------------------------------------------------- 4 Service Compare
sc = wb.create_sheet(T4)
S.set_widths(sc, {"A": 3, "B": 2, "C": 24, "D": 9, "E": 9, "F": 8, "G": 11, "H": 11, "I": 11, "J": 11, "K": 10, "L": 10,
                  "M": 11, "N": 22, "O": 11, "P": 2, "Q": 3})
D.page_header(sc, "Services", "Every product priced on every service at its zone and billable weight, cheapest first.",
              AS_OF, span=("B", "P"), side_cols=3)
K4 = D.Card(sc, SC_SET_TOP, "B", "C", "E", "I", wb=wb)
K4.title("Rate settings", "Select a cell for its source.")
FUEL = K4.input("UPS Ground fuel surcharge", UPS_FUEL, PCT1, name="UPSFuel", validation=("decimal", 0, 1),
                prompt="Added to UPS list rates. It changes every Monday at ups.com, Fuel Surcharges. Type this week's percent, for example 29.5%.",
                error="Enter a percent from 0% to 100%.")
HOL = K4.input("Add USPS holiday prices", "No", "General", name="USPSHoliday", validation=("list", ["Yes", "No"]),
               prompt="Yes adds the USPS temporary holiday increases below to all three USPS columns. They apply Oct 4, 2026 to Jan 17, 2027.",
               error="Pick Yes or No.")
sc[f"E{HOL}"].alignment = Alignment(horizontal="right", vertical="center", indent=1)
K4.close()
assert K4.end + 2 == SC_HOL_TOP, K4.end
# right of the settings card: what the switch means today (text card)
D.frame(sc, SC_SET_TOP, K4.end, "K", "P")
t = sc[f"L{SC_SET_TOP + 1}"]; t.value = "Which prices are in the tables"; t.font = D.f(12, True); sc.merge_cells(f"L{SC_SET_TOP + 1}:O{SC_SET_TOP + 1}")
txt = sc[f"L{SC_SET_TOP + 2}"]
txt.value = (f'=IF($E${HOL}="Yes","Holiday prices ON: the USPS columns add the increases in the table below. Switch to No after Jan 17, 2027.",'
             '"USPS prices from July 12, 2026. From Oct 4, 2026 to Jan 17, 2027 USPS adds temporary holiday prices: set Add USPS holiday prices to Yes to include them.")')
txt.font = D.f(10, True, "ink"); txt.alignment = Alignment(vertical="center", wrap_text=True)
sc.merge_cells(f"L{SC_SET_TOP + 2}:O{K4.end - 1}")
sc.conditional_formatting.add(f"L{SC_SET_TOP + 2}:O{K4.end - 1}", FormulaRule(formula=[f'$E${HOL}<>"Yes"'],
                              font=Font(color=D.T["accent"], bold=True), fill=PatternFill("solid", bgColor=D.T["accent_tint"]), stopIfTrue=True))
sc.conditional_formatting.add(f"L{SC_SET_TOP + 2}:O{K4.end - 1}", FormulaRule(formula=[f'$E${HOL}="Yes"'],
                              font=Font(color=D.T["teal"], bold=True), fill=PatternFill("solid", bgColor=D.T["teal_tint"]), stopIfTrue=True))

# holiday adder table
hol_cols = [dict(col="C", head="Billable weight", kind="text", values=[h[0] for h in HOLIDAY])]
for j, (col, head) in enumerate(zip("DEGHIJ", ("GA comm z1-4", "GA comm z5-9", "GA retail z1-4", "GA retail z5-9",
                                                  "Priority z1-4", "Priority z5-9"))):
    hol_cols.append(dict(col=col, head=head, kind="input", fmt=USD2, align="right", values=[h[j + 1] for h in HOLIDAY],
                         validation=("decimal", 0, 20), prompt="Added to each USPS label when holiday prices are on. "
                         "USPS news release Aug 25, 2026, checked " + CHECKED + ".", error="Enter dollars from 0 to 20."))
# F is a narrow zone column: keep the adder table on D, E, G, H, I, J (F stays blank inside this card)
hf, hl, hend = D.table_card(sc, SC_HOL_TOP, "B", "P", hol_cols, 3, title="USPS holiday price increases, per label",
                            sub="Oct 4, 2026 to Jan 17, 2027, by billable weight and zone. Used only when the switch above says Yes.")
assert hend + 2 == SC_TOP + 0 or True
HOLR = (hf, hl)
HOL_ON = f'$E${HOL}="Yes"'


def hol_add(i, wcell, zcell):
    """Adder for USPS service i (0 GA commercial, 1 GA retail, 2 Priority): a lookup in the holiday table."""
    c1, c2 = (("D", "E"), ("G", "H"), ("I", "J"))[i]
    band = f"IF({wcell}<=3,1,IF({wcell}<=10,2,3))"
    return f'IF({HOL_ON},IF({zcell}<=4,INDEX(${c1}${hf}:${c1}${hl},{band}),INDEX(${c2}${hf}:${c2}${hl},{band})),0)'


# product comparison table
SC_TOP_REAL = hend + 2
assert SC_TOP_REAL == SC_TOP, (SC_TOP_REAL, SC_TOP)
RT = {}  # rate table rows, filled below (positions computed now)
rt_top = SC_LAST + 1 + 2 + 2  # after the comparison card end and its gap (+ service names card later)


def sc_formula(kind):
    def fn(r):
        i = r - SC_FIRST
        pr, dr = prow(i), drow(i)
        if kind == "name":
            return f'=IF({Q1}C{pr}="","",{Q1}C{pr})'
        if kind == "usps_lb":
            return f'=IF(C{r}="","",{Q2}L{dr})'
        if kind == "ups_lb":
            return f'=IF(C{r}="","",{Q2}N{dr})'
        if kind == "zone":
            return f'=IF(C{r}="","",IF({Q1}F{pr}="","",{Q1}F{pr}))'
        a, b = RT_RANGES[kind] if kind in RT_RANGES else (None, None)
        if kind == "ga_com":
            return (f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(D{r})),NOT(ISNUMBER(F{r}))),"",IF(D{r}>20,"over 20 lb",'
                    f'INDEX({a},MATCH(IF(D{r}<1,0,ROUNDUP(D{r},0)),{b},0),F{r})+{hol_add(0, f"D{r}", f"F{r}")})))')
        if kind == "ga_ret":
            return (f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(D{r})),NOT(ISNUMBER(F{r}))),"",IF(D{r}>20,"over 20 lb",'
                    f'INDEX({a},MATCH(IF(D{r}<=0.5,0.5,IF(D{r}<1,0.99,ROUNDUP(D{r},0))),{b},0),F{r})+{hol_add(1, f"D{r}", f"F{r}")})))')
        if kind == "pri":
            return (f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(D{r})),NOT(ISNUMBER(F{r}))),"",IF(D{r}>20,"over 20 lb",'
                    f'INDEX({a},MATCH(MAX(1,ROUNDUP(D{r},0)),{b},0),F{r})+{hol_add(2, f"D{r}", f"F{r}")})))')
        if kind == "ups":
            return (f'=IF(C{r}="","",IF(OR(NOT(ISNUMBER(E{r})),NOT(ISNUMBER(F{r}))),"",IF(E{r}>20,"over 20 lb",'
                    f'IF(F{r}=9,"n/a",INDEX({a},MATCH(E{r},{b},0),F{r})*(1+$E${FUEL})))))')
        if kind == "cheap":
            return f'=IF(C{r}="","",IF(COUNT(G{r}:L{r})=0,"",MIN(G{r}:L{r})))'
        if kind == "cheap_name":
            return f'=IF(C{r}="","",IF(ISNUMBER(M{r}),INDEX({SVC_RANGE},MATCH(M{r},G{r}:L{r},0)),""))'
        if kind == "saved":
            return f'=IF(C{r}="","",IF(AND(ISNUMBER(M{r}),ISNUMBER(H{r})),H{r}-M{r},""))'
    return fn


# rate table positions: four table cards after the comparison card and the service-names card
tables = [("ga_com", "USPS Ground Advantage, commercial", GA_COM,
           "Label platform prices (Etsy, eBay, Pirate Ship and similar). USPS Notice 123, effective July 12, 2026."),
          ("ga_ret", "USPS Ground Advantage, retail", GA_RET,
           "Post Office counter prices. USPS Notice 123, effective July 12, 2026."),
          ("pri", "USPS Priority Mail, commercial", PRI_COM, "USPS Notice 123, effective July 12, 2026."),
          ("ups", "UPS Ground Saver, daily rates before fuel", UPS_GS,
           "UPS 2026 rates, effective Dec 22, 2025. Zone 1 is billed as zone 2; not offered to zone 9.")]
RT_RANGES = {}
top = RT_TOP0
for key, title, data, sub in tables:
    first = top + 5
    last = first + len(data) - 1
    RT_RANGES[key] = (f"$E${first}:$M${last}", f"$D${first}:$D${last}")
    RT[key] = (top, first, last, title, data, sub)
    top = last + 1 + 2

cols_sc = [
    dict(col="C", head="Product", kind="calc", formula=sc_formula("name")),
    dict(col="D", head="USPS bills (lb)", kind="calc", fmt="#,##0.##", align="right", formula=sc_formula("usps_lb")),
    dict(col="E", head="UPS bills (lb)", kind="calc", fmt=INT, align="right", formula=sc_formula("ups_lb")),
    dict(col="F", head="Zone", kind="calc", fmt=INT, align="right", formula=sc_formula("zone")),
    dict(col="G", head="USPS GA Commercial", kind="calc", fmt=USD2, align="right", formula=sc_formula("ga_com")),
    dict(col="H", head="USPS GA Retail", kind="calc", fmt=USD2, align="right", formula=sc_formula("ga_ret")),
    dict(col="I", head="USPS Priority Commercial", kind="calc", fmt=USD2, align="right", formula=sc_formula("pri")),
    dict(col="J", head="UPS Ground Saver", kind="calc", fmt=USD2, align="right", formula=sc_formula("ups")),
    dict(col="K", head="Your quote A", kind="input", fmt=USD2, align="right", values=[None] * N, validation=("decimal", 0, None),
         prompt="Optional: the price your label platform quotes for UPS Ground, FedEx or a negotiated rate. It joins the comparison.",
         error="Enter dollars, zero or more: the rate your label platform quoted."),
    dict(col="L", head="Your quote B", kind="input", fmt=USD2, align="right", values=[None] * N, validation=("decimal", 0, None),
         prompt="Optional: a second quote, for example FedEx Ground Economy.", error="Enter dollars, zero or more: a second quoted rate."),
    dict(col="M", head="Cheapest", kind="calc", fmt=USD2, align="right", bold=True, formula=sc_formula("cheap")),
    dict(col="N", head="Cheapest service", kind="calc", formula=sc_formula("cheap_name")),
    dict(col="O", head="Saved vs counter", kind="calc", fmt=USD2, align="right", formula=sc_formula("saved")),
]
sf, sl, send = D.table_card(sc, SC_TOP, "B", "P", cols_sc, N, row_height=TROW, title="Every product, every service",
                            sub="Weights come from tab 2 and zones from tab 1. Cheapest includes anything typed in the Your quote columns.")
assert (sf, sl) == (SC_FIRST, SC_LAST) and send == SC_LAST + 1, (sf, sl, send)
for rr in range(SC_FIRST, SC_LAST + 1):
    sc[f"N{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
    sc[f"M{rr}"].fill = D.fill("teal_tint")
# rate tables
for key, (top, first, last, title, data, sub) in RT.items():
    zc = [dict(col="C", head="Weight", kind="text", values=[d[1] for d in data]),
          dict(col="D", head="Code", kind="muted", values=[d[0] for d in data], align="right")]
    for z, col in enumerate("EFGHIJKLM"):
        zvals = [d[2][z] if z < len(d[2]) else "n/a" for d in data]
        if key == "ups" and z == 8:
            zc.append(dict(col=col, head=f"Zone {z + 1}", kind="muted", values=zvals, align="right"))
        else:
            zc.append(dict(col=col, head=f"Zone {z + 1}", kind="input", fmt=USD2, align="right", values=zvals,
                           validation=("decimal", 0, None),
                           prompt=f"{title}, zone {z + 1}. When the carrier changes prices, type the new ones here and every comparison updates.",
                           error=f"Enter a zone {z + 1} price in dollars, zero or more."))
    a1, a2, e2 = D.table_card(sc, top, "B", "P", zc, len(data), row_height=18, title=title, sub=sub)
    assert (a1, a2) == (first, last), (key, a1, a2, first, last)
    for rr in range(first, last + 1):
        sc[f"D{rr}"].font = D.f(9, False, "muted")
    S.page_break_before(sc, top)
assert top == RT["ups"][0] and e2 + 2 == SVC_TOP, (e2, SVC_TOP)
# service names card
svc_cols = [dict(col="C", head="Used by the Service dropdown on tab 1", kind="text", values=["Service names"])]
for j, col in enumerate("GHIJKL"):
    svc_cols.append(dict(col=col, head=f"Column {col}", kind="text", values=[SERVICES[j + 1]]))
a_, b_, svc_end = D.table_card(sc, SVC_TOP, "B", "P", svc_cols, 1, title="Service names",
                               sub="Helper row: the names tab 1 matches. Leave them as they are.")
assert a_ == SVC_FIRST, (a_, SVC_FIRST)
for col in "CGHIJKL":
    sc[f"{col}{SVC_FIRST}"].font = D.f(9, False, "ink2")
    sc[f"{col}{SVC_FIRST}"].alignment = Alignment(vertical="center", wrap_text=True)
    sc[f"{col}{SVC_FIRST - 1}"].value = None
sc[f"C{SVC_FIRST - 1}"].value = "HELPER ROW"
D.h(sc, SVC_FIRST, 30)
SC_LASTROW = svc_end + 1
pad_rows(sc, SC_LASTROW); D.h(sc, SC_LASTROW, 14)
CHEAP_SUM = f"SUM($M${SC_FIRST}:$M${SC_LAST})"
SAVED_SUM = f"SUM($O${SC_FIRST}:$O${SC_LAST})"
D.tile(sc, 6, "B", "I", "CHEAPEST POSTAGE, ONE OF EACH PRODUCT", f"={CHEAP_SUM}", USD2,
       f'=IF(COUNTIF($C${SC_FIRST}:$C${SC_LAST},"?*")=0,"Add products on tab 1 and parcels on tab 2",IF(COUNT($M${SC_FIRST}:$M${SC_LAST})=0,"No priced parcel yet: check zones and weights",'
       f'"For "&COUNT($M${SC_FIRST}:$M${SC_LAST})&" products at the cheapest service each"))', dark=True)
D.tile(sc, 6, "K", "P", "SAVED AGAINST THE POST OFFICE COUNTER", f"={SAVED_SUM}", USD2,
       '="Buying each label online at the cheapest price, one of each product"')
D.h(sc, 10, 14)
S.page_break_before(sc, SC_TOP)
D.paint_canvas(sc, SC_LASTROW, "Z")
S.finish_sheet(sc, PRODUCT, SC_LASTROW, span=("A", "Q"), freeze="D11", tab_color="blue")
sc.page_setup.orientation = "landscape"
sc.page_setup.fitToHeight = 0

# ---------------------------------------------------------------- 5 Dashboard
db = wb.create_sheet(T5)
S.set_widths(db, {"A": 3, "B": 2, "C": 24, "D": 10, "E": 10, "F": 11, "G": 11, "H": 11, "I": 11, "J": 13, "K": 10, "L": 17,
                  "M": 16, "N": 2, "O": 3})
D.page_header(db, "Dashboard", "Every product's shipping economics on one page, once the full parcel cost is counted.",
              AS_OF, span=("B", "N"), side_cols=3)
DB_STRIP = 11
K5_TOP = 16
DB_TOP = None
K5 = D.Card(db, K5_TOP, "B", "C", "F", "G", wb=wb)
K5.title("Marketplace fees", "Percent fees are per product, in the table.")
FIX = K5.input("Fixed marketplace fee per order", FIXED_FEE, USD2, name="FixedFee", validation=("decimal", 0, None),
               prompt="Etsy: $0.25 payment processing plus the $0.20 listing renewal = $0.45 (Etsy fees page, checked Oct 7, 2026). Set yours for eBay or others.",
               prompt_title="Fixed fee per order", error="Enter dollars, zero or more.")
K5.close()
# right: how to read
D.frame(db, K5_TOP, K5.end, "I", "N")
t = db[f"J{K5_TOP + 1}"]; t.value = "How to read the checks"; t.font = D.f(12, True); db.merge_cells(f"J{K5_TOP + 1}:M{K5_TOP + 1}")
t = db[f"J{K5_TOP + 2}"]
t.value = ("Losing money: the order costs more than it brings in. Thin: under 15% margin on the order. Etsy fees, "
           "checked Oct 7, 2026: 6.5% plus 3% + $0.25 on item and shipping, $0.20 listing.")
t.font = D.f(9, False, "ink2"); t.alignment = Alignment(vertical="top", wrap_text=True)
db.merge_cells(f"J{K5_TOP + 2}:M{K5.end - 1}")
DB_TOP = K5.end + 2
DB_FIRST = DB_TOP + 5
DB_LAST = DB_FIRST + N - 1
DB_TOT = DB_LAST + 1


def db_formula(kind):
    def fn(r):
        pr = prow(r - DB_FIRST)
        if kind == "name":
            return f'=IF({Q1}C{pr}="","",{Q1}C{pr})'
        if kind == "sale":
            return f'=IF(C{r}="","",{Q1}D{pr})'
        if kind == "ship":
            return f'=IF(C{r}="","",{Q1}E{pr})'
        if kind == "true":
            return f'=IF(C{r}="","",{Q1}P{pr})'
        if kind == "fees":
            return f'=IF(C{r}="","",F{r}*(D{r}+E{r})+$F${FIX})'
        if kind == "net":
            return f'=IF(C{r}="","",IF(ISNUMBER(H{r}),D{r}+E{r}-I{r}-G{r}-H{r},""))'
        if kind == "margin":
            return f'=IF(C{r}="","",IF(AND(ISNUMBER(J{r}),D{r}+E{r}>0),J{r}/(D{r}+E{r}),""))'
        if kind == "shipflag":
            return f'=IF(C{r}="","",{Q1}R{pr})'
        if kind == "flag":
            return f'=IF(C{r}="","",IF(NOT(ISNUMBER(J{r})),"",IF(J{r}<0,"Losing money",IF(K{r}<0.15,"Thin","OK"))))'
    return fn


cols_db = [
    dict(col="C", head="Product", kind="calc", formula=db_formula("name")),
    dict(col="D", head="Sale price", kind="calc", fmt=USD2, align="right", formula=db_formula("sale")),
    dict(col="E", head="Shipping charged", kind="calc", fmt=USD2, align="right", formula=db_formula("ship")),
    dict(col="F", head="Fee %", kind="input", fmt=PCT1, align="right", values=[f[0] for f in FEES] + [None] * (N - len(FEES)),
         validation=("decimal", 0, 0.6), prompt="Percent fees on item plus shipping. Etsy: 6.5% transaction plus 3% processing = 9.5%. Type a percent, for example 9.5%.",
         error="Enter a percent from 0% to 60%."),
    dict(col="G", head="Product cost", kind="input", fmt=USD2, align="right", values=[f[1] for f in FEES] + [None] * (N - len(FEES)),
         validation=("decimal", 0, None), prompt="What one item costs you to make or buy, in dollars.", error="Enter dollars, zero or more."),
    dict(col="H", head="True shipping cost", kind="calc", fmt=USD2, align="right", formula=db_formula("true")),
    dict(col="I", head="Fees", kind="calc", fmt=USD2, align="right", formula=db_formula("fees")),
    dict(col="J", head="Net profit per order", kind="calc", fmt=USD2, align="right", bold=True, formula=db_formula("net")),
    dict(col="K", head="Order margin", kind="calc", fmt=PCT, align="right", formula=db_formula("margin")),
    dict(col="L", head="Shipping check", kind="calc", formula=db_formula("shipflag")),
    dict(col="M", head="Profit check", kind="calc", formula=db_formula("flag")),
]
bf, bl, bend = D.table_card(db, DB_TOP, "B", "N", cols_db, N + 1, row_height=TROW, title="Every product",
                            sub="Yellow columns are yours. The rest fills in from tab 1.")
assert (bf, bl) == (DB_FIRST, DB_TOT), (bf, bl)
totals_row(db, DB_TOT, D.cols("C", "M"), "C", "Totals, one of each", [
    ("H", f"=SUM(H{DB_FIRST}:H{DB_LAST})", USD2), ("I", f"=SUM(I{DB_FIRST}:I{DB_LAST})", USD2),
    ("J", f"=SUM(J{DB_FIRST}:J{DB_LAST})", USD2)])
for rr in range(DB_FIRST, DB_LAST + 1):
    for k in "LM":
        db[f"{k}{rr}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
word_rule(db, f"L{DB_FIRST}:L{DB_LAST}", f"$L{DB_FIRST}", [("Under-recovered", "accent", "accent_tint"),
                                                          ("Covered", "teal", "teal_tint"), ("Enter postage", "gold", "input_fill")])
word_rule(db, f"M{DB_FIRST}:M{DB_LAST}", f"$M{DB_FIRST}", [("Losing money", "accent", "accent_tint"),
                                                          ("Thin", "gold", "input_fill"), ("OK", "teal", "teal_tint")])
neg_rule(db, f"J{DB_FIRST}:J{DB_TOT}", f"J{DB_FIRST}")
LOSING = f'COUNTIF($M${DB_FIRST}:$M${DB_LAST},"Losing money")'
THIN = f'COUNTIF($M${DB_FIRST}:$M${DB_LAST},"Thin")'
UNDER5 = f'COUNTIF($L${DB_FIRST}:$L${DB_LAST},"Under-recovered")'
COST_SUM = f"SUM($H${DB_FIRST}:$H${DB_LAST})"
COLL_SUM = f"SUM($E${DB_FIRST}:$E${DB_LAST})"
NETSHIP = f"{COLL_SUM}-{COST_SUM}"
DBN = f"COUNT($J${DB_FIRST}:$J${DB_LAST})"
v1, _, _ = D.tile(db, 6, "B", "G", "NET SHIPPING SHORTFALL, ONE OF EACH", f"={NETSHIP}", USD2,
                  f'="You collect "&TEXT({COLL_SUM},"$#,##0.00")&" and spend "&TEXT({COST_SUM},"$#,##0.00")&" shipping one of each"', dark=True)
v2, _, _ = D.tile(db, 6, "I", "N", "PRODUCTS LOSING MONEY", f"={LOSING}", INT,
                  f'=IF(COUNTIF($C${DB_FIRST}:$C${DB_LAST},"?*")=0,"No products yet",IF({DBN}=0,"No product has a full cost yet: enter postage on tab 1","of "&{DBN}&" priced products. "&{THIN}&" more with a thin margin, under 15%"))')
D.status_rule(db, v2.coordinate, f"{v2.coordinate}>0", fill_tint=False)
db.conditional_formatting.add(v1.coordinate, FormulaRule(formula=[f"{v1.coordinate}<0"], font=Font(color=D.T["accent_tint"] if False else "F08A66", bold=True), stopIfTrue=True))
D.h(db, 10, 14)
D.h(db, DB_STRIP - 1 + 0, 14)
D.h(db, 11, 10)
D.stat_strip(db, 12, [
    ("C:C", "Under-recovering", f"={UNDER5}", INT),
    ("D:E", "Avg true cost", f"={PAVG_TRUE}", USD2),
    ("F:G", "Avg shortfall", f"={PAVG_SHORT}", USD2),
    ("H:I", "Shipping cost", f"={COST_SUM}", USD2),
    ("J:K", "Shipping collected", f"={COLL_SUM}", USD2),
    ("L:M", "Postage share", f"={PAVG_SHARE}", PCT),
])
D.h(db, 14, 10)
D.frame(db, 11, 14, "B", "N")
neg_rule(db, "F13", "F13")
DB_LASTROW = bend + 1
pad_rows(db, DB_LASTROW); D.h(db, DB_LASTROW, 14)
S.page_break_before(db, DB_TOP)
D.paint_canvas(db, DB_LASTROW, "Z")
S.finish_sheet(db, PRODUCT, DB_LASTROW, span=("A", "O"), freeze="D11", tab_color="gold")
db.page_setup.orientation = "portrait"  # narrower than the other tables: portrait keeps all 30 rows on one page
db.page_setup.fitToHeight = 0

# =====================================================================  Start Here and Terms (card style, from #13)
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
            m = re.match(r"^([A-Z0-9][A-Za-z0-9 ,]{1,34})\. (.*)$", text, re.S) if kind in ("para", "num") else None
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
        Lc = sh[f"C{r}"]
        if kind == "num":
            Lc.value = left; Lc.font = D.f(18, True, "accent"); Lc.alignment = Alignment(horizontal="center", vertical="center")
        elif kind.startswith("chip"):
            Lc.value = left[0]; Lc.number_format = left[1]; Lc.alignment = Alignment(horizontal="center", vertical="center")
            if kind == "chip-in":
                Lc.fill = D.fill("input_fill"); Lc.font = D.f(9, True, "input_text")
                Lc.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
            elif kind == "chip-calc":
                Lc.font = D.f(9, False, "ink"); Lc.border = Border(bottom=D.side("hair"))
            else:
                Lc.fill = D.fill("ink"); Lc.font = D.f(9, True, "on_ink")
        D.h(sh, r, ht); r += 1
    D.h(sh, r, 12)
    D.frame(sh, top, r, "B", "F")
    return r + 2


MONEY_CLAUSE = ("Calculations are estimates for planning and depend on your inputs. They aren't accounting, tax or financial advice. "
                "Check fees, rates and interest against your own statements and the provider's current terms.")
NOTICE = ("For general information and planning only. This is not legal, tax, financial, medical or other professional advice, and using it "
          "doesn't create a professional relationship. Results are estimates based on the numbers you enter. Figures were checked "
          f"on {CHECKED} and can change. See the Terms tab before you rely on anything here. " + MONEY_CLAUSE)

sh = wb.create_sheet("Start Here", 0)
S.set_widths(sh, SH_GRID)
D.page_header(sh, PRODUCT, "Start here. Five working tabs, about 20 minutes with your own products.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
r = 6
r = sh_card(sh, r, "What it does", [(None,
    "Most shipping calculators stop at the label. This workbook adds the box, filler, tape, label and your packing time, "
    "checks what each carrier really bills once dim weight is counted, prices every product on USPS and UPS, tests free-shipping "
    "thresholds against your own order history, and shows which products lose money once the full parcel cost is in.", "para")])
r = sh_card(sh, r, "Five steps", [
    (1, "1 Parcel Costs. Set your hourly rate, then one row per product: prices, zone, packaging and packing minutes. About 10 minutes.", "num"),
    (2, "2 Dim Weight. Type each product's packed box size and weight. See what USPS, UPS and FedEx bill. About 5 minutes.", "num"),
    (3, "3 Free Shipping. Your average order, shipping charged, margin and three thresholds. Read the verdict row. About 3 minutes.", "num"),
    (4, "4 Services. Nothing to type: every product priced on every service, cheapest first. Add your own quotes if you have them.", "num"),
    (5, "5 Dashboard. Add fee percent and product cost per product, then read which products lose money once shipping is counted.", "num"),
])
r = sh_card(sh, r, "How to read the cells", [
    ((HOURLY, USD2), "Yellow cells with blue numbers are yours to change. Type over the example. Each one shows a hint when you select it.", "chip-in"),
    ((9.95, USD2), "Plain numbers are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((13.95, USD2), "Dark tiles are your answers. They sit at the top of every working tab and stay on screen as you scroll.", "chip-key"),
    (None, "Each tab is protected without a password. To change anything else, use Review, Unprotect Sheet in Excel, or Data, "
           "Protect sheets and ranges in Google Sheets.", "note"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "The example: a 10-product sample shop", [
    (None, "Ceramic mug. $4.95 shipping charged on a parcel that really costs $13.19 once the box, filler and 6 minutes of packing "
           "are in. UPS bills it 3 lb for a 1.1 lb mug.", "para"),
    (None, "Grapevine wreath. 2.5 lb on the scale, 15 lb to USPS because the box is over a cubic foot: a $21.15 label instead of $11.57.", "para"),
    (None, "Framed print. Under a cubic foot, so USPS bills the scale weight (4 lb); UPS and FedEx bill 6 lb for the same box. "
           "Charging $12 leaves a $10.47 gap.", "para"),
    (None, "Earrings. Free shipping, so the shortfall shows the whole $9.76, which the $42 price has to cover. It does, comfortably.", "para"),
    (None, "Soap set. Covered by 20 cents at $9.95, which shows how thin covered can be. The wooden puzzle is covered at zone 4; "
           "change it to zone 8 and watch it flip.", "para"),
    (None, "Across the shop. Shipping one of each costs $139.51 and brings in $93.60, a $45.91 shortfall. Free shipping over $75 "
           "beats charging shipping by about $396 per 100 orders on the sample assumptions.", "para"),
])
r = sh_card(sh, r, "Good to know", [
    (None, "Your own shop. Type over the sample on tab 1 (columns Product to Pack min), tab 2 (box sizes and weights) and the "
           "two yellow columns on tab 5. To start empty, select those yellow cells and press Delete. Every other tab reads from them.", "para"),
    (None, "Rates. Tab 4 carries USPS Notice 123 prices effective July 12, 2026 and UPS Ground Saver 2026 daily rates, checked "
           f"{CHECKED}. USPS adds temporary holiday prices from Oct 4, 2026 to Jan 17, 2027: set Add USPS holiday prices on tab 4 to Yes "
           "to include them. When a carrier changes prices, type the new ones into the yellow rate tables and every comparison updates.", "para"),
    (None, "More than 30 products. Save a second copy of the workbook for the next 30.", "para"),
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. Built for Excel and Google Sheets "
           "with plain formulas; no macros, no add-ons, no sign-up. It doesn't print labels, buy postage or connect to any carrier.", "para"),
])
r = sh_card(sh, r, "Before you rely on a number", [(None, NOTICE, "note")])
pad_rows(sh, r - 1, 12)
D.paint_canvas(sh, r - 1, "Z")
S.finish_sheet(sh, PRODUCT, r - 1, span=("A", "G"), tab_color="teal")

tm = wb.create_sheet("Terms")
S.set_widths(tm, SH_GRID)
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version {VERSION}. Read this before you rely on a number.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
paras = open(os.path.join(HERE, "LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().strip().split("\n\n")[1:]
r = 6
r = sh_card(tm, r, "More from the shop", [
    (None, ("Etsy Profit Calculator: true margin and payout check for Etsy sellers", "https://www.etsy.com/listing/4584721212"), "link"),
    (None, ("Inventory Reorder Planner: cash-aware stock planning", "https://www.etsy.com/listing/4585004344"), "link"),
    (None, ("Everything in the shop: etsy.com/shop/ProofNotFluff", "https://www.etsy.com/shop/ProofNotFluff"), "link"),
])
S.page_break_before(tm, r)
r = sh_card(tm, r, "Terms of Use and disclaimer", [(None, pp, "para") for pp in paras])
r = sh_card(tm, r, "A small ask", [
    (None, "If this workbook helped you price your shipping, a short review on Etsy helps other sellers find it. Thank you.", "para"),
])
pad_rows(tm, r - 1, 12)
D.paint_canvas(tm, r - 1, "Z")
S.finish_sheet(tm, PRODUCT, r - 1, span=("A", "G"), tab_color="note")

wb.active = 0
problems = [pp for pp in S.audit(wb) if "input without validation" not in pp]
if problems:
    print("AUDIT:", *problems, sep="\n  ")
wb.save(OUT)
print("saved", OUT)
print({"P_FIRST": P_FIRST, "P_AVG": P_AVG, "HR": HR, "D_FIRST": D_FIRST, "DV": (DV_USPS, DV_TH, DV_UPS), "SC_FIRST": SC_FIRST,
       "FUEL": FUEL, "HOL": HOL, "HOLR": HOLR, "RT": {k: v[1:3] for k, v in RT.items()}, "SVC": SVC_FIRST, "DB_FIRST": DB_FIRST,
       "DB_TOT": DB_TOT, "FIX": FIX, "FS": dict(AOV=AOV, SHIP=SHIP, TC=TC, TCO=TCO, TCU=TCU, MRG=MRG, LIFT=LIFT, PROF=F_PROF,
       COST=F_COST, BE=F_BE, REC=REC, **SROWS)})
