#!/usr/bin/env python3
"""Chicago restaurant daily list: pest and hood places the City posted since the last run (Todd, Oct 23, 2026, move 1).

The founding-seat tier ($149 a month, at most 3 seats per trade in Chicago) gets this list every morning. The $39
weekly list (tools/rest_leads.py) is unchanged. Built in GitHub Actions (.github/workflows/inspections-daily.yml)
from the same dataset the weekly list uses, so the two cannot disagree on a place, a result or a category.

What counts as new: a failed or "Pass w/ Conditions" inspection (not a license inspection) that cited a pest or a
hood and exhaust violation, dated within the last RECENT_DAYS days of what the City has published, and not on an
earlier daily list. The City posts results a few days late and not always in date order, so the window is a few days
wide (two weeks) and the seen file keeps a place from being listed twice for the same inspection. A rerun on the same day rebuilds
the same list (keys first seen today count as not yet seen), so a manual run never empties the morning's list.

Wording rule (Todd, Oct 17): the City's result, inspection type, date and violation codes, in our words. Never the
inspector's notes, never "dirty" or "unsafe". The one-line summary is built from the codes, not the notes.

Outputs:
  named list (members only): written outside the repo by the runner, then sealed (tools/rest_seal.py) to
    permits/inspections-chicago/daily.sealed.json. It names businesses with failed records, so it is never committed
    in clear text and never put on a public page.
  permits/inspections-chicago/daily.json (public): counts by trade, a 30-day history of counts, and up to 3 examples
    with no business name and no street (community area only), for the free page and the cold email lede.
  permits/inspections-chicago/daily-seen.json (public): HMAC-SHA256 keys of inspection ids already listed, 60 days.
    City inspection ids count up, so a plain salted hash could be reversed by trying every id; the HMAC key is the
    REST_DAILY_KEY Actions secret, never given to buyers (until Todd adds it, the REST_LEADS_PASSWORD secret stands in),
    and the run stops if neither is set. When the key changes, old keys stop matching and the next run relists up to
    RECENT_DAYS of places once.
  daily.json also carries pestByDate (failed or conditional inspections that cited pests, per City date, for each of
    the 14 days, with the Restaurant facility type split out) and pestLast7 (the 7 days ending on the newest City date):
    the seat offer's 14-day counts and the pest cold email's {n} (Todd, Oct 24). Counts only.
  The named file also carries "earlier": places sent on an earlier morning whose inspection is still in the window,
    rebuilt each morning from the data and the seen keys, so the members' page shows 14 days and nothing named is kept.
  Public examples carry area, facility type, result and trade only: no date and no inspection type, so a single fail
    in a small area cannot be matched back to the City record.

Phone (move 2): each row carries "phone" and "phoneSource" (and the City's coordinates, for the match), filled by
  tools/phones.py in the runner before the list is sealed. The public file gets only the count of rows with a phone.

Usage: REST_DAILY_KEY=... python3 tools/rest_daily.py DATASET.json NAMED_OUT.json   (DATASET from rest_leads.py RAW OUT)
       python3 tools/rest_daily.py --selftest
"""
import datetime as dt, hashlib, hmac, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rest_leads as RL  # noqa: E402

OUT_DIR = os.path.join(ROOT, "permits", "inspections-chicago")
PUBLIC = os.path.join(OUT_DIR, "daily.json")
SEEN = os.path.join(OUT_DIR, "daily-seen.json")
SALT = "proofnotfluff-rest-daily-v2-hmac"
RECENT_DAYS, KEEP_DAYS, HISTORY_DAYS = 14, 60, 30
TRADES = [("pests", "Pest control", "pests"), ("hood", "Hood and exhaust cleaning", "hood and exhaust")]
TRADE_KEYS = [k for k, _, _ in TRADES]
WORDS = {k: w for k, _, w in TRADES}


def key(inspection_id, secret):
    assert secret, "no HMAC key: set REST_DAILY_KEY"
    return hmac.new(secret.encode(), (SALT + "|" + str(inspection_id)).encode(), hashlib.sha256).hexdigest()[:24]


def load_seen(path=SEEN):
    if not os.path.exists(path):
        return {}
    d = json.load(open(path))
    assert d.get("salt") == SALT, "seen file salt changed"
    return dict(d.get("keys", {}))


def summary(x):
    """One plain line from the City's fields: result, inspection type, date, and the codes in our words."""
    parts = [f"{WORDS[c]} (code{'s' if len(x['c'][c]) > 1 else ''} {', '.join(str(n) for n in x['c'][c])})"
             for c in TRADE_KEYS if c in x["c"]]
    cited = parts[0] if len(parts) == 1 else " and ".join(parts)
    return f"{x['r']} on a {x['t'].lower()} inspection, {RL.pretty(x['d'])}. The City cited {cited}."


def row(pk, p, iid, x, trades, listed_on):
    """One named row for the members' list. listedOn: the morning this place first went out on a daily list."""
    return {"place": pk, "name": p["name"], "address": p["address"], "zip": p["zip"], "area": p["area"] or "Chicago",
            "type": p["type"], "date": x["d"], "result": x["r"], "inspectionType": x["t"], "trades": trades,
            "codes": {c: x["c"][c] for c in trades}, "summary": summary(x), "record": RL.RECORD + iid,
            "fails90": p["fails90"], "lat": p.get("lat"), "lon": p.get("lon"), "listedOn": listed_on,
            "phone": "", "phoneSource": ""}


def earlier(data, seen, secret, recent_from, today_places):
    """Places already sent on an earlier morning whose newest qualifying inspection is still inside the window, so a
    member who missed a morning loses nothing (move 3, Oct 24). Rebuilt each morning from the City's data and the seen
    keys, so nothing named is stored between runs. listedOn is the morning the place first went out."""
    before = {k: v for k, v in seen.items() if v < data["asOf"]}
    P, I = data["places"], data["inspections"]
    out = []
    for pk in data["lists"]["flagged"]:
        if pk in today_places:
            continue
        p = P[pk]
        for iid in p["flaggedIds"]:                       # newest first
            x = I[iid]
            trades = [c for c in TRADE_KEYS if c in x["c"]]
            if x["d"] < recent_from or not trades:
                continue
            days = [before[key(i, secret)] for i in [iid] + list(x.get("dup") or []) if key(i, secret) in before]
            if days:
                out.append(row(pk, p, iid, x, trades, min(days)))
            break
    out.sort(key=lambda it: (it["date"], it["name"]))
    out.sort(key=lambda it: (it["listedOn"], it["date"]), reverse=True)
    return out


def pest_counts(data, recent_from):
    """Public counts for the seat offer and the cold email (Todd, Oct 24): failed or conditional inspections that cited
    pests, one per visit (duplicate reports are already merged), by the City's inspection date, for every day of the
    window. "restaurant": those at places whose City facility type is Restaurant. last7: the 7 days ending on the newest
    date the City has published (the email's {n}; never the daily file's total). Counts only, no names, no places."""
    P, I = data["places"], data["inspections"]
    through = dt.date.fromisoformat(data["through"])
    days = [(through - dt.timedelta(days=i)).isoformat() for i in range(RECENT_DAYS - 1, -1, -1)]
    by = {d: {"date": d, "pests": 0, "restaurant": 0} for d in days}
    done = set()
    for pk in data["lists"]["flagged"]:
        p = P[pk]
        for iid in p["flaggedIds"]:
            x = I[iid]
            if iid in done or x["d"] not in by or "pests" not in x["c"]:
                continue
            done.add(iid)
            by[x["d"]]["pests"] += 1
            by[x["d"]]["restaurant"] += p["type"] == "Restaurant"
    seven = days[-7:]
    last7 = {"from": seven[0], "to": seven[-1], "inspections": sum(by[d]["pests"] for d in seven),
             "restaurantInspections": sum(by[d]["restaurant"] for d in seven)}
    return [by[d] for d in days], last7


def pick(data, seen, secret):
    """New pest and hood rows: (items, ids to mark seen). One item per place, its newest qualifying inspection.
    Keys first seen today do not count, so a same-day rerun gives the same list."""
    seen = {k for k, v in seen.items() if v < data["asOf"]}
    P, I = data["places"], data["inspections"]
    through = dt.date.fromisoformat(data["through"])
    recent_from = (through - dt.timedelta(days=RECENT_DAYS - 1)).isoformat()
    items, mark = [], []
    for pk in data["lists"]["flagged"]:
        p = P[pk]
        for iid in p["flaggedIds"]:                       # newest first
            x = I[iid]
            trades = [c for c in TRADE_KEYS if c in x["c"]]
            if x["d"] < recent_from or not trades:
                continue
            ids = [iid] + list(x.get("dup") or [])
            if any(key(i, secret) in seen for i in ids):
                break                                      # this place's newest qualifying visit is already out
            items.append(row(pk, p, iid, x, trades, data["asOf"]))
            mark += ids
            break
    items.sort(key=lambda it: (it["date"], it["name"]))
    items.sort(key=lambda it: it["date"], reverse=True)
    return items, mark, recent_from


def public(data, items, recent_from, old=None):
    """The public file: counts and unnamed examples only."""
    counts = {c: sum(1 for it in items if c in it["trades"]) for c in TRADE_KEYS}
    counts["places"] = len(items)
    hist = [h for h in (old or {}).get("history", []) if h.get("asOf") != data["asOf"]]
    hist.append({"asOf": data["asOf"], "through": data["through"], **counts})
    hist = sorted(hist, key=lambda h: h["asOf"])[-HISTORY_DAYS:]
    ex = [{"area": it["area"], "type": it["type"], "result": it["result"], "trades": [WORDS[c] for c in it["trades"]]}
          for it in items if it["area"] and it["area"] != "Chicago"][:3]
    by_date, last7 = pest_counts(data, recent_from)
    return {"product": "Chicago Restaurant Daily List", "asOf": data["asOf"], "asOfText": data["asOfText"],
            "through": data["through"], "throughText": data["throughText"], "recentFrom": recent_from,
            "source": data["source"], "counts": counts, "history": hist, "examples": ex,
            "pestByDate": by_date, "pestLast7": last7,
            "note": "Places the City posted since the last daily list, with a failed or conditional result that cited a pest "
                    "or a hood and exhaust violation. Business names are sent only to members."}


def run(data, named_out, secret, public_path=PUBLIC, seen_path=SEEN):
    seen = load_seen(seen_path)
    items, mark, recent_from = pick(data, seen, secret)
    before = earlier(data, seen, secret, recent_from, {it["place"] for it in items})
    today = data["asOf"]
    for k in mark:
        seen.setdefault(key(k, secret), today)
    cut = (dt.date.fromisoformat(today) - dt.timedelta(days=KEEP_DAYS)).isoformat()
    seen = {k: v for k, v in seen.items() if v >= cut}
    old = json.load(open(public_path)) if os.path.exists(public_path) else None
    pub = public(data, items, recent_from, old)
    named = {"product": "Chicago Restaurant Daily List", "asOf": today, "through": data["through"], "recentFrom": recent_from,
             "source": data["source"], "counts": pub["counts"], "items": items, "earlier": before,
             "pestByDate": pub["pestByDate"], "pestLast7": pub["pestLast7"]}
    json.dump(named, open(named_out, "w"), indent=1)
    json.dump(pub, open(public_path, "w"), indent=1)
    json.dump({"about": "Inspection ids already sent on a daily list, as HMAC-SHA256 keys under a secret (tools/rest_daily.py). No names, no ids.",
               "salt": SALT, "keys": dict(sorted(seen.items()))}, open(seen_path, "w"), indent=1)
    return named, pub


def selftest():
    import tempfile
    V, T, C = RL.V, RL.T, RL.CAT_CASES
    pest_v, hood_v = C[0][0], C[3][0]
    assert RL.categorize(pest_v) == {"pests": [38]} and RL.categorize(hood_v) == {"hood": [56]}, "planted notes moved category"
    base = {"address": "1234 W MAIN ST ", "zip": "60601", "latitude": "41.88", "longitude": "-87.63", "risk": "Risk 1 (High)",
            "_area": "Loop", "facility_type": "Restaurant"}
    R = lambda i, name, lic, typ, res, day, v="", **kw: dict(base, inspection_id=str(i), dba_name=name, license_=lic, inspection_type=typ,
                                                            results=res, inspection_date=day + "T00:00:00.000", violations=v, **kw)

    def raw(rows, fetched):
        return {"source": {"name": "x", "url": RL.DATASET_PAGE, "fetchedAt": fetched, "terms": RL.CITY_TERMS},
                "rows": rows, "history": []}
    day1 = [
        R(1, "ACME TACOS", "111", "Canvass", "Fail", "2026-10-21", pest_v),                       # pests, recent
        R(2, "FRY HOUSE", "444", "Complaint", "Pass w/ Conditions", "2026-10-20", hood_v),        # hood, recent
        R(3, "BOTH GRILL", "555", "Canvass", "Fail", "2026-10-21", pest_v + " | " + hood_v, _area="West Town"),  # both trades
        R(4, "OLD FAIL", "666", "Canvass", "Fail", "2026-10-01", pest_v),                         # outside the 14-day window
        R(5, "NO TRADE BAR", "777", "Canvass", "Fail", "2026-10-21", V(10, "NO SOAP")),           # nothing a seat buyer does
        R(6, "NEW PLACE", "888", "License", "Fail", "2026-10-21", pest_v),                        # license inspection: not flagged
        R(7, "CLEAN CAFE", "999", "Canvass", "Pass", "2026-10-21", pest_v),                       # passed: not flagged
        R(8, "KIPP ONE ACADEMY", "1010", "Canvass", "Fail", "2026-10-21", pest_v, facility_type="School"),
        R(9, "FRY HOUSE", "444", "Complaint", "Pass w/ Conditions", "2026-10-20", hood_v),        # duplicate report of id 2
    ]
    tmp = tempfile.mkdtemp()
    pub_p, seen_p, out_p = (os.path.join(tmp, n) for n in ("daily.json", "seen.json", "named.json"))
    SK = "planted-secret"
    d1 = RL.build(raw(day1, "2026-10-22T12:00:00+00:00"), set())
    n1, p1 = run(d1, out_p, SK, pub_p, seen_p)
    names = [it["name"] for it in n1["items"]]
    assert names == ["Acme Tacos", "Both Grill", "Fry House"], names
    both = next(it for it in n1["items"] if it["name"] == "Both Grill")
    assert both["trades"] == ["pests", "hood"] and both["codes"] == {"pests": [38], "hood": [56]}, both
    assert both["summary"] == "Fail on a canvass inspection, Oct 21, 2026. The City cited pests (code 38) and hood and exhaust (code 56).", both["summary"]
    assert p1["counts"] == {"pests": 2, "hood": 2, "places": 3}, p1["counts"]
    assert n1["recentFrom"] == "2026-10-08", n1["recentFrom"]
    assert n1["earlier"] == [] and p1["pestLast7"]["inspections"] == 2 and p1["pestLast7"]["restaurantInspections"] == 2, p1["pestLast7"]
    blob = json.dumps(p1) + open(seen_p).read()
    for leak in ("Acme", "Fry House", "Both Grill", "Main St", "MAIN", "111", "444", "2026-10-21", "Canvass"):
        assert leak not in json.dumps(p1["examples"]) + open(seen_p).read(), f"public file identifies a failed place: {leak}"
    for leak in ("Acme", "Fry House", "Both Grill", "Main St", "MAIN"):
        assert leak not in blob, f"public file names a failed place: {leak}"
    assert all(set(e) == {"area", "type", "result", "trades"} for e in p1["examples"]), p1["examples"]
    assert [e["area"] for e in p1["examples"]] == ["Loop", "West Town", "Loop"], p1["examples"]
    for t in json.dumps(n1).upper(), json.dumps(p1).upper():
        assert "COMMENTS" not in t and "NO SOAP" not in t and "DIRTY" not in t and "UNSAFE" not in t, "notes or judgment words leaked"
    # the seen keys cannot be reversed without the secret: trying every id with the public salt matches nothing
    keys = set(json.load(open(seen_p))["keys"])
    guess = lambda i: hashlib.sha256((SALT + "|" + str(i)).encode()).hexdigest()
    assert not any(guess(i)[:24] in keys or guess(i)[:20] in keys for i in range(0, 2000)), "seen keys reversible without the secret"
    assert key(1, SK) in keys and key(1, "other") not in keys and key(1, SK) != key(1, "other")
    try:
        key(1, "")
        raise SystemExit("rest_daily selftest FAIL: ran without an HMAC key")
    except AssertionError:
        pass
    # same day, run again (a manual dispatch): the same list and the same history, never an empty morning
    n1b, p1b = run(d1, out_p, SK, pub_p, seen_p)
    assert [it["name"] for it in n1b["items"]] == names and p1b["counts"] == p1["counts"], "a same-day rerun changed the list"
    assert len(p1b["history"]) == 1 and p1b["history"][0]["places"] == 3 and json.load(open(seen_p))["keys"] == {k: "2026-10-22" for k in keys}
    # day 2: the same rows, a late post (dated 2 days back), a very late post (10 days back) and a new fail at a listed place
    day2 = day1 + [R(10, "LATE POST DINER", "1212", "Canvass", "Fail", "2026-10-20", pest_v),
                   R(11, "ACME TACOS", "111", "Canvass Re-Inspection", "Fail", "2026-10-22", pest_v),
                   R(12, "VERY LATE GRILL", "1313", "Complaint", "Fail", "2026-10-12", hood_v),
                   R(13, "CORNER MART", "1414", "Canvass", "Fail", "2026-10-22", pest_v, facility_type="Grocery Store")]
    d2 = RL.build(raw(day2, "2026-10-23T12:00:00+00:00"), set())
    n2, p2 = run(d2, out_p, SK, pub_p, seen_p)
    assert [it["name"] for it in n2["items"]] == ["Acme Tacos", "Corner Mart", "Late Post Diner", "Very Late Grill"], [it["name"] for it in n2["items"]]
    assert all(it["listedOn"] == "2026-10-23" for it in n2["items"])
    # earlier mornings stay on the members' list while their inspection is in the window (move 3); today's places are not repeated
    assert [(it["name"], it["listedOn"]) for it in n2["earlier"]] == [("Both Grill", "2026-10-22"), ("Fry House", "2026-10-22")], n2["earlier"]
    # pest counts by City date: one per visit, every day of the window, restaurant type split, the 7 days ending on "through"
    bd = {b["date"]: b for b in p2["pestByDate"]}
    assert len(p2["pestByDate"]) == 14 and p2["pestByDate"][0]["date"] == "2026-10-09" and p2["pestByDate"][-1]["date"] == "2026-10-22"
    assert (bd["2026-10-21"]["pests"], bd["2026-10-22"]["pests"], bd["2026-10-22"]["restaurant"], bd["2026-10-20"]["pests"]) == (2, 2, 1, 1), bd
    assert sum(b["pests"] for b in p2["pestByDate"]) == 5 and bd["2026-10-12"]["pests"] == 0, "hood-only visit counted as pests"
    assert p2["pestLast7"] == {"from": "2026-10-16", "to": "2026-10-22", "inspections": 5, "restaurantInspections": 4}, p2["pestLast7"]
    assert "Corner" not in json.dumps(p2) and "Acme" not in json.dumps(p2), "public counts name a place"
    assert n2["items"][0]["date"] == "2026-10-22", "a new visit to a listed place comes back once"
    assert [h["asOf"] for h in p2["history"]] == ["2026-10-22", "2026-10-23"] and p2["history"][-1]["places"] == 4, p2["history"]
    # day 3: nothing new posted, so nothing is listed twice
    n3, p3 = run(RL.build(raw(day2, "2026-10-24T12:00:00+00:00"), set()), out_p, SK, pub_p, seen_p)
    assert n3["items"] == [] and p3["counts"] == {"pests": 0, "hood": 0, "places": 0}, n3["items"]
    assert [it["name"] for it in n3["earlier"]] == ["Acme Tacos", "Corner Mart", "Late Post Diner", "Very Late Grill", "Both Grill", "Fry House"], [it["name"] for it in n3["earlier"]]
    assert n3["earlier"][0]["date"] == "2026-10-22" and n3["earlier"][0]["listedOn"] == "2026-10-23", "earlier row lost the newer visit"
    s = json.load(open(seen_p))
    assert s["salt"] == SALT and len(s["keys"]) == 8, s
    # seen keys age out after KEEP_DAYS
    run(RL.build(raw(day2, "2026-12-31T12:00:00+00:00"), set()), out_p, SK, pub_p, seen_p)
    assert json.load(open(seen_p))["keys"] == {}, "old seen keys kept"
    for t in (__doc__ or "", summary.__doc__ or "", pick.__doc__ or ""):
        assert chr(0x2014) not in t and chr(0x2013) not in t
    print("rest_daily selftest ok (13 planted inspections over 4 days: window, trades, duplicates, late posts, same-day rerun, "
          "no repeats, earlier mornings kept, pest counts by date and last 7 days, HMAC keys, no names in public files)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif len(a) == 2:
        secret = os.environ.get("REST_DAILY_KEY", "") or os.environ.get("REST_LEADS_PASSWORD", "")
        if not secret:
            raise SystemExit("rest_daily: neither REST_DAILY_KEY nor REST_LEADS_PASSWORD is set; the seen keys need one. Stopping.")
        if not os.environ.get("REST_DAILY_KEY"):
            print("rest_daily: REST_DAILY_KEY not set yet; using the members' password as the key")
        named, pub = run(json.load(open(a[0])), a[1], secret)
        print(json.dumps({"asOf": pub["asOf"], "through": pub["through"], **pub["counts"]}))
    else:
        raise SystemExit(__doc__)
