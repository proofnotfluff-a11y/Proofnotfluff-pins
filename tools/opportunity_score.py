#!/usr/bin/env python3
"""Opportunity scorer for the radar agent (.claude/skills/radar/SKILL.md; Todd, Oct 23, 2026 live chat).

Scores public-data product ideas on evidence, never on feel. Each idea is one file, scout/candidates/<slug>.json
(schema pnf.opportunity.v1, fields in scout/RUBRIC.md). Every factor needs a source {url, date}; a factor without
one scores 0. Kill rules run first and are final:
  K1 no buyer we can name and reach (buyer.who and a reach channel with a source)
  K2 data terms that forbid commercial use
  K3 a never-sell category (coo/CONSTITUTION.md 2: medical, legal filing, immigration, investment advice)
  K4 anything near Cata-Kor (longevity or supplement products) before 2027-09-21 (Todd's non-compete)
  K5 private people as the subject (homes, residents, named individuals): CLAUDE.md 5
Factors, each 0 to 5, weighted to 100: buyer 15, pay 15, demand 15, data 15, license 10, effort 10, speed 10, fit 10.
Money: expected paying members in January 2027 from outreach at the desk's cap (40 first emails a week a product)
times net price after Gumroad fees, at three conversion rates (assumptions until we have our own: CONV). Confidence
is capped at medium until our own conversion is recorded (OWN_CONVERSION). Reviews (scout/reviews/<slug>.json, written
by the run from independent subagents) move an idea: all three PASS -> todd; a FAIL -> fix (one round); a second
FAIL -> dropped, or todd with the reason when the code score is 75+.

Usage: python3 tools/opportunity_score.py            score every candidate, write scout/opportunities.json and
                                                     scout/OPPORTUNITIES.md
       python3 tools/opportunity_score.py --check    validate every candidate and review file (exit 1 on a problem)
       python3 tools/opportunity_score.py --selftest planted cases for every kill rule, factor and review state
       --today YYYY-MM-DD to score as of a date (default: Chicago today)
"""
import argparse, datetime as dt, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, "scout", "candidates")
REV = os.path.join(ROOT, "scout", "reviews")
OUT_JSON = os.path.join(ROOT, "scout", "opportunities.json")
OUT_MD = os.path.join(ROOT, "scout", "OPPORTUNITIES.md")
SCHEMA = "pnf.opportunity.v1"
GOAL, GOAL_DATE = 1000, dt.date(2027, 1, 31)
NONCOMPETE_END = dt.date(2027, 9, 21)
BAND = (29, 199)                      # coo/CONSTITUTION.md 1, off-Etsy band
WEIGHTS = {"buyer": 15, "pay": 15, "demand": 15, "data": 15, "license": 10, "effort": 10, "speed": 10, "fit": 10}
REVIEW_FLOOR = 60                     # code score an idea needs before reviewers spend tokens on it
ESCALATE = 75                         # a twice-failed idea this strong goes to Todd with the reason instead of dropping
GATES_DAYS = 5                        # holdout, design director, Legal desk, Todd's go (design/LAUNCH_CHECKLIST.md)
FUNNEL_DAYS = 28                      # 3 free Monday emails then the 7-day trial (coo/DECISIONS-2026-10-22.md 1)
EMAILS_WEEK = 40                      # first emails a week a product (coo/PIVOT.md LEADS FOCUS)
CONV = {"low": 0.0025, "likely": 0.0075, "high": 0.02}   # first email to paying member; assumption, not our data
OWN_CONVERSION = False                # True once a payer exists; until then confidence tops out at medium
FEE_RATE, FEE_FIXED = 0.129, 0.80     # Gumroad 10% plus $0.50, card processing about 2.9% plus $0.30
STATUSES = ("new", "review", "fix", "todd", "parked", "dropped", "killed", "go", "built")
CADENCE_DAYS = {"daily": 1, "weekly": 7, "monthly": 31, "quarterly": 92, "yearly": 366, "static": 100000}

NEVER_SELL = re.compile(r"\b(medical|diagnos\w*|patients?|treatment|prescri\w+|clinic(al)?|immigra\w+|visa|green card|"
                        r"court filing|legal filing|file a lawsuit|investment advice|stock picks?|trading signals?|buy or sell)\b", re.I)
CATAKOR = re.compile(r"\b(supplements?|nutraceuticals?|longevity|anti.?aging|nad\+?|nmn|glutathione|vitamins?|"
                     r"dietary|akg|healthspan|wellness products?)\b", re.I)
PRIVATE = re.compile(r"\b(homeowners?|residents?|single.family homes?|private (persons?|individuals?)|individuals' names|"
                     r"named people|tenants?|voters?|obituar\w+|divorce|eviction defendants?)\b", re.I)


def chicago_today():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date()
    except Exception:
        return dt.date.today()


def d(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (TypeError, ValueError):
        return None


def src_ok(s, today, max_age=365):
    """A source is {url, date}: an http(s) URL and a date no later than today and within max_age days."""
    if not isinstance(s, dict):
        return False
    when = d(s.get("date"))
    return str(s.get("url", "")).startswith(("http://", "https://")) and when is not None and when <= today and (today - when).days <= max_age


def text_of(c):
    b = c.get("buyer") or {}
    return " ".join(str(x) for x in (c.get("name"), c.get("pitch"), b.get("who"), " ".join(c.get("categories") or []),
                                      (c.get("data") or {}).get("subject"), (c.get("data") or {}).get("dataset")) if x)


def kills(c, today):
    out, b, lic = [], c.get("buyer") or {}, ((c.get("data") or {}).get("license") or {})
    if not str(b.get("who", "")).strip() or not str(b.get("reach", "")).strip() or not src_ok(b.get("reachSource"), today):
        out.append("K1 no buyer we can name and reach (buyer.who, buyer.reach and a dated reachSource)")
    if lic.get("commercialUse") == "forbidden":
        out.append("K2 the data terms forbid commercial use")
    t = text_of(c)
    m = NEVER_SELL.search(t)
    if m:
        out.append(f"K3 never-sell category ({m.group(0)!r}; coo/CONSTITUTION.md 2)")
    m = CATAKOR.search(t)
    if m and today < NONCOMPETE_END:
        out.append(f"K4 near Cata-Kor's category ({m.group(0)!r}) before {NONCOMPETE_END}")
    m = PRIVATE.search(" ".join(str(x) for x in ((c.get("data") or {}).get("subject"), c.get("pitch")) if x))
    if m:
        out.append(f"K5 private people as the subject ({m.group(0)!r}; CLAUDE.md 5)")
    return out


def first_dollar(c, today):
    days = float((c.get("build") or {}).get("days") or 30)
    return today + dt.timedelta(days=int(round(days)) + GATES_DAYS + FUNNEL_DAYS)


def factors(c, today):
    f, notes = {}, {}
    b, p, dm, da = c.get("buyer") or {}, c.get("price") or {}, c.get("demand") or {}, c.get("data") or {}
    # buyer: how many reachable payers exist, with a counted source
    n = b.get("count")
    if isinstance(n, (int, float)) and src_ok(b.get("countSource"), today):
        f["buyer"] = 5 if n >= 300 else 4 if n >= 100 else 3 if n >= 50 else 2 if n >= 20 else 1
    else:
        f["buyer"], notes["buyer"] = 0, "no counted, dated buyer source"
    # pay: what they pay competitors today against our price
    ours = p.get("monthly") or 0
    comp = [x.get("monthly") for x in (p.get("competitors") or []) if isinstance(x.get("monthly"), (int, float)) and src_ok(x, today)]
    if comp and ours:
        top = max(comp)
        f["pay"] = 5 if top >= 2 * ours else 4 if top >= ours else 2 if top >= 0.5 * ours else 1
    else:
        f["pay"], notes["pay"] = 0, "no dated competitor price"
    if ours and not (BAND[0] <= ours <= BAND[1]):
        notes["price"] = f"${ours} is outside the ${BAND[0]} to ${BAND[1]} band: Todd sets it"
    # demand: evidenced search wording and AI-style questions, one point each, five at most
    qs = [q for q in (dm.get("searchQueries") or []) + (dm.get("aiQueries") or []) if src_ok(q, today)]
    f["demand"] = min(5, len(qs))
    if not qs:
        notes["demand"] = "no dated search or question evidence"
    # data: cadence, freshness, monthly volume counted from the source, a documented API
    cad = da.get("cadence")
    score = {"daily": 5, "weekly": 5, "monthly": 3, "quarterly": 1}.get(cad, 0)
    last = d(da.get("lastUpdated"))
    if score and (last is None or (today - last).days > 2 * CADENCE_DAYS[cad] + 3):
        score, notes["data"] = 0, f"stale: last update {da.get('lastUpdated')} for a {cad} source"
    vol = da.get("recordsPerMonth")
    if score:
        if not (isinstance(vol, (int, float)) and src_ok(da.get("recordsSource"), today)):
            score, notes["data"] = max(0, score - 2), "monthly volume not counted from the source"
        elif vol < 30:
            score, notes["data"] = max(0, score - 2), f"thin: {vol} records a month"
        elif vol < 100:
            score -= 1
        if not da.get("apiStable"):
            score = max(0, score - 1)
    f["data"] = score
    # license
    lic = da.get("license") or {}
    f["license"] = {"allowed": 5, "unclear": 2}.get(lic.get("commercialUse"), 0) if src_ok(lic, today, 3650) else 0
    if f["license"] < 5:
        notes["license"] = f"license {lic.get('commercialUse', 'not read')}: the data and legal reviewer reads the terms"
    # effort to build and keep
    bd = c.get("build") or {}
    days = bd.get("days")
    f["effort"] = 0 if days is None else 5 if days <= 3 else 4 if days <= 7 else 3 if days <= 14 else 1 if days <= 30 else 0
    if (bd.get("maintHoursMonth") or 0) > 8:
        f["effort"] = max(0, f["effort"] - 1)
    # speed to money against the Jan 31 goal
    fd = first_dollar(c, today)
    f["speed"] = 5 if fd <= dt.date(2026, 12, 31) else 3 if fd <= dt.date(2027, 1, 15) else 1 if fd <= GOAL_DATE else 0
    # fit with what we already pull
    fit = c.get("fit") or {}
    f["fit"] = min(5, 2 * bool(fit.get("samePortal")) + 2 * bool(fit.get("existingTools")) + bool(fit.get("sameBuyerTypes")))
    return f, notes


def money(c, today):
    """Expected net dollars in January 2027 from the product alone, at three conversion rates."""
    price = (c.get("price") or {}).get("monthly") or 0
    net = max(0.0, price * (1 - FEE_RATE) - FEE_FIXED)
    launch = first_dollar(c, today) - dt.timedelta(days=FUNNEL_DAYS)
    weeks = max(0.0, (dt.date(2027, 1, 1) - launch).days / 7)
    reach = (c.get("buyer") or {}).get("count") or 0
    emails = min(reach, int(weeks * EMAILS_WEEK))
    payers = {k: emails * v for k, v in CONV.items()}
    usd = {k: round(v * net) for k, v in payers.items()}
    return {"netPerMember": round(net, 2), "emailsByJan": emails, "payers": {k: round(v, 1) for k, v in payers.items()},
            "janNet": usd, "shareOfGoal": {k: round(v / GOAL, 2) for k, v in usd.items()}}


def confidence(c, f, today):
    sourced = sum(1 for k in ("buyer", "pay", "demand", "data", "license") if f.get(k, 0) > 0)
    level = "high" if sourced == 5 else "medium" if sourced >= 4 else "low"
    if not OWN_CONVERSION and level == "high":
        level = "medium"
    return level


def review_state(slug, score):
    p = os.path.join(REV, f"{slug}.json")
    if not os.path.exists(p):
        return None, []
    rows = json.load(open(p, encoding="utf-8")).get("reviews") or []
    by = {}
    for r in rows:
        by.setdefault(r.get("reviewer"), []).append(r)
    latest = {k: sorted(v, key=lambda r: (r.get("round", 1), r.get("date", "")))[-1] for k, v in by.items()}
    fails2 = [k for k, v in by.items() if sum(1 for r in v if r.get("verdict") == "FAIL") >= 2]
    if fails2:
        why = "; ".join(f"{k}: {latest[k].get('reasons', [''])[0]}" for k in fails2)
        return ("todd" if score >= ESCALATE else "dropped"), [f"second FAIL ({why})"]
    need = ("demand", "data-legal", "redteam")
    if all(k in latest and latest[k].get("verdict") == "PASS" for k in need):
        return "todd", []
    if any(latest.get(k, {}).get("verdict") == "FAIL" for k in need):
        return "fix", [f"{k}: {latest[k].get('reasons', [''])[0]}" for k in need if latest.get(k, {}).get("verdict") == "FAIL"]
    return "review", []


def score_one(c, today):
    ks = kills(c, today)
    f, notes = factors(c, today)
    total = round(sum(f[k] / 5 * w for k, w in WEIGHTS.items()))
    m = money(c, today)
    held = c.get("status") in ("go", "built")
    if ks:
        status, why = "killed", ks
    else:
        rs, why = review_state(c.get("slug"), total)
        status = c.get("status") if held else rs or ("review" if total >= REVIEW_FLOOR else "parked")
        if status == "parked":
            why = [f"code score {total} under the review floor {REVIEW_FLOOR}"]
    return {"slug": c.get("slug"), "name": c.get("name"), "score": 0 if ks else total, "factors": f, "notes": notes,
            "kills": ks, "status": status, "why": why, "money": m, "confidence": confidence(c, f, today),
            "firstDollar": first_dollar(c, today).isoformat(), "price": (c.get("price") or {}).get("monthly"),
            "buyer": (c.get("buyer") or {}).get("who"), "source": (c.get("data") or {}).get("url")}


def validate(c, path):
    probs = []
    name = os.path.basename(path)
    if c.get("schema") != SCHEMA:
        probs.append(f"{name}: schema must be {SCHEMA}")
    if c.get("slug") != name[:-5]:
        probs.append(f"{name}: slug must match the file name")
    if c.get("status", "new") not in STATUSES:
        probs.append(f"{name}: status {c.get('status')!r} is not one of {', '.join(STATUSES)}")
    raw = json.dumps(c, ensure_ascii=False)
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", raw):
        probs.append(f"{name}: an email address; candidates carry business-level facts only")
    if "—" in raw or "–" in raw:
        probs.append(f"{name}: an em or en dash")
    for k in ("buyer", "price", "demand", "data", "build", "fit"):
        if not isinstance(c.get(k), dict):
            probs.append(f"{name}: missing object {k!r}")
    return probs


def load_all():
    out = []
    for p in sorted(glob.glob(os.path.join(CAND, "*.json"))):
        out.append((p, json.load(open(p, encoding="utf-8"))))
    return out


def check():
    probs = []
    for p, c in load_all():
        probs += validate(c, p)
    for p in sorted(glob.glob(os.path.join(REV, "*.json"))):
        r = json.load(open(p, encoding="utf-8"))
        for row in r.get("reviews") or []:
            if row.get("reviewer") not in ("demand", "data-legal", "redteam") or row.get("verdict") not in ("PASS", "FAIL"):
                probs.append(f"{os.path.basename(p)}: a review row needs reviewer demand, data-legal or redteam and verdict PASS or FAIL")
            if not isinstance(row.get("score"), (int, float)) or not 1 <= row["score"] <= 5:
                probs.append(f"{os.path.basename(p)}: a review row needs a 1 to 5 score")
    return probs


def write(today):
    rows = sorted((score_one(c, today) for _, c in load_all()), key=lambda r: (r["status"] in ("killed", "dropped"), -r["score"]))
    json.dump({"schema": "pnf.opportunities.v1", "scoredAt": today.isoformat(), "goal": f"${GOAL} month by {GOAL_DATE}",
               "assumptions": {"conversion": CONV, "emailsPerWeek": EMAILS_WEEK, "funnelDays": FUNNEL_DAYS, "gatesDays": GATES_DAYS,
                               "fees": "Gumroad 10% plus $0.50, processing about 2.9% plus $0.30", "ownConversion": OWN_CONVERSION},
               "ranked": rows}, open(OUT_JSON, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    L = [f"# Opportunity list (radar, scored {today.isoformat()})", "",
         "Written by tools/opportunity_score.py from scout/candidates/ and scout/reviews/. Do not edit by hand; edit a candidate file and rerun.",
         f"Goal: ${GOAL} net in one month by {GOAL_DATE}. January net is the expected dollars from this product alone at the desk's outreach cap,",
         f"at {CONV['low']:.2%}, {CONV['likely']:.2%} and {CONV['high']:.2%} of first emails becoming paying members (assumptions until a payer exists).", "",
         "| # | Idea | Status | Score | Jan net (low / likely / high) | Confidence | First $ | Price | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(rows, 1):
        m = r["money"]["janNet"]
        L.append(f"| {i} | {r['name']} | {r['status']} | {r['score']} | ${m['low']} / ${m['likely']} / ${m['high']} | {r['confidence']} | "
                 f"{r['firstDollar']} | ${r['price'] or 0} | {'; '.join(r['why'] or list(r['notes'].values())[:2]) or 'all factors sourced'} |")
    L += ["", "Factor scores (0 to 5): buyer, pay, demand, data, license, effort, speed, fit.", ""]
    for r in rows:
        L.append(f"- {r['slug']}: " + ", ".join(f"{k} {v}" for k, v in r["factors"].items()) + (f". Kill: {'; '.join(r['kills'])}" if r["kills"] else ""))
    open(OUT_MD, "w", encoding="utf-8").write("\n".join(L) + "\n")
    return rows


def selftest():
    today = dt.date(2026, 10, 23)
    S = lambda u="https://example.gov/x", dte="2026-10-20": {"url": u, "date": dte}
    base = {"schema": SCHEMA, "slug": "t", "name": "Test list", "pitch": "new trucking companies for insurance agents",
            "buyer": {"who": "Commercial truck insurance agencies", "count": 400, "countSource": S(), "reach": "agency websites list a business inbox", "reachSource": S()},
            "price": {"monthly": 49, "competitors": [{"name": "X", "monthly": 99, **S()}]},
            "demand": {"searchQueries": [{"q": "new authority leads", **S()}, {"q": "new trucking company leads", **S()}], "aiQueries": [{"q": "where to buy new mc leads", **S()}]},
            "data": {"publisher": "US DOT", "dataset": "carrier census", "subject": "trucking companies", "url": "https://data.transportation.gov/x", "cadence": "daily",
                     "lastUpdated": "2026-10-22", "recordsPerMonth": 5000, "recordsSource": S(), "apiStable": True,
                     "license": {"commercialUse": "allowed", **S()}},
            "build": {"days": 5, "maintHoursMonth": 2}, "fit": {"samePortal": True, "existingTools": ["tools/socrata.py"], "sameBuyerTypes": False}}
    import copy
    def v(**ch):
        c = copy.deepcopy(base)
        for path, val in ch.items():
            o = c
            keys = path.split("__")
            for k in keys[:-1]:
                o = o[k]
            o[keys[-1]] = val
        return score_one(c, today)
    cases, bad = [], 0
    strong = v()
    cases.append(("strong idea reaches review", strong["status"] == "review" and strong["score"] >= 80, strong["score"]))
    cases.append(("strong idea money positive", strong["money"]["janNet"]["likely"] > 0, strong["money"]))
    cases.append(("confidence capped at medium", strong["confidence"] == "medium", strong["confidence"]))
    cases.append(("K1 no reach", v(buyer__reach="")["status"] == "killed", None))
    cases.append(("K1 undated reach source", v(buyer__reachSource={"url": "https://x.org"})["status"] == "killed", None))
    cases.append(("K2 forbidden license", v(data__license={"commercialUse": "forbidden", **S()})["status"] == "killed", None))
    cases.append(("K3 medical", v(pitch="new patients list for clinics")["status"] == "killed", None))
    cases.append(("K3 investment advice", v(pitch="stock picks from filings")["status"] == "killed", None))
    cases.append(("K4 supplements before Sept 2027", v(pitch="new supplement brands for co-packers")["status"] == "killed", None))
    k4later = score_one({**copy.deepcopy(base), "pitch": "new supplement brands"}, dt.date(2027, 10, 1))
    cases.append(("K4 lifts after the non-compete", "killed" != k4later["status"] or any(not k.startswith("K4") for k in k4later["kills"]), k4later["kills"]))
    cases.append(("K5 homeowners", v(data__subject="homeowners with a code violation")["status"] == "killed", None))
    cases.append(("stale data scores 0", v(data__lastUpdated="2026-08-01")["factors"]["data"] == 0, None))
    cases.append(("uncounted volume loses points", v(data__recordsSource=None)["factors"]["data"] < 5, None))
    cases.append(("no competitor price scores 0", v(price__competitors=[])["factors"]["pay"] == 0, None))
    cases.append(("old competitor price not counted", v(price__competitors=[{"name": "X", "monthly": 99, **S(dte="2024-01-01")}])["factors"]["pay"] == 0, None))
    cases.append(("unclear license scores 2", v(data__license={"commercialUse": "unclear", **S()})["factors"]["license"] == 2, None))
    cases.append(("price outside band flagged", "price" in v(price__monthly=249)["notes"], None))
    cases.append(("slow build loses speed", v(build__days=90)["factors"]["speed"] == 0, None))
    weak = v(buyer__count=10, price__competitors=[], demand__searchQueries=[], demand__aiQueries=[])
    cases.append(("weak idea parked", weak["status"] == "parked", weak["score"]))
    # review states, in a throwaway reviews folder
    global REV
    import tempfile
    saved = REV
    REV = tempfile.mkdtemp()
    def rv(rows, score=82):
        json.dump({"reviews": rows}, open(os.path.join(REV, "t.json"), "w"))
        return review_state("t", score)[0]
    P = lambda k, r=1: {"reviewer": k, "verdict": "PASS", "score": 4, "round": r, "reasons": ["ok"]}
    F = lambda k, r=1: {"reviewer": k, "verdict": "FAIL", "score": 2, "round": r, "reasons": ["no buyer pays"]}
    cases.append(("three PASS goes to Todd", rv([P("demand"), P("data-legal"), P("redteam")]) == "todd", None))
    cases.append(("one FAIL is a fix round", rv([P("demand"), F("data-legal"), P("redteam")]) == "fix", None))
    cases.append(("fixed after one FAIL goes to Todd", rv([P("demand"), F("data-legal"), P("data-legal", 2), P("redteam")]) == "todd", None))
    cases.append(("second FAIL drops", rv([P("demand"), F("redteam"), F("redteam", 2), P("data-legal")], 70) == "dropped", None))
    cases.append(("second FAIL on a strong idea goes to Todd", rv([F("demand"), F("demand", 2)], 80) == "todd", None))
    cases.append(("missing reviewer stays in review", rv([P("demand")]) == "review", None))
    REV = saved
    cases.append(("validate catches an email", any("email" in p for p in validate({**base, "note": "a@b.com"}, "t.json")), None))
    cases.append(("validate catches a dash", any("dash" in p for p in validate({**base, "name": "a — b"}, "t.json")), None))
    for label, okay, detail in cases:
        if not okay:
            bad += 1
            print(f"FAIL {label}: {detail}")
    print(f"{'OK' if not bad else 'ERROR'} opportunity_score selftest: {len(cases) - bad} of {len(cases)} planted cases right")
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--today")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.check:
        probs = check()
        for p in probs:
            print("ERROR opportunity:", p)
        print(f"{'OK' if not probs else 'ERROR'} opportunity: {len(load_all())} candidates, {len(probs)} problems")
        sys.exit(1 if probs else 0)
    today = d(a.today) or chicago_today()
    rows = write(today)
    for r in rows:
        m = r["money"]["janNet"]
        print(f"{r['status']:8} {r['score']:3}  ${m['low']}/${m['likely']}/${m['high']}  {r['slug']}")


if __name__ == "__main__":
    main()
