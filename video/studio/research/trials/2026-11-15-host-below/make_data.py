#!/usr/bin/env python3
"""usage: make_data.py. Every number the video shows or says, read from the heat read's own files (never typed):
../../heat/2026-11-13-results.json and ../../heat/queries.json -> video/data.js."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); HEAT = os.path.join(HERE, "..", "..", "heat")
R = json.load(open(os.path.join(HEAT, "2026-11-13-results.json"))); Q = json.load(open(os.path.join(HEAT, "queries.json")))
area = lambda s: {"slug": s, "label": Q["areas"][s]["label"], "kept": R["areas"][s]["kept"], "hot": R["areas"][s]["hot"]}
topic = next(t for t in R["topics"] if t["topic"] == "giant-model-on-laptop")
rank = sorted(R["areas"], key=lambda s: -R["areas"][s]["hot"])
D = {"source": "video/studio/research/heat/2026-11-13-results.json and queries.json", "read": R["read"],
     "searches": R["searches"], "queries": sum(len(a["queries"]) for a in Q["areas"].values()), "areas": len(R["areas"]),
     "videos": R["videos"], "hot": R["hot"], "days": R["rules"]["days"], "min_views": R["rules"]["min_views"], "ratio": R["rules"]["ratio"],
     "per_area": Q["per_area"], "winner": area(rank[0]), "second": area(rank[1]), "chatgpt": area("chatgpt"), "trades": area("trades"), "small": area("small-business"),
     "rank": [[s, R["areas"][s]["hot"]] for s in rank],
     "laptop": {"videos": topic["videos"], "small_channel_wins": topic["small_channel_wins"], "small_means_under": 100000}}
assert D["winner"]["slug"] == "local-ai" and D["second"]["slug"] == "claude", "the ranking changed: rewrite the script"
assert D["chatgpt"]["hot"] < D["second"]["hot"] < D["winner"]["hot"], "ChatGPT is no longer behind Claude and the winner: rewrite the script"
open(os.path.join(HERE, "video", "data.js"), "w").write("window.DATA = " + json.dumps(D, indent=1) + ";\n")
print({k: D[k] for k in ("searches", "videos", "hot", "days", "min_views", "ratio")}, D["winner"], D["second"], D["trades"], D["small"], D["laptop"])
