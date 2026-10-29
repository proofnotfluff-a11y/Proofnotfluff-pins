#!/usr/bin/env python3
"""Stress test numbers (.claude/skills/stress-test/SKILL.md; Todd, live chat, Oct 29, 2026: "Founder: stress test").

Code does every sum so the model never counts. Standard library only, no network. Adapted from the MIT-licensed
founder-cfo and founder-pricing tools in github.com/Jakeschincariol/founder-skill (fd9385b, (c) 2026 Jake Schincariol),
rewritten for our products: units are months of a seat or a subscription, or one-off downloads, and the platform fee
(Gumroad 10% plus $0.50 a sale on our own links) comes off every sale.

  cfo  FILE.json [--price P] [--volume V] [--out FILE.md] [--json]
       FILE: {product, unit, price, fee_pct, fee_fixed, variable:[{label,cost,source}], fixed_monthly:[...],
              startup:[...], cap (most units a month, e.g. 3 seats), ramp: 12 numbers (units sold or held each month),
              goal_month (net dollars a month we need from it, optional)}
       Every cost carries a source ("Gumroad pricing page", "estimate: <why>"); a cost with no source fails.
  price FILE.json [--out FILE.md]
       FILE: {product, current, answers:[{too_cheap, cheap, expensive, too_expensive}], simulated: true|false}
       Van Westendorp range from the four answers. Simulated answers say so on every line: they pick what to test,
       they are never proof and never go in copy, a listing, an email or a decide row as evidence.
  --selftest

Exit 0 on a report, 2 on bad input, 1 on a failed selftest.
"""
import argparse, json, math, sys


class InputError(Exception):
    pass


def usd(v, cents=False):
    s = "-" if v < 0 else ""
    return s + ("$%s" % ("{:,.2f}" if cents else "{:,.0f}").format(abs(v if cents else round(v))))


def total(items, field):
    t = 0.0
    for i, it in enumerate(items or []):
        if not isinstance(it, dict) or "cost" not in it:
            raise InputError(f"{field}[{i}] needs a cost")
        if not str(it.get("source") or "").strip():
            raise InputError(f"{field}[{i}] ({it.get('label', '?')}) has no source: name a page, a quote or 'estimate: <why>'")
        t += float(it["cost"])
    return t


def analyse(spec, price=None, volume=1.0, var_scale=1.0):
    if price is None and "price" not in spec:
        raise InputError("price is missing")
    p = float(spec["price"] if price is None else price)
    if p <= 0:
        raise InputError("price must be above zero")
    ramp = spec.get("ramp")
    if not isinstance(ramp, list) or len(ramp) != 12:
        raise InputError("ramp needs 12 numbers, units in each month of year 1")
    ramp = [float(u) * volume for u in ramp]
    fee = p * float(spec.get("fee_pct", 0)) / 100 + float(spec.get("fee_fixed", 0))
    var = total(spec.get("variable"), "variable") * var_scale + fee
    fixed = total(spec.get("fixed_monthly"), "fixed_monthly")
    startup = total(spec.get("startup"), "startup")
    contrib = p - var
    breakeven = math.inf if contrib <= 0 else fixed / contrib
    cap = spec.get("cap")
    months, cum, payback = [], -startup, None
    for m, u in enumerate(ramp, 1):
        net = u * contrib - fixed
        cum += net
        if payback is None and cum >= 0:
            payback = m
        months.append({"month": m, "units": u, "gross": u * p, "net": net, "cumulative": cum})
    year_net = sum(m["net"] for m in months)
    best = max(months, key=lambda m: m["net"])
    flags = []
    if contrib <= 0:
        flags.append("Each sale loses money after fees and direct costs.")
    if cap is not None and not math.isinf(breakeven) and breakeven > float(cap):
        flags.append(f"Break-even needs {math.ceil(breakeven)} units a month but the cap is {cap}.")
    if cap is not None and max(ramp) > float(cap):
        flags.append(f"The ramp goes above the cap of {cap}.")
    if year_net < 0:
        flags.append(f"Year 1 loses {usd(-year_net)} after fixed costs.")
    if payback is None and startup > 0:
        flags.append("The startup spend is not earned back in year 1.")
    goal = spec.get("goal_month")
    goal_units = None
    if goal and contrib > 0:
        goal_units = math.ceil((float(goal) + fixed) / contrib)
        if cap is not None and goal_units > float(cap):
            flags.append(f"The {usd(float(goal))} month goal needs {goal_units} units a month; the cap is {cap}.")
    return {"price": p, "fee": fee, "variable": var, "contribution": contrib, "fixed": fixed, "startup": startup,
            "breakeven": breakeven, "cap": cap, "months": months, "year_net": year_net, "payback": payback,
            "best_month": best, "goal": goal, "goal_units": goal_units, "flags": flags}


def cfo_report(spec, a):
    u = spec.get("unit", "unit")
    be = "never" if math.isinf(a["breakeven"]) else str(math.ceil(a["breakeven"]))
    L = [f"# Stress test numbers: {spec.get('product', 'product')}", "",
         "Every number comes from the input file and its named sources. Estimates are marked in the file.", "",
         f"- One {u}: price {usd(a['price'], True)}, platform fee {usd(a['fee'], True)}, "
         f"direct costs {usd(a['variable'] - a['fee'], True)}, leaves {usd(a['contribution'], True)}.",
         f"- Fixed costs {usd(a['fixed'])} a month; startup {usd(a['startup'])}.",
         f"- Break-even: {be} {u}s a month" + (f" (cap {a['cap']})." if a["cap"] is not None else "."),
         f"- Year 1 net after fixed costs: {usd(a['year_net'])}; best month {a['best_month']['month']} at "
         f"{usd(a['best_month']['net'])}.",
         f"- Startup earned back: {'month %d' % a['payback'] if a['payback'] else 'not in year 1'}."]
    if a["goal_units"]:
        L.append(f"- The {usd(float(a['goal']))} month needs {a['goal_units']} {u}s a month from this product alone.")
    L += ["", f"| month | {u}s | gross | net | cumulative |", "| ---: | ---: | ---: | ---: | ---: |"]
    for m in a["months"]:
        L.append(f"| {m['month']} | {m['units']:g} | {usd(m['gross'])} | {usd(m['net'])} | {usd(m['cumulative'])} |")
    L += ["", "| what if | leaves per unit | break-even a month | year 1 net |", "| --- | ---: | ---: | ---: |"]
    for name, kw in (("Base", {}), ("Price -20%", {"price": a["price"] * 0.8}), ("Half the units", {"volume": 0.5}),
                     ("Direct costs +25%", {"var_scale": 1.25})):
        s = analyse(spec, **kw)
        b = "never" if math.isinf(s["breakeven"]) else str(math.ceil(s["breakeven"]))
        L.append(f"| {name} | {usd(s['contribution'], True)} | {b} | {usd(s['year_net'])} |")
    L += ["", "## Red flags", ""] + ([f"- {f}" for f in a["flags"]] or ["- None in these numbers."])
    return "\n".join(L) + "\n"


def van_westendorp(answers):
    keys = ("too_cheap", "cheap", "expensive", "too_expensive")
    rows = []
    for i, r in enumerate(answers or []):
        try:
            rows.append([float(r[k]) for k in keys])
        except (KeyError, TypeError, ValueError):
            raise InputError(f"answers[{i}] needs {', '.join(keys)} as numbers")
    if len(rows) < 8:
        raise InputError(f"{len(rows)} answers; at least 8 are needed for a range")
    n = len(rows)
    lo, hi = min(min(r) for r in rows), max(max(r) for r in rows)
    grid = [lo + (hi - lo) * i / 400 for i in range(401)]
    tc = lambda p: sum(r[0] >= p for r in rows) / n          # falling as price rises
    ch = lambda p: sum(r[1] >= p for r in rows) / n
    ex = lambda p: sum(r[2] <= p for r in rows) / n          # rising
    te = lambda p: sum(r[3] <= p for r in rows) / n
    def cross(falling, rising):
        for i, p in enumerate(grid):
            if falling(p) <= rising(p):
                if falling(p) < rising(p):
                    return round(p, 2)
                j = i                                         # a tie (often both 0): take the middle of the flat stretch
                while j + 1 < len(grid) and falling(grid[j + 1]) == rising(grid[j + 1]):
                    j += 1
                return round((p + grid[j]) / 2, 2)
        return round(hi, 2)
    return {"n": n, "PMC": cross(tc, lambda p: 1 - ch(p)), "PME": cross(lambda p: 1 - ex(p), te),
            "OPP": cross(tc, te), "IPP": cross(ch, ex)}


def price_report(spec, v):
    sim = bool(spec.get("simulated", True))
    tag = " (simulated buyers: a test plan, not proof)" if sim else ""
    cur = spec.get("current")
    L = [f"# Price range: {spec.get('product', 'product')}{tag}", "",
         f"- {v['n']} answers. Acceptable range {usd(v['PMC'], True)} to {usd(v['PME'], True)}; least resistance "
         f"{usd(v['OPP'], True)}; bargain equals expensive at {usd(v['IPP'], True)}."]
    if cur is not None:
        c = float(cur)
        where = "inside" if v["PMC"] <= c <= v["PME"] else ("below" if c < v["PMC"] else "above")
        L.append(f"- Current price {usd(c, True)} is {where} the range{tag}.")
    return "\n".join(L) + "\n"


def selftest():
    ok = True
    def check(name, cond):
        nonlocal ok
        if not cond:
            ok = False
            print(f"FAIL selftest: {name}")
    seat = {"product": "seat", "unit": "seat-month", "price": 149, "fee_pct": 10, "fee_fixed": 0.5,
            "variable": [], "fixed_monthly": [{"label": "hosting", "cost": 0, "source": "GitHub Pages, free"}],
            "startup": [], "cap": 3, "ramp": [0, 1, 1, 2, 2, 3, 3, 3, 3, 3, 3, 3], "goal_month": 1000}
    a = analyse(seat)
    check("fee is 10% plus 50 cents", abs(a["fee"] - 15.4) < 1e-9)
    check("contribution", abs(a["contribution"] - 133.6) < 1e-9)
    check("goal over cap is flagged", a["goal_units"] == 8 and any("cap is 3" in f for f in a["flags"]))
    check("year net", abs(a["year_net"] - 133.6 * 27) < 1e-6)
    bad = dict(seat, fixed_monthly=[{"label": "ads", "cost": 50}])
    try:
        analyse(bad); check("cost without a source is refused", False)
    except InputError:
        pass
    loss = dict(seat, price=0.4)
    check("a sale under its fee is flagged", any("loses money" in f for f in analyse(loss)["flags"]))
    try:
        analyse(dict(seat, ramp=[1, 2])); check("short ramp refused", False)
    except InputError:
        pass
    ans = [{"too_cheap": 20 + i, "cheap": 40 + 2 * i, "expensive": 90 + 3 * i, "too_expensive": 140 + 4 * i} for i in range(10)]
    v = van_westendorp(ans)
    check("range is ordered", v["PMC"] <= v["PME"] and 20 <= v["PMC"] and v["PME"] <= 180)
    check("simulated label", "not proof" in price_report({"answers": ans, "current": 149}, v))
    try:
        van_westendorp(ans[:3]); check("too few answers refused", False)
    except InputError:
        pass
    print("OK stress_numbers selftest: 10 planted cases" if ok else "stress_numbers selftest failed")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("mode", choices=["cfo", "price"], nargs="?")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--price", type=float)
    ap.add_argument("--volume", type=float, default=1.0)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.mode or not a.file:
        ap.error("give cfo FILE or price FILE")
    try:
        spec = json.load(open(a.file, encoding="utf-8"))
        if a.mode == "cfo":
            r = analyse(spec, price=a.price, volume=a.volume)
            text = json.dumps({k: (None if isinstance(v, float) and math.isinf(v) else v) for k, v in r.items()}, indent=1) \
                if a.json else cfo_report(spec, r)
        else:
            text = price_report(spec, van_westendorp(spec.get("answers")))
    except (OSError, ValueError, InputError) as e:
        print(f"ERROR stress_numbers: {e}", file=sys.stderr)
        return 2
    if a.out:
        open(a.out, "w", encoding="utf-8").write(text)
        print(f"wrote {a.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
