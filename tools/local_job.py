#!/usr/bin/env python3
"""Send text jobs to the GEEKOM local model server and wait for the answers, in one command.

    python3 tools/local_job.py send <job.json> [<job.json> ...] [--wait] [--timeout 900] [--every 30]
    python3 tools/local_job.py wait <name> [<name> ...] [--timeout 900] [--every 30]
    python3 tools/local_job.py health

The lane is the private repo proofnotfluff-a11y/pnf-local-jobs, cloned at $PNF_LOCAL_JOBS (default
/home/claude/pnf-local-jobs). A job file is named <slug>-<kind>-<date>-r<round>.json and holds kind, model (workhorse or
fast), prompt, input, schema (required) and optional system, max_tokens, think, checks. `send` copies each file into
jobs/, commits and pushes; the poller on the box answers in answers/<same name>.json (status ok, bad_json, error,
timeout). `wait` fetches every --every seconds until each answer is on the remote, pulls once and prints
"<name>: <status> <seconds>s". Exit 0 when every answer came back, 2 on timeout.

Rules (Local AI architecture doc, Nov 5, 2026): business fields only, never a person's name, email or phone, a key, or
anything from data/. Every answer is checked by Claude against the source before anything uses it. A new job kind starts
in shadow mode (Claude does the job too; the local answer is only compared). No answer in 15 minutes or a status other
than ok: do the job on Claude, note it, and do not retry the box that day for that job. "stop local" = control/stop.
"""
import argparse, json, os, re, shutil, subprocess, sys, time

LANE = os.environ.get("PNF_LOCAL_JOBS", "/home/claude/pnf-local-jobs")
NAME = re.compile(r"^[a-z0-9][a-z0-9-]*-[a-z-]+-\d{4}-\d{2}-\d{2}(-\d{4})?-r\d+$")
PERSON = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")


def git(*args):
    return subprocess.run(["git", *args], cwd=LANE, capture_output=True, text=True)


def stopped():
    return os.path.exists(os.path.join(LANE, "control", "stop"))


def problems(job, name):
    out = []
    if not NAME.match(name):
        out.append(f"name {name!r} is not <slug>-<kind>-<date>-r<round>")
    for k in ("kind", "model", "prompt", "input", "schema"):
        if k not in job:
            out.append(f"missing {k}")
    if job.get("model") not in ("workhorse", "fast"):
        out.append("model must be workhorse or fast")
    blob = json.dumps(job)
    if PERSON.search(blob):
        out.append("an email address or phone number is in the job: the lane carries business fields only")
    return out


def send(paths):
    git("pull", "-q", "--rebase", "--autostash")
    if stopped():
        print("local_job: control/stop is set (stop local): do the work on Claude")
        return 3
    names = []
    for p in paths:
        job = json.load(open(p, encoding="utf-8"))
        name = os.path.splitext(os.path.basename(p))[0]
        bad = problems(job, name)
        if bad:
            print(f"local_job: {name} refused: " + "; ".join(bad))
            return 1
        dst = os.path.join(LANE, "jobs", name + ".json")
        if os.path.exists(dst) or os.path.exists(os.path.join(LANE, "answers", name + ".json")):
            print(f"local_job: {name} already sent (a new round is a new name)")
            return 1
        shutil.copyfile(p, dst)
        git("add", dst)
        names.append(name)
    r = git("commit", "-q", "-m", "jobs: " + ", ".join(names))
    if r.returncode:
        print("local_job: commit failed: " + (r.stderr or r.stdout).strip()[:200])
        return 1
    r = git("push", "-q", "origin", "HEAD:main")
    if r.returncode:
        git("pull", "-q", "--rebase")
        r = git("push", "-q", "origin", "HEAD:main")
    if r.returncode:
        print("local_job: push failed: " + (r.stderr or r.stdout).strip()[:200])
        return 1
    print("local_job: sent " + ", ".join(names))
    return 0, names


def on_remote(name):
    return git("cat-file", "-e", f"origin/main:answers/{name}.json").returncode == 0


def wait(names, timeout, every):
    end = time.time() + timeout
    waiting = list(names)
    while True:
        git("fetch", "-q", "origin", "main")
        waiting = [n for n in waiting if not on_remote(n)]
        if not waiting or time.time() >= end:
            break
        time.sleep(min(every, max(1, end - time.time())))
    git("pull", "-q", "--rebase", "--autostash", "origin", "main")
    for n in names:
        p = os.path.join(LANE, "answers", n + ".json")
        if n in waiting or not os.path.exists(p):
            print(f"{n}: none")
            continue
        a = json.load(open(p, encoding="utf-8"))
        print(f"{n}: {a.get('status', 'unknown')} {a.get('seconds', '?')}s {a.get('model', '')}")
    return 2 if waiting else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["send", "wait", "health"])
    ap.add_argument("items", nargs="*")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--every", type=int, default=30)
    a = ap.parse_args()
    if a.cmd == "health":
        git("pull", "-q", "--rebase", "--autostash")
        print(open(os.path.join(LANE, "status", "health.json"), encoding="utf-8").read().strip())
        print("stop local: " + ("ON" if stopped() else "off"))
        return 0
    if a.cmd == "send":
        r = send(a.items)
        if isinstance(r, int):
            return r
        return wait(r[1], a.timeout, a.every) if a.wait else 0
    return wait(a.items, a.timeout, a.every)


if __name__ == "__main__":
    sys.exit(main())
