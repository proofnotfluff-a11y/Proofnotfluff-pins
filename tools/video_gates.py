#!/usr/bin/env python3
"""The video engine's code gates on a spec, in the blueprint's order, before any reviewer or any ElevenLabs character:
  1 spec_lint    the Rat check formula (tools/spec_lint.py rat_check_problems), on every hook written
  2 voice_lint   no AI-sounding phrase in anything said, shown or captioned (tools/voice_lint.py)
  3 legal_scan   no personal detail, promise wording, banned word or em dash (tools/legal_scan.py's lists)
  facts-code     every evidence number recomputed from its path in the data file at the spec's commit and fingerprint
                 (the facts reviewer, gate 4, still judges labels, periods and computed numbers)
Each gate writes one line into spec "gates" with --write. A gate never edits the spec's words.

Usage: python3 tools/video_gates.py code SPEC [--write] [--allow-test] [--data FILE]
       python3 tools/video_gates.py texts SPEC          everything the video says and shows, for a reviewer
       python3 tools/video_gates.py --selftest
"""
import argparse, datetime as dt, hashlib, json, os, re, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import spec_lint  # noqa: E402
import voice_lint  # noqa: E402
import legal_scan  # noqa: E402
import video_story  # noqa: E402


def tool_ref(name):
    p = os.path.join(HERE, name)
    return f"tools/{name}@{hashlib.sha256(open(p, 'rb').read()).hexdigest()[:12]}"


def gate1(spec, allow_test=False):
    return spec_lint.rat_check_problems(spec, allow_test=allow_test)


def gate2(spec):
    out = []
    for where, text in spec_lint.rat_texts(spec):
        for name, words in voice_lint.tells(text):
            out.append(f"{where}: AI-sounding phrase {name} ({words.strip()!r})")
    return out


def gate3(spec):
    out = []
    for where, text in spec_lint.rat_texts(spec):
        for p in legal_scan.PERSONAL:
            if re.search(p, text, re.I):
                out.append(f"{where}: personal detail matching {p!r}")
        for p in legal_scan.PROMISES:
            for m in re.finditer(p, text, re.I):
                ctx = text[max(0, m.start() - 50): m.end() + 50]
                if re.search(r"\b(no|not|nothing|can't|cannot|doesn't|don't|won't|isn't|aren't|without|never|neither|nor)\b[^.]{0,40}" + p, ctx, re.I):
                    continue
                out.append(f"{where}: promise wording {m.group(0)!r}")
        for w in legal_scan.BANNED:
            if re.search(r"\b" + re.escape(w) + r"\b", text, re.I):
                out.append(f"{where}: banned word {w!r}")
        if legal_scan.EMDASH in text or "–" in text:
            out.append(f"{where}: an em or en dash")
    return out


def git_show(commit, path):
    r = subprocess.run(["git", "-C", ROOT, "show", f"{commit}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def facts_code(spec, data_path=None):
    """Recompute every number whose path resolves, from the exact file the spec names (its commit and sha256)."""
    ev = spec.get("evidence") or {}
    raw = open(data_path, "rb").read() if data_path else (git_show(ev.get("commit"), ev.get("file")) if ev.get("commit") not in (None, "uncommitted") else None)
    if raw is None and ev.get("file") and os.path.exists(os.path.join(ROOT, ev["file"])):
        raw = open(os.path.join(ROOT, ev["file"]), "rb").read()
    if raw is None:
        return ["the data file at the spec's commit could not be read"], 0
    out = []
    if hashlib.sha256(raw).hexdigest() != ev.get("sha256"):
        out.append("the data file's sha256 does not match the spec's evidence fingerprint")
    d = json.loads(raw)
    checked = 0
    for x in ev.get("numbers") or []:
        got = video_story.resolve(d, x["path"])
        if got is None:
            continue
        checked += 1
        if got != x["value"]:
            out.append(f"{x['id']}: the spec says {x['value']!r}, {x['path']} is {got!r}")
    return out, checked


def run_code(spec_path, write=False, allow_test=False, data=None):
    spec = json.load(open(spec_path, encoding="utf-8"))
    now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    res = {}
    for name, fn, tool in (("spec_lint", lambda: gate1(spec, allow_test), "spec_lint.py"), ("voice_lint", lambda: gate2(spec), "voice_lint.py"),
                           ("legal_scan", lambda: gate3(spec), "legal_scan.py")):
        try:
            p = fn()
        except Exception as e:
            p = [f"the gate could not run: {type(e).__name__}: {str(e)[:120]}"]
        res[name] = {"pass": not p, "problems": p, "at": now, "tool": tool_ref(tool)}
    try:
        p, n = facts_code(spec, data)
    except Exception as e:
        p, n = [f"could not run: {type(e).__name__}: {str(e)[:120]}"], 0
    res["facts_code"] = {"pass": not p and n > 0, "problems": p or ([] if n else ["no number could be recomputed"]), "checked": n, "at": now,
                         "tool": tool_ref("video_gates.py")}
    if write:
        spec.setdefault("gates", {}).update(res)
        open(spec_path, "w", encoding="utf-8").write(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
    return res


def selftest():
    bad = []
    base = json.load(open(os.path.join(ROOT, "video", "fixtures", "spec-example.json"), encoding="utf-8"))
    data = os.path.join(ROOT, "video", "fixtures", "normal.json")

    def run(spec):
        d = tempfile.mkdtemp()
        p = os.path.join(d, "spec.json")
        json.dump(spec, open(p, "w"), ensure_ascii=False)
        return run_code(p, allow_test=True, data=data)

    r = run(base)
    if not all(v["pass"] for v in r.values()):
        bad.append(f"the worked example passes gates 1 to 3 and the number recompute: {[(k, v['problems'][:2]) for k, v in r.items() if not v['pass']]}")

    def plant(name, gate, mut):
        s = json.loads(json.dumps(base))
        mut(s)
        if run(s)[gate]["pass"]:
            bad.append(f"planted {name} is caught by {gate}")

    plant("a wrong number on screen", "spec_lint", lambda s: s["lines"][1].update(say="Lake View logged 310 rat complaints."))
    plant("a wrong number in the evidence", "facts_code", lambda s: s["evidence"]["numbers"][2].update(value=310))
    plant("an em dash", "spec_lint", lambda s: s["lines"][2].update(say=s["lines"][2]["say"] + " — and rising."))
    plant("an em dash (legal scan)", "legal_scan", lambda s: s["lines"][2].update(say=s["lines"][2]["say"] + " — and rising."))
    plant("an AI-sounding phrase", "voice_lint", lambda s: s["lines"][6].update(say="Let's delve into what this means for your crew."))
    plant("a personal detail", "legal_scan", lambda s: s["lines"][6].update(say="Edison Park is quiet this month."))
    plant("promise wording", "legal_scan", lambda s: s["captions"].update(instagram=s["captions"]["instagram"] + " Guaranteed jobs."))
    plant("rats found", "spec_lint", lambda s: s["lines"][1].update(say="Lake View found 300 rats."))
    plant("the close said twice", "spec_lint", lambda s: s["lines"][6].update(tts="See it free at proofnotfluff dot com slash rats."))
    plant("digits in a heard line", "spec_lint", lambda s: s["lines"][1].update(tts="Lake View logged 300 rat complaints."))
    plant("two hooks only", "spec_lint", lambda s: s.update(hooks=s["hooks"][:2]))
    plant("an unapproved voice", "spec_lint", lambda s: s["voice"].update(voiceIds=["21m00Tcm4TlvDq8ikWAM"]))
    plant("a caption with no AI voice line", "spec_lint", lambda s: s["captions"].update(instagram=s["captions"]["instagram"].replace("Narrated by an AI voice.", "")))
    plant("an address on screen", "spec_lint", lambda s: s["screen"]["scenes"]["why"].update(title="Calls near 4100 N Hampton Dr"))
    for b in bad:
        print("FAIL", b)
    print(f"video_gates selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (worked example passes; wrong number on screen and in the "
          "evidence, em dash, AI phrase, personal detail, promise, rats found, close twice, digits heard, too few hooks, voice, AI line, address)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["code", "texts"])
    ap.add_argument("spec", nargs="?")
    ap.add_argument("--write", action="store_true"); ap.add_argument("--allow-test", action="store_true"); ap.add_argument("--data")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.cmd == "texts":
        for where, text in spec_lint.rat_texts(json.load(open(a.spec, encoding="utf-8"))):
            if text.strip():
                print(f"{where}: {text}")
        return
    if a.cmd == "code":
        res = run_code(a.spec, a.write, a.allow_test, a.data)
        for k, v in res.items():
            print(f"{'PASS' if v['pass'] else 'FAIL'} {k}" + (f": {'; '.join(v['problems'][:5])}" if v["problems"] else ""))
        sys.exit(0 if all(v["pass"] for v in res.values()) else 1)
    print(__doc__)


if __name__ == "__main__":
    main()
