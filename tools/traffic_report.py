#!/usr/bin/env python3
"""Weekly website traffic report for proofnotfluff.com (Todd's go, Oct 26, 2026, 11:02 am: "Go with your
recommendation"). Answers two questions every Monday: how much traffic the site gets, and which free pages
(calculators, question pages, lead pages, the weekly City pages) bring it in.

Runs in GitHub Actions (.github/workflows/traffic-weekly.yml) with one read-only Cloudflare API token, the repo secret
CF_ANALYTICS_TOKEN (permissions: Account, Account Analytics, Read; Account, Account Settings, Read). It reads Cloudflare
Web Analytics, the cookie-free counter already on every page (site/analytics.json holds the site's public beacon token),
through Cloudflare's GraphQL API, and writes counts only to seo/traffic/weekly.json and seo/traffic/history.json:
visits and page views per page, where visits came from (by referring site), and the anonymous stage counts each
calculator records (e/<slug>/use/ when someone types a number, e/<slug>/upgrade/ when someone clicks to buy). No IP,
visitor, device or anything a visitor typed is ever read or written. Cloudflare samples low traffic, so small numbers
are estimates; the report says so.

Google search numbers (impressions, clicks, position per page) come from seo/search-console.json, which the Friday
index-request run writes from Search Console on Todd's PC; the report attaches them when that file is under 10 days old.

The scoreboard's Website traffic panel shows meta/traffic, which the Monday scheduled task copies from weekly.json.

Usage: python3 tools/traffic_report.py             pull last week (Mon to Sun, Chicago) and write the files
       python3 tools/traffic_report.py --selftest  planted API answers, no network
"""
import argparse, datetime as dt, json, os, re, sys, urllib.request
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "seo", "traffic")
API = "https://api.cloudflare.com/client/v4"
CHI = ZoneInfo("America/Chicago")
HOST = "proofnotfluff.com"
SEARCH = [("Google", r"(^|\.)google\.[a-z.]+$"), ("Bing", r"(^|\.)bing\.com$"), ("DuckDuckGo", r"(^|\.)duckduckgo\.com$"),
          ("Yahoo", r"(^|\.)yahoo\.com$"), ("Ecosia", r"(^|\.)ecosia\.org$")]
AI = r"(^|\.)(chatgpt\.com|openai\.com|perplexity\.ai|claude\.ai|gemini\.google\.com|copilot\.microsoft\.com)$"
SOCIAL = r"(^|\.)(facebook\.com|instagram\.com|linkedin\.com|lnkd\.in|pinterest\.[a-z.]+|t\.co|x\.com|twitter\.com|youtube\.com|tiktok\.com|reddit\.com)$"
ZERO_WEEKS = 3       # a live page with no visits this long gets flagged
# Our own visits (audit Oct 29, 2026, Todd's yes): the site's tag skips automated browsers and any browser opened once with
# ?pnf-internal=1 (tools/make_site.py analytics_tag), so they never reach Cloudflare from Oct 29 on. Our preview pages are
# also left out here; they are counted under ownLeftOut instead of as visits.
OWN = re.compile(r"^preview(/|$)")
OWN_FROM = "2026-10-29"


def source_of(host):
    h = (host or "").lower().strip().rstrip(".")
    if not h or h == HOST or h.endswith("." + HOST):
        return "Direct"
    for name, pat in SEARCH:
        if re.search(pat, h):
            return name
    if re.search(AI, h):
        return "AI assistants"
    if re.search(SOCIAL, h):
        return "Social"
    if h.endswith("etsy.com") or h.endswith("gumroad.com"):
        return "Etsy and Gumroad"
    return "Other sites"


def is_search(label):
    return label in {n for n, _ in SEARCH}


def week_window(today):
    """Last whole Monday to Sunday in Chicago before `today`, and the week before it, as UTC datetimes."""
    monday = today - dt.timedelta(days=today.weekday())        # this week's Monday
    start = monday - dt.timedelta(days=7)
    to_utc = lambda d: dt.datetime.combine(d, dt.time(0), CHI).astimezone(dt.timezone.utc)
    return {"from": start, "to": monday - dt.timedelta(days=1), "fromUtc": to_utc(start), "toUtc": to_utc(monday),
            "prevFromUtc": to_utc(start - dt.timedelta(days=7)), "prevToUtc": to_utc(start),
            "trendFromUtc": to_utc(monday - dt.timedelta(days=84))}


def path_slug(path):
    p = (path or "/").split("?")[0].split("#")[0]
    p = re.sub(r"/index\.html$", "/", p)
    m = re.match(r"^/e/([^/]+)/(use|upgrade)/?$", p)
    if m:
        return None, (m.group(1), m.group(2))
    s = p.strip("/")
    return (s or "home"), None


def load_pages():
    """Live pages: docs/sitemap.xml is the live list; site/pages.json gives each its name, kind and publish date."""
    locs = re.findall(r"<loc>https://proofnotfluff\.com/([^<]*)</loc>", open(os.path.join(ROOT, "docs", "sitemap.xml"), encoding="utf-8").read())
    specs = {p["slug"]: p for p in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"]}
    kinds = {"question": "Question page", "leads": "Lead list", "restleads": "Lead list", "licleads": "Lead list",
             "newin": "Weekly City page", "rodents": "Weekly City page"}
    out = {}
    for loc in locs:
        slug = loc.strip("/") or "home"
        sp = specs.get(slug, {})
        name = sp.get("h1") or {"home": "Home", "shop": "Shop", "calculators": "Free calculators", "questions": "Questions"}.get(slug, slug.replace("-", " ").capitalize())
        kind = "Calculator" if sp and sp.get("kind") not in kinds else kinds.get(sp.get("kind"), "Other page")
        out[slug] = {"slug": slug, "name": name, "kind": kind, "published": sp.get("published", ""), "staged": bool(sp.get("stages"))}
    return out


def build(by_path, prev_path, by_source, by_week, w, pages, fetched, search=None):
    """by_path/prev_path: [{path, views, visits}]; by_source: [{path, host, visits}]; by_week: [{date, visits}]."""
    rows, stage, own = {}, {}, {"visits": 0, "views": 0}
    def add(table, r, key):
        slug, st = path_slug(r["path"])
        if slug and OWN.match(slug):
            if key == "now":
                own["visits"] += int(r.get("visits", 0)); own["views"] += int(r.get("views", 0))
            return
        if st:
            if key == "now":
                stage.setdefault(st[0], {"use": 0, "upgrade": 0})[st[1]] += int(r.get("views", 0))
            return
        x = table.setdefault(slug, {"views": 0, "visits": 0})
        x["views"] += int(r.get("views", 0)); x["visits"] += int(r.get("visits", 0))
    now, prev = {}, {}
    for r in by_path:
        add(now, r, "now")
    for r in prev_path:
        add(prev, r, "prev")
    srcs, page_search = {}, {}
    for r in by_source:
        slug, st = path_slug(r["path"])
        if st or (slug and OWN.match(slug)):
            continue
        lab = source_of(r.get("host"))
        srcs[lab] = srcs.get(lab, 0) + int(r.get("visits", 0))
        if is_search(lab):
            page_search[slug] = page_search.get(slug, 0) + int(r.get("visits", 0))
    today = w["to"] + dt.timedelta(days=1)
    for slug in set(pages) | set(now):
        meta = pages.get(slug, {"slug": slug, "name": slug, "kind": "Not in the sitemap", "published": ""})
        x, p = now.get(slug, {}), prev.get(slug, {})
        st = stage.get(slug, {})
        rows[slug] = {"slug": slug, "name": meta["name"], "kind": meta["kind"], "published": meta.get("published", ""),
                      "visits": x.get("visits", 0), "views": x.get("views", 0), "prev": p.get("visits", 0),
                      "search": page_search.get(slug, 0), "uses": st.get("use", 0), "upgrades": st.get("upgrade", 0),
                      "staged": bool(meta.get("staged"))}
    if search:
        for slug, s in (search.get("pages") or {}).items():
            if slug in rows:
                rows[slug].update({"gImpr": s.get("impressions", 0), "gClicks": s.get("clicks", 0), "gPos": s.get("position")})
    tv, pv = sum(r["visits"] for r in rows.values()), sum(r["visits"] for r in prev_rows(prev))
    ordered = sorted(rows.values(), key=lambda r: (-r["visits"], -r["views"], r["name"]))
    def old_enough(r):
        if not r["published"]:
            return True      # live before Oct 22, 2026, when publish dates began
        return (today - dt.date.fromisoformat(r["published"])).days >= 7 * ZERO_WEEKS
    zero = [r["slug"] for r in ordered if r["kind"] != "Not in the sitemap" and r["visits"] == 0 and r["prev"] == 0 and old_enough(r)]
    fresh = [r["slug"] for r in ordered if r["published"] and (today - dt.date.fromisoformat(r["published"])).days < 7 * ZERO_WEEKS]
    weeks = {}
    for r in by_week:
        d = dt.date.fromisoformat(r["date"][:10])
        wk = (d - dt.timedelta(days=d.weekday())).isoformat()
        weeks[wk] = weeks.get(wk, 0) + int(r.get("visits", 0))
    # One number per week: the report's own week and the week before come from the page counts, so the trend can never
    # show a second figure for them (Oct 19 to 25 read 204 in totals and 300 in the trend). Older weeks keep the daily counts.
    weeks[w["from"].isoformat()] = tv
    weeks[(w["from"] - dt.timedelta(days=7)).isoformat()] = pv
    trend = [{"week": k, "visits": v} for k, v in sorted(weeks.items()) if k < (w["to"] + dt.timedelta(days=1)).isoformat()][-12:]
    calc = [r for r in ordered if r["kind"] == "Calculator"]
    return {
        "about": "Counts only, from Cloudflare Web Analytics (cookie-free, sampled at low traffic, so small numbers are estimates) and the anonymous calculator stage counts. Built by tools/traffic_report.py.",
        "ownVisits": (f"Our own visits are left out from {OWN_FROM} (automated checks and our marked browsers never count; our preview pages are "
                      "set aside under ownLeftOut)." if w["to"].isoformat() >= OWN_FROM else
                      f"This week is before {OWN_FROM}, when our own visits began to be left out, so it still includes our checks."),
        "ok": True, "fetchedAt": fetched,
        "week": {"from": w["from"].isoformat(), "to": w["to"].isoformat()},
        "totals": {"visits": tv, "views": sum(r["views"] for r in rows.values()), "prevVisits": pv,
                   "change": round((tv / pv - 1) * 100) if pv else None,
                   "search": sum(v for k, v in srcs.items() if is_search(k)),
                   "uses": sum(r["uses"] for r in calc), "upgrades": sum(r["upgrades"] for r in rows.values()),
                   "pagesWithVisits": sum(1 for r in rows.values() if r["visits"]), "livePages": len(pages)},
        "ownLeftOut": own,
        "sources": [{"label": k, "visits": v} for k, v in sorted(srcs.items(), key=lambda kv: -kv[1]) if v],
        "trend": trend,
        "pages": ordered,
        "flags": {"zero": zero, "new": fresh, "zeroWeeks": ZERO_WEEKS},
        "search": ({"date": search.get("date"), "clicks": sum(s.get("clicks", 0) for s in (search.get("pages") or {}).values()),
                    "impressions": sum(s.get("impressions", 0) for s in (search.get("pages") or {}).values())} if search else None),
    }


def prev_rows(prev):
    return list(prev.values())


# ---------- Cloudflare ----------
def call(path, token, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    if body is not None:
        if d.get("errors"):
            raise SystemExit("Cloudflare GraphQL: " + "; ".join(e.get("message", "") for e in d["errors"])[:400])
        return d["data"]
    if not d.get("success"):
        raise SystemExit("Cloudflare API: " + json.dumps(d.get("errors"))[:400])
    return d["result"]


Q = """query($a: String!, $s: String!, $f: Time!, $t: Time!, $pf: Time!, $pt: Time!, $tf: Time!) { viewer { accounts(filter: {accountTag: $a}) {
 now: rumPageloadEventsAdaptiveGroups(limit: 2000, filter: {siteTag: $s, datetime_geq: $f, datetime_lt: $t}, orderBy: [count_DESC]) { count sum { visits } dimensions { requestPath } }
 prev: rumPageloadEventsAdaptiveGroups(limit: 2000, filter: {siteTag: $s, datetime_geq: $pf, datetime_lt: $pt}, orderBy: [count_DESC]) { count sum { visits } dimensions { requestPath } }
 src: rumPageloadEventsAdaptiveGroups(limit: 5000, filter: {siteTag: $s, datetime_geq: $f, datetime_lt: $t}, orderBy: [count_DESC]) { count sum { visits } dimensions { requestPath refererHost } }
 days: rumPageloadEventsAdaptiveGroups(limit: 200, filter: {siteTag: $s, datetime_geq: $tf, datetime_lt: $t}, orderBy: [date_ASC]) { count sum { visits } dimensions { date } }
} } }"""


def pull():
    token = os.environ.get("CF_ANALYTICS_TOKEN", "").strip()
    now = dt.datetime.now(CHI)
    w = week_window(now.date())
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "weekly.json")
    if not token:
        json.dump({"ok": False, "reason": "Waiting for the Cloudflare key (the CF_ANALYTICS_TOKEN repo secret).",
                   "fetchedAt": now.isoformat(timespec="seconds"), "week": {"from": w["from"].isoformat(), "to": w["to"].isoformat()}},
                  open(out, "w", encoding="utf-8"), indent=1)
        print("traffic: no CF_ANALYTICS_TOKEN secret yet; wrote the waiting note")
        return
    beacon = json.load(open(os.path.join(ROOT, "site", "analytics.json"), encoding="utf-8"))["cloudflare"]
    accounts = call("/accounts?per_page=50", token)
    site, acct = None, None
    for a in accounts:
        for s in call(f"/accounts/{a['id']}/rum/site_info/list?per_page=100", token):
            if s.get("site_token") == beacon or s.get("site_tag") == beacon:
                site, acct = s["site_tag"], a["id"]
    if not site:
        raise SystemExit("traffic: no Web Analytics site with our beacon token in the accounts this key can read")
    t = lambda x: x.strftime("%Y-%m-%dT%H:%M:%SZ")
    d = call("/graphql", token, {"query": Q, "variables": {"a": acct, "s": site, "f": t(w["fromUtc"]), "t": t(w["toUtc"]),
                                                           "pf": t(w["prevFromUtc"]), "pt": t(w["prevToUtc"]), "tf": t(w["trendFromUtc"])}})
    acc = d["viewer"]["accounts"][0]
    flat = lambda rows, extra=(): [dict({"views": r["count"], "visits": r["sum"]["visits"], "path": r["dimensions"].get("requestPath", "")},
                                        **{k: r["dimensions"].get(v) for k, v in extra}) for r in rows]
    by_week = [{"date": r["dimensions"]["date"], "visits": r["sum"]["visits"]} for r in acc["days"]]
    sc = os.path.join(ROOT, "seo", "search-console.json")
    search = None
    if os.path.isfile(sc):
        s = json.load(open(sc, encoding="utf-8"))
        if s.get("date") and (now.date() - dt.date.fromisoformat(s["date"])).days <= 10:
            search = s
    rep = build(flat(acc["now"]), flat(acc["prev"]), flat(acc["src"], (("host", "refererHost"),)), by_week, w, load_pages(),
                now.isoformat(timespec="seconds"), search)
    json.dump(rep, open(out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    hist_f = os.path.join(OUT_DIR, "history.json")
    hist = json.load(open(hist_f, encoding="utf-8")) if os.path.isfile(hist_f) else []
    hist = [h for h in hist if h["week"] != rep["week"]["from"]] + [{"week": rep["week"]["from"], **{k: rep["totals"][k] for k in ("visits", "views", "search", "uses", "upgrades")}}]
    json.dump(sorted(hist, key=lambda h: h["week"])[-104:], open(hist_f, "w", encoding="utf-8"), indent=1)
    T = rep["totals"]
    print(f"traffic {rep['week']['from']} to {rep['week']['to']}: {T['visits']} visits ({T['change']}% on the week before), "
          f"{T['search']} from search, {T['uses']} calculator uses, {T['upgrades']} buy clicks, {len(rep['flags']['zero'])} pages with no visits")


def selftest():
    w = week_window(dt.date(2026, 11, 2))   # a Monday
    assert (w["from"].isoformat(), w["to"].isoformat()) == ("2026-10-26", "2026-11-01"), w
    assert w["fromUtc"].isoformat() == "2026-10-26T05:00:00+00:00" and w["toUtc"].isoformat() == "2026-11-02T06:00:00+00:00", w   # DST ends Nov 1
    assert week_window(dt.date(2026, 11, 4))["from"].isoformat() == "2026-10-26", "a mid-week run reports the last whole week"
    assert path_slug("/") == ("home", None) and path_slug("/snow-removal-pricing-calculator/") == ("snow-removal-pricing-calculator", None)
    assert path_slug("/e/snow-removal-pricing-calculator/use/") == (None, ("snow-removal-pricing-calculator", "use"))
    assert path_slug("/new-in-chicago/index.html?x=1") == ("new-in-chicago", None)
    assert source_of("www.google.com") == "Google" and source_of("google.co.uk") == "Google" and source_of("proofnotfluff.com") == "Direct"
    assert source_of("") == "Direct" and source_of("chatgpt.com") == "AI assistants" and source_of("l.facebook.com") == "Social"
    assert source_of("notgoogle.example.com") == "Other sites" and source_of("www.bing.com") == "Bing"
    pages = {"home": {"slug": "home", "name": "Home", "kind": "Other page", "published": ""},
             "snow-removal-pricing-calculator": {"slug": "snow-removal-pricing-calculator", "name": "Snow Removal Pricing Calculator", "kind": "Calculator", "published": "2026-10-26"},
             "markup-calculator": {"slug": "markup-calculator", "name": "Markup Calculator", "kind": "Calculator", "published": ""},
             "chicago-rat-complaints": {"slug": "chicago-rat-complaints", "name": "Chicago Rat Complaints", "kind": "Weekly City page", "published": "2026-10-01"}}
    now = [{"path": "/", "views": 120, "visits": 100}, {"path": "/snow-removal-pricing-calculator/", "views": 30, "visits": 25},
           {"path": "/e/snow-removal-pricing-calculator/use/", "views": 9, "visits": 0}, {"path": "/e/snow-removal-pricing-calculator/upgrade/", "views": 2, "visits": 0},
           {"path": "/old-page/", "views": 3, "visits": 3}, {"path": "/preview/new-page/", "views": 7, "visits": 2}]
    prev = [{"path": "/", "views": 90, "visits": 80}, {"path": "/e/snow-removal-pricing-calculator/use/", "views": 4, "visits": 0}]
    src = [{"path": "/", "host": "", "visits": 70}, {"path": "/", "host": "www.google.com", "visits": 30},
           {"path": "/snow-removal-pricing-calculator/", "host": "www.bing.com", "visits": 5}, {"path": "/snow-removal-pricing-calculator/", "host": "proofnotfluff.com", "visits": 20},
           {"path": "/e/snow-removal-pricing-calculator/use/", "host": "proofnotfluff.com", "visits": 0}, {"path": "/old-page/", "host": "chatgpt.com", "visits": 3},
           {"path": "/preview/new-page/", "host": "", "visits": 2}]
    days = [{"date": "2026-10-19", "visits": 40}, {"date": "2026-10-25", "visits": 40}, {"date": "2026-10-26", "visits": 60}, {"date": "2026-11-01", "visits": 68},
            {"date": "2026-11-02", "visits": 999}]
    r = build(now, prev, src, days, w, pages, "2026-11-02T07:00:00-06:00",
              {"date": "2026-10-30", "pages": {"snow-removal-pricing-calculator": {"impressions": 40, "clicks": 3, "position": 18.2}}})
    T = r["totals"]
    assert (T["visits"], T["views"], T["prevVisits"], T["change"]) == (128, 153, 80, 60), T      # stage pages are not visits
    assert (T["search"], T["uses"], T["upgrades"], T["pagesWithVisits"]) == (35, 9, 2, 3), T
    snow = next(p for p in r["pages"] if p["slug"] == "snow-removal-pricing-calculator")
    assert (snow["visits"], snow["search"], snow["uses"], snow["upgrades"], snow["gClicks"]) == (25, 5, 9, 2, 3), snow
    assert r["pages"][0]["slug"] == "home" and any(p["kind"] == "Not in the sitemap" for p in r["pages"]), "order, and pages outside the sitemap kept"
    assert r["flags"]["zero"] == ["chicago-rat-complaints", "markup-calculator"], r["flags"]      # snow is new, so not flagged
    assert r["flags"]["new"] == ["snow-removal-pricing-calculator"]
    assert [s["label"] for s in r["sources"]] == ["Direct", "Google", "Bing", "AI assistants"], r["sources"]
    assert r["trend"] == [{"week": "2026-10-19", "visits": 80}, {"week": "2026-10-26", "visits": 128}], r["trend"]   # the running week is left out
    assert r["ownLeftOut"] == {"visits": 2, "views": 7} and not any(p["slug"].startswith("preview") for p in r["pages"]), "our preview pages left out"
    off = build(now, prev, src, [{"date": "2026-10-27", "visits": 300}, {"date": "2026-10-20", "visits": 999}, {"date": "2026-10-12", "visits": 5}],
                w, pages, "x")
    assert off["trend"] == [{"week": "2026-10-12", "visits": 5}, {"week": "2026-10-19", "visits": 80}, {"week": "2026-10-26", "visits": 128}], \
        "the trend shows the same number as the totals for the report week and the week before"
    assert "left out from" in r["ownVisits"] and "before" in build([], [], [], [], week_window(dt.date(2026, 10, 26)), pages, "x")["ownVisits"]
    assert r["search"] == {"date": "2026-10-30", "clicks": 3, "impressions": 40}
    blob = json.dumps(r)
    assert not re.search(r"\b\d{1,3}(\.\d{1,3}){3}\b", blob) and "userAgent" not in blob, "counts only"
    empty = build([], [], [], [], w, pages, "x")
    assert empty["totals"]["change"] is None and empty["totals"]["visits"] == 0, "no traffic: no divide by zero"
    print("traffic_report selftest: ok (windows across the DST change, paths, sources, stage counts, flags, trend, one number per week, "
          "our preview pages left out, Search Console, counts only)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        try:
            pull()
        except (SystemExit, Exception) as e:   # keep the reason where the scoreboard and the next chat can read it
            if isinstance(e, SystemExit) and e.code in (0, None):
                raise
            msg = str(e)[:400]
            os.makedirs(OUT_DIR, exist_ok=True)
            w = week_window(dt.datetime.now(CHI).date())
            json.dump({"ok": False, "reason": "The weekly pull failed: " + msg, "fetchedAt": dt.datetime.now(CHI).isoformat(timespec="seconds"),
                       "week": {"from": w["from"].isoformat(), "to": w["to"].isoformat()}}, open(os.path.join(OUT_DIR, "weekly.json"), "w", encoding="utf-8"), indent=1)
            print("traffic: pull failed:", msg)
            sys.exit(1)
