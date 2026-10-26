#!/usr/bin/env python3
"""Gumroad cover (1280 x 720) and thumbnail (600 x 600) for each area seat (launches/chicago-cleaning-area-seats.md).
Same look as the pest seat cover (launches/chicago-pest-seat/): the site's fonts and colours, no weekly numbers, so the
images stay true week to week. The seat's area is lit on the City's community area outlines; the rest are grey.

Usage: python3 tools/area_covers.py OUT_DIR   (needs Playwright with chromium)
"""
import asyncio, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import area_seats as A  # noqa: E402

FONTS = os.path.join(ROOT, "docs", "assets", "fonts")
LIT = ["#2F5F9E", "#C8502F", "#2E6B66", "#A87C1F", "#8A5A8E", "#5F7F4F"]


def map_svg(cfg, geo, slug, width):
    f, w, h = A._proj(geo, width)
    i = next(n for n, t in enumerate(cfg["territories"]) if t["slug"] == slug)
    mine = set(cfg["territories"][i]["areas"])
    paths = []
    for a in geo["areas"]:
        d = " ".join("M" + " L".join(f"{px},{py}" for px, py in (f(x, y) for x, y in r)) + " Z" for r in a["rings"])
        on = a["name"] in mine
        paths.append(f'<path d="{d}" fill="{LIT[i] if on else "#D9D3C7"}" stroke="#F3F1EC" stroke-width="{1.2 if on else 0.9}"/>')
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{"".join(paths)}</svg>', h


CSS = f"""@font-face{{font-family:P;font-weight:700;src:url(file://{FONTS}/poppins-700.woff2)}}
@font-face{{font-family:P;font-weight:600;src:url(file://{FONTS}/poppins-600.woff2)}}
@font-face{{font-family:In;font-weight:400;src:url(file://{FONTS}/inter-400.woff2)}}
@font-face{{font-family:In;font-weight:600;src:url(file://{FONTS}/inter-600.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#F3F1EC;color:#1D2433;font-family:In;overflow:hidden;position:relative}}
.eb{{font:700 15px P;letter-spacing:.12em;color:#2E6B66}}
.brand{{position:absolute;font:700 17px P}}.bars5{{display:flex;gap:6px;margin-top:6px}}.bars5 b{{width:26px;height:5px;border-radius:3px}}"""
BARS = '<div class="bars5"><b style="background:#C8502F"></b><b style="background:#2E6B66"></b><b style="background:#6A4C93"></b><b style="background:#2F5F9E"></b><b style="background:#A87C1F"></b></div>'


def cover_html(t, svg, price):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:1280px;height:720px}}.l{{position:absolute;left:64px;top:62px;width:640px}}
h1{{font:700 52px/1.08 P;margin:18px 0 20px;letter-spacing:-.015em}}.sub{{font-size:20px;line-height:1.5;color:#3A4152}}
.fact{{display:inline-flex;align-items:center;gap:10px;margin:22px 0 0;padding:8px 14px;border-radius:999px;background:#E3EFED;color:#1E4C48;font:600 15px In}}
.fact i{{width:12px;height:12px;border-radius:50%;background:#2E6B66}}
ul{{list-style:none;margin:22px 0 0}}li{{font:600 18px P;margin:11px 0;display:flex;align-items:center;gap:12px}}
li i{{width:22px;height:22px;border-radius:50%;background:#2E6B66;position:relative;flex:none}}
li i:after{{content:"";position:absolute;left:7px;top:4px;width:6px;height:11px;border:solid #fff;border-width:0 2.5px 2.5px 0;transform:rotate(45deg)}}
.price{{display:flex;align-items:center;gap:16px;margin-top:36px}}.pill{{background:#C8502F;color:#fff;font:700 22px P;padding:12px 24px;border-radius:12px}}
.cancel{{font-size:16px;color:#3A4152}}.map{{position:absolute;right:72px;top:40px}}.brand{{right:56px;bottom:40px;text-align:right}}.brand .bars5{{justify-content:flex-end}}
</style></head><body><div class="l"><div class="eb">CHICAGO · CONSTRUCTION CLEANING · AREA SEAT</div>
<h1>{t['name']}</h1>
<p class="sub">Every open big construction project in your area, with the builder on each, on your members' page every Monday.</p>
<span class="fact"><i></i>One cleaning company holds this area</span>
<ul><li><i></i>Closest to a final clean first</li><li><i></i>Builder's office phone or email where listed</li><li><i></i>Members' app, map and Excel file</li></ul>
<div class="price"><span class="pill">${price} a month</span><span class="cancel">No lock-in. Cancel any time</span></div></div>
<div class="map">{svg}</div><div class="brand">ProofNotFluff{BARS}</div></body></html>"""


def thumb_html(t, svg):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:600px;height:600px}}.t{{position:absolute;left:40px;top:36px;width:520px}}
h1{{font:700 34px/1.12 P;margin:8px 0 0}}.map{{position:absolute;left:50%;transform:translateX(-50%);top:168px}}
.brand{{right:36px;bottom:32px;text-align:right;font-size:15px}}.brand .bars5{{justify-content:flex-end}}.brand .bars5 b{{width:20px}}
</style></head><body><div class="t"><div class="eb">CHICAGO CLEANING LEADS · AREA SEAT</div><h1>{t['name']}</h1></div>
<div class="map">{svg}</div><div class="brand">ProofNotFluff{BARS}</div></body></html>"""


async def render(out, price="149"):
    from playwright.async_api import async_playwright
    cfg, geo = A.load(), json.load(open(A.GEO))
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for t in cfg["territories"]:
            svg_c, _ = map_svg(cfg, geo, t["slug"], 500)
            svg_t, _ = map_svg(cfg, geo, t["slug"], 420)
            for name, html, (w, h) in [("cover-1280x720", cover_html(t, svg_c.replace('width="500"', 'width="430"').replace(f'height="', 'data-h="', 1), price), (1280, 720)),
                                       ("thumb-600x600", thumb_html(t, svg_t.replace('width="420"', 'width="320"').replace('height="', 'data-h="', 1)), (600, 600))]:
                pg = await b.new_page(viewport={"width": w, "height": h})
                path = os.path.join(out, f"{t['slug']}-{name}.html")
                open(path, "w").write(html)
                await pg.goto("file://" + path); await pg.wait_for_timeout(300)
                await pg.screenshot(path=os.path.join(out, f"{t['slug']}-{name}.png"))
                os.remove(path)
                await pg.close()
        await b.close()


if __name__ == "__main__":
    asyncio.run(render(sys.argv[1]))
