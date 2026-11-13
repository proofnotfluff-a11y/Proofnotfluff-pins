"""usage: render.py [out_dir]. One full render: the browser draws each frame from the time, ffmpeg encodes; then music and sounds are laid under it."""
import base64, json, os, subprocess, sys, time
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, "video")
OUT = sys.argv[1] if len(sys.argv) > 1 else "/tmp/pnf-trial-out"; os.makedirs(OUT, exist_ok=True)   # the MP4 stays off main
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", "..")); FPS = 30
silent = os.path.join(OUT, "silent.tmp.mp4")
with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + os.path.join(D, "stage.html"))
    for _ in range(100):
        if pg.evaluate("window.READY === true || !!window.BOOT_ERROR"): break
        pg.wait_for_timeout(100)
    dur = pg.evaluate("window.DURATION"); sfx = pg.evaluate("window.SFX"); n = int(round(dur * FPS)); t0 = time.time()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                            "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", "-color_range", "tv", silent], stdin=subprocess.PIPE)
    for i in range(n):
        url = pg.evaluate(f"(drawAt({i / FPS:.5f}), document.getElementById('c').toDataURL('image/jpeg', 0.95))")
        enc.stdin.write(base64.b64decode(url.split(",", 1)[1]))
    enc.stdin.close(); rc = enc.wait(); b.close()
    if errs or rc: raise SystemExit(f"render failed: {errs[:3]} rc {rc}")
    print(f"frames: {n} in {time.time() - t0:.0f} s")
# sound: one of the repo's own tracks (composed in code, ours), the studio's own effects on the beats
music = os.path.join(REPO, "tools/music/tracks/night-shift.opus"); SF = os.path.join(REPO, "video/studio/_runtime/sfx")
cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", music]; filt = [f"[0:a]atrim=0:{dur},afade=t=out:st={dur - 1.4}:d=1.4,volume=0.9[m]"]; mix = ["[m]"]
for k, (t, name, vol) in enumerate(sfx):
    cmd += ["-i", os.path.join(SF, name + ".wav")]; filt.append(f"[{k + 1}:a]adelay={int(max(0, t) * 1000)}:all=1,volume={vol * 0.8}[s{k}]"); mix.append(f"[s{k}]")
filt.append("".join(mix) + f"amix=inputs={len(mix)}:normalize=0:duration=longest,atrim=0:{dur},loudnorm=I=-14:TP=-2.5:LRA=11[a]")
wav = os.path.join(OUT, "mix.wav"); subprocess.run(cmd + ["-filter_complex", ";".join(filt), "-map", "[a]", "-ar", "48000", wav], check=True)
tmp = os.path.join(OUT, "trial.tmp.mp4"); final = os.path.join(OUT, "pnf-trial-statement-demo.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", silent, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", tmp], check=True)
os.replace(tmp, final); os.remove(silent); print(final)
