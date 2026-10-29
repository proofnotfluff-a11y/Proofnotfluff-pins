#!/usr/bin/env python3
"""Question pages (site/pages.json kind "question", written by tools/make_site.py, which calls page_html here).

coo/LEADS_DESK.md, Free search traffic (Todd, Oct 18, 2026): one page a week per live lead product, answering a real
question its buyers ask in public (recorded in seo/QUESTIONS.md with where and when it was asked). The answer comes
first, then how to do it, with this Monday's real numbers read from the product's own free-page data file, so the
numbers refresh every time the product's workflow rebuilds the site. Every number and rule names its primary source
and date on the page. A failed or conditional restaurant is never named.

A spec's text fields may hold {placeholders}; stats() fills them from the data file named by the spec's "stats" key.
An unknown placeholder stops the build (KeyError), so a page can never print a number the data does not hold.
Until a live session flips it after Todd's go, a spec carries "draft": true: noindex, off the index and the sitemap.

Usage: python3 tools/question_site.py --selftest
"""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _n(v):
    return f"{v:,}"


def _billions(v, places=1):
    return f"${v / 1e9:.{places}f} billion"


def _date(iso):
    import make_site as M
    return M.nice_date(iso[:10])


def _join(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def _top_gcs(c, k=3):
    g = c["topGCs"][:k]
    return {f"gc{i + 1}": x["name"] for i, x in enumerate(g)} | {f"gc{i + 1}n": _n(x["projects"]) for i, x in enumerate(g)}


def _slug(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


def stats(kind, d):
    """Formatted numbers for a question page, from the product's committed free-page data (one function per product)."""
    if kind in ("chicago_construction", "austin_construction"):
        c = d["counts"]
        s = {"kept": _n(c["kept"]), "fetched": _n(c["fetched"]), "newBuild": _n(c["keptByType"].get("New construction", 0)),
             "nearFinish": _n(c["nearFinish"]), "homes": _n(c["keptUnits"]), "asOf": _date(d["source"]["fetchedAt"]),
             "from": _date(d["window"]["from"]), "to": _date(d["window"]["to"]), "dataset": d["source"]["name"],
             "datasetUrl": d["source"]["url"]}
        s["cost"] = _billions(c["keptCost"], 1 if kind == "chicago_construction" else 2)
        s["areas"] = _join(f"{a} ({_n(n)})" for a, n in c["topAreas"][:3])
        s |= _top_gcs(c)
        s["gcRows"] = [[x["name"], _n(x["projects"]), _billions(x["cost"], 2) if x["cost"] >= 1e9 else f"${x['cost'] / 1e6:,.1f} million"]
                       for x in c["topGCs"][:5]]
        s["areaRows"] = [[a, _n(n)] for a, n in c["topAreas"][:5]]
        if kind == "austin_construction":
            s["builders"] = _n(c["builders"])
            top = max(x["projects"] for x in c["topGCs"])
            names = [x["name"] for x in c["topGCs"] if x["projects"] == top]
            s["topLine"] = (f"On this Monday's list, {_join(names)} each have {top} active projects." if len(names) > 1 else
                            f"On this Monday's list, {names[0]} has the most active projects, {top}.")
            s["underWay"] = _n(c["byStage"].get("Work under way", 0))
            s["justIssued"] = _n(c["byStage"].get("Permit issued", 0))
        else:
            s["reno"] = _n(c["keptByType"].get("Renovation", 0))
        return s
    if kind == "chicago_restaurant":
        c, w = d["counts"], d["window"]
        b = c["byCat"]
        return {"flagged": _n(c["flagged"]), "opening": _n(c["opening"]), "openingPassed": _n(c["openingPassed"]),
                "hood": _n(b["hood"]), "pests": _n(b["pests"]), "drain": _n(b["drain"]), "clean": _n(b["clean"]),
                "new": _n(c["new"]), "repeat": _n(c["repeat"]), "from": _date(w["from"]), "through": d["throughText"],
                "asOf": d["asOfText"], "dataset": d["source"]["name"], "datasetUrl": d["source"]["url"],
                "areas": _join(f"{a} ({_n(n)})" for a, n in c["areas"][:3]),
                "areaRows": [[a, _n(n)] for a, n in c["areas"][:5]],
                "catRows": [["Pests", _n(b["pests"])], ["Hood or exhaust", _n(b["hood"])], ["Grease trap or drain", _n(b["drain"])],
                            ["Kitchen cleaning", _n(b["clean"])]]}
    if kind == "kit_cashflow":   # the kit's question pages: the free calculator's own defaults (workbook example 1, week 1)
        c = next(x for x in d["pages"] if x["slug"] == "ecommerce-13-week-cash-flow-calculator")["defaults"]
        num = lambda k: int(c[k].replace(",", ""))
        cash, inn, out, po, wk = num("openingCash"), num("weeklyIn"), num("weeklyOut"), num("poAmount"), num("poWeek")
        net = inn - out
        end = lambda w, lag=0: cash + net * w - (po if w >= wk else 0) - (inn if lag and w == wk else 0)
        low = end(wk)
        m = lambda v: ("-$" if v < 0 else "$") + _n(abs(v))
        rows = []
        for w in range(1, 8):
            rows.append([f"Week {w}", m(cash + net * (w - 1) - (po if w - 1 >= wk else 0)), m(inn), m(out),
                         m(po) if w == wk else "$0", m(end(w))])
        moved = cash + net * (wk + 1) - po
        half = po // 2   # the balance split in two equal payments, weeks wk and wk + 2
        split = min(cash + net * w - (half if w >= wk else 0) - (po - half if w >= wk + 2 else 0) for w in range(1, 14))
        return {"cash": m(cash), "in": m(inn), "out": m(out), "net": m(net), "po": m(po), "poWeek": str(wk),
                "preWeek": str(wk - 1), "pre": m(end(wk - 1)), "low": m(low), "need": m(-low) if low < 0 else "$0",
                "lagLow": m(end(wk, lag=1)), "lagNeed": m(-end(wk, lag=1)), "moved": m(moved), "movedWeek": str(wk + 1),
                "w13": m(end(13)), "weekRows": rows, "half": m(half), "splitWeek": str(wk + 2), "splitLow": m(split)}
    if kind == "kit_dd7":   # Amazon DD+7 question pages: the free DD+7 calculator's own model (PNF.payoutGap) and defaults
        import subprocess
        c = next(x for x in d["pages"] if x["slug"] == "amazon-dd7-payout-calculator")["defaults"]
        base = {k: float(str(v).replace(",", "")) for k, v in c.items()}
        cases = {"base": {}, "daily": {"schedule": 1}, "mfn": {"fulfil": 1, "tracked": 0},
                 "mfnDaily": {"fulfil": 1, "tracked": 0, "schedule": 1}, "slowBank": {"schedule": 1, "bankDays": 5}}
        js = ('const P=require(process.argv[1]);const b=JSON.parse(process.argv[2]),c=JSON.parse(process.argv[3]);const o={};'
              'for(const k in c)o[k]=P.payoutGap(Object.assign({},b,c[k]));console.log(JSON.stringify(o));')
        out = json.loads(subprocess.run(["node", "-e", js, os.path.join(ROOT, "docs", "assets", "pnf-calc.js"), json.dumps(base),
                                         json.dumps(cases)], capture_output=True, text=True, check=True).stdout)
        m = lambda v: ("-$" if v < 0 else "$") + _n(abs(round(v)))
        s = {"sales": m(base["sales"]), "deliver": str(int(base["deliverDays"])), "edd": str(int(base["eddDays"])),
             "cash": m(base["cash"]), "costs": m(base["costs"]), "bank": str(int(base["bankDays"]))}
        for k, r in out.items():
            s |= {k + "Held": m(r["heldMax"]), k + "HeldMin": m(r["heldMin"]), k + "HeldDays": str(r["heldDays"]),
                  k + "Fast": str(r["fastest"]), k + "Slow": str(r["slowest"]), k + "Low": m(r["low"]),
                  k + "LowDay": str(r["lowDay"]), k + "Need": m(r["need"]), k + "First": str(r["first"]), k + "Avail": str(r["avail"])}
        s["heldDiff"] = m(out["base"]["heldMax"] - out["daily"]["heldMax"])
        row = lambda label, k: [label, s[k + "Held"], s[k + "Fast"] + (" to " + s[k + "Slow"] if s[k + "Fast"] != s[k + "Slow"] else "") + " days",
                                s[k + "Low"] + " (day " + s[k + "LowDay"] + ")", s[k + "Need"]]
        s["leverRows"] = [row("FBA, 14-day scheduled payout", "base"), row("FBA, payout requested every day", "daily"),
                          row("FBA, daily request, 5 days to the bank", "slowBank"),
                          row("Merchant fulfilled, no valid tracking, 14-day payout", "mfn"),
                          row("Merchant fulfilled, no valid tracking, daily request", "mfnDaily")]
        return s
    if kind == "lights":   # Christmas light question pages: the free lights calculator's own model (PNF.lightsQuote) and defaults
        import subprocess
        c = next(x for x in d["pages"] if x["slug"] == "christmas-light-installation-pricing-calculator")["defaults"]
        cases = {"base": {}, "bought": {"owner": "1"}, "own": {"owner": "1", "matPerFt": "0", "shrubMat": "0"},
                 "slow": {"ftPerHour": "25"}, "fast": {"ftPerHour": "60"}, "small": {"feet": "80", "shrubs": "0"}, "big": {"feet": "300"}}
        js = ('const P=require(process.argv[1]);const b=JSON.parse(process.argv[2]),c=JSON.parse(process.argv[3]);const o={};'
              'for(const k in c)o[k]=P.lightsQuote(Object.assign({},b,c[k]));console.log(JSON.stringify(o));')
        out = json.loads(subprocess.run(["node", "-e", js, os.path.join(ROOT, "docs", "assets", "pnf-calc.js"), json.dumps(c),
                                         json.dumps(cases)], capture_output=True, text=True, check=True).stdout)
        r2 = lambda v: round(v + 1e-9, 2)   # half up, as the calculator page shows its example
        m = lambda v: "$" + _n(round(v)) if abs(v - round(v)) < 0.005 else f"${r2(v):,.2f}"
        f = lambda v: f"${r2(v):,.2f}"
        s = {"feet": c["feet"], "shrubs": c["shrubs"], "pace": c["ftPerHour"], "shrubMin": c["shrubMin"], "people": c["people"],
             "rate": m(float(c["rate"])), "takedown": c["takedownPct"] + "%", "matFt": f(float(c["matPerFt"])), "shrubMat": m(float(c["shrubMat"])),
             "seasons": c["seasons"], "storage": m(float(c["storage"])), "tripMin": c["tripMin"], "miles": c["tripMiles"],
             "perMile": str(round(float(c["perMile"]) * 100)) + " cents", "margin": c["margin"] + "%",
             "smallFeet": cases["small"]["feet"], "bigFeet": cases["big"]["feet"], "slowPace": cases["slow"]["ftPerHour"],
             "fastPace": cases["fast"]["ftPerHour"]}
        for k, r in out.items():
            s |= {k + "Quote": m(r["quote"]), k + "PerFt": f(r["perFt"]), k + "Floor": f(r["floor"]), k + "FloorPerFt": f(r["floorPerFt"]),
                  k + "Profit": f(r["profit"]), k + "Next": m(r["quote2"]), k + "Work": f"{r2(r['workHrs']):.2f}", k + "Crew": f"{r2(r['crewHrs']):.2f}",
                  k + "Labor": f(r["labor"]), k + "Drive": f(r["drive"]), k + "Mat": f(r["materials"])}
        row = lambda label, k: [label, s[k + "Quote"], s[k + "PerFt"], s[k + "FloorPerFt"], s[k + "Profit"]]
        s["caseRows"] = [row(f"Example: {c['feet']} ft, {c['shrubs']} bushes, your lights lent, {c['seasons']} seasons", "base"),
                         row("Customer buys the lights this year", "bought"),
                         row("Customer's own lights, labor only", "own"),
                         row(f"Slower crew, {cases['slow']['ftPerHour']} ft an hour each", "slow"),
                         row(f"Faster crew, {cases['fast']['ftPerHour']} ft an hour each", "fast"),
                         row(f"Small house, {cases['small']['feet']} ft, no bushes", "small"),
                         row(f"Big house, {cases['big']['feet']} ft and {c['shrubs']} bushes", "big")]
        return s
    if kind == "lights_choice":   # by the foot or by the hour, lend or sell the lights: the same model and cases as "lights"
        c = next(x for x in d["pages"] if x["slug"] == "christmas-light-installation-pricing-calculator")["defaults"]
        import subprocess
        cases = {"base": {}, "bought": {"owner": "1"}, "own": {"owner": "1", "matPerFt": "0", "shrubMat": "0"},
                 "slow": {"ftPerHour": "25"}, "fast": {"ftPerHour": "60"}}
        js = ('const P=require(process.argv[1]);const b=JSON.parse(process.argv[2]),c=JSON.parse(process.argv[3]);const o={};'
              'for(const k in c)o[k]=P.lightsQuote(Object.assign({},b,c[k]));console.log(JSON.stringify(o));')
        out = json.loads(subprocess.run(["node", "-e", js, os.path.join(ROOT, "docs", "assets", "pnf-calc.js"), json.dumps(c),
                                         json.dumps(cases)], capture_output=True, text=True, check=True).stdout)
        s = stats("lights", d)
        r2 = lambda v: round(v + 1e-9, 2)
        f = lambda v: f"${r2(v):,.2f}"
        m = lambda v: "$" + _n(round(v)) if abs(v - round(v)) < 0.005 else f"${r2(v):,.2f}"
        hr = lambda v: "$" + _n(round(v + 1e-9))
        people, trips = int(c["people"]), 2 + int(c["serviceCalls"])
        driveHrs = trips * people * float(c["tripMin"]) / 60
        mileage = trips * float(c["tripMiles"]) * float(c["perMile"])
        storage = float(c["storage"])
        b = out["base"]
        hrs = lambda r: r["workHrs"] + driveHrs   # person-hours on the job: hanging, bushes, takedown and both drives
        # what each person-hour is paid: the quote less the lights, storage and mileage, over the person-hours
        pay = lambda q, r, lights, stor: (q - lights - stor - mileage) / hrs(r)
        s |= {"driveHrs": f"{r2(driveHrs):.2f}", "mileage": f(mileage), "matAll": m(b["matAll"]),
              "baseHrs": f"{r2(hrs(b)):.2f}", "basePay": hr(pay(b["quote"], b, b["materials"], storage)),
              "y1Pay": hr(pay(b["quote"], b, b["matAll"], storage)), "y2Pay": hr(pay(b["quote"], b, 0, storage)),
              "ownPay": hr(pay(out["own"]["quote"], out["own"], 0, 0)),
              "boughtY1Pay": hr(pay(out["bought"]["quote"], out["bought"], b["matAll"], 0)),
              "boughtY2Pay": hr(pay(out["bought"]["quote2"], out["bought"], 0, 0))}
        for k in ("slow", "fast"):
            r = out[k]
            s |= {k + "Hrs": f"{r2(hrs(r)):.2f}", k + "FootPay": hr(pay(b["quote"], r, r["materials"], storage)),
                  k + "HourPay": hr(pay(r["quote"], r, r["materials"], storage)), k + "FootProfit": f(b["quote"] - r["floor"])}
        n = int(c["seasons"])
        tot = {"base": b["quote"] * n, "bought": out["bought"]["quote"] + out["bought"]["quote2"] * (n - 1), "own": out["own"]["quote"] * n}
        prof = {"base": (b["quote"] - b["floor"]) * n, "bought": out["bought"]["profit"] + out["bought"]["profit2"] * (n - 1),
                "own": (out["own"]["quote"] - out["own"]["floor"]) * n}
        s |= {k + "Total": m(v) for k, v in tot.items()} | {k + "Profit3": f(v) for k, v in prof.items()}
        s["laterSeasons"] = f"seasons 2 and {n}" if n == 3 else f"seasons 2 to {n}"
        s |= {"baseFootPay": s["basePay"], "baseHourPay": s["basePay"]}
        s["paceRows"] = [[f"{pace} ft an hour each", s[k + "Hrs"], m(b["quote"]), s[k + "FootPay"], s[k + "Quote"], s[k + "HourPay"]]
                         for pace, k in ((s["slowPace"], "slow"), (s["pace"], "base"), (s["fastPace"], "fast"))]
        s["ownerRows"] = [["You lend the lights", s["baseQuote"], s["baseNext"], s["baseTotal"], s["baseProfit3"], "You"],
                          ["The customer buys them", s["boughtQuote"], s["boughtNext"], s["boughtTotal"], s["boughtProfit3"], "The customer"],
                          ["The customer's own lights", s["ownQuote"], s["ownNext"], s["ownTotal"], s["ownProfit3"], "The customer"]]
        return s
    if kind == "lights_calendar":   # when to start advertising lights: the same model, turned into crew time per visit and a pre-Thanksgiving calendar
        import datetime as dt
        s = stats("lights", d)
        c = next(x for x in d["pages"] if x["slug"] == "christmas-light-installation-pricing-calculator")["defaults"]
        import subprocess
        js = ('const P=require(process.argv[1]);console.log(JSON.stringify(P.lightsQuote(JSON.parse(process.argv[2]))));')
        b = json.loads(subprocess.run(["node", "-e", js, os.path.join(ROOT, "docs", "assets", "pnf-calc.js"), json.dumps(c)],
                                      capture_output=True, text=True, check=True).stdout)
        people, trip = int(c["people"]), float(c["tripMin"]) / 60
        inst = b["installHrs"] / people + trip   # clock hours for the crew: on the roof together, plus the drive there
        take = b["takedownHrs"] / people + trip
        today = dt.date.today()
        yr = today.year if today.month >= 3 else today.year - 1
        nov1 = dt.date(yr, 11, 1)
        tg = nov1 + dt.timedelta(days=(3 - nov1.weekday()) % 7 + 21)   # Thanksgiving: the fourth Thursday of November
        days = [nov1 + dt.timedelta(days=i) for i in range((tg - nov1).days) if (nov1 + dt.timedelta(days=i)).weekday() < 5]
        wd = len(days)
        q = b["quote"]
        h1 = lambda v: f"{v + 1e-9:.1f}"
        nd = lambda x: x.strftime("%b ") + str(x.day)
        s |= {"instVisit": h1(inst), "takeVisit": h1(take), "tripMin": c["tripMin"], "season": str(yr), "tgDate": nd(tg),
              "firstDay": nd(days[0]), "lastDay": nd(days[-1]), "weekdays": str(wd), "nextYear": str(yr + 1),
              "instSite": h1(b["installHrs"] / people), "takeSite": h1(b["takedownHrs"] / people)}
        rows = []
        for hrs in (6, 8, 10):
            per = int(hrs / inst + 1e-9)
            perT = int(hrs / take + 1e-9)
            houses = per * wd
            tdays = -(-houses // perT) if perT else 0
            s |= {f"h{hrs}Per": str(per), f"h{hrs}Houses": _n(houses), f"h{hrs}Rev": "$" + _n(round(houses * q)),
                  f"h{hrs}TakePer": str(perT), f"h{hrs}TakeDays": str(tdays)}
            rows.append([f"{hrs} hours", str(per), _n(houses), "$" + _n(round(houses * q)), f"{perT} a day, {tdays} working days"])
        s["calRows"] = rows
        return s
    if kind == "rats":   # rat question pages: the free Rat Index's own weekly file (311 counts by community area, no addresses)
        import rodents_site as R
        ix = R.index(d, R.load_json(R.POP), None)
        c, w, ed, A = d["counts"], d["window"], d["edition"], ix["areas"]
        byCount = sorted(A.values(), key=lambda a: (-a["d30"], a["name"]))
        byRate, byYear = ix["order"], ix["year"]
        r2 = lambda v: f"{v:.2f}"
        s = {"d7": _n(c["d7"]), "d30": _n(c["d30"]), "prev30": _n(c["prev30"]), "change": R.pct((c["d30"] / c["prev30"] - 1) * 100),
             "from7": _date(w["from7"]), "from30": _date(w["from30"]), "to": _date(w["to"]), "prevFrom": _date(w["prevFrom"]),
             "prevTo": _date(w["prevTo"]), "medClose": f"{c['medClose']:.1f}", "asOf": _date(d["source"]["fetchedAt"][:10]),
             "dataset": d["source"]["name"], "datasetUrl": d["source"]["url"], "cityRate": r2(ix["city"]["r30"]),
             "cityYearRate": r2(ix["city"]["rYear"]), "edYear": str(ed["year"]), "edFrom": _date(ed["from"]), "edTo": _date(ed["to"]),
             "edTotal": _n(ed["total"]), "edPrevTotal": _n(ed["prevTotal"]),
             "edChange": R.pct((ed["total"] / ed["prevTotal"] - 1) * 100), "areasWith": _n(c["areasWith30"])}
        for i, a in enumerate(byCount[:3]):
            s |= {f"c{i + 1}": a["name"], f"c{i + 1}n": _n(a["d30"]), f"c{i + 1}r": r2(a["r30"]), f"c{i + 1}k": a["place"]}
        for i, a in enumerate(byRate[:3]):
            s |= {f"r{i + 1}": a["name"], f"r{i + 1}n": _n(a["d30"]), f"r{i + 1}r": r2(a["r30"]), f"r{i + 1}k": a["place"]}
        for i, a in enumerate(byYear[:3]):
            s |= {f"y{i + 1}": a["name"], f"y{i + 1}n": _n(a["year"]), f"y{i + 1}r": r2(a["rYear"])}
        low = byRate[-1]
        s |= {"low": low["name"], "lowN": _n(low["d30"]), "lowR": r2(low["r30"])}
        e = byCount[0]   # worked example: the area with the most complaints in 30 days
        s |= {"exPop": _n(e["pop"]), "exClose": f"{e['medClose']:.1f}" if e.get("medClose") is not None else "not shown",
              "exPrev": _n(e["prev30"]), "exChange": R.area_change(e), "exSlug": e["slug"]}
        s["countRows"] = [[a["name"], _n(a["d30"]), r2(a["r30"]), a["place"]] for a in byCount[:10]]
        s["rateRows"] = [[a["name"], r2(a["r30"]), _n(a["d30"]), _n(a["pop"])] for a in byRate[:10]]
        return s
    raise KeyError(f"no stats for {kind}")


def fill(text, s):
    return text.format_map(s)


def page_html(p):
    import make_site as M
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    pages = {x["slug"]: x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"]}
    kit = None if p["product"] in pages else next(x for x in M.load_store()["products"] if x["key"] == p["product"])
    prod = pages[p["product"]] if kit is None else {"slug": kit["page"], "price": kit["price"],
                                                     "checkout": M.utm(kit["checkout"], "site", kit["campaign"])}
    s = stats(p["stats"], d) | {"price": "$" + str(prod["price"])}
    F = lambda t: re.sub(r"\[([^\]]+)\]\((\.\./[a-z0-9/#-]*)\)", r'<a href="\2">\1</a>',
                         re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", E(fill(t, s))))
    url = M.BASE + p["slug"] + "/"
    rel = "../"
    checkout = prod.get("checkout")
    price = E(str(prod["price"]))
    if checkout:
        checkout = checkout.replace("utm_medium=site", "utm_medium=question")
        checkout += "&utm_content=" + p["slug"]
    sample = f'{rel}{prod["slug"]}/'

    def buy(cls="btn ld-btnbig"):
        if kit:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">Get the workbook: ${price}</a>'
        if checkout:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">Get the full list: ${price} a month</a>'
        return f'<a class="{cls}" href="{sample}">See the free sample</a>'

    answer = "".join(f"<p>{F(x)}</p>" for x in p["answer"])
    steps = "".join(f'<li><h3>{F(h)}</h3><p>{F(t)}</p></li>' for h, t in p["steps"])
    tiles = "".join(f'<div class="tile{" key" if i == 0 else ""}"><div class="lab">{F(lab)}</div><div class="val">{F(val)}</div>'
                    f'<div class="sub">{F(sub)}</div></div>' for i, (lab, val, sub) in enumerate(p["tiles"]))
    numbers = (f'<section class="block"><h2>{F(p["numbersTitle"])}</h2><div class="tiles ld-tiles">{tiles}</div>'
               + "".join(f"<p>{F(x)}</p>" for x in p["numbers"]) + "</section>")
    def table(t):
        rows = s[t["rows"]] if isinstance(t["rows"], str) else t["rows"]
        head = "".join(f'<th scope="col">{F(h)}</th>' for h in t["head"])
        body_rows = "".join("<tr>" + "".join((f'<th scope="row">{F(c)}</th>' if i == 0 else f"<td>{F(c)}</td>") for i, c in enumerate(r)) + "</tr>"
                            for r in rows)
        return (f'<section class="block" id="{_slug(t["title"])}"><h2>{F(t["title"])}</h2>' + "".join(f"<p>{F(x)}</p>" for x in t.get("intro", []))
                + f'<div class="qa-tw" role="region" tabindex="0" aria-label="{F(t["title"])}"><table class="qa-t"><thead><tr>{head}</tr></thead><tbody>{body_rows}</tbody></table></div>'
                + "".join(f'<p class="qa-tnote">{F(x)}</p>' for x in t.get("notes", [])) + "</section>")

    tables = "".join(table(t) for t in p.get("tables", []))
    sections = "".join(f'<section class="block" id="{_slug(h)}"><h2>{F(h)}</h2>' + "".join(f"<p>{F(x)}</p>" for x in paras) + "</section>"
                       for h, paras in p.get("sections", []))
    related = "".join(f'<li><a href="{rel}{E(slug)}/">{E(label)}</a></li>' for slug, label in p["related"]
                      if slug in pages and (M.is_live(pages[slug]) or p.get("draft")))
    cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta{" ld-buy" if checkout else ""}"><div>'
                f'<h2>{F(p["cta"]["title"])}</h2><p>{F(p["cta"]["text"])}</p>'
                f'<p class="ld-buybtn">{buy()}</p>'
                + (f'<p class="ld-secure">Secure checkout by Gumroad. One payment. <a href="{rel}refunds/">Refunds</a></p>' if kit else
                   '<p class="ld-secure">Secure checkout by Gumroad. Cancel any time.</p>' if checkout else "")
                + (f'<p class="qa-free"><a href="{sample}">Or try the free calculator first</a></p></div></div></section>' if kit else
                   f'<p class="qa-free"><a href="{sample}">Or see this week\'s free sample first</a></p></div></div></section>'))
    srcs = "".join(f'<li><a href="{E(fill(u, s))}" rel="noopener">{F(label)}</a>, {F(when)}</li>'
                   for label, u, when in p["sources"])
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Questions", "questions/"), (fill(p["eyebrow"], s), None)] if M.LIVE_QUESTIONS
                               else [("Home", ""), (fill(p["eyebrow"], s), None)])
    calc = p.get("calculator")
    calc_html = (f'<p class="qa-calc">{E(calc[2])} <a href="{rel}{E(calc[0])}/">the free {E(calc[1])}</a>.</p>' if calc else "")
    body = (f'{crumb}<article class="qa"><p class="eyebrow">{F(p["eyebrow"])}</p><h1>{F(p["h1"])}</h1>'
            f'<p class="asof qa-upd"><span class="qa-by">By ProofNotFluff, run by a finance executive</span> · {F(p["updated"])}</p>'
            f'<div class="qa-answer"><p class="qa-tag">The short answer</p>{answer}</div>'
            # store v2 (design review, Oct 24, 2026): a reader from search gets the free step first, the purchase as the text link
            + (f'<div class="ld-heroact qa-act"><a class="btn ld-btnbig" href="{sample}">'
               + ('Try the free calculator' if kit else 'See this week\'s free sample') + f'</a>{buy("ld-textlink")}</div>'
               if checkout else f'<div class="ld-heroact qa-act">{buy()}</div>')
            + (f'<p class="ld-heronote">One payment of ${price}. Excel and Google Sheets.</p>' if kit else
               '<p class="ld-heronote">New list every Monday. Cancel any time.</p>' if checkout else '')
            + f'{numbers}{tables}'
            f'<section class="block"><h2>{F(p["stepsTitle"])}</h2><ol class="qa-steps">{steps}</ol>{calc_html}</section>'
            f'{sections}{cta_html}{M.faq_block([(fill(q, s), fill(a, s)) for q, a in p["faq"]])}'
            + (f'<section class="block"><h2>Related pages</h2><ul class="qa-rel">{related}</ul></section>' if related else "")
            + f'<section class="block qa-src"><h2>Sources</h2><ul>{srcs}</ul></section></article>')
    full = d.get("source", {}).get("fetchedAt") or d.get("asOf") or ""
    mod = full[:10]
    article = {"@context": "https://schema.org", "@type": "Article", "headline": fill(p["h1"], s), "description": fill(p["desc"], s),
               "mainEntityOfPage": url, "image": M.BASE + f'assets/og/{p["slug"]}.png', "inLanguage": "en-US",
               "author": {"@type": "Organization", "name": "ProofNotFluff", "url": M.BASE},
               "publisher": {"@type": "Organization", "name": "ProofNotFluff", "url": M.BASE}}
    if re.match(r"\d{4}-\d{2}-\d{2}$", mod):
        stamp = full.replace("Z", "+00:00") if "T" in full else mod + "T08:00:00-05:00"
        article["dateModified"] = stamp
        article["datePublished"] = p.get("published", stamp)
    if p.get("published"):
        article.setdefault("datePublished", p["published"])
    article.setdefault("dateModified", article.get("datePublished"))
    if str(article.get("dateModified", ""))[:10] < str(article.get("datePublished", ""))[:10]:   # a page published after its data pull
        article["dateModified"] = article["datePublished"]   # a page with no data date still says when it changed (SEO audit, Oct 24)
    article["publisher"]["logo"] = {"@type": "ImageObject", "url": M.BASE + "assets/logo-512.png", "width": 512, "height": 512}
    ld = (M.ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": fill(q, s), "acceptedAnswer": {"@type": "Answer", "text": fill(a, s)}}
                         for q, a in p["faq"]]}, crumb_ld, article)
          + "<style>.ld-page .asof,.ld-page footer p{color:var(--muted)}"
          ".qa{max-width:none}.qa-answer,.qa .qa-tw,.qa-rel,.qa details,.qa .qa-steps,.qa .qa-src ul{max-width:760px}.qa>h1{max-width:820px;text-wrap:pretty;font-size:clamp(28px,4vw,40px)}.qa p{max-width:72ch}.qa-answer p{max-width:62ch}.qa-steps li{max-width:72ch}.qa-upd{margin:10px 0 0}.ld-page h2,.ld-page h3,.ld-page summary{text-wrap:balance}"
          ".qa-answer strong{font-weight:700;color:var(--ink)}.ld-page .ld-tiles .tile .sub{text-wrap:balance}"
          ".qa-rel{list-style:none;padding:0;margin:12px 0 0;max-width:820px}.qa-rel li{margin:0 0 10px}.qa-rel a{display:flex;justify-content:space-between;align-items:center;gap:12px;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;font-weight:600;color:var(--ink);text-decoration:none}"
          ".qa-rel a::after{content:'\\2192';font-weight:400;color:var(--muted)}.qa-rel a:hover{border-color:var(--ink)}"
          ".qa-answer{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ink);border-radius:12px;padding:18px 20px;margin:18px 0 0}"
          ".qa-answer p{margin:0 0 12px;font-size:17.5px;line-height:1.6}.qa-answer p:last-child{margin:0}"
          ".qa-answer .qa-tag{font:600 12px/1 Poppins,system-ui,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}"
          ".qa-act{margin:18px 0 8px}"
          ".qa-steps{margin:14px 0 0;padding:0 0 0 22px}.qa-steps li{margin:0 0 16px;padding-left:4px}"
          ".qa-steps h3{font:600 17px/1.35 Poppins,system-ui,sans-serif;margin:0 0 6px;color:var(--ink)}.qa-steps p{margin:0;line-height:1.6}"
          ".qa-src ul{margin:10px 0 0;padding-left:20px}.qa-src li{margin:0 0 8px;line-height:1.5}"
          ".qa-src li{font-size:14.5px;color:var(--muted);overflow-wrap:break-word}"
          ".qa-tw{overflow-x:auto;margin:14px 0 0;max-width:820px}.qa-t{border-collapse:collapse;width:100%;font-size:15.5px;background:var(--card);border:1px solid var(--line);border-radius:10px}"
          ".qa-t th,.qa-t td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}.qa-t thead th{font:700 12px/1.3 system-ui,-apple-system,\"Segoe UI\",Roboto,Arial,sans-serif;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);background:var(--canvas2)}"
          ".qa-t tbody th{font-weight:600;color:var(--ink)}.qa-t tbody tr:last-child>*{border-bottom:0}.qa-t td:not(:first-child){font-variant-numeric:tabular-nums}.qa-tnote{font-size:14.5px;color:var(--muted);margin-top:10px}"
          ".qa-by{font-weight:600;color:var(--ink2)}.qa-calc{margin:6px 0 0;font-size:16px}"
          ".qa-free{margin:12px 0 0;font-size:15px}.ld-cta .qa-free a{color:#fff}.ld-page .ld-cta p.ld-buybtn{margin-top:16px}"
          ".ld-page .ld-tiles .tile .lab{letter-spacing:.04em;overflow-wrap:anywhere}"
          "@media(max-width:600px){.ld-page .ld-tiles .tile .lab{font-size:11.5px;letter-spacing:.02em;white-space:normal}.qa h1{font-size:27px;line-height:1.12}.qa-answer{padding:14px 16px}.qa-answer p{font-size:16px;line-height:1.55}}</style>")
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    if kit:
        foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
                f'<p>{F(p["footnote"])} Calculations are estimates for planning and depend on your inputs. They aren\'t accounting, tax '
                'or financial advice. Check fees, payout timing and terms against your own statements and the provider\'s current terms.</p>'
                '<p>ProofNotFluff is not affiliated with or endorsed by Shopify, Amazon or any platform named here.</p>'
                '<p>Made by ProofNotFluff with AI assistance. The page counts visits with Cloudflare Web Analytics, '
                'which sets no cookies.</p></div></footer>\n</body></html>')
    else:
        foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
              f'<p>{F(p["footnote"])} Public information for planning sales calls; not legal or business advice and no promise of work. '
              'No business named here has endorsed or works with ProofNotFluff.</p>'
              f'<p>{E(prod.get("disclaimer") or city_note(M, p["city"], d))}</p>'
              + ("" if prod.get("disclaimer") else f'<p>ProofNotFluff is not affiliated with or endorsed by the City of {E(p["city"])}.</p>')
              + '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, '
              'which sets no cookies.</p></div></footer>\n</body></html>')
    return (M.HEAD.format(title=F(p["title"]), desc=F(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page"',
                          robots=robots, analytics=M.analytics_tag(), ogtype="article") + body + foot)


def city_note(M, city, d):
    """The City's own required wording where it has one (Chicago), else the source's attribution and license (Austin)."""
    if city in M.CITY_DISCLAIMER:
        return M.CITY_DISCLAIMER[city]
    src = d["source"]
    return f'Data: {src["attribution"]}, published under {src["license"]}. The City has not reviewed or endorsed this page.'


def selftest():
    import sys
    sys.path.insert(0, HERE)
    specs = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "question"]
    assert specs, "no question pages in site/pages.json"
    rest = json.load(open(os.path.join(ROOT, "permits", "inspections-chicago", "rest-sample.json"), encoding="utf-8"))
    for p in specs:
        html = page_html(p)
        text = re.sub(r"<[^>]+>", " ", html)
        assert "—" not in html and "–" not in html, p["slug"] + ": dash"
        assert "{" not in re.sub(r"<script.*?</script>|<style.*?</style>", "", html, flags=re.S), p["slug"] + ": unfilled placeholder"
        assert html.count("<h1>") == 1, p["slug"] + ": one H1"
        assert ('noindex' in html) == bool(p.get("draft")), p["slug"] + ": draft pages are noindex, live pages are not"
        assert ("not legal or business advice" in html or "or financial advice" in html) and "AI assistance" in html, p["slug"] + ": footer notices"
        assert re.search(r"Source|Sources", text), p["slug"] + ": sources"
        for w in ("guarantee", "guaranteed", "will win", "you will get", "dirty", "filthy", "infested", "violator", "offender"):
            assert w not in text.lower(), (p["slug"], w)
        # a failed or conditional restaurant is never named on a public page (the free page rule)
        for x in rest["examples"].get("flagged", []) + rest["examples"].get("repeat", []):
            if x.get("name"):
                assert x["name"] not in html, (p["slug"], "names a failed place")
    # planted: an unknown placeholder must stop the build
    bad = dict(specs[0], answer=["{noSuchNumber} projects"])
    try:
        page_html(bad)
        raise AssertionError("an unknown placeholder printed")
    except KeyError:
        pass
    print(f"question_site selftest ok ({len(specs)} pages)")


if __name__ == "__main__":
    selftest()
