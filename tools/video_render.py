#!/usr/bin/env python3
"""Rat check renderer: spec + narration timings -> props (every box from tools/video_layout.py) -> the layout check ->
Remotion paints the frames -> ffmpeg lays the voice clips and the music bed under them at -14 LUFS -> render manifest,
contact sheet and critic frames. Spec: the blueprint's "Media and voice" pins (Remotion only, 1080 x 1920, 30 fps, H.264,
AAC, 45 to 60 s, under 100 MB, one music bed mastered to -14 LUFS, clips used exactly as returned).

Usage
  video_render.py props SPEC WORDS.json --out PROPS.json           build the props and run the layout check
  video_render.py render SPEC WORDS.json --out DIR [--browser PATH] the full render into DIR (video.mp4, manifest.json,
                                                                   props.json, sheet.jpg)
  video_render.py frames MP4 --out DIR [--fps 5]                   frames for the render critic
  video_render.py --selftest                                       the composer on the fixture spec, no render
Exit 1 when the layout check fails, the length leaves 45 to 60 s, or any step fails: nothing is retried blind.
"""
import argparse, datetime as dt, difflib, hashlib, json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import video_layout as L  # noqa: E402
import video_voice  # noqa: E402

TEMPLATE = os.path.join(ROOT, "video", "templates", "rat-check")
T = L.T
X0, XW = L.LEFT, L.RIGHT - L.LEFT          # 72, 858
CB = 1010                                   # content bottom; captions live below it
CAP_Y, CAP_H = 1040, 196
GAP, SCENE_GAP, CTA_GAP, START = 0.32, 0.25, 0.5, 0.10
DRIFT = 4


class RenderError(Exception):
    pass


def cfg():
    return json.load(open(os.path.join(ROOT, "video", "config.json"), encoding="utf-8"))


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------------
# Timeline

def timeline(spec, words):
    segs = {s["key"]: s for s in words["segments"]}
    order = video_voice.segments(spec)
    t, out, prev_scene = START, [], None
    for i, s in enumerate(order):
        if s["key"] not in segs:
            raise RenderError(f"no narration for line {s['key']}")
        v = segs[s["key"]]
        if i:
            t += GAP + (SCENE_GAP if s["scene"] != prev_scene else 0) + (CTA_GAP if s["key"] == "cta" else 0)
        out.append({"key": s["key"], "scene": s["scene"], "start": round(t, 3), "end": round(t + v["seconds"], 3),
                    "say": s["say"], "tts": s["tts"], "words": [dict(w, start=round(t + w["start"], 3), end=round(t + w["end"], 3)) for w in v["words"]],
                    "file": v["file"]})
        t += v["seconds"]
        prev_scene = s["scene"]
    c = cfg()["video"]
    cta = out[-1]
    end_start = max(0.0, cta["start"] - 0.35)
    total = max(c["minSeconds"] + 0.5, cta["end"] + 1.6, end_start + c["endCardMinSeconds"])
    total = round(int(total * 30 + 0.999) / 30, 3)
    if total > c["maxSeconds"]:
        raise RenderError(f"the narration runs {cta['end']:.1f} s, so the cut would be {total:.1f} s (at most {c['maxSeconds']}): shorten the script")
    scenes, cur = [], None
    for seg in out:
        if seg["scene"] != cur:
            if scenes:
                scenes[-1]["end"] = round(seg["start"] - (0.35 if seg["scene"] == "end" else 0.15), 3)
            scenes.append({"scene": seg["scene"], "start": 0.0 if not scenes else round(seg["start"] - (0.35 if seg["scene"] == "end" else 0.15), 3)})
            cur = seg["scene"]
    scenes[-1]["end"] = total
    return {"segments": out, "scenes": scenes, "seconds": total}


# ---------------------------------------------------------------------------------------------------------------------
# Scenes

def brand_bars(prefix, t0, t1, y=286):
    return [L.rect(f"{prefix}-bar{i}", X0 + i * 68, y, 56, 10, T["bars"][i], radius=3, t_in=t0, t_out=t1, role="decor") for i in range(5)]


def eyebrow(prefix, text, t0, t1, color):
    return L.text_el(f"{prefix}-eyebrow", text, X0, 316, XW, "P", 700, 42, color, lh=1.15, tracking=0.06, upper=True, max_lines=2,
                     t_in=t0, t_out=t1, anim="none")


def bg(prefix, color, t0, t1):
    return L.rect(f"{prefix}-bg", 0, 0, L.W, L.H, color, t_in=t0, t_out=t1, role="background")


def hook_scene(spec, sc):
    s, t0, t1 = spec["screen"], sc["start"], sc["end"]
    els = [bg("hook", T["ink"], t0, t1)] + brand_bars("hook", t0, t1)
    e = eyebrow("hook", s.get("eyebrow", "CHICAGO RAT CHECK"), t0, t1, T["accentInk"])
    els.append(e)
    y = e["y"] + e["h"] + 28
    area = L.text_el("hook-area", s["area"], X0, y, XW, "P", 700, 72, T["white"], lh=1.05, max_lines=2, t_in=t0, t_out=t1, anim="none")
    els.append(area)
    y = area["y"] + area["h"] + 24
    h = s["headline"]
    number = h["number"] + (f" {h['unit']}" if h.get("unit") else "")
    num = L.text_el("hook-number", number, X0, y, XW, "P", 700, 300, T["white"], lh=1.0, max_lines=1, shrink_to=150, t_in=t0, t_out=t1, anim="none")
    els.append(num)
    y = num["y"] + num["h"] + 28
    lab = L.text_el("hook-label", h["label"], X0, y, XW, "P", 600, 48, T["white"], lh=1.15, max_lines=3, t_in=t0, t_out=t1, anim="none")
    els.append(lab)
    y = lab["y"] + lab["h"] + 26
    per = L.text_el("hook-period", f"City 311 data, {s['period']}", X0, y, XW, "I", 600, 42, T["soft"], lh=1.15, max_lines=1, t_in=t0, t_out=t1, anim="none")
    els.append(per)
    over = per["y"] + per["h"] - CB
    if over > 0:   # take the space back from the big number, never from the words
        num2 = L.text_el("hook-number", number, X0, num["y"], XW, "P", 700, max(150, num["size"] - over - 4), T["white"], lh=1.0, max_lines=1, shrink_to=150, t_in=t0, t_out=t1, anim="none")
        d = num["h"] - num2["h"]
        els[els.index(num)] = num2
        for x in (lab, per):
            x["y"] -= d
    return els


def scene_head(prefix, spec, sc, title_key, title_lines=2):
    s = spec["screen"]
    t0, t1 = sc["start"], sc["end"]
    els = [bg(prefix, T["canvas"], t0, t1)] + brand_bars(prefix, t0, t1)
    e = eyebrow(prefix, s.get("eyebrow", "CHICAGO RAT CHECK"), t0, t1, T["accent"])
    els.append(e)
    title = ((s.get("scenes") or {}).get(title_key) or {}).get("title", "") if title_key else ""
    y = e["y"] + e["h"] + 24
    if title:
        tl = L.text_el(f"{prefix}-title", title, X0, y, XW, "P", 700, 56, T["ink"], lh=1.08, max_lines=title_lines, shrink_to=46, t_in=t0, t_out=t1, anim="rise")
        els.append(tl)
        y = tl["y"] + tl["h"]
    return els, y + 36


def picture_scene(spec, sc):
    s, t0, t1 = spec["screen"], sc["start"], sc["end"]
    is_map = spec["screen"]["chart"]["kind"] == "map"
    els, top = scene_head("pic", spec, sc, "picture", 1 if is_map else 2)
    ch = s["chart"]
    bottom = CB
    if is_map:
        els += map_picture(spec, ch, t0, t1, top, bottom, sc.get("segments", []))
    elif ch["kind"] == "bars":
        els += bars_picture(ch, t0, t1, top, bottom, "pic")
    elif ch["kind"] == "line":
        els += line_picture(ch, t0, t1, top, bottom)
    return els


def map_picture(spec, ch, t0, t1, top, bottom, segs):
    """The map at full height on the left; on the right one stat block at a time, following the narration: each line's
    first number in screen.chart.stats is the block on screen while that line is said. The focus area is the only
    accent on the map, and a leader line ties it to its name."""
    s = spec["screen"]
    paths, cent, used = L.map_paths((X0, top, 400, bottom - top))
    fill = {"hi": T["ink"], "lo": T["white"], "focus": T["accent"]}
    areas = [{"n": a["n"], "d": paths[a["n"]], "fill": fill[a["cls"]], "focus": a["cls"] == "focus"} for a in ch["areas"]]
    m = {"id": "pic-map", "kind": "map", "role": "map", "x": round(used[0], 1), "y": round(used[1], 1), "w": round(used[2], 1), "h": round(used[3], 1),
         "areas": areas, "stroke": T["ink2"], "strokeWidth": 2.5, "focusColor": T["accent"], "focusStroke": T["ink"], "tIn": t0 + 0.25, "tOut": t1,
         "focusIn": t0 + 0.9, "restColor": T["ink"], "anim": "fade", "group": None}
    els = [m]
    cx = round(used[0] + used[2] + 36, 1)
    cw = L.RIGHT - cx
    stats = ch.get("stats") or {}
    blocks = []
    for g in segs:
        sid = next((i for i in g.get("show", []) if i in stats), None)
        if sid and (not blocks or blocks[-1][1] != sid):
            blocks.append((g["start"] - 0.1, sid))
    if not blocks and stats:
        blocks = [(t0, next(iter(stats)))]
    legs = []
    for i, (cls, text) in enumerate(ch["legend"]):
        legs.append((cls, L.text_el(f"pic-leg{i}", text, cx + 52, 0, cw - 52, "I", 600, 48, T["ink2"], lh=1.15, max_lines=2, t_in=t0 + 0.6, t_out=t1)))
    leg_h = sum(e["h"] + 20 for _, e in legs) - 20
    leg_top = bottom - leg_h
    m["focusSpans"] = [[round(t0 if k == 0 else st_, 3), round(blocks[k + 1][0] if k + 1 < len(blocks) else t1, 3)]
                       for k, (st_, sid) in enumerate(blocks) if stats[sid].get("who") == "area"] or [[t0, t1]]
    for k, (start, sid) in enumerate(blocks):
        st = stats[sid]
        b0 = t0 if k == 0 else start
        b1 = blocks[k + 1][0] if k + 1 < len(blocks) else t1
        y = top + 8
        mine = st.get("who") == "area"
        nm = L.text_el(f"pic-stat{k}-name", st["name"], cx, y, cw, "P", 600, 42, T["muted"], lh=1.12, upper=True, tracking=0.04, max_lines=2, t_in=b0, t_out=b1)
        y = nm["y"] + nm["h"] + 6
        bg_ = L.text_el(f"pic-stat{k}-big", st["big"], cx, y, cw, "P", 700, 96, T["accent"] if mine else T["ink"], lh=1.0, max_lines=1, shrink_to=56, t_in=b0, t_out=b1)
        y = bg_["y"] + bg_["h"] + 12
        lb = L.text_el(f"pic-stat{k}-label", st["label"], cx, y, cw, "I", 600, 48, T["ink2"], lh=1.15, max_lines=4, t_in=b0, t_out=b1)
        y = lb["y"] + lb["h"] + 18
        els += [nm, bg_, lb]
        if st.get("part"):
            a, b = st["part"]
            els.append(L.rect(f"pic-stat{k}-track", cx, y, cw, 16, T["line"], radius=8, t_in=b0, t_out=b1, role="decor"))
            els.append(L.rect(f"pic-stat{k}-fill", cx, y, round(cw * a / b, 1), 16, T["ink"], radius=8, t_in=b0, t_out=b1, anim="grow", role="decor"))
        if mine and ch.get("focus") in cent:
            fx, fy = cent[ch["focus"]]
            els.append({"id": f"pic-stat{k}-leader", "kind": "leader", "role": "decor", "x": round(min(fx, cx), 1), "y": round(min(fy, nm["y"] + 26), 1),
                        "w": round(abs(cx - 10 - fx), 1), "h": round(abs(nm["y"] + 26 - fy), 1) or 1,
                        "points": [[round(fx, 1), round(fy, 1)], [round(cx - 10, 1), round(nm["y"] + 26, 1)]], "color": T["accent"], "width": 4,
                        "tIn": max(b0, t0 + 0.9), "tOut": b1, "anim": "fade", "group": None})
    yy = leg_top
    for i, (cls, e) in enumerate(legs):
        e["y"] = yy
        els.append(L.rect(f"pic-leg{i}-swatch", cx, yy + 5, 40, 40, fill[cls], radius=6, t_in=t0 + 0.6, t_out=t1, anim="fade", line=T["ink2"] if cls == "lo" else None))
        els.append(e)
        yy += e["h"] + 20
    return els


def bars_picture(ch, t0, t1, top, bottom, prefix):
    rows = ch["rows"]
    n = len(rows)
    pitch = min(128, (bottom - top) / max(1, n))
    vmax = max(abs(r["value"]) for r in rows) or 1
    bar_max = 600
    els = []
    for i, r in enumerate(rows):
        y = top + i * pitch
        ti = t0 + 0.3 + 0.12 * i
        lab = L.text_el(f"{prefix}-row{i}-label", r["label"], X0, y, XW, "I", 600, 44, T["ink"], lh=1.12, max_lines=1, shrink_to=42, t_in=ti, t_out=t1, group="pic")
        bw = max(8, round(bar_max * abs(r["value"]) / vmax))
        bar = L.rect(f"{prefix}-row{i}-bar", X0, y + 58, bw, 40, T["accent"] if r.get("focus") else T["ink"], radius=6, t_in=ti, t_out=t1, anim="grow", group="pic")
        val = L.text_el(f"{prefix}-row{i}-value", r["shown"] + (f" {ch['unit']}" if ch.get("unit") in ("days",) else ""), X0 + bw + 16, y + 52,
                        L.RIGHT - (X0 + bw + 16), "P", 700, 48, T["accent"] if r.get("focus") else T["ink"], lh=1.0, max_lines=1, shrink_to=42,
                        t_in=ti + 0.5, t_out=t1, group="pic")
        els += [lab, bar, val]
    return els


def line_picture(ch, t0, t1, top, bottom):
    els = []
    lab = L.text_el("pic-line-label", "Rat complaints per week", X0, top, XW, "I", 600, 42, T["ink2"], lh=1.15, max_lines=1, t_in=t0 + 0.2, t_out=t1)
    els.append(lab)
    ctop = lab["y"] + lab["h"] + 76
    cbot = bottom - 72
    x1, x2 = X0 + 20, L.RIGHT - 20
    ys = [p["y"] for p in ch["points"]]
    vmax = max(ys) * 1.08 or 1
    pts = []
    for i, v in enumerate(ys):
        x = x1 + (x2 - x1) * i / (len(ys) - 1)
        y = cbot - (cbot - ctop) * v / vmax
        pts.append([round(x, 1), round(y, 1)])
    hl = ch.get("highlightLast") or 0
    dots = [pts[0] + [T["ink"]], pts[-1] + [T["accent"]]]
    els.append({"id": "pic-line", "kind": "line", "role": "map", "x": X0, "y": ctop - 70, "w": XW, "h": cbot - ctop + 70 + 12,
                "points": pts, "color": T["ink"], "highlight": T["accent"], "highlightFrom": len(pts) - hl if hl else -1, "dots": dots,
                "tIn": t0 + 0.3, "tOut": t1, "anim": "draw", "group": "pic"})
    fv = L.text_el("pic-line-first", ch["firstShown"], max(X0, pts[0][0] - 20), pts[0][1] - 66, 300, "P", 700, 48, T["ink"], lh=1.0, max_lines=1,
                   t_in=t0 + 1.4, t_out=t1, group="pic")
    lvw = L.text_width(ch["lastShown"], "P", 700, 48)
    lv = L.text_el("pic-line-last", ch["lastShown"], L.RIGHT - lvw, pts[-1][1] - 66, lvw + 0.5, "P", 700, 48, T["accent"], lh=1.0, max_lines=1,
                   t_in=t0 + 1.5, t_out=t1, group="pic")
    els += [fv, lv]
    d1 = L.text_el("pic-line-from", ch["fromShown"], X0, cbot + 22, 400, "I", 600, 42, T["ink2"], lh=1.15, max_lines=1, t_in=t0 + 0.3, t_out=t1)
    d2w = L.text_width(ch["toShown"], "I", 600, 42)
    d2 = L.text_el("pic-line-to", ch["toShown"], L.RIGHT - d2w, cbot + 22, d2w + 0.5, "I", 600, 42, T["ink2"], lh=1.15, max_lines=1, t_in=t0 + 0.3, t_out=t1)
    els += [d1, d2]
    return els


def compare_scene(spec, sc):
    s, t0, t1 = spec["screen"], sc["start"], sc["end"]
    els, top = scene_head("cmp", spec, sc, "compare")
    cards = s["compare"]["cards"]
    gap = 24
    cw = (XW - gap) / 2
    chh = min(440, CB - top)
    vmax = max(c["value"] for c in cards) or 1
    for i, c in enumerate(cards):
        x = X0 + i * (cw + gap)
        ti = t0 + 0.3 + 0.25 * i
        els.append(L.rect(f"cmp-card{i}", round(x, 1), top, round(cw, 1), chh, T["card"], radius=24, t_in=ti, t_out=t1, anim="fade", role="container", line=T["line"]))
        lb = L.text_el(f"cmp-card{i}-label", c["label"], x + 28, top + 28, cw - 56, "P", 600, 42, T["muted"], lh=1.12, upper=True, tracking=0.04,
                       max_lines=3, t_in=ti, t_out=t1)
        els.append(lb)
        vy = lb["y"] + lb["h"] + 18
        vv = L.text_el(f"cmp-card{i}-value", c["shown"], x + 28, vy, cw - 56, "P", 700, 120, T["accent"] if c.get("focus") else T["ink"],
                       lh=1.0, max_lines=1, shrink_to=64, t_in=ti + 0.1, t_out=t1)
        els.append(vv)
        if s["compare"].get("unit"):
            un = L.text_el(f"cmp-card{i}-unit", s["compare"]["unit"], x + 28, vv["y"] + vv["h"] + 6, cw - 56, "I", 600, 42, T["ink2"], lh=1.15,
                           max_lines=1, t_in=ti + 0.1, t_out=t1)
            els.append(un)
        bw = max(8, round((cw - 56) * c["value"] / vmax))
        els.append(L.rect(f"cmp-card{i}-bar", round(x + 28, 1), top + chh - 28 - 24, bw, 24, T["accent"] if c.get("focus") else T["ink"], radius=4,
                          t_in=ti + 0.2, t_out=t1, anim="grow"))
    return els


def why_scene(spec, sc):
    s, t0, t1 = spec["screen"], sc["start"], sc["end"]
    els = [bg("why", T["canvas"], t0, t1)] + brand_bars("why", t0, t1)
    e = eyebrow("why", s.get("eyebrow", "CHICAGO RAT CHECK"), t0, t1, T["accent"])
    els.append(e)
    w = (s.get("scenes") or {}).get("why") or {}
    y = e["y"] + e["h"] + 40
    tl = L.text_el("why-title", w.get("title", ""), X0, y, XW, "P", 700, 72, T["ink"], lh=1.08, max_lines=4, shrink_to=56, t_in=t0, t_out=t1, anim="rise")
    els.append(tl)
    y = tl["y"] + tl["h"] + 48
    rows = w.get("bars") or (s.get("whyBars") if w.get("number") else None)
    if rows:
        pitch = 48 + 12 + 96 + 32
        card_h = min(CB - y, 56 + pitch * len(rows))
        els.append(L.rect("why-card", X0, y, XW, card_h, T["card"], radius=24, t_in=t0 + 0.4, t_out=t1, anim="fade", role="container", line=T["line"]))
        vmax = max(abs(r["value"]) for r in rows) or 1
        inner_x, inner_w = X0 + 36, XW - 72
        col = max(L.text_width(r["shown"], "P", 700, 64) for r in rows) + 28   # the value column never meets a bar
        yy = y + 32
        for i, r in enumerate(rows):
            ti = t0 + 0.5 + 0.2 * i
            lab = L.text_el(f"why-row{i}-label", r["label"], inner_x, yy, inner_w, "P", 600, 42, T["muted"], lh=1.12, upper=True, tracking=0.04, max_lines=1, t_in=ti, t_out=t1)
            bw = max(12, round((inner_w - col - 16) * abs(r["value"]) / vmax))
            bar = L.rect(f"why-row{i}-bar", inner_x, yy + 60, bw, 96, T["accent"] if r.get("focus") else T["ink"], radius=8, t_in=ti, t_out=t1, anim="grow")
            vw = L.text_width(r["shown"], "P", 700, 64)
            val = L.text_el(f"why-row{i}-value", r["shown"], inner_x + bw + 16, yy + 76, vw + 0.5, "P", 700, 64,
                            T["accent"] if r.get("focus") else T["ink2"], lh=1.0, max_lines=1, t_in=ti + 0.4, t_out=t1)
            els += [lab, bar, val]
            yy += pitch
    elif w.get("number"):
        card_h = CB - y
        if card_h >= 220:
            els.append(L.rect("why-card", X0, y, XW, min(card_h, 330), T["card"], radius=24, t_in=t0 + 0.4, t_out=t1, anim="fade", role="container", line=T["line"]))
            nv = L.text_el("why-number", w["number"], X0 + 36, y + 32, XW - 72, "P", 700, 150, T["ink"], lh=1.0, max_lines=1, shrink_to=80, t_in=t0 + 0.5, t_out=t1)
            els.append(nv)
            nl = L.text_el("why-number-label", w.get("numberLabel", ""), X0 + 36, nv["y"] + nv["h"] + 14, XW - 72, "I", 600, 44, T["ink2"], lh=1.15,
                           max_lines=2, t_in=t0 + 0.5, t_out=t1)
            els.append(nl)
    return els


def end_scene(spec, sc):
    t0, t1 = sc["start"], sc["end"]
    ec = spec["endCard"]
    els = [bg("end", T["ink"], t0, t1)] + brand_bars("end", t0, t1)
    e = eyebrow("end", spec["screen"].get("eyebrow", "CHICAGO RAT CHECK"), t0, t1, T["accentInk"])
    els.append(e)
    a = L.text_el("end-line", ec["line"], X0, e["y"] + e["h"] + 40, XW, "P", 700, 88, T["white"], lh=1.05, max_lines=2, t_in=t0, t_out=t1, anim="rise")
    els.append(a)
    p = L.text_el("end-path", ec["path"], X0, a["y"] + a["h"] + 36, XW, "P", 700, 76, T["accentInk"], lh=1.1, max_lines=1, shrink_to=48, t_in=t0 + 0.2, t_out=t1, anim="rise")
    els.append(p)
    sub = L.text_el("end-sub", ec.get("sub", "The free Chicago Rat Index, updated every Monday."), X0, p["y"] + p["h"] + 40, XW, "I", 400, 46, T["soft"],
                    lh=1.25, max_lines=3, t_in=t0 + 0.4, t_out=t1)
    els.append(sub)
    h = spec["screen"]["headline"]
    cy = sub["y"] + sub["h"] + 64
    who = L.text_el("end-recap-area", spec["screen"]["area"], X0, cy, XW, "P", 600, 42, T["soft"], lh=1.12, upper=True, tracking=0.04,
                    max_lines=1, t_in=t0 + 0.5, t_out=t1)
    big = L.text_el("end-recap-number", h["number"] + (f" {h['unit']}" if h.get("unit") else ""), X0, who["y"] + who["h"] + 8, XW, "P", 700, 96,
                    T["white"], lh=1.0, max_lines=1, shrink_to=60, t_in=t0 + 0.5, t_out=t1)
    els += [who, big]
    els.append(L.text_el("end-brand", "ProofNotFluff", X0, big["y"] + big["h"] + 64, XW, "P", 700, 48, T["white"], lh=1.15, max_lines=1, t_in=t0 + 0.4, t_out=t1))
    return els


SCENES = {"hook": hook_scene, "picture": picture_scene, "compare": compare_scene, "why": why_scene, "end": end_scene}


# ---------------------------------------------------------------------------------------------------------------------
# Captions: the "say" text (what the screen shows), timed by the heard words (what ElevenLabs read).

def norm(w):
    return re.sub(r"[^a-z0-9%]", "", w.lower())


def align(say_words, heard):
    """Time every caption word from the heard words: the same words match one to one; a caption number ("221.4%")
    takes the span of the heard words that say it ("two hundred twenty-one point four percent")."""
    a = [norm(w) for w in say_words]
    b = [norm(w["w"]) for w in heard]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out = [None] * len(say_words)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k] = (heard[j1 + k]["start"], heard[j1 + k]["end"])
        elif i2 > i1:
            if j2 > j1:
                s, e = heard[j1]["start"], heard[j2 - 1]["end"]
            else:
                s = heard[j1 - 1]["end"] if j1 else (heard[0]["start"] if heard else 0)
                e = s
            span = (e - s) / (i2 - i1) if i2 > i1 else 0
            for k in range(i2 - i1):
                out[i1 + k] = (round(s + span * k, 3), round(s + span * (k + 1), 3))
    return out


GLUE = {"a", "an", "the", "of", "to", "in", "on", "at", "for", "and", "or", "but", "is", "are", "was", "were", "be", "by", "with",
        "from", "that", "this", "its", "it's", "if", "as", "than", "just", "up", "one", "more", "less", "fewer", "about", "over", "under",
        "nearly", "almost", "only"}


CAP_GAP = 0   # normal word spacing; the highlight pill pads behind the word (design read 4)

BREAK_BEFORE = {"are", "is", "was", "were", "in", "on", "to", "and", "but", "if"}


def phrase_breaks(words, chunks, fits=None):
    """Move a chunk's tail into the next chunk when it ends on a word that waits for the next one ('are', 'the', 'of'),
    or splits a two-word name ('South | Chicago'), so captions break at phrase ends."""
    out = [list(c) for c in chunks]
    for i in range(len(out) - 1):
        while (len(out[i + 1]) < 3 and len(out[i]) > 3 and not re.search(r"[.!?]$", words[out[i][-1]])
               and (fits is None or fits(" ".join(words[j] for j in [out[i][-1]] + out[i + 1])))):
            out[i + 1].insert(0, out[i].pop())   # no one- or two-word tail card
        for _ in range(3):
            if len(out[i]) <= 2:
                break
            last, nxt = words[out[i][-1]], words[out[i + 1][0]]
            glue = last.lower().strip(",.") in GLUE and not re.search(r"[,.!?]$", last)
            name = last[:1].isupper() and nxt[:1].isupper() and not re.search(r"[,.!?]$", last)
            count = bool(re.search(r"\d", last)) and not re.search(r"[,.!?%]$", last) and nxt[:1].islower()   # "45 | rat complaints"
            if not (glue or name or count):
                break
            out[i + 1].insert(0, out[i].pop())
        if len(out[i + 1]) <= 4 and not re.search(r"[.!?]$", words[out[i][-1]]):
            # a short tail card joins the clause it belongs to: break after the last comma, else before the last
            # 'are'/'is'/'in'... in the chunk, when the moved words and the tail still fit the caption's two lines
            cand = [k + 1 for k, wi in enumerate(out[i][:-1]) if re.search(r",$", words[wi])] or \
                   [k for k, wi in enumerate(out[i]) if k >= 3 and words[wi].lower() in BREAK_BEFORE]
            if cand:
                k = cand[-1]
                tail = out[i][k:] + out[i + 1]
                if fits is None or fits(" ".join(words[j] for j in tail)):
                    out[i + 1] = tail
                    out[i] = out[i][:k]
    return [c for c in out if c]


def captions(tl):
    out = []
    font, weight, size, lh = "I", 600, 52, 1.25
    inner = XW - 48 - 6 * CAP_GAP   # wrap width leaves the extra word gaps room on a line
    for seg in tl["segments"]:
        if seg["scene"] == "end":
            continue
        words = seg["say"].split()
        times = align(words, seg["words"])
        chunks, cur = [], []
        for i, w in enumerate(words):
            trial = cur + [i]
            text = " ".join(words[j] for j in trial)
            ok = L.wrap(text, font, weight, size, inner, 0, 2)
            if ok is None and cur:
                chunks.append(cur)
                cur = [i]
            else:
                cur = trial
            if re.search(r"[.!?]$", w) and len(cur) >= 3 and i < len(words) - 1:
                chunks.append(cur)
                cur = []
        if cur:
            chunks.append(cur)
        chunks = phrase_breaks(words, chunks, lambda t: L.wrap(t, font, weight, size, inner, 0, 2) is not None)
        merged = []   # no fragment cards: a chunk under 4 words joins its neighbor when the two fit in 2 lines
        for ch in chunks:
            if merged and (len(ch) < 4 or len(merged[-1]) < 4) and L.wrap(" ".join(words[j] for j in merged[-1] + ch), font, weight, size, inner, 0, 2):
                merged[-1] = merged[-1] + ch
            else:
                merged.append(ch)
        chunks = merged
        on_ink = seg["scene"] == "hook"
        colors = ({"color": T["white"], "dim": T["soft"], "pill": T["white"], "pillText": T["ink"]} if on_ink else
                  {"color": T["ink"], "dim": T["ink2"], "pill": T["ink"], "pillText": T["white"]})   # accent stays the data's
        for ci, ch in enumerate(chunks):
            text = " ".join(words[j] for j in ch)
            lines = L.wrap(text, font, weight, size, inner, 0, 2) or [text]
            t_in = times[ch[0]][0]
            t_out = times[chunks[ci + 1][0]][0] if ci + 1 < len(chunks) else seg["end"] + GAP * 0.9
            k, lw = 0, []
            for line in lines:
                n = len(line.split())
                row = []
                for m in range(n):
                    before = " ".join(words[ch[k + j]] for j in range(m))
                    x = L.text_width(before + (" " if before else ""), font, weight, size) + CAP_GAP * m   # room for the pill
                    j = ch[k + m]
                    nxt = times[j + 1][0] if j + 1 < len(words) else seg["end"]
                    row.append({"text": words[j], "tIn": times[j][0], "tOut": round(max(times[j][1], nxt), 3), "x": round(x, 1),
                                "w": round(L.text_width(words[j], font, weight, size), 1)})
                lw.append(row)
                k += n
            wpx = max(L.text_width(l, font, weight, size) + CAP_GAP * (len(l.split()) - 1) for l in lines)
            out.append({"id": f"cap-{seg['key']}-{ci}", "kind": "caption", "role": "text", "text": text, "lines": lines, "lineWords": lw,
                        "x": X0, "y": CAP_Y + 24 + (145 - len(lines) * size * lh) / 2, "w": round(wpx, 1), "h": round(len(lines) * size * lh),
                        "slotW": inner, "font": font, "weight": weight, "size": size, "lh": lh, **colors,
                        "tIn": round(t_in, 3), "tOut": round(t_out, 3), "group": None, "seg": seg["key"]})
    return out


def caption_cards(caps, tl):
    """One white card behind the captions for each spoken scene, shown from that scene's first caption (never an empty
    card on frame one), and none on the end card, whose own words carry the close."""
    out = []
    for sc in tl["scenes"]:
        if sc["scene"] in ("end", "hook"):   # on the ink frames the captions sit straight on the ground
            continue
        mine = [c for c in caps if sc["start"] <= c["tIn"] < sc["end"]]
        if not mine:
            continue
        out.append(L.rect(f"capcard-{sc['scene']}", X0, CAP_Y, XW, CAP_H, T["card"], radius=24, t_in=min(c["tIn"] for c in mine),
                          t_out=sc["end"], role="container", line=T["line"] if sc["scene"] != "hook" else None))
    return out


def build_props(spec, words):
    tl = timeline(spec, words)
    els = []
    show = {l.get("id"): l.get("show", []) for l in spec.get("lines", [])}
    for sc in tl["scenes"]:
        sc["segments"] = [dict(g, show=show.get(g["key"], [])) for g in tl["segments"] if g["scene"] == sc["scene"]]
        fn = SCENES.get(sc["scene"])
        if not fn:
            raise RenderError(f"unknown scene {sc['scene']}")
        els += fn(spec, sc)
    caps = captions(tl)
    seg_scene = {g["key"]: g["scene"] for g in tl["segments"]}
    caps.sort(key=lambda c: c["tIn"])
    for i, c in enumerate(caps):   # a caption holds until the next one in its scene, so the card is never empty
        sc = next(x for x in tl["scenes"] if x["start"] <= c["tIn"] < x["end"])
        nxt = caps[i + 1] if i + 1 < len(caps) else None
        c["tOut"] = round(nxt["tIn"] if nxt and seg_scene[nxt["seg"]] == seg_scene[c["seg"]] else sc["end"], 3)
    if caps and seg_scene[caps[0]["seg"]] == "hook":
        caps[0]["tIn"] = 0.0   # frame one carries the first caption too, its words dim until they are said
    # captions sit straight on the frame at x 72 in every scene (design read 4): no card
    c = cfg()["video"]
    end_start = next(s["start"] for s in tl["scenes"] if s["scene"] == "end")
    props = {"schema": "pnf.video.props.v1", "videoId": spec["videoId"], "fps": c["fps"], "width": c["width"], "height": c["height"],
             "seconds": tl["seconds"], "background": T["canvas"], "drift": DRIFT, "elements": els, "captions": caps,
             "progress": None,
             "timeline": {"segments": [{k: s[k] for k in ("key", "scene", "start", "end", "file")} for s in tl["segments"]],
                          "scenes": [{k: v for k, v in x.items() if k != "segments"} for x in tl["scenes"]], "hookEnds": tl["segments"][0]["end"] if tl["segments"][0]["key"] == "hook" else None,
                          "endCardFrom": end_start},
             "words": [dict(w, seg=s["key"]) for s in tl["segments"] for w in s["words"]]}
    return props


def screen_text(props):
    """Every piece of text the video shows (for the numbers-on-screen check)."""
    out = []
    for e in props["elements"]:
        if e["kind"] == "text":
            out.append({"id": e["id"], "text": " ".join(e["lines"]), "tIn": e["tIn"], "tOut": e["tOut"]})
    for c in props["captions"]:
        out.append({"id": c["id"], "text": c["text"], "tIn": c["tIn"], "tOut": c["tOut"]})
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Render

def run(cmd, cwd=None, timeout=1800):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if r.returncode:
        raise RenderError(f"{os.path.basename(cmd[0])} failed: {(r.stderr or r.stdout)[-800:]}")
    return r


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    txt = r.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", txt)
    p = re.findall(r"Peak:\s+(-?[\d.]+|-inf) dBFS", txt)
    return (float(i[-1]) if i else None), (float(p[-1]) if p and p[-1] != "-inf" else None)


def mix_audio(tl_segments, voice_dir, seconds, out_wav, music_id):
    """The voice clips at their timeline starts, untouched, and the music bed about 14 LU under the voice; then the whole
    mix to -14 LUFS integrated with the true peak at or below -1.5 dBTP (two-pass loudnorm, linear)."""
    lib = json.load(open(os.path.join(ROOT, "tools", "music", "library.json"), encoding="utf-8"))
    track = next(t for t in lib["tracks"] if t["id"] == music_id)
    tmp = tempfile.mkdtemp()
    voice_wav = voice_track(tl_segments, voice_dir, seconds, os.path.join(tmp, "voice.wav"))
    vl, _ = loudness(voice_wav)
    if vl is None:
        raise RenderError("could not measure the voice loudness")
    music = os.path.join(ROOT, "tools", "music", track["file"])
    gain = (vl - 14.0) - track["lufs"]
    fade_at = max(0.0, seconds - 1.8)
    mix = os.path.join(tmp, "mix.wav")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", voice_wav, "-i", music, "-filter_complex",
         f"[1:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{seconds},asetpts=PTS-STARTPTS,volume={gain:.2f}dB,"
         f"afade=t=out:st={fade_at:.2f}:d=1.8,apad,atrim=0:{seconds}[m];[0:a][m]amix=inputs=2:normalize=0:duration=first[a]",
         "-map", "[a]", "-ar", "48000", "-ac", "2", mix])
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", mix, "-af", "loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mix, "-af",
         f"loudnorm=I=-14:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
         f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=48000",
         "-ar", "48000", "-ac", "2", out_wav])
    shutil.rmtree(tmp, ignore_errors=True)
    return {"musicId": music_id, "musicGainDb": round(gain, 2), "voiceLufsBefore": vl}


def voice_track(tl_segments, voice_dir, seconds, out_wav):
    """The voice clips alone, each at its timeline start, untouched (no speed change, no trim)."""
    inputs, filt = [], []
    for i, s in enumerate(tl_segments):
        inputs += ["-i", os.path.join(voice_dir, s["file"])]
        ms = int(round(s["start"] * 1000))
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms}[v{i}]")
    n = len(tl_segments)
    filt.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0,apad,atrim=0:{seconds}[voice]")
    run(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[voice]", "-ac", "2", "-ar", "48000", out_wav])
    return out_wav


def envelope(wav, fps=30):
    """The voice's loudness per video frame, 0 to 1 (RMS over each frame, scaled to the loudest frame), for the wave."""
    import array, wave as _w
    w = _w.open(wav, "rb")
    sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
    data = array.array("h", w.readframes(n))
    w.close()
    step = sr // fps
    env = []
    for f in range(0, n // step):
        seg = data[f * step * ch:(f + 1) * step * ch]
        rms = (sum(x * x for x in seg[::4]) / max(1, len(seg[::4]))) ** 0.5
        env.append(rms)
    top = sorted(env)[int(len(env) * 0.98)] if env else 1
    return [round(min(1.0, v / top), 3) if top else 0 for v in env]


INK_SCENES = ("hook", "end")


def wave_el(env, scenes=None):
    """One quiet color per background (ink2 on canvas, soft on ink), so the data keeps the only accent."""
    spans = [[sc["start"], sc["end"], T["soft"] if sc["scene"] in INK_SCENES else T["ink2"]] for sc in (scenes or [])]
    return {"id": "wave", "kind": "wave", "role": "decor", "x": X0, "y": 1290, "w": XW, "h": 150, "bars": 24, "colors": [T["ink2"]],
            "colorSpans": spans, "env": env, "tIn": 0.0, "tOut": None, "anim": "none", "group": None}


def stage_public():
    pub = os.path.join(TEMPLATE, "public", "fonts")
    os.makedirs(pub, exist_ok=True)
    for f in ("poppins-700.woff2", "poppins-600.woff2", "inter-400.woff2", "inter-600.woff2", "inter-700.woff2"):
        shutil.copy(os.path.join(L.FONT_DIR, f), os.path.join(pub, f))


def remotion_version():
    try:
        return json.load(open(os.path.join(TEMPLATE, "node_modules", "remotion", "package.json")))["version"]
    except OSError:
        return None


def node_version():
    try:
        return subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.strip()
    except OSError:
        return None


def render(spec_path, words_path, out_dir, browser=None):
    spec = json.load(open(spec_path, encoding="utf-8"))
    words = json.load(open(words_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    props = build_props(spec, words)
    probs = L.check(props)
    props_path = os.path.join(out_dir, "props.json")
    json.dump(props, open(props_path, "w"), indent=None)
    if probs:
        raise RenderError("layout check failed before rendering: " + "; ".join(probs[:6]))
    want = cfg()["remotion"]
    have = remotion_version()
    if have != want:
        raise RenderError(f"Remotion {have} is installed, the pin is {want} (npm ci in {os.path.relpath(TEMPLATE, ROOT)})")
    stage_public()
    voice_dir = os.path.dirname(os.path.abspath(words_path))
    env_wav = voice_track(props["timeline"]["segments"], voice_dir, props["seconds"], os.path.join(out_dir, "voice-only.wav"))
    props["elements"].append(wave_el(envelope(env_wav, props["fps"]), props["timeline"]["scenes"]))
    os.remove(env_wav)
    json.dump(props, open(props_path, "w"), indent=None)
    silent = os.path.join(out_dir, "silent.mp4")
    cmd = ["npx", "remotion", "render", "src/index.jsx", "RatCheck", silent, f"--props={os.path.abspath(props_path)}", "--muted",
           "--log=error", f"--concurrency={max(1, min(4, os.cpu_count() or 1))}"]
    if browser:
        cmd.append(f"--browser-executable={browser}")
    run(cmd, cwd=TEMPLATE, timeout=3600)
    audio = os.path.join(out_dir, "audio.wav")
    mixinfo = mix_audio(props["timeline"]["segments"], voice_dir, props["seconds"], audio, spec.get("music") or cfg()["music"]["id"])
    final = os.path.join(out_dir, "video.mp4")
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", audio, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac",
         "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", final])
    os.remove(silent)
    os.remove(audio)
    lufs, tp = true_peak_and_lufs(final)
    secs = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", final], capture_output=True, text=True).stdout)
    man = {"schema": "pnf.video.manifest.v1", "videoId": spec["videoId"], "mp4": "video.mp4", "sha256": sha_file(final),
           "bytes": os.path.getsize(final), "seconds": round(secs, 3), "lufs": lufs, "truePeak": tp, "remotion": have, "node": node_version(),
           "voice": {"id": words["voiceId"], "name": words["voiceName"], "model": words["model"], "test": words.get("test", False), "chars": words["chars"]},
           "voiceFiles": [{"key": s["key"], "file": s["file"], "sha256": s["sha256"], "seconds": s["seconds"]} for s in words["segments"]],
           "music": mixinfo, "specSha256": sha_file(spec_path), "propsSha256": sha_file(props_path), "layout": "PASS",
           "renderedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    json.dump(man, open(os.path.join(out_dir, "manifest.json"), "w"), indent=1)
    contact_sheet(final, props, os.path.join(out_dir, "sheet.jpg"))
    return man


def true_peak_and_lufs(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-map", "0:a", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)


def contact_sheet(mp4, props, out):
    """Twelve frames: frame one, the end of the hook, the middle and end of every scene, the end card."""
    times = [0.0]
    if props["timeline"].get("hookEnds"):
        times.append(props["timeline"]["hookEnds"])
    scenes = props["timeline"]["scenes"]
    for sc in scenes[:-1]:
        times += [sc["start"] + 1.6, (sc["start"] + sc["end"]) / 2]
    end = scenes[-1]
    times = sorted({round(min(max(0, t), props["seconds"] - 0.05), 2) for t in times})
    while len(times) > 10:   # thin the middle, keep frame one
        times.pop(len(times) // 2)
    times += [round(end["start"] + 1.2, 2), round(props["seconds"] - 0.1, 2)]   # the end card, always shown
    tmp = tempfile.mkdtemp()
    files = []
    for i, t in enumerate(times):
        f = os.path.join(tmp, f"{i:02d}.jpg")
        for back in (0, 0.2, 0.5):   # a seek past the last decodable frame writes nothing: step back, never skip the end card
            run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, t - back):.3f}", "-i", mp4, "-frames:v", "1", "-vf", "scale=360:640", f])
            if os.path.exists(f):
                t = round(max(0, t - back), 2)
                break
        else:
            raise RenderError(f"no frame at {t:.2f} s for the contact sheet")
        files.append((f, t))
    from PIL import Image, ImageDraw
    cols = 4
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 360 + (cols + 1) * 12, rows * (640 + 40) + 12), "#E2DDD3")
    dr = ImageDraw.Draw(sheet)
    for k, (f, t) in enumerate(files):
        im = Image.open(f)
        x, y = 12 + (k % cols) * 372, 12 + (k // cols) * 680
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + 646), f"{t:.2f} s", fill="#1D2433", font=L.font("I", 600, 24))
    sheet.save(out, quality=88)
    shutil.rmtree(tmp, ignore_errors=True)
    return [t for _, t in files]


def strips(mp4, props, out_dir, fps=5, per_sheet_s=4, transcript=None):
    """The render critic's view (the Video-Use idea, Oct 27: the model never watches the raw video): every frame at 5 a
    second, 4 seconds to a sheet, each frame labeled with its time and the words being spoken then, plus a word-timed
    transcript file. words come from the narration timeline, or from a speech-to-text transcript when one is given."""
    from PIL import Image, ImageDraw
    tmp = tempfile.mkdtemp()
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", f"fps={fps},scale=270:480", "-q:v", "3", os.path.join(tmp, "f%05d.jpg")])
    files = sorted(f for f in os.listdir(tmp) if f.endswith(".jpg"))
    words = transcript or [{"w": w["w"], "start": w["start"], "end": w["end"]} for w in props["words"]]
    os.makedirs(out_dir, exist_ok=True)
    per = per_sheet_s * fps
    cols, lab = 5, 56
    f_small, f_tiny = L.font("I", 600, 20), L.font("I", 400, 17)
    out = []
    for k in range(0, len(files), per):
        chunk = files[k:k + per]
        rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 270 + (cols + 1) * 8, rows * (480 + lab) + 8), "#E2DDD3")
        dr = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            t = (k + i) / fps
            x, y = 8 + (i % cols) * 278, 8 + (i // cols) * (480 + lab)
            sheet.paste(Image.open(os.path.join(tmp, f)), (x, y))
            said = " ".join(w["w"] for w in words if w["start"] <= t + 0.1 and w["end"] >= t - 0.1)
            dr.text((x + 2, y + 482), f"{t:05.2f} s", fill="#1D2433", font=f_small)
            dr.text((x + 2, y + 506), said[:34], fill="#4A5163", font=f_tiny)
        name = os.path.join(out_dir, f"strip-{k // per + 1:02d}-{k / fps:05.1f}s.jpg")
        sheet.save(name, quality=85)
        out.append(name)
    with open(os.path.join(out_dir, "transcript.txt"), "w") as fh:
        for w in words:
            fh.write(f"{w['start']:06.2f} {w['end']:06.2f} {w['w']}\n")
    shutil.rmtree(tmp, ignore_errors=True)
    return out


def frames(mp4, out_dir, fps=5):
    os.makedirs(out_dir, exist_ok=True)
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", f"fps={fps},scale=540:960", "-q:v", "4", os.path.join(out_dir, "f%04d.jpg")])
    return sorted(os.listdir(out_dir))


# ---------------------------------------------------------------------------------------------------------------------

def selftest():
    bad = []
    fx = os.path.join(ROOT, "video", "fixtures", "spec-example.json")
    spec = json.load(open(fx, encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    words = video_voice.test_voice(spec, tmp)
    try:
        props = build_props(spec, words)
    except RenderError as e:
        print("FAIL", e)
        return 1
    p = L.check(props)
    if p:
        bad.append("the example spec lays out clean: " + "; ".join(p[:4]))
    if not 45 <= props["seconds"] <= 60:
        bad.append(f"the example runs {props['seconds']} s")
    num = next(e for e in props["elements"] if e["id"] == "hook-number")
    if num["tIn"] != 0.0 or num["anim"] != "none":
        bad.append("frame one shows the number")
    say = "Up 221.4% since last year."
    heard = [{"w": w, "start": i * 0.3, "end": i * 0.3 + 0.25} for i, w in enumerate("Up two hundred twenty-one point four percent since last year.".split())]
    t = align(say.split(), heard)
    if not (t[1][0] == 0.3 and abs(t[1][1] - heard[6]["end"]) < 1e-6 and t[2][0] == heard[7]["start"]):
        bad.append(f"a caption number takes the span of its heard words: {t}")
    for b in bad:
        print("FAIL", b)
    print(f"video_render selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (timeline, scenes, captions, layout check clean, "
          "45 to 60 s, frame one shows the number, number alignment)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["props", "render", "frames", "strips"])
    ap.add_argument("--props"); ap.add_argument("--transcript")
    ap.add_argument("a", nargs="?"); ap.add_argument("b", nargs="?")
    ap.add_argument("--out"); ap.add_argument("--browser"); ap.add_argument("--fps", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    try:
        if a.cmd == "props":
            props = build_props(json.load(open(a.a)), json.load(open(a.b)))
            json.dump(props, open(a.out, "w"))
            p = L.check(props)
            for x in p:
                print("FAIL layout:", x)
            print(f"props: {len(props['elements'])} elements, {len(props['captions'])} captions, {props['seconds']} s; layout {'PASS' if not p else 'FAIL'}")
            sys.exit(1 if p else 0)
        elif a.cmd == "render":
            m = render(a.a, a.b, a.out, a.browser)
            print(f"rendered {m['videoId']}: {m['seconds']} s, {m['lufs']} LUFS, peak {m['truePeak']} dBTP, {m['bytes'] / 1e6:.1f} MB, voice {m['voice']['name']}")
        elif a.cmd == "strips":
            props = json.load(open(a.props or os.path.join(os.path.dirname(a.a), "props.json")))
            tr = json.load(open(a.transcript))["words"] if a.transcript else None
            n = strips(a.a, props, a.out, a.fps, transcript=tr)
            print(f"{len(n)} timeline sheets and transcript.txt in {a.out}")
        elif a.cmd == "frames":
            n = frames(a.a, a.out, a.fps)
            print(f"{len(n)} frames")
    except RenderError as e:
        print(f"ERROR render: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
