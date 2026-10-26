#!/usr/bin/env python3
"""Chicago Rat Complaints by Neighborhood: the free weekly page (site/pages.json kind "rodents", written by
tools/make_site.py, which calls page_html here). Todd's go, Oct 26, 2026 ("Make all of them",
coo/DECISIONS-2026-10-26.md).

Data: permits/rodents-chicago/weekly.json (tools/rodents_chicago.py, weekly GitHub Action): City of Chicago 311
requests of type "Rodent Baiting/Rat Complaint", counted by community area. Counts only; no address, location or
resident text exists in the file, so none can reach the page. Residents get the City's own way to report rats (311);
pest control companies get the restaurant list and the daily pest seat, which are built from food inspection records,
not from these complaints (the page says so).

Usage: python3 tools/rodents_site.py --selftest
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "permits", "rodents-chicago", "weekly.json")


def load(p):
    f = os.path.join(ROOT, p.get("data", "permits/rodents-chicago/weekly.json"))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


FEW = 10   # under 10 complaints a year earlier, a percent change is noise: the page says "too few" instead


def area_change(a):
    return "too few" if a["prev30"] < FEW else pct(a["change"])


def pct(x):
    if x is None:
        return "new"
    return ("+" if x > 0 else "") + f"{x:.0f}%" if abs(x) >= 1 else "about the same"


def change_words(x):
    if x is None:
        return "with none a year earlier"
    if abs(x) < 1:
        return "about the same as a year earlier"
    return f'{abs(x):.0f}% {"more" if x > 0 else "fewer"} than the same 30 days a year earlier'


CSS = ("<style>.rc-bars{margin:12px 0 8px;padding:16px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".rc-bars figcaption{font-weight:700;color:var(--ink);margin-bottom:6px}"
       ".rc-bar{display:grid;grid-template-columns:minmax(118px,190px) 1fr 52px;gap:2px 10px;align-items:center;margin:9px 0;font-size:14.5px;color:var(--ink2)}"
       ".rc-bar>span{font-weight:600;color:var(--ink)}.rc-bar i{display:block;height:12px;border-radius:6px;background:var(--accent)}"
       ".rc-bar b{text-align:right;color:var(--ink);font-variant-numeric:tabular-nums}.rc-bar small{grid-column:2/-1;font-size:13px;color:var(--muted)}"
       ".rc-wk{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:6px;align-items:end;height:170px;margin:12px 0 4px;padding:16px 18px 10px;"
       "background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".rc-wk div{display:flex;flex-direction:column;justify-content:flex-end;align-items:center;height:100%;gap:4px}"
       ".rc-wk i{display:block;width:100%;max-width:38px;border-radius:5px 5px 0 0;background:var(--accent);opacity:.55}.rc-wk div:last-child i{opacity:1}"
       ".rc-wk b{font:600 12.5px system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".rc-wk span{font-size:11.5px;color:var(--muted);white-space:nowrap}"
       ".rc-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".rc-tw:focus-visible{outline:3px solid var(--accent);outline-offset:2px}"
       ".rc-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:520px}.rc-t th,.rc-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums}"
       ".rc-t th:first-child,.rc-t td:first-child{text-align:left}.rc-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card);position:sticky;top:0}"
       ".rc-t tbody th{font-weight:600;color:var(--ink)}.rc-t tr:last-child td,.rc-t tr:last-child th{border-bottom:0}"
       ".rc-up{color:var(--warn-ink)}.rc-two{display:grid;gap:16px}@media(min-width:900px){.rc-two{grid-template-columns:1fr 1fr}}"
       ".rc-two .cta{grid-template-columns:1fr;height:100%}.rc-two .cta h2{margin-top:0;text-wrap:balance}"
       ".rc-steps{margin:8px 0 0;padding-left:22px}section.block .cta .rc-steps li{margin:6px 0;color:var(--band-text)}.cta .rc-more,.cta .rc-more a{color:var(--band-text)}"
       ".rc-more-t{margin:12px 0 0}.rc-more-t summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".rc-more-t[open] summary{margin-bottom:8px}"
       "@media(max-width:599px){.rc-t{min-width:0}.rc-t th:nth-child(2),.rc-t td:nth-child(2){display:none}.rc-t th,.rc-t td{padding:9px 8px}.rc-wk div:not(:first-child):not(:last-child) span{visibility:hidden}.rc-wk span{font-size:10.5px}.rc-wk{height:140px}.rc-wk div:not(:last-child) b{visibility:hidden}.rc-bar{grid-template-columns:minmax(96px,130px) 1fr 44px}}</style>")


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    head = lambda rb: M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(crumb_ld, faq_ld) + CSS,
                                    bodycls=' class="ld-page"', robots=rb, analytics=M.analytics_tag())
    if not d:   # before the first weekly pull: a draft shell, never published (is_live needs the data too)
        body = f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first weekly count is on its way.</p></div>'
        return head('<meta name="robots" content="noindex, nofollow">') + body + "</main></body></html>"
    c, w, src = d["counts"], d["window"], d["source"]
    pulled = M.nice_date(src["fetchedAt"][:10])
    areas = [a for a in d["areas"] if a["d30"] or a["prev30"] or a["d7"]]
    top = sorted(areas, key=lambda a: (-a["d30"], a["name"]))
    lead = top[0] if top else None
    tie = bool(lead and len(top) > 1 and top[1]["d30"] == lead["d30"])
    lede = (f'{c["d30"]:,} rat complaints came in to Chicago 311 in the 30 days to {E(M.nice_date(w["to"]))}, '
            f'{change_words(c["change"])}. {c["d7"]:,} came in the last 7 days.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Last 7 days</div><div class="val">{c["d7"]:,}</div><div class="sub">rat complaints to 311</div></div>'
             f'<div class="tile"><div class="lab">Last 30 days</div><div class="val">{c["d30"]:,}</div><div class="sub">in {c["areasWith30"]:,} of 77 community areas</div></div>'
             f'<div class="tile"><div class="lab">Against a year ago</div><div class="val">{E(pct(c["change"]))}</div><div class="sub">{c["prev30"]:,} in the same 30 days of {E(w["prevTo"][:4])}</div></div>'
             + (f'<div class="tile"><div class="lab">Most complaints</div><div class="val rc-name">{E(lead["name"])}</div><div class="sub">{lead["d30"]:,} in 30 days</div></div>'
                if lead and not tie else "")
             + f'</div><p class="asof">From City of Chicago 311 records pulled {E(pulled)}. Updated every Monday.</p>')
    peak = max((a["d30"] for a in top[:10]), default=1) or 1
    bars = ('<figure class="rc-bars" aria-label="Community areas with the most rat complaints in the last 30 days">'
            '<figcaption>Most rat complaints, last 30 days</figcaption>'
            + "".join(f'<div class="rc-bar"><span>{E(a["name"])}</span><i style="width:{max(6, round(a["d30"] / peak * 100))}%"></i><b>{a["d30"]:,}</b>'
                      f'<small>{a["d7"]:,} in the last 7 days · {"too few a year ago to compare" if a["prev30"] < FEW else E(pct(a["change"])) + " on a year ago"}</small></div>' for a in top[:10])
            + '</figure>')
    wpeak = max((x["count"] for x in d["weeks"]), default=1) or 1
    weeks = ('<div class="rc-wk" role="img" aria-label="Rat complaints each week for the last 12 weeks, '
             + E(", ".join(f'{x["count"]:,}' for x in d["weeks"])) + '">'
             + "".join(f'<div><b>{x["count"]:,}</b><i style="height:{max(3, round(x["count"] / wpeak * 100))}%"></i>'
                       f'<span>{E(M.nice_date(x["from"]).rsplit(",", 1)[0])}</span></div>' for x in d["weeks"])
             + '</div><p class="asof">Each bar is 7 days, oldest on the left; the last bar is the week to '
             + E(M.nice_date(w["to"])) + '.</p>')
    row = lambda a: (f'<tr><th scope="row">{E(a["name"])}</th><td>{a["d7"]:,}</td><td>{a["d30"]:,}</td><td>{a["prev30"]:,}</td>'
                     f'<td{" class=rc-up" if a["prev30"] >= FEW and (a["change"] or 0) >= 25 else ""}>{E(area_change(a))}</td></tr>')
    thead = ('<thead><tr><th scope="col">Community area</th><th scope="col">7 days</th><th scope="col">30 days</th>'
             f'<th scope="col">Same 30 days, {E(w["prevTo"][:4])}</th><th scope="col">Change</th></tr></thead>')
    tbl = lambda rs, label: (f'<div class="rc-tw" role="region" aria-label="{E(label)}" tabindex="0"><table class="rc-t">{thead}'
                             f'<tbody>{"".join(row(a) for a in rs)}</tbody></table></div>')
    SHOW = 20
    table = (tbl(top[:SHOW], f"Rat complaints, the {min(SHOW, len(top))} community areas with the most")
             + (f'<details class="rc-more-t"><summary>Show the other {len(top) - SHOW} community areas</summary>'
                + tbl(top[SHOW:], "Rat complaints, the other community areas") + '</details>' if len(top) > SHOW else "")
             + f'<p class="asof">Change compares the last 30 days with the same 30 days a year earlier; under {FEW} complaints a year earlier it shows as too few to compare.'
             + (f' {c["noArea30"]:,} of the last 30 days\' complaints had no community area on the record and count only in the city total.' if c.get("noArea30") else "")
             + '</p>')
    resident = p["resident"]
    vendor = p["vendor"]
    two = ('<section class="block" id="help"><div class="rc-two">'
           f'<div class="cta ld-cta"><div><h2>{E(resident["title"])}</h2>'
           + '<ol class="rc-steps">' + "".join(f"<li>{E(t)}</li>" for t in resident["steps"]) + '</ol>'
           + (f'<p class="rc-more"><a href="{E(resident["more"][1])}" rel="noopener">{E(resident["more"][0])}</a>, City of Chicago</p>' if resident.get("more") else "")
           + f'<p class="ld-buybtn"><a class="btn" href="{E(resident["url"])}" rel="noopener">{E(resident["button"])}</a></p></div></div>'
           f'<div class="cta ld-cta"><div><h2>{E(vendor["title"])}</h2><p>{E(vendor["text"])}</p>'
           + f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(vendor["slug"])}/">{E(vendor["button"])}</a></p></div></div>'
           '</div></section>')
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>'
            f'<div class="ld-heroact rl-act"><a class="btn" href="#areas">See every neighborhood</a></div></div>'
            f'{tiles}'
            f'<section class="block" id="top"><h2>Where the complaints are</h2>{bars}</section>'
            f'<section class="block" id="weeks"><h2>Week by week</h2>{weeks}</section>'
            f'<section class="block" id="areas"><h2>Every community area</h2>{table}</section>'
            f'{two}{method}{M.faq_block(p["faq"])}')
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(src["url"])}">311 Service Requests dataset</a>, requests of type '
            f'{E(src["srType"])}, pulled {E(pulled)}'
            + (", with requests the City marked as duplicates left out" if src.get("duplicatesLeftOut") else "")
            + '. A complaint is one report to 311; it does not say rats were found, and a count says nothing about any '
            'one building, block or business. Counts only: no address or report details are kept.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            'cookies.</p></div></footer>\n</body></html>')
    return head(robots) + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "rodents"][0]
    import rodents_chicago as R, datetime as dt
    w = R.windows(dt.date(2026, 10, 26))
    d = R.build({6: 40, 24: 30, 0: 2}, {6: 243, 24: 208, 22: 169, 0: 9}, {6: 200, 24: 0, 22: 169},
                [{"d": "2026-10-25T00:00:00.000", "n": "150"}], w, "2026-10-26T06:00:00-0500")
    import tempfile
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        html = page_html(dict(spec, data=os.path.relpath(tmp.name, ROOT)))
    finally:
        os.unlink(tmp.name)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert "Lake View" in html and "629 rat complaints came in" in html, "total in the lede"
    assert ">+22%<" in html and ">too few<" in html and ">about the same<" in html, "change words"
    assert "9 of the last 30 days" in html and "too few to compare" in html, "notes under the table"
    assert M.E(M.CITY_DISCLAIMER["Chicago"]) in html, "City disclaimer"
    assert "address" not in json.dumps(d["areas"]), "counts only"
    assert 'tabindex="0"' in html and 'role="region"' in html, "scrollable table reachable by keyboard"
    shell = page_html(dict(spec, data="permits/rodents-chicago/none.json"))
    assert "noindex" in shell, "no data: the shell is never indexed"
    print("rodents_site selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
