#!/usr/bin/env python3
"""Studio commands (video/studio/CLAUDE.md, CONTEXT.md). One command per stage; every output is a file a person or a
fresh reviewer checks before the next stage runs.

  kit                      build _runtime/map.js (77 community areas), pixfont.js and the sounds (below)
  sound                    our own sounds, made in code: _runtime/sfx/*.wav (effects, takes, tick ladder, sting) and the
                           room loops for "music: rooms [tune]": _runtime/music/<room>.wav (classic), music/<tune>/<room>.wav
  tunes [SLUG]             the room tunes (key, tempo, chords); with a slug, the tunes its neighbours in line leave free
  new SLUG                 a video folder from _templates
  data SLUG                resolve brief.md's numbers block against the data file -> 04_scene/data.js (refuses a mismatch)
  speak SLUG [--take N ...] [--voice ID]   ask the Studio voice workflow to speak script.md (writes 01_voice/speak.json)
  ci-voice                 (the workflow) speak, join, transcribe, re-spell, pace; text to main, audio to video-renders
  estimate SLUG            stand-in word timings from script.md (marked estimate: for storyboards and looks, never posted)
  fetch SLUG               pull this video's audio from the video-renders branch
  remix SLUG               mix the sound again onto the finished render (video copied)
  mouth SLUG               lip sync from the voice: a mouth shape (0 to 3) for every frame -> 02_transcript/mouth.js
                           (stills, lint and render make it themselves when the voice is here)
  cues SLUG                match cues.md quotes to words.json -> cues.json, cues.js; prints the timing table
                           (cues.md's "music: rooms [tune] [level]" or "music: <library bed> [level]" picks the bed)
  grab SLUG                capture docs/chicago-rat-complaints/ at phone width -> 04_scene/assets/rat-page.png
  stills SLUG [--look L]   a frame at every cue -> 05_render/sheets/*.jpg and 05_render/sheet.jpg
  render SLUG [--look L] [--from S --to S] [--out F]   frames in Chromium, the mix, H.264/AAC
  check SLUG [--mp4 F]     length, loudness, black, frozen, file -> 05_render/qa.json
  lint SLUG                the layout check in code: text off the safe area, under the host, the dialog box or other text;
                           the hook rules (hook, below); captions; each lesson its own world
  hook SLUG                the opening in code: picture changes by 1 s and twice by 3 s, host on by 3 s, a 9 to 12 word
                           spoken hook said by 3.6 s; 40 to 55 s for a v2 lesson (75 s at most for v1)
  script SLUG              a v2 lesson's script in code (_shared/voice.md, Lead Clinic v2): 100 to 135 words, the drop-in
                           with no percent, source or call-out, no tail (turn, honest note, spoken asks), the button
                           echoes the hook, SCENE.sendLine set for the end card
  gatepack SLUG            timeline sheets (2 frames a second) and first frames for the fresh reviewers -> 05_render/gates/
  export SLUG              a copy under 9.5 MB for posting (two-pass H.264; Chrome uploads cap at 10 MB) -> 05_render/SLUG-post.mp4
  ready SLUG               every gate passed: queue it for posting (video/studio/queue.json, fingerprints of what the gates saw)
                           --first: ahead of every lesson still waiting; --not-before <Central time>: no earlier slot takes it
                           (Todd, live chat, Nov 8, 2026, 5:10 pm: "post tomorrow 11:37")
  hookb SLUG               the lesson's second opening (01_voice/hook-b.md, 03_cues/hook-b.md) -> videos/SLUG-hookb/,
                           the same lesson after the hook; asks the voice workflow for take 1 only (Instagram trial reels)
  hookready SLUG           SLUG-hookb passed its gates (HOOKB_GATES) and matches the queued lesson after the hook: pin it
  next                     the oldest queued lesson not yet on all four platforms, and the commit its gates passed at
                           (buffer rule: 3 a day at 6+ waiting, 2 at 3 to 5, 1 at 1 or 2; a short waits 24 h after its parent)
  missed [SLOT]            after the post log is recorded: was a post due at the last slot (or SLOT), and did one go up?
                           MISSED, INCOMPLETE, OK or TOO EARLY (the recorder tells Todd on MISSED or INCOMPLETE)
  postcaptions SLUG        the captions to paste, per platform, with any AI voice line taken out (Todd, Oct 29)
  waiting                  the queued lessons with no post yet, in posting order (the daily run's queue rule reads it)
  variety [SLUG]           no two queued lessons alike: own example, no shared hook pattern plus treatment, no two
                           in a row open on the same hook pattern (brief.md's Hook pattern, Treatment and Example lines; lint and ready run it);
                           with a slug, its tune differs from the lessons before and after it in line (cues.md music line)
  postcopy SLUG            render the queued lesson from that commit, check its fingerprints, export it to the upload folder
  posted SLUG PLATFORM URL record one live post (instagram, instagram-trial, tiktok, facebook, youtube); SLUG-hookb
                           instagram-trial records the second opening's trial reel
  trials                   Instagram trial reels not yet shared to followers (due at 72 hours), with the hook B reel
  feedshared SLUG          record that the trial reel was shared to followers (the same post, not a second one);
                           SLUG-hookb when the second opening won
  recuts                   each posted lesson's 90-day re-cut date, re-cuts done (brief.md "Re-cut of:"), numbers if read
  sendcheck SLUG           the send moment in code (Todd, Nov 7): brief.md's Send line, the end card names that person, one
                           cue marked [send] that runs 2.5 s or more and starts before half the runtime, and (after the send
                           gate) the reviewer named the same person and thing; lint adds the measured still hold
  copycheck SLUG           the proven lane's copy check (Todd, Nov 7, 12:08 pm): no 6-word run shared with the source, wording
                           not close overall, a different opening, captions too; writes 05_render/reviews/copy.json
  sourceprint URL FILE HOW hash a source's words (FILE under data/, never committed) into research/proven/<id>.json
  nextlane                 the lane the next new lesson takes in the 7-day test (proven, proven, story; config laneTest)
  selftest                 planted cases for the send, length, copy and lane checks (tools/test_video_gates.py runs it)
  status SLUG              what exists
"""
import argparse, base64, datetime as dt, difflib, glob, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VIDEOS = os.path.join(HERE, "videos")
RUNTIME = os.path.join(HERE, "_runtime")
BRANCH = "video-renders"
FPS = 30
DEFAULT_VOICE = "W3pJy9ibur1FKUihVxzY"   # Todd's own voice clone (Todd, Oct 28, 1:41 pm; _shared/voice.md)
LIBRARY_VOICE = "iP95p4xoKVk53GoZ742B"   # Chris, ElevenLabs library voice, the fallback (Todd, Oct 28, 11:51 am)
# Todd, Oct 28, 1:03 pm: "Just make me sound a bit smoother and more confident". Steadier delivery, close to his timbre.
# Eleven v4 reads only stability and similarity (ElevenLabs v4 docs: no style or speed slider). Steadier and a touch less
# clone-tight for a natural, even delivery (Todd, Oct 30, 2026, 4:01 pm: "go with your recommendation on everything").
VOICE_SETTINGS = {"W3pJy9ibur1FKUihVxzY": {"stability": 0.7, "similarity_boost": 0.7}}
MODEL = "eleven_v4"
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_192"
MAX_CHARS = 2400
sys.path.insert(0, os.path.join(ROOT, "tools"))


def vdir(slug, *p):
    return os.path.join(VIDEOS, slug, *p)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def now():
    return dt.datetime.now(dt.timezone(dt.timedelta(hours=-5))).isoformat(timespec="seconds")


def sh(cmd, check=True, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if check and r.returncode:
        raise SystemExit(f"ERROR {os.path.basename(cmd[0])}: {(r.stderr or r.stdout)[-600:]}")
    return r


def write_js(path, var, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(f"window.{var} = " + json.dumps(obj, ensure_ascii=False) + ";\n")


# ---------------------------------------------------------------------------------------------------------------------
# kit: the map and the sounds

def build_map():
    geo = json.load(open(os.path.join(ROOT, "site", "geo", "chicago-community-areas.json"), encoding="utf-8"))
    import video_layout as L
    xs, ys = [], []
    for a in geo["areas"]:
        for poly in a["polys"]:
            for ring in poly:
                for lon, lat in ring:
                    xs.append(lon); ys.append(lat)
    k = math.cos(math.radians((min(ys) + max(ys)) / 2))
    gw, gh = (max(xs) - min(xs)) * k, max(ys) - min(ys)
    s = 1000 / gw
    areas = []
    for a in geo["areas"]:
        rings, A, cx, cy = [], 0.0, 0.0, 0.0
        for poly in a["polys"]:
            for ring in poly:
                pts = [((lon - min(xs)) * k * s, (max(ys) - lat) * s) for lon, lat in ring]
                far = max(range(len(pts)), key=lambda i: (pts[i][0] - pts[0][0]) ** 2 + (pts[i][1] - pts[0][1]) ** 2)
                simp = L._simplify(pts[:far + 1], 1.2)[:-1] + L._simplify(pts[far:], 1.2)
                if len(simp) >= 3:
                    rings.append([[round(x, 1), round(y, 1)] for x, y in simp])
                for i in range(len(pts) - 1):
                    cr = pts[i][0] * pts[i + 1][1] - pts[i + 1][0] * pts[i][1]
                    A += cr; cx += (pts[i][0] + pts[i + 1][0]) * cr; cy += (pts[i][1] + pts[i + 1][1]) * cr
        areas.append({"n": a["n"], "name": a.get("name", ""), "polys": rings, "c": [round(cx / (3 * A), 1), round(cy / (3 * A), 1)] if A else [0, 0]})
    write_js(os.path.join(RUNTIME, "map.js"), "MAP", {"about": "Chicago's 77 community areas from site/geo/chicago-community-areas.json, north up, 1000 wide", "w": 1000, "h": round(gh * s, 1), "areas": areas})
    print(f"map.js: {len(areas)} areas")


def write_wav(path, y, sr):
    import numpy as np
    os.makedirs(os.path.dirname(path), exist_ok=True)
    pcm = (np.clip(y, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def synth(name, seconds, fn, sr=44100, gain_db=0.0):
    """One sound made in code, peak-normalized to 0.7 (times gain_db) -> _runtime/sfx/<name>.wav."""
    import numpy as np
    t = np.arange(int(seconds * sr)) / sr
    y = fn(t, np)
    write_wav(os.path.join(RUNTIME, "sfx", name + ".wav"), y / (np.max(np.abs(y)) + 1e-9) * 0.7 * 10 ** (gain_db / 20), sr)


# Chip voices, band-limited so they never alias into whistles: PolyBLEP pulses, additive triangles.
def _blep(ph, dt):
    import numpy as np
    out = np.zeros_like(ph)
    a = ph < dt
    x = ph[a] / dt[a]; out[a] = 2 * x - x * x - 1
    b = ph > 1 - dt
    x = (ph[b] - 1) / dt[b]; out[b] = x * x + 2 * x + 1
    return out


def pulse(f, duty, sr):
    """A pulse wave (duty 0.125, 0.25 or 0.5) following the frequency curve f (Hz, one value per sample)."""
    import numpy as np
    dt = np.minimum(f / sr, 0.49)
    ph = np.concatenate([[0.0], np.cumsum(dt)[:-1]]) % 1.0
    y = np.where(ph < duty, 1.0, -1.0) + _blep(ph, dt) - _blep((ph - duty) % 1.0, dt)
    return y - (2 * duty - 1)


def tri(f, sr, nh=12):
    """A triangle wave from its odd harmonics, each kept only below 0.45 of the sample rate."""
    import numpy as np
    ph = 2 * np.pi * np.concatenate([[0.0], np.cumsum(f / sr)[:-1]])
    y = np.zeros_like(ph)
    for i, k in enumerate(range(1, 2 * nh, 2)):
        y += np.where(k * f < 0.45 * sr, (-1) ** i * np.sin(k * ph) / (k * k), 0.0)
    return y * 8 / np.pi ** 2


def onepole(x, fc, sr, high=False):
    """A gentle 6 dB per octave filter (low-pass, or high-pass with high=True)."""
    from scipy.signal import lfilter
    import numpy as np
    a = math.exp(-2 * math.pi * fc / sr)
    lp = lfilter([1 - a], [1, -a], x)
    return x - lp if high else lp


def midi_hz(m, cents=0.0):
    return 440.0 * 2 ** ((m - 69 + cents / 100) / 12)


def build_pixfont():
    """A 1-bit pixel font for the arcade look, cut from DejaVu Sans Bold (body) and Poppins Bold (display) at small sizes
    with anti-aliasing off. Each glyph is rows of 0/1; the kit draws them as blocks."""
    from PIL import Image, ImageDraw, ImageFont
    srcs = {"body": ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10),
            "display": (os.path.join(os.path.expanduser("~"), ".cache", "pnf-video-fonts"), 15)}   # 15 px: an open s that never reads as e (design gate, Oct 28)
    import video_layout as L
    disp = L.ttf_path("P", 700)
    out = {}
    for name, (path, size) in srcs.items():
        f = ImageFont.truetype(disp if name == "display" else path, size)
        asc, desc = f.getmetrics()
        H = asc + desc
        glyphs = {}
        for c in range(32, 127):
            ch = chr(c)
            w = max(1, int(round(f.getlength(ch))))
            im = Image.new("1", (w + 4, H + 2), 0)
            d = ImageDraw.Draw(im); d.fontmode = "1"; d.text((1, 0), ch, font=f, fill=1)
            px = im.load()
            rows = ["".join("1" if px[x, y] else "0" for x in range(w + 2)) for y in range(H)]
            ink = [x for x in range(w + 2) if any(r[x] == "1" for r in rows)]
            if ink:   # trim to the ink, so every letter sits one pixel from the next (even spacing; design gate, Oct 28)
                rows = [r[ink[0]:ink[-1] + 1] for r in rows]; w = ink[-1] - ink[0] + 1
            else:     # the space: a clear word gap, about twice the letter gap plus a narrow letter
                w = 3 if name == "body" else 4; rows = ["0" * w for _ in range(H)]
            glyphs[ch] = {"w": w, "rows": rows}
        out[name] = {"h": H, "asc": asc, "glyphs": glyphs}
    write_js(os.path.join(RUNTIME, "pixfont.js"), "PIXFONT", out)
    print(f"pixfont.js: body {out['body']['h']} px, display {out['display']['h']} px")


SFX_VARIANTS = 4     # name_0 .. name_3; name.wav is name_0 (the centre: no pitch or level change)
TICK_STEPS = 13      # tick_0 .. tick_12: each one semitone above the last, for counters


def build_sfx():
    """Our sounds, made in code. Each effect gets SFX_VARIANTS takes (own noise seed, pitch within +/- 40 cents, stamps
    +/- 25, level within +/- 1.5 dB), so a sound heard twice is never the same file twice in a row. The tick is a
    ladder instead: tick_N is N semitones up."""
    import numpy as np
    sr = 44100
    env = lambda t, a, d: np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)

    def stamp(t, rng, p):   # transient + body + tail, every layer on the same first sample
        click = rng.standard_normal(len(t)) * (t < 0.002)
        click = onepole(onepole(click, 2000 * p, sr, high=True), 2000 * p, sr, high=True)
        click *= 0.5 / (np.max(np.abs(click)) + 1e-9)                                     # 2 ms click, high-passed, -6 dB
        f = 110 * p * np.maximum(2 ** (-t / 0.12), 0.5)                                    # 110 Hz falling to 55 Hz over 120 ms
        body = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.minimum(t / 0.002, 1) * np.exp(-t / 0.09)
        tail = onepole(onepole(rng.standard_normal(len(t)), 1500 * p, sr), 1500 * p, sr)   # 300 ms of low-passed noise, -15 dB
        tail *= 10 ** (-15 / 20) / (np.max(np.abs(tail)) + 1e-9) * np.exp(-t / 0.12) * np.clip(1 - t / 0.3, 0, 1)
        slap = onepole(onepole(rng.standard_normal(len(t)), 600 * p, sr, high=True), 1000 * p, sr)
        slap *= 10 ** (-12 / 20) / (np.max(np.abs(slap)) + 1e-9) * np.exp(-t / 0.012) * (t < 0.04)   # paper slap: a phone speaker hears this
        return click + body + tail + slap

    def whoosh(t, rng, p):
        n = rng.standard_normal(len(t))
        k = max(2, int(sr * 0.002 / p)); sm = np.convolve(n, np.ones(k) / k, mode="same")
        return sm * np.sin(np.pi * np.clip(t / 0.42, 0, 1)) ** 2

    makers = {
        "blip": (0.18, 40, lambda t, rng, p: np.sin(2 * np.pi * (880 + 600 * t) * p * t) * env(t, 0.004, 0.05)),
        "pop": (0.22, 40, lambda t, rng, p: np.sin(2 * np.pi * (420 + 900 * np.exp(-t * 30)) * p * t) * env(t, 0.003, 0.06)),
        "stamp": (0.45, 25, stamp),
        "chime": (1.4, 40, lambda t, rng, p: (np.sin(2 * np.pi * 784 * p * t) + 0.6 * np.sin(2 * np.pi * 1175 * p * t) + 0.3 * np.sin(2 * np.pi * 1568 * p * t)) * env(t, 0.005, 0.45)),
        "whoosh": (0.45, 40, whoosh),
        "squeak": (0.25, 40, lambda t, rng, p: np.sin(2 * np.pi * (2400 + 900 * np.sin(2 * np.pi * 9 * t)) * p * t) * env(t, 0.01, 0.07)),
    }
    for si, (name, (secs, cents, fn)) in enumerate(makers.items()):
        for k in range(SFX_VARIANTS):
            rng = np.random.default_rng(1000 * si + k)
            c, db = (0.0, 0.0) if k == 0 else (rng.uniform(-cents, cents), rng.uniform(-1.5, 1.5))
            p = 2 ** (c / 1200)
            synth(f"{name}_{k}", secs, lambda t, np, fn=fn, rng=rng, p=p: fn(t, rng, p), sr, db)
            if k == 0:
                synth(name, secs, lambda t, np, fn=fn, p=p, s=1000 * si: fn(t, np.random.default_rng(s), p), sr, db)
    tick = lambda t, rng, p: (np.sin(2 * np.pi * 2200 * p * t) * env(t, 0.001, 0.012)
                              + 0.5 * rng.standard_normal(len(t)) * (t < 0.0005))   # 0.5 ms click + 12 ms tone
    for k in range(TICK_STEPS):
        rng = np.random.default_rng(9000 + k)
        db = 0.0 if k == 0 else rng.uniform(-1.5, 1.5)
        synth(f"tick_{k}", 0.08, lambda t, np, rng=rng, k=k: tick(t, rng, 2 ** (k / 12)), sr, db)
        if k == 0:
            synth("tick", 0.08, lambda t, np: tick(t, np.random.default_rng(9000), 1.0), sr)
    print(f"sfx: {' '.join(makers)} ({SFX_VARIANTS} takes each), tick_0..tick_{TICK_STEPS - 1} (a rising ladder)")
    build_sting()


def chip_note(kind, midi, dur, sr, duty=0.25, cents=0.0, a=0.005, d=0.12, s=0.6, r=0.04, vib=False):
    """One chip note: a pulse or triangle, attack a, decay to s over d, held for dur, released over r. vib: 5.5 Hz,
    +/- 20 cents, fading in from 150 ms."""
    import numpy as np
    n = int((dur + r) * sr)
    t = np.arange(n) / sr
    f = np.full(n, midi_hz(midi, cents))
    if vib:
        f *= 2 ** (20 / 1200 * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - 0.15) / 0.1, 0, 1))
    y = pulse(f, duty, sr) if kind == "pulse" else tri(f, sr)
    e = np.where(t < a, t / a, np.maximum(s, 1 - (1 - s) * (t - a) / d))
    e *= np.clip(1 - (t - dur) / r, 0, 1)
    return y * e


def build_sting():
    """The brand sting: E5, G5, C6 (200, 200, 600 ms) on a soft 25% pulse with a triangle an octave down; the last note
    has vibrato and an echo (300 ms later, -9 dB, +7 cents). Always the same file: it is a logo."""
    import numpy as np
    sr = 44100
    y = np.zeros(int(1.75 * sr))
    def put(at, sig, g):
        i = int(at * sr); y[i:i + len(sig)] += g * sig[:len(y) - i]
    for at, dur, m, last in [(0.0, 0.2, 76, False), (0.2, 0.2, 79, False), (0.4, 0.6, 84, True)]:
        r = 0.25 if last else 0.03
        for echo, g, c in ([(0.0, 1.0, 0.0), (0.3, 10 ** (-9 / 20), 7.0)] if last else [(0.0, 1.0, 0.0)]):
            put(at + echo, chip_note("pulse", m, dur, sr, 0.25, c, r=r, vib=last), 0.5 * g)
            put(at + echo, chip_note("tri", m - 12, dur, sr, cents=c, r=r, vib=last), 0.45 * g)
    y = onepole(onepole(y, 4500, sr), 4500, sr)   # soft: no fizz on top
    write_wav(os.path.join(RUNTIME, "sfx", "sting.wav"), y / np.max(np.abs(y)) * 0.7, sr)
    print("sfx: sting (E5 G5 C6)")


# Room loops: 8 bars of one tune, so any room can cross into any other on the beat. "classic" is the first tune (A minor,
# 96 BPM, 20.0 s a loop) and keeps its files at _runtime/music/<room>.wav, so every cue file that says plain "music: rooms"
# and every pinned lesson plays exactly what it played before.
BPM, LOOP_BARS = 96, 8
BEAT = 60 / BPM
ROOMS = ("framing", "blackboard", "workshop", "garage")
CHORDS = [  # per bar: triad (around the octave below middle C), bass root
    ([57, 60, 64], 45), ([53, 57, 60], 41), ([55, 60, 64], 48), ([55, 59, 62], 43),   # Am  F  C  G
    ([57, 60, 64], 45), ([53, 57, 60], 41), ([57, 62, 65], 38), ([56, 59, 64], 40)]   # Am  F  Dm E (back to Am)
LEAD = [(0, 1.5, 72), (1.5, 0.5, 71), (2, 2, 69), (8, 1, 67), (9, 1, 72), (10, 2, 76),   # (beat, beats, note): call and
        (16, 1.5, 76), (17.5, 0.5, 74), (18, 2, 72), (24, 1, 69), (25, 1, 72), (26, 2, 74), (28, 2, 71), (30, 2, 68)]   # rest

NOTE_PC = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def chord(name):
    """'Am', 'Bb', 'C' -> (triad, bass root): each chord tone at its first note from F3 (53) up, the root from D2 (38) up
    (the classic tune's voicings, bar for bar, except its Dm)."""
    m = re.match(r"([A-G])(b|#)?(m?)$", name)
    pc = (NOTE_PC[m.group(1)] + {"b": -1, "#": 1, None: 0}[m.group(2)]) % 12
    up = lambda q, lo: lo + (q - lo) % 12
    return sorted(up((pc + i) % 12, 53) for i in (0, 3 if m.group(3) else 4, 7)), up(pc, 38)


# Tunes for "music: rooms <tune>" (Todd, Oct 29, 2026, 8:11 pm: "can we vary the retro video game music ... it's just
# different tunes for each video"). Every one is ours, composed here: its own key, tempo, 8-bar progression and lead,
# played by the four room grooves. No neighbour in the posting line plays the same tune (anim.py variety).
# The brand sting (E5 G5 C6) lands on whatever bar is playing when the close comes (bars 1 to 8 all occur in our
# lessons), so every new tune keeps C, E and G natural in every chord and lead note (no C#, D#, F# or G#): under any bar
# the sting is a chord tone or a colour note, never a half step off one. classic's bar 8 (E major, G#) and its last lead
# note (G#4) are the one exception, kept as they were (sting_rubs).
# Each tune: key, bpm, chord names, lead (beat, beats, note), swing (beats added to every off-beat eighth), arp (blackboard:
# the order it walks the triad, 3 = the root an octave up) and arp_rate (notes a beat), riff (garage bass, semitones over
# each bar's root, 8 a bar), kicks (garage), plucks (framing: (beat, tone)), stabs (workshop chord stabs), lead_duty
# (None: each room's own).
TUNES = {
    "classic": {"key": "A minor", "bpm": 96, "names": "Am F C G Am F Dm E", "chords": CHORDS, "lead": LEAD, "swing": 0,
                "arp": (0, 1, 2, 3), "arp_rate": 4, "riff": (0, 0, 12, 0, 7, 0, 12, 7), "kicks": (0, 2, 2.5),
                "plucks": ((1, 2), (2.5, 1), (3.5, 3)), "stabs": (0.5, 1.5, 2.5, 3.5), "lead_duty": None},
    "sunny": {"key": "C major", "bpm": 120, "names": "C Am F G C Am Dm G", "swing": 0,
              "lead": [(0, 0.5, 72), (0.5, 0.5, 76), (1, 1, 79), (2, 2, 76), (6, 1, 72), (7, 1, 74),
                       (8, 1.5, 77), (9.5, 0.5, 76), (10, 2, 72), (12, 1, 71), (13, 1, 74), (14, 2, 79),
                       (16, 0.5, 72), (16.5, 0.5, 76), (17, 1, 79), (18, 1, 81), (19, 1, 79), (20, 2, 76), (22, 2, 72),
                       (24, 1, 74), (25, 1, 77), (26, 2, 81), (28, 1, 79), (29, 1, 74), (30, 2, 71)],
              "arp": (0, 2, 1, 3), "arp_rate": 4, "riff": (0, 12, 0, 12, 7, 12, 0, 12), "kicks": (0, 2),
              "plucks": ((1, 1), (2, 2), (3, 3)), "stabs": (0.5, 1.5, 2.5, 3.5), "lead_duty": None},
    "quest": {"key": "D minor", "bpm": 108, "names": "Dm Bb F C Dm Bb Gm C", "swing": 0,
              "lead": [(0, 1.5, 74), (1.5, 0.5, 76), (2, 2, 77), (4, 1, 77), (5, 1, 74), (6, 2, 70),
                       (8, 1.5, 72), (9.5, 0.5, 74), (10, 2, 69), (12, 3, 67),
                       (16, 1.5, 74), (17.5, 0.5, 76), (18, 1, 77), (19, 1, 81), (20, 2, 82), (22, 1, 81), (23, 1, 77),
                       (24, 2, 79), (26, 1, 77), (27, 1, 74), (28, 2, 76), (30, 2, 72)],
              "arp": (0, 1, 2, 3, 2, 1), "arp_rate": 4, "riff": (0, 7, 12, 7, 0, 7, 12, 7), "kicks": (0, 1.5, 2),
              "plucks": ((1, 2), (2, 1), (3, 3)), "stabs": (0, 1.5, 3), "lead_duty": 0.5},
    "night": {"key": "E minor (Phrygian)", "bpm": 88, "names": "Em F Em Dm Am G F Em", "swing": 0,
              "lead": [(0, 2, 76), (2, 1, 79), (3, 1, 77), (4, 2, 77), (6, 2, 72), (8, 2, 71), (10, 1, 74), (11, 1, 76),
                       (12, 3, 77), (16, 2, 76), (18, 1, 72), (19, 1, 69), (20, 2, 71), (22, 2, 74),
                       (24, 1.5, 72), (25.5, 0.5, 74), (26, 2, 77), (28, 4, 76)],
              "arp": (3, 2, 1, 0), "arp_rate": 2, "riff": (0, 0, 7, 0, 12, 0, 7, 12), "kicks": (0, 2.5),
              "plucks": ((1.5, 2), (3, 3)), "stabs": (1, 3), "lead_duty": 0.5},
    "chase": {"key": "F major", "bpm": 132, "names": "F C Dm Bb F C Bb C", "swing": 0,
              "lead": [(0, 0.5, 77), (0.5, 0.5, 81), (1, 0.5, 84), (1.5, 0.5, 81), (2, 1, 77), (3, 1, 72),
                       (4, 1, 76), (5, 1, 79), (6, 2, 72), (8, 0.5, 74), (8.5, 0.5, 77), (9, 0.5, 81), (9.5, 0.5, 77),
                       (10, 2, 74), (12, 1, 70), (13, 1, 74), (14, 2, 77),
                       (16, 0.5, 77), (16.5, 0.5, 81), (17, 0.5, 84), (17.5, 0.5, 81), (18, 1, 77), (19, 1, 72),
                       (20, 1, 76), (21, 1, 79), (22, 2, 84), (24, 1, 82), (25, 1, 77), (26, 2, 74),
                       (28, 1, 76), (29, 1, 79), (30, 1, 72), (31, 1, 76)],
              "arp": (0, 1, 2, 3), "arp_rate": 4, "riff": (0, 12, 0, 12, 0, 12, 7, 12), "kicks": (0, 1, 2, 3),
              "plucks": ((0.5, 2), (1.5, 1), (2.5, 2), (3.5, 3)), "stabs": (0.5, 1.5, 2.5, 3.5), "lead_duty": 0.125},
    "bounce": {"key": "G Mixolydian", "bpm": 112, "names": "G F C G Am C F G", "swing": 1 / 6,
               "lead": [(0, 0.5, 74), (0.5, 1, 79), (1.5, 0.5, 77), (2, 1, 74), (3, 1, 71), (5, 0.5, 72), (5.5, 0.5, 74),
                        (6, 2, 77), (8, 1, 76), (9, 0.5, 79), (9.5, 0.5, 76), (10, 2, 72), (13, 1, 71), (14, 2, 74),
                        (16, 1, 76), (17, 0.5, 72), (17.5, 0.5, 76), (18, 2, 81), (20, 1, 79), (21, 1, 76), (22, 2, 72),
                        (24, 1, 77), (25, 0.5, 81), (25.5, 0.5, 77), (26, 2, 72), (28, 1, 74), (29, 1, 71), (30, 2, 67)],
               "arp": (0, 1, 2), "arp_rate": 3, "riff": (0, 0, 7, 12, 0, 0, 7, 12), "kicks": (0, 2, 3.5),
               "plucks": ((0.5, 2), (1.5, 1), (2.5, 2), (3.5, 3)), "stabs": (0.5, 1.5, 2.5, 3.5), "lead_duty": None},
}
for _t in TUNES.values():
    _t.setdefault("chords", [chord(n) for n in _t["names"].split()])
DEFAULT_TUNE = "classic"


def tune_beat(tune):
    return 60 / TUNES[tune]["bpm"]


def tune_path(tune, room):
    """classic keeps its first files (_runtime/music/<room>.wav); every other tune has its own folder."""
    return os.path.join(RUNTIME, "music", *(() if tune == DEFAULT_TUNE else (tune,)), room + ".wav")


def sting_rubs(tune):
    """Where the sting (E5 G5 C6) would rub: bars whose chord, and lead notes whose pitch, sit a half step off one of its
    notes from outside the C major scale (C#, D#, F#, G#). Returns ([bar numbers], [lead beats])."""
    t, bad = TUNES[tune], (1, 3, 6, 8)
    bars = [i + 1 for i, (triad, root) in enumerate(t["chords"]) if any(n % 12 in bad for n in list(triad) + [root])]
    return bars, [b for b, _, m in t["lead"] if m % 12 in bad]


def build_music(only=None):
    """Each tune's four chiptune loops, one per room, synthesized band-limited at 44.1 kHz and written as mono 22.05 kHz
    16-bit wav (under 1 MB each) to tune_path(). In one tune every room plays the same key, tempo, chords and quiet square
    lead; the rooms differ in what plays under it (the tune sets each part's pattern):
      framing     half-time: triangle bass on 1 and 3, sparse 25% plucks, a soft snare on 3, hats on 2 and 4
      blackboard  12.5% pulse arpeggios (sixteenths, triplets or eighths), triangle bass on every beat, light eighth hats
      workshop    25% chord stabs, eighth hats with an open hat, bouncing triangle bass, kick on 1 and 3
      garage      50% pulse bass riff, triangle kick slides, noise snare on 2 and 4, eighth hats
    classic is the tune the studio played first and comes out byte for byte as it always has."""
    import numpy as np
    from scipy.signal import resample_poly
    sr = 44100
    for ti, (name, tn) in enumerate(TUNES.items()):
        if only and name not in only:
            continue
        BEAT = 60 / tn["bpm"]   # this tune's beat (the module BEAT is classic's)
        swing = tn["swing"]
        sw = (lambda b: b + swing if abs(b % 1 - 0.5) < 1e-9 else b) if swing else (lambda b: b)   # off-beat eighths late
        L = int(round(LOOP_BARS * 4 * BEAT * sr))
        for ri, room in enumerate(ROOMS):
            rng = np.random.default_rng(500 + ri + 100 * ti)
            y = np.zeros(L + 2 * sr)

            def put(beat, sig, g):
                i = int(round(sw(beat) * BEAT * sr)); y[i:i + len(sig)] += g * sig

            def noise(dur, fc, decay, high=True):
                n = int(dur * sr); t = np.arange(n) / sr
                return onepole(rng.standard_normal(n), fc, sr, high=high) * np.exp(-t / decay)

            def kick():
                n = int(0.16 * sr); t = np.arange(n) / sr
                return tri(150 * (50 / 150) ** np.clip(t / 0.08, 0, 1), sr) * np.exp(-t / 0.07)

            for bar, (triad, root) in enumerate(tn["chords"]):
                b0 = bar * 4
                tones = [triad[0], triad[1], triad[2], triad[0] + 12]
                if room == "framing":
                    for k in (0, 2):
                        put(b0 + k, chip_note("tri", root if k == 0 else root + 7, 1.8 * BEAT, sr, s=0.8, r=0.08), 0.42)
                    for k, j in tn["plucks"]:
                        put(b0 + k, chip_note("pulse", tones[j], 0.09, sr, 0.25, d=0.06, s=0.3, r=0.12), 0.16)
                    put(b0 + 2, noise(0.12, 900, 0.035), 0.10)
                    for k in (1, 3):
                        put(b0 + k, noise(0.03, 6000, 0.008), 0.07)
                    put(b0, kick(), 0.30)
                elif room == "blackboard":
                    arp, rate = [tones[j] for j in tn["arp"]], tn["arp_rate"]
                    for k in range(4 * rate):
                        put(b0 + k / rate, chip_note("pulse", arp[k % len(arp)], 0.13, sr, 0.125, d=0.08, s=0.4, r=0.02), 0.11)
                    for k in range(4):
                        put(b0 + k, chip_note("tri", root, 0.9 * BEAT, sr, s=0.8, r=0.05), 0.40)
                    for k in range(8):
                        put(b0 + k / 2, noise(0.03, 7000, 0.006), 0.045 if k % 2 else 0.06)
                elif room == "workshop":
                    for k in tn["stabs"]:
                        for m in triad:
                            put(b0 + k, chip_note("pulse", m, 0.11, sr, 0.25, d=0.08, s=0.4, r=0.03), 0.07)
                    for k in range(8):
                        put(b0 + k / 2, chip_note("tri", root + (12 if k % 2 else 0), 0.42 * BEAT, sr, s=0.8, r=0.03), 0.36)
                        put(b0 + k / 2, noise(0.12 if k == 7 else 0.03, 7000, 0.04 if k == 7 else 0.007), 0.06)
                    for k in (0, 2):
                        put(b0 + k, kick(), 0.35)
                else:   # garage
                    riff = tn["riff"]
                    for k in range(8):
                        put(b0 + k / 2, onepole(chip_note("pulse", root + riff[k], 0.4 * BEAT, sr, 0.5, d=0.1, s=0.5, r=0.03), 1800, sr), 0.16)
                    for k in tn["kicks"]:
                        put(b0 + k, kick(), 0.45)
                    for k in (1, 3):   # the snare kept under 3 kHz, out of the voice's consonants
                        put(b0 + k, onepole(onepole(noise(0.12, 600, 0.04), 2500, sr), 2500, sr), 0.30)
                    for k in range(8):
                        put(b0 + k / 2, noise(0.03, 7000, 0.007), 0.05)
            lead_duty, lead_g = {"framing": (0.5, 0.06), "blackboard": (0.25, 0.06), "workshop": (0.25, 0.06), "garage": (0.25, 0.036)}[room]
            lead_duty = tn["lead_duty"] or lead_duty
            for beat, beats, m in tn["lead"]:   # quiet (about 16 dB under the rest), with an echo 1/8 later at -9 dB, +7 cents
                dur = beats * BEAT * 0.92
                for at, g, c in ((0, 1.0, 0.0), (0.5, 10 ** (-9 / 20), 7.0)):
                    put(beat + at, chip_note("pulse", m, dur, sr, lead_duty, c, d=0.12, s=0.6, r=0.06, vib=beats >= 1), lead_g * g)
            y[:len(y) - L] += y[L:]          # what rings past the end comes back in at the start: a seamless loop
            y = onepole(y[:L], 20, sr, high=True)
            y = resample_poly(y, 1, 2)       # to 22.05 kHz, through resample_poly's anti-alias filter
            y *= 0.12 / np.sqrt(np.mean(y ** 2))   # the same RMS in every room and tune, so a crossfade never jumps
            if np.max(np.abs(y)) > 0.95:
                y *= 0.95 / np.max(np.abs(y))
            write_wav(tune_path(name, room), y, sr // 2)
        bars, notes = sting_rubs(name)
        rub = "the sting fits every bar" if not bars and not notes else f"the sting rubs on bar {', '.join(map(str, bars))}" + (f" and the lead at beat {', '.join(f'{b:g}' for b in notes)}" if notes else "")
        print(f"music: {name}: {' '.join(ROOMS)} ({LOOP_BARS} bars at {tn['bpm']} BPM, {tn['key']}, {tn['names']}, {LOOP_BARS * 4 * BEAT:.1f} s each; {rub})")


# ---------------------------------------------------------------------------------------------------------------------
# brief numbers -> data.js (every number on screen comes from here)

def resolve(doc, path):
    cur = doc
    for part in re.findall(r"[^.\[\]]+(?:\[[^\]]+\])?", path):
        m = re.match(r"([^\[]+)(?:\[(\w+)=([^\]]+)\])?$", part)
        key, fk, fv = m.groups()
        cur = cur[int(key)] if isinstance(cur, list) and key.isdigit() else cur[key]
        if fk:
            cur = next(x for x in cur if str(x.get(fk)) == fv)
    return cur


def fmt_shown(v, shown):
    """The shown text must be the value as the file has it (a whole number, or one decimal as stored)."""
    digits = re.sub(r"[^\d.\-]", "", shown.replace(",", ""))
    try:
        return float(digits) == float(v)
    except ValueError:
        return False


def brief_block(slug):
    txt = open(vdir(slug, "01_voice", "brief.md"), encoding="utf-8").read()
    m = re.search(r"```json\s+numbers\s*\n(.*?)```", txt, re.S)
    if not m:
        raise SystemExit("ERROR data: brief.md has no ```json numbers block")
    return json.loads(m.group(1))


def cmd_data(slug):
    b = brief_block(slug)
    path = os.path.join(ROOT, b["file"])
    doc = json.load(open(path, encoding="utf-8"))
    commit = sh(["git", "-C", ROOT, "log", "-1", "--format=%h", "--", b["file"]], check=False).stdout.strip()
    out, bad = {}, []
    for key, spec in b["numbers"].items():
        v = resolve(doc, spec["path"])
        if not fmt_shown(v, spec["shown"]):
            bad.append(f"{key}: file has {v}, brief shows {spec['shown']}")
        out[key] = {"value": v, "shown": spec["shown"], "path": spec["path"]}
    if bad:
        raise SystemExit("ERROR data: " + "; ".join(bad))
    extra = {k: resolve(doc, p) for k, p in (b.get("pull") or {}).items()}
    write_js(vdir(slug, "04_scene", "data.js"), "DATA", {"file": b["file"], "commit": commit, "sha256": sha(path), "numbers": out, "pull": extra})
    print(f"data.js: {len(out)} numbers from {b['file']} at {commit}, every shown value matches the file")


# ---------------------------------------------------------------------------------------------------------------------
# script -> takes, words

TAG = re.compile(r"\[[^\]]*\]")
SOFT_TAG = re.compile(r"(?i)lean|whisper|soft|breath|quiet|hush|intimate|murmur|close to|aside")
_NW = "one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety"
ABOUT_EXACT = re.compile(rf"(?i)\babout\s+(?:(?:{_NW})\s+(?:{_NW})(?:-(?:{_NW}))?\b|(?:twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)-(?:one|two|three|four|five|six|seven|eight|nine)\b|\w+ point \w+)")


def takes_of(slug):
    txt = open(vdir(slug, "01_voice", "script.md"), encoding="utf-8").read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip() and not p.strip().startswith("#")]
    return [" ".join(p.split()) for p in paras]


def spoken_words(take):
    return [w for w in TAG.sub(" ", take).split() if re.search(r"\w", w)]


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


ACRONYMS = {"HVAC", "ACHR", "BLS", "ACCA", "AI", "CRM", "ROI", "FAQ", "DIY", "LLC", "IRS", "CPA", "HOA", "GC"}   # stay in caps on screen (Oct 28: "achr" in a bubble)


def display(w):
    core = re.sub(r"[^A-Za-z]", "", w)
    if core in ACRONYMS:
        return w
    return w.lower() if len(w) > 1 and w.isupper() and w.isalpha() else w   # a stressed word in caps reads normally on screen


def cmd_estimate(slug):
    takes = takes_of(slug)
    t, words, tk = 0.15, [], []
    for i, tx in enumerate(takes):
        t0 = t
        for w in spoken_words(tx):
            d = 0.11 + 0.042 * len(w)
            words.append({"w": display(w), "start": round(t, 3), "end": round(t + d, 3), "take": i + 1})
            t += d + 0.05 + (0.22 if re.search(r"[.!?]$", w) else (0.1 if w.endswith(",") else 0))
        tk.append({"n": i + 1, "start": round(t0, 3), "end": round(t, 3)})
        t += 0.35
    doc = {"schema": "pnf.studio.words.v1", "source": "estimate", "about": "Stand-in timings from script.md; never rendered for posting.",
           "words": words, "takes": tk, "end": round(words[-1]["end"], 3)}
    os.makedirs(vdir(slug, "02_transcript"), exist_ok=True)
    json.dump(doc, open(vdir(slug, "02_transcript", "words.json"), "w"), indent=1)
    write_js(vdir(slug, "02_transcript", "words.js"), "WORDS", doc)
    print(f"words.json (estimate): {len(words)} words, {doc['end']:.1f} s")


# ---------------------------------------------------------------------------------------------------------------------
# voice (request locally, run in the Studio voice workflow)

def cmd_speak(slug, takes=None, voice=None):
    tk = takes_of(slug)
    chars = sum(len(t) for t in tk)
    if chars > MAX_CHARS:
        raise SystemExit(f"ERROR speak: {chars} characters (limit {MAX_CHARS}); shorten the script")
    v = voice or DEFAULT_VOICE
    req = {"schema": "pnf.studio.speak.v1", "voice": v, "model": MODEL, "takes": takes or "all", "settings": VOICE_SETTINGS.get(v),
           "scriptSha256": sha(vdir(slug, "01_voice", "script.md")), "requestedAt": now()}
    json.dump(req, open(vdir(slug, "01_voice", "speak.json"), "w"), indent=1)
    print(f"speak.json: {len(tk)} takes, {chars} characters, voice {req['voice']}; push it to run the Studio voice workflow")


def eleven(text, prev, nxt, voice, key, settings=None):
    body = {"text": text, "model_id": MODEL}
    if settings:
        body["voice_settings"] = settings
    if prev:
        body["previous_text"] = prev
    if nxt:
        body["next_text"] = nxt
    req = urllib.request.Request(API.format(voice=voice), data=json.dumps(body).encode(), method="POST",
                                 headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            msg = e.read()[:300].decode("utf-8", "replace").replace(key, "<key>")
            if e.code == 400 and settings and "setting" in msg.lower():   # the model refused a setting: speak without them
                print("WARN speak: voice settings refused, speaking with the voice's own settings")
                return eleven(text, prev, nxt, voice, key, None)
            if e.code < 500 or attempt:
                raise SystemExit(f"ERROR speak: ElevenLabs answered {e.code}: {msg}")
        except Exception as e:
            if attempt:
                raise SystemExit(f"ERROR speak: ElevenLabs did not answer ({type(e).__name__})")
        time.sleep(4)


def seconds_of(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


_WHISPER = {}


def transcribe(audio, model="medium.en", offset=0.0):
    from faster_whisper import WhisperModel
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = _WHISPER.get(model) or _WHISPER.setdefault(model, WhisperModel(model, device="cpu", compute_type="int8"))
    segs, _ = m.transcribe(np.frombuffer(pcm, dtype=np.float32), language="en", word_timestamps=True, beam_size=5, vad_filter=False)
    return [{"w": w.word.strip(), "start": round(w.start + offset, 3), "end": round(w.end + offset, 3), "p": round(w.probability, 3)} for s in segs for w in (s.words or [])]


ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def num_words(n):
    """1667 -> one thousand six hundred sixty seven (how a number is said)."""
    if n < 20: return [ONES[n]]
    if n < 100: return [TENS[n // 10]] + (num_words(n % 10) if n % 10 else [])
    for size, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand"), (100, "hundred")):
        if n >= size:
            return num_words(n // size) + [name] + (num_words(n % size) if n % size else [])


def say_heard(heard):
    """Whisper writes numbers as digits ("$1,000.", "25%"); say them as words so they line up with the script.
    Each spoken word keeps a share of the token's time and remembers it came from a number."""
    out, merged = [], []
    for h in heard:   # "$1" ",000." is one number
        if merged and re.match(r"^,\d", h["w"].strip()) and re.search(r"\d$", merged[-1]["w"].strip()):
            merged[-1] = dict(merged[-1], w=merged[-1]["w"].strip() + h["w"].strip(), end=h["end"])
        else:
            merged.append(h)
    for h in merged:
        raw = h["w"].strip()
        m = re.fullmatch(r"([$]?)(\d[\d,]*)?(?:\.(\d+))?(%?)([.,!?]?)", raw)
        if not m or not (m.group(2) or m.group(3)) or len((m.group(2) or "").replace(",", "")) > 12:
            out.append(dict(h, num=bool(re.search(r"\d", raw)) or raw in ("$", "%"))); continue
        ws = num_words(int(m.group(2).replace(",", ""))) if m.group(2) else []   # ".12" is said "point one two"
        if m.group(3): ws += ["point"] + [ONES[int(c)] for c in m.group(3)]
        if m.group(4): ws.append("percent")
        if m.group(1): ws.append("dollars")
        n = len(ws)
        for i, w in enumerate(ws):
            s0 = h["start"] + (h["end"] - h["start"]) * i / n
            out.append({"w": w, "start": round(s0, 3), "end": round(h["start"] + (h["end"] - h["start"]) * (i + 1) / n, 3), "num": True})
    return out


def write_words(slug, req, info, heard, takes):
    """Script words with Whisper's times: words.json, words.js, transcript.md (flags and pace per take). Returns (doc, pace)."""
    script_words, take_of = [], []
    for i, t in enumerate(takes):
        ws = spoken_words(t)
        script_words += ws; take_of += [i + 1] * len(ws)
    times, flags = respell(script_words, heard)
    words = [{"w": display(w), "start": s, "end": e, "take": take_of[i]} for i, (w, (s, e)) in enumerate(zip(script_words, times))]
    pace = []
    for x in info:
        n = sum(1 for w in words if w["take"] == x["n"])
        wpm = round(n / max(0.1, x["seconds"]) * 60)
        x["wpm"] = wpm
        note = "slow: rewrite it as talk, then speak --take %d" % x["n"] if wpm < 150 else ("fast: give it a landing beat, then speak --take %d" % x["n"] if wpm > 200 else "")
        pace.append(f"  {x['n']:02d}  {x['start']:6.1f} s  {wpm} wpm  {note}")
    doc = {"schema": "pnf.studio.words.v1", "source": "whisper medium.en int8, re-spelled from script.md", "voice": req["voice"], "model": req["model"],
           "words": words, "takes": [{k: x[k] for k in ("n", "start", "end", "wpm")} for x in info], "flags": flags, "end": round(words[-1]["end"], 3),
           "heard": heard}
    os.makedirs(vdir(slug, "02_transcript"), exist_ok=True)
    json.dump(doc, open(vdir(slug, "02_transcript", "words.json"), "w"), indent=1)
    write_js(vdir(slug, "02_transcript", "words.js"), "WORDS", {k: doc[k] for k in ("words", "takes", "end", "source")})
    lines, cur, ct = [], [], None
    for w in words:
        if not cur:
            ct = w["start"]
        cur.append(w["w"])
        if re.search(r"[.!?]$", w["w"]):
            lines.append(f"`{int(ct // 60):02d}:{ct % 60:04.1f}` " + " ".join(cur)); cur = []
    if cur:
        lines.append(f"`{int(ct // 60):02d}:{ct % 60:04.1f}` " + " ".join(cur))
    open(vdir(slug, "02_transcript", "transcript.md"), "w").write(
        f"# Transcript: {slug}\n\nVoice {req['voice']} ({req['model']}), {len(words)} words, {doc['end']:.1f} s of voice.\n\n"
        + ("## Flags\n" + "\n".join(f"- {f}" for f in flags) + "\n\n" if flags else "## Flags\nnone\n\n")
        + "## Pace per take (target 160 to 195 wpm)\n```\n" + "\n".join(pace) + "\n```\n\n## Words\n\n" + "\n\n".join(lines) + "\n")
    return doc, pace


def respell(script_words, heard):
    """Script words win; Whisper gives the times. Returns (words, flags)."""
    heard = say_heard(heard)
    a = [norm(w) for w in script_words]
    b = [norm(h["w"]) for h in heard]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    out, flags = [None] * len(script_words), []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                out[i1 + k] = (heard[j1 + k]["start"], heard[j1 + k]["end"])
        elif tag == "replace":
            span = (heard[j1]["start"], heard[j2 - 1]["end"])
            n = i2 - i1
            for k in range(n):   # spread the heard span over the script words ("forty-five" heard as "45")
                out[i1 + k] = (round(span[0] + (span[1] - span[0]) * k / n, 3), round(span[0] + (span[1] - span[0]) * (k + 1) / n, 3))
            same = norm("".join(script_words[i1:i2])) == norm("".join(h["w"] for h in heard[j1:j2]))   # "auto-reply" heard as "auto reply"
            numeric = all(heard[j].get("num") or not norm(heard[j]["w"]) for j in range(j1, j2))   # "a thousand" heard as "$1,000", "twenty-five percent" as "25 %"
            # a proper name Whisper cannot spell ("ServiceTitan" heard as "service tightens", "Invoca" as "and Voca"):
            # a capitalized name inside the phrase and a close spelling of the whole phrase count as heard
            name = any(re.match(r"[A-Z]", w) for w in script_words[i1:i2][1 if i1 == 0 or re.search(r"[.!?]$", script_words[i1 - 1]) else 0:]) or \
                any(re.search(r"[a-z][A-Z]", w) for w in script_words[i1:i2])
            close = difflib.SequenceMatcher(a=norm("".join(script_words[i1:i2])), b=norm("".join(h["w"] for h in heard[j1:j2]))).ratio() >= 0.75
            if not (same or numeric or (name and close)):
                flags.append(f"{heard[j1]['start']:.1f} s heard '{' '.join(h['w'] for h in heard[j1:j2])}' for '{' '.join(script_words[i1:i2])}'")
        elif tag == "delete":
            flags.append(f"dropped '{' '.join(script_words[i1:i2])}': not heard")
        elif tag == "insert" and not all(heard[j].get("num") for j in range(j1, j2)):   # "a hundred" written "100" says "one" too
            flags.append(f"{heard[j1]['start']:.1f} s added '{' '.join(h['w'] for h in heard[j1:j2])}': not in the script")
    last = 0.0
    for i, v in enumerate(out):   # a dropped word sits at the previous word's end, zero length
        if v is None:
            out[i] = (last, last)
        last = out[i][1]
    # a dash Whisper hears is quoted into the flag; spell it so the transcript passes the em dash check (Nov 7)
    flags = [f.replace("—", "(dash)").replace("–", "(dash)") for f in flags]
    return out, flags


def credits(key):
    """ElevenLabs characters used and left this period (numbers only; the key is never written)."""
    try:
        req = urllib.request.Request("https://api.elevenlabs.io/v1/user/subscription", headers={"xi-api-key": key})
        with urllib.request.urlopen(req, timeout=30) as r:
            d = json.load(r)
        return {"used": d.get("character_count"), "limit": d.get("character_limit"), "tier": d.get("tier"),
                "resetsAt": d.get("next_character_count_reset_unix")}
    except Exception as e:
        return {"error": type(e).__name__}


def cmd_ci_voice():
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    work = tempfile.mkdtemp()
    done = []
    for req_path in sorted(glob.glob(os.path.join(VIDEOS, "*", "01_voice", "speak.json"))):
        slug = req_path.split(os.sep)[-3]
        req = json.load(open(req_path))
        tk_path = vdir(slug, "01_voice", "takes.json")
        prev = json.load(open(tk_path)) if os.path.exists(tk_path) else {}
        if prev.get("requestedAt") == req["requestedAt"]:
            continue
        if not key:
            raise SystemExit("ERROR speak: ELEVENLABS_API_KEY is not set as a repo secret")
        takes = takes_of(slug)
        out = os.path.join(work, slug)
        os.makedirs(os.path.join(out, "takes"), exist_ok=True)
        old = os.path.join(work, "old")
        if req["takes"] != "all":   # keep the other takes from the renders branch
            sh(["git", "-C", ROOT, "fetch", "--depth", "1", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}"])
            os.makedirs(old, exist_ok=True)
            prev12 = prev.get("voiceSha256", "")[:12]   # the takes of the voice main has now (its voices/ copy first)
            src = req.get("takesFrom") or slug   # a second opening keeps its lesson's other takes (anim.py hookb)
            arc = subprocess.run(["git", "-C", ROOT, "archive", f"origin/{BRANCH}", f"studio/{src}/voices/{prev12}/takes"], capture_output=True)
            if arc.returncode or not prev12:
                arc = subprocess.run(["git", "-C", ROOT, "archive", f"origin/{BRANCH}", f"studio/{src}/01_voice/takes"], capture_output=True)
                subprocess.run(["tar", "-x", "-C", old], input=arc.stdout)
            else:
                subprocess.run(["tar", "-x", "-C", old], input=arc.stdout)
                os.makedirs(os.path.join(old, "studio", src, "01_voice"), exist_ok=True)
                shutil.move(os.path.join(old, "studio", src, "voices", prev12, "takes"), os.path.join(old, "studio", src, "01_voice", "takes"))
        info = []
        for i, t in enumerate(takes):
            n = i + 1
            f = os.path.join(out, "takes", f"{n:02d}.mp3")
            keep = os.path.join(old, "studio", req.get("takesFrom") or slug, "01_voice", "takes", f"{n:02d}.mp3")
            if req["takes"] != "all" and n not in req["takes"] and os.path.exists(keep):
                shutil.copy(keep, f)
            else:
                open(f, "wb").write(eleven(t, takes[i - 1] if i else None, takes[i + 1] if i + 1 < len(takes) else None, req["voice"], key, req.get("settings")))
            info.append({"n": n, "file": f"takes/{n:02d}.mp3", "sha256": sha(f), "seconds": round(seconds_of(f), 3), "chars": len(t)})
        # join the takes with a short breath between paragraphs
        lst = os.path.join(out, "list.txt")
        gap = os.path.join(out, "gap.mp3")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", "0.32", "-c:a", "libmp3lame", "-b:a", "128k", gap])
        with open(lst, "w") as fh:
            for i, x in enumerate(info):
                fh.write(f"file '{os.path.join(out, x['file'])}'\n")
                if i + 1 < len(info):
                    fh.write(f"file '{gap}'\n")
        voice = os.path.join(out, "voice.mp3")
        sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "160k", voice])
        t0 = 0.0
        for x in info:
            x["start"] = round(t0, 3); t0 += x["seconds"]; x["end"] = round(t0, 3); t0 += 0.32
        # one take at a time: on the whole file Whisper can skip a paragraph (lesson 9's take 4 vanished once)
        heard = []
        for x in info:
            heard += transcribe(os.path.join(out, x["file"]), offset=x["start"])
        doc, pace = write_words(slug, req, info, heard, takes)
        flags = doc["flags"]
        json.dump({"schema": "pnf.studio.takes.v1", "requestedAt": req["requestedAt"], "voice": req["voice"], "model": req["model"],
                   "scriptSha256": req["scriptSha256"], "voiceSha256": sha(voice), "takes": info, "chars": sum(x["chars"] for x in info),
                   "at": now(), "credits": credits(key)}, open(tk_path, "w"), indent=1)
        done.append((slug, out))
        print(f"{slug}: {len(info)} takes, {doc['end']:.1f} s, {len(flags)} flag(s)\n" + "\n".join(pace))
    if not done:
        print("nothing to speak")
        return
    publish_audio(done)


def git(*a, cwd=ROOT, check=True):
    return sh(["git", *a], check=check, cwd=cwd)


def push_retry(cwd, branch):
    for i in range(4):
        if git("push", "origin", f"HEAD:{branch}", cwd=cwd, check=False).returncode == 0:
            return
        git("pull", "--rebase", "origin", branch, cwd=cwd, check=False)
        time.sleep(5 + 5 * i)
    raise SystemExit(f"ERROR publish: could not push to {branch}")


def publish_audio(done):
    git("config", "user.name", "proofnotfluff-bot"); git("config", "user.email", "proofnotfluff-bot@users.noreply.github.com")
    wt = os.path.join(tempfile.mkdtemp(), "renders")
    if git("ls-remote", "--heads", "origin", BRANCH, check=False).stdout.strip():
        git("fetch", "--depth", "1", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
        git("worktree", "add", "-B", BRANCH, wt, f"origin/{BRANCH}")
    else:
        raise SystemExit("ERROR publish: no video-renders branch")
    queued = {i["slug"] for i in load_queue()["items"]}
    for slug, out in done:
        # every voice under voices/<sha12>/; 01_voice too unless the lesson is queued (its pinned code reads 01_voice)
        dsts = [os.path.join(wt, "studio", slug, "voices", sha(os.path.join(out, "voice.mp3"))[:12])]
        if slug not in queued:
            dsts.append(os.path.join(wt, "studio", slug, "01_voice"))
        for dst in dsts:
            if os.path.exists(dst):
                shutil.rmtree(dst)
            os.makedirs(dst)
            shutil.copytree(os.path.join(out, "takes"), os.path.join(dst, "takes"))
            shutil.copy(os.path.join(out, "voice.mp3"), os.path.join(dst, "voice.mp3"))
    git("add", "-A", cwd=wt)
    if git("diff", "--cached", "--quiet", cwd=wt, check=False).returncode:
        git("commit", "-m", "Studio voice: " + ", ".join(s for s, _ in done), cwd=wt)
        push_retry(wt, BRANCH)
    for slug, _ in done:
        git("add", vdir(slug, "01_voice", "takes.json"), vdir(slug, "02_transcript"))
    if git("diff", "--cached", "--quiet", check=False).returncode:
        git("commit", "-m", "Studio words: " + ", ".join(s for s, _ in done))
        push_retry(ROOT, os.environ.get("GITHUB_REF_NAME") or "main")   # a lab branch's voice stays on that branch


def cmd_rewords(slug):
    """Re-time words.json from the stored Whisper words (after a respell fix), without re-voicing."""
    d = json.load(open(vdir(slug, "02_transcript", "words.json")))
    tk = json.load(open(vdir(slug, "01_voice", "takes.json")))
    req = {"voice": d["voice"], "model": d["model"]}
    info = [dict(x) for x in tk["takes"]]
    doc, pace = write_words(slug, req, info, d["heard"], takes_of(slug))
    print(f"{slug}: {len(doc['words'])} words, {doc['end']:.1f} s, {len(doc['flags'])} flag(s)" + "".join("\n  " + f for f in doc["flags"]))


def cmd_fetch(slug):
    git("fetch", "--depth", "1", "origin", f"+refs/heads/{BRANCH}:refs/remotes/origin/{BRANCH}")
    dst = vdir(slug, "01_voice", "audio")
    os.makedirs(dst, exist_ok=True)
    # each voice is kept under voices/<sha12>/ (a re-voice of a queued lesson never overwrites 01_voice, which the queued
    # version's own code reads, so posting the old cut keeps working while the rebuild is gated); 01_voice is the fallback
    want = json.load(open(vdir(slug, "01_voice", "takes.json")))["voiceSha256"][:12]
    for rel in (f"studio/{slug}/voices/{want}", f"studio/{slug}/01_voice"):
        arc = subprocess.run(["git", "-C", ROOT, "archive", f"origin/{BRANCH}", rel], capture_output=True)
        if not arc.returncode:
            break
    if arc.returncode:
        raise SystemExit(f"ERROR fetch: no audio for {slug} on {BRANCH} yet")
    tmp = tempfile.mkdtemp()
    subprocess.run(["tar", "-x", "-C", tmp], input=arc.stdout, check=True)
    src = os.path.join(tmp, *rel.split("/"))
    for f in os.listdir(src):
        p = os.path.join(src, f)
        (shutil.copytree(p, os.path.join(dst, f), dirs_exist_ok=True) if os.path.isdir(p) else shutil.copy(p, dst))
    tk = json.load(open(vdir(slug, "01_voice", "takes.json")))
    got = sha(os.path.join(dst, "voice.mp3"))
    print(f"voice.mp3 {'PASS' if got == tk['voiceSha256'] else 'FAIL'} sha256 {got[:12]} vs takes.json {tk['voiceSha256'][:12]}")
    if got != tk["voiceSha256"]:
        raise SystemExit(1)


# ---------------------------------------------------------------------------------------------------------------------
# cues

CUE = re.compile(r'^##\s+([\w.\-]+)\s+"([^"]+)"(.*)$')
# cues.md's music line: "music: <library bed id> [level]", or "music: rooms [tune] [level]" (the room loops; plain rooms is
# the classic tune, TUNES lists the rest). A tune name starts with a letter, a level with a digit.
MUSIC_LINE = re.compile(r"^music:\s*([\w\-]+)(?:\s+([a-z][\w\-]*))?(?:\s+([\d.]+))?\s*$")


def music_entry(m):
    """cues.json's music entry from a MUSIC_LINE match. classic writes no tune key, so a plain "music: rooms" cue file
    comes out as it always has."""
    mid, tune = m.group(1), (m.group(2) or "").lower() or None
    if tune and mid != "rooms":
        raise SystemExit(f"ERROR cues: a tune name only follows rooms ('music: rooms {tune}'), not '{mid}'")
    if tune and tune not in TUNES:
        raise SystemExit(f"ERROR cues: no tune '{tune}' (tunes: {', '.join(TUNES)})")
    out = {"id": mid, "level": float(m.group(3) or 0.16)}
    if tune and tune != DEFAULT_TUNE:
        out["tune"] = tune
    return out



def cmd_cues(slug):
    src = open(vdir(slug, "03_cues", "cues.md"), encoding="utf-8").read().splitlines()
    wd = json.load(open(vdir(slug, "02_transcript", "words.json")))
    words = wd["words"]
    toks = [norm(w["w"]) for w in words]
    cues, music, cur = [], None, None
    for ln in src:
        m = MUSIC_LINE.match(ln.strip())
        if m:   # music: steady-hands 0.12 (a library bed), music: rooms (classic) or music: rooms quest (a tune); level optional
            music = music_entry(m)
            continue
        if ln.strip().startswith("music:"):   # a music line that does not parse would fall back to quiet-math unseen
            raise SystemExit(f"ERROR cues: '{ln.strip()}' is not 'music: rooms [tune] [level]' or 'music: <bed id> [level]' (tunes: {', '.join(TUNES)})")
        m = CUE.match(ln.strip())
        if m:
            cid, quote, rest = m.groups()
            sfx = re.search(r"\[sfx:\s*([\w\-]+)\]", rest)
            shift = re.search(r"(?<![\w@])([+\-]\d+(?:\.\d+)?)", rest)
            pin = re.search(r"@(\d+(?:\.\d+)?)", rest)
            cur = {"id": cid, "level": cid.count("."), "quote": quote, "sfx": sfx.group(1) if sfx else None,
                   "shift": float(shift.group(1)) if shift else 0.0, "pin": float(pin.group(1)) if pin else None, "text": ""}
            if SEND_MARK.search(rest):   # the send card goes up on this cue (Todd, Nov 7, 9:27 am; send_cue_problems)
                cur["send"] = True
            if PAYOFF_MARK.search(rest):   # v4: the outcome or the answer lands on this cue (lint_v4: by 40% of the runtime)
                cur["payoff"] = True
            cues.append(cur)
        elif cur is not None and ln.strip():
            cur["text"] = (cur["text"] + " " + ln.strip()).strip()
    pos, bad = 0, []
    for c in cues:
        q = [norm(x) for x in c["quote"].split() if norm(x)]
        hit = None
        for i in range(pos, len(toks) - len(q) + 1):
            if toks[i:i + len(q)] == q:
                hit = i; break
        if hit is None:
            close = difflib.get_close_matches(" ".join(q), [" ".join(toks[i:i + len(q)]) for i in range(len(toks) - len(q) + 1)], n=1)
            bad.append(f"{c['id']} \"{c['quote']}\" not found in order after word {pos} (closest: {close[0] if close else 'none'})")
            continue
        c["t"] = round(c["pin"] if c["pin"] is not None else max(0.0, words[hit]["start"] + c["shift"]), 3)
        c["word"] = hit
        pos = hit + 1
    if bad:
        raise SystemExit("ERROR cues: " + "; ".join(bad))
    cues[0]["t"] = 0.0
    # 3.1 s tail: the end card, up for the last 3.0 s (player.js, IMPROVE 000; style board, Oct 29); a v4 lesson has no end
    # card and ends 1 s after the last word (V4_TAIL)
    duration = round(wd["end"] + (V4_TAIL if is_v4(slug) else 3.1), 3)
    for i, c in enumerate(cues):
        nxt = next((d for d in cues[i + 1:] if d["level"] <= c["level"]), None)
        c["end"] = nxt["t"] if nxt else duration
    doc = {"schema": "pnf.studio.cues.v1", "source": wd.get("source"), "music": music, "duration": duration, "cues": cues}
    json.dump(doc, open(vdir(slug, "03_cues", "cues.json"), "w"), indent=1)
    write_js(vdir(slug, "03_cues", "cues.js"), "CUES", doc)
    for c in cues:
        print(f"{'  ' * c['level']}{c['id']:<{22 - 2 * c['level']}} {c['t']:6.2f} {c['end']:6.2f}  {c['quote'][:40]}" + (f"  [sfx: {c['sfx']}]" if c["sfx"] else "")
              + ("  [send]" if c.get("send") else ""))
    print(f"-> {len(cues)} cues, {duration:.1f} s ({wd.get('source')})")


# ---------------------------------------------------------------------------------------------------------------------
# mouth: lip sync from the voice (research run 2026-10-28, upgrade 2; _shared/looks.md Motion)

MOUTH_T = (0.15, 0.40, 0.72)   # level thresholds: closed below 0.15, slightly open, open, wide open above 0.72


def cmd_mouth(slug, quiet=False):
    """The voice's loudness, frame by frame, as 4 mouth shapes (0 closed, 1 slightly open, 2 open, 3 wide open) ->
    02_transcript/mouth.js. Loudness over 40 ms on the 300 to 3,400 Hz band; closed outside a word or below the voice's
    10th percentile minus 6 dB; scaled between the 20th and 95th percentiles with a square root; opens in about 15 ms,
    closes in about 70 ms; each shape held at least 2 frames; shifted 2 frames early (the eye forgives a mouth that leads
    the sound, not one that lags); wide open kept under 10% of talking frames."""
    import numpy as np
    from scipy.signal import butter, sosfiltfilt
    voice = vdir(slug, "01_voice", "audio", "voice.mp3")
    if not os.path.exists(voice):
        raise SystemExit(f"ERROR mouth: no voice for {slug} (anim.py fetch {slug})")
    wd = json.load(open(vdir(slug, "02_transcript", "words.json")))
    words = wd["words"]
    sr = 16000
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", voice, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
    if r.returncode:
        raise SystemExit(f"ERROR mouth: ffmpeg could not read {voice}")
    raw = r.stdout
    x = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    x = sosfiltfilt(butter(4, [300, 3400], btype="bandpass", fs=sr, output="sos"), x)
    hop, win = int(sr * 0.005), int(sr * 0.040)   # a 5 ms envelope, each point the RMS of the 40 ms around it
    c2 = np.concatenate([[0.0], np.cumsum(x * x)])
    centers = np.arange(0, len(x), hop)
    lo, hi = np.clip(centers - win // 2, 0, len(x)), np.clip(centers + win // 2, 0, len(x))
    rms = np.sqrt((c2[hi] - c2[lo]) / np.maximum(1, hi - lo))
    tc = centers / sr
    inword = np.zeros(len(tc), bool)
    for w in words:
        inword |= (tc >= w["start"]) & (tc < w["end"])
    db = 20 * np.log10(rms + 1e-9)
    gate = np.percentile(db[inword], 10) - 6.0
    voiced = inword & (db > gate)
    p20, p95 = np.percentile(rms[voiced], 20), np.percentile(rms[voiced], 95)
    v = np.where(voiced, np.sqrt(np.clip((rms - p20) / max(1e-9, p95 - p20), 0, 1)), 0.0)
    # one pole: opens fast (15 ms), closes slower (70 ms)
    a_up, a_dn = 1 - math.exp(-5 / 15), 1 - math.exp(-5 / 70)
    env = np.zeros_like(v); e = 0.0
    for i, s in enumerate(v):
        e += (s - e) * (a_up if s > e else a_dn); env[i] = e
    dur = json.load(open(vdir(slug, "03_cues", "cues.json")))["duration"] if os.path.exists(vdir(slug, "03_cues", "cues.json")) else len(x) / sr + 1
    n = int(math.ceil(dur * FPS)) + 1
    ft = (np.arange(n) + 0.5) / FPS                        # the middle of each frame's time on screen
    idx = np.clip(np.round(ft / 0.005).astype(int), 0, len(env) - 1)
    fv = np.where(ft * sr < len(x), env[idx], 0.0)
    talk = np.zeros(n, bool)
    for w in words:
        talk |= (ft >= w["start"]) & (ft < w["end"])
    fv = np.where(talk, fv, 0.0)

    def shapes(t3):
        q = np.zeros(n, int)
        q[fv >= MOUTH_T[0]] = 1; q[fv >= MOUTH_T[1]] = 2; q[fv >= t3] = 3
        # every shape holds at least 2 frames: a 1-frame shape takes the shape before it
        for _ in range(4):
            runs = np.flatnonzero(np.diff(np.concatenate([[-1], q, [-1]])))
            for a, b in zip(runs[:-1], runs[1:]):
                if b - a == 1 and a > 0:
                    q[a] = q[a - 1]
        q = np.concatenate([q[2:], [0, 0]])               # 2 frames early
        return q
    t3 = MOUTH_T[2]
    q = shapes(t3)
    talking = max(1, int(talk.sum()))
    while (q == 3).sum() / talking >= 0.10 and t3 < 0.98:   # keep the wide-open shape rare (it looks shouty when common)
        t3 += 0.02; q = shapes(t3)
    share = [round(float((q[talk] == k).sum()) / talking, 3) for k in range(4)]
    doc = {"schema": "pnf.studio.mouth.v1", "fps": FPS, "voiceSha256": sha(voice), "wordsSha256": sha(vdir(slug, "02_transcript", "words.json")),
           "thresholds": [MOUTH_T[0], MOUTH_T[1], round(t3, 2)], "gateDb": round(float(gate), 1), "talkingFrames": talking,
           "share": share, "levels": "".join(str(int(k)) for k in q)}
    write_js(vdir(slug, "02_transcript", "mouth.js"), "MOUTH", doc)
    if not quiet:
        print(f"mouth: {n} frames, {talking} talking; closed {share[0]:.0%}, slightly open {share[1]:.0%}, open {share[2]:.0%}, "
              f"wide open {share[3]:.1%} (under 10%: {'PASS' if share[3] < 0.10 else 'FAIL'}), wide threshold {t3:.2f} -> 02_transcript/mouth.js")
    return doc


def ensure_mouth(slug):
    """Stills, lint and render draw the mouth from the voice when the voice is here: (re)write mouth.js when it is
    missing or was made from another voice or other word timings. Without the voice, a committed mouth.js is used as is."""
    voice, mj = vdir(slug, "01_voice", "audio", "voice.mp3"), vdir(slug, "02_transcript", "mouth.js")
    words = vdir(slug, "02_transcript", "words.json")
    if not os.path.exists(voice) or not os.path.exists(words) or not json.load(open(words)).get("source", "").startswith("whisper"):
        return
    if os.path.exists(mj):
        try:
            old = json.loads(open(mj).read().split("=", 1)[1].strip().rstrip(";"))
            if old.get("voiceSha256") == sha(voice) and old.get("wordsSha256") == sha(words):
                return
        except Exception:
            pass
    cmd_mouth(slug)


# ---------------------------------------------------------------------------------------------------------------------
# the page, stills and the render (Chromium through Playwright)

def browser():
    from playwright.sync_api import sync_playwright
    return sync_playwright().start()


def cmd_grab(slug):
    pw = browser()
    b = pw.chromium.launch()
    pg = b.new_page(viewport={"width": 430, "height": 932}, device_scale_factor=2)
    pg.goto("file://" + os.path.join(ROOT, "docs", "chicago-rat-complaints", "index.html"))
    pg.wait_for_timeout(1500)
    out = vdir(slug, "04_scene", "assets", "rat-page.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pg.screenshot(path=out, full_page=True)
    b.close(); pw.stop()
    print(f"rat-page.png: {out} (captured {now()} from docs/chicago-rat-complaints/index.html)")


def open_stage(slug, look=None):
    ensure_mouth(slug)
    pw = browser()
    b = pw.chromium.launch(args=["--allow-file-access-from-files"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
    url = "file://" + os.path.join(RUNTIME, "stage.html") + f"?v={slug}" + (f"&look={look}" if look else "")
    pg.goto(url)
    for _ in range(200):
        if pg.evaluate("window.READY === true || !!window.BOOT_ERROR"):
            break
        pg.wait_for_timeout(100)
    err = pg.evaluate("window.BOOT_ERROR || null")
    if err:
        raise SystemExit("ERROR stage: " + err[:600])
    return pw, b, pg


def frame(pg, t, path=None, fmt="png"):
    pg.evaluate(f"drawAt({t:.4f})")
    return pg.locator("#c").screenshot(path=path, type=fmt, **({"quality": 92} if fmt == "jpeg" else {}))


def sheet(images, labels, out, cols=4, scale=0.3):
    from PIL import Image, ImageDraw, ImageFont
    tiles = [Image.open(p).convert("RGB").resize((int(1080 * scale), int(1920 * scale))) for p in images]
    tw, th = tiles[0].size
    rows = math.ceil(len(tiles) / cols)
    pad, lab = 12, 34
    S = Image.new("RGB", (cols * (tw + pad) + pad, rows * (th + lab + pad) + pad), (226, 221, 211))
    d = ImageDraw.Draw(S)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    except Exception:
        f = ImageFont.load_default()
    for i, (t, l) in enumerate(zip(tiles, labels)):
        x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + lab + pad)
        S.paste(t, (x, y)); d.text((x, y + th + 6), l, fill=(29, 36, 51), font=f)
    S.save(out, quality=90)


def cmd_stills(slug, look=None):
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    out = vdir(slug, "05_render", "sheets"); os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "*")):
        os.remove(f)
    # the opening every half second to 3 s (the hook rules, IMPROVE 00a), then one frame a cue
    times = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0] + [t for t in (min(c["t"] + 0.6, c["end"] - 0.05) for c in cues["cues"][1:]) if t > 3.2] + [cues["duration"] - 0.3]
    pw, b, pg = open_stage(slug, look)
    paths, labels = [], []
    for i, t in enumerate(times):
        p = os.path.join(out, f"f{i:02d}-{t:06.2f}.png")
        frame(pg, t, p); paths.append(p)
        cid = next((c["id"] for c in reversed(cues["cues"]) if c["t"] <= t), "")
        labels.append(f"{t:5.2f} s  {cid}")
    b.close(); pw.stop()
    for k in range(0, len(paths), 12):
        sheet(paths[k:k + 12], labels[k:k + 12], os.path.join(out, f"sheet-{k // 12 + 1}.jpg"))
    pick = [paths[int(round(i * (len(paths) - 1) / 11))] for i in range(12)]
    sheet(pick, [labels[paths.index(p)] for p in pick], vdir(slug, "05_render", "sheet.jpg"))
    print(f"stills: {len(paths)} frames, {math.ceil(len(paths) / 12)} sheet(s) in {out}; contact sheet 05_render/sheet.jpg")


# The bed sits this far under the voice (loudness against loudness): under speech, and in gaps of 600 ms or more.
UNDER_SPEECH_DB, UNDER_GAP_DB = 18.0, 10.0
DUCK_LEAD, DUCK_ATTACK, DUCK_RELEASE, PHRASE_GAP = 0.08, 0.08, 0.45, 0.6
# The bed's EQ keeps it out of the voice's way: no rumble, a dip where the voice's body and consonants live, no fizz.
BED_EQ = "highpass=f=90:poles=2,equalizer=f=300:t=q:w=1:g=-2,equalizer=f=2800:t=q:w=0.8:g=-3,lowpass=f=7000:poles=2"
SR = 48000


def loudness(path, af=None):
    """Integrated loudness (LUFS) of a file, optionally after a filter chain."""
    r = sh(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af", (af + "," if af else "") + "ebur128", "-f", "null", "-"], check=False)
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)
    if not i:
        raise SystemExit(f"ERROR mix: no loudness reading for {path}")
    return float(i[-1])


def phrases(words, gap=PHRASE_GAP):
    """Words joined into phrases wherever the pause between them is under `gap` seconds."""
    out = []
    for w in words:
        if out and w["start"] - out[-1][1] < gap:
            out[-1][1] = max(out[-1][1], w["end"])
        else:
            out.append([w["start"], w["end"]])
    return out


def duck_env(words, seconds, speech_db, gap_db, dips=()):
    """The bed's gain, sample by sample: gap_db in pauses, speech_db under the voice. Each phrase pulls it down over 80 ms,
    starting 80 ms before the first word; after the phrase it comes back up over 450 ms. Pauses under 600 ms stay down,
    so it never pumps between words. dips: (start, end, dB) extra cuts (the sting), with the same ramps. Ends with a 1.8 s
    fade out."""
    import numpy as np
    n = int(round(seconds * SR))
    t = np.arange(n) / SR
    d = np.zeros(n)
    for s, e in phrases(words):
        i0, i1 = max(0, int((s - DUCK_LEAD) * SR)), min(n, int((e + DUCK_RELEASE) * SR) + 1)
        if i0 >= n:
            continue
        tt = t[i0:i1]
        up = np.clip((tt - (s - DUCK_LEAD)) / DUCK_ATTACK, 0, 1)
        down = np.clip(1 - (tt - e) / DUCK_RELEASE, 0, 1)
        d[i0:i1] = np.maximum(d[i0:i1], np.minimum(up, down))
    g_db = gap_db - (gap_db - speech_db) * d
    for s, e, db in dips:
        x = np.minimum(np.clip((t - (s - 0.2)) / 0.2, 0, 1), np.clip(1 - (t - e) / DUCK_RELEASE, 0, 1))
        g_db = g_db + db * x
    return (10 ** (g_db / 20) * np.clip((seconds - t) / 1.8, 0, 1)).astype("float32")


def voice_of(slug, cues):
    voice = vdir(slug, "01_voice", "audio", "voice.mp3")
    return voice if os.path.exists(voice) and cues.get("source", "").startswith("whisper") else None


def decode(path, sr=SR, ch=2):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(ch), "-ar", str(sr), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype="<f4").reshape(-1, ch).copy()


def steady_bed(track, seconds, work):
    """A library track long enough for the lesson. The tracks run 36 to 60 s, so when the lesson is longer the A and B
    sections (bar 2 to the end of B) loop on the bar line, with a 20 ms crossfade at each join."""
    import numpy as np
    from scipy.io import wavfile
    path = os.path.join(ROOT, "tools", "music", track["file"])
    if track.get("music_ends_s", track.get("seconds", 0)) >= seconds or "sections" not in track or "out_s" not in track:
        return path   # long enough: it plays as written, its own ending included
    x = decode(path)
    a, z = int(dict((s[0], s[1]) for s in track["sections"])["A"] * track["bar_s"] * SR), int(track["out_s"] * SR)
    out, xf = x[:z].copy(), int(0.02 * SR)
    ramp = np.linspace(0, 1, xf)[:, None]
    while len(out) < seconds * SR + xf:
        body = x[a:z].copy()
        body[:xf] = body[:xf] * ramp + x[z:z + xf] * (1 - ramp)   # the old bar's ring fades as the loop starts
        out = np.concatenate([out, body])
    p = os.path.join(work, "steady.wav")
    wavfile.write(p, SR, out[:int(seconds * SR) + 1].astype("float32"))
    return p


def room_of(cue):
    m = re.match(r"\s*room:\s*([a-z]+)", cue.get("text", ""), re.I)
    return m.group(1).lower() if m else None


def room_plan(cues):
    """[(time, room)] at each room change: a top-level cue whose description starts "Room: <name>." moves the music there;
    one without a Room: line stays in the room before it (the first defaults to framing)."""
    plan, cur = [], None
    for c in cues["cues"]:
        if c["level"] != 0:
            continue
        r = room_of(c)
        if r and r not in ROOMS:
            print(f"mix: no music for room '{r}' on {c['id']}; it keeps {cur or ROOMS[0]} ({', '.join(ROOMS)} have loops)")
            r = None
        r = r or cur or ROOMS[0]
        if r != cur:
            plan.append((0.0 if not plan else c["t"], r)); cur = r
    return plan


def rooms_bed(cues, seconds, work, tune=DEFAULT_TUNE):
    """The tune's room loops laid end to end on one beat grid (every loop starts at 0 s, so all are in step), with a
    crossfade one of the tune's beats long centred on each room change. The fade curve is the mean of equal-power and equal-gain: the rooms share some
    parts (bass notes, kicks) and not others, so either pure curve bumps or dips up to 3 dB at the join; the mean keeps
    it within about 1.5 dB."""
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import resample_poly
    if tune not in TUNES:
        raise SystemExit(f"ERROR render: no tune '{tune}' (tunes: {', '.join(TUNES)})")
    BEAT = tune_beat(tune)   # the crossfade is one beat of this tune
    n = int(round(seconds * SR)) + 1
    t = np.arange(n) / SR
    plan = room_plan(cues)
    bed = np.zeros(n)
    for i, (t0, r) in enumerate(plan):
        p = tune_path(tune, r)
        if not os.path.exists(p):
            raise SystemExit(f"ERROR render: no music for room '{r}' in the tune {tune} (anim.py sound)")
        sr, x = wavfile.read(p)
        loop = resample_poly(x / 32768.0, SR, sr)
        t1 = plan[i + 1][0] if i + 1 < len(plan) else seconds + BEAT
        up = np.ones(n) if i == 0 else np.clip((t - (t0 - BEAT / 2)) / BEAT, 0, 1)
        down = np.clip(((t1 + BEAT / 2) - t) / BEAT, 0, 1)
        fade = lambda x: 0.5 * (np.sin(np.pi / 2 * x) + 0.5 - 0.5 * np.cos(np.pi * x))
        w = fade(up) * fade(down)
        k = w > 0
        bed[k] += w[k] * loop[np.arange(n)[k] % len(loop)]
    print(f"mix: rooms ({tune}, {TUNES[tune]['bpm']} BPM) " + ", ".join(f"{r} {t0:.2f} s" for t0, r in plan))
    path = os.path.join(work, "rooms.wav")
    wavfile.write(path, SR, bed.astype("float32"))
    return path


def bed_stem(slug, seconds, cues, work, dips=()):
    """The music bed as its own 48 kHz stereo wav: the source, EQ'd, times the ducking envelope. Returns its path."""
    from scipy.io import wavfile
    voice = voice_of(slug, cues)
    lib = json.load(open(os.path.join(ROOT, "tools", "music", "library.json")))
    mus = cues.get("music") or {"id": "quiet-math", "level": 0.16}
    if mus["id"] == "rooms":
        bed = rooms_bed(cues, seconds, work, mus.get("tune", DEFAULT_TUNE))
    else:
        track = next((t for t in lib["tracks"] if t["id"] == mus["id"]), None)
        if not track:
            raise SystemExit(f"ERROR render: music '{mus['id']}' is not in tools/music/library.json (or say music: rooms)")
        bed = steady_bed(track, seconds, work)
    if voice:   # the bed's level comes from the voice: 18 dB under it while talking, 10 dB under in pauses
        lv, lb = loudness(voice), loudness(bed, f"atrim=0:{seconds},{BED_EQ}")
        speech_db, gap_db = lv - UNDER_SPEECH_DB - lb, lv - UNDER_GAP_DB - lb
        words = json.load(open(vdir(slug, "02_transcript", "words.json")))["words"]
        print(f"mix: voice {lv:.1f} LUFS, bed {lb:.1f} LUFS after EQ; bed gain {speech_db:.1f} dB under speech, {gap_db:.1f} dB in pauses, {len(phrases(words))} phrases")
    else:       # estimate timings: no voice to duck under, the bed plays at the cue file's level
        speech_db = gap_db = 20 * math.log10(max(0.01, mus["level"])); words = []
    env = os.path.join(work, "env.wav")
    wavfile.write(env, SR, duck_env(words, seconds, speech_db, gap_db, dips))
    out = os.path.join(work, "bed.wav")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", bed, "-i", env, "-filter_complex",
        f"[0:a]aresample=48000,aformat=sample_fmts=flt:channel_layouts=stereo,atrim=0:{seconds},asetpts=PTS-STARTPTS,{BED_EQ},"
        f"apad,atrim=0:{seconds}[mb];[1:a]aformat=sample_fmts=flt:sample_rates=48000,pan=stereo|c0=c0|c1=c0[me];"
        f"[mb][me]amultiply,atrim=0:{seconds}[m]", "-map", "[m]", "-c:a", "pcm_f32le", out])
    return out


def sfx_plan(cues):
    """[(time, wav)] for every [sfx: name] cue, the take chosen in cue order so a render is always the same:
    the Nth use of a sound gets take N mod 4 (stamp_0, stamp_1, ...); ticks in a row inside one section climb the
    ladder (tick_0, tick_1, ... up to +12 semitones), and any other sound or a new section starts the count again.
    A name that is already a file (stamp_2, tick_5) plays as written. The sting is not here (sting_at)."""
    d = os.path.join(RUNTIME, "sfx")
    seen, run, out = {}, 0, []
    for c in cues["cues"]:
        if c["level"] == 0:
            run = 0
        name = c.get("sfx")
        if not name or name == "sting":
            continue
        takes = sorted(glob.glob(os.path.join(d, glob.escape(name) + "_[0-9]*.wav")), key=lambda p: int(p.rsplit("_", 1)[1][:-4]))
        if name == "tick" and takes:
            f = takes[min(run, len(takes) - 1)]; run += 1
        else:
            run = 0
            k = seen.get(name, 0); seen[name] = k + 1
            f = takes[k % len(takes)] if takes else os.path.join(d, name + ".wav")
        if not os.path.exists(f):
            raise SystemExit(f"ERROR render: no sound '{name}' (anim.py sound)")
        out.append((c["t"], f))
    return out


STING_DB, STING_DIP_DB = -12, -12


def sting_at(cues):
    """When the brand sting plays, or None. It is a logo, so it plays at most once, only on the brand moment: a cue
    marked [sfx: sting] inside the last top-level section (the close). Marked anywhere else, it is left out."""
    last = max(i for i, c in enumerate(cues["cues"]) if c["level"] == 0)
    for i, c in enumerate(cues["cues"]):
        if c.get("sfx") == "sting":
            if i >= last:
                return c["t"]
            print(f"mix: [sfx: sting] on {c['id']} left out: the sting plays only on the brand moment in the last section")
    return None


def mix(slug, seconds, out_wav, cues):
    voice = voice_of(slug, cues)
    has_voice = bool(voice)
    work = tempfile.mkdtemp()
    inputs, filt, labels = [], [], []
    if has_voice:
        inputs += ["-i", voice]; filt.append(f"[{len(inputs) // 2 - 1}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{seconds}[v]"); labels.append("[v]")
    st = sting_at(cues)
    sting = os.path.join(RUNTIME, "sfx", "sting.wav")
    if st is not None and not os.path.exists(sting):
        raise SystemExit("ERROR render: no sound 'sting' (anim.py sound)")
    dips = [(st, st + seconds_of(sting), STING_DIP_DB)] if st is not None else []   # the bed steps back for the logo
    inputs += ["-i", bed_stem(slug, seconds, cues, work, dips)]
    filt.append(f"[{len(inputs) // 2 - 1}:a]aformat=channel_layouts=stereo,apad,atrim=0:{seconds}[m]")
    labels.append("[m]")
    for t, f, db in [(t, f, -13) for t, f in sfx_plan(cues)] + ([(st, sting, STING_DB)] if st is not None else []):
        inputs += ["-i", f]
        i = len(inputs) // 2 - 1
        ms = int(t * 1000)
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume={db}dB,adelay={ms}|{ms},apad,atrim=0:{seconds}[s{i}]")
        labels.append(f"[s{i}]")
    # a gentle compressor evens out the voice's peaks, so loudness can reach -14 LUFS under the -1.5 dBTP ceiling
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{seconds},"
                "acompressor=threshold=0.125:ratio=2.5:attack=5:release=120:makeup=1[a]")
    tmp = out_wav + ".pre.wav"
    sh(["ffmpeg", "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[a]", "-ar", "48000", "-ac", "2", tmp])
    r = sh(["ffmpeg", "-hide_banner", "-i", tmp, "-af", "loudnorm=I=-14:TP=-2.0:LRA=11:print_format=json", "-f", "null", "-"], check=False)
    m = json.loads(r.stderr[r.stderr.rindex("{"):r.stderr.rindex("}") + 1])
    target = -14 if has_voice else -16
    lim = 10 ** (-3.5 / 20)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af",
        f"loudnorm=I={target}:TP=-2.0:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
        f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true,aresample=192000,"
        f"alimiter=limit={lim:.4f}:attack=1:release=60:level=disabled,aresample=48000", "-ar", "48000", "-ac", "2", out_wav])
    for _ in range(2):   # the limiter can pull loudness under target (a -15.1 LUFS mix): add the gap back, limit again
        got = loudness(out_wav)
        if got is None or got >= target - 0.4:
            break
        fix = out_wav + ".fix.wav"
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", out_wav, "-af", f"volume={target - got + 0.2:.2f}dB,aresample=192000,"
            f"alimiter=limit={lim:.4f}:attack=1:release=60:level=disabled,aresample=48000", "-ar", "48000", "-ac", "2", fix])
        os.replace(fix, out_wav)
    os.remove(tmp); shutil.rmtree(work, ignore_errors=True)
    return has_voice


def cmd_remix(slug):
    """Mix the sound again onto the finished render (video copied), after a sound-only fix."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    out = vdir(slug, "05_render", f"{slug}.mp4")
    tmp = tempfile.mkdtemp(); wav = os.path.join(tmp, "a.wav")
    mix(slug, cues["duration"], wav, cues)
    new = os.path.join(tmp, "new.mp4")
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", out, "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", new])
    shutil.move(new, out); shutil.rmtree(tmp, ignore_errors=True)
    print(f"remix: {out}")


QUEUE = os.path.join(HERE, "queue.json")
PLATFORMS = ("instagram", "tiktok", "facebook", "youtube")
GATES = ("qa", "facts", "facts-captions", "render-critic", "buyer", "send", "design", "golden")
# The new line (Todd, live chat, Nov 6, 2026, 7:15 am: "Go with you recommendations", the gate list amendment in
# coo/CONSTITUTION.md): story lessons swap buyer and golden for retell, read-aloud and compare (prompts/README.md).
STORY_GATES = ("qa", "facts", "facts-captions", "render-critic", "story", "send", "design")
# story = retell + read-aloud + compare in one fresh reviewer (prompts/story.md; Todd, live chat, Nov 6, 2026, 10:54 am:
# "Go with your rec"). A lesson gated before that with the three separate files still passes on them:
STORY_GATES_NOV6 = ("qa", "facts", "facts-captions", "render-critic", "retell", "read-aloud", "compare", "send", "design")


# A short (Format short; Todd, live chat, Nov 7, 2026, 8:33 am: "Go", recommendation 3): one fix from a queued story
# lesson, 18 to 35 s, its own opening and voice, the parent's scenes and facts. It has no story arc to retell, so the story
# gate drops; read-aloud counts still run in code (anim.py readcheck). Every other gate stays.
SHORT_GATES = ("qa", "facts", "facts-captions", "render-critic", "send", "design")
# A proven lesson (Format proven; Todd, live chat, Nov 7, 2026, 12:08 pm: "Go", to the proven idea lane): no story score or
# second-source bar; the copy check (copy, code: copy_problems, written by `anim.py copycheck`) joins the short's gates.
PROVEN_GATES = ("qa", "facts", "facts-captions", "render-critic", "send", "design", "copy")


# The viewer gate (Todd, live chat, Nov 8, 2026, 10:11 pm: "Yes", to a fresh stranger who sees only the frames and the
# words and must say what the video is about, what they get and whether they would watch to the end; prompts/viewer.md).
VIEWER_GATE_FROM = "2026-11-29"


def viewer_review_problems(d):
    """A viewer review's PASS must agree with its own answers: the same point as the one idea, something got, watched to
    the end, nothing confusing."""
    if not d or not d.get("pass"):
        return []
    sc, out = d.get("score") or {}, []
    if str(sc.get("matches_idea", "")).lower() != "same":
        out.append(f"PASS but the viewer's point is '{sc.get('matches_idea')}' against the one idea (same only)")
    if str(sc.get("watch_to_end", "")).lower() != "yes":
        out.append("PASS but the viewer would not watch to the end")
    if str(sc.get("gets", "nothing")).strip().lower() in ("", "nothing", "none"):
        out.append("PASS but the viewer gets nothing from it")
    if str(sc.get("confused", "none")).strip().lower() not in ("", "none", "no"):
        out.append(f"PASS but the viewer was confused by: {sc.get('confused')}")
    return out


def gates_for(slug):
    g = _gates_for(slug)
    if os.path.basename(slug)[:10] >= VIEWER_GATE_FROM and lesson_format(slug) in GUIDE_FORMATS and "viewer" not in g:
        g = g + ("viewer",)
    return g


def _gates_for(slug):
    if lesson_format(slug) in V4_FORMATS:   # Todd, Nov 9, 2:11 pm: four gates, each with a reason (formats.md "v4")
        return V4_GATES
    if lesson_format(slug) == "short":
        return SHORT_GATES
    if lesson_format(slug) == "proven":   # a source-matched experiment has no send card, so no send gate (Todd, Nov 8, 8:25 pm)
        return tuple(g for g in PROVEN_GATES if g != "send") if source_matched(slug) else PROVEN_GATES
    if lesson_format(slug) != "story":
        return GATES
    rev = vdir(slug, "05_render", "reviews")
    return STORY_GATES if os.path.exists(os.path.join(rev, "story.json")) or not os.path.exists(os.path.join(rev, "retell.json")) \
        else STORY_GATES_NOV6
# Two openings per lesson as two Instagram trial reels (Todd, live chat, Nov 1, 2026, 4:35 pm: "Do both", to two hook
# versions per lesson as Instagram trial reels and a send reviewer gate). The second opening is the same lesson after the
# hook (hookb_drift proves it), so it reruns only the gates its new opening can change; send and golden judge the whole
# lesson and carry over from it, facts-captions too (same captions file).
HOOKB_SUFFIX = "-hookb"
HOOKB_GATES = ("qa", "facts", "render-critic", "buyer", "design")


def fingerprints(slug):
    """What the gates saw: change any of these and the lesson must be gated again before it posts."""
    files = {"script": ("01_voice", "script.md"), "takes": ("01_voice", "takes.json"), "words": ("02_transcript", "words.json"),
             "cues": ("03_cues", "cues.json"), "scene": ("04_scene", "scene.js"), "data": ("04_scene", "data.js"),
             "captions": ("05_render", "captions.json"), "mouth": ("02_transcript", "mouth.js")}
    fp = {k: sha(vdir(slug, *v))[:12] for k, v in files.items() if os.path.exists(vdir(slug, *v))}
    for f in ("kit.js", "player.js", "looks.js", "pixfont.js"):
        fp["runtime_" + f.split(".")[0]] = sha(os.path.join(HERE, "_runtime", f))[:12]
    return fp


def load_queue():
    return json.load(open(QUEUE)) if os.path.exists(QUEUE) else {"schema": "pnf.studio.queue.v1", "items": []}


def save_queue(q):
    json.dump(q, open(QUEUE, "w"), indent=1); open(QUEUE, "a").write("\n")


def queue_first(items, item):
    """`ready <slug> --first` (Todd, live chat, Nov 8, 2026, 5:10 pm: "Row 3 now, post tomorrow 11:37"): the gated lesson
    goes ahead of every lesson still waiting (no platform up, not held), so the next slot posts it. A lesson already
    started on some platform keeps its place (pick_next finishes it first anyway), and so does everything posted or held.
    Returns a new list with the lesson in it once."""
    rest = [i for i in items if i["slug"] != item["slug"]]
    at = next((n for n, i in enumerate(rest) if not i.get("posts") and not i.get("hold")), len(rest))
    return rest[:at] + [item] + rest[at:]


def cmd_ready(slug, first=False, not_before=None):
    rev = vdir(slug, "05_render", "reviews")
    bad = []
    for g in gates_for(slug):
        f = vdir(slug, "05_render", "qa.json") if g == "qa" else os.path.join(rev, f"{g}.json")
        if not os.path.exists(f):
            bad.append(f"{g}: no file"); continue
        d = json.load(open(f))
        if not (d.get("pass") or d.get("override")):   # override: Todd's word in chat on a held gate, quoted with its time
            bad.append(f"{g}: FAIL")
    if not os.path.exists(vdir(slug, "05_render", "captions.json")):
        bad.append("captions.json: missing")
    if is_v4(slug):   # v4: no hook-pattern or tune bookkeeping; the payoff mark and the captions (labels, source) instead
        bad += [f"v4: {x}" for x in v4_static_problems(slug)]
    else:
        bad += [f"variety: {x}" for x in queue_variety_problems(slug)]
    bad += [f"send: {x}" for x in send_problems(slug, review=True)]   # Todd, Nov 7, 9:27 am (the hold is lint's)
    if "viewer" in gates_for(slug):   # Todd, Nov 8, 10:11 pm: the viewer gate's PASS must agree with its own answers
        vf = os.path.join(rev, "viewer.json")
        bad += [f"viewer: {x}" for x in viewer_review_problems(json.load(open(vf)) if os.path.exists(vf) else None)]
    if lesson_format(slug) == "proven":   # Todd, Nov 7, 12:08 pm: the copy check runs again on the files being pinned
        bad += [f"copy: {x}" for x in proven_problems(slug)[0]]
    if bad:
        raise SystemExit("ERROR ready: " + "; ".join(bad))
    # the gated files must be committed: the queue pins that commit, and posting renders from it (so later runtime
    # improvements never change a video that already passed its gates)
    dirty = sh(["git", "-C", ROOT, "status", "--porcelain", "--", os.path.relpath(os.path.join(HERE, "_runtime"), ROOT),
                os.path.relpath(vdir(slug), ROOT)], check=False).stdout.strip().splitlines()
    dirty = [d for d in dirty if "/05_render/sheet" not in d and "/05_render/qa.json" not in d and "/reviews/" not in d]
    if dirty:
        raise SystemExit("ERROR ready: commit the lesson and the runtime first: " + "; ".join(d.strip() for d in dirty[:6]))
    head = sh(["git", "-C", ROOT, "rev-parse", "HEAD"]).stdout.strip()
    # the pin must already be on GitHub: a later `git pull --rebase` gives an unpushed commit a new id, and posting
    # then can't fetch it (Oct 30: markup-margin's pin was rebased away and the 7:46 run could not post).
    sh(["git", "-C", ROOT, "fetch", "-q", "origin", "main"], check=False)
    if sh(["git", "-C", ROOT, "merge-base", "--is-ancestor", head, "origin/main"], check=False).returncode:
        raise SystemExit("ERROR ready: push the lesson commit to main first (git pull --rebase, git push), then run ready")
    q = load_queue()
    item = {"slug": slug, "readyAt": now(), "commit": head, "fingerprints": fingerprints(slug), "posts": {}}
    if not_before:   # a Central time, e.g. 2026-11-09T00:00: no slot before it takes the lesson
        from zoneinfo import ZoneInfo
        nb = dt.datetime.fromisoformat(not_before)
        item["notBefore"] = (nb if nb.tzinfo else nb.replace(tzinfo=ZoneInfo("America/Chicago"))).isoformat(timespec="minutes")
    pos = next((n for n, i in enumerate(q["items"]) if i["slug"] == slug), None)
    if pos is None:
        q["items"].append(item)
    elif q["items"][pos]["posts"]:   # a lesson already live anywhere keeps its pin: every platform shows the same cut
        raise SystemExit(f"ERROR ready: {slug} is already posted on {', '.join(q['items'][pos]['posts'])}")
    else:   # a rebuild on the newest runtime (queue rule) keeps its place in line
        q["items"][pos] = item
    if first:   # Todd's word for this lesson in a live chat: first in the waiting line
        q["items"] = queue_first(q["items"], item)
    save_queue(q)
    where = "first in the waiting line" if first else ("queued" if pos is None else "re-pinned at place " + str(pos + 1))
    print(f"ready: {slug} {where} (place {[i['slug'] for i in q['items']].index(slug) + 1} of {len(q['items'])})")


# ---------------------------------------------------------------- the second opening (hook B)
HOOKB_LINE = re.compile(r"(?im)^line:\s*(.+)$")
HOOKB_PATTERN = re.compile(r"(?im)^pattern:\s*([a-z-]+)\s*$")
CUE_HEAD = re.compile(r"(?m)^## ([a-z0-9][a-z0-9.\-]*)\b")


def cue_blocks(text):
    """cues.md split into (preamble, [(name, block text)]): a block runs from its '## name' line to the next one."""
    heads = list(CUE_HEAD.finditer(text))
    if not heads:
        return text, []
    pre = text[:heads[0].start()]
    blocks = [(m.group(1), text[m.start():(heads[i + 1].start() if i + 1 < len(heads) else len(text))]) for i, m in enumerate(heads)]
    return pre, blocks


def is_hook_cue(name):
    return name == "hook" or name.startswith("hook.")


def hookb_parts(slug):
    """The lesson's second opening: 01_voice/hook-b.md (Pattern: and Line:) and 03_cues/hook-b.md (its hook cues)."""
    fv, fc = vdir(slug, "01_voice", "hook-b.md"), vdir(slug, "03_cues", "hook-b.md")
    if not (os.path.exists(fv) and os.path.exists(fc)):
        raise SystemExit(f"ERROR hookb: {slug} needs 01_voice/hook-b.md (Pattern:, Line:) and 03_cues/hook-b.md (its hook cues); "
                         "_templates/hook-b-voice.md and hook-b-cues.md show the shape")
    v = open(fv, encoding="utf-8").read()
    line, pat = HOOKB_LINE.search(v), HOOKB_PATTERN.search(v)
    if not line or not pat:
        raise SystemExit("ERROR hookb: 01_voice/hook-b.md needs a 'Pattern: <hook pattern>' line and a 'Line: <the spoken opening>' line")
    if pat.group(1) not in HOOK_PATTERNS:
        raise SystemExit(f"ERROR hookb: pattern {pat.group(1)} is not one of {', '.join(sorted(HOOK_PATTERNS))}")
    if pat.group(1) == variety_of(slug)["hook"]:
        raise SystemExit(f"ERROR hookb: the second opening uses the lesson's own hook pattern ({pat.group(1)}); a test needs another")
    _, blocks = cue_blocks(open(fc, encoding="utf-8").read())
    if not blocks or any(not is_hook_cue(n) for n, _ in blocks) or blocks[0][0] != "hook":
        raise SystemExit("ERROR hookb: 03_cues/hook-b.md holds only hook cues ('## hook' first, then '## hook.<name>')")
    return " ".join(line.group(1).split()), pat.group(1), blocks


def hookb_script(slug, line):
    """script.md with its first paragraph (take 1) swapped for the second opening's line."""
    txt = open(vdir(slug, "01_voice", "script.md"), encoding="utf-8").read()
    parts = re.split(r"(\n\s*\n)", txt)
    for i, p in enumerate(parts):
        if p.strip() and not p.strip().startswith("#") and not re.fullmatch(r"\n\s*\n", p):
            parts[i] = line
            return "".join(parts)
    raise SystemExit("ERROR hookb: script.md has no paragraph")


def hookb_cues(slug, blocks):
    pre, mine = cue_blocks(open(vdir(slug, "03_cues", "cues.md"), encoding="utf-8").read())
    rest = [b for n, b in mine if not is_hook_cue(n)]
    if not rest or len(rest) == len(mine):
        raise SystemExit("ERROR hookb: the lesson's cues.md needs its opening as '## hook' cues and the rest after them")
    body = "".join(b if b.endswith("\n") else b + "\n" for _, b in blocks)
    return pre + body + ("\n" if not body.endswith("\n\n") else "") + "".join(rest)


HOOKB_SCENE_LINE = "window.HOOK = 'b';   // anim.py hookb: the second opening; scene.js draws its hook cues for it\n"


def cmd_hookb(slug):
    """Make videos/<slug>-hookb/: the lesson with its second opening. Same brief, facts, scene, captions and every take
    after the first; the voice workflow speaks take 1 only and keeps the rest from the lesson's own voice."""
    if slug.endswith(HOOKB_SUFFIX):
        raise SystemExit("ERROR hookb: give the lesson's own slug")
    if not os.path.exists(vdir(slug, "01_voice", "takes.json")):
        raise SystemExit(f"ERROR hookb: {slug} has no voice yet (takes.json); voice the lesson first")
    line, pat, blocks = hookb_parts(slug)
    b = slug + HOOKB_SUFFIX
    for sub in ("01_voice", "03_cues", "04_scene", "05_render"):
        os.makedirs(vdir(b, sub), exist_ok=True)
    for f in ("brief.md", "facts.json", "takes.json"):
        if os.path.exists(vdir(slug, "01_voice", f)):
            shutil.copy(vdir(slug, "01_voice", f), vdir(b, "01_voice", f))
    brief = open(vdir(b, "01_voice", "brief.md"), encoding="utf-8").read()
    brief = re.sub(r"(?im)^(- \*\*Hook pattern:\*\*\s*).*$", lambda m: m.group(1) + pat, brief, count=1)
    open(vdir(b, "01_voice", "brief.md"), "w", encoding="utf-8").write(
        brief.rstrip("\n") + f"\n- **Hook B of:** {slug} (anim.py hookb; the same lesson after the hook)\n")
    open(vdir(b, "01_voice", "script.md"), "w", encoding="utf-8").write(hookb_script(slug, line))
    open(vdir(b, "03_cues", "cues.md"), "w", encoding="utf-8").write(hookb_cues(slug, blocks))
    shutil.rmtree(vdir(b, "04_scene"))
    shutil.copytree(vdir(slug, "04_scene"), vdir(b, "04_scene"))
    sj = open(vdir(slug, "04_scene", "scene.js"), encoding="utf-8").read()
    open(vdir(b, "04_scene", "scene.js"), "w", encoding="utf-8").write(HOOKB_SCENE_LINE + sj)
    if os.path.exists(vdir(slug, "05_render", "captions.json")):
        shutil.copy(vdir(slug, "05_render", "captions.json"), vdir(b, "05_render", "captions.json"))
    cmd_speak(b, [1])
    req = json.load(open(vdir(b, "01_voice", "speak.json")))
    req["takesFrom"] = slug
    json.dump(req, open(vdir(b, "01_voice", "speak.json"), "w"), indent=1)
    print(f"hookb: {b} made ({pat}: \"{line}\"). Next: check_repo, push, wait for the voice workflow, then fetch, cues, "
          f"stills, lint, render, check, gatepack {b}; gates {', '.join(HOOKB_GATES)}; then hookready {slug}")


def hookb_drift(slug, ref=None):
    """What differs between the lesson and its second opening outside the hook: must be nothing. ref: compare with the
    lesson as pinned at that commit (what its gates saw and what posts), not the working copy."""
    b, out = slug + HOOKB_SUFFIX, []
    def lesson(*p):   # the lesson's file, at ref when given; None when missing
        if ref:
            r = sh(["git", "-C", ROOT, "show", f"{ref}:{os.path.relpath(vdir(slug, *p), ROOT)}"], check=False)
            return r.stdout if r.returncode == 0 else None
        return open(vdir(slug, *p), encoding="utf-8").read() if os.path.exists(vdir(slug, *p)) else None
    def mine(*p):
        return open(vdir(b, *p), encoding="utf-8").read() if os.path.exists(vdir(b, *p)) else None
    paras = lambda t: [" ".join(x.split()) for x in re.split(r"\n\s*\n", t or "") if x.strip() and not x.strip().startswith("#")]
    if paras(lesson("01_voice", "script.md"))[1:] != paras(mine("01_voice", "script.md"))[1:]:
        out.append("script.md differs after the first paragraph")
    ca, cb = cue_blocks(lesson("03_cues", "cues.md") or "")[1], cue_blocks(mine("03_cues", "cues.md") or "")[1]
    if [x for x in ca if not is_hook_cue(x[0])] != [x for x in cb if not is_hook_cue(x[0])]:
        out.append("cues.md differs after the hook cues")
    if mine("04_scene", "scene.js") != HOOKB_SCENE_LINE + (lesson("04_scene", "scene.js") or ""):
        out.append("scene.js is not the lesson's scene.js with the hook line")
    for f in (("04_scene", "data.js"), ("05_render", "captions.json")):
        if lesson(*f) is not None and lesson(*f) != mine(*f):
            out.append(f"{'/'.join(f)} differs")
    ka, kb = json.loads(lesson("01_voice", "takes.json") or "{}"), json.loads(mine("01_voice", "takes.json") or "{}")
    if not ka.get("takes") or [t.get("sha256") for t in ka["takes"][1:]] != [t.get("sha256") for t in kb.get("takes", [])[1:]]:
        out.append("the voice after take 1 is not the lesson's own (takes.json)")
    return out


def cmd_hookready(slug):
    b = slug + HOOKB_SUFFIX
    if not os.path.isdir(vdir(b)):
        raise SystemExit(f"ERROR hookready: no {b} (anim.py hookb {slug})")
    bad = []
    for g in HOOKB_GATES:
        f = vdir(b, "05_render", "qa.json") if g == "qa" else vdir(b, "05_render", "reviews", f"{g}.json")
        if not os.path.exists(f):
            bad.append(f"{g}: no file"); continue
        if not json.load(open(f)).get("pass"):
            bad.append(f"{g}: FAIL")
    q = load_queue()
    it = next((i for i in q["items"] if i["slug"] == slug), None)
    if not it:
        bad.append(f"{slug} is not queued (ready it first)")
    elif "instagram" in it["posts"]:
        bad.append(f"{slug} is already on Instagram: the two openings go up together")
    bad += [f"drift: {x}" for x in hookb_drift(slug, it.get("commit") if it else None)]
    if bad:
        raise SystemExit("ERROR hookready: " + "; ".join(bad))
    dirty = sh(["git", "-C", ROOT, "status", "--porcelain", "--", os.path.relpath(vdir(b), ROOT)], check=False).stdout.strip().splitlines()
    dirty = [d for d in dirty if "/05_render/sheet" not in d and "/05_render/qa.json" not in d and "/reviews/" not in d]
    if dirty:
        raise SystemExit("ERROR hookready: commit the second opening first: " + "; ".join(d.strip() for d in dirty[:6]))
    head = sh(["git", "-C", ROOT, "rev-parse", "HEAD"]).stdout.strip()
    sh(["git", "-C", ROOT, "fetch", "-q", "origin", "main"], check=False)
    if sh(["git", "-C", ROOT, "merge-base", "--is-ancestor", head, "origin/main"], check=False).returncode:
        raise SystemExit("ERROR hookready: push the commit to main first, then run hookready")
    it["hookB"] = {"slug": b, "readyAt": now(), "commit": head, "fingerprints": fingerprints(b)}
    save_queue(q)
    print(f"hookready: {b} pinned to {slug}; it goes up as a second Instagram trial reel with the lesson")


def queue_pin(slug):
    """(queue item, pin) for a lesson or its second opening; the pin holds commit and fingerprints."""
    base = slug[:-len(HOOKB_SUFFIX)] if slug.endswith(HOOKB_SUFFIX) else slug
    it = next((i for i in load_queue()["items"] if i["slug"] == base), None)
    if not it:
        return None, None
    return it, (it.get("hookB") if base != slug else it)


def cmd_waiting():
    print(json.dumps([i["slug"] for i in load_queue()["items"] if not i["posts"] and not i.get("hold")]))


# Story gate noise rule (Todd, live chat, Nov 6, 2026, 6:04 pm: "Yes", to: a "lost at" line counts only when two fresh
# reviewers flag the same moment, and a lesson that fails the story gate 3 rounds in a row goes to the back of the line).
# Before it, lsa-max-bid ran 24 script rounds: every reviewer retold the message "same", each named a different lost line.
STORY_RULE = "lost-at-twice"


def _sentences(text):
    if "\n## Words" in text:                                          # transcript.md: only the spoken words
        text = text.split("\n## Words", 1)[1]
    text = re.sub(r"(?s)```.*?```", " ", text)                        # pace tables
    text = re.sub(r"`\d+:\d+(\.\d+)?`", " ", text)                     # word times
    text = re.sub(r"\[[^\]]*\]", " ", text)                       # [bracket] voice tags
    text = re.sub(r"(?m)^\s*(#.*|NOTE.*|\|.*)$", " ", text)          # headings, notes, tables
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+|\n{2,}", text) if len(x.strip().split()) >= 2]


def _toks(t):
    return set(re.findall(r"[a-z0-9$']+", t.lower()))


def lost_line(slug, quote):
    """The index and text of the sentence a reviewer's "lost at" quote points to, in the words the gate read
    (transcript.md once it exists, else script.md)."""
    for rel in (("02_transcript", "transcript.md"), ("01_voice", "script.md")):
        f = vdir(slug, *rel)
        if not os.path.exists(f):
            continue
        sents = _sentences(open(f, encoding="utf-8").read())
        q = _toks(quote)
        if not sents or not q:
            continue
        best = max(range(len(sents)), key=lambda i: (len(q & _toks(sents[i])) / len(q),
                                                     difflib.SequenceMatcher(None, quote.lower(), sents[i].lower()).ratio()))
        if len(q & _toks(sents[best])) / len(q) >= 0.5:
            return best, sents[best], "/".join(rel)
    return None, None, None


def cmd_lostmatch(slug, a, b):
    """Do two fresh reviewers' "lost at" quotes point at the same moment? SAME: the line counts and gets fixed.
    DIFFERENT (or either is none): the retell's lost-at part passes (STORY_RULE). Run on the same words both read."""
    none = lambda x: not x or x.strip().lower() in ("none", "no", "nowhere", "n/a")
    if none(a) or none(b):
        print(json.dumps({"verdict": "DIFFERENT", "why": "one reviewer was lost nowhere", "rule": STORY_RULE})); return
    ia, sa, src = lost_line(slug, a); ib, sb, _ = lost_line(slug, b)
    if ia is None or ib is None:
        raise SystemExit("ERROR lostmatch: a quote is not in the words (check the quote against " + (src or "script.md") + ")")
    same = abs(ia - ib) <= 1 and (ia == ib or len(_toks(a) & _toks(b)) >= 2)
    print(json.dumps({"verdict": "SAME" if same else "DIFFERENT", "a": {"line": ia, "text": sa}, "b": {"line": ib, "text": sb},
                      "words": src, "rule": STORY_RULE}, ensure_ascii=False))


def story_fails_in_row(slug):
    """Story gate FAILs in a row, newest first, counting only rounds judged under STORY_RULE."""
    f = vdir(slug, "05_render", "reviews", "story.json")
    n, d = 0, json.load(open(f)) if os.path.exists(f) else None
    while isinstance(d, dict) and d.get("rule") == STORY_RULE:
        if d.get("pass") or d.get("override"):
            break
        n, d = n + 1, d.get("earlier")
    return n


# Smoother line (Todd, live chat, Nov 6, 2026, 7:14 pm: "Go with your recommendations for all"): a lesson not queued
# after 3 runs is shelved, so cloud stops sinking into one video. Runs counted from that word on.
SHELF_SINCE = "2026-11-07T01:14:00Z"
SHELF_RUNS = 3


_HISTORY = []


def _history_since():
    """Runs clone shallow (depth 1), which hides the commits the count needs: fetch back to SHELF_SINCE once."""
    if not _HISTORY:
        _HISTORY.append(1)
        if sh(["git", "-C", ROOT, "rev-parse", "--is-shallow-repository"], check=False).stdout.strip() == "true":
            sh(["git", "-C", ROOT, "fetch", "-q", f"--shallow-since={SHELF_SINCE}", "origin", "main"], check=False)


def runs_on(slug):
    """Distinct run sessions with a commit touching the lesson since SHELF_SINCE (from the Claude-Session trailer)."""
    _history_since()
    r = sh(["git", "-C", ROOT, "log", f"--since={SHELF_SINCE}", "--format=%B%x00", "--", os.path.relpath(vdir(slug), ROOT)],
           check=False)
    return len({m for m in re.findall(r"Claude-Session: (\S+)", r.stdout or "")})


def cmd_tomake():
    """Lessons built but not queued, in the order a run works them: oldest first; a lesson with 3 or more story FAILs
    in a row goes to the back (STORY_RULE); one with SHELF_RUNS runs since SHELF_SINCE and still not queued is shelved
    (not worked; its story goes back to Ready in research/STORIES.md for a clean rebuild under a new slug)."""
    queued = {i["slug"] for i in load_queue()["items"]}
    rows = []
    for d in sorted(os.listdir(VIDEOS)):
        if d in queued or d.endswith(HOOKB_SUFFIX) or not os.path.exists(vdir(d, "01_voice", "brief.md")):
            continue
        if lesson_format(d) not in ("story", "proven") or os.path.exists(vdir(d, "SHELVED")):
            continue                                         # the 6 old-line lessons stay held (REBUILD.md); shelved stay out
        rows.append({"slug": d, "story_fails_in_row": story_fails_in_row(d), "runs": runs_on(d)})
    for r in rows:
        r["place"] = ("shelve: %d runs, not queued" % r["runs"]) if r["runs"] >= SHELF_RUNS else \
            "back of line: 3 story FAILs in a row" if r["story_fails_in_row"] >= 3 else "in line"
    rows.sort(key=lambda r: (r["place"].startswith("shelve"), r["story_fails_in_row"] >= 3))
    print(json.dumps(rows, indent=1))


def cmd_shelve(slug, reason):
    """Mark a lesson shelved (videos/<slug>/SHELVED). The run also moves its story back to Ready in STORIES.md."""
    if not reason:
        raise SystemExit("ERROR shelve: give a reason")
    open(vdir(slug, "SHELVED"), "w").write(f"{now()} {reason}\n")
    print(f"shelved: {slug}")


# Read-aloud counts in code (same Todd word): what a script can count, code decides the same way every time, before any
# AI reads it. The AI read-aloud keeps the judgment parts (the chain, set-up, one voice, order).
BREATH_WORDS = 32


def cmd_readcheck(slug, which=""):
    """script.md by default (before the voice); `readcheck <slug> transcript` after it. Exit 1 on a fault."""
    f = vdir(slug, "02_transcript", "transcript.md") if which == "transcript" else vdir(slug, "01_voice", "script.md")
    sents = _sentences(open(f, encoding="utf-8").read())
    n = [len(x.split()) for x in sents]
    breath = [(i + 1, x) for i, x in enumerate(sents) if n[i] > BREATH_WORDS]
    choppy, i = [], 0
    while i < len(n):
        j = i
        while j < len(n) and n[j] <= 4:
            j += 1
        if j - i >= 3:
            choppy.append((i + 1, " / ".join(sents[i:j])))
        i = max(j, i + 1)
    andthen = [(i + 1, x) for i, x in enumerate(sents) if re.match(r"(?i)^(and then|and so then|then)\b", x)]
    out = {"words": os.path.relpath(f, VIDEOS), "sentences": len(sents), "breath_fails": len(breath),
           "choppy_runs": len(choppy), "and_then_starts": len(andthen),
           "faults": [f"breath s{i} ({len(x.split())} words): {x[:90]}" for i, x in breath] +
                     [f"choppy from s{i}: {x[:90]}" for i, x in choppy] +
                     [f"and-then s{i}: {x[:90]}" for i, x in andthen]}
    out["pass"] = not out["faults"]
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if not out["pass"]:
        raise SystemExit(1)


# Words that already passed are not re-judged (same Todd word): when the story gate passes on script.md, `storysnap`
# keeps those words; after the voice, `storycarry` lists only the sentences that changed, and the after-voice story
# check reads only those (in context). No changed sentence: retell and read-aloud carry over; compare still runs after
# the render.
def cmd_storysnap(slug):
    src = vdir(slug, "01_voice", "script.md")
    shutil.copy(src, vdir(slug, "05_render", "reviews", "story-passed-words.md"))
    print("snapshot: words that passed the story gate kept")


def cmd_storycarry(slug):
    snap = vdir(slug, "05_render", "reviews", "story-passed-words.md")
    tr = vdir(slug, "02_transcript", "transcript.md")
    if not os.path.exists(snap) or not os.path.exists(tr):
        raise SystemExit("ERROR storycarry: needs story-passed-words.md (storysnap after a pass) and transcript.md")
    old = _sentences(open(snap, encoding="utf-8").read()); new = _sentences(open(tr, encoding="utf-8").read())
    norm = lambda x: " ".join(re.findall(r"[a-z0-9$']+", x.lower()))
    changed = [(i + 1, x) for i, x in enumerate(new)
               if max((difflib.SequenceMatcher(None, norm(x), norm(o)).ratio() for o in old), default=0) < 0.9]
    out = {"carry": not changed, "changed": [f"s{i}: {x}" for i, x in changed], "sentences": len(new)}
    print(json.dumps(out, indent=1, ensure_ascii=False))


def cmd_hold(slug, reason, off=False):
    """Take a lesson out of the posting line (Todd, Oct 30, 2026, 4:01 pm: too thin to post; rebuild or drop it).
    A held lesson is skipped by next and not counted by waiting. `unhold` puts it back."""
    q = load_queue()
    it = next((i for i in q["items"] if i["slug"] == slug), None)
    if not it:
        raise SystemExit(f"ERROR hold: {slug} is not in the queue")
    if off:
        it.pop("hold", None)
    else:
        if not reason:
            raise SystemExit("ERROR hold: give a reason")
        it["hold"] = {"reason": reason, "at": now()}
    save_queue(q)
    print(f"{'unheld' if off else 'held'}: {slug}")


# Post what we can make. Buffer rule (Todd, live chat, Nov 7, 2026, 8:33 am: "Go", to the social engine audit's
# recommendation 2; replaces Nov 6's "1 a day until 3 wait"): 3 a day when 6 or more lessons wait, 2 a day at 3 to 5,
# 1 a day at 1 or 2 (video/config.json posting "cadence"). The buffer is counted as this morning's line: lessons waiting
# now plus lessons started today. A lesson already started always finishes its platforms.
# A short (Format short, recommendation 3) posts only once its parent lesson went up 24 h or more before, never on the
# parent's first day; until then the line skips it and takes the next lesson.
CADENCE_DEFAULT = [{"waiting": 6, "perDay": 3}, {"waiting": 3, "perDay": 2}, {"waiting": 0, "perDay": 1}]
SHORT_GAP_HOURS = 24


def burst_today(day=None):
    """config posting.burst (Todd, live chat, Nov 8, 2026, 10:08 am: 5 posts today and 5 tomorrow) when `day` is one of its days."""
    from zoneinfo import ZoneInfo
    cfg = json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8")).get("posting", {})
    day = day or dt.datetime.now(ZoneInfo("America/Chicago")).date()
    b = cfg.get("burst") or {}
    return b if day.isoformat() in b.get("days", []) else None


def cadence_cap(buffer, day=None):
    cfg = json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8")).get("posting", {})
    b = burst_today(day) if day else None
    if b:
        return b.get("perDay", 5)
    rows = sorted(cfg.get("cadence", CADENCE_DEFAULT), key=lambda r: -r["waiting"])
    cap = next((r["perDay"] for r in rows if buffer >= r["waiting"]), 1)
    return min(cap, cfg.get("perDay", 3))


def _post_times(i, before=None):
    out = []
    for p in i.get("posts", {}).values():
        if isinstance(p, dict) and p.get("at"):
            t = dt.datetime.fromisoformat(p["at"].replace("Z", "+00:00"))
            if before is None or t < before:
                out.append(t)
    return out


def started_today(items, at=None):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    at = at or dt.datetime.now(tz)
    today = at.astimezone(tz).date()
    n = 0
    for i in items:
        ats = _post_times(i, at)
        if ats and min(ats).astimezone(tz).date() == today:
            n += 1
    return n


def derived_from(slug):
    """A short's parent lesson, from brief.md's '- **Derived from:** `slug`' line."""
    p = vdir(slug, "01_voice", "brief.md")
    m = re.search(r"(?im)^- \*\*Derived from:\*\*\s*`?([a-z0-9-]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
    return m.group(1).lower() if m else None


def pick_next(items, at, fmt=None, parent=None):
    """What the posting line takes at time `at`, with only the posts made before `at` counted. Returns
    (item or None, why). fmt and parent are lookups (tests pass made-up ones)."""
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    fmt = fmt or lesson_format
    parent = parent or derived_from
    by = {i["slug"]: i for i in items}
    day = at.astimezone(tz).date()
    # notBefore (`ready --first --not-before`, Todd, live chat, Nov 8, 2026, 5:10 pm: "post tomorrow 11:37"): a lesson put
    # first for a later slot is not taken by an earlier one
    ready = lambda i: (not i.get("readyAt") or dt.datetime.fromisoformat(i["readyAt"]) <= at) and \
        (not i.get("notBefore") or dt.datetime.fromisoformat(i["notBefore"]) <= at)
    waiting = [i for i in items if ready(i) and not _post_times(i, at) and not i.get("hold")]
    st = started_today(items, at)
    cap = cadence_cap(len(waiting) + st, day)
    skipped = []
    for i in items:
        posted = _post_times(i, at)
        if (i.get("hold") and not posted) or not ready(i):
            continue
        missing = [p for p in PLATFORMS if not (isinstance(i["posts"].get(p), dict)
                   and dt.datetime.fromisoformat(i["posts"][p]["at"].replace("Z", "+00:00")) < at)]
        if not missing:
            continue
        if posted:
            return i, "finish"
        if st >= cap:
            return None, f"cadence: {cap} a day with {len(waiting) + st} in this morning's line ({st} started today)"
        if fmt(i["slug"]) == "short":
            par = by.get(parent(i["slug"]) or "")
            pt = _post_times(par, at) if par else []
            if not pt or at - min(pt) < dt.timedelta(hours=SHORT_GAP_HOURS) or min(pt).astimezone(tz).date() == day:
                skipped.append(i["slug"])
                continue
        return i, "new"
    return None, ("short spacing: " + ", ".join(skipped)) if skipped else "nothing waiting"


def cmd_next():
    from zoneinfo import ZoneInfo
    items = load_queue()["items"]
    it, why = pick_next(items, dt.datetime.now(ZoneInfo("America/Chicago")))
    if not it:
        print(json.dumps({"slug": None} if why == "nothing waiting" else {"slug": None, "why": why}))
        return
    missing = [p for p in PLATFORMS if p not in it["posts"]]
    b = burst_today()
    print(json.dumps({"slug": it["slug"], "missing": missing, "commit": it.get("commit"), "perRun": (b or {}).get("perRun", 1)}))


# Missed-slot alarm (Todd, live chat, Nov 7, 2026, 8:33 am: "Go", recommendation 5). PC posting runs have gone up as
# late as 90 minutes after their slot (Nov 2 lunch 13:07 for 11:37), so a slot's posting window is 3 hours. Each cloud
# recorder run, after it records the post log, checks the latest slot whose window has closed in the last 14 hours
# (17:33 checks lunch, 21:33 end of day, 9:33 last evening; 12:33 none), so each slot is checked once: was a post due
# there (the same rule as `next`), and did anything go up in its window? Due and nothing up: MISSED (the laptop asleep,
# Chrome signed out, the extension dropped). A lesson started 3 hours or more before with platforms missing: INCOMPLETE.
SLOT_WINDOW = dt.timedelta(hours=3)


def slot_times(day):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    cfg = json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8")).get("posting", {})
    out = []
    for s_ in cfg.get("slots", []):
        h, m = map(int, s_["central"].split(":"))
        out.append((s_["name"], dt.datetime.combine(day, dt.time(h, m), tz)))
    return out


def missed_check(items, slot_name, slot_at, now_at, fmt=None, parent=None):
    it, why = pick_next(items, slot_at + dt.timedelta(minutes=1), fmt, parent)
    window_end = slot_at + SLOT_WINDOW
    up = [i["slug"] for i in items if any(slot_at - dt.timedelta(minutes=10) <= t <= window_end for t in _post_times(i))]
    res = {"slot": slot_name, "at": slot_at.isoformat(timespec="minutes"), "due": it["slug"] if it else None,
           "why": why, "postedInWindow": up}
    if now_at < window_end:
        res["status"] = "TOO EARLY"
    elif it and not up:
        res["status"] = "MISSED"
    else:
        res["status"] = "OK"
    late = [i["slug"] for i in items if _post_times(i) and len(_post_times(i)) < len(PLATFORMS)
            and now_at - min(_post_times(i)) >= SLOT_WINDOW and not i.get("hold")]
    if late:
        res["incomplete"] = late
        if res["status"] == "OK":
            res["status"] = "INCOMPLETE"
    return res


def slot_to_check(nowt):
    """The latest slot whose 3-hour window closed in the last 14 hours (None: nothing to check this run)."""
    cands = slot_times(nowt.date() - dt.timedelta(days=1)) + slot_times(nowt.date())
    done = [s_ for s_ in cands if s_[1] + SLOT_WINDOW <= nowt and nowt - s_[1] <= dt.timedelta(hours=14)]
    return done[-1] if done else None


def cmd_missed(slot_name=None):
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    nowt = dt.datetime.now(tz)
    if slot_name:
        pick = [s_ for s_ in slot_times(nowt.date()) if s_[0] == slot_name][:1]
        pick = pick[0] if pick else None
    else:
        pick = slot_to_check(nowt)
    if not pick:
        print(json.dumps({"slot": slot_name, "status": "NO SLOT TO CHECK"}))
        return
    print(json.dumps(missed_check(load_queue()["items"], pick[0], pick[1], nowt)))


AI_VOICE_LINE = re.compile(r"AI version of my", re.I)   # Todd, Oct 29, 2026: never in a caption, whatever the file says


def postcaptions(slug):
    """The text to paste on each platform: captions.json with any AI voice line taken out (Todd, Oct 29, 2026)."""
    d = json.load(open(vdir(slug, "05_render", "captions.json")))
    out = {}
    for plat in PLATFORMS:
        for k, v in d.get(plat, {}).items():
            if isinstance(v, str):
                v = "\n".join(l for l in v.split("\n") if not AI_VOICE_LINE.search(l))
            out[f"{plat}.{k}"] = v
    for k, v in out.items():
        if isinstance(v, str) and AI_VOICE_LINE.search(v):
            raise SystemExit(f"ERROR postcaptions: {k} still carries the AI voice line")
    return out


def cmd_postcaptions(slug):
    print(json.dumps(postcaptions(slug), indent=1, ensure_ascii=False))


def cmd_postcopy(slug):
    """Render the queued lesson from the commit its gates passed at, check every fingerprint, export the post copy
    to videos/<slug>/05_render/<slug>-post.mp4 in this checkout (the path Chrome's file_upload reads)."""
    _, it = queue_pin(slug)   # a lesson, or its second opening (SLUG-hookb, pinned by hookready)
    if not it or not it.get("commit"):
        raise SystemExit(f"ERROR postcopy: {slug} is not queued with a commit")
    wt = tempfile.mkdtemp(prefix="gated-")
    sh(["git", "-C", ROOT, "fetch", "--depth", "1", "origin", it["commit"]], check=False)
    if sh(["git", "-C", ROOT, "cat-file", "-e", it["commit"] + "^{commit}"], check=False).returncode:
        raise SystemExit(f"ERROR postcopy: pinned commit {it['commit'][:12]} is not on GitHub (rebased away); hold the "
                         "post and tell Todd: the lesson needs re-pinning to a pushed commit with the same fingerprints")
    sh(["git", "-C", ROOT, "worktree", "add", "--detach", wt, it["commit"]])
    try:
        cmd = [sys.executable, os.path.join(wt, "video", "studio", "anim.py")]
        g = subprocess.run(cmd + ["fingerprint", slug], capture_output=True, text=True)
        fp = json.loads(g.stdout.strip().splitlines()[-1])
        changed = [k for k, v in it["fingerprints"].items() if fp.get(k) != v]
        if changed:
            raise SystemExit(f"ERROR postcopy: the pinned commit does not match what the gates saw: {', '.join(changed)}")
        for c in (["fetch", slug], ["render", slug]):   # the pinned commit's own code makes the picture and sound
            r = subprocess.run(cmd + c, capture_output=True, text=True)
            print((r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else c[0])
            if r.returncode:
                raise SystemExit(f"ERROR postcopy: {c[0]} failed")
        wr = os.path.join(wt, "video", "studio", "videos", slug, "05_render")   # packaging only: today's export
        cmd_export(slug, os.path.join(wr, f"{slug}.mp4"), os.path.join(wr, f"{slug}-post.mp4"))
        src = os.path.join(wt, "video", "studio", "videos", slug, "05_render", f"{slug}-post.mp4")
        # Chrome's file_upload reads the repo path; /mnt/user-data/outputs is refused (LEARNINGS Oct 28; usage audit Oct 30).
        # The worktree is removed below, so the upload copy goes to the main checkout (gitignored, never committed).
        dst = vdir(slug, "05_render", f"{slug}-post.mp4")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        try:   # older sessions looked here; harmless if the folder is not writable
            os.makedirs("/mnt/user-data/outputs", exist_ok=True)
            shutil.copy(src, os.path.join("/mnt/user-data/outputs", f"{slug}.mp4"))
        except OSError:
            pass
        print(f"postcopy: upload {dst} ({os.path.getsize(dst) / 1e6:.1f} MB) from {it['commit'][:12]}")
    finally:
        sh(["git", "-C", ROOT, "worktree", "remove", "--force", wt], check=False)


def _at(at):
    """A post time from the scoreboard post log (scheduled runs on Todd's PC can't push; the cloud recorder commits
    their posts later with the time they really went up). None: now."""
    if not at:
        return now()
    try:
        return dt.datetime.fromisoformat(at.replace("Z", "+00:00")).astimezone(dt.timezone(dt.timedelta(hours=-5))).isoformat(timespec="seconds")
    except ValueError:
        raise SystemExit(f"ERROR: bad time {at!r} (ISO 8601, e.g. 2026-10-30T16:52:00Z)")


def cmd_posted(slug, platform, url, at=None):
    trial = platform == "instagram-trial"   # the Instagram post went up as a trial reel (non-followers first)
    platform = "instagram" if trial else platform
    if platform not in PLATFORMS:
        raise SystemExit(f"ERROR posted: platform must be one of {', '.join(PLATFORMS)}")
    q = load_queue()
    if slug.endswith(HOOKB_SUFFIX):   # the second opening: an Instagram trial reel only
        it = next((i for i in q["items"] if i["slug"] == slug[:-len(HOOKB_SUFFIX)]), None)
        if not it or not it.get("hookB"):
            raise SystemExit(f"ERROR posted: {slug} is not pinned (anim.py hookready)")
        if not trial:
            raise SystemExit("ERROR posted: the second opening goes up only as an Instagram trial reel (instagram-trial)")
        it["hookB"]["post"] = {"url": url, "at": _at(at), "trial": True}
        save_queue(q)
        print(f"posted: {slug} as the second Instagram trial reel")
        return
    it = next((i for i in q["items"] if i["slug"] == slug), None)
    if not it:
        raise SystemExit(f"ERROR posted: {slug} is not in the queue")
    it["posts"][platform] = {"url": url, "at": _at(at), **({"trial": True} if trial else {})}
    save_queue(q)
    print(f"posted: {slug} on {platform} ({len(it['posts'])} of 4)")



# Instagram trial first, then the feed; a fresh re-cut of the winners about 90 days on (Todd, Oct 29, 2026, 3:59 pm:
# "Fold it in"; POSTING.md). The trial reel is the lesson's one Instagram post; sharing it to followers is not a second
# post. Mirrored or flipped reposts never: a re-cut is a new lesson (new slug, new hook and opening, every gate, variety).
TRIAL_HOURS, RECUT_DAYS = 72, 90


def _age_hours(at):
    return (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(at)).total_seconds() / 3600


def cmd_feedshared(slug, at=None):
    """The trial reel shared to followers. SLUG-hookb: the second opening won and was the one shared."""
    q = load_queue()
    won_b = slug.endswith(HOOKB_SUFFIX)
    base = slug[:-len(HOOKB_SUFFIX)] if won_b else slug
    it = next((i for i in q["items"] if i["slug"] == base), None)
    if not it or "instagram" not in it["posts"]:
        raise SystemExit(f"ERROR feedshared: {base} has no Instagram trial post")
    if won_b and not (it.get("hookB") or {}).get("post"):
        raise SystemExit(f"ERROR feedshared: {slug} has no trial reel recorded")
    it["instagramFeed"] = {"at": _at(at), **({"hook": "b" if won_b else "a"} if it.get("hookB", {}).get("post") else {})}
    save_queue(q)
    print(f"feedshared: {slug} shared to followers")


def cmd_trials():
    """Instagram trial reels not yet shared to followers; due once 72 hours old."""
    out = []
    for i in load_queue()["items"]:
        ig = i["posts"].get("instagram")
        if ig and not i.get("instagramFeed") and ig.get("trial"):
            h = _age_hours(ig["at"])
            row = {"slug": i["slug"], "url": ig["url"], "hours": round(h, 1), "due": h >= TRIAL_HOURS}
            hb = (i.get("hookB") or {}).get("post")
            if hb:   # two openings: share the one that kept more viewers (POSTING.md), never both
                hh = _age_hours(hb["at"])
                row.update(hookB={"slug": i["hookB"]["slug"], "url": hb["url"], "hours": round(hh, 1)}, due=min(h, hh) >= TRIAL_HOURS)
            out.append(row)
    print(json.dumps(out))


def cmd_recuts():
    """Every posted lesson's re-cut date (90 days after its feed post), the ones already re-cut, and its numbers if read."""
    done = {}
    for d in sorted(os.listdir(VIDEOS)):
        p = os.path.join(VIDEOS, d, "01_voice", "brief.md")
        m = re.search(r"(?im)^- \*\*Re-cut of:\*\*\s*`?([0-9a-z-]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
        if m:
            done[m.group(1)] = d
    rows = []
    for i in load_queue()["items"]:
        if not i["posts"]:
            continue
        feed = (i.get("instagramFeed") or {}).get("at") or min(v["at"] for v in i["posts"].values())
        due = dt.datetime.fromisoformat(feed) + dt.timedelta(days=RECUT_DAYS)
        days = round(-_age_hours(due.isoformat()) / 24)
        mf = os.path.join(HERE, "research", "metrics", f"{i['slug']}.json")
        rows.append({"slug": i["slug"], "recutOn": due.date().isoformat(), "daysLeft": days, "recutDone": done.get(i["slug"]),
                     "metrics": json.load(open(mf)) if os.path.exists(mf) else None})
    print(json.dumps(rows, indent=1))

def cmd_gatepack(slug):
    """What the fresh reviewers look at: timeline sheets at 2 frames a second (labeled), the first frames, in
    05_render/gates/ (not committed). The stills (cmd stills) are the other half."""
    from PIL import Image, ImageDraw
    mp4 = vdir(slug, "05_render", f"{slug}.mp4")
    out = vdir(slug, "05_render", "gates"); shutil.rmtree(out, ignore_errors=True); os.makedirs(os.path.join(out, "fr"))
    sh(["ffmpeg", "-loglevel", "error", "-i", mp4, "-vf", "fps=2,scale=216:384", os.path.join(out, "fr", "%03d.png")])
    fs = sorted(glob.glob(os.path.join(out, "fr", "*.png"))); per, cols = 30, 10
    for s0 in range(0, len(fs), per):
        chunk = fs[s0:s0 + per]; rows = (len(chunk) + cols - 1) // cols
        o = Image.new("RGB", (cols * 216, rows * 404), "white"); d = ImageDraw.Draw(o)
        for i, f in enumerate(chunk):
            x, y = (i % cols) * 216, (i // cols) * 404; o.paste(Image.open(f), (x, y)); d.text((x + 4, y + 386), f"{(s0 + i) * 0.5:.1f} s", fill="black")
        o.save(os.path.join(out, f"timeline-{s0 // per + 1}.jpg"), quality=88)
    for t in ("0", "0.8", "2.0"):
        sh(["ffmpeg", "-loglevel", "error", "-y", "-ss", t, "-i", mp4, "-frames:v", "1", os.path.join(out, f"frame-{t}s.png")])
    shutil.rmtree(os.path.join(out, "fr"), ignore_errors=True)
    print(f"gatepack: {out} ({(len(fs) + per - 1) // per} timeline sheets, 3 first frames)")



JUDGE_Q = re.compile(r"(?i)\b(would you|what would|wh(o|at)'?s right|who is right|who'?s wrong|fair\b|too far|right call|your call|"
                     r"you decide|should (he|she|they|the|i|you|we)|do you (take|let|wait|call|pay|charge|walk|chase|eat|keep|sell|accept|fire|hire)|"
                     r"would your|is (he|she|it|this|that) (right|wrong|fair))")
QUIZ_Q = re.compile(r"(?i)\b(do you know (your|what|how)|what('?s| is) your|how much (do|does) your)\b")


def judge_question(line):
    """A line that asks the viewer to judge the scene (decision 4), never a quiz about the viewer's own numbers."""
    line = (line or "").strip()
    return "?" in line and bool(JUDGE_Q.search(line)) and not QUIZ_Q.search(line)

def captions_problems(slug):
    """_shared/captions.md in code: line 1 under 100 characters, a send line, no AI voice line (Todd, Oct 29), hashtag counts, no em or
    en dashes, YouTube title under 100 with no hashtags and 5 to 10 tags. Returns a list of problems."""
    f = vdir(slug, "05_render", "captions.json")
    if not os.path.exists(f):
        return ["captions.json missing"]
    d, out = json.load(open(f)), []
    tags = {"instagram": (3, 5), "tiktok": (3, 5), "facebook": (2, 3), "youtube": (2, 3)}
    for pl, (lo, hi) in tags.items():
        if pl not in d:
            out.append(f"{pl}: missing"); continue
        text = d[pl]["description"] if pl == "youtube" else d[pl]["caption"]
        first = text.split("\n")[0]
        if len(first) >= 100: out.append(f"{pl}: line 1 is {len(first)} characters (under 100)")
        if not re.search(r"(?i)\bsend this\b|\bsave this\b", text): out.append(f"{pl}: no send or save line")
        if re.search(r"(?i)narrated by an ai|ai version of my own voice", text): out.append(f"{pl}: the AI voice line (Todd, Oct 29: none in any caption)")
        n = len(re.findall(r"(?<!\w)#\w+", text))
        if not lo <= n <= hi: out.append(f"{pl}: {n} hashtags ({lo} to {hi})")
        if re.search(r"(?i)#(fyp|foryou|viral)\b", text): out.append(f"{pl}: banned hashtag")
        if re.search("[\u2013\u2014]", text): out.append(f"{pl}: an em or en dash")
    if lesson_format(slug) == "proven" and os.path.basename(slug)[:10] >= STUDIO_V3_FROM and not slug.endswith(HOOKB_SUFFIX):   # decision 4 (Todd, Nov 8): a judge-the-scene question in each caption and the YouTube title
        for pl in ("instagram", "tiktok", "facebook"):
            body = [ln.strip() for ln in (d.get(pl, {}).get("caption") or "").split("\n") if ln.strip() and not ln.strip().startswith("#")]
            if not any(judge_question(ln) for ln in body[-4:]):
                out.append(f"{pl}: no judge-the-scene question before the send line (captions.md, decision 4)")
        if not judge_question(d.get("youtube", {}).get("title", "")):
            out.append("youtube: the title asks no judge-the-scene question (captions.md, decision 4)")
    y = d.get("youtube", {})
    if y:
        if len(y.get("title", "")) >= 100 or "#" in y.get("title", ""): out.append("youtube: title 100+ characters or has a hashtag")
        if not 5 <= len(y.get("tags", [])) <= 10: out.append(f"youtube: {len(y.get('tags', []))} tags (5 to 10)")
        if re.search("[\u2013\u2014]", y.get("title", "")): out.append("youtube: an em or en dash in the title")
    return out


# which worlds (rooms and set pieces) a lesson draws, counted per lint step (Todd, Oct 28, 7:37 pm: "You are cycling
# through the same scenery ... come up with new cool graphic motion for each video")
WORLD_SPY = """(() => { if (window.__spy) return; window.__spy = true; const mk = window.Kit.make;
  const note = (w) => { if (window.__used) window.__used[w] = 1; };
  window.Kit.make = function (...a) { const k = mk.apply(this, a); const r = k.room;
    k.room = function (n, ...b) { note('room:' + n); return r.call(this, n, ...b); };
    // k.sets is a getter (sets.js), so a plain assignment would be dropped: redefine it as a value
    for (const key of ['set', 'sets']) if (k[key] && typeof k[key] === 'object') { const o = k[key];
      Object.defineProperty(k, key, {configurable: true, writable: true, value: new Proxy(o, {get(t, p) { const f = t[p]; return typeof f === 'function' ? function (...b) { note('set:' + String(p)); return f.apply(this, b); } : f; }})}); }
    return k; }; })()"""
BASE_ROOMS = ("room:framing", "room:blackboard", "room:workshop", "room:garage")


def variety_problems(slug, share):
    """Each lesson its own world: writes 04_scene/worlds.json (share of the runtime each world is on screen) and compares
    with the two lessons before it. Rules: no set piece from either of the two lessons before (Todd, Oct 31, 2026: "put
    measures in place to mitigate those risks as much as possible", on mass-produced flags; was the last one only); at
    least 3 set pieces new against the two before; the four stock rooms on screen at most 40% of the runtime."""
    json.dump({"schema": "pnf.studio.worlds.v1", "share": share}, open(vdir(slug, "04_scene", "worlds.json"), "w"), indent=1)
    vids = sorted(d for d in os.listdir(VIDEOS) if re.match(r"\d{4}-\d\d-\d\d-", d) and not d.endswith(HOOKB_SUFFIX))
    prev = [d for d in vids if d < slug][-2:]
    mine = {w for w, v in share.items() if v >= 0.05}
    sets = {w for w in mine if w.startswith("set:")}
    out = []
    room_share = sum(v for w, v in share.items() if w in BASE_ROOMS)
    if room_share > 0.4:
        out.append(f"the stock rooms fill {room_share:.0%} of the runtime (at most 40%): build this lesson's own worlds (_shared/sets.md)")
    seen = []
    for d in prev:
        f = os.path.join(VIDEOS, d, "04_scene", "worlds.json")
        if os.path.exists(f):
            seen.append({w for w, v in json.load(open(f))["share"].items() if v >= 0.05 and w.startswith("set:")})
    if seen and sets & set().union(*seen):
        out.append(f"reuses set pieces from the last two lessons: {', '.join(sorted(sets & set().union(*seen)))}")
    new = sets - set().union(*seen) if seen else sets
    if len(new) < 3 and not source_matched(slug) and not recs_apply(slug):   # a source-matched experiment draws what its source shows (Todd, Nov 8, 8:25 pm); no minimum from RECS_FROM (call 4)
        out.append(f"{len(new)} set piece(s) new against the two lessons before (at least 3)")
    return out



# Variety across the queue (Todd, Oct 29, 2026, 3:56 pm: "Go with your recommendations for everything", to a check that
# no two queued lessons share a hook pattern, format and example, so the platforms never read us as mass-produced).
# brief.md names three things: the hook pattern, the treatment (the lesson's format) and the real example it is built on.
# Rules for a lesson against the other unposted lessons in the queue: its example is its own (also against the last 3
# posted lessons that name one); no other unposted lesson has the same hook pattern and treatment; and the lessons right
# before and after it in posting order do not open on the same hook pattern.
HOOK_PATTERNS = {"stuck-moment", "two-shops", "object-number", "which-pick", "your-move", "problem-question", "result-first", "myth", "receipt"}
TREATMENTS = {"story", "myth-fact", "steps", "before-after", "math-board", "copy-this"}
VARIETY_FIELDS = (("hook", "Hook pattern"), ("treatment", "Treatment"), ("example", "Example"))


def variety_of(slug):
    p = vdir(slug, "01_voice", "brief.md")
    txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    out = {}
    for key, label in VARIETY_FIELDS:
        m = re.search(r"(?im)^- \*\*" + label + r":\*\*\s*`?([a-z0-9-]+)`?", txt)
        out[key] = m.group(1).lower() if m else None
    return out


# The tune (Todd, Oct 29, 2026, 8:11 pm: "different tunes for each video"): a lesson's music is not the same as the
# lesson right before or right after it in the posting line (the last posted lesson, then the unposted queue in order).
# Its music is its 03_cues/cues.md music line (the source of truth): "music: rooms" is classic, "music: rooms <tune>" that
# tune, a library bed id (quiet-math) is a tune of its own, and a cues.md with no music line plays quiet-math (bed_stem).
# Before cues.md exists, brief.md's "- **Music:**" line stands in. Posting never runs this, so a lesson pinned before the
# rule still posts; `variety SLUG`, lint and ready hold a new or rebuilt lesson to it.
def music_of(slug):
    cm = vdir(slug, "03_cues", "cues.md")
    if os.path.exists(cm):
        music = None
        for ln in open(cm, encoding="utf-8").read().splitlines():
            if ln.strip().startswith("music:"):
                music = ln.strip()
        if music is None:
            return "quiet-math"
        m = MUSIC_LINE.match(music)
        if not m:
            return music[len("music:"):].strip() or "?"   # unreadable: shown as written, so the message names it
        return ((m.group(2) or DEFAULT_TUNE).lower() if m.group(1) == "rooms" else m.group(1))
    p = vdir(slug, "01_voice", "brief.md")
    m = re.search(r"(?im)^- \*\*Music:\*\*\s*`?(?:music:\s*)?(?:rooms\s+)?([a-z0-9-]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
    return m.group(1).lower() if m else None


def music_known():
    lib = os.path.join(ROOT, "tools", "music", "library.json")
    return set(TUNES) | ({t["id"] for t in json.load(open(lib))["tracks"]} if os.path.exists(lib) else set())


def posting_line(slug):
    """The posting line around a lesson: the last posted lesson (by its latest post time), then the unposted lessons in
    queue order, with a lesson not yet queued at the back."""
    items = load_queue()["items"]
    order = [i["slug"] for i in items if not i["posts"] and not i.get("hold") and os.path.isdir(vdir(i["slug"]))]
    if slug not in order:
        order.append(slug)
    posted = [i for i in items if i["posts"] and i["slug"] != slug and os.path.isdir(vdir(i["slug"]))]
    last = max(posted, key=lambda i: max((p.get("at", "") if isinstance(p, dict) else "") for p in i["posts"].values()), default=None)
    return ([last["slug"]] if last else []) + order


def music_problems(slug):
    me = music_of(slug)
    if not me:
        return []
    if me not in music_known():
        return [f"music '{me}' is not a tune ({', '.join(TUNES)}) or a bed in tools/music/library.json"]
    line = posting_line(slug)
    n = line.index(slug)
    near = {k: music_of(line[k]) for k in (n - 1, n + 1) if 0 <= k < len(line)}
    free = [t for t in TUNES if t not in near.values()]
    return [f"music '{me}' is also the {'lesson before' if k < n else 'next lesson'} in line's ({line[k]}): "
            f"'music: rooms <tune>' in cues.md, free: {', '.join(free)}" for k, o in near.items() if o == me]


def queue_variety_problems(slug, music=True):
    """Hook pattern, treatment and example (below), and the tune (music_problems) and caption openers
    (opener_problems) when music is True (a new or rebuilt lesson)."""
    return queue_hook_problems(slug) + (music_problems(slug) + opener_problems(slug) if music else [])


# Caption and title openers (Todd, Oct 31, 2026, 11:58 am: "put measures in place to mitigate those risks as much as
# possible", on mass-produced flags; three of five captions had opened "How to ..." and two "How to price a job").
# The first 3 words of the Instagram and TikTok caption and of the YouTube title differ from the same platform's opener on
# the last 4 posted lessons and every unposted lesson in the queue. No captions.json yet: nothing to check.
OPENER_FIELDS = (("instagram", "caption"), ("tiktok", "caption"), ("youtube", "title"))


def opener_of(slug, pl, field):
    f = vdir(slug, "05_render", "captions.json")
    if not os.path.exists(f):
        return None
    text = (json.load(open(f)).get(pl) or {}).get(field) or ""
    words = re.findall(r"[a-z0-9$%']+", text.split("\n")[0].lower())
    return " ".join(words[:3]) if len(words) >= 3 else None


def opener_problems(slug):
    items = load_queue()["items"]
    posted = [i for i in items if i["posts"] and i["slug"] != slug and os.path.isdir(vdir(i["slug"]))]
    posted.sort(key=lambda i: max((p.get("at", "") if isinstance(p, dict) else "") for p in i["posts"].values()))
    others = [i["slug"] for i in posted[-4:]] + [i["slug"] for i in items if not i["posts"] and i["slug"] != slug
                                                 and os.path.isdir(vdir(i["slug"]))]
    out = []
    for pl, field in OPENER_FIELDS:
        me = opener_of(slug, pl, field)
        if not me:
            continue
        same = [o for o in others if opener_of(o, pl, field) == me]
        if same:
            out.append(f"{pl} {field} opens '{me}' like {', '.join(same)}: start it another way")
    return out


def queue_hook_problems(slug):
    me = variety_of(slug)
    out = [f"brief.md has no '- **{label}:**' line (_templates/brief.md)" for key, label in VARIETY_FIELDS if not me[key]]
    if me["hook"] and me["hook"] not in HOOK_PATTERNS:
        out.append(f"hook pattern '{me['hook']}' is not one of {', '.join(sorted(HOOK_PATTERNS))}")
    if me["treatment"] and me["treatment"] not in TREATMENTS:
        out.append(f"treatment '{me['treatment']}' is not one of {', '.join(sorted(TREATMENTS))}")
    if out:
        return out
    items = load_queue()["items"]
    order = [i["slug"] for i in items if not i["posts"] and not i.get("hold") and os.path.isdir(vdir(i["slug"]))]   # held lessons never post (Oct 31)
    if slug not in order:
        order.append(slug)   # a new lesson joins the back of the line
    # the last 3 posted by when they went up, not by their place in queue.json (Oct 31: let-me-think, posted Oct 29, was
    # read as posted today and blocked a lesson)
    pt = lambda i: max((p.get("at", "") if isinstance(p, dict) else "") for p in i["posts"].values())
    posted = [i["slug"] for i in sorted((i for i in items if i["posts"] and i["slug"] != slug and os.path.isdir(vdir(i["slug"]))), key=pt)][-3:]
    n = order.index(slug)
    for other in order[:n] + order[n + 1:] + posted:
        o = variety_of(other)
        kin = derived_from(slug) == other or derived_from(other) == slug   # a short and its parent tell the same story
        if kin and o["hook"] == me["hook"]:
            out.append(f"hook pattern '{me['hook']}' is also its parent's or short's ({other}): a short opens another way")
        if o["example"] and o["example"] == me["example"] and not kin:
            out.append(f"example '{me['example']}' is also {other}'s")
        if other in order and o["hook"] == me["hook"] and o["treatment"] == me["treatment"]:
            out.append(f"same hook pattern and treatment as {other} ({me['hook']}, {me['treatment']})")
    for other in [order[k] for k in (n - 1, n + 1) if 0 <= k < len(order)]:
        if variety_of(other)["hook"] == me["hook"]:
            out.append(f"hook pattern '{me['hook']}' is also the next lesson in line's ({other})")
    out += format_rotation_problems(slug, order, posted)
    out += lane_problems(slug, posted + [o for o in order])
    return out


# Format rotation (Todd, live chat, Oct 30, 2026: three a day, "unique and not following a cookie cutter template";
# _shared/formats.md). Held only for lessons planned after the rule (brief.md carries a named format other than v2), so
# the lessons already gated keep their place: the lesson before it in line is not the same format, and no format fills
# more than 2 of the 6 lessons around it in line (3 a day: no format twice in a posting day, at most twice in two days).
def rotation_shape(slug):
    """What rotates: a story lesson's '- **Shape:**' line (moment, receipt, two-shops, myth-three, scenario, case, ...),
    any other lesson's format."""
    f = lesson_format(slug)
    if f == "short":
        return "short"   # at most one short in a posting day (the day window below)
    if f in GUIDE_FORMATS:
        p = vdir(slug, "01_voice", "brief.md")
        m = re.search(r"(?im)^- \*\*Shape:\*\*\s*`?([a-z0-9-]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
        return "story:" + (m.group(1).lower() if m else "unnamed")
    return f


def format_rotation_problems(slug, order, posted):
    p = vdir(slug, "01_voice", "brief.md")
    txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    m = re.search(r"(?im)^- \*\*Format:\*\*\s*`?([a-z0-9-]+)`?", txt)
    if not m or m.group(1).lower() in ("v2", "v1"):
        return []
    me = lesson_format(slug)
    if me == "v1":
        return [f"format '{m.group(1)}' is not one of {', '.join(FORMATS)}"]
    line = posted + [o for o in order]
    n = line.index(slug)
    out = []
    # A story lesson (REBUILD.md: "formats become a menu, not a cage"; "variety checks stay only where they stop repeats")
    # rotates on its Shape line (the skeleton the engine picked for this story), not on "story", which every new-line lesson is.
    me = rotation_shape(slug)
    if n > 0 and rotation_shape(line[n - 1]) == me:
        out.append(f"format '{me}' is also the lesson before it in line's ({line[n - 1]})")
    # four a day (Todd, Oct 31, 2026, 9:08 am; 11:58 am: "put measures in place to mitigate those risks"): no format
    # twice in a posting day (the last 4 in line) and at most twice in two days (the last 8)
    day = line[max(0, n - 3):n + 1]
    if sum(1 for o in day if rotation_shape(o) == me) > 1:
        out.append(f"format '{me}' is twice in one posting day ({', '.join(day)})")
    window = line[max(0, n - 7):n + 1]
    if sum(1 for o in window if rotation_shape(o) == me) > 2:
        out.append(f"format '{me}' fills more than 2 of the last 8 in line ({', '.join(window)})")
    return out


# Lanes (Todd, live chat, Nov 1, 2026, 9:01 am: "go with your recommendation", on 8:41 am: "what do you think about pivoting
# into specifically focusing and purposing new AI innovations for tradespeople and their businesses?"). brief.md names one
# lane, `- **Lane:** ai` or `core` (no line reads core). video/config.json "lanes": mode "alternate" puts the two lanes
# turn about in the posting line (2 of 4 a day each) for the test; mode "ai" or "core" makes every new lesson that lane.
LANES = ("ai", "core")


def lesson_lane(slug):
    p = vdir(slug, "01_voice", "brief.md")
    m = re.search(r"(?im)^- \*\*Lane:\*\*\s*`?([a-z]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
    return m.group(1).lower() if m else "core"


def lane_cfg():
    return json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8")).get("lanes", {"mode": "core"})


def lane_problems(slug, line):
    p = vdir(slug, "01_voice", "brief.md")
    txt = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    if not re.search(r"(?im)^- \*\*Lane:\*\*", txt):
        return []
    me, mode = lesson_lane(slug), lane_cfg().get("mode", "core")
    if me not in LANES:
        return [f"lane '{me}' is not one of {', '.join(LANES)}"]
    n = line.index(slug)
    if mode == "alternate" and n > 0 and lesson_lane(line[n - 1]) == me:
        return [f"lane '{me}' is also the lesson before it in line's ({line[n - 1]}); the lane test alternates"]
    if mode in LANES and me != mode:
        return [f"lane '{me}': video/config.json lanes mode is '{mode}'"]
    return []


def cmd_lanes():
    """Which lane the next lesson is, then each lane's numbers from research/metrics (newest read per platform):
    views, shares + saves + follows per 1,000 views, Facebook 3 s holds per 100 views, TikTok average watch."""
    cfg = lane_cfg()
    line = posting_line("__none__")[:-1]
    last = line[-1] if line else None
    mode = cfg.get("mode", "core")
    nxt = mode if mode in LANES else ("core" if last and lesson_lane(last) == "ai" else "ai")
    print(f"lanes: mode {mode}" + (f" until {cfg['until']}" if cfg.get("until") else "") + f"; make next: {nxt}"
          + (f" (last in line {last}, {lesson_lane(last)})" if last else ""))
    tot = {l: {"lessons": 0, "views": 0, "acts": 0, "fbv": 0, "fb3": 0, "tt": []} for l in LANES}
    for f in sorted(glob.glob(os.path.join(HERE, "research", "metrics", "2*.json"))):
        d = json.load(open(f, encoding="utf-8")); slug = d.get("slug") or os.path.basename(f)[:-5]
        if not os.path.isdir(vdir(slug)):
            continue
        last_p = {}
        for r in d.get("reads", []):
            for pl, v in r.get("platforms", {}).items():
                last_p.setdefault(pl, {}).update({k: x for k, x in v.items() if isinstance(x, (int, float))})
        t = tot[lesson_lane(slug)]; t["lessons"] += 1
        for pl, v in last_p.items():
            t["views"] += v.get("views", 0); t["acts"] += sum(v.get(k, 0) for k in ("shares", "saves", "follows"))
            if pl == "facebook" and "threeSecViews" in v:
                t["fbv"] += v.get("views", 0); t["fb3"] += v["threeSecViews"]
            if pl == "tiktok" and "avgWatchS" in v:
                t["tt"].append(v["avgWatchS"])
    for l, t in tot.items():
        per = 1000 * t["acts"] / t["views"] if t["views"] else 0
        hold = 100 * t["fb3"] / t["fbv"] if t["fbv"] else 0
        tt = sum(t["tt"]) / len(t["tt"]) if t["tt"] else 0
        print(f"lane {l}: {t['lessons']} lessons, {t['views']} views, shares+saves+follows {t['acts']} ({per:.1f} per 1,000),"
              f" FB 3 s holds {hold:.0f} per 100, TikTok avg watch {tt:.1f} s")


def cmd_tunes(slug=None):
    """The room tunes (name, key, tempo, chords). With a slug: its music now, its neighbours' in line, and the free tunes."""
    for name, t in TUNES.items():
        print(f"{name:8s} {t['key']:20s} {t['bpm']:3d} BPM  {t['names']}" + ("  (plain 'music: rooms')" if name == DEFAULT_TUNE else ""))
    if slug:
        line = posting_line(slug); n = line.index(slug)
        near = [(line[k], music_of(line[k])) for k in (n - 1, n + 1) if 0 <= k < len(line)]
        print(f"{slug}: music {music_of(slug)}; in line next to " + (", ".join(f"{o} ({m})" for o, m in near) or "nothing")
              + "; free: " + ", ".join(t for t in TUNES if t not in {m for _, m in near}))


def cmd_variety(slug=None):
    """No two queued lessons alike (rules above). With a slug: that lesson against the queue, the tune included. Without:
    every unposted lesson; they are pinned, so a tune shared with a neighbour is a note for its rebuild, not a FAIL."""
    slugs = [slug] if slug else [i["slug"] for i in load_queue()["items"] if not i["posts"]]
    bad = 0
    for s_ in slugs:
        probs = queue_variety_problems(s_, music=bool(slug))
        v = variety_of(s_)
        notes = [] if slug else music_problems(s_)
        if probs:
            bad += 1
            print(f"variety: FAIL {s_}: " + "; ".join(probs))
        else:
            print(f"variety: PASS {s_} ({v['hook']}, {v['treatment']}, {v['example']}, music {music_of(s_)})"
                  + (" note: " + "; ".join(notes) + " (pinned: its rebuild picks another tune)" if notes else ""))
    if bad:
        sys.exit(1)

# The hook rules in code (IMPROVE 00a and 00c; Todd, Oct 29, 2026: "get this fixed today"; style board target spec): the
# picture changes within 1 s and at least twice in the first 3 s, the host is on screen by 3 s, the spoken hook is 9 to 12
# words and lands in the first 3 s, and the whole lesson runs 75 s or less (end card included).
# A 9 to 12 word line takes about 3.3 s at our fastest natural pace (lesson 3), so the spoken hook must be said by 3.6 s;
# the on-screen hook carries the first 3 s from frame 0.
HOOK = {"first_change_by": 1.0, "changes_in": 3.0, "changes_min": 2, "host_by": 3.0, "words": (9, 12), "said_by": 3.6, "max_seconds": 75.0}
# Lead Clinic v2 (Todd's yes, Oct 29, 2026, 12:14 pm; research/viral-formats-2026-10.md; _shared/voice.md): a lesson whose
# brief.md has "- **Format:** v2" runs 40 to 50 s with the end card (55 s hard cap), 100 to 135 spoken words, opens on a
# moment (no percent, no source, no call-out), has no tail after the answer, and puts the send line on the end card.
V2 = {"min_seconds": 40.0, "max_seconds": 55.0, "words": (100, 135)}
V2_TAIL = [(r"(?i)\bpart people skip\b", "the turn line"), (r"(?i)\bhonest note\b", "a spoken honest note"),
           (r"(?i)\b(send|save) this\b", "a spoken send or save line"), (r"(?i)\b(like and (follow|subscribe)|follow (us|me|for)|subscribe|comment (below|yes|\w+ below)|drop a comment)\b", "a spoken like, follow or comment ask")]
V2_CALLOUT = re.compile(r"(?i)^(trade|hvac|plumbing|roofing|electrical|contractor|home service|small business)?\s*(owners?|pros|contractors|plumbers|electricians|roofers),")
V2_SOURCEWORDS = {"percent", "percentage", "study", "survey", "report", "data", "according"}


# Formats (Todd, live chat, Oct 30, 2026: "Ensure that the videos are unique and not following a cookie cutter template so
# we do not get flagged by the platforms for mass produced AI content"; _shared/formats.md). A format is the lesson's
# skeleton: its beats, its length and its word count. "v2" is the Lead Clinic (clinic). Every format keeps the v2 script
# rules (drop-in opener, no tail, button echoes the hook); only the bands differ.
FORMATS = {
    "clinic":     {"min_seconds": 40.0, "max_seconds": 55.0, "words": (100, 135)},
    "quick-math": {"min_seconds": 20.0, "max_seconds": 34.0, "words": (45, 80)},
    "fix-this":   {"min_seconds": 25.0, "max_seconds": 42.0, "words": (60, 100)},
    "two-shops":  {"min_seconds": 35.0, "max_seconds": 52.0, "words": (85, 125)},
    "myth-three": {"min_seconds": 30.0, "max_seconds": 48.0, "words": (75, 115)},
    "scenario":   {"min_seconds": 42.0, "max_seconds": 62.0, "words": (110, 160)},
    # Depth formats (Todd, Oct 30, 2026, 4:01 pm: "go with your recommendation on everything. Drive this hard, and let's
    # get real good videos out"; research/topics-2026-10-30.md): a playbook part teaches one step of a setup; a case walks
    # one real setup end to end.
    "playbook":   {"min_seconds": 40.0, "max_seconds": 58.0, "words": (100, 150)},
    "case":       {"min_seconds": 70.0, "max_seconds": 92.0, "words": (180, 245)},
    # The story desk (Todd, live chat, Nov 2, 2026, 12:28 pm: "find really, really interesting new stories about trades in AI
    # software implementation"; _shared/investigative.md): one documented story, receipts on screen, a setup card.
    "dispatch":   {"min_seconds": 45.0, "max_seconds": 70.0, "words": (115, 180)},
    # The new line (Todd, live chat, Nov 2, 2026, 8:49 pm, PRINCIPLES.md: "We can elaborate more and relax restrictions on
    # number of words. Storytelling is the most important skill"; REBUILD.md "Relaxed"): a story from the story desk
    # (00_story/story.md), told whole. Its word band, the spoken hook's length and the opening rules are guides (NOTE lines),
    # not gates; the retell and read-aloud gates judge it. Length stays a hard band. The ceiling dropped from 90 s to 70 s
    # (Todd, live chat, Nov 7, 2026, 9:27 am, the shorter middle: after-hours-robot ran 87.6 s and was watched 29 s); the
    # aim is 50 to 65 s (STORY_AIM, a NOTE). Lessons queued before keep their pins.
    "story":      {"min_seconds": 40.0, "max_seconds": 70.0, "words": (110, 175)},
    # A short (Todd, live chat, Nov 7, 2026, 8:33 am: "Go", recommendation 3): one fix cut from a queued story lesson,
    # brief.md "- **Derived from:** `<parent slug>`". 7-day test to Nov 14 (_shared/formats.md "Short").
    "short":      {"min_seconds": 18.0, "max_seconds": 35.0, "words": (45, 95)},
    # The proven idea lane (Todd, live chat, Nov 7, 2026, 11:58 am: "We can find what is actually working out there and
    # create our own videos based on that."; 12:08 pm: "Go"): our own version of an outlier pattern in research/PROVEN.md,
    # 50 to 65 s (a hard band), with the send moment and the copy check (_shared/formats.md "Proven").
    "proven":     {"min_seconds": 50.0, "max_seconds": 65.0, "words": (120, 170)},
}
# Formats whose word band, spoken hook length and drop-in rules are guides, not errors (REBUILD.md "Relaxed").
GUIDE_FORMATS = {"story", "short", "proven"}
FORMAT_ALIASES = {"v2": "clinic"}
# Engine v4 (Todd, live chat, Nov 9, 2026, 2:11 pm: "I want you to take the reigns and I want you to modify this engine so
# that we go viral. Make all the necessary changes"; coo/DECISIONS-2026-11-09.md; _shared/formats.md "v4"). Three short
# formats a stranger can judge: verdict (a real dispute, the viewer calls it), invoice (where the money goes, line by
# line), call (a phone call acted out, said once to be a reenactment). 18 to 35 s, the whole frame, no host lecture, no
# end card (a 1 s tail). Why: viewers gave every earlier lesson 3 to 29 s whatever its length, and no gate score moved
# views (research/STUDY-2026-11-08.md). Four gates (V4_GATES); the checks are lint_v4.
V4_FORMATS = {"verdict", "invoice", "call"}
for _f in V4_FORMATS:
    FORMATS[_f] = {"min_seconds": 18.0, "max_seconds": 35.0, "words": (45, 95)}
V4_FROM = "2026-11-30"
V4_GATES = ("qa", "facts", "render-critic", "viewer")
V4_TAIL = 1.0            # cmd_cues: seconds after the last word (no end card)
V4_SAFE = (40, 250, 1040, 1440)   # x0, y0, x1, y1: clear of the platform's top bar and bottom caption and buttons
V4_SIDE = (930, 1040)    # right of x 930 is clear only above y 1040 (the like, comment and share buttons sit below)
V4_HOLD_MAX = 4.0        # no set of words stands unchanged longer than this
V4_PAYOFF_BY = 0.40      # the cue marked [payoff] starts by this share of the runtime
V4_TEXT_FLOOR = 42       # ink height in frame units
V4_LABELS = {"instagram": ("aiLabel", True), "facebook": ("aiLabel", True), "tiktok": ("aiGenerated", True), "youtube": ("aiUse", False)}
PAYOFF_MARK = re.compile(r"\[payoff\]", re.I)


def is_v4(slug):
    return lesson_format(slug) in V4_FORMATS


def lesson_format(slug):
    """The lesson's format from brief.md's '- **Format:**' line ('v2' reads as clinic); 'v1' for lessons planned before
    Oct 29, 2026 with no Format line."""
    p = vdir(slug, "01_voice", "brief.md")
    m = re.search(r"(?im)^- \*\*Format:\*\*\s*`?([a-z0-9-]+)`?", open(p, encoding="utf-8").read()) if os.path.exists(p) else None
    f = FORMAT_ALIASES.get(m.group(1).lower(), m.group(1).lower()) if m else "v1"
    return f if f in FORMATS else "v1"


def is_modern(slug):
    """Every named format (clinic and the newer ones) runs the v2 script rules; only v1 lessons keep the old ones."""
    return lesson_format(slug) != "v1"


# Source-matched experiments (Todd, live chat, Nov 8, 2026, 8:25 pm: "#1 let's not keep strict rules or a standard template.
# We need to experiment to see what works. We'll keep testing different viral videos to learn what works."). A proven
# lesson whose brief.md says `- **Match:** source` takes its source's structure: its length (`- **Source length:** N s`,
# within 20%, plus our end card), its beat order, whether it answers. Off for it: the send card and the send gate, the
# hard hook (12 words by 3.6 s, a 5 to 8 word cover), the opening move rotation and the 3 new set pieces. Every honesty
# rule stays: facts, facts on captions, EXAMPLE tags, the copy check, our own art and words, render critic, design.
MATCH_LINE = re.compile(r"(?im)^- \*\*Match:\*\*\s*source\b")
SOURCE_LEN = re.compile(r"(?im)^- \*\*Source length:\*\*\s*(\d+(?:\.\d+)?)\s*s\b")


def matched_band(seconds, end_card=3.1):
    return (round(max(8.0, seconds * 0.8), 2), round(seconds * 1.2 + end_card, 2))


def source_matched(slug):
    if lesson_format(slug) != "proven":
        return False
    bp = vdir(slug, "01_voice", "brief.md")
    return os.path.exists(bp) and bool(MATCH_LINE.search(open(bp, encoding="utf-8").read()))


def length_band(slug):
    if source_matched(slug):
        m = SOURCE_LEN.search(open(vdir(slug, "01_voice", "brief.md"), encoding="utf-8").read())
        if not m:
            raise SystemExit(f"ERROR {slug}: a source-matched lesson needs '- **Source length:** <seconds> s' in brief.md")
        return matched_band(float(m.group(1)))
    f = FORMATS.get(lesson_format(slug))
    return (f["min_seconds"], f["max_seconds"]) if f else (45.0, HOOK["max_seconds"])


CFG_VIDEO_END = json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8"))["video"].get("endCardMinSeconds", 3.5)


def script_problems(slug, send_line=None, notes=None):
    """The v2 script rules in code (_shared/voice.md, Lead Clinic v2). Returns a list of problems ([] for a v1 lesson).
    For a GUIDE_FORMATS lesson the craft rules that used to squeeze sentences (word band, drop-in, echo) go to `notes`
    (a list the caller prints as NOTE) instead of the problems; the voice and honesty rules stay errors."""
    if not is_modern(slug):
        return []
    takes = takes_of(slug)
    words = [w for tk in takes for w in spoken_words(tk)]
    out = []
    guide = notes if notes is not None else []
    soft = guide if lesson_format(slug) in GUIDE_FORMATS else out
    lo, hi = FORMATS[lesson_format(slug)]["words"]
    if not lo <= len(words) <= hi:
        soft.append(f"{len(words)} spoken words ({lo} to {hi})")
    # Length before any voice is made (Todd, Nov 1, 2026: the lunch slot went empty; ai-night-quote was voiced long and cut
    # after). Our takes run 147 to 175 words a minute, gaps included (14 lessons, median about 159): at 160 the lesson plus
    # the end card must fit its format's top length, or it is cut before any credits are spent.
    top = FORMATS[lesson_format(slug)]["max_seconds"]
    est = len(words) * 60 / 160 + CFG_VIDEO_END
    wp = vdir(slug, "02_transcript", "words.json")
    voiced = os.path.exists(wp) and json.load(open(wp)).get("source", "estimate") != "estimate"
    if est > top and not voiced:   # once the voice exists, its real length is judged by hook and check, not this estimate
        out.append(f"about {est:.1f} s at 160 words a minute with the end card, over {lesson_format(slug)}'s {top:.0f} s;"
                   f" cut about {int((est - top) * 160 / 60) + 1} words before voicing")
    text = " ".join(TAG.sub(" ", tk) for tk in takes)
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", " ".join(text.split())) if s.strip()]
    hook, n = [], 0
    for s in sents:
        hook.append(s); n += len(s.split())
        if n >= HOOK["words"][0]:
            break
    hook_text = " ".join(hook)
    hw = {norm(w) for w in hook_text.split()}
    sources = set()
    fp = vdir(slug, "01_voice", "facts.json")
    if os.path.exists(fp):
        for k, v in json.load(open(fp)).items():
            if isinstance(v, dict) and ("url" in v or "publisher" in v):
                sources |= {norm(k)} | ({norm(v["publisher"].split()[0])} if v.get("publisher") else set())
    bad = sorted((hw & (V2_SOURCEWORDS | sources)) - {""})
    if bad:
        soft.append(f"the drop-in names a percent or a source ({', '.join(bad)}): open on a moment, the proof comes later")
    if V2_CALLOUT.search(hook_text):
        soft.append("the drop-in opens on an audience call-out: put the trade inside the scene")
    for rx, what in V2_TAIL:
        m = re.search(rx, text)
        if m:
            out.append(f"{what} in the script (\"{m.group(0)}\"): v2 ends on the button, the send line rides on the end card")
    stop = {"that", "this", "with", "your", "they", "them", "have", "what", "when", "then", "about", "there", "their", "just", "from", "into", "says"}
    last = {norm(w) for w in sents[-1].split()} if sents else set()
    if not {w for w in hw & last if len(w) >= 4 and w not in stop}:
        soft.append("the button does not echo the drop-in (repeat one of its words in the last sentence)")
    # Sound human (Todd, Oct 30, 2026, 1:12 pm: the price-a-job voice "starts whispering"; "about sixteen sixty-seven"
    # sounds weird; 4:01 pm: "go with your recommendation on everything"). Tags must be something a listener hears: a
    # staging or softness tag makes Eleven v4 go quiet (ElevenLabs tag guidance). Two tags a script at most. An exact
    # number is said plainly; a rounded one says so ("call it").
    tags = [t.lower() for tk in takes for t in TAG.findall(tk)]
    soft = [t for t in tags if SOFT_TAG.search(t)]
    if soft:
        out.append(f"soft or staging tag {', '.join(sorted(set(soft)))}: it makes the voice go quiet; use no tag or [conversational]")
    if len(tags) > 2:
        out.append(f"{len(tags)} delivery tags (2 a script at most; pace is a writing job)")
    m = ABOUT_EXACT.search(text)
    if m:
        out.append(f"\"{m.group(0)}\": an exact number takes no \"about\"; say it plainly or round it (\"call it seventeen hundred\")")
    if send_line is not None and not source_matched(slug) and not re.search(r"(?i)\bsend this to (whoever|your)\b", send_line or ""):   # a source-matched experiment has no send (Todd, Nov 8, 8:25 pm)
        out.append(f"SCENE.sendLine is {send_line!r}: the end card needs a send line that names a role")
    return out


def cmd_script(slug):
    if not is_modern(slug):
        print(f"script: {slug} is a v1 lesson (no Format: v2 line in brief.md); the v1 12-point check applies")
        return
    sl = None
    sj = vdir(slug, "04_scene", "scene.js")
    if os.path.exists(sj):
        m = re.search(r"sendLine:\s*'([^']*)'", open(sj, encoding="utf-8").read())
        sl = m.group(1) if m else ""
    notes = []
    bad = script_problems(slug, sl, notes)
    if os.path.basename(slug)[:10] >= STUDIO_V3_FROM and not slug.endswith(HOOKB_SUFFIX):   # before any voice is made
        bad += opener_move_problems(slug)
    if proven_hook_hard(slug):
        sp = vdir(slug, "01_voice", "script.md")
        hn = script_hook_words("\n".join(ln for ln in open(sp, encoding="utf-8").read().splitlines() if not ln.lstrip().startswith(("#", "<!--", ">")))) if os.path.exists(sp) else 0
        if hn > HOOK["words"][1]:
            bad.append(f"the spoken hook is {hn} words (12 or fewer by 3.6 s for a proven lesson; {PROVEN_HOOK_NOTE})")
    takes = takes_of(slug)
    nw = sum(len(spoken_words(tk)) for tk in takes)
    for x in notes:
        print("NOTE script (a guide, not a gate; REBUILD.md Relaxed): " + x)
    for x in bad:
        print("ERROR script: " + x)
    print("script: " + ("FAIL" if bad else "PASS") + f" v2, {nw} words in {len(takes)} takes" + ("" if sl is None else f", end card send line {sl!r}"))
    if bad:
        sys.exit(1)
# ---------------------------------------------------------------- the send moment and the shorter middle
# Todd, live chat, Nov 7, 2026, 9:27 am: "Write the next prompt to make adjustments and fix so the next video improves."
# (his yes to both fixes; coo/DECISIONS-2026-11-07.md "Why after-hours-robot stalled"). after-hours-robot and
# lsa-missed-calls both held viewers (skip 26% and 29%) and both stalled near 1,280 IG views with 0 or 1 share: they
# passed the hold test and failed the send test. So every story lesson and short from SEND_FROM on carries one
# forwardable thing on screen (the exact text, call script or setting) for a named person in the owner's shop, held
# still long enough to screenshot, and it lands before the halfway point.
SEND_FROM = "2026-11-19"   # lessons dated from here on (ask-chatgpt and later); queued lessons keep their pins
SEND_HOLD = 2.5            # seconds the send card holds still, no motion over it
STORY_AIM = (50.0, 65.0)   # a story lesson's aim (a NOTE); the hard ceiling is FORMATS["story"]
SEND_BRIEF = re.compile(r"(?im)^- \*\*Send:\*\*[ \t]*(.*?)[ \t]*$")
SEND_GROUP = re.compile(r"(?i)\b(contractors|owners|everyone|anyone|anybody|network|friends|people|followers|team|crew|everybody|you)\b")
SEND_MARK = re.compile(r"\[send\]", re.I)
SEND_STILL_LEVEL, SEND_STILL_SHARE = 24, 0.01   # a sample moves when 1% of the card's pixels change by 24+ levels
END_TAIL = 3.1   # cmd_cues: the end card's tail after the last word
SEND_PIX_JS = """(r) => { const c = document.getElementById('c');
  const x = Math.max(0, Math.floor(r[0])), y = Math.max(0, Math.floor(r[1]));
  const w = Math.max(1, Math.min(1080 - x, Math.ceil(r[2] - x))), h = Math.max(1, Math.min(1920 - y, Math.ceil(r[3] - y)));
  if (!window.__sp) window.__sp = document.createElement('canvas');
  window.__sp.width = w; window.__sp.height = h; const g = window.__sp.getContext('2d');
  g.clearRect(0, 0, w, h); g.drawImage(c, x, y, w, h, 0, 0, w, h);
  const d = g.getImageData(0, 0, w, h).data, out = [];
  for (let j = 0; j < h; j += 3) for (let i = 0; i < w; i += 3) { const k = (j * w + i) * 4; out.push((d[k] + d[k + 1] + d[k + 2]) / 3 | 0); }
  return out; }"""


# ---------------------------------------------------------------- Todd's five calls (live chat, Nov 9, 2026, 7:33 am: "Recs")
# The viewer gate's calibration on damage-or-not and hail-or-wear found five of our own rules confusing strangers
# (coo/DECISIONS-2026-11-09.md). For lessons dated from RECS_FROM on: (1) room changes are plain cuts on the beat or a
# simple slide, never a full-screen move or a black frame; (2) a made-up scene is said once (the voice sets it up or one
# small MADE-UP EXAMPLE line on its first frame) and EXAMPLE tags sit only beside made-up numbers; (3) no SNOW name tag
# (the player); (4) no minimum of new set pieces, only no reuse from the last two lessons; (5) the send card builds line
# by line as it is spoken, holds about 3 s once full, then moves on, and shows again on the end card (SCENE.endSend).
RECS_FROM = "2026-11-29"
CUT_MOVES = ("cut", "slide")
SEND_HOLD_MAX = 4.0   # call 5: the full card holds about 3 s, at most this, then the video moves on
MADE_UP = "MADE-UP EXAMPLE"


def recs_apply(slug):
    return os.path.basename(slug)[:10] >= RECS_FROM


def move_problems(scene_text):
    """Call 1: SCENE.transitions names only 'cut' or 'slide', and k.cut takes no kind but 'cut'."""
    out = []
    m = re.search(r"transitions\s*[:=]\s*\{([^}]*)\}", scene_text or "")
    bad = sorted({v for v in re.findall(r":\s*['\"](\w+)['\"]", m.group(1)) if v not in CUT_MOVES}) if m else []
    if bad:
        out.append(f"SCENE.transitions uses {', '.join(bad)}: a room change is a plain cut on the beat or 'slide' (call 1, viewers read the moves as broken renders)")
    kinds = sorted({k_ for k_ in re.findall(r"k\.cut\([^)]*?kind:\s*['\"](\w+)['\"]", scene_text or "") if k_ != "cut"})
    if kinds:
        out.append(f"k.cut kind {', '.join(kinds)}: a shot change is a plain cut (drop the kind; call 1)")
    return out


def example_tag_problems(samples, step):
    """Call 2, on lint's samples [(t, [(text, tag, x0, y0, x1, y1, a)])]: an EXAMPLE tag on screen while no scene text
    beside it carries a number, and the MADE-UP EXAMPLE line shown in more than one stretch."""
    out, lone, runs, prev = [], [], 0, None
    for t, xs in samples:
        texts = [x[0].strip() for x in xs if x[1] == "scene"]
        # a number beside it: a digit outside a list number ("1  THE HOUSE" is a step, not a made-up number)
        if "EXAMPLE" in (x.upper() for x in texts) and not any(re.search(r"\d", re.sub(r"^\d+[.)]?\s+", "", x)) for x in texts if x.upper() != "EXAMPLE"):
            lone.append(t)
        on = MADE_UP in (x.upper() for x in texts)
        if on and (prev is None or t - prev > step * 1.5):
            runs += 1
        prev = t if on else prev
    if lone:
        out.append(f"an EXAMPLE tag with no number beside it at {lone[0]:.2f} s ({len(lone)} samples): tags only on made-up numbers; say a made-up scene once (the voice, or k.madeUp on its first frame)")
    if runs > 1:
        out.append(f"the MADE-UP EXAMPLE line shows {runs} times: once, on the first made-up frame")
    return out


def recs_send_scene_problems(scene_text):
    """Call 5 in the scene: the card's body lines arrive as spoken (k.sendCard linesOn) and the end card shows it again
    (SCENE.endSend)."""
    out = []
    if not re.search(r"\blinesOn\s*:", scene_text or ""):
        out.append("the send card has no linesOn: build it line by line as each line is spoken (call 5)")
    if re.search(r"k\.sendCard\([^;]*?\bexample:\s*true", scene_text or ""):
        out.append("the send card carries an EXAMPLE tag: it is the thing to send, not a made-up number (call 2)")
    if not re.search(r"\bendSend\s*:", scene_text or ""):
        out.append("no SCENE.endSend: show the send card's lines again on the end card (call 5)")
    return out


def send_still_seconds(samples, step):
    """samples: [(t, signature, pixels)] inside the send window, in time order. The longest run in which the same scene
    texts sit in the same places and the card's pixels stay within SEND_STILL_SHARE of the run's first sample."""
    best, run, anchor, sig0 = 0.0, 0, None, None
    for _, sig, px in samples:
        same = bool(sig) and sig == sig0 and anchor is not None and len(px) == len(anchor) and \
            sum(1 for a_, b_ in zip(px, anchor) if abs(a_ - b_) >= SEND_STILL_LEVEL) <= SEND_STILL_SHARE * max(1, len(px))
        if same:
            run += 1
        else:
            run, anchor, sig0 = (1, px, sig) if sig else (0, None, None)
        best = max(best, run * step)
    return round(best, 2)


def send_applies(slug):
    return os.path.basename(slug)[:10] >= SEND_FROM and lesson_format(slug) in GUIDE_FORMATS and not source_matched(slug)


def _phrase(s):
    s = re.sub(r"[^a-z0-9 ]", " ", str(s).lower())
    s = " ".join(s.split())
    return re.sub(r"^(the|your|my|our) ", "", s)


def send_of(text):
    """brief.md's Send line as (who, thing), or None. Form: '- **Send:** <who it goes to>: <the thing on screen>'."""
    m = SEND_BRIEF.search(text or "")
    if not m:
        return None
    val = m.group(1).strip().strip("`")
    who, sep, thing = val.partition(": ")
    return (who.strip(), thing.strip()) if sep else (val, "")


def send_brief_problems(text):
    """The Send line exists, names one person in the owner's shop by role (never a group or the viewer) and the exact
    thing on screen (3 words or more)."""
    s = send_of(text)
    if s is None:
        return ["brief.md has no '- **Send:** <who it goes to>: <the thing on screen>' line"]
    who, thing = s
    out = []
    if not who or not thing:
        out.append(f"the Send line '{(who + ' ' + thing).strip()[:60]}' needs both parts: '<who it goes to>: <the thing on screen>'")
    if who and (len(who.split()) < 2 or SEND_GROUP.search(who)):
        out.append(f"the Send line's person '{who}' must be one person in the owner's shop by role (whoever answers the phones, "
                   f"the office manager, a partner), never a group or the viewer")
    if thing and len(thing.split()) < 3:
        out.append(f"the Send line's thing '{thing}' must name the exact text, call script or setting on screen")
    return out


def send_card_problems(who, send_line):
    """The end card's send line names the same person as brief.md's Send line, word for word."""
    if not who:
        return []
    if not send_line:
        return [f"the end card has no send line; it must name {who!r}"]
    if _phrase(who) not in _phrase(send_line):
        return [f"the end card's send line {send_line!r} does not name the Send line's person {who!r}"]
    return []


def send_cue_problems(doc, still=None, recs=False):
    """One cue in cues.md carries [send] (cues.json 'send': true). It runs SEND_HOLD s or more before the next cue, holds
    still that long (still: seconds the card held with no motion over it, measured by lint; None skips that part), and
    starts before the halfway point of the runtime, end card included."""
    cues, dur = doc.get("cues", []), float(doc.get("duration", 0))
    sends = [c for c in cues if c.get("send")]
    if len(sends) != 1:
        return [f"{len(sends)} cues marked [send] in cues.md (exactly one: the cue where the send card goes up)"]
    c = sends[0]
    t0 = float(c.get("t", 0))
    nxt = min([float(d["t"]) for d in cues if float(d.get("t", 0)) > t0 + 1e-6] + [dur - END_TAIL])
    out = []
    if nxt - t0 < SEND_HOLD - 1e-6:
        out.append(f"the send cue '{c['id']}' runs {nxt - t0:.2f} s before the next cue ({SEND_HOLD} s or more to screenshot)")
    if still is not None and still < SEND_HOLD - 1e-6:
        out.append(f"the send card holds still {still:.2f} s (needs {SEND_HOLD} s with no motion over it)")
    if recs and still is not None and still > SEND_HOLD_MAX + 1e-6:
        out.append(f"the full send card sits still {still:.2f} s (call 5: about 3 s once full, at most {SEND_HOLD_MAX} s; build it line by line as spoken, then move on)")
    if dur and t0 >= dur / 2:
        out.append(f"the send moment starts at {t0:.2f} s, after the halfway point ({dur / 2:.2f} s of {dur:.2f} s): move the payoff earlier")
    return out


def send_match_problems(send, review):
    """The send gate's reviewer, who never saw the brief, named the person and the thing on screen from the video alone:
    its score.person shares a role word with the Send line's person, and score.thing shares at least half the Send line's
    thing words (4+ letters)."""
    if not send:
        return ["no Send line in brief.md"]
    sc = (review or {}).get("score") or {}
    who, thing = send
    stop = {"whoever", "your", "their", "that", "this", "with", "from", "into", "what", "when", "shop", "screen"}
    words = lambda s: {w for w in _phrase(s).split() if len(w) >= 4 and w not in stop}
    out = []
    p, t = sc.get("person") or "", sc.get("thing") or ""
    if not p or p.lower() == "none" or not (words(who) & words(p)):
        out.append(f"the send reviewer named {p or 'no one'!r}, not the Send line's person {who!r}")
    need = words(thing)
    got = need & words(t)
    if not t or not need or len(got) * 2 < len(need):
        out.append(f"the send reviewer named the thing {t or 'nothing'!r}, not the Send line's {thing!r} ({len(got)} of {len(need)} words)")
    return out


def send_problems(slug, send_line=None, still=None, review=False):
    """Every code check of the send moment for one lesson (lint runs it with the measured hold; ready with the reviewer)."""
    if not send_applies(slug):
        return []
    bp = vdir(slug, "01_voice", "brief.md")
    text = open(bp, encoding="utf-8").read() if os.path.exists(bp) else ""
    out = send_brief_problems(text)
    send = send_of(text)
    if send_line is None:
        sj = vdir(slug, "04_scene", "scene.js")
        m = re.search(r"sendLine:\s*'([^']*)'", open(sj, encoding="utf-8").read()) if os.path.exists(sj) else None
        send_line = m.group(1) if m else ("" if os.path.exists(sj) else None)
    if send and send_line is not None:
        out += send_card_problems(send[0], send_line)
    cj = vdir(slug, "03_cues", "cues.json")
    if os.path.exists(cj):
        out += send_cue_problems(json.load(open(cj)), still, recs=recs_apply(slug))
    if recs_apply(slug):
        sj = vdir(slug, "04_scene", "scene.js")
        if os.path.exists(sj):
            out += recs_send_scene_problems(open(sj, encoding="utf-8").read())
    if review:
        rp = vdir(slug, "05_render", "reviews", "send.json")
        out += send_match_problems(send, json.load(open(rp)) if os.path.exists(rp) else None) if send else []
    return out


def cmd_sendcheck(slug):
    bad = send_problems(slug, review=os.path.exists(vdir(slug, "05_render", "reviews", "send.json")))
    for x in bad:
        print("ERROR send: " + x)
    print("sendcheck: " + ("FAIL" if bad else "PASS") + ("" if send_applies(slug) else f" (not a send lesson: before {SEND_FROM} or not story/short)"))
    if bad:
        sys.exit(1)


def story_aim_note(slug, seconds):
    if lesson_format(slug) == "story" and not STORY_AIM[0] <= seconds <= STORY_AIM[1]:
        return f"the lesson runs {seconds:.1f} s (aim {STORY_AIM[0]:.0f} to {STORY_AIM[1]:.0f} s for a story lesson)"
    return ""


# ---------------------------------------------------------------- the proven idea lane and its copy check
# Todd, live chat, Nov 7, 2026, 11:58 am: "Can't we examine top performing videos on youtube shorts and make our own
# variation? ... We can find what is actually working out there and create our own videos based on that."; 12:08 pm: "Go".
# Ideas and formats aren't owned; words, footage and art are. So a proven lesson takes an outlier's pattern from
# research/PROVEN.md and says it in our own words: no run of COPY_RUN words shared with the source, its overall wording not
# close, and an opening worded differently. The source's words never enter the repo: research/proven/<id>.json keeps only
# salted hashes of its word runs (a sourceprint), made from the transcript or on-screen text the run read itself.
PROVEN_DIR = os.path.join(HERE, "research", "proven")
COPY_RUN = 6                      # any shared run of 6 or more words fails
COPY_SHARE, COPY_COVER = 0.15, 0.25   # too close overall: 15% of our 3-word runs in the source, or 25% of its in ours
OPEN_WORDS, SRC_OPEN_WORDS, OPEN_SHARE = 15, 25, 0.34   # the opening: no shared 4-word run, under a third of 3-word runs
SOURCE_LINE = re.compile(r"(?im)^- \*\*Source:\*\*[ \t]*`?(\S+?)`?[ \t]*$")
STARTED_LINE = re.compile(r"(?im)^- \*\*Started:\*\*[ \t]*`?(\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2})")
_SALT = "pnf-proven|"


def _ctoks(text):
    t = TAG.sub(" ", str(text or "")).lower().replace("’", "'")
    t = re.sub(r"(?<=\d),(?=\d{3})", "", t)
    return re.sub(r"[^a-z0-9$%]+", " ", t.replace("'", "")).split()


def _grams(toks, n):
    return [" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)]


def _gh(g):
    return hashlib.sha1((_SALT + g).encode()).hexdigest()[:12]


def source_id(url):
    m = re.search(r"(?:shorts/|[?&]v=|youtu\.be/)([\w-]{11})", url or "")
    return m.group(1) if m else "u" + hashlib.sha1((url or "").encode()).hexdigest()[:11]


def sourceprint(text, url, how, read=None):
    toks = _ctoks(text)
    op = toks[:SRC_OPEN_WORDS]
    return {"schema": "pnf.studio.sourceprint.v1", "source": url, "read": read or dt.date.today().isoformat(), "how": how,
            "words": len(toks), "g3": sorted({_gh(g) for g in _grams(toks, 3)}),
            "g6": sorted({_gh(g) for g in _grams(toks, COPY_RUN)}),
            "open3": sorted({_gh(g) for g in _grams(op, 3)}), "open4": sorted({_gh(g) for g in _grams(op, 4)})}


def spoken_text(slug):
    p = vdir(slug, "01_voice", "script.md")
    lines = open(p, encoding="utf-8").read().splitlines() if os.path.exists(p) else []
    return " ".join(l for l in lines if l.strip() and not l.lstrip().startswith("#"))


def _strings(o):
    if isinstance(o, str):
        yield o
    elif isinstance(o, dict):
        for v in o.values():
            yield from _strings(v)
    elif isinstance(o, list):
        for v in o:
            yield from _strings(v)


def copy_problems(text, fp, captions=()):
    """Our script (and caption texts) against a sourceprint. Returns (problems, stats)."""
    if not fp or fp.get("words", 0) < 8 or not fp.get("g6"):
        return ["the source has no sourceprint of 8 words or more (read its transcript or on-screen text, then `anim.py "
                "sourceprint`)"], {}
    toks = _ctoks(text)
    s3, s6 = set(fp["g3"]), set(fp["g6"])
    out = []
    hits = [g for g in _grams(toks, COPY_RUN) if _gh(g) in s6]
    if hits:
        out.append(f"{len(hits)} run(s) of {COPY_RUN}+ words match the source, first: '{hits[0]}': say it in our own words")
    g3 = _grams(toks, 3)
    mine = {_gh(g) for g in g3}
    share = sum(1 for g in g3 if _gh(g) in s3) / max(1, len(g3))
    cover = len(mine & s3) / max(1, len(s3))
    if share >= COPY_SHARE:
        out.append(f"{share:.0%} of the script's 3-word runs are in the source (under {COPY_SHARE:.0%}): too close overall")
    if cover >= COPY_COVER:
        out.append(f"the script repeats {cover:.0%} of the source's 3-word runs (under {COPY_COVER:.0%}): too close overall")
    first = re.split(r"(?<=[.?!])\s", TAG.sub(" ", str(text or "")).strip(), maxsplit=1)[0]
    op = _ctoks(first)[:OPEN_WORDS]
    o4 = [g for g in _grams(op, 4) if _gh(g) in set(fp.get("open4", []))]
    o3 = _grams(op, 3)
    oshare = sum(1 for g in o3 if _gh(g) in set(fp.get("open3", []))) / max(1, len(o3))
    if o4 or oshare >= OPEN_SHARE:
        out.append(f"the opening '{' '.join(op)}' is worded like the source's opening ({len(o4)} shared 4-word runs, "
                   f"{oshare:.0%} of its 3-word runs): open with different words")
    for c in captions:
        ch = [g for g in _grams(_ctoks(c), COPY_RUN) if _gh(g) in s6]
        if ch:
            out.append(f"a caption shares a {COPY_RUN}+ word run with the source: '{ch[0]}'")
            break
    return out, {"run_hits": len(hits), "share3": round(share, 3), "cover3": round(cover, 3), "open_share3": round(oshare, 3),
                 "open_hits4": len(o4), "words": len(toks), "source_words": fp.get("words")}


# The 100K bar (Todd, live chat, Nov 7, 2026, 7:17 pm: "1,225 is not viral and out bar of 1,000 is far too low. We need
# topics that are actually interesting. We need to change this standard to 100K+ views"; 7:20 pm, of "100K+ and 5x": yes).
# A proven lesson started from PROVEN_BAR_FROM on must name a research/PROVEN.md bank row with 100,000 views or more and
# 5x its channel's typical. Lessons started before it keep the old bar (1,000 views and 5x).
PROVEN_MIN_VIEWS, PROVEN_MIN_RATIO, PROVEN_BAR_FROM = 100000, 5.0, "2026-11-07 19:17"
_BANK_ROW = re.compile(r"(?m)^\|\s*(\d+)\s*\|[^|]*?youtube\.com/shorts/([A-Za-z0-9_-]{11})[^|]*\|\s*([\d,.]+)(K|M)?\s+vs\s+([\d,.]+)(K|M)?\s*\(([\d,.]+)x\)")


def _num(v, unit):
    n = float(v.replace(",", ""))
    return int(round(n * {"K": 1e3, "M": 1e6}.get(unit or "", 1)))


def proven_bank(text=None):
    """{video id: (row, views, ratio)} from the bank tables of research/PROVEN.md (or the text given)."""
    if text is None:
        p = os.path.join(HERE, "research", "PROVEN.md")
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    out = {}
    for m in _BANK_ROW.finditer(text):
        out.setdefault(m.group(2), (int(m.group(1)), _num(m.group(3), m.group(4)), float(m.group(7).replace(",", ""))))
    return out


def proven_bar_problems(text, bank):
    st = STARTED_LINE.search(text or ""); m = SOURCE_LINE.search(text or "")
    if not st or st.group(1).replace("T", " ") < PROVEN_BAR_FROM or not m:
        return []
    vid = source_id(m.group(1)) if "shorts/" not in m.group(1) else m.group(1).rstrip("/").split("shorts/")[-1][:11]
    row = bank.get(vid)
    if not row:
        return [f"source {vid} is not a research/PROVEN.md bank row (the 100K bar reads its views there)"]
    if row[1] < PROVEN_MIN_VIEWS or row[2] < PROVEN_MIN_RATIO:
        return [f"source {vid} (PROVEN.md row {row[0]}) has {row[1]:,} views at {row[2]}x: under the bar of {PROVEN_MIN_VIEWS:,} views and {PROVEN_MIN_RATIO:g}x (Todd, Nov 7, 7:17 pm)"]
    return []


def proven_brief_problems(text, bank=None):
    out = []
    m = SOURCE_LINE.search(text or "")
    if not m or not m.group(1).startswith("https://"):
        out.append("brief.md has no '- **Source:** <https link>' line (the outlier this lesson is our version of)")
    else:
        out += proven_bar_problems(text, proven_bank() if bank is None else bank)
    if not re.search(r"(?im)^- \*\*Shape:\*\*\s*\S", text or ""):
        out.append("brief.md has no '- **Shape:**' line (rotation reads it)")
    return out


def load_sourceprint(url):
    p = os.path.join(PROVEN_DIR, source_id(url) + ".json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else None


# The viewer check (Todd, live chat, Nov 8, 2026, 9:51 pm, after hail-or-wear, a drawn roof with nothing real to judge:
# "If the viral video focuses on real footage we obviously can't use that as a basis for our video. ... When ideating these
# videos, take a step back and ask if it makes sense from the viewers perspective. Find viral videos that will work in the
# context of a faceless animated videos that we are creating"). A proven lesson started after it says, in brief.md, what
# made the source work and that our animated version keeps it, and what a viewer gets from ours.
VIEWER_FROM = "2026-11-29"
VIEWER_LINE = re.compile(r"(?im)^- \*\*Viewer check:\*\*\s*(.+)$")
INGREDIENT_LINE = re.compile(r"(?im)^- \*\*Key ingredient:\*\*\s*(.+)$")
FOOTAGE_WORDS = re.compile(r"(?i)\b(real footage|raw footage|phone footage|live[- ]action|on camera|their footage|a real person|real people)\b")


def viewer_check_problems(text):
    out = []
    ing, view = INGREDIENT_LINE.search(text), VIEWER_LINE.search(text)
    if not ing or len(ing.group(1).split()) < 6:
        out.append("brief.md needs '- **Key ingredient:** <what made the source work, in a sentence>' (Todd, Nov 8, 9:51 pm)")
    elif FOOTAGE_WORDS.search(ing.group(1)) and not re.search(r"(?i)\b(we can draw|drawn|animat)", ing.group(1)):
        out.append("the source's key ingredient is real footage or real people, which a faceless animated lesson cannot carry: pick another row")
    if not view or len(view.group(1).split()) < 12:
        out.append("brief.md needs '- **Viewer check:** <a stranger watching our animated version gets ..., in a sentence>' (Todd, Nov 8, 9:51 pm)")
    return out


def proven_problems(slug):
    bp = vdir(slug, "01_voice", "brief.md")
    text = open(bp, encoding="utf-8").read() if os.path.exists(bp) else ""
    out = proven_brief_problems(text)
    if os.path.basename(slug)[:10] >= VIEWER_FROM:
        out += viewer_check_problems(text)
    m = SOURCE_LINE.search(text)
    fp = load_sourceprint(m.group(1)) if m else None
    if m and not fp:
        out.append(f"no sourceprint at research/proven/{source_id(m.group(1))}.json for {m.group(1)}")
    cj = vdir(slug, "05_render", "captions.json")
    caps = list(_strings(json.load(open(cj, encoding="utf-8")))) if os.path.exists(cj) else []
    probs, stats = copy_problems(spoken_text(slug), fp, caps) if fp else ([], {})
    return out + probs, stats


def cmd_sourceprint(url, path, how):
    """Hash a source's words (a transcript or on-screen text the run read itself, kept out of the repo) into
    research/proven/<id>.json. The text file itself is never committed (keep it under data/)."""
    text = open(path, encoding="utf-8").read()
    fp = sourceprint(text, url, how)
    os.makedirs(PROVEN_DIR, exist_ok=True)
    out = os.path.join(PROVEN_DIR, source_id(url) + ".json")
    json.dump(fp, open(out, "w"), indent=0); open(out, "a").write("\n")
    print(f"sourceprint: {os.path.relpath(out, ROOT)} ({fp['words']} words, {len(fp['g6'])} 6-word runs hashed)")


def cmd_copycheck(slug):
    if lesson_format(slug) != "proven":
        print(f"copycheck: {slug} is not a proven lesson (Format proven)"); return
    bad, stats = proven_problems(slug)
    for x in bad:
        print("ERROR copy: " + x)
    rev = vdir(slug, "05_render", "reviews")
    os.makedirs(rev, exist_ok=True)
    json.dump({"gate": "copy", "pass": not bad, "at": now(), "stats": stats, "problems": bad,
               "script_sha": sha(vdir(slug, "01_voice", "script.md"))[:12] if os.path.exists(vdir(slug, "01_voice", "script.md")) else None},
              open(os.path.join(rev, "copy.json"), "w"), indent=1)
    print("copycheck: " + ("FAIL" if bad else "PASS") + f" {json.dumps(stats)}")
    if bad:
        sys.exit(1)


def lane_test():
    return json.load(open(os.path.join(HERE, "..", "config.json"), encoding="utf-8")).get("laneTest") or {}


def next_lane(started, cfg):
    """started: [(started_at, format)] for new proven and story lessons. The lane the next new lesson takes: the
    pattern (proven, proven, story) in turn from cfg['from'] while the test runs; None when no test runs."""
    if not cfg or cfg.get("mode") != "on":
        return None
    n = sum(1 for at, f in started if at >= cfg["from"] and f in ("proven", "story"))
    pat = cfg.get("pattern") or ["proven", "proven", "story"]
    return pat[n % len(pat)]


# Topic first (Todd, video-lab chat, Nov 8, 2026, to "Should the proven lane pick its next source row by that first (money
# between two people, or our phone topics), before any other row at the 100K bar?": "Yes, pick by topic first"). Our top 4
# lessons by views are the phone cluster; 9 of the 14 owner Shorts at the bar are money between two people
# (research/STUDY-2026-11-08.md). eligible_rows orders those rows first, then by views.
PULL_TOPIC = re.compile(r"(?i)(won'?t pay|don'?t pay|doesn'?t pay|not pay|non-?payment|payment|get paid|collect|lowball|offered|worth when you sell|"
                        r"labou?r cost|leave|quit|hire|staff|a-players|price objection|\bcalls?\b|phone|missed|after hours|after-hours|answer)")


def _row_topic(vid, text=None):
    if text is None:
        p = os.path.join(HERE, "research", "PROVEN.md")
        text = open(p, encoding="utf-8").read() if os.path.exists(p) else ""
    ln = next((x for x in text.splitlines() if x.startswith("|") and vid in x), "")
    cols = [c.strip() for c in ln.split("|")]
    return cols[4] if len(cols) > 4 else ""


def topic_rank(topic):
    """0 for money between two people or our phone cluster, 1 for any other topic."""
    return 0 if PULL_TOPIC.search(topic or "") else 1


def eligible_rows():
    """Bank rows at the bar, with a sourceprint, that no lesson's brief has used as its Source; topic first (PULL_TOPIC),
    then most views. Returns row numbers in pick order."""
    used = set()
    for d in os.listdir(VIDEOS):
        bp = vdir(d, "01_voice", "brief.md")
        m = SOURCE_LINE.search(open(bp, encoding="utf-8").read()) if os.path.exists(bp) else None
        if m and "shorts/" in m.group(1):
            used.add(m.group(1).rstrip("/").split("shorts/")[-1][:11])
    ok = [(v, r) for v, r in proven_bank().items() if r[1] >= PROVEN_MIN_VIEWS and r[2] >= PROVEN_MIN_RATIO and v not in used
          and os.path.exists(os.path.join(PROVEN_DIR, source_id(f"https://www.youtube.com/shorts/{v}") + ".json"))]
    return [r[0] for v, r in sorted(ok, key=lambda vr: (topic_rank(_row_topic(vr[0])), -vr[1][1]))]


def cmd_nextlane():
    cfg = lane_test()
    rows = []
    for d in sorted(os.listdir(VIDEOS)):
        bp = vdir(d, "01_voice", "brief.md")
        if not os.path.exists(bp):
            continue
        m = STARTED_LINE.search(open(bp, encoding="utf-8").read())
        if m:
            rows.append((m.group(1).replace("T", " "), lesson_format(d)))
    lane = next_lane(rows, cfg)
    if lane == "proven" and not eligible_rows():
        print(f"nextlane: none (no unused research/PROVEN.md row has {PROVEN_MIN_VIEWS:,}+ views, {PROVEN_MIN_RATIO:g}x and a "
              f"sourceprint; every new lesson is proven (Todd, Nov 8): queue a watch-video sourceprint job for a new 100K row "
              f"and make no story)")
        return
    if lane is None:
        print("nextlane: no lane test runs (video/config.json laneTest mode is not on): story lane")
        return
    made = sum(1 for at, f in rows if at >= cfg["from"] and f in ("proven", "story"))
    if lane == "proven":
        print("pick order (topic first, Todd Nov 8; then views): rows " + ", ".join(str(r) for r in eligible_rows()))
    print(f"nextlane: {lane} ({made} new lessons started since {cfg['from']}; pattern {', '.join(cfg.get('pattern', []))}; "
          f"verdict {cfg.get('verdict')})")


def cmd_selftest():
    """Planted cases for the send moment and the shorter middle: every bad case must be caught, every good one pass."""
    good_brief = "- **Format:** story\n- **Send:** whoever answers the phones: the text to send back, word for word\n"
    doc = lambda cues, dur: {"duration": dur, "cues": cues}
    c = lambda i, t, send=False: dict({"id": i, "t": t, "level": 0}, **({"send": True} if send else {}))
    cases = [
        ("brief good", send_brief_problems(good_brief), False),
        ("brief missing Send line", send_brief_problems("- **Format:** story\n"), True),
        ("brief Send line with no thing", send_brief_problems("- **Send:** whoever answers the phones\n"), True),
        ("brief Send line to a group", send_brief_problems("- **Send:** other contractors: the text to send back\n"), True),
        ("brief Send line to the viewer", send_brief_problems("- **Send:** you: the text to send back word for word\n"), True),
        ("brief Send line one-word person", send_brief_problems("- **Send:** partner: the text to send back\n"), True),
        ("brief Send line vague thing", send_brief_problems("- **Send:** the office manager: this tip\n"), True),
        ("end card names the person", send_card_problems("whoever answers the phones", "Send this to whoever answers the phones."), False),
        ("end card names someone else", send_card_problems("whoever answers the phones", "Send this to your office manager."), True),
        ("end card has no send line", send_card_problems("the office manager", ""), True),
        ("send cue good", send_cue_problems(doc([c("hook", 0), c("fix", 20, True), c("why", 24)], 55.0), still=3.2), False),
        ("no send cue", send_cue_problems(doc([c("hook", 0), c("fix", 20), c("why", 24)], 55.0)), True),
        ("two send cues", send_cue_problems(doc([c("hook", 0), c("fix", 20, True), c("why", 24, True)], 55.0)), True),
        ("send cue too short", send_cue_problems(doc([c("hook", 0), c("fix", 20, True), c("why", 22.0)], 55.0)), True),
        ("send card moves", send_cue_problems(doc([c("hook", 0), c("fix", 20, True), c("why", 24)], 55.0), still=1.75), True),
        ("send after halfway", send_cue_problems(doc([c("hook", 0), c("fix", 30, True), c("why", 34)], 55.0)), True),
        ("send exactly at halfway", send_cue_problems(doc([c("hook", 0), c("fix", 27.5, True), c("why", 31)], 55.0)), True),
        ("send last cue, holds to the end", send_cue_problems(doc([c("hook", 0), c("fix", 20, True)], 45.0)), False),
        # Todd's five calls (live chat, Nov 9, 2026, 7:33 am, "Recs")
        ("call 5: a full card still 13.5 s fails", send_cue_problems(doc([c("hook", 0), c("fix", 12, True), c("why", 26)], 55.0), still=13.5, recs=True), True),
        ("call 5: a card built line by line, full 3.0 s, passes", send_cue_problems(doc([c("hook", 0), c("fix", 12, True), c("why", 20)], 55.0), still=3.0, recs=True), False),
        ("call 5: before RECS_FROM the long hold is not checked", send_cue_problems(doc([c("hook", 0), c("fix", 12, True), c("why", 26)], 55.0), still=13.5), False),
        ("call 5: no linesOn and no endSend fail", recs_send_scene_problems("k.sendCard({at: 12, lines: ['a', 'b']});"), True),
        ("call 5: linesOn and endSend pass", recs_send_scene_problems("k.sendCard({at: 12, lines: ['a'], linesOn: [12]}); window.SCENE = {endSend: ['a']};"), False),
        ("call 1: a mosaic room move fails", move_problems("window.SCENE = {transitions: {fix: 'mosaic', close: 'cut'}};"), True),
        ("call 1: cuts and a slide pass", move_problems("window.SCENE = {transitions: {fix: 'slide', close: 'cut'}};"), False),
        ("call 1: a k.cut iris fails", move_problems("if (k.cut(3.2, {kind: 'iris'})) draw2();"), True),
        ("call 1: a plain k.cut passes", move_problems("if (k.cut(3.2)) draw2();"), False),
        ("call 2: an EXAMPLE tag with no number fails", example_tag_problems([(1.0, [("EXAMPLE", "scene", 0, 0, 1, 1, 1), ("SAY THIS", "scene", 0, 0, 1, 1, 1)])], 0.25), True),
        ("call 2: an EXAMPLE tag beside only step numbers fails", example_tag_problems([(1.0, [("EXAMPLE", "scene", 0, 0, 1, 1, 1), ("1  THE HOUSE AND ADDRESS", "scene", 0, 0, 1, 1, 1)])], 0.25), True),
        ("call 2: an EXAMPLE tag on the send card fails", recs_send_scene_problems("k.sendCard({at: 12, linesOn: [12], steps: ['a'], example: true}); window.SCENE = {endSend: ['a']};"), True),
        ("call 2: an EXAMPLE tag beside a made-up number passes", example_tag_problems([(1.0, [("EXAMPLE", "scene", 0, 0, 1, 1, 1), ("$4,800 JOB", "scene", 0, 0, 1, 1, 1)])], 0.25), False),
        ("call 2: the made-up line twice fails", example_tag_problems([(t_, [("MADE-UP EXAMPLE", "scene", 0, 0, 1, 1, 1)] if t_ in (1.0, 1.25, 9.0) else []) for t_ in (1.0, 1.25, 1.5, 9.0)], 0.25), True),
        ("call 2: the made-up line once passes", example_tag_problems([(t_, [("MADE-UP EXAMPLE", "scene", 0, 0, 1, 1, 1)] if t_ < 2 else []) for t_ in (1.0, 1.25, 1.5, 9.0)], 0.25), False),
        ("call 1: two lessons both on cuts are not a copied transition", fresh_problems({"slug": "x", "transitions": {"send": "cut", "close": "cut"}}, [{"slug": "a", "transitions": {"send": "cut", "close": "cut"}}])[0], False),
        ("reviewer names both", send_match_problems(("whoever answers the phones", "the text-back message to a missed caller"),
                                                    {"score": {"person": "my wife, who answers our phones", "thing": "the missed caller text-back message"}}), False),
        ("reviewer names the wrong person", send_match_problems(("whoever answers the phones", "the text-back message to a missed caller"),
                                                                {"score": {"person": "my brother-in-law who owns a shop", "thing": "the missed caller text-back message"}}), True),
        ("reviewer names no thing", send_match_problems(("whoever answers the phones", "the text-back message to a missed caller"),
                                                        {"score": {"person": "the woman who answers our phones", "thing": "none"}}), True),
        ("reviewer names another thing", send_match_problems(("the office manager", "the Google profile hours setting"),
                                                             {"score": {"person": "our office manager", "thing": "a survey chart about Yelp"}}), True),
        ("card still 3.0 s", send_still_seconds([(i * 0.25, ("CARD",), [10] * 100) for i in range(12)], 0.25) < SEND_HOLD, False),
        ("snow drifts over the card", send_still_seconds([(i * 0.25, ("CARD",), [10] * 100 if i % 4 else [10] * 90 + [200] * 10) for i in range(12)], 0.25) < SEND_HOLD, True),
        ("card slides the whole time", send_still_seconds([(i * 0.25, (f"CARD@{i}",), [10] * 100) for i in range(12)], 0.25) < SEND_HOLD, True),
        ("no text on screen", send_still_seconds([(i * 0.25, (), [10] * 100) for i in range(12)], 0.25) < SEND_HOLD, True),
        ("story 87.6 s over the ceiling", 87.6 > FORMATS["story"]["max_seconds"], True),
        ("story 66.2 s under the ceiling", 66.2 > FORMATS["story"]["max_seconds"], False),
    ]
    # The proven lane's copy check and rotation (Todd, live chat, Nov 7, 2026, 12:08 pm: "Go"). The source is made up here.
    src = ("Every missed call on a busy Monday is a homeowner who already decided to hire someone. They dial the next number "
           "on the list within two minutes. Most shops never call back until the evening, and by then the job is booked with a "
           "competitor across town. Put a text back on every missed call and you keep the job.")
    fp = sourceprint(src, "https://www.youtube.com/shorts/AAAAAAAAAAA", "planted", "2026-11-07")
    ours = ("Your phone buzzes while you're up a ladder. By the time you climb down, that caller has moved on to another "
            "plumber. Here's the fix that takes ten minutes tonight: one automatic reply that goes out the second a call rings "
            "out. It says you're on a job, asks what they need, and promises a call by five.")
    close = ("Every missed call on a slow Monday means a homeowner who already decided. Then they dial the next number. Most "
             "shops never call back, and the job gets booked by a competitor across the street. Put a text back on it, keep the job.")
    cp = lambda text, caps=(): copy_problems(text, fp, caps)[0]
    st = lambda n, f="proven", at="2026-11-08 09:00": [(at, f)] * n
    lt = {"mode": "on", "from": "2026-11-07 13:00", "pattern": ["proven", "proven", "story"]}
    _bk = {"AAAAAAAAAAA": (7, 1225, 21.1), "BBBBBBBBBBB": (11, 2433807, 291.3), "CCCCCCCCCCC": (12, 400000, 3.0)}
    _bb = lambda at, vid: f"- **Format:** proven\n- **Source:** https://www.youtube.com/shorts/{vid}\n- **Started:** {at}\n- **Shape:** card\n"
    cases += [
        ("copy: our own words pass", cp(ours), False),
        ("copy: the source word for word", cp(src), True),
        ("copy: one 6-word run from the source", cp(ours + " They dial the next number on the list and forget you."), True),
        ("copy: a 5-word run alone passes", cp(ours + " Then they dial the next number fast."), False),
        ("copy: close wording with no 6-word run", cp(close), True),
        ("copy: the source's opening reworded slightly", cp("Every missed call on Monday costs you. " + ours), True),
        ("copy: a caption with a 6-word run", cp(ours, ["Most shops never call back until the evening, so fix it."]), True),
        ("copy: no sourceprint", copy_problems(ours, None)[0], True),
        ("copy: brief with no Source line", proven_brief_problems("- **Format:** proven\n- **Shape:** card\n"), True),
        ("copy: brief with Source and Shape", proven_brief_problems("- **Format:** proven\n- **Source:** https://www.youtube.com/shorts/AAAAAAAAAAA\n- **Shape:** card\n"), False),
        ("100K bar: a source with 1,225 views started after the bar", proven_brief_problems(_bb("2026-11-07 19:30", "AAAAAAAAAAA"), _bk), True),
        ("100K bar: 400,000 views at 3x is under 5x", proven_brief_problems(_bb("2026-11-08 09:00", "CCCCCCCCCCC"), _bk), True),
        ("100K bar: a source not in the bank", proven_brief_problems(_bb("2026-11-08 09:00", "ZZZZZZZZZZZ"), _bk), True),
        ("100K bar: 2,433,807 views at 291x passes", proven_brief_problems(_bb("2026-11-08 09:00", "BBBBBBBBBBB"), _bk), False),
        ("100K bar: a lesson started before the bar keeps the old bar", proven_brief_problems(_bb("2026-11-07 16:50", "AAAAAAAAAAA"), _bk), False),
        ("100K bar: the real bank reads row 1 at 10M", proven_bank().get("zQiyPFqazDg", (0, 0, 0))[1] < 10000000, False),
        ("lane: first new lesson is proven", next_lane([], lt) != "proven", False),
        ("lane: third new lesson is story", next_lane(st(2), lt) != "story", False),
        ("lane: fourth new lesson is proven again", next_lane(st(2) + st(1, "story"), lt) != "proven", False),
        ("lane: lessons before the test do not count", next_lane(st(2, at="2026-11-06 09:00"), lt) != "proven", False),
        ("lane: shorts do not count", next_lane(st(2, "short"), lt) != "proven", False),
        ("proven 66 s over the 65 s band", 66.0 > FORMATS["proven"]["max_seconds"], True),
        ("proven 49 s under the 50 s band", 49.0 < FORMATS["proven"]["min_seconds"], True),
        ("proven gates carry the copy check and drop the story gate", "copy" not in PROVEN_GATES or "story" in PROVEN_GATES, False),
    ]
    # Studio changes 1, 2 and 4 (Todd, live chat, Nov 7, 2026, 6:59 pm: "Go with your recommendation"). Planted frames:
    # (text, tag, x0, y0, x1, y1, alpha), 0.25 s apart; end card from 20 s.
    def held(boxes, t0=1.0, t1=3.0):
        return [(t0 + i * 0.25, list(boxes)) for i in range(int((t1 - t0) / 0.25) + 1)]
    cal = [(str(d), "scene", 100 + 60 * (d % 7), 600 + 40 * (d // 7), 130 + 60 * (d % 7), 630 + 40 * (d // 7), 1) for d in range(1, 15)]
    cmd_ = "## send \"the only question\"\nThe card: FOR THE LEAD TECHNICIAN / \"Let's walk the job together.\" 94% OF CUSTOMERS, EXAMPLE\n"
    lv = lambda frames: layout_v3_problems(frames, cmd_, 20.0)
    ok_box = ("FOR THE LEAD TECHNICIAN", "scene", 72, 300, 700, 357, 1)
    cases += [
        ("cues: a drawn string written in cues.md passes", lv(held([ok_box])), False),
        ("cues: a drawn string missing from cues.md", lv(held([ok_box, ("AFTER-HOURS MESSAGE", "scene", 72, 400, 700, 457, 1)])), True),
        ("cues: case, quotes and a wrapped line still match", lv(held([("let's walk the", "scene", 72, 400, 500, 457, 1), ("JOB TOGETHER.", "scene", 72, 470, 500, 527, 1)])), False),
        ("cues: a set's own label missing (deco) is caught", lv(held([("New text message", "deco", 300, 400, 600, 430, 1)])), True),
        ("cues: a number not in cues.md is caught", lv(held([("87%", "scene", 300, 400, 600, 457, 1)])), True),
        ("cues: a calendar grid is ornament", lv(held(cal)), False),
        ("cues: a HUD token is ornament", lv(held([("LV 2", "scene", 700, 200, 800, 230, 1), ("XP", "scene", 820, 200, 860, 230, 1)])), False),
        ("cues: a count-up frame under 0.5 s is ignored", lv(held([("41%", "scene", 300, 400, 600, 457, 1)], 1.0, 1.25)), False),
        ("cues: cover words on frame 0 count however short", lv(held([("NO CHECK IN THE MAIL", "scene", 72, 400, 700, 457, 1)], 0.0, 0.25)), True),
        ("cues: end card words are not judged", lv(held([("Send this to your office manager.", "scene", 100, 800, 900, 857, 1)], 20.0, 22.0)), False),
        ("edge: scene text to x 936 is caught", lv(held([("EXAMPLE", "scene", 800, 400, 936, 457, 1)])), True),
        ("edge: scene text to x 930 passes", lv(held([("EXAMPLE", "scene", 800, 400, 930, 457, 1)])), False),
        ("edge: a set's ornament past 930 is not judged", layout_v3_problems(held([("OPEN", "deco", 911, 606, 998, 636, 1)]), cmd_ + "OPEN sign", 20.0), False),
        ("type: 30 px set-size label is left to the design gate", lv(held([("94% OF CUSTOMERS", "scene", 72, 400, 600, 430, 1)])), False),
        ("type: a 20 px shrunk label is caught", lv(held([("94% OF CUSTOMERS", "scene", 72, 400, 400, 420, 1)])), True),
    ]
    fs = lambda slug, cover, send=("fade4", "iris"), shot=None: {"slug": slug, "cover": cover, "shot1": shot, "send": [[0, 3], [1, 3]],
                                                                   "close": None, "transitions": {"send": send[0], "close": send[1]}}
    cv_a = [[c, r] for c in range(1, 11) for r in range(4, 9)]
    cv_b = [[c, r] for c in range(1, 6) for r in range(10, 14)]
    cases += [
        ("fresh: a cover laid out like the lesson before", fresh_problems(fs("x", cv_a), [fs("a", cv_a, ("mosaic", "gameover"))])[0], True),
        ("fresh: a cover laid out its own way", fresh_problems(fs("x", cv_a), [fs("a", cv_b, ("mosaic", "gameover"))])[0], False),
        ("fresh: send and close transitions both copied", fresh_problems(fs("x", cv_a, ("fade4", "iris")), [fs("a", cv_b, ("fade4", "iris"))])[0], True),
        ("fresh: one transition shared is fine", fresh_problems(fs("x", cv_a, ("fade4", "iris")), [fs("a", cv_b, ("fade4", "gameover"))])[0], False),
        ("fresh: the same send card (a kit piece) is only reported", fresh_problems(fs("x", cv_a, ("dissolve", "iris")), [fs("a", cv_b, ("fade4", "iris"))])[0], False),
        ("fresh: a first hook cut like the lesson before", fresh_problems(fs("x", cv_a, shot=cv_b), [fs("a", cv_b, ("mosaic", "gameover"), shot=cv_b)])[0], True),
    ]
    # The hook move library: the real openings of Nov 6 to 8, oldest first
    real = [("three-fixes", "Missed calls cost this shop twenty-eight hundred a month."), ("robot", "An AI receptionist can earn its keep."),
            ("ask-chatgpt", "Nine at night, her furnace quits."), ("lsa-reports-short", "Google's help page says your old reports won't come with you."),
            ("angi", "Two in the afternoon, you're up on a roof, and your pocket buzzes."), ("after-hours", "It's ten to seven on a weeknight."),
            ("chatgpt-check", "A marketing firm says ChatGPT jobs average eleven and a half grand a ticket."), ("pay-before", "The job's done.")]
    ot = opener_text_problems
    cases += [
        ("hooks: classify a clock moment", hook_move("Nine at night, her furnace quits.") != "clock-moment", False),
        ("hooks: classify a question", hook_move("Do you know your close rate?") != "question", False),
        ("hooks: classify 'at nine' as a clock moment", hook_move("Missed call at nine, and one short text can answer it.") != "clock-moment", False),
        ("hooks: classify a short line", hook_move("The job's done.") != "short-line", False),
        ("hooks: classify a money line", hook_move("Missed calls cost this shop twenty-eight hundred a month.") != "money", False),
        ("hooks: classify a you-scene", hook_move("You open your reports to check last week's spend.") != "you-scene", False),
        ("hooks: after-hours (a clock moment right after angi's)", ot(real[5][1], real[:5]), True),
        ("hooks: members (a third clock moment in 5)", ot("Picture the first cold night of the year.", real[3:8]), True),
        ("hooks: a question after these eight is free", ot("Would your tech take a card in the driveway?", real), False),
        ("hooks: the same first three words", ot("The job's done, and the van is gone.", real), True),
        ("hooks: half the content words of one before", ot("Every receptionist can earn its keep", real[:2]), True),
        ("hooks: a money line two after a money line", ot("Your trucks lose four hundred a week idling.", real[:6]), False),
    ]
    cases += [
        ("topic: a customer who won't pay is pulled first", topic_rank("the homeowner who won't pay after the job is done") != 0, False),
        ("topic: missed calls are pulled first", topic_rank("paying for leads, then missing the calls") != 0, False),
        ("topic: why good people leave is pulled first", topic_rank("why good people leave a trades business") != 0, False),
        ("topic: AI tools are not", topic_rank("AI tools for trades owners (AI lane)") == 0, False),
        ("topic: the real bank's row 21 reads as pulled", topic_rank(_row_topic("jjtJQ-VUhtY")) != 0, False),
    ]
    cases += [
        ("hook: 21 words to the first stop (pay-before's) is over 12", script_hook_words("The job's done. The homeowner smiles and says, \"I'll mail you a check.\" Your tech loads the truck.") > 12, True),
        ("hook: two short sentences of 11 words pass", script_hook_words("The job's done. Now she says she'll mail you a check.") > 12, False),
        ("cover: 94% plus 8 words is over 8", cover_word_problems([("94%", "scene"), ("OF HOME SERVICE CUSTOMERS", "scene"), ("OWN A CREDIT CARD", "scene"), ("Source: ServiceTitan", "scene")]), True),
        ("cover: 6 words with a source line and a tag pass", cover_word_problems([("$4,800 JOB.", "scene"), ("NO CHECK. NO ANSWER.", "scene"), ("Source: ServiceTitan, citing Visa", "scene"), ("EXAMPLE", "scene")]), False),
        ("cover: 3 words is under 5", cover_word_problems([("THE JOB'S DONE.", "scene")]), True),
    ]
    cases += [
        ("judge: 'Would you let the truck leave without payment?' counts", not judge_question("Would you let the truck leave without payment?"), False),
        ("judge: 'Did she go too far?'", not judge_question("Did she go too far, or was he right to wait?"), False),
        ("judge: a quiz about the viewer's numbers is not one", judge_question("Do you know your close rate?"), False),
        ("judge: a statement is not one", judge_question("Get paid before the truck leaves."), False),
        ("judge: pay-before's real YouTube title has none", not judge_question("Get Paid Before the Truck Leaves (HVAC and Plumbing Business)"), True),
    ]
    # ready --first (Todd, live chat, Nov 8, 2026, 5:10 pm): the lesson goes ahead of the waiting line, never ahead of a
    # lesson already started, and the next slot then takes it
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Chicago")
    t_ = lambda h, d=9: dt.datetime(2026, 11, d, h, 0, tzinfo=tz).isoformat()
    up = lambda *ps: {p: {"url": "u", "at": t_(8, 8)} for p in ps}
    q0 = [{"slug": "2026-11-01-posted", "readyAt": t_(1, 1), "posts": up(*PLATFORMS)},
          {"slug": "2026-11-02-held", "readyAt": t_(1, 1), "posts": {}, "hold": "old gates"},
          {"slug": "2026-11-03-waits", "readyAt": t_(1, 1), "posts": {}},
          {"slug": "2026-11-04-waits", "readyAt": t_(1, 1), "posts": {}}]
    new_ = {"slug": "2026-11-26-new", "readyAt": t_(19, 8), "posts": {}}
    qf = queue_first(q0, new_)
    order = [i["slug"] for i in qf]
    fmt_, par_ = (lambda s_: "proven"), (lambda s_: None)
    lunch = dt.datetime(2026, 11, 9, 11, 38, tzinfo=tz)
    started = [dict(q0[0], slug="2026-11-00-started", posts=up("instagram"))] + q0[1:]
    qs = queue_first(started, new_)
    cases += [
        ("first: the lesson is ahead of the waiting lessons", order.index("2026-11-26-new") > order.index("2026-11-03-waits"), False),
        ("first: posted and held lessons keep their places", order[:2] != ["2026-11-01-posted", "2026-11-02-held"], False),
        ("first: the lesson is in the line once", order.count("2026-11-26-new") != 1, False),
        ("first: moving a lesson already in line", [i["slug"] for i in queue_first(q0 + [new_], new_)].count("2026-11-26-new") != 1, False),
        ("first: the Nov 9 lunch slot takes it", (pick_next(qf, lunch, fmt_, par_)[0] or {}).get("slug") != "2026-11-26-new", False),
        ("first: without --first the slot takes the old head", (pick_next(q0 + [new_], lunch, fmt_, par_)[0] or {}).get("slug") == "2026-11-26-new", False),
        ("first: a lesson already started still finishes first", (pick_next(qs, lunch, fmt_, par_)[0] or {}).get("slug") != "2026-11-00-started", False),
        ("first: not before tomorrow, tonight's evening slot keeps the old head", (pick_next(queue_first(q0, dict(new_, notBefore=t_(0, 9))), dt.datetime(2026, 11, 8, 20, 14, tzinfo=tz), fmt_, par_)[0] or {}).get("slug") != "2026-11-03-waits", False),
        ("first: not before tomorrow, the Nov 9 lunch slot takes it", (pick_next(queue_first(q0, dict(new_, notBefore=t_(0, 9))), lunch, fmt_, par_)[0] or {}).get("slug") != "2026-11-26-new", False),
        ("first: planted bug, no not-before, tonight's slot takes it early", (pick_next(qf, dt.datetime(2026, 11, 8, 20, 14, tzinfo=tz), fmt_, par_)[0] or {}).get("slug") == "2026-11-26-new", True),
        ("match: a brief with the Match line is matched", not MATCH_LINE.search("- **Format:** proven\n- **Match:** source\n"), False),
        ("match: a brief without it is not", MATCH_LINE.search("- **Format:** proven\n- **Source:** x\n"), False),
        ("match: a 20 s source gives 16 to 27.1 s with the end card", matched_band(20.0) != (16.0, 27.1), False),
        ("match: a 57 s cut of a 20 s source is out of the band", not (57.07 > matched_band(20.0)[1]), False),
        ("match: the length line parses", (SOURCE_LEN.search("- **Source length:** 20 s") or [None, ''])[1] != '20', False),
        ("viewer: a drawable ingredient and a viewer line pass", viewer_check_problems("- **Key ingredient:** whiteboard math one step at a time, each step a number the viewer can check\n- **Viewer check:** a shop owner watching ours sees his own hourly rate built on the board and leaves knowing what to bill\n"), False),
        ("viewer: hail-or-wear's ingredient (real roof footage) is refused", viewer_check_problems("- **Key ingredient:** real footage of a damaged roof the viewer can judge for himself\n- **Viewer check:** a roofer watching ours sees our drawn roof and is asked to call it hail or wear\n"), True),
        ("viewer: no viewer check line", viewer_check_problems("- **Key ingredient:** a famous cheap price everyone knows and the money model behind it\n"), True),
        ("viewer: a one-word ingredient", viewer_check_problems("- **Key ingredient:** skit\n- **Viewer check:** a stranger gets the customer who will not pay acted out and the line to say before the truck leaves\n"), True),
        ("viewer gate: an honest PASS stands", viewer_review_problems({"pass": True, "score": {"matches_idea": "same", "watch_to_end": "yes", "gets": "the four photos to take", "confused": "none"}}), False),
        ("viewer gate: PASS with a close point", viewer_review_problems({"pass": True, "score": {"matches_idea": "close", "watch_to_end": "yes", "gets": "a list", "confused": "none"}}), True),
        ("viewer gate: PASS but would leave", viewer_review_problems({"pass": True, "score": {"matches_idea": "same", "watch_to_end": "no", "gets": "a list", "confused": "none"}}), True),
        ("viewer gate: PASS but gets nothing (hail-or-wear's shape)", viewer_review_problems({"pass": True, "score": {"matches_idea": "same", "watch_to_end": "yes", "gets": "nothing", "confused": "none"}}), True),
        ("viewer gate: PASS but confused", viewer_review_problems({"pass": True, "score": {"matches_idea": "same", "watch_to_end": "yes", "gets": "a list", "confused": "the drawn roof, nothing to judge"}}), True),
        ("viewer gate: on every video from 2026-11-29, not before", ("viewer" in gates_for("2026-11-26-damage-or-not")) or VIEWER_GATE_FROM != "2026-11-29", False),
        ("first: planted bug, put at the very end", (pick_next(q0 + [new_], lunch, fmt_, par_)[0] or {}).get("slug") != "2026-11-26-new", True),
    ]
    right = 0
    for name, got, caught in cases:
        hit = bool(got)
        if hit == caught:
            right += 1
        else:
            print(f"FAIL {name}: {'missed' if caught else 'flagged a good case'} ({got})")
    print(f"studio send and proven selftest: {right} of {len(cases)} planted cases right ({sum(1 for x in cases if x[2])} bad caught)")
    if right != len(cases):
        sys.exit(1)
    v4_selftest()


def v4_selftest():
    """Planted cases for the v4 checks (payoff by 40%, no hold over 4 s, the gate list, the band): bad ones caught, good ones pass."""
    c = lambda i, t, pay=False: dict({"id": i, "t": t, "level": 0}, **({"payoff": True} if pay else {}))
    sig = lambda s: ((s, 0, 0, 10, 10),)
    run = lambda pairs, step=0.25: [(round(i * step, 3), sig(s) if s else ()) for i, s in enumerate(pairs)]
    cases = [
        ("v4 payoff by 40%", payoff_problems({"duration": 27.0, "cues": [c("hook", 0), c("turn", 9.0, True), c("why", 14)]}), False),
        ("v4 payoff late", payoff_problems({"duration": 27.0, "cues": [c("hook", 0), c("turn", 14.0, True)]}), True),
        ("v4 no payoff cue", payoff_problems({"duration": 27.0, "cues": [c("hook", 0), c("turn", 9.0)]}), True),
        ("v4 two payoff cues", payoff_problems({"duration": 27.0, "cues": [c("hook", 0, True), c("turn", 9.0, True)]}), True),
        ("v4 words change every 3 s", hold_problems(run(["A"] * 12 + ["B"] * 12 + ["C"] * 12), 0.25), False),
        ("v4 a card held 6 s", hold_problems(run(["A"] * 8 + ["B"] * 24 + ["C"] * 4), 0.25), True),
        ("v4 a card held to the end 5 s", hold_problems(run(["A"] * 8 + ["B"] * 20), 0.25), True),
        ("v4 an empty stretch is not a held card", hold_problems(run(["A"] * 8 + [""] * 30 + ["B"] * 8), 0.25), False),
        ("v4 gates are qa, facts, render-critic, viewer", list(V4_GATES) != ["qa", "facts", "render-critic", "viewer"], False),
        ("v4 band is 18 to 35 s", [1] if any((FORMATS[f]["min_seconds"], FORMATS[f]["max_seconds"]) != (18.0, 35.0) for f in V4_FORMATS) else [], False),
        ("v4 labels: Meta and TikTok on, YouTube off", [1] if V4_LABELS != {"instagram": ("aiLabel", True), "facebook": ("aiLabel", True), "tiktok": ("aiGenerated", True), "youtube": ("aiUse", False)} else [], False),
    ]
    right = 0
    for name, probs, want_bad in cases:
        ok = bool(probs) == want_bad
        right += ok
        print(f"{'ok  ' if ok else 'WRONG'} {name}" + (f": {probs}" if not ok else ""))
    print(f"v4 selftest: {right} of {len(cases)}")
    if right != len(cases):
        sys.exit(1)


HOOK_DIFF, HOOK_LEVEL, HOOK_MERGE, HOOK_FPS = 0.08, 40, 0.4, 15
ACCENT_ERROR_FROM, ACCENT_ERROR_LATE = "2026-11-15", 0.5   # IMPROVE 00a-3: late accent texts fail lint from these lessons on
ACCENT_STRICT_FROM = "2026-11-17"   # IMPROVE 00a-3 step 2 (Nov 2, end-of-day run): from these lessons on, any late accent fails (0.0 s)
READ_ERROR_FROM, READ_ERROR_SHARE = "2026-11-29", 0.5   # IMPROVE 00a-5 step 2 (Nov 8, evening run): from these lessons on, a text held under half its read time fails lint
HOOK_JS = """(t) => { window.__boxes = []; drawAt(t); const b = window.__boxes; window.__boxes = null;
  if (!window.__sm) { window.__sm = document.createElement('canvas'); window.__sm.width = 108; window.__sm.height = 192; }
  const g = window.__sm.getContext('2d'); g.imageSmoothingEnabled = true; g.drawImage(document.getElementById('c'), 0, 0, 108, 192);
  const d = g.getImageData(0, 0, 108, 192).data, out = new Array(108 * 192 * 3);
  for (let i = 0, j = 0; i < d.length; i += 4) { out[j++] = d[i]; out[j++] = d[i + 1]; out[j++] = d[i + 2]; }
  return {host: b.some((x) => x.tag === 'host'), px: out}; }"""



# Decision 2 (Todd, video-lab chat, Nov 8, 2026, to "For proven lessons, make it a hard check again: the source's conflict
# in 5 to 8 words on frame 0, and spoken in 12 words or fewer by 3.6 s?": "Yes, hard check for proven (Recommended)").
# For proven lessons dated STUDIO_V3_FROM on: the spoken hook (whole sentences to 9 or more words) is 12 words or fewer
# (script, before the voice) and ends by 3.6 s (hook and lint, after it); the cover's words on frame 0 (scene text, the
# source line and the EXAMPLE tag aside) number 5 to 8. The 9-word floor stays a note.
PROVEN_HOOK_NOTE = "decision 2, Nov 8"
COVER_WORDS = (5, 8)


def proven_hook_hard(slug):
    return lesson_format(slug) == "proven" and not source_matched(slug) and os.path.basename(slug)[:10] >= STUDIO_V3_FROM and not slug.endswith(HOOKB_SUFFIX)


def script_hook_words(text):
    """The spoken hook's word count from script text: whole sentences until 9 or more words."""
    n = 0
    for x in re.split(r"(?<=[.?!])\s+", " ".join(TAG.sub(" ", text).split())):
        n += len(x.split())
        if n >= HOOK["words"][0]:
            break
    return n


def cover_word_problems(frame0):
    """frame0: the lint boxes on frame 0. Counts the cover's words: scene text, not the source line, not EXAMPLE."""
    words = []
    for s_, tag, *_ in frame0:
        st = str(s_).strip()
        if tag != "scene" or not st or st.lower().startswith("source") or st.upper() in ("EXAMPLE", MADE_UP):
            continue
        words += re.findall(r"[A-Za-z0-9$%][A-Za-z0-9$%.,'\u2019-]*", st)
    n = len(words)
    lo, hi = COVER_WORDS
    return [] if lo <= n <= hi else [f"the cover says {n} words on frame 0 ({lo} to {hi}: the source's conflict, short): {' '.join(words)[:80]}"]

def spoken_hook(words):
    """The spoken hook: whole sentences from the first word until there are 9 or more words. Returns (words, end time)."""
    n, end = 0, 0.0
    for w in words:
        n += 1; end = w["end"]
        if n >= HOOK["words"][0] and re.search(r"[.?!]$", w["w"]):
            break
    return n, end


def hook_report(slug, pg=None):
    """Measures the opening on a 108 x 192 copy of each frame, 15 a second from 0 to 3 s: a picture change is 8% or more of
    the pixels moving by 40+ levels against the last change (frame 0 first); changes under 0.4 s apart are one change (a
    room's close and open is one cut). Returns the numbers and the problems (each rule above that fails)."""
    import numpy as np
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    own = pg is None
    if own:
        pw, b, pg = open_stage(slug)
    events, peaks, host_at, anchor, last = [], [], None, None, -9.0
    for i in range(int(HOOK["changes_in"] * HOOK_FPS) + 1):
        t = i / HOOK_FPS
        r = pg.evaluate(f"({HOOK_JS})({t:.4f})")
        f = np.array(r["px"], dtype=np.int16).reshape(192, 108, 3)
        if r["host"] and host_at is None:
            host_at = t
        if anchor is None:
            anchor = f; continue
        frac = float((np.abs(f - anchor).max(axis=2) > HOOK_LEVEL).mean())
        if frac >= HOOK_DIFF:
            if t - last >= HOOK_MERGE:
                events.append(round(t, 2)); peaks.append(round(frac, 3)); last = t
            anchor = f
    if own:
        b.close(); pw.stop()
    words = json.load(open(vdir(slug, "02_transcript", "words.json")))["words"]
    n, said = spoken_hook(words)
    rep = {"first_change": events[0] if events else None, "changes_by_3s": len(events), "changes": events, "share": peaks, "host_at": host_at,
           "hook_words": n, "hook_said_by": round(said, 2), "seconds": round(cues["duration"], 2)}
    bad = []
    if rep["first_change"] is None or rep["first_change"] > HOOK["first_change_by"]:
        bad.append(f"the picture first changes at {rep['first_change']} s (by {HOOK['first_change_by']} s)")
    if len(events) < HOOK["changes_min"]:
        bad.append(f"{len(events)} picture change(s) in the first {HOOK['changes_in']:.0f} s (at least {HOOK['changes_min']})")
    v4 = is_v4(slug)
    if not v4 and (host_at is None or host_at > HOOK["host_by"]):
        bad.append(f"the host is not on screen by {HOOK['host_by']:.0f} s")
    soft = rep.setdefault("notes", []) if lesson_format(slug) in GUIDE_FORMATS or v4 else bad
    hard = bad if proven_hook_hard(slug) else soft   # Todd, Nov 8: decision 2 (PROVEN_HOOK_NOTE)
    if n > HOOK["words"][1]:
        hard.append(f"the spoken hook is {n} words (12 or fewer)")
    elif n < HOOK["words"][0]:
        soft.append(f"the spoken hook is {n} words ({HOOK['words'][0]} to {HOOK['words'][1]})")
    if said > HOOK["said_by"]:
        hard.append(f"the spoken hook ends at {said:.2f} s (by {HOOK['said_by']} s)")
    lo, hi = length_band(slug)
    if cues["duration"] > hi or (is_modern(slug) and cues["duration"] < lo):
        bad.append(f"the lesson runs {cues['duration']:.1f} s ({lo:.0f} to {hi:.0f} s for a {lesson_format(slug)} lesson, end card included)")
    aim = story_aim_note(slug, cues["duration"])
    if aim:
        rep.setdefault("notes", []).append(aim)
    return rep, bad


def cmd_hook(slug):
    rep, bad = hook_report(slug)
    print(json.dumps(rep))
    for x in rep.get("notes", []):
        print("NOTE hook (a guide, not a gate; REBUILD.md Relaxed): " + x)
    for x in bad:
        print("ERROR hook: " + x)
    print("hook: " + ("FAIL" if bad else "PASS") + f" first change {rep['first_change']} s, {rep['changes_by_3s']} changes by 3 s, host {rep['host_at']} s, "
          f"spoken hook {rep['hook_words']} words by {rep['hook_said_by']} s, {rep['seconds']} s long")
    if bad:
        sys.exit(1)


LABEL_FLOOR_PX = 36   # ink height in 1080-wide frame units; the design gate caps type at 4 under 36 px labels


def accent_report(slug, first_seen, step=0.25):
    """M3 (IMPROVE 00a-3): each scene text that shows a word the voice says near it (a 4+ letter word or a number) should
    land 0.2 to 0.3 s before that word starts. Returns ([(text, word, lead)] for texts that show up a step or more after
    the word began, count landing in time). lead = word start minus first shown; negative is late. Sampled at lint's step,
    so a lead is good to about that step."""
    wp = vdir(slug, "02_transcript", "words.json")
    if not os.path.exists(wp):
        return [], 0
    wd = json.load(open(wp)); words = wd["words"] if isinstance(wd, dict) else wd
    norm = lambda w: re.sub(r"[^a-z0-9]", "", str(w).lower())
    spoken = [(norm(w["w"]), w["start"]) for w in words if norm(w["w"])]
    late, ontime = [], 0
    # a typed-in text shows as its growing prefixes: keep the whole text, timed from its first letters
    full = {}
    for s_, t0 in sorted(first_seen.items(), key=lambda kv: -len(kv[0])):
        owner = next((f for f in full if f.startswith(s_)), None)
        if owner:
            full[owner] = min(full[owner], t0)
        else:
            full[s_] = t0
    for s_, t0 in full.items():
        toks = {norm(x) for x in re.split(r"[\s/,.:;!?()]+", s_)}
        toks = {x for x in toks if len(x) >= 4 or x.isdigit()}
        near = [(abs(st - t0), w, st) for w, st in spoken if w in toks and t0 - 3.0 <= st <= t0 + 1.0]
        if not near:
            continue
        _, w, st = min(near)
        lead = round(st - t0, 2)
        if lead < -step - 1e-6:
            late.append((s_, w, lead))
        elif lead <= 0.6:
            ontime += 1
    return sorted(late, key=lambda x: x[2]), ontime


def read_time_report(first_seen, last_seen, duration, step=0.25):
    """M6 (IMPROVE 00a-5): every on-screen text holds letters / 15 + 1.5 s. A typed-in text counts from its first letters
    to the last time its whole text shows; texts still up at the end card (they leave with the lesson) are not judged.
    Returns [(text, held, need)] for the ones that leave early, worst first. Sampled at lint's step."""
    out = []
    shape = lambda x: re.sub(r"\d+(\.\d+)?", "#", x)   # a counter shows a new number each frame: one shape, many texts
    shapes = {}
    for s_ in last_seen:
        shapes[shape(s_)] = shapes.get(shape(s_), 0) + 1
    for s_, t1 in last_seen.items():
        if shapes[shape(s_)] >= 3:   # a counting number (k.count, a stopwatch): judged as one moving text, not here
            continue
        if t1 >= duration - 3.5 - step:   # on screen into the end card's last 3.5 s: it leaves with the lesson
            continue
        t0 = min([first_seen[p] for p in first_seen if s_.startswith(p) and len(p) >= 3] + [first_seen.get(s_, t1)])
        letters = sum(c.isalnum() for c in s_)
        if letters < 3 or any(o != s_ and o.startswith(s_) for o in last_seen):   # a typing prefix of a longer text
            continue
        held, need = t1 - t0 + step, letters / 15 + 1.5
        if held + step < need:
            out.append((s_, held, need))
    return sorted(out, key=lambda x: x[1] - x[2])


PIXEL_MOVES = ("levelselect", "dissolve", "gameover", "mosaic", "fade4")   # sets.js room moves on the pixel grid (_shared/sets.md)


def room_move_report(moves):
    """IMPROVE 00a-4 (Nov 1, evening run): M4 wants room changes that travel on the pixel grid, never a plain cut. Every
    section after the first changes room; SCENE.transitions names its move, else the player falls back to the room's
    own move, then blinds. Returns a WARN line, or '' when every change uses a pixel-native move."""
    secs = (moves or {}).get("s") or []
    tr = (moves or {}).get("t") or {}
    changes = secs[1:]
    if not changes:
        return ""
    plain = [x for x in changes if tr.get(x) not in PIXEL_MOVES]
    if not plain:
        return ""
    used = sorted({tr[x] for x in changes if tr.get(x) in PIXEL_MOVES})
    lead = "no room change uses a pixel-native move" if len(plain) == len(changes) else f"{len(plain)} of {len(changes)} room changes use no pixel-native move"
    return (f"{lead} (M4: SCENE.transitions = {{section: {' | '.join(PIXEL_MOVES)}}}; "
            f"plain: {', '.join(plain)}" + (f"; used: {', '.join(used)}" if used else "") + ")")


STUDIO_V3_FROM = "2026-11-26"
CONTENT_X1 = 930
MONTHS = "jan feb mar apr may jun jul aug sep sept oct nov dec january february march april june july august september october november december"
DAYS = "s m t w th f sa su mo tu we fr mon tue wed thu fri sat sun monday tuesday wednesday thursday friday saturday sunday"
GRID_WORDS = set((MONTHS + " " + DAYS).split())
HUD_WORDS = {"lv", "xp", "hp", "vs", "ko"}


def _stoks(s):
    """A drawn string or cues.md as plain tokens: lowercase words and numbers (9.8%, 100,000, $29 kept whole), no other
    punctuation, so wrapping, quote marks and case never decide a match."""
    s = str(s).lower().replace("’", "'").replace("‘", "'")
    return re.findall(r"\$?[a-z0-9]+(?:[.,'][a-z0-9]+)*%?", s)


def _is_num(tok):
    return bool(re.fullmatch(r"\$?[0-9][0-9.,]*%?", tok))


def _runs(ts, step):
    """Contiguous runs of sample times as (start, end) pairs."""
    out, start, prev = [], None, None
    for x in sorted(ts):
        if prev is None or x - prev > step * 1.5:
            if prev is not None:
                out.append((start, prev))
            start = x
        prev = x
    if prev is not None:
        out.append((start, prev))
    return out


def grid_strings(samples):
    """Set-piece grid labels a viewer reads as one picture, never one at a time: a frame with 5 or more different labels
    made only of numbers, months and weekdays (a calendar, a score grid), and HUD tokens (LV 2, XP, VS). They are
    ornament, so the cues.md and type-floor rules skip them; every other drawn string is a claim or a label."""
    grid = set()
    for _, boxes in samples:
        cand = {b[0].strip() for b in boxes if _stoks(b[0]) and all(_is_num(x) or x in GRID_WORDS for x in _stoks(b[0]))}
        if len(cand) >= 5:
            grid |= cand
        for b in boxes:
            tk = _stoks(b[0])
            if tk and any(x in HUD_WORDS for x in tk) and all(x in HUD_WORDS or _is_num(x) for x in tk):
                grid.add(b[0].strip())
    return grid


def layout_v3_problems(samples, cues_text, end_t, step=0.25, floor_px=28, edge=CONTENT_X1):
    """Studio changes 1 and 4 (Todd, live chat, Nov 7, 2026, 6:59 pm: "Go with your recommendation"; coo/DECISIONS-2026-11-07.md)
    in code, for lessons dated from STUDIO_V3_FROM. samples: [(t, [(text, tag, x0, y0, x1, y1, alpha)])] for scene and
    set (deco) text, before the end card. Fails, for anything on screen 0.5 s or more in a row:
    (1) a drawn string missing from cues.md (the facts gate reads cues.md as the list of everything drawn);
    (2) scene text past x 930, the content edge the render critic and the stage contract use (lint's own edge is 950);
    (3) any text under 28 px of ink, smaller than the kit's smallest face (30 px): a shrunk or scaled-down label.
    Grid labels (grid_strings) are skipped for (1) and (3)."""
    cues_t = " " + " ".join(_stoks(cues_text)) + " "
    grid = grid_strings(samples)
    seen, wide, small = {}, {}, {}
    for t, boxes in samples:
        if t >= end_t:
            continue
        for s, tag, x0, y0, x1, y1, a in boxes:
            s = s.strip()
            if a <= 0.6 or not s or tag not in ("scene", "deco"):
                continue
            seen.setdefault(s, []).append(t)
            if tag == "scene" and s not in grid and x1 > edge + 0.5:
                wide.setdefault(s, []).append((t, x1))
            if s not in grid and y1 - y0 < floor_px and any(c.isalnum() for c in s):
                small.setdefault(s, []).append((t, y1 - y0))
    # 0.5 s in a row, or on frame 0 at all: the cover is the feed's thumbnail, however briefly it holds
    long_enough = lambda ts: min(ts) <= 1e-6 or any(b - a >= 0.5 - 1e-6 for a, b in _runs(ts, step))
    out = []
    for s, ts in sorted(seen.items(), key=lambda kv: kv[1][0]):
        tk = _stoks(s)
        if s in grid or not tk or not long_enough(ts):
            continue
        if not (sum(c.isalnum() for c in s) >= 2 or any(c.isdigit() for c in s)):
            continue
        if (" " + " ".join(tk) + " ") not in cues_t:
            out.append(f"{ts[0]:5.2f} s: drawn string not in cues.md: '{s[:60]}' (write it in cues.md exactly; facts reads cues.md)")
    for s, hits in sorted(wide.items(), key=lambda kv: kv[1][0][0]):
        ts = [h[0] for h in hits]
        if long_enough(ts):
            out.append(f"{ts[0]:5.2f} s: '{s[:50]}' runs to x {max(h[1] for h in hits):.0f}, past the x {edge} content edge")
    for s, hits in sorted(small.items(), key=lambda kv: kv[1][0][0]):
        ts = [h[0] for h in hits]
        if long_enough(ts):
            out.append(f"{ts[0]:5.2f} s: '{s[:50]}' is {min(h[1] for h in hits):.0f} px tall, under the {floor_px} px type floor")
    return out


# Freshness in code (studio change 2; Todd, live chat, Nov 7, 2026, 6:59 pm: "Go with your recommendation";
# coo/DECISIONS-2026-11-07.md). The design gate failed round 0 on copies of the lesson before: a cover in the same layout,
# a hook cut that repeated the last lesson's move, the send and close transitions copied. A lesson's layout exists from its
# first `stills`, so this runs there (and in lint), before render: the frames that carry a lesson's identity (the cover,
# the first hook cut, the send card, the last frame before the end card) as which cells of a 12 x 24 grid hold settled
# scene text, and its send and close transitions, against the two lessons before it (the same two variety uses).
# The send card is a kit piece (k.sendCard) and is meant to look the same every time, so its layout is reported, not failed.
FRESH_GRID = (12, 24)   # 90 x 80 frame-unit cells over 1080 x 1920
FRESH_MATCH = 0.85      # cover or first-cut layout this close to a lesson before fails (Nov 8 calibration: the 21
                        # neighbour pairs of the last 12 lessons ran 0.00 to 0.66, and one cover copy ran 0.97)
FRESH_KEYS = ("cover", "shot1", "send", "close")


def layout_cells(boxes):
    """The cells of a 12 x 24 grid that settled scene text covers, from one frame's lint boxes."""
    cw, ch = 1080 / FRESH_GRID[0], 1920 / FRESH_GRID[1]
    cells = set()
    for s, tag, x0, y0, x1, y1, a in boxes:
        if tag != "scene" or a <= 0.6 or not str(s).strip():
            continue
        for cx in range(max(0, int(x0 // cw)), min(FRESH_GRID[0] - 1, int((x1 - 1) // cw)) + 1):
            for cy in range(max(0, int(y0 // ch)), min(FRESH_GRID[1] - 1, int((y1 - 1) // ch)) + 1):
                cells.add((cx, cy))
    return cells


def jaccard(a, b):
    a, b = {tuple(x) for x in (a or [])}, {tuple(x) for x in (b or [])}
    return round(len(a & b) / len(a | b), 2) if (a or b) else 0.0


def _boxes_at(pg, t):
    bx = pg.evaluate(f"(() => {{ window.__boxes = []; drawAt({t:.3f}); const r = window.__boxes; window.__boxes = null; return r; }})()")
    return [(x["s"], x["tag"], x["x0"], x["y0"], x["x1"], x["y1"], x["a"]) for x in bx]


def fresh_signature(slug, pg=None, hook=None):
    """{cover, shot1, send, close: grid cells or None, transitions: {send, close}} for one lesson. Opens its stage unless
    given a page; uses the hook report's first change for the first cut."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    own = pg is None
    if own:
        pw, b, pg = open_stage(slug)
    try:
        if hook is None:
            hook, _ = hook_report(slug, pg)
        wd = json.load(open(vdir(slug, "02_transcript", "words.json"))); words = wd["words"] if isinstance(wd, dict) else wd
        end_t = (words[-1]["end"] + 0.1) if words else cues["duration"] - END_TAIL
        tops = [c for c in cues["cues"] if c.get("level", 0) == 0]
        send = [c for c in cues["cues"] if c.get("send")]
        tr = pg.evaluate("(window.SCENE && window.SCENE.transitions) || {}") or {}
        ch = hook.get("changes") or []
        times = {"cover": 0.0, "shot1": (ch[0] + 0.3) if ch else None,
                 "send": (float(send[0]["t"]) + 1.5) if send else None, "close": end_t - 0.4}
        sig = {"slug": slug}
        for k_, t in times.items():
            sig[k_] = sorted(layout_cells(_boxes_at(pg, t))) if t is not None else None
        sec = next((c["id"].split(".")[0] for c in reversed(tops) if send and c["t"] <= float(send[0]["t"]) + 1e-6), None)
        sig["transitions"] = {"send": tr.get(sec) if sec else None, "close": tr.get(tops[-1]["id"]) if len(tops) > 1 else None}
    finally:
        if own:
            b.close(); pw.stop()
    return sig


def fresh_problems(me, others):
    """me and others: fresh signatures (others = the two lessons before). Returns (problems, report): a cover or first cut
    whose text layout matches one before at FRESH_MATCH or more, or send and close transitions both the same as one
    before. The report holds every match number, for the design gate."""
    out, rep = [], {}
    for o in others:
        m = {k_: jaccard(me.get(k_), o.get(k_)) for k_ in FRESH_KEYS if me.get(k_) and o.get(k_)}
        rep[o["slug"]] = dict(m, transitions=o.get("transitions"))
        for k_, name in (("cover", "cover (frame 0)"), ("shot1", "first hook cut")):
            if m.get(k_, 0) >= FRESH_MATCH:
                out.append(f"the {name} lays out its text like {o['slug']}'s ({m[k_]:.2f} match, {FRESH_MATCH} fails): move the hero, the lines or the shot")
        a, b_ = me.get("transitions") or {}, o.get("transitions") or {}
        if a.get("send") and a.get("close") and a.get("send") == b_.get("send") and a.get("close") == b_.get("close") \
                and not {a["send"], a["close"]} <= set(CUT_MOVES):   # plain cuts are the rule from Nov 9 (call 1)
            out.append(f"send and close transitions ({a['send']}, {a['close']}) copy {o['slug']}'s: change at least one (SCENE.transitions)")
    return out, rep


def lessons_before(slug, n=2):
    vids = sorted(d for d in os.listdir(VIDEOS) if re.match(r"\d{4}-\d\d-\d\d-", d) and not d.endswith(HOOKB_SUFFIX)
                  and os.path.exists(os.path.join(VIDEOS, d, "03_cues", "cues.json")) and os.path.exists(os.path.join(VIDEOS, d, "04_scene", "scene.js")))
    return [d for d in vids if d < slug][-n:]


def fresh_check(slug, pg=None, hook=None, write=True, me=None):
    """Signature for slug (or me, already taken), compared with the two lessons before; writes 04_scene/fresh.json.
    Returns (problems, report). Opens each lesson before in its own browser, so call it with no other stage open."""
    me = me or fresh_signature(slug, pg, hook)
    others = []
    for d in lessons_before(slug):
        try:
            others.append(fresh_signature(d))
        except (Exception, SystemExit) as e:   # a lesson before that no longer boots is skipped, and said so
            print(f"NOTE fresh: {d} skipped ({str(e)[:120]})")
    probs, rep = fresh_problems(me, others)
    if write:
        json.dump({"schema": "pnf.studio.fresh.v1", "me": me, "against": rep, "problems": probs},
                  open(vdir(slug, "04_scene", "fresh.json"), "w"), indent=None)
    return probs, rep


def cmd_cuestrings(slug, step=0.25):
    """Studio change 1: every string the scene draws (0.5 s or more, before the end card), and whether cues.md holds it.
    The same rule lint fails on for lessons from STUDIO_V3_FROM; run it after the first stills."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    wd = json.load(open(vdir(slug, "02_transcript", "words.json"))); wl = wd["words"] if isinstance(wd, dict) else wd
    end_t = (wl[-1]["end"] + 0.1) if wl else cues["duration"] - END_TAIL
    pw, b, pg = open_stage(slug)
    t, samples = 0.0, []
    while t < end_t:
        samples.append((t, [x for x in _boxes_at(pg, t) if x[1] in ("scene", "deco") and x[6] > 0.6 and str(x[0]).strip()]))
        t += step
    b.close(); pw.stop()
    probs = [p for p in layout_v3_problems(samples, open(vdir(slug, "03_cues", "cues.md"), encoding="utf-8").read(), end_t, step) if "cues.md" in p]
    for p in probs:
        print("MISSING " + p)
    print(f"cuestrings: {len(probs)} drawn string(s) missing from cues.md")
    if probs:
        sys.exit(1)


def cmd_fresh(slug):
    probs, rep = fresh_check(slug)
    for d, m in rep.items():
        print(f"fresh vs {d}: " + ", ".join(f"{k_} {v:.2f}" for k_, v in m.items() if k_ in FRESH_KEYS) + f"; transitions {m.get('transitions')}")
    for p in probs:
        print("ERROR fresh: " + p)
    print("fresh: " + ("FAIL" if probs else "PASS") + f" against {len(rep)} lesson(s) before")
    if probs:
        sys.exit(1)



# The hook move library (_shared/hooks.md; video-lab chat, Nov 8, 2026, Todd: "a hook move library with variety checks in
# code"). The brief's Hook pattern label never saw the real opening: 4 of the 7 lessons made Nov 6 to 8 opened on a clock
# moment ("Nine at night...", "Two in the afternoon...", "It's ten to seven on a weeknight.", "Picture the first cold
# night...") under four different labels. So the first spoken sentence of script.md is classified here, and from lessons
# dated STUDIO_V3_FROM a move may not repeat either of the two lessons before, nor appear in 2 of the 5 before; nor may
# the first three words, or half the first sentence's content words, repeat one of the lessons before.
HOOK_MOVES = (
    ("question", None),   # the first sentence asks the viewer something (ends in ?)
    ("clock-moment", r"\b(\d{1,2}(:\d\d)?\s?(am|pm|a\.m\.|p\.m\.)|at (one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)|o'clock|noon|midnight|night|tonight|weeknight|weekend|morning|afternoon|evening|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b"),
    ("you-scene", r"^(you|you're|your)\b"),
    ("money", r"(\$\d|\b(dollars?|grand|hundred|thousand|million|cost|costs|paid|pay|price|priced|charge[sd]?|losing|lose)\b)"),
    ("source-says", r"\b(says|said|reports?|survey(ed)?|study|data|according)\b"),
    ("short-line", None),  # five words or fewer
    ("claim", None),
)
OPENER_STOP = {"that", "this", "with", "your", "they", "them", "have", "what", "when", "then", "about", "there", "their",
               "just", "from", "into", "says", "it's", "you're", "here's", "were", "will", "would", "every", "after"}


def first_sentence(slug):
    p = vdir(slug, "01_voice", "script.md")
    if not os.path.exists(p):
        return ""
    t = TAG.sub(" ", open(p, encoding="utf-8").read())
    t = "\n".join(ln for ln in t.splitlines() if not ln.lstrip().startswith(("#", "<!--", ">")))
    sents = [x.strip() for x in re.split(r"(?<=[.?!])\s+", " ".join(t.split())) if x.strip()]
    return sents[0] if sents else ""


def hook_move(sentence):
    s = sentence.strip().lower().replace("’", "'")
    if not s:
        return None
    if s.endswith("?"):
        return "question"
    for name, rx in HOOK_MOVES:
        if rx and re.search(rx, s):
            return name
    return "short-line" if len(s.split()) <= 5 else "claim"


def opener_move_problems(slug):
    """The opening's variety against the 6 lessons made before it (by slug date). A source-matched experiment opens the
    way its source does (Todd, Nov 8, 8:25 pm), so it is not held to our own rotation."""
    if source_matched(slug):
        return []
    return opener_text_problems(first_sentence(slug), [(d, first_sentence(d)) for d in lessons_before(slug, 6)])


def opener_text_problems(me, before):
    out = []
    if not me:
        return out
    mv = hook_move(me)
    toks = lambda x: [w for w in re.findall(r"[a-z0-9']+", x.lower().replace("’", "'"))]
    content = lambda x: {w for w in toks(x) if len(w) >= 4 and w not in OPENER_STOP}
    moves = [(d, hook_move(t)) for d, t in before if t]
    near = [d for d, m in moves[-2:] if m == mv]
    if near:
        out.append(f"the opening is a {mv} move like {', '.join(near)} right before it (_shared/hooks.md: pick another move)")
    elif sum(1 for _, m in moves[-5:] if m == mv) >= 2:
        out.append(f"the opening is a {mv} move, already {sum(1 for _, m in moves[-5:] if m == mv)} of the 5 lessons before (_shared/hooks.md: pick another move)")
    for d, t in before:
        if t and toks(t)[:3] == toks(me)[:3]:
            out.append(f"the first three words '{' '.join(toks(me)[:3])}' open {d} too")
        a, b_ = content(me), content(t)
        if a and b_ and len(a & b_) / len(a) >= 0.5:
            out.append(f"the first sentence shares {len(a & b_)} of its {len(a)} content words with {d}'s ({', '.join(sorted(a & b_))})")
    return out


def cmd_hookmoves(slug=None):
    """The opening moves of the last 8 lessons, and the ones free for the next lesson (_shared/hooks.md)."""
    rows = [(d, first_sentence(d)) for d in lessons_before(slug or "9999", 8)]
    for d, t in rows:
        print(f"{d:36} {hook_move(t) or '-':13} {t[:70]}")
    taken = {hook_move(t) for _, t in rows[-2:]} | {m for m in {hook_move(t) for _, t in rows[-5:]} if sum(1 for _, t in rows[-5:] if hook_move(t) == m) >= 2}
    print("free for the next lesson: " + ", ".join(n for n, _ in HOOK_MOVES if n not in taken))


# The Nov 14 read (video-lab chat, Nov 8, 2026, Todd: "Set up a fair test that the Nov 14 read can judge, so we know
# whether the changes helped"; research/TEST-2026-11-14.md holds the plan and the bars, set before any result).
# One table, read the same way for both arms: rounds each gate took (from reviews/ and its r<n>/ folders), and each
# platform's numbers at the read nearest 72 h after its post (research/metrics). Arms: "v3" = lessons dated from
# STUDIO_V3_FROM (changes 1, 2, 4 and the hook moves in code); "base" = the proven lessons made before them.
COHORT_GATES = ("facts", "render-critic", "design", "send", "facts-captions")
PHONE_TOPIC = re.compile(r"(?i)\b(call|calls|phone|phones|missed|after[- ]hours|voicemail|text back|receptionist|answer)\b")


def gate_rounds(slug):
    """{gate: rounds it took to its last verdict}: the highest round seen in reviews/<gate>.json, reviews/r<n>/ and
    01_voice/prevoice/<gate>-r<n>.json, plus one. None when the gate never ran."""
    out = {}
    rv = vdir(slug, "05_render", "reviews")
    for g in COHORT_GATES:
        hi = -1
        f = os.path.join(rv, g + ".json")
        if os.path.exists(f):
            try:
                hi = max(hi, int(json.load(open(f)).get("round", 0) or 0))
            except Exception:
                pass
        for d in glob.glob(os.path.join(rv, "r[0-9]*")):
            if os.path.exists(os.path.join(d, g + ".json")):
                hi = max(hi, int(os.path.basename(d)[1:]))
        for f in glob.glob(vdir(slug, "01_voice", "prevoice", g + "-r[0-9]*.json")):
            m = re.search(r"-r(\d+)\.json$", f)
            hi = max(hi, int(m.group(1)) if m else hi)
        out[g] = hi + 1 if hi >= 0 else None
    return out


def _iso(x):
    try:
        return dt.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    except Exception:
        return None


def reads_at(slug, hours=72):
    """{platform: {metric: value}} from the read nearest `hours` after that platform's post (within 24 h of it), and the
    read's age in hours. Hidden or missing values are left out."""
    mf = os.path.join(HERE, "research", "metrics", slug + ".json")
    item = next((i for i in load_queue()["items"] if i["slug"] == slug), None)
    if not os.path.exists(mf) or not item or not item.get("posts"):
        return {}
    out = {}
    for pl, post in item["posts"].items():
        at = _iso(post.get("at")) if isinstance(post, dict) else None
        if not at:
            continue
        best = None
        for r in json.load(open(mf)).get("reads", []):
            ra = _iso(r.get("readAt"))
            m = (r.get("platforms") or {}).get(pl)
            if not ra or not m:
                continue
            age = (ra - at).total_seconds() / 3600
            if age > 0 and abs(age - hours) <= 24 and (best is None or abs(age - hours) < abs(best[0] - hours)):
                best = (age, {k: v for k, v in m.items() if isinstance(v, (int, float))})
        if best:
            out[pl] = dict(best[1], ageH=round(best[0], 1))
    return out


def cohort_rows():
    rows = []
    for d in sorted(os.listdir(VIDEOS)):
        if not re.match(r"\d{4}-\d\d-\d\d-", d) or d.endswith(HOOKB_SUFFIX) or lesson_format(d) != "proven":
            continue
        brief = open(vdir(d, "01_voice", "brief.md"), encoding="utf-8").read() if os.path.exists(vdir(d, "01_voice", "brief.md")) else ""
        rows.append({"slug": d, "arm": "v3" if d[:10] >= STUDIO_V3_FROM else "base",
                     "topic": "phone" if PHONE_TOPIC.search(first_sentence(d) + " " + brief[:600]) else "other",
                     "move": hook_move(first_sentence(d)), "rounds": gate_rounds(d), "at72": reads_at(d),
                     "acted": os.path.exists(vdir(d, "04_scene", "scene.js")) and "k.client(" in open(vdir(d, "04_scene", "scene.js"), encoding="utf-8").read()})
    return rows


def cmd_cohort():
    rows = cohort_rows()
    print("arm   lesson                              topic  move          " + " ".join(f"{g[:8]:>8}" for g in COHORT_GATES) + "  views72 (ig/tt/yt/fb)  shares72 follows72")
    for r in rows:
        a = r["at72"]
        v = "/".join(str(a.get(p, {}).get("views", "-")) for p in ("instagram", "tiktok", "youtube", "facebook"))
        sh = sum(a.get(p, {}).get("shares", 0) for p in a); fo = sum(a.get(p, {}).get("follows", 0) for p in a)
        print(f"{r['arm'] + ('*' if r.get('acted') else ''):5} {r['slug'][:35]:35} {r['topic']:6} {str(r['move']):13} " + " ".join(f"{str(r['rounds'][g] if r['rounds'][g] is not None else '-'):>8}" for g in COHORT_GATES)
              + f"  {v:21} {sh:8} {fo:9}")
    json.dump({"schema": "pnf.studio.cohort.v1", "at": now(), "rows": rows}, open(os.path.join(HERE, "research", "tests", "cohort.json"), "w"), indent=1)
    print("* = acts the conflict with k.client (decision 3's test lesson)\nwritten research/tests/cohort.json")

def captions_v4_problems(slug):
    """A v4 lesson's captions in code: the dilemma first (line 1 under 100 characters), one question, the source named when
    the brief names one, 3 to 5 hashtags (2 to 3 on Facebook and YouTube), no AI voice line, no dashes, and each
    platform's AI label set as its own rules require (V4_LABELS: the voice is a clone, which Meta and TikTok label;
    YouTube exempts a clone of your own voice)."""
    f = vdir(slug, "05_render", "captions.json")
    if not os.path.exists(f):
        return ["captions.json missing"]
    d, out = json.load(open(f)), []
    bp = vdir(slug, "01_voice", "brief.md")
    sourced = bool(re.search(r"(?im)^- \*\*Source:\*\*\s*\S", open(bp, encoding="utf-8").read())) if os.path.exists(bp) else False
    tags = {"instagram": (3, 5), "tiktok": (3, 5), "facebook": (2, 3), "youtube": (2, 3)}
    for pl, (lo, hi) in tags.items():
        if pl not in d:
            out.append(f"{pl}: missing"); continue
        text = d[pl].get("description" if pl == "youtube" else "caption") or ""
        first = text.split("\n")[0]
        if not first or len(first) >= 100: out.append(f"{pl}: line 1 is {len(first)} characters (1 to 99)")
        if "?" not in text: out.append(f"{pl}: no question for the viewer")
        if sourced and not re.search(r"(?i)\bsource:", text): out.append(f"{pl}: the brief names a source but the caption has no 'Source:' line")
        if AI_VOICE_LINE.search(text): out.append(f"{pl}: the AI voice line (Todd, Oct 29: none in any caption)")
        n = len(re.findall(r"(?<!\w)#\w+", text))
        if not lo <= n <= hi: out.append(f"{pl}: {n} hashtags ({lo} to {hi})")
        if re.search(r"(?i)#(fyp|foryou|viral)\b", text): out.append(f"{pl}: banned hashtag")
        if re.search("[\u2013\u2014]", text): out.append(f"{pl}: an em or en dash")
        key, want = V4_LABELS[pl]
        got = (d[pl].get("settings") or {}).get(key)
        if got is not want: out.append(f"{pl}: settings.{key} is {got!r} (must be {want!r}: the platform's own AI rule for a cloned voice)")
    y = d.get("youtube", {})
    if y:
        t = y.get("title", "")
        if not t or len(t) > 70 or "#" in t: out.append(f"youtube: the title is {len(t)} characters or has a hashtag (1 to 70, none)")
        if "?" not in t and "$" not in t: out.append("youtube: the title has no question and no dollar figure (the dilemma, not a search phrase)")
        if not 5 <= len(y.get("tags", [])) <= 10: out.append(f"youtube: {len(y.get('tags', []))} tags (5 to 10)")
        if re.search("[\u2013\u2014]", t): out.append("youtube: an em or en dash in the title")
    return out


def payoff_problems(cues):
    """v4: exactly one cue marked [payoff], starting by V4_PAYOFF_BY of the runtime."""
    ps = [c for c in cues.get("cues", []) if c.get("payoff")]
    if len(ps) != 1:
        return [f"{len(ps)} cues marked [payoff] in cues.md (exactly 1: the cue where the outcome or the answer lands)"]
    t, dur = float(ps[0]["t"]), float(cues["duration"])
    return [] if t <= V4_PAYOFF_BY * dur + 1e-6 else [f"the payoff cue '{ps[0]['id']}' starts at {t:.1f} s of {dur:.1f} s ({100 * t / dur:.0f}%; by {100 * V4_PAYOFF_BY:.0f}%)"]


def hold_problems(samples, step, limit=None):
    """v4: no set of settled words stands unchanged longer than V4_HOLD_MAX. samples: [(t, signature)], a signature being the
    sorted (string, box) tuples of the scene text on that frame; an empty frame resets the run."""
    limit = V4_HOLD_MAX if limit is None else limit
    out, start, prev = [], None, None
    for t, sig in list(samples) + [(None, None)]:
        if sig is not None and sig and sig == prev:
            continue
        if prev and start is not None:
            last = (t if t is not None else samples[-1][0] + step) - start
            if last > limit + 1e-6:
                out.append(f"{start:.2f} to {start + last:.2f} s: the same words stand {last:.1f} s ({limit:.0f} s at most): '{prev[0][0][:40]}'")
        start, prev = t, sig
    return out


def v4_static_problems(slug):
    """The v4 checks that need no browser: the payoff mark, the word band (a note), the captions and the plain cuts."""
    out = []
    cj = vdir(slug, "03_cues", "cues.json")
    if os.path.exists(cj):
        out += payoff_problems(json.load(open(cj)))
    if os.path.exists(vdir(slug, "05_render", "captions.json")):
        out += [f"captions: {x}" for x in captions_v4_problems(slug)]
    sj = vdir(slug, "04_scene", "scene.js")
    if os.path.exists(sj):
        out += [f"moves: {x}" for x in move_problems(open(sj, encoding="utf-8").read())]
    return out


def lint_v4(slug, step=0.25):
    """The v4 layout check: every settled scene text inside the v4 safe area (V4_SAFE, V4_SIDE), not under the captions or
    other text, at least V4_TEXT_FLOOR px of ink; no set of words standing over V4_HOLD_MAX; the picture changing by 1 s
    and twice by 3 s; the length band; the payoff by 40%; the captions and labels. Exit 1 on an ERROR."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    pw, b, pg = open_stage(slug)
    hook, hook_bad = hook_report(slug, pg)
    hits, small, sigs, t = {}, {}, [], 0.0
    def ov(p_, q_):
        w = min(p_["x1"], q_["x1"]) - max(p_["x0"], q_["x0"]); h = min(p_["y1"], q_["y1"]) - max(p_["y0"], q_["y0"])
        return max(0, w) * max(0, h)
    x0s, y0s, x1s, y1s = V4_SAFE
    while t < cues["duration"]:
        bx = pg.evaluate(f"(() => {{ window.__boxes = []; drawAt({t:.3f}); const r = window.__boxes; window.__boxes = null; return r; }})()")
        texts = [x for x in bx if x["tag"] == "scene" and x["a"] > 0.6 and x["s"].strip()]
        caps = [x for x in bx if x["tag"] == "dialogbox"]
        for x in texts:
            if x["x0"] < x0s or x["x1"] > x1s or x["y0"] < y0s or x["y1"] > y1s:
                hits.setdefault(("off the safe area", x["s"]), []).append(t)
            elif x["x1"] > V4_SIDE[0] and x["y1"] > V4_SIDE[1]:
                hits.setdefault(("under the platform's side buttons", x["s"]), []).append(t)
            for c in caps:
                if ov(x, c) > 0.08 * (x["x1"] - x["x0"]) * (x["y1"] - x["y0"]):
                    hits.setdefault(("under the captions", x["s"]), []).append(t)
            k_ = x["s"].strip()[:40]
            small[k_] = max(small.get(k_, 0), round(x["y1"] - x["y0"]))
        for i, x in enumerate(texts):
            for y in texts[i + 1:]:
                if ov(x, y) > 0.15 * min((x["x1"] - x["x0"]) * (x["y1"] - x["y0"]), (y["x1"] - y["x0"]) * (y["y1"] - y["y0"])):
                    hits.setdefault(("text on text", x["s"] + " / " + y["s"]), []).append(t)
        sigs.append((round(t, 3), tuple(sorted((x["s"].strip(), round(x["x0"]), round(x["y0"]), round(x["x1"]), round(x["y1"])) for x in texts))))
        t += step
    b.close(); pw.stop()
    errors = [f"ERROR lint hook: {x}" for x in hook_bad]
    errors += [f"ERROR lint v4: {x}" for x in v4_static_problems(slug)]
    errors += [f"ERROR lint hold: {x}" for x in hold_problems(sigs, step)]
    for (kind, what), ts in sorted(hits.items(), key=lambda kv: kv[1][0]):
        runs, start, prev = [], ts[0], ts[0]
        for x in ts[1:] + [None]:
            if x is None or x - prev > step * 1.5:
                if prev - start >= 0.5 - 1e-6:
                    runs.append((start, prev))
                if x is not None:
                    start = x
            if x is not None:
                prev = x
        for a0, a1 in runs:
            errors.append(f"ERROR lint {a0:5.2f} to {a1:5.2f} s: {kind}: {what[:70]}")
    errors += [f"ERROR lint type: '{s_}' is {h_} px tall ({V4_TEXT_FLOOR} or more)" for s_, h_ in sorted(small.items(), key=lambda kv: kv[1])
               if h_ < V4_TEXT_FLOOR and any(ch.isalnum() for ch in s_)]
    wp = vdir(slug, "02_transcript", "words.json")
    n = len(json.load(open(wp))["words"]) if os.path.exists(wp) else 0
    lo, hi = FORMATS[lesson_format(slug)]["words"]
    if n and not lo <= n <= hi:
        print(f"NOTE lint v4 (a guide, not a gate): {n} spoken words ({lo} to {hi})")
    for x in hook.get("notes", []):
        print("NOTE lint v4 (a guide, not a gate): " + x)
    print("hook: " + json.dumps(hook))
    print("\n".join(errors) if errors else f"lint: PASS v4 0 layout problems ({cues['duration']:.1f} s at {step} s steps); first change {hook['first_change']} s, "
          f"{hook['changes_by_3s']} by 3 s; payoff by {100 * V4_PAYOFF_BY:.0f}%; no hold over {V4_HOLD_MAX:.0f} s")
    if errors:
        sys.exit(1)


def cmd_lint(slug, step=0.25):
    if is_v4(slug):
        return lint_v4(slug, step)
    """The layout check in code, before a reviewer has to find it: every settled scene text inside the safe area
    (x 20 to 950, y 262 to 1250), not under the host, the dialog box or other text. Problems that last under 0.5 s
    (slide-ins, slams) are ignored. Exit 1 on an ERROR."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    pw, b, pg = open_stage(slug)
    hits = {}
    def ov(p, q, pad=0):
        w = min(p["x1"], q["x1"]) - max(p["x0"], q["x0"]) + pad; h = min(p["y1"], q["y1"]) - max(p["y0"], q["y0"]) + pad
        return max(0, w) * max(0, h)
    hook, hook_bad = hook_report(slug, pg)   # before the world spy, on a clean page
    send_line = pg.evaluate("(window.SCENE && window.SCENE.sendLine) || ''") if is_modern(slug) else None
    moves = pg.evaluate("(() => { const S = window.SCENE || {}; return {t: S.transitions || {}, s: Object.keys(S.sections || {})}; })()")
    pg.evaluate(WORLD_SPY)
    t, worlds, steps, small, first_seen, last_seen = 0.0, {}, 0, {}, {}, {}
    # the send card's hold (Todd, Nov 7, 9:27 am): sampled from its cue to the next cue (or the end card)
    sc = [c for c in cues["cues"] if c.get("send")] if send_applies(slug) else []
    s0 = float(sc[0]["t"]) if len(sc) == 1 else None
    s1 = min([float(d["t"]) for d in cues["cues"] if float(d["t"]) > s0 + 1e-6] + [cues["duration"] - END_TAIL]) if s0 is not None else None
    send_samples, v3_samples = [], []
    v3 = os.path.basename(slug)[:10] >= STUDIO_V3_FROM and not slug.endswith(HOOKB_SUFFIX)
    while t < cues["duration"]:
        bx, used = pg.evaluate(f"(() => {{ window.__boxes = []; window.__used = {{}}; drawAt({t:.3f}); const r = window.__boxes; window.__boxes = null; return [r, Object.keys(window.__used)]; }})()")
        steps += 1
        for w in used:
            worlds[w] = worlds.get(w, 0) + 1
        texts = [x for x in bx if x["tag"] == "scene" and x["a"] > 0.6 and x["s"].strip()]
        v3_samples.append((t, [(x["s"], x["tag"], x["x0"], x["y0"], x["x1"], x["y1"], x["a"]) for x in bx
                               if x["tag"] in ("scene", "deco") and x["a"] > 0.6 and x["s"].strip()]))
        host = [x for x in bx if x["tag"] == "host"]; dlg = [x for x in bx if x["tag"] == "dialogbox"]
        for x in texts:
            if x["x0"] < 20 or x["x1"] > 950 or x["y0"] < 262 or x["y1"] > 1250:
                hits.setdefault(("off the safe area", x["s"]), []).append(t)
            for o, name in [(h, "under the host") for h in host] + [(d, "under the dialog box") for d in dlg]:
                if ov(x, o) > 0.08 * (x["x1"] - x["x0"]) * (x["y1"] - x["y0"]):
                    hits.setdefault((name, x["s"]), []).append(t)
        if s0 is not None and s0 - 1e-6 <= t < s1 - 1e-6:
            sig = tuple(sorted((x["s"].strip(), round(x["x0"]), round(x["y0"]), round(x["x1"]), round(x["y1"])) for x in texts))
            box = [min(x["x0"] for x in texts) - 8, min(x["y0"] for x in texts) - 8, max(x["x1"] for x in texts) + 8,
                   max(x["y1"] for x in texts) + 8] if texts else [0, 0, 1, 1]
            send_samples.append((t, sig, pg.evaluate(f"({SEND_PIX_JS})({json.dumps(box)})") if texts else []))
        for x in texts:   # M3 accent timing (IMPROVE 00a-3): when each scene text first shows
            first_seen.setdefault(x["s"].strip(), t)
            last_seen[x["s"].strip()] = t   # M6 read time (IMPROVE 00a-5): when it was last on screen
        for x in texts:   # the type floor (IMPROVE 00b): a label's tallest settled ink height, over the whole lesson
            k_ = x["s"].strip()[:40]
            small[k_] = max(small.get(k_, 0), round(x["y1"] - x["y0"]))
        for i, x in enumerate(texts):
            for y in texts[i + 1:]:
                if ov(x, y) > 0.15 * min((x["x1"] - x["x0"]) * (x["y1"] - x["y0"]), (y["x1"] - y["x0"]) * (y["y1"] - y["y0"])):
                    hits.setdefault(("text on text", x["s"] + " / " + y["s"]), []).append(t)
        t += step
    me = fresh_signature(slug, pg, hook) if v3 else None   # studio change 2: this lesson's frames, while its stage is open
    b.close(); pw.stop()
    errors = [f"ERROR lint captions: {x}" for x in captions_problems(slug)] if os.path.exists(vdir(slug, "05_render", "captions.json")) and not slug.endswith(HOOKB_SUFFIX) else []
    errors += [f"ERROR lint hook: {x}" for x in hook_bad]
    still = send_still_seconds(send_samples, step) if s0 is not None else None
    errors += [f"ERROR lint send: {x}" for x in send_problems(slug, send_line, still)]
    if still is not None:
        print(f"send: card up at {s0:.2f} s of {cues['duration']:.2f} s (half {cues['duration'] / 2:.2f} s), holds still {still:.2f} s")
    lint_notes = []
    errors += [f"ERROR lint script: {x}" for x in script_problems(slug, send_line, lint_notes)]
    for x in lint_notes + hook.get("notes", []):
        print("NOTE lint (a guide, not a gate; REBUILD.md Relaxed): " + x)
    if not slug.endswith(HOOKB_SUFFIX):   # a second opening is its lesson after the hook: the lesson passed variety
        errors += [f"ERROR lint variety: {x}" for x in variety_problems(slug, {w: round(n / max(1, steps), 3) for w, n in worlds.items()})]
        errors += [f"ERROR lint queue variety: {x}" for x in queue_variety_problems(slug)]
    for (kind, what), ts in sorted(hits.items(), key=lambda kv: kv[1][0]):
        runs, start, prev = [], ts[0], ts[0]
        for x in ts[1:] + [None]:
            if x is None or x - prev > step * 1.5:
                if prev - start >= 0.5 - 1e-6:
                    runs.append((start, prev))
                if x is not None:
                    start = x
            if x is not None:
                prev = x
        for a0, a1 in runs:
            errors.append(f"ERROR lint {a0:5.2f} to {a1:5.2f} s: {kind}: {what[:70]}")
    if v3:   # studio changes 1, 2 and 4 (Todd, live chat, Nov 7, 2026, 6:59 pm: "Go with your recommendation")
        wd = json.load(open(vdir(slug, "02_transcript", "words.json"))); wl = wd["words"] if isinstance(wd, dict) else wd
        end_t = (wl[-1]["end"] + 0.1) if wl else cues["duration"] - END_TAIL
        cm = vdir(slug, "03_cues", "cues.md")
        errors += [f"ERROR lint layout: {x}" for x in layout_v3_problems(v3_samples, open(cm, encoding="utf-8").read() if os.path.exists(cm) else "", end_t, step)]
        errors += [f"ERROR lint opening: {x}" for x in opener_move_problems(slug)]
        if proven_hook_hard(slug):
            errors += [f"ERROR lint cover: {x}" for x in cover_word_problems(v3_samples[0][1] if v3_samples and v3_samples[0][0] == 0 else [])]
        if recs_apply(slug):   # Todd's calls 1 and 2 (live chat, Nov 9, 2026, 7:33 am, "Recs")
            sj_ = vdir(slug, "04_scene", "scene.js")
            errors += [f"ERROR lint moves: {x}" for x in move_problems(open(sj_, encoding="utf-8").read() if os.path.exists(sj_) else "")]
            errors += [f"ERROR lint example: {x}" for x in example_tag_problems(v3_samples, step)]
        fp, frep = fresh_check(slug, me=me)
        errors += [f"ERROR lint fresh: {x}" for x in fp]
        for d, m in frep.items():
            print(f"fresh vs {d}: " + ", ".join(f"{k_} {v:.2f}" for k_, v in m.items() if k_ in FRESH_KEYS) + f"; transitions {m.get('transitions')}")
    print("hook: " + json.dumps(hook))
    late, ontime = accent_report(slug, first_seen, step)
    # IMPROVE 00a-3 (Nov 1, lunch run): for lessons dated from ACCENT_ERROR_FROM on, a text that lands ACCENT_ERROR_LATE s
    # or more after its spoken word is an ERROR (the scene moves it ahead of the word); smaller slips stay a WARN.
    # Step 2 (Nov 2, end-of-day run): three-fixes and price-list-quote both passed at 0.5 with 0 late texts, so lessons
    # dated from ACCENT_STRICT_FROM on fail on any text that lands a lint step or more after its word.
    day = os.path.basename(slug)[:10]
    if day >= ACCENT_ERROR_FROM:
        limit = 0.0 if day >= ACCENT_STRICT_FROM else ACCENT_ERROR_LATE
        errors += [f"ERROR lint accents: '{s_[:40]}' lands {-lead:.2f} s after '{w_}' (M3: 0.2 to 0.3 s before; move it ahead or rename it)"
                   for s_, w_, lead in late if lead <= -limit]
    if late:   # a warning, not an ERROR (M3, _shared/standard.md): the design gate and render critic judge it
        print(f"WARN lint accents: {len(late)} scene texts land after their spoken word (M3 wants 0.2 to 0.3 s before; "
              f"{ontime} land in time): " + "; ".join(f"'{s_[:30]}' {lead:+.2f} s vs '{w_}'" for s_, w_, lead in late[:12]))
    short = read_time_report(first_seen, last_seen, cues["duration"], step)
    # IMPROVE 00a-5 step 2 (Nov 8, evening run): three proven lessons in a row kept 21 to 26% of their runtime on TikTok
    # (rule 2, the middle), and the waiting lessons flash words for a third of their read time (worth-without-you: 'WHO
    # DOES IT?' 0.2 of 2.1 s). For lessons dated from READ_ERROR_FROM on, a text held under READ_ERROR_SHARE of its read
    # time is an ERROR (hold it longer or cut it); shorter slips stay the WARN below.
    if day >= READ_ERROR_FROM:
        errors += [f"ERROR lint read time: '{s_[:40]}' holds {held:.1f} of {need:.1f} s (M6: letters / 15 + 1.5 s; under half fails)"
                   for s_, held, need in short if held < READ_ERROR_SHARE * need]
    if short:   # a warning, not an ERROR (M6, _shared/standard.md): the design gate and render critic judge it
        print(f"WARN lint read time: {len(short)} scene texts leave before a viewer can read them (M6: letters / 15 + 1.5 s): "
              + "; ".join(f"'{s_[:30]}' {held:.1f} of {need:.1f} s" for s_, held, need in short[:12]))
    plain = room_move_report(moves) if not recs_apply(slug) else ""
    if plain:   # a warning, not an ERROR (M4, _shared/standard.md; IMPROVE 00a-4): the design gate judges the travel
        print("WARN lint room moves: " + plain)
    small = {s_: h_ for s_, h_ in small.items() if h_ < LABEL_FLOOR_PX and any(c.isalnum() for c in s_)}
    if small:   # a warning, not an ERROR: lessons pinned before Oct 31 keep their labels; the design gate weighs them
        print(f"WARN lint type: {len(small)} scene labels under {LABEL_FLOOR_PX} px tall (IMPROVE 00b): "
              + "; ".join(f"'{s_}' {h_} px" for s_, h_ in sorted(small.items(), key=lambda kv: kv[1])[:12]))
    print("\n".join(errors) if errors else f"lint: PASS 0 layout problems ({cues['duration']:.1f} s at {step} s steps); hook PASS (first change {hook['first_change']} s, {hook['changes_by_3s']} by 3 s, host {hook['host_at']} s, spoken hook {hook['hook_words']} words by {hook['hook_said_by']} s)")
    if errors:
        sys.exit(1)


def cmd_export(slug, src=None, out=None):
    """Chrome's file upload takes at most 10 MB a call, so the post copy aims at 9.3 MB (two-pass, pixel art tune)."""
    src = src or vdir(slug, "05_render", f"{slug}.mp4")
    out = out or vdir(slug, "05_render", f"{slug}-post.mp4")
    if os.path.getsize(src) / 1e6 < 9.5:   # the steady pixel look renders small: the render itself is the post copy
        sh(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-c", "copy", "-movflags", "+faststart", out])
        print(f"export: {out} ({os.path.getsize(out) / 1e6:.1f} MB, the render as is)")
        return
    secs = float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src]).stdout.strip())
    for fit in (1.0, 0.85, 0.7):   # two-pass can overshoot on pixel art: aim lower until it fits
        vk = int(9.3 * 8 * 1000 * fit / secs) - 128
        tmp = tempfile.mkdtemp()
        base = ["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-c:v", "libx264", "-preset", "slow", "-tune", "animation",
                "-b:v", f"{vk}k", "-pix_fmt", "yuv420p", "-passlogfile", os.path.join(tmp, "p")]
        sh(base + ["-pass", "1", "-an", "-f", "mp4", os.devnull])
        sh(base + ["-pass", "2", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out])
        shutil.rmtree(tmp, ignore_errors=True)
        mb = os.path.getsize(out) / 1e6
        if mb < 9.9:
            break
    if mb >= 9.9:
        raise SystemExit(f"ERROR export: {mb:.1f} MB, over the 10 MB upload cap")
    print(f"export: {out} ({mb:.1f} MB, video {vk} kbps)")


def cmd_render(slug, look=None, t_from=None, t_to=None, out=None):
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    a = t_from or 0.0
    z = t_to or cues["duration"]
    n = int(round((z - a) * FPS))
    out = out or vdir(slug, "05_render", f"{slug}.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    tmp = tempfile.mkdtemp()
    pw, b, pg = open_stage(slug, look)
    t0 = time.time()
    enc = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", os.path.join(tmp, "silent.mp4")], stdin=subprocess.PIPE)
    for i in range(n):
        enc.stdin.write(frame(pg, a + i / FPS))
        if i and i % 300 == 0:
            print(f"  {i}/{n} frames, {time.time() - t0:.0f} s")
    enc.stdin.close(); enc.wait()
    b.close(); pw.stop()
    wav = os.path.join(tmp, "mix.wav")
    seconds = n / FPS
    if a:   # a clip (style tests) gets its own slice of the mix
        full = os.path.join(tmp, "full.wav"); has_voice = mix(slug, cues["duration"], full, cues)
        sh(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{a:.3f}", "-t", f"{seconds:.3f}", "-i", full, wav])
    else:
        has_voice = mix(slug, seconds, wav, cues)
    sh(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(tmp, "silent.mp4"), "-i", wav, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-movflags", "+faststart", out])
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"render: {out} ({n} frames, {seconds:.2f} s, {'voice' if has_voice else 'no voice (estimate timings)'}, {time.time() - t0:.0f} s)")
    return out


def cmd_check(slug, mp4=None):
    import video_qa as Q
    mp4 = mp4 or vdir(slug, "05_render", f"{slug}.mp4")
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    close_cue = max(c["t"] for c in cues["cues"] if c["level"] == 0)
    # IMPROVE 00i (Oct 30): the frozen window runs to the end card (0.1 s after the last word, as player.js END_T), not
    # the close cue, so the close room is checked too.
    try:
        ws = json.load(open(vdir(slug, "02_transcript", "words.json")))["words"]
        end_card = round(ws[-1]["end"] + 0.1, 3) if ws else close_cue
    except Exception:
        end_card = close_cue
    end_card = max(end_card, close_cue)
    checks = []
    lo, hi = length_band(slug)
    def c_len():
        secs = float(Q.probe(mp4)["format"]["duration"])
        return round(secs, 3), lo <= secs <= hi, f"{secs:.2f} s ({lo:.1f} to {hi:.1f}, {lesson_format(slug)} lesson, end card included)"
    for name, fn in [("length", c_len), ("loudness", lambda: Q.c_loudness(mp4)), ("black", lambda: Q.c_black(mp4)),
                     ("frozen", lambda: Q.c_frozen(mp4, end_card)),
                     # M1 (_shared/standard.md; Todd, Oct 31, 2026: "We need to set a higher standard"): never flat
                     ("flat", lambda: Q.c_flat(mp4, end_card))]:
        try:
            v, ok, d = fn()
        except Exception as e:
            v, ok, d = None, False, f"could not run: {e}"
        checks.append({"name": name, "value": v, "pass": ok, "detail": d})
    info = Q.probe(mp4)
    vs = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    au = [s for s in info["streams"] if s["codec_type"] == "audio"]
    fok = vs["codec_name"] == "h264" and (vs["width"], vs["height"]) == (1080, 1920) and vs["r_frame_rate"] in ("30/1",) and au and au[0]["codec_name"] == "aac"
    dec = sh(["ffmpeg", "-v", "error", "-i", mp4, "-f", "null", "-"], check=False)
    fok = fok and not dec.stderr.strip() and int(info["format"]["size"]) < 100e6
    checks.append({"name": "file", "value": {"sha256": sha(mp4), "bytes": int(info["format"]["size"])}, "pass": bool(fok),
                   "detail": f"H.264 1080x1920 30 fps, AAC, {int(info['format']['size']) / 1e6:.1f} MB, decodes clean" if fok else "file problem"})
    wd = json.load(open(vdir(slug, "02_transcript", "words.json")))
    checks.append({"name": "voice", "value": wd.get("source"), "pass": str(wd.get("source", "")).startswith("whisper") and not wd.get("flags"),
                   "detail": f"{wd.get('source')}, {len(wd.get('flags') or [])} flag(s)"})
    doc = {"schema": "pnf.studio.qa.v1", "slug": slug, "mp4Sha256": sha(mp4), "checks": checks, "pass": all(c["pass"] for c in checks), "at": now()}
    json.dump(doc, open(vdir(slug, "05_render", "qa.json"), "w"), indent=1)
    for c in checks:
        print(f"{c['name']}: {'PASS' if c['pass'] else 'FAIL'} {c['detail']}")
    print("qa:", "PASS" if doc["pass"] else "FAIL")


def cmd_status(slug):
    for rel in ["01_voice/brief.md", "01_voice/script.md", "01_voice/speak.json", "01_voice/takes.json", "01_voice/audio/voice.mp3",
                "02_transcript/words.json", "02_transcript/transcript.md", "03_cues/cues.md", "03_cues/cues.json", "04_scene/data.js",
                "04_scene/scene.js", "05_render/sheet.jpg", f"05_render/{slug}.mp4", "05_render/qa.json"]:
        p = vdir(slug, rel)
        print(f"{'x' if os.path.exists(p) else ' '} {rel}")


def cmd_new(slug):
    d = vdir(slug)
    if os.path.exists(d):
        raise SystemExit(f"ERROR new: {slug} exists")
    for sub in ["01_voice", "02_transcript", "03_cues", "04_scene/assets", "05_render"]:
        os.makedirs(os.path.join(d, sub))
    for f in ["brief.md", "script.md"]:
        shutil.copy(os.path.join(HERE, "_templates", f), os.path.join(d, "01_voice", f))
    shutil.copy(os.path.join(HERE, "_templates", "cues.md"), os.path.join(d, "03_cues", "cues.md"))
    shutil.copy(os.path.join(HERE, "_templates", "scene.js"), os.path.join(d, "04_scene", "scene.js"))
    print(f"new: {d}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd")
    ap.add_argument("slug", nargs="?")
    ap.add_argument("rest", nargs="*")
    ap.add_argument("--look"); ap.add_argument("--from", dest="t_from", type=float); ap.add_argument("--to", dest="t_to", type=float)
    ap.add_argument("--out"); ap.add_argument("--mp4"); ap.add_argument("--take", type=int, action="append"); ap.add_argument("--voice"); ap.add_argument("--first", action="store_true"); ap.add_argument("--not-before", dest="not_before")
    a = ap.parse_args()
    c = a.cmd
    if c == "kit":
        build_map(); build_sfx(); build_music(); build_pixfont()
    elif c == "sound":
        build_sfx(); build_music()
    elif c == "ci-voice":
        cmd_ci_voice()
    elif c == "next":
        cmd_next()
    elif c == "missed":
        cmd_missed(a.slug)
    elif c == "postcaptions":
        cmd_postcaptions(a.slug)
    elif c == "waiting":
        cmd_waiting()
    elif c == "lostmatch":
        cmd_lostmatch(a.slug, *(a.rest + ["", ""])[:2])
    elif c == "tomake":
        cmd_tomake()
    elif c == "shelve":
        cmd_shelve(a.slug, " ".join(a.rest))
    elif c == "readcheck":
        cmd_readcheck(a.slug, (a.rest or [""])[0])
    elif c == "storysnap":
        cmd_storysnap(a.slug)
    elif c == "storycarry":
        cmd_storycarry(a.slug)
    elif c == "cohort":
        cmd_cohort()
    elif c == "hookmoves":
        cmd_hookmoves(a.slug)
    elif c == "fresh":
        cmd_fresh(a.slug)
    elif c == "cuestrings":
        cmd_cuestrings(a.slug)
    elif c == "variety":
        cmd_variety(a.slug)
    elif c == "lanes":
        cmd_lanes()
    elif c == "tunes":
        cmd_tunes(a.slug)
    elif c == "trials":
        cmd_trials()
    elif c == "recuts":
        cmd_recuts()
    elif c == "selftest":
        cmd_selftest()
    elif c == "nextlane":
        cmd_nextlane()
    elif not a.slug:
        raise SystemExit(f"{c} needs a slug")
    elif c == "new":
        cmd_new(a.slug)
    elif c == "feedshared":
        cmd_feedshared(a.slug, a.rest[0] if a.rest else None)
    elif c == "data":
        cmd_data(a.slug)
    elif c == "speak":
        cmd_speak(a.slug, a.take, a.voice)
    elif c == "estimate":
        cmd_estimate(a.slug)
    elif c == "rewords":
        cmd_rewords(a.slug)
    elif c == "fetch":
        cmd_fetch(a.slug)
    elif c == "cues":
        cmd_cues(a.slug)
    elif c == "mouth":
        cmd_mouth(a.slug)
    elif c == "grab":
        cmd_grab(a.slug)
    elif c == "stills":
        cmd_stills(a.slug, a.look)
    elif c == "hold":
        cmd_hold(a.slug, " ".join(a.rest))
    elif c == "unhold":
        cmd_hold(a.slug, "", off=True)
    elif c == "posted":
        cmd_posted(a.slug, a.rest[0] if len(a.rest) > 0 else "", a.rest[1] if len(a.rest) > 1 else "",
                   a.rest[2] if len(a.rest) > 2 else None)
    elif c == "ready":
        cmd_ready(a.slug, a.first, a.not_before)
    elif c == "hookb":
        cmd_hookb(a.slug)
    elif c == "hookready":
        cmd_hookready(a.slug)
    elif c == "export":
        cmd_export(a.slug)
    elif c == "lint":
        cmd_lint(a.slug)
    elif c == "hook":
        cmd_hook(a.slug)
    elif c == "script":
        cmd_script(a.slug)
    elif c == "sendcheck":
        cmd_sendcheck(a.slug)
    elif c == "copycheck":
        cmd_copycheck(a.slug)
    elif c == "sourceprint":   # anim.py sourceprint <source url> <text file under data/> <how it was read>
        cmd_sourceprint(a.slug, a.rest[0], " ".join(a.rest[1:]) or "read by the run")

    elif c == "gatepack":
        cmd_gatepack(a.slug)
    elif c == "postcopy":
        cmd_postcopy(a.slug)
    elif c == "fingerprint":
        print(json.dumps(fingerprints(a.slug)))
    elif c == "remix":
        cmd_remix(a.slug)
    elif c == "render":
        cmd_render(a.slug, a.look, a.t_from, a.t_to, a.out)
    elif c == "check":
        cmd_check(a.slug, a.mp4)
    elif c == "status":
        cmd_status(a.slug)
    else:
        raise SystemExit(f"unknown command {c}")


if __name__ == "__main__":
    main()
