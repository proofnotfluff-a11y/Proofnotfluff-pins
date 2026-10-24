#!/usr/bin/env python3
"""The free weekly sample page for Chicago Restaurant Inspection Leads (site/pages.json kind "restleads", written by
tools/make_site.py, which calls page_html here). Data: permits/inspections-chicago/rest-sample.json (tools/rest_leads.py
--sample), committed by the inspections workflow every Monday.

Public page rule (Oct 2026): the free page never names a business with a failed result. Failed, conditional and repeat
examples show the facility type, community area, date, the City's result and our categories only; the "opening soon"
examples show the business name and address, because a license inspection is a step toward opening. The paid list
(licensed to one business for its own prospecting) names every place.

Until Todd launches, the page spec carries "draft": true, so it is written with noindex and left off the index and the
sitemap; with no "checkout" key it shows the planned price and no buy button.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def _res_cls(r):
    u = (r or "").upper()
    return {"FAIL": "fail", "PASS W/ CONDITIONS": "pwc", "PASS": "pass"}.get(u, "oth")


LOCK_S = ('<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">'
          '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>')


def seat_spec(p):
    """The founding seat offer (move 3, Todd Oct 23 and 24, 2026): shown only once its Gumroad checkout is in site/pages.json
    (seat.checkout), or in the live session's preview build (PNF_SEAT_PREVIEW=1, never committed). Pest control only."""
    seat = p.get("seat") or {}
    if seat.get("checkout") or os.environ.get("PNF_SEAT_PREVIEW") == "1":
        return seat
    return None


def seat_html(p, seat, rel):
    """The offer block: the cap first, seats open, no lock-in, the public-records line, the last 14 days of daily pest
    counts by City inspection date, and the exact phone coverage, all from permits/inspections-chicago/daily.json."""
    import make_site as M
    E = M.E
    d = json.load(open(os.path.join(ROOT, seat["data"]), encoding="utf-8"))
    days, st = d["pestByDate"], d["seat"]
    cap, taken, price = int(seat["seats"]), int(seat.get("taken") or 0), E(str(seat["price"]))
    left = max(cap - taken, 0)
    total = sum(x["pests"] for x in days)
    top = max([x["pests"] for x in days] + [1])
    md = lambda iso: M.nice_date(iso).rsplit(",", 1)[0]          # "Oct 21"
    bars = "".join(
        f'<li><span class="sb-n num">{x["pests"]}</span><span class="sb-b" style="height:{max(2, round(96 * x["pests"] / top))}px"></span>'
        f'<span class="sb-d">{E(md(x["date"]).split(" ")[1])}</span></li>' for x in days)
    rows = "".join(f'<tr><th scope="row">{E(M.nice_date(x["date"]))}</th><td>{x["pests"]}</td></tr>' for x in days)
    rng = f'{E(md(days[0]["date"])).replace(" ", "&nbsp;")} to {E(md(days[-1]["date"])).replace(" ", "&nbsp;")}'
    per_day = f"{total / len(days):.1f}".rstrip("0").rstrip(".")
    phone = (f'A listed phone on <b>{st["withPhone14"]} of {st["places14"]}</b> pest places from the last 14 days ({st["coverage14"]:g}%). '
             'A number is shown only when the business name and street address both match the City record, so some places have none.'
             if st.get("phonesChecked") and st["places14"] else "Phones are checked each morning; this morning's check did not run.")
    co = seat.get("checkout")
    terms = rel + "chicago-pest-daily-members/#/terms"
    top_btn = (f'<p class="sb-top"><a class="btn ld-btnbig" href="{E(co)}" rel="noopener">Take a founding seat, ${price} a month</a></p>'
               if left and co else "")
    if left and co:
        act = (f'<p class="ld-buybtn"><a class="btn ld-btnbig" href="{E(co)}" rel="noopener">Take a founding seat, ${price} a month</a></p>'
               f'<p class="ld-secure">Secure checkout by Gumroad. ${price} is charged at checkout and again each month until you cancel. '
               f'No lock-in: cancel any time from your Gumroad receipt or library and you are not charged again. <a href="{rel}refunds/">Refunds and cancelling</a> · <a href="{E(terms)}">Seat Terms</a></p>')
    elif left:
        act = (f'<p class="ld-buybtn"><span class="btn ld-btnbig sb-off" aria-disabled="true">Take a founding seat, ${price} a month</span></p>'
               '<p class="ld-secure">Preview: the checkout link goes here once the Gumroad tier exists.</p>')
    else:
        act = ('<p class="ld-buybtn"><a class="btn ld-btnbig" href="mailto:hello@proofnotfluff.com?subject=Pest%20seat%20waitlist">'
               'Ask for the next open seat</a></p><p class="ld-secure">All seats are taken. Write to hello@proofnotfluff.com and we will tell you '
               'when one opens.</p>')
    return (f'<section class="block sb" id="seat" aria-labelledby="seatH"><div class="sb-card">'
            '<p class="eyebrow sb-eye">Founding seat for pest control</p>'
            f'<h2 id="seatH">At most {cap} Chicago pest control companies hold a seat at a time.</h2>'
            '<div class="sb-cols"><div class="sb-main">'
            f'<p class="sb-left"><span class="sb-dots" aria-hidden="true">{"".join("<i class=on></i>" if i < left else "<i></i>" for i in range(cap))}</span>'
            f'<b>{left} of {cap} seats open</b></p>'
            f'<p class="sb-terms"><b>No lock-in.</b> ${price} a month, cancel any time.</p>{top_btn}'
            '<p class="sb-lede">The City\'s public records, cleaned and on your members\' page each morning after the City\'s overnight update: the Chicago food '
            'places whose failed or conditional inspection had a pest violation, named, with street address, the City\'s violation codes and the listed '
            'phone when we find one. License inspections and the places under "Who is left out?" are not included.</p>'
            '</div><div class="sb-side">'
            f'<figure class="sb-fig"><figcaption><b>Inspections with a pest violation, by City inspection date, {rng}</b>'
            f'<span>{total:,} failed or conditional inspections in 14 days, about {per_day} a day. The newest days fill in as the City posts results, often a few days after the inspection. A pest violation can be insects or rodents seen, or a gap or record the City says lets pests in; each record says which.</span></figcaption>'
            f'<ol class="sb-chart" aria-hidden="true">{bars}</ol>'
            f'<table class="sr"><caption>Failed or conditional inspections with a pest violation, by City inspection date</caption>'
            f'<thead><tr><th scope="col">Date</th><th scope="col">Inspections</th></tr></thead><tbody>{rows}</tbody></table></figure>'
            f'<p class="sb-phone">{phone}</p>'
            f'<p class="sb-asof">City records through {E(d["throughText"])}, pulled {E(d["asOfText"])}. Refreshed every morning.</p></div></div>'
            '<ul class="sb-get checks"><li>New places each morning, after the City\'s overnight refresh, with the last 14 days kept so a missed morning loses nothing.</li>'
            '<li>Each place: name, street, ZIP, community area, the City\'s result, date and violation codes, failed visits in 90 days, and a link to the City\'s record.</li>'
            '<li>A Call button, called marks and private notes on your phone or computer, and a CSV download.</li></ul>'
            f'<p class="sb-same">The same records reach our weekly list (${E(str(p["price"]))} a month, not capped) each Monday, and a pest control company that asks can get one free morning of this list by email before it decides. A seat gets them each morning.</p>'
            f'{act}</div></section>')


SEAT_CSS = (".sb .sb-card{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);box-shadow:var(--shadow);padding:24px 20px}"
            ".sb .sb-card>p,.sb .sb-get{max-width:68ch;text-wrap:pretty}.sb .sb-fig{max-width:none}"
            ".sb .ld-secure{font-size:14px;color:var(--muted)}.sb .ld-secure a{color:var(--teal)}"
            ".sb .sb-top{margin:4px 0 18px}"
            ".sb .sb-eye{margin:0 0 6px}.sb h2{margin:0 0 10px}"
            ".sb-left{display:flex;align-items:center;gap:10px;margin:0 0 6px;font-size:17px}"
            ".sb-dots{display:inline-flex;gap:5px}.sb-dots i{width:14px;height:14px;border-radius:50%;border:2px solid var(--teal)}.sb-dots i.on{background:var(--teal)}"
            ".sb-terms{margin:0 0 12px;font-size:17px}.sb-lede{margin:0 0 18px;color:var(--ink2)}"
            ".sb-fig{margin:0 0 16px;padding:16px;border:1px solid var(--line);border-radius:12px;background:var(--canvas2)}"
            ".sb-fig figcaption b{text-wrap:balance}.sb-fig figcaption{display:flex;flex-direction:column;gap:2px;margin:0 0 12px}.sb-fig figcaption span{color:var(--muted);font-size:14px}"
            ".sb-chart{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(14,minmax(0,1fr));gap:4px;align-items:end;height:150px}"
            ".sb-chart li{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%;min-width:0}"
            ".sb-chart .sb-b{display:block;width:100%;max-width:28px;background:var(--teal);border-radius:4px 4px 0 0;flex:none}"
            ".sb-chart .sb-n{font-size:12.5px;font-weight:700;color:var(--ink);margin:0 0 3px}"
            ".sb-chart .sb-d{font-size:12px;color:var(--muted);margin:5px 0 0;border-top:1px solid var(--line);width:100%;text-align:center;padding-top:4px}"
            "@media(max-width:420px){.sb-chart{gap:2px}.sb-chart .sb-n,.sb-chart .sb-d{font-size:11px}}"
            ".sb-phone{margin:0 0 4px}.sb-asof{margin:0 0 12px;color:var(--muted);font-size:14px}.sb-get{margin:0 0 12px;padding-left:20px}.sb-get li{margin:0 0 6px}"
            ".sb-same{margin:0 0 6px;color:var(--ink2)}.sb .ld-buybtn{margin-top:16px}"
            ".sb-off{opacity:.55;cursor:not-allowed}"
            # store v2 (design review, Oct 24): the offer and the chart side by side on wide screens, the details under both
            ".sb-cols{display:grid;grid-template-columns:minmax(0,1fr);gap:0 32px;align-items:start}"
            "@media(min-width:960px){.sb-cols{grid-template-columns:minmax(0,1fr) minmax(0,1.05fr)}.sb .sb-lede{margin-bottom:0}}"
            ".sb-get.checks{padding-left:0;margin:18px 0 14px}@media(min-width:960px){.sb-get.checks{grid-template-columns:repeat(3,minmax(0,1fr));gap:12px 24px;max-width:none}}")


def page_html(p):
    import make_site as M
    E = M.E
    d = json.load(open(os.path.join(ROOT, p["data"]), encoding="utf-8"))
    c = d["counts"]
    url = M.BASE + p["slug"] + "/"
    rel = "../"
    price = E(str(p["price"]))
    checkout = p.get("checkout")
    trial = int(p.get("trialDays") or 0) if checkout else 0      # Gumroad free trial (Todd, Oct 22, 9:29 pm)
    faq = list(p["faq"]) + ([["Can I try it before I pay?",
                              f"Yes. Start a {trial}-day free trial on Gumroad: your card goes in at checkout, nothing is charged for {trial} days, "
                              f"then it is ${p['price']} a month until you cancel. Cancel before day {trial} and you pay nothing."]] if trial else [])
    asof = E(d["asOfText"])
    w = d["window"]
    seat = seat_spec(p)
    if seat and seat.get("checkout"):            # "every Monday" headlines become daily and weekly once the seat tier exists
        p = dict(p, eyebrow=seat["eyebrow"], cta=dict(p["cta"], title=seat["ctaTitle"]))
    if seat:
        faq = [[q, a + " The daily pest list also leaves out license inspections, the check the City does before it issues a food license."]
               if q == "Who is left out?" else [q, a] for q, a in faq]
        faq = faq + [["What is the founding seat?",
                      f"A ${seat['price']} a month membership for Chicago pest control companies only, capped at {seat['seats']} companies at a time. "
                      "Each morning, after the City's overnight update, your members' page shows the food places whose failed or conditional "
                      "inspection had a pest violation, named, with the listed phone when the name and address match, and keeps the last 14 days. "
                      "It renews monthly until you cancel. No lock-in: cancel any time from your Gumroad receipt or library. The same records reach "
                      "the weekly list each Monday."]]

    keyof = {c["label"]: c["key"] for c in d.get("categories", [])}

    def card_anon(x):
        cats = ", ".join(x["categories"]) or "None in a category"
        kind = x["type"] if x["type"] not in ("", "Not given") else "Food business"
        keys = " ".join(keyof.get(k, "") for k in x["categories"]).strip()
        return (f'<article class="ld-proj" data-cats="{E(keys)}"><p class="ld-pill rp-{_res_cls(x["result"])}">City result: {E(x["result"])}</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(("An " if kind[:1].lower() in "aeiou" else "A ") + kind.lower())} in {E(x["area"])}</span></div>'
                f'<p class="rl-lock">{LOCK_S}Name and address hidden: on the members\' list</p>'
                f'<dl class="ld-meta"><div><dt>Categories</dt><dd>{E(cats)}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {M.nb(x["inspectionType"])}</dd></div></dl></article>')

    def card_open(x):
        return (f'<article class="ld-proj" data-cats="open"><p class="ld-pill rp-{_res_cls(x["result"])}">License inspection: {E(x["result"])}</p>'
                f'<div class="ld-ptop"><span class="ld-cost" style="font-size:20px">{E(x["name"])}</span><span class="ld-type">{E(x["type"])}</span></div>'
                f'<dl class="ld-meta"><div><dt>Where</dt><dd>{E(x["address"])}, {E(x["area"])}</dd></div>'
                f'<div><dt>Inspected</dt><dd>{E(M.nice_date(x["date"]))}, {M.nb(x["inspectionType"])}</dd></div></dl></article>')

    notify = p.get("notify") or "mailto:hello@proofnotfluff.com?subject=Chicago%20Restaurant%20Inspection%20Leads%3A%20tell%20me%20when%20it%20opens"

    def buy(cls="btn ld-btnbig"):
        """The primary action: the checkout once the product is on sale, until then a note to the ProofNotFluff mailbox."""
        if checkout:
            return f'<a class="{cls}" href="{E(checkout)}" rel="noopener">' + (f"Start your {trial}-day free trial" if trial else f"Get the full list, ${price} a month") + '</a>'
        return f'<a class="{cls}" href="{E(notify)}">Tell me when it opens</a>'

    lede = (f'{c["flagged"]:,} Chicago food businesses failed or passed with conditions with a pest, hood, grease trap or cleaning violation in the last 30 days, and {c["opening"]:,} had '
            f'the license inspection Chicago does before it issues a food license. {E(p["lede"])}')
    sub_link = (f'<a class="ld-textlink ld-trialbtn" href="{E(checkout)}" rel="noopener">Try {trial} days free, then ${price} a month</a>' if trial else
                f'<a class="ld-textlink" href="{E(checkout)}" rel="noopener">Subscribe, ${price} a month</a>' if checkout else
                f'<a class="ld-textlink" href="{E(notify)}">Tell me when it opens</a>')
    seat_note = (f' Pest control? <a href="#seat">A separate ${seat["price"]} daily pest list has at most {seat["seats"]} seats</a>.' if seat and seat.get("checkout") else "")
    every = "Full list every Monday." if seat and seat.get("checkout") else "New list every Monday."
    hero_act = (f'<div class="ld-heroact rl-act" id="ldHeroCta"><a class="btn ld-btnbig" href="#sample">See this week\'s free sample</a>{sub_link}</div>'
                + (f'<p class="ld-heronote">{every} Card at checkout, nothing charged for {trial} days. No lock-in, cancel any time.{seat_note}</p>' if trial else
                   '<p class="ld-heronote">New list every Monday. Cancel any time.</p>' if checkout else
                   f'<p class="ld-heronote">${price} a month when it opens. New list every Monday.</p>'))
    bc = c["byCat"]
    tiles = (f'<div class="tiles ld-tiles">'
             f'<div class="tile key"><div class="lab">Failed or conditional</div><div class="val">{c["flagged"]:,}</div><div class="sub">last 30 days</div></div>'
             f'<div class="tile"><div class="lab">Opening soon</div><div class="val">{c["opening"]:,}</div><div class="sub">license inspections</div></div>'
             f'<div class="tile"><div class="lab">Failed more than once</div><div class="val">{c["repeat"]:,}</div><div class="sub">2 or more fails in 90 days</div></div>'
             f'<div class="tile"><div class="lab">New this week</div><div class="val">{c["new"]:,}</div><div class="sub">inspected in the last 7 days</div></div></div>'
             f'<p class="asof">The City\'s own public inspection records, cleaned and sorted by the violation that fits your trade. City records through {E(d["throughText"])}, pulled {asof}. Refreshed every Monday.</p>')
    tabs = [("all", "All", c.get("places", c["flagged"] + c["opening"]), "on this week's lists: failed or conditional in our four categories, or a license inspection."),
            ("hood", "Hood and exhaust", bc["hood"], "failed or passed with conditions with a hood or exhaust violation."),
            ("pests", "Pests", bc["pests"], "failed or passed with conditions with a pest violation."),
            ("drain", "Grease trap", bc["drain"], "failed or passed with conditions with a grease trap or drain violation."),
            ("clean", "Kitchen cleaning", bc["clean"], "failed or passed with conditions with a cleaning violation."),
            ("open", "Opening soon", c["opening"], "had the license inspection the City does before it issues a food license. This sample names only places that passed.")]
    tab_btns = "".join(f'<button type="button" aria-pressed="{"true" if k == "all" else "false"}" data-t="{k}" data-n="{n:,}" data-b="{E(b)}">'
                       f'{E(lab)}<span class="c">{n:,}</span></button>' for k, lab, n, b in tabs)
    ex = d["examples"]
    seen, anon = set(), []
    for x in ex.get("flagged", []) + ex.get("repeat", []):   # repeat fails are failed records too; each record shows once
        k = (x.get("area"), x.get("date"), x.get("inspectionType"), tuple(x.get("categories", [])))
        if k not in seen:
            seen.add(k); anon.append(x)
    cards = "".join(card_anon(x) for x in anon) + "".join(card_open(x) for x in ex["opening"])
    sample = (f'<section class="block" id="sample"><h2>This week\'s free sample</h2>'
              '<p>Real records from this week\'s pull. Failed and conditional places show the record without the name; the members\' list names '
              'each place, with its address, its 24-month City inspection history and the City\'s violation codes. Places that passed a license '
              'inspection are named here, because a license inspection is a step toward opening.</p>'
              f'<div class="rl-tabs" role="group" aria-label="Show records for" id="rlTabs" hidden>{tab_btns}</div>'
              f'<p class="rl-tabnote" id="rlNote" aria-live="polite"><b>{tabs[0][2]:,} places</b> {E(tabs[0][3])} This free sample shows {len(anon) + len(ex["opening"])}.</p>'
              f'<div class="ld-list rl3" id="rlList">{cards}</div>'
              '<p class="rl-empty" id="rlEmpty" hidden>No place in this week\'s free sample has this category. Members see every one.</p>'
              f'<p class="rl-more" id="rlMore">Members see every place on all three lists, named, with address, the City\'s violation codes and 24 months of history. '
              + (f'<a href="{E(checkout)}" rel="noopener">Try {trial} days free, then ${price} a month</a>.' if trial else
                 f'<a href="{E(checkout)}" rel="noopener">Subscribe, ${price} a month</a>.' if checkout else "") + '</p></section>')
    links = "".join(f'<li><a href="{rel}{E(l[0])}/">{E(l[1])}</a></li>' for l in p.get("links", []))
    method = ('<section class="block"><h2>How to use this list</h2>' + "".join(f"<p>{E(x)}</p>" for x in p["method"])
              + (f'<p>Price the visit before you call:</p><ul class="qa-rel">{links}</ul>' if links else "") + "</section>")
    later = ""
    if p.get("kitForm"):
        later = (f'<div class="ld-later"><p><b>Not ready yet?</b> Leave your email and we will let you know when the list adds new areas or features.</p>'
                 f'<form class="ld-form" action="https://app.kit.com/forms/{E(p["kitForm"])}/subscriptions" method="post"><label for="ldEmail">Email</label>'
                 '<div class="ld-frow"><input id="ldEmail" name="email_address" type="email" required autocomplete="email" placeholder="you@company.com"><button class="btn" type="submit">Keep me posted</button></div></form>'
                 '<small class="ld-note">Unsubscribe in one click. Your email is stored with Kit, our email provider, and never sold.</small></div>')
    if checkout:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta ld-buy"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-buybtn">{buy()}</p>'
                    + (f'<p class="ld-secure">Secure checkout by Gumroad. Your card goes in at checkout and nothing is charged for {trial} days. '
                       f'Then it is ${price} a month until you cancel. Cancel in your Gumroad library before day {trial} and you pay nothing. '
                       f'<a href="{rel}refunds/">Refunds and cancelling</a></p>' if trial else
                       f'<p class="ld-secure">Secure checkout by Gumroad. Cancel any time. <a href="{rel}refunds/">Refunds and cancelling</a></p>')
                    + f'</div>{later}</div></section>')
    else:
        cta_html = (f'<section class="block" id="ldCta"><div class="cta ld-cta"><div><h2>{E(p["cta"]["title"])}</h2><p>{E(p["cta"]["text"])}</p>'
                    f'<p class="ld-price">${price} a month when it opens.</p><p class="ld-buybtn">{buy()}</p></div></div></section>')
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), ("Shop", "shop/"), (p["h1"], None)])
    body = (f'{crumb}<div class="ld-hero"><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{lede}</p>{hero_act}</div>{tiles}'
            # store v2 (design review, Oct 24, 2026): the free sample comes first and the $149 seat right after it; the hero note
            # still links pest control owners straight to #seat
            f'{sample}{seat_html(p, seat, rel) if seat else ""}{method}{cta_html}{M.guides_block(p["slug"], rel=rel)}{M.faq_block(faq)}')
    body = M.otp_bar(body)
    sbar = ((f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>{trial} days free</b><span> · then ${price} a month</span></p>'
             f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Try free</a></div></div>') if trial else
            (f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>${price} a month</b><span> · <span class="ld-sbl">full list </span>{"every week" if seat and seat.get("checkout") else "every Monday"}</span></p>'
             f'<a class="btn" href="{E(checkout)}" rel="noopener" tabindex="-1">Subscribe</a></div></div>') if checkout else "")
    script = r"""<script>(function(){var tb=document.getElementById('rlTabs');if(tb){tb.hidden=false;
var bs=[].slice.call(tb.querySelectorAll('button')),cs=[].slice.call(document.querySelectorAll('#rlList .ld-proj')),
note=document.getElementById('rlNote'),empty=document.getElementById('rlEmpty');
function pick(t){var n=0;bs.forEach(function(b){var on=b.dataset.t===t;b.setAttribute('aria-pressed',String(on));});
cs.forEach(function(c){var ok=t==='all'||(' '+c.dataset.cats+' ').indexOf(' '+t+' ')>=0;c.hidden=!ok;if(ok)n++});empty.hidden=n>0;
bs.forEach(function(b){if(b.dataset.t===t)note.innerHTML='<b>'+b.dataset.n+' places</b> '+b.dataset.b+(n?' This free sample shows '+n+'.':'')})}
bs.forEach(function(b){b.addEventListener('click',function(){pick(b.dataset.t)})});
var q=(location.search.match(/[?&]trade=([a-z]+)/)||[])[1];if(q&&bs.some(function(b){return b.dataset.t===q}))pick(q)}
var bar=document.getElementById('ldBar'),hero=document.getElementById('ldHeroCta'),cta=document.getElementById('ldCta');
if(!bar||!hero||!cta||!('IntersectionObserver' in window))return;
var hv=true,cv=false,sv=false,link=bar.querySelector('a');
function set(){var on=!hv&&!cv&&!sv;bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',String(!on));link.tabIndex=on?0:-1}
var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.target===hero)hv=e.isIntersecting;else if(e.target.id==='seat')sv=e.isIntersecting;else cv=e.isIntersecting});set()});
var st=document.getElementById('seat');if(st)io.observe(st);io.observe(hero);io.observe(cta)})();</script>"""
    prod = next((x for x in M.store_products() if x["key"] == p["slug"]), None)
    ld = (M.ld_tags({"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
          crumb_ld, M.product_ld(prod, url) if prod else None, M.page_ld(p, url) if M.is_live(p) else None)
          # small grey text darkened to pass WCAG AA on the warm canvas (axe, Oct 2026); scoped to this page only
          + "<style>.ld-page .asof,.ld-page footer p{color:var(--muted)}"
          ".ld-pill.rp-fail{background:var(--rp-fail-bg);color:var(--rp-fail)}.ld-pill.rp-pwc{background:var(--rp-pwc-bg);color:var(--rp-pwc)}"
          ".ld-pill.rp-pass{background:var(--chip-near-bg);color:var(--chip-near)}.ld-pill.rp-oth{background:var(--chip-insp-bg);color:var(--chip-insp)}"
          ".rl-act{margin:18px 0 24px}.ld-page .ld-tiles .tile .lab{letter-spacing:.04em;overflow-wrap:anywhere}"
          "@media(max-width:600px){.ld-page .ld-tiles .tile .lab{font-size:11.5px;letter-spacing:.02em;white-space:normal}}"
          ".rl3 .ld-pill{margin:0 0 10px}.rl3 .ld-ptop{margin:0 0 12px}"
          ".rl-lock{display:flex;align-items:center;gap:6px;margin:0 0 6px;font-size:13px;color:var(--muted)}.rl-lock svg{flex:none}"
          "@media(min-width:1000px){.ld-list.rl3{grid-template-columns:repeat(4,minmax(0,1fr))}}"
          ".rl-trades{list-style:none;margin:14px 0 0;padding:0;background:var(--card);border:1px solid var(--line);border-radius:12px}"
          ".rl-trades li{display:flex;justify-content:space-between;align-items:center;gap:16px;padding:12px 16px;border-top:1px solid var(--rule)}"
          ".rl-trades li:first-child{border-top:0}.rl-trades .nm{font-weight:600;color:var(--ink)}"
          ".rl-trades .nm small{display:block;font-size:13.5px;font-weight:400;color:var(--muted);margin-top:2px}"
          ".rl-trades .n{font:700 18px/1 Poppins,system-ui,sans-serif;color:var(--ink);font-variant-numeric:tabular-nums}"
          # design director round 2: the trade card is the FAQ's measure (C1), the price line clears the button (C2),
          # and no heading or question leaves one word alone on a phone (C3)
          ".rl-trades{max-width:760px}section.block .rl-trades li{max-width:none}"
          ".ld-page .ld-cta p.ld-buybtn{margin-top:16px}"
          ".ld-page h2,.ld-page summary{text-wrap:balance}" + (SEAT_CSS if seat else "") + "</style>")
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    src = d["source"]
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>Source: {E(src["name"])} ({E(src["url"])}), City records through {E(d["throughText"])}, pulled {asof}. Filtered by ProofNotFluff: '
            'inspections of the last 30 days at food businesses, less the places under "Who is left out?" above, with a City result of Fail or '
            'Pass w/ Conditions and a violation in one of '
            'four categories, a license inspection, or two failed inspections in 90 days. Categories are ProofNotFluff\'s reading of the City\'s '
            'violation codes; inspector notes are not republished. A record repeats the City\'s result on that date; it does not say a place is '
            'clean, safe or open today. No business named here has endorsed or works with ProofNotFluff. Public information for planning sales calls; '
            'not legal or business advice and no promise of work.</p>'
            f'<p>{E(M.CITY_DISCLAIMER["Chicago"])}</p>'
            '<p>Made by ProofNotFluff with AI assistance from public City data. The page counts visits with Cloudflare Web Analytics, which sets no '
            f'cookies.</p></div></footer>\n{sbar}\n{script}\n</body></html>')
    return (M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=ld, bodycls=' class="ld-page' + (' has-sbar' if sbar else '') + '"',
                          robots=robots, analytics=M.analytics_tag()) + body + foot)


def selftest():
    import re, sys, tempfile
    sys.path.insert(0, HERE)
    import rest_leads, rest_xlsx
    s = rest_leads.sample(rest_leads.build(rest_xlsx._planted()))
    tmp = tempfile.mkdtemp()
    f = os.path.join(tmp, "s.json")
    json.dump(s, open(f, "w"))
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json")))["pages"] if x.get("kind") == "restleads"][0]
    p = dict(spec, data=os.path.relpath(f, ROOT))
    html = page_html(p)
    assert 'content="noindex' in html or not spec.get("draft"), "draft page must be noindex"
    assert "Acme" not in html and "Fry House" not in html, "the free page names a place with a failed result"
    assert "New Place" in html, "openings are named"
    assert "Tell me when it opens" in html or "Get the full list, $" in html or "-day free trial</a>" in html, "a primary action on the page"
    if spec.get("checkout") and spec.get("trialDays"):   # a trial is never offered without its terms next to it (Legal, trial review item 9)
        assert html.count("nothing is charged for") >= 2 and "Can I try it before I pay?" in html, "trial terms on the page"
    assert "one’s own risk" in html or "one's own risk" in html.replace("&#x27;", "'")
    assert "—" not in html
    faq = dict((q, a) for q, a in spec["faq"])
    assert faq.get("Who is left out?") == rest_leads.LEFT_OUT, "the free page states the shared left-out sentence (holdout round 2)"
    assert "named after a person" not in html and "full name" not in html, "one wording for the person-name rule"
    for w in ("dirty", "filthy", "infested", "violator", "offender"):
        assert w not in re.sub(r"<[^>]+>", " ", html).lower(), w
    # the founding seat offer (move 3): hidden until its checkout exists, the cap as the headline, counts from daily.json
    # (Oct 24: the seat now has its checkout in site/pages.json, so the no-checkout case is planted by blanking it)
    assert 'id="seat"' not in page_html(dict(p, seat=dict(spec["seat"], checkout=""))) or os.environ.get("PNF_SEAT_PREVIEW") == "1", "seat shown with no checkout"
    days = [{"date": f"2026-10-{10 + i:02d}", "pests": [0, 0, 0, 4, 8, 5, 4, 0, 0, 7, 11, 4, 1, 1][i], "restaurant": 0} for i in range(14)]
    dj = os.path.join(tmp, "daily.json")
    json.dump({"pestByDate": days, "throughText": "Oct 23, 2026", "asOfText": "Oct 24, 2026", "seat": {"places14": 42, "withPhone14": 29, "coverage14": 69.0, "phonesChecked": True}}, open(dj, "w"))
    live = page_html(dict(p, seat=dict(spec["seat"], data=os.path.relpath(dj, ROOT), checkout="https://example.gumroad.com/l/seat")))
    t = re.sub(r"<[^>]+>", " ", live)
    assert '<h2 id="seatH">At most 3 Chicago pest control companies hold a seat at a time.</h2>' in live, "the cap is the seat headline"
    for want in ("3 of 3 seats open", "No lock-in.", "$149 a month", "The City's public records, cleaned", "each morning after the City's overnight update", "License inspections",
                 "29 of 42", "(69%)", "45 failed or conditional inspections in 14 days, about 3.2 a day", "not capped", "one free morning", "Take a founding seat, $149 a month",
                 "charged at checkout and again each month", "Refreshed every morning", "A separate $149 daily pest list"):
        assert want in t.replace("&#x27;", "'").replace("&#39;", "'"), want
    assert live.count("Take a founding seat, $149 a month</a>") == 2, "a second seat button under the price line"
    assert live.count('<span class="sb-b"') == 14 and "height:96px" in live, "14 bars, the tallest at full height"
    assert "Free sample, weekly list, daily pest seat" in live and "cited pests" not in live and "Get the full list every week" in live, "headlines daily and weekly once the seat is on sale"
    assert "every Monday" not in live.split("<main")[1].split('id="sample"')[0].replace("Full list every Monday.", "").replace("Refreshed every Monday.", ""), "bare Monday headline"
    full = page_html(dict(p, seat=dict(spec["seat"], data=os.path.relpath(dj, ROOT), checkout="https://example.gumroad.com/l/seat", taken=3)))
    assert "0 of 3 seats open" in full and "Take a founding seat" not in full and 'class="sb-top"' not in full and "Ask for the next open seat" in full, "a full cap sells no seat"
    assert "—" not in live and "–" not in live
    print("rest_site selftest ok (sample page and the founding seat offer)")


if __name__ == "__main__":
    selftest()
