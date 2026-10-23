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
                + f'<div class="qa-tw"><table class="qa-t"><thead><tr>{head}</tr></thead><tbody>{body_rows}</tbody></table></div>'
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
            f'<div class="ld-heroact qa-act">{buy()}<a class="ld-textlink" href="{sample}">'
            + ('Try the free calculator' if kit else 'See this week\'s sample') + '</a></div>'
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
    ld = (M.ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": fill(q, s), "acceptedAnswer": {"@type": "Answer", "text": fill(a, s)}}
                         for q, a in p["faq"]]}, crumb_ld, article)
          + "<style>.ld-page .asof,.ld-page footer p{color:var(--muted)}"
          ".qa{max-width:none}.qa>h1{max-width:820px;text-wrap:pretty;font-size:clamp(28px,4vw,40px)}.qa p{max-width:72ch}.qa-answer p{max-width:62ch}.qa-steps li{max-width:72ch}.qa-upd{margin:10px 0 0}.ld-page h2,.ld-page h3,.ld-page summary{text-wrap:balance}"
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
          ".qa-t th,.qa-t td{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line);vertical-align:top}.qa-t thead th{font:600 13px/1.3 Poppins,system-ui,sans-serif;letter-spacing:.03em;color:var(--muted);background:var(--canvas2)}"
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
