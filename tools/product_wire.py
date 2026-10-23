#!/usr/bin/env python3
"""Launch wiring check (radar, Todd, Oct 23, 2026): no lead product goes live half-wired.

Todd's words: "Anytime we create a new product, I want to make sure that it's integrated with the overall system,
meaning that the new product comes automatically on the website. There's a 7-day free trial. There's a pricing
established. There is also going to be maintenance of that product on an ongoing basis. And also that there is
relevant blog posts to optimize SEO."

launches/WIRING.json holds one entry per product. This tool checks every piece against the real files:
  page        site/pages.json spec of a lead kind, not a draft, and docs/<slug>/index.html built without noindex
  store       a site/store.json product card, and the home page and /shop/ both link to the product page
  trial       trialDays is 7 on the spec, and the built page says "7-day free trial"
  price       spec price equals the entry's, inside $29 to $199 (coo/CONSTITUTION.md 1), with priceReason written down
  checkout    a Gumroad checkout with utm tags, on the built page
  forms       the Kit form and the free Monday form are on the page and named in store.json kitForms, or {"na": why}
  outreach    the templates file exists and its copy gate is a known one, or {"na": why}
  refresh     the data workflow exists, runs on a schedule and writes the product's data file
  data        the data file and profile exist and are fresh (fetchedAt within freshDays)
  members     the members' page is built
  health      the source dataset and expected columns are set, and every expected column is in the profile
  questions   seo/BACKLOG.md has questionsMin rows mapped to the product (question pages for the daily run)
  ai          the page carries Product structured data and WebPage data whose dateModified is the day its data was
              pulled (research_notes/ai-recommendation-2026-10-23.md: true freshness and consistent business details help
              AI search; llms.txt and extra schema showed no effect, so neither is required)
  launch      launches/<slug>.md exists
  scoreboard  the scoreboard leadproducts doc id is set
Also: every non-draft lead page with a checkout must have a live entry here, so a product cannot go live unregistered.
Legacy products (live before Oct 23) print gaps as WARN; any other live product prints them as ERROR and fails.

Usage: python3 tools/product_wire.py                 check every product, exit 1 on any ERROR
       python3 tools/product_wire.py --slug <slug>   one product, every gap as ERROR (the launch step's gate)
       python3 tools/product_wire.py --todd <slug>   Todd's account steps for that product, as one short checklist
       python3 tools/product_wire.py --new <slug>    add a "building" entry from scout/candidates/<slug>.json
       python3 tools/product_wire.py --selftest      planted gaps, each must be caught
"""
import argparse, copy, datetime as dt, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEAD_KINDS = ("leads", "restleads", "licleads")
BAND = (29, 199)
GATES = ("templates", "signal-templates", "file")
ITEMS = ("page", "store", "trial", "price", "checkout", "forms", "outreach", "refresh", "data", "members", "health",
         "questions", "ai", "launch", "scoreboard")


def rd(root, rel):
    p = os.path.join(root, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def jl(root, rel):
    t = rd(root, rel)
    return json.loads(t) if t else None


def today():
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date()
    except Exception:
        return dt.date.today()


def na(v):
    return isinstance(v, dict) and str(v.get("na", "")).strip()


def check_product(root, slug, e, pages, store, backlog, llms, on=None):
    """Returns {item: [problems]} for one product."""
    on = on or today()
    P = {k: [] for k in ITEMS}
    spec = next((p for p in pages if p.get("slug") == slug), None)
    html = rd(root, f"docs/{slug}/index.html") or ""
    if not spec or spec.get("kind") not in LEAD_KINDS:
        P["page"].append("no lead-kind spec in site/pages.json")
    elif spec.get("draft"):
        P["page"].append("the spec is still a draft")
    if not html:
        P["page"].append(f"docs/{slug}/index.html is not built")
    elif 'name="robots" content="noindex' in html:
        P["page"].append("the built page carries noindex")
    spec = spec or {}
    if not any(x.get("key") == slug for x in store.get("products", [])):
        P["store"].append("no site/store.json product card")
    for rel, where in (("docs/index.html", "home page"), ("docs/shop/index.html", "shop")):
        if not re.search(rf'href="(\.\./)?{re.escape(slug)}/[#"]', rd(root, rel) or ""):
            P["store"].append(f"the {where} does not link to /{slug}/")
    if spec.get("trialDays") != 7 or e.get("trialDays", 7) != 7:
        P["trial"].append(f"trialDays is {spec.get('trialDays')!r}, must be 7")
    if html and "7-day free trial" not in html:
        P["trial"].append("the built page does not say 7-day free trial")
    try:
        sp = float(spec.get("price"))
    except (TypeError, ValueError):
        sp = None
    if sp is None or sp != float(e.get("price") or -1):
        P["price"].append(f"spec price {spec.get('price')!r} differs from the wiring price {e.get('price')!r}")
    if not (BAND[0] <= float(e.get("price") or 0) <= BAND[1]):
        P["price"].append(f"price {e.get('price')!r} outside the ${BAND[0]} to ${BAND[1]} band")
    if len(str(e.get("priceReason", ""))) < 30:
        P["price"].append("priceReason missing or under 30 characters")
    co = str(spec.get("checkout", ""))
    if not re.match(r"https://[\w.-]*gumroad\.com/l/", co) or "utm_source=" not in co:
        P["checkout"].append("no Gumroad checkout with utm tags on the spec")
    elif co.split("?")[0] not in html:
        P["checkout"].append("the checkout link is not on the built page")
    forms = store.get("kitForms", {})
    for key in ("kitForm", "mondayForm"):
        v = e.get(key)
        if na(v):
            continue
        if not v:
            P["forms"].append(f"{key} not set (a form id, or {{\"na\": why}})")
        elif str(v) not in forms:
            P["forms"].append(f"{key} {v} is not named in store.json kitForms")
    if not any(str(e.get(k)) in html for k in ("kitForm", "mondayForm") if not na(e.get(k)) and e.get(k)) and not all(na(e.get(k)) for k in ("kitForm", "mondayForm")):
        P["forms"].append("neither Kit form is on the built page")
    o = e.get("outreach") or {}
    if not na(o):
        if not o.get("templates") or rd(root, o["templates"]) is None:
            P["outreach"].append("the outreach templates file is missing")
        if o.get("gate") not in GATES:
            P["outreach"].append(f"outreach gate {o.get('gate')!r} is not one of {', '.join(GATES)}")
    wf = rd(root, e.get("workflow") or "-") or ""
    if not wf:
        P["refresh"].append("the data refresh workflow is missing")
    else:
        if "cron:" not in wf:
            P["refresh"].append("the workflow has no schedule")
        data_dir = os.path.dirname(e.get("data") or "x/x")
        if data_dir not in wf and os.path.basename(e.get("data") or "") not in wf:
            P["refresh"].append(f"the workflow does not write {data_dir}/")
    d = jl(root, e.get("data") or "-")
    prof = jl(root, e.get("profile") or "-")
    if d is None:
        P["data"].append("the data file is missing")
    else:
        f = str(((d.get("source") or {}).get("fetchedAt")) or d.get("asOf") or "")[:10]
        try:
            age = (on - dt.date.fromisoformat(f)).days
            if age > int(e.get("freshDays") or 9):
                P["data"].append(f"data is {age} days old (fetched {f}), over {e.get('freshDays')}")
        except ValueError:
            P["data"].append("the data file has no fetchedAt date")
    if prof is None:
        P["data"].append("the profile file is missing")
    if not rd(root, f"docs/{e.get('members') or '-'}/index.html"):
        P["members"].append("the members' page is not built")
    s = e.get("source") or {}
    if not s.get("portal") or not s.get("dataset") or not s.get("expectColumns"):
        P["health"].append("source portal, dataset and expectColumns must be set")
    elif prof:
        miss = [c for c in s["expectColumns"] if c not in (prof.get("columns") or [])]
        if miss:
            P["health"].append("expected columns missing from the profile: " + ", ".join(miss[:5]))
    if not isinstance(e.get("holdout"), dict) or "dateField" not in e["holdout"]:
        P["health"].append("holdout settings missing")
    n = len(re.findall(rf"^\|[^|]*\|[^|]*\|\s*{re.escape(slug)}\s*\|", backlog or "", re.M))
    if n < int(e.get("questionsMin") or 3):
        P["questions"].append(f"{n} seo/BACKLOG.md rows map to it, under {e.get('questionsMin') or 3}")
    if html and '"@type": "Product"' not in html:
        P["ai"].append("no Product structured data on the page")
    fetched = str((((d or {}).get("source") or {}).get("fetchedAt")) or (d or {}).get("asOf") or "")[:10]
    if html and not re.search(r'"@type": "WebPage"[^<]*"dateModified": "' + re.escape(fetched) + '"', html):
        P["ai"].append(f"no WebPage data with dateModified {fetched or '(no data date)'} on the page")
    if not rd(root, e.get("launch") or f"launches/{slug}.md"):
        P["launch"].append("no launch record")
    if not (e.get("scoreboard") or {}).get("leadproducts"):
        P["scoreboard"].append("no scoreboard leadproducts doc id")
    return P


def run(root=ROOT, only=None, strict=False, on=None):
    wiring = jl(root, "launches/WIRING.json") or {}
    pages = (jl(root, "site/pages.json") or {}).get("pages", [])
    store = jl(root, "site/store.json") or {}
    backlog, llms = rd(root, "seo/BACKLOG.md"), rd(root, "docs/llms.txt")
    prods = wiring.get("products", {})
    lines, errors = [], 0
    if not only:
        for p in pages:
            if p.get("kind") in LEAD_KINDS and not p.get("draft") and p.get("checkout"):
                if prods.get(p["slug"], {}).get("status") != "live":
                    lines.append(f"ERROR wire {p['slug']}: a live lead page with a checkout has no live entry in launches/WIRING.json")
                    errors += 1
    for slug, e in prods.items():
        if only and slug != only:
            continue
        if e.get("status") != "live" and not only:
            continue
        probs = check_product(root, slug, e, pages, store, backlog, llms, on)
        level = "WARN" if e.get("legacy") and not strict else "ERROR"
        gaps = [(k, x) for k in ITEMS for x in probs[k]]
        for k, x in gaps:
            lines.append(f"{level} wire {slug} {k}: {x}")
        errors += len(gaps) if level == "ERROR" else 0
        lines.append(f"{'OK' if not gaps else level} wire {slug}: {len(ITEMS) - len({k for k, _ in gaps})} of {len(ITEMS)} pieces wired")
    return lines, errors


def todd_steps(slug, root=ROOT):
    e = (jl(root, "launches/WIRING.json") or {}).get("products", {}).get(slug)
    if not e:
        return [f"{slug} has no entry in launches/WIRING.json"]
    name = next((x.get("name") for x in (jl(root, "site/store.json") or {}).get("products", []) if x.get("key") == slug), slug)
    steps = [f"1. Gumroad, your account: new Membership product \"{name}\", tier Monthly at ${e.get('price')}, free trial 7 days, "
             f"card at signup. Paste name, summary and description from launches/{slug}.md. Upload the cover and thumbnail from "
             f"launches/{slug}/. Post-purchase content: the members' link https://proofnotfluff.com/{e.get('members')}/ and the password "
             f"(I give you its name, never the value). Turn on Discover. Publish, then paste the checkout link here. About 12 minutes.",
             "2. Tell me in chat: go on the page, price and checkout. I wire the link, rebuild and check every piece."]
    k = 3
    for key, what in (("kitForm", "waitlist"), ("mondayForm", "free Monday email")):
        if not na(e.get(key)) and not e.get(key):
            steps.append(f"{k}. Kit, your account: new form for the {what} of \"{name}\" (double opt-in, confirm to the product page); paste its number here. About 4 minutes.")
            k += 1
    if not na(e.get("outreach")):
        steps.append(f"{k}. Say go on outreach for \"{name}\" when you have seen the finished page and the first drafts.")
    return steps


def new_entry(slug, root=ROOT):
    c = jl(root, f"scout/candidates/{slug}.json")
    if not c:
        sys.exit(f"no scout/candidates/{slug}.json")
    w = jl(root, "launches/WIRING.json")
    if slug in w["products"]:
        sys.exit(f"{slug} already has an entry")
    da = c.get("data") or {}
    w["products"][slug] = {"status": "building", "legacy": False, "price": (c.get("price") or {}).get("monthly"),
                           "priceReason": (c.get("price") or {}).get("reason", ""), "kitForm": None, "mondayForm": None,
                           "outreach": None, "workflow": None, "data": None, "profile": None, "members": None, "freshDays": 9,
                           "source": {"portal": "", "dataset": "", "expectColumns": [], "url": da.get("url")}, "holdout": None,
                           "questionsMin": 3, "launch": f"launches/{slug}.md", "scoreboard": {"leadproducts": ""}}
    json.dump(w, open(os.path.join(root, "launches", "WIRING.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"added {slug} as building; product-builder fills each piece, then python3 tools/product_wire.py --slug {slug} must pass")


def selftest():
    tmp = tempfile.mkdtemp()
    try:
        for rel in ("launches/WIRING.json", "site/pages.json", "site/store.json", "seo/BACKLOG.md", ".github/workflows", "docs/index.html", "docs/shop"):
            src = os.path.join(ROOT, rel)
            dst = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            (shutil.copytree if os.path.isdir(src) else shutil.copy)(src, dst)
        slug = "chicago-construction-cleaning-leads"
        e0 = jl(ROOT, "launches/WIRING.json")["products"][slug]
        for rel in (f"docs/{slug}/index.html", f"docs/{e0['members']}/index.html", e0["data"], e0["profile"], e0["launch"],
                    e0["outreach"]["templates"]):
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            shutil.copy(os.path.join(ROOT, rel), os.path.join(tmp, rel))
        on = dt.date.fromisoformat(str(jl(ROOT, e0["data"])["source"]["fetchedAt"])[:10])
        hp = os.path.join(tmp, "docs", slug, "index.html")
        base_html = open(hp).read()
        w = jl(tmp, "launches/WIRING.json")
        w["products"] = {slug: dict(e0, legacy=False)}
        json.dump(w, open(os.path.join(tmp, "launches/WIRING.json"), "w"))
        lines, errs = run(tmp, only=slug, strict=True, on=on)
        cases = [("baseline fully wired", errs == 0, lines)]
        def plant(label, item, fn, restore):
            fn()
            lines, errs = run(tmp, only=slug, strict=True, on=on)
            cases.append((label, any(f" {item}:" in l for l in lines if l.startswith("ERROR")), [l for l in lines if l.startswith("ERROR")][:2]))
            restore()
        def edit_wiring(k, v):
            def go():
                ww = jl(tmp, "launches/WIRING.json"); ww["products"][slug][k] = v
                json.dump(ww, open(os.path.join(tmp, "launches/WIRING.json"), "w"))
            return go
        def reset_wiring():
            ww = jl(tmp, "launches/WIRING.json"); ww["products"] = {slug: dict(e0, legacy=False)}
            json.dump(ww, open(os.path.join(tmp, "launches/WIRING.json"), "w"))
        def edit_spec(k, v):
            def go():
                pp = jl(tmp, "site/pages.json")
                for p in pp["pages"]:
                    if p["slug"] == slug:
                        p[k] = v
                json.dump(pp, open(os.path.join(tmp, "site/pages.json"), "w"))
            return go
        pages_orig = rd(tmp, "site/pages.json")
        reset_pages = lambda: open(os.path.join(tmp, "site/pages.json"), "w").write(pages_orig)
        reset_html = lambda: open(hp, "w").write(base_html)
        plant("trial off", "trial", edit_spec("trialDays", None), reset_pages)
        plant("trial text gone", "trial", lambda: open(hp, "w").write(base_html.replace("7-day free trial", "trial")), reset_html)
        plant("price outside band", "price", edit_wiring("price", 19), reset_wiring)
        plant("price reason missing", "price", edit_wiring("priceReason", ""), reset_wiring)
        plant("spec price differs", "price", edit_spec("price", "49"), reset_pages)
        plant("checkout without utm", "checkout", edit_spec("checkout", "https://proofnotfluff.gumroad.com/l/vpnaoq"), reset_pages)
        plant("draft page", "page", edit_spec("draft", True), reset_pages)
        plant("noindex page", "page", lambda: open(hp, "w").write(base_html.replace("<head>", '<head><meta name="robots" content="noindex">', 1)), reset_html)
        plant("form not set", "forms", edit_wiring("mondayForm", None), reset_wiring)
        plant("form not on page", "forms", lambda: open(hp, "w").write(base_html.replace(e0["mondayForm"], "0000000").replace(e0["kitForm"], "0000001")), reset_html)
        plant("no workflow", "refresh", edit_wiring("workflow", ".github/workflows/none.yml"), reset_wiring)
        plant("stale data", "data", edit_wiring("freshDays", -1), reset_wiring)
        plant("no members page", "members", edit_wiring("members", "nowhere"), reset_wiring)
        plant("expected column gone", "health", edit_wiring("source", dict(e0["source"], expectColumns=["no_such_column"])), reset_wiring)
        plant("too few questions", "questions", edit_wiring("questionsMin", 99), reset_wiring)
        plant("no Product data", "ai", lambda: open(hp, "w").write(base_html.replace('"@type": "Product"', '"@type": "Thing"')), reset_html)
        plant("stale dateModified", "ai", lambda: open(hp, "w").write(re.sub(r'"dateModified": "[^"]*"', '"dateModified": "2001-01-01"', base_html)), reset_html)
        plant("no launch record", "launch", edit_wiring("launch", "launches/none.md"), reset_wiring)
        plant("no scoreboard doc", "scoreboard", edit_wiring("scoreboard", {}), reset_wiring)
        plant("bad outreach gate", "outreach", edit_wiring("outreach", {"templates": e0["outreach"]["templates"], "gate": "none"}), reset_wiring)
        store_orig = rd(tmp, "site/store.json")
        def drop_card():
            s = json.loads(store_orig); s["products"] = [x for x in s["products"] if x["key"] != slug]
            json.dump(s, open(os.path.join(tmp, "site/store.json"), "w"))
        plant("no store card", "store", drop_card, lambda: open(os.path.join(tmp, "site/store.json"), "w").write(store_orig))
        # an unregistered live page
        ww = jl(tmp, "launches/WIRING.json"); ww["products"] = {}
        json.dump(ww, open(os.path.join(tmp, "launches/WIRING.json"), "w"))
        lines, errs = run(tmp, on=on)
        cases.append(("live page with no entry", any("has no live entry" in l for l in lines), lines[:1]))
        bad = 0
        for label, okay, detail in cases:
            if not okay:
                bad += 1
                print(f"FAIL {label}: {detail}")
        print(f"{'OK' if not bad else 'ERROR'} product_wire selftest: {len(cases) - bad} of {len(cases)} planted cases right")
        return bad == 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--slug")
    ap.add_argument("--todd")
    ap.add_argument("--new")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.todd:
        print("\n".join(todd_steps(a.todd)))
        return
    if a.new:
        new_entry(a.new)
        return
    lines, errors = run(only=a.slug, strict=bool(a.slug))
    print("\n".join(lines))
    print(f"product_wire: {errors} error{'s' if errors != 1 else ''}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
