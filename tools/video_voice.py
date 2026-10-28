#!/usr/bin/env python3
"""Narration for the Rat check videos: ElevenLabs Eleven v4 through its own API, one clip per spoken line, with the
character timings ElevenLabs returns turned into word timings for the captions. Runs only inside the Video render
workflow (.github/workflows/video-render.yml), where the key lives as the ELEVENLABS_API_KEY secret (Todd's narration
route, call 3, Option A). The key is read from the environment, sent only in the xi-api-key header, and never printed,
logged or written to a file (CONSTITUTION 4).

Clips are used exactly as ElevenLabs returns them: no speed change, no silence trim (cmo/CONTENT_PLAYBOOK.md section 9);
the length is fitted with the script, before any character is spent.

Usage
  video_voice.py segments SPEC                          the spoken lines in order (key, caption, heard), with characters
  video_voice.py eleven SPEC --voice ID --out DIR       narrate every line; writes DIR/<key>.mp3 and DIR/words.json
  video_voice.py test SPEC --out DIR                    a stand-in voice for pipeline tests (tones, never publishable)
  video_voice.py --selftest
words.json: {"schema": "pnf.video.words.v1", "voiceId", "voiceName", "model", "test", "chars", "segments": [{"key",
  "file", "sha256", "seconds", "say", "tts", "words": [{"w", "start", "end"}]}]}
"""
import argparse, base64, hashlib, json, math, os, re, struct, subprocess, sys, tempfile, time, urllib.request, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format={fmt}"
MAX_CHARS_PER_VOICE = 1500   # a Rat check script is about 600 to 750 characters; anything far past that is a bug


def config():
    return json.load(open(os.path.join(ROOT, "video", "config.json"), encoding="utf-8"))


def segments(spec):
    """The spoken lines in the order the video plays them: the chosen hook, the body lines, the close."""
    out = []
    h = spec.get("hook") or {}
    if h.get("say"):
        out.append({"key": "hook", "say": h["say"], "tts": h.get("tts") or h["say"], "scene": "hook"})
    for i, l in enumerate(spec.get("lines", []), 1):
        out.append({"key": l.get("id") or f"l{i}", "say": l["say"], "tts": l.get("tts") or l["say"], "scene": l.get("scene", "picture")})
    c = spec.get("cta") or {}
    if c.get("say"):
        out.append({"key": "cta", "say": c["say"], "tts": c.get("tts") or c["say"], "scene": "end"})
    return out


def words_from_alignment(al):
    """ElevenLabs gives one start and end time per character; a word runs from its first letter to its last."""
    chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
    words, cur, s0, e0 = [], "", None, None
    for ch, s, e in zip(chars, st, en):
        if ch.isspace():
            if cur:
                words.append({"w": cur, "start": round(s0, 3), "end": round(e0, 3)})
            cur, s0, e0 = "", None, None
            continue
        if not cur:
            s0 = s
        cur += ch
        e0 = e
    if cur:
        words.append({"w": cur, "start": round(s0, 3), "end": round(e0, 3)})
    return words


def probe_seconds(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True)
    return round(float(r.stdout.strip()), 3)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def eleven(spec, voice_id, out_dir, key=None, model=None, fmt=None):
    cfg = config()
    key = key or os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SystemExit("ERROR voice: ELEVENLABS_API_KEY is not set in this run (the video is blocked, never narrated in another voice)")
    model = model or cfg["voice"]["model"]
    fmt = fmt or cfg["voice"]["outputFormat"]
    segs = segments(spec)
    chars = sum(len(s["tts"]) for s in segs)
    if chars > MAX_CHARS_PER_VOICE:
        raise SystemExit(f"ERROR voice: {chars} characters for one voice (limit {MAX_CHARS_PER_VOICE}); shorten the script first")
    os.makedirs(out_dir, exist_ok=True)
    names = {v: k for k, v in cfg["voice"]["approvedOct15"].items()}
    out = {"schema": "pnf.video.words.v1", "voiceId": voice_id, "voiceName": names.get(voice_id, "?"), "model": model,
           "test": False, "chars": chars, "segments": []}
    for i, s in enumerate(segs):
        body = {"text": s["tts"], "model_id": model,
                "previous_text": segs[i - 1]["tts"] if i else None, "next_text": segs[i + 1]["tts"] if i + 1 < len(segs) else None}
        req = urllib.request.Request(API.format(voice=voice_id, fmt=fmt), data=json.dumps(body).encode(), method="POST",
                                     headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
        data = None
        for attempt in range(2):   # one retry on a network or 5xx error; a 4xx is a stop
            try:
                with urllib.request.urlopen(req, timeout=120) as r:
                    data = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                msg = e.read()[:300].decode("utf-8", "replace")
                msg = msg.replace(key, "<key>")
                if e.code < 500 or attempt:
                    raise SystemExit(f"ERROR voice: ElevenLabs answered {e.code} on line {s['key']}: {msg}")
            except Exception as e:
                if attempt:
                    raise SystemExit(f"ERROR voice: ElevenLabs did not answer on line {s['key']}: {type(e).__name__}")
            time.sleep(3)
        f = os.path.join(out_dir, f"{s['key']}.mp3")
        open(f, "wb").write(base64.b64decode(data["audio_base64"]))
        al = data.get("alignment") or data.get("normalized_alignment")
        if not al:
            raise SystemExit(f"ERROR voice: no word timings came back for line {s['key']}")
        out["segments"].append({"key": s["key"], "file": os.path.basename(f), "sha256": sha(f), "seconds": probe_seconds(f),
                                "say": s["say"], "tts": s["tts"], "scene": s["scene"], "words": words_from_alignment(al)})
    json.dump(out, open(os.path.join(out_dir, "words.json"), "w"), indent=1)
    return out


def test_voice(spec, out_dir):
    """A stand-in for pipeline tests: a soft tone per word at about 2.7 words a second. Marked test: true, so spec_lint,
    the QA and the publisher refuse it for anything that posts."""
    os.makedirs(out_dir, exist_ok=True)
    segs = segments(spec)
    out = {"schema": "pnf.video.words.v1", "voiceId": "test", "voiceName": "test tones", "model": "test", "test": True,
           "chars": sum(len(s["tts"]) for s in segs), "segments": []}
    sr = 44100
    for s in segs:
        ws = s["tts"].split()
        t, words, frames = 0.08, [], []
        for w in ws:
            d = 0.16 + 0.045 * len(w)
            words.append({"w": w, "start": round(t, 3), "end": round(t + d, 3)})
            t += d + 0.07
        total = t + 0.15
        n = int(total * sr)
        buf = bytearray()
        for i in range(n):
            x = i / sr
            amp = 0.0
            for wd in words:
                if wd["start"] <= x < wd["end"]:
                    p = (x - wd["start"]) / (wd["end"] - wd["start"])
                    amp = 0.25 * math.sin(math.pi * p)
                    break
            v = amp * (math.sin(2 * math.pi * 196 * x) + 0.4 * math.sin(2 * math.pi * 392 * x))
            buf += struct.pack("<h", int(max(-1, min(1, v)) * 32000))
        wav = os.path.join(out_dir, f"{s['key']}.wav")
        with wave.open(wav, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes(bytes(buf))
        mp3 = os.path.join(out_dir, f"{s['key']}.mp3")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libmp3lame", "-b:a", "128k", mp3], check=True)
        os.remove(wav)
        out["segments"].append({"key": s["key"], "file": os.path.basename(mp3), "sha256": sha(mp3), "seconds": probe_seconds(mp3),
                                "say": s["say"], "tts": s["tts"], "scene": s["scene"], "words": words})
    json.dump(out, open(os.path.join(out_dir, "words.json"), "w"), indent=1)
    return out


def selftest():
    bad = []
    al = {"characters": list("Rats up here"), "character_start_times_seconds": [0.0, .1, .2, .3, .35, .4, .5, .55, .6, .7, .8, .9],
          "character_end_times_seconds": [.1, .2, .3, .35, .4, .5, .55, .6, .7, .8, .9, 1.0]}
    w = words_from_alignment(al)
    if [x["w"] for x in w] != ["Rats", "up", "here"] or w[0]["start"] != 0.0 or w[2]["end"] != 1.0:
        bad.append(f"words from character timings: {w}")
    spec = {"hook": {"say": "Rats are up 221%.", "tts": "Rats are up two hundred twenty-one percent."},
            "lines": [{"id": "l1", "say": "Forty-five complaints.", "scene": "picture"}], "cta": {"say": "See it free."}}
    keys = [s["key"] for s in segments(spec)]
    if keys != ["hook", "l1", "cta"]:
        bad.append(f"segment order {keys}")
    if segments(spec)[0]["tts"].count("two hundred") != 1:
        bad.append("the heard line is the tts field")
    env = dict(os.environ)
    env.pop("ELEVENLABS_API_KEY", None)
    r = subprocess.run([sys.executable, __file__, "eleven", "/dev/null", "--voice", "x", "--out", tempfile.mkdtemp()], env=env,
                       capture_output=True, text=True)
    if r.returncode == 0 or "ELEVENLABS_API_KEY is not set" not in (r.stdout + r.stderr):
        bad.append("no key: the run stops with one line")
    for b in bad:
        print("FAIL", b)
    print(f"video_voice selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (word timings, segment order, heard lines, no key stops)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["segments", "eleven", "test"])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--voice"); ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.cmd == "eleven" and not os.environ.get("ELEVENLABS_API_KEY"):
        raise SystemExit("ERROR voice: ELEVENLABS_API_KEY is not set in this run (the video is blocked, never narrated in another voice)")
    spec = json.load(open(a.spec, encoding="utf-8"))
    if a.cmd == "segments":
        for s in segments(spec):
            print(f"{s['key']:>5} ({len(s['tts'])} chars) {s['tts']}")
        print(f"total {sum(len(s['tts']) for s in segments(spec))} characters")
    elif a.cmd == "eleven":
        o = eleven(spec, a.voice, a.out)
        print(f"narrated {len(o['segments'])} lines in {o['voiceName']} ({o['chars']} characters)")
    elif a.cmd == "test":
        o = test_voice(spec, a.out)
        print(f"test voice: {len(o['segments'])} lines")


if __name__ == "__main__":
    main()
