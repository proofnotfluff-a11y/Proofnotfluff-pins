#!/usr/bin/env python3
"""Crew map (Todd, Nov 8, 2026): flag crew jobs that go quiet, the failure a "succeeded" run can hide.

Two kinds of job, one line each, "OK|QUIET|FAIL|PAUSED|UNKNOWN <kind> <name>: <detail>":
  workflow  every scheduled GitHub workflow, found from its own cron lines (none to list by hand): FAIL when its newest
            finished run failed, QUIET when its last success is older than 1.5 x its longest gap between runs + 6 h
  task      each scheduled task in coo/CREW_MAP.json: QUIET when no commit touched its proof paths within 1.5 x
            everyHours; PAUSED when --runs is given and no enabled task name contains its "task" text
Reading only: GitHub's run history through gh, and git history (a shallow clone is deepened with --fetch).

Usage: python3 tools/crew_map.py [--runs data/cos/runs.json] [--fetch] [--out data/cos/crew_map.json]
       python3 tools/crew_map.py --selftest
"""
import argparse, datetime as dt, glob, json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "coo", "CREW_MAP.json")
UTC = dt.timezone.utc


def field(text, lo, hi):
    out = set()
    for part in text.split(","):
        rng, _, step = part.partition("/")
        a, b = (lo, hi) if rng == "*" else (int(rng.split("-")[0]), int(rng.split("-")[-1]))
        out.update(range(a, b + 1, int(step or 1)))
    return out


def max_gap_hours(crons, start=dt.datetime(2026, 1, 1, tzinfo=UTC), days=730):
    """Longest gap between two fires of one or more 5-field crons (UTC), over two years."""
    fires = set()
    for cron in ([crons] if isinstance(crons, str) else crons):
        m, h, dom, mon, dow = re.sub(r"^CRON_TZ=\S+\s+", "", cron.strip()).split()[:5]
        M, H, D, MO = field(m, 0, 59), field(h, 0, 23), field(dom, 1, 31), field(mon, 1, 12)
        W = {d % 7 for d in field(dow, 0, 7)}
        for i in range(days):
            day = start + dt.timedelta(days=i)
            d_ok, w_ok = day.day in D, (day.isoweekday() % 7) in W
            hit = (d_ok or w_ok) if dom != "*" and dow != "*" else (d_ok and w_ok)
            if day.month in MO and hit:
                fires.update(day.replace(hour=hh, minute=mm) for hh in H for mm in M)
    fires = sorted(fires)
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(fires, fires[1:])]
    return max(gaps) if gaps else None


def workflow_crons(path):
    crons, in_sched = [], False
    for line in open(path, encoding="utf-8"):
        s = line.split("#", 1)[0].rstrip()
        if re.match(r"\s*schedule:", s):
            in_sched = True; continue
        m = re.search(r"cron:\s*['\"]([^'\"]+)['\"]", s)
        if in_sched and m:
            crons.append(m.group(1))
        elif in_sched and s.strip() and not s.strip().startswith("-") and not m:
            in_sched = False
    return crons


def judge_workflow(name, gap, runs, now):
    """runs: newest first, dicts with status, conclusion, created_at."""
    done = [r for r in runs if r.get("status") == "completed"]
    if done and done[0].get("conclusion") not in ("success", "skipped", "cancelled", "neutral"):
        return "FAIL", f"newest run {done[0].get('conclusion')} on {done[0]['created_at'][:10]}"
    ok = [r for r in done if r.get("conclusion") == "success"]
    limit = dt.timedelta(hours=gap * 1.5 + 6)
    if not ok:
        return "QUIET", "no successful run in the last 20"
    last = dt.datetime.fromisoformat(ok[0]["created_at"].replace("Z", "+00:00"))
    return ("QUIET" if now - last > limit else "OK"), f"last success {last:%b %d %H:%M} UTC, runs every {gap:g} h at most"


def judge_task(entry, last, now, runs):
    if runs is not None:
        named = [t for t in runs if entry["task"].lower() in str(t.get("name", "")).lower()]
        if not named:
            return "UNKNOWN", f"no scheduled task name contains \"{entry['task']}\"; fix coo/CREW_MAP.json"
        if not any(t.get("enabled", True) for t in named):
            return "PAUSED", "its scheduled task is paused"
    if last is None:
        return "QUIET", f"no commit to {', '.join(entry['proof'])} in history"
    limit = dt.timedelta(hours=entry["everyHours"] * 1.5)
    return ("QUIET" if now - last > limit else "OK"), f"last proof {last:%b %d %H:%M} UTC, expected every {entry['everyHours']} h"


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True)


def last_commit(paths):
    out = git("log", "-1", "--format=%cI", "--", *paths).stdout.strip()
    return dt.datetime.fromisoformat(out) if out else None


def repo_slug():
    url = git("remote", "get-url", "origin").stdout.strip()
    m = re.search(r"github\.com[/:]([^/]+/[^/.]+)", url)
    return m.group(1) if m else None


def run(args, now):
    items, cmap = [], json.load(open(MAP, encoding="utf-8"))
    runs = json.load(open(args.runs, encoding="utf-8")).get("tasks") if args.runs and os.path.exists(args.runs) else None
    slug = repo_slug()
    for path in sorted(glob.glob(os.path.join(ROOT, ".github", "workflows", "*.y*ml"))):
        crons = workflow_crons(path)
        name = os.path.basename(path)
        if not crons or name in cmap.get("skipWorkflows", []):
            continue
        gap = max_gap_hours(crons)
        r = subprocess.run(["gh", "api", f"repos/{slug}/actions/workflows/{name}/runs?per_page=20"], capture_output=True, text=True)
        if r.returncode:
            items.append(("UNKNOWN", "workflow", name, "run history unreadable: " + (r.stderr.strip().splitlines() or ["gh failed"])[-1][:80]))
            continue
        st, detail = judge_workflow(name, gap, json.loads(r.stdout).get("workflow_runs", []), now)
        items.append((st, "workflow", name, detail))
    shallow = git("rev-parse", "--is-shallow-repository").stdout.strip() == "true"
    if shallow and args.fetch:
        days = max(e["everyHours"] for e in cmap["tasks"]) * 2 // 24 + 2
        git("fetch", "-q", f"--shallow-since={(now - dt.timedelta(days=days)):%Y-%m-%d}", "origin", "main")
        shallow = False
    for e in cmap["tasks"]:
        if shallow:
            items.append(("UNKNOWN", "task", e["task"], "shallow clone: rerun with --fetch")); continue
        st, detail = judge_task(e, last_commit(e["proof"]), now, runs)
        items.append((st, "task", e["task"], detail))
    return items


def selftest():
    fails = []
    def expect(label, got, want):
        if got != want:
            fails.append(f"{label}: got {got}, want {want}")
    expect("daily cron gap", max_gap_hours("10 12 * * *"), 24.0)
    expect("weekly cron gap", max_gap_hours("10 13 * * 1"), 168.0)
    expect("four a day gap", max_gap_hours("CRON_TZ=America/Chicago 33 9,12,17,21 * * *"), 12.0)
    expect("weekday gap", max_gap_hours("10 15 * * 1-5"), 72.0)
    expect("every 6 h gap", max_gap_hours("7 */6 * * *"), 6.0)
    now = dt.datetime(2026, 11, 8, 12, tzinfo=UTC)
    ok_run = [{"status": "completed", "conclusion": "success", "created_at": "2026-11-08T05:00:00Z"}]
    old_run = [{"status": "completed", "conclusion": "success", "created_at": "2026-11-05T05:00:00Z"}]
    bad_run = [{"status": "completed", "conclusion": "failure", "created_at": "2026-11-08T05:00:00Z"}] + ok_run
    expect("fresh daily workflow", judge_workflow("w", 24, ok_run, now)[0], "OK")
    expect("daily workflow quiet 3 days", judge_workflow("w", 24, old_run, now)[0], "QUIET")
    expect("newest run failed", judge_workflow("w", 24, bad_run, now)[0], "FAIL")
    expect("never succeeded", judge_workflow("w", 24, [], now)[0], "QUIET")
    e = {"task": "PNF video studio", "proof": ["video/studio/"], "everyHours": 24}
    expect("task with fresh proof", judge_task(e, now - dt.timedelta(hours=20), now, None)[0], "OK")
    expect("task succeeded but no output for 2 days", judge_task(e, now - dt.timedelta(hours=48), now, None)[0], "QUIET")
    expect("paused task", judge_task(e, None, now, [{"name": "PNF video studio: record", "enabled": False}])[0], "PAUSED")
    expect("enabled task, no proof ever", judge_task(e, None, now, [{"name": "PNF video studio: record", "enabled": True}])[0], "QUIET")
    expect("two crons merged", max_gap_hours(["0 12 * * 1", "0 12 * * 4"]), 96.0)
    expect("map name matches no task", judge_task(e, None, now, [{"name": "PNF radar", "enabled": True}])[0], "UNKNOWN")
    expect("commented cron skipped", workflow_crons_text("on:\n  # schedule:\n  #   - cron: '1 1 * * *'\n  workflow_dispatch:\n"), [])
    for f in fails:
        print("FAIL", f)
    print(f"crew_map selftest: {17 - len(fails)} of 17 right")
    return 1 if fails else 0


def workflow_crons_text(text):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(text)
    try:
        return workflow_crons(f.name)
    finally:
        os.unlink(f.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs"); ap.add_argument("--out"); ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    now = dt.datetime.now(UTC)
    items = run(a, now)
    for st, kind, name, detail in items:
        print(f"{st} {kind} {name}: {detail}")
    flagged = [f"{n} ({st.lower()})" for st, k, n, d in items if st in ("QUIET", "FAIL")]
    count = lambda s: sum(1 for i in items if i[0] == s)
    print(f"crew_map: {len(items)} watched, {count('OK')} ok, {count('QUIET')} quiet, {count('FAIL')} failed, "
          f"{count('PAUSED')} paused, {count('UNKNOWN')} unknown")
    if a.out:
        os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
        json.dump({"checkedAt": now.isoformat(), "flagged": flagged, "unknown": count("UNKNOWN"),
                   "items": [dict(zip(("status", "kind", "name", "detail"), i)) for i in items]}, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
