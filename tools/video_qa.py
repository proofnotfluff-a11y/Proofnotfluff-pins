#!/usr/bin/env python3
"""Video QA, gate 5 of the video engine: every check runs in code on the finished MP4, and a check that cannot run
counts as a FAIL (blueprint, "Video QA thresholds (gate 5)"; settings in video/config.json "qa").

  length        45.0 to 60.0 seconds
  loudness      -14 LUFS integrated, plus or minus 1; true peak at or below -1.5 dBTP
  black         no black stretch of 0.5 s or longer (ffmpeg blackdetect)
  frozen        no frozen stretch of 1.0 s or longer outside the end card (ffmpeg freezedetect)
  hook          the hook's last word ends by 3.0 s (the narration timeline the mix was built from)
  numbers       every number the video means to show is read on screen, and no other number is (Tesseract, 2 frames a second)
  safe-band     every word read on screen sits between y 270 and 1250 and left of x 930
  faces         no face at 0.6 confidence or more, one frame a second (OpenCV YuNet)
  file          opens, decodes to the end, 1080 x 1920, 30 fps, H.264 and AAC, under 100 MB, matches the manifest's sha256
  layout        the pre-render layout check on props.json (no overlaps, nothing outside the band, no text under 42 px)

Usage
  video_qa.py check DIR [--spec SPEC]         DIR holds video.mp4, manifest.json, props.json; writes DIR/qa.json
  video_qa.py recheck DIR --fault KIND [--at SECONDS] [--text NUMBER]
        the render critic's fault, re-checked in code before anything changes; KIND is one of hook-number,
        number-readable, overlap, audio-end. Prints CONFIRMED or NOT CONFIRMED with the measured value.
  video_qa.py --selftest                      planted failures for every check (renders tiny clips with ffmpeg)
"""
import argparse, hashlib, json, os, re, shutil, subprocess, sys, tempfile, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import video_layout as L  # noqa: E402

YUNET_URL = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx"
YUNET_SHA = "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4"
MODELS = os.path.join(os.path.expanduser("~"), ".cache", "pnf-video-models")
NUMTOK = re.compile(r"^[+\-]?\d[\d,]*(?:\.\d+)?%?$")


def cfg():
    return json.load(open(os.path.join(ROOT, "video", "config.json"), encoding="utf-8"))["qa"]


def vcfg():
    return json.load(open(os.path.join(ROOT, "video", "config.json"), encoding="utf-8"))["video"]


def sh(cmd, timeout=900):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def sha_file(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def norm_num(tok):
    """'+221.4%' -> '221.4'; '4,554' -> '4554'; '40.0' -> '40'."""
    t = tok.strip().strip(".,;:()?!\"'").lstrip("+-").rstrip("%")
    t = t.replace(",", "")
    if not re.fullmatch(r"\d+(?:\.\d+)?", t):
        return None
    if "." in t:
        t = t.rstrip("0").rstrip(".")
    return t


def numbers_in(text):
    out = set()
    for tok in re.split(r"\s+", text or ""):
        tok = tok.strip(".,;:()?!\"'")
        if NUMTOK.match(tok):
            n = norm_num(tok)
            if n is not None:
                out.add(n)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# Each check returns (value, pass, detail).

def probe(mp4):
    r = sh(["ffprobe", "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate",
            "-of", "json", mp4])
    if r.returncode:
        raise RuntimeError(r.stderr[-300:])
    return json.loads(r.stdout)


def c_length(mp4):
    secs = float(probe(mp4)["format"]["duration"])
    v = vcfg()
    return round(secs, 3), v["minSeconds"] <= secs <= v["maxSeconds"], f"{secs:.2f} s (45.0 to 60.0)"


def c_loudness(mp4):
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-map", "0:a:0", "-af", "ebur128=peak=true", "-f", "null", "-"])
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r.stderr)
    if not i or not p:
        raise RuntimeError("no loudness reading (no audio stream?)")
    lufs, tp = float(i[-1]), float(p[-1])
    q = cfg()
    ok = abs(lufs - q["lufs"]) <= q["lufsTol"] and tp <= q["truePeakMax"]
    return {"lufs": lufs, "truePeak": tp}, ok, f"{lufs} LUFS (target -14 +/- 1), true peak {tp} dBTP (at most -1.5)"


def c_black(mp4):
    q = cfg()
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-vf", f"blackdetect=d={q['blackMaxSeconds']}:pix_th=0.10", "-an", "-f", "null", "-"])
    hits = re.findall(r"black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)", r.stderr)
    return [[float(a), float(b)] for a, b, _ in hits], not hits, f"{len(hits)} black stretch(es) of 0.5 s or more"


def c_frozen(mp4, end_card_from):
    q = cfg()
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", mp4, "-vf", f"freezedetect=n={q.get('freezeNoiseDb', -60)}dB:d={q['freezeMaxSeconds']}", "-an", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", r.stderr)]
    ends = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", r.stderr)]
    dur = float(probe(mp4)["format"]["duration"])
    spans = [[s, ends[i] if i < len(ends) else dur] for i, s in enumerate(starts)]
    bad = [s for s in spans if s[0] < end_card_from - 0.05]
    return spans, not bad, f"{len(bad)} frozen stretch(es) of 1.0 s or more before the end card at {end_card_from:.2f} s"


def c_hook(props):
    q = cfg()
    hook = [w for w in props.get("words", []) if w.get("seg") == "hook"]
    if not hook:
        raise RuntimeError("no hook words in the timeline")
    end = max(w["end"] for w in hook)
    return round(end, 3), end <= q["hookEndsBy"], f"hook's last word ends at {end:.2f} s (by 3.00)"


def sample_frames(mp4, per_second, out_dir, scale=None):
    os.makedirs(out_dir, exist_ok=True)
    vf = f"fps={per_second}" + (f",scale={scale}" if scale else "")
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", vf, "-q:v", "2", os.path.join(out_dir, "f%04d.png")], timeout=1800)
    if r.returncode:
        raise RuntimeError(r.stderr[-300:])
    files = sorted(f for f in os.listdir(out_dir) if f.endswith(".png"))
    return [(os.path.join(out_dir, f), (i + 0.5) / per_second) for i, f in enumerate(files)]


def ocr_words(png):
    """Words Tesseract reads on one frame, with boxes in frame pixels; dark grounds are read inverted too."""
    from PIL import Image, ImageOps
    im = Image.open(png).convert("L")
    words = []
    for variant in (im, ImageOps.invert(im)):
        tmp = png + ".v.png"
        variant.save(tmp)
        r = sh(["tesseract", tmp, "-", "--psm", "11", "-l", "eng", "tsv"], timeout=120)
        os.remove(tmp)
        if r.returncode:
            raise RuntimeError("tesseract failed: " + r.stderr[-200:])
        for line in r.stdout.splitlines()[1:]:
            p = line.split("\t")
            if len(p) < 12 or not p[11].strip():
                continue
            try:
                conf = float(p[10])
            except ValueError:
                continue
            words.append({"text": p[11].strip(), "conf": conf, "x": int(p[6]), "y": int(p[7]), "w": int(p[8]), "h": int(p[9])})
    return words


def expected_numbers(props):
    import video_render
    out = {}
    for t in video_render.screen_text(props):
        for n in numbers_in(t["text"]):
            out.setdefault(n, []).append(t["id"])
    return out


def c_numbers_and_band(mp4, props, work):
    q = cfg()
    frames = sample_frames(mp4, q["ocrPerSecond"], os.path.join(work, "ocr"))
    want = expected_numbers(props)
    seen, extra, outside = {}, [], []
    # drawn shapes the props mark as decor (the voice wave, the brand bars) are not text: a rounded bar at rest can
    # read as "0", so a read whose center sits inside one is ignored (Oct 27, the first CI render)
    decor = [e for e in props.get("elements", []) if e.get("role") == "decor"]

    def in_decor(w, t):
        cx, cy = w["x"] + w["w"] / 2, w["y"] + w["h"] / 2
        return any(e["x"] - 4 <= cx <= e["x"] + e["w"] + 4 and e["y"] - 4 <= cy <= e["y"] + e["h"] + 4
                   and e["tIn"] <= t and (e.get("tOut") is None or t < e["tOut"]) for e in decor)
    for f, t in frames:
        for w in ocr_words(f):
            if in_decor(w, t):
                continue
            tok = w["text"].strip(".,;:()?!\"'")
            if NUMTOK.match(tok) and w["conf"] >= 60:
                n = norm_num(tok)
                if n in want:
                    seen.setdefault(n, t)
                elif n is not None and w["conf"] >= 75:
                    extra.append({"n": n, "t": round(t, 2), "conf": w["conf"]})
            if w["conf"] >= 70 and len(re.sub(r"\W", "", w["text"])) >= 2:
                if w["y"] < q["safeTop"] or w["y"] + w["h"] > q["safeBottom"] or w["x"] + w["w"] > L.W - q["rightClear"] + 2:
                    outside.append({"text": w["text"], "t": round(t, 2), "y": w["y"], "bottom": w["y"] + w["h"], "right": w["x"] + w["w"]})
    missing = sorted(set(want) - set(seen))
    num = ({"expected": sorted(want), "seen": sorted(seen), "missing": missing, "unexpected": extra[:10]},
           not missing and not extra,
           f"{len(seen)} of {len(want)} numbers read on screen; missing {missing or 'none'}; unexpected {[e['n'] for e in extra][:6] or 'none'}")
    band = (outside[:10], not outside, f"{len(outside)} word(s) read outside y {q['safeTop']} to {q['safeBottom']} or in the right {q['rightClear']} px")
    return num, band


def yunet():
    """The face model: the saved copy in video/models/ first (cloud runs cannot download it), then the cache, then the
    download. Every copy must match the pinned sha256."""
    saved = os.path.join(ROOT, "video", "models", "face_detection_yunet_2023mar.onnx")
    if os.path.exists(saved) and sha_file(saved) == YUNET_SHA:
        return saved
    os.makedirs(MODELS, exist_ok=True)
    p = os.path.join(MODELS, "face_detection_yunet_2023mar.onnx")
    if not os.path.exists(p) or sha_file(p) != YUNET_SHA:
        urllib.request.urlretrieve(YUNET_URL, p + ".part")
        if sha_file(p + ".part") != YUNET_SHA:
            os.remove(p + ".part")
            raise RuntimeError("the YuNet model download does not match its pinned sha256")
        os.replace(p + ".part", p)
    return p


def faces_in(png, model, thr):
    import cv2
    img = cv2.imread(png)
    h, w = img.shape[:2]
    det = cv2.FaceDetectorYN.create(model, "", (w, h), thr, 0.3, 5000)
    _, faces = det.detect(img)
    return [] if faces is None else [float(f[-1]) for f in faces]


def c_faces(mp4, work):
    q = cfg()
    model = yunet()
    frames = sample_frames(mp4, q["facesPerSecond"], os.path.join(work, "faces"), scale="540:960")
    hits = []
    for f, t in frames:
        sc = faces_in(f, model, q["faceConfidence"])
        if sc:
            hits.append({"t": round(t, 2), "score": round(max(sc), 3)})
    return hits[:10], not hits, f"{len(hits)} frame(s) with a face at 0.6 or more ({len(frames)} frames checked)"


def c_file(mp4, manifest):
    v = vcfg()
    info = probe(mp4)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    probs = []
    if not vs or vs[0]["codec_name"] != "h264":
        probs.append("video is not H.264")
    elif (vs[0]["width"], vs[0]["height"]) != (v["width"], v["height"]):
        probs.append(f"{vs[0]['width']} x {vs[0]['height']}")
    elif vs[0]["r_frame_rate"] not in ("30/1", "30000/1000"):
        probs.append(f"frame rate {vs[0]['r_frame_rate']}")
    if not au or au[0]["codec_name"] != "aac":
        probs.append("audio is not AAC")
    size = int(info["format"]["size"])
    if size >= v["maxMB"] * 1e6:
        probs.append(f"{size / 1e6:.1f} MB")
    r = sh(["ffmpeg", "-v", "error", "-i", mp4, "-f", "null", "-"], timeout=900)
    if r.returncode or r.stderr.strip():
        probs.append("does not decode cleanly to the end: " + r.stderr.strip()[:120])
    digest = sha_file(mp4)
    if digest != manifest.get("sha256"):
        probs.append("sha256 does not match the manifest")
    return {"sha256": digest, "bytes": size}, not probs, "; ".join(probs) or f"opens, decodes to the end, {size / 1e6:.1f} MB, matches the manifest"


def c_layout(props):
    p = L.check(props)
    return p[:10], not p, f"{len(p)} layout problem(s) in {len(props['elements']) + len(props.get('captions', []))} boxes"


CHECKS = ["length", "loudness", "black", "frozen", "hook", "numbers", "safe-band", "faces", "file", "layout"]


def run_all(d, spec=None):
    mp4 = os.path.join(d, "video.mp4")
    manifest = json.load(open(os.path.join(d, "manifest.json"), encoding="utf-8"))
    props = json.load(open(os.path.join(d, "props.json"), encoding="utf-8"))
    work = tempfile.mkdtemp()
    results = []

    def add(name, fn):
        try:
            value, ok, detail = fn()
        except Exception as e:   # a check that could not run is a FAIL, never a pass
            value, ok, detail = None, False, f"could not run: {type(e).__name__}: {str(e)[:200]}"
        results.append({"name": name, "value": value, "pass": bool(ok), "detail": detail})

    add("length", lambda: c_length(mp4))
    add("loudness", lambda: c_loudness(mp4))
    add("black", lambda: c_black(mp4))
    add("frozen", lambda: c_frozen(mp4, props["timeline"]["endCardFrom"]))
    add("hook", lambda: c_hook(props))
    try:
        num, band = c_numbers_and_band(mp4, props, work)
        results.append({"name": "numbers", "value": num[0], "pass": bool(num[1]), "detail": num[2]})
        results.append({"name": "safe-band", "value": band[0], "pass": bool(band[1]), "detail": band[2]})
    except Exception as e:
        for n in ("numbers", "safe-band"):
            results.append({"name": n, "value": None, "pass": False, "detail": f"could not run: {type(e).__name__}: {str(e)[:200]}"})
    add("faces", lambda: c_faces(mp4, work))
    add("file", lambda: c_file(mp4, manifest))
    add("layout", lambda: c_layout(props))
    if spec:
        add("spec-match", lambda: spec_match(spec, manifest))
    shutil.rmtree(work, ignore_errors=True)
    names = {r["name"] for r in results}
    for n in CHECKS:
        if n not in names:
            results.append({"name": n, "value": None, "pass": False, "detail": "did not run"})
    qa = {"schema": "pnf.video.qa.v1", "videoId": manifest["videoId"], "mp4Sha256": sha_file(mp4), "voice": manifest.get("voice"),
          "checks": results, "pass": all(r["pass"] for r in results)}
    json.dump(qa, open(os.path.join(d, "qa.json"), "w"), indent=1)
    return qa


def spec_match(spec_path, manifest):
    s = sha_file(spec_path)
    return s, s == manifest.get("specSha256"), "the render is of this exact spec" if s == manifest.get("specSha256") else "the spec changed after the render"


# ---------------------------------------------------------------------------------------------------------------------
# The render critic's faults, re-checked in code (blueprint, Review rubrics): a fault changes nothing until confirmed.

def frame_at(mp4, t, out):
    r = sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{max(0, t):.3f}", "-i", mp4, "-frames:v", "1", out])
    if r.returncode:
        raise RuntimeError(r.stderr[-200:])
    return out


def recheck(d, kind, at=None, text=None):
    mp4 = os.path.join(d, "video.mp4")
    props = json.load(open(os.path.join(d, "props.json"), encoding="utf-8"))
    tmp = tempfile.mkdtemp()
    if kind == "hook-number":
        hook = next(e for e in props["elements"] if e["id"] == "hook-number")
        want = numbers_in(" ".join(hook["lines"]))
        got = set()
        for t in (0.0, 0.5, 1.0, 1.5, 2.0):
            for w in ocr_words(frame_at(mp4, t, os.path.join(tmp, f"h{t}.png"))):
                n = norm_num(w["text"].strip(".,;:()"))
                if n:
                    got.add((n, t))
        first = min((t for n, t in got if n in want), default=None)
        ok = first is not None and first <= 2.0
        return (not ok), f"hook number {sorted(want)} first read at {first} s (needs 2.0 s or earlier)"
    if kind == "number-readable":
        n = norm_num(text or "")
        if at is None or not n:
            raise SystemExit("number-readable needs --at and --text")
        reads = [norm_num(w["text"].strip(".,;:()")) for w in ocr_words(frame_at(mp4, at, os.path.join(tmp, "n.png"))) if w["conf"] >= 50]
        ok = n in reads
        return (not ok), f"{text} at {at:.2f} s: {'read' if ok else 'not read'} on screen"
    if kind == "overlap":
        p = L.check(props)
        if at is not None:
            p = [x for x in p]
        return bool(p), f"{len(p)} layout problem(s): {p[:3]}"
    if kind == "audio-end":
        secs = float(probe(mp4)["format"]["duration"])
        r = sh(["ffmpeg", "-hide_banner", "-nostats", "-ss", f"{secs - 0.4:.3f}", "-i", mp4, "-map", "0:a:0", "-af", "volumedetect", "-f", "null", "-"])
        m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
        tail = float(m.group(1)) if m else 0.0
        last_word = max(w["end"] for w in props["words"])
        ok = tail <= -35 and last_word <= secs - 0.8
        return (not ok), f"last 0.4 s mean {tail} dB (needs -35 or quieter); last word ends {secs - last_word:.2f} s before the end"
    raise SystemExit(f"unknown fault kind {kind}")


# ---------------------------------------------------------------------------------------------------------------------
# Planted failures: tiny synthetic clips, each built to break exactly one check.

def make_clip(path, seconds=50.0, color="0xF3F1EC", text=None, text_y=600, face=None, black=None, frozen=False, lufs=-14.0, size=72, small=False):
    """A test MP4 with moving noise (never frozen unless asked), optional drawn text, a black stretch, a face picture."""
    vf = [f"color=c={color}:s={'270x480' if small else '1080x1920'}:r=30:d={seconds}[bg]"]
    chain = "[bg]"
    if not frozen:   # a small box sliding along the bottom keeps every frame different (overlay's x can use time)
        vf.append(f"color=c=0x1D2433:s={'30x30' if small else '120x120'}:r=30:d={seconds}[box]")
        vf.append(f"{chain}[box]overlay=x='mod(t*{75 if small else 300},{225 if small else 900})':y={370 if small else 1700}[m]")
        chain = "[m]"
    if text:
        font = L.ttf_path("P", 700)
        vf.append(f"{chain}drawtext=fontfile={font}:expansion=none:text='{text}':fontsize={size}:fontcolor=0x1D2433:x=72:y={text_y}[t]")
        chain = "[t]"
    if black:
        vf.append(f"{chain}drawbox=x=0:y=0:w=1080:h=1920:color=black:t=fill:enable='between(t,{black[0]},{black[1]})'[k]")
        chain = "[k]"
    graph = ";".join(vf)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", f"sine=f=220:d={seconds}:sample_rate=48000"]
    if face:
        cmd += ["-loop", "1", "-i", face]
        graph += f";[1:v]scale=420:-1[fc];{chain}[fc]overlay=300:500[o]"
        chain = "[o]"
    cmd += ["-filter_complex", graph + f";[0:a]volume={lufs + 14 - 3:.1f}dB,aformat=channel_layouts=stereo[a]", "-map", chain, "-map", "[a]",
            "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-r", "30", "-c:a", "aac", "-t", str(seconds), path]
    r = sh(cmd, timeout=600)
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])
    return path


def planted_face(path):
    """A drawn face (no real person: shapes only) that YuNet scores well above 0.6, for the planted face test."""
    from PIL import Image, ImageDraw, ImageFilter
    im = Image.new("RGB", (600, 760), (205, 215, 225))
    d = ImageDraw.Draw(im)
    d.ellipse((90, 30, 510, 520), fill=(60, 40, 30))
    d.ellipse((130, 110, 470, 640), fill=(224, 172, 140))
    d.rectangle((250, 600, 350, 760), fill=(214, 160, 128))
    for cx in (225, 375):
        d.ellipse((cx - 55, 300, cx + 55, 350), fill=(250, 250, 250))
        d.ellipse((cx - 22, 303, cx + 22, 347), fill=(70, 50, 40))
        d.ellipse((cx - 10, 315, cx + 10, 335), fill=(10, 10, 10))
        d.line((cx - 60, 270, cx + 55, 262), fill=(50, 35, 25), width=12)
    d.polygon([(300, 340), (270, 450), (330, 450)], fill=(200, 140, 110))
    d.ellipse((265, 440, 335, 470), fill=(180, 120, 95))
    d.chord((220, 480, 380, 560), 0, 180, fill=(150, 60, 60))
    im.filter(ImageFilter.GaussianBlur(3)).save(path)
    return path


def selftest():
    bad = []
    work = tempfile.mkdtemp()

    def expect(name, ok):
        if not ok:
            bad.append(name)

    # length
    short = make_clip(os.path.join(work, "short.mp4"), seconds=20.0, small=True)
    expect("length: a 20 s cut fails", not c_length(short)[1])
    good = make_clip(os.path.join(work, "good.mp4"), seconds=50.0, small=True)
    expect("length: a 50 s cut passes", c_length(good)[1])
    # loudness: our own mix at -14 passes; a quiet one fails
    mixed = os.path.join(work, "mixed.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", good, "-af", "loudnorm=I=-14:TP=-2:LRA=11", "-c:v", "copy", "-c:a", "aac", "-ar", "48000", mixed])
    expect("loudness: -14 LUFS passes", c_loudness(mixed)[1])
    quiet = os.path.join(work, "quiet.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", good, "-af", "volume=-12dB", "-c:v", "copy", "-c:a", "aac", quiet])
    expect("loudness: a quiet mix fails", not c_loudness(quiet)[1])
    # black and frozen
    blk = make_clip(os.path.join(work, "black.mp4"), seconds=14, black=(10, 11.2), small=True)
    expect("black: a 1.2 s black stretch fails", not c_black(blk)[1])
    expect("black: our canvas is not black", c_black(good)[1])
    ink = make_clip(os.path.join(work, "ink.mp4"), seconds=6, color="0x1D2433", small=True)
    expect("black: the ink ground is not black", c_black(ink)[1])
    frz = make_clip(os.path.join(work, "frozen.mp4"), seconds=6, frozen=True, small=True)
    expect("frozen: a still video fails", not c_frozen(frz, 5.5)[1])
    expect("frozen: a moving video passes", c_frozen(good, 47.0)[1])
    expect("frozen: a still end card is allowed", c_frozen(frz, 0.0)[1])
    # hook timing, including silence planted at the start
    props = {"words": [{"seg": "hook", "start": 0.1, "end": 0.6}, {"seg": "hook", "start": 0.7, "end": 2.4}]}
    expect("hook: ends by 3.0 passes", c_hook(props)[1])
    late = {"words": [dict(w, start=w["start"] + 2.0, end=w["end"] + 2.0) for w in props["words"]]}
    expect("hook: silence at the start pushes the hook past 3.0 and fails", not c_hook(late)[1])
    # numbers on screen and the safe band: a wrong number and a caption below the band
    ok_props = {"elements": [{"id": "n", "kind": "text", "lines": ["221.4%"], "tIn": 0, "tOut": None}], "captions": []}
    right = make_clip(os.path.join(work, "num.mp4"), seconds=1, text="221.4%", size=120)
    num, band = c_numbers_and_band(right, ok_props, work)
    expect("numbers: the spec's number on screen passes", num[1])
    expect("safe band: text inside the band passes", band[1])
    wrong = make_clip(os.path.join(work, "wrong.mp4"), seconds=1, text="212.4%", size=120)
    num, _ = c_numbers_and_band(wrong, ok_props, work)
    expect("numbers: a wrong number on screen fails", not num[1])
    low = make_clip(os.path.join(work, "low.mp4"), seconds=1, text="221.4%", text_y=1400, size=120)
    _, band = c_numbers_and_band(low, ok_props, work)
    expect("safe band: a caption below y 1250 fails", not band[1])
    # faces. Only this selftest skips when the model cannot be had here (a cloud run cannot download it, Oct 29, 2026);
    # on a real video the face check still fails closed as "could not run" when the model is missing.
    try:
        yunet()
        have_model = True
    except Exception as e:
        have_model = False
        print(f"SKIP faces: the face model is not saved in video/models/ and cannot be downloaded here ({type(e).__name__}); "
              "the face check on a real video still fails closed without it")
    if have_model:
        face_png = planted_face(os.path.join(work, "face.png"))
        fc = make_clip(os.path.join(work, "face.mp4"), seconds=3, face=face_png)
        expect("faces: a face in a frame fails", not c_faces(fc, work)[1])
        expect("faces: our plain frames pass", c_faces(make_clip(os.path.join(work, "noface.mp4"), seconds=3), work)[1])
    # file
    full = make_clip(os.path.join(work, "full.mp4"), seconds=2)
    expect("file: an intact MP4 passes", c_file(full, {"sha256": sha_file(full)})[1])
    expect("file: a changed MP4 fails the fingerprint", not c_file(full, {"sha256": "0" * 64})[1])
    expect("file: the wrong frame size fails", not c_file(good, {"sha256": sha_file(good)})[1])
    broken = os.path.join(work, "broken.mp4")
    data = open(full, "rb").read()
    open(broken, "wb").write(data[: len(data) // 2])
    try:
        expect("file: a cut-off MP4 fails", not c_file(broken, {"sha256": sha_file(broken)})[1])
    except Exception:
        pass   # a file that will not even probe fails in run_all as "could not run"
    # a check that cannot run is a FAIL
    d2 = os.path.join(work, "pkg")
    os.makedirs(d2)
    shutil.copy(full, os.path.join(d2, "video.mp4"))
    json.dump({"videoId": "t", "sha256": sha_file(full)}, open(os.path.join(d2, "manifest.json"), "w"))
    json.dump({"elements": [], "captions": [], "seconds": 50, "timeline": {"endCardFrom": 47}, "words": []}, open(os.path.join(d2, "props.json"), "w"))
    qa = run_all(d2)
    hook = next(c for c in qa["checks"] if c["name"] == "hook")
    expect("a check that cannot run (no hook words) is a FAIL", not hook["pass"] and "could not run" in hook["detail"])
    expect("qa.json fails as a whole when any check fails", not qa["pass"])
    shutil.rmtree(work, ignore_errors=True)
    for b in bad:
        print("FAIL", b)
    print(f"video_qa selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (length, loudness, black, frozen, hook and silence at the "
          f"start, wrong number, safe band, {'face' if have_model else 'face SKIPPED, no model here'}, file and fingerprint, a check that cannot run)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["check", "recheck"])
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--spec"); ap.add_argument("--fault"); ap.add_argument("--at", type=float); ap.add_argument("--text")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.cmd == "check":
        qa = run_all(a.dir, a.spec)
        for c in qa["checks"]:
            print(f"{'PASS' if c['pass'] else 'FAIL'} {c['name']}: {c['detail']}")
        print(f"video QA: {'PASS' if qa['pass'] else 'FAIL'} {sum(c['pass'] for c in qa['checks'])} of {len(qa['checks'])} checks")
        sys.exit(0 if qa["pass"] else 1)
    if a.cmd == "recheck":
        confirmed, detail = recheck(a.dir, a.fault, a.at, a.text)
        print(f"{'CONFIRMED' if confirmed else 'NOT CONFIRMED'} {a.fault}: {detail}")
        sys.exit(1 if confirmed else 0)
    print(__doc__)


if __name__ == "__main__":
    main()
