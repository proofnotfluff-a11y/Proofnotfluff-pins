#!/usr/bin/env python3
"""Etsy listing video that shows the REAL workbook working: one number changes, the answers update.

Usage: python3 tools/listing_video.py spec.json out.mp4 [--xlsx built.xlsx] [--keep work_dir]
(--xlsx overrides the spec's workbook path: engines keep the spec, the workbook is built fresh.)

Why: the winning spreadsheet listings all carry a demo of the file working (research report
"Etsy success cases and playbook", Oct 6, 2026). This tool films the product itself: each state
is the shipped workbook with a few input cells changed, recalculated and rendered by LibreOffice
(tools/render_xlsx.py), so every number on screen is the file's own output. Changed cells are
found by comparing renders and outlined automatically. Silent, 30 fps, H.264, 3 to 15 seconds.

Spec (paths relative to the spec file):
{
  "xlsx": "Hourly-Rate-Quick-Calculator.xlsx",
  "sheet": "Calculator",                     the tab to film (render file NN-<sheet>.png)
  "crop": [0, 0.049, 1, 0.29],               fractions of the rendered sheet (left, top, right, bottom)
  "dpi": 220,
  "eyebrow": "HOURLY RATE CALCULATOR",
  "size": [1920, 1440],                      video size; 4:3 matches the listing photos
  "states": [
    {"caption": "Your numbers in: {D9} an hour.", "hold": 3.4},
    {"set": {"D15": 75000}, "caption": "Want $75,000? Now {D9}.", "hold": 3.6}
  ]
}
Each state's "set" is applied on top of the shipped file (states do not stack unless you repeat
the earlier values). Captions take {CELL} (formatted with the cell's own number format) or
{Sheet Name!CELL}, read from LibreOffice's recalculated copy, so captions can't drift from the file.
Afterwards: open <out>.frames.png (first and last frame of every state) and check every number.
"""
import json, os, re, shutil, subprocess, sys, tempfile
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import listing_images as li  # noqa: E402

FPS = 30
FADE, PULSE = 0.6, 0.45


def fmt_value(v, nf):
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    nf = (nf or "General").split(";")[0]
    dec = 0
    m = re.search(r"0\.(0+)", nf)
    if m:
        dec = len(m.group(1))
    if "%" in nf:
        return f"{v * 100:,.{dec}f}%"
    s = f"{abs(v):,.{dec}f}"
    if "$" in nf:
        return ("-" if v < 0 else "") + "$" + s
    if nf == "General":
        return f"{v:,}" if isinstance(v, int) or float(v).is_integer() else f"{v:,.2f}"
    return ("-" if v < 0 else "") + s


def caption_text(tpl, wb_vals, wb_fmt, default_sheet):
    def sub(m):
        ref = m.group(1)
        sheet, cell = (ref.rsplit("!", 1) if "!" in ref else (default_sheet, ref))
        sheet = sheet.strip("'")
        v = wb_vals[sheet][cell].value
        if v is None:
            sys.exit(f"caption cell {sheet}!{cell} is empty after recalculation")
        return fmt_value(v, wb_fmt[sheet][cell].number_format)
    return re.sub(r"\{([^{}]+![A-Z]+[0-9]+|[A-Z]+[0-9]+)\}", sub, tpl)


def render_state(src, sets, sheet, dpi, work, i):
    import openpyxl
    wb = openpyxl.load_workbook(src, rich_text=True)
    for ref, val in (sets or {}).items():
        sh, cell = (ref.rsplit("!", 1) if "!" in ref else (sheet, ref))
        wb[sh.strip("'")][cell].value = val
    p = os.path.join(work, f"state{i}.xlsx")
    wb.save(p)
    out = os.path.join(work, f"r{i}")
    r = subprocess.run([sys.executable, os.path.join(HERE, "render_xlsx.py"), p, out, "--dpi", str(dpi)],
                       capture_output=True, text=True)
    if "ERROR VALUES: 0" not in r.stdout:
        sys.exit(f"state {i} renders with errors:\n{r.stdout}\n{r.stderr}")
    key = sheet.replace(" ", "-")
    pngs = [f for f in os.listdir(out) if f.endswith(".png") and f.split("-", 1)[-1][:-4] == key]
    if len(pngs) != 1:
        sys.exit(f"could not find the render of '{sheet}' in {sorted(os.listdir(out))}")
    vals = openpyxl.load_workbook(os.path.join(out, "recalc.xlsx"), data_only=True)
    return os.path.join(out, pngs[0]), vals, wb


def changed_boxes(a, b, pad, gap):
    """Boxes (crop pixels) around every value that differs between two renders, widened to the
    whole number or phrase it sits in (b is the new render)."""
    if a.size != b.size:
        b = b.resize(a.size)
    A = np.asarray(a, dtype=np.int16); B = np.asarray(b, dtype=np.int16)
    d = np.abs(A - B).max(axis=2) > 60
    lab, n = ndimage.label(ndimage.binary_dilation(d, structure=np.ones((pad, pad))))
    boxes = []
    for sl in ndimage.find_objects(lab):
        y0, y1, x0, x1 = sl[0].start, sl[0].stop, sl[1].start, sl[1].stop
        if d[y0:y1, x0:x1].sum() < 25:
            continue
        ys = np.where(d[y0:y1, x0:x1].any(axis=1))[0]
        band = B[y0 + ys[0]:y0 + ys[-1] + 1]
        bg = np.median(band[:, x0:x1].reshape(-1, 3), axis=0)
        inkpx = np.abs(band - bg).max(axis=2) > 60
        frac = inkpx.mean(axis=0)
        ink = (frac > 0) & (frac < 0.85)  # text strokes, not borders, gridlines or filled bars
        xs = np.where(d[y0:y1, x0:x1].any(axis=0))[0]
        l, r = x0 + xs[0], x0 + xs[-1]
        while True:  # grow left and right across the ink run, allowing small gaps
            seg = ink[max(0, l - gap):l]
            if seg.any():
                l = max(0, l - gap) + int(np.where(seg)[0][0])
            else:
                break
        while True:
            seg = ink[r + 1:r + 1 + gap]
            if seg.any():
                r = r + 1 + int(np.where(seg)[0][-1])
            else:
                break
        if y0 + ys[0] <= 2 or y0 + ys[-1] >= B.shape[0] - 3:
            continue  # a row cut by the crop edge
        boxes.append([l, y0 + ys[0], r, y0 + ys[-1]])
    merged = []  # merge boxes that now overlap
    for bx in sorted(boxes):
        if merged and bx[0] <= merged[-1][2] + 4 and not (bx[3] < merged[-1][1] or bx[1] > merged[-1][3]):
            m = merged[-1]; merged[-1] = [min(m[0], bx[0]), min(m[1], bx[1]), max(m[2], bx[2]), max(m[3], bx[3])]
        else:
            merged.append(bx)
    return [tuple(m) for m in merged]


def compose(spec, caption, shot, boxes, glow):
    """One design frame 2000 px tall at the video's shape (4:3 by default, the listing photo
    shape; "size": [2160, 1080] gives 2:1) in the listing photos' style."""
    W, H = spec.get("size", [1920, 1440])
    Wd, Hd, M = round(2000 * W / H), 2000, 150
    im = Image.new("RGBA", (Wd, Hd), li.CANVAS + (255,))
    d = ImageDraw.Draw(im)
    li.bars(d, M, 110)
    d.text((M, 180), spec["eyebrow"], font=li.font("Bold", 46), fill=li.ACCENT)
    y = li.text_block(d, (M, 250), caption, li.font("Bold", 92), li.INK, Wd - 2 * M, 0.98, max_lines=2)
    top, bottom = max(y + 60, 420), Hd - 200
    pad = 26
    x0, x1 = M, Wd - M
    iw = x1 - x0 - 2 * pad
    if shot.height * iw / shot.width > bottom - top - 2 * pad:
        iw = int((bottom - top - 2 * pad) * shot.width / shot.height)
        x0 = (Wd - iw) // 2 - pad; x1 = x0 + iw + 2 * pad
    sc = iw / shot.width
    h = int(shot.height * sc) + 2 * pad
    y0 = top + (bottom - top - h) // 2
    li.shadow_card(im, (x0, y0, x1, y0 + h))
    im.alpha_composite(shot.resize((iw, h - 2 * pad), Image.LANCZOS).convert("RGBA"), (x0 + pad, y0 + pad))
    if boxes and glow > 0:
        layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        a = int(255 * glow)
        for bx0, by0, bx1, by1 in boxes:
            r = (x0 + pad + bx0 * sc - 14, y0 + pad + by0 * sc - 10, x0 + pad + bx1 * sc + 14, y0 + pad + by1 * sc + 10)
            ld.rounded_rectangle(r, radius=12, fill=li.ACCENT + (int(a * 0.12),), outline=li.ACCENT + (a,), width=6)
        im.alpha_composite(layer)
    d = ImageDraw.Draw(im)
    d.text((M, Hd - 130), "ProofNotFluff", font=li.font("Bold", 50), fill=li.INK)
    ft = spec.get("formats", "Excel, Google Sheets, LibreOffice  |  Instant download")
    f = li.font("Regular", 40)
    d.text((Wd - M - d.textlength(ft, font=f), Hd - 122), ft, font=f, fill=li.MUTED)
    return im.convert("RGB")


def main():
    args = sys.argv[1:]
    keep = xlsx_arg = None
    if "--xlsx" in args:
        i = args.index("--xlsx"); xlsx_arg = os.path.abspath(args[i + 1]); del args[i:i + 2]
    if "--keep" in args:
        i = args.index("--keep"); keep = args[i + 1]; del args[i:i + 2]
    if len(args) != 2:
        sys.exit(__doc__)
    spec_path, out = args
    spec = json.load(open(spec_path))
    base = os.path.dirname(os.path.abspath(spec_path))
    src = xlsx_arg or (spec["xlsx"] if os.path.isabs(spec["xlsx"]) else os.path.join(base, spec["xlsx"]))
    W, H = spec.get("size", [1920, 1440])
    work = keep or tempfile.mkdtemp(prefix="lv_")
    os.makedirs(work, exist_ok=True)
    dpi = spec.get("dpi", 220)

    states = []
    for i, st in enumerate(spec["states"]):
        png, vals, wb = render_state(src, st.get("set"), spec["sheet"], dpi, work, i)
        shot = li.load_crop(os.path.dirname(png), os.path.basename(png), spec["crop"])
        cap = caption_text(st["caption"], vals, wb, spec["sheet"])
        states.append({"shot": shot, "caption": cap, "hold": float(st.get("hold", 3.4))})
        print(f"state {i}: {cap}")
    for i in range(1, len(states)):
        states[i]["boxes"] = changed_boxes(states[i - 1]["shot"], states[i]["shot"], pad=max(8, dpi // 14), gap=max(10, dpi // 12))
        print(f"state {i}: {len(states[i]['boxes'])} changed areas outlined")
        if not states[i]["boxes"]:
            sys.exit(f"state {i} looks identical to state {i - 1}; change an input that moves an answer")

    total = states[0]["hold"] + sum(FADE + s["hold"] for s in states[1:])
    if not 3 <= total <= 15:
        sys.exit(f"video would be {total:.1f} s; Etsy takes 3 to 15 s")

    def frame(st, glow):
        return compose(spec, st["caption"], st["shot"], st.get("boxes"), glow).resize((W, H), Image.LANCZOS)

    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264",
                           "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow", "-movflags", "+faststart", out],
                          stdin=subprocess.PIPE)
    keyframes, n = [], 0

    def emit(img, count):
        nonlocal n
        b = img.tobytes()
        for _ in range(count):
            ff.stdin.write(b); n += 1

    plain = frame(states[0], 0)
    emit(plain, round(states[0]["hold"] * FPS)); keyframes.append(plain)
    prev = plain
    for st in states[1:]:
        nxt_plain = frame(st, 0)
        k = round(FADE * FPS)
        for f in range(1, k + 1):
            emit(Image.blend(prev, nxt_plain, f / k), 1)
        full = frame(st, 1.0)
        p = round(PULSE * FPS)
        for f in range(1, p + 1):
            emit(Image.blend(nxt_plain, full, f / p), 1)
        emit(full, max(1, round(st["hold"] * FPS) - p))
        keyframes += [full]
        prev = full
    ff.stdin.close()
    if ff.wait() != 0:
        sys.exit("ffmpeg failed")

    sheet = Image.new("RGB", (W // 2 * min(3, len(keyframes)) + 20 * (min(3, len(keyframes)) - 1),
                              (H // 2 + 20) * ((len(keyframes) + 2) // 3) - 20), "white")
    for i, kf in enumerate(keyframes):
        sheet.paste(kf.resize((W // 2, H // 2)), ((i % 3) * (W // 2 + 20), (i // 3) * (H // 2 + 20)))
    sheet.save(out + ".frames.png")
    mb = os.path.getsize(out) / 1e6
    print(json.dumps({"out": out, "seconds": round(n / FPS, 2), "frames": n, "size": [W, H], "mb": round(mb, 2),
                      "frames_sheet": out + ".frames.png"}))
    if mb > 100:
        sys.exit("over Etsy's 100 MB limit")
    if not keep:
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
