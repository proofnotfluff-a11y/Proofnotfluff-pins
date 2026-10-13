#!/usr/bin/env python3
"""The promo videos' sound: picks a track from the music library, cuts it to the picture, adds the sound effects
and the sonic logo, ducks the music under the narration and masters the mix.

Used by make_demo.py (product demos) and make_slides.py (the slideshow Short). Nothing here needs fluidsynth or a
network: the tracks are pre-rendered in tools/music/tracks (see tools/music/compose.py: original compositions on an MIT-licensed
soundfont, no third-party recordings or melodies, so no rights holder can claim them).

Why it works this way (research Oct 13, 2026, notes in research_notes/Short video audio and edit best practice):
- One track on every video gives no recall benefit and reads as mass production on YouTube ("minimal variation
  across videos"); a short fixed sound at the end gives the brand recall instead. So the bed rotates (mood, then the
  track used longest ago) and the sonic logo is the constant.
- YouTube plays at -14 LUFS and never turns quiet videos up; the old mixes sat at -24. Masters land at -14 LUFS
  integrated, true peak under -1 dBTP.
- Music sits about 14 LU under the voice while it speaks (Torcoli et al., AES 2019: 10 LU minimum, general
  listeners want about 4 more) and comes up in the pauses, instead of one constant low level.

Command line, for checking a track:  python3 soundtrack.py --list | --pick [mood]
"""
import datetime, hashlib, json, math, os, subprocess, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MUSIC = os.path.join(HERE, "music")
LIBRARY = os.path.join(MUSIC, "library.json")
USED = os.path.join(MUSIC, "used")     # one small JSON file per rendered spec: no merge conflicts between runs
SR = 48000
MOODS = ["calm", "upbeat", "playful", "driving", "tension"]

TARGET_LUFS = -14.0       # the whole video, integrated (YouTube's playback reference)
CEILING_DBTP = -2.0       # limiter ceiling; AAC adds up to about 1 dB on long videos, the file stays under -1 dBTP
VOICE_LUFS = -15.0        # every narration line is set to this before the master
MUSIC_UNDER_LU = 14.0     # music this far under the voice while it speaks (the low end of the 14 to 18 LU band)
MUSIC_GAP_LU = 6.0        # and this far under it in the pauses
LOGO_UNDER_LU = 6.0       # the sonic logo, never ducked
XF = 0.03                 # crossfade at every music edit, seconds


# ---------------------------------------------------------------------------------------------- setup
def ensure():
    try:
        import scipy, soundfile  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "scipy", "soundfile"], check=True)


def decode(path, channels=2):
    """Any audio file to float32 at 48 kHz (ffmpeg decodes the Opus tracks natively at 48 kHz)."""
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-f", "f32le", "-ac", str(channels), "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32).copy()
    return x.reshape(-1, channels) if channels > 1 else x


# ------------------------------------------------------------------------------------------- metering
# ITU-R BS.1770-4 K-weighting at 48 kHz (the two standard biquads), 400 ms blocks, absolute and relative gates.
_K1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_K2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def lufs(x):
    from scipy.signal import lfilter
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 1:
        x = x[:, None]
    y = lfilter(_K2[0], _K2[1], lfilter(_K1[0], _K1[1], x, axis=0), axis=0)
    sq = (y ** 2).sum(axis=1)
    blk, hop = int(0.4 * SR), int(0.1 * SR)
    if len(sq) < blk:
        return -70.0
    c = np.concatenate([[0.0], np.cumsum(sq)])
    st = np.arange(0, len(sq) - blk + 1, hop)
    z = (c[st + blk] - c[st]) / blk
    lz = -0.691 + 10 * np.log10(z + 1e-20)
    z = z[lz > -70]
    if not len(z):
        return -70.0
    rel = -0.691 + 10 * np.log10(z.mean()) - 10
    z = z[-0.691 + 10 * np.log10(z) > rel]
    return float(-0.691 + 10 * np.log10(z.mean()))


def _tp_env(x):
    """Per-sample peak of the 4x oversampled signal (all channels), computed in 5 s chunks to keep memory low."""
    from scipy.signal import resample_poly
    x = np.asarray(x)
    two = x if x.ndim == 2 else x[:, None]
    n = len(two)
    out = np.zeros(n, dtype=np.float32)
    B, P = SR * 5, 64
    for ch in range(two.shape[1]):
        col = two[:, ch].astype(np.float32)
        for a in range(0, n, B):
            b = min(n, a + B)
            lo, hi = max(0, a - P), min(n, b + P)
            y = np.abs(resample_poly(col[lo:hi], 4, 1))[(a - lo) * 4:(a - lo) * 4 + (b - a) * 4]
            out[a:b] = np.maximum(out[a:b], y.reshape(-1, 4).max(axis=1))
    return out


def true_peak_db(x):
    return float(20 * np.log10(_tp_env(x).max() + 1e-12))


def limit(x, ceiling_db=CEILING_DBTP, release_ms=80):
    """Lookahead peak limiter (5 ms) with 4x oversampled detection, so the true peak stays under the ceiling."""
    from scipy.signal import lfilter
    from scipy.ndimage import maximum_filter1d, uniform_filter1d
    x = np.asarray(x, dtype=np.float64)
    ceil = 10 ** (ceiling_db / 20.0)
    w = 2 * int(SR * 0.005) + 1
    peak = maximum_filter1d(_tp_env(x), size=w)
    g = np.minimum(1.0, ceil / (peak.astype(np.float64) + 1e-12))
    g = uniform_filter1d(g, size=w)     # a 10 ms ramp into each reduction instead of a step; still full depth on the peak
    r = math.exp(-1.0 / (SR * release_ms / 1000.0))
    g = np.minimum(g, 1 - lfilter([1 - r], [1, -r], 1 - g))
    return x * (g[:, None] if x.ndim == 2 else g)


# -------------------------------------------------------------------------------------------- library
def library():
    return json.load(open(LIBRARY))["tracks"]


def used_log():
    """Every logged render, oldest first (the newest 60 count)."""
    out = []
    try:
        names = os.listdir(USED)
    except OSError:
        return out
    for n in names:
        if n.endswith(".json"):
            try:
                out.append(json.load(open(os.path.join(USED, n))))
            except (OSError, ValueError):
                pass
    out.sort(key=lambda u: u.get("at", ""))
    return out[-60:]


def pick(mood=None, want=None, key=""):
    """The track for one video. The spec's own "music" wins; a spec rendered before keeps its track (the CMO's
    review render and the promote run's render then match); otherwise the mood's track used longest ago,
    never-used first. Ties break on a hash of the spec name, so two videos rendered the same day differ even when
    the log was not committed."""
    tracks = library()
    by_id = {t["id"]: t for t in tracks}
    if want:
        if want in by_id:
            return by_id[want]
        raise SystemExit(f"music '{want}' is not in tools/music/library.json; ids: {', '.join(by_id)}")
    if mood and mood not in MOODS:
        raise SystemExit(f"mood '{mood}' unknown; use one of {MOODS}")
    log = used_log()
    for u in reversed(log):
        t = by_id.get(u.get("track"))
        if key and u.get("spec") == key and t and (not mood or mood in t["moods"]):
            return t
    pool = [t for t in tracks if not mood or mood in t["moods"]] or tracks
    last = {}
    for i, u in enumerate(log):
        if u.get("spec") != key:
            last[u.get("track")] = i
    return min(pool, key=lambda t: (last.get(t["id"], -1), hashlib.sha1((key + t["id"]).encode()).hexdigest()))


def record(track_id, video, mood=None, palette=None, spec=None):
    """Log the pick as tools/music/used/<spec>.json. Commit the folder with the run's other changes so the next
    video rotates from it; a re-render of the same spec rewrites its own file and touches nothing else."""
    import re
    key = re.sub(r"[^A-Za-z0-9._-]+", "-", spec or os.path.splitext(os.path.basename(video))[0])[:120]
    os.makedirs(USED, exist_ok=True)
    entry = {"at": datetime.datetime.now().isoformat(timespec="seconds"), "spec": spec or "",
             "video": os.path.basename(video), "track": track_id, "mood": mood or "", "palette": palette or ""}
    with open(os.path.join(USED, key + ".json"), "w") as f:
        json.dump(entry, f, indent=1)


def tonic_hz(track, octave=6):
    pcs = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
           "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
    pc = pcs[track["key"].split()[0]]
    return 440.0 * 2 ** ((12 * (octave + 1) + pc - 69) / 12.0)


# ------------------------------------------------------------------------------------- cut to picture
def runs(track, reveal, cta, total):
    """Video-time runs of track audio: (video_start, track_start, seconds). B's downbeat lands on `reveal`; A loops
    under everything before it (its last bar is the fill into B), B loops after it, and the ending starts at `cta`
    (make_demo passes the moment after the closing line, so the ending chord and the logo are heard in the clear)."""
    bar = track["bar_s"]
    sec = {s[0]: s for s in track["sections"]}
    a0, b0, nA, nB = sec["A"][1], sec["B"][1], sec["A"][2], sec["B"][2]
    out = []
    j = math.floor((0.0 - reveal) / bar)
    while reveal + j * bar < cta:
        v0 = reveal + j * bar
        tb = (b0 + j % nB) if j >= 0 else (a0 + j % nA)
        s0 = tb * bar
        start, ts = max(0.0, v0), s0 + max(0.0, -v0)
        end = min(cta, v0 + bar)
        if out and abs(out[-1][1] + out[-1][2] - ts) < 1e-6 and abs(out[-1][0] + out[-1][2] - start) < 1e-6:
            out[-1] = (out[-1][0], out[-1][1], out[-1][2] + end - start)
        else:
            out.append((start, ts, end - start))
        j += 1
    out.append((cta, track["out_s"], max(0.0, total - cta)))
    return [r for r in out if r[2] > 1e-4]


def bed(track, reveal, cta, total):
    src = decode(os.path.join(MUSIC, track["file"]))
    n = int(round(total * SR))
    y = np.zeros((n, 2), dtype=np.float64)
    xf = int(XF * SR)
    rs = runs(track, reveal, cta, total)
    for k, (v0, s0, length) in enumerate(rs):
        pre = xf if k > 0 else 0
        i0 = int(round(v0 * SR)) - pre
        j0 = int(round(s0 * SR)) - pre
        m = int(round((v0 + length) * SR)) - i0
        if k == len(rs) - 1:
            m = n - i0
        seg = np.zeros((m, 2))
        avail = src[max(0, j0):max(0, j0) + m]
        seg[:len(avail)] = avail
        w = np.ones(m)
        if pre:
            w[:pre] = np.sin(np.linspace(0, np.pi / 2, pre))
        if k < len(rs) - 1:
            w[-xf:] *= np.cos(np.linspace(0, np.pi / 2, xf))
        y[i0:i0 + m] += seg * w[:, None]
    fin = int(0.02 * SR)
    y[:fin] *= np.linspace(0, 1, fin)[:, None]
    fout = min(int(0.45 * SR), n)
    y[-fout:] *= np.linspace(1, 0, fout)[:, None] ** 1.5
    return y, rs


def biquad(kind, f0, gain_db, q):
    """RBJ cookbook peaking and low-shelf filters at SR."""
    A = 10 ** (gain_db / 40.0)
    w = 2 * math.pi * f0 / SR
    al, c = math.sin(w) / (2 * q), math.cos(w)
    if kind == "peak":
        b, a = [1 + al * A, -2 * c, 1 - al * A], [1 + al / A, -2 * c, 1 - al / A]
    else:
        sq = 2 * math.sqrt(A) * al
        b = [A * ((A + 1) - (A - 1) * c + sq), 2 * A * ((A - 1) - (A + 1) * c), A * ((A + 1) - (A - 1) * c - sq)]
        a = [(A + 1) + (A - 1) * c + sq, -2 * ((A - 1) + (A + 1) * c), (A + 1) + (A - 1) * c - sq]
    return np.array(b) / a[0], np.array(a) / a[0]


def voice_space(x):
    """A wide 2.5 dB dip around 2.5 kHz in the music, where the narration's consonants live."""
    from scipy.signal import lfilter
    b, a = biquad("peak", 2500.0, -2.5, 0.8)
    return lfilter(b, a, x, axis=0)


def duck(voice, under_db, gap_db, frame=0.01, look=0.1, hold=0.2, attack=0.05, release=0.25):
    """Gain in dB for every sample of the music: `under_db` while the voice speaks (from `look` before a word to
    `hold` after it), `gap_db` in the pauses, moving down fast and back up slowly."""
    hop = int(frame * SR)
    nf = int(math.ceil(len(voice) / hop))
    v = np.pad(voice, (0, nf * hop - len(voice))).reshape(nf, hop)
    level = 10 * np.log10((v ** 2).mean(axis=1) + 1e-12)
    active = np.flatnonzero(level > -48.0)
    on = np.zeros(nf, dtype=bool)
    ahead, behind = int(look / frame), int(hold / frame)
    for i in active:
        on[max(0, i - ahead):i + behind + 1] = True
    target = np.where(on, under_db, gap_db)
    a_att, a_rel = math.exp(-frame / attack), math.exp(-frame / release)
    g = np.empty(nf)
    cur = target[0]
    for k in range(nf):
        t = target[k]
        a = a_att if t < cur else a_rel
        cur = a * cur + (1 - a) * t
        g[k] = cur
    centers = (np.arange(nf) + 0.5) * hop
    return np.interp(np.arange(len(voice)), centers, g), on


# ------------------------------------------------------------------------------------------ narration
def clip(path):
    """A narration line, mono 48 kHz, trimmed to 30 ms either side of the speech and set to VOICE_LUFS."""
    x = decode(path, channels=1).astype(np.float64)
    hop = int(0.005 * SR)
    nf = len(x) // hop
    if nf:
        lv = 10 * np.log10((x[:nf * hop].reshape(nf, hop) ** 2).mean(axis=1) + 1e-12)
        loud = np.flatnonzero(lv > lv.max() - 45)
        if len(loud):
            a = max(0, loud[0] * hop - int(0.03 * SR))
            b = min(len(x), (loud[-1] + 1) * hop + int(0.03 * SR))
            x = x[a:b]
    from scipy.signal import butter, sosfilt, lfilter
    # voice EQ for phone speakers: rumble out, a little less boom under 180 Hz, a little more presence at 3.5 kHz
    x = sosfilt(butter(2, 90, "highpass", fs=SR, output="sos"), x)
    for kind, f0, gain, q in (("lowshelf", 180, -3.0, 0.7), ("peak", 3500, 2.5, 0.9)):
        b, a = biquad(kind, f0, gain, q)
        x = lfilter(b, a, x)
    level = lambda y: lufs(y) if len(y) > int(0.45 * SR) else 20 * np.log10(np.sqrt(np.mean(y ** 2)) + 1e-12)
    x = x * 10 ** ((VOICE_LUFS - level(x)) / 20.0)
    x = level_voice(x)
    x = x * 10 ** ((VOICE_LUFS - level(x)) / 20.0)
    r = int(0.004 * SR)
    x[:r] *= np.linspace(0, 1, r)
    x[-r:] *= np.linspace(1, 0, r)
    return x


def level_voice(x, over_db=4.0, ratio=3.0, knee_db=6.0, attack_ms=3.0, release_ms=60.0):
    """Voice compressor. The synthetic voice throws single syllables 12 to 20 dB over its average; without this the
    master limiter would have to flatten them to reach -14 LUFS. Works on a 5 ms RMS level, 3:1 above a point
    `over_db` over the line's loudness (VOICE_LUFS), with a soft knee."""
    from scipy.signal import lfilter
    win = int(0.005 * SR)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same") + 1e-12)
    lvl = 20 * np.log10(rms)
    thr = VOICE_LUFS + over_db
    d = lvl - thr
    red = np.where(d <= -knee_db / 2, 0.0,
                   np.where(d >= knee_db / 2, d * (1 - 1 / ratio), (1 - 1 / ratio) * (d + knee_db / 2) ** 2 / (2 * knee_db)))
    a = math.exp(-1.0 / (SR * attack_ms / 1000.0))
    r = math.exp(-1.0 / (SR * release_ms / 1000.0))
    # gain reduction follows fast when it rises and slowly when it falls (attack and release on the reduction)
    g = np.empty_like(red)
    cur = 0.0
    for i0 in range(0, len(red), 256):          # block-wise one-pole with the coefficient chosen per block
        blk = red[i0:i0 + 256]
        coef = a if blk.max() > cur else r
        out = lfilter([1 - coef], [1, -coef], blk, zi=[cur * coef])[0]
        g[i0:i0 + 256] = np.maximum(out, blk if coef == a else out)
        cur = g[i0 + len(blk) - 1]
    return x * 10 ** (-g / 20.0)


def prepare(path):
    """Trim and level a freshly synthesized line in place; returns its new length in seconds."""
    import soundfile as sf
    x = clip(path)
    sf.write(path, x.astype(np.float32), SR, subtype="FLOAT")
    return len(x) / SR


# ---------------------------------------------------------------------------------------- sound effects
def _bp(x, lo, hi):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def sfx_tick(rng):
    """One keystroke: a short high click on a soft low thock."""
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    click = _bp(rng.normal(0, 1, n), 2200, 7500) * np.exp(-t / 0.0022)
    thock = np.sin(2 * np.pi * rng.uniform(170, 230) * t) * np.exp(-t / 0.012) * (1 - np.exp(-t / 0.0008))
    y = click / (np.abs(click).max() + 1e-9) + 0.45 * thock
    return y / np.abs(y).max() * rng.uniform(0.75, 1.0)


def sfx_pop():
    """The reveal: a quick falling pop with a little air."""
    n = int(0.16 * SR)
    t = np.arange(n) / SR
    f = 360 + 950 * np.exp(-t / 0.014)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.035) * (1 - np.exp(-t / 0.0012))
    air = _bp(np.random.default_rng(7).normal(0, 1, n), 3000, 9000) * np.exp(-t / 0.012) * 0.25
    y = body + air
    return y / np.abs(y).max()


def sfx_chime(f0):
    """The fix: tonic then fifth on a soft bell, in the track's key."""
    n = int(1.1 * SR)
    t = np.arange(n) / SR
    y = np.zeros(n)
    for delay, f, amp in ((0.0, f0, 1.0), (0.075, f0 * 1.5, 0.8)):
        tt = np.clip(t - delay, 0, None)
        on = t >= delay
        env = np.exp(-tt / 0.32) * (1 - np.exp(-tt / 0.002)) * on
        y += amp * env * (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.12)
                          + 0.12 * np.sin(2 * np.pi * 3.01 * f * tt) * np.exp(-tt / 0.06))
    return y / np.abs(y).max()


def sfx_whoosh(seconds=0.45):
    """Into the end card: noise that climbs through three bands and stops on the cut."""
    n = int(seconds * SR)
    t = np.linspace(0, 1, n)
    rng = np.random.default_rng(11)
    y = np.zeros((n, 2))
    for (lo, hi), at in (((250, 900), 0.45), ((900, 2600), 0.75), ((2600, 7000), 0.95)):
        env = np.exp(-((t - at) / 0.22) ** 2)
        for ch in range(2):
            y[:, ch] += _bp(rng.normal(0, 1, n), lo, hi) * env
    y *= (t ** 1.6)[:, None] * np.minimum(1, (1 - t) / 0.08)[:, None]
    pan = np.stack([1 - 0.35 * t, 0.65 + 0.35 * t], axis=1)
    y *= pan
    return y / np.abs(y).max()


SFX_PEAK = {"tick": 0.035, "pop": 0.17, "chime": 0.11, "whoosh": 0.07}


def sfx_bus(events, n, track):
    """events: (kind, time) with kind tick, pop, chime or whoosh (time = the moment it lands on)."""
    rng = np.random.default_rng(5)
    y = np.zeros((n, 2))
    pop = sfx_pop()
    chime = sfx_chime(tonic_hz(track, 6)) if track else sfx_chime(1046.5)
    whoosh = sfx_whoosh()
    for kind, at in events:
        if kind == "tick":
            s = sfx_tick(rng)
            p = rng.uniform(-0.25, 0.25)
            s = np.stack([s * (1 - p), s * (1 + p)], axis=1) / 1.25
            i = int(at * SR)
        elif kind == "pop":
            s = np.stack([pop, pop], axis=1)
            i = int(at * SR)
        elif kind == "chime":
            s = np.stack([chime * 0.92, chime], axis=1)
            i = int(at * SR)
        elif kind == "whoosh":
            s = whoosh
            i = int(at * SR) - len(s)
        else:
            continue
        s = s * SFX_PEAK[kind]
        a, b = max(0, i), min(n, i + len(s))
        if b > a:
            y[a:b] += s[a - i:b - i]
    return y


# ------------------------------------------------------------------------------------------------ mix
def mix(track, total, reveal, cta, out_wav, voice=(), sfx=(), logo=True, button=None):
    """Write the finished soundtrack. voice: (start, wav) lines already passed through prepare(); sfx: (kind, time).
    `button` is where the music's ending and the sonic logo land (default: `cta`, the end card). With no voice the
    music is the soundtrack and goes straight to the master level. Returns measurements."""
    ensure()
    import soundfile as sf
    n = int(round(total * SR))
    button = cta if button is None else button
    music, rs = bed(track, reveal, button, total)
    v = np.zeros(n)
    for start, path in voice:
        x = decode(path, channels=1).astype(np.float64)
        i = int(round(max(0.0, start) * SR))
        j = min(n, i + len(x))
        if j > i:
            v[i:j] += x[:j - i]
    out = {"track": track["id"], "edits": len(rs)}
    if voice:
        music = voice_space(music)
        ml = lufs(music)
        g, on = duck(v, VOICE_LUFS - MUSIC_UNDER_LU - ml, VOICE_LUFS - MUSIC_GAP_LU - ml)
        music = music * (10 ** (g / 20.0))[:, None]
        talk = np.repeat(on, int(0.01 * SR))[:n]
        if talk.sum() > SR and (~talk).sum() > SR // 2:
            out["music_under_voice_lu"] = round(lufs(v[talk]) - lufs(music[talk]), 1)
    else:
        music = music * 10 ** ((VOICE_LUFS - lufs(music)) / 20.0)
    fx = sfx_bus(sfx, n, track)
    if logo and track.get("logo"):
        lg = decode(os.path.join(MUSIC, track["logo"]))
        lg = lg * 10 ** ((VOICE_LUFS - LOGO_UNDER_LU - lufs(lg)) / 20.0)
        i = int(round(button * SR))
        j = min(n, i + len(lg))
        if j > i:
            fx[i:j] += lg[:j - i]
    y = music + v[:, None] + fx
    gain = TARGET_LUFS - lufs(y)
    for _ in range(3):        # the limiter takes a little loudness off; aim again until the master lands on target
        z = limit(y * 10 ** (gain / 20.0), CEILING_DBTP)
        miss = TARGET_LUFS - lufs(z)
        if abs(miss) < 0.1:
            break
        gain += miss
    y = z
    sf.write(out_wav, y.astype(np.float32), SR, subtype="FLOAT")
    out.update({"lufs": round(lufs(y), 1), "true_peak_dbtp": round(true_peak_db(y), 1)})
    return out


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--list":
        for t in library():
            print(f"{t['id']:20s} {t['bpm']:4d} bpm  {t['key']:9s} {', '.join(t['moods'])}")
    elif a[0] == "--pick":
        print(json.dumps(pick(a[1] if len(a) > 1 else None, key="cli")["id"]))
