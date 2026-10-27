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
        "keywords": ("chicago city contracts, city of chicago contracts, chicago bids, city of chicago bid opportunities, "
                     "janitorial, snow removal, landscaping, demolition, roofing, hvac, electrical, plumbing, contract awards, procurement")}

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
       ".cc-t.cc-stack td.d{font-weight:500;padding-bottom:6px}.cc-t.cc-stack td.n{text-align:left}"
       ".cc-pick{grid-template-columns:1fr}"
       ".cc-t.cc-stack td[data-l]:not(.d){display:grid;grid-template-columns:132px minmax(0,1fr);column-gap:8px;align-items:start}"
       ".cc-t.cc-stack td[data-l]:not(.d)::before{min-width:0;margin:0;padding-top:2px}"
       ".cc-t.cc-stack a{display:inline-flex;align-items:center;min-height:44px;min-width:44px}"
       ".cc-t.cc-stack tbody th a{min-height:44px}.cc-pre{display:none}}"
       "@media(max-width:759px){main ul.cc-pick li a{padding:14px 16px}main ul.cc-chips li a{padding:0 14px}}"
       ".cc-chips a{min-width:44px;justify-content:center}.nw{white-space:nowrap}"
       ".cc-pick .cc-end.z{color:var(--muted);font-weight:500}.cc-none{color:var(--muted)}"
       ".cc-grp{margin:22px 0 0;font-size:13px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}.cc-grp+.cc-pick{margin-top:10px}"
       ".ld-hero .cc-hact{margin-bottom:22px}@media(min-width:760px){.ld-hero .cc-hact{margin-bottom:26px}}"
       ".cc-sumd>summary{display:none}.cc-sumd>summary::-webkit-details-marker{display:none}"
       "@media(max-width:699px){.cc-sumd>summary{display:flex;align-items:center;min-height:48px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink);list-style:none}"
       ".cc-sumd[open]>summary{margin-bottom:8px}}"
       ".cc-sum{min-width:0}.cc-sum th,.cc-sum td{padding:10px 10px}"
       ".cc-sumd .cc-tw{border:0;border-top:1px solid var(--line);border-radius:0;margin:0}.cc-sumd{border:1px solid var(--line);border-radius:12px;overflow:hidden;background:var(--card);margin-top:12px}"
       ".cc-nd{color:var(--muted);font-weight:400}nav.otp .otp-in a{min-height:44px}"
       ".cc-pick b{text-wrap:balance}.cc-pick small{text-wrap:pretty}section.block p.cc-empty{max-width:none}.cc-fine{margin-top:14px}.cc-fine .asof{font-size:14px;margin:0 0 8px}"
       "@media(max-width:419px){.cc-hact .btn,.cc-hact .st-btn2,.cc-act .btn,.cc-act .st-btn2{width:100%;justify-content:center}}"
       ".fnav{gap:0;margin:0 -11px 10px}.fnav a{padding:0 11px;justify-content:center}"
       "@media(max-width:699px){.cc-t.cc-stack td[data-l]>.cv>a{align-items:flex-start;padding-top:2px}"
       ".cc-t.cc-stack.cc-map td[data-l]:not(.d){display:block}.cc-t.cc-stack.cc-map td[data-l]:not(.d)::before{content:none}.cc-sumd{border:0;background:none;overflow:visible}.cc-sumd .cc-tw{border:1px solid var(--line);border-radius:12px}}"
       "</style>"
       "<script>try{if(matchMedia('(max-width:699px)').matches){document.addEventListener('DOMContentLoaded',function(){var d=document.querySelector('.cc-sumd');if(d)d.removeAttribute('open')})}}catch(e){}</script>")


def table(label, head, rows, stack=True, cls=""):
    """A scrollable, keyboard-reachable table; on phones each row stacks into a card with its labels."""
    th = "".join(f'<th scope="col"{" class=n" if n else ""}>{h}</th>' for h, n in head)
    return (f'<div class="cc-tw" role="region" aria-label="{label}" tabindex="0"><table class="cc-t{" cc-stack" if stack else ""}{cls}">'
            f'<thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>')


GROUPS = [("Building systems", ["hvac", "electrical", "plumbing", "roofing"]),
          ("Building care", ["janitorial", "painting", "pest-control", "pressure-washing"]),
          ("Grounds and site", ["landscaping", "snow-removal", "demolition", "hauling"])]


def dept(E, x):
    """A department, or a quiet note when the City left it blank."""
    return '<span class="cc-nd">Department not stated</span>' if x in ("", "Not stated") else E(x)


def otp(items):
    """The site's on-this-page bar (assets/pnf-ui.js highlights the section in view)."""
    return ('<nav class="otp" aria-label="On this page"><div class="otp-in">'
            + "".join(f'<a href="#{k}">{v}</a>' for k, v in items) + '</div></nav>')


def td(v, label, num=False, cls=""):
    c = " ".join(x for x in (("n" if num else ""), cls) if x)
    return f'<td{f" class={chr(34)}{c}{chr(34)}" if c else ""} data-l="{label}"><span class="cv">{v}</span></td>'


def pdf_link(E, u, label):
    """label names the record: "contract 75076" or "the change to contract 32835 approved Oct 9, 2026"."""
    return f'<a href="{E(u)}" rel="noopener">PDF<span class="sr"> of {E(label)}</span></a>' if u else '<span class="cc-sub nw">No PDF</span>'


SR = "<style>.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}</style>"


def value_cell(E, e):
    if e["requirements"] and e["value"] == 0:
        return '<span class="cc-tag req">$0, orders as needed</span>'
    n = e.get("changes", e["revisions"])
    sub = f'<span class="cc-sub">{plural(n, "change")}</span>' if n else ""
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
            f'<div class="cc-bid"><h3>Current bid opportunities</h3><p>The Department of Procurement Services page for bids, plans too large for eProcurement, and notices from other City offices.</p>'
            f'<a class="st-btn2" href="{E(FALLBACK["bids"])}" rel="noopener">Procurement Services bids</a></div>'
            + (weekly or f'<div class="cc-bid"><h3>Doing business with the City</h3><p>How the City buys, how to register, and its alerts and workshops.</p>'
                         f'<a class="st-btn2" href="{E(FALLBACK["overview"])}" rel="noopener">Procurement Services</a></div>')
            + '</div>'
            f'<p class="asof">We link to the City\'s lists and copy no open bid onto this page; only the City\'s lists are complete. '
            f'<a href="{E(FALLBACK["overview"])}" rel="noopener">Doing Business with the City of Chicago</a>, Department of Procurement Services.'
            + (f' Links checked {E(checked)}.' if checked else "") + '</p>')


def flags(trades):
    """What the shown rows hold, so each note explains only what a visitor can see."""
    rows = [r for t in trades for r in t["rows"]]
    ends = [e for t in trades for e in t["ending"]]
    return {"awards": any(r[1] == 0 for r in rows), "zero": any(r[1] == 0 and r[5] == 0 for r in rows) or any(e["requirements"] and e["value"] == 0 for e in ends),
            "neg": any(r[5] < 0 for r in rows), "changes": any(r[1] > 0 for r in rows),
            "withheld": any(r[4] == "Name withheld" for r in rows) or any(e["vendor"] == "Name withheld" for e in ends)}


def reading_notes(f, hub=False):
    li = ['<li><b>Awards, not open bids</b>This tracker lists contracts the City has already approved. To bid on new work, use the City\'s bid lists on this page.</li>']
    if f["awards"] or f["changes"]:
        li.append('<li><b>Award totals are not unit prices</b>An award is the most the City may spend over the whole contract, often years and many sites or items. It does not say what one job or one hour pays.</li>')
    if f["zero"]:
        li.append('<li><b>$0 means orders as needed</b>The City lists some blanket contracts at $0. The City orders as it needs, and no amount is promised. They are counted, but not in totals or medians.</li>')
    if f["changes"]:
        li.append('<li><b>Changes are counted separately</b>The first entry for a contract is the award. Later changes (more money, less money, more time) are shown on their own'
                  + (' and are never counted in award totals. ' + ('On the trade pages and in the CSVs, money taken out shows as a negative amount.' if hub else 'Money taken out shows as a negative amount.') + '</li>' if f["neg"] else ' and are never counted in award totals.</li>'))
    li.append('<li><b>End dates are mostly on blanket contracts</b>The City records end dates mostly on blanket contracts (repeat purchases). Many standard contracts, such as most construction, end when the work is accepted, so they do not show as ending.</li>')
    li.append('<li><b>Sorted by the contract\'s own words</b>A contract joins a trade when its description uses that trade\'s words. One contract can count in two trades, and work described in other words is missed.</li>')
    return '<ul class="cc-read">' + "".join(li) + '</ul>'


def trade_map(E, d, data_mod):
    rows = []
    for t in data_mod.TRADES:
        rows.append(f'<tr><th scope="row">{E(t["name"])}</th>{td(E("; ".join(t["words"])), "Words")}</tr>')
    return (table("The words that put a contract in each trade", [("Trade", False), ("A contract joins when its description uses", False)], rows, cls=" cc-map")
            + '<details class="cc-more cc-fine"><summary>What every trade leaves out</summary><p class="asof">Matching ignores capital letters, and most words also find their longer forms (roof finds roofing). Left out of every trade: anything the City buys rather than hires, meaning a contract described as a purchase, and lists of supplies, parts, products or vehicles '
            'that name no work such as service, repair, maintenance or removal; upkeep of the City\'s own machines and fleet; design, engineering and consulting; '
            'software; art; grants to agencies; leases; redevelopment deals; deals with other public bodies, such as the Board of Education and other intergovernmental agreements; '
            'and airport terminal projects the City pays airlines or airline groups to run (the vendor is the airline). A few more words keep look-alikes out (rock salt from snow removal, lead paint removal from painting, '
            'elevators from HVAC, holiday trees and tree inventories from landscaping). Contracts only for inspection or construction supervision are left out too.</p></details>')


def footer(E, M, rel, d, trades=None):
    s = d["source"]
    wh_clause = "; a name that does not read as a business shows as Name withheld" if flags(trades or d["trades"])["withheld"] else ""
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: City of Chicago Data Portal, <a href="{E(s["url"])}">Contracts dataset ({E(s["dataset"])})</a>, contracts the City has awarded since 1993 and the changes to them, '
            f'last updated by the City {E(M.nice_date(s["rowsUpdatedAt"]))}, read by us {E(M.nice_date(s["fetchedAt"]))}. We keep the awards and changes approved in the last 36 months and the contracts ending in the next 12, '
            f'sort them into trades by the words in their descriptions, and drop every vendor address. Vendor names are business names as the City lists them{wh_clause}. </p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p><p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago.</p>'
            '<p>Public information, not legal, tax or financial advice. Before you bid, check the solicitation and its rules with the City\'s Department of Procurement Services.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n</body></html>')


def head(M, E, p, url, rel, title, desc, ld, robots):
    return M.HEAD.format(title=E(title), desc=E(desc), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS + SR, bodycls=' class="ld-page"',
                         robots=robots, analytics=M.analytics_tag())


def summary(d):
    """Citywide numbers with each contract counted once, though a contract can sit in two trades."""
    T, w = d["trades"], d["window"]
    new = {}
    for t in T:
        for r in t["rows"]:
            if r[1] == 0:
                new[r[9] or id(r)] = r
    n12 = [r for r in new.values() if r[0] >= w["from12"]]
    return {"awards12": len(n12), "total12": round(sum(r[5] for r in n12 if r[5] > 0), 2),
            "awards36": len(new), "ending": len({e["contract"] for t in T for e in t["ending"]})}


def wh(rows):
    """The note under a table that shows a withheld vendor name."""
    if any((r.get("vendor") if isinstance(r, dict) else None) == "Name withheld" for r in rows):
        return ' Name withheld: the City lists a vendor name that does not read as a business, so we do not show it.'
    return ""


def mods_sentence(a):
    """How many changes, leaving out any part that is zero."""
    parts = []
    if a["modsUp"]:
        parts.append(f'{a["modsUp"]:,} added {usd(a["modsUpTotal"])}')
    if a["modsDown"]:
        parts.append(f'{a["modsDown"]:,} took out {usd(-a["modsDownTotal"])}')
    if a["modsZero"]:
        parts.append(f'{a["modsZero"]:,} changed no money (often more time)')
    n = a["mods"]
    if len(parts) == 1 and not a["modsUp"] and not a["modsDown"]:
        return f'{plural(n, "change")} in 36 months, ' + ("with no money change (often more time)." if n == 1 else
                                                         ("both" if n == 2 else "all") + " with no money change (often more time).")
    body = parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + " and " + parts[-1]
    return f'{plural(n, "change")} in 36 months: {body}.'


def short(t, n=60):
    """A description cut at a word boundary for screen-reader labels."""
    return t if len(t) <= n else t[:n].rsplit(" ", 1)[0].rstrip(",;:-(") 


GLOSS = {"BID": "Bid means a competitive bid", "RFP": "RFP is a request for proposals", "RFQ": "RFQ is a request for qualifications",
         "SOLE SOURCE": "Sole source means one supplier was picked without a bid", "EMERGENCY": "Emergency means bought fast for an emergency",
         "": "Not stated means the City left it blank", "Not stated": "Not stated means the City left it blank"}


def proc_note(groups):
    """Explain only the procurement types this table shows."""
    seen = [GLOSS[g["name"]] for g in groups if g["name"] in GLOSS]
    seen = list(dict.fromkeys(seen))
    return "How bought is the City's procurement type." + (" " + "; ".join(seen) + "." if seen else "")


def low(t):
    """The trade name inside a sentence: lower case, but HVAC stays HVAC."""
    return t["name"] if t["key"] == "hvac" else t["name"].lower()


def page_html(p):
    import make_site as M
    import dp_contracts_data as DD
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d, src = load(p)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faqs = [q for q in p["faq"] if (d and flags(d["trades"])["zero"]) or "$0" not in q[0]]
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}
    if not d:
        return (head(M, E, p, url, rel, p["title"], p["desc"], M.ld_tags(crumb_ld), '<meta name="robots" content="noindex, nofollow">')
                + f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first daily pull is on its way.</p></div></main></body></html>')
    s, w, T = d["source"], d["window"], d["trades"]
    S = summary(d)
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": p["h1"], "url": url, "description": p["desc"],
          "isBasedOn": s["url"], "creator": {"@type": "Organization", "name": "ProofNotFluff"},
          "temporalCoverage": f'{w["from36"]}/{w["today"]}', "dateModified": s["fetchedAt"][:10],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": f'{url}{t["key"]}/{csv_name(t)}'} for t in T]}
    lede = (f'The City of Chicago publishes the contracts it awards. We sort the last 36 months into {len(T)} trades, so you can see who wins City work in yours, '
            f'what it was worth, and which contracts end in the next 12 months and may go back out to bid.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Ending in 12 months</div><div class="val">{S["ending"]:,}</div><div class="sub">contracts in these trades; the work may go back out to bid</div></div>'
             f'<div class="tile"><div class="lab">New awards, 12 months</div><div class="val">{S["awards12"]:,}</div><div class="sub">{E(usd_short(S["total12"]))} in all</div></div>'
             f'<div class="tile"><div class="lab">New awards, 36 months</div><div class="val">{S["awards36"]:,}</div><div class="sub">since {E(M.nice_date(w["from36"]))}</div></div>'
             f'<div class="tile"><div class="lab">City data as of</div><div class="val">{E(M.nice_date(s["rowsUpdatedAt"]).rsplit(",", 1)[0])}</div><div class="sub">refreshed here every morning</div></div>'
             '</div>'
             f'<p class="asof">New awards approved from {E(M.nice_date(w["from36"]))} to {E(M.nice_date(w["today"]))}, from the City\'s Contracts dataset. '
             'Each contract counts once here; a contract that names two trades counts in both trades, so the trade cards add up to more.</p>')
    nw = lambda x: f'<span class="nw">{x}</span>'
    card = lambda t: (
        f'<li><a href="{E(t["key"])}/"><b>{E(t["name"])}<span aria-hidden="true">&rarr;</span></b>'
        f'<small class="cc-end{" z" if not t["ending"] else ""}">{nw(plural(len(t["ending"]), "contract"))} ending in 12 months</small>'
        + (f'<small>{nw(plural(t["m36"]["awards"], "new award"))} in 36 months'
           + (f', {nw(E(usd_short(t["m36"]["total"])))}' if t["m36"]["total"] else "") + '</small>' if t["m36"]["awards"] else
           (f'<small>No new award in 36 months; {nw(plural(t["m36"]["mods"], "change"))} to older contracts</small>' if t["m36"]["mods"] else '<small>No new award or change in 36 months</small>')) + '</a></li>')
    by = {t["key"]: t for t in T}
    cards = "".join(f'<h3 class="cc-grp">{E(g)}</h3><ul class="cc-pick">{"".join(card(by[k]) for k in ks if k in by)}</ul>' for g, ks in GROUPS)
    rows = []
    order = [k for _, ks in GROUPS for k in ks]
    for t in sorted(T, key=lambda x: order.index(x["key"]) if x["key"] in order else 99):
        a, b = t["m12"], t["m36"]
        none = '<span class="cc-none">No award</span>'
        rows.append(f'<tr><th scope="row"><a href="{E(t["key"])}/">{E(t["name"])}</a></th>'
                    + td(f'{len(t["ending"]):,}', "Ending, 12 mo", True)
                    + td(f'{a["awards"]:,}', "New awards, 12 mo", True) + td(E(usd(a["total"])) if a["total"] else none, "Total, 12 mo", True)
                    + td(f'{b["awards"]:,}', "New awards, 36 mo", True) + td(E(usd(b["total"])) if b["total"] else none, "Total, 36 mo", True)
                    + td(E(usd(b["median"])) if b["median"] else none, "Median award", True) + '</tr>')
    summ = table("City contract awards by trade", [("Trade", False), ("Ending<br>12 mo", True), ("New awards<br>12 mo", True), ("Total<br>12 mo", True),
                                                   ("New awards<br>36 mo", True), ("Total<br>36 mo", True), ("Median award<br>36 mo", True)], rows, cls=" cc-sum")
    ending = sorted({e["contract"]: (e, t) for t in T for e in t["ending"]}.values(), key=lambda x: (x[0]["end"], -x[0]["value"]))
    names = {}
    for t in T:
        for e in t["ending"]:
            names.setdefault(e["contract"], []).append(t["short"])
    erows = [f'<tr>{td(E(M.nice_date(e["end"])), "Ends", cls="dt")}'
             f'<td class="d" data-l="Covers">{E(clean(e["description"]))}<span class="cc-sub">{E(", ".join(names[e["contract"]]))} · {dept(E, e["department"])}</span></td>'
             + td(E(e["vendor"]), "Vendor") + td(value_cell(E, e), "Value so far", True) + td(pdf_link(E, e["pdf"], "contract " + e["contract"]), "Contract") + '</tr>'
             for e, t in ending[:12]]
    ehead = [("Ends", False), ("What it covers", False), ("Vendor", False), ("Value so far", True), ("Contract", False)]
    FIRST = 5
    end_html = (table("City contracts in these trades ending soonest", ehead, erows[:FIRST])
                + (f'<details class="cc-more"><summary>Show {len(erows) - FIRST} more contracts ending soon</summary>'
                   + table("More City contracts in these trades ending soon", ehead, erows[FIRST:]) + '</details>' if len(erows) > FIRST else "")
                + (f'<p class="asof">The {min(12, len(ending))} that end soonest of the {plural(len(ending), "contract")} ending in the next 12 months. Every one is on its trade\'s page and in its CSV. '
                   'Value so far adds up the award and every change since.</p>') if ending else '<p class="cc-empty">No contract in these trades has an end date in the next 12 months.</p>')
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(lede)}</p>'
            '<div class="ld-heroact cc-act cc-hact"><a class="btn" href="#trades">Pick your trade</a><a class="st-btn2" href="#bids">Where open bids are</a></div></div>'
            f'{tiles}'
            + otp([("trades", "Trades"), ("ending", "Ending soon"), ("all", "All trades"), ("bids", "Open bids"), ("faq", "Questions")])
            + f'<section class="block" id="trades"><h2>Pick your trade</h2><p>Each trade has its own page with every award, change and ending contract, and a CSV to download.</p>{cards}</section>'
            f'<section class="block" id="ending"><h2>Contracts ending soonest</h2><p>When a City contract ends, the City may bid the work again. These end next.</p>{end_html}</section>'
            f'<section class="block" id="all"><h2>Every trade at a glance</h2><details class="cc-sumd" open><summary>Compare all 12 trades side by side</summary>{summ}</details><p class="asof">Totals and medians use new awards only. Changes to contracts are on each trade\'s page.</p></section>'
            f'<section class="block" id="bids"><h2>Where open bids are</h2><p>This page shows awards. Open City bids live on the City\'s own lists.</p>{bids_block(E, M, src)}</section>'
            f'<section class="block" id="read"><h2>How to read these numbers</h2>{reading_notes(flags(T), hub=True)}</section>'
            f'<section class="block" id="map"><h2>The trade map</h2><p>How a contract is placed in a trade, word for word.</p>{trade_map(E, d, DD)}</section>'
            '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + '</section>'
            f'<div id="faq">{M.faq_block(faqs)}</div>'
            '<div class="cc-act"><a class="btn" href="#trades">Pick your trade</a><a class="st-btn2" href="' + E(FALLBACK["eproc"]) + '" rel="noopener">See open City bids</a></div>')
    return head(M, E, p, url, rel, p["title"], p["desc"], M.ld_tags(crumb_ld, faq_ld, ds), robots) + body + footer(E, M, rel, d)


def csv_name(t):
    return f"chicago-city-contracts-{t['key']}.csv"


CSV_COLS = ["record", "approval_date", "end_date", "description", "department", "vendor", "amount_usd", "contract_type",
            "procurement_type", "specification_number", "contract_number", "revision_number", "contract_pdf"]


def safe(v):
    """No spreadsheet formula can start a text cell (=, +, -, @): such text gets a leading apostrophe."""
    if isinstance(v, str) and re.fullmatch(r"-?\d+(?:\.\d+)?", v):
        return v   # an amount, negative or not, stays a number
    return "'" + v if isinstance(v, str) and v[:1] in ("=", "+", "-", "@") else v


def trade_csv(d, t):
    out = io.StringIO()
    wtr = csv.writer(out, lineterminator="\n")
    wtr.writerow(CSV_COLS)
    for e in t["ending"]:
        wtr.writerow([safe(x) for x in ["ending in the next 12 months (value so far)", e["approved"], e["end"], clean(e["description"]), e["department"], e["vendor"],
                                         f'{e["value"]:.2f}', e["contractType"], e["procurementType"], e["spec"], e["contract"], e["revisions"], e["pdf"]]])
    for r in rows_of(t, d["rowCols"]):
        kind = "new award" if r["revision"] == 0 else ("transfer to a new contract number" if r["revision"] < 0 else "change")
        wtr.writerow([safe(x) for x in [kind, r["approved"], r["end"], clean(r["description"]), r["department"], r["vendor"], f'{r["amount"]:.2f}',
                                         r["contractType"], r["procurementType"], r["spec"], r["contract"], max(r["revision"], 0), r["pdf"]]])
    s = d["source"]
    fl = flags([t])
    wtr.writerow([])
    wtr.writerow([safe(f'Source: City of Chicago Data Portal, Contracts ({s["dataset"]}), {s["url"]}, read {s["fetchedAt"][:10]}. '
                       f'Awards and changes approved {d["window"]["from36"]} to {d["window"]["today"]}, and contracts whose latest end date falls from {d["window"]["today"]} to {d["window"]["endTo"]}, both days included. '
                       + ('An award of 0 on a blanket contract means the City orders as needed and promises no amount. ' if fl["zero"] else '')
                       + ('Negative amounts are changes that took money out. ' if fl["neg"] else '')
                       + ('Award totals are not unit prices. ' if fl["awards"] or fl["changes"] else '') + 'Vendor addresses are not included'
                       + ('; "Name withheld" marks a vendor name that does not read as a business.' if fl["withheld"] else '.'))])
    wtr.writerow([safe(f'Trade words: {"; ".join(next(x for x in __import__("dp_contracts_data").TRADES if x["key"] == t["key"])["words"])}. '
                       'Purchases of goods, fleet upkeep, design and engineering, software, art, grants, leases, redevelopment deals, deals with other public bodies and airline-run airport terminal projects are left out.')])
    import make_site as M
    wtr.writerow([M.CITY_DISCLAIMER["Chicago"]])
    wtr.writerow(["ProofNotFluff is not affiliated with or endorsed by the City of Chicago. Public information, not legal, tax or financial advice. "
                  "Before you bid, check the solicitation and its rules with the City's Department of Procurement Services."])
    return "\ufeff" + out.getvalue()   # a byte-order mark, so Excel reads the City's disclaimer (one\u2019s) word for word


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
    n_end = len(t["ending"])
    first = ((f'{plural(a36["awards"], "new City award")} matched {low(t)}{" work" if t["key"] == "electrical" else ""} in the last 36 months'
              + (f', worth {usd_short(a36["total"])}' + (" in all" if a36["paid"] > 1 else "") if a36["total"] else "")) if a36["awards"] else f'No new City award matched {low(t)} in the last 36 months')
    if not a36["awards"] and not n_end:
        lede = first + ', and no contract in this trade ends in the next 12 months.'
    else:
        lede = first + '. ' + (f'{plural(n_end, "contract")} in this trade {"ends" if n_end == 1 else "end"} in the next 12 months.' if n_end
                               else 'No contract in this trade ends in the next 12 months.')
    na, ne = a36["awards"], len(t["ending"])
    desc = (f'City of Chicago contracts for {low(t)}{" work" if t["key"] == "electrical" else ""}: ' + (plural(na, "new award") if na else "no new awards") + ' in 36 months, '
            + (plural(ne, "contract") + " ending" if ne else "none ending") + ' in the next 12 months'
            + (', with vendors and contract PDFs' if na or ne else '') + '. Free, updated daily.')
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile{" key" if t["ending"] else ""}"><div class="lab">Ending in 12 months</div><div class="val">{len(t["ending"]):,}</div><div class="sub">{"the work may go back out to bid" if t["ending"] else "none ends in the next 12 months"}</div></div>'
             f'<div class="tile"><div class="lab">New awards, 12 months</div><div class="val">{a12["awards"]:,}</div><div class="sub">{E(usd_short(a12["total"])) if a12["total"] else "none in 12 months"}'
             + (f', plus {a12["zero"]:,} at $0' if a12["zero"] else "") + '</div></div>'
             f'<div class="tile"><div class="lab">New awards, 36 months</div><div class="val">{a36["awards"]:,}</div><div class="sub">'
             + ((f'{E(usd_short(a36["total"]))}, median {E(usd_short(a36["median"]))}' if a36["paid"] > 1 else E(usd_short(a36["total"]))) if a36["median"] else ("none in 36 months" if not a36["awards"] else "no dollar total")) + '</div></div>'
             f'<div class="tile"><div class="lab">Changes, 36 months</div><div class="val">{a36["mods"]:,}</div><div class="sub">'
             + (f'{E(usd_short(a36["modsUpTotal"]))} added' if a36["modsUpTotal"] else ("none in 36 months" if not a36["mods"] else ("no money change" if not a36["modsDown"] else "no money added")))
             + (f', {E(usd_short(-a36["modsDownTotal"]))} taken out' if a36["modsDownTotal"] else "") + '</div></div></div>'
             f'<p class="asof">City data as of {E(M.nice_date(s["rowsUpdatedAt"]))}.' + ((' Totals and medians use new awards only;' if a36["paid"] > 1 else ' Totals use new awards only;') + ' award totals are not unit prices.' if a36["awards"] else '') + '</p>')
    erows = [f'<tr>{td(E(M.nice_date(e["end"])), "Ends", cls="dt")}'
             f'<td class="d" data-l="Covers">{E(clean(e["description"]))}<span class="cc-sub">{dept(E, e["department"])} · <span class="nw">contract {E(e["contract"])}</span>'
             + (f' · <span class="nw">spec {E(e["spec"])}</span>' if e["spec"] else "") + '</span></td>'
             + td(E(e["vendor"]), "Vendor") + td(value_cell(E, e), "Value so far", True)
             + td(E(M.nice_date(e["approved"])) if e["approved"] else "Not stated", "First approved", cls="dt") + td(pdf_link(E, e["pdf"], "contract " + e["contract"]), "Contract") + '</tr>'
             for e in t["ending"]]
    th_end = [("Ends", False), ("What it covers", False), ("Vendor", False), ("Value so far", True), ("First approved", False), ("Contract", False)]
    end_html = (table(f'{t["name"]} contracts ending in the next 12 months', th_end, erows[:5])
                + (f'<details class="cc-more"><summary>Show the other {len(erows) - 5} ending contracts</summary>'
                   + table(f'More {low(t)} contracts ending in the next 12 months', th_end, erows[5:]) + '</details>' if len(erows) > 5 else "")
                + '<p class="asof">Sorted by the latest end date on the contract, after any time extensions. Value so far adds up the award and every change since. '
                  + (' A $0 value is a contract the City orders from as needed.' if any(e["requirements"] and e["value"] == 0 for e in t["ending"]) else '') + wh(t["ending"]) + '</p>') if erows else (
        f'<p class="cc-empty">No City contract that matched {E(low(t))} has an end date in the next 12 months. Many standard contracts, such as most construction, '
        'end when the work is accepted, so they do not show as ending.</p>')
    SHOW = 25
    nrow = lambda r: (f'<tr>{td(E(M.nice_date(r["approved"])), "Approved", cls="dt")}'
                      f'<td class="d" data-l="Covers">{E(clean(r["description"]))}<span class="cc-sub">{dept(E, r["department"])}</span></td>'
                      + td(E(r["vendor"]), "Vendor") + td(award_cell(r), "Award", True) + td(E(proc(r["procurementType"] or "Not stated")), "How bought")
                      + td(pdf_link(E, r["pdf"], "contract " + r["contract"]), "Contract") + '</tr>')
    nhead = [("Approved", False), ("What it covers", False), ("Vendor", False), ("Award", True), ("How bought", False), ("Contract", False)]
    new_html = (table(f'New {low(t)} awards, newest first', nhead, [nrow(r) for r in new[:SHOW]])
                + (f'<details class="cc-more"><summary>Show the other {plural(len(new) - SHOW, "new award")}</summary>'
                   + table(f'Older new {low(t)} awards', nhead, [nrow(r) for r in new[SHOW:]]) + '</details>' if len(new) > SHOW else "")
                + (f'<p class="asof">{wh(new).strip()}</p>' if wh(new) else "")
                ) if new else f'<p class="cc-empty">No new City award matched {E(low(t))} from {E(M.nice_date(w["from36"]))} to {E(M.nice_date(w["today"]))}.' + (" Changes to older contracts are below." if mods else "") + '</p>'
    mrow = lambda r: (f'<tr>{td(E(M.nice_date(r["approved"])), "Approved", cls="dt")}'
                      f'<td class="d" data-l="Covers">{E(clean(r["description"]))}<span class="cc-sub">{E(r["vendor"])} · <span class="nw">contract {E(r["contract"])}</span></span></td>'
                      + td(("+" + usd(r["amount"])) if r["amount"] > 0 else (usd(r["amount"]) if r["amount"] < 0 else "No money change"), "Change", True)
                      + td(pdf_link(E, r["pdf"], f'the change to contract {r["contract"]} approved {M.nice_date(r["approved"])}'), "Contract") + '</tr>')
    mhead = [("Approved", False), ("Contract changed", False), ("Change", True), ("Contract", False)]
    MSHOW = 10
    mod_html = ((f'<p>{E(mods_sentence(a36))}'
                 + (f' {plural(len(moved), "record")} only moved a contract to a new number and {"is" if len(moved) == 1 else "are"} not counted as new awards.' if moved else "") + '</p>'
                 + table(f'Changes to {low(t)} contracts, newest first', mhead, [mrow(r) for r in mods[:MSHOW]])
                 + (f'<details class="cc-more"><summary>Show the other {"change" if len(mods) - MSHOW == 1 else str(len(mods) - MSHOW) + " changes"}</summary>'
                    + table(f'Older changes to {low(t)} contracts', mhead, [mrow(r) for r in mods[MSHOW:]]) + '</details>' if len(mods) > MSHOW else "")
                 + (f'<p class="asof">{wh(mods).strip()}</p>' if wh(mods) else ""))
                if mods else '<p class="cc-empty">No changes to contracts in this trade in the last 36 months.</p>')
    grp = lambda xs, label, first: table(label, [(first, False), ("New awards", True), ("Total", True)],
                                         [f'<tr><th scope="row">{E(proc(x["name"])) if first == "How bought" else dept(E, x["name"])}</th>'
                                          + td(f'{x["n"]:,}' + (f' <span class="cc-sub">{x["zero"]:,} at $0</span>' if x["zero"] else ""), "New awards", True)
                                          + td(E(usd(x["total"])) if x["total"] else "None", "Total", True) + '</tr>' for x in xs])
    lo = low(t)
    who = ((f'<div class="cc-two"><div><h3>Which departments buy it</h3>{grp(t["byDept"], "New " + lo + " awards by City department", "Department")}</div>'
            f'<div><h3>How the City bought it</h3>{grp(t["byProc"], "New " + lo + " awards by procurement type", "How bought")}</div></div>'
            + f'<p class="asof">{E(proc_note(t["byProc"]))}</p>')
           if new else "")
    vend = (table(f'Vendors with the most new {low(t)} award dollars', [("Vendor", False), ("New awards", True), ("Total", True)],
                  [f'<tr><th scope="row">{E(v["name"])}</th>' + td(f'{v["n"]:,}', "New awards", True) + td(E(usd(v["total"])), "Total", True) + '</tr>' for v in t["topVendors"]])
            + '<p class="asof">Ranked by the dollar total of new awards in 36 months. Business names as the City lists them; one firm can appear under more than one spelling.'
            + (' A vendor shown as Name withheld is left out of this ranking.' if any(r["vendor"] == "Name withheld" for r in new) else "") + '</p>'
            ) if t["topVendors"] else '<p class="cc-empty">No vendor won a new award in this trade in the last 36 months.</p>'
    others = "".join(f'<li><a href="../{E(x["key"])}/"{" aria-current=page" if x["key"] == t["key"] else ""}>{E(x["short"])}</a></li>' for x in d["trades"])
    words = "; ".join(t["words"])
    ds = {"@context": "https://schema.org", "@type": "Dataset", "name": h1, "url": url, "description": desc, "isBasedOn": s["url"],
          "creator": {"@type": "Organization", "name": "ProofNotFluff"}, "dateModified": s["fetchedAt"][:10],
          "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + csv_name(t)}]}
    empty = not new and not mods and not t["ending"]
    zero_html = (f'<section class="block" id="none"><h2>No {E(low(t))} contracts in 36 months</h2><p class="cc-empty">No City contract matched {E(low(t))} from '
                 f'{E(M.nice_date(w["from36"]))} to {E(M.nice_date(w["today"]))}, and none ends in the next 12 months. Many standard contracts, such as most construction, '
                 'end when the work is accepted, so they do not show as ending.</p>'
                 f'<p>Check another trade:</p><ul class="cc-chips">{others}</ul></section>')
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow"><span class="cc-pre">Free tracker of City awards · </span><span class="nw">{E(t["short"])}</span></p><h1>{E(h1)}</h1><p class="lede">{E(lede)}</p>'
            + (f'<div class="ld-heroact cc-act cc-hact"><a class="btn" href="#ending">See ending contracts</a><a class="st-btn2" href="{E(csv_name(t))}" download>Download the CSV</a></div></div>'
               if t["ending"] else f'<div class="ld-heroact cc-act cc-hact"><a class="btn" href="#bids">See open City bids</a><a class="st-btn2" href="{E(csv_name(t))}" download>Download the CSV</a></div></div>')
            + f'{tiles}'
            + (zero_html if empty else otp([("ending", "Ending"), ("new", "New awards"), ("vendors", "Who wins"), ("changes", "Changes"), ("bids", "Open bids")])
            + f'<section class="block" id="ending"><h2>Contracts ending in the next 12 months</h2>' + (('<p>When this contract ends, the City may bid the work again. Watch the City\'s bid lists in case it is bid again.</p>' if len(t["ending"]) == 1 else '<p>When these end, the City may bid the work again. Watch the City\'s bid lists for any rebid.</p>') if t["ending"] else '') + f'{end_html}</section>'
            f'<section class="block" id="new"><h2>New awards, last 36 months</h2>{new_html}</section>'
            + (f'<section class="block" id="who"><h2>Who buys it, and how</h2>{who}</section>' if who else "")
            + f'<section class="block" id="vendors"><h2>Who wins it</h2>{vend}</section>'
            f'<section class="block" id="changes"><h2>Changes to contracts</h2>{mod_html}</section>')
            + f'<section class="block" id="bids"><h2>Where open bids are</h2>{bids_block(E, M, src)}</section>'
            f'<section class="block" id="words"><h2>What counts as {E(low(t))}</h2><p>A City contract joins this trade when its description uses any of these words: {E(words)}. '
            f'Purchases of goods, fleet upkeep, design and engineering, software, art, grants, leases, redevelopment deals, deals with other public bodies and airline-run airport terminal projects are left out. <a href="../#map">See the whole trade map</a>.</p>'
            f'{reading_notes(flags([t]))}</section>'
            + ("" if empty else f'<section class="block"><h2>All 12 trades</h2><ul class="cc-chips">{others}</ul></section>')
            + (f'<div class="cc-act"><a class="btn" href="{E(FALLBACK["eproc"])}" rel="noopener">See open City bids</a><a class="st-btn2" href="../">All trades</a></div>' if empty else
               f'<div class="cc-act"><a class="btn" href="{E(csv_name(t))}" download>Download the {E("HVAC" if t["key"] == "hvac" else t["short"].lower())} CSV</a><a class="st-btn2" href="../">All trades</a></div>'))
    return head(M, E, p, url, rel, f'{h1} | ProofNotFluff', desc, M.ld_tags(crumb_ld, ds), robots) + body + footer(E, M, rel, d, [t])


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
        sp = dict(spec, draft=True, data=os.path.relpath(os.path.join(tmp, "contracts.json"), ROOT))
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
    assert ",-2000.00," in csvt, "a negative amount stays a number in the CSV"
    assert "\n'=HYPERLINK" not in csvt and ",'=HYPERLINK" in csvt, "no formula can start a CSV cell"
    assert len(extras) == 2 * len(DD.TRADES), "a page and a CSV per trade"
    assert isinstance(META["keywords"], str), "make_site's search index reads keywords as one string"
    assert 'role="region"' in sub and 'tabindex="0"' in sub, "scrollable tables reachable by keyboard"
    assert page_html(dict(spec, data="site/datapages/dp_contracts/none.json")).count("noindex") == 1, "no data: an unindexed shell"
    print("dp_contracts selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
