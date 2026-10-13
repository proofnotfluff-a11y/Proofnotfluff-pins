#!/usr/bin/env python3
"""ProofNotFluff music library: the original background tracks the promo videos use.

Every track is composed here in code (chord progressions, grooves, bass lines, motifs) and rendered with the
FluidR3 GM soundfont (MIT licence). No samples or melodies come from anyone's recordings, so there is no rights
holder who could claim a track on any platform, and the shop's $0 tool budget holds.

Run it offline where fluidsynth and the soundfont are installed (the scheduled runs never need them; they only
read the rendered files):
    apt-get install -y fluidsynth fluid-soundfont-gm && pip install mido pyloudnorm scipy
    python3 tools/music/compose.py              # every track
    python3 tools/music/compose.py ledger-lofi  # one track

Writes tools/music/tracks/<id>.opus (80 kbps), tools/music/tracks/<id>_logo.opus (the sonic logo in that
track's key) and tools/music/library.json.

Shape of every track: a 2-bar intro already at full groove (no fade-in, so second zero has energy), A (8 bars,
a drum fill on its last bar), B (8 bars, the lift: a motif, busier drums, a crash on its first beat, 2 dB up),
then a 2-bar ending on the home chord. library.json records the tempo, the bar length and the sections, so
tools/soundtrack.py can cut the track to the picture: A loops under the setup, B lands on the result reveal,
and the ending lands on the end card with the sonic logo.
"""
import json, math, os, subprocess, sys, tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TRACKS_DIR = os.path.join(HERE, "tracks")
LIBRARY = os.path.join(HERE, "library.json")
SF2 = os.environ.get("PNF_SF2", "/usr/share/sounds/sf2/FluidR3_GM.sf2")
SR = 44100
TPB = 480                # MIDI ticks per beat
STEP = TPB // 4          # one 16th note
LIBRARY_LUFS = -16.0     # every file sits at the same loudness; the video mix sets the final level
LOGO_LUFS = -18.0        # the sonic logo files
LIFT_DB = 2.0            # B sections and the ending sit this much above A
CEILING_DB = -2.0        # true-peak ceiling before encoding (Opus adds a little overshoot)
OPUS_KBPS = "80k"

PC = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7,
      "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}
Q = {"maj": [0, 4, 7], "min": [0, 3, 7], "dim": [0, 3, 6], "sus2": [0, 2, 7], "sus4": [0, 5, 7],
     "7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "m7": [0, 3, 7, 10], "m7b5": [0, 3, 6, 10], "6": [0, 4, 7, 9],
     "m6": [0, 3, 7, 9], "add9": [0, 4, 7, 14], "madd9": [0, 3, 7, 14], "9": [0, 4, 7, 10, 14],
     "maj9": [0, 4, 7, 11, 14], "m9": [0, 3, 7, 10, 14], "7sus4": [0, 5, 7, 10]}
MAJOR, MINOR = [0, 2, 4, 5, 7, 9, 11], [0, 2, 3, 5, 7, 8, 10]

# General MIDI drum notes
KICK, STICK, SNARE, CLAP, CHAT, PHAT, OHAT, LTOM, MTOM, HTOM, CRASH, RIDE, TAMB, SHAKE, CLAVE, BLOCK = (
    36, 37, 38, 39, 42, 44, 46, 45, 47, 50, 49, 51, 54, 70, 75, 76)


# ----------------------------------------------------------------------------------------------- harmony
def bass_note(pc, lo=33):
    return lo + ((pc - lo) % 12)


def voicing(chord, lo=55, hi=72, rootless=False):
    pc, ivs = chord
    tones = [(pc + i) % 12 for i in ivs]
    if rootless and len(tones) >= 4:
        tones = tones[1:]
    best, best_d = None, 1e9
    for r in range(len(tones)):
        order = tones[r:] + tones[:r]
        notes, base = [], lo
        for t in order:
            n = base + ((t - base) % 12)
            notes.append(n)
            base = n + 1
        d = abs((notes[0] + notes[-1]) / 2 - (lo + hi) / 2) + max(0, notes[-1] - hi) * 3
        if d < best_d:
            best, best_d = notes, d
    return best


class Ctx:
    """What a part generator sees for one bar."""

    def __init__(self, track, sec, bar, nbars, chord, nxt, rng):
        self.t, self.sec, self.bar, self.nbars, self.chord, self.nxt, self.rng = track, sec, bar, nbars, chord, nxt, rng
        self.root = chord[0]
        self.lift = sec == "B"
        self.fill = sec in ("A", "intro") and bar == nbars - 1 and track.get("_next") == "B"

    def vel(self, base, spread=6):
        return int(max(1, min(127, base + self.rng.integers(-spread, spread + 1))))


# ------------------------------------------------------------------------------------- melodic parts
def p_rhodes(c, a):
    v = voicing(c.chord, a.get("lo", 55), a.get("hi", 72), rootless=True)
    hits = [(0, 7), (10, 6)] if not c.lift else [(0, 5), (6, 3), (10, 5), (14, 2)]
    out = []
    for st, du in hits:
        base = c.vel(a.get("v", 64))
        for k, n in enumerate(v):
            out.append((st + k * 0.07, n, base - 2 * k, du))
    return out


def p_stabs(c, a):
    v = voicing(c.chord, a.get("lo", 58), a.get("hi", 75), rootless=a.get("rootless", False))
    steps = a.get("steps", (2, 6, 10, 14))
    if c.lift:
        steps = a.get("lift_steps", steps)
    return [(s, n, c.vel(a.get("v", 74) + (6 if s % 4 == 2 else 0)), a.get("dur", 1.2)) for s in steps for n in v]


def p_arp(c, a):
    lo = a.get("lo", 60)
    v = voicing(c.chord, lo, lo + 12)
    tones = v + [n + 12 for n in v]
    seq = tones + tones[-2:0:-1] if a.get("shape", "updown") == "updown" else tones
    rate = a.get("rate", 1) if c.lift or not a.get("slow_a") else 2
    out = []
    for i, s in enumerate(range(0, 16, rate)):
        out.append((s, seq[i % len(seq)], c.vel(a.get("v", 58) + (8 if s % 4 == 0 else 0)), rate * a.get("gate", 0.9)))
    return out


def p_pluck(c, a):
    v = voicing(c.chord, a.get("lo", 55), a.get("hi", 71))
    b = bass_note(c.root, 40)
    pat = [(0, b), (2, v[1 % len(v)]), (4, v[2 % len(v)]), (6, v[1 % len(v)]), (8, b + 7 if b + 7 < v[0] else b),
           (10, v[2 % len(v)]), (12, v[-1]), (14, v[1 % len(v)])]
    if c.lift:
        pat += [(3, v[-1]), (11, v[0])]
    return [(s, n, c.vel(a.get("v", 64) + (6 if s % 4 == 0 else -4)), 3.5) for s, n in pat]


def p_strum(c, a):
    v = voicing(c.chord, a.get("lo", 52), a.get("hi", 71))
    out = []
    steps = range(0, 16, 2) if c.lift or not a.get("half_a") else (0, 6, 8, 14)
    for s in steps:
        down = s % 4 == 0
        acc = 80 if s in (0, 8) else (66 if down else 54)
        for k, n in enumerate(v if down else v[::-1]):
            out.append((s + k * 0.06, n, c.vel(a.get("v", 0) + acc), 1.7))
    return out


def p_piano(c, a):
    v = voicing(c.chord, a.get("lo", 55), a.get("hi", 74))
    base = a.get("v", 62)
    if not c.lift and not a.get("busy"):
        return [(s, n, c.vel(base - (6 if s else 0)), 7.5) for s in (0, 8) for n in v]
    low = bass_note(c.root, 43)
    pat = [(0, [low] + v), (3, [v[-1]]), (6, v[:2]), (8, [low + 7 if low + 7 < v[0] else low] + v), (11, [v[-1]]), (14, v[1:])]
    return [(s, n, c.vel(base + (6 if s in (0, 8) else -6)), 2.6) for s, ns in pat for n in ns]


def p_pad(c, a):
    v = voicing(c.chord, a.get("lo", 55), a.get("hi", 74), rootless=a.get("rootless", False))
    return [(0, n, c.vel(a.get("v", 52), 3), 15.8) for n in v]


def p_pizz(c, a):
    v = voicing(c.chord, a.get("lo", 55), a.get("hi", 72))
    order = [0, 2, 1, 2] if len(v) >= 3 else [0, 1, 0, 1]
    steps = range(0, 16, 2) if not c.lift else range(0, 16, 1)
    out = []
    for i, s in enumerate(steps):
        n = v[order[i % 4] % len(v)] + (12 if c.lift and i % 8 == 7 else 0)
        out.append((s, n, c.vel(a.get("v", 66) + (8 if s % 4 == 0 else 0)), 0.8))
    return out


def p_stacc(c, a):
    v = voicing(c.chord, a.get("lo", 50), a.get("hi", 67))
    steps = range(0, 16, 2) if not c.lift else range(0, 16, 1)
    return [(s, n, c.vel(a.get("v", 62) + (10 if s % 4 == 0 else 0)), 0.9 if not c.lift else 0.6) for s in steps for n in v]


def p_motif(c, a):
    """A short figure on chord tones, the same shape every bar so it reads as a hook; only in the lift."""
    if not c.lift and not a.get("always"):
        return []
    lo = a.get("lo", 72)
    v = voicing(c.chord, lo, lo + 12)
    tones = v + [v[0] + 12]
    rhythm = a.get("rhythm", (0, 3, 6, 10, 12))
    shape = a.get("shape", (2, 1, 0, 1, 3))
    if c.bar % 2 == 1:
        shape = shape[::-1]
    return [(s, tones[shape[i % len(shape)] % len(tones)], c.vel(a.get("v", 66) - (0 if i == 0 else 4)), a.get("dur", 2.5))
            for i, s in enumerate(rhythm)]


def p_bells(c, a):
    if not c.lift and not a.get("always"):
        return []
    v = voicing(c.chord, a.get("lo", 76), a.get("lo", 76) + 12)
    return [(0, v[-1], c.vel(a.get("v", 58)), 6), (10, v[0], c.vel(a.get("v", 58) - 8), 6)]


# --------------------------------------------------------------------------------------------- bass
def approach(c):
    target = bass_note(c.nxt[0])
    return target - 1 if c.rng.random() < 0.6 else target + 2


def b_root8(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    return [(s, r + (12 if c.lift and s % 4 == 2 else 0), c.vel(86 if s % 4 == 0 else 72), 1.6) for s in range(0, 16, 2)]


def b_rootfifth(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    out = [(0, r, c.vel(92), 5.5), (8, r + 7, c.vel(80), 3.5)]
    if c.lift:
        out += [(6, r, c.vel(66), 1.5), (11, r + 7, c.vel(64), 1.5)]
    out.append((14, approach(c), c.vel(70), 1.8))
    return out


def b_walk(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    third = r + (3 if 3 in [(i % 12) for i in (np.array(c.chord[1]))] else 4)
    return [(0, r, c.vel(88), 3.6), (4, third, c.vel(74), 3.6), (8, r + 7, c.vel(80), 3.6), (12, approach(c), c.vel(72), 3.6)]


def b_sync(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    pat = [(0, r, 96, 2.5), (3, r, 70, 1.0), (6, r + 12, 82, 1.4), (10, r, 90, 1.8), (13, r + 7, 72, 1.0)]
    if c.lift:
        pat += [(8, r + 10, 60, 0.8), (15, r + 12, 66, 0.8)]
    return [(s, n, c.vel(v), d) for s, n, v, d in pat]


def b_offbeat(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    out = [(s, r, c.vel(90), 1.5) for s in (2, 6, 10, 14)]
    if c.lift:
        out += [(0, r + 12, c.vel(60), 0.8), (8, r + 12, c.vel(60), 0.8)]
    return out


def b_sub(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    out = [(0, r, c.vel(104), 9.5), (10, r, c.vel(84), 2.0), (13, r, c.vel(76), 2.5)]
    return out


def b_pedal(c, a):
    r = bass_note(c.root, a.get("lo", 33))
    return [(0, r, c.vel(84), 15.5)] if not c.lift else [(0, r, c.vel(90), 7.5), (8, r, c.vel(84), 7.5)]


# -------------------------------------------------------------------------------------------- drums
def d_boombap(c, a):
    out = [(0, KICK, c.vel(104), 1), (10, KICK, c.vel(96), 1), (4, SNARE, c.vel(96), 1), (12, SNARE, c.vel(98), 1)]
    if c.bar % 2 == 1:
        out.append((7, KICK, c.vel(80), 1))
    if c.rng.random() < 0.5:
        out.append((15, SNARE, c.vel(32), 1))
    hats = range(0, 16, 2) if not c.lift else range(0, 16, 1)
    out += [(s, CHAT, c.vel(68 if s % 4 == 0 else (52 if s % 2 == 0 else 34)), 1) for s in hats]
    if c.lift and c.bar % 2 == 1:
        out.append((14, OHAT, c.vel(60), 2))
    return out


def d_four(c, a):
    out = [(s, KICK, c.vel(112, 3), 1) for s in (0, 4, 8, 12)]
    if c.lift or c.bar >= 2:
        out += [(4, CLAP, c.vel(96), 1), (12, CLAP, c.vel(98), 1)]
    out += [(s, CHAT, c.vel(46 if s % 2 else 58), 1) for s in range(16) if s % 4 != 2]
    if c.lift:
        out += [(s, OHAT, c.vel(74), 2) for s in (2, 6, 10, 14)]
    return out


def d_pop(c, a):
    out = [(0, KICK, c.vel(108), 1), (8, KICK, c.vel(100), 1), (4, SNARE, c.vel(100), 1), (12, SNARE, c.vel(102), 1)]
    out.append((10 if c.bar % 2 else 6, KICK, c.vel(84), 1))
    out += [(s, CHAT, c.vel(62 if s % 4 == 0 else 48), 1) for s in range(0, 16, 2)]
    if c.lift:
        out += [(s, TAMB, c.vel(50 if s % 2 else 64), 1) for s in range(0, 16, 1) if s % 4 != 0]
    return out


def d_halftime(c, a):
    out = [(0, KICK, c.vel(110), 1), (7 if c.bar % 2 else 6, KICK, c.vel(92), 1), (11, KICK, c.vel(88), 1),
           (8, CLAP, c.vel(104), 1), (8, SNARE, c.vel(80), 1)]
    hats = range(0, 16, 2) if not c.lift else range(0, 16, 1)
    out += [(s, CHAT, c.vel(64 if s % 4 == 0 else 46), 1) for s in hats]
    if c.lift and c.bar % 2 == 1:
        out += [(14 + k * 0.33, CHAT, c.vel(40 + 8 * k), 0.3) for k in range(6)]
    return out


def d_funk(c, a):
    out = [(0, KICK, c.vel(106), 1), (3, KICK, c.vel(78), 1), (10, KICK, c.vel(98), 1),
           (4, SNARE, c.vel(100), 1), (12, SNARE, c.vel(102), 1), (7, SNARE, c.vel(30), 1), (9, SNARE, c.vel(28), 1)]
    out += [(s, CHAT, c.vel(70 if s % 4 == 0 else (56 if s % 2 == 0 else 38)), 1) for s in range(16)]
    if c.lift:
        out += [(14, OHAT, c.vel(66), 2), (6, KICK, c.vel(70), 1)]
    return out


def d_brush(c, a):
    out = [(0, RIDE, c.vel(66), 1), (4, RIDE, c.vel(60), 1), (6, RIDE, c.vel(46), 1), (8, RIDE, c.vel(64), 1),
           (12, RIDE, c.vel(60), 1), (14, RIDE, c.vel(46), 1), (4, PHAT, c.vel(50), 1), (12, PHAT, c.vel(52), 1),
           (0, KICK, c.vel(56), 1), (4, SNARE, c.vel(48), 1), (12, SNARE, c.vel(52), 1)]
    if c.lift:
        out += [(10, KICK, c.vel(50), 1), (15, SNARE, c.vel(34), 1)]
    return out


def d_light(c, a):
    out = [(0, KICK, c.vel(96), 1), (8, KICK, c.vel(88), 1), (4, STICK, c.vel(78), 1), (12, STICK, c.vel(80), 1)]
    out += [(s, SHAKE, c.vel(50 if s % 2 else 62), 1) for s in range(16)]
    if c.lift:
        out += [(10, KICK, c.vel(80), 1), (4, TAMB, c.vel(66), 1), (12, TAMB, c.vel(68), 1)]
    return out


def d_cinema(c, a):
    if not c.lift:
        return [(0, LTOM, c.vel(92), 2), (10, LTOM, c.vel(80), 2), (14, MTOM, c.vel(60), 1)]
    out = [(s, LTOM if s % 4 == 0 else MTOM, c.vel(86 if s % 4 == 0 else 64), 1) for s in range(0, 16, 2)]
    out += [(0, KICK, c.vel(104), 1), (8, KICK, c.vel(96), 1), (12, SNARE, c.vel(92), 1)]
    return out


def d_pulse(c, a):
    out = [(s, BLOCK, c.vel(52 if s % 4 else 70), 1) for s in range(16)]
    out += [(0, KICK, c.vel(84), 1), (8, KICK, c.vel(78), 1)]
    if c.lift:
        out += [(s, KICK, c.vel(100), 1) for s in (4, 12)] + [(s, CHAT, c.vel(54), 1) for s in range(2, 16, 4)]
        if c.bar % 2 == 1:
            out.append((12, CLAP, c.vel(96), 1))
    return out


DRUMS = {"boombap": d_boombap, "four": d_four, "pop": d_pop, "halftime": d_halftime, "funk": d_funk,
         "brush": d_brush, "light": d_light, "cinema": d_cinema, "pulse": d_pulse}
PARTS = {"rhodes": p_rhodes, "stabs": p_stabs, "arp": p_arp, "pluck": p_pluck, "strum": p_strum, "piano": p_piano,
         "pad": p_pad, "pizz": p_pizz, "stacc": p_stacc, "motif": p_motif, "bells": p_bells,
         "root8": b_root8, "rootfifth": b_rootfifth, "walk": b_walk, "sync": b_sync, "offbeat": b_offbeat,
         "sub": b_sub, "pedal": b_pedal}


def drum_fill(c, kind):
    if kind in ("cinema",):
        return [(12, LTOM, c.vel(80), 1), (13, MTOM, c.vel(86), 1), (14, MTOM, c.vel(92), 1), (15, HTOM, c.vel(100), 1)]
    if kind in ("brush",):
        return [(14, SNARE, c.vel(50), 1), (15, SNARE, c.vel(58), 1)]
    return [(12 + k * 0.5, SNARE, c.vel(56 + 10 * k), 0.5) for k in range(8)]


# ------------------------------------------------------------------------------------------- tracks
def C(sym):
    """'Gm7' -> (pitch class, intervals); quality names follow Q (m = minor triad)."""
    root = sym[:2] if len(sym) > 1 and sym[1] in "#b" else sym[:1]
    q = sym[len(root):] or "maj"
    q = {"m": "min"}.get(q, q)
    return (PC[root], Q[q])


def prog(s):
    return [C(x) for x in s.split()]


TRACKS = [
    dict(id="ledger-lofi", title="Ledger", moods=["calm"], bpm=82, key="F", swing=0.6, kit=0, drums="boombap",
         A=prog("Gm9 C9 Fmaj9 Dm7"), B=prog("Bbmaj7 Am7 Gm7 C7sus4"), tonic="Fmaj9", lofi=True,
         parts=[("rhodes", 4, dict(v=66), 96, 52, 60), ("rootfifth", 33, {}, 100, 64, 10),
                ("motif", 11, dict(lo=74, rhythm=(0, 3, 6, 11), v=62), 84, 76, 56)]),
    dict(id="brass-tacks", title="Brass Tacks", moods=["playful", "driving"], bpm=104, key="E", minor=True, kit=0, drums="funk",
         A=prog("Em7 A7 Em7 A7"), B=prog("Cmaj7 B7 Em7 A7"), tonic="Em9",
         parts=[("stabs", 7, dict(steps=(2, 5, 10, 13), lift_steps=(2, 5, 7, 10, 13, 15), dur=0.9, v=70), 92, 48, 24),
                ("sync", 36, {}, 104, 64, 8), ("motif", 61, dict(lo=67, rhythm=(0, 6, 10), dur=1.4, v=70), 78, 82, 36)]),
    dict(id="night-shift", title="Night Shift", moods=["driving"], bpm=122, key="A", minor=True, kit=24, drums="four",
         pump=7, A=prog("Am9 Fmaj7 Cmaj7 G6"), B=prog("Fmaj7 G6 Am9 Em7"), tonic="Am9",
         parts=[("stabs", 90, dict(steps=(2, 6, 10, 14), lift_steps=(2, 6, 9, 10, 14), dur=1.1, v=72, rootless=True), 88, 56, 40),
                ("offbeat", 38, dict(lo=33), 100, 64, 6), ("pad", 89, dict(v=46), 70, 64, 70),
                ("arp", 81, dict(lo=69, rate=2, v=48, gate=0.5), 66, 84, 50)]),
    dict(id="fine-print", title="Fine Print", moods=["tension"], bpm=96, key="D", minor=True, kit=0, drums="pulse",
         A=prog("Dm Bb Gm A7"), B=prog("Dm Bb C A7"), tonic="Dm",
         parts=[("pizz", 45, dict(v=70), 92, 44, 40), ("pad", 49, dict(lo=50, v=56), 82, 80, 64),
                ("pedal", 32, dict(lo=31), 96, 64, 20), ("stacc", 48, dict(lo=55, v=58), 74, 72, 50)]),
    dict(id="clean-books", title="Clean Books", moods=["upbeat", "playful"], bpm=100, key="G", kit=8, drums="light",
         A=prog("G D Em C"), B=prog("C D Em G"), tonic="Gadd9",
         parts=[("pluck", 25, dict(v=66), 96, 48, 40), ("rootfifth", 32, dict(lo=31), 96, 64, 14),
                ("piano", 0, dict(v=56, lo=60, hi=79), 70, 80, 44), ("motif", 73, dict(lo=74, rhythm=(0, 4, 8, 12), v=58), 66, 84, 50)]),
    dict(id="margin-call", title="Margin Call", moods=["tension", "driving"], bpm=100, key="B", minor=True, kit=24, drums="pop",
         A=prog("Bm G D A"), B=prog("G A Bm D"), tonic="Bm",
         parts=[("arp", 81, dict(lo=62, rate=1, v=46, gate=0.6, slow_a=True), 72, 40, 56), ("root8", 39, dict(lo=35), 98, 64, 8),
                ("pad", 90, dict(v=50), 74, 88, 66), ("motif", 62, dict(lo=71, rhythm=(0, 6, 8, 14), dur=1.6, v=62), 70, 64, 50)]),
    dict(id="steady-hands", title="Steady Hands", moods=["calm"], bpm=88, key="C", kit=8, drums="light",
         A=prog("Am7 Fmaj7 C G6"), B=prog("Fmaj7 G Em7 Am7"), tonic="Cmaj7",
         parts=[("piano", 0, dict(v=60, busy=False), 96, 56, 50), ("pad", 89, dict(v=46, lo=52), 70, 72, 70),
                ("pedal", 32, dict(lo=31), 88, 64, 20), ("bells", 11, dict(lo=76, v=52), 66, 84, 60)]),
    dict(id="pocket-change", title="Pocket Change", moods=["playful", "upbeat"], bpm=112, key="C", kit=0, drums="pop",
         A=prog("C Am F G"), B=prog("F G Em Am"), tonic="C6",
         parts=[("arp", 12, dict(lo=64, rate=2, v=66, gate=0.8), 92, 44, 30), ("pizz", 45, dict(lo=60, v=56), 74, 84, 34),
                ("rootfifth", 33, {}, 98, 64, 8), ("motif", 12, dict(lo=76, rhythm=(0, 2, 6, 10, 12), v=60, dur=1.5), 74, 70, 30)]),
    dict(id="breakeven", title="Breakeven", moods=["tension"], bpm=92, key="E", minor=True, kit=16, drums="cinema",
         A=prog("Em C G D"), B=prog("C G D Em"), tonic="Em",
         parts=[("stacc", 48, dict(lo=47, v=64), 92, 56, 56), ("piano", 0, dict(v=58, lo=60, hi=79), 80, 76, 50),
                ("pedal", 32, dict(lo=28), 92, 64, 24), ("pad", 52, dict(v=44, lo=60), 70, 64, 80)]),
    dict(id="side-hustle", title="Side Hustle", moods=["upbeat"], bpm=118, key="D", kit=16, drums="pop",
         A=prog("D A Bm G"), B=prog("G A Bm D"), tonic="D",
         parts=[("strum", 27, dict(v=-6, half_a=True), 88, 44, 40), ("pad", 16, dict(v=48), 70, 84, 40),
                ("root8", 34, dict(lo=33), 98, 64, 10), ("motif", 27, dict(lo=69, rhythm=(0, 3, 6, 8, 12), v=60, dur=1.5), 74, 76, 44)]),
    dict(id="quiet-math", title="Quiet Math", moods=["calm"], bpm=84, key="E", kit=0, drums="light",
         A=prog("Emaj7 C#m7 Amaj7 B6"), B=prog("Amaj7 B6 G#m7 C#m7"), tonic="Emaj9",
         parts=[("pad", 94, dict(v=48, lo=52), 84, 64, 80), ("bells", 11, dict(lo=72, v=60, always=True), 80, 76, 66),
                ("pedal", 32, dict(lo=28), 84, 64, 20), ("pluck", 24, dict(v=48, lo=60, hi=76), 66, 48, 50)]),
    dict(id="cash-flow", title="Cash Flow", moods=["driving"], bpm=140, key="G", minor=True, kit=24, drums="halftime",
         pump=8, A=prog("Gm7 Ebmaj7 Bb F"), B=prog("Ebmaj7 F Gm7 Bb"), tonic="Gm9",
         parts=[("pad", 90, dict(v=62, lo=55), 86, 64, 48), ("sub", 38, dict(lo=31), 102, 64, 6),
                ("motif", 81, dict(lo=74, rhythm=(0, 3, 6, 10, 14), v=58, dur=1.2), 70, 70, 50),
                ("arp", 98, dict(lo=72, rate=2, v=44, gate=0.5), 60, 50, 60)]),
    dict(id="line-item", title="Line Item", moods=["calm"], bpm=92, key="Bb", swing=0.64, kit=40, drums="brush",
         A=prog("Cm7 F7 Bbmaj7 Gm7"), B=prog("Ebmaj7 Ab7 Bbmaj7 G7"), tonic="Bbmaj9",
         parts=[("rhodes", 11, dict(v=58, lo=57, hi=74), 90, 56, 50), ("walk", 32, dict(lo=31), 100, 64, 20),
                ("motif", 11, dict(lo=74, rhythm=(0, 3, 6, 10), v=56), 72, 80, 50)]),
    dict(id="red-ink", title="Red Ink", moods=["tension"], bpm=140, key="C", minor=True, kit=25, drums="halftime",
         A=prog("Cm Ab Eb Bb"), B=prog("Ab Bb Cm Cm"), tonic="Cm",
         parts=[("piano", 0, dict(v=50, lo=55, hi=72), 86, 60, 56), ("sub", 39, dict(lo=31), 104, 64, 6),
                ("bells", 98, dict(lo=72, v=48), 70, 76, 60), ("pad", 95, dict(v=40, lo=50), 64, 64, 70)]),
    dict(id="tidy-sum", title="Tidy Sum", moods=["upbeat", "driving"], bpm=116, key="A", kit=0, drums="pop",
         A=prog("A E F#m D"), B=prog("D E F#m A"), tonic="Aadd9",
         parts=[("stabs", 0, dict(steps=(2, 6, 10, 14), lift_steps=(0, 2, 6, 8, 10, 14), dur=1.6, v=62), 90, 56, 40),
                ("root8", 38, dict(lo=33), 98, 64, 8), ("motif", 98, dict(lo=76, rhythm=(0, 3, 6, 8, 11), v=58, dur=1.6), 74, 74, 50),
                ("pad", 89, dict(v=40), 60, 64, 60)]),
    dict(id="overhead", title="Overhead", moods=["tension"], bpm=104, key="F#", minor=True, kit=0, drums="pulse",
         A=prog("F#m D E C#7"), B=prog("D E F#m C#7"), tonic="F#m",
         parts=[("root8", 38, dict(lo=30), 92, 64, 10), ("stacc", 48, dict(lo=54, v=56), 80, 70, 50),
                ("pad", 89, dict(v=48, lo=49), 76, 58, 70), ("motif", 47, dict(lo=50, rhythm=(0, 8), v=70, dur=3), 66, 64, 40)]),
    dict(id="fresh-start", title="Fresh Start", moods=["upbeat"], bpm=120, key="F", kit=0, drums="four",
         A=prog("F C Dm Bb"), B=prog("Bb C Dm F"), tonic="Fadd9",
         parts=[("pad", 48, dict(v=54, lo=53), 84, 54, 64), ("piano", 0, dict(v=56, lo=60, hi=79, busy=True), 80, 74, 44),
                ("root8", 33, {}, 96, 64, 10), ("motif", 73, dict(lo=77, rhythm=(0, 4, 6, 10, 12), v=56), 66, 80, 56)]),
    dict(id="spreadsheet-groove", title="Spreadsheet Groove", moods=["calm", "driving"], bpm=90, key="A", minor=True, swing=0.56,
         kit=8, drums="boombap", A=prog("Am7 Dm7 G7 Cmaj7"), B=prog("Fmaj7 E7 Am7 Am7"), tonic="Am9", lofi=True,
         parts=[("pad", 16, dict(v=50, rootless=True), 86, 48, 36), ("rootfifth", 33, {}, 100, 64, 10),
                ("motif", 27, dict(lo=69, rhythm=(0, 3, 10), v=62, dur=2), 74, 80, 40)]),
]


# ---------------------------------------------------------------------------------------- arranging
def arrange(t):
    """intro (2 bars at full groove), A (8 bars, the fill on its last bar), B (8 bars, the lift), the 2-bar ending.
    make_demo.py loops A under the setup and B after the reveal, so one of each is all a video needs."""
    bar_s = 60.0 / t["bpm"] * 4
    return [("intro", 2), ("A", 8), ("B", 8), ("out", 2)], bar_s


def to_beats(step, swing):
    beats = step / 4.0
    if not swing or swing == 0.5:
        return beats
    b = math.floor(beats)
    f = beats - b
    f = f * (swing / 0.5) if f < 0.5 else swing + (f - 0.5) * ((1 - swing) / 0.5)
    return b + f


def compose(t):
    rng = np.random.default_rng(sum(map(ord, t["id"])) * 7919)
    sections, bar_s = arrange(t)
    swing = t.get("swing")
    jitter = 10 if swing else 5
    music, drums = {}, []
    lifts = []
    bar0 = 0
    kind = t["drums"]
    for si, (sec, nb) in enumerate(sections):
        t["_next"] = sections[si + 1][0] if si + 1 < len(sections) else None
        progn = t["B"] if sec == "B" else t["A"]
        if sec == "B":
            lifts.append(round(bar0 * bar_s, 4))
        for b in range(nb):
            gb = bar0 + b
            chord = progn[b % len(progn)]
            nxt = progn[(b + 1) % len(progn)]
            c = Ctx(t, "A" if sec == "intro" else sec, b, nb, chord, nxt, rng)
            if sec == "out":
                if b == 0:
                    tonic = C(t["tonic"])
                    for (name, prog_, args, vol, pan, rev) in t["parts"]:
                        if name in ("motif", "bells", "arp", "pizz", "stacc"):
                            continue
                        if name in PARTS and PARTS[name].__name__.startswith("b_"):
                            ev = [(0, bass_note(tonic[0], args.get("lo", 33)), 88, 28)]
                        else:   # the home chord rings for both bars, so it covers an end card of any length
                            ev = [(0.0 + k * 0.08, n, 62, 31) for k, n in enumerate(voicing(tonic, args.get("lo", 55), args.get("hi", 74)))]
                        music.setdefault(name, []).extend((gb, s, n, v, d) for s, n, v, d in ev)
                    drums += [(gb, 0, KICK, 100, 1), (gb, 0, CRASH, 96, 4)]
                continue
            for (name, prog_, args, vol, pan, rev) in t["parts"]:
                ev = PARTS[name](c, args)
                music.setdefault(name, []).extend((gb, s, n, v, d) for s, n, v, d in ev)
            dev = DRUMS[kind](c, t)
            if c.fill:
                dev = [e for e in dev if e[0] < 12 or e[1] in (KICK,)] + drum_fill(c, kind)
            if sec == "B" and b == 0:
                dev.append((0, CRASH, c.vel(100), 4))
            drums += [(gb, s, n, v, d) for s, n, v, d in dev]
        bar0 += nb

    def ticks(gb, s):
        beats = gb * 4 + to_beats(s, swing)
        return max(0, int(round(beats * TPB + rng.normal(0, jitter))))

    parts_midi = {}
    for (name, prog_, args, vol, pan, rev) in t["parts"]:
        parts_midi[name] = [(ticks(gb, s), max(30, int(d * STEP)), n, v) for gb, s, n, v, d in music.get(name, [])]
    drum_midi = [(ticks(gb, s), max(30, int(d * STEP)), n, v) for gb, s, n, v, d in drums]
    total_s = bar0 * bar_s
    t["_sections"] = [[sec, sum(nb for _, nb in sections[:i]), nb] for i, (sec, nb) in enumerate(sections)]
    return parts_midi, drum_midi, lifts, bar_s, total_s


def write_midi(path, t, tracks):
    import mido
    mid = mido.MidiFile(type=1, ticks_per_beat=TPB)
    meta = mido.MidiTrack()
    meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(t["bpm"]), time=0))
    mid.tracks.append(meta)
    for ch, prog_, vol, pan, rev, events in tracks:
        tr = mido.MidiTrack()
        tr.append(mido.Message("program_change", channel=ch, program=prog_, time=0))
        for cc, val in ((7, vol), (10, pan), (91, rev), (93, 20 if ch != 9 else 0)):
            tr.append(mido.Message("control_change", channel=ch, control=cc, value=int(val), time=0))
        msgs = []
        for start, dur, note, vel in events:
            msgs.append((start, 1, mido.Message("note_on", channel=ch, note=int(note), velocity=int(vel))))
            msgs.append((start + dur, 0, mido.Message("note_off", channel=ch, note=int(note), velocity=0)))
        msgs.sort(key=lambda m: (m[0], m[1]))
        now = 0
        for at, _, m in msgs:
            m.time = at - now
            now = at
            tr.append(m)
        mid.tracks.append(tr)
    mid.save(path)


def render(mid_path, wav_path):
    subprocess.run(["fluidsynth", "-ni", "-q", "-r", str(SR), "-g", "0.5", "-o", "audio.file.format=float",
                    "-o", "synth.reverb.room-size=0.55", "-o", "synth.reverb.level=0.7",
                    "-F", wav_path, SF2, mid_path], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import soundfile as sf
    x, sr = sf.read(wav_path, dtype="float32", always_2d=True)
    return x


# ---------------------------------------------------------------------------------------------- mixing
def biquad_hp(x, f):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, f, "highpass", fs=SR, output="sos"), x, axis=0)


def biquad_lp(x, f):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, f, "lowpass", fs=SR, output="sos"), x, axis=0)


def envelope(x, attack_ms, release_ms):
    """Peak follower on a mono signal."""
    a = math.exp(-1.0 / (SR * attack_ms / 1000.0))
    r = math.exp(-1.0 / (SR * release_ms / 1000.0))
    from scipy.signal import lfilter
    rect = np.abs(x)
    # fast approximation: one-pole smoothing with release, then max with the raw rectified signal for attack
    env = lfilter([1 - r], [1, -r], rect)
    return np.maximum(env, lfilter([1 - a], [1, -a], rect))


def compress(x, thresh_db, ratio, attack_ms=10, release_ms=120, makeup_db=0.0):
    mono = x.mean(axis=1)
    env = envelope(mono, attack_ms, release_ms) + 1e-9
    lvl = 20 * np.log10(env)
    over = np.maximum(0.0, lvl - thresh_db)
    gain_db = -over * (1 - 1.0 / ratio) + makeup_db
    return x * (10 ** (gain_db / 20.0))[:, None]


def limit(x, ceiling_db=-1.5, release_ms=60):
    """Lookahead peak limiter (5 ms) with 4x oversampled peak detection, so true peak stays under the ceiling."""
    from scipy.signal import resample_poly
    from scipy.ndimage import maximum_filter1d
    ceil = 10 ** (ceiling_db / 20.0)
    over = np.abs(resample_poly(x, 4, 1, axis=0)).max(axis=1)
    peak = over.reshape(-1, 4).max(axis=1) if len(over) % 4 == 0 else np.pad(over, (0, 4 - len(over) % 4)).reshape(-1, 4).max(axis=1)
    peak = peak[:len(x)]
    look = int(SR * 0.005)
    peak = maximum_filter1d(peak, size=2 * look + 1)
    g = np.minimum(1.0, ceil / (peak + 1e-12))
    r = math.exp(-1.0 / (SR * release_ms / 1000.0))
    from scipy.signal import lfilter
    smooth = 1 - lfilter([1 - r], [1, -r], 1 - g)   # recovers slowly, follows drops instantly via the min below
    g = np.minimum(g, smooth)
    return x * g[:, None]


def loudness(x):
    import pyloudnorm as pyln
    return pyln.Meter(SR).integrated_loudness(x)


def vinyl(n, rng):
    crackle = np.zeros(n, dtype=np.float32)
    idx = rng.integers(0, n, size=n // 2200)
    crackle[idx] = rng.normal(0, 0.35, size=len(idx))
    crackle = biquad_hp(crackle[:, None], 1500)[:, 0]
    hiss = biquad_lp(rng.normal(0, 0.004, size=(n, 1)), 5000)[:, 0]
    return np.stack([crackle + hiss, np.roll(crackle, 37) + hiss], axis=1) * 0.5


def pump(x, kick_times_s, depth_db, beat_s):
    g = np.ones(len(x), dtype=np.float32)
    depth = 10 ** (-depth_db / 20.0)
    rel = int(beat_s * 0.65 * SR)
    shape = depth + (1 - depth) * (1 - np.exp(-np.linspace(0, 4, rel)))
    for kt in kick_times_s:
        i = int(kt * SR)
        if i >= len(g):
            continue
        j = min(len(g), i + rel)
        g[i:j] = np.minimum(g[i:j], shape[: j - i])
    return x * g[:, None]


def build(t, work):
    parts_midi, drum_midi, lifts, bar_s, total_s = compose(t)
    tracks = [(i if i < 9 else i + 1, prog_, vol, pan, rev, parts_midi[name])
              for i, (name, prog_, args, vol, pan, rev) in enumerate(t["parts"])]
    mpath, dpath = os.path.join(work, t["id"] + "_m.mid"), os.path.join(work, t["id"] + "_d.mid")
    write_midi(mpath, t, tracks)
    write_midi(dpath, t, [(9, t.get("kit", 0), 112, 64, 28, drum_midi)])
    m = render(mpath, mpath[:-4] + ".wav")
    d = render(dpath, dpath[:-4] + ".wav")
    n = max(len(m), len(d))
    m = np.pad(m, ((0, n - len(m)), (0, 0)))
    d = np.pad(d, ((0, n - len(d)), (0, 0)))
    m = biquad_hp(m, 45)
    d = biquad_hp(d, 30)
    m = m * 10 ** ((-20.0 - loudness(m)) / 20.0)        # both stems to the same loudness, so drum_gain sets the balance
    d = d * 10 ** ((-20.0 - loudness(d)) / 20.0)
    d = compress(d, -24, 3.0, attack_ms=4, release_ms=90)
    beat_s = 60.0 / t["bpm"]
    if t.get("pump"):
        kicks = sorted({e[0] / TPB * beat_s for e in drum_midi if e[2] == KICK})
        m = pump(m, kicks, t["pump"], beat_s)
    mix = m * t.get("music_gain", 1.0) + d * t.get("drum_gain", 0.7)
    rng = np.random.default_rng(sum(map(ord, t["id"])))
    if t.get("lofi"):
        mix = biquad_lp(mix, 6800)
        mix = np.tanh(mix * 2.0) / 2.0
        cr = vinyl(len(mix), rng)
        cr *= 10 ** (-46 / 20.0) / (np.sqrt(np.mean(cr ** 2)) + 1e-9)
        mix = mix + cr
    mix = compress(mix, -22, 2.0, attack_ms=12, release_ms=160)
    mix = mix * section_gain(len(mix), t["_sections"], bar_s)[:, None]
    end = int(min(len(mix), (total_s + 1.5) * SR))   # keep the last chord's ring, cut the dead tail
    mix = mix[:end]
    fade = int(1.2 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    ramp = int(0.004 * SR)
    mix[:ramp] *= np.linspace(0, 1, ramp)[:, None]
    gain = 10 ** ((LIBRARY_LUFS - loudness(mix)) / 20.0)
    mix = limit(mix * gain, CEILING_DB)
    return mix.astype(np.float32), lifts, bar_s, total_s


def section_gain(n, sections, bar_s, lift_db=LIFT_DB, ramp_s=0.02):
    """B sections and the ending sit LIFT_DB above A, so the lift reads even under a ducked voice-over.
    Each change finishes on the downbeat it belongs to, so the downbeat itself is never smeared."""
    g = np.ones(n, dtype=np.float32)
    up = 10 ** (lift_db / 20.0)
    for kind, bar, nb in sections:
        if kind in ("B", "out"):
            g[int(bar * bar_s * SR):int((bar + nb) * bar_s * SR)] = up
    r = int(ramp_s * SR)
    for kind, bar, nb in sections:
        i = int(bar * bar_s * SR)
        if 0 < i < n:
            a, b = g[max(0, i - r - 1)], g[i]
            if a != b:
                g[max(0, i - r):i] = np.linspace(a, b, i - max(0, i - r), endpoint=False)
    return g


def logo(t, work):
    """The sonic logo: tonic, fifth, octave (two quick notes and a ringing third) on vibraphone with a celesta an
    octave up. Same rhythm and shape on every video, in the key of the track it closes, so it never clashes with
    the final chord. make_demo.py plays it, unducked, as the end card lands."""
    import mido
    tonic = C(t["tonic"])[0]
    base = 67 + ((tonic - 67) % 12)            # tonic between G4 and F#5
    mid = mido.MidiFile(type=1, ticks_per_beat=TPB)
    meta = mido.MidiTrack(); meta.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(120), time=0)); mid.tracks.append(meta)
    sec = TPB * 2                               # ticks per second at 120 bpm
    notes = [(0.0, 0, 92, 0.5), (0.13, 7, 88, 0.5), (0.26, 12, 100, 2.2)]
    for ch, prog_, shift, vscale in ((0, 11, 0, 1.0), (1, 8, 12, 0.62)):
        tr = mido.MidiTrack()
        tr.append(mido.Message("program_change", channel=ch, program=prog_, time=0))
        for cc, val in ((7, 110), (10, 64 if ch == 0 else 74), (91, 70), (93, 0)):
            tr.append(mido.Message("control_change", channel=ch, control=cc, value=val, time=0))
        msgs = []
        for at, iv, vel, dur in notes:
            n = base + iv + shift
            msgs.append((int(at * sec), 1, mido.Message("note_on", channel=ch, note=n, velocity=int(vel * vscale))))
            msgs.append((int((at + dur) * sec), 0, mido.Message("note_off", channel=ch, note=n, velocity=0)))
        msgs.sort(key=lambda m: (m[0], m[1]))
        now = 0
        for at, _, m in msgs:
            m.time = at - now; now = at; tr.append(m)
        mid.tracks.append(tr)
    path = os.path.join(work, t["id"] + "_logo.mid")
    mid.save(path)
    x = render(path, path[:-4] + ".wav")
    x = biquad_hp(x, 120)
    x = x[:int(3.0 * SR)]
    fade = int(0.8 * SR)
    x[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 2
    x = x * 10 ** ((LOGO_LUFS - loudness(x)) / 20.0)
    return limit(x, CEILING_DB).astype(np.float32)


def encode(wav, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libopus", "-b:a", OPUS_KBPS,
                    "-vbr", "on", "-application", "audio", out], check=True)


def main(ids):
    import soundfile as sf
    os.makedirs(TRACKS_DIR, exist_ok=True)
    lib = {x["id"]: x for x in json.load(open(LIBRARY))["tracks"]} if os.path.exists(LIBRARY) else {}
    todo = [t for t in TRACKS if not ids or t["id"] in ids]
    with tempfile.TemporaryDirectory() as work:
        for t in todo:
            t = dict(t)
            mix, lifts, bar_s, total_s = build(t, work)
            wav = os.path.join(work, t["id"] + ".wav")
            sf.write(wav, mix, SR, subtype="FLOAT")
            out = os.path.join(TRACKS_DIR, t["id"] + ".opus")
            encode(wav, out)
            lg = logo(t, work)
            lwav = os.path.join(work, t["id"] + "_logo.wav")
            sf.write(lwav, lg, SR, subtype="FLOAT")
            lout = os.path.join(TRACKS_DIR, t["id"] + "_logo.opus")
            encode(lwav, lout)
            out_bar = t["_sections"][-1][1]
            lib[t["id"]] = {"id": t["id"], "title": t["title"], "moods": t["moods"], "bpm": t["bpm"],
                            "key": t["key"] + (" minor" if t.get("minor") else " major"), "drums": t["drums"],
                            "beats_per_bar": 4, "bar_s": round(bar_s, 6), "sections": t["_sections"],
                            "lifts_s": lifts, "out_s": round(out_bar * bar_s, 4), "music_ends_s": round(total_s, 2),
                            "seconds": round(len(mix) / SR, 2), "lufs": round(loudness(mix), 1),
                            "file": "tracks/" + t["id"] + ".opus", "logo": "tracks/" + t["id"] + "_logo.opus"}
            print(json.dumps({k: lib[t["id"]][k] for k in ("id", "bpm", "seconds", "lifts_s", "out_s", "lufs")}))
    order = [t["id"] for t in TRACKS if t["id"] in lib]
    json.dump({"note": "Original tracks composed in tools/music/compose.py and rendered with the FluidR3 GM soundfont "
                       "(MIT licence). No third-party recordings, samples or melodies, so no rights holder can claim them; "
                       "free to use on every platform.",
               "lufs": LIBRARY_LUFS, "tracks": [lib[i] for i in order]}, open(LIBRARY, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
