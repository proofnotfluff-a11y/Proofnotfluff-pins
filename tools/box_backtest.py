#!/usr/bin/env python3
"""Backtest the local box against Opus's saved story-gate verdicts (Todd, live chat, Nov 7, 2026, 5:22 am: "Yes and to
all your recommendations ... I want to be clear that the box is our work horse and we should be heavily utilizing it").

Why: the box earns a rung only after 3 clean live jobs in a row (video/studio/_shared/local.md), which takes weeks. Opus
has already judged 20+ script rounds; replaying those exact words to the box, several times each, measures in a night how
often the box agrees with Opus and how steady it is. Pure code scores it; no Claude is needed to check.

  python3 tools/box_backtest.py make [--samples 3] [--date YYYY-MM-DD]   write replay jobs to <scratch>/backtest/, then
                                                                        python3 tools/local_job.py send <scratch>/backtest/*.json
  python3 tools/box_backtest.py score                                   agreement table; writes video/studio/research/box-backtest.json

Pairs: a story.json round N whose words are known exactly: the box's own pre-check job for round N carries them, and the
verdict either names "rN words" or has no "on" (the r12 to r24 labels were script versions). A verdict judged on other
words (round 25 judged r24 words) is left out, never guessed. Numbers only are written to the repo.
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS = os.path.join(ROOT, "video", "studio", "videos")
LANE = os.environ.get("PNF_LOCAL_JOBS", "/home/claude/pnf-local-jobs")
OUT = os.path.join(ROOT, "video", "studio", "research", "box-backtest.json")
KINDS = ("retell", "read-aloud")
NONE = {"", "none", "no", "nowhere", "n/a", "nothing"}


def short(slug):
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", slug).split("-")[0]


def verdicts(slug):
    """{round: {"retell": bool, "read-aloud": bool}} for rounds judged on known words."""
    f = os.path.join(VIDEOS, slug, "05_render", "reviews", "story.json")
    out, d = {}, json.load(open(f)) if os.path.exists(f) else None
    while isinstance(d, dict):
        m = re.fullmatch(r"r?(\d+)", str(d.get("round", "")))
        on = str(d.get("on") or "")
        parts = d.get("parts") if isinstance(d.get("parts"), dict) else {}
        if m and not d.get("carried") and (not on or re.search(r"\br%s words" % m.group(1), on)):
            n = int(m.group(1))
            v = {}
            for k, key in (("retell", "retell"), ("read-aloud", "read_aloud")):
                p = parts.get(key)
                if isinstance(p, dict) and isinstance(p.get("pass"), bool):
                    v[k] = p["pass"]
            if v and n not in out:
                out[n] = v
        d = d.get("earlier")
    return out


def source_jobs(slug):
    """{(kind, round): job} from the box's own live pre-checks (the exact words Opus judged)."""
    out = {}
    for f in glob.glob(os.path.join(LANE, "jobs", f"{slug}-*.json")):
        m = re.search(r"-(retell|read-aloud)-\d{4}-\d{2}-\d{2}-r(\d+)\.json$", f)
        if m and "-night-" not in f:
            out[(m.group(1), int(m.group(2)))] = json.load(open(f, encoding="utf-8"))
    return out


def pairs():
    rows = []
    for slug in sorted(os.listdir(VIDEOS)):
        v, src = verdicts(slug), source_jobs(slug)
        for (kind, n), job in sorted(src.items()):
            if n in v and kind in v[n]:
                rows.append((slug, kind, n, job, v[n][kind]))
    return rows


def make(samples, date, outdir):
    os.makedirs(outdir, exist_ok=True)
    for f in glob.glob(os.path.join(outdir, "*.json")):
        os.remove(f)
    n = 0
    for slug, kind, rnd, job, _ in pairs():
        for s in range(1, samples + 1):
            name = f"bt-{short(slug)}-s{s}-{kind}-{date}-r{rnd}"
            j = dict(job)
            j["model"] = "workhorse"
            json.dump(j, open(os.path.join(outdir, name + ".json"), "w", encoding="utf-8"), indent=1)
            n += 1
    print(f"backtest: {n} replay jobs in {outdir} ({len(pairs())} judged rounds x {samples} samples)")


def box_pass(kind, out):
    if not isinstance(out, dict):
        return None
    if kind == "retell":
        return str(out.get("lost_at", "")).strip().strip(".").lower() in NONE
    return bool(out.get("pass")) if "pass" in out else None


def score():
    want = {(short(s), k, r): (s, p) for s, k, r, _, p in pairs()}
    tally = {}
    for f in glob.glob(os.path.join(LANE, "answers", "*bt-*.json")):
        name = os.path.basename(f)[:-5]
        m = re.fullmatch(r"(trial-)?bt-([a-z0-9]+)-s(\d+)-(retell|read-aloud)-\d{4}-\d{2}-\d{2}-r(\d+)", name)
        if not m:
            continue
        model = "trial" if m.group(1) else "workhorse"
        key = (m.group(2), m.group(4), int(m.group(5)))
        if key not in want:
            continue
        a = json.load(open(f, encoding="utf-8"))
        b = box_pass(m.group(4), a.get("output")) if a.get("status") == "ok" else None
        t = tally.setdefault((model, m.group(4)), {})
        t.setdefault(key, {"opus": want[key][1], "box": []})["box"].append(b)
    report = {"made": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "rule": __doc__.split("\n")[0], "rows": []}
    for (model, kind), rounds in sorted(tally.items()):
        votes = [(r["opus"], b) for r in rounds.values() for b in r["box"] if b is not None]
        steady = [len(set(x for x in r["box"] if x is not None)) == 1 for r in rounds.values() if any(x is not None for x in r["box"])]
        if not votes:
            continue
        agree = sum(o == b for o, b in votes)
        row = {"model": model, "kind": kind, "rounds": len(rounds), "answers": len(votes),
               "agree_pct": round(100 * agree / len(votes), 1),
               "box_pass_opus_fail": sum(1 for o, b in votes if b and not o),
               "box_fail_opus_pass": sum(1 for o, b in votes if o and not b),
               "opus_pass_rounds": sum(1 for r in rounds.values() if r["opus"]),
               "steady_pct": round(100 * sum(steady) / len(steady), 1) if steady else None}
        report["rows"].append(row)
        print(f"{model:9} {kind:10} agree {row['agree_pct']:5}% of {row['answers']} | box PASS where Opus FAIL "
              f"{row['box_pass_opus_fail']} | box FAIL where Opus PASS {row['box_fail_opus_pass']} | same answer every "
              f"sample {row['steady_pct']}% | {row['rounds']} rounds, Opus passed {row['opus_pass_rounds']}")
    if not report["rows"]:
        print("backtest: no scored answers yet")
        return 1
    json.dump(report, open(OUT, "w"), indent=1)
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["make", "score", "pairs"])
    ap.add_argument("--samples", type=int, default=3)
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--out", default=os.path.join(os.environ.get("TMPDIR", "/tmp"), "backtest"))
    a = ap.parse_args()
    if a.cmd == "pairs":
        for s, k, r, _, p in pairs():
            print(s, k, r, "Opus", "PASS" if p else "FAIL")
        return 0
    if a.cmd == "make":
        make(a.samples, a.date, a.out)
        return 0
    return score()


if __name__ == "__main__":
    sys.exit(main())
