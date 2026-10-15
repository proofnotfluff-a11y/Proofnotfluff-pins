#!/usr/bin/env python3
"""Fiverr gig gallery images in the v3 house style, from the real product.

Usage: python3 tools/fiverr_images.py <spec.json> <out_dir>

Fiverr shows gig images at 1280 x 769 (about 5:3; minimum 712 x 430) and as small cards in search, so the cover
puts the promise in big type on an ink panel at the left and the real product on the right. Every image is drawn
at twice that size and scaled down, so text stays crisp. Screenshots come from tools/render_xlsx.py PNGs or
browser screenshots of our own pages; nothing is mocked up. Any image that shows example numbers carries a
"stamp" (for example "SAMPLE DATA"), so no one mistakes it for a client's results.

spec.json (paths relative to the spec file, or to "base"):
{
  "footer": "Excel + Google Sheets  |  Built with your numbers",
  "images": [
    {"type": "cover", "name": "gig1-cover", "eyebrow": "13-WEEK CASH FLOW",
     "title": "See your lowest cash week before it hits.", "sub": "Built for your brand, with your numbers.",
     "badges": ["Shopify", "Amazon", "TikTok Shop"],
     "shot": "r/01-Dashboard.png", "crop": [0, 0, 1, 0.5], "stamp": "SAMPLE DATA"},
    {"type": "shot", "name": "gig1-dashboard", "eyebrow": "THE DASHBOARD", "title": "...", "sub": "...",
     "shot": "...", "crop": [0, 0, 1, 1], "trim": false, "stamp": "SAMPLE DATA",
     "marks": [{"box": [0.05, 0.1, 0.5, 0.3], "label": "Lowest cash week"}]},
    {"type": "inside", "name": "gig1-whats-inside", "eyebrow": "WHAT YOU GET", "title": "...",
     "items": ["...", "..."], "shot": "...", "crop": [0, 0, 1, 1], "stamp": "SAMPLE DATA"}
  ]
}
crop and box values are fractions (left, top, right, bottom): crop of the source PNG, box of the cropped area.
"trim": true cuts the sheet's canvas and card frame off a one-card crop. "fit": "width" (fill the card's width and
fade out at the bottom) or "contain" (show the whole crop); covers default to width, the rest to contain.
Output: <out_dir>/<name>.png at 1280 x 769, names letters, numbers and hyphens only (Fiverr's file rule).
Open every image with the Read tool afterwards and check every number against the product.
"""
import json, os, re, sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from listing_images import (ACCENT, ACCENT_ON_INK, CANVAS, CARD, INK, INK2, MUTED, ON_INK_SOFT,  # noqa: E402
                            bars, check, font, load_crop, shadow_card, text_block, wrap)

W, H = 2560, 1538          # drawn at 2x
OUT = (1280, 769)          # Fiverr's recommended gallery size
M = 110
WHITE = (255, 255, 255)


def card(img, shot, box, pad=22, radius=26, fit="contain", marks=None, stamp=None):
    """A framed white card holding the screenshot; returns the card's box."""
    x0, y0, x1, y1 = box
    iw, ih = x1 - x0 - 2 * pad, y1 - y0 - 2 * pad
    if fit == "contain":  # the whole crop shows; the card shrinks around it, centred
        scale = min(iw / shot.width, ih / shot.height)
        nw, nh = max(1, int(shot.width * scale)), max(1, int(shot.height * scale))
        x0 += (iw - nw) // 2
        y0 += (ih - nh) // 2
        x1, y1, iw, ih = x0 + nw + 2 * pad, y0 + nh + 2 * pad, nw, nh
        s, cut = shot.resize((iw, ih), Image.LANCZOS), False
    else:  # fill the width; a long crop fades out at the bottom, a short one gets a shorter card, centred
        s = shot.resize((iw, max(1, round(shot.height * iw / shot.width))), Image.LANCZOS)
        cut = s.height > ih
        if not cut:
            y0 += (ih - s.height) // 2
            ih = s.height
            y1 = y0 + ih + 2 * pad
        s = s.crop((0, 0, iw, min(ih, s.height)))
    shadow_card(img, (x0, y0, x1, y1), radius=radius)
    img.paste(s, (x0 + pad, y0 + pad))
    if cut:  # soft fade into the card so a cut screenshot reads as "continues below"
        fh = min(130, s.height // 3)
        fade = Image.linear_gradient("L").resize((iw, fh))
        img.paste(Image.new("RGB", (iw, fh), CARD), (x0 + pad, y0 + pad + s.height - fh), fade)
    d = ImageDraw.Draw(img)
    for mk in marks or []:
        bx0, by0, bx1, by1 = mk["box"]
        rx0, rx1 = x0 + pad + bx0 * iw, x0 + pad + bx1 * iw
        ry0, ry1 = y0 + pad + by0 * s.height, y0 + pad + by1 * s.height
        d.rounded_rectangle([rx0 - 8, ry0 - 8, rx1 + 8, ry1 + 8], radius=16, outline=ACCENT, width=7)
        if mk.get("label"):
            f = font("Bold", 36)
            pw, ph = d.textlength(mk["label"], font=f) + 48, 62
            lx = min(max(rx0 - 8, x0 + pad), x1 - pad - pw)
            ly = ry0 - 8 - ph - 10
            if ly < y0 + pad:  # no room above the box: sit just under it
                ly = ry1 + 8 + 10
            d.rounded_rectangle([lx, ly, lx + pw, ly + ph], radius=ph // 2, fill=ACCENT)
            d.text((lx + 24, ly + 9), mk["label"], font=f, fill=WHITE)
    if stamp:  # a tag straddling the card's top edge, so it never hides a number
        f = font("Bold", 32)
        pw, ph = d.textlength(stamp, font=f) + 44, 56
        sx, sy = x1 - pw - 36, y0 - ph // 2
        d.rounded_rectangle([sx, sy, sx + pw, sy + ph], radius=ph // 2, fill=ACCENT)
        d.text((sx + 22, sy + 8), stamp, font=f, fill=WHITE)
    return (x0, y0, x1, y1)


def footer(d, text, on_ink_until=0):
    d.text((M, H - 122), "ProofNotFluff", font=font("Bold", 48), fill=WHITE if on_ink_until > M else INK)
    if text:
        f = font("Regular", 36)
        tw = d.textlength(text, font=f)
        d.text((W - M - tw, H - 112), text, font=f, fill=MUTED)


def cover(spec, img, base, foot):
    d = ImageDraw.Draw(img)
    split = int(W * 0.46)
    d.rectangle([0, 0, split, H], fill=INK)
    tw = split - 2 * M
    bars(d, M, 112, w=78, h=14, gap=16)
    d.text((M, 168), spec["eyebrow"], font=font("Bold", 46), fill=ACCENT_ON_INK)
    y = text_block(d, (M, 248), spec["title"], font("Bold", 112), WHITE, tw, 1.0, max_lines=4)
    if spec.get("sub"):
        y = text_block(d, (M, y + 26), spec["sub"], font("Regular", 48), ON_INK_SOFT, tw, 1.15, max_lines=3)
    bf, x, by = font("Medium", 38), M, y + 40
    for b in spec.get("badges") or []:
        bw = d.textlength(b, font=bf) + 52
        if x + bw > split - M:  # wrap the pills onto a second row
            x, by = M, by + 84
        d.rounded_rectangle([x, by, x + bw, by + 66], radius=33, outline=ON_INK_SOFT, width=3)
        d.text((x + 26, by + 10), b, font=bf, fill=WHITE)
        x += bw + 18
    if by + 66 > H - 170:
        sys.exit(f"{spec['name']}: the cover text runs into the footer; shorten the title, sub or badges")
    footer(d, "", on_ink_until=split)
    shot = load_crop(base, spec["shot"], spec["crop"], spec.get("trim", False))
    card(img, shot, (split + 90, 112, W - M, H - 112), fit=spec.get("fit", "width"), marks=spec.get("marks"),
         stamp=spec.get("stamp"))


def shot_image(spec, img, base, foot):
    d = ImageDraw.Draw(img)
    bars(d, M, 100, w=78, h=14, gap=16)
    d.text((M, 150), spec["eyebrow"], font=font("Bold", 44), fill=ACCENT)
    y = text_block(d, (M, 212), spec["title"], font("Bold", 84), INK, W - 2 * M, 1.0, max_lines=2)
    if spec.get("sub"):
        y = text_block(d, (M, y + 8), spec["sub"], font("Regular", 44), INK2, W - 2 * M, 1.12, max_lines=1)
    shot = load_crop(base, spec["shot"], spec["crop"], spec.get("trim", False))
    card(img, shot, (M, y + 40, W - M, H - 160), fit=spec.get("fit", "contain"), marks=spec.get("marks"),
         stamp=spec.get("stamp"))
    footer(d, foot)


def inside(spec, img, base, foot):
    d = ImageDraw.Draw(img)
    left = int(W * 0.47)
    bars(d, M, 100, w=78, h=14, gap=16)
    d.text((M, 150), spec.get("eyebrow", "WHAT YOU GET"), font=font("Bold", 44), fill=ACCENT)
    y = text_block(d, (M, 212), spec["title"], font("Bold", 84), INK, left - M, 1.0, max_lines=2) + 30
    f = font("Regular", 46)
    for item in spec.get("items", []):
        check(d, M, y + 4, r=26)
        y = text_block(d, (M + 84, y), item, f, INK, left - M - 84, 1.12, max_lines=2) + 22
    if y > H - 170:
        sys.exit(f"{spec['name']}: the list runs into the footer; cut items or words")
    shot = load_crop(base, spec["shot"], spec["crop"], spec.get("trim", False))
    card(img, shot, (left + 70, 112, W - M, H - 160), fit=spec.get("fit", "contain"), marks=spec.get("marks"),
         stamp=spec.get("stamp"))
    footer(d, foot)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path, encoding="utf-8"))
    base = spec.get("base") or os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(out, exist_ok=True)
    foot = spec.get("footer", "Excel + Google Sheets  |  Built with your numbers")
    for item in spec["images"]:
        if not re.fullmatch(r"[A-Za-z0-9-]+", item["name"]):
            sys.exit(f"{item['name']}: Fiverr file names take letters, numbers and hyphens only")
        if "—" in json.dumps(item, ensure_ascii=False):
            sys.exit(f"{item['name']}: an em dash in the copy")
        img = Image.new("RGBA", (W, H), CANVAS + (255,))
        {"cover": cover, "shot": shot_image, "inside": inside}[item["type"]](item, img, base, foot)
        p = os.path.join(out, item["name"] + ".png")
        img.convert("RGB").resize(OUT, Image.LANCZOS).save(p, optimize=True)
        print(p)


if __name__ == "__main__":
    main()
