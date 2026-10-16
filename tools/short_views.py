#!/usr/bin/env python3
"""Refresh scoreboard Short views from a YouTube Data API videos.list reply.

Why: the shop run read Short views in YouTube Studio, but Chrome's YouTube is
signed in to a personal account (Oct 15), so shorts/<slug>.views froze on
Oct 11 and the 100-view walkthrough rule, the 500-view follow-up rule and the
hook scores ran on zeros. Any cloud run can fetch the numbers instead.

Route (cloud, no Chrome, no key in the repo):
  1. ArtifactData list shorts with out_dir DIR (files DIR/shorts/<slug>.json).
  2. python3 tools/short_views.py ids DIR/shorts
       prints the comma-joined YouTube ids (at most 50 per call).
  3. Zapier YouTube "Make API GET Request":
       url https://www.googleapis.com/youtube/v3/videos
       querystring {part: statistics, id: <ids>}
     Save the reply's body (or the whole Zapier result) as REPLY.json.
  4. python3 tools/short_views.py apply DIR/shorts REPLY.json VERSIONS.json OUT.json "Oct 15, 9:20 pm"
       VERSIONS.json maps slug -> version from the list result.
       Writes OUT.json: {"writes": [...]} ready for one ArtifactData batch
       (only Shorts whose views changed), and prints the rule flags.

Flags (ledger GROWTH RULES): a Short past 100 views needs a walkthrough
(CMO); a Short past 500 views earns 3 follow-ups on its topic.
"""
import json
import re
import sys
from pathlib import Path

ID_RE = re.compile(r"(?:shorts/|v=|youtu\.be/)([\w-]{11})")


def load_shorts(folder):
    shorts = {}
    for f in sorted(Path(folder).glob("*.json")):
        doc = json.loads(f.read_text())
        doc = doc.get("data", doc)
        m = ID_RE.search(doc.get("url") or "")
        if m:
            shorts[f.stem] = {"id": m.group(1), "views": doc.get("views", 0) or 0,
                              "product": doc.get("product"), "title": doc.get("title", "")}
    return shorts


def parse_reply(reply):
    """Accept the bare videos.list body or Zapier's {results:[{body:...}]} wrapper."""
    if "results" in reply:
        reply = reply["results"][0].get("body", {})
    if isinstance(reply, str):
        reply = json.loads(reply)
    out = {}
    for item in reply.get("items", []):
        stats = item.get("statistics", {})
        out[item["id"]] = int(stats.get("viewCount", 0))
    return out


def plan(shorts, views, versions, as_of):
    writes, flags = [], []
    for slug, s in shorts.items():
        if s["id"] not in views:
            flags.append(f"MISSING {slug}: {s['id']} not in the API reply (deleted or private?)")
            continue
        new = views[s["id"]]
        if new >= 500:
            flags.append(f"FOLLOW-UPS {slug}: {new} views (#{s['product']}), 3 follow-ups unless already made")
        elif new >= 100:
            flags.append(f"WALKTHROUGH {slug}: {new} views (#{s['product']}), needs a walkthrough unless it has one")
        if new != s["views"]:
            w = {"op": "update", "collection": "shorts", "doc_id": slug,
                 "data": {"views": new, "viewsAsOf": as_of}}
            if slug in versions:
                w["if_version"] = versions[slug]
            writes.append(w)
    return writes, flags


def main(argv):
    if len(argv) >= 2 and argv[0] == "ids":
        ids = [s["id"] for s in load_shorts(argv[1]).values()]
        for i in range(0, len(ids), 50):
            print(",".join(ids[i:i + 50]))
        return 0
    if len(argv) == 6 and argv[0] == "apply":
        shorts = load_shorts(argv[1])
        views = parse_reply(json.loads(Path(argv[2]).read_text()))
        versions = json.loads(Path(argv[3]).read_text())
        writes, flags = plan(shorts, views, versions, argv[5])
        Path(argv[4]).write_text(json.dumps({"writes": writes}, indent=2))
        total = sum(views.get(s["id"], 0) for s in shorts.values())
        print(f"{len(shorts)} Shorts, {total} views, {len(writes)} changed")
        for f in flags:
            print(f)
        return 0
    print(__doc__)
    return 2


def _selftest():
    shorts = {"a": {"id": "AAAAAAAAAAA", "views": 0, "product": "20", "title": ""},
              "b": {"id": "BBBBBBBBBBB", "views": 600, "product": "13", "title": ""}}
    reply = {"results": [{"body": {"items": [
        {"id": "AAAAAAAAAAA", "statistics": {"viewCount": "120"}},
        {"id": "BBBBBBBBBBB", "statistics": {"viewCount": "600"}}]}}]}
    writes, flags = plan(shorts, parse_reply(reply), {"a": 3}, "now")
    assert writes == [{"op": "update", "collection": "shorts", "doc_id": "a",
                       "data": {"views": 120, "viewsAsOf": "now"}, "if_version": 3}], writes
    assert any(f.startswith("WALKTHROUGH a") for f in flags)
    assert any(f.startswith("FOLLOW-UPS b") for f in flags)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["selftest"]:
        _selftest()
        sys.exit(0)
    sys.exit(main(sys.argv[1:]))
