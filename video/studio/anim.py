#!/usr/bin/env python3
"""Studio commands (video/studio/CLAUDE.md, CONTEXT.md). One command per stage; every output is a file a person or a
fresh reviewer checks before the next stage runs.

  kit                      build _runtime/map.js (77 community areas) and _runtime/sfx/*.wav (our own sounds, made in code)
  new SLUG                 a video folder from _templates
  data SLUG                resolve brief.md's numbers block against the data file -> 04_scene/data.js (refuses a mismatch)
  speak SLUG [--take N ...] [--voice ID]   ask the Studio voice workflow to speak script.md (writes 01_voice/speak.json)
  ci-voice                 (the workflow) speak, join, transcribe, re-spell, pace; text to main, audio to video-renders
  estimate SLUG            stand-in word timings from script.md (marked estimate: for storyboards and looks, never posted)
  fetch SLUG               pull this video's audio from the video-renders branch
  cues SLUG                match cues.md quotes to words.json -> cues.json, cues.js; prints the timing table
  grab SLUG                capture docs/chicago-rat-complaints/ at phone width -> 04_scene/assets/rat-page.png
  stills SLUG [--look L]   a frame at every cue -> 05_render/sheets/*.jpg and 05_render/sheet.jpg
  render SLUG [--look L] [--from S --to S] [--out F]   frames in Chromium, the mix, H.264/AAC
  check SLUG [--mp4 F]     length, loudness, black, frozen, file -> 05_render/qa.json
  status SLUG              what exists
"""
import argparse, base64, datetime as dt, difflib, glob, hashlib, json, math, os, re, shutil, subprocess, sys, tempfile, time, urllib.request, urllib.error, wave

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
VIDEOS = os.path.join(HERE, "videos")
RUNTIME = os.path.join(HERE, "_runtime")
BRANCH = "video-renders"
FPS = 30
DEFAULT_VOICE = "iP95p4xoKVk53GoZ742B"   # Chris, ElevenLabs library voice (_shared/voice.md; Todd, Oct 28, 11:51 am)
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


def synth(name, seconds, fn, sr=44100):
    import numpy as np
    t = np.arange(int(seconds * sr)) / sr
    y = fn(t, np)
    y = y / (np.max(np.abs(y)) + 1e-9) * 0.7
    pcm = (y * 32767).astype("<i2")
    os.makedirs(os.path.join(RUNTIME, "sfx"), exist_ok=True)
    with wave.open(os.path.join(RUNTIME, "sfx", name + ".wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def build_sfx():
    env = lambda t, a, d, np: np.minimum(t / a, 1) * np.exp(-np.maximum(t - a, 0) / d)
    synth("blip", 0.18, lambda t, np: np.sin(2 * np.pi * (880 + 600 * t) * t) * env(t, 0.004, 0.05, np))
    synth("tick", 0.08, lambda t, np: np.sin(2 * np.pi * 2200 * t) * env(t, 0.001, 0.012, np))
    synth("pop", 0.22, lambda t, np: np.sin(2 * np.pi * (420 + 900 * np.exp(-t * 30)) * t) * env(t, 0.003, 0.06, np))
    synth("stamp", 0.4, lambda t, np: (np.sin(2 * np.pi * 95 * t) + 0.5 * np.random.default_rng(3).standard_normal(len(t)) * np.exp(-t * 60)) * env(t, 0.002, 0.09, np))
    synth("chime", 1.4, lambda t, np: (np.sin(2 * np.pi * 784 * t) + 0.6 * np.sin(2 * np.pi * 1175 * t) + 0.3 * np.sin(2 * np.pi * 1568 * t)) * env(t, 0.005, 0.45, np))
    def whoosh(t, np):
        n = np.random.default_rng(7).standard_normal(len(t))
        k = int(44100 * 0.002); sm = np.convolve(n, np.ones(k) / k, mode="same")
        return sm * np.sin(np.pi * np.clip(t / 0.42, 0, 1)) ** 2
    synth("whoosh", 0.45, whoosh)
    synth("squeak", 0.25, lambda t, np: np.sin(2 * np.pi * (2400 + 900 * np.sin(2 * np.pi * 9 * t)) * t) * env(t, 0.01, 0.07, np))
    print("sfx: blip tick pop stamp chime whoosh squeak")


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


def display(w):
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
    req = {"schema": "pnf.studio.speak.v1", "voice": voice or DEFAULT_VOICE, "model": MODEL, "takes": takes or "all",
           "scriptSha256": sha(vdir(slug, "01_voice", "script.md")), "requestedAt": now()}
    json.dump(req, open(vdir(slug, "01_voice", "speak.json"), "w"), indent=1)
    print(f"speak.json: {len(tk)} takes, {chars} characters, voice {req['voice']}; push it to run the Studio voice workflow")


def eleven(text, prev, nxt, voice, key):
    body = {"text": text, "model_id": MODEL}
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
            if e.code < 500 or attempt:
                raise SystemExit(f"ERROR speak: ElevenLabs answered {e.code}: {msg}")
        except Exception as e:
            if attempt:
                raise SystemExit(f"ERROR speak: ElevenLabs did not answer ({type(e).__name__})")
        time.sleep(4)


def seconds_of(path):
    return float(sh(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def transcribe(audio, model="medium.en"):
    from faster_whisper import WhisperModel
    import numpy as np
    pcm = subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-i", audio, "-ac", "1", "-ar", "16000", "-f", "f32le", "-"], capture_output=True, check=True).stdout
    m = WhisperModel(model, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(np.frombuffer(pcm, dtype=np.float32), language="en", word_timestamps=True, beam_size=5, vad_filter=False)
    return [{"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)} for s in segs for w in (s.words or [])]


def respell(script_words, heard):
    """Script words win; Whisper gives the times. Returns (words, flags)."""
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
            if not all(re.search(r"\d", heard[j]["w"]) for j in range(j1, j2)):
                flags.append(f"{heard[j1]['start']:.1f} s heard '{' '.join(h['w'] for h in heard[j1:j2])}' for '{' '.join(script_words[i1:i2])}'")
        elif tag == "delete":
            flags.append(f"dropped '{' '.join(script_words[i1:i2])}': not heard")
        elif tag == "insert":
            flags.append(f"{heard[j1]['start']:.1f} s added '{' '.join(h['w'] for h in heard[j1:j2])}': not in the script")
    last = 0.0
    for i, v in enumerate(out):   # a dropped word sits at the previous word's end, zero length
        if v is None:
            out[i] = (last, last)
        last = out[i][1]
    return out, flags


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
                open(f, "wb").write(eleven(t, takes[i - 1] if i else None, takes[i + 1] if i + 1 < len(takes) else None, req["voice"], key))
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
        heard = transcribe(voice)
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
        json.dump({"schema": "pnf.studio.takes.v1", "requestedAt": req["requestedAt"], "voice": req["voice"], "model": req["model"],
                   "scriptSha256": req["scriptSha256"], "voiceSha256": sha(voice), "takes": info, "chars": sum(x["chars"] for x in info),
                   "at": now()}, open(tk_path, "w"), indent=1)
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
        m = re.match(r"^music:\s*([\w\-]+)\s+([\d.]+)", ln.strip())
        if m:
            music = {"id": m.group(1), "level": float(m.group(2))}
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
    duration = round(wd["end"] + 1.9, 3)
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


def mix(slug, seconds, out_wav, cues):
    voice = vdir(slug, "01_voice", "audio", "voice.mp3")
    has_voice = os.path.exists(voice) and cues.get("source", "").startswith("whisper")
    lib = json.load(open(os.path.join(ROOT, "tools", "music", "library.json")))
    mus = cues.get("music") or {"id": "quiet-math", "level": 0.16}
    track = next(t for t in lib["tracks"] if t["id"] == mus["id"])
    inputs, filt, labels = [], [], []
    if has_voice:
        inputs += ["-i", voice]; filt.append(f"[{len(inputs) // 2 - 1}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{seconds}[v]"); labels.append("[v]")
    inputs += ["-i", os.path.join(ROOT, "tools", "music", track["file"])]
    mi = len(inputs) // 2 - 1
    gain_db = 20 * math.log10(max(0.01, mus["level"]))
    filt.append(f"[{mi}:a]aresample=48000,aformat=channel_layouts=stereo,atrim=0:{seconds},asetpts=PTS-STARTPTS,volume={gain_db:.1f}dB,"
                f"afade=t=out:st={max(0, seconds - 1.8):.2f}:d=1.8,apad,atrim=0:{seconds}[m]")
    labels.append("[m]")
    for c in cues["cues"]:
        if not c.get("sfx"):
            continue
        f = os.path.join(RUNTIME, "sfx", c["sfx"] + ".wav")
        if not os.path.exists(f):
            raise SystemExit(f"ERROR render: no sound '{c['sfx']}' (anim.py kit)")
        inputs += ["-i", f]
        i = len(inputs) // 2 - 1
        ms = int(c["t"] * 1000)
        filt.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,volume=-13dB,adelay={ms}|{ms},apad,atrim=0:{seconds}[s{i}]")
        labels.append(f"[s{i}]")
    filt.append("".join(labels) + f"amix=inputs={len(labels)}:normalize=0:duration=longest,atrim=0:{seconds}[a]")
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
    os.remove(tmp)
    return has_voice


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
    for name, fn in [("length", lambda: Q.c_length(mp4)), ("loudness", lambda: Q.c_loudness(mp4)), ("black", lambda: Q.c_black(mp4)),
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
    ap.add_argument("--look"); ap.add_argument("--from", dest="t_from", type=float); ap.add_argument("--to", dest="t_to", type=float)
    ap.add_argument("--out"); ap.add_argument("--mp4"); ap.add_argument("--take", type=int, action="append"); ap.add_argument("--voice")
    a = ap.parse_args()
    c = a.cmd
    if c == "kit":
        build_map(); build_sfx()
    elif c == "ci-voice":
        cmd_ci_voice()
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
    elif c == "fetch":
        cmd_fetch(a.slug)
    elif c == "cues":
        cmd_cues(a.slug)
    elif c == "grab":
        cmd_grab(a.slug)
    elif c == "stills":
        cmd_stills(a.slug, a.look)
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
