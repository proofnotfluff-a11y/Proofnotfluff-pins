#!/usr/bin/env python3
"""usage: render.py OUT_DIR VOICE_WAV. One full render: the browser draws each frame from the time and ffmpeg encodes;
then the voice (the tightened take, voice.py tighten), one of the repo's own music tracks kept low under it, and the
studio's own sound effects on the beats. The MP4 stays off main."""
import base64, json, os, subprocess, sys, time
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "video")
OUT, VOICE = sys.argv[1], sys.argv[2]; os.makedirs(OUT, exist_ok=True)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..")); FPS = 30
silent = os.path.join(OUT, "silent.tmp.mp4")
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None, args=["--allow-file-access-from-files", "--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + os.path.join(D, "stage.html"))
    for _ in range(150):
        if pg.evaluate("window.READY === true || !!window.BOOT_ERROR"): break
        pg.wait_for_timeout(100)
    if errs or pg.evaluate("window.BOOT_ERROR"): raise SystemExit(f"stage failed: {errs} {pg.evaluate('window.BOOT_ERROR')}")
    if not pg.evaluate("window.STAGE.hasMouth"): raise SystemExit("no mouth.js: run voice.py mouth first")
    dur = pg.evaluate("window.DURATION"); sfx = pg.evaluate("window.SFX"); n = int(round(dur * FPS)); t0 = time.time()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", silent], stdin=subprocess.PIPE)
    for i in range(n):
        url = pg.evaluate(f"(drawAt({i / FPS:.5f}), document.getElementById('c').toDataURL('image/jpeg', 0.95))")
        enc.stdin.write(base64.b64decode(url.split(",", 1)[1]))
    enc.stdin.close(); rc = enc.wait(); b.close()
    if errs or rc: raise SystemExit(f"render failed: {errs[:3]} rc {rc}")
    print(f"frames: {n} in {time.time() - t0:.0f} s")
music = os.path.join(REPO, "tools/music/tracks/ledger-lofi.opus"); SF = os.path.join(REPO, "video/studio/_runtime/sfx")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", VOICE, "-i", music]
filt = ["[0:a]aresample=48000,volume=1.0[v]", f"[1:a]aresample=48000,atrim=0:{dur},afade=t=in:st=0:d=0.3,afade=t=out:st={dur - 1.2}:d=1.2,volume=0.11[m]"]; mix = ["[v]", "[m]"]
for k, (t, name, vol) in enumerate(sorted(sfx)):
    cmd += ["-i", os.path.join(SF, name + ".wav")]
    filt.append(f"[{k + 2}:a]aresample=48000,adelay={int(max(0, t) * 1000)}:all=1,volume={vol * 0.3:.3f}[s{k}]"); mix.append(f"[s{k}]")
filt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,apad,atrim=0:{dur}[a]")
raw = os.path.join(OUT, "mix.raw.wav"); subprocess.run(cmd + ["-filter_complex", ";".join(filt), "-map", "[a]", "-ar", "48000", "-ac", "2", raw], check=True)
import re
lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", raw, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr)[-1])
wav = os.path.join(OUT, "mix.wav")   # one gain to -14 LUFS, then a limiter so no peak passes -2 dB
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", f"volume={-14.0 - lufs:.2f}dB,alimiter=limit=0.79:level=false", "-ar", "48000", wav], check=True); os.remove(raw)
tmp = os.path.join(OUT, "trial.tmp.mp4"); final = os.path.join(OUT, "pnf-trial-host-below.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, final); os.remove(silent); print(final)
