#!/usr/bin/env python3
"""Two takes of one paragraph, stability 0.7 and 0.5, everything else the lessons' own voice (anim.py, unchanged).

  voice.py ci OUT   (the studio-trial-voice workflow) writes OUT/stability-0.7.mp3, OUT/stability-0.5.mp3, OUT/heard.json
"""
import hashlib, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); TRIAL = os.path.dirname(HERE)
STUDIO = os.path.abspath(os.path.join(TRIAL, "..", "..", ".."))
sys.path.insert(0, STUDIO)
import anim  # noqa: E402  (a library here: nothing in it is changed or run as a command)

sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
SETTINGS = [0.7, 0.5]


def text():
    t = open(os.path.join(HERE, "script.md"), encoding="utf-8").read()
    return " ".join(" ".join(p.split()) for p in re.split(r"\n\s*\n", t) if p.strip() and not p.strip().startswith("#"))


def ci(out):
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise SystemExit("ERROR speak: ELEVENLABS_API_KEY is not set as a repo secret")
    req = json.load(open(os.path.join(HERE, "speak.json")))
    if req["scriptSha256"] != sha(os.path.join(HERE, "script.md")):
        raise SystemExit("ERROR speak: script.md changed after speak.json was written")
    t = text()
    if len(t) * len(SETTINGS) > anim.MAX_CHARS:
        raise SystemExit("ERROR speak: over the studio's character limit")
    os.makedirs(out, exist_ok=True)
    takes = []
    for s in SETTINGS:
        f = os.path.join(out, f"stability-{s}.mp3")
        open(f, "wb").write(anim.eleven(t, None, None, req["voice"], key, {"stability": s, "similarity_boost": 0.7}))
        takes.append({"stability": s, "similarity_boost": 0.7, "file": os.path.basename(f), "sha256": sha(f), "seconds": round(anim.seconds_of(f), 3)})
    json.dump({"schema": "pnf.trial.voice-ab.v1", "requestedAt": req["requestedAt"], "voice": req["voice"], "model": req["model"],
               "chars": len(t) * len(SETTINGS), "takes": takes, "credits": anim.credits(key)}, open(os.path.join(out, "heard.json"), "w"), indent=1)
    print(f"spoken: {len(takes)} takes, {len(t)} characters each")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "ci":
        ci(sys.argv[2])
    else:
        raise SystemExit(__doc__)
