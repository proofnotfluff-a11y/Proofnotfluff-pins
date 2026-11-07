#!/usr/bin/env python3
"""Merge the night shift's pulse reads into one checked list (Todd, live chat, Nov 7, 2026, 5:22 am: "the box is our work
horse and we should be heavily utilizing it on value add tasks").

The 21:33 studio run hands the box pulse-night-extract jobs (8 thread pages each, video/studio/_shared/nightshift.md).
This script, run by the 9:33 run, keeps only what code can prove, so Claude checks a short list instead of 80 pages:
  - the item's url is one of the pages that job asked the box to read (no invented links), and that page came back ok
  - the quote is 10 words or fewer and appears in no item as a person's email or phone number
  - one item per (url, problem); near-duplicate problems on the same url are dropped
Then it counts, for each item, how many other pages raise a problem sharing 3 or more key words, the "threads" signal
trade-pulse ranks by. Writes video/studio/research/pulse/night-<date>.json (numbers, urls, our paraphrase; no names).

  python3 tools/pulse_merge.py [--date YYYY-MM-DD]     date = the night the jobs were named for (default yesterday)
"""
import argparse
import datetime as dt
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANE = os.environ.get("PNF_LOCAL_JOBS", "/home/claude/pnf-local-jobs")
PULSE = os.path.join(ROOT, "video", "studio", "research", "pulse")
PERSON = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+|\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")
STOP = set("""a an and are as at be but by can do for from has have how i if in is it its just my no not of on or our so
that the their them they this to up was we what when who why will with you your our me get got any all more than""".split())


def words(t):
    return {w for w in re.findall(r"[a-z0-9$%']+", (t or "").lower()) if w not in STOP and len(w) > 2}


def merge(date):
    items, seen, report = [], set(), {"jobs": 0, "ok": 0, "pages_ok": 0, "raw": 0, "kept": 0, "dropped": {}}
    def drop(why):
        report["dropped"][why] = report["dropped"].get(why, 0) + 1
    for jf in sorted(glob.glob(os.path.join(LANE, "fetch", f"pulse-night-extract-{date}-r*.json"))):
        name = os.path.basename(jf)[:-5]
        report["jobs"] += 1
        af = os.path.join(LANE, "answers", name + ".json")
        if not os.path.exists(af):
            drop("no answer yet"); continue
        job, ans = json.load(open(jf, encoding="utf-8")), json.load(open(af, encoding="utf-8"))
        if ans.get("status") != "ok":
            drop("job not ok"); continue
        report["ok"] += 1
        okpages = {p.get("url") for p in ans.get("pages", []) if p.get("status") == "ok"}
        report["pages_ok"] += len(okpages)
        asked = set(job.get("urls", []))
        for it in (ans.get("output") or {}).get("items", []):
            report["raw"] += 1
            url, prob = str(it.get("url", "")).strip(), str(it.get("problem", "")).strip()
            quote = str(it.get("quote_under_10_words", "") or "").strip()
            if url not in asked:
                drop("url not one the box was asked to read"); continue
            if url not in okpages:
                drop("page did not load"); continue
            if not prob:
                drop("no problem stated"); continue
            if quote and len(quote.split()) > 10:
                quote = ""
                drop("quote over 10 words (quote removed, item kept)")
            if PERSON.search(prob + " " + quote):
                drop("email or phone in text"); continue
            key = (url, frozenset(list(words(prob))[:8]))
            if any(u == url and len(words(prob) & set(k)) >= 3 for u, k in seen):
                drop("near duplicate on the same page"); continue
            seen.add(key)
            items.append({"problem": prob[:200], "trade": str(it.get("trade", ""))[:40], "quote": quote, "url": url,
                          "date_on_page": str(it.get("date_on_page", ""))[:20], "job": name})
    for i, it in enumerate(items):
        w = words(it["problem"])
        it["also_on_pages"] = len({o["url"] for o in items if o["url"] != it["url"] and len(w & words(o["problem"])) >= 3})
        it["n"] = i + 1
    items.sort(key=lambda x: -x["also_on_pages"])
    report["kept"] = len(items)
    out = {"date": date, "rule": "tools/pulse_merge.py: url asked and loaded, quote 10 words or fewer, no contact details",
           "report": report, "items": items}
    os.makedirs(PULSE, exist_ok=True)
    path = os.path.join(PULSE, f"night-{date}.json")
    json.dump(out, open(path, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"pulse_merge: {report['jobs']} jobs, {report['ok']} ok, {report['pages_ok']} pages read, {report['raw']} items, "
          f"{report['kept']} kept -> {os.path.relpath(path, ROOT)}; dropped {report['dropped']}")
    return 0 if report["jobs"] else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=(dt.date.today() - dt.timedelta(1)).isoformat())
    return merge(ap.parse_args().date)


if __name__ == "__main__":
    sys.exit(main())
