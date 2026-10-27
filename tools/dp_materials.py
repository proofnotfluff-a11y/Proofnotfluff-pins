#!/usr/bin/env python3
"""Material Price Changes Since Your Quote: the free page /material-price-changes/ (site/pages.json kind "datapage",
module dp_materials, written by tools/make_site.py, which calls page_html and extra_pages here).
Todd's go: Oct 27, 2026, 12:17 pm, "Let's do them all" (coo/DECISIONS-2026-10-27.md, coo/PARALLEL_BUILDS.md, build B9;
research_notes/kimi-2026-10-27-r10.md item 11).

Data, all under site/datapages/dp_materials/:
- ppi.json: BLS producer price indexes by commodity, monthly, not seasonally adjusted, as the BLS Public Data API
  returns them (tools/dp_materials_bls.py, run by .github/workflows/dp_materials.yml on each weekday, so a BLS
  release and its revisions land the same day). Footnote "P" marks a preliminary value.
- series.json: which series the page shows; each id and title is BLS's own, with the BLS page it was read from.
  "group" and "buyers" are our plain words for finding a material.
- schedule.json: BLS's PPI release dates, read from bls.gov/schedule/news_release/ppi.htm.

What the page says, and why: these are national (and one Midwest) producer price indexes, what U.S. producers get for
their goods, not what a Chicago supplier charges; BLS revises each month for up to 4 months, so preliminary months are
labeled; index levels of different materials are not comparable, only their percent changes. The calculator does what
BLS's own Price Adjustment Guide for Contracts shows: an amount at the quote month's index, times today's index over
the quote month's index. It runs in the browser; nothing typed is sent anywhere.

Usage: python3 tools/dp_materials.py --selftest
"""
import datetime as dt, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DIR = os.path.join(ROOT, "site", "datapages", "dp_materials")
SLUG = "material-price-changes"

META = {"h1": "Material Price Changes Since Your Quote",
        "card": "How far lumber, copper wire, concrete, steel and other materials trades buy moved since the month you quoted, from BLS price indexes. Free calculator and CSV.",
        "keywords": ["material prices", "material price increase", "price escalation", "producer price index", "PPI",
                     "lumber prices", "copper wire prices", "steel prices", "concrete prices", "quote", "change order", "BLS"]}

BLS_PPI = "https://www.bls.gov/ppi/"
BLS_GUIDE = "https://www.bls.gov/ppi/publications/price-adjustment-guide-for-contracting-parties.htm"
BLS_SCHED = "https://www.bls.gov/schedule/news_release/ppi.htm"
BLS_API = "https://www.bls.gov/developers/"
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTH_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
GROUPS = ["Wood", "Concrete and masonry", "Metals and wire", "Roofing, walls and paint", "Plumbing, HVAC and electrical", "Fuel"]
DEFAULT = "copper-wire-and-cable"     # the calculator opens on a worked example (UX law 15)
DASHES = ("—", "–")


# ------------------------------------------------------------------ data
def _json(name, p=None):
    f = os.path.join(ROOT, (p or {}).get("dataDir", os.path.relpath(DIR, ROOT)), name)
    return json.load(open(f, encoding="utf-8")) if os.path.isfile(f) else None


def ym_add(ym, n):
    y, m = int(ym[:4]), int(ym[5:7]) - 1 + n
    return f"{y + m // 12}-{m % 12 + 1:02d}"


def mlabel(ym, long=False):
    return f'{(MONTH_LONG if long else MON)[int(ym[5:7]) - 1]} {ym[:4]}'


def pct(a, b):
    return None if not a else (b / a - 1) * 100


def pct_txt(x):
    if x is None:
        return "n/a"
    return "0.0%" if abs(x) < 0.05 else f"{x:+.1f}%"


def move_words(x):
    if x is None:
        return "not comparable"
    if abs(x) < 0.05:
        return "unchanged"
    return f'{"up" if x > 0 else "down"} {abs(x):.1f}%'


def load(p=None):
    """Everything the page needs, computed once; None before the first BLS pull."""
    ppi, spec, sched = _json("ppi.json", p), _json("series.json", p), _json("schedule.json", p)
    if not ppi or not spec:
        return None
    by_id = {s["id"]: s for s in ppi["series"]}
    mats = []
    for s in spec["series"]:
        got = by_id.get(s["id"])
        if not got or not got["obs"]:
            continue
        obs = got["obs"]
        at = {o[0]: o for o in obs}
        last = obs[-1]
        m1, y12 = at.get(ym_add(last[0], -1)), at.get(ym_add(last[0], -12))
        mats.append(dict(s, obs=obs, at=at, last=last, m1o=m1, y12o=y12,
                         m1=pct(m1[1], last[1]) if m1 else None, y12=pct(y12[1], last[1]) if y12 else None,
                         area="Midwest region" if "Midwest" in s["title"] else "national"))
    nxt = None
    if sched:
        today = dt.date.today().isoformat()
        nxt = next(({"month": r[0], "date": r[1]} for r in sched["releases"] if r[1] >= today), None)
    latest = max(m["last"][0] for m in mats)
    return {"ppi": ppi, "spec": spec, "sched": sched, "next": nxt, "mats": mats, "latest": latest,
            "prelim": sorted({o[0] for m in mats for o in m["obs"] if "P" in o[2]}),
            "fetched": ppi["source"]["fetchedAt"]}


def lastmod(p):
    d = load(p)
    return d["fetched"][:10] if d else None


# ------------------------------------------------------------------ pieces
CSS = ("<style>"
       ":root{--mp-up:#a63e21;--mp-dn:#00856f}@media(prefers-color-scheme:dark){:root{--mp-up:#e2683f;--mp-dn:#1fa293}}"
       ".mp-hero .lede{max-width:780px}.mp-hero .ld-heroact{margin-bottom:20px}.mp-name,.mp-dv .n,.mp-t tbody th,.mp-rel a,.mp-res .sub{overflow-wrap:anywhere}.mp-tiles .lab,.mp-res .lab{white-space:normal}.mp-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}@media(min-width:900px){.mp-tiles{grid-template-columns:repeat(4,minmax(0,1fr))}}"
       ".mp-tiles .val small{font-size:.55em;font-weight:600;color:inherit;opacity:.8}.mp-name{font-size:clamp(16px,9cqi,22px)!important;line-height:1.25}"
       ".mp-calc{margin-top:8px}@media(min-width:900px){.mp-calc{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}"
       ".mp-calc .row{grid-template-columns:minmax(0,1fr) minmax(0,260px)}.mp-calc .field select{text-align:left;padding-right:28px;min-height:44px}"
       ".mp-calc .field input{min-height:44px}.mp-calc .row label{font-weight:600}.mp-calc .row label small{display:block;font-weight:400;color:var(--muted);font-size:13px}"
       "@media(max-width:599px){.mp-calc .row{grid-template-columns:1fr;gap:6px}}"
       ".mp-res .tiles{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}.mp-res .tile.key{grid-column:1/-1}.mp-res .tile.key .val{font-size:clamp(30px,11cqi,46px)}"
       ".mp-say{margin:14px 0 0;font-size:15.5px;line-height:1.5;color:var(--ink)}.mp-pnote{margin:10px 0 0;font-size:13.5px;color:var(--muted)}"
       ".mp-acts{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:14px}.mp-acts [role=status]{font-size:13.5px;color:var(--teal-ink)}"
       ".mp-p{display:inline-block;margin-left:5px;padding:0 5px;border-radius:5px;font:700 11px/17px system-ui,sans-serif;letter-spacing:.04em;"
       "color:var(--tag-ink);border:1px solid currentColor;vertical-align:1px;text-decoration:none;cursor:help}"
       ".mp-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin:10px 0 0;padding:0;list-style:none;font-size:13.5px;color:var(--muted)}"
       ".mp-key i{display:inline-block;width:18px;height:10px;border-radius:3px;margin-right:6px;vertical-align:0}"
       ".mp-dv{margin:12px 0 0;padding:14px 16px 10px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".mp-dv ol{list-style:none;margin:0;padding:0}section.block .mp-dv li,section.block .mp-rel li,section.block .mp-key li{max-width:none}"
       ".mp-dv a{display:grid;grid-template-columns:minmax(150px,240px) minmax(0,1fr) 76px;gap:4px 12px;align-items:center;min-height:44px;"
       "padding:2px 6px;margin:0 -6px;border-radius:8px;color:var(--ink);text-decoration:none;position:relative}"
       ".mp-dv a:hover,.mp-dv a:focus-visible{background:var(--rule)}.mp-dv a:focus-visible{outline:3px solid var(--focus);outline-offset:1px}"
       ".mp-dv .n{font-size:14.5px;font-weight:600;line-height:1.25}.mp-dv b{text-align:right;font:700 14.5px system-ui,sans-serif;font-variant-numeric:tabular-nums}"
       ".mp-tr{position:relative;height:14px}.mp-tr::before{content:'';position:absolute;left:var(--z,50%);top:-6px;bottom:-6px;width:1px;background:var(--dash)}"
       ".mp-tr i{position:absolute;top:0;height:14px}.mp-up{background:var(--mp-up);border-radius:0 4px 4px 0}"
       ".mp-dn{background:var(--mp-dn);border-radius:4px 0 0 4px}"
       ".mp-dv .tip{display:none;position:absolute;z-index:3;left:auto;right:70px;top:100%;margin-top:2px;padding:6px 10px;border-radius:8px;"
       "background:var(--band);color:#fff;font-size:13px;white-space:nowrap;box-shadow:var(--shadow-soft);pointer-events:none}"
       ".mp-dv a:hover .tip,.mp-dv a:focus-visible .tip{display:block}"
       "@media(max-width:599px){main .mp-dv li a{grid-template-columns:minmax(0,1fr) 70px;padding:6px 6px}main .mp-rel li a{padding:0 14px}.mp-dv .n{grid-column:1/-1}.mp-dv .mp-tr{grid-column:1}.mp-dv .tip{right:6px}}"
       ".mp-tw{overflow-x:auto;margin:12px 0 0;border:1px solid var(--line);border-radius:12px;background:var(--card)}"
       ".mp-tw:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".mp-t{width:100%;border-collapse:collapse;font-size:14.5px}.mp-t th,.mp-t td{padding:10px 12px;border-bottom:1px solid var(--rule);text-align:right;font-variant-numeric:tabular-nums;vertical-align:middle}"
       ".mp-t th:first-child,.mp-t td:first-child{text-align:left}.mp-t thead th{font-size:13px;color:var(--muted);font-weight:700;background:var(--card)}"
       ".mp-t tbody th{font-weight:600;color:var(--ink)}.mp-t tbody th a{color:var(--ink)}.mp-t tbody th small{display:block;font-weight:400;color:var(--muted);font-size:12.5px;margin-top:2px}"
       ".mp-t .g th{background:var(--canvas2);font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);padding:7px 12px}"
       ".mp-t thead th{white-space:nowrap}.mp-t tr:last-child td,.mp-t tr:last-child th{border-bottom:0}.mp-t td.u{color:var(--warn-ink)}.mp-t td.d{color:var(--teal-ink)}"
       ".mp-sp{display:block;width:96px;height:26px;margin-left:auto}"
       "@media(max-width:599px){.mp-t .c2,.mp-t .c5{display:none}.mp-t th,.mp-t td{padding:9px 8px}}"
       ".mp-read{display:grid;gap:12px;margin-top:12px}@media(min-width:900px){.mp-read{grid-template-columns:repeat(2,minmax(0,1fr))}}"
       ".mp-read div{padding:14px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card)}.mp-read h3{margin:0 0 4px;font-size:16px}.mp-read p{margin:0;color:var(--ink2);font-size:15px}"
       ".mp-dl{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-top:14px}"
       ".mp-lc{position:relative;margin:12px 0 0;padding:14px 12px 8px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       ".mp-lc svg{display:block;width:100%;height:auto;touch-action:pan-y}.mp-lc svg.n{display:none}@media(max-width:599px){.mp-lc svg.w{display:none}.mp-lc svg.n{display:block}}.mp-lc:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".mp-lc .gl{stroke:var(--rule);stroke-width:1}.mp-lc .ax{fill:var(--muted);font:11.5px system-ui,sans-serif;font-variant-numeric:tabular-nums}"
       ".mp-lc .ln{fill:none;stroke:var(--teal);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}.mp-lc .lp{stroke-dasharray:4 4}"
       ".mp-lc .ar{fill:var(--teal);opacity:.1}.mp-lc .dot{fill:var(--teal);stroke:var(--card);stroke-width:2}"
       ".mp-lc .xh{stroke:var(--ink2);stroke-width:1}.mp-lc .el{fill:var(--ink);font:700 12.5px system-ui,sans-serif}"
       ".mp-lc .tt{position:absolute;top:8px;padding:7px 10px;border-radius:8px;background:var(--band);color:#fff;font-size:13px;line-height:1.35;"
       "pointer-events:none;white-space:nowrap;box-shadow:var(--shadow-soft)}.mp-lc .tt b{display:block;font-size:15px}"
       ".mp-more{margin:12px 0 0}.mp-more summary{display:flex;align-items:center;min-height:44px;padding:0 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);cursor:pointer;font-weight:600;color:var(--ink)}"
       ".mp-more[open] summary{margin-bottom:8px}.mp-id{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:.95em}"
       ".mp-rel{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0;padding:0;list-style:none}.mp-rel a{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;"
       "border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);text-decoration:none;font-weight:600;font-size:14.5px}.mp-rel a:hover{border-color:var(--accent)}"
       "@media(prefers-reduced-motion:no-preference){.mp-res .val{transition:opacity .15s}}"
       "</style>")


def P(o, E):
    return ('<abbr class="mp-p" title="Preliminary: BLS can revise it for up to 4 months after it first comes out">P</abbr>'
            if o and "P" in o[2] else "")


def calc_data(d):
    """The compact series list the calculator reads: [slug, title, group, id, area, [[YYYY-MM, value, 1 if preliminary]]]."""
    return [[m["slug"], m["title"], m["group"], m["id"], m["area"], [[o[0], o[1], 1 if "P" in o[2] else 0] for o in m["obs"]]] for m in d["mats"]]


def calc_html(d, E, default=DEFAULT, heading=True):
    mats = d["mats"]
    dflt = next((m for m in mats if m["slug"] == default), mats[0])
    q = ym_add(dflt["last"][0], -12)
    q = q if q in dflt["at"] else dflt["obs"][0][0]
    opts = "".join(f'<optgroup label="{E(g)}">' + "".join(
        f'<option value="{E(m["slug"])}"{" selected" if m is dflt else ""}>{E(m["title"])}</option>' for m in mats if m["group"] == g) + '</optgroup>'
        for g in GROUPS if any(m["group"] == g for m in mats))
    months = "".join(f'<option value="{o[0]}"{" selected" if o[0] == q else ""}>{mlabel(o[0])}{" (preliminary)" if "P" in o[2] else ""}</option>'
                     for o in reversed(dflt["obs"][:-1]))
    amt = 10000
    now, then = dflt["last"], dflt["at"][q]
    ch = pct(then[1], now[1])
    new = amt * now[1] / then[1]
    say = (f'{E(dflt["title"])} is {move_words(ch)} from {mlabel(q)} to {mlabel(now[0])}. '
           f'${amt:,.2f} of it at the {mlabel(q)} index is ${new:,.2f} at the {mlabel(now[0])} index.')
    pnote = (f'{mlabel(now[0])} is preliminary: BLS can revise it for up to 4 months after it first comes out.' if "P" in now[2] else "")
    return ((f'<h2 id="quote-h">What your quote is worth now</h2><p>Pick the material, the month you priced the job and the material cost in your quote. '
             'The result moves with the BLS index for that material, the way BLS shows contracts adjusting a price.</p>' if heading else "")
            + '<div class="grid mp-calc" data-mp-calc>'
            '<form class="card" novalidate onsubmit="return false">'
            '<fieldset><legend>Your quote</legend>'
            f'<div class="row"><label for="mp-mat">Material<small>BLS price index</small></label><div class="field"><select id="mp-mat">{opts}</select></div></div>'
            f'<div class="row"><label for="mp-mon">Month you quoted<small>The index for that month</small></label><div class="field"><select id="mp-mon">{months}</select></div></div>'
            f'<div class="row"><label for="mp-amt">Material cost in the quote<small>Just the material, not labor</small></label>'
            f'<div class="field has-pre"><span class=pre>$</span><input id="mp-amt" type="text" inputmode="decimal" value="10,000" autocomplete="off" aria-describedby="mp-err"></div>'
            '<span class="calc-err" id="mp-err" hidden>Type an amount, like 10,000 or 2.5k.</span></div>'
            '</fieldset>'
            '<div class="calc-reset"><button type="button" class="st-btn2" data-mp-reset>Reset the example</button></div>'
            '</form>'
            '<div class="sticky"><div class="card mp-res" aria-live="polite">'
            '<div class="tiles">'
            f'<div class="tile key"><div class="lab">Change since your quote</div><div class="val" data-mp="ch">{pct_txt(ch)}</div>'
            f'<div class="sub" data-mp="span">{E(dflt["title"])}, {mlabel(q)} to {mlabel(now[0])}</div></div>'
            f'<div class="tile"><div class="lab">Your amount today</div><div class="val" data-mp="new">${new:,.0f}</div><div class="sub" data-mp="from">from ${amt:,.0f}</div></div>'
            f'<div class="tile"><div class="lab">Difference</div><div class="val" data-mp="diff">{"+" if new >= amt else "-"}${abs(new - amt):,.0f}</div>'
            f'<div class="sub" data-mp="idx">index {then[1]:,.1f} then, {now[1]:,.1f} now</div></div>'
            '</div>'
            f'<p class="mp-say" data-mp="say">{say}</p>'
            f'<p class="mp-pnote" data-mp="pnote"{"" if pnote else " hidden"}>{E(pnote)}</p>'
            '<div class="mp-acts"><button type="button" class="st-btn2" data-mp-copy>Copy this as a sentence</button><span role="status" data-mp="copied"></span></div>'
            f'<p class="mp-pnote">A national price index, not your supplier\'s price. Use it to see the size of a move; the price you pay is on your supplier\'s invoice.</p>'
            '</div></div></div>')


def calc_js(d):
    data = json.dumps({"s": calc_data(d), "dflt": DEFAULT}, separators=(",", ":"))
    return ("<script>(function(){var D=" + data + ";"
            r"""
var root=document.querySelector('[data-mp-calc]');if(!root)return;
var mat=root.querySelector('#mp-mat'),mon=root.querySelector('#mp-mon'),amt=root.querySelector('#mp-amt'),err=root.querySelector('#mp-err');
var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function lab(ym){return M[+ym.slice(5,7)-1]+' '+ym.slice(0,4)}
function ser(slug){for(var i=0;i<D.s.length;i++)if(D.s[i][0]===slug)return D.s[i];return D.s[0]}
function back(ym,n){var y=+ym.slice(0,4),m=+ym.slice(5,7)-1-n;y+=Math.floor(m/12);m=((m%12)+12)%12;return y+'-'+(m<9?'0':'')+(m+1)}
function out(k){return root.querySelector('[data-mp="'+k+'"]')}
function money(x,c){return '$'+x.toLocaleString('en-US',{minimumFractionDigits:c,maximumFractionDigits:c})}
function pc(x){return Math.abs(x)<0.05?'0.0%':(x>0?'+':'-')+Math.abs(x).toFixed(1)+'%'}
function words(x){return Math.abs(x)<0.05?'unchanged':(x>0?'up ':'down ')+Math.abs(x).toFixed(1)+'%'}
function parse(s){s=String(s).trim().toLowerCase().replace(/[$,\s]/g,'');var k=1;if(/k$/.test(s)){k=1000;s=s.slice(0,-1)}else if(/m$/.test(s)){k=1e6;s=s.slice(0,-1)}
 if(!/^\d*\.?\d+$/.test(s))return NaN;return parseFloat(s)*k}
function fillMonths(keep){var s=ser(mat.value),o=s[5],want=keep;var have={};for(var i=0;i<o.length-1;i++)have[o[i][0]]=1;
 if(!have[want]){want=back(o[o.length-1][0],12);if(!have[want])want=o[0][0]}
 mon.textContent='';for(var j=o.length-2;j>=0;j--){var op=document.createElement('option');op.value=o[j][0];op.textContent=lab(o[j][0])+(o[j][2]?' (preliminary)':'');if(o[j][0]===want)op.selected=true;mon.appendChild(op)}}
var last='';
function run(){var s=ser(mat.value),o=s[5],now=o[o.length-1],then=null;for(var i=0;i<o.length;i++)if(o[i][0]===mon.value)then=o[i];
 var a=parse(amt.value),bad=!(a>=0)||!then;amt.setAttribute('aria-invalid',bad?'true':'false');err.hidden=!bad;root.querySelector('.mp-res').style.opacity=bad?.45:1;if(bad)return;
 var ch=(now[1]/then[1]-1)*100,nw=a*now[1]/then[1],df=nw-a;
 out('ch').textContent=pc(ch);out('span').textContent=s[1]+', '+lab(then[0])+' to '+lab(now[0]);
 out('new').textContent=money(nw,nw<1000?2:0);out('from').textContent='from '+money(a,a<1000?2:0);
 out('diff').textContent=(df<0?'-':'+')+money(Math.abs(df),Math.abs(df)<1000?2:0);
 out('idx').textContent='index '+then[1].toFixed(1)+' then, '+now[1].toFixed(1)+' now';
 out('say').textContent=s[1]+' is '+words(ch)+' from '+lab(then[0])+' to '+lab(now[0])+'. '+money(a,2)+' of it at the '+lab(then[0])+' index is '+money(nw,2)+' at the '+lab(now[0])+' index.';
 var pl=[];if(then[2])pl.push(lab(then[0]));if(now[2])pl.push(lab(now[0]));var pn=out('pnote');
 pn.hidden=!pl.length;pn.textContent=pl.length?pl.join(' and ')+(pl.length>1?' are':' is')+' preliminary: BLS can revise '+(pl.length>1?'them':'it')+' for up to 4 months after it first comes out.':'';
 last=s[1]+', BLS producer price index '+s[3]+' ('+s[4]+', not seasonally adjusted): '+then[1].toFixed(3)+' in '+lab(then[0])+(then[2]?' (preliminary)':'')+' and '+now[1].toFixed(3)+' in '+lab(now[0])+(now[2]?' (preliminary)':'')+', '+words(ch)+'. '+money(a,2)+' at the '+lab(then[0])+' index is '+money(nw,2)+' at the '+lab(now[0])+' index. Source: U.S. Bureau of Labor Statistics, via proofnotfluff.com/material-price-changes/';
 out('copied').textContent=''}
mat.addEventListener('change',function(){fillMonths(mon.value);run()});mon.addEventListener('change',run);amt.addEventListener('input',run);
root.querySelector('[data-mp-reset]').addEventListener('click',function(){mat.value=root.getAttribute('data-default')||D.dflt;fillMonths('');amt.value='10,000';run()});
root.querySelector('[data-mp-copy]').addEventListener('click',function(){var st=out('copied');
 function ok(){st.textContent='Copied.'}function no(){var t=document.createElement('textarea');t.value=last;t.setAttribute('readonly','');t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();
  try{document.execCommand('copy');ok()}catch(e){st.textContent='Copy did not work here; select the sentence above instead.'}document.body.removeChild(t)}
 if(navigator.clipboard&&window.isSecureContext)navigator.clipboard.writeText(last).then(ok,no);else no()});
run()})();</script>""")


def diverging(d, E, rel):
    mats = sorted([m for m in d["mats"] if m["y12"] is not None], key=lambda m: (-m["y12"], m["title"]))
    neg = max([0] + [-m["y12"] for m in mats])
    pos = max([0] + [m["y12"] for m in mats])
    span = (neg + pos) or 1
    zero = neg / span * 100          # the zero line sits where the scale puts it, so one small drop does not waste half the width
    rows = []
    for m in mats:
        w = max(0.8, abs(m["y12"]) / span * 100)
        cls = "mp-up" if m["y12"] >= 0 else "mp-dn"
        where = f"left:{zero:.2f}%" if m["y12"] >= 0 else f"right:{100 - zero:.2f}%"
        tip = f'{m["y12o"][1]:,.1f} in {mlabel(m["y12o"][0])}, {m["last"][1]:,.1f} in {mlabel(m["last"][0])}'
        rows.append(f'<li><a href="{rel}{SLUG}/{E(m["slug"])}/"><span class="n">{E(m["title"])}</span>'
                    f'<span class="mp-tr" aria-hidden="true" style="--z:{zero:.2f}%"><i class="{cls}" style="{where};width:{w:.1f}%"></i></span>'
                    f'<b>{pct_txt(m["y12"])}</b><span class="tip" aria-hidden="true">{E(tip)}</span></a></li>')
    return ('<figure class="mp-dv" aria-labelledby="mp-dv-cap"><figcaption id="mp-dv-cap" class="sr">12-month change in each material\'s price index, '
            f'{mlabel(d["latest"])} against {mlabel(ym_add(d["latest"], -12))}, largest rise first</figcaption><ol>' + "".join(rows) + '</ol>'
            '<ul class="mp-key" aria-hidden="true"><li><i style="background:var(--mp-up)"></i>Price index up</li><li><i style="background:var(--mp-dn)"></i>Price index down</li>'
            '<li>Bars start at the zero line; tap one for its page</li></ul></figure>')


def spark(m):
    pts = [o for o in m["obs"] if o[0] >= ym_add(m["last"][0], -12)]
    if len(pts) < 3:
        return ""
    vs = [o[1] for o in pts]
    lo, hi = min(vs), max(vs)
    rng = (hi - lo) or 1
    xy = [(2 + i * 92 / (len(pts) - 1), 22 - (v - lo) / rng * 18) for i, v in enumerate(vs)]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in xy)
    x, y = xy[-1]
    return (f'<svg class="mp-sp" viewBox="0 0 96 26" aria-hidden="true" focusable="false"><path d="{path}" fill="none" stroke="var(--muted)" stroke-width="1.5" stroke-linejoin="round"/>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="var(--accent)" stroke="var(--card)" stroke-width="1.5"/></svg>')


def table(d, E, rel):
    L = mlabel(d["latest"])
    head = (f'<thead><tr><th scope="col">Material</th><th scope="col" class="c2">Index, {L}</th><th scope="col">1 month</th>'
            '<th scope="col">12 months</th><th scope="col" class="c5">Last 12 months</th></tr></thead>')
    cls = lambda x: "" if x is None or abs(x) < 0.05 else (' class="u"' if x > 0 else ' class="d"')
    body = []
    for g in GROUPS:
        ms = [m for m in d["mats"] if m["group"] == g]
        if not ms:
            continue
        body.append(f'<tr class="g"><th scope="rowgroup" colspan="5">{E(g)}</th></tr>')
        for m in ms:
            body.append(f'<tr><th scope="row"><a href="{rel}{SLUG}/{E(m["slug"])}/">{E(m["title"])}</a><small>{E(m["buyers"])}</small></th>'
                        f'<td class="c2">{m["last"][1]:,.1f}{P(m["last"], E)}</td><td{cls(m["m1"])}>{pct_txt(m["m1"])}</td>'
                        f'<td{cls(m["y12"])}>{pct_txt(m["y12"])}</td><td class="c5">{spark(m)}</td></tr>')
    return (f'<div class="mp-tw" role="region" aria-label="Every material, latest index and changes" tabindex="0"><table class="mp-t">{head}<tbody>{"".join(body)}</tbody></table></div>'
            f'<p class="asof">1 month compares {L} with {mlabel(ym_add(d["latest"], -1))}; 12 months compares {L} with {mlabel(ym_add(d["latest"], -12))}. '
            'Changes come from BLS\'s index values, rounded once to a tenth of a percent. '
            '<abbr class="mp-p" title="Preliminary">P</abbr> marks a preliminary month BLS can still revise.</p>')


def csv_text(mats):
    rows = ["series_id,bls_title,area,month,index,preliminary"]
    for m in mats:
        t = '"' + m["title"].replace('"', '""') + '"'
        rows += [f'{m["id"]},{t},{m["area"]},{o[0]},{o[1]},{"yes" if "P" in o[2] else "no"}' for o in m["obs"]]
    return "\n".join(rows) + "\n"


def nice_ticks(lo, hi, n=5):
    import math
    span = hi - lo or 1
    step = 10 ** math.floor(math.log10(span / n))
    for k in (1, 2, 2.5, 5, 10):
        if span / (step * k) <= n:
            step *= k
            break
    a = math.floor(lo / step) * step
    b = math.ceil(hi / step) * step
    out, v = [], a
    while v <= b + step / 2:
        out.append(round(v, 6))
        v += step
    return out


def line_svg(m, W, H, L, R, T, B, cls):
    obs = m["obs"]
    ticks = nice_ticks(min(o[1] for o in obs), max(o[1] for o in obs), 5 if H > 260 else 4)
    lo, hi = ticks[0], ticks[-1]
    first = obs[0][0]
    idx = lambda ym: (int(ym[:4]) - int(first[:4])) * 12 + int(ym[5:7]) - int(first[5:7])
    n = idx(obs[-1][0]) or 1
    X = lambda ym: L + idx(ym) / n * (W - L - R)
    Y = lambda v: T + (hi - v) / (hi - lo or 1) * (H - T - B)
    pts = [(X(o[0]), Y(o[1]), o) for o in obs]

    def path(ps):
        out, prev = [], None
        for x, y, o in ps:   # a month BLS has no value for breaks the line rather than drawing across it
            out.append(("M" if prev is None or idx(o[0]) - idx(prev[0]) > 1 else "L") + f"{x:.1f},{y:.1f}")
            prev = o
        return " ".join(out)
    final = [q for q in pts if "P" not in q[2][2]]
    prel = [q for q in pts if "P" in q[2][2]]
    if final and prel:
        prel = [final[-1]] + prel
    area = (f'M{pts[0][0]:.1f},{H - B} ' + " ".join(f"L{x:.1f},{y:.1f}" for x, y, _ in pts) + f' L{pts[-1][0]:.1f},{H - B} Z')
    grid = "".join(f'<line class="gl" x1="{L}" x2="{W - R + 8}" y1="{Y(t):.1f}" y2="{Y(t):.1f}"/><text class="ax" x="{L - 7}" y="{Y(t) + 4:.1f}" text-anchor="end">{t:,.0f}</text>'
                   for t in ticks)
    years = sorted({o[0][:4] for o in obs if o[0][5:7] == "01"})
    every = 2 if W > 500 else 3
    xl = "".join(f'<text class="ax" x="{X(y + "-01"):.1f}" y="{H - 8}" text-anchor="middle">{y if i % every == (len(years) - 1) % every else ""}</text>'
                 for i, y in enumerate(years))
    x, y, o = pts[-1]
    end = f'<circle class="dot" cx="{x:.1f}" cy="{y:.1f}" r="4"/><text class="el" x="{x + 7:.1f}" y="{y + 4:.1f}">{o[1]:,.1f}</text>'
    pdata = json.dumps([[q[2][0], q[2][1], 1 if "P" in q[2][2] else 0, round(q[0], 1), round(q[1], 1)] for q in pts], separators=(",", ":"))
    return (f'<svg class="{cls}" viewBox="0 0 {W} {H}" aria-hidden="true" focusable="false" data-w="{W}" data-pts=\'{pdata}\'>{grid}{xl}'
            f'<path class="ar" d="{area}"/><path class="ln" d="{path(final)}"/>' + (f'<path class="ln lp" d="{path(prel)}"/>' if prel else "")
            + f'<line class="xh" x1="0" x2="0" y1="{T}" y2="{H - B}" visibility="hidden"/><circle class="dot hv" r="5" cx="0" cy="0" visibility="hidden"/>{end}'
            f'<rect x="{L}" y="{T}" width="{W - L - R}" height="{H - T - B}" fill="transparent" class="hit"/></svg>')


def line_chart(m, E):
    obs = m["obs"]
    lo_o, hi_o, o = min(obs, key=lambda o: o[1]), max(obs, key=lambda o: o[1]), obs[-1]
    aria = (f'Line chart of the {m["title"]} price index, {mlabel(obs[0][0])} to {mlabel(obs[-1][0])}: {obs[0][1]:,.1f} at the start, '
            f'high {hi_o[1]:,.1f} in {mlabel(hi_o[0])}, low {lo_o[1]:,.1f} in {mlabel(lo_o[0])}, {o[1]:,.1f} in {mlabel(o[0])}. Every month is in the table below.')
    # two drawings, one for wide screens and one for phones, so the axis text stays readable at both sizes
    return (f'<figure class="mp-lc" tabindex="0" role="img" aria-label="{E(aria)}">'
            + line_svg(m, 720, 300, 46, 52, 14, 30, "w") + line_svg(m, 360, 250, 38, 48, 12, 28, "n")
            + '<div class="tt" hidden></div></figure>'
            '<ul class="mp-key"><li><svg width="22" height="10" aria-hidden="true"><line x1="1" x2="21" y1="5" y2="5" stroke="var(--teal)" stroke-width="2"/></svg>Final</li>'
            '<li><svg width="22" height="10" aria-hidden="true"><line x1="1" x2="21" y1="5" y2="5" stroke="var(--teal)" stroke-width="2" stroke-dasharray="4 4"/></svg>Preliminary, may be revised</li>'
            '<li>Hover, tap or use the arrow keys for any month</li></ul>')


LINE_JS = r"""<script>(function(){var f=document.querySelector('.mp-lc');if(!f)return;var tt=f.querySelector('.tt'),cur=-1;
var M=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
function vis(){var v=f.querySelectorAll('svg');for(var i=0;i<v.length;i++)if(v[i].getBoundingClientRect().width>0)return v[i];return v[0]}
function pts(svg){if(!svg._p)svg._p=JSON.parse(svg.getAttribute('data-pts'));return svg._p}
function show(i){var svg=vis(),P=pts(svg),W=+svg.getAttribute('data-w');if(cur<0)cur=P.length-1;cur=Math.max(0,Math.min(P.length-1,i<0?P.length-1:i));
 var p=P[cur],r=svg.getBoundingClientRect(),k=r.width/W,xh=svg.querySelector('.xh'),dot=svg.querySelector('.hv');
 xh.setAttribute('x1',p[3]);xh.setAttribute('x2',p[3]);xh.setAttribute('visibility','visible');dot.setAttribute('cx',p[3]);dot.setAttribute('cy',p[4]);dot.setAttribute('visibility','visible');
 tt.textContent='';var b=document.createElement('b');b.textContent=p[1].toFixed(3);tt.appendChild(b);tt.appendChild(document.createTextNode(M[+p[0].slice(5,7)-1]+' '+p[0].slice(0,4)+(p[2]?', preliminary':'')));
 tt.hidden=false;var x=p[3]*k+(r.left-f.getBoundingClientRect().left),tw=tt.offsetWidth;tt.style.left=(x+tw+14>f.clientWidth?x-tw-10:x+10)+'px'}
function hide(){var v=f.querySelectorAll('.xh,.hv');for(var i=0;i<v.length;i++)v[i].setAttribute('visibility','hidden');tt.hidden=true}
function near(ev){var svg=vis(),P=pts(svg),W=+svg.getAttribute('data-w'),r=svg.getBoundingClientRect(),x=(ev.clientX-r.left)*W/r.width,b=0,bd=1e9;
 for(var i=0;i<P.length;i++){var dd=Math.abs(P[i][3]-x);if(dd<bd){bd=dd;b=i}}return b}
var hits=f.querySelectorAll('.hit');for(var h=0;h<hits.length;h++){hits[h].addEventListener('pointermove',function(e){show(near(e))});hits[h].addEventListener('pointerdown',function(e){show(near(e))})}
f.addEventListener('pointerleave',hide);f.addEventListener('focus',function(){show(cur)});f.addEventListener('blur',hide);
f.addEventListener('keydown',function(e){var s={ArrowLeft:-1,ArrowRight:1,ArrowDown:-12,ArrowUp:12}[e.key];if(cur<0)cur=pts(vis()).length-1;
 if(e.key==='Home'){show(0);e.preventDefault()}else if(e.key==='End'){show(1e6);e.preventDefault()}else if(s){show(cur+s);e.preventDefault()}})})();</script>"""


def read_right(d, E):
    nx = d.get("next")
    upd = (f'BLS publishes the {mlabel(nx["month"], long=True)} numbers on {E(nice(nx["date"]))}, and this page picks them up the same day.' if nx else
           "BLS publishes each month's numbers in the middle of the next month; this page picks them up that day.")
    by = {m["slug"]: m for m in d["mats"]}
    a, b = by.get("lumber"), by.get("steel-mill-products")
    pair = (f'a lumber index of {a["last"][1]:,.0f} and a steel mill products index of {b["last"][1]:,.0f} say nothing about which costs more'
            if a and b else "two index numbers say nothing about which material costs more")
    blocks = [("National numbers, not Chicago prices",
               "Each index tracks what U.S. producers get for that material across the country (one, ready-mix concrete, is also shown for the Midwest). "
               "It shows how far prices moved, not what a Chicago supplier charges you."),
              ("The last 4 months can still change",
               "BLS revises each month for up to 4 months after it first comes out. Those months carry a P. Run a quote again after a revision and the result can move a little."),
              ("Compare the changes, not the index numbers",
               f"Each material has its own starting point, so {pair}. The percent changes compare fine."),
              ("When it updates", upd)]
    return '<div class="mp-read">' + "".join(f'<div><h3>{E(h)}</h3><p>{E(t)}</p></div>' for h, t in blocks) + '</div>'


def nice(iso):
    d = dt.date.fromisoformat(iso[:10])
    return f"{MON[d.month - 1]} {d.day}, {d.year}"


def example(d):
    m = next((x for x in d["mats"] if x["slug"] == DEFAULT), d["mats"][0])
    q = m["y12o"] or m["obs"][0]
    new = 10000 * m["last"][1] / q[1]
    return m, q, new


def faqs(d):
    m, q, new = example(d)
    L = mlabel(d["latest"])
    nx = d.get("next")
    return [
        ("How do I work out how much a material went up since my quote?",
         f"Divide the price index for this month by the index for the month you quoted, then multiply your material cost by that number. "
         f"{m['title']} was {q[1]:,.3f} in {mlabel(q[0])} and {m['last'][1]:,.3f} in {mlabel(m['last'][0])}, so $10,000 of it then is "
         f"${new:,.2f} at the {mlabel(m['last'][0])} index, {move_words(pct(q[1], m['last'][1]))}. The calculator on this page does the same math for every material here."),
        ("Are these Chicago prices?",
         "No. These are producer price indexes from the U.S. Bureau of Labor Statistics: what U.S. producers get for each material, measured across "
         "the country. Ready-mix concrete is also shown for the Midwest region. Your supplier's price in Chicago can be higher or lower, and can move "
         "at a different speed. Use the index to see the size of a move."),
        ("Why did a number change after I used it?",
         "BLS revises each month for up to 4 months after it first comes out, as late reports arrive. Months still open to revision carry a P on this page. "
         f"Right now {mlabel(d['prelim'][0]) if d['prelim'] else L} to {L} are preliminary."),
        ("Which index should I use for a material I buy?",
         "Pick the one closest to what you buy: copper wire and cable for an electrician's wire, ready-mixed concrete for a pour, gypsum products for drywall. "
         "Each material's page shows its BLS series ID, so anyone can look up the same numbers on bls.gov."),
        ("Are these seasonally adjusted?",
         "No. Every index here is not seasonally adjusted, which is the kind BLS's Price Adjustment Guide for Contracts says to use when a price follows an index."),
        ("When does this page update?",
         (f"BLS releases the producer price index once a month. The next release, for {mlabel(nx['month'])}, is on {nice(nx['date'])}, and the page "
          "picks it up the same day, along with any revisions to the 4 months before it." if nx else
          "BLS releases the producer price index once a month, around the middle of the month; the page picks it up the same day.")),
        ("Can I download the numbers?",
         "Yes. The CSV on this page has every month since January " + d["mats"][0]["obs"][0][0][:4] + " for every material, with BLS's series ID and a column "
         "that says which months are preliminary. Each material's page has its own CSV too."),
    ]


METHOD = [
    "Every number comes from the U.S. Bureau of Labor Statistics producer price index by commodity, not seasonally adjusted, read through the BLS Public Data API on each weekday so a new release or revision lands the same day.",
    "The materials are BLS series for what trade owners commonly buy: wood, concrete and masonry, steel, aluminum, copper wire, roofing, drywall, insulation, paint, pipe, fixtures, heating equipment and diesel. Each series ID and title is BLS's own.",
    "A change is the later index divided by the earlier one, less one, shown as a percent rounded to a tenth. The calculator multiplies your amount by the same ratio, which is how BLS's Price Adjustment Guide for Contracts shows a price following an index.",
    "The page shows BLS's numbers as BLS publishes them and adds nothing to them. It is not a price quote, and it does not say what any contract allows; the contract and BLS's own pages do.",
]


def head_html(M, E, title, desc, url, rel, ld, robots):
    return M.HEAD.format(title=E(title), desc=E(desc), url=url, rel=rel, shop=M.SHOP, ld=ld + CSS, bodycls=' class="ld-page"', robots=robots,
                         analytics=M.analytics_tag())


def foot_html(M, E, rel, d, extra=""):
    pulled = M.nice_date(d["fetched"][:10])
    return (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: U.S. Bureau of Labor Statistics, <a href="{BLS_PPI}">Producer Price Index</a> by commodity, not seasonally adjusted, '
            f'retrieved through the <a href="{BLS_API}">BLS Public Data API</a> on {E(pulled)}. Release dates: '
            f'<a href="{BLS_SCHED}">BLS PPI release schedule</a>. How a price follows an index: <a href="{BLS_GUIDE}">BLS Price Adjustment Guide for Contracts</a>.{extra}</p>'
            '<p>BLS.gov cannot vouch for the data or analyses derived from these data after the data have been retrieved from BLS.gov. '
            'ProofNotFluff is not affiliated with or endorsed by the U.S. Bureau of Labor Statistics.</p>'
            '<p>Public information, not legal, tax or financial advice, and not a price quote from any supplier.</p>'
            '<p>Made by ProofNotFluff with AI assistance from public BLS data. The calculator runs in your browser; nothing you type in it is sent anywhere. '
            'The page counts visits with Cloudflare Web Analytics, which sets no cookies.</p></div></footer>\n')


def shell(p, M, E, url, rel):
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    return (head_html(M, E, p["title"], p["desc"], url, rel, M.ld_tags(crumb_ld), '<meta name="robots" content="noindex, nofollow">')
            + f'{crumb}<div class="ld-hero"><h1>{E(p["h1"])}</h1><p class="lede">The first BLS pull is on its way.</p></div></main></body></html>')


# ------------------------------------------------------------------ the page
def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    d = load(p)
    if not d:
        return shell(p, M, E, url, rel)
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    L = mlabel(d["latest"])
    ys = [m for m in d["mats"] if m["y12"] is not None]
    up = sorted(ys, key=lambda m: -m["y12"])
    n_up = sum(1 for m in ys if m["y12"] >= 0.05)
    top, low = up[0], up[-1]
    nx = d.get("next")
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    fq = faqs(d)
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in fq]}
    ds_ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Material price indexes for trade owners (BLS PPI)",
             "description": f"Monthly BLS producer price indexes for {len(d['mats'])} building materials and diesel fuel, not seasonally adjusted, with preliminary months marked.",
             "url": url, "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": "ProofNotFluff"},
             "isBasedOn": BLS_PPI, "temporalCoverage": f'{d["mats"][0]["obs"][0][0]}/{d["latest"]}',
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": url + "material-price-indexes.csv"}]}
    app_ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": "Material price change since your quote calculator", "url": url + "#quote",
              "applicationCategory": "BusinessApplication", "operatingSystem": "Any", "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    lede = (f'How far {len(d["mats"])} materials trades buy have moved since the month you quoted, from the federal producer price index. '
            f'{n_up} of {len(ys)} are up on a year ago. Free, no sign-up.')
    tiles = ('<div class="tiles ld-tiles mp-tiles">'
             f'<div class="tile key"><div class="lab">Biggest rise, 12 months</div><div class="val mp-name">{E(top["title"])}</div><div class="sub" style="color:var(--band-text)">{pct_txt(top["y12"])} since {mlabel(top["y12o"][0])}</div></div>'
             f'<div class="tile"><div class="lab">{"Biggest drop" if low["y12"] < 0 else "Smallest rise"}, 12 months</div><div class="val mp-name">{E(low["title"])}</div><div class="sub">{pct_txt(low["y12"])} since {mlabel(low["y12o"][0])}</div></div>'
             f'<div class="tile"><div class="lab">Up on a year ago</div><div class="val">{n_up} <small>of {len(ys)}</small></div><div class="sub">materials on this page</div></div>'
             f'<div class="tile"><div class="lab">Latest month</div><div class="val">{L}</div><div class="sub">{"preliminary; " if d["latest"] in d["prelim"] else ""}'
             + (f'next BLS update {E(nice(nx["date"]))}' if nx else "BLS updates monthly") + '</div></div>'
             '</div>'
             f'<p class="asof">BLS producer price indexes, national, not seasonally adjusted, through {L}, retrieved from BLS on {E(M.nice_date(d["fetched"][:10]))}.</p>')
    body = (f'{crumb}<div class="ld-hero mp-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(lede)}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#quote">Check a quote</a><a class="st-btn2" href="#all">See every material</a></div></div>'
            f'{tiles}'
            f'<section class="block" id="quote" aria-labelledby="quote-h">{calc_html(d, E)}</section>'
            f'<section class="block" id="moves"><h2>Where prices moved in a year</h2><p>Change in each price index from {mlabel(ym_add(d["latest"], -12))} to {L}, largest rise first.</p>{diverging(d, E, rel)}</section>'
            f'<section class="block" id="all"><h2>Every material</h2>{table(d, E, rel)}'
            f'<div class="mp-dl"><a class="st-btn2" href="material-price-indexes.csv" download>Download every month (CSV)</a>'
            f'<span class="asof" style="margin:0">{len(d["mats"])} series, {E(mlabel(d["mats"][0]["obs"][0][0]))} to {L}, with a preliminary column</span></div></section>'
            f'<section class="block" id="read"><h2>Read these numbers right</h2>{read_right(d, E)}</section>'
            '<section class="block"><h2>How this page is made</h2>' + "".join(f"<p>{E(x)}</p>" for x in METHOD) + '</section>'
            f'{M.faq_block(fq)}'
            '<p class="rl-act"><a class="btn" href="#quote">Check a quote</a> <a class="st-btn2" href="material-price-indexes.csv" download>Download the CSV</a></p>')
    return (head_html(M, E, p["title"], p["desc"], url, rel, M.ld_tags(crumb_ld, app_ld, ds_ld, faq_ld), robots) + body
            + foot_html(M, E, rel, d) + calc_js(d) + "</body></html>")


SOURCE_NAMES = {"wp.item": "BLS's list of producer price index items", "producerpriceindexconcrete": "BLS's concrete and related products index table",
                "ready-mix-concrete-indexes": "BLS's notice on regional ready-mix concrete indexes"}


def source_link(src, E):
    """series.json titleSource ("host/path (what it is), read <date>") as a link with plain words."""
    path = src.split(" (")[0].strip()
    name = next((v for k, v in SOURCE_NAMES.items() if k in path), "BLS's own pages")
    return f'<a href="https://{E(path)}">{E(name)}</a>'


def sub_html(p, m, d):
    import make_site as M
    E = M.E
    rel = "../../"
    url = M.BASE + p["slug"] + "/" + m["slug"] + "/"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    L = mlabel(m["last"][0])
    first = m["obs"][0]
    since = pct(first[1], m["last"][1])
    h1 = f'{m["title"]} price index'
    title = f'{m["title"]} Price Index: Change Since Your Quote | ProofNotFluff'
    desc = (f'BLS producer price index for {m["title"].lower()}, {m["area"]}: {m["last"][1]:,.1f} in {L}, {move_words(m["m1"])} on the month and '
            f'{move_words(m["y12"])} on a year. Free calculator, chart and CSV.')
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], p["slug"] + "/"), (m["title"], None)])
    lede = (f'The {m["area"]} producer price index for {m["title"].lower()} was {m["last"][1]:,.1f} in {L}, '
            f'{move_words(m["m1"])} on the month and {move_words(m["y12"])} on {mlabel(ym_add(m["last"][0], -12))}. Bought by {m["buyers"] if m["buyers"][1:2].isupper() else m["buyers"][0].lower() + m["buyers"][1:]}.')
    tiles = ('<div class="tiles ld-tiles mp-tiles">'
             f'<div class="tile key"><div class="lab">Index, {L}</div><div class="val">{m["last"][1]:,.1f}</div><div class="sub" style="color:var(--band-text)">{"preliminary" if "P" in m["last"][2] else "final"}</div></div>'
             f'<div class="tile"><div class="lab">1 month</div><div class="val">{pct_txt(m["m1"])}</div><div class="sub">since {mlabel(ym_add(m["last"][0], -1))}</div></div>'
             f'<div class="tile"><div class="lab">12 months</div><div class="val">{pct_txt(m["y12"])}</div><div class="sub">since {mlabel(ym_add(m["last"][0], -12))}</div></div>'
             f'<div class="tile"><div class="lab">Since {mlabel(first[0])}</div><div class="val">{pct_txt(since)}</div><div class="sub">index {first[1]:,.1f} then</div></div></div>')
    rows = lambda os_: "".join(f'<tr><th scope="row">{mlabel(o[0])}{P(o, E)}</th><td>{o[1]:,.3f}</td>'
                               f'<td>{pct_txt(pct(m["at"][ym_add(o[0], -1)][1], o[1])) if ym_add(o[0], -1) in m["at"] else "n/a"}</td>'
                               f'<td>{pct_txt(pct(m["at"][ym_add(o[0], -12)][1], o[1])) if ym_add(o[0], -12) in m["at"] else "n/a"}</td></tr>' for o in os_)
    thead = '<thead><tr><th scope="col">Month</th><th scope="col">Index</th><th scope="col">1 month</th><th scope="col">12 months</th></tr></thead>'
    newest = list(reversed(m["obs"]))
    tbl = (f'<div class="mp-tw" role="region" aria-label="{E(m["title"])} index by month, last 24 months" tabindex="0"><table class="mp-t">{thead}<tbody>{rows(newest[:24])}</tbody></table></div>'
           + (f'<details class="mp-more"><summary>Show {len(newest) - 24} earlier months</summary><div class="mp-tw" role="region" aria-label="{E(m["title"])} index, earlier months" tabindex="0">'
              f'<table class="mp-t">{thead}<tbody>{rows(newest[24:])}</tbody></table></div></details>' if len(newest) > 24 else "")
           + '<p class="asof"><abbr class="mp-p" title="Preliminary">P</abbr> marks a preliminary month BLS can still revise. n/a: BLS has no value for the month compared.</p>')
    same = [x for x in d["mats"] if x["group"] == m["group"] and x is not m]
    rel_links = ('<ul class="mp-rel">' + "".join(f'<li><a href="../{E(x["slug"])}/">{E(x["title"])}</a></li>' for x in same) + '</ul>') if same else ""
    about = (f'<p>BLS series <span class="mp-id">{E(m["id"])}</span>, "{E(m["title"])}": producer price index by commodity, {m["area"]}, not seasonally adjusted. '
             f'The series ID and title are BLS\'s own, as listed in {source_link(m["titleSource"], E)}. '
             'Anyone can look up the same numbers on bls.gov with this ID.</p>')
    body = (f'{crumb}<div class="ld-hero mp-hero"><p class="eyebrow">BLS producer price index</p><h1>{E(h1)}</h1><p class="lede">{E(lede)}</p>'
            '<div class="ld-heroact rl-act"><a class="btn" href="#quote">Check a quote</a><a class="st-btn2" href="#months">See every month</a></div></div>'
            f'{tiles}'
            f'<section class="block" id="chart"><h2>{E(m["title"])} index since {mlabel(first[0])}</h2>{line_chart(m, E)}</section>'
            f'<section class="block" id="quote" aria-labelledby="quote-h">{calc_html(d, E, default=m["slug"])}</section>'
            f'<section class="block" id="months"><h2>Every month</h2>{tbl}'
            f'<div class="mp-dl"><a class="st-btn2" href="{E(m["slug"])}.csv" download>Download this series (CSV)</a>'
            f'<a class="st-btn2" href="../#all">All {len(d["mats"])} materials</a></div></section>'
            f'<section class="block"><h2>About this index</h2>{about}{read_right(d, E)}</section>'
            + (f'<section class="block"><h2>More in {E(m["group"].lower())}</h2>{rel_links}</section>' if rel_links else "")
            + '<p class="rl-act"><a class="btn" href="#quote">Check a quote</a> <a class="st-btn2" href="../">Every material</a></p>')
    js = calc_js(d).replace("var root=document.querySelector('[data-mp-calc]');", "var root=document.querySelector('[data-mp-calc]');if(root)root.setAttribute('data-default'," + json.dumps(m["slug"]) + ");")
    return (head_html(M, E, title, desc, url, rel, M.ld_tags(crumb_ld), robots) + body + foot_html(M, E, rel, d) + js + LINE_JS + "</body></html>")


def extra_pages(p):
    d = load(p)
    if not d:
        return []
    out = [("material-price-indexes.csv", csv_text(d["mats"]))]
    for m in d["mats"]:
        out.append((f'{m["slug"]}/index.html', sub_html(p, m, d)))
        out.append((f'{m["slug"]}/{m["slug"]}.csv', csv_text([m])))
    return out


# ------------------------------------------------------------------ self checks
def selftest():
    sys.path.insert(0, HERE)
    import make_site as M, tempfile, shutil, re
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("slug") == SLUG][0]
    tmp = tempfile.mkdtemp(dir=ROOT)
    try:
        obs = lambda base, step, last_p=2: [[ym_add("2025-01", i), round(base + step * i, 3), "P" if i >= 21 - last_p else ""] for i in range(21)]
        series = [{"id": "WPU081", "title": "Lumber", "slug": "lumber", "group": "Wood", "buyers": "Framers", "titleSource": "x (y)"},
                  {"id": "WPU10260314", "title": "Copper wire and cable", "slug": "copper-wire-and-cable", "group": "Metals and wire", "buyers": "Electricians", "titleSource": "x (y)"},
                  {"id": "WPU13330101B", "title": "Midwest region ready-mix concrete", "slug": "midwest-ready-mix-concrete", "group": "Concrete and masonry", "buyers": "Concrete", "titleSource": "x (y)"}]
        ppi = {"source": {"fetchedAt": "2026-10-27T13:00:00-05:00", "footnotes": {"P": "Preliminary."}}, "latest": "2026-09",
               "series": [{"id": "WPU081", "title": "Lumber", "obs": obs(300, -2)}, {"id": "WPU10260314", "title": "Copper wire and cable", "obs": obs(500, 5)},
                          {"id": "WPU13330101B", "title": "Midwest region ready-mix concrete", "obs": obs(200, 1)}]}
        json.dump(ppi, open(os.path.join(tmp, "ppi.json"), "w"))
        json.dump({"series": series}, open(os.path.join(tmp, "series.json"), "w"))
        json.dump({"releases": [["2099-01", "2099-02-12"]]}, open(os.path.join(tmp, "schedule.json"), "w"))
        p = dict(spec, dataDir=os.path.relpath(tmp, ROOT))
        d = load(p)
        cu = next(m for m in d["mats"] if m["slug"] == "copper-wire-and-cable")
        assert cu["last"] == ["2026-09", 600.0, "P"] and cu["y12o"][0] == "2025-09", cu["last"]
        assert abs(cu["y12"] - (600 / 540 - 1) * 100) < 1e-9 and pct_txt(cu["y12"]) == "+11.1%", cu["y12"]
        assert pct_txt(next(m for m in d["mats"] if m["slug"] == "lumber")["y12"]) == "-8.5%"   # 260 against 284, 12 steps of -2
        assert next(m for m in d["mats"] if m["slug"] == "midwest-ready-mix-concrete")["area"] == "Midwest region"
        html = page_html(p)
        for bad in DASHES:
            assert bad not in html, "no em or en dashes"
        assert html.count("<h1>") == 1 and 'id="quote"' in html and "Copy this as a sentence" in html
        assert "+11.1%" in html and "$11,111" in html, "worked example matches the math (10,000 x 600 / 540)"
        assert "Feb 12, 2099" in html, "next release date from schedule.json"
        assert "not seasonally adjusted" in html and "not a price quote" in html and "4 months" in html
        assert json.loads(re.search(r'<script type="application/ld\+json">(\{"@context": "https://schema.org", "@type": "FAQPage".*?)</script>', html).group(1))
        ex = dict(extra_pages(p))
        assert ex["material-price-indexes.csv"].splitlines()[0] == "series_id,bls_title,area,month,index,preliminary"
        assert len(ex["material-price-indexes.csv"].splitlines()) == 1 + 3 * 21
        sub = ex["lumber/index.html"]
        assert "Lumber price index" in sub and sub.count('data-pts=') == 2 and "WPU081" in sub and "lumber.csv" in sub and sub.count("<h1>") == 1
        assert "'data-default',\"lumber\"" in sub, "sub-page calculator opens on its own material"
        assert all(b not in sub for b in DASHES)
        os.remove(os.path.join(tmp, "ppi.json"))
        assert "noindex" in page_html(p) and extra_pages(p) == [], "no data: a noindex shell and no sub-pages"
        assert nice_ticks(181.2, 263.9) == [180, 200, 220, 240, 260, 280], nice_ticks(181.2, 263.9)
    finally:
        shutil.rmtree(tmp)
    print("dp_materials selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
