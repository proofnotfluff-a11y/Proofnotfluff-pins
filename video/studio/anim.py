#!/usr/bin/env python3
"""Studio commands (video/studio/CLAUDE.md, CONTEXT.md). One command per stage; every output is a file a person or a
fresh reviewer checks before the next stage runs.

  kit                      build _runtime/map.js (77 community areas), pixfont.js and the sounds (below)
  sound                    our own sounds, made in code: _runtime/sfx/*.wav (effects, takes, tick ladder, sting) and
                           _runtime/music/<room>.wav (the four room loops for "music: rooms")
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
  grab SLUG                capture docs/chicago-rat-complaints/ at phone width -> 04_scene/assets/rat-page.png
  stills SLUG [--look L]   a frame at every cue -> 05_render/sheets/*.jpg and 05_render/sheet.jpg
  render SLUG [--look L] [--from S --to S] [--out F]   frames in Chromium, the mix, H.264/AAC
  check SLUG [--mp4 F]     length, loudness, black, frozen, file -> 05_render/qa.json
  lint SLUG                the layout check in code: text off the safe area, under the host, the dialog box or other text
  gatepack SLUG            timeline sheets (2 frames a second) and first frames for the fresh reviewers -> 05_render/gates/
  export SLUG              a copy under 9.5 MB for posting (two-pass H.264; Chrome uploads cap at 10 MB) -> 05_render/SLUG-post.mp4
  ready SLUG               every gate passed: queue it for posting (video/studio/queue.json, fingerprints of what the gates saw)
  next                     the oldest queued lesson not yet on all four platforms, and the commit its gates passed at
  waiting                  the queued lessons with no post yet, in posting order (the daily run's queue rule reads it)
  postcopy SLUG            render the queued lesson from that commit, check its fingerprints, export it to the upload folder
  posted SLUG PLATFORM URL record one live post (instagram, tiktok, facebook, youtube)
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
VOICE_SETTINGS = {"W3pJy9ibur1FKUihVxzY": {"stability": 0.6, "similarity_boost": 0.8, "style": 0.15, "use_speaker_boost": True}}
MODEL = "eleven_v4"
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"
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


# Room loops: one key (A minor), one tempo (96 BPM), 8 bars = 20.0 s, so any room can cross into any other on the beat.
BPM, LOOP_BARS = 96, 8
BEAT = 60 / BPM
ROOMS = ("framing", "blackboard", "workshop", "garage")
CHORDS = [  # per bar: triad (around the octave below middle C), bass root
    ([57, 60, 64], 45), ([53, 57, 60], 41), ([55, 60, 64], 48), ([55, 59, 62], 43),   # Am  F  C  G
    ([57, 60, 64], 45), ([53, 57, 60], 41), ([57, 62, 65], 38), ([56, 59, 64], 40)]   # Am  F  Dm E (back to Am)
LEAD = [(0, 1.5, 72), (1.5, 0.5, 71), (2, 2, 69), (8, 1, 67), (9, 1, 72), (10, 2, 76),   # (beat, beats, note): call and
        (16, 1.5, 76), (17.5, 0.5, 74), (18, 2, 72), (24, 1, 69), (25, 1, 72), (26, 2, 74), (28, 2, 71), (30, 2, 68)]   # rest


def build_music():
    """Four chiptune loops, one per room, synthesized band-limited at 44.1 kHz and written as mono 22.05 kHz 16-bit wav
    (under 1 MB each) to _runtime/music/<room>.wav. Same key, tempo, chords and quiet square lead in every room; the
    rooms differ in what plays under it:
      framing     half-time: triangle bass on 1 and 3, sparse 25% plucks, a soft snare on 3, hats on 2 and 4
      blackboard  12.5% pulse arpeggios in sixteenths, triangle bass on every beat, light eighth hats
      workshop    25% offbeat chord stabs, eighth hats with an open hat, bouncing triangle bass, kick on 1 and 3
      garage      50% pulse bass riff, triangle kick slide on 1 and 3, noise snare on 2 and 4, eighth hats"""
    import numpy as np
    from scipy.signal import resample_poly
    sr = 44100
    L = int(round(LOOP_BARS * 4 * BEAT * sr))
    for ri, room in enumerate(ROOMS):
        rng = np.random.default_rng(500 + ri)
        y = np.zeros(L + 2 * sr)

        def put(beat, sig, g):
            i = int(round(beat * BEAT * sr)); y[i:i + len(sig)] += g * sig

        def noise(dur, fc, decay, high=True):
            n = int(dur * sr); t = np.arange(n) / sr
            return onepole(rng.standard_normal(n), fc, sr, high=high) * np.exp(-t / decay)

        def kick():
            n = int(0.16 * sr); t = np.arange(n) / sr
            return tri(150 * (50 / 150) ** np.clip(t / 0.08, 0, 1), sr) * np.exp(-t / 0.07)

        for bar, (triad, root) in enumerate(CHORDS):
            b0 = bar * 4
            if room == "framing":
                for k in (0, 2):
                    put(b0 + k, chip_note("tri", root if k == 0 else root + 7, 1.8 * BEAT, sr, s=0.8, r=0.08), 0.42)
                for k, m in ((1, triad[2]), (2.5, triad[1]), (3.5, triad[0] + 12)):
                    put(b0 + k, chip_note("pulse", m, 0.09, sr, 0.25, d=0.06, s=0.3, r=0.12), 0.16)
                put(b0 + 2, noise(0.12, 900, 0.035), 0.10)
                for k in (1, 3):
                    put(b0 + k, noise(0.03, 6000, 0.008), 0.07)
                put(b0, kick(), 0.30)
            elif room == "blackboard":
                arp = [triad[0], triad[1], triad[2], triad[0] + 12]
                for k in range(16):
                    put(b0 + k / 4, chip_note("pulse", arp[k % 4], 0.13, sr, 0.125, d=0.08, s=0.4, r=0.02), 0.11)
                for k in range(4):
                    put(b0 + k, chip_note("tri", root, 0.9 * BEAT, sr, s=0.8, r=0.05), 0.40)
                for k in range(8):
                    put(b0 + k / 2, noise(0.03, 7000, 0.006), 0.045 if k % 2 else 0.06)
            elif room == "workshop":
                for k in range(4):
                    for m in triad:
                        put(b0 + k + 0.5, chip_note("pulse", m, 0.11, sr, 0.25, d=0.08, s=0.4, r=0.03), 0.07)
                for k in range(8):
                    put(b0 + k / 2, chip_note("tri", root + (12 if k % 2 else 0), 0.42 * BEAT, sr, s=0.8, r=0.03), 0.36)
                    put(b0 + k / 2, noise(0.12 if k == 7 else 0.03, 7000, 0.04 if k == 7 else 0.007), 0.06)
                for k in (0, 2):
                    put(b0 + k, kick(), 0.35)
            else:   # garage
                riff = [0, 0, 12, 0, 7, 0, 12, 7]
                for k in range(8):
                    put(b0 + k / 2, onepole(chip_note("pulse", root + riff[k], 0.4 * BEAT, sr, 0.5, d=0.1, s=0.5, r=0.03), 1800, sr), 0.16)
                for k in (0, 2, 2.5):
                    put(b0 + k, kick(), 0.45)
                for k in (1, 3):   # the snare kept under 3 kHz, out of the voice's consonants
                    put(b0 + k, onepole(onepole(noise(0.12, 600, 0.04), 2500, sr), 2500, sr), 0.30)
                for k in range(8):
                    put(b0 + k / 2, noise(0.03, 7000, 0.007), 0.05)
        lead_duty, lead_g = {"framing": (0.5, 0.06), "blackboard": (0.25, 0.06), "workshop": (0.25, 0.06), "garage": (0.25, 0.036)}[room]
        for beat, beats, m in LEAD:   # quiet (about 16 dB under the rest), with an echo 1/8 later at -9 dB, +7 cents
            dur = beats * BEAT * 0.92
            for at, g, c in ((0, 1.0, 0.0), (0.5, 10 ** (-9 / 20), 7.0)):
                put(beat + at, chip_note("pulse", m, dur, sr, lead_duty, c, d=0.12, s=0.6, r=0.06, vib=beats >= 1), lead_g * g)
        y[:len(y) - L] += y[L:]          # what rings past the end comes back in at the start: a seamless loop
        y = onepole(y[:L], 20, sr, high=True)
        y = resample_poly(y, 1, 2)       # to 22.05 kHz, through resample_poly's anti-alias filter
        y *= 0.12 / np.sqrt(np.mean(y ** 2))   # the same RMS in every room, so a crossfade never jumps
        if np.max(np.abs(y)) > 0.95:
            y *= 0.95 / np.max(np.abs(y))
        write_wav(os.path.join(RUNTIME, "music", room + ".wav"), y, sr // 2)
    print(f"music: {' '.join(ROOMS)} ({LOOP_BARS} bars at {BPM} BPM, A minor, {LOOP_BARS * 4 * BEAT:.1f} s each)")


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
            arc = subprocess.run(["git", "-C", ROOT, "archive", f"origin/{BRANCH}", f"studio/{slug}/01_voice/takes"], capture_output=True)
            subprocess.run(["tar", "-x", "-C", old], input=arc.stdout)
        info = []
        for i, t in enumerate(takes):
            n = i + 1
            f = os.path.join(out, "takes", f"{n:02d}.mp3")
            keep = os.path.join(old, "studio", slug, "01_voice", "takes", f"{n:02d}.mp3")
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
    for slug, out in done:
        dst = os.path.join(wt, "studio", slug, "01_voice")
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
        push_retry(ROOT, "main")


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
    arc = subprocess.run(["git", "-C", ROOT, "archive", f"origin/{BRANCH}", f"studio/{slug}/01_voice"], capture_output=True)
    if arc.returncode:
        raise SystemExit(f"ERROR fetch: no audio for {slug} on {BRANCH} yet")
    tmp = tempfile.mkdtemp()
    subprocess.run(["tar", "-x", "-C", tmp], input=arc.stdout, check=True)
    src = os.path.join(tmp, "studio", slug, "01_voice")
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


def cmd_cues(slug):
    src = open(vdir(slug, "03_cues", "cues.md"), encoding="utf-8").read().splitlines()
    wd = json.load(open(vdir(slug, "02_transcript", "words.json")))
    words = wd["words"]
    toks = [norm(w["w"]) for w in words]
    cues, music, cur = [], None, None
    for ln in src:
        m = re.match(r"^music:\s*([\w\-]+)(?:\s+([\d.]+))?\s*$", ln.strip())
        if m:   # music: steady-hands 0.12 (a library bed) or music: rooms (the room loops); the level is optional
            music = {"id": m.group(1), "level": float(m.group(2) or 0.16)}
            continue
        m = CUE.match(ln.strip())
        if m:
            cid, quote, rest = m.groups()
            sfx = re.search(r"\[sfx:\s*([\w\-]+)\]", rest)
            shift = re.search(r"(?<![\w@])([+\-]\d+(?:\.\d+)?)", rest)
            pin = re.search(r"@(\d+(?:\.\d+)?)", rest)
            cur = {"id": cid, "level": cid.count("."), "quote": quote, "sfx": sfx.group(1) if sfx else None,
                   "shift": float(shift.group(1)) if shift else 0.0, "pin": float(pin.group(1)) if pin else None, "text": ""}
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
    duration = round(wd["end"] + 2.9, 3)   # 2.9 s tail: the end card (player.js, IMPROVE 000)
    for i, c in enumerate(cues):
        nxt = next((d for d in cues[i + 1:] if d["level"] <= c["level"]), None)
        c["end"] = nxt["t"] if nxt else duration
    doc = {"schema": "pnf.studio.cues.v1", "source": wd.get("source"), "music": music, "duration": duration, "cues": cues}
    json.dump(doc, open(vdir(slug, "03_cues", "cues.json"), "w"), indent=1)
    write_js(vdir(slug, "03_cues", "cues.js"), "CUES", doc)
    for c in cues:
        print(f"{'  ' * c['level']}{c['id']:<{22 - 2 * c['level']}} {c['t']:6.2f} {c['end']:6.2f}  {c['quote'][:40]}" + (f"  [sfx: {c['sfx']}]" if c["sfx"] else ""))
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
    times = [0.0, 0.5] + [min(c["t"] + 0.6, c["end"] - 0.05) for c in cues["cues"][1:]] + [cues["duration"] - 0.3]
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


def rooms_bed(cues, seconds, work):
    """The room loops laid end to end on one beat grid (every loop starts at 0 s, so all are in step), with a one-beat
    crossfade centred on each room change. The fade curve is the mean of equal-power and equal-gain: the rooms share some
    parts (bass notes, kicks) and not others, so either pure curve bumps or dips up to 3 dB at the join; the mean keeps
    it within about 1.5 dB."""
    import numpy as np
    from scipy.io import wavfile
    from scipy.signal import resample_poly
    n = int(round(seconds * SR)) + 1
    t = np.arange(n) / SR
    plan = room_plan(cues)
    bed = np.zeros(n)
    for i, (t0, r) in enumerate(plan):
        p = os.path.join(RUNTIME, "music", r + ".wav")
        if not os.path.exists(p):
            raise SystemExit(f"ERROR render: no music for room '{r}' (anim.py sound)")
        sr, x = wavfile.read(p)
        loop = resample_poly(x / 32768.0, SR, sr)
        t1 = plan[i + 1][0] if i + 1 < len(plan) else seconds + BEAT
        up = np.ones(n) if i == 0 else np.clip((t - (t0 - BEAT / 2)) / BEAT, 0, 1)
        down = np.clip(((t1 + BEAT / 2) - t) / BEAT, 0, 1)
        fade = lambda x: 0.5 * (np.sin(np.pi / 2 * x) + 0.5 - 0.5 * np.cos(np.pi * x))
        w = fade(up) * fade(down)
        k = w > 0
        bed[k] += w[k] * loop[np.arange(n)[k] % len(loop)]
    print("mix: rooms " + ", ".join(f"{r} {t0:.2f} s" for t0, r in plan))
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
        bed = rooms_bed(cues, seconds, work)
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
GATES = ("qa", "facts", "facts-captions", "render-critic", "buyer", "design", "golden")


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


def cmd_ready(slug):
    rev = vdir(slug, "05_render", "reviews")
    bad = []
    for g in GATES:
        f = vdir(slug, "05_render", "qa.json") if g == "qa" else os.path.join(rev, f"{g}.json")
        if not os.path.exists(f):
            bad.append(f"{g}: no file"); continue
        d = json.load(open(f))
        if not (d.get("pass") or d.get("override")):   # override: Todd's word in chat on a held gate, quoted with its time
            bad.append(f"{g}: FAIL")
    if not os.path.exists(vdir(slug, "05_render", "captions.json")):
        bad.append("captions.json: missing")
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
    q = load_queue()
    item = {"slug": slug, "readyAt": now(), "commit": head, "fingerprints": fingerprints(slug), "posts": {}}
    pos = next((n for n, i in enumerate(q["items"]) if i["slug"] == slug), None)
    if pos is None:
        q["items"].append(item)
    elif q["items"][pos]["posts"]:   # a lesson already live anywhere keeps its pin: every platform shows the same cut
        raise SystemExit(f"ERROR ready: {slug} is already posted on {', '.join(q['items'][pos]['posts'])}")
    else:   # a rebuild on the newest runtime (queue rule) keeps its place in line
        q["items"][pos] = item
    save_queue(q)
    print(f"ready: {slug} {'queued' if pos is None else 're-pinned at place ' + str(pos + 1)} ({len(q['items'])} in the queue)")


def cmd_waiting():
    print(json.dumps([i["slug"] for i in load_queue()["items"] if not i["posts"]]))


def cmd_next():
    for i in load_queue()["items"]:
        missing = [p for p in PLATFORMS if p not in i["posts"]]
        if missing:
            print(json.dumps({"slug": i["slug"], "missing": missing, "commit": i.get("commit")}))
            return
    print(json.dumps({"slug": None}))


def cmd_postcopy(slug):
    """Render the queued lesson from the commit its gates passed at, check every fingerprint, export the post copy
    to /mnt/user-data/outputs/<slug>.mp4 (the folder Chrome's upload reads)."""
    it = next((i for i in load_queue()["items"] if i["slug"] == slug), None)
    if not it or not it.get("commit"):
        raise SystemExit(f"ERROR postcopy: {slug} is not queued with a commit")
    wt = tempfile.mkdtemp(prefix="gated-")
    sh(["git", "-C", ROOT, "fetch", "--depth", "1", "origin", it["commit"]], check=False)
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
        os.makedirs("/mnt/user-data/outputs", exist_ok=True)
        dst = os.path.join("/mnt/user-data/outputs", f"{slug}.mp4")
        shutil.copy(src, dst)
        print(f"postcopy: {dst} ({os.path.getsize(dst) / 1e6:.1f} MB) from {it['commit'][:12]}")
    finally:
        sh(["git", "-C", ROOT, "worktree", "remove", "--force", wt], check=False)


def cmd_posted(slug, platform, url):
    if platform not in PLATFORMS:
        raise SystemExit(f"ERROR posted: platform must be one of {', '.join(PLATFORMS)}")
    q = load_queue()
    it = next((i for i in q["items"] if i["slug"] == slug), None)
    if not it:
        raise SystemExit(f"ERROR posted: {slug} is not in the queue")
    it["posts"][platform] = {"url": url, "at": now()}
    save_queue(q)
    print(f"posted: {slug} on {platform} ({len(it['posts'])} of 4)")


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


def captions_problems(slug):
    """_shared/captions.md in code: line 1 under 100 characters, a send line, the AI voice line, hashtag counts, no em or
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
        if "Narrated by an AI version of my own voice." not in text: out.append(f"{pl}: no AI voice line")
        n = len(re.findall(r"(?<!\w)#\w+", text))
        if not lo <= n <= hi: out.append(f"{pl}: {n} hashtags ({lo} to {hi})")
        if re.search(r"(?i)#(fyp|foryou|viral)\b", text): out.append(f"{pl}: banned hashtag")
        if re.search("[\u2013\u2014]", text): out.append(f"{pl}: an em or en dash")
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
    with the two lessons before it. Rules: no set piece from the previous lesson; at least 3 set pieces new against the
    two before; the four stock rooms on screen at most 40% of the runtime."""
    json.dump({"schema": "pnf.studio.worlds.v1", "share": share}, open(vdir(slug, "04_scene", "worlds.json"), "w"), indent=1)
    vids = sorted(d for d in os.listdir(VIDEOS) if re.match(r"\d{4}-\d\d-\d\d-", d))
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
    if seen and sets & seen[-1]:
        out.append(f"reuses the last lesson's set pieces: {', '.join(sorted(sets & seen[-1]))}")
    new = sets - set().union(*seen) if seen else sets
    if len(new) < 3:
        out.append(f"{len(new)} set piece(s) new against the two lessons before (at least 3)")
    return out


def cmd_lint(slug, step=0.25):
    """The layout check in code, before a reviewer has to find it: every settled scene text inside the safe area
    (x 20 to 950, y 262 to 1250), not under the host, the dialog box or other text. Problems that last under 0.5 s
    (slide-ins, slams) are ignored. Exit 1 on an ERROR."""
    cues = json.load(open(vdir(slug, "03_cues", "cues.json")))
    pw, b, pg = open_stage(slug)
    hits = {}
    def ov(p, q, pad=0):
        w = min(p["x1"], q["x1"]) - max(p["x0"], q["x0"]) + pad; h = min(p["y1"], q["y1"]) - max(p["y0"], q["y0"]) + pad
        return max(0, w) * max(0, h)
    pg.evaluate(WORLD_SPY)
    t, worlds, steps = 0.0, {}, 0
    while t < cues["duration"]:
        bx, used = pg.evaluate(f"(() => {{ window.__boxes = []; window.__used = {{}}; drawAt({t:.3f}); const r = window.__boxes; window.__boxes = null; return [r, Object.keys(window.__used)]; }})()")
        steps += 1
        for w in used:
            worlds[w] = worlds.get(w, 0) + 1
        texts = [x for x in bx if x["tag"] == "scene" and x["a"] > 0.6 and x["s"].strip()]
        host = [x for x in bx if x["tag"] == "host"]; dlg = [x for x in bx if x["tag"] == "dialogbox"]
        for x in texts:
            if x["x0"] < 20 or x["x1"] > 950 or x["y0"] < 262 or x["y1"] > 1250:
                hits.setdefault(("off the safe area", x["s"]), []).append(t)
            for o, name in [(h, "under the host") for h in host] + [(d, "under the dialog box") for d in dlg]:
                if ov(x, o) > 0.08 * (x["x1"] - x["x0"]) * (x["y1"] - x["y0"]):
                    hits.setdefault((name, x["s"]), []).append(t)
        for i, x in enumerate(texts):
            for y in texts[i + 1:]:
                if ov(x, y) > 0.15 * min((x["x1"] - x["x0"]) * (x["y1"] - x["y0"]), (y["x1"] - y["x0"]) * (y["y1"] - y["y0"])):
                    hits.setdefault(("text on text", x["s"] + " / " + y["s"]), []).append(t)
        t += step
    b.close(); pw.stop()
    errors = [f"ERROR lint captions: {x}" for x in captions_problems(slug)] if os.path.exists(vdir(slug, "05_render", "captions.json")) else []
    errors += [f"ERROR lint variety: {x}" for x in variety_problems(slug, {w: round(n / max(1, steps), 3) for w, n in worlds.items()})]
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
    print("\n".join(errors) if errors else f"lint: PASS 0 layout problems ({cues['duration']:.1f} s at {step} s steps)")
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
    end_card = max(c["t"] for c in cues["cues"] if c["level"] == 0)
    checks = []
    def c_len():
        secs = float(Q.probe(mp4)["format"]["duration"])
        return round(secs, 3), 45.0 <= secs <= 90.0, f"{secs:.2f} s (45.0 to 90.0, studio lessons)"
    for name, fn in [("length", c_len), ("loudness", lambda: Q.c_loudness(mp4)), ("black", lambda: Q.c_black(mp4)),
                     ("frozen", lambda: Q.c_frozen(mp4, end_card))]:
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
    ap.add_argument("--out"); ap.add_argument("--mp4"); ap.add_argument("--take", type=int, action="append"); ap.add_argument("--voice")
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
    elif c == "waiting":
        cmd_waiting()
    elif not a.slug:
        raise SystemExit(f"{c} needs a slug")
    elif c == "new":
        cmd_new(a.slug)
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
    elif c == "posted":
        cmd_posted(a.slug, a.rest[0] if len(a.rest) > 0 else "", a.rest[1] if len(a.rest) > 1 else "")
    elif c == "ready":
        cmd_ready(a.slug)
    elif c == "export":
        cmd_export(a.slug)
    elif c == "lint":
        cmd_lint(a.slug)
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
