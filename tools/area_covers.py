#!/usr/bin/env python3
"""Gumroad cover (1280 x 720) and thumbnail (600 x 600) for each area seat (launches/chicago-cleaning-area-seats.md).
Same look as the pest seat cover (launches/chicago-pest-seat/): the site's fonts and colours, no weekly numbers, so the
images stay true week to week. The seat's area is lit on the City's community area outlines; the rest are grey.

Usage: python3 tools/area_covers.py OUT_DIR   (needs Playwright with chromium)
"""
import asyncio, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import area_seats as A  # noqa: E402
from exclusive_areas import ring_area_centroid  # noqa: E402

FONTS = os.path.join(ROOT, "docs", "assets", "fonts")
LIT = ["#2F5F9E", "#C8502F", "#2E6B66", "#A87C1F", "#8A5A8E", "#5F7F4F"]


GHOST = "#D6CFC1"


def map_svg(cfg, geo, slug, width):
    """The City's community areas, the seat's area lit with a plain white outline (design director, round 5).
    Returns (svg, drawing body, bbox of the lit area, (w, h))."""
    f, w, h = A._proj(geo, width)
    i = next(n for n, t in enumerate(cfg["territories"]) if t["slug"] == slug)
    mine = set(cfg["territories"][i]["areas"])
    grey, lit, pts = [], [], []
    for a in geo["areas"]:
        sizes = [abs(ring_area_centroid(r)[0]) for r in a["rings"]]
        rings = [r for r, z in zip(a["rings"], sizes) if z >= 0.12 * max(sizes)]   # no detached slivers at card size, Northerly Island included
        proj = [[f(x, y) for x, y in r] for r in rings]
        d = " ".join("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in r) + " Z" for r in proj)
        if a["name"] in mine:
            pts += [q for r in proj for q in r]
            lit.append(f'<path d="{d}" fill="{LIT[i]}" stroke="#FFFFFF" stroke-width="1.6" stroke-linejoin="round"/>')
        else:
            grey.append(f'<path d="{d}" fill="{GHOST}" stroke="#F3F1EC" stroke-width="0.9"/>')
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    body = "".join(grey) + "".join(lit)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {w + 4} {h + 4}" width="{w + 4}" height="{h + 4}">{body}</svg>'
    return svg, body, (min(xs), min(ys), max(xs), max(ys)), (w + 4, h + 4)


def framed_svg(body, bbox, full, box_w, box_h, pad=0.45):
    """The drawing framed on the seat's own area, the rest of the city a ghost beyond it (one rule for all six thumbnails;
    design director, round 5)."""
    x0, y0, x1, y1 = bbox
    bw, bh = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    r = box_w / box_h
    if bw / bh < r:
        bw = bh * r
    else:
        bh = bw / r
    bw, bh = min(bw, full[0] * 1.02), min(bh, full[1] * 1.02)
    if bw / bh < r:
        bw = bh * r
    else:
        bh = bw / r
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - bw / 2:.1f} {cy - bh / 2:.1f} {bw:.1f} {bh:.1f}" '
            f'width="{box_w}" height="{box_h}" preserveAspectRatio="xMidYMid meet">{body}</svg>')


CSS = f"""@font-face{{font-family:P;font-weight:700;src:url(file://{FONTS}/poppins-700.woff2)}}
@font-face{{font-family:P;font-weight:600;src:url(file://{FONTS}/poppins-600.woff2)}}
@font-face{{font-family:In;font-weight:400;src:url(file://{FONTS}/inter-400.woff2)}}
@font-face{{font-family:In;font-weight:600;src:url(file://{FONTS}/inter-600.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#F3F1EC;color:#1D2433;font-family:In;overflow:hidden;position:relative}}
.eb{{font:700 17px P;letter-spacing:.14em;color:#2E6B66}}
.brand{{position:absolute;font:700 20px P}}.bars5{{display:flex;gap:7px;margin-top:7px}}.bars5 b{{width:28px;height:6px;border-radius:3px}}"""
BARS = '<div class="bars5"><b style="background:#C8502F"></b><b style="background:#2E6B66"></b><b style="background:#6A4C93"></b><b style="background:#2F5F9E"></b><b style="background:#A87C1F"></b></div>'
EYEBROW = "CHICAGO · CONSTRUCTION CLEANING · AREA SEAT"   # one string on covers and thumbnails (design director, round 4)
FIT_JS = """async()=>{await document.fonts.ready;for(const h of document.querySelectorAll('h1[data-fit]')){let s=+h.dataset.fit;
while(s>30&&h.getBoundingClientRect().height>s*1.08*2+2){s-=1;h.style.fontSize=s+'px';}}}"""   # a title never runs past two lines


def cover_html(t, svg, price):
    # text anchored at one top on all six (eyebrow at y 150) so baselines match; the map has 64 px margins top, bottom and
    # right; the brand sits bottom left where the map leaves room; the price is plain text (design director, rounds 4 and 5)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:1280px;height:720px}}.l{{position:absolute;left:64px;top:132px;width:620px}}
h1{{font:700 54px/1.08 P;margin:18px 0 18px;letter-spacing:-.015em;text-wrap:balance}}.sub{{font-size:22px;line-height:1.45;color:#3A4152;text-wrap:pretty}}
ul{{list-style:none;margin:24px 0 0}}li{{font:600 22px In;margin:12px 0;display:flex;align-items:center;gap:14px}}
li i{{width:26px;height:26px;border-radius:50%;background:#2E6B66;position:relative;flex:none}}
li i:after{{content:"";position:absolute;left:9px;top:5px;width:6px;height:12px;border:solid #fff;border-width:0 2.5px 2.5px 0;transform:rotate(45deg)}}
.price{{display:flex;align-items:baseline;gap:16px;margin-top:28px}}.amt{{font:700 32px P;color:#1D2433}}
.cancel{{font-size:20px;color:#5C6270}}.map{{position:absolute;right:64px;top:64px}}.map svg{{display:block}}.brand{{left:64px;bottom:56px}}
</style></head><body><div class="l"><div class="eb">{EYEBROW}</div>
<h1 data-fit="54">{t['name']}</h1>
<p class="sub">Open apartment and commercial projects of $500,000 or more in your area, with the builder on each, every Monday.</p>
<ul><li><i></i>One cleaning company holds this area</li><li><i></i>Closest to a final clean first</li></ul>
<div class="price"><span class="amt">${price} a month</span><span class="cancel">No lock-in. Cancel any time</span></div></div>
<div class="map">{svg}</div><div class="brand">ProofNotFluff{BARS}</div></body></html>"""


def thumb_html(t, svg):
    # title as large as two lines allow, the map framed on the seat's own area in the lower part, the brand bottom left
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:600px;height:600px}}.t{{position:absolute;left:40px;top:34px;width:520px}}
.eb{{font-size:15px;letter-spacing:.12em}}h1{{font:700 56px/1.08 P;margin:10px 0 0;letter-spacing:-.015em;text-wrap:balance}}
.map{{position:absolute;left:40px;top:214px;width:520px;height:300px;border-radius:14px;overflow:hidden;background:#ECE8E0}}.map svg{{display:block}}
.brand{{left:40px;bottom:28px;font-size:22px}}.brand .bars5 b{{width:24px}}
</style></head><body><div class="t"><div class="eb">{EYEBROW}</div><h1 data-fit="56">{t['name']}</h1></div>
<div class="map">{svg}</div><div class="brand">ProofNotFluff{BARS}</div></body></html>"""


def by_height(svg, size, height):
    """Draw the svg at a given height; the width follows its aspect."""
    w = round(height * size[0] / size[1])
    return re.sub(r'^<svg ([^>]*?)width="[^"]+" height="[^"]+"', lambda m: f'<svg {m.group(1)}width="{w}" height="{height}"', svg, count=1)


async def render(out, price="149"):
    from playwright.async_api import async_playwright
    cfg, geo = A.load(), json.load(open(A.GEO))
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for t in cfg["territories"]:
            svg, body, bbox, full = map_svg(cfg, geo, t["slug"], 500)
            for name, html, (w, h) in [("cover-1280x720", cover_html(t, by_height(svg, full, 592), price), (1280, 720)),
                                       ("thumb-600x600", thumb_html(t, framed_svg(body, bbox, full, 520, 300)), (600, 600))]:
                pg = await b.new_page(viewport={"width": w, "height": h})
                path = os.path.join(out, f"{t['slug']}-{name}.html")
                open(path, "w").write(html)
                await pg.goto("file://" + path); await pg.evaluate(FIT_JS); await pg.wait_for_timeout(300)
                await pg.screenshot(path=os.path.join(out, f"{t['slug']}-{name}.png"))
                os.remove(path)
                await pg.close()
        await b.close()


if __name__ == "__main__":
    asyncio.run(render(sys.argv[1]))
