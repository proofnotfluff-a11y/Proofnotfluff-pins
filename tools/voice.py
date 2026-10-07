#!/usr/bin/env python3
"""Offline narration for the promo studio (Kokoro, an open-weight neural voice that runs on CPU).

Why offline: the cloud sandbox cannot open the web-socket the free online voices use, and the crew
never holds vendor keys. Kokoro's model files (about 350 MB) are fetched once per sandbox from the
kokoro-onnx GitHub release and cached in tools/work_voice/; a clip of 15 seconds takes about 5 s.

Usage:
  python3 voice.py "text to say" out.wav [--voice am_michael] [--speed 1.0]
  python3 voice.py --list
In code: from voice import say; seconds = say(text, "out.wav", voice="am_michael")

Voices the crew may use (set in the spec as "voice", or PNF_VOICE in the environment; "none" keeps a
video silent): am_michael, am_adam, af_heart, af_bella. Todd chose am_michael as the brand voice Oct 7; see the ledger
PROMO STUDIO line. Every script line is still a caption, so a muted viewer loses nothing.
"""
import os, sys, json, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "work_voice")
REL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = {"kokoro-v1.0.onnx": 325_000_000, "voices-v1.0.bin": 28_000_000}
VOICES = ["am_michael", "am_adam", "af_heart", "af_bella"]
DEFAULT = os.environ.get("PNF_VOICE", "am_michael")  # the brand voice, Todd Oct 7 ("Michael is good"); the ledger PROMO STUDIO line is the record
SR = 24000


def ensure_model():
    os.makedirs(CACHE, exist_ok=True)
    for name, min_size in FILES.items():
        p = os.path.join(CACHE, name)
        if not os.path.exists(p) or os.path.getsize(p) < min_size * 0.9:
            tmp = p + ".part"
            urllib.request.urlretrieve(REL + name, tmp)
            os.replace(tmp, p)
    try:
        import kokoro_onnx, soundfile  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "kokoro-onnx==0.4.9", "soundfile==0.13.1"], check=True)


_K = None


def _kokoro():
    global _K
    if _K is None:
        ensure_model()
        from kokoro_onnx import Kokoro
        _K = Kokoro(os.path.join(CACHE, "kokoro-v1.0.onnx"), os.path.join(CACHE, "voices-v1.0.bin"))
    return _K


def clean(text):
    """Spoken form: dollar amounts and percents read naturally; no markup."""
    import re
    t = re.sub(r"<[^>]+>", "", text or "")
    t = t.replace("&", " and ")
    t = re.sub(r"(?<=\d)\s*/\s*(?=[a-z\d])", " per ", t)      # 120/hour -> 120 per hour; leaves "and/or" alone
    t = re.sub(r"(?<=\d)\s*[xX]\s*(?=\$?\d)", " times ", t)   # 3 x $2.99 -> 3 times 2.99; leaves "tax" alone
    t = re.sub(r"\$(\d[\d,]*)(\.(\d\d))?", lambda m: f"{m.group(1).replace(',', '')} dollars" + (f" and {int(m.group(3))} cents" if m.group(3) and int(m.group(3)) else ""), t)
    t = t.replace("%", " percent")
    return re.sub(r"\s+", " ", t).strip()


def say(text, out_wav, voice=None, speed=1.0, sr=44100):
    """Synthesize one line to a 44.1 kHz mono wav; returns its length in seconds (0 when voice is none)."""
    voice = voice or DEFAULT
    if not text or voice in (None, "", "none"):
        return 0.0
    if voice not in VOICES:
        raise SystemExit(f"unknown voice {voice}; use one of {VOICES} or none")
    import soundfile as sf
    samples, native = _kokoro().create(clean(text), voice=voice, speed=speed, lang="en-us")
    raw = out_wav + ".raw.wav"
    sf.write(raw, samples, native)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-ar", str(sr), "-ac", "1", out_wav], check=True)
    os.remove(raw)
    return len(samples) / native


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--list":
        print(json.dumps({"voices": VOICES, "default": DEFAULT})); sys.exit(0)
    v, sp = DEFAULT, 1.0
    if "--voice" in a:
        i = a.index("--voice"); v = a[i + 1]; del a[i:i + 2]
    if "--speed" in a:
        i = a.index("--speed"); sp = float(a[i + 1]); del a[i:i + 2]
    secs = say(a[0], a[1], voice=v, speed=sp)
    print(json.dumps({"out": a[1], "seconds": round(secs, 2), "voice": v}))
