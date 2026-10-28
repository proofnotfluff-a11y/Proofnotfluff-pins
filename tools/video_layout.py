#!/usr/bin/env python3
"""Rat check layout: every box on screen is decided here, in code, before anything renders. The Remotion template
(video/templates/rat-check) only paints the elements this file lists, at the positions and line breaks it gives, so the
pre-render layout check sees exactly what the frame will show (blueprint gate 5, "Layout, before rendering": each scene
reports its element boxes; code finds no overlaps, nothing outside the safe band and no text under 42 px tall).

Design: the ProofNotFluff tokens (design/CAROUSEL_STANDARD.md; the system wins on a value): canvas #F3F1EC, card #FFFFFF,
line #E2DDD3, ink #1D2433, ink2 #4A5163, accent #C8502F, accent on ink #E88062, soft #B9C0CE, the five brand bars;
Poppins for display, Inter for sentences, both from docs/assets/fonts. Frame 1080 x 1920; all text between y 270 and
1250 and out of the right 150 px (the app's buttons); margins 72 px left.

Used by tools/video_render.py (props for the painter) and tools/video_qa.py (the layout check).
Usage: python3 tools/video_layout.py check <props.json>      PASS or FAIL lines, exit 1 on a FAIL
       python3 tools/video_layout.py --selftest
"""
import hashlib, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FONT_DIR = os.path.join(ROOT, "docs", "assets", "fonts")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "pnf-video-fonts")
T = {"canvas": "#F3F1EC", "card": "#FFFFFF", "line": "#E2DDD3", "ink": "#1D2433", "ink2": "#4A5163", "muted": "#6B7180",
     "teal": "#2E6B66", "accent": "#C8502F", "accentInk": "#E88062", "soft": "#B9C0CE", "white": "#FFFFFF",
     "bars": ["#C8502F", "#2E6B66", "#6B4FA0", "#2F5F9E", "#A87C1F"]}
W, H = 1080, 1920
LEFT, RIGHT = 72, 1080 - 150          # content runs x 72 to 930
SAFE_TOP, SAFE_BOTTOM = 270, 1250
MIN_TEXT = 42
FONTS = {("P", 700): "poppins-700.woff2", ("P", 600): "poppins-600.woff2", ("I", 400): "inter-400.woff2",
         ("I", 600): "inter-600.woff2", ("I", 700): "inter-700.woff2"}
_font_cache = {}


def ttf_path(fam, weight):
    """docs/assets/fonts ships woff2; PIL measures from a TTF converted once into the user cache."""
    src = os.path.join(FONT_DIR, FONTS[(fam, weight)])
    os.makedirs(CACHE, exist_ok=True)
    digest = hashlib.sha256(open(src, "rb").read()).hexdigest()[:12]
    out = os.path.join(CACHE, f"{fam}{weight}-{digest}.ttf")
    if not os.path.exists(out):
        from fontTools.ttLib import TTFont
        f = TTFont(src)
        f.flavor = None
        f.save(out)
    return out


def font(fam, weight, size):
    key = (fam, weight, size)
    if key not in _font_cache:
        from PIL import ImageFont
        _font_cache[key] = ImageFont.truetype(ttf_path(fam, weight), size)
    return _font_cache[key]


def text_width(text, fam, weight, size, tracking=0.0):
    w = font(fam, weight, size).getlength(text)
    return w + tracking * size * max(0, len(text) - 1)


def wrap(text, fam, weight, size, width, tracking=0.0, max_lines=3):
    """Greedy wrap, then balance: no line ends on one orphan word when a better split exists."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, fam, weight, size, tracking) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    if len(lines) >= 2 and len(lines[-1].split()) == 1 and len(lines[-2].split()) > 2:
        a = lines[-2].split()
        cand = [" ".join(a[:-1]), a[-1] + " " + lines[-1]]
        if text_width(cand[1], fam, weight, size, tracking) <= width:
            lines[-2:] = cand
    if len(lines) == 2:   # balance two lines
        best = lines
        best_d = abs(text_width(lines[0], fam, weight, size, tracking) - text_width(lines[1], fam, weight, size, tracking))
        ws = text.split()
        for i in range(1, len(ws)):
            l1, l2 = " ".join(ws[:i]), " ".join(ws[i:])
            w1, w2 = text_width(l1, fam, weight, size, tracking), text_width(l2, fam, weight, size, tracking)
            if w1 <= width and w2 <= width and abs(w1 - w2) < best_d and len(ws[i:]) > 1:
                best, best_d = [l1, l2], abs(w1 - w2)
        lines = best
    if any(text_width(l, fam, weight, size, tracking) > width + 0.5 for l in lines):
        return None
    return lines if len(lines) <= max_lines else None


def text_el(id_, text, x, y, width, fam, weight, size, color, lh=1.15, tracking=0.0, upper=False, max_lines=3,
            t_in=0.0, t_out=None, anim="fade", align="left", shrink_to=None, group=None, role="text"):
    """A text element with its lines and exact box; shrinks the font (never below shrink_to or 42 px) until it fits."""
    s = text.upper() if upper else text
    size0 = size
    while True:
        lines = wrap(s, fam, weight, size, width, tracking, max_lines)
        if lines:
            break
        floor = max(MIN_TEXT, shrink_to or size0)
        if size <= floor:
            lines = wrap(s, fam, weight, size, width, tracking, 99) or [s]
            break
        size -= 2
    widths = [text_width(l, fam, weight, size, tracking) for l in lines]
    w = max(widths) if widths else 0
    h = round(len(lines) * size * lh)
    bx = x if align == "left" else (x + width - w if align == "right" else x + (width - w) / 2)
    return {"id": id_, "kind": "text", "role": role, "text": s, "lines": lines, "x": round(bx, 1), "y": round(y, 1),
            "w": round(w, 1), "h": h, "slotW": width, "font": fam, "weight": weight, "size": size, "lh": lh,
            "tracking": tracking, "color": color, "align": align, "tIn": t_in, "tOut": t_out, "anim": anim, "group": group}


def rect(id_, x, y, w, h, color, radius=0, t_in=0.0, t_out=None, anim="none", role="shape", group=None, line=None):
    return {"id": id_, "kind": "rect", "role": role, "x": x, "y": y, "w": w, "h": h, "color": color, "radius": radius,
            "tIn": t_in, "tOut": t_out, "anim": anim, "group": group, "line": line}


# ---------------------------------------------------------------------------------------------------------------------
# The map: Chicago's 77 community areas from site/geo/chicago-community-areas.json, projected and simplified in code.

def _simplify(pts, tol):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1e-9
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * pts[i][0] - dx * pts[i][1] + x2 * y1 - y2 * x1) / n
        if d > dmax:
            dmax, idx = d, i
    if dmax > tol:
        return _simplify(pts[:idx + 1], tol)[:-1] + _simplify(pts[idx:], tol)
    return [pts[0], pts[-1]]


def map_paths(box, tol=0.9):
    """SVG paths for every community area, fitted into box (x, y, w, h), north up, equal-area enough for a city."""
    geo = json.load(open(os.path.join(ROOT, "site", "geo", "chicago-community-areas.json"), encoding="utf-8"))
    xs, ys = [], []
    for a in geo["areas"]:
        for poly in a["polys"]:
            for ring in poly:
                for lon, lat in ring:
                    xs.append(lon); ys.append(lat)
    lat0 = (min(ys) + max(ys)) / 2
    k = math.cos(math.radians(lat0))
    gw, gh = (max(xs) - min(xs)) * k, max(ys) - min(ys)
    bx, by, bw, bh = box
    s = min(bw / gw, bh / gh)
    ox = bx + (bw - gw * s) / 2
    oy = by + (bh - gh * s) / 2
    out, cent = {}, {}
    for a in geo["areas"]:
        d, area_sum, cx, cy = [], 0.0, 0.0, 0.0
        for poly in a["polys"]:
            for ring in poly:
                pts = [((lon - min(xs)) * k * s + ox, (max(ys) - lat) * s + oy) for lon, lat in ring]
                far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
                simp = _simplify(pts[:far + 1], tol)[:-1] + _simplify(pts[far:], tol)   # a closed ring: split at its far point
                if len(simp) < 3:
                    continue
                d.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in simp) + "Z")
                for i in range(len(pts) - 1):
                    cr = pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
                    area_sum += cr
                    cx += (pts[i][0] + pts[i + 1][0]) * cr
                    cy += (pts[i][1] + pts[i + 1][1]) * cr
        out[a["n"]] = "".join(d)
        if area_sum:
            cent[a["n"]] = (cx / (3 * area_sum), cy / (3 * area_sum))
    used = (ox, oy, gw * s, gh * s)
    return out, cent, used


# ---------------------------------------------------------------------------------------------------------------------
# The layout check: overlaps, safe band, right clear zone, minimum text size, inside the frame.

def overlap(a, b):
    return not (a["x"] + a["w"] <= b["x"] or b["x"] + b["w"] <= a["x"] or a["y"] + a["h"] <= b["y"] or b["y"] + b["h"] <= a["y"])


def inside(a, b, pad=0):
    return (a["x"] >= b["x"] - pad and a["y"] >= b["y"] - pad and a["x"] + a["w"] <= b["x"] + b["w"] + pad
            and a["y"] + a["h"] <= b["y"] + b["h"] + pad)


def live_together(a, b, end):
    ao, bo = a["tOut"] if a["tOut"] is not None else end, b["tOut"] if b["tOut"] is not None else end
    return a["tIn"] < bo and b["tIn"] < ao


def check(props):
    """Every problem with the boxes, as lines. Backgrounds, cards and the map are containers: an element may sit inside
    one; any other two elements on screen at the same time must not touch."""
    els = props["elements"] + [c for c in props.get("captions", [])]
    end = props["seconds"]
    out = []
    drift = props.get("drift", 0)
    for e in els:
        pad = drift if e.get("group") == "pic" else 0
        if e["kind"] in ("text", "caption"):
            if e["size"] < MIN_TEXT:
                out.append(f"{e['id']}: text {e['size']} px is under {MIN_TEXT} px")
            if e["y"] - pad < SAFE_TOP or e["y"] + e["h"] + pad > SAFE_BOTTOM:
                out.append(f"{e['id']}: text at y {e['y']:.0f} to {e['y'] + e['h']:.0f} leaves the safe band {SAFE_TOP} to {SAFE_BOTTOM}")
            if e["x"] < LEFT - 0.5 or e["x"] + e["w"] > RIGHT + 0.5:
                out.append(f"{e['id']}: text at x {e['x']:.0f} to {e['x'] + e['w']:.0f} leaves x {LEFT} to {RIGHT}")
            if e["w"] > e.get("slotW", e["w"]) + 0.5:
                out.append(f"{e['id']}: text is {e['w']:.0f} px wide in a {e['slotW']} px slot (cut off)")
        if e["x"] < 0 or e["y"] < 0 or e["x"] + e["w"] > W or e["y"] + e["h"] > H:
            out.append(f"{e['id']}: outside the 1080 x 1920 frame")
    boxes = [e for e in els if e.get("role") not in ("background",)]
    for i, a in enumerate(boxes):
        for b in boxes[i + 1:]:
            if not live_together(a, b, end):
                continue
            if a.get("role") in ("container", "map") and inside(b, a, 1):
                continue
            if b.get("role") in ("container", "map") and inside(a, b, 1):
                continue
            if a.get("role") == "decor" or b.get("role") == "decor":
                continue
            ga = drift if a.get("group") == "pic" else 0
            gb = drift if b.get("group") == "pic" else 0
            ea = dict(a, x=a["x"] - ga, y=a["y"] - ga, w=a["w"] + 2 * ga, h=a["h"] + 2 * ga)
            eb = dict(b, x=b["x"] - gb, y=b["y"] - gb, w=b["w"] + 2 * gb, h=b["h"] + 2 * gb)
            if overlap(ea, eb):
                out.append(f"{a['id']} and {b['id']} overlap while both are on screen")
    return out


def selftest():
    bad = []
    e = text_el("t", "Rat complaints in South Chicago vs. the same 30 days last year", LEFT, 600, 858, "P", 700, 64, T["ink"])
    if not e["lines"] or e["w"] > 858 or len(e["lines"]) > 3:
        bad.append(f"wrap fits the slot: {e['lines']} {e['w']}")
    if len(e["lines"]) >= 2 and len(e["lines"][-1].split()) == 1:
        bad.append("no orphan word on the last line")
    big = text_el("n", "+221.4%", LEFT, 500, 858, "P", 700, 320, T["ink"], max_lines=1, shrink_to=140)
    if big["w"] > 858 or len(big["lines"]) != 1:
        bad.append(f"the big number shrinks to fit one line ({big['size']} px, {big['w']:.0f} px)")
    good = {"seconds": 50, "elements": [rect("bg", 0, 0, W, H, T["canvas"], role="background"),
                                        dict(text_el("a", "CHICAGO RAT CHECK", LEFT, 300, 858, "P", 700, 42, T["accent"])),
                                        dict(text_el("b", "Rat complaints", LEFT, 400, 858, "P", 700, 64, T["ink"]))], "captions": []}
    if check(good):
        bad.append(f"a clean layout passes: {check(good)}")
    planted = [
        ("text under 42 px", lambda p: p["elements"].append(text_el("s", "Source line", LEFT, 700, 858, "I", 400, 30, T["ink2"]))),
        ("caption outside the safe band", lambda p: p["elements"].append(text_el("c", "Low caption", LEFT, 1300, 858, "I", 600, 56, T["ink"]))),
        ("text in the right 150 px", lambda p: p["elements"].append(text_el("r", "Right", 900, 800, 160, "I", 600, 48, T["ink"]))),
        ("two texts overlapping", lambda p: p["elements"].append(text_el("o", "Rat complaints again", LEFT, 410, 858, "P", 700, 64, T["ink"]))),
    ]
    for name, plant in planted:
        p = json.loads(json.dumps(good))
        plant(p)
        if not check(p):
            bad.append(f"planted {name} is caught")
    later = json.loads(json.dumps(good))
    later["elements"].append(dict(text_el("o2", "Rat complaints again", LEFT, 410, 858, "P", 700, 64, T["ink"]), tIn=10.0))
    later["elements"][2]["tOut"] = 9.0
    if check(later):
        bad.append("two texts at the same place but not on screen together pass")
    paths, cent, used = map_paths((LEFT, 470, 460, 560))
    if len(paths) != 77 or not all(paths.values()):
        bad.append(f"the map has 77 outlines ({len(paths)})")
    if not (LEFT - 1 <= used[0] and used[0] + used[2] <= LEFT + 461 and 469 <= used[1] and used[1] + used[3] <= 1031):
        bad.append(f"the map fits its box {used}")
    for b in bad:
        print("FAIL", b)
    print(f"video_layout selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (wrap, no orphan, shrink to fit, clean pass, "
          "under 42 px, safe band, right zone, overlap, time-separated pass, map outlines)")
    return 1 if bad else 0


def main():
    if sys.argv[1:2] == ["--selftest"]:
        sys.exit(selftest())
    if sys.argv[1:2] == ["check"] and len(sys.argv) > 2:
        props = json.load(open(sys.argv[2], encoding="utf-8"))
        p = check(props)
        for x in p:
            print("FAIL layout:", x)
        n = len(props["elements"]) + len(props.get("captions", []))
        print(f"layout: {'PASS' if not p else 'FAIL'} {n} boxes, {len(p)} problems")
        sys.exit(1 if p else 0)
    print(__doc__)


if __name__ == "__main__":
    main()
