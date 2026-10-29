#!/usr/bin/env python3
"""Writes compare_map.json (plan = Snowball) and compare_map_avalanche.json for tools/compare_xlsx.py.
Old file: v2 Debt-Payoff-Tracker.xlsx (Oct 5, 2026). New file: this engine's build. Run from this folder."""
import datetime as dt, json

def serial(y, m, d):
    return (dt.date(y, m, d) - dt.date(1899, 12, 30)).days

DB, LG, DS = "'2 Debts'", "'3 Payment Log'", "'1 Dashboard'"
inputs = {"monthly": {"old": "Debts!D4", "new": f"{DS}!D15"},
          "plan": {"old": "Dashboard!N1", "new": f"{DS}!D19"}}
for i in range(6):
    o, n = 8 + i, 17 + i
    for k, oc, nc in (("name", "B", "D"), ("bal", "D", "F"), ("asof", "E", "G"), ("apr", "F", "H"), ("min", "G", "I")):
        inputs[f"{k}{i+1}"] = {"old": f"Debts!{oc}{o}", "new": f"{DB}!{nc}{n}"}
for k in range(14):
    o, n = 5 + k, 17 + k
    for f, oc, nc in (("date", "A", "C"), ("debt", "B", "D"), ("amt", "C", "E")):
        inputs[f"log{f}{k+1}"] = {"old": f"'Payment Log'!{oc}{o}", "new": f"{LG}!{nc}{n}"}

def outputs(plan):
    out = {"owed": ("Dashboard!B6", f"{DS}!D25"), "paid": ("Dashboard!C6", f"{DS}!D26"),
           "interest_since": ("Dashboard!D6", f"{DS}!D27"), "paid_off": ("Dashboard!E6", f"{DS}!D28"),
           "log_fix": ("Dashboard!F6", f"{DS}!D29"), "monthly_status": ("Dashboard!B3", f"{DS}!C17"),
           "sum_minimums": ("Debts!F4", f"{DB}!F8"),
           "snow_date": ("Dashboard!C9", f"{DS}!I15"), "snow_months": ("Dashboard!C10", "'4 Snowball Plan'!C8"),
           "snow_interest": ("Dashboard!C11", f"{DS}!I16"), "snow_saved": ("Dashboard!C12", f"{DS}!I17"),
           "aval_date": ("Dashboard!D9", f"{DS}!I19"), "aval_months": ("Dashboard!D10", "'5 Avalanche Plan'!C8"),
           "aval_interest": ("Dashboard!D11", f"{DS}!I20"), "aval_saved": ("Dashboard!D12", f"{DS}!I21"),
           "min_date": ("Dashboard!E9", f"{DS}!I23"), "min_interest": ("Dashboard!E11", f"{DS}!I24"),
           "counted_total": ("'Payment Log'!H4", f"{LG}!C8"), "log_fix_rows": ("'Payment Log'!H5", f"{LG}!F8")}
    pay, off = ("D", "E") if plan == "Snowball" else ("F", "G")
    for i in range(6):
        o, n, nd = 18 + i, 44 + i, 17 + i
        out[f"next_debt{i+1}"] = (f"Dashboard!B{o}", f"{DS}!C{n}")
        out[f"next_bal{i+1}"] = (f"Dashboard!C{o}", f"{DS}!D{n}")
        out[f"next_pay{i+1}"] = (f"Dashboard!{pay}{o}", f"{DS}!H{n}")
        out[f"next_off{i+1}"] = (f"Dashboard!{off}{o}", f"{DS}!I{n}")
        for k, oc, nc in (("paid", "H", "J"), ("int", "I", "K"), ("today", "J", "L"), ("status", "K", "M"),
                          ("snow_order", "L", "N"), ("aval_order", "M", "O"), ("min_months", "N", "P"), ("min_int", "O", "Q")):
            out[f"{k}{i+1}"] = (f"Debts!{oc}{8+i}", f"{DB}!{nc}{nd}")
        out[f"snow_paidoff{i+1}"] = (f"'Snowball Plan'!{chr(ord('H')+i)}4", f"'4 Snowball Plan'!{chr(ord('J')+i)}14")
        out[f"aval_paidoff{i+1}"] = (f"'Avalanche Plan'!{chr(ord('H')+i)}4", f"'5 Avalanche Plan'!{chr(ord('J')+i)}14")
    out["next_pay_total"] = (f"Dashboard!{pay}43", f"{DS}!H69")
    out["next_bal_total"] = ("Dashboard!C43", f"{DS}!D69")
    for k in range(14):
        out[f"counted{k+1}"] = (f"'Payment Log'!E{5+k}", f"{LG}!G{17+k}")
    for m in (1, 2, 12, 24, 40, 60):
        sp = "Snowball Plan" if plan == "Snowball" else "Avalanche Plan"
        out[f"plan_balance_m{m}"] = (f"'{sp}'!E{9+m}", f"'{sp[0:0]}{'4 ' if plan=='Snowball' else '5 '}{sp}'!G{20+m}")
        out[f"plan_interest_m{m}"] = (f"'{sp}'!F{9+m}", f"'{'4 ' if plan=='Snowball' else '5 '}{sp}'!H{20+m}")
    return {k: {"old": a, "new": b} for k, (a, b) in out.items()}

def cases(plan):
    P = {"plan": plan}
    c = [
        {"name": "example", "set": dict(P)},
        {"name": "high: $3,000 a month", "set": {**P, "monthly": 3000}},
        {"name": "low: $900 a month", "set": {**P, "monthly": 900}},
        {"name": "below minimums: $500", "set": {**P, "monthly": 500}},
        {"name": "blank monthly amount", "set": {**P, "monthly": None}},
        {"name": "store card paid off by a logged $900", "set": {**P, "logdate13": serial(2026, 10, 5), "logdebt13": "Store card", "logamt13": 900}},
        {"name": "new Visa statement Sep 1", "set": {**P, "bal1": 4500, "asof1": serial(2026, 9, 1)}},
        {"name": "personal loan as-of in the future", "set": {**P, "asof5": serial(2026, 12, 1)}},
        {"name": "0% student loan, car minimum below interest", "set": {**P, "apr4": 0, "min3": 50}},
        {"name": "as-of older than 120 months", "set": {**P, "asof3": serial(2015, 1, 1)}},
        {"name": "log errors: unknown debt, missing amount, future date",
         "set": {**P, "logdate13": serial(2026, 10, 1), "logdebt13": "Boat", "logamt13": 50,
                 "logdate14": serial(2026, 10, 2), "logdebt14": "Visa card", "logamt14": None}},
        {"name": "sixth debt added", "set": {**P, "name6": "Medical bill", "bal6": 600, "asof6": serial(2026, 9, 15), "apr6": 0, "min6": 25,
                                             "logdate13": serial(2026, 10, 1), "logdebt13": "Medical bill", "logamt13": 25}},
        {"name": "every debt cleared", "set": {**P, **{f"name{i}": None for i in range(1, 6)}, **{f"bal{i}": None for i in range(1, 6)},
                                               **{f"asof{i}": None for i in range(1, 6)}}},
        {"name": "high APR, huge balance", "set": {**P, "bal1": 250000, "apr1": 0.36, "min1": 2000, "monthly": 5000}},
    ]
    return c

WHY = "The monthly amount moved from Debts!D4 to the Dashboard's Your plan card, so the message no longer names cell D4."
INTENDED = [{"case": "below minimums: $500", "outputs": ["monthly_status"], "why": WHY},
            {"case": "blank monthly amount", "outputs": ["monthly_status"], "why": WHY},
            {"case": "as-of older than 120 months", "outputs": [f"next_off{i}" for i in range(1, 6)],
             "why": "v2 said Done for a debt whose balance reads Update as-of; v3 says Update as-of."}]
for plan, fn in (("Snowball", "compare_map.json"), ("Avalanche", "compare_map_avalanche.json")):
    json.dump({"tolerance": 0.005, "inputs": inputs, "outputs": outputs(plan), "cases": cases(plan), "intended": INTENDED}, open(fn, "w"), indent=1)
    print(fn, len(outputs(plan)), "outputs", len(cases(plan)), "cases")
