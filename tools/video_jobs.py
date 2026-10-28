#!/usr/bin/env python3
"""Render jobs for the Video render workflow (.github/workflows/video-render.yml). A run of the video engine asks for a
render by committing video/jobs/<videoId>.json:
  {"schema": "pnf.video.job.v1", "videoId", "spec": "video/specs/<videoId>.json", "voices": ["<ElevenLabs voice id>" | "test"],
   "requestedAt", "run"}
The workflow then calls `run` (narrate, render, transcribe, gate 5, critic sheets, per voice) and `publish` (the heavy
files to the video-renders branch, the small JSON to main). A job whose result already matches its job and spec
fingerprints is skipped, so a re-run never re-spends ElevenLabs characters.

Usage (in the workflow): python3 tools/video_jobs.py run --out DIR ; python3 tools/video_jobs.py publish --out DIR
       python3 tools/video_jobs.py status VIDEO_ID        what main holds for a job (for the engine's run)
"""
import argparse, datetime as dt, glob, hashlib, json, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
BRANCH = "video-renders"


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def voice_name(vid):
    if vid == "test":
        return "test"
    cfg = json.load(open(os.path.join(ROOT, "video", "config.json")))
    return {v: k for k, v in cfg["voice"]["approvedOct15"].items()}.get(vid, vid[:8])


def sh(cmd, cwd=None, check=True, env=None):
    r = subprocess.run(cmd, cwd=cwd or ROOT, capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError(f"{' '.join(cmd[:3])} failed: {(r.stderr or r.stdout)[-600:]}")
    return r


def pending():
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "video", "jobs", "*.json"))):
        job = json.load(open(f))
        spec = os.path.join(ROOT, job["spec"])
        res = os.path.join(ROOT, "video", "renders", job["videoId"], "result.json")
        if os.path.exists(res):
            r = json.load(open(res))
            if r.get("jobSha256") == sha(f) and os.path.exists(spec) and r.get("specSha256") == sha(spec):
                continue
        out.append((f, job))
    return out


def run(out_root):
    jobs = pending()
    print(f"{len(jobs)} job(s) to render")
    for f, job in jobs:
        vid = job["videoId"]
        spec = os.path.join(ROOT, job["spec"])
        result = {"schema": "pnf.video.render_result.v1", "videoId": vid, "jobSha256": sha(f), "specSha256": sha(spec) if os.path.exists(spec) else None,
                  "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "branch": BRANCH, "voices": []}
        for v in job["voices"]:
            name = voice_name(v)
            d = os.path.join(out_root, vid, name)
            os.makedirs(os.path.join(d, "voice"), exist_ok=True)
            entry = {"voiceId": v, "name": name, "status": "failed", "path": f"{vid}/{name}/"}
            try:
                if not os.path.exists(spec):
                    raise RuntimeError(f"no spec at {job['spec']}")
                if v == "test":
                    sh([sys.executable, "tools/video_voice.py", "test", spec, "--out", os.path.join(d, "voice")])
                else:
                    if not os.environ.get("ELEVENLABS_API_KEY"):
                        entry.update(status="blocked", error="ELEVENLABS_API_KEY is not set as a repo secret")
                        result["voices"].append(entry)
                        continue
                    sh([sys.executable, "tools/video_voice.py", "eleven", spec, "--voice", v, "--out", os.path.join(d, "voice")])
                sh([sys.executable, "tools/video_render.py", "render", spec, os.path.join(d, "voice", "words.json"), "--out", d])
                tr = sh([sys.executable, "tools/video_transcribe.py", os.path.join(d, "video.mp4"), "--out", os.path.join(d, "transcript.json")], check=False)
                if tr.returncode:
                    entry["transcriptError"] = tr.stdout[-200:] + tr.stderr[-200:]
                qa = sh([sys.executable, "tools/video_qa.py", "check", d, "--spec", spec], check=False)
                print(qa.stdout)
                strip_cmd = [sys.executable, "tools/video_render.py", "strips", os.path.join(d, "video.mp4"), "--out", os.path.join(d, "strips")]
                if os.path.exists(os.path.join(d, "transcript.json")):
                    strip_cmd += ["--transcript", os.path.join(d, "transcript.json")]
                sh(strip_cmd)
                q = json.load(open(os.path.join(d, "qa.json")))
                m = json.load(open(os.path.join(d, "manifest.json")))
                entry.update(status="rendered", qaPass=q["pass"], mp4Sha256=m["sha256"], seconds=m["seconds"], lufs=m["lufs"], truePeak=m["truePeak"],
                             chars=m["voice"]["chars"], failed=[c["name"] for c in q["checks"] if not c["pass"]])
            except Exception as e:
                entry["error"] = str(e)[-500:]
            result["voices"].append(entry)
            print(f"{vid} {name}: {entry['status']} {entry.get('error', '')[:200]}")
        os.makedirs(os.path.join(out_root, vid), exist_ok=True)
        json.dump(result, open(os.path.join(out_root, vid, "result.json"), "w"), indent=1)


def push_with_retry(cwd, branch):
    for i in range(4):
        r = sh(["git", "push", "origin", f"HEAD:{branch}"], cwd=cwd, check=False)
        if r.returncode == 0:
            return
        sh(["git", "pull", "--rebase", "origin", branch], cwd=cwd, check=False)
        time.sleep(5 + 5 * i)
    raise RuntimeError(f"could not push to {branch}")


def publish(out_root):
    vids = [d for d in sorted(os.listdir(out_root)) if os.path.isdir(os.path.join(out_root, d))] if os.path.isdir(out_root) else []
    if not vids:
        print("nothing to publish")
        return
    sh(["git", "config", "user.name", "proofnotfluff-bot"]); sh(["git", "config", "user.email", "proofnotfluff-bot@users.noreply.github.com"])
    wt = os.path.join(os.path.dirname(out_root), "renders-branch")
    have = sh(["git", "ls-remote", "--heads", "origin", BRANCH], check=False).stdout.strip()
    if have:
        sh(["git", "fetch", "--depth", "1", "origin", BRANCH])
        sh(["git", "worktree", "add", wt, f"origin/{BRANCH}"])
        sh(["git", "checkout", "-B", BRANCH], cwd=wt)
    else:
        sh(["git", "worktree", "add", "--detach", wt])
        sh(["git", "checkout", "--orphan", BRANCH], cwd=wt)
        sh(["git", "rm", "-rf", "--quiet", "."], cwd=wt, check=False)
        open(os.path.join(wt, "README.md"), "w").write("# Video renders\n\nWritten only by the Video render workflow: one folder per video id and voice "
                                                       "(video.mp4, sheet.jpg, strips/, transcript.json, voice/, props.json, manifest.json, qa.json). "
                                                       "Public data only, counts from the City's 311 records. Nothing here is posted.\n")
    for vid in vids:
        src = os.path.join(out_root, vid)
        dst = os.path.join(wt, vid)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        for d, _, fs in os.walk(dst):
            for fn in fs:
                if fn.endswith(".wav"):
                    os.remove(os.path.join(d, fn))
    sh(["git", "add", "-A"], cwd=wt)
    if sh(["git", "diff", "--cached", "--quiet"], cwd=wt, check=False).returncode:
        sh(["git", "commit", "-m", f"Video renders: {', '.join(vids)}"], cwd=wt)
        push_with_retry(wt, BRANCH)
    for vid in vids:
        res = json.load(open(os.path.join(out_root, vid, "result.json")))
        for v in res["voices"]:
            src = os.path.join(out_root, vid, v["name"])
            dst = os.path.join(ROOT, "video", "renders", vid, v["name"])
            os.makedirs(dst, exist_ok=True)
            for fn in ("manifest.json", "qa.json"):
                if os.path.exists(os.path.join(src, fn)):
                    shutil.copy(os.path.join(src, fn), os.path.join(dst, fn))
        res["rendersCommit"] = sh(["git", "rev-parse", "HEAD"], cwd=wt).stdout.strip()
        json.dump(res, open(os.path.join(ROOT, "video", "renders", vid, "result.json"), "w"), indent=1)
    sh(["git", "add", "-A", "video/renders"])
    if sh(["git", "diff", "--cached", "--quiet"], check=False).returncode:
        sh(["git", "commit", "-m", f"Video render results: {', '.join(vids)}"])
        push_with_retry(ROOT, "main")
    print(f"published {len(vids)} video(s)")


def status(vid):
    res = os.path.join(ROOT, "video", "renders", vid, "result.json")
    if not os.path.exists(res):
        print(f"{vid}: no result yet")
        return 2
    r = json.load(open(res))
    for v in r["voices"]:
        print(f"{vid} {v['name']}: {v['status']}" + (f", QA {'PASS' if v.get('qaPass') else 'FAIL ' + ','.join(v.get('failed', []))}" if v["status"] == "rendered" else "")
              + (f", {v['seconds']} s, {v['lufs']} LUFS, {v.get('chars')} characters" if v.get("seconds") else "") + (f" ({v['error'][:160]})" if v.get("error") else ""))
    print(f"files: git fetch origin {r['branch']} then {r['branch']}:{vid}/<voice>/ (commit {r.get('rendersCommit', '?')[:12]})")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run", "publish", "status"])
    ap.add_argument("video", nargs="?")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "work", "video", "jobs"))
    a = ap.parse_args()
    if a.cmd == "run":
        run(a.out)
    elif a.cmd == "publish":
        publish(a.out)
    else:
        sys.exit(status(a.video))


if __name__ == "__main__":
    main()
