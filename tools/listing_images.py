#!/usr/bin/env python3
"""Etsy listing images from a product's real renders, in the v3 house style.

Usage: python3 tools/listing_images.py <spec.json> <out_dir>

Every image is 2000 x 2000 and shows the real product: screenshots come from
tools/render_xlsx.py PNGs (render at --dpi 220 for crisp crops). Nothing is mocked up.

spec.json:
{
  "formats": "Excel, Google Sheets, LibreOffice | Instant download",
  "images": [
    {"type": "cover", "eyebrow": "HOURLY RATE CALCULATOR", "title": "Know the hourly rate that pays you.",
     "sub": "Type six numbers. Get your minimum rate, ...",
     "shot": "r/02-Calculator.png", "crop": [0, 0, 1, 0.30]},
    {"type": "shot", "eyebrow": "SEE THE MATH", "title": "...", "sub": "...",
     "shot": "r/02-Calculator.png", "crop": [0, 0.1, 1, 0.42],
     "marks": [{"box": [0.47, 0.05, 1, 0.6], "label": "Every dollar traced"}]},
    {"type": "inside", "title": "What's inside",
     "tabs": [{"name": "Calculator", "shot": "r/02-Calculator.png", "crop": [0, 0, 1, 0.5]}],
     "items": ["Minimum hourly rate, rounded for your rate card", "..."]}
  ]
}
"trim": true cuts the sheet's canvas and card frame off a one-card crop (use it whenever
the crop is a single card). Marks draw an accent outline; a label sits beside the card
when there is room, else on the outline.
crop and box values are fractions (left, top, right, bottom): crop of the source PNG,
box of the cropped area. Output files: 1-<type>.png, 2-<type>.png, ... in order.
Open every image with the Read tool afterwards; check every number against the product.
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2000
INK, INK2, MUTED = (29, 36, 51), (74, 81, 99), (123, 129, 141)
CANVAS, CARD, FRAME = (243, 241, 236), (255, 255, 255), (226, 221, 211)
ACCENT, ACCENT_ON_INK, ON_INK_SOFT = (200, 80, 47), (232, 128, 98), (185, 192, 206)
TEAL, TEAL_TINT = (46, 107, 102), (226, 239, 236)
BARS = [(200, 80, 47), (46, 107, 102), (107, 79, 160), (47, 95, 158), (168, 124, 31)]
FONT_DIR = "/usr/share/fonts/truetype/google-fonts"
M = 130  # outer margin


def font(weight, size):
    for name in (f"Poppins-{weight}.ttf", "Poppins-Regular.ttf"):
        p = os.path.join(FONT_DIR, name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", size)


def wrap(draw, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, f, fill, width, leading=1.18, max_lines=None):
    x, y = xy
    lines = wrap(draw, text, f, width)
    if max_lines and len(lines) > max_lines:
        sys.exit(f"text too long for {max_lines} lines: {text!r}")
    asc, desc = f.getmetrics()
    step = int((asc + desc) * leading)
    for ln in lines:
        draw.text((x, y), ln, font=f, fill=fill)
        y += step
    return y


def bars(draw, x, y, w=96, h=16, gap=18):
    for i, c in enumerate(BARS):
        draw.rounded_rectangle([x + i * (w + gap), y, x + i * (w + gap) + w, y + h], radius=h // 2, fill=c)


def _plain(px_line):
    """True when a pixel row or column is one flat color: canvas, a frame line or blank card.
    The outer 4% at each end is ignored so a sliver of a neighbouring card at the crop edge
    doesn't count, but a short line of text anywhere else does."""
    n = len(px_line)
    cut = max(1, int(n * 0.04))
    core = px_line[cut:n - cut] or px_line
    ref = sorted(core)[len(core) // 2]
    if not any(max(abs(ref[i] - k[i]) for i in range(3)) <= 3 for k in (CANVAS, CARD, FRAME, (239, 235, 228))):
        return False  # a flat tinted band (a status pill, a total row) is content, never trimmed
    off = sum(1 for c in core if max(abs(c[i] - ref[i]) for i in range(3)) > 6)
    return off <= max(1, len(core) // 500)


def trim(im, keep=70):
    """Cut flat canvas, frame lines and empty card padding off every edge, then keep a
    small white margin, so a crop of one card never shows the sheet's own frame."""
    W, H = im.size
    px = im.load()
    step = max(1, min(W, H) // 400)
    rows = lambda y: [px[x, y] for x in range(0, W, step)]
    cols = lambda x: [px[x, y] for y in range(0, H, step)]
    t, b, l, r = 0, H - 1, 0, W - 1
    rows = lambda y: [px[x, y] for x in range(l, r + 1, step)]
    cols = lambda x: [px[x, y] for y in range(t, b + 1, step)]
    while True:  # repeat: once the canvas above a card is gone, its frame line becomes flat too
        before = (t, b, l, r)
        while t < b and _plain(rows(t)): t += 1
        while b > t and _plain(rows(b)): b -= 1
        while l < r and _plain(cols(l)): l += 1
        while r > l and _plain(cols(r)): r -= 1
        if (t, b, l, r) == before:
            break
    inner = im.crop((l, t, r + 1, b + 1))
    out = Image.new("RGB", (inner.width + 2 * keep, inner.height + 2 * keep), CARD)
    out.paste(inner, (keep, keep))
    return out


def load_crop(base, shot, crop, trim_edges=False):
    im = Image.open(os.path.join(base, shot)).convert("RGB")
    W, H = im.size
    x0, y0, x1, y1 = crop
    im = im.crop((int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H)))
    return trim(im) if trim_edges else im


def shadow_card(img, box, radius=28, blur=34, offset=18, alpha=70):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(sh)
    d.rounded_rectangle([x0, y0 + offset, x1, y1 + offset], radius=radius, fill=(20, 24, 36, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(sh)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(box, radius=radius, fill=CARD + (255,), outline=FRAME + (255,), width=2)


def place_shot(img, shot, box, pad=26, radius=28, marks=None, fit="width"):
    """Draw a framed card in box and fit the screenshot inside.
    fit="width": fill the width and fade out if it runs long (cover, thumbnails).
    fit="contain": shrink the card, centered, so the whole crop shows (detail shots)."""
    x0, y0, x1, y1 = box
    iw, ih = x1 - x0 - 2 * pad, y1 - y0 - 2 * pad
    if fit == "contain" and shot.height * iw / shot.width > ih:
        nw = int(ih * shot.width / shot.height)
        x0 += (iw - nw) // 2; x1 = x0 + nw + 2 * pad; iw = nw
    if fit == "contain":
        h = 2 * pad + int(shot.height * iw / shot.width)
        if h < y1 - y0:  # center the card in the space it was given
            y0 += (y1 - y0 - h) // 2
        y1 = y0 + h
        box = (x0, y0, x1, y1)
    shadow_card(img, box, radius=radius)
    scale = iw / shot.width
    s = shot.resize((iw, max(1, int(shot.height * scale))), Image.LANCZOS)
    cut = s.height > ih
    s = s.crop((0, 0, iw, min(ih, s.height)))
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    layer.paste(s, (x0 + pad, y0 + pad))
    if cut:  # soft fade into the card so a cut screenshot reads as "continues below"
        fade = Image.new("L", (iw, 140))
        for yy in range(140):
            fade.paste(int(255 * yy / 139), (0, yy, iw, yy + 1))
        white = Image.new("RGBA", (iw, 140), CARD + (255,))
        layer.paste(white, (x0 + pad, y0 + pad + s.height - 140), fade)
    mask = Image.new("L", img.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([x0 + 2, y0 + 2, x1 - 2, y1 - 2], radius=radius - 2, fill=255)
    img.paste(layer, (0, 0), Image.composite(layer, Image.new("RGBA", img.size), mask).split()[3])
    d = ImageDraw.Draw(img)
    for mk in marks or []:
        bx0, by0, bx1, by1 = mk["box"]
        rx0 = x0 + pad + bx0 * iw; rx1 = x0 + pad + bx1 * iw
        ry0 = y0 + pad + by0 * s.height; ry1 = y0 + pad + by1 * s.height
        d.rounded_rectangle([rx0 - 10, ry0 - 10, rx1 + 10, ry1 + 10], radius=18, outline=ACCENT, width=8)
        if mk.get("label"):
            f = font("Bold", 40)
            tw = d.textlength(mk["label"], font=f)
            pw, ph = tw + 56, 68
            cy = (ry0 + ry1) / 2
            if S - M - x1 >= pw + 40:      # room to the right of the card
                lx, ly = x1 + 40, cy - ph / 2
                d.line([(rx1 + 10, cy), (lx, cy)], fill=ACCENT, width=6)
            elif x0 - M >= pw + 40:        # room to the left
                lx, ly = x0 - 40 - pw, cy - ph / 2
                d.line([(lx + pw, cy), (rx0 - 10, cy)], fill=ACCENT, width=6)
            else:                          # on the outline's top edge
                lx, ly = min(max(rx0 - 10, M), S - M - pw), ry0 - 10 - ph / 2
            d.rounded_rectangle([lx, ly, lx + pw, ly + ph], radius=ph // 2, fill=ACCENT)
            d.text((lx + 28, ly + 9), mk["label"], font=f, fill=(255, 255, 255))


def footer(img, formats, on_ink=False):
    d = ImageDraw.Draw(img)
    col = (255, 255, 255) if on_ink else INK
    soft = ON_INK_SOFT if on_ink else MUTED
    f1, f2 = font("Bold", 46), font("Regular", 34)
    d.text((M, S - 112), "ProofNotFluff", font=f1, fill=col)
    tw = d.textlength(formats, font=f2)
    d.text((S - M - tw, S - 104), formats, font=f2, fill=soft)


def cover(spec, im, base, formats):
    d = ImageDraw.Draw(im)
    bars(d, M, 120)
    d.text((M, 196), spec["eyebrow"], font=font("Bold", 44), fill=ACCENT_ON_INK)
    tf, sf = font("Bold", 104), font("Regular", 46)
    # measure first so the ink band ends just under the card's top edge
    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    a1, d1 = tf.getmetrics(); a2, d2 = sf.getmetrics()
    h = len(wrap(probe, spec["title"], tf, S - 2 * M)) * int((a1 + d1) * 0.98) + 22 + \
        len(wrap(probe, spec["sub"], sf, S - 2 * M)) * int((a2 + d2) * 1.12)
    top = 266 + h + 70
    if top > 900:
        sys.exit("cover title and sub are too long; keep them to 2 + 2 lines")
    d.rectangle([0, 0, S, top + 150], fill=INK)
    bars(d, M, 120)
    d.text((M, 196), spec["eyebrow"], font=font("Bold", 44), fill=ACCENT_ON_INK)
    y = text_block(d, (M, 266), spec["title"], tf, (255, 255, 255), S - 2 * M, 0.98, max_lines=3)
    text_block(d, (M, y + 22), spec["sub"], sf, ON_INK_SOFT, S - 2 * M, 1.12, max_lines=3)
    shot = load_crop(base, spec["shot"], spec["crop"])
    place_shot(im, shot, (M, top, S - M, S - 170), marks=spec.get("marks"))
    footer(im, formats)


def shot_image(spec, im, base, formats):
    d = ImageDraw.Draw(im)
    bars(d, M, 120)
    d.text((M, 196), spec["eyebrow"], font=font("Bold", 44), fill=ACCENT)
    y = text_block(d, (M, 266), spec["title"], font("Bold", 88), INK, S - 2 * M, 0.98, max_lines=2)
    if spec.get("sub"):
        y = text_block(d, (M, y + 14), spec["sub"], font("Regular", 44), INK2, S - 2 * M, 1.12, max_lines=2)
    shot = load_crop(base, spec["shot"], spec["crop"], spec.get("trim", False))
    place_shot(im, shot, (M, y + 70, S - M, S - 170), marks=spec.get("marks"), fit="contain")
    footer(im, formats)


def check(d, x, y, r=30):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=TEAL)
    d.line([(x + r * 0.55, y + r * 1.02), (x + r * 0.88, y + r * 1.36), (x + r * 1.48, y + r * 0.7)], fill=(255, 255, 255), width=8, joint="curve")


def inside(spec, im, base, formats):
    d = ImageDraw.Draw(im)
    bars(d, M, 120)
    d.text((M, 196), spec.get("eyebrow", "ONE DOWNLOAD"), font=font("Bold", 44), fill=ACCENT)
    text_block(d, (M, 266), spec.get("title", "What's inside"), font("Bold", 88), INK, S - 2 * M, 0.98, max_lines=1)
    tabs = spec.get("tabs", [])
    n = max(1, len(tabs))
    gap = 50
    tw = (S - 2 * M - gap * (n - 1)) // n
    top, th = 430, 760
    for i, t in enumerate(tabs):
        x0 = M + i * (tw + gap)
        place_shot(im, load_crop(base, t["shot"], t["crop"]), (x0, top, x0 + tw, top + th), pad=18, radius=22)
        d = ImageDraw.Draw(im)
        f = font("Medium", 40)
        lw = d.textlength(t["name"], font=f)
        d.rounded_rectangle([x0, top + th + 34, x0 + lw + 48, top + th + 100], radius=33, fill=TEAL_TINT)
        d.text((x0 + 24, top + th + 42), t["name"], font=f, fill=TEAL)
    y = top + th + 165
    f = font("Regular", 40)
    a, de = f.getmetrics(); lh = int((a + de) * 1.08)
    items = spec.get("items", [])
    colw = (S - 2 * M - 60) // 2
    half = (len(items) + 1) // 2
    for col, chunk in enumerate((items[:half], items[half:])):
        cx, cy = M + col * (colw + 60), y
        for it in chunk:
            check(d, cx, cy + 2, r=26)
            end = text_block(d, (cx + 76, cy), it, f, INK, colw - 80, 1.08, max_lines=2)
            cy = end + 30
        if cy > S - 190:
            sys.exit("the inside list runs into the footer; cut items or words")
    footer(im, formats)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    spec_path, out = sys.argv[1], sys.argv[2]
    spec = json.load(open(spec_path))
    base = spec.get("base") or os.path.dirname(os.path.abspath(spec_path))
    os.makedirs(out, exist_ok=True)
    formats = spec.get("formats", "Excel, Google Sheets, LibreOffice | Instant download")
    for i, img in enumerate(spec["images"], 1):
        im = Image.new("RGBA", (S, S), CANVAS + (255,))
        {"cover": cover, "shot": shot_image, "inside": inside}[img["type"]](img, im, base, formats)
        p = os.path.join(out, f"{i}-{img['type']}.png")
        im.convert("RGB").save(p, optimize=True)
        print(p)


if __name__ == "__main__":
    main()
