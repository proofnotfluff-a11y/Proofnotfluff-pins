#!/usr/bin/env python3
"""Render a social carousel (1080 x 1350 JPGs) from cmo/carousels/<date>.json.

Usage: python3 tools/make_carousel.py cmo/carousels/2026-10-25.json --out /home/claude/carousel/2026-10-25
Writes slide-1.jpg ... slide-N.jpg and sheet.jpg (all slides on one image, for the design gate).

Todd, Oct 25, 2026: "Build in code" (slides are rendered here, not in Canva, so a scheduled run can post them).
Look: design/CAROUSEL_STANDARD.md. Poppins 600/700 for display, Inter 400/600 for sentences, both bundled
in docs/assets/fonts. Titles and body use text-wrap: balance, so no line ends on one orphan word.

Slide roles and their json fields (every slide: eyebrow, title, optional source):
  hook   ink band: number, title, sub
  proof  tiles: [{label, value, accent?}] (2 or 3; accent: true paints the one bar that matters)
  where  rows: [[rank, name, value], ...] (5 at most)
  why    body, card: {label, value}
  work   body, bars: [{label, value}] (first bar ink, last bar accent, widths from the numbers)
  offer  body, price ("7 days free, then $29 a month"), terms
  cta    ink band: domain
"""
import argparse, html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONTS = os.path.join(ROOT, "docs", "assets", "fonts")
T = {"canvas": "#F3F1EC", "card": "#FFFFFF", "line": "#E2DDD3", "ink": "#1D2433", "ink2": "#4A5163",
     "muted": "#6B7180", "teal": "#2E6B66", "accent": "#C8502F", "accentInk": "#E88062", "soft": "#B9C0CE",
     "bars": ["#C8502F", "#2E6B66", "#6B4FA0", "#2F5F9E", "#A87C1F"]}
DASHES = re.compile("[–—]")


def esc(s):
    return html.escape(str(s or ""), quote=False).replace("'", "\u2019").replace("\n", "<br>")


def num(v):
    m = re.search(r"[\d,.]+", str(v))
    return float(m.group(0).replace(",", "")) if m else 0.0


def _font(file):
    import base64
    with open(os.path.join(FONTS, file), "rb") as fh:
        return "data:font/woff2;base64," + base64.b64encode(fh.read()).decode()


def css():
    # Fonts go in as data URIs: a page set from a string cannot load file:// fonts.
    f = lambda fam, w, file: (f"@font-face{{font-family:'{fam}';font-weight:{w};"
                              f"src:url('{_font(file)}') format('woff2')}}")
    return "".join([f("P", 600, "poppins-600.woff2"), f("P", 700, "poppins-700.woff2"),
                    f("I", 400, "inter-400.woff2"), f("I", 600, "inter-600.woff2"), f("I", 700, "inter-700.woff2")]) + f"""
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{width:1080px;height:1350px;overflow:hidden}}
.s{{position:relative;width:1080px;height:1350px;background:{T['canvas']};color:{T['ink']};font-family:I}}
.s.ink{{background:{T['ink']};color:#fff}}
.bars{{position:absolute;left:96px;top:96px;display:flex;gap:12px}}
.bars i{{display:block;width:56px;height:10px;border-radius:3px}}
.foot{{position:absolute;left:96px;right:96px;top:1222px;display:flex;justify-content:space-between;
 font:700 24px/1.2 P;color:{T['ink2']}}}
.ink .foot{{color:{T['soft']}}}
.src{{position:absolute;left:96px;right:96px;top:1160px;font:400 22px/1.3 I;color:{T['ink2']}}}
.c{{position:absolute;left:96px;width:888px;top:186px}}
.c.mid{{top:106px;height:1116px;display:flex;flex-direction:column;justify-content:center}}
.c.fill{{top:186px;height:926px;display:flex;flex-direction:column}}
.grow{{flex:1;min-height:0;display:flex;flex-direction:column;justify-content:space-evenly}}
.e{{font:700 26px/1.2 P;letter-spacing:.08em;text-transform:uppercase;color:{T['accent']};margin-bottom:16px}}
.ink .e{{color:{T['accentInk']}}}
h1,h2{{font-family:P;font-weight:700;text-wrap:balance}}
h2{{font-size:60px;line-height:1.05;max-width:800px}}
.big{{font:700 300px/1 P;letter-spacing:-.02em;margin:8px 0 0}}
.hook h2{{font-size:72px;max-width:888px;margin-top:24px}}
.cta h2{{font-size:72px;max-width:760px}}
.b{{font:400 36px/1.35 I;color:{T['ink2']};max-width:888px;text-wrap:balance;margin-top:48px}}
.ink .b{{color:{T['soft']}}}
.hook .b{{margin-top:32px;max-width:840px}}
.card{{background:{T['card']};border:1px solid {T['line']};border-radius:24px;padding:36px 48px}}
.mt{{margin-top:48px}}
.lab{{font:700 22px/1.2 P;letter-spacing:.06em;text-transform:uppercase;color:{T['muted']}}}
.tiles{{gap:24px;margin-top:48px}}
.tiles .card{{flex:1;display:flex;align-items:center;padding:0 48px}}
.tiles .tv{{width:330px;white-space:nowrap}}
.tbar{{flex:1;height:32px;margin-left:32px}}
.tbar i{{display:block;height:32px;border-radius:8px;background:{T['ink']}}}
.val{{font:700 96px/1 P;color:{T['ink']};margin-top:10px}}
.huge{{font:700 240px/1 P;color:{T['ink']};margin-top:12px;letter-spacing:-.02em}}
.rows{{margin-top:48px;padding:8px 48px}}
.row{{flex:1;display:flex;align-items:center;border-top:1px solid {T['line']};font:400 40px/1.1 I;color:{T['ink']}}}
.row:first-child{{border-top:0}}
.row .n{{flex:1}}
.row .v{{font:700 56px/1 P}}
.why .card{{margin-top:48px;justify-content:center}}
.why .huge{{font-size:280px}}
.why .card{{justify-content:center;gap:16px}}
.why .tbar{{flex:none;margin:8px 0 0}}
.work .card{{margin-top:48px}}
.offer .card{{margin-top:48px;justify-content:flex-start;padding-top:56px}}
.inc{{margin-top:40px;border-top:1px solid {T['line']};padding-top:32px;display:flex;flex-direction:column;gap:24px}}
.inc div{{display:flex;align-items:center;gap:24px;font:400 34px/1.2 I;color:{T['ink']}}}
.ck{{width:14px;height:28px;border:solid {T['teal']};border-width:0 6px 6px 0;transform:rotate(45deg);margin:0 8px 8px 6px}}
.offer .lead{{font-size:36px}}
.offer .price{{font-size:112px;white-space:nowrap}}
.offer .terms{{font-size:34px}}
.where .b,.why .b{{margin-top:40px}}
.bl{{font:700 22px/1.2 P;letter-spacing:.06em;text-transform:uppercase;color:{T['muted']};margin:0 0 12px}}
.bar{{height:96px;border-radius:12px;display:flex;align-items:center;padding-left:32px;
 font:700 44px/1 P;color:#fff;min-width:180px}}
.lead{{font:700 30px/1.2 P;color:{T['ink2']}}}
.price{{font:700 96px/1.1 P;color:{T['ink']};margin:8px 0 16px}}
.terms{{font:400 30px/1.3 I;color:{T['ink2']}}}
.btn{{display:inline-block;align-self:flex-start;margin-top:64px;background:{T['accent']};color:#fff;
 font:700 48px/1.2 P;padding:27px 48px;border-radius:16px}}
"""


def slide(s, i, n, footer):
    role = s["role"]
    ink = s.get("ground") == "ink" or role in ("hook", "cta")
    eb = f'<div class="e">{esc(s.get("eyebrow"))}</div>' if s.get("eyebrow") else ""
    title = f'<h2>{esc(s.get("title"))}</h2>' if s.get("title") else ""
    body = f'<div class="b">{esc(s.get("body"))}</div>' if s.get("body") else ""
    mid = role in ("hook", "cta")
    if role == "hook":
        inner = f'{eb}<div class="big">{esc(s["number"])}</div>{title}<div class="b">{esc(s.get("sub"))}</div>'
    elif role == "proof":
        top = max(num(t["value"]) for t in s["tiles"]) or 1
        tiles = "".join(f'<div class="card"><div class="tv"><div class="lab">{esc(t["label"])}</div><div class="val">{esc(t["value"])}</div></div>'
                        f'<div class="tbar"><i style="width:{max(0.06, num(t["value"]) / top) * 100:.1f}%' + (f';background:{T["accent"]}' if t.get("accent") else "") + '"></i></div></div>'
                        for t in s["tiles"])
        inner = f'{eb}{title}<div class="tiles grow">{tiles}</div>'
    elif role == "where":
        # The order is the rank: no rank column (a tie read as "1, 2, 2, 4" looks like a typo).
        rows = "".join(f'<div class="row"><span class="n">{esc(r[1])}</span>'
                       f'<span class="v">{esc(r[2])}</span></div>' for r in s["rows"][:5])
        inner = f'{eb}{title}<div class="card rows grow">{rows}</div>{body}'
    elif role == "why":
        c = s["card"]
        ofbar = (f'<div class="tbar"><i style="width:{num(c["value"]) / num(c["of"]) * 100:.1f}%"></i></div>' if c.get("of") else "")
        inner = f'{eb}{title}<div class="card grow"><div class="lab">{esc(c["label"])}</div><div class="huge">{esc(c["value"])}</div>{ofbar}</div>{body}'
    elif role == "work":
        bars = s["bars"]; top = max(num(b["value"]) for b in bars) or 1
        out = []
        for k, b in enumerate(bars):
            w = max(0.19, num(b["value"]) / top) * 100
            col = T["accent"] if k == len(bars) - 1 else T["ink"]
            out.append(f'<div class="bl">{esc(b["label"])}</div><div class="bar" style="width:{w:.1f}%;background:{col}">{esc(b["value"])}</div>')
        inner = f'{eb}{title}<div class="card grow">{"".join(out)}</div>{body}'
    elif role == "offer":
        p = s["price"]; m = re.match(r"(.*?then)\s+(.*)", p)
        lead, price = (m.group(1), m.group(2)) if m else ("", p)
        inner = (f'{eb}{title}{body}<div class="card grow"><div class="lead">{esc(lead)}</div>'
                 f'<div class="price">{esc(price)}</div><div class="terms">{esc(s.get("terms"))}</div>'
                 + (('<div class="inc">' + "".join(f'<div><span class="ck"></span>{esc(x)}</div>' for x in s["includes"]) + '</div>') if s.get("includes") else "")
                 + '</div>')
    elif role == "cta":
        sub = f'<div class="b">{esc(s.get("sub"))}</div>' if s.get("sub") else ""
        inner = f'{eb}{title}<div class="btn">{esc(s["domain"])}</div>{sub}'
    else:
        raise SystemExit(f"unknown role {role} on slide {i}")
    bars = "".join(f'<i style="background:{c}"></i>' for c in T["bars"])
    src = f'<div class="src">{esc(s["source"])}</div>' if s.get("source") else ""
    right = footer.get("right", "n/N").replace("n", str(i)).replace("N", str(n)).replace("/7", f"/{n}")
    return (f'<div class="s {"ink" if ink else ""} {role}"><div class="bars">{bars}</div>'
            f'<div class="c {"mid" if mid else "fill"}">{inner}</div>{src}'
            f'<div class="foot"><span>{esc(footer.get("left", "ProofNotFluff"))}</span><span>{right}</span></div></div>')


def check(spec):
    errs = []
    for s in spec["slides"]:
        for k, v in s.items():
            if isinstance(v, str) and DASHES.search(v):
                errs.append(f"slide {s.get('n')} {k}: em or en dash")
        n = s.get("n"); t = s.get("title") or ""
        if s.get("role") == "why" and s.get("card") and str(s["card"].get("value")) in t:
            errs.append(f"slide {n}: the card number {s['card']['value']} repeats in the title (say it once)")
        shown = [str(x.get("value")) for x in s.get("tiles", []) + s.get("bars", [])] + [str(r[2]) for r in s.get("rows", [])]
        if s.get("card"): shown.append(str(s["card"].get("value")))
        for tok in re.findall(r"\$?\d[\d,.]*%?", t):
            if s.get("role") != "hook" and tok in shown:
                errs.append(f"slide {n}: {tok} is in the title and the data; title the meaning, let the data carry the number")
        words = [w for w in re.findall(r"[A-Za-z']+", t) if len(w) > 3]
        if s.get("role") not in ("offer",) and len(words) >= 3 and sum(w[0].isupper() for w in words) == len(words):
            errs.append(f"slide {n}: title in Title Case; use sentence case")
        e = set(re.findall(r"[a-z]{4,}", (s.get("eyebrow") or "").lower()))
        sub = set(re.findall(r"[a-z]{4,}", ((s.get("sub") or "") + " " + (s.get("body") or "")).lower()))
        if len(e) >= 2 and len(e & sub) >= max(2, len(e) - 1):
            errs.append(f"slide {n}: eyebrow and sub or body say the same thing")
        if s.get("role") == "where" and len(s.get("rows", [])) < 3:
            errs.append(f"slide {n}: a ranked list needs 3 to 5 rows")
    for k, v in (spec.get("captions") or {}).items():
        if DASHES.search(v):
            errs.append(f"caption {k}: em or en dash")
    return errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("spec"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    errs = check(spec)
    if errs:
        print("\n".join("ERROR " + e for e in errs)); sys.exit(1)
    os.makedirs(a.out, exist_ok=True)
    from playwright.sync_api import sync_playwright
    from PIL import Image
    slides = spec["slides"]; n = len(slides); footer = spec.get("footer", {})
    paths = []; hook_top = 0
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(slides, 1):
            pg.set_content(f"<!doctype html><html><head><meta charset='utf-8'><style>{css()}</style></head>"
                           f"<body>{slide(s, i, n, footer)}</body></html>")
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            if s["role"] == "hook":
                hook_top = pg.evaluate("() => document.querySelector('.c').firstElementChild.getBoundingClientRect().top")
            elif s["role"] == "cta" and hook_top:
                pg.evaluate(f"() => {{ const c=document.querySelector('.c'); c.style.justifyContent='flex-start'; c.style.paddingTop='{hook_top - 106}px' }}")
            over = pg.evaluate("""() => { const c=document.querySelector('.c'); const r=c.getBoundingClientRect();
              const kids=[...c.querySelectorAll('*')].map(e=>e.getBoundingClientRect().bottom);
              const bottom=Math.max(r.top,...kids); const src=document.querySelector('.src');
              const limit=src?src.getBoundingClientRect().top-24:1198; return bottom>limit?Math.round(bottom-limit):0 }""")
            if over:
                print(f"ERROR slide {i}: content runs {over}px into the source line or footer"); b.close(); sys.exit(1)
            gap = pg.evaluate("""() => { const c=document.querySelector('.c.fill'); if(!c) return 0;
              const last=[...c.children].pop().getBoundingClientRect().bottom; return Math.round(c.getBoundingClientRect().bottom-last) }""")
            if gap > 120:
                print(f"ERROR slide {i}: {gap}px empty under the content (fill the frame, Oct 26 rule)"); b.close(); sys.exit(1)
            png = os.path.join(a.out, f"slide-{i}.png")
            pg.screenshot(path=png)
            jpg = png[:-4] + ".jpg"; Image.open(png).convert("RGB").save(jpg, quality=92); os.remove(png)
            paths.append(jpg)
        b.close()
    ims = [Image.open(x).resize((360, 450)) for x in paths]
    cols = 4; rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 370 - 10, rows * 460 - 10), "white")
    for k, im in enumerate(ims):
        sheet.paste(im, ((k % cols) * 370, (k // cols) * 460))
    sheet.save(os.path.join(a.out, "sheet.jpg"), quality=90)
    print("OK", len(paths), "slides ->", a.out)


if __name__ == "__main__":
    main()
