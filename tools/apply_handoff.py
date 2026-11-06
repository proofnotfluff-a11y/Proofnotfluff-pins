#!/usr/bin/env python3
"""Apply an index-request hand-off record to seo/ (Todd's go in a live chat, Nov 6, 2026: "ok let's go with one").

The index-request run lives on Todd's PC (it needs the built-in browser for Search Console) and cannot push to
GitHub, so it writes its results into the scoreboard, collection "handoffs", doc "index-request-YYYY-MM-DD".
The daily cloud question-pages run saves each pending record to data/handoff-<date>.json and runs this tool on it.

    python3 tools/apply_handoff.py data/handoff-2026-11-06.json [--check]

Run steps (question-pages step 1a, after its preflight):
  1. ArtifactData query on the scoreboard https://claude.ai/artifact/N9eKZy7Pv39njSe4izVgbE, collection "handoffs",
     where status == "pending", oldest date first.
  2. For each: save it to data/handoff-<date>.json and run this tool on it.
  3. Exit 1: leave the record pending and send Todd its one-line reason.
  4. Exit 0: the seo/ changes go into this run's commit, or their own commit "apply index-request hand-off <date>"
     if no page publishes today (check_repo exits 0, git push origin HEAD:main, pull --rebase once on a reject,
     never force).
  5. After the push succeeds, update the record (if_version from the query): status "applied", applied_on today,
     commit <short hash>. Never mark applied before the push.

Record fields: run "index-request"; date "YYYY-MM-DD"; status "pending" or "applied"; results_lines [lines for
seo/RESULTS.md, each "- YYYY-MM-DD ..."]; search_console {date, window, pages {slug: {impressions, clicks,
position}}} or null; index_requests {url: "YYYY-MM-DD"} (only URLs requested in that run); once applied,
applied_on and commit.

Checks first, all of them, and changes nothing if any fails (exit 1, every problem named on the one summary line):
  run is "index-request"; date is a real YYYY-MM-DD; every results line is one line starting "- " plus a date;
  no em or en dash anywhere in the record; search_console has only date, window and pages, each page only
  impressions, clicks (whole numbers, 0 or more) and position (a number or null), counts only, no queries;
  index_requests keys are proofnotfluff.com URLs in the live list (tools/indexnow_submit.py --all --dry-run).
Then applies:
  results lines are appended to seo/RESULTS.md, skipping any line already there (so a second run adds nothing);
  seo/search-console.json is written only when the record's date is newer than the file's;
  index_requests merge into seo/index-requests.json, keeping the later date per URL.
--check runs the checks and prints what would change, writing nothing.
Prints one summary line. Exit 0 applied (or nothing to add), 1 on any problem.
"""
import datetime as dt
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "seo", "RESULTS.md")
SC_FILE = os.path.join(ROOT, "seo", "search-console.json")
IR_FILE = os.path.join(ROOT, "seo", "index-requests.json")
BASE = "https://proofnotfluff.com/"
KEYS = {"run", "date", "status", "results_lines", "search_console", "index_requests", "applied_on", "commit"}
DASHES = ("\u2012", "\u2013", "\u2014", "\u2015")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LINE_RE = re.compile(r"^- (\d{4}-\d{2}-\d{2})\b")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def real_date(s):
    if not isinstance(s, str) or not DATE_RE.match(s):
        return False
    try:
        dt.date.fromisoformat(s)
        return True
    except ValueError:
        return False


def strings(x, path="record"):
    """Every string in the record, keys included, with where it sits."""
    if isinstance(x, str):
        yield path, x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield f"{path} key", str(k)
            yield from strings(v, f"{path}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x):
            yield from strings(v, f"{path}[{i}]")


def live_urls():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "indexnow_submit.py"), "--all", "--dry-run"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    return {line.split("would send", 1)[1].strip() for line in r.stdout.splitlines() if "would send" in line}


def is_count(v):
    return isinstance(v, int) and not isinstance(v, bool) and v >= 0


def check(rec):
    bad = []
    if not isinstance(rec, dict):
        return ["the record is not a JSON object"]
    extra = set(rec) - KEYS
    if extra:
        bad.append(f"unknown fields: {', '.join(sorted(extra))}")
    if rec.get("run") != "index-request":
        bad.append(f"run is {rec.get('run')!r}, not 'index-request'")
    if not real_date(rec.get("date")):
        bad.append(f"date {rec.get('date')!r} is not YYYY-MM-DD")
    if rec.get("status") not in ("pending", "applied"):
        bad.append(f"status {rec.get('status')!r} is not pending or applied")
    for where, s in strings(rec):
        if any(d in s for d in DASHES):
            bad.append(f"em or en dash in {where}")

    lines = rec.get("results_lines")
    if not isinstance(lines, list):
        bad.append("results_lines is not a list")
    else:
        for i, ln in enumerate(lines):
            m = LINE_RE.match(ln) if isinstance(ln, str) else None
            if not m or not real_date(m.group(1)):
                bad.append(f"results_lines[{i}] does not start with '- YYYY-MM-DD'")
            elif "\n" in ln or "\r" in ln:
                bad.append(f"results_lines[{i}] holds a line break")

    sc = rec.get("search_console")
    if sc is not None:
        if not isinstance(sc, dict):
            bad.append("search_console is not an object or null")
        else:
            if set(sc) != {"date", "window", "pages"}:
                bad.append(f"search_console fields are {sorted(sc)}, want only date, window, pages")
            if not real_date(sc.get("date")):
                bad.append(f"search_console.date {sc.get('date')!r} is not YYYY-MM-DD")
            if not isinstance(sc.get("window"), str) or not sc.get("window"):
                bad.append("search_console.window is not a text")
            pages = sc.get("pages")
            if not isinstance(pages, dict):
                bad.append("search_console.pages is not an object")
            else:
                for slug, v in pages.items():
                    if not SLUG_RE.match(slug):
                        bad.append(f"search_console page {slug!r} is not a slug")
                    if not isinstance(v, dict) or set(v) != {"impressions", "clicks", "position"}:
                        bad.append(f"search_console page {slug!r} must hold only impressions, clicks, position")
                        continue
                    if not is_count(v["impressions"]) or not is_count(v["clicks"]):
                        bad.append(f"search_console page {slug!r}: impressions and clicks must be whole numbers, 0 or more")
                    p = v["position"]
                    if p is not None and (isinstance(p, bool) or not isinstance(p, (int, float)) or p < 0):
                        bad.append(f"search_console page {slug!r}: position must be a number or null")

    ir = rec.get("index_requests")
    if not isinstance(ir, dict):
        bad.append("index_requests is not an object")
    elif ir:
        live = live_urls()
        if live is None:
            bad.append("could not read the live list (tools/indexnow_submit.py --all --dry-run failed)")
        for url, day in ir.items():
            if not url.startswith(BASE):
                bad.append(f"index_requests {url!r} is not a proofnotfluff.com URL")
            elif live is not None and url not in live:
                bad.append(f"index_requests {url!r} is not in the live list")
            if not real_date(day):
                bad.append(f"index_requests {url!r} date {day!r} is not YYYY-MM-DD")
    return bad


def write(path, text):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, path)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    dry = "--check" in argv
    if len(args) != 1:
        print("usage: python3 tools/apply_handoff.py <file.json> [--check]")
        return 1
    try:
        rec = json.load(open(args[0], encoding="utf-8"))
    except (OSError, ValueError) as e:
        print(f"apply_handoff: FAIL, cannot read {args[0]}: {e}")
        return 1
    bad = check(rec)
    if bad:
        print(f"apply_handoff: FAIL, {len(bad)} problem(s), nothing changed: {'; '.join(bad)}")
        return 1

    # Plan every change first, then write.
    results = open(RESULTS, encoding="utf-8").read() if os.path.isfile(RESULTS) else ""
    have = set(results.splitlines())
    new_lines, seen = [], set()
    for ln in rec["results_lines"]:
        ln = ln.rstrip()
        if ln not in have and ln not in seen:
            new_lines.append(ln)
            seen.add(ln)
    skipped = len(rec["results_lines"]) - len(new_lines)

    sc, sc_note, sc_text = rec.get("search_console"), "none in record", None
    if sc is not None:
        old = None
        if os.path.isfile(SC_FILE):
            try:
                old = json.load(open(SC_FILE, encoding="utf-8")).get("date")
            except (OSError, ValueError):
                old = None
        if old is None or sc["date"] > old:
            sc_text = json.dumps(sc, indent=1, ensure_ascii=False) + "\n"
            sc_note = f"written ({sc['date']}, {sc['window']}, {len(sc['pages'])} pages)"
        else:
            sc_note = f"kept (file {old} is not older than {sc['date']})"

    ir_old = json.load(open(IR_FILE, encoding="utf-8")) if os.path.isfile(IR_FILE) else {}
    ir_new, added, later = dict(ir_old), 0, 0
    for url, day in rec["index_requests"].items():
        if url not in ir_new:
            ir_new[url], added = day, added + 1
        elif day > ir_new[url]:
            ir_new[url], later = day, later + 1

    summary = (f"apply_handoff: {'CHECK OK' if dry else 'OK'}, index-request {rec['date']}: results +{len(new_lines)} "
               f"({skipped} already there), search-console {sc_note}, index-requests +{added} new, {later} later date")
    if dry:
        print(summary)
        return 0
    if new_lines:
        sep = "" if not results or results.endswith("\n") else "\n"
        write(RESULTS, results + sep + "\n".join(new_lines) + "\n")
    if sc_text is not None:
        write(SC_FILE, sc_text)
    if added or later:
        write(IR_FILE, json.dumps(ir_new, indent=1, ensure_ascii=False) + "\n")
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
