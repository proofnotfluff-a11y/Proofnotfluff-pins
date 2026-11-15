#!/usr/bin/env python3
"""The trial's voice, outside the lesson line. Reuses the studio's own voice code (video/studio/anim.py) unchanged.

  voice.py ci OUT      (the studio-trial-voice workflow) speak script.md take by take with the lesson voice, join,
                       time every word with Whisper. Writes OUT/voice.mp3, OUT/takes/NN.mp3, OUT/heard.json.
  voice.py words DIR   (a chat) DIR holds what ci wrote: line the script's words up with the heard times.
                       Writes voice/words.json, voice/transcript.md, video/words.js. Prints flags and pace.
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


def mouth(d, rhubarb):
    """Rhubarb's cues (shape per time) as one letter a frame, 2 frames early like the lessons' mouth (the eye forgives a
    mouth that leads the sound, not one that lags). X (rest) outside words. Plus the studio's own loudness levels."""
    voice = os.path.join(d, "voice.mp3"); wav = os.path.join(d, "voice16.wav"); txt = os.path.join(d, "dialog.txt")
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
    doc = {"schema": "pnf.trial.mouth.v1", "fps": fps, "lead_frames": lead, "tool": "Rhubarb Lip Sync 1.13.0 (MIT), pocketSphinx, dialog file",
           "voiceSha256": wd["voiceSha256"], "shapes": "".join(shapes), "cues": len(cues)}
    open(os.path.join(TRIAL, "video", "mouth.js"), "w").write("window.MOUTH = " + json.dumps(doc) + ";\n")
    share = {s: round(doc["shapes"].count(s) / n, 3) for s in "ABCDEFGHX"}
    print(f"mouth: {len(cues)} cues, {n} frames, share {share}")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"ci": lambda: ci(a[1]), "words": lambda: words(a[1]), "mouth": lambda: mouth(a[1], a[2])}[a[0]]()
