#!/usr/bin/env python3
"""Send text jobs to the GEEKOM local model server and wait for the answers, in one command.

    python3 tools/local_job.py send <job.json> [<job.json> ...] [--wait] [--timeout 900] [--every 30]
    python3 tools/local_job.py wait <name> [<name> ...] [--timeout 900] [--every 30]
    python3 tools/local_job.py fetch <job.json> [...] [--wait]   (job has urls instead of input: the box reads the pages)
    python3 tools/local_job.py health
    python3 tools/local_job.py night [--days 1]   (the night shift's jobs and their answers: video/studio/_shared/nightshift.md)

The lane is the private repo proofnotfluff-a11y/pnf-local-jobs, cloned at $PNF_LOCAL_JOBS (default
/home/claude/pnf-local-jobs). A job file is named <slug>-<kind>-<date>-r<round>.json and holds kind, model (workhorse,
fast or trial), prompt, input, schema (required) and optional system, max_tokens, think, checks. `send` copies each file into
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
TRIAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_trial.json")
PERSON = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")


def git(*args):
    return subprocess.run(["git", *args], cwd=LANE, capture_output=True, text=True)


def stopped():
    return os.path.exists(os.path.join(LANE, "control", "stop"))


def problems(job, name):
    out = []
    if not NAME.match(name):
        out.append(f"name {name!r} is not <slug>-<kind>-<date>-r<round>")
    for k in ("kind", "model", "prompt", "urls" if "urls" in job else "input", "schema"):
        if k not in job:
            out.append(f"missing {k}")
    if "urls" in job and not (isinstance(job["urls"], list) and 1 <= len(job["urls"]) <= 8
                              and all(str(u).startswith("https://") for u in job["urls"])):
        out.append("urls must be 1 to 8 https pages")
    if job.get("model") not in ("workhorse", "fast", "trial"):
        out.append("model must be workhorse, fast or trial")
    blob = json.dumps(job)
    if PERSON.search(blob):
        out.append("an email address or phone number is in the job: the lane carries business fields only")
    return out


def trial_model():
    """A model on trial (tools/local_trial.json, until a date): every job also goes to it as a twin named trial-<name>,
    so each shadow job compares the day-one model, the trial model and Claude on the same input (Todd, Nov 6, 2026)."""
    if not os.path.exists(TRIAL):
        return None
    t = json.load(open(TRIAL, encoding="utf-8"))
    return t.get("model") if time.strftime("%Y-%m-%d") <= t.get("until", "") else None


def send(paths, folder="jobs"):
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
        if (folder == "fetch") != ("urls" in job):
            print(f"local_job: {name} refused: a job with urls goes through fetch, one with input through send")
            return 1
        dst = os.path.join(LANE, folder, name + ".json")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        if os.path.exists(dst) or os.path.exists(os.path.join(LANE, "answers", name + ".json")):
            print(f"local_job: {name} already sent (a new round is a new name)")
            return 1
        shutil.copyfile(p, dst)
        git("add", dst)
        names.append(name)
        tm = trial_model()
        if tm and job["model"] != tm and not name.startswith("trial-"):
            twin = os.path.join(LANE, folder, "trial-" + name + ".json")
            if not os.path.exists(twin):
                json.dump(dict(job, model=tm), open(twin, "w", encoding="utf-8"), indent=1)
                git("add", twin)
                names.append("trial-" + name)
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


def night(days):
    """The night shift (Todd, live chat, Nov 6, 2026, 10:16 pm: "Yes do it"): every job named <slug>-night-<kind>-<date>-r<n>
    from the last `days` days, with its answer's status. Exit 0; a missing answer prints "none" and is not waited for."""
    import datetime as dt
    git("pull", "-q", "--rebase", "--autostash")
    today = dt.date.today()
    keep = {(today - dt.timedelta(d)).isoformat() for d in range(days + 1)}
    rows = []
    for folder in ("jobs", "fetch"):
        d = os.path.join(LANE, folder)
        for f in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            n = f[:-5]
            m = re.search(r"-night-[a-z-]+-(\d{4}-\d{2}-\d{2})-r\d+$", n)
            if not f.endswith(".json") or not m or m.group(1) not in keep:
                continue
            a = os.path.join(LANE, "answers", f)
            st = json.load(open(a, encoding="utf-8")).get("status", "unknown") if os.path.exists(a) else "none"
            rows.append(f"{n}: {st}")
    print("\n".join(rows) if rows else "night: no night jobs in the last %d day(s)" % days)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["send", "fetch", "wait", "health", "night"])
    ap.add_argument("items", nargs="*")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--every", type=int, default=30)
    ap.add_argument("--days", type=int, default=1)
    a = ap.parse_args()
    if a.cmd == "night":
        return night(a.days)
    if a.cmd == "health":
        git("pull", "-q", "--rebase", "--autostash")
        print(open(os.path.join(LANE, "status", "health.json"), encoding="utf-8").read().strip())
        print("stop local: " + ("ON" if stopped() else "off"))
        return 0
    if a.cmd in ("send", "fetch"):
        r = send(a.items, "jobs" if a.cmd == "send" else "fetch")
        if isinstance(r, int):
            return r
        return wait(r[1], a.timeout, a.every) if a.wait else 0
    return wait(a.items, a.timeout, a.every)


if __name__ == "__main__":
    sys.exit(main())
