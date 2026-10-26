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


def map_svg(cfg, geo, slug, width, halo_w=8):
    """The City's community areas, the seat's area lit with a soft ring. Returns (svg, height, bbox of the lit area)."""
    f, w, h = A._proj(geo, width)
    i = next(n for n, t in enumerate(cfg["territories"]) if t["slug"] == slug)
    mine = set(cfg["territories"][i]["areas"])
    grey, halo, lit, pts = [], [], [], []
    for a in geo["areas"]:
        sizes = [abs(ring_area_centroid(r)[0]) for r in a["rings"]]
        rings = [r for r, z in zip(a["rings"], sizes) if z >= 0.12 * max(sizes)]   # no detached slivers at card size, Northerly Island included (design director, rounds 2 and 3)
        proj = [[f(x, y) for x, y in r] for r in rings]
        d = " ".join("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in r) + " Z" for r in proj)
        if a["name"] in mine:
            pts += [q for r in proj for q in r]
            lit.append(f'<path d="{d}" fill="{LIT[i]}" stroke="#F3F1EC" stroke-width="1.2"/>')
            # a soft ring in the seat colour so a small area still reads at Gumroad card size (design director, round 3)
            halo.append(f'<path d="{d}" fill="{LIT[i]}" stroke="{LIT[i]}" stroke-width="{halo_w}" stroke-opacity=".4" stroke-linejoin="round"/>')
        else:
            grey.append(f'<path d="{d}" fill="#D9D3C7" stroke="#F3F1EC" stroke-width="0.9"/>')
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    pad = halo_w
    body = "".join(grey) + "".join(halo) + "".join(lit)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{-pad} {-pad} {w + 2 * pad} {h + 2 * pad}" '
           f'width="{w + 2 * pad}" height="{h + 2 * pad}">{body}</svg>')
    return svg, h + 2 * pad, bbox, body


def inset_svg(body, bbox, zoom_box=None):
    """The same drawing zoomed on the lit area, for a round inset (thumbnails of the small areas; design director, round 4)."""
    x0, y0, x1, y1 = bbox
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    side = max(x1 - x0, y1 - y0) * 1.9
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - side / 2:.1f} {cy - side / 2:.1f} {side:.1f} {side:.1f}" '
            f'width="100%" height="100%" preserveAspectRatio="xMidYMid slice">{body}</svg>')


CSS = f"""@font-face{{font-family:P;font-weight:700;src:url(file://{FONTS}/poppins-700.woff2)}}
@font-face{{font-family:P;font-weight:600;src:url(file://{FONTS}/poppins-600.woff2)}}
@font-face{{font-family:In;font-weight:400;src:url(file://{FONTS}/inter-400.woff2)}}
@font-face{{font-family:In;font-weight:600;src:url(file://{FONTS}/inter-600.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}body{{background:#F3F1EC;color:#1D2433;font-family:In;overflow:hidden;position:relative}}
.eb{{font:700 15px P;letter-spacing:.12em;color:#2E6B66}}
.brand{{position:absolute;font:700 17px P}}.bars5{{display:flex;gap:6px;margin-top:6px}}.bars5 b{{width:26px;height:5px;border-radius:3px}}"""
BARS = '<div class="bars5"><b style="background:#C8502F"></b><b style="background:#2E6B66"></b><b style="background:#6A4C93"></b><b style="background:#2F5F9E"></b><b style="background:#A87C1F"></b></div>'
EYEBROW = "CHICAGO · CONSTRUCTION CLEANING · AREA SEAT"   # one string on covers and thumbnails (design director, round 4)


def cover_html(t, svg, price):
    # the text block is centred in one band (y 90 to 630) on all six, so one and two line titles share the same margins;
    # nothing under 20 px, and the price is plain text, not a button (design director, round 4)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:1280px;height:720px}}.l{{position:absolute;left:64px;top:90px;height:540px;width:620px;display:flex;flex-direction:column;justify-content:center}}
h1{{font:700 54px/1.08 P;margin:18px 0 18px;letter-spacing:-.015em;text-wrap:balance}}.sub{{font-size:22px;line-height:1.45;color:#3A4152;text-wrap:pretty;max-width:600px}}
ul{{list-style:none;margin:26px 0 0}}li{{font:600 22px In;margin:12px 0;display:flex;align-items:center;gap:14px}}
li i{{width:26px;height:26px;border-radius:50%;background:#2E6B66;position:relative;flex:none}}
li i:after{{content:"";position:absolute;left:9px;top:5px;width:6px;height:12px;border:solid #fff;border-width:0 2.5px 2.5px 0;transform:rotate(45deg)}}
.price{{display:flex;align-items:baseline;gap:16px;margin-top:30px}}.amt{{font:700 32px P;color:#1D2433}}
.cancel{{font-size:20px;color:#5C6270}}.map{{position:absolute;right:72px;top:40px}}.brand{{right:56px;bottom:40px;text-align:right}}.brand .bars5{{justify-content:flex-end}}
</style></head><body><div class="l"><div class="eb">{EYEBROW}</div>
<h1>{t['name']}</h1>
<p class="sub">Open apartment and commercial projects of $500,000 or more in your area, with the builder on each, every Monday.</p>
<ul><li><i></i>One cleaning company holds this area</li><li><i></i>Closest to a final clean first</li></ul>
<div class="price"><span class="amt">${price} a month</span><span class="cancel">No lock-in. Cancel any time</span></div></div>
<div class="map">{svg}</div><div class="brand">ProofNotFluff{BARS}</div></body></html>"""


def thumb_html(t, svg, inset, colour):
    # a bigger map to the right, the brand bottom left where the map leaves room, and for the small areas a round inset
    # that shows the area three times larger (design director, round 4)
    ins = (f'<div class="ins" style="border-color:#fff;box-shadow:0 0 0 2px {colour}66,0 6px 18px rgba(29,36,51,.18)">{inset}</div>'
           if inset else "")
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
body{{width:600px;height:600px}}.t{{position:absolute;left:40px;top:36px;width:520px}}
.eb{{font-size:13px}}h1{{font:700 34px/1.12 P;margin:8px 0 0;text-wrap:balance}}.map{{position:absolute;right:44px;top:168px}}
.ins{{position:absolute;left:40px;top:250px;width:190px;height:190px;border-radius:50%;overflow:hidden;border:4px solid #fff;background:#F3F1EC}}
.brand{{left:40px;bottom:32px;font-size:15px}}.brand .bars5 b{{width:20px}}
</style></head><body><div class="t"><div class="eb">{EYEBROW}</div><h1>{t['name']}</h1></div>
<div class="map">{svg}</div>{ins}<div class="brand">ProofNotFluff{BARS}</div></body></html>"""


def size(svg, width):
    """Set the drawn width on the <svg> tag; the height follows the viewBox."""
    return re.sub(r'^<svg ([^>]*?)width="[^"]+" height="[^"]+"', lambda m: f'<svg {m.group(1)}width="{width}"', svg, count=1)


async def render(out, price="149"):
    from playwright.async_api import async_playwright
    cfg, geo = A.load(), json.load(open(A.GEO))
    os.makedirs(out, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for n, t in enumerate(cfg["territories"]):
            svg_c, _, _, _ = map_svg(cfg, geo, t["slug"], 500)
            svg_t, _, bbox, body = map_svg(cfg, geo, t["slug"], 420, halo_w=6)
            small = max(bbox[2] - bbox[0], bbox[3] - bbox[1]) < 0.22 * 420   # Loop, Near North, West
            inset = inset_svg(body, bbox) if small else ""
            for name, html, (w, h) in [("cover-1280x720", cover_html(t, size(svg_c, 430), price), (1280, 720)),
                                       ("thumb-600x600", thumb_html(t, size(svg_t, 330), inset, LIT[n]), (600, 600))]:
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
