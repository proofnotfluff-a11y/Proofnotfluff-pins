#!/usr/bin/env python3
"""The video engine's ledger: video/LEDGER.md. One run at a time (the lock), one state change per write, and every write
names the state it replaces, so a run never guesses where a video stands (blueprint, Publishing operations).

The file has three parts, all written only by this tool:
  ## Lock      "lock: none" or "lock: <run id> <ISO start>"; a lock older than 2 hours is cleared and noted
  ## Rows      one JSON object per line (schema pnf.video.ledger_row.v1), newest last; a video's state is its last row
  ## Touches   one line per touch by Todd ("post" or a fix note), with its time: the MVP's effort test reads these

States and the moves allowed between them (anything else is refused):
  planned -> drafted -> gated -> rendering -> rendered -> qa_passed -> reviewed -> preview_sent -> approved -> posting
  -> published; a fix round goes back one stage (drafted or rendering) and bumps "round"; "failed" ends an attempt and
  its slot takes the next candidate as a new video id ("replaced" records the link). "posting" is written before the
  post and "published" with the link after it; a run that finds "posting" checks the account before anything else, then
  writes "published" (the post exists) or "approved" (it does not).

Usage
  video_ledger.py lock --run ID [--now ISO]            exit 3: a live lock (wait for the next slot)
  video_ledger.py unlock --run ID
  video_ledger.py state --video ID                     prints the current state (or "none")
  video_ledger.py set --video ID --from STATE --to STATE [--run ID] [--spec F] [--mp4 F] [--caption-file F]
        [--post-url U] [--story-type T --area N] [--note TEXT] [--round N]
  video_ledger.py touch --video ID --what TEXT [--at ISO]   Todd's "post" or fix note (counts toward the effort test)
  video_ledger.py bound --video ID --spec F --mp4 F --caption-file F   exit 1 unless all three match the approved row
  video_ledger.py check [--file F]                     schema and transitions of every row
  video_ledger.py --selftest
"""
import argparse, datetime as dt, hashlib, json, os, re, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LEDGER = os.path.join(ROOT, "video", "LEDGER.md")
LOCK_MAX_H = 2
STATES = ["planned", "drafted", "gated", "rendering", "rendered", "qa_passed", "reviewed", "preview_sent", "approved",
          "posting", "published", "flagged", "failed", "replaced"]
MOVES = {
    None: {"planned"},
    "planned": {"drafted", "failed"},
    "drafted": {"gated", "drafted", "failed"},
    "gated": {"rendering", "drafted", "failed"},
    "rendering": {"rendered", "rendering", "failed"},
    "rendered": {"qa_passed", "rendering", "failed"},
    "qa_passed": {"reviewed", "rendering", "drafted", "failed"},
    "reviewed": {"preview_sent", "drafted", "rendering", "failed"},
    "preview_sent": {"approved", "drafted", "rendering", "failed"},
    "approved": {"posting", "drafted", "rendering", "failed"},
    "posting": {"published", "approved"},
    "published": {"flagged"},
    "flagged": set(),
    "failed": {"replaced"},
    "replaced": set(),
}
HEADER = """# Video engine ledger (Phase 0, the Rat check MVP)

Written only by tools/video_ledger.py (blueprint: Publishing operations). The lock keeps one run at a time; every row
names the state it replaces; "posting" is written before a post and "published" with its link after it. Fingerprints
bind Todd's "post" to the exact spec, MP4 and caption he saw. Touches are his words with their times (the MVP's
effort test: at most one per video after setup). Read: `python3 tools/video_ledger.py state --video <id>`.
"""
ZERO = "0" * 64


class LedgerError(Exception):
    pass


def now_iso(now=None):
    t = now or dt.datetime.now(dt.timezone(dt.timedelta(hours=-5)))
    return t.isoformat(timespec="seconds")


def parse_time(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))


def sha_file(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read(path=LEDGER):
    if not os.path.exists(path):
        return {"lock": None, "rows": [], "touches": [], "raw": ""}
    raw = open(path, encoding="utf-8").read()
    lock, rows, touches, part = None, [], [], None
    for line in raw.splitlines():
        if line.startswith("## "):
            part = line[3:].strip().lower()
            continue
        if part == "lock" and line.startswith("lock:"):
            v = line[5:].strip()
            if v != "none":
                rid, at = v.split()
                lock = {"run": rid, "at": at}
        elif part == "rows" and line.startswith("{"):
            rows.append(json.loads(line))
        elif part == "touches" and line.startswith("- "):
            touches.append(line[2:])
    return {"lock": lock, "rows": rows, "touches": touches, "raw": raw}


def render(state):
    lock = "lock: none" if not state["lock"] else f"lock: {state['lock']['run']} {state['lock']['at']}"
    rows = "\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in state["rows"])
    touches = "\n".join(f"- {t}" for t in state["touches"])
    return f"{HEADER}\n## Lock\n{lock}\n\n## Rows\n{rows}\n\n## Touches\n{touches}\n".replace("\n\n\n", "\n\n")


def write(state, path, expect_raw):
    """Write only if nobody changed the file since it was read (else the run stops: the ledger moved underneath it)."""
    cur = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
    if cur != expect_raw:
        raise LedgerError("the ledger changed since this run read it; stop and re-read (never overwrite)")
    tmp = path + ".tmp"
    open(tmp, "w", encoding="utf-8").write(render(state))
    os.replace(tmp, path)


def current(rows, video):
    last = None
    for r in rows:
        if r["videoId"] == video:
            last = r
    return last


def lock(path, run, now=None):
    st = read(path)
    t = now or dt.datetime.now(dt.timezone.utc)
    note = None
    if st["lock"]:
        age_h = (t - parse_time(st["lock"]["at"])).total_seconds() / 3600
        if st["lock"]["run"] == run:
            return "held"
        if age_h < LOCK_MAX_H:
            raise LedgerError(f"live lock by {st['lock']['run']} since {st['lock']['at']}: wait for the next slot")
        note = f"{now_iso(t)} cleared a stale lock by {st['lock']['run']} from {st['lock']['at']} ({age_h:.1f} h old)"
        st["touches"].append(f"{note} (system, not a touch by Todd)")
    st["lock"] = {"run": run, "at": now_iso(t)}
    write(st, path, st["raw"])
    return note or "locked"


def unlock(path, run):
    st = read(path)
    if not st["lock"]:
        return "none"
    if st["lock"]["run"] != run:
        raise LedgerError(f"the lock belongs to {st['lock']['run']}, not {run}")
    st["lock"] = None
    write(st, path, st["raw"])
    return "unlocked"


def set_state(path, video, frm, to, run=None, spec=None, mp4=None, caption=None, post_url=None, story_type=None, area=None,
              note=None, round_=None, now=None):
    st = read(path)
    if st["lock"] and run and st["lock"]["run"] != run:
        raise LedgerError(f"the lock belongs to {st['lock']['run']}")
    last = current(st["rows"], video)
    have = last["state"] if last else None
    want = None if frm in (None, "none") else frm
    if have != want:
        raise LedgerError(f"{video} is {have or 'none'}, not {frm}: the ledger moved underneath this run; stop")
    if to not in MOVES.get(have, set()):
        raise LedgerError(f"{video}: {have or 'none'} -> {to} is not an allowed move")
    row = {"schema": "pnf.video.ledger_row.v1", "videoId": video, "state": to, "prev": have, "at": now_iso(now),
           "specSha256": sha_file(spec) if spec else (last or {}).get("specSha256", ZERO),
           "mp4Sha256": sha_file(mp4) if mp4 else (last or {}).get("mp4Sha256", ZERO),
           "captionSha256": sha_text(caption) if caption is not None else (last or {}).get("captionSha256", ZERO),
           "postUrl": post_url or (last or {}).get("postUrl"),
           "touches": sum(1 for t in st["touches"] if f" {video} " in f" {t} " and "(system" not in t),
           "round": round_ if round_ is not None else (last or {}).get("round", 0)}
    for k in ("storyType", "area"):
        if last and k in last:
            row[k] = last[k]
    if story_type:
        row["storyType"] = story_type
    if area is not None:
        row["area"] = int(area)
    if run:
        row["run"] = run
    if note:
        row["note"] = note
    if to == "published" and not row["postUrl"]:
        raise LedgerError("published needs the post link")
    if to == "posting":
        dup = [r for r in st["rows"] if r["state"] == "published" and r["captionSha256"] == row["captionSha256"]]
        if dup:
            raise LedgerError(f"caption fingerprint already published as {dup[0]['videoId']}: refuse (no double posts)")
    st["rows"].append(row)
    write(st, path, st["raw"])
    return row


def touch(path, video, what, at=None):
    st = read(path)
    if "\n" in what:
        raise LedgerError("one line per touch")
    st["touches"].append(f"{at or now_iso()} {video} {what}")
    write(st, path, st["raw"])


def bound(path, video, spec, mp4, caption):
    """Todd's yes is bound to the exact files: all three fingerprints must match the approved row."""
    st = read(path)
    rows = [r for r in st["rows"] if r["videoId"] == video and r["state"] == "approved"]
    if not rows:
        return [f"{video}: no approved row"]
    r = rows[-1]
    out = []
    for name, got, want in (("spec", sha_file(spec), r["specSha256"]), ("mp4", sha_file(mp4), r["mp4Sha256"]),
                            ("caption", sha_text(caption), r["captionSha256"])):
        if got != want:
            out.append(f"{video}: the {name} changed after Todd's yes ({got[:12]} vs {want[:12]}); it needs a new yes")
    return out


def check(path=LEDGER):
    """Every row parses, carries the required keys, and every state follows from the one before it."""
    st = read(path)
    out, last = [], {}
    need = ["videoId", "state", "at", "specSha256", "mp4Sha256", "captionSha256", "postUrl", "touches"]
    for i, r in enumerate(st["rows"], 1):
        miss = [k for k in need if k not in r]
        if miss:
            out.append(f"row {i}: missing {miss}")
            continue
        if r.get("schema") != "pnf.video.ledger_row.v1":
            out.append(f"row {i}: schema {r.get('schema')!r}")
        if r["state"] not in STATES:
            out.append(f"row {i}: unknown state {r['state']!r}")
        prev = last.get(r["videoId"])
        if r.get("prev") != prev:
            out.append(f"row {i}: {r['videoId']} names prev {r.get('prev')!r} but the ledger had {prev!r}")
        if r["state"] not in MOVES.get(prev, set()):
            out.append(f"row {i}: {r['videoId']} {prev} -> {r['state']} is not allowed")
        for k in ("specSha256", "mp4Sha256", "captionSha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", str(r[k])):
                out.append(f"row {i}: {k} is not a sha256")
        last[r["videoId"]] = r["state"]
    if st["lock"]:
        try:
            parse_time(st["lock"]["at"])
        except ValueError:
            out.append("lock time does not parse")
    for t in st["touches"]:
        if not re.match(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", t):
            out.append(f"touch without a time: {t[:60]}")
    return out


def selftest():
    bad = []
    d = tempfile.mkdtemp()
    p = os.path.join(d, "LEDGER.md")
    open(p, "w").write(render({"lock": None, "rows": [], "touches": []}))
    t0 = dt.datetime(2026, 11, 2, 7, 0, tzinfo=dt.timezone(dt.timedelta(hours=-6)))

    def must_fail(name, fn):
        try:
            fn()
            bad.append(f"{name}: not refused")
        except LedgerError:
            pass

    lock(p, "run-1", t0)
    must_fail("a second run waits on a live lock", lambda: lock(p, "run-2", t0 + dt.timedelta(minutes=30)))
    lock(p, "run-2", t0 + dt.timedelta(hours=3))
    if read(p)["lock"]["run"] != "run-2":
        bad.append("a lock older than 2 hours is cleared and taken")
    f = os.path.join(d, "spec.json"); open(f, "w").write("{}")
    m = os.path.join(d, "v.mp4"); open(m, "wb").write(b"mp4")
    set_state(p, "2026-11-02-rats-a", "none", "planned", run="run-2", story_type="A", area=46)
    must_fail("a write naming the wrong prior state", lambda: set_state(p, "2026-11-02-rats-a", "drafted", "gated", run="run-2"))
    must_fail("a move that skips stages", lambda: set_state(p, "2026-11-02-rats-a", "planned", "published", run="run-2", post_url="x"))
    must_fail("another run's write while locked", lambda: set_state(p, "2026-11-02-rats-a", "planned", "drafted", run="run-9"))
    for a, b in (("planned", "drafted"), ("drafted", "gated"), ("gated", "rendering"), ("rendering", "rendered"),
                 ("rendered", "qa_passed"), ("qa_passed", "reviewed"), ("reviewed", "preview_sent"), ("preview_sent", "approved")):
        set_state(p, "2026-11-02-rats-a", a, b, run="run-2", spec=f, mp4=m, caption="caption one")
    touch(p, "2026-11-02-rats-a", '"post"', at="2026-11-02T07:31:00-06:00")
    if bound(p, "2026-11-02-rats-a", f, m, "caption one"):
        bad.append("unchanged files match the approved row")
    open(m, "wb").write(b"mp4 changed")
    if not bound(p, "2026-11-02-rats-a", f, m, "caption one"):
        bad.append("an MP4 changed after the yes is caught")
    open(m, "wb").write(b"mp4")
    set_state(p, "2026-11-02-rats-a", "approved", "posting", run="run-2")
    must_fail("published without a link", lambda: set_state(p, "2026-11-02-rats-a", "posting", "published", run="run-2"))
    row = set_state(p, "2026-11-02-rats-a", "posting", "published", run="run-2", post_url="https://www.instagram.com/reel/x/")
    if row["touches"] != 1:
        bad.append(f"the touch is counted ({row['touches']})")
    set_state(p, "2026-11-04-rats-a", "none", "planned", run="run-2")
    for a, b in (("planned", "drafted"), ("drafted", "gated"), ("gated", "rendering"), ("rendering", "rendered"),
                 ("rendered", "qa_passed"), ("qa_passed", "reviewed"), ("reviewed", "preview_sent"), ("preview_sent", "approved")):
        set_state(p, "2026-11-04-rats-a", a, b, run="run-2", spec=f, mp4=m, caption="caption one")
    must_fail("a caption already published is refused", lambda: set_state(p, "2026-11-04-rats-a", "approved", "posting", run="run-2"))
    if check(p):
        bad.append(f"a clean ledger checks clean: {check(p)}")
    raw = open(p).read()
    open(p, "w").write(raw.replace('"prev": "rendered"', '"prev": "gated"', 1))
    if not check(p):
        bad.append("a tampered row is caught")
    open(p, "w").write(raw)
    st = read(p)
    open(p, "a").write("\n")
    must_fail("a write after someone else changed the file", lambda: write(st, p, st["raw"]))
    unlock(p, "run-2")
    for b in bad:
        print("FAIL", b)
    print(f"video_ledger selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (lock, stale lock, states, wrong prior state, "
          "skipped stage, other run, fingerprints bound to the yes, no post link, duplicate caption, tampering, concurrent write)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["lock", "unlock", "state", "set", "touch", "bound", "check"])
    ap.add_argument("--file", default=LEDGER)
    ap.add_argument("--run"); ap.add_argument("--video"); ap.add_argument("--from", dest="frm"); ap.add_argument("--to")
    ap.add_argument("--spec"); ap.add_argument("--mp4"); ap.add_argument("--caption-file"); ap.add_argument("--post-url")
    ap.add_argument("--story-type"); ap.add_argument("--area"); ap.add_argument("--note"); ap.add_argument("--round", type=int)
    ap.add_argument("--what"); ap.add_argument("--at"); ap.add_argument("--now")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    cap = open(a.caption_file, encoding="utf-8").read() if a.caption_file else None
    try:
        if a.cmd == "lock":
            print(lock(a.file, a.run, parse_time(a.now) if a.now else None))
        elif a.cmd == "unlock":
            print(unlock(a.file, a.run))
        elif a.cmd == "state":
            r = current(read(a.file)["rows"], a.video)
            print(r["state"] if r else "none")
        elif a.cmd == "set":
            r = set_state(a.file, a.video, a.frm, a.to, a.run, a.spec, a.mp4, cap, a.post_url, a.story_type, a.area, a.note, a.round)
            print(f"{r['videoId']}: {r['prev'] or 'none'} -> {r['state']}")
        elif a.cmd == "touch":
            touch(a.file, a.video, a.what, a.at)
            print("touch logged")
        elif a.cmd == "bound":
            p = bound(a.file, a.video, a.spec, a.mp4, cap or "")
            for x in p:
                print("ERROR", x)
            print("bound: " + ("PASS, spec, MP4 and caption match the yes" if not p else "FAIL"))
            sys.exit(1 if p else 0)
        elif a.cmd == "check":
            p = check(a.file)
            for x in p:
                print("ERROR", x)
            print(f"ledger: {'ok' if not p else str(len(p)) + ' problems'}")
            sys.exit(1 if p else 0)
        else:
            ap.print_help()
    except LedgerError as e:
        print(f"ERROR ledger: {e}")
        sys.exit(3 if "live lock" in str(e) else 1)


if __name__ == "__main__":
    main()
