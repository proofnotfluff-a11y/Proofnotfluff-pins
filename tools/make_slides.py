#!/usr/bin/env python3
"""ProofNotFluff Short, slideshow style: full-screen slides with text, music only, every frame rendered.
Usage: python3 make_slides.py spec.json out.mp4
Spec: {"theme":"ink"|"paper", "footer": str, "slides":[{"type":"hook"|"stat"|"compare"|"fix"|"cta", ...}]}
 hook:    kicker, title_html
 stat:    kicker, label, value, sub, kind ""|"bad"|"good"
 compare: kicker, left:{label,value,kind}, right:{label,value,kind}, note
 fix:     kicker, title, formula, sub
 cta:     title, button, sub
"""
import json, os, subprocess, sys, wave, shutil, math
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30; W, H = 1080, 1920; FONTS = "/usr/share/fonts/truetype"
BPM = 90; BAR = 60 / BPM * 4; SLIDE = 2 * BAR  # 5.33 s per slide

def music(duration, path, sr=44100, seed=11):
    rng = np.random.default_rng(seed); t = np.arange(int(duration * sr)) / sr
    chords = [[146.83, 220.0, 293.66, 369.99], [123.47, 185.0, 246.94, 293.66], [98.0, 146.83, 196.0, 246.94], [110.0, 164.81, 220.0, 277.18]]
    out = np.zeros_like(t); seg = SLIDE
    for i in range(int(math.ceil(duration / seg)) + 1):
        ch = chords[i % 4]; s = i * seg; e = min(s + seg, duration)
        if s >= duration: break
        idx = (t >= s) & (t < e); tt = t[idx] - s
        env = np.minimum(tt / 0.9, 1) * np.minimum((e - s - tt) / 0.9, 1)
        pad = np.zeros_like(tt)
        for f in ch:
            for k, a in ((1, 1.0), (2, 0.22), (3, 0.06)):
                pad += a * np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6.28)) * (1 + 0.06 * np.sin(2 * np.pi * 0.2 * tt))
        out[idx] += 0.12 * env * pad / 12
        ii = idx.nonzero()[0]
        for b in range(8):
            bt = b * (60 / BPM)
            if bt >= e - s: break
            f = ch[[0, 2, 1, 3][b % 4]] * 2
            m = (tt >= bt) & (tt < bt + 1.2); x = tt[m] - bt
            out[ii[m]] += 0.06 * np.exp(-x * 3) * np.sin(2 * np.pi * f * x) * (1 - np.exp(-x * 300))
            if b % 2 == 0:  # soft kick
                m2 = (tt >= bt) & (tt < bt + 0.25); x2 = tt[m2] - bt
                out[ii[m2]] += 0.18 * np.exp(-x2 * 18) * np.sin(2 * np.pi * (60 + 40 * np.exp(-x2 * 30)) * x2)
    k = int(sr / 2200); out = np.convolve(out, np.ones(k) / k, mode="same")
    out *= np.minimum(t / 1.0, 1) * np.minimum((duration - t) / 2.0, 1)
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.6
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((out * 32767).astype(np.int16).tobytes())

def slide_html(s, i, theme):
    d = lambda k: f'style="animation-delay:{i*SLIDE + k:.2f}s"'
    kick = f'<div class="k" {d(0.25)}>{s.get("kicker","")}</div>' if s.get("kicker") else ""
    if s["type"] == "hook":
        body = f'{kick}<h1 class="big" {d(0.45)}>{s["title_html"]}</h1>'
    elif s["type"] == "stat":
        body = f'{kick}<div class="lab" {d(0.4)}>{s["label"]}</div><div class="num {s.get("kind","")}" {d(0.7)}>{s["value"]}</div><div class="sub" {d(1.2)}>{s.get("sub","")}</div>'
    elif s["type"] == "compare":
        L, R = s["left"], s["right"]
        body = (f'{kick}<div class="cmp"><div class="box {L.get("kind","")}" {d(0.4)}><div class="lab">{L["label"]}</div><div class="num">{L["value"]}</div></div>'
                f'<div class="box {R.get("kind","")}" {d(1.1)}><div class="lab">{R["label"]}</div><div class="num">{R["value"]}</div></div></div><div class="sub" {d(1.9)}>{s.get("note","")}</div>')
    elif s["type"] == "fix":
        body = f'{kick}<h2 {d(0.4)}>{s["title"]}</h2><div class="formula" {d(0.9)}>{s["formula"]}</div><div class="sub" {d(1.6)}>{s.get("sub","")}</div>'
    else:
        body = f'<h2 {d(0.3)}>{s["title"]}</h2><div class="btn" {d(0.9)}>{s["button"]}</div><div class="sub" {d(1.4)}>{s.get("sub","")}</div>'
    return f'<section style="animation-delay:{i*SLIDE:.2f}s,{(i+1)*SLIDE-0.35:.2f}s">{body}</section>'

def html(spec):
    th = spec.get("theme", "ink")
    bg, fg, muted, box = ("#1D2433", "#fff", "#B9C0CC", "rgba(255,255,255,.07)") if th == "ink" else ("#F5F2EC", "#1D2433", "#5E6670", "#fff")
    bad = "#F08A66" if th == "ink" else "#C8502F"; kick = "#E9B49F" if th == "ink" else "#C8502F"
    n = len(spec["slides"]); last = n * SLIDE
    secs = "".join(slide_html(s, i, th) for i, s in enumerate(spec["slides"]))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url(file://{FONTS}/google-fonts/Poppins-Bold.ttf);font-weight:700}}
@font-face{{font-family:PM;src:url(file://{FONTS}/google-fonts/Poppins-Medium.ttf)}}
@font-face{{font-family:C;src:url(file://{FONTS}/crosextra/Carlito-Regular.ttf)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{bg};color:{fg};font-family:C;position:relative}}
.bars{{position:absolute;top:140px;left:90px;display:flex;gap:10px;z-index:5}}.bars i{{width:56px;height:10px;border-radius:5px;display:block}}
.foot{{position:absolute;bottom:150px;left:90px;right:90px;font-family:P;font-size:28px;color:#9AA3B5;letter-spacing:1px;z-index:5}} .foot b{{display:block;font-family:C;font-weight:400;font-size:26px;color:#7F8899;margin-top:8px;letter-spacing:0}}
.prog{{position:absolute;top:110px;left:90px;right:90px;height:6px;background:rgba(128,128,128,.25);border-radius:3px;z-index:5}} .prog i{{display:block;height:100%;width:0;background:#C8502F;border-radius:3px;animation:grow {last:.2f}s linear forwards}}
@keyframes grow{{to{{width:100%}}}}
section{{position:absolute;left:90px;right:90px;top:300px;bottom:360px;display:flex;flex-direction:column;justify-content:center;opacity:0;animation:sin .5s ease-out forwards, sout .35s ease-in forwards}}
@keyframes sin{{from{{opacity:0;transform:translateX(60px)}}to{{opacity:1;transform:none}}}} @keyframes sout{{from{{opacity:1;transform:none}}to{{opacity:0;transform:translateX(-60px)}}}}
section>*{{opacity:0;transform:translateY(34px);animation:up .55s cubic-bezier(.2,.7,.2,1) forwards}} @keyframes up{{to{{opacity:1;transform:none}}}}
.k{{font-family:P;font-size:30px;letter-spacing:4px;color:{kick};margin-bottom:34px}}
h1.big{{font-family:P;font-size:104px;line-height:1.08;letter-spacing:-1px}} h1 span,.num.bad,.box.bad .num{{color:{bad}}}
h2{{font-family:P;font-size:76px;line-height:1.12;margin-bottom:30px}}
.lab{{font-size:40px;color:{muted}}} .num{{font-family:P;font-size:220px;line-height:1;margin:12px 0 26px}} .num.good{{color:#5BBFA7}}
.sub{{font-size:40px;line-height:1.38;color:{fg};opacity:.92}}
.cmp{{display:flex;gap:26px;margin-bottom:34px}} .box{{flex:1;background:{box};border-radius:26px;padding:40px 36px;box-shadow:0 8px 24px rgba(0,0,0,.08)}} .box .num{{font-size:110px;margin:10px 0 0}} .box.good{{background:#2E6B66;color:#fff}} .box.good .lab{{color:#DDEFEC}}
.formula{{font-family:P;font-size:64px;background:{box};border-radius:26px;padding:40px 44px;margin-bottom:30px;line-height:1.3}}
.btn{{display:inline-block;align-self:flex-start;background:#C8502F;color:#fff;font-family:P;font-size:38px;padding:26px 44px;border-radius:60px;margin:10px 0 30px}}
</style></head><body>
<div class="prog"><i></i></div>
<div class="bars"><i style="background:#C8502F"></i><i style="background:#2E6B66"></i><i style="background:#6B4FA0"></i><i style="background:#2F5F9E"></i><i style="background:#8A6A1F"></i></div>
{secs}
<div class="foot">PROOFNOTFLUFF<b>{spec.get("footer","Written by a finance executive")}</b></div>
</body></html>"""

def render(page_html, nframes, workdir):
    from playwright.sync_api import sync_playwright
    fdir = os.path.join(workdir, "frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    hp = os.path.join(workdir, "scene.html"); open(hp, "w").write(page_html)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H}); pg.goto("file://" + hp); pg.wait_for_timeout(300)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(nframes):
            pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", i * 1000 / FPS)
            pg.screenshot(path=os.path.join(fdir, f"f{i:05d}.png"))
        b.close()
    return fdir

# YouTube made links in Shorts descriptions unclickable (Aug 31, 2023), so a CTA that points
# to the description sends viewers nowhere. Every CTA ends on a route that works.
CTA_SUB = "On Etsy: etsy.com/shop/ProofNotFluff"

def fix_cta(spec):
    for s in spec["slides"]:
        if s.get("type") == "cta":
            sub = s.get("sub", "")
            if not sub or "description" in sub.lower() or "link below" in sub.lower():
                s["sub"] = CTA_SUB
    return spec

def main(spec_path, out):
    spec = fix_cta(json.load(open(spec_path))); work = os.path.join(HERE, "work"); os.makedirs(work, exist_ok=True)
    total = len(spec["slides"]) * SLIDE
    fdir = render(html(spec), int(total * FPS), work)
    mp = os.path.join(work, "music.wav"); music(total, mp)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp, "-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"),
                    "-map", "1:v", "-map", "0:a", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(fdir, ignore_errors=True); print(json.dumps({"out": out, "seconds": round(total, 1), "slides": len(spec["slides"])}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
