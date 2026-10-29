#!/usr/bin/env python3
"""Preflight for a ProofNotFluff KDP print pack.

Usage: python3 preflight.py <pack dir> <expected pages> [--render-pages 1,2,3]

Checks (written to <pack dir>/preflight.json):
- page count, and every page exactly 612 x 792 pt
- nothing drawn inside the KDP margins: 0.375 in on the gutter side (left on
  odd pages, right on even pages), 0.25 in on the other three sides; checked
  two ways: vector objects via pdfplumber and rendered pixels at 150 dpi
- pdffonts: every font embedded
- no AcroForm and no widget annotations
- interior is grayscale (rendered pixels have R = G = B)
- cover page size equals the computed spread within 0.5 pt
- extracted text has no em dashes and no banned words
- renders: 50 dpi contact sheet of every page, 150 dpi of chosen pages and
  the cover, into <pack dir>/render/
"""
import glob
import json
import os
import re
import subprocess
import sys

import pdfplumber
import pikepdf
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnfprint as P  # noqa: E402

PT = 72.0
GUTTER = 0.375 * PT
OUTER = 0.25 * PT


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def page_box(page_no, w, h):
    """Allowed content box (x0, y0, x1, y1) in PDF points, origin bottom-left."""
    if page_no % 2 == 1:
        return GUTTER, OUTER, w - OUTER, h - OUTER
    return OUTER, OUTER, w - GUTTER, h - OUTER


def check_vectors(interior):
    """Every char, line, rect, curve and image must sit inside the allowed box.
    Returns a list of violations."""
    viol = []
    with pdfplumber.open(interior) as pdf:
        for i, page in enumerate(pdf.pages):
            n = i + 1
            w, h = page.width, page.height
            x0, y0, x1, y1 = page_box(n, w, h)
            objs = []
            for kind in ("chars", "lines", "rects", "curves", "images"):
                for o in getattr(page, kind):
                    objs.append((kind, o))
            for kind, o in objs:
                # pdfplumber: top/bottom measured from the page top
                ox0, ox1 = o["x0"], o["x1"]
                oy0, oy1 = h - o["bottom"], h - o["top"]
                if kind == "chars" and not o.get("text", "").strip():
                    continue
                if ox0 < x0 - 0.3 or ox1 > x1 + 0.3 or oy0 < y0 - 0.3 or oy1 > y1 + 0.3:
                    viol.append({"page": n, "kind": kind,
                                 "bbox": [round(ox0, 1), round(oy0, 1), round(ox1, 1), round(oy1, 1)],
                                 "text": o.get("text", "")[:30]})
    return viol


def check_overlaps(interior, tol=0.8):
    """Chars on the same baseline must not overprint: a glyph whose x0 sits
    more than tol pt left of the previous glyph's x1 is flagged (catches
    table headers that run into the next column)."""
    hits = []
    with pdfplumber.open(interior) as pdf:
        for i, page in enumerate(pdf.pages):
            lines = {}
            for ch in page.chars:
                if not ch.get("text", "").strip():
                    continue
                lines.setdefault(round(ch["bottom"], 1), []).append(ch)
            for base, chars in lines.items():
                chars.sort(key=lambda c: c["x0"])
                for a, b in zip(chars, chars[1:]):
                    if b["x0"] < a["x1"] - tol:
                        hits.append({"page": i + 1, "baseline": base,
                                     "chars": a["text"] + "|" + b["text"],
                                     "overlap_pt": round(a["x1"] - b["x0"], 2)})
    return hits


def check_pixels(interior, outdir):
    """Render at 150 dpi and confirm the margin strips are pure white and the
    page is grayscale."""
    os.makedirs(outdir, exist_ok=True)
    prefix = os.path.join(outdir, "px")
    for f in glob.glob(prefix + "*.png"):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", "150", "-png", interior, prefix], check=True)
    files = sorted(glob.glob(prefix + "-*.png"))
    viol = []
    not_gray = []
    dpi = 150
    g = int(round(0.375 * dpi))
    o = int(round(0.25 * dpi))
    for i, f in enumerate(files):
        n = i + 1
        im = Image.open(f).convert("RGB")
        W, H = im.size
        # grayscale check
        r, gg, b = im.split()
        diff = max(Image.eval(Image.merge("RGB", (r, gg, b)).convert("L"), lambda v: v).getextrema())
        px = im.getdata()
        # sample every 7th pixel for speed
        bad = 0
        for j in range(0, len(px), 7):
            p = px[j]
            if abs(p[0] - p[1]) > 2 or abs(p[1] - p[2]) > 2:
                bad += 1
                if bad > 5:
                    break
        if bad > 5:
            not_gray.append(n)
        left = g if n % 2 == 1 else o
        right = o if n % 2 == 1 else g
        strips = {
            "left": im.crop((0, 0, left, H)),
            "right": im.crop((W - right, 0, W, H)),
            "top": im.crop((0, 0, W, o)),
            "bottom": im.crop((0, H - o, W, H)),
        }
        for name, strip in strips.items():
            lo, hi = strip.convert("L").getextrema()
            if lo < 250:
                viol.append({"page": n, "strip": name, "darkest": lo})
        del diff
    for f in files:
        os.remove(f)
    return viol, not_gray


def check_fonts(pdf):
    out = run(["pdffonts", pdf])
    rows = [ln for ln in out.splitlines()[2:] if ln.strip()]
    fonts = []
    not_emb = []
    for ln in rows:
        parts = ln.split()
        # name may contain spaces; emb column is the 4th from the end: emb sub uni objectID(2 tokens)
        emb = parts[-5]
        name = parts[0]
        fonts.append({"name": name, "embedded": emb == "yes"})
        if emb != "yes":
            not_emb.append(name)
    return fonts, not_emb


def check_forms(pdf):
    with pikepdf.open(pdf) as doc:
        has_acroform = "/AcroForm" in doc.Root
        widgets = 0
        for page in doc.pages:
            for a in page.get("/Annots", []):
                if a.get("/Subtype") == "/Widget":
                    widgets += 1
        return has_acroform, widgets


def page_sizes(pdf):
    with pikepdf.open(pdf) as doc:
        sizes = []
        for page in doc.pages:
            box = [float(v) for v in page.MediaBox]
            sizes.append((round(box[2] - box[0], 2), round(box[3] - box[1], 2)))
        return sizes


def text_checks(pdf):
    txt = run(["pdftotext", "-layout", pdf, "-"])
    hits = []
    for i, page in enumerate(txt.split("\f")):
        probs = P.copy_problems(page)
        if probs:
            # locate the lines
            for ln in page.splitlines():
                lp = P.copy_problems(ln)
                if lp:
                    hits.append({"page": i + 1, "problems": lp, "line": ln.strip()[:100]})
    en = txt.count("–")
    return hits, en, txt


def render(interior, cover, outdir, pages_150):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.png")):
        os.remove(f)
    subprocess.run(["pdftoppm", "-r", "50", "-png", interior, os.path.join(outdir, "p")], check=True)
    files = sorted(glob.glob(os.path.join(outdir, "p-*.png")))
    ims = [Image.open(f).convert("RGB") for f in files]
    w, h = ims[0].size
    cols = 6
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (w + 6), rows * (h + 6)), (110, 110, 110))
    for i, im in enumerate(ims):
        sheet.paste(im, ((i % cols) * (w + 6), (i // cols) * (h + 6)))
    sheet.save(os.path.join(outdir, "contact-sheet.png"))
    for f in files:
        os.remove(f)
    for pg in pages_150:
        subprocess.run(["pdftoppm", "-r", "150", "-png", "-f", str(pg), "-l", str(pg), interior,
                        os.path.join(outdir, "page")], check=True)
    subprocess.run(["pdftoppm", "-r", "60", "-png", cover, os.path.join(outdir, "cover")], check=True)
    return sorted(os.path.basename(f) for f in glob.glob(os.path.join(outdir, "*.png")))


def main():
    pack = os.path.abspath(sys.argv[1])
    expected = int(sys.argv[2])
    pages_150 = [1, 2]
    if "--render-pages" in sys.argv:
        pages_150 = [int(x) for x in sys.argv[sys.argv.index("--render-pages") + 1].split(",")]
    interior = os.path.join(pack, "interior.pdf")
    cover = os.path.join(pack, "cover.pdf")
    report = {"pack": pack, "interior": "interior.pdf", "cover": "cover.pdf", "checks": {}}
    ok_all = True

    sizes = page_sizes(interior)
    n = len(sizes)
    bad_sizes = [i + 1 for i, s in enumerate(sizes) if s != (612.0, 792.0)]
    report["checks"]["page_count"] = {"value": n, "expected": expected, "range_ok": 24 <= n <= 110,
                                      "ok": n == expected and 24 <= n <= 110}
    report["checks"]["trim_size"] = {"all_612x792": not bad_sizes, "bad_pages": bad_sizes,
                                     "ok": not bad_sizes}
    ok_all &= report["checks"]["page_count"]["ok"] and not bad_sizes

    viol = check_vectors(interior)
    report["checks"]["margins_vector"] = {
        "rule": "gutter 0.375 in (left on odd pages, right on even), 0.25 in elsewhere",
        "violations": viol[:40], "count": len(viol), "ok": not viol}
    ok_all &= not viol

    overlaps = check_overlaps(interior)
    report["checks"]["glyph_overlaps"] = {"rule": "same baseline, x0 < previous x1 - 0.8 pt",
                                          "hits": overlaps[:40], "count": len(overlaps),
                                          "ok": not overlaps}
    ok_all &= not overlaps

    pviol, not_gray = check_pixels(interior, os.path.join(pack, "render"))
    report["checks"]["margins_pixels_150dpi"] = {"violations": pviol[:40], "count": len(pviol),
                                                  "ok": not pviol}
    report["checks"]["grayscale"] = {"non_gray_pages": not_gray, "ok": not not_gray}
    ok_all &= not pviol and not not_gray

    fonts, not_emb = check_fonts(interior)
    report["checks"]["fonts_interior"] = {"fonts": fonts, "not_embedded": not_emb, "ok": not not_emb}
    cfonts, cnot = check_fonts(cover)
    report["checks"]["fonts_cover"] = {"fonts": cfonts, "not_embedded": cnot, "ok": not cnot}
    ok_all &= not not_emb and not cnot

    acro, widgets = check_forms(interior)
    report["checks"]["no_form_fields"] = {"acroform": acro, "widget_annotations": widgets,
                                          "ok": not acro and widgets == 0}
    ok_all &= not acro and widgets == 0
    info = run(["pdfinfo", interior])
    report["checks"]["pdfinfo_form"] = re.search(r"Form:\s+(\S+)", info).group(1) if "Form:" in info else "n/a"

    spine_pt, cw, ch = P.cover_geometry(n)
    csz = page_sizes(cover)
    cok = len(csz) == 1 and abs(csz[0][0] - cw) <= 0.5 and abs(csz[0][1] - ch) <= 0.5
    report["checks"]["cover_size"] = {"pages": len(csz), "actual_pt": list(csz[0]) if csz else None,
                                      "expected_pt": [round(cw, 2), round(ch, 2)],
                                      "spine_in": round(spine_pt / PT, 4),
                                      "spread_in": [round(cw / PT, 4), round(ch / PT, 4)],
                                      "spine_text_allowed": spine_pt >= 0.25 * PT, "ok": cok}
    ok_all &= cok

    hits, en, txt = text_checks(interior)
    chits, cen, ctxt = text_checks(cover)
    report["checks"]["copy_interior"] = {"em_dash_or_banned": hits, "en_dashes": en, "ok": not hits}
    report["checks"]["copy_cover"] = {"em_dash_or_banned": chits, "en_dashes": cen, "ok": not chits}
    ok_all &= not hits and not chits
    flat = re.sub(r"\s+", " ", txt)
    etsy_n = len(re.findall(r"ProofNotFluff shop on Etsy", flat))
    report["checks"]["etsy_line"] = {"count_in_interior": etsy_n, "expected": 1, "ok": etsy_n == 1,
                                     "other_etsy_mentions": len(re.findall(r"Etsy", flat)) - etsy_n}
    ok_all &= report["checks"]["etsy_line"]["ok"]
    ask = ("review on Amazon" in flat) or ("Amazon review" in flat)
    report["checks"]["amazon_review_ask"] = {"present": ask, "ok": ask}
    ok_all &= report["checks"]["amazon_review_ask"]["ok"]

    files = render(interior, cover, os.path.join(pack, "render"), pages_150)
    report["renders"] = files
    report["fonts_note"] = P.register_fonts()["note"]
    report["ok"] = bool(ok_all)
    with open(os.path.join(pack, "preflight.json"), "w") as fh:
        json.dump(report, fh, indent=2)
    print(json.dumps({k: v.get("ok") if isinstance(v, dict) else v for k, v in report["checks"].items()},
                     indent=1))
    print("OVERALL", "PASS" if ok_all else "FAIL")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
