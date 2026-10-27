#!/usr/bin/env python3
"""Chicago Trade License Finder: the free data page chicago-trade-licenses (site/pages.json kind "datapage",
module dp_licenses, written by tools/make_site.py). Todd's go, Oct 27, 2026, 12:17 pm ("Let's do them all",
coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md); research_notes/kimi-2026-10-27-r10.md item 5.

Data: site/datapages/dp_licenses/licenses.json, written by hand from each agency's own page in the run that
checked it (every line carries its source and checked date; tools/dp_licenses_check.py validates the file and, in
the dp_licenses GitHub Action, re-reads each source page for the line's figures). No person, no business, no advice:
every answer ends with "check with" the agency and its link.

Page: one section per trade with a trade selector (all sections show without script), the general contractor class
picker (largest single project value plus demolition scope gives the class, fee and insurance), and one sub-page per
trade under /chicago-trade-licenses/<trade>/.

Usage: python3 tools/dp_licenses.py --selftest
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "site", "datapages", "dp_licenses", "licenses.json")

META = {"h1": "Chicago Trade License Finder",
        "card": "What the City and the State require for 12 trades: license, fee, insurance, bond, exam and renewal, each linked to the agency page",
        "keywords": "license licence licensing chicago general contractor class electrical plumbing hvac mechanical refrigeration roofing pest control "
                    "cleaning painting landscaping pesticide junk removal hauling pressure washing surface cleaning snow removal fee insurance bond exam renewal"}

TOPICS = [("city", "City of Chicago"), ("state", "State of Illinois"), ("fee", "Fee"), ("insurance", "Insurance"), ("bond", "Bond"),
          ("exam", "Exam"), ("renewal", "Renewal"), ("carryover", "Suburb licenses"), ("federal", "Federal")]


def load(p=None):
    return json.load(open(DATA, encoding="utf-8")) if os.path.isfile(DATA) else None


def lastmod(p):
    d = load(p)
    return d["checked"] if d else None


def nice(iso):
    import make_site as M
    return M.nice_date(iso)


def money(n):
    return f"${n:,.0f}"


CSS = ("<style>"
       ".lf-pick{display:flex;flex-wrap:wrap;align-items:end;gap:10px 14px;margin:4px 0 8px}"
       ".lf-pick label{display:block;font-weight:700;font-size:15px;margin-bottom:6px;color:var(--ink)}"
       ".lf-sel{-webkit-appearance:none;appearance:none;font:inherit;font-size:16px;font-weight:700;min-height:48px;min-width:min(100%,320px);padding:0 42px 0 14px;"
       "border-radius:10px;border:1px solid var(--input-line);background:var(--input) url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='%23888' stroke-width='3' stroke-linecap='round'%3E%3Cpath d='m6 9 6 6 6-6'/%3E%3C/svg%3E\") no-repeat right 14px center;color:var(--input-ink)}"
       ".lf-sel:focus-visible,.lf-in:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".lf-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,230px),1fr));gap:10px;margin:14px 0 0;padding:0;list-style:none}"
       ".lf-grid a{display:flex;align-items:center;justify-content:space-between;gap:10px;min-height:52px;padding:10px 14px;background:var(--card);border:1px solid var(--line);"
       "border-radius:12px;color:var(--ink);font-weight:600;text-decoration:none}.lf-grid a:hover{border-color:var(--ink2)}"
       ".lf-grid small{display:block;font-weight:400;color:var(--muted);font-size:13px}"
       ".lf-trade{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px;margin:18px 0;scroll-margin-top:12px}"
       ".lf-trade>h2{margin:0 0 4px}.lf-trade>p.lf-sum{margin:0 0 12px;color:var(--ink2);max-width:760px}"
       ".lf-dl{margin:0;display:grid;grid-template-columns:minmax(0,1fr)}"
       ".lf-dl>div{display:grid;grid-template-columns:minmax(0,1fr);gap:2px 18px;padding:12px 0;border-top:1px solid var(--rule)}"
       "@media(min-width:760px){.lf-dl>div{grid-template-columns:170px minmax(0,1fr)}}"
       ".lf-dl dt{font-weight:700;color:var(--ink);font-size:15px}.lf-dl dd{margin:0}"
       ".lf-dl dd p{margin:0 0 4px;color:var(--ink2);max-width:760px}.lf-dl dd p+p.lf-t{margin-top:10px}"
       ".lf-src{font-size:13px;color:var(--muted)}.lf-src a{color:var(--teal)}"
       ".lf-lv{display:inline-block;font-size:11.5px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;color:var(--muted);margin-right:6px}"
       ".lf-check{margin:14px 0 0;padding:12px 14px;border-radius:10px;background:var(--teal-tint);color:var(--teal-ink);font-weight:600;max-width:none}"
       ".lf-check a{color:var(--teal-ink)}"
       ".lf-calc{display:grid;gap:18px;grid-template-columns:minmax(0,1fr);background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:20px}"
       "@media(min-width:880px){.lf-calc{grid-template-columns:minmax(0,1fr) minmax(0,1.1fr)}}"
       ".lf-f{margin:0 0 14px}.lf-f label{display:block;font-weight:700;font-size:15px;color:var(--ink)}.lf-f small{display:block;color:var(--muted);font-size:13px;margin:2px 0 6px}"
       ".lf-dol{position:relative}.lf-dol span{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-weight:700;color:var(--input-ink);pointer-events:none}"
       ".lf-in{width:100%;font:inherit;font-size:17px;font-weight:700;min-height:48px;padding:0 12px 0 26px;border-radius:10px;border:1px solid var(--input-line);background:var(--input);color:var(--input-ink)}"
       ".lf-calc .lf-sel{width:100%}"
       ".lf-out{border-radius:12px;background:var(--canvas2);border:1px solid var(--line);padding:16px}"
       ".lf-out .lab{font-size:11.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}"
       ".lf-cls{font-family:Poppins,system-ui,sans-serif;font-weight:700;font-size:clamp(26px,6vw,38px);line-height:1.1;margin:2px 0 10px;color:var(--ink)}"
       ".lf-kv{display:grid;grid-template-columns:auto minmax(0,1fr);gap:6px 14px;margin:0}.lf-kv dt{color:var(--muted);font-size:14px}.lf-kv dd{margin:0;font-weight:600;color:var(--ink);font-variant-numeric:tabular-nums}"
       ".lf-why{margin:10px 0 0;font-size:14px;color:var(--ink2)}"
       ".lf-tw{overflow-x:auto;margin:14px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".lf-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".lf-t{width:100%;border-collapse:collapse;font-size:14.5px;min-width:560px}.lf-t th,.lf-t td{padding:9px 12px;border-bottom:1px solid var(--rule);text-align:left;vertical-align:top}"
       ".lf-t thead th{font-size:13px;color:var(--muted);font-weight:700}.lf-t tbody th{color:var(--ink)}.lf-t td{color:var(--ink2);font-variant-numeric:tabular-nums}"
       ".lf-t tr:last-child td,.lf-t tr:last-child th{border-bottom:0}.lf-t tr.on th,.lf-t tr.on td{background:var(--teal-tint);color:var(--teal-ink)}"
       ".lf-hide{display:none}"
       "</style>")


def src_line(s, d, E):
    return (f'<p class="lf-src">Source: <a href="{E(s["url"])}" rel="noopener">{E(s["title"])}</a>, {E(s["agency"])}, '
            f'checked {E(nice(s.get("checked") or d["checked"]))}</p>')


def check_line(t, d, E):
    links = " and ".join(f'<a href="{E(d["sources"][c]["url"])}" rel="noopener">{E(d["sources"][c]["agency"])}</a>' for c in t["check"])
    return f'<p class="lf-check">Check with {links} before you apply or bid. Fees and rules change, and this page is not legal advice.</p>'


def trade_html(t, d, E, h="h2", gc_link=None):
    rows = []
    for key, label in TOPICS:
        items = [x for x in t["rows"] if x["topic"] == key]
        if not items:
            continue
        ps = "".join(f'<p class="lf-t">{E(x["text"])}</p>' + src_line(d["sources"][x["src"]], d, E) for x in items)
        rows.append(f'<div><dt>{E(label)}</dt><dd>{ps}</dd></div>')
    extra = (f'<p class="lf-src"><a href="{gc_link}">Find your general contractor class</a> from the largest project you take on.</p>' if gc_link else "")
    return (f'<section class="lf-trade" id="{E(t["slug"])}" data-trade="{E(t["slug"])}"><{h}>{E(t["name"])}</{h}><p class="lf-sum">{E(t["summary"])}</p>'
            f'<dl class="lf-dl">{"".join(rows)}</dl>{extra}{check_line(t, d, E)}</section>')


def classes_table(d, E):
    rows = "".join(f'<tr data-cls="{E(c["class"])}"><th scope="row">Class {E(c["class"])}</th><td>{E(c["limit_words"])}</td><td>{E(c["demolition_words"])}</td>'
                   f'<td>{E(c["insurance_words"])}</td><td>{money(c["fee"])}</td><td>{money(c["renewal"])}</td></tr>' for c in d["gc_classes"])
    return ('<div class="lf-tw" role="region" aria-label="City of Chicago general contractor license classes" tabindex="0"><table class="lf-t">'
            '<thead><tr><th scope="col">Class</th><th scope="col">Largest single project</th><th scope="col">Demolition</th>'
            '<th scope="col">Insurance</th><th scope="col">Fee</th><th scope="col">Renewal</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def gc_picker(d, E):
    g = d["gc"]
    s = d["sources"][g["src"]]
    opts = "".join(f'<option value="{E(k)}">{E(v)}</option>' for k, v in g["demo_options"])
    return ('<div class="lf-calc" id="gc-class"><div>'
            '<div class="lf-f"><label for="lf-val">Largest single project value</label>'
            f'<small>{E(g["value_hint"])}</small>'
            '<div class="lf-dol"><span aria-hidden="true">$</span><input class="lf-in" id="lf-val" type="text" inputmode="decimal" autocomplete="off" value="750,000" aria-describedby="lf-out"></div></div>'
            '<div class="lf-f"><label for="lf-demo">Demolition in your work</label>'
            f'<small>{E(g["demo_hint"])}</small>'
            f'<select class="lf-sel" id="lf-demo">{opts}</select></div></div>'
            '<div class="lf-out" id="lf-out" role="status" aria-live="polite" aria-atomic="true"><div class="lab">Smallest class that covers it</div>'
            '<div class="lf-cls" id="lf-cls">Class D</div>'
            '<dl class="lf-kv"><dt>Fee</dt><dd id="lf-fee"></dd><dt>Renewal</dt><dd id="lf-ren"></dd><dt>Insurance</dt><dd id="lf-ins"></dd><dt>Covers</dt><dd id="lf-cov"></dd></dl>'
            '<p class="lf-why" id="lf-why"></p>'
            f'<p class="lf-check">Check with the <a href="{E(s["url"])}" rel="noopener">{E(s["agency"])}</a> before you apply. This picker reads the class table below; it is not legal advice.</p>'
            '</div></div>'
            + classes_table(d, E)
            + src_line(s, d, E)
            + f'<p class="lf-src">{E(g["note"])}</p>')


def script(d):
    data = json.dumps([{k: c[k] for k in ("class", "max", "demo", "fee", "renewal", "insurance_words", "limit_words")} for c in d["gc_classes"]])
    return ("<script>(function(){var C=" + data + ";"
            "var v=document.getElementById('lf-val'),dm=document.getElementById('lf-demo');"
            "var rank={none:0,ordinary:1,complex:2};"
            "function money(n){return '$'+Math.round(n).toLocaleString('en-US')}"
            "function parse(s){s=String(s||'').toLowerCase().replace(/[$,\\s]/g,'');var m=s.match(/^(\\d*\\.?\\d+)(k|m|million)?$/);if(!m)return NaN;"
            "var n=parseFloat(m[1]);if(m[2]==='k')n*=1e3;if(m[2]==='m'||m[2]==='million')n*=1e6;return n}"
            "function pick(){if(!v)return;var n=parse(v.value),need=rank[dm.value]||0,el=function(i){return document.getElementById(i)};"
            "var rows=document.querySelectorAll('.lf-t tr[data-cls]');rows.forEach(function(r){r.classList.remove('on')});"
            "if(!(n>=0)){el('lf-cls').textContent='Enter a value';['lf-fee','lf-ren','lf-ins','lf-cov'].forEach(function(i){el(i).textContent=''});"
            "el('lf-why').textContent='Type the dollar value of the largest single project, for example 750000 or 1.2m.';return}"
            "var c=null;for(var i=C.length-1;i>=0;i--){var x=C[i];if((x.max===null||n<=x.max)&&rank[x.demo]>=need){c=x;break}}"
            "if(!c)c=C[0];el('lf-cls').textContent='Class '+c['class'];el('lf-fee').textContent=money(c.fee)+' for the license';"
            "el('lf-ren').textContent=money(c.renewal)+' each year';el('lf-ins').textContent=c.insurance_words;el('lf-cov').textContent=c.limit_words;"
            "var w='A '+money(n)+' project'+(need===2?' with complex demolition':need===1?' with ordinary demolition':' with no demolition')+' fits Class '+c['class']+'.';"
            "var lo=C.filter(function(x){return x.max!==null&&n<=x.max});"
            "if(need>0&&lo.length&&rank[lo[lo.length-1].demo]<need)w+=' The project value alone would fit Class '+lo[lo.length-1]['class']+', but that class does not cover this demolition.';"
            "w+=' A higher class covers it too.';el('lf-why').textContent=w;"
            "rows.forEach(function(r){if(r.getAttribute('data-cls')===c['class'])r.classList.add('on')})}"
            "if(v){v.addEventListener('input',pick);dm.addEventListener('change',pick);pick()}"
            "var s=document.getElementById('lf-trade');if(s){var all=document.querySelectorAll('.lf-trade');s.parentNode.parentNode.hidden=false;"
            "function show(k){all.forEach(function(t){t.classList.toggle('lf-hide',!!k&&t.getAttribute('data-trade')!==k)});"
            "var n=document.getElementById('lf-count');if(n)n.textContent=k?'Showing 1 of '+all.length+' trades':'Showing all '+all.length+' trades'}"
            "s.addEventListener('change',function(){show(s.value);if(s.value){history.replaceState(null,'','#'+s.value)}else{history.replaceState(null,'',location.pathname)}});"
            "var h=location.hash.slice(1);if(h&&document.querySelector('.lf-trade[data-trade=\"'+h.replace(/[^a-z-]/g,'')+'\"]')){s.value=h;show(h)}else{show('')}}"
            "})();</script>")


def foot(d, rel, E, M):
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Every line on this page was read on the issuing agency\'s own page on {E(nice(d["checked"]))} and links to it. Agencies change fees and rules; '
            'the agency page is the one that counts.</p>'
            '<p>Public information, not legal, tax or insurance advice. ProofNotFluff is not affiliated with or endorsed by the City of Chicago, '
            'the State of Illinois or any agency named here.</p>'
            '<p>Made by ProofNotFluff with AI assistance, reviewed and tested by the shop owner. The class picker runs in your browser; nothing you type is sent '
            'anywhere. The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n'
            + script(d) + '\n</body></html>')


def head(p, M, E, url, rel, title, desc, robots, ld):
    return M.HEAD.format(title=E(title), desc=E(desc), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(*ld) + CSS,
                         bodycls=' class="ld-page"', robots=robots, analytics=M.analytics_tag())


def page_html(p):
    import make_site as M
    E = M.E
    d = load(p)
    url, rel = M.BASE + p["slug"] + "/", "../"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (META["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in d["faq"]]}
    trades = d["trades"]
    opts = '<option value="">All 12 trades</option>'.replace("12", str(len(trades))) + "".join(f'<option value="{E(t["slug"])}">{E(t["name"])}</option>' for t in trades)
    grid = ('<ul class="lf-grid">' + "".join(f'<li><a href="{E(t["slug"])}/"><span>{E(t["name"])}<small>{E(t["card"])}</small></span>{M.ARROW}</a></li>' for t in trades) + '</ul>')
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(META["h1"])}</h1>'
            f'<p class="lede">{E(d["lede"])}</p>'
            f'<p class="asof">Every line checked on {E(nice(d["checked"]))} on the agency\'s own page, linked beside it.</p></div>'
            '<section class="block" id="trades"><h2>Pick your trade</h2>'
            '<div class="lf-pick" hidden><div><label for="lf-trade">Trade</label>'
            f'<select class="lf-sel" id="lf-trade">{opts}</select></div><p class="asof" id="lf-count" aria-live="polite"></p></div>'
            f'{"".join(trade_html(t, d, E, gc_link="#gc-class" if t["slug"] == "general-contractor" else None) for t in trades)}</section>'
            f'<section class="block" id="gc"><h2>Which general contractor class do you need?</h2><p>{E(d["gc"]["intro"])}</p>{gc_picker(d, E)}</section>'
            f'<section class="block" id="each"><h2>One page per trade</h2><p>The same facts on a page of their own, to save or send.</p>{grid}</section>'
            '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in d["method"]) + '</section>'
            f'{M.faq_block(d["faq"])}')
    return head(p, M, E, url, rel, p["title"], p["desc"], robots, [crumb_ld, faq_ld]) + body + foot(d, rel, E, M)


def extra_pages(p):
    import make_site as M
    E = M.E
    d = load(p)
    out = []
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    for t in d["trades"]:
        url, rel = M.BASE + p["slug"] + "/" + t["slug"] + "/", "../../"
        crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (META["h1"], p["slug"] + "/"), (t["name"], None)])
        gc = t["slug"] == "general-contractor"
        others = "".join(f'<li><a href="../{E(x["slug"])}/"><span>{E(x["name"])}<small>{E(x["card"])}</small></span>{M.ARROW}</a></li>' for x in d["trades"] if x is not t)
        body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">Chicago trade license finder</p><h1>{E(t["h1"])}</h1>'
                f'<p class="lede">{E(t["summary"])}</p><p class="asof">Every line checked on {E(nice(d["checked"]))} on the agency\'s own page, linked beside it.</p></div>'
                + trade_html(dict(t, summary=t["page_summary"]), d, E, h="h2", gc_link="#gc-class" if gc else None)
                + (f'<section class="block" id="gc"><h2>Which class do you need?</h2><p>{E(d["gc"]["intro"])}</p>{gc_picker(d, E)}</section>' if gc else "")
                + f'<section class="block"><h2>Other trades</h2><p><a href="../">See every trade on one page</a>, or pick another.</p><ul class="lf-grid">{others}</ul></section>')
        title = t["title"]
        out.append((t["slug"] + "/index.html", head(p, M, E, url, rel, title, t["desc"], robots, [crumb_ld]) + body + foot(d, rel, E, M)))
    return out


DASH = re.compile("[–—]")


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == "chicago-trade-licenses"][0]
    M.PAGES_LIVE[:] = []
    d = load(spec)
    html = page_html(spec)
    assert html.count("<h1>") == 1 and not DASH.search(html), "one h1, no dashes"
    assert html.count('class="lf-trade"') == len(d["trades"]) == 12, "12 trade sections"
    assert html.count('class="lf-check"') == 13, "every trade and the picker end with check with"
    for t in d["trades"]:
        for r in t["rows"]:
            assert r["src"] in d["sources"], (t["slug"], r["src"])
    subs = extra_pages(spec)
    assert len(subs) == 12 and all(s.count("<h1>") == 1 and not DASH.search(s) for _, s in subs), "12 sub-pages"
    assert "noindex" in html, "a draft entry renders noindex"
    print("dp_licenses selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
