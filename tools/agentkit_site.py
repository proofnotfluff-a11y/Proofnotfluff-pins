#!/usr/bin/env python3
"""Unattended Agent Kit: the offer page and waitlist (site/pages.json kind "agentkit", written by tools/make_site.py,
which calls page_html here). Todd's go, Oct 26, 2026, 12:38 pm (coo/DECISIONS-2026-10-26.md, coo/OPPORTUNITIES.md,
scoreboard todo agent-kit-test): a side test, offer and waitlist before any build.

A new product, page type and price, so the page is a draft: noindex, off the sitemap, index, hub and every link list,
until Todd says go in a live chat (coo/CONSTITUTION.md section 2). The waitlist form shows only once the spec has
"kitForm" (the Kit form number Todd makes); before that the button reads "Waitlist opens soon". The free lite
version's link shows only once the spec has "liteUrl" (the public GitHub repo, Todd's step).

Every line of terminal output on the page is real output of the lite kit (launches/agent-kit/lite.tar.gz), captured
on the date in "proofAsOf"; --selftest reruns the lite kit and fails if the page shows a line the kit no longer prints.

Usage: python3 tools/agentkit_site.py --selftest
"""
import json, os, re, shutil, subprocess, sys, tarfile, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LITE = os.path.join(ROOT, "launches", "agent-kit", "lite.tar.gz")

CSS = ("<style>"
       ".ak-note{margin:10px 0 0;font-size:14.5px;color:var(--ink2)}"
       ".ak-term{margin:0;border-radius:12px;background:#10141c;border:1px solid #2c3343;overflow:hidden;min-width:0}"
       ".ak-term figcaption{display:flex;align-items:center;gap:8px;padding:10px 14px;border-bottom:1px solid #2c3343;"
       "font:600 13px system-ui,sans-serif;color:#c9cfdb}"
       ".ak-term figcaption i{display:inline-block;width:9px;height:9px;border-radius:50%;flex:none}"
       ".ak-term.ok figcaption i{background:#6cc0b6}.ak-term.stop figcaption i{background:#ef8c6b}"
       ".ak-term pre{margin:0;padding:14px;overflow-x:auto;font:13px/1.6 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:#e8ebf0;white-space:pre-wrap;overflow-wrap:normal}"
       ".ak-term pre .c{display:block;white-space:nowrap}@media(min-width:900px){.ak-term pre{font-size:12px}}"
       ".ld-hero .eyebrow,.ak-hero h1{text-wrap:balance}.ak-hero h1{margin-bottom:20px}"
       ".ak-side{display:grid;gap:12px;min-width:0}.ak-side .ak-term{display:none}@media(min-width:1000px){.ak-side .ak-term{display:block}}"
       ".ak-side .ak-tree{margin:0}.ak-side figure{margin:0}.ak-side .ak-files figcaption{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px}"
       ".ak-card h3,.ak-steps h3{color:var(--ink);font-size:18px;margin-bottom:8px}"
       ".ak-box{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:6px 20px 18px;margin-top:12px}"
       "@media(min-width:900px){.ak-box .ak-list.cols{columns:2;column-gap:32px}.ak-box .ak-list.cols li{break-inside:avoid}}"
       ".ak-boxfoot{display:flex;flex-wrap:wrap;align-items:center;gap:10px 18px;margin-top:14px;padding-top:14px;border-top:1px solid var(--rule)}"
       ".block .ak-boxfoot p{margin:0;font-weight:700;color:var(--ink)}"
       ".ak-two>div{display:flex;flex-direction:column}.ak-two .asof{margin-top:auto;padding-top:14px}"
       ".ak-page .otp{background:var(--canvas);-webkit-backdrop-filter:none;backdrop-filter:none;border-bottom:1px solid var(--line)}"
       ".ak-page .rl-act{margin:24px 0 0}"
       "@media(prefers-color-scheme:dark){.ak-wait .cta{background:var(--card);border-color:var(--line)}}"
       ".ak-hero{display:grid;gap:28px;align-items:center}"
       "@media(min-width:1000px){.ak-hero{grid-template-columns:minmax(0,1.45fr) minmax(0,1fr)}}"
       ".ak-hero .ld-heroact .st-btn2{min-height:52px;padding:0 20px;border-radius:12px;font-size:17px}"
       ".ak-tree{margin:12px 0 0;padding:12px 14px;border-radius:10px;background:var(--canvas2);border:1px solid var(--line);"
       "font:12.5px/1.65 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--ink);white-space:pre;overflow-x:auto}"
       ".ak-tree:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       "@media(max-width:899px){.ak-page main{padding-bottom:76px}}@media(min-width:900px){.ak-page .ld-sbar{display:none}}"
       ".ak-term pre:focus-visible{outline:3px solid #9fe0d7;outline-offset:-3px}"
       ".ak-term .nw{white-space:nowrap}.ak-term .c{color:#9aa1ae}.ak-term .g{color:#8fd8ce}.ak-term .r{color:#f6ad94}"
       ".ak-terms{display:grid;gap:14px;margin-top:12px}@media(min-width:900px){.ak-terms{grid-template-columns:repeat(3,minmax(0,1fr))}}"
       ".ak-grid{display:grid;gap:14px;margin-top:12px;padding:0;list-style:none}@media(min-width:720px){.ak-grid{grid-template-columns:1fr 1fr}}"
       ".ak-card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}"
       ".ak-card h3{margin:0 0 6px;font-size:17px}.block .ak-card p{margin:0;color:var(--ink2);max-width:none}"
       ".ak-steps{counter-reset:ak;display:grid;gap:12px;margin:12px 0 0;padding:0;list-style:none}"
       "@media(min-width:900px){.ak-steps{grid-template-columns:repeat(3,minmax(0,1fr))}}"
       ".ak-steps li{counter-increment:ak;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}"
       ".ak-steps li::before{content:counter(ak);display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;"
       "border-radius:50%;background:var(--teal-tint);color:var(--teal-ink);font-weight:700;margin-bottom:8px}"
       ".ak-steps h3{margin:0 0 4px;font-size:17px}.block .ak-steps p{margin:0;color:var(--ink2);max-width:none}"
       ".ak-list{margin:12px 0 0;padding-left:22px}.ak-list li{margin:7px 0}"
       ".ak-two{display:grid;gap:16px;grid-template-columns:minmax(0,1fr)}@media(min-width:900px){.ak-two{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}}"
       ".ak-two>div{min-width:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px}"
       ".ak-two h2{margin-top:0}"
       ".ak-facts{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));margin-top:12px}"
       ".block .ld-cta .ak-price{margin:10px 0 0;color:#fff;font-weight:600}"
       ".block .ld-cta .ak-fine{margin-top:10px;font-size:13px;color:var(--band-text)}"
       ".ak-wait .ld-form{margin-top:14px;max-width:560px}"
       "</style>")


def load_lite_proof():
    """Rerun the lite kit in a throwaway folder: the clean pass, the rules line deleted from the router, and the
    gate's comment check switched off."""
    out = {}
    with tempfile.TemporaryDirectory() as tmp:
        with tarfile.open(LITE) as t:
            t.extractall(tmp, filter="data")
        base = os.path.join(tmp, "agent-guardrails-lite")
        run = lambda d: subprocess.run([sys.executable, "-I", os.path.join(d, "tools", "preflight.py"), "daily-report"],
                                       cwd=d, capture_output=True, text=True, timeout=300)
        p = run(base)
        out["pass"] = (p.returncode, p.stdout.strip().splitlines())
        d = os.path.join(tmp, "norules"); shutil.copytree(base, d)
        f = os.path.join(d, "CLAUDE.md"); s = open(f, encoding="utf-8").read()
        s = s.replace("- Read ops/CONSTITUTION.md before anything else. It binds every run.\n", "")
        open(f, "w", encoding="utf-8").write(s)
        p = run(d)
        out["norules"] = (p.returncode, p.stdout.strip().splitlines())
        d = os.path.join(tmp, "weak"); shutil.copytree(base, d)
        f = os.path.join(d, "tools", "context_gate.py"); s = open(f, encoding="utf-8").read()
        s = s.replace('    text = re.sub(r"<!--.*?(?:-->|\\Z)", "", text, flags=re.S)\n', "")
        open(f, "w", encoding="utf-8").write(s)
        p = run(d)
        out["weak"] = (p.returncode, p.stdout.strip().splitlines())
    return out


def term(t, rel_e, hidden=False):
    E = rel_e
    lines = []
    for x in t["lines"]:
        cls = "g" if x.startswith("OK") or (x.startswith("preflight") and "0 errors" in x) else ("r" if x.startswith(("ERROR", "preflight")) else "")
        x = re.sub(r"\(exit (\d+)\)", r'<span class="nw">(exit \1)</span>', E(x))   # keep "exit 0" together, plain space
        lines.append(f'<span class="{cls}">{x}</span>' if cls else x)
    if hidden:   # the hero copy of a panel shown again under Proof: hidden from screen readers, out of the tab order
        return (f'<figure class="ak-term {E(t["tone"])}" aria-hidden="true"><figcaption><i></i>{E(t["title"])}</figcaption>'
                f'<pre><span class="c">$ {E(t["cmd"])}</span>\n' + "\n".join(lines) + "</pre></figure>")
    return (f'<figure class="ak-term {E(t["tone"])}"><figcaption><i aria-hidden="true"></i>{E(t["title"])}</figcaption>'
            f'<pre tabindex="0" aria-label="{E(t["title"])}: terminal output"><span class="c">$ {E(t["cmd"])}</span>\n'
            + "\n".join(lines) + "</pre></figure>")


def page_html(p):
    import make_site as M
    E = M.E
    url, rel = M.BASE + p["slug"] + "/", "../"
    robots = "" if M.is_live(p) else '<meta name="robots" content="noindex, nofollow">'
    crumb, crumb_ld = M.crumbs(rel, [("Home", ""), (p["h1"], None)])
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p["faq"]]}
    head = M.HEAD.format(title=E(p["title"]), desc=E(p["desc"]), url=url, rel=rel, shop=M.SHOP, ld=M.ld_tags(crumb_ld, faq_ld) + CSS,
                         bodycls=' class="ld-page ak-page"', robots=robots, analytics=M.analytics_tag())
    w = p["waitlist"]
    if p.get("kitForm"):
        form = (f'<form class="ld-form" action="https://app.kit.com/forms/{E(p["kitForm"])}/subscriptions" method="post">'
                '<label for="akEmail">Email</label><div class="ld-frow"><input id="akEmail" name="email_address" type="email" required autocomplete="email" placeholder="you@company.com">'
                f'<button class="btn" type="submit">{E(w["button"])}</button></div></form>'
                f'<p class="ak-fine">{E(w["fine"])}</p>')
    else:
        form = '<p class="ld-buybtn"><span class="btn soon" aria-disabled="true">Waitlist opens soon</span></p>'
    open_ = bool(p.get("kitForm"))   # before the Kit form exists, no button points at a waitlist that cannot take an email
    acts = (f'<a class="btn ld-btnbig" href="#waitlist">{E(p["heroCta"])}</a><a class="st-btn2" href="#proof">{E(p["heroCta2"])}</a>' if open_
            else f'<a class="btn ld-btnbig" href="#proof">{E(p["heroCtaSoon"])}</a>')
    hero_term = next(t for t in p["proof"]["terms"] if t["key"] == p["proof"].get("heroKey", "norules"))
    hero = (f'<div class="ld-hero ak-hero"><div><p class="eyebrow">{E(p["eyebrow"])}</p><h1>{E(p["h1"])}</h1><p class="lede">{E(p["lede"])}</p>'
            f'<div class="ld-heroact" id="akHeroCta">{acts}</div>'
            f'<p class="ak-note">{E(p["heroNote"])}</p></div>'
            f'<div class="ak-side">{term(hero_term, E, hidden=True)}'
            f'<figure class="ak-files" aria-hidden="true"><figcaption>{E(p["lite"]["treeCap"])}</figcaption><pre class="ak-tree">{E(chr(10).join(p["lite"]["tree"]))}</pre></figure></div></div>')
    otp = ('<nav class="otp" aria-label="On this page"><div class="otp-in">'
           + "".join(f'<a href="#{s}">{E(l)}</a>' for s, l in p["otp"]) + '</div></nav>')
    proof = (f'<section class="block" id="proof"><h2>{E(p["proof"]["title"])}</h2><p>{E(p["proof"]["text"])}</p>'
             '<div class="ak-terms">' + "".join(term(t, E) for t in p["proof"]["terms"]) + '</div>'
             f'<p class="asof">{E(p["proof"]["asof"])}</p></section>')
    fears = (f'<section class="block" id="fears"><h2>{E(p["fears"]["title"])}</h2><ul class="ak-grid">'
             + "".join(f'<li class="ak-card"><h3>{E(h)}</h3><p>{E(t)}</p></li>' for h, t in p["fears"]["items"]) + '</ul></section>')
    how = (f'<section class="block" id="how"><h2>{E(p["how"]["title"])}</h2><ol class="ak-steps">'
           + "".join(f'<li><h3>{E(h)}</h3><p>{E(t)}</p></li>' for h, t in p["how"]["steps"]) + '</ol></section>')
    foot_act = (f'<a class="btn" href="#waitlist">{E(p["heroCta"])}</a>' if open_ else "")
    inside = (f'<section class="block" id="inside"><h2>{E(p["inside"]["title"])}</h2><div class="ak-box"><ul class="ak-list cols">'
              + "".join(f"<li>{E(x)}</li>" for x in p["inside"]["items"])
              + f'</ul><div class="ak-boxfoot"><p>{E(p["bar"])}</p>{foot_act}</div><p class="asof">{E(p["inside"]["note"])}</p></div></section>')
    lite = p["lite"]
    lite_act = (f'<p class="ld-buybtn"><a class="st-btn2" href="{E(p["liteUrl"])}" rel="noopener">{E(lite["button"])}</a></p>' if p.get("liteUrl")
                else f'<p class="asof">{E(lite["pending"])}</p>')
    facts = p["facts"]
    tree = (f'<pre class="ak-tree" tabindex="0" aria-label="What the lite version holds">{E(chr(10).join(lite["tree"]))}</pre>')
    two = ('<section class="block" id="lite"><div class="ak-two">'
           f'<div><h2>{E(lite["title"])}</h2><p>{E(lite["text"])}</p>{tree}{lite_act}</div>'
           f'<div><h2>{E(facts["title"])}</h2><p>{E(facts["text"])}</p><div class="ak-facts">'
           + "".join(f'<div class="tile"><div class="lab">{E(a)}</div><div class="val">{E(b)}</div><div class="sub">{E(c)}</div></div>' for a, b, c in facts["tiles"])
           + f'</div><p class="asof">{E(facts["asof"])}</p></div></div></section>')
    notfor = (f'<section class="block" id="notfor"><h2>{E(p["notFor"]["title"])}</h2><div class="ak-box"><ul class="ak-list">'
              + "".join(f"<li>{E(x)}</li>" for x in p["notFor"]["items"]) + '</ul></div></section>')
    wait = (f'<section class="block ak-wait" id="waitlist"><div class="cta ld-cta"><div><h2>{E(w["title"])}</h2><p>{E(w["text"])}</p>'
            f'<p class="ak-price">{E(w["price"])}</p>{form}</div></div></section>')
    body = (crumb + hero + otp + proof + fears + how + inside + two + notfor + wait + M.faq_block(p["faq"])
            + (f'<p class="rl-act"><a class="btn" href="#waitlist">{E(p["heroCta"])}</a></p>' if open_ else ""))
    if open_:   # phones: a slim bar after the hero, hidden while the hero buttons or the waitlist band are on screen
        body += (f'<div class="ld-sbar" id="ldBar" aria-hidden="true"><div class="wrap"><p><b>{E(p["bar"])}</b></p>'
                 f'<a class="btn" href="#waitlist" tabindex="-1">{E(p["heroCta"])}</a></div></div>'
                 "<script>(function(){var bar=document.getElementById('ldBar'),hero=document.getElementById('akHeroCta'),cta=document.getElementById('waitlist');"
                 "if(!bar||!hero||!cta||!('IntersectionObserver' in window))return;var hv=true,cv=false,link=bar.querySelector('a');"
                 "function set(){var on=!hv&&!cv;bar.classList.toggle('on',on);bar.setAttribute('aria-hidden',String(!on));link.tabIndex=on?0:-1}"
                 "var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.target===hero)hv=e.isIntersecting;else cv=e.isIntersecting});set()});"
                 "io.observe(hero);io.observe(cta)})();</script>")
    foot = (f'</main>\n<footer><div class="wrap">{M.foot_nav(rel)}'
            f'<p>{E(p["credit"])}</p>'
            '<p>Not legal, security or financial advice. You are responsible for what your agent does; the kit helps you set rules and checks, '
            'and it cannot promise that a model follows them.</p>'
            '<p>Claude and Claude Code are trademarks of Anthropic. ProofNotFluff is not affiliated with or endorsed by Anthropic.</p>'
            '<p>Made by ProofNotFluff with AI assistance, reviewed and tested by the shop owner. The page counts visits with Cloudflare Web '
            'Analytics, which sets no cookies.</p></div></footer>\n</body></html>')
    return head + body + foot


def selftest():
    sys.path.insert(0, HERE)
    import make_site as M
    spec = [x for x in json.load(open(os.path.join(ROOT, "site", "pages.json"), encoding="utf-8"))["pages"] if x.get("kind") == "agentkit"][0]
    html = page_html(spec)
    assert html.count("<h1>") == 1 and "—" not in html and "–" not in html, "one h1, no dashes"
    assert 'name="robots" content="noindex, nofollow"' in html if spec.get("draft") else True, "a draft is noindex"
    assert ("app.kit.com/forms/" in html) == bool(spec.get("kitForm")), "the form shows only with a Kit form number"
    assert "Waitlist opens soon" in html or spec.get("kitForm"), "no form: the disabled button"
    with_form = page_html(dict(spec, kitForm="1234567"))
    assert 'action="https://app.kit.com/forms/1234567/subscriptions"' in with_form and 'type="email" required' in with_form, "Kit form"
    assert "2603.16021" in html and "MIT" in html, "the ICM credit"
    for bad in ("Todd", "Millen", "Chicago", "@gmail", "getproofnotfluff"):
        assert bad not in html.replace("hello@proofnotfluff.com", ""), f"private term {bad!r} on the page"
    proof = load_lite_proof()
    shown = {t["key"]: t for t in spec["proof"]["terms"]}
    for key, (code, lines) in proof.items():
        assert key in shown, f"proof panel {key} missing"
        assert shown[key]["lines"] == lines, f"panel {key} no longer matches the lite kit: {lines}"
        assert code == (0 if key == "pass" else 1), f"panel {key} exit {code}"
    import re
    n = re.search(r"(\d+) planted failures caught", " ".join(proof["pass"][1])).group(1)
    assert f"its {n} planted-failure tests" in spec["lite"]["text"], f"the lite text must say {n} planted-failure tests"
    print(f"agentkit_site selftest: ok ({sum(len(v[1]) for v in proof.values())} terminal lines match the lite kit)")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
