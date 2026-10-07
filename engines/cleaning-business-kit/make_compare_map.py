#!/usr/bin/env python3
"""Writes compare_map.json (old v2 workbook vs the v3 build) from cells.json, which build_xlsx.py writes next to its output.
Usage: python3 make_compare_map.py <cells.json>"""
import json, sys
C = json.load(open(sys.argv[1]))
O = {"yn": "'2 Your Numbers'!", "bi": "'1 Business Info'!", "cr": "'3 Cleaning Rates'!", "ps": "'5 Price Sheet'!",
     "qb": "'4 Quote Builder'!", "cl": "'6 Client List'!", "jl": "'7 Job Log'!", "mm": "'8 Money by Month'!"}
N = {"yn": "'1 Your Numbers'!", "cr": "'2 Cleaning Rates'!", "ps": "'3 Price Sheet'!", "qb": "'4 Quote Builder'!",
     "cl": "'5 Client List'!", "jl": "'6 Job Log'!"}
inp, out = {}, {}
y, cr, ps, qb, cl, jl = (C[k] for k in ("yn", "cr", "ps", "qb", "cl", "jl"))
def I(k, o, n): inp[k] = {"old": o, "new": n}
def Q(k, o, n): out[k] = {"old": o, "new": n}
# Your Numbers
for k, orow, nref in (("take_home", 5, f"D{y['TH']}"), ("weeks", 6, f"D{y['WK']}"), ("hours", 7, f"D{y['HW']}"), ("share", 8, f"D{y['SH']}"),
                      ("se", 28, f"D{y['SE']}"), ("se_base", 29, f"D{y['SB']}"), ("income", 30, f"D{y['IT']}"), ("margin", 31, f"D{y['MG']}"),
                      ("per_mile", 32, f"D{y['CPM']}"), ("mph", 33, f"D{y['SPD']}"), ("helper_pay", 34, f"D{y['HP']}"), ("payroll", 35, f"D{y['PR']}")):
    I(k, f"{O['yn']}B{orow}", N["yn"] + nref)
for i, r in enumerate(y["costs"]):
    I(f"cost{i + 1}", f"{O['yn']}B{13 + i}", f"{N['yn']}D{r}")
for k, orow, nref in (("billable_hours", 9, f"D{y['BH']}"), ("costs_month", 24, f"D{y['CM']}"), ("costs_year", 25, f"D{y['CY']}"),
                      ("helper_cost", 36, f"D{y['HC']}"), ("profit_needed", 39, f"I{y['profit']}"), ("revenue_needed", 40, f"I{y['rev']}"),
                      ("break_even", 41, f"I{y['be']}"), ("target", 42, f"I{y['tg']}"), ("guess", 44, f"I{y['guess']}"), ("gap", 45, f"I{y['gap']}")):
    Q(k, f"{O['yn']}B{orow}", N["yn"] + nref)
bizlabels = ["Business name", "Your name", "Phone", "Email", "Website or social page", "Service area", "Payment methods you accept"]
for i, lab in enumerate(bizlabels):
    I(f"biz{i}", f"{O['bi']}B{4 + i}", f"{N['yn']}D{y['biz'][lab]}")
I("notice", f"{O['bi']}B11", f"{N['yn']}D{y['NOTICE']}"); I("fee", f"{O['bi']}B12", f"{N['yn']}D{y['FEE']}")
I("valid", f"{O['bi']}B13", f"{N['yn']}D{y['VALID']}"); I("supplies_line", f"{O['bi']}B14", f"{N['yn']}D{y['biz']['Supplies line on the quote']}")
# Cleaning Rates
I("sqft_min", f"{O['cr']}B5", f"{N['cr']}D{cr['SQ']}")
for i, r in enumerate(cr["rooms"]):
    I(f"room{i}", f"{O['cr']}B{8 + i}", f"{N['cr']}D{r}")
I("pet_min", f"{O['cr']}B14", f"{N['cr']}D{cr['PET']}")
for i in range(4):
    I(f"sv_mult{i}", f"{O['cr']}B{18 + i}", f"{N['cr']}D{cr['sv_first'] + i}")
    I(f"sv_sup{i}", f"{O['cr']}C{18 + i}", f"{N['cr']}E{cr['sv_first'] + i}")
    I(f"cd_mult{i}", f"{O['cr']}B{25 + i}", f"{N['cr']}D{cr['cd_first'] + i}")
    I(f"disc{i}", f"{O['cr']}B{32 + i}", f"{N['cr']}D{cr['fr_first'] + i}")
    Q(f"visits{i}", f"{O['cr']}C{32 + i}", f"{N['cr']}E{cr['fr_first'] + i}")
I("min_charge", f"{O['cr']}B38", f"{N['cr']}D{cr['MINC']}"); I("typ_miles", f"{O['cr']}B39", f"{N['cr']}D{cr['TMI']}")
for i in range(10):
    for col_o, col_n, k in (("A", "C", "name"), ("B", "D", "min"), ("C", "E", "sup")):
        I(f"ad_{k}{i}", f"{O['cr']}{col_o}{43 + i}", f"{N['cr']}{col_n}{cr['ad_first'] + i}")
    Q(f"ad_price{i}", f"{O['cr']}D{43 + i}", f"{N['cr']}F{cr['ad_first'] + i}")
# Price Sheet
for i in range(6):
    I(f"ps_size{i}", f"{O['ps']}A{5 + i}", f"{N['ps']}C{ps['first'] + i}")
    for co, cn in zip("BCDEF", "DEFGH"):
        Q(f"ps_{co}{i}", f"{O['ps']}{co}{5 + i}", f"{N['ps']}{cn}{ps['first'] + i}")
for i in range(10):
    Q(f"ps_addon{i}", f"{O['ps']}A{13 + i}", f"{N['ps']}C{ps['add_first'] + i}")
    Q(f"ps_addon_price{i}", f"{O['ps']}C{13 + i}", f"{N['ps']}D{ps['add_first'] + i}")
Q("ps_footer", f"{O['ps']}A24", f"{N['ps']}C{ps['foot']}")
Q("ps_title", f"{O['ps']}A1", f"{N['ps']}C{ps['title_row']}")
# Quote Builder
I("client", f"{O['qb']}B5", f"{N['qb']}D{qb['CLIENT']}"); I("qdate", f"{O['qb']}B6", f"{N['qb']}D{qb['DATE']}")
I("sqft", f"{O['qb']}B7", f"{N['qb']}D{qb['SQ']}")
for i, r in enumerate(qb["rooms"]):
    I(f"q_room{i}", f"{O['qb']}B{8 + i}", f"{N['qb']}D{r}")
for k, orow, nr in (("pets", 14, qb["PET"]), ("condition", 15, qb["CD"]), ("service", 16, qb["SV"]), ("freq", 17, qb["FR"]),
                    ("cleaners", 18, qb["CL"]), ("helpers", 19, qb["HE"]), ("miles", 20, qb["MI"])):
    I(k, f"{O['qb']}B{orow}", f"{N['qb']}D{nr}")
for i, r in enumerate(qb["add"]):
    I(f"qty{i}", f"{O['qb']}B{24 + i}", f"{N['qb']}D{r}")
for k, orow in (("x_sq", 37), ("x_rm", 38), ("x_bs", 39), ("x_cm", 40), ("x_sm", 41), ("x_ah", 42), ("x_tp", 43), ("x_ck", 44), ("x_dr", 45),
                ("x_lr", 46), ("x_lc", 47), ("x_vc", 48), ("x_su", 49), ("x_fl", 50), ("x_one", 53), ("x_dis", 54), ("x_vis", 55),
                ("x_dp", 56), ("x_vm", 57), ("x_rv", 58), ("x_pv", 59), ("x_eh", 60)):
    Q(f"q_{k}", f"{O['qb']}B{orow}", f"{N['qb']}I{qb[k]}")
for k, orow in (("x_sm", 41), ("x_ah", 42), ("x_tp", 43), ("x_ck", 44), ("x_dr", 45), ("x_lr", 46), ("x_lc", 47), ("x_vc", 48), ("x_su", 49), ("x_fl", 50)):
    Q(f"qdeep_{k}", f"{O['qb']}C{orow}", f"{N['qb']}J{qb[k]}")
Q("q_check", f"{O['qb']}B61", f"{N['qb']}C{qb['pill']}")
for k, orow in (("name", 64), ("contact", 65), ("for", 66), ("home", 67), ("price", 68), ("addons", 69), ("supplies", 70), ("cancel", 71), ("valid", 72)):
    Q(f"quote_{k}", f"{O['qb']}A{orow}", f"{N['qb']}C{qb['lines'][k]}")
# Client List: first 3 rows
for i in range(3):
    ro, rn = 6 + i, cl["first"] + i
    for co, cn in zip("ABCDEF", "CDEFGH"):
        I(f"cl{i}_{co}", f"{O['cl']}{co}{ro}", f"{N['cl']}{cn}{rn}")
    Q(f"cl{i}_visits", f"{O['cl']}G{ro}", f"{N['cl']}I{rn}"); Q(f"cl{i}_rev", f"{O['cl']}H{ro}", f"{N['cl']}J{rn}")
Q("cl_rev", f"{O['cl']}C3", f"{N['cl']}{cl['rev']}"); Q("cl_count", f"{O['cl']}G3", f"{N['cl']}{cl['count']}")
# Job Log: first 3 rows
for i in range(3):
    ro, rn = 6 + i, jl["first"] + i
    for co, cn in zip("ABCDEFGHI", "CDEFGHIJK"):
        I(f"jl{i}_{co}", f"{O['jl']}{co}{ro}", f"{N['jl']}{cn}{rn}")
    for co, cn in zip("JKLMN", "LMNOP"):
        Q(f"jl{i}_{co}", f"{O['jl']}{co}{ro}", f"{N['jl']}{cn}{rn}")
Q("jl_below", f"{O['jl']}H3", f"{N['jl']}{jl['strip_below']}")
# Money by Month
I("year", f"{O['mm']}B3", f"{N['jl']}D{jl['year']}")
for m in range(12):
    I(f"mm_other{m}", f"{O['mm']}H{6 + m}", f"{N['jl']}J{jl['mm_first'] + m}")
for m in (8, 9, 10):
    for co, cn in zip("ABCDEFGIJKL", "CDEFGHIKLMN"):
        Q(f"mm{m}_{co}", f"{O['mm']}{co}{6 + m}", f"{N['jl']}{cn}{jl['mm_first'] + m}")
for co, cn in zip("BCDEFGHIJKL", "DEFGHIJKLMN"):
    Q(f"mm_year_{co}", f"{O['mm']}{co}18", f"{N['jl']}{cn}{jl['mm_tot']}")
cases = [
    {"name": "example"},
    {"name": "high", "set": {"take_home": 120000, "hours": 55, "share": 0.8, "sqft": 4200, "q_room0": 5, "q_room1": 4, "q_room4": 2,
                             "q_room5": 3, "pets": 3, "cleaners": 3, "helpers": 2, "miles": 40, "condition": "Heavy buildup",
                             "service": "Deep clean", "freq": "Weekly", "qty0": 1, "qty2": 1, "qty4": 1}},
    {"name": "low", "set": {"take_home": 20000, "weeks": 30, "sqft": 600, "q_room0": 1, "q_room1": 1, "q_room2": 0, "q_room5": 0,
                            "pets": 0, "cleaners": 1, "helpers": 0, "miles": 4, "freq": "One time", "qty1": None, "qty3": None}},
    {"name": "blank take-home and square feet", "set": {"take_home": None, "sqft": None, "cost1": None, "per_mile": None}},
    {"name": "edits: discounts, minimum, add-on, months, a new job and client",
     "set": {"disc2": 0.3, "disc3": 0.35, "min_charge": 300, "ad_name8": "Garage sweep", "ad_min8": 25, "ad_sup8": 3, "qty8": 1,
             "mm_other9": 150, "mm_other0": 75, "sv_mult1": 2, "cd_mult2": 1.4, "condition": "Needs extra work",
             "jl2_A": 46300, "jl2_B": "New client", "jl2_C": "Move-in or move-out (empty home)", "jl2_D": 520, "jl2_E": 9,
             "jl2_F": 4.5, "jl2_G": 1, "jl2_H": 22, "jl2_I": 25, "cl2_A": "New client", "cl2_D": "Weekly", "cl2_F": 160,
             "margin": 0.25, "payroll": 0.2}},
    {"name": "edge: blank team, speed and weeks", "set": {"cleaners": None, "helpers": None, "mph": None, "weeks": None, "miles": 0,
                                                       "condition": "Well kept", "service": "Light touch-up", "freq": "Monthly",
                                                       "jl0_E": None, "jl1_E": 0, "jl1_G": 0.5}},
    {"name": "edge: helpers equal cleaners, one-time move-out", "set": {"cleaners": 3, "helpers": 3, "service": "Move-in or move-out (empty home)",
                                                                      "freq": "One time", "year": 2027, "typ_miles": 0}},
    {"name": "empty home", "set": {"sqft": None, "q_room0": 0, "q_room1": 0, "q_room2": 0, "q_room3": 0, "q_room4": 0, "q_room5": 0,
                                   "pets": 0}},
]
intended = [{"case": "empty home", "outputs": ["q_check"],
             "why": "v2 ran the floor check on an empty home; v3 asks for the home first."}]
json.dump({"tolerance": 0.005, "inputs": inp, "outputs": out, "cases": cases, "intended": intended}, open(__import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "compare_map.json"), "w"), indent=1)
print(len(inp), "inputs", len(out), "outputs", len(cases), "cases")
