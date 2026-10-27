#!/usr/bin/env python3
"""Chicago City Contracts by Trade: the free daily page /chicago-city-contracts/ and one sub-page and CSV per trade
(site/pages.json kind "datapage", module dp_contracts; written by tools/make_site.py). Todd's go, Oct 27, 2026,
12:17 pm ("Let's do them all", coo/PARALLEL_BUILDS.md, research_notes/kimi-2026-10-27-r10.md item 3).

Data: site/datapages/dp_contracts/contracts.json (tools/dp_contracts_data.py, daily GitHub Action) and sources.json
(tools/dp_contracts_probe.py, same Action). Business fields only: no vendor address is ever pulled, and a vendor name
that does not read as a business is shown as "Name withheld". Awards, not open bids: the page links to the City's own
bid lists and copies none of them.

Usage: python3 tools/dp_contracts.py --selftest
"""
import csv, io, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "site", "datapages", "dp_contracts")

META = {"h1": "Chicago City Contracts by Trade",
        "card": "Who wins City work in 12 trades, what it was worth, and which contracts end in the next 12 months",
        "keywords": ["chicago city contracts", "city of chicago contracts", "chicago bids", "city of chicago bid opportunities",
                     "chicago janitorial contract", "chicago snow removal contract", "chicago landscaping contract",
                     "chicago demolition contract", "city contract awards chicago", "chicago procurement"]}

FALLBACK = {"bids": "https://www.chicago.gov/city/en/depts/dps/provdrs/contract/svcs/current_bid_opportunities.html",
            "eproc": "https://www.chicago.gov/city/en/depts/dps/isupplier/current-bids.html",
            "overview": "https://www.chicago.gov/city/en/depts/dps/provdrs/contract/svcs/DPSOverview.html"}


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", "site/datapages/dp_contracts/contracts.json"))
    if not os.path.isfile(f):
        return None, None
    d = json.load(open(f, encoding="utf-8"))
    s = os.path.join(os.path.dirname(f), "sources.json")
    return d, (json.load(open(s, encoding="utf-8")) if os.path.isfile(s) else {})


def lastmod(p):
    d, _ = load(p)
    return d["source"]["fetchedAt"][:10] if d else None


def clean(t):
    """The City's text as written, with its broken characters mended (O�Hare, a � between words)."""
    t = re.sub(r"\s+�\s+", ", ", t or "")
    return re.sub(r"\s+", " ", t.replace("�", "'")).strip()


def usd(x):
    return ("-" if x < 0 else "") + f"${abs(x):,.0f}"


def usd_short(x):
    a = abs(x)
    s = (f"${a / 1e9:,.1f} billion" if a >= 1e9 else f"${a / 1e6:,.1f} million" if a >= 1e6 else f"${a:,.0f}")
    return ("-" if x < 0 else "") + s


def plural(n, one, many=None):
    return f"{n:,} {one if n == 1 else (many or one + 's')}"


def rows_of(t, cols):
    return [dict(zip(cols, r)) for r in t["rows"]]


CSS = ("<style>"
       ".cc-pick{list-style:none;margin:14px 0 0;padding:0;display:grid;gap:10px;grid-template-columns:repeat(auto-fill,minmax(248px,1fr))}"
       ".cc-pick a{display:flex;flex-direction:column;gap:4px;min-height:44px;height:100%;padding:14px 16px;border:1px solid var(--line);border-radius:12px;"
       "background:var(--card);color:var(--ink);text-decoration:none;box-shadow:var(--shadow-soft);transition:border-color .15s,transform .15s}"
       ".cc-pick a:hover{border-color:var(--teal);transform:translateY(-1px)}.cc-pick a:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".cc-pick b{font-size:17px;display:flex;justify-content:space-between;gap:8px;align-items:baseline}.cc-pick b span{color:var(--teal);font-size:15px}"
       ".cc-pick small{font-size:13.5px;color:var(--muted);line-height:1.4}.cc-pick .cc-end{color:var(--ink2);font-weight:600}"
       ".cc-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".cc-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".cc-t{width:100%;border-collapse:collapse;font-size:14.5px}.cc-t th,.cc-t td{padding:10px 12px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}"
       ".cc-t thead th{font-size:12.5px;letter-spacing:.04em;text-transform:uppercase;color:var(--muted);font-weight:700;background:var(--card);white-space:nowrap}"
       ".cc-t td.n,.cc-t th.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.cc-t tbody th{font-weight:600;color:var(--ink)}"
       ".cc-t tr:last-child td,.cc-t tr:last-child th{border-bottom:0}.cc-t td.d{min-width:220px;color:var(--ink)}.cc-t .cc-sub{display:block;font-size:12.5px;color:var(--muted);margin-top:2px}"
       ".cc-t a{color:var(--teal);font-weight:600;white-space:nowrap}.cc-t .cc-zero{color:var(--tag-ink);font-weight:600}"
       ".cc-tag{display:inline-block;font-size:12px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--teal-tint);color:var(--teal-ink);white-space:nowrap}"
       ".cc-tag.req{background:var(--input);color:var(--tag-ink)}"
       ".cc-bids{display:grid;gap:12px;margin-top:12px}@media(min-width:820px){.cc-bids{grid-template-columns:repeat(3,minmax(0,1fr))}}"
       ".cc-bid{padding:16px 18px;border:1px solid var(--line);border-radius:12px;background:var(--card);display:flex;flex-direction:column;gap:6px}"
       ".cc-bid h3{margin:0;font-size:16.5px}.cc-bid p{margin:0;font-size:14.5px;color:var(--ink2)}.cc-bid .st-btn2{margin-top:auto;align-self:flex-start}"
       ".cc-bid.key{background:var(--band);border-color:var(--band-line)}.cc-bid.key h3{color:#fff}.cc-bid.key p{color:var(--band-text)}"
       ".cc-bid.key .btn{margin-top:auto;align-self:flex-start;min-height:46px;display:inline-flex;align-items:center}"
       ".cc-read{display:grid;gap:10px;margin:12px 0 0;padding:0;list-style:none}@media(min-width:820px){.cc-read{grid-template-columns:1fr 1fr}}"
       ".cc-read li{padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);font-size:14.5px;color:var(--ink2);max-width:none}"
       ".cc-read li b{display:block;color:var(--ink);font-size:15.5px;margin-bottom:3px}"
       ".cc-chips{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}"
       ".cc-chips a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink);font-weight:600;font-size:14.5px;text-decoration:none}"
       ".cc-chips a:hover{border-color:var(--teal)}.cc-chips a[aria-current]{background:var(--ink);color:var(--card);border-color:var(--ink)}"
       ".cc-more{margin:12px 0 0}.cc-more summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".cc-more[open] summary{margin-bottom:8px}.cc-empty{padding:16px 18px;border:1px dashed var(--dash);border-radius:12px;color:var(--ink2);background:var(--canvas2);margin:12px 0 0}"
       ".cc-act{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:16px}.cc-act .btn,.cc-act .st-btn2{min-height:46px;display:inline-flex;align-items:center}"
       ".cc-two{display:grid;gap:16px}@media(min-width:900px){.cc-two{grid-template-columns:1fr 1fr}}.cc-two h3{margin:0 0 4px;font-size:17px}"
       ".cc-val{font-variant-numeric:tabular-nums}.cc-t td.dt{white-space:nowrap}.ld-tiles .lab{white-space:normal}"
       ".cc-sum thead th{white-space:normal;vertical-align:bottom;line-height:1.3}"
       "@media(max-width:699px){.cc-t.cc-stack thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}"
       ".cc-t.cc-stack,.cc-t.cc-stack tbody,.cc-t.cc-stack tr,.cc-t.cc-stack td,.cc-t.cc-stack th{display:block;width:auto}"
       ".cc-t.cc-stack tr{padding:12px 14px;border-bottom:1px solid var(--rule)}.cc-t.cc-stack tr:last-child{border-bottom:0}"
       ".cc-t.cc-stack td,.cc-t.cc-stack th{border:0;padding:3px 0;text-align:left;min-width:0;white-space:normal}"
       ".cc-t.cc-stack td[data-l]:not(.d)::before{content:attr(data-l);display:inline-block;min-width:132px;margin-right:6px;font-size:12.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.03em}"
       ".cc-t.cc-stack td.d{font-weight:600;padding-bottom:6px}.cc-t.cc-stack td.n{text-align:left}"
       ".cc-pick{grid-template-columns:1fr}}"
       "</style>")


def table(label, head, rows, stack=True, cls=""):
    """A scrollable, keyboard-reachable table; on phones each row stacks into a card with its labels."""
    th = "".join(f'<th scope="col"{" class=n" if n else ""}>{h}</th>' for h, n in head)
    return (f'<div class="cc-tw" role="region" aria-label="{label}" tabindex="0"><table class="cc-t{" cc-stack" if stack else ""}{cls}">'
            f'<thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


def td(v, label, num=False, cls=""):
    c = " ".join(x for x in (("n" if num else ""), cls) if x)
    return f'<td{f" class={chr(34)}{c}{chr(34)}" if c else ""} data-l="{label}">{v}</td>'


def pdf_link(E, u, what):
    return f'<a href="{E(u)}" rel="noopener">PDF<span class="sr"> of the contract for {E(clean(what)[:60])}</span></a>' if u else '<span class="cc-sub">No PDF listed</span>'


SR = "<style>.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}</style>"


def value_cell(E, e):
    if e["requirements"] and e["value"] == 0:
        return '<span class="cc-tag req">$0, orders as needed</span>'
    sub = f'<span class="cc-sub">{plural(e["revisions"], "change")}</span>' if e["revisions"] else ""
    return f'<span class="cc-val">{usd(e["value"])}</span>{sub}'


def award_cell(r):
    if r["amount"] == 0:
        return '<span class="cc-tag req">$0, orders as needed</span>'
    return usd(r["amount"])


def bids_block(E, M, src, rel_short=False):
    """Where open bids actually live: the City's own lists, as our Action found them that morning."""
    b = (src or {}).get("bids", {})
    w = b.get("weekly") or {}
    checked = M.nice_date((src or {}).get("checkedAt", "")[:10]) if src else ""
    weekly = ""
    if w.get("url") and w.get("date"):
        weekly = (f'<div class="cc-bid"><h3>Weekly bid opportunity list</h3><p>A PDF the City posts each week. When we checked on {E(checked)}, '
                  f'its bid page linked the list dated {E(M.nice_date(w["date"]))}.</p>'
                  f'<a class="st-btn2" href="{E(w["url"])}" rel="noopener">Open the weekly list (PDF)</a></div>')
    return ('<div class="cc-bids">'
            f'<div class="cc-bid key"><h3>eProcurement bid opportunities</h3><p>The City\'s live list of bids and requests for proposals open for responses, with due dates. '
            'You register as a vendor to respond.</p>'
            f'<a class="btn" href="{E(FALLBACK["eproc"])}" rel="noopener">See open City bids</a></div>'
            f'<div class="cc-bid"><h3>Current Bid Opportunities</h3><p>The Department of Procurement Services page for bids, plans too large for eProcurement, and notices from other City offices.</p>'
            f'<a class="st-btn2" href="{E(FALLBACK["bids"])}" rel="noopener">Procurement Services bids</a></div>'
            + (weekly or f'<div class="cc-bid"><h3>Doing business with the City</h3><p>How the City buys, how to register, and its alerts and workshops.</p>'
                         f'<a class="st-btn2" href="{E(FALLBACK["overview"])}" rel="noopener">Procurement Services</a></div>')
            + '</div>'
            f'<p class="asof">We link to the City\'s lists and copy no open bid onto this page; only the City\'s lists are complete. '
            f'<a href="{E(FALLBACK["overview"])}" rel="noopener">Doing Business with the City of Chicago</a>, Department of Procurement Services.'
            + (f' Links checked {E(checked)}.' if checked else "") + '</p>')


def reading_notes():
    return ('<ul class="cc-read">'
            '<li><b>Awards, not open bids</b>These are contracts the City has already approved. To bid on new work, use the City\'s bid lists below.</li>'
            '<li><b>Award totals are not unit prices</b>An award is the most the City may spend over the whole contract, often years and many sites or items. It does not say what one job or one hour pays.</li>'
            '<li><b>$0 means orders as needed</b>The City lists some blanket contracts at $0. The City orders as it needs, and no amount is promised. They are counted, but not in totals or medians.</li>'
            '<li><b>Changes are counted apart</b>A new award is revision 0. Later changes (more money, less money, more time) are modifications, shown on their own. Money taken out shows as a negative amount and is never subtracted from award totals.</li>'
            '<li><b>End dates cover blanket contracts</b>The City records an end date only for blanket contracts (repeat purchases). Standard contracts, most construction, end when the work is accepted, so they never show as ending.</li>'
            '<li><b>Sorted by the contract\'s own words</b>A contract joins a trade when its description uses that trade\'s words (the map is below). One contract can count in two trades, and work described in other words is missed.</li>'
            '</ul>')


def trade_map(E, d, data_mod):
    rows = []
    for t in data_mod.TRADES:
        rows.append(f'<tr><th scope="row">{E(t["name"])}</th>{td(E("; ".join(t["words"])), "Words")}</tr>')
    return (table("The words that put a contract in each trade", [("Trade", False), ("A contract joins when its description uses", False)], rows)
            + '<p class="asof">Matching ignores capitals, and most words also find their longer forms (roof finds roofing). Left out of every trade: purchases of goods or equipment (supplies, parts, vehicles) '
            'unless the description also names work such as service, repair, maintenance or removal; upkeep of the City\'s own machines and fleet; design, engineering and consulting; '
            'software; art; grants to agencies; leases; and redevelopment deals. A few more words keep look-alikes out (rock salt from snow removal, lead paint removal from painting, '
            'elevators from HVAC).</p>')


def footer(E, M, rel, d):
    s = d["source"]
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(s["url"])}">Contracts dataset ({E(s["dataset"])})</a>, contracts and modifications the City has awarded since 1993, '
            f'last updated by the City {E(M.nice_date(s["rowsUpdatedAt"]))}, read by us {E(M.nice_date(s["fetchedAt"]))}. We keep the awards and changes approved in the last 36 months and the contracts ending in the next 12, '
            'sort them into trades by the words in their descriptions, and drop every vendor address. Vendor names are business names as the City lists them. </p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Public information, not legal, tax or financial advice. Before you bid, check the solicitation and its rules with the City\'s Department of Procurement Services.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n</body></html>')


def head(M, E, p, url, rel, title, desc, ld, robots):
    return M.HEAD.format(title=E(title), desc=E(desc), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS + SR, bodycls=' class="ld-page"',
                         robots=robots, analytics=M.analytics_tag())


def summary(d):
    T = d["trades"]
    return {"awards12": sum(t["m12"]["awards"] for t in T), "total12": sum(t["m12"]["total"] for t in T),
            "awards36": sum(t["m36"]["awards"] for t in T), "ending": len({e["contract"] for t in T for e in t["ending"]})}


def page_html(p):
    import make_site as M
    import dp_contracts_data as DD
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d, src = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    if not d:
        return (head(M, E, p, url, rel, p["title"], p["desc"], M.ld_tags(crumb_ld), '<meta name="robots" content="noindex, nofollow">')
                + f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first daily pull is on its way.</p></div></main></body></html>')
    s, w, T = d["source"], d["window"], d["trades"]
    S = summary(d)
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": p["h1"], "url": url, "description": p["desc"],
          "isBasedOn": s["url"], "creator": {"@type": "Organization", "name": "ProofNotFluff"},
          "temporalCoverage": f'{w["from36"]}/{w["today"]}', "dateModified": s["fetchedAt"][:10],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f'{url}{t["key"]}/{csv_name(t)}'} for t in T]}
    lede = (f'The City of Chicago publishes every contract it awards. We sort the last three years into {len(T)} trades, so you can see who wins City work in yours, '
            f'what it was worth, and which contracts end in the next 12 months and may go back out to bid.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Ending in 12 months</div><div class="val">{S["ending"]:,}</div><div class="sub">contracts in these trades; the work may go back out to bid</div></div>'
             f'<div class="tile"><div class="lab">New awards, 12 months</div><div class="val">{S["awards12"]:,}</div><div class="sub">{E(usd_short(S["total12"]))} across {len(T)} trades</div></div>'
             f'<div class="tile"><div class="lab">New awards, 36 months</div><div class="val">{S["awards36"]:,}</div><div class="sub">since {E(M.nice_date(w["from36"]))}</div></div>'
             f'<div class="tile"><div class="lab">City data as of</div><div class="val">{E(M.nice_date(s["rowsUpdatedAt"]).rsplit(",", 1)[0])}</div><div class="sub">refreshed here every morning</div></div>'
             '</div>'
             f'<p class="asof">Contracts approved from {E(M.nice_date(w["from36"]))} to {E(M.nice_date(w["today"]))}, from the City\'s Contracts dataset. '
             'A contract that names two trades counts in both, so trade counts add up to more than these totals.</p>')
    cards = "".join(
        f'<li><a href="{E(t["key"])}/"><b>{E(t["name"])}<span aria-hidden="true">&rarr;</span></b>'
        f'<small class="cc-end">{plural(len(t["ending"]), "contract")} ending in 12 months</small>'
        + (f'<small>{plural(t["m36"]["awards"], "new award")} in 36 months'
           + (f', {E(usd_short(t["m36"]["total"]))}' if t["m36"]["total"] else "") + '</small>' if t["m36"]["awards"] else
           f'<small>No new award in 36 months; {plural(t["m36"]["mods"], "change")} to older contracts</small>') + '</a></li>' for t in T)
    rows = []
    for t in T:
        a, b = t["m12"], t["m36"]
        rows.append(f'<tr><th scope="row"><a href="{E(t["key"])}/">{E(t["name"])}</a></th>'
                    + td(f'{a["awards"]:,}', "New awards, 12 mo", True) + td(E(usd(a["total"])) if a["total"] else "None", "Total, 12 mo", True)
                    + td(f'{b["awards"]:,}', "New awards, 36 mo", True) + td(E(usd(b["total"])) if b["total"] else "None", "Total, 36 mo", True)
                    + td(E(usd(b["median"])) if b["median"] else "None", "Median award", True)
                    + td(f'{len(t["ending"]):,}', "Ending, 12 mo", True) + '</tr>')
    summ = table("City contract awards by trade", [("Trade", False), ("New awards, 12 mo", True), ("Total, 12 mo", True), ("New awards, 36 mo", True),
                                                   ("Total, 36 mo", True), ("Median award, 36 mo", True), ("Ending in 12 mo", True)], rows, cls=" cc-sum")
    ending = sorted({e["contract"]: (e, t) for t in T for e in t["ending"]}.values(), key=lambda x: (x[0]["end"], -x[0]["value"]))
    names = {}
    for t in T:
        for e in t["ending"]:
            names.setdefault(e["contract"], []).append(t["short"])
    erows = [f'<tr>{td(E(M.nice_date(e["end"])), "Ends", cls="dt")}'
             f'<td class="d" data-l="Covers">{E(clean(e["description"]))}<span class="cc-sub">{E(", ".join(names[e["contract"]]))} · {E(e["department"])}</span></td>'
             + td(E(e["vendor"]), "Vendor") + td(value_cell(E, e), "Value so far", True) + td(pdf_link(E, e["pdf"], e["description"]), "Contract") + '</tr>'
             for e, t in ending[:12]]
    end_html = (table("City contracts in these trades ending soonest", [("Ends", False), ("What it covers", False), ("Vendor", False), ("Value so far", True), ("Contract", False)], erows)
                + (f'<p class="asof">The {min(12, len(ending))} that end soonest of {plural(len(ending), "contract")}. Every one is on its trade\'s page and in its CSV. '
                   'Value so far adds up the award and every change since.</p>') if ending else '<p class="cc-empty">No contract in these trades has an end date in the next 12 months.</p>')
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(lede)}</p>'
            '<div class="ld-heroact cc-act"><a class="btn" href="#trades">Pick your trade</a><a class="st-btn2" href="#bids">Where open bids are</a></div></div>'
            f'{tiles}'
            f'<section class="block" id="trades"><h2>Pick your trade</h2><p>Each trade has its own page with every award, change and ending contract, and a CSV to download.</p><ul class="cc-pick">{cards}</ul></section>'
            f'<section class="block" id="ending"><h2>Contracts ending soonest</h2><p>When a City contract ends, the work often goes back out to bid. These end next.</p>{end_html}</section>'
            f'<section class="block" id="all"><h2>Every trade at a glance</h2>{summ}<p class="asof">Totals and medians use new awards with a dollar amount. Changes to contracts are on each trade\'s page.</p></section>'
            f'<section class="block" id="bids"><h2>Where open bids are</h2><p>This page shows awards. Open City bids live on the City\'s own lists.</p>{bids_block(E, M, src)}</section>'
            f'<section class="block" id="read"><h2>How to read these numbers</h2>{reading_notes()}</section>'
            f'<section class="block" id="map"><h2>The trade map</h2><p>How a contract is placed in a trade, word for word.</p>{trade_map(E, d, DD)}</section>'
            '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + '</section>'
            f'{M.faq_block(p["faq"])}'
            '<div class="cc-act"><a class="btn" href="#trades">Pick your trade</a><a class="st-btn2" href="' + E(FALLBACK["eproc"]) + '" rel="noopener">See open City bids</a></div>')
    return head(M, E, p, url, rel, p["title"], p["desc"], M.ld_tags(crumb_ld, faq_ld, ds), robots) + body + footer(E, M, rel, d)


def csv_name(t):
    return f"chicago-city-contracts-{t['key']}.csv"


CSV_COLS = ["record", "approval_date", "end_date", "description", "department", "vendor", "amount_usd", "contract_type",
            "procurement_type", "specification_number", "contract_number", "revision_number", "contract_pdf"]


def safe(v):
    """No spreadsheet formula can start a text cell (=, +, -, @): such text gets a leading apostrophe."""
    return "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@") else v


def trade_csv(d, t):
    out = io.StringIO()
    wtr = csv.writer(out, lineterminator="\n")
    wtr.writerow(CSV_COLS)
    for e in t["ending"]:
        wtr.writerow([safe(x) for x in ["ending in next 12 months (value so far)", e["approved"], e["end"], clean(e["description"]), e["department"], e["vendor"],
                                         f'{e["value"]:.2f}', e["contractType"], e["procurementType"], e["spec"], e["contract"], e["revisions"], e["pdf"]]])
    for r in rows_of(t, d["rowCols"]):
        kind = "new award" if r["revision"] == 0 else ("transfer to a new contract number" if r["revision"] < 0 else "modification")
        wtr.writerow([safe(x) for x in [kind, r["approved"], r["end"], clean(r["description"]), r["department"], r["vendor"], f'{r["amount"]:.2f}',
                                         r["contractType"], r["procurementType"], r["spec"], r["contract"], max(r["revision"], 0), r["pdf"]]])
    s = d["source"]
    wtr.writerow([])
    wtr.writerow([safe(f'Source: City of Chicago Data Portal, Contracts ({s["dataset"]}), {s["url"]}, read {s["fetchedAt"][:10]}. '
                       f'Awards and modifications approved {d["window"]["from36"]} to {d["window"]["today"]}, and contracts whose latest end date falls by {d["window"]["endTo"]}. '
                       'An award of 0 on a blanket contract depends upon requirements (orders as needed). Negative amounts are modifications that took money out. '
                       'Award totals are not unit prices. Vendor addresses are not included; "Name withheld" marks a vendor name that does not read as a business.')])
    wtr.writerow([safe(f'Trade words: {", ".join(next(x for x in __import__("dp_contracts_data").TRADES if x["key"] == t["key"])["words"])}. '
                       'Purchases of goods, fleet upkeep, design and engineering, software, art, grants, leases and redevelopment deals are left out.')])
    import make_site as M
    wtr.writerow([M.CITY_DISCLAIMER["Chicago"]])
    return out.getvalue()


PROC = {"BID": "Bid", "RFP": "RFP", "RFQ": "RFQ", "SOLE SOURCE": "Sole source", "EMERGENCY": "Emergency", "MASTER AGREEMENT": "Master agreement",
        "JOINT PURCHASE": "Joint purchase", "REFERENCE CONTRACT": "Reference contract", "": "Not stated", "Not stated": "Not stated"}


def proc(x):
    return PROC.get(x, x.capitalize() if x.isupper() else x)


def trade_page(p, d, src, t):
    import make_site as M
    E = M.E
    base = M.BASE + p["slug"] + "/"
    url, rel = base + t["key"] + "/", "../../"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    h1 = f'Chicago City Contracts: {t["name"]}'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], p["slug"] + "/"), (t["name"], None)])
    s, w = d["source"], d["window"]
    a12, a36 = t["m12"], t["m36"]
    rows = rows_of(t, d["rowCols"])
    new = [r for r in rows if r["revision"] == 0]
    mods = [r for r in rows if r["revision"] > 0]
    moved = [r for r in rows if r["revision"] < 0]
    lede = (f'{plural(a36["awards"], "new City award")} matched {t["name"].lower()} in the last 36 months'
            + (f', worth {usd_short(a36["total"])} in all' if a36["total"] else "")
            + f'. {plural(len(t["ending"]), "contract")} in this trade {"ends" if len(t["ending"]) == 1 else "end"} in the next 12 months.')
    desc = (f'City of Chicago contracts for {t["name"].lower()}: {plural(a36["awards"], "new award")} in 36 months, {plural(len(t["ending"]), "contract")} ending in the next 12 months, '
            'who won them and the contract PDFs. Free, updated daily from City records.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Ending in 12 months</div><div class="val">{len(t["ending"]):,}</div><div class="sub">the work may go back out to bid</div></div>'
             f'<div class="tile"><div class="lab">New awards, 12 months</div><div class="val">{a12["awards"]:,}</div><div class="sub">{E(usd_short(a12["total"])) if a12["total"] else "no dollar total"}'
             + (f', plus {a12["zero"]:,} at $0' if a12["zero"] else "") + '</div></div>'
             f'<div class="tile"><div class="lab">New awards, 36 months</div><div class="val">{a36["awards"]:,}</div><div class="sub">'
             + (f'{E(usd_short(a36["total"]))}, median {E(usd_short(a36["median"]))}' if a36["median"] else "no dollar total") + '</div></div>'
             f'<div class="tile"><div class="lab">Changes, 36 months</div><div class="val">{a36["mods"]:,}</div><div class="sub">'
             + (f'{E(usd_short(a36["modsUpTotal"]))} added' if a36["modsUpTotal"] else "no money added")
             + (f', {E(usd_short(-a36["modsDownTotal"]))} taken out' if a36["modsDownTotal"] else "") + '</div></div></div>'
             f'<p class="asof">City data as of {E(M.nice_date(s["rowsUpdatedAt"]))}. Totals and medians use new awards with a dollar amount; award totals are not unit prices.</p>')
    erows = [f'<tr>{td(E(M.nice_date(e["end"])), "Ends", cls="dt")}'
             f'<td class="d" data-l="Covers">{E(clean(e["description"]))}<span class="cc-sub">{E(e["department"])} · contract {E(e["contract"])}'
             + (f' · spec {E(e["spec"])}' if e["spec"] else "") + '</span></td>'
             + td(E(e["vendor"]), "Vendor") + td(value_cell(E, e), "Value so far", True)
             + td(E(M.nice_date(e["approved"])) if e["approved"] else "Not stated", "First approved", cls="dt") + td(pdf_link(E, e["pdf"], e["description"]), "Contract") + '</tr>'
             for e in t["ending"]]
    end_html = (table(f'{t["name"]} contracts ending in the next 12 months', [("Ends", False), ("What it covers", False), ("Vendor", False), ("Value so far", True),
                                                                              ("First approved", False), ("Contract", False)], erows)
                + '<p class="asof">Ending by the latest end date on the contract, after any time extensions. Value so far adds up the award and every change since. '
                  'A $0 value is a contract the City orders from as needed.</p>') if erows else (
        f'<p class="cc-empty">No City contract that matched {E(t["name"].lower())} has an end date in the next 12 months. Standard contracts, such as most construction, '
        'end when the work is accepted and never show here.</p>')
    SHOW = 25
    nrow = lambda r: (f'<tr>{td(E(M.nice_date(r["approved"])), "Approved", cls="dt")}'
                      f'<td class="d" data-l="Covers">{E(clean(r["description"]))}<span class="cc-sub">{E(r["department"])}</span></td>'
                      + td(E(r["vendor"]), "Vendor") + td(award_cell(r), "Award", True) + td(E(proc(r["procurementType"] or "Not stated")), "How bought")
                      + td(pdf_link(E, r["pdf"], r["description"]), "Contract") + '</tr>')
    nhead = [("Approved", False), ("What it covers", False), ("Vendor", False), ("Award", True), ("How bought", False), ("Contract", False)]
    new_html = (table(f'New {t["name"].lower()} awards, newest first', nhead, [nrow(r) for r in new[:SHOW]])
                + (f'<details class="cc-more"><summary>Show the other {len(new) - SHOW} new awards</summary>'
                   + table(f'Older new {t["name"].lower()} awards', nhead, [nrow(r) for r in new[SHOW:]]) + '</details>' if len(new) > SHOW else "")
                ) if new else f'<p class="cc-empty">No new City award matched {E(t["name"].lower())} from {E(M.nice_date(w["from36"]))} to {E(M.nice_date(w["today"]))}. Changes to older contracts are below.</p>'
    mrow = lambda r: (f'<tr>{td(E(M.nice_date(r["approved"])), "Approved", cls="dt")}'
                      f'<td class="d" data-l="Covers">{E(clean(r["description"]))}<span class="cc-sub">{E(r["vendor"])} · contract {E(r["contract"])}, change {r["revision"]}</span></td>'
                      + td(("+" + usd(r["amount"])) if r["amount"] > 0 else (usd(r["amount"]) if r["amount"] < 0 else "No money change"), "Change", True)
                      + td(pdf_link(E, r["pdf"], r["description"]), "Contract") + '</tr>')
    mhead = [("Approved", False), ("Contract changed", False), ("Change", True), ("Contract", False)]
    MSHOW = 10
    mod_html = ((f'<p>{plural(a36["mods"], "change")} in 36 months: {a36["modsUp"]:,} added {E(usd(a36["modsUpTotal"]))}, {a36["modsDown"]:,} took out {E(usd(-a36["modsDownTotal"]))}, '
                 f'and {a36["modsZero"]:,} changed no money (often more time).'
                 + (f' {plural(len(moved), "record")} only moved a contract to a new number and {"is" if len(moved) == 1 else "are"} not counted as new awards.' if moved else "") + '</p>'
                 + table(f'Changes to {t["name"].lower()} contracts, newest first', mhead, [mrow(r) for r in mods[:MSHOW]])
                 + (f'<details class="cc-more"><summary>Show the other {len(mods) - MSHOW} changes</summary>'
                    + table(f'Older changes to {t["name"].lower()} contracts', mhead, [mrow(r) for r in mods[MSHOW:]]) + '</details>' if len(mods) > MSHOW else ""))
                if mods else '<p class="cc-empty">No changes to contracts in this trade in the last 36 months.</p>')
    grp = lambda xs, label, first: table(label, [(first, False), ("New awards", True), ("Total", True)],
                                         [f'<tr><th scope="row">{E(proc(x["name"]) if first == "How bought" else x["name"])}</th>'
                                          + td(f'{x["n"]:,}' + (f' <span class="cc-sub">{x["zero"]:,} at $0</span>' if x["zero"] else ""), "New awards", True)
                                          + td(E(usd(x["total"])) if x["total"] else "None", "Total", True) + '</tr>' for x in xs])
    lo = t["name"].lower()
    who = ((f'<div class="cc-two"><div><h3>Which departments buy it</h3>{grp(t["byDept"], "New " + lo + " awards by City department", "Department")}</div>'
            f'<div><h3>How the City bought it</h3>{grp(t["byProc"], "New " + lo + " awards by procurement type", "How bought")}</div></div>'
            '<p class="asof">How bought is the City\'s procurement type as written: BID is a competitive bid, RFP a request for proposals, RFQ a request for qualifications.</p>')
           if new else "")
    vend = (table(f'Vendors with the most new {t["name"].lower()} award dollars', [("Vendor", False), ("New awards", True), ("Total", True)],
                  [f'<tr><th scope="row">{E(v["name"])}</th>' + td(f'{v["n"]:,}', "New awards", True) + td(E(usd(v["total"])), "Total", True) + '</tr>' for v in t["topVendors"]])
            + '<p class="asof">Ranked by the dollar total of new awards in 36 months. Business names as the City lists them; one firm can appear under more than one spelling.'
            + (f' {plural(t["withheld"], "row")} in this trade show "Name withheld" because the vendor name does not read as a business.' if t["withheld"] else "") + '</p>'
            ) if t["topVendors"] else '<p class="cc-empty">No vendor won a new award with a dollar amount in this trade in the last 36 months.</p>'
    others = "".join(f'<li><a href="../{E(x["key"])}/"{" aria-current=page" if x["key"] == t["key"] else ""}>{E(x["short"])}</a></li>' for x in d["trades"])
    words = "; ".join(t["words"])
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": h1, "url": url, "description": desc, "isBasedOn": s["url"],
          "creator": {"@type": "Organization", "name": "ProofNotFluff"}, "dateModified": s["fetchedAt"][:10],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + csv_name(t)}]}
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">Free tracker of City awards · {E(t["short"])}</p><h1>{E(h1)}</h1><p class="lede">{E(lede)}</p>'
            f'<div class="ld-heroact cc-act"><a class="btn" href="#ending">See ending contracts</a><a class="st-btn2" href="{E(csv_name(t))}" download>Download the CSV</a></div></div>'
            f'{tiles}'
            f'<section class="block" id="ending"><h2>Contracts ending in the next 12 months</h2><p>When these end, the City may bid the work again. Watch the City\'s bid lists for the rebid.</p>{end_html}</section>'
            f'<section class="block" id="new"><h2>New awards, last 36 months</h2>{new_html}</section>'
            + (f'<section class="block" id="who"><h2>Who buys it, and how</h2>{who}</section>' if who else "")
            + f'<section class="block" id="vendors"><h2>Who wins it</h2>{vend}</section>'
            f'<section class="block" id="changes"><h2>Changes to contracts</h2>{mod_html}</section>'
            f'<section class="block" id="bids"><h2>Where open bids are</h2>{bids_block(E, M, src)}</section>'
            f'<section class="block" id="words"><h2>What counts as {E(t["name"].lower())}</h2><p>A City contract joins this trade when its description uses any of these words: {E(words)}. '
            f'Purchases of goods, fleet upkeep, design and engineering, software, art, grants, leases and redevelopment deals are left out. <a href="../#map">See the whole trade map</a>.</p>'
            f'{reading_notes()}</section>'
            f'<section class="block"><h2>Other trades</h2><ul class="cc-chips">{others}</ul></section>'
            f'<div class="cc-act"><a class="btn" href="{E(csv_name(t))}" download>Download the {E(t["short"].lower())} CSV</a><a class="st-btn2" href="../">All trades</a></div>')
    return head(M, E, p, url, rel, f'{h1} | ProofNotFluff', desc, M.ld_tags(crumb_ld, ds), robots) + body + footer(E, M, rel, d)


def extra_pages(p):
    d, src = load(p)
    if not d:
        return []
    out = []
    for t in d["trades"]:
        out.append((f'{t["key"]}/index.html', trade_page(p, d, src, t)))
        out.append((f'{t["key"]}/{csv_name(t)}', trade_csv(d, t)))
    return out


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, dp_contracts_data as DD, datetime as dt, tempfile, shutil
    M.PAGES_LIVE[:] = []
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == "chicago-city-contracts"][0]
    R = lambda desc, a, rv=0, ad="2026-05-01", po="P1", end=None, v="ACME CLEANING INC": {
        "purchase_order_description": desc, "award_amount": str(a), "revision_number": str(rv), "approval_date": ad + "T00:00:00.000",
        "contract_type": "WORK SERVICES / FACILITIES MAINT.", "purchase_order_contract_number": po, "end_date": (end + "T00:00:00.000") if end else None,
        "vendor_name": v, "procurement_type": "BID", "department": "DEPT OF FLEET AND FACILITY MANAGEMENT", "contract_pdf": {"url": "https://example.org/c.pdf"},
        "specification_number": "1234"}
    rows = [R("JANITORIAL SERVICES - O�HARE", 100000, po="A"), R("JANITORIAL SERVICES", 300000, po="B", ad="2024-01-10"),
            R("JANITORIAL SERVICES", 0, po="D", v="JANE DOE"), R("JANITORIAL SERVICES", -2000, rv=2, po="A"), R("=HYPERLINK(1) JANITORIAL SERVICES", 7000, rv=1, po="A")]
    ending = [R("JANITORIAL SERVICES", 0, po="D", end="2027-01-31", v="JANE DOE")]
    d = DD.build(rows, ending, dt.date(2026, 10, 27), {"name": "Contracts", "rowsUpdatedAtIso": "2026-10-27T03:17:28-05:00"}, "2026-10-27T08:00:00-05:00")
    tmp = tempfile.mkdtemp(dir=ROOT)
    try:
        json.dump(d, open(os.path.join(tmp, "contracts.json"), "w"))
        json.dump({"checkedAt": "2026-10-27T07:05:00-05:00", "bids": {"weekly": {"url": "https://www.chicago.gov/x/102626.pdf", "date": "2026-10-26"}}},
                  open(os.path.join(tmp, "sources.json"), "w"))
        sp = dict(spec, data=os.path.relpath(os.path.join(tmp, "contracts.json"), ROOT))
        html = page_html(sp)
        extras = dict(extra_pages(sp))
    finally:
        shutil.rmtree(tmp)
    sub = extras["janitorial/index.html"]
    csvt = extras["janitorial/chicago-city-contracts-janitorial.csv"]
    for h in [html, sub] + [v for k, v in extras.items() if k.endswith(".html")]:
        assert h.count("<h1>") == 1 and "—" not in h and "–" not in h, "one h1, no dashes"
        assert M.E(M.CITY_DISCLAIMER["Chicago"]) in h, "City disclaimer, word for word"
        assert "noindex" in h, "draft pages stay out of search"
    assert "O&#x27;HARE" in sub and "�" not in sub, "broken characters mended"
    assert "JANE" not in html + sub + csvt and "Name withheld" in sub, "a person's name never shows"
    assert "$0, orders as needed" in sub and "not unit prices" in sub, "zero-dollar label and the unit price note"
    assert "+$7,000" in sub and "-$2,000" in sub, "modifications apart, money out shown negative"
    assert "Jan 31, 2027" in sub and "Oct 26, 2026" in sub, "ending contract and the weekly list date"
    assert "\n'=HYPERLINK" not in csvt and ",'=HYPERLINK" in csvt, "no formula can start a CSV cell"
    assert len(extras) == 2 * len(DD.TRADES), "a page and a CSV per trade"
    assert 'role="region"' in sub and 'tabindex="0"' in sub, "scrollable tables reachable by keyboard"
    assert page_html(dict(spec, data="site/datapages/dp_contracts/none.json")).count("noindex") == 1, "no data: an unindexed shell"
    print("dp_contracts selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
