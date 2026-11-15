#!/usr/bin/env python3
"""usage: pack.py MP4 OUT. What a fresh reviewer gets, and nothing from the build: frames cut from the finished MP4
(two a second on sheets, full-size stills, one second of the face frame by frame, three stills with the apps' own
button areas drawn over them), the words as heard, and for the facts check unchanged copies of the source files.
Also runs the code checks on the MP4 and prints them as one JSON line (file, length, loudness, black frames)."""
import glob, hashlib, json, os, re, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
M, P = sys.argv[1], sys.argv[2].rstrip("/") + "/"
shutil.rmtree(P, ignore_errors=True)
for d in ("viewer", "design", "facts/source", "_f"): os.makedirs(P + d)
run = lambda *a: subprocess.run(a, check=True, capture_output=True, text=True)
run("ffmpeg", "-loglevel", "error", "-i", M, "-vf", "fps=2,scale=360:640", P + "_f/t%03d.jpg")
STILLS = [0, 0.7, 2.4, 4.2, 6.6, 8.9, 12.9, 16.9, 19.4, 22.3, 24.4, 26.1, 28.6, 31.3, 33.2, 36.2, 38.6, 41.9, 44.2, 47.6, 51.4]; MS = 24.0   # the stills, and the second shown frame by frame
for t in STILLS: run("ffmpeg", "-loglevel", "error", "-ss", str(t), "-i", M, "-frames:v", "1", "-q:v", "3", P + f"design/full-{t:05.1f}s.jpg")
run("ffmpeg", "-loglevel", "error", "-ss", str(MS), "-i", M, "-frames:v", "30", "-vf", "crop=400:440:340:1070", P + "_f/m%02d.jpg")
fp = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; font = ImageFont.truetype(fp, 22) if os.path.exists(fp) else ImageFont.load_default()
fs = sorted(glob.glob(P + "_f/t*.jpg")); per = 10
for k in range(0, len(fs), per):
    s = Image.new("RGB", (360 * 5, 674 * 2), "#111"); d = ImageDraw.Draw(s)
    for i, f in enumerate(fs[k:k + per]):
        x, y = (i % 5) * 360, (i // 5) * 674; s.paste(Image.open(f), (x, y + 34)); d.text((x + 8, y + 5), f"{(k + i) * 0.5:.1f} s", fill="#fff", font=font)
    s.save(P + f"viewer/timeline-{k // per + 1:02d}.jpg", quality=84)
for f in glob.glob(P + "viewer/timeline-*.jpg"): shutil.copy(f, P + "design/"); shutil.copy(f, P + "facts/")
w = json.load(open(os.path.join(HERE, "voice", "words.json")))["words"]; lines, cur, t0 = [], [], None
for q in w:
    if not cur: t0 = q["start"]
    cur.append(q["w"])
    if q["w"][-1] in ".?!": lines.append(f"[{t0:4.1f} s] " + " ".join(cur)); cur = []
tr = "The voice, word for word (one man's voice all the way through):\n\n" + "\n".join(lines) + "\n"
for r in ("viewer", "design", "facts"): open(P + r + "/words.txt", "w").write(tr)
s = Image.new("RGB", (200 * 10, 220 * 3), "#111")
for i, f in enumerate(sorted(glob.glob(P + "_f/m*.jpg"))): s.paste(Image.open(f).resize((200, 220), Image.NEAREST), ((i % 10) * 200, (i // 10) * 220))
s.save(P + "design/mouth-one-second.jpg", quality=90)
said = " ".join(f"{q['w']} ({q['start']:.2f} to {q['end']:.2f})" for q in w if q["end"] > MS and q["start"] < MS + 1)
open(P + "design/mouth-one-second.txt", "w").write(f"mouth-one-second.jpg: 30 frames in a row, left to right, top to bottom: the host's face from {MS} s to {MS + 1} s (each frame is 1/30 s). Words said in that second, with their start and end by speech recognition (give or take 0.05 s): {said}\n")
for name in (f"full-{STILLS[0]:05.1f}s", f"full-{STILLS[11]:05.1f}s", f"full-{STILLS[-1]:05.1f}s"):
    im = Image.open(P + f"design/{name}.jpg").convert("RGBA"); ov = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    for box in ([0, 0, 1080, 220], [0, 1470, 1080, 1920], [940, 900, 1080, 1470]): d.rectangle(box, fill=(255, 0, 90, 70))
    Image.alpha_composite(im, ov).convert("RGB").save(P + f"design/zones-{name}.jpg", quality=88)
open(P + "design/zones.txt", "w").write("zones-*.jpg: the pink areas are where the apps draw their own buttons and text over a video (top 220 px, bottom 450 px, a right column 140 px wide from y 900 to 1470). Conservative public figures, not exact for every phone.\n")
src = ["video/studio/research/heat/2026-11-13-results.json", "video/studio/research/heat/queries.json"] + [f"video/studio/research/metrics/{s}.json" for s in ("2026-11-17-after-hours-robot", "2026-11-14-ai-night-quote", "2026-11-19-ask-chatgpt")]
idx = []
for f in src:
    shutil.copy(os.path.join(REPO, f), P + "facts/source/" + os.path.basename(f)); idx.append(f"{os.path.basename(f)}  = repo file {f}  sha256 {hashlib.sha256(open(os.path.join(REPO, f), 'rb').read()).hexdigest()[:16]}")
open(P + "facts/source/INDEX.txt", "w").write("Copies of the repo's own files, unchanged:\n" + "\n".join(idx) + "\n")
for f in glob.glob(P + "design/full-*.jpg"): shutil.copy(f, P + "facts/")
shutil.rmtree(P + "_f")
# code checks on the MP4
pr = json.loads(run("ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_name,width,height,r_frame_rate", "-of", "json", M).stdout)
eb = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", M, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True).stderr
lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", eb)[-1]); peak = float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", eb)[-1])
bl = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", M, "-vf", "blackdetect=d=0.05:pix_th=0.08", "-an", "-f", "null", "-"], capture_output=True, text=True).stderr.count("black_start")
v = next(x for x in pr["streams"] if x["codec_name"] == "h264"); dur = float(pr["format"]["duration"])
qa = {"file": f"{v['width']}x{v['height']} {v['r_frame_rate']} h264 + aac, {int(pr['format']['size']) // 1024} KB", "file_pass": v["width"] == 1080 and v["height"] == 1920 and v["r_frame_rate"] == "30/1",
      "length_s": round(dur, 2), "loudness_lufs": lufs, "true_peak_dbfs": peak, "loudness_pass": -15.0 <= lufs <= -13.0 and peak <= -1.0, "black_frames": bl, "black_pass": bl == 0,
      "mp4_sha256": hashlib.sha256(open(M, "rb").read()).hexdigest()}
print(json.dumps(qa))
