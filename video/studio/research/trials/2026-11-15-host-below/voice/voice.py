#!/usr/bin/env python3
"""The trial's voice, outside the lesson line. Reuses the studio's own voice code (video/studio/anim.py) unchanged.

  voice.py ci OUT      (the studio-trial-voice workflow) speak script.md take by take with the lesson voice, join,
                       time every word with Whisper. Writes OUT/voice.mp3, OUT/takes/NN.mp3, OUT/heard.json.
  voice.py words DIR   (a chat) DIR holds what ci wrote: line the script's words up with the heard times.
                       Writes voice/words.json, voice/transcript.md, video/words.js. Prints flags and pace.
  voice.py tighten DIR (a chat) cut the dead air: every silence longer than KEEP s is shortened to KEEP s (only silence is
                       removed, from its middle; no word is touched). Writes DIR/voice-tight.wav and moves the word times.
  voice.py mouth DIR RHUBARB   (a chat) mouth shapes from the voice with Rhubarb Lip Sync (MIT), plus the studio's
                       own 4 loudness levels as the fallback. Writes video/mouth.js.
"""
import hashlib, json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TRIAL = os.path.dirname(HERE)
STUDIO = os.path.abspath(os.path.join(TRIAL, "..", "..", ".."))
sys.path.insert(0, STUDIO)
import anim  # noqa: E402  (a library here: nothing in it is changed or run as a command)

GAP = 0.32
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()


def takes():
    txt = open(os.path.join(HERE, "script.md"), encoding="utf-8").read()
    paras = [p.strip() for p in re.split(r"\n\s*\n", txt) if p.strip()]
    return [" ".join(p.split()) for p in paras if not p.startswith("#")]


def ci(out):
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SystemExit("ERROR speak: ELEVENLABS_API_KEY is not set as a repo secret")
    req = json.load(open(os.path.join(HERE, "speak.json"))); tk = takes()
    if req["scriptSha256"] != sha(os.path.join(HERE, "script.md")):
        raise SystemExit("ERROR speak: script.md changed after speak.json was written")
    if sum(len(t) for t in tk) > anim.MAX_CHARS:
        raise SystemExit("ERROR speak: over the studio's character limit")
    os.makedirs(os.path.join(out, "takes"), exist_ok=True); info = []
    for i, t in enumerate(tk):
        f = os.path.join(out, "takes", f"{i + 1:02d}.mp3")
        open(f, "wb").write(anim.eleven(t, tk[i - 1] if i else None, tk[i + 1] if i + 1 < len(tk) else None, req["voice"], key, req.get("settings")))
        info.append({"n": i + 1, "file": f"takes/{i + 1:02d}.mp3", "sha256": sha(f), "seconds": round(anim.seconds_of(f), 3), "chars": len(t)})
    gap, lst, voice = os.path.join(out, "gap.mp3"), os.path.join(out, "list.txt"), os.path.join(out, "voice.mp3")
    anim.sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", str(GAP), "-c:a", "libmp3lame", "-b:a", "128k", gap])
    with open(lst, "w") as fh:
        for i, x in enumerate(info):
            fh.write(f"file '{os.path.join(out, x['file'])}'\n")
            if i + 1 < len(info):
                fh.write(f"file '{gap}'\n")
    anim.sh(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "160k", voice])
    t0, heard = 0.0, []
    for x in info:
        x["start"] = round(t0, 3); t0 += x["seconds"]; x["end"] = round(t0, 3); t0 += GAP
        heard += anim.transcribe(os.path.join(out, x["file"]), offset=x["start"])   # one take at a time, like the lessons
    json.dump({"schema": "pnf.trial.heard.v1", "requestedAt": req["requestedAt"], "voice": req["voice"], "model": req["model"],
               "scriptSha256": req["scriptSha256"], "voiceSha256": sha(voice), "takes": info, "heard": heard,
               "chars": sum(x["chars"] for x in info), "credits": anim.credits(key)}, open(os.path.join(out, "heard.json"), "w"), indent=1)
    os.remove(gap); os.remove(lst)
    print(f"spoken: {len(info)} takes, {t0 - GAP:.1f} s, {len(heard)} words heard")


def words(d):
    h = json.load(open(os.path.join(d, "heard.json"))); tk = takes()
    if h["scriptSha256"] != sha(os.path.join(HERE, "script.md")):
        raise SystemExit("ERROR words: the voice was spoken from a different script.md")
    sw, take_of = [], []
    for i, t in enumerate(tk):
        ws = anim.spoken_words(t); sw += ws; take_of += [i + 1] * len(ws)
    times, flags = anim.respell(sw, h["heard"])
    ws = [{"w": anim.display(w), "start": s, "end": e, "take": take_of[i]} for i, (w, (s, e)) in enumerate(zip(sw, times))]
    pace = []
    for x in h["takes"]:
        n = sum(1 for w in ws if w["take"] == x["n"]); x["wpm"] = round(n / max(0.1, x["seconds"]) * 60)
        pace.append(f"  {x['n']:02d}  {x['start']:6.1f} s  {x['seconds']:5.1f} s  {x['wpm']} wpm")
    doc = {"schema": "pnf.studio.words.v1", "source": "whisper medium.en int8, re-spelled from script.md", "voice": h["voice"], "model": h["model"],
           "voiceSha256": h["voiceSha256"], "words": ws, "takes": [{k: x[k] for k in ("n", "start", "end", "wpm")} for x in h["takes"]],
           "flags": flags, "end": round(ws[-1]["end"], 3)}
    json.dump(doc, open(os.path.join(HERE, "words.json"), "w"), indent=1)
    open(os.path.join(TRIAL, "video", "words.js"), "w").write("window.WORDS = " + json.dumps({k: doc[k] for k in ("words", "takes", "end", "source")}) + ";\n")
    lines, cur, ct = [], [], None
    for w in ws:
        if not cur:
            ct = w["start"]
        cur.append(w["w"])
        if re.search(r"[.!?]$", w["w"]):
            lines.append(f"`{ct:04.1f}` " + " ".join(cur)); cur = []
    open(os.path.join(HERE, "transcript.md"), "w").write(
        f"# Transcript: host-below trial\n\nVoice {h['voice']} ({h['model']}), {len(ws)} words, {doc['end']:.1f} s of voice.\n\n## Flags\n"
        + ("\n".join(f"- {f}" for f in flags) if flags else "none") + "\n\n## Pace per take\n```\n" + "\n".join(pace) + "\n```\n\n## Words\n\n" + "\n\n".join(lines) + "\n")
    print(f"words: {len(ws)}, {doc['end']:.1f} s, flags: {flags or 'none'}\n" + "\n".join(pace))


KEEP = 0.34


def tighten(d):
    import numpy as np
    src = os.path.join(d, "voice.mp3"); sr = 44100
    wd = json.load(open(os.path.join(HERE, "words.json")))
    if wd.get("tightened"):
        raise SystemExit("words.json is already tightened: run `words` again first")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", src, "-af", "silencedetect=noise=-40dB:d=0.25", "-f", "null", "-"], capture_output=True, text=True).stderr
    sil = list(zip([float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)], [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]))
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout, dtype=np.float32).copy()
    cuts = []   # [from, to] seconds removed, in the middle of a silence, never inside a word
    for s0, e0 in sil:
        if s0 < 0.05 or e0 > len(x) / sr - 0.05 or e0 - s0 <= KEEP:
            continue
        mid = (s0 + e0) / 2; cut = (e0 - s0) - KEEP; a, b = mid - cut / 2, mid + cut / 2
        if any(w["start"] - 0.03 < b and w["end"] + 0.03 > a for w in wd["words"]):
            continue   # Whisper puts a word here: leave it
        cuts.append([round(a, 3), round(b, 3)])
    out, pos, fade = [], 0, int(sr * 0.006)
    for a, b in cuts:
        seg = x[pos:int(a * sr)].copy(); seg[-fade:] *= np.linspace(1, 0, fade); out.append(seg)
        pos = int(b * sr); x[pos:pos + fade] *= np.linspace(0, 1, fade)
    out.append(x[pos:]); y = np.concatenate(out)
    wav = os.path.join(d, "voice-tight.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-", wav], input=y.tobytes(), check=True)
    shift = lambda t: round(t - sum(b - a for a, b in cuts if b <= t + 1e-6), 3)
    for w in wd["words"]:
        w["start"], w["end"] = shift(w["start"]), shift(w["end"])
    for t in wd["takes"]:
        t["start"], t["end"] = shift(t["start"]), shift(t["end"])
    wd["end"] = wd["words"][-1]["end"]; wd["tightened"] = {"keep": KEEP, "cuts": cuts, "removed": round(sum(b - a for a, b in cuts), 2), "wavSha256": sha(wav)}
    json.dump(wd, open(os.path.join(HERE, "words.json"), "w"), indent=1)
    open(os.path.join(TRIAL, "video", "words.js"), "w").write("window.WORDS = " + json.dumps({k: wd[k] for k in ("words", "takes", "end", "source")}) + ";\n")
    n = len(wd["words"]); print(f"tightened: {len(cuts)} cuts, {wd['tightened']['removed']} s removed, voice now {len(y) / sr:.1f} s, last word ends {wd['end']} s, {round(n / wd['end'] * 60)} wpm overall")


def mouth(d, rhubarb):
    """Rhubarb's cues (shape per time) as one letter a frame, 2 frames early like the lessons' mouth (the eye forgives a
    mouth that leads the sound, not one that lags). X (rest) outside words. Plus the studio's own loudness levels."""
    voice = os.path.join(d, "voice-tight.wav") if os.path.exists(os.path.join(d, "voice-tight.wav")) else os.path.join(d, "voice.mp3")
    wav = os.path.join(d, "voice16.wav"); txt = os.path.join(d, "dialog.txt")
    anim.sh(["ffmpeg", "-y", "-loglevel", "error", "-i", voice, "-ac", "1", "-ar", "16000", wav])
    open(txt, "w").write("\n".join(anim.TAG.sub(" ", t) for t in takes()) + "\n")
    out = os.path.join(d, "rhubarb.json")
    r = subprocess.run([rhubarb, "-f", "json", "-d", txt, "--extendedShapes", "GHX", "-o", out, wav], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit("ERROR mouth: rhubarb failed: " + r.stderr[-300:])
    cues = json.load(open(out))["mouthCues"]; wd = json.load(open(os.path.join(HERE, "words.json")))
    fps, lead = anim.FPS, 2
    n = int((wd["end"] + 1.5) * fps) + 1; shapes = []
    for i in range(n):
        t = (i + lead) / fps
        c = next((c for c in cues if c["start"] <= t < c["end"]), None)
        shapes.append(c["value"] if c else "X")
    # Rhubarb holds a shape through a short pause; on a big face an open mouth with no sound reads as wrong. Shut it
    # (rest) on any frame the voice itself is silent, the way the lessons' own mouth does, and drop one-frame shapes.
    import numpy as np
    x = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", wav, "-f", "f32le", "-"], capture_output=True, check=True).stdout, dtype=np.float32)
    quiet = 0
    for i in range(n):
        t = (i + lead) / fps; seg = x[max(0, int((t - 0.01) * 16000)):int((t + 0.045) * 16000)]
        if len(seg) == 0 or float(np.sqrt(np.mean(seg ** 2))) < 0.008:
            quiet += shapes[i] not in "XA"; shapes[i] = "X"
    for i in range(1, n - 1):
        if shapes[i] != shapes[i - 1] and shapes[i] != shapes[i + 1] and shapes[i] != "X":
            shapes[i] = shapes[i - 1]
    doc = {"schema": "pnf.trial.mouth.v1", "fps": fps, "lead_frames": lead, "tool": "Rhubarb Lip Sync 1.13.0 (MIT), pocketSphinx, dialog file; shut on silent frames",
           "shut_on_silence_frames": quiet,
           "voiceSha256": wd["voiceSha256"], "shapes": "".join(shapes), "cues": len(cues)}
    open(os.path.join(TRIAL, "video", "mouth.js"), "w").write("window.MOUTH = " + json.dumps(doc) + ";\n")
    share = {s: round(doc["shapes"].count(s) / n, 3) for s in "ABCDEFGHX"}
    print(f"mouth: {len(cues)} cues, {n} frames, share {share}")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"ci": lambda: ci(a[1]), "tighten": lambda: tighten(a[1]), "words": lambda: words(a[1]), "mouth": lambda: mouth(a[1], a[2])}[a[0]]()
