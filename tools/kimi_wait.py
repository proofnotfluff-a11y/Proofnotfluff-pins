#!/usr/bin/env python3
"""Wait for Kimi answers in one command instead of one tool call per minute (usage audit, Oct 30, 2026).

    python3 tools/kimi_wait.py <job name> [<job name> ...] [--timeout 900] [--every 30]

Checks origin/main every --every seconds (git fetch only, so local work is never touched) until every
kimi/answers/<name>.json exists there or --timeout seconds pass. Then it pulls once (git pull --rebase --autostash)
so the answers are on disk, and prints one line per job: "<name>: <status>" or "<name>: none". Exit 0 when every
answer came back (whatever its status), 2 on timeout. Run it with a tool timeout a little over --timeout.
Same rule as the kimi-jobs SKILL: no answer or a status other than ok means do that work on Claude.
"""
import argparse, json, os, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def on_remote(name):
    return git("cat-file", "-e", f"origin/main:kimi/answers/{name}.json").returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="+")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--every", type=int, default=30)
    a = ap.parse_args()
    end = time.time() + a.timeout
    waiting = list(a.names)
    while True:
        git("fetch", "-q", "origin", "main")
        waiting = [n for n in waiting if not on_remote(n)]
        if not waiting or time.time() >= end:
            break
        time.sleep(min(a.every, max(1, end - time.time())))
    if len(waiting) < len(a.names):
        r = git("pull", "-q", "--rebase", "--autostash", "origin", "main")
        if r.returncode:
            print("kimi_wait: git pull failed: " + (r.stderr or r.stdout).strip()[:200])
    for n in a.names:
        p = os.path.join(ROOT, "kimi", "answers", f"{n}.json")
        if n in waiting or not os.path.exists(p):
            print(f"{n}: none")
            continue
        try:
            print(f"{n}: {json.load(open(p, encoding='utf-8')).get('status', 'unknown')}")
        except Exception as e:
            print(f"{n}: bad_file ({type(e).__name__})")
    return 2 if waiting else 0


if __name__ == "__main__":
    sys.exit(main())
