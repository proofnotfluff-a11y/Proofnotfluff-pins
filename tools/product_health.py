#!/usr/bin/env python3
"""Weekly health check for every live lead product (radar, Todd, Oct 23, 2026: "there is also going to be
maintenance of that product on an ongoing basis").

Two halves, because the cloud agents cannot reach the City portals:
  --live   runs on GitHub's runner (.github/workflows/product-health.yml) and writes qa/health/<date>.json:
           source   the dataset's own metadata: every expected column still there, rows updated recently
           fresh    our data file was fetched within freshDays
           holdout  up to 5 random records from our published sample, looked up in the source by id: found, same date
           links    the product page and members' page answer 200; the page still says "7-day free trial" and carries
                    the checkout; the Gumroad checkout answers 200 and shows the price (the trial text there is
                    checked when the page shows it, else "not confirmed")
  --repo   runs anywhere: the wiring of every live product (tools/product_wire.py) and the newest qa/health report,
           one PASS or FAIL line a product. Exit 1 on any FAIL. The radar run turns each FAIL into a to-do and a
           message to Todd.
The report holds counts and results only: no business name, address or person (CLAUDE.md 5).

Usage: python3 tools/product_health.py --live [--out qa/health/<date>.json]
       python3 tools/product_health.py --repo
       python3 tools/product_health.py --selftest
"""
import argparse, datetime as dt, glob, json, os, random, re, sys, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
UA = {"User-Agent": "ProofNotFluff product health (github.com/proofnotfluff-a11y/proofnotfluff-pins)"}
SITE = "https://proofnotfluff.com/"
SAMPLE_N = 5


def today():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date()
    except Exception:
        return dt.date.today()


def http(url, timeout=40):
    """(status, text). Never raises."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception as e:
        return 0, f"{type(e).__name__}"


def records(d, path):
    x = d.get(path)
    out = []
    if isinstance(x, list):
        out = x
    elif isinstance(x, dict):
        for v in x.values():
            if isinstance(v, list):
                out += v
            elif isinstance(v, dict):
                for w in v.values():
                    if isinstance(w, list):
                        out += w
    return [r for r in out if isinstance(r, dict)]


def q(s):
    return str(s).replace("'", "''")


def holdout(e, data, fetch, rng):
    h = e.get("holdout") or {}
    portal, ds = e["source"]["portal"], e["source"]["dataset"]
    rows = records(data, h.get("path") or "")
    pick = rng.sample(rows, min(SAMPLE_N, len(rows))) if rows else []
    found = same = 0
    for r in pick:
        if h.get("field") and h.get("id"):
            where = f"{h['field']}='{q(r.get(h['id']))}'"
            if h["field"] == "doing_business_as_name":
                where = f"({where} OR legal_name='{q(r.get(h['id']))}')"
        else:
            parts = [f"{col}='{q(r.get(k))}'" for k, col in (h.get("match") or {}).items() if r.get(k) is not None]
            if h.get("dateField") and r.get(h.get("date")):
                parts.append(f"date_trunc_ymd({h['dateField']})='{q(r[h['date']])}T00:00:00.000'")
            where = " AND ".join(parts)
        url = f"{portal}/resource/{ds}.json?" + urllib.parse.urlencode({"$where": where, "$limit": 20})
        code, body = fetch(url)
        try:
            got = json.loads(body) if code == 200 else []
        except ValueError:
            got = []
        if got:
            found += 1
            if not h.get("dateField") or not h.get("date") or any(str(g.get(h["dateField"], ""))[:10] == str(r.get(h["date"]))[:10] for g in got):
                same += 1
    ok = bool(pick) and found == len(pick) and same == len(pick)
    return {"result": "PASS" if ok else "FAIL", "sampled": len(pick), "found": found, "sameDate": same}


def live_one(slug, e, fetch, on, rng):
    out = {"slug": slug}
    portal, ds = e["source"]["portal"], e["source"]["dataset"]
    code, body = fetch(f"{portal}/api/views/{ds}.json")
    try:
        meta = json.loads(body) if code == 200 else {}
    except ValueError:
        meta = {}
    cols = [c.get("fieldName") for c in meta.get("columns", [])]
    miss = [c for c in e["source"]["expectColumns"] if c not in cols]
    upd = meta.get("rowsUpdatedAt")
    upd_day = dt.datetime.fromtimestamp(upd, dt.timezone.utc).date() if isinstance(upd, (int, float)) else None
    stale_src = upd_day is None or (on - upd_day).days > int(e.get("freshDays") or 9)
    out["source"] = {"result": "PASS" if meta and not miss and not stale_src else "FAIL", "http": code,
                     "missingColumns": miss, "rowsUpdatedAt": upd_day.isoformat() if upd_day else None}
    data = json.load(open(os.path.join(ROOT, e["data"]), encoding="utf-8"))
    f = str(((data.get("source") or {}).get("fetchedAt")) or data.get("asOf") or "")[:10]
    try:
        age = (on - dt.date.fromisoformat(f)).days
    except ValueError:
        age = None
    out["fresh"] = {"result": "PASS" if age is not None and age <= int(e.get("freshDays") or 9) else "FAIL", "fetchedAt": f, "ageDays": age}
    out["holdout"] = holdout(e, data, fetch, rng)
    pc, ptxt = fetch(f"{SITE}{slug}/")
    mc, _ = fetch(f"{SITE}{e['members']}/")
    spec = next((p for p in json.load(open(os.path.join(ROOT, "site/pages.json"), encoding="utf-8"))["pages"] if p["slug"] == slug), {})
    co = str(spec.get("checkout", ""))
    cc, ctxt = fetch(co) if co else (0, "")
    price = str(e.get("price"))
    trial_gum = "confirmed" if re.search(r"(7|seven)[- ]day", ctxt, re.I) and re.search(r"trial", ctxt, re.I) else "not confirmed"
    link_ok = pc == 200 and mc == 200 and "7-day free trial" in ptxt and co.split("?")[0] in ptxt and cc == 200 and f"${price}" in ctxt
    out["links"] = {"result": "PASS" if link_ok else "FAIL", "page": pc, "members": mc, "checkout": cc,
                    "pageSaysTrial": "7-day free trial" in ptxt, "checkoutOnPage": co.split("?")[0] in ptxt,
                    "priceOnCheckout": f"${price}" in ctxt, "trialOnGumroad": trial_gum}
    out["result"] = "PASS" if all(out[k]["result"] == "PASS" for k in ("source", "fresh", "holdout", "links")) else "FAIL"
    return out


def live(out_path=None, fetch=http, on=None, seed=None):
    on = on or today()
    rng = random.Random(seed)
    w = json.load(open(os.path.join(ROOT, "launches", "WIRING.json"), encoding="utf-8"))["products"]
    rep = {"schema": "pnf.health.v1", "date": on.isoformat(), "products": [live_one(s, e, fetch, on, rng) for s, e in w.items() if e.get("status") == "live"]}
    rep["result"] = "PASS" if all(p["result"] == "PASS" for p in rep["products"]) else "FAIL"
    out_path = out_path or os.path.join(ROOT, "qa", "health", f"{on.isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(rep, open(out_path, "w", encoding="utf-8"), indent=1)
    for p in rep["products"]:
        print(summary(p))
    return rep


def summary(p):
    bits = [f"source {p['source']['result']}" + (f" (missing {', '.join(p['source']['missingColumns'][:3])})" if p["source"].get("missingColumns") else ""),
            f"fresh {p['fresh']['result']} {p['fresh'].get('ageDays')}d",
            f"holdout {p['holdout']['result']} {p['holdout']['found']}/{p['holdout']['sampled']}",
            f"links {p['links']['result']}", f"Gumroad trial {p['links']['trialOnGumroad']}"]
    return f"{p['result']} {p['slug']}: " + ", ".join(bits)


def repo():
    import product_wire
    lines, _ = product_wire.run()
    probs = {}
    for l in lines:
        m = re.match(r"(WARN|ERROR) wire (\S+) (\w+): (.*)", l)
        if m:
            probs.setdefault(m.group(2), []).append(f"{m.group(3)}: {m.group(4)}")
    reports = sorted(glob.glob(os.path.join(ROOT, "qa", "health", "*.json")))
    rep = json.load(open(reports[-1], encoding="utf-8")) if reports else None
    w = json.load(open(os.path.join(ROOT, "launches", "WIRING.json"), encoding="utf-8"))["products"]
    bad = 0
    for s, e in w.items():
        if e.get("status") != "live":
            continue
        lp = next((p for p in (rep or {}).get("products", []) if p["slug"] == s), None)
        live_line = summary(lp) if lp else "no runner report yet (dispatch product-health)"
        fail = (lp is None) or lp["result"] != "PASS"
        bad += fail
        print(f"{'FAIL' if fail else 'PASS'} {s}: runner {rep['date'] if rep else 'none'}: {live_line.split(': ', 1)[-1]}; wiring gaps {len(probs.get(s, []))}"
              + (f" ({'; '.join(probs[s][:3])})" if probs.get(s) else ""))
    print(f"product_health: {bad} of {sum(1 for e in w.values() if e.get('status') == 'live')} live products failing")
    return bad


def selftest():
    w = json.load(open(os.path.join(ROOT, "launches", "WIRING.json"), encoding="utf-8"))["products"]
    slug, e = "chicago-construction-cleaning-leads", w["chicago-construction-cleaning-leads"]
    data = json.load(open(os.path.join(ROOT, e["data"]), encoding="utf-8"))
    spec = next(p for p in json.load(open(os.path.join(ROOT, "site/pages.json")))["pages"] if p["slug"] == slug)
    on = dt.date.fromisoformat(data["source"]["fetchedAt"][:10])
    stamp = dt.datetime(on.year, on.month, on.day, tzinfo=dt.timezone.utc).timestamp()
    ids = {r["permit"]: r["issued"] for r in records(data, "projects")}
    def make(cols=None, upd=stamp, page_trial=True, gum_price=True, drift=False):
        cols = cols if cols is not None else e["source"]["expectColumns"]
        def fetch(url):
            if "/api/views/" in url:
                return 200, json.dumps({"columns": [{"fieldName": c} for c in cols], "rowsUpdatedAt": upd})
            if "/resource/" in url:
                pid = re.search(r"permit_%3D%27([^%]+)%27", url)
                pid = pid.group(1) if pid else ""
                return 200, json.dumps([{"permit_": pid, "issue_date": ("2001-01-01" if drift else ids.get(pid, "")) + "T00:00:00.000"}] if pid in ids else [])
            if "gumroad" in url:
                return 200, ("$29 a month, 7 day free trial" if gum_price else "sold out")
            if url.endswith(f"{slug}/"):
                return 200, (("7-day free trial " if page_trial else "") + spec["checkout"].split("?")[0])
            return 200, "ok"
        return fetch
    def one(**k):
        return live_one(slug, e, make(**k), on, random.Random(7))
    cases = [("healthy product passes", one()["result"] == "PASS", one()),
             ("dropped column fails source", one(cols=e["source"]["expectColumns"][1:])["source"]["result"] == "FAIL", None),
             ("source not updated fails", one(upd=stamp - 40 * 86400)["source"]["result"] == "FAIL", None),
             ("holdout date drift fails", one(drift=True)["holdout"]["result"] == "FAIL", None),
             ("trial text gone fails links", one(page_trial=False)["links"]["result"] == "FAIL", None),
             ("checkout price gone fails links", one(gum_price=False)["links"]["result"] == "FAIL", None),
             ("Gumroad trial read", one()["links"]["trialOnGumroad"] == "confirmed", None),
             ("stale data fails fresh", live_one(slug, e, make(), on + dt.timedelta(days=30), random.Random(7))["fresh"]["result"] == "FAIL", None)]
    rep_text = json.dumps(one())
    cases.append(("report carries no names or addresses", not any(str(r.get("address", "zz")) in rep_text for r in records(data, "projects")), None))
    bad = 0
    for label, okay, detail in cases:
        if not okay:
            bad += 1
            print(f"FAIL {label}: {str(detail)[:300]}")
    print(f"{'OK' if not bad else 'ERROR'} product_health selftest: {len(cases) - bad} of {len(cases)} planted cases right")
    return bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--repo", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.live:
        rep = live(a.out)
        sys.exit(0 if rep["result"] == "PASS" else 1)
    sys.exit(1 if repo() else 0)


if __name__ == "__main__":
    main()
