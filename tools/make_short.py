#!/usr/bin/env python3
"""Build a ProofNotFluff YouTube Short from a scene spec.

Usage: python3 make_short.py spec.json out.mp4
Spec: {"kicker": str, "headline_html": str, "cells": [{"label","value","kind"}], "fix": str, "cta": str,
       "voice_lines": [str x5], "voice": "ryan-medium"|"lessac-medium", "theme": "ink"|"paper"}
Every frame is rendered individually (no screen recording), voice is Piper TTS, music is synthesized here.
"""
import json, os, subprocess, sys, wave, shutil, urllib.request, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30
W, H = 1080, 1920
FONTS = "/usr/share/fonts/truetype"

def ensure_voice(name):
    d = os.path.join(HERE, "voices"); os.makedirs(d, exist_ok=True)
    onnx = os.path.join(d, f"en-us-{name}.onnx")
    if not os.path.exists(onnx):
        url = f"https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-{name}.tar.gz"
        tgz = os.path.join(d, "v.tar.gz"); urllib.request.urlretrieve(url, tgz)
        subprocess.run(["tar", "xzf", tgz, "-C", d], check=True); os.remove(tgz)
    return onnx

def tts(lines, voice, workdir):
    from piper import PiperVoice
    v = PiperVoice.load(ensure_voice(voice))
    paths, durs = [], []
    for i, t in enumerate(lines):
        p = os.path.join(workdir, f"line{i}.wav")
        with wave.open(p, "wb") as w: v.synthesize_wav(t, w)
        with wave.open(p) as w: durs.append(w.getnframes() / w.getframerate())
        paths.append(p)
    return paths, durs

def music(duration, path, sr=44100, seed=7):
    """Soft pad chords plus a slow plucked line, generated, royalty free by construction."""
    rng = np.random.default_rng(seed)
    t = np.arange(int(duration * sr)) / sr
    # D major-ish progression: D, Bm, G, A (two bars each at 72 bpm, 4/4) -> 6.67 s per chord
    chords = [[146.83, 220.0, 293.66, 369.99], [123.47, 185.0, 246.94, 293.66], [98.0, 146.83, 196.0, 246.94], [110.0, 164.81, 220.0, 277.18]]
    seg = 60 / 72 * 8
    out = np.zeros_like(t)
    for i in range(int(math.ceil(duration / seg)) + 1):
        ch = chords[i % 4]; s = i * seg; e = min(s + seg, duration)
        if s >= duration: break
        idx = (t >= s) & (t < e); tt = t[idx] - s
        env = np.minimum(tt / 1.2, 1) * np.minimum((e - s - tt) / 1.2, 1)
        pad = np.zeros_like(tt)
        for f in ch:
            for k, a in ((1, 1.0), (2, 0.25), (3, 0.08)):
                pad += a * np.sin(2 * np.pi * f * k * tt + rng.uniform(0, 6.28)) * (1 + 0.08 * np.sin(2 * np.pi * 0.15 * tt))
        out[idx] += 0.12 * env * pad / 12
        # pluck on beats 1 and 3 of each bar, root or fifth, octave up
        for b in range(8):
            bt = b * (60 / 72)
            if bt >= e - s: break
            if b % 2 == 0:
                f = ch[0] * (2 if b % 4 == 0 else 1.5)
                m = (tt >= bt) & (tt < bt + 1.5); x = tt[m] - bt
                out[idx.nonzero()[0][m]] += 0.07 * np.exp(-x * 2.2) * np.sin(2 * np.pi * f * x) * (1 - np.exp(-x * 200))
    # gentle lowpass by moving average, then fade in/out
    k = int(sr / 1800); out = np.convolve(out, np.ones(k) / k, mode="same")
    fade = np.minimum(t / 1.5, 1) * np.minimum((duration - t) / 2.5, 1)
    out = out * fade
    out = out / (np.max(np.abs(out)) + 1e-9) * 0.5
    pcm = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())

def html(spec, times):
    th = spec.get("theme", "ink")
    bg, fg, muted, cellbg = ("#1D2433", "#fff", "#C9CEDA", "rgba(255,255,255,.07)") if th == "ink" else ("#F5F2EC", "#1D2433", "#5E6670", "#fff")
    kick = "#E9B49F" if th == "ink" else "#C8502F"; bad = "#F08A66" if th == "ink" else "#C8502F"
    cells = "".join(f'<div class="cell {c.get("kind","")}" style="animation-delay:{times["cells"][i]:.2f}s"><div class="l">{c["label"]}</div><div class="v">{c["value"]}</div></div>' for i, c in enumerate(spec["cells"]))
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url(file://{FONTS}/google-fonts/Poppins-Bold.ttf);font-weight:700}}
@font-face{{font-family:C;src:url(file://{FONTS}/crosextra/Carlito-Regular.ttf)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{bg};color:{fg};font-family:C;position:relative}}
.bars{{position:absolute;top:150px;left:90px;display:flex;gap:10px}}.bars i{{width:56px;height:10px;border-radius:5px;display:block}}
.k{{position:absolute;top:200px;left:90px;font-family:P;font-size:30px;letter-spacing:4px;color:{kick}}}
h1{{position:absolute;top:262px;left:90px;width:900px;font-family:P;font-size:84px;line-height:1.1}} h1 span{{color:{bad}}}
.grid{{position:absolute;top:700px;left:90px;width:900px;display:grid;grid-template-columns:1fr 1fr;gap:26px}}
.cell{{background:{cellbg};border-radius:24px;padding:34px 36px;box-shadow:0 6px 20px rgba(0,0,0,.08)}} .cell .l{{font-size:30px;color:{muted}}} .cell .v{{font-family:P;font-size:70px;margin-top:8px}}
.cell.bad .v{{color:{bad}}} .cell.good{{background:#2E6B66;color:#fff}} .cell.good .l{{color:#DDEFEC}}
p{{position:absolute;top:1190px;left:90px;width:900px;font-size:40px;line-height:1.38}}
.pill{{position:absolute;top:1430px;left:90px;background:#C8502F;color:#fff;font-family:P;font-size:34px;padding:22px 40px;border-radius:60px}}
.foot{{position:absolute;top:1640px;left:90px;font-family:P;font-size:28px;color:#9AA3B5;letter-spacing:1px}} .foot b{{display:block;font-family:C;font-weight:400;font-size:26px;color:#7F8899;margin-top:8px;letter-spacing:0}}
.bars,.k,h1,.cell,p,.pill{{opacity:0;transform:translateY(36px);animation:fade .55s cubic-bezier(.2,.7,.2,1) forwards}}
@keyframes fade{{to{{opacity:1;transform:none}}}}
</style></head><body>
<div class="bars" style="animation-delay:.1s"><i style="background:#C8502F"></i><i style="background:#2E6B66"></i><i style="background:#6B4FA0"></i><i style="background:#2F5F9E"></i><i style="background:#8A6A1F"></i></div>
<div class="k" style="animation-delay:.3s">{spec["kicker"]}</div>
<h1 style="animation-delay:{times["headline"]:.2f}s">{spec["headline_html"]}</h1>
<div class="grid">{cells}</div>
<p style="animation-delay:{times["fix"]:.2f}s">{spec["fix"]}</p>
<div class="pill" style="animation-delay:{times["cta"]:.2f}s">{spec["cta"]}</div>
<div class="foot">PROOFNOTFLUFF<b>{spec.get("footer", "Written by a finance executive")}</b></div>
</body></html>"""

def render_frames(page_html, nframes, workdir):
    from playwright.sync_api import sync_playwright
    fdir = os.path.join(workdir, "frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    hp = os.path.join(workdir, "scene.html"); open(hp, "w").write(page_html)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": W, "height": H})
        pg.goto("file://" + hp); pg.wait_for_timeout(300)
        pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
        for i in range(nframes):
            pg.evaluate("t=>document.getAnimations().forEach(a=>{a.currentTime=t})", i * 1000 / FPS)
            pg.screenshot(path=os.path.join(fdir, f"f{i:05d}.png"), type="png")
        b.close()
    return fdir

def main(spec_path, out):
    spec = json.load(open(spec_path)); work = os.path.join(HERE, "work"); os.makedirs(work, exist_ok=True)
    paths, durs = tts(spec["voice_lines"], spec.get("voice", "ryan-medium"), work)
    gap = 0.45; starts = []; t = 0.6
    for d in durs: starts.append(t); t += d + gap
    total = t + 1.2
    n = len(spec["cells"])
    # line 0 -> headline, line 1 -> cells 0,1, line 2 -> cell 2, line 3 -> cell 3 + fix, line 4 -> cta
    times = {"headline": starts[0], "cells": [starts[1], starts[1] + 1.4, starts[2], starts[3]][:n], "fix": starts[3] + 1.6, "cta": starts[4]}
    fdir = render_frames(html(spec, times), int(total * FPS), work)
    mpath = os.path.join(work, "music.wav"); music(total, mpath)
    # voice track: place each line at its start
    inputs = []; filt = []
    for i, p in enumerate(paths):
        inputs += ["-i", p]; filt.append(f"[{i+1}:a]aresample=44100,adelay={int(starts[i]*1000)}|{int(starts[i]*1000)}[v{i}]")
    vmix = "".join(f"[v{i}]" for i in range(len(paths)))
    filt.append(f"{vmix}amix=inputs={len(paths)}:normalize=0,volume=1.6[voice]")
    filt.append(f"[0:a]volume=0.22[mus]")
    filt.append(f"[voice][mus]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", mpath] + inputs + ["-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"),
           "-filter_complex", ";".join(filt), "-map", f"{len(paths)+1}:v", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print(json.dumps({"out": out, "seconds": round(total, 1), "lines": len(paths)}))

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
