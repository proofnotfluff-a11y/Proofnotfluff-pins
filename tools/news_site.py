#!/usr/bin/env python3
"""Chicago Trades News: the free weekly brief (site/pages.json kind "tradesnews", written by tools/make_site.py, which
calls page_html here). Todd, live chat, Oct 27, 2026: "Trades News - start with Chicago. This could be any major news
impacting the trades in Chicago. New regulations, news events, tax related news, etc. Anything that would be useful to
workers in the trades."

Data: site/news/chicago-trades.json, written by the daily trades-news run (.claude/skills/trades-news/SKILL.md). Each
item is our own plain words about one change, with the page that says so linked. check() below is the code gate: it
stops the build (make_site.py, and so the repo's site-sync check) on a missing source, a dash, an unknown trade or
category, a headline or summary over its length, or a date that is not a date. Nothing on the page is copied from a
news story; facts come from the linked pages and were read in the run that wrote them (CONSTITUTION 2, VERIFY BEFORE
POSTING).

Also writes docs/<slug>/feed.xml (RSS 2.0), so a reader can follow the brief without an email signup.

Usage: python3 tools/news_site.py --check [file]   validate a data file
       python3 tools/news_site.py --selftest       planted good and bad items
"""
import datetime as dt, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "news", "chicago-trades.json")

CATEGORIES = ["Rules and permits", "Licensing", "Safety", "Tax and pay", "Jobs and projects"]
TRADES = ["All trades", "General contractors", "Electrical", "Plumbing", "HVAC", "Roofing", "Painting", "Cleaning",
          "Pest control", "Landscaping and snow", "Restaurant service trades"]
STAGES = {"proposed": "Proposed", "passed": "Passed", "in effect": "In effect", "announced": "Announced",
          "under way": "Under way", "open": "Open now", "final rule": "Final rule"}
KEEP_DAYS = 120          # items older than this (by news date) and already in effect leave the page
LIMITS = {"headline": 90, "what": 420, "why": 330}
DASHES = ("—", "–")


def load(p=None):
    f = os.path.join(ROOT, (p or {}).get("data", "site/news/chicago-trades.json"))
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def _date(s):
    return dt.date.fromisoformat(s) if isinstance(s, str) and len(s) == 10 else None


def check(d):
    """A list of problems; empty means the file may be built and published."""
    bad = []
    if not _date(d.get("updated")):
        bad.append("updated: not a YYYY-MM-DD date")
    ids = set()
    for i, it in enumerate(d.get("items") or []):
        at = f"item {i + 1} ({it.get('id', '?')})"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", it.get("id") or ""):
            bad.append(f"{at}: id must be lowercase words joined by hyphens")
        if it.get("id") in ids:
            bad.append(f"{at}: duplicate id")
        ids.add(it.get("id"))
        for k, n in LIMITS.items():
            v = it.get(k) or ""
            if not v.strip():
                bad.append(f"{at}: {k} is empty")
            elif len(v) > n:
                bad.append(f"{at}: {k} is {len(v)} characters, over {n}")
        for k in ("headline", "what", "why"):
            if any(c in (it.get(k) or "") for c in DASHES):
                bad.append(f"{at}: {k} has an em or en dash")
            if "“" in (it.get(k) or "") or '"' in (it.get(k) or ""):
                bad.append(f"{at}: {k} has a quotation; write it in our own words")
        if not _date(it.get("date")):
            bad.append(f"{at}: date is not YYYY-MM-DD")
        if it.get("effective") is not None and not _date(it.get("effective")):
            bad.append(f"{at}: effective is not YYYY-MM-DD or null")
        if not _date(it.get("checked")):
            bad.append(f"{at}: checked (the day every fact was read on its source) is missing")
        if it.get("stage") not in STAGES:
            bad.append(f"{at}: stage {it.get('stage')!r} not one of {sorted(STAGES)}")
        if it.get("category") not in CATEGORIES:
            bad.append(f"{at}: category {it.get('category')!r}")
        tr = it.get("trades") or []
        if not tr or any(t not in TRADES for t in tr):
            bad.append(f"{at}: trades {tr!r}")
        if it.get("link") is not None and not (re.fullmatch(r"[a-z0-9-]+", str((it["link"] or {}).get("slug", ""))) and (it["link"] or {}).get("text")):
            bad.append(f"{at}: link needs text and a site slug")
        src = it.get("sources") or []
        if not src:
            bad.append(f"{at}: no source")
        for s in src:
            if not (s.get("name") or "").strip() or not str(s.get("url") or "").startswith("https://"):
                bad.append(f"{at}: a source needs a name and an https link")
            if any(c in (s.get("name") or "") for c in DASHES):
                bad.append(f"{at}: source name has a dash")
    return bad


def shown(d, today):
    """Items on the page, newest news first: everything within KEEP_DAYS, plus older items whose date is still ahead."""
    out = []
    for it in d.get("items") or []:
        age = (today - _date(it["date"])).days
        eff = _date(it.get("effective"))
        if age <= KEEP_DAYS or (eff and eff >= today):
            out.append(it)
    return sorted(out, key=lambda x: (x["date"], x["id"]), reverse=True)


def nice(iso):
    d = _date(iso)
    return f"{d:%b} {d.day}, {d.year}" if d else ""


def stage_text(it, today):
    eff = _date(it.get("effective"))
    st = it["stage"]
    if eff and st in ("passed", "in effect", "final rule", "announced"):
        return ("Starts " if eff > today else "In effect since ") + nice(it["effective"])
    if eff and st == "open":
        return "Open until " + nice(it["effective"]) if eff >= today else "Closed " + nice(it["effective"])
    if eff and st == "proposed":
        return "Proposed, would start " + nice(it["effective"])
    return STAGES[st]


def slug_t(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")


CSS = ("<style>"
       ".tn-bar{position:sticky;top:var(--hdr-h,64px);z-index:5;display:grid;gap:10px;margin:8px 0 14px;padding:12px 14px;background:var(--card);border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow-soft)}"
       "@media(min-width:760px){.tn-bar{grid-template-columns:minmax(220px,300px) 1fr;align-items:end}}"
       ".tn-bar label{display:grid;gap:6px;font-size:13px;font-weight:700;color:var(--muted)}"
       ".tn-bar select{min-height:44px;font:inherit;font-size:15px;font-weight:600;line-height:1.2;color:var(--ink);background:var(--card) var(--sel-arrow) no-repeat right 14px center;border:1px solid var(--line);border-radius:10px;padding:0 38px 0 12px;appearance:none;-webkit-appearance:none}"
       ".tn-chips{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;border:0;min-width:0}.tn-chips legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px;padding:0}"
       ".tn-chips button{min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--ink2);font:inherit;font-size:14.5px;font-weight:600;cursor:pointer}"
       ".tn-chips button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".tn-count{margin:0 0 10px;color:var(--muted);font-size:14px}"
       ".tn-list{display:grid;gap:14px}"
       ".tn-item{padding:18px 20px;background:var(--card);border:1px solid var(--line);border-radius:14px;scroll-margin-top:150px}"
       ".tn-item:target{outline:3px solid var(--focus);outline-offset:2px}"
       ".tn-top{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;margin:0 0 8px;font-size:13px;color:var(--muted)}"
       ".tn-cat{display:inline-flex;align-items:center;min-height:26px;padding:0 10px;border-radius:999px;background:var(--teal-tint);color:var(--teal-ink);font-weight:700}"
       ".tn-st{display:inline-flex;align-items:center;min-height:26px;padding:0 10px;border-radius:999px;border:1px solid var(--line);color:var(--ink);font-weight:700}"
       ".tn-st.soon{background:var(--warn-tint);border-color:transparent;color:var(--warn-ink)}"
       ".tn-item h4{max-width:72ch;font-family:Poppins,system-ui,-apple-system,'Segoe UI',Roboto,Arial,sans-serif;font-weight:700;letter-spacing:-.01em;margin:0 0 8px;font-size:clamp(18px,2.4vw,21px);line-height:1.3;color:var(--ink);text-wrap:balance}"
       ".tn-item p{margin:0 0 8px;color:var(--ink2);max-width:72ch}.tn-item .tn-why{color:var(--ink)}.tn-item .tn-why b{color:var(--ink)}"
       ".tn-for{margin:10px 0 0;font-size:14px;color:var(--muted)}.tn-for b{color:var(--ink2);font-weight:600}.tn-more{margin:4px 0 0}.tn-more a{font-weight:700;color:var(--ink)}"
       ".tn-src{display:grid;grid-template-columns:auto 1fr;gap:4px 10px;align-items:baseline;margin:12px 0 0;padding-top:10px;border-top:1px solid var(--rule);font-size:14px;color:var(--muted)}"
       ".tn-src>span+span{display:flex;flex-wrap:wrap;gap:2px 14px}.tn-src a{display:inline-flex;align-items:center;min-height:28px;color:var(--ink);font-weight:600}"
       "@media(max-width:759px){main .tn-src a{padding:8px 0;min-height:0}.tn-src>span+span{row-gap:0}}"
       "@media(max-width:599px){.tn-top .tn-copy{width:44px;padding:0;justify-content:center}.tn-top .tn-copy .tn-ct{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}"
       ".ld-page .cta .ld-buybtn{display:flex;flex-wrap:wrap;gap:12px;margin-top:16px}"
       ".tn-copy{margin-left:auto;display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:0 12px;border:1px solid var(--line);border-radius:10px;background:transparent;color:var(--ink2);font:inherit;font-size:13px;font-weight:600;cursor:pointer}.tn-copy svg{width:16px;height:16px}"
       ".tn-st.new{background:var(--accent);border-color:var(--accent);color:#fff}"
       ".tn-group{margin:22px 0 10px;font-size:19px}.tn-group small{font:inherit;font-size:14px;font-weight:600;color:var(--muted);margin-left:6px}"
       ".ld-page .ld-tiles{margin-top:24px}.ld-heroact .st-btn2{min-height:52px}"
       ".cta .st-btn2{border-color:rgba(255,255,255,.7);color:#fff}.cta .st-btn2:hover{background:#fff;color:var(--band)}"
       ".tn-soon{display:grid;gap:0;margin:8px 0 0;padding:0;list-style:none;border:1px solid var(--line);border-radius:12px;background:var(--card);overflow:hidden}"
       "section.block .tn-soon li{max-width:none}.tn-soon li{display:grid;grid-template-columns:118px 1fr;gap:12px;align-items:center;padding:12px 16px;border-bottom:1px solid var(--rule)}.tn-soon li:last-child{border-bottom:0}"
       ".tn-soon time{font-weight:700;color:var(--ink);font-variant-numeric:tabular-nums}.tn-soon a{color:var(--ink);font-weight:600;display:inline-block;padding:6px 0;text-underline-offset:3px;text-decoration-color:color-mix(in srgb,currentColor 35%,transparent)}.tn-soon a:hover{text-decoration-color:currentColor}"
       ".tn-soon small{display:block;color:var(--muted);font-size:13px}"
       ".tn-empty{padding:18px;border:1px dashed var(--dash);border-radius:12px;color:var(--ink2)}"
       "@media(max-width:599px){.tn-item{padding:16px}.tn-soon li{grid-template-columns:1fr;gap:2px}.tn-bar{position:static}}"
       "</style>")


COPY_ICO = ('<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">'
            '<path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>')


def item_html(it, today, E, new=False, rel="../"):
    eff = _date(it.get("effective"))
    soon = bool(eff and 0 <= (eff - today).days <= 75)
    src = "".join(f'<a href="{E(s["url"])}" rel="noopener">{E(s["name"])}</a>' for s in it["sources"])
    data_tr = "|".join(it["trades"])
    return (f'<article class="tn-item" id="{E(it["id"])}" data-cat="{E(it["category"])}" data-trades="{E(data_tr)}" aria-labelledby="h-{E(it["id"])}">'
            '<div class="tn-top">' + ('<span class="tn-st new">New</span>' if new else "") + f'<span class="tn-cat">{E(it["category"])}</span><span class="tn-st{" soon" if soon else ""}">{E(stage_text(it, today))}</span>'
            + f'<span>Reported <time datetime="{E(it["date"])}">{E(nice(it["date"]))}</time></span>'
            f'<button class="tn-copy" type="button" data-copy="{E(it["id"])}" hidden aria-label="Copy link to this item">{COPY_ICO}<span class="tn-ct">Copy link</span></button></div>'
            f'<h4 id="h-{E(it["id"])}">{E(it["headline"])}</h4><p>{E(it["what"])}</p>'
            f'<p class="tn-why"><b>What it means for you:</b> {E(it["why"])}</p>'
            + (f'<p class="tn-more"><a href="{rel}{E(it["link"]["slug"])}/">{E(it["link"]["text"])}</a></p>' if it.get("link") else "")
            + f'<p class="tn-for"><b>For:</b> {E(", ".join(it["trades"]))}</p>'
            f'<p class="tn-src"><span>Source{"s" if len(it["sources"]) > 1 else ""}:</span><span>{src}</span></p></article>')


JS = r"""<script>(function(){var R=document.getElementById("tn");if(!R)return;var items=[].slice.call(R.querySelectorAll(".tn-item")),sel=document.getElementById("tn-trade"),
cnt=document.getElementById("tn-count"),cat="",bar=document.getElementById("tn-bar"),empty=document.getElementById("tn-empty");bar.hidden=false;
function run(){var t=sel.value,n=0;items.forEach(function(a){var tr=a.dataset.trades.split("|");var ok=(!t||tr.indexOf(t)>=0||tr.indexOf("All trades")>=0)&&(!cat||a.dataset.cat===cat);a.hidden=!ok;if(ok)n++;});
R.querySelectorAll(".tn-list").forEach(function(l){var h=l.previousElementSibling,v=[].filter.call(l.children,function(a){return !a.hidden;}).length;l.hidden=!v;if(h&&h.classList.contains("tn-group")){h.hidden=!v;h.querySelector("small").textContent=v;}});
cnt.textContent=n===items.length?"Showing all "+n+" items":"Showing "+n+" of "+items.length+" items";empty.hidden=n>0;
try{var u=new URL(location.href);t?u.searchParams.set("trade",t):u.searchParams.delete("trade");history.replaceState(null,"",u.pathname+u.search+u.hash);localStorage.setItem("pnf-tn-trade",t);}catch(e){}}
var q="";try{q=new URL(location.href).searchParams.get("trade")||localStorage.getItem("pnf-tn-trade")||"";}catch(e){}
if(q&&[].some.call(sel.options,function(o){return o.value===q;}))sel.value=q;
sel.addEventListener("change",run);
R.querySelectorAll(".tn-chips button").forEach(function(b){b.addEventListener("click",function(){cat=b.dataset.cat;R.querySelectorAll(".tn-chips button").forEach(function(x){x.setAttribute("aria-pressed",String(x===b));});run();});});
document.getElementById("tn-clear").addEventListener("click",function(){sel.value="";cat="";R.querySelectorAll(".tn-chips button").forEach(function(x){x.setAttribute("aria-pressed",String(!x.dataset.cat));});run();sel.focus();});
if(navigator.clipboard){R.querySelectorAll(".tn-copy").forEach(function(b){b.hidden=false;b.addEventListener("click",function(){var u=location.origin+location.pathname+"#"+b.dataset.copy;
navigator.clipboard.writeText(u).then(function(){var t=b.querySelector(".tn-ct"),o=t.textContent;t.textContent="Link copied";b.setAttribute("aria-label","Link copied");setTimeout(function(){t.textContent=o;b.setAttribute("aria-label","Copy link to this item");},1800);});});});}
run();})();</script>"""


def page_html(p, today=None):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    if d is None:
        raise SystemExit(f"{p['slug']}: no news file at {p.get('data')}")
    bad = check(d)
    if bad:
        raise SystemExit(f"{p['slug']}: the news file fails its check:\n  " + "\n  ".join(bad))
    today = today or _date(d["updated"])
    items = shown(d, today)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    coll = {"@context": "https://schema.org", "@type": "CollectionPage", "name": p["h1"], "url": url, "dateModified": d["updated"],
            "isAccessibleForFree": True, "publisher": {"@type": "Organization", "name": "ProofNotFluff"},
            "mainEntity": {"@type": "ItemList", "numberOfItems": len(items), "itemListElement": [
                {"@type": "ListItem", "position": i, "url": url + "#" + it["id"], "name": it["headline"]} for i, it in enumerate(items, 1)]}}
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    feed = f'<link rel="alternate" type="application/rss+xml" title="{E(p["h1"])}" href="{url}feed.xml">'
    head = M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(crumb_ld, coll, faq_ld) + CSS + feed,
                         bodycls=' class="ld-page"', robots=robots, analytics=M.analytics_tag())
    ahead = sorted((it for it in items if _date(it.get("effective")) and _date(it["effective"]) >= today and it["stage"] != "proposed"),
                   key=lambda x: (x["effective"], x["id"]))
    n_cat = {c: sum(1 for it in items if it["category"] == c) for c in CATEGORIES}
    nxt = ahead[0] if ahead else None
    week_from = _date(d["updated"]) - dt.timedelta(days=7)
    fresh = [it for it in items if _date(it["date"]) > week_from]
    older = [it for it in items if _date(it["date"]) <= week_from]
    tiles = ('<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">New this week</div><div class="val">{len(fresh)}</div><div class="sub">of {len(items)} items on the page, each with its source</div></div>'
             + (f'<div class="tile"><div class="lab">Next date</div><div class="val rc-name">{E(nice(nxt["effective"]))}</div><div class="sub">{E(nxt["headline"])}</div></div>' if nxt else "")
             + f'<div class="tile"><div class="lab">Tax and pay</div><div class="val">{n_cat["Tax and pay"]}</div><div class="sub">items on what you pay or earn</div></div>'
             f'<div class="tile"><div class="lab">Rules and permits</div><div class="val">{n_cat["Rules and permits"]}</div><div class="sub">items on how you work</div></div>'
             f'</div><p class="asof">As of {E(nice(d["updated"]))}. Checked for new items every morning. Every fact was read on the linked page the day it was written.</p>')
    soon = ""
    if ahead:
        soon = ('<section class="block" id="dates"><h2>Dates coming up</h2><ol class="tn-soon">'
                + "".join(f'<li><time datetime="{E(it["effective"])}">{E(nice(it["effective"]))}</time><span><a href="#{E(it["id"])}">{E(it["headline"])}</a>'
                          f'<small>{E(it["category"])} · {E(", ".join(it["trades"]))}</small></span></li>' for it in ahead[:8])
                + "</ol></section>")
    opts = "".join(f'<option value="{E(t)}">{E(t)}</option>' for t in TRADES[1:])
    chips = ('<button type="button" data-cat="" aria-pressed="true">All</button>'
             + "".join(f'<button type="button" data-cat="{E(c)}" aria-pressed="false">{E(c)}</button>' for c in CATEGORIES if n_cat[c]))
    bar = (f'<div class="tn-bar" id="tn-bar" hidden><label for="tn-trade">Your trade<select id="tn-trade"><option value="">Every trade</option>{opts}</select></label>'
           f'<fieldset class="tn-chips"><legend>Topic</legend>{chips}</fieldset></div>')
    grp = lambda h, xs, new: (f'<h3 class="tn-group">{h} <small>{len(xs)}</small></h3><div class="tn-list">{"".join(item_html(it, today, E, new, rel) for it in xs)}</div>' if xs else "")
    lst = (f'<section class="block" id="tn" aria-labelledby="tn-h"><h2 id="tn-h">The brief</h2>{bar}'
           '<p class="tn-count" id="tn-count" aria-live="polite"></p>'
           + grp("New this week", fresh, True) + grp("Still in play", older, False)
           + '<div class="tn-empty" id="tn-empty" hidden><p>Nothing for that trade and topic this week. Items marked All trades show for everyone.</p>'
           '<button class="st-btn2" type="button" id="tn-clear">Show every item</button></div></section>')
    more = p.get("more") or {}
    cta = (f'<section class="block"><div class="cta ld-cta"><div><h2>{E(more["title"])}</h2><p>{E(more["text"])}</p>'
           f'<p class="ld-buybtn"><a class="btn" href="{rel}{E(more["slug"])}/">{E(more["button"])}</a> '
           f'<a class="st-btn2" href="{url}feed.xml">Follow by RSS</a></p></div></div></section>') if more else ""
    method = '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"]) + "</section>"
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#tn">Read the brief</a>'
            + ('<a class="st-btn2" href="#dates">Dates coming up</a>' if ahead else "") + '</div></div>'
            f'{tiles}{soon}{lst}{method}{M.faq_block(p["faq"])}{cta}')
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            '<p>News in plain words, with the City, State, federal or news page each item comes from linked. Not legal, tax or financial '
            'advice: check the source, and ask your accountant, lawyer or licensing office before you act on any change.</p>'
            '<p>ProofNotFluff is not affiliated with or endorsed by the City of Chicago, the State of Illinois or any agency or company named here.</p>'
            '<p>Made by ProofNotFluff with AI assistance. Every item is checked against its source by a second reviewer before it is published. '
            'The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n' + JS + '</body></html>')
    return head + body + foot


def feed_xml(p, d, today=None):
    import make_site as M
    today = today or _date(d["updated"])
    url = M.BASE + p["slug"] + "/"
    X = lambda s: html.escape(str(s), quote=False)
    rfc = lambda iso: dt.datetime.combine(_date(iso), dt.time(12)).strftime("%a, %d %b %Y %H:%M:%S -0500")
    items = "".join(f'<item><title>{X(it["headline"])}</title><link>{X(url + "#" + it["id"])}</link><guid isPermaLink="false">pnf-tn-{X(it["id"])}</guid>'
                    f'<pubDate>{rfc(it["date"])}</pubDate><category>{X(it["category"])}</category>'
                    f'<description>{X(it["what"] + " What it means for you: " + it["why"] + " Source: " + it["sources"][0]["name"] + ", " + it["sources"][0]["url"])}</description></item>'
                    for it in shown(d, today))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
            f'<title>{X(p["h1"])}</title><link>{X(url)}</link><description>{X(p["desc"])}</description><language>en-us</language>'
            f'<lastBuildDate>{rfc(d["updated"])}</lastBuildDate>{items}</channel></rss>\n')


def _planted():
    good = {"id": "chicago-permit-fee-change", "date": "2026-10-20", "effective": "2027-01-01", "checked": "2026-10-27", "stage": "passed",
            "category": "Rules and permits", "trades": ["General contractors", "Electrical"], "headline": "Planted headline about a permit fee",
            "what": "The City changed a fee. It starts in January.", "why": "Price jobs that start after New Year with the new fee.",
            "sources": [{"name": "City of Chicago, Department of Buildings", "url": "https://www.chicago.gov/example"}]}
    return {"updated": "2026-10-27", "items": [good, dict(good, id="old-and-done", date="2026-03-01", effective="2026-04-01", stage="in effect"),
                                               dict(good, id="old-but-ahead", date="2026-03-01", effective="2027-03-01", category="Tax and pay", trades=["All trades"])]}


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    d = _planted()
    assert check(d) == [], check(d)
    today = dt.date(2026, 10, 27)
    ids = [x["id"] for x in shown(d, today)]
    assert ids == ["chicago-permit-fee-change", "old-but-ahead"], ids          # old and already in effect leaves the page
    assert stage_text(d["items"][0], today) == "Starts Jan 1, 2027" and stage_text(d["items"][1], today) == "In effect since Apr 1, 2026"
    planted = [("id", "Bad Id"), ("headline", "x" * 91), ("what", "A — dash."), ("why", 'He said "copy".'), ("date", "Oct 20"),
               ("stage", "rumor"), ("category", "Gossip"), ("trades", ["Plumbers"]), ("sources", []),
               ("sources", [{"name": "x", "url": "http://insecure"}]), ("checked", None), ("effective", "soon")]
    for k, v in planted:
        bad = check({"updated": "2026-10-27", "items": [dict(d["items"][0], **{k: v})]})
        assert bad, f"planted bad {k} not caught"
    dup = {"updated": "2026-10-27", "items": [d["items"][0], d["items"][0]]}
    assert any("duplicate" in b for b in check(dup)), "duplicate id"
    import tempfile
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "tradesnews"][0]
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, dir=ROOT)
    json.dump(d, tmp); tmp.close()
    try:
        page = page_html(dict(spec, data=os.path.relpath(tmp.name, ROOT)), today)
        rss = feed_xml(spec, d, today)
    finally:
        os.unlink(tmp.name)
    assert page.count("<h1>") == 1 and not any(c in page for c in DASHES), "one h1, no dashes"
    assert 'id="chicago-permit-fee-change"' in page and "old-and-done" not in page and "Dates coming up" in page, "items and dates"
    assert "Not legal, tax or financial advice" in page.replace("Not legal, tax or financial \nadvice", "Not legal, tax or financial advice") or "Not legal, tax or financial" in page
    assert rss.startswith("<?xml") and rss.count("<item>") == 2 and "&#" not in rss.split("<item>")[0], "feed"
    try:
        page_html(dict(spec, data="site/news/none.json"), today)
        raise AssertionError("no file must stop the build")
    except SystemExit:
        pass
    print("news_site selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--check" in sys.argv:
        f = sys.argv[sys.argv.index("--check") + 1] if len(sys.argv) > sys.argv.index("--check") + 1 else DATA
        bad = check(json.load(open(f, encoding="utf-8")))
        print("\n".join(bad) if bad else f"{f}: ok")
        sys.exit(1 if bad else 0)
