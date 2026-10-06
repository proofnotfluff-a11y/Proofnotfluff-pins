#!/usr/bin/env python3
"""#5 True Profit System for Etsy Sellers, version 3 (dashboard design, Oct 6, 2026).

Same inputs, formulas and worked example (a small candle shop, September 2026) as the
live v1 file Etsy-True-Profit-System.xlsx (Sep 29, 2026), rebuilt to
design/WORKBOOK_STANDARD.md section 0. tools/compare_xlsx.py with compare_map.json proves
the answers match. v1's seven working tabs become six: the Offsite Ads shock model now sits
on the Listings tab under the listing table, because it reads the same SKUs.

Fixes in v3 (declared in compare_map.json "intended" where an answer changes):
- Dashboard monthly table: a blank first month showed #VALUE! in eleven rows in Excel (2000-01 and on in
  LibreOffice); now those rows are blank.
- Pricing: a target margin plus fee rates of 100% or more (or fee rates alone of 100% or more)
  gave a negative or #DIV/0! list price; now blank with a plain status line.
- Payouts status said "Reconciled" with no deposits entered; it now says none are entered.
- Dashboard tax reserve no longer goes negative when profit is negative (MAX of 0).
- A blank Offsite Ads tier now uses the 15% rate (v1 fell to 12%).
- Payouts holds 26 deposit rows (a year of twice-monthly deposits; v1 had 40) so printing has no bare pages.
- Payouts example note said 12 orders; Sep 1 to 14 holds 13.
- Fees re-checked on Etsy's Fees & Payments Policy (updated Oct 5, 2026) and help pages,
  and the IRS estimated tax due dates, Oct 6, 2026; full Terms of Use tab; every tab
  protected without a password; validation and an input message on every input.

Usage: python3 engines/etsy-true-profit/build_xlsx.py out.xlsx
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
from openpyxl.worksheet.datavalidation import DataValidation  # noqa: E402

PRODUCT = "True Profit System for Etsy Sellers"
CHECKED = "Oct 6, 2026"
AS_OF = f"Fees checked {CHECKED}"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else "True-Profit-System-for-Etsy-Sellers.xlsx"
USD0, USD2, PCT, INT = S.FMT["usd0"], S.FMT["usd2"], S.FMT["pct"], S.FMT["int"]
PCT1, DATE, TXT = "0.0%", S.FMT["date"], "@"
PTS = '0.0" pts";-0.0" pts"'
TAX_SOURCES = "the IRS estimated tax page (irs.gov, Estimated taxes, individuals)"

# ---------------------------------------------------------------- example data (v1, unchanged)
SHOP, CURRENCY, TARGET = "Willow & Wick Candle Co.", "USD", 0.30
FEES = [  # name, label, value, fmt, applies to, prompt, validation
    ("TransactionFee", "Transaction fee", 0.065, PCT1, "item + shipping",
     "6.5% of item price plus the shipping you charge (and gift wrap). Not charged on US sales tax. Etsy Fees & Payments Policy, checked " + CHECKED + ".",
     ("decimal", 0, 0.5)),
    ("ListingFee", "Listing fee", 0.20, USD2, "listing and renewal",
     "$0.20 when a listing is created or renews, and again after each sale of a multi-quantity listing (auto-renew). Checked " + CHECKED + ".",
     ("decimal", 0, 5)),
    ("ProcessingRate", "Processing, percent", 0.03, PCT1, "item + shipping + tax",
     "US rate 3% of the total the buyer paid, sales tax included. Rates differ outside the US: type yours. Etsy help, checked " + CHECKED + ".",
     ("decimal", 0, 0.5)),
    ("ProcessingFixed", "Processing, per order", 0.25, USD2, "each order",
     "US fixed part: $0.25 per order. Rates differ outside the US: type yours. Etsy help, checked " + CHECKED + ".",
     ("decimal", 0, 5)),
    ("AdsRateUnder", "Offsite Ads, under $10K", 0.15, PCT1, "item + shipping",
     "15% of item plus shipping on an order attributed to an Offsite Ad, for shops under $10K in 365 days. Checked " + CHECKED + ".",
     ("decimal", 0, 0.5)),
    ("AdsRateOver", "Offsite Ads, $10K or more", 0.12, PCT1, "item + shipping",
     "12% once a shop reaches $10K in any 365 days; from then on Offsite Ads are required for the life of the shop. Checked " + CHECKED + ".",
     ("decimal", 0, 0.5)),
    ("AdsThreshold", "Offsite Ads threshold", 10000, USD0, "sales in 365 days",
     "Under this in 365 days: 15% and you can opt out. At or over it: 12% and you can't. Checked " + CHECKED + ".",
     ("decimal", 0, None)),
    ("AdsCap", "Offsite Ads cap per order", 100, USD0, "most per order",
     "The Offsite Ads fee on one order never goes over this. Etsy help, checked " + CHECKED + ".",
     ("decimal", 0, None)),
]
LISTINGS = [("8 oz Soy Candle", 24, 6.1, 3, 5.5, 6.25, 1.1, "N"), ("Wax Melt 6-Pack", 12, 2.4, 1.5, 4, 4.6, 0.6, "Y"),
            ("3-Wick Candle 14 oz", 44, 9.8, 4, 6.5, 7.4, 1.6, "N"), ("Candle Gift Set (3)", 52, 14.5, 6, 8, 9.1, 2.4, "N"),
            ("Room Spray 4 oz", 16, 4.2, 2.2, 4.5, 5.1, 0.7, "N")]
N_LIST = 20
ORDERS = [('2026-09-01', '3381000', '8 oz Soy Candle', 1, 24, 5.5, 0, 'N'), ('2026-09-02', '3381137', '3-Wick Candle 14 oz', 1, 44, 6.5, 3.54, 'N'),
          ('2026-09-03', '3381274', 'Wax Melt 6-Pack', 2, 24, 6, 1.88, 'Y'), ('2026-09-04', '3381411', '8 oz Soy Candle', 2, 48, 7.5, 0, 'N'),
          ('2026-09-05', '3381548', 'Room Spray 4 oz', 1, 16, 4.5, 1.64, 'N'), ('2026-09-06', '3381685', 'Candle Gift Set (3)', 1, 52, 8, 0, 'Y'),
          ('2026-09-07', '3381822', '8 oz Soy Candle', 1, 24, 5.5, 0, 'N'), ('2026-09-08', '3381959', '8 oz Soy Candle', 1, 24, 5.5, 1.77, 'N'),
          ('2026-09-09', '3382096', '3-Wick Candle 14 oz', 1, 44, 6.5, 0, 'N'), ('2026-09-10', '3382233', 'Wax Melt 6-Pack', 1, 12, 4, 1.16, 'N'),
          ('2026-09-11', '3382370', '8 oz Soy Candle', 1, 24, 5.5, 0, 'Y'), ('2026-09-12', '3382507', 'Room Spray 4 oz', 2, 32, 6.5, 0, 'N'),
          ('2026-09-13', '3382644', '3-Wick Candle 14 oz', 2, 88, 8.5, 8.44, 'N'), ('2026-09-15', '3382781', 'Candle Gift Set (3)', 1, 52, 8, 0, 'N'),
          ('2026-09-17', '3382918', '8 oz Soy Candle', 1, 24, 5.5, 2.07, 'N'), ('2026-09-18', '3383055', 'Wax Melt 6-Pack', 3, 36, 8, 0, 'Y'),
          ('2026-09-20', '3383192', '3-Wick Candle 14 oz', 1, 44, 6.5, 0, 'N'), ('2026-09-22', '3383329', '8 oz Soy Candle', 2, 48, 7.5, 3.33, 'N'),
          ('2026-09-24', '3383466', 'Room Spray 4 oz', 1, 16, 4.5, 0, 'N'), ('2026-09-26', '3383603', 'Candle Gift Set (3)', 1, 52, 8, 4.95, 'Y')]
N_ORD = 200
PAYOUTS = [('2026-09-16', 412.57, '2026-09-01', '2026-09-14', 47.38, 0), ('2026-09-30', 238.08, '2026-09-15', '2026-09-28', 31.86, 0)]
N_PAY = 26
QUARTERS = [("Q1 (Jan to Mar)", "2026-04-15", "Yes", 180), ("Q2 (Apr to May)", "2026-06-15", "Yes", 165),
            ("Q3 (Jun to Aug)", "2026-09-15", "Yes", 210), ("Q4 (Sep to Dec)", "2027-01-15", "No", None)]
d = lambda s: dt.datetime.strptime(s, "%Y-%m-%d")  # noqa: E731

wb = S.new_workbook(PRODUCT, version="3")
GRID = {"A": 3, "B": 2, "C": 31, "D": 14, "E": 2, "F": 3, "G": 2, "H": 24, "I": 12, "J": 17, "K": 2, "L": 3}


def rich_notes(ws, top, notes, span=("C", "J"), frame_span=("B", "K"), title="Notes and sources"):
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


def fill_heights(ws, last):
    for rr in range(1, last + 1):
        if ws.row_dimensions[rr].height is None:
            D.h(ws, rr, D.GRID_ROW)


def word_rules(ws, rng, first_cell, words):
    for word, color, tint in words:
        ws.conditional_formatting.add(rng, FormulaRule(formula=[f'{first_cell}="{word}"'], font=Font(color=D.T[color], bold=True),
                                                       fill=PatternFill("solid", bgColor=D.T[tint]), stopIfTrue=True))


FLAG_WORDS = (("REPRICE", "accent", "accent_tint"), ("WATCH", "gold", "input_fill"), ("OK", "teal", "teal_tint"))
NOTICE = ("For general information and planning only. This is not legal, tax, financial, medical or other professional advice, "
          "and using it doesn't create a professional relationship. Results are estimates based on the numbers you enter. "
          f"Figures were checked on {CHECKED} and can change. See the Terms tab before you rely on anything here.")

# =====================================================================  1 Setup
su = wb.create_sheet("1 Setup")
S.set_widths(su, GRID)
D.page_header(su, "Setup", "Your target margin and Etsy's fees, set once. Every other tab reads from here.", AS_OF)
TOP = 11
A = D.Card(su, TOP, "B", "C", "D", "E", wb=wb)
A.title("Your shop", "Type over the yellow cells. Every tab updates.")
A.eyebrow("SHOP NAME")
SN = A._row()
c = S.input_cell(su, f"C{SN}", SHOP, TXT, name="ShopName", wb=wb, validation=("textLength", 0, 60),
                 prompt_title="Shop name", prompt="Your Etsy shop name, up to 60 characters. Used only as a label.")
c.font = D.f(11, True, "input_text"); c.fill = D.fill("input_fill")
c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
for k in ("C", "D"):
    cc = su[f"{k}{SN}"]; cc.fill = D.fill("input_fill")
    cc.border = Border(top=D.side("input_line"), bottom=D.side("input_line"),
                       left=D.side("input_line") if k == "C" else None, right=D.side("input_line") if k == "D" else None)
su.merge_cells(f"C{SN}:D{SN}")
CUR = A.input("Currency", CURRENCY, TXT, name="Currency", validation=("textLength", 0, 10),
              prompt="A label only, for example USD. To change the symbol on money cells, use Format, Number.")
TM = A.input("Target profit margin", TARGET, PCT1, name="TargetMargin", validation=("decimal", 0, 0.9),
             prompt="Net profit divided by revenue (item plus shipping charged). 30% is a common floor for handmade goods. Type a percent.")
A.eyebrow("OFFSITE ADS")
TIER = A.input("Your Offsite Ads tier", "Under $10K", TXT, name="AdsTier", validation=("list", ["Under $10K", "$10K or more"]),
               prompt="Under $10K if your shop has never made $10,000 in any 365 days. Otherwise $10K or more.",
               prompt_title="Offsite Ads tier")
su[f"D{TIER}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
A.close()

B = D.Card(su, TOP, "G", "H", "I", "K", extra="J", wb=wb)
B.title("Etsy fee table", "Etsy's US fees. Change a cell when Etsy changes a fee.")
FEE = {}
for name, lab, val, fmt, applies, prompt, val_rule in FEES:
    rr = B.input(lab, val, fmt, name=name, validation=val_rule, prompt=prompt, prompt_title=lab[:32])
    n = su[f"J{rr}"]; n.value = applies; n.font = D.f(9, False, "muted")
    n.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    FEE[name] = f"'1 Setup'!$I${rr}"
B.eyebrow("USED IN EVERY TAB")
ADS = B.calc("Offsite Ads rate applied", f'=IF($D${TIER}="$10K or more",$I${FEE["AdsRateOver"].split("$")[-1]},$I${FEE["AdsRateUnder"].split("$")[-1]})',
             PCT1, total=True, tint="total_tint")
B.close()
FEE["AdsRate"] = f"'1 Setup'!$I${ADS}"
FEE["Target"] = f"'1 Setup'!$D${TM}"
S.define_name(wb, "AdsRate", su, f"I{ADS}")

D.tile(su, 6, "B", "E", "OFFSITE ADS RATE USED IN EVERY TAB", f"=$I${ADS}", PCT1,
       f'=IF($D${TIER}="","Pick your Offsite Ads tier under Your shop.","Tier: "&$D${TIER}&". Capped at "&TEXT($I${FEE["AdsCap"].split("$")[-1]},"$#,##0")&" an order.")', dark=True)
D.tile(su, 6, "G", "K", "YOUR TARGET PROFIT MARGIN", f"=$D${TM}", PCT1,
       '="Listings under it show WATCH. Five points under shows REPRICE."')
D.h(su, 10, 14)

n_top = max(A.end, B.end) + 2
SU_NOTES = [
    ("Where the fees come from", "Etsy's Fees & Payments Policy (etsy.com/legal/fees, updated Oct 5, 2026): $0.20 listing fee, "
     "auto-renewed at $0.20 after each sale of a multi-quantity listing; 6.5% transaction fee on item price plus shipping and gift wrap, "
     "not on US sales tax. Etsy help, Payment processing fees: US shops pay 3% plus $0.25, on the total including shipping and sales tax. "
     f"Etsy help, How Etsy's Offsite Ads Work: 15%, or 12% once a shop reaches $10,000 in 365 days, at most $100 an order. Checked {CHECKED}."),
    ("Outside the US", "Processing fees vary by the country of your bank account, and some countries add a regulatory operating fee. "
     "Type your own rates into the fee table."),
    ("When Etsy changes a fee", "Etsy announces fee changes to sellers before they take effect. Re-check each January and after any "
     "policy email, change the yellow cell, and every tab updates."),
    ("Before you rely on a number", NOTICE),
]
n_end = rich_notes(su, n_top, SU_NOTES)
S.page_break_before(su, n_top)
D.h(su, n_end + 1, 14)
fill_heights(su, n_end)
D.paint_canvas(su, n_end + 1, "Z")
S.finish_sheet(su, PRODUCT, n_end + 1, span=("A", "L"), freeze="A11", tab_color="teal")
TF, LF, PR, PF, CAP, AR, TG = (FEE[k] for k in ("TransactionFee", "ListingFee", "ProcessingRate", "ProcessingFixed", "AdsCap", "AdsRate", "Target"))

# =====================================================================  2 Listings
li = wb.create_sheet("2 Listings")
S.set_widths(li, {"A": 3, "B": 2, "C": 22, "D": 10, "E": 11, "F": 10, "G": 10, "H": 10, "I": 11, "J": 9, "K": 11, "L": 11, "M": 11,
                  "N": 10, "O": 11, "P": 11, "Q": 11, "R": 11, "S": 10, "T": 12, "U": 2, "V": 3})
D.page_header(li, "Listings", "True profit on every listing after Etsy's fees, and what an Offsite Ads sale does to it.", AS_OF,
              span=("B", "U"), side_cols=5)
L_TOP = 11
l_first = L_TOP + 5
l_last = l_first + N_LIST - 1
LR = {k: f"${k}${l_first}:${k}${l_last}" for k in "CDEFGHIJKLMNOPQRST"}
D.h(li, 6, 10)
D.stat_strip(li, 7, [
    ("C:D", "Listings entered", f'=COUNTIF({LR["C"]},"?*")', INT),
    ("E:H", "Flagged reprice", f'=COUNTIF({LR["T"]},"REPRICE")', INT),
    ("I:L", "Flagged watch", f'=COUNTIF({LR["T"]},"WATCH")', INT),
    ("M:P", "Your target margin", f"={TG}", PCT1),
    ("Q:T", "Offsite Ads rate applied", f"={AR}", PCT1),
])
D.h(li, 9, 10)
D.frame(li, 6, 9, "B", "U")
D.status_rule(li, "E8", "E8>0", fill_tint=False)
D.h(li, 10, 14)


def lc(kind):
    def fn(r):
        g = f'IF(C{r}="","",'
        return {
            "rev": f'={g}D{r}+G{r})',
            "tf": f"={g}{TF}*(D{r}+G{r}))",
            "pf": f"={g}{PR}*(D{r}+G{r})+{PF})",
            "lf": f"={g}{LF})",
            "ad": f'={g}IF(J{r}="Y",MIN({AR}*(D{r}+G{r}),{CAP}),0))',
            "fees": f"={g}L{r}+M{r}+N{r}+O{r})",
            "cost": f"={g}E{r}+F{r}+H{r}+I{r})",
            "profit": f"={g}K{r}-P{r}-Q{r})",
            "margin": f"={g}IF(K{r}>0,R{r}/K{r},0))",
            "flag": f'={g}IF(S{r}<{TG}-0.05,"REPRICE",IF(S{r}<{TG},"WATCH","OK")))',
        }[kind]
    return fn


money_in = dict(fmt=USD2, align="right", validation=("decimal", 0, None), error="Enter 0 or more, in dollars, for example 6.10.")
cols_l = [
    dict(col="C", head="Listing or SKU", kind="input", values=[x[0] for x in LISTINGS], validation=("textLength", 0, 40),
         prompt="A short name you will recognise. It feeds the SKU list on the Orders tab.", error="Up to 40 characters."),
    dict(col="D", head="List price", kind="input", values=[x[1] for x in LISTINGS], prompt="Your listing price for one item, in dollars.", **money_in),
    dict(col="E", head="Materials", kind="input", values=[x[2] for x in LISTINGS], prompt="Materials for one item, in dollars.", **money_in),
    dict(col="F", head="Labor cost", kind="input", values=[x[3] for x in LISTINGS],
         prompt="What you pay yourself per item. Even $2: a margin that only works because your time is free is not a margin.", **money_in),
    dict(col="G", head="Shipping charged", kind="input", values=[x[4] for x in LISTINGS], prompt="Shipping the buyer pays you. 0 for free shipping.", **money_in),
    dict(col="H", head="Actual shipping", kind="input", values=[x[5] for x in LISTINGS], prompt="What the label really costs you.", **money_in),
    dict(col="I", head="Packaging", kind="input", values=[x[6] for x in LISTINGS], prompt="Box, mailer, tissue, tape, insert card.", **money_in),
    dict(col="J", head="Offsite Ads? Y/N", kind="input", align="center", values=[x[7] for x in LISTINGS], validation=("list", ["Y", "N"]),
         prompt="Y to price this listing as if the sale came through an Offsite Ad.", error="Pick Y or N."),
    dict(col="K", head="Revenue", kind="calc", fmt=USD2, align="right", formula=lc("rev")),
    dict(col="L", head="Transaction fee", kind="calc", fmt=USD2, align="right", formula=lc("tf")),
    dict(col="M", head="Processing fee", kind="calc", fmt=USD2, align="right", formula=lc("pf")),
    dict(col="N", head="Listing fee", kind="calc", fmt=USD2, align="right", formula=lc("lf")),
    dict(col="O", head="Offsite Ads fee", kind="calc", fmt=USD2, align="right", formula=lc("ad")),
    dict(col="P", head="Total Etsy fees", kind="calc", fmt=USD2, align="right", formula=lc("fees")),
    dict(col="Q", head="Total costs", kind="calc", fmt=USD2, align="right", formula=lc("cost")),
    dict(col="R", head="Net profit", kind="calc", fmt=USD2, align="right", bold=True, formula=lc("profit")),
    dict(col="S", head="Margin", kind="calc", fmt=PCT1, align="right", bold=True, formula=lc("margin")),
    dict(col="T", head="Flag", kind="calc", align="center", formula=lc("flag")),
]
f1, f2, l_end = D.table_card(li, L_TOP, "B", "U", cols_l, N_LIST, title="Your listings",
                             sub="One row per listing. Yellow columns are yours. Processing fee here leaves out sales tax, which depends on "
                                 "the buyer's state; the Orders tab uses the real tax on each order.")
assert (f1, f2) == (l_first, l_last)
for r in range(l_first, l_last + 1):
    li[f"C{r}"].alignment = Alignment(horizontal="left", vertical="center", indent=1)
word_rules(li, f"T{l_first}:T{l_last}", f"$T{l_first}", FLAG_WORDS)
for formula, color in ((f'AND($S{l_first}<>"",$S{l_first}<{TG}-0.05)', "accent"),
                       (f'AND($S{l_first}<>"",$S{l_first}<{TG},$S{l_first}>={TG}-0.05)', "gold"),
                       (f'AND($S{l_first}<>"",$S{l_first}>={TG})', "teal")):
    li.conditional_formatting.add(f"S{l_first}:S{l_last}", FormulaRule(formula=[formula], font=Font(color=D.T[color], bold=True), stopIfTrue=True))
LST = "'2 Listings'!"

# ---- Offsite Ads check (v1 AdsShock tab), same SKUs
a_top = l_end + 2
S.page_break_before(li, a_top)
D.h(li, a_top, 12)
r = a_top + 1
t = li[f"C{r}"]; t.value = "Offsite Ads check"; t.font = D.f(12, True); li.merge_cells(f"C{r}:T{r}"); D.h(li, r, 24); r += 1
t = li[f"C{r}"]; t.value = ("What one ad-attributed sale does to each listing, and your blended margin at the share of orders that come "
                            "through Offsite Ads. Find your share in Shop Manager, Stats, Offsite Ads.")
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top", wrap_text=True); li.merge_cells(f"C{r}:T{r}"); D.h(li, r, 18); r += 1
D.h(li, r, 8); r += 1
STRIP = r
a_first = STRIP + 2 + 1 + 1 + 1  # strip (2 rows), gap, header row offset handled below
D.stat_strip(li, STRIP, [
    ("C:D", "Share of orders via Offsite Ads", "", PCT1),
    ("E:H", "Blended margin, no ad sales", "", PCT1),
    ("I:L", "At your ad share", "", PCT1),
    ("M:P", "If every sale were an ad sale", "", PCT1),
    ("Q:T", "Listings to opt out or reprice", "", INT),
])
SHARE = f"C{STRIP + 1}"
c = S.input_cell(li, SHARE, 0.3, PCT1, name="AdsShare", wb=wb, validation=("decimal", 0, 1),
                 prompt_title="Share via Offsite Ads", prompt="Share of your orders that come through Offsite Ads. Most shops land between 10% and 40%. Type a percent.")
c.font = D.f(18, True, "input_text"); c.fill = D.fill("input_fill"); c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
for k in ("C", "D"):
    cc = li[f"{k}{STRIP + 1}"]; cc.fill = D.fill("input_fill")
    cc.border = Border(top=D.side("input_line"), bottom=D.side("input_line"),
                       left=D.side("input_line") if k == "C" else None, right=D.side("input_line") if k == "D" else None)
r = STRIP + 2
D.h(li, r, 8); r += 1
head = r
a_first = head + 1
a_last = a_first + N_LIST - 1


def ac(kind):
    def fn(rr):
        src = l_first + (rr - a_first)
        g = f'IF($C${src}="","",'
        return {
            "sku": f"={g}$C${src})",
            "rev": f"={g}$K${src})",
            "p0": f"={g}$K${src}-$L${src}-$M${src}-$N${src}-$Q${src})",
            "m0": f"={g}IF(D{rr}>0,E{rr}/D{rr},0))",
            "fee": f"={g}MIN({AR}*D{rr},{CAP}))",
            "p1": f"={g}E{rr}-G{rr})",
            "m1": f"={g}IF(D{rr}>0,H{rr}/D{rr},0))",
            "pts": f"={g}(I{rr}-F{rr})*100)",
            "chg": f"={g}-G{rr})",
            "dec": f'={g}IF(I{rr}<{TG}-0.05,"OPT OUT OR REPRICE",IF(I{rr}<{TG},"WATCH","OK")))',
        }[kind]
    return fn


# header and body drawn by hand so the table sits under the strip inside one card
cols_a = [("C", "Listing or SKU", "sku", None, "left"), ("D", "Revenue", "rev", USD2, "right"), ("E", "Net profit, no ads", "p0", USD2, "right"),
          ("F", "Margin, no ads", "m0", PCT1, "right"), ("G", "Ads fee if attributed", "fee", USD2, "right"),
          ("H", "Net profit if ad sale", "p1", USD2, "right"), ("I", "Margin if ad sale", "m1", PCT1, "right"),
          ("J", "Margin change", "pts", PTS, "right"), ("K", "Profit change", "chg", USD2, "right")]
for col, hd, *_ in cols_a:
    cc = li[f"{col}{head}"]; cc.value = hd.upper(); cc.font = D.f(8, True, "muted")
    cc.alignment = Alignment(horizontal=_[2], vertical="bottom", wrap_text=True)
dec_cols = D.cols("L", "T")
cc = li[f"L{head}"]; cc.value = "DECISION"; cc.font = D.f(8, True, "muted"); cc.alignment = Alignment(horizontal="left", vertical="bottom", indent=1)
li.merge_cells(f"L{head}:T{head}")
for k in D.cols("C", "T"):
    li[f"{k}{head}"].border = Border(bottom=D.side("ink"))
D.h(li, head, 30)
for rr in range(a_first, a_last + 1):
    D.h(li, rr, D.GRID_ROW)
    for col, hd, kind, fmt, al in cols_a:
        cc = li[f"{col}{rr}"]; cc.value = ac(kind)(rr)
        if fmt:
            cc.number_format = fmt
        cc.font = D.f(10, kind in ("p1", "m1")); cc.alignment = Alignment(horizontal=al, vertical="center", indent=1 if al == "left" else 0)
    cc = li[f"L{rr}"]; cc.value = ac("dec")(rr); cc.font = D.f(10, True)
    cc.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    li.merge_cells(f"L{rr}:T{rr}")
    for k in D.cols("C", "T"):
        li[f"{k}{rr}"].border = Border(bottom=D.side("hair"))
word_rules(li, f"L{a_first}:T{a_last}", f"$L{a_first}", (("OPT OUT OR REPRICE", "accent", "accent_tint"), ("WATCH", "gold", "input_fill"), ("OK", "teal", "teal_tint")))
for formula, color in ((f'AND($I{a_first}<>"",$I{a_first}<{TG}-0.05)', "accent"),
                       (f'AND($I{a_first}<>"",$I{a_first}<{TG},$I{a_first}>={TG}-0.05)', "gold"),
                       (f'AND($I{a_first}<>"",$I{a_first}>={TG})', "teal")):
    li.conditional_formatting.add(f"I{a_first}:I{a_last}", FormulaRule(formula=[formula], font=Font(color=D.T[color], bold=True), stopIfTrue=True))
AD = {k: f"{k}{a_first}:{k}{a_last}" for k in "DEFGHIJKL"}
SV = STRIP + 1
li[f"E{SV}"] = f'=IF(SUM({AD["D"]})>0,SUM({AD["E"]})/SUM({AD["D"]}),0)'
li[f"I{SV}"] = f'=IF(SUM({AD["D"]})>0,(SUM({AD["E"]})-$C${SV}*SUM({AD["G"]}))/SUM({AD["D"]}),0)'
li[f"M{SV}"] = f'=IF(SUM({AD["D"]})>0,SUM({AD["H"]})/SUM({AD["D"]}),0)'
li[f"Q{SV}"] = f'=COUNTIF({AD["L"]},"OPT OUT OR REPRICE")'
D.status_rule(li, f"Q{SV}", f"Q{SV}>0", fill_tint=False)
a_note = a_last + 1
cc = li[f"C{a_note}"]
cc.value = ("Decision rule: a listing that turns red here should be opted out of Offsite Ads (possible only under $10K in sales) or "
            "repriced at the Pricing tab's ad-sale price. Blended margins weight every listing equally; the Orders tab has your real mix.")
cc.font = D.f(9, False, "muted"); cc.alignment = Alignment(vertical="center", wrap_text=True); li.merge_cells(f"C{a_note}:T{a_note}")
D.h(li, a_note, 32)
a_end = a_note + 1
D.h(li, a_end, 14)
D.frame(li, a_top, a_end, "B", "U")
fill_heights(li, a_end)
D.paint_canvas(li, a_end + 1, "Z")
S.finish_sheet(li, PRODUCT, a_end + 1, span=("A", "V"), freeze="A10", tab_color="accent")
li.page_setup.orientation = "landscape"
ADS_SV = SV

# =====================================================================  3 Pricing
pr = wb.create_sheet("3 Pricing")
S.set_widths(pr, GRID)
D.page_header(pr, "Pricing", "Start from the profit or margin you want and get the list price that delivers it after every fee.", AS_OF)
TOP = 11
PA = D.Card(pr, TOP, "B", "C", "D", "E", wb=wb)
PA.title("Set a profit per unit", "The list price that leaves this profit after fees.")
A6 = PA.input("Net profit you want per unit", 8, USD2, name="ProfitWanted", validation=("decimal", 0, None),
              prompt="What you want to keep from one sale after fees and costs, in dollars. Example: 8.", prompt_title="Profit per unit")
A7 = PA.input("Materials (COGS)", 6.1, USD2, validation=("decimal", 0, None), prompt="Materials for one item, in dollars.")
A8 = PA.input("Labor cost", 3, USD2, validation=("decimal", 0, None), prompt="What you pay yourself per item, in dollars.")
A9 = PA.input("Shipping you charge the buyer", 5.5, USD2, validation=("decimal", 0, None), prompt="Shipping the buyer pays. 0 for free shipping.",
              prompt_title="Shipping charged")
A10 = PA.input("Actual shipping cost", 6.25, USD2, validation=("decimal", 0, None), prompt="What the label really costs you.")
A11 = PA.input("Packaging cost", 1.1, USD2, validation=("decimal", 0, None), prompt="Box, mailer, tissue, tape, insert card.")
PA.close()

PB = D.Card(pr, PA.end + 2, "B", "C", "D", "E", wb=wb)
PB.title("Set a margin", "The list price that hits your target margin.")
B20 = PB.calc("Target margin, from Setup", f"={TG}", PCT1, bold=True)
B21 = PB.input("Materials (COGS)", 9.8, USD2, validation=("decimal", 0, None), prompt="Materials for one item, in dollars.")
B22 = PB.input("Labor cost", 4, USD2, validation=("decimal", 0, None), prompt="What you pay yourself per item, in dollars.")
B23 = PB.input("Shipping you charge the buyer", 6.5, USD2, validation=("decimal", 0, None), prompt="Shipping the buyer pays. 0 for free shipping.",
               prompt_title="Shipping charged")
B24 = PB.input("Actual shipping cost", 7.4, USD2, validation=("decimal", 0, None), prompt="What the label really costs you.")
B25 = PB.input("Packaging cost", 1.6, USD2, validation=("decimal", 0, None), prompt="Box, mailer, tissue, tape, insert card.")
PB.close()

RA = D.Card(pr, TOP, "G", "H", "I", "K", extra="J", wb=wb)
RA.title("Your price for that profit", "Fees are a share of price plus shipping, so the sum solves backwards.")
ca_costs = RA.calc("Costs plus fixed fees", f"=$D${A6}+$D${A7}+$D${A8}+$D${A10}+$D${A11}+{LF}+{PF}", USD2)
pr[f"H{ca_costs}"] = "Profit, costs and fixed fees"
FIXED_A = f"($D${A6}+$D${A7}+$D${A8}+$D${A10}+$D${A11}+{LF}+{PF})"
DEN_A = f"(1-{TF}-{PR})"
DEN_A2 = f"(1-{TF}-{PR}-{AR})"
ra13 = RA.calc("List price, no Offsite Ads", f'=IF({DEN_A}<=0,"",{FIXED_A}/{DEN_A}-$D${A9})', USD2, total=True, tint="total_tint")
ra14 = RA.calc("List price if an ad sale", f'=IF({DEN_A2}<=0,"",{FIXED_A}/{DEN_A2}-$D${A9})', USD2, bold=True)
ra15 = RA.calc("Price of ad exposure", f'=IF(OR(I{ra13}="",I{ra14}=""),"",I{ra14}-I{ra13})', USD2)
ra16 = RA.calc("Margin at the no-ads price", f'=IF(I{ra13}="","",IF(I{ra13}+$D${A9}>0,$D${A6}/(I{ra13}+$D${A9}),0))', PCT1)
RA.eyebrow("WHERE THE NO-ADS PRICE GOES")
w1 = RA.r; w4 = RA.r + 3
wmx = f"MAX($I${w1}:$I${w4})"
RA.bar("Your profit", f"=$D${A6}", USD2, wmx, "teal")
RA.bar("Materials, labor, packaging", f"=$D${A7}+$D${A8}+$D${A11}", USD2, wmx, "gold")
RA.bar("Shipping cost not covered", f"=$D${A10}-$D${A9}", USD2, wmx, "blue")
RA.bar("Etsy fees", f'=IF(I{ra13}="","",(I{ra13}+$D${A9})*({TF}+{PR})+{LF}+{PF})', USD2, wmx, "accent")
RA.close()

RB = D.Card(pr, max(RA.end, PA.end) + 2, "G", "H", "I", "K", extra="J", wb=wb)
RB.title("Your price for that margin", "Same fees, solved for a margin instead of a dollar profit.")
FIXED_B = f"($D${B21}+$D${B22}+$D${B24}+$D${B25}+{LF}+{PF})"
DEN_B = f"(1-{TF}-{PR}-$D${B20})"
DEN_B2 = f"(1-{TF}-{PR}-{AR}-$D${B20})"
rb27 = RB.calc("List price, no Offsite Ads", f'=IF({DEN_B}<=0,"",{FIXED_B}/{DEN_B}-$D${B23})', USD2, total=True, tint="total_tint")
rb28 = RB.calc("List price if an ad sale", f'=IF({DEN_B2}<=0,"",{FIXED_B}/{DEN_B2}-$D${B23})', USD2, bold=True)
rb29 = RB.calc("Net profit per unit, no ads", f'=IF(I{rb27}="","",(I{rb27}+$D${B23})*$D${B20})', USD2)
pill = RB.text(f'=IF({DEN_B}<=0,"No price reaches this margin: fees and margin take all of it",IF({DEN_B2}<=0,"An ad sale cannot reach this margin at any price",'
               f'IF(I{rb27}="","","Round up, never down: "&TEXT(I{rb27},"$#,##0.00")&" becomes "&TEXT(CEILING(I{rb27},0.5),"$#,##0.00")&" or "&TEXT(CEILING(I{rb27},1),"$#,##0"))))', size=9, color="ink2", bold=True)
pr[f"H{pill}"].alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
RB.close()
D.status_rule(pr, f"H{pill}:J{pill}", f"OR({DEN_B}<=0,{DEN_B2}<=0)", good="ink2", fill_tint=False)
D.tile(pr, 6, "B", "E", f'="LIST PRICE FOR "&TEXT($D${A6},"$#,##0.00")&" PROFIT A UNIT"', f"=$I${ra13}", USD2,
       f'=IF($I${ra13}="","No price works: the fee rates take all of it",IF($I${ra14}="","An ad sale cannot reach this profit at any price","If the sale comes through Offsite Ads: "&TEXT($I${ra14},"$#,##0.00")))', dark=True)
D.tile(pr, 6, "G", "K", f'="LIST PRICE FOR A "&TEXT($D${B20},"0%")&" MARGIN"', f"=$I${rb27}", USD2,
       f'=IF($I${rb27}="","No price reaches this margin after fees","Net profit "&TEXT($I${rb29},"$#,##0.00")&" a unit; ad sale price "&IF($I${rb28}="","none",TEXT($I${rb28},"$#,##0.00")))')
D.h(pr, 10, 14)
n_top = max(PB.end, RB.end) + 2
PR_NOTES = [
    ("How it solves", "Every fee except the listing fee and the fixed processing fee is a share of price plus shipping. So the "
     "price plus shipping you need is (profit + costs + fixed fees) divided by (1 minus the fee rates), less the shipping you charge."),
    ("Ad-sale price", "Assumes the Offsite Ads fee is under its per-order cap, which holds for any order under about $666 at 15%."),
    ("If the price looks impossible", "The answer is rarely a lower price. It is lower cost, less labor per unit, or a different product."),
    ("Before you rely on a number", NOTICE),
]
n_end = rich_notes(pr, n_top, PR_NOTES)
S.page_break_before(pr, n_top)
D.h(pr, n_end + 1, 14)
fill_heights(pr, n_end)
D.paint_canvas(pr, n_end + 1, "Z")
S.finish_sheet(pr, PRODUCT, n_end + 1, span=("A", "L"), freeze="A11", tab_color="accent")

# =====================================================================  4 Orders
od = wb.create_sheet("4 Orders")
S.set_widths(od, {"A": 3, "B": 2, "C": 14, "D": 11, "E": 22, "F": 7, "G": 11, "H": 11, "I": 11, "J": 9, "K": 10, "L": 11, "M": 11,
                  "N": 11, "O": 11, "P": 10, "Q": 11, "R": 11, "S": 11, "T": 11, "U": 2, "V": 3})
D.page_header(od, "Orders", "One row per order. Fees, payout and true profit work out as you type.", AS_OF, span=("B", "U"), side_cols=5)
O_TOP = 11
o_first = O_TOP + 5
o_last = o_first + N_ORD - 1
OR_ = {k: f"${k}${o_first}:${k}${o_last}" for k in "CDEFGHIJKLMNOPQRST"}
D.h(od, 6, 10)
MONTH = "C8"
D.stat_strip(od, 7, [
    ("C:D", "Month (yyyy-mm)", "", TXT),
    ("E:E", "Orders", f"=COUNTIF({OR_['K']},$C$8)", INT),
    ("F:H", "Gross sales", f"=SUMIF({OR_['K']},$C$8,{OR_['L']})", USD2),
    ("I:K", "Total Etsy fees", f"=SUMIF({OR_['K']},$C$8,{OR_['Q']})", USD2),
    ("L:M", "Net payout", f"=SUMIF({OR_['K']},$C$8,{OR_['R']})", USD2),
    ("N:O", "Net profit", f"=SUMIF({OR_['K']},$C$8,{OR_['T']})", USD2),
    ("P:Q", "True margin", "=IF(F8>0,N8/F8,0)", PCT1),
    ("R:T", "Fees as % of sales", "=IF(F8>0,I8/F8,0)", PCT1),
])
c = S.input_cell(od, MONTH, "2026-09", TXT, name="SummaryMonth", wb=wb, validation=("textLength", 7, 7),
                 prompt_title="Month to summarize", prompt="Type the month as yyyy-mm, for example 2026-09. The strip sums that month's orders.",
                 error="Type the month as yyyy-mm, for example 2026-09.")
c.font = D.f(18, True, "input_text"); c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
for k in ("C", "D"):
    cc = od[f"{k}8"]; cc.fill = D.fill("input_fill")
    cc.border = Border(top=D.side("input_line"), bottom=D.side("input_line"),
                       left=D.side("input_line") if k == "C" else None, right=D.side("input_line") if k == "D" else None)
D.h(od, 9, 10)
D.frame(od, 6, 9, "B", "U")
D.status_rule(od, "N8", "N8<0", fill_tint=False)
D.h(od, 10, 14)
SKU_LIST = f"{LST}$C${l_first}:$C${l_last}"


def oc(kind):
    def fn(r):
        g = f'IF(C{r}="","",'
        return {
            "month": f'={g}TEXT(C{r},"yyyy-mm"))',
            "rev": f"={g}G{r}+H{r})",
            "tf": f"={g}{TF}*(G{r}+H{r}))",
            "pf": f"={g}{PR}*(G{r}+H{r}+I{r})+{PF})",
            "ad": f'={g}IF(J{r}="Y",MIN({AR}*(G{r}+H{r}),{CAP}),0))',
            "ren": f"={g}{LF}*F{r})",
            "fees": f"={g}M{r}+N{r}+O{r}+P{r})",
            "pay": f"={g}L{r}-Q{r})",
            "cost": f"={g}IFERROR(INDEX({LST}$Q${l_first}:$Q${l_last},MATCH(E{r},{SKU_LIST},0))*F{r},0))",
            "profit": f"={g}R{r}-S{r})",
        }[kind]
    return fn


cols_o = [
    dict(col="C", head="Order date", kind="input", fmt=DATE, values=[d(o[0]) for o in ORDERS], validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"),
         prompt="The order date from Etsy, for example 9/1/2026.", error="Enter a date, for example 9/1/2026."),
    dict(col="D", head="Order ID", kind="input", values=[o[1] for o in ORDERS], validation=("textLength", 0, 20),
         prompt="Etsy's order number, so you can find it again.", error="Up to 20 characters."),
    dict(col="E", head="SKU", kind="input", values=[o[2] for o in ORDERS], validation=("list_range", SKU_LIST),
         prompt="Pick from the list. It comes from the Listings tab.", error="Pick a listing from the list, or add it on the Listings tab."),
    dict(col="F", head="Qty", kind="input", fmt=INT, align="right", values=[o[3] for o in ORDERS], validation=("whole", 1, 1000),
         prompt="Items in the order, a whole number.", error="Enter a whole number from 1 to 1,000."),
    dict(col="G", head="Item total", kind="input", fmt=USD2, align="right", values=[o[4] for o in ORDERS], validation=("decimal", 0, None),
         prompt="Price times quantity, after any discount, in dollars.", error="Enter 0 or more dollars."),
    dict(col="H", head="Shipping charged", kind="input", fmt=USD2, align="right", values=[o[5] for o in ORDERS], validation=("decimal", 0, None),
         prompt="Shipping the buyer paid.", error="Enter 0 or more dollars."),
    dict(col="I", head="Sales tax Etsy collected", kind="input", fmt=USD2, align="right", values=[o[6] for o in ORDERS], validation=("decimal", 0, None),
         prompt="Etsy collects and pays this tax, so it never reaches you, but the processing fee is charged on it. Log it.", error="Enter 0 or more dollars."),
    dict(col="J", head="Offsite Ads? Y/N", kind="input", align="center", values=[o[7] for o in ORDERS], validation=("list", ["Y", "N"]),
         prompt="Y if Etsy marks the order as an Offsite Ads sale.", error="Pick Y or N."),
    dict(col="K", head="Month", kind="calc", align="center", formula=oc("month")),
    dict(col="L", head="Revenue", kind="calc", fmt=USD2, align="right", formula=oc("rev")),
    dict(col="M", head="Transaction fee", kind="calc", fmt=USD2, align="right", formula=oc("tf")),
    dict(col="N", head="Processing fee", kind="calc", fmt=USD2, align="right", formula=oc("pf")),
    dict(col="O", head="Offsite Ads fee", kind="calc", fmt=USD2, align="right", formula=oc("ad")),
    dict(col="P", head="Renewal fee", kind="calc", fmt=USD2, align="right", formula=oc("ren")),
    dict(col="Q", head="Total Etsy fees", kind="calc", fmt=USD2, align="right", formula=oc("fees")),
    dict(col="R", head="Net payout", kind="calc", fmt=USD2, align="right", formula=oc("pay")),
    dict(col="S", head="Product and ship cost", kind="calc", fmt=USD2, align="right", formula=oc("cost")),
    dict(col="T", head="Net profit", kind="calc", fmt=USD2, align="right", bold=True, formula=oc("profit")),
]
f1, f2, o_end = D.table_card(od, O_TOP, "B", "U", cols_o, N_ORD, title="Order log",
                             sub="Yellow columns come from your Etsy order page. Product and ship cost is the listing's total costs "
                                 "(materials, labor, actual shipping, packaging) times the quantity.")
assert (f1, f2) == (o_first, o_last)
for r in range(o_first, o_last + 1):
    od[f"D{r}"].number_format = TXT
D.status_rule(od, f"T{o_first}:T{o_last}", f"T{o_first}<0", fill_tint=False)
D.paint_canvas(od, o_end + 1, "Z")
S.finish_sheet(od, PRODUCT, o_end + 1, span=("A", "V"), freeze=f"A{o_first}", tab_color="blue")
od.page_setup.orientation = "landscape"
od.print_title_rows = f"{o_first - 1}:{o_first - 1}"
od.print_area = f"A1:V{o_first + 24}"
ORD = "'4 Orders'!"
OREF = {k: f"{ORD}${k}${o_first}:${k}${o_last}" for k in "CDEFGHIJKLMNOPQRST"}

# =====================================================================  5 Payouts
po = wb.create_sheet("5 Payouts")
S.set_widths(po, {"A": 3, "B": 2, "C": 14, "D": 12, "E": 14, "F": 14, "G": 12, "H": 13, "I": 11, "J": 11, "K": 10, "L": 12, "M": 12,
                  "N": 12, "O": 12, "P": 15, "Q": 2, "R": 3})
D.page_header(po, "Payouts", "Match every Etsy deposit to the orders and fees behind it. The balance must be $0.00.", AS_OF,
              span=("B", "Q"), side_cols=4)
p_steps_top = 11
p_first_guess = None
D.h(po, 6, 10)
D.stat_strip(po, 7, [
    ("C:E", "Unreconciled balance", "", USD2),
    ("F:P", "Status", "", TXT),
])
D.h(po, 9, 10)
D.frame(po, 6, 9, "B", "Q")
D.h(po, 10, 14)
# five steps card
r = p_steps_top
D.h(po, r, 12); r += 1
t = po[f"C{r}"]; t.value = "Reconcile a deposit in five steps"; t.font = D.f(12, True); po.merge_cells(f"C{r}:P{r}"); D.h(po, r, 24); r += 1
STEPS = [
    "Open the deposit. In Shop Manager, Finances, Payment account, note the deposit date, the amount that reached your bank and the sales period it covers.",
    "Type those four into the yellow cells. The sheet pulls gross sales and every order fee for that period from the Orders tab.",
    "Add charges not tied to one order: new listing fees, shipping labels bought on Etsy, Etsy Ads and refunds, from the same activity list.",
    "Add any adjustment Etsy made, such as a fee credit or a dispute reversal, as a plus or minus.",
    "Read the variance. Zero means every cent is explained. Anything else means a missing order, a changed fee rate or a charge not yet entered.",
]
W_STEP = sum(S.width_of(po, k) for k in D.cols("D", "P"))
for i, s in enumerate(STEPS, 1):
    n = po[f"C{r}"]; n.value = i; n.font = D.f(16, True, "accent"); n.alignment = Alignment(horizontal="center", vertical="center")
    t = po[f"D{r}"]; t.value = s; t.font = D.f(10); t.alignment = Alignment(vertical="center", wrap_text=True); po.merge_cells(f"D{r}:P{r}")
    D.h(po, r, max(S.text_height(s, W_STEP, 10) + 6, 24)); r += 1
D.h(po, r, 12)
D.frame(po, p_steps_top, r, "B", "Q")
P_TOP = r + 2
p_first = P_TOP + 5
p_last = p_first + N_PAY - 1


def sumifs(col, r):
    return f'SUMIFS({OREF[col]},{OREF["C"]},">="&E{r},{OREF["C"]},"<="&F{r})'


def pc(kind):
    def fn(r):
        g = f'IF(C{r}="","",'
        return {
            "gross": f"={g}{sumifs('L', r)})", "tf": f"={g}{sumifs('M', r)})", "pf": f"={g}{sumifs('N', r)})",
            "ad": f"={g}{sumifs('O', r)})", "ren": f"={g}{sumifs('P', r)})",
            "exp": f"={g}G{r}-H{r}-I{r}-J{r}-K{r}-L{r}+M{r})",
            "var": f"={g}ROUND(D{r}-N{r},2))",
            "tax": f"={g}{sumifs('I', r)})",
        }[kind]
    return fn


date_in = dict(kind="input", fmt=DATE, validation=("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), error="Enter a date, for example 9/16/2026.")
cols_p = [
    dict(col="C", head="Deposit date", values=[d(p[0]) for p in PAYOUTS], prompt="The day the deposit reached your bank.", **date_in),
    dict(col="D", head="Bank deposit", kind="input", fmt=USD2, align="right", values=[p[1] for p in PAYOUTS], validation=("decimal", None, None),
         prompt="The amount that reached your bank, in dollars.", error="Enter the deposit in dollars."),
    dict(col="E", head="Period start", values=[d(p[2]) for p in PAYOUTS], prompt="First order date the deposit covers.", **date_in),
    dict(col="F", head="Period end", values=[d(p[3]) for p in PAYOUTS], prompt="Last order date the deposit covers.", **date_in),
    dict(col="G", head="Gross sales", kind="calc", fmt=USD2, align="right", formula=pc("gross")),
    dict(col="H", head="Less transaction", kind="calc", fmt=USD2, align="right", formula=pc("tf")),
    dict(col="I", head="Less processing", kind="calc", fmt=USD2, align="right", formula=pc("pf")),
    dict(col="J", head="Less Offsite Ads", kind="calc", fmt=USD2, align="right", formula=pc("ad")),
    dict(col="K", head="Less renewals", kind="calc", fmt=USD2, align="right", formula=pc("ren")),
    dict(col="L", head="Less other charges", kind="input", fmt=USD2, align="right", values=[p[4] for p in PAYOUTS], validation=("decimal", 0, None),
         prompt="Labels, new listing fees, Etsy Ads and refunds for the period, added up, in dollars.", error="Enter 0 or more dollars."),
    dict(col="M", head="Adjustments", kind="input", fmt=USD2, align="right", values=[p[5] for p in PAYOUTS], validation=("decimal", None, None),
         prompt="A fee credit (plus) or a dispute reversal (minus), in dollars.", error="Enter dollars, plus or minus."),
    dict(col="N", head="Expected deposit", kind="calc", fmt=USD2, align="right", bold=True, formula=pc("exp")),
    dict(col="O", head="Variance", kind="calc", fmt=USD2, align="right", bold=True, formula=pc("var")),
    dict(col="P", head="Memo: tax Etsy remitted", kind="calc", fmt=USD2, align="right", formula=pc("tax")),
]
# table_card validation needs explicit kinds for unbounded decimals
for col in cols_p:
    v = col.get("validation")
    if v and v[0] == "decimal" and v[1] is None:
        col["validation"] = ("decimal", -1000000, 10000000)
f1, f2, p_end = D.table_card(po, P_TOP, "B", "Q", cols_p, N_PAY, title="Deposits",
                             sub="One row per Etsy deposit. Fees come from the Orders tab for the dates you give; sales tax is a memo "
                                 "only, since Etsy pays it to the state.")
assert (f1, f2) == (p_first, p_last)
for word_bad in (True,):
    po.conditional_formatting.add(f"O{p_first}:O{p_last}", FormulaRule(formula=[f'AND($O{p_first}<>"",ABS($O{p_first})>0.005)'],
                                  font=Font(color=D.T["accent"], bold=True), fill=PatternFill("solid", bgColor=D.T["accent_tint"]), stopIfTrue=True))
    po.conditional_formatting.add(f"O{p_first}:O{p_last}", FormulaRule(formula=[f'AND($O{p_first}<>"",ABS($O{p_first})<=0.005)'],
                                  font=Font(color=D.T["teal"], bold=True), fill=PatternFill("solid", bgColor=D.T["teal_tint"]), stopIfTrue=True))
po["C8"] = f"=SUM(O{p_first}:O{p_last})"
po["F8"] = f'=IF(COUNT(C{p_first}:C{p_last})=0,"No deposits entered yet.",IF(ABS(C8)<=0.005,"Reconciled. Every deposit is explained.","Not reconciled. Find the deposit with a non-zero variance."))'
po["F8"].font = D.f(14, True)
for rng, cell in (("C8:E8", "C8"), ("F8:P8", "C8")):
    po.conditional_formatting.add(rng, FormulaRule(formula=["ABS($C$8)>0.005"], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
    po.conditional_formatting.add(rng, FormulaRule(formula=["ABS($C$8)<=0.005"], font=Font(color=D.T["teal"], bold=True), stopIfTrue=True))
p_note_top = p_end + 2
P_NOTES = [
    ("The example", "The $412.57 deposit on Sep 16 covers 13 orders from Sep 1 to 14. Gross sales less every fee, less $47.38 of shipping "
     "labels and a new listing fee, lands on $412.57 exactly. Change it to $410.00 and the variance and the balance turn red."),
    ("Where to find it on Etsy", "Shop Manager, Finances, Payment account. Each deposit shows the amount sent to your bank; the activity "
     "list shows every fee and charge by date."),
    ("Before you rely on a number", NOTICE),
]
p_note_end = rich_notes(po, p_note_top, P_NOTES, span=("C", "P"), frame_span=("B", "Q"))
D.h(po, p_note_end + 1, 14)
fill_heights(po, p_note_end)
D.paint_canvas(po, p_note_end + 1, "Z")
S.finish_sheet(po, PRODUCT, p_note_end + 1, span=("A", "R"), freeze="A10", tab_color="gold")
po.page_setup.orientation = "landscape"
po.print_area = [f"A1:R{p_first + 13}", f"A{p_note_top}:R{p_note_end + 1}"]  # 14 deposit rows print; the rest stay on screen
PAY_BAL = "'5 Payouts'!$C$8"
PAY_STATUS = "'5 Payouts'!$F$8"

# =====================================================================  6 Dashboard
db = wb.create_sheet("6 Dashboard")
S.set_widths(db, {"A": 3, "B": 2, "C": 26, "D": 13, "E": 13, "F": 2, "G": 3, "H": 2, "I": 13, "J": 13, "K": 16, "L": 2, "M": 3})
D.page_header(db, "Dashboard", "True profit, payouts, fees and your tax reserve on one screen.", AS_OF, span=("B", "L"))
TOT_SALES = f"SUM({OREF['L']})"
TOT_PROFIT = f"SUM({OREF['T']})"
D.tile(db, 6, "B", "F", "TRUE PROFIT, ALL LOGGED ORDERS", f"={TOT_PROFIT}", USD2,
       f'="True margin "&TEXT(IF({TOT_SALES}>0,{TOT_PROFIT}/{TOT_SALES},0),"0.0%")&" on "&TEXT({TOT_SALES},"$#,##0")&" of sales"', dark=True)
v, sub, _ = D.tile(db, 6, "H", "L", "UNRECONCILED PAYOUT BALANCE", f"={PAY_BAL}", USD2, f"={PAY_STATUS}")
db.conditional_formatting.add(v.coordinate, FormulaRule(formula=[f"ABS(${v.column_letter}${v.row})>0.005"], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
db.conditional_formatting.add(v.coordinate, FormulaRule(formula=[f"ABS(${v.column_letter}${v.row})<=0.005"], font=Font(color=D.T["teal"], bold=True), stopIfTrue=True))
D.h(db, 10, 14)

# headline card
K1 = D.Card(db, 11, "B", "C", "E", "L", extra="K", wb=wb)
K1.title("The numbers that matter", "From the Orders, Payouts and Listings tabs.")
k_bal = K1.calc("Unreconciled payout balance", f"={PAY_BAL}", USD2, bold=True)
k_pro = K1.calc("True profit, all logged orders", f"={TOT_PROFIT}", USD2)
k_mar = K1.calc("True margin, all logged orders", f"=IF({TOT_SALES}>0,E{k_pro}/{TOT_SALES},0)", PCT1)
k_ads = K1.calc("Blended margin at your ad share", f"={LST}$I${ADS_SV}", PCT1)
K1.close()
D.status_rule(db, f"E{k_bal}", f"ABS(E{k_bal})>0.005", fill_tint=False)

# monthly table
M_TOP = K1.end + 2
r = M_TOP
D.h(db, r, 12); r += 1
t = db[f"C{r}"]; t.value = "Monthly true profit"; t.font = D.f(12, True); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 24); r += 1
t = db[f"C{r}"]; t.value = "Type the first month you want to see; twelve months follow. Sums come from the Orders tab."
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top"); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 18); r += 1
FM = r
lab = db[f"C{r}"]; lab.value = "First month (yyyy-mm)"; lab.font = D.f(10); lab.alignment = Alignment(vertical="center")
c = S.input_cell(db, f"D{r}", "2026-01", TXT, name="FirstMonth", wb=wb, validation=("textLength", 7, 7), prompt_title="First month",
                 prompt="Type a month as yyyy-mm, for example 2026-01. Twelve months follow it.", error="Type the month as yyyy-mm, for example 2026-01.")
c.font = D.f(10, True, "input_text"); c.alignment = Alignment(horizontal="right", vertical="center", indent=1)
c.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
D.h(db, r, D.GRID_ROW); r += 1
D.h(db, r, 8); r += 1
mh = r
for col, hd, al in (("C", "Month", "left"), ("D", "Gross sales", "right"), ("E", "Etsy fees", "right"), ("I", "Net profit", "right"),
                    ("J", "Margin", "right"), ("K", "", "left")):
    cc = db[f"{col}{mh}"]; cc.value = hd.upper(); cc.font = D.f(8, True, "muted"); cc.alignment = Alignment(horizontal=al, vertical="bottom")
for k in D.cols("C", "K"):
    db[f"{k}{mh}"].border = Border(bottom=D.side("ink"))
D.h(db, mh, 24)
m_first = mh + 1
m_last = m_first + 11
for i, rr in enumerate(range(m_first, m_last + 1)):
    D.h(db, rr, D.GRID_ROW)
    if i == 0:
        mf = f'=IF($D${FM}="","",$D${FM})'
    else:
        p = f"C{rr - 1}"
        mf = f'=IF({p}="","",IFERROR(TEXT(DATE(VALUE(LEFT({p},4)),VALUE(RIGHT({p},2))+1,1),"yyyy-mm"),""))'
    vals = [("C", mf, None, "left"),
            ("D", f"=SUMIF({OREF['K']},C{rr},{OREF['L']})", USD2, "right"),
            ("E", f"=SUMIF({OREF['K']},C{rr},{OREF['Q']})", USD2, "right"),
            ("I", f"=SUMIF({OREF['K']},C{rr},{OREF['T']})", USD2, "right"),
            ("J", f"=IF(D{rr}>0,I{rr}/D{rr},0)", PCT1, "right"),
            ("K", f'=IFERROR(REPT("{D.BAR_CHAR}",MAX(0,ROUND(I{rr}/MAX($I${m_first}:$I${m_last})*12,0))),"")', None, "left")]
    for col, fml, fmt, al in vals:
        cc = db[f"{col}{rr}"]; cc.value = fml
        if fmt:
            cc.number_format = fmt
        cc.font = D.f(9 if col == "K" else 10, col == "I", "teal" if col == "K" else "ink")
        cc.alignment = Alignment(horizontal=al, vertical="center", indent=1 if col == "K" else 0)
    for k in D.cols("C", "K"):
        db[f"{k}{rr}"].border = Border(bottom=D.side("hair"))
D.status_rule(db, f"I{m_first}:I{m_last}", f"I{m_first}<0", fill_tint=False)
r = m_last + 1
D.h(db, r, 12)
D.frame(db, M_TOP, r, "B", "L")
M_END = r

# fees card, left; best and worst, right is a full-width table below
FE = D.Card(db, M_END + 2, "B", "C", "E", "L", extra="K", wb=wb)
FE.title("Where the fees went", "Every logged order, by fee type.")
fe1 = FE.r; fe4 = FE.r + 3
fmx = f"MAX($E${fe1}:$E${fe4})"
fe_rows = [FE.bar(lab_, f"=SUM({OREF[col]})", USD2, fmx, "accent") for lab_, col in
           (("Transaction fees", "M"), ("Processing fees", "N"), ("Offsite Ads fees", "O"), ("Renewal fees", "P"))]
fe_tot = FE.calc("Total Etsy fees", f"=SUM(E{fe1}:E{fe4})", USD2, total=True, tint="total_tint")
fe_pct = FE.calc("Fees as a share of gross sales", f"=IF({TOT_SALES}>0,E{fe_tot}/{TOT_SALES},0)", PCT1, bold=True)
FE.close()
S.page_break_before(db, FE.top)

# best and worst
BW_TOP = FE.end + 2
r = BW_TOP
D.h(db, r, 12); r += 1
t = db[f"C{r}"]; t.value = "Best and worst listings by margin"; t.font = D.f(12, True); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 24); r += 1
t = db[f"C{r}"]; t.value = "From the Listings tab. Fix the bottom five first: reprice, cut a cost or retire the listing."
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top"); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 18); r += 1
D.h(db, r, 8); r += 1
bh = r
for col, hd, al in (("C", "Top five", "left"), ("D", "Margin", "right"), ("I", "Bottom five", "left"), ("K", "Margin", "right")):
    cc = db[f"{col}{bh}"]; cc.value = hd.upper(); cc.font = D.f(8, True, "muted"); cc.alignment = Alignment(horizontal=al, vertical="bottom")
for k in D.cols("C", "K"):
    db[f"{k}{bh}"].border = Border(bottom=D.side("ink"))
D.h(db, bh, 24)
bw_first = bh + 1
# helper rank keys sit at the bottom of this tab (filled below); KEY is set after it exists
BW_ROWS = list(range(bw_first, bw_first + 5))
for rr in BW_ROWS:
    D.h(db, rr, D.GRID_ROW)
    for k in D.cols("C", "K"):
        db[f"{k}{rr}"].border = Border(bottom=D.side("hair"))
r = BW_ROWS[-1] + 1
D.h(db, r, 12)
D.frame(db, BW_TOP, r, "B", "L")
BW_END = r

# tax reserve
TX = D.Card(db, BW_END + 2, "B", "C", "E", "L", extra="K", wb=wb)
TX.title("Tax reserve", "Set money aside as you earn it, not in April.")
t_rate = TX.input("Share of net profit to set aside", 0.25, PCT, name="TaxReserveRate", validation=("decimal", 0, 0.6),
                  prompt="25% to 30% is a common starting point for self-employment plus income tax. Your tax preparer can give you a real number.",
                  prompt_title="Tax set-aside share")
t_np = TX.calc("Net profit, all logged orders", f"=E{k_pro}", USD2)
t_res = TX.calc("Reserve you should have set aside", f"=MAX(0,E{t_rate}*E{t_np})", USD2, bold=True)
t_have = TX.input("Amount set aside so far", 40, USD2, name="TaxSetAside", validation=("decimal", 0, None),
                  prompt="What is in your tax savings account now, in dollars.")
t_short = TX.calc("Shortfall: move this to your tax account", f"=MAX(0,E{t_res}-E{t_have})", USD2, total=True, tint="total_tint")
TX.close()
D.status_rule(db, f"E{t_short}", f"E{t_short}>0", fill_tint=False)

# quarterly estimated tax, full width table
Q_TOP = TX.end + 2
S.page_break_before(db, Q_TOP)
r = Q_TOP
D.h(db, r, 12); r += 1
t = db[f"C{r}"]; t.value = "Quarterly estimated tax"; t.font = D.f(12, True); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 24); r += 1
t = db[f"C{r}"]; t.value = ("IRS due dates for 2026 (irs.gov, Estimated taxes). A date on a weekend or holiday moves to the next business day. "
                            f"Checked {CHECKED}.")
t.font = D.f(9, False, "muted"); t.alignment = Alignment(vertical="top", wrap_text=True); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 26); r += 1
D.h(db, r, 8); r += 1
qh = r
for col, hd, al in (("C", "Period", "left"), ("D", "Due date", "right"), ("E", "Paid?", "center"), ("I", "Amount paid", "right")):
    cc = db[f"{col}{qh}"]; cc.value = hd.upper(); cc.font = D.f(8, True, "muted"); cc.alignment = Alignment(horizontal=al, vertical="bottom")
for k in D.cols("C", "K"):
    db[f"{k}{qh}"].border = Border(bottom=D.side("ink"))
D.h(db, qh, 24)
q_first = qh + 1
Q_ROWS = []
for i, (lab_, due, paid, amt) in enumerate(QUARTERS):
    rr = q_first + i; Q_ROWS.append(rr)
    D.h(db, rr, D.GRID_ROW)
    cc = db[f"C{rr}"]; cc.value = lab_; cc.font = D.f(10); cc.alignment = Alignment(vertical="center")
    for k in D.cols("C", "K"):
        db[f"{k}{rr}"].border = Border(bottom=D.side("hair"))
    for col, val, fmt, vrule, prompt, al in (
            ("D", d(due), DATE, ("date", "DATE(2000,1,1)", "DATE(2100,12,31)"), "The IRS due date. Change it if the year changes.", "right"),
            ("E", paid, TXT, ("list", ["Yes", "No"]), "Yes once the payment is made.", "center"),
            ("I", amt, USD2, ("decimal", 0, None), "What you paid for this quarter, in dollars.", "right")):
        cc = S.input_cell(db, f"{col}{rr}", val, fmt, validation=vrule, prompt=prompt,
                          prompt_title={"D": "Due date", "E": "Paid?", "I": "Amount paid"}[col], allow_blank=True)
        cc.font = D.f(10, True, "input_text"); cc.alignment = Alignment(horizontal=al, vertical="center", indent=1 if al != "center" else 0)
        cc.border = Border(left=D.side("input_line"), right=D.side("input_line"), top=D.side("input_line"), bottom=D.side("input_line"))
db.conditional_formatting.add(f"E{Q_ROWS[0]}:E{Q_ROWS[-1]}", FormulaRule(formula=[f'$E{Q_ROWS[0]}="No"'], font=Font(color=D.T["accent"], bold=True), stopIfTrue=True))
r = Q_ROWS[-1] + 1
D.h(db, r, 12)
D.frame(db, Q_TOP, r, "B", "L")
Q_END = r

DB_NOTES = [
    ("True profit", "Revenue (item plus shipping charged) less every Etsy fee on the order and the listing's own costs times quantity. "
     "Sales tax is not revenue: Etsy collects it and pays it to the state."),
    ("Tax", "The reserve and the quarterly dates are an organizer, not tax advice. "
     + S.TAX_TIER_CLAUSE.format(date="October 6, 2026", sources=TAX_SOURCES)),
    ("Before you rely on a number", NOTICE),
]
n_top = Q_END + 2
n_end = rich_notes(db, n_top, DB_NOTES, span=("C", "K"), frame_span=("B", "L"))
S.page_break_before(db, n_top)

# helper: margin rank keys for the best and worst table (v1 kept these on the Listings tab)
h_top = n_end + 2
r = h_top
D.h(db, r, 12); r += 1
t = db[f"C{r}"]; t.value = "Helper: margin rank keys"; t.font = D.f(10, True, "muted"); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 20); r += 1
t = db[f"C{r}"]; t.value = "Each listing's margin plus a tiny row number, so two listings with the same margin both show. Leave as is."
t.font = D.f(9, False, "muted"); db.merge_cells(f"C{r}:K{r}"); D.h(db, r, 18); r += 1
hk_first = r
for i in range(N_LIST):
    rr = hk_first + i
    src = l_first + i
    cc = db[f"C{rr}"]; cc.value = f'=IF({LST}$C${src}="","",{LST}$S${src}+ROW()/1000000000)'
    cc.number_format = "0.000000000"; cc.font = D.f(9, False, "muted"); cc.alignment = Alignment(horizontal="left", vertical="center")
    D.h(db, rr, 13)
hk_last = hk_first + N_LIST - 1
r = hk_last + 1
D.h(db, r, 12)
D.frame(db, h_top, r, "B", "L")
DB_LAST = r + 1
D.h(db, DB_LAST, 14)
KEY = f"$C${hk_first}:$C${hk_last}"
NAMES = f"{LST}$C${l_first}:$C${l_last}"
MARGS = f"{LST}$S${l_first}:$S${l_last}"
for i, rr in enumerate(BW_ROWS, 1):
    for col, fn, src, fmt, al in (("C", "LARGE", NAMES, None, "left"), ("D", "LARGE", MARGS, PCT1, "right"),
                                   ("I", "SMALL", NAMES, None, "left"), ("K", "SMALL", MARGS, PCT1, "right")):
        cc = db[f"{col}{rr}"]
        # the key range is offset from the listing rows, so match on position inside the key range
        cc.value = f'=IFERROR(INDEX({src},MATCH({fn}({KEY},{i}),{KEY},0)),"")'
        if fmt:
            cc.number_format = fmt
        cc.font = D.f(10, col in ("D", "K")); cc.alignment = Alignment(horizontal=al, vertical="center")
for col in ("D", "K"):
    rng = f"{col}{BW_ROWS[0]}:{col}{BW_ROWS[-1]}"
    a0 = f"${col}{BW_ROWS[0]}"
    for formula, color in ((f'AND({a0}<>"",{a0}<{TG}-0.05)', "accent"), (f'AND({a0}<>"",{a0}<{TG},{a0}>={TG}-0.05)', "gold"),
                           (f'AND({a0}<>"",{a0}>={TG})', "teal")):
        db.conditional_formatting.add(rng, FormulaRule(formula=[formula], font=Font(color=D.T[color], bold=True), stopIfTrue=True))
fill_heights(db, DB_LAST)
D.paint_canvas(db, DB_LAST, "Z")
S.finish_sheet(db, PRODUCT, DB_LAST, span=("A", "M"), freeze="A11", tab_color="purple")

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


sh = wb.create_sheet("Start Here", 0)
S.set_widths(sh, SH_GRID)
D.page_header(sh, PRODUCT, "Start here. Six working tabs, about twenty minutes to reconcile your first payout.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
r = 6
r = sh_card(sh, r, "What it does", [(None,
    "You know your Etsy sales. This shows your profit: every listing after Etsy's transaction, processing, listing and Offsite Ads "
    "fees; the list price that hits the profit or margin you want; every order's true profit; and a payout check that explains "
    "each deposit to the cent. The workbook opens with a sample candle shop filled in, so you can see what right looks like first.", "para")])
r = sh_card(sh, r, "Six steps", [
    (1, "Setup. Type your target margin and pick your Offsite Ads tier. The fee table holds Etsy's US fees, checked Oct 6, 2026.", "num"),
    (2, "Listings. One row per listing: price, materials, labor, shipping and packaging. Flags say OK, WATCH or REPRICE.", "num"),
    (3, "Pricing. Type the profit or margin you want and read the list price, with and without an Offsite Ads sale.", "num"),
    (4, "Orders. Log the orders behind one deposit from your Etsy order page. Fees and true profit work out per order.", "num"),
    (5, "Payouts. Type the deposit and its dates, then charges not tied to an order. The balance must read $0.00.", "num"),
    (6, "Dashboard. True profit by month, where the fees went, best and worst listings, and your tax reserve.", "num"),
])
S.page_break_before(sh, r)
r = sh_card(sh, r, "How to read the cells", [
    ((0.3, PCT1), "Yellow cells with blue numbers are yours to change. Type over the example. Each one shows a hint when you select it.", "chip-in"),
    ((29.5, USD2), "Plain numbers are formulas. They update on their own and are locked so a stray keystroke can't break them.", "chip-calc"),
    ((22.01, USD2), "Dark tiles are your answers. They sit at the top of Setup, Pricing and Dashboard and stay on screen as you scroll.", "chip-key"),
    (None, "Each tab is protected without a password. To change anything else, use Review, Unprotect Sheet in Excel, or Data, "
           "Protect sheets and ranges in Google Sheets.", "note"),
])
r = sh_card(sh, r, "The example", [(None,
    "A sample candle shop with a 30% target margin. The 8 oz Soy Candle at $24 plus $5.50 shipping keeps $9.80, a 33.2% margin: OK. "
    "The Wax Melt 6-Pack, marked as an Offsite Ads sale, keeps 15.8%: REPRICE. To keep $8 a unit on the candle, list it at $22.01, "
    "or $27.48 if the sale comes through Offsite Ads. September's 20 orders bring $856.00 of sales, $126.11 of Etsy fees (14.7%) "
    "and $268.44 of true profit (31.4%). The $412.57 deposit on Sep 16 reconciles to the cent.", "para")])
r = sh_card(sh, r, "Good to know", [
    (None, "Google Sheets. Upload the .xlsx to Google Drive, open it, then File, Save as Google Sheets. Check that the SKU dropdown "
           "on the Orders tab works. Every formula is a plain formula that works in Excel, Google Sheets, Numbers and LibreOffice. "
           "No macros, no add-ons, no sign-up.", "para"),
    (None, "Starting fresh. Type over the sample rows with your own, or clear the yellow cells. The formulas stay.", "para"),
    (None, "Outside the US. Payment processing fees depend on your bank's country. Type your own rates on the Setup tab.", "para"),
    (None, "Printing. Orders prints its first 25 rows and Payouts its first 14 deposits. To print more, select the rows and "
           "print the selection.", "para"),
])
r = sh_card(sh, r, "Before you rely on a number", [(None, NOTICE + " "
    + S.TAX_TIER_CLAUSE.format(date="October 6, 2026", sources=TAX_SOURCES), "note")])
D.paint_canvas(sh, r - 1, "Z")
S.finish_sheet(sh, PRODUCT, r - 1, span=("A", "G"), tab_color="teal")

tm = wb.create_sheet("Terms")
S.set_widths(tm, SH_GRID)
D.page_header(tm, "Terms of Use", f"{PRODUCT}, version 3. Read this before you rely on a number.", f"Checked {CHECKED}",
              span=("B", "F"), side_cols=2)
paras = open(os.path.join(HERE, "LICENSE-AND-DISCLAIMER.txt"), encoding="utf-8").read().strip().split("\n\n")[1:]
r = 6
r = sh_card(tm, r, "More from the shop", [
    (None, ("Shipping cost calculator for Etsy and eBay sellers", "https://www.etsy.com/listing/4585097496"), "link"),
    (None, ("Inventory spreadsheet with a reorder planner", "https://www.etsy.com/listing/4585004344"), "link"),
    (None, ("Everything in the shop: etsy.com/shop/ProofNotFluff", "https://www.etsy.com/shop/ProofNotFluff"), "link"),
])
S.page_break_before(tm, r)
r = sh_card(tm, r, "Terms of Use and disclaimer", [(None, p, "para") for p in paras])
r = sh_card(tm, r, "A small ask", [
    (None, "If this workbook showed you a number you didn't know, a short review on Etsy helps other sellers find it. Thank you.", "para"),
])
D.paint_canvas(tm, r - 1, "Z")
S.finish_sheet(tm, PRODUCT, r - 1, span=("A", "G"), tab_color="note")

def set_error(ws, cell, text):
    for dv in ws.data_validations.dataValidation:
        if cell in str(dv.sqref).split():
            dv.error = text
            return
    raise SystemExit(f"no validation on {ws.title}!{cell}")


set_error(su, f"C{SN}", "Up to 60 characters.")
set_error(su, f"D{CUR}", "Up to 10 characters, for example USD.")
set_error(su, f"D{TM}", "Enter a percent from 0% to 90%.")
for nm in ("TransactionFee", "ProcessingRate", "AdsRateUnder", "AdsRateOver"):
    set_error(su, "I" + FEE[nm].split("$")[-1], "Enter a percent from 0% to 50%.")
set_error(su, "I" + FEE["ListingFee"].split("$")[-1], "Enter dollars from $0 to $5, for example 0.20.")
set_error(su, "I" + FEE["ProcessingFixed"].split("$")[-1], "Enter dollars from $0 to $5, for example 0.25.")
set_error(li, SHARE, "Enter a percent from 0% to 100%.")
set_error(od, MONTH, "Type the month as yyyy-mm, for example 2026-09.")
set_error(db, f"D{FM}", "Type the month as yyyy-mm, for example 2026-01.")
set_error(db, f"E{t_rate}", "Enter a percent from 0% to 60%.")
for rr in Q_ROWS:
    set_error(db, f"D{rr}", "Enter a date, for example 4/15/2026.")
    set_error(db, f"E{rr}", "Pick Yes or No.")
for rr in (A6, A7, A8, A9, A10, A11, B21, B22, B23, B24, B25):
    set_error(pr, f"D{rr}", "Enter 0 or more, in dollars.")

wb.active = 0
problems = [p for p in S.audit(wb) if "input without validation" not in p]
if problems:
    print("AUDIT:", *problems, sep="\n  ")
wb.save(OUT)
print("saved", OUT)
print({"setup": dict(TM=TM, TIER=TIER, ADS=ADS, SN=SN, CUR=CUR, fees={k: v for k, v in FEE.items()}),
       "listings": dict(first=l_first, ads_first=a_first, strip=ADS_SV),
       "pricing": dict(A6=A6, A7=A7, A8=A8, A9=A9, A10=A10, A11=A11, B20=B20, B21=B21, B22=B22, B23=B23, B24=B24, B25=B25,
                       ra13=ra13, ra14=ra14, ra15=ra15, ra16=ra16, rb27=rb27, rb28=rb28, rb29=rb29, pill=pill),
       "orders": dict(first=o_first), "payouts": dict(first=p_first),
       "dash": dict(k_bal=k_bal, k_pro=k_pro, k_mar=k_mar, k_ads=k_ads, FM=FM, m_first=m_first, fe_tot=fe_tot, fe_pct=fe_pct,
                    bw=BW_ROWS, t_rate=t_rate, t_res=t_res, t_have=t_have, t_short=t_short, q=Q_ROWS, hk=hk_first)})
