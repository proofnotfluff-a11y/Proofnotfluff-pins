#!/usr/bin/env python3
"""usage: verify.py. Works every number the video says or shows out again from the heat read's own files and checks the
script, the captions, data.js and the captures against them. Exit 1 on any miss. No model: one right answer each."""
import json, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); HEAT = os.path.join(HERE, "..", "..", "heat")
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..")))
import anim, importlib.util  # noqa: E402
_sp = importlib.util.spec_from_file_location("trial_voice", os.path.join(HERE, "voice", "voice.py")); voice = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(voice)
R = json.load(open(os.path.join(HEAT, "2026-11-13-results.json"))); Q = json.load(open(os.path.join(HEAT, "queries.json")))
js = lambda f, name: json.loads(re.sub(r";\s*$", "", open(os.path.join(HERE, "video", f)).read().split(f"window.{name} = ", 1)[1]))
D, SH = js("data.js", "DATA"), js("shots.js", "SHOTS")
checks = []
def ok(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# 1. the files themselves
A = R["areas"]; rank = sorted(A, key=lambda s: -A[s]["hot"]); lap = next(t for t in R["topics"] if t["topic"] == "giant-model-on-laptop")
ok("searches in the results file equal the queries in queries.json", R["searches"] == sum(len(a["queries"]) for a in Q["areas"].values()) == 62)
ok("every area kept 40", all(a["kept"] == Q["per_area"] == 40 for a in A.values()))
ok("the winner is AI on your own machine", rank[0] == "local-ai" and A["local-ai"]["hot"] == 23 and A[rank[1]]["hot"] < 23)
ok("Claude is second, alone", rank[1] == "claude" and A["claude"]["hot"] == 21 and A[rank[2]]["hot"] < 21)
ok("trades 2 of 40", A["trades"]["hot"] == 2 and A["trades"]["kept"] == 40)
ok("ChatGPT 11 of 40, behind Claude and the winner (\"isn't ChatGPT\", \"NOT FIRST\")", A["chatgpt"]["hot"] == 11 and A["chatgpt"]["kept"] == 40 and rank.index("chatgpt") > 1)
ok("16 areas", len(A) == 16 == len(Q["areas"]))
ok("small channel means under 100,000 subscribers (the file's own note)", "under 100,000 subscribers" in R["note"])
ok("the laptop topic is hot videos, 12, 7 from small channels", lap["videos"] == 12 and lap["small_channel_wins"] == 7 and "grouping of hot videos into topics" in R["note"])

# 2. data.js is what make_data.py makes from those files today
before = open(os.path.join(HERE, "video", "data.js")).read()
subprocess.run([sys.executable, os.path.join(HERE, "make_data.py")], check=True, capture_output=True)
ok("data.js matches a fresh make_data.py", open(os.path.join(HERE, "video", "data.js")).read() == before)

# 3. every number spoken, in order, against the files
takes = voice.takes(); words = [w for t in takes for w in anim.spoken_words(t)]
NUM = {w: i for i, w in enumerate(anim.ONES)}; NUM.update({w: i * 10 for i, w in enumerate(anim.TENS) if w != "_"})
def number_runs(ws):
    """[(first word, last word, value)] for each run of number words ("a hundred forty-eight" -> 148)."""
    out, i = [], 0
    toks = [re.sub(r"[^a-z-]", "", w.lower()) for w in ws]
    while i < len(toks):
        parts = toks[i].split("-"); j = i
        if not all(p in NUM or p in ("hundred", "thousand") for p in parts) and not (toks[i] == "a" and i + 1 < len(toks) and toks[i + 1] in ("hundred", "thousand")):
            i += 1; continue
        total, cur = 0, 0
        while j < len(toks):
            ps = toks[j].split("-")
            if toks[j] == "a" and j + 1 < len(toks) and toks[j + 1] in ("hundred", "thousand") and cur == 0: cur = 1
            elif all(p in NUM for p in ps): cur += sum(NUM[p] for p in ps)
            elif toks[j] == "hundred": cur = max(cur, 1) * 100
            elif toks[j] == "thousand": total += max(cur, 1) * 1000; cur = 0
            else: break
            j += 1
            if re.search(r"[.,?!]$", ws[j - 1]): break
        out.append((i, j - 1, total + cur)); i = j
    return out
runs = number_runs(words)
EXPECT = [("areas counted", len(A)), ("weeks = days / 7", R["rules"]["days"] // 7), ("videos", R["videos"]), ("kept in each area", Q["per_area"]),
          ("hot floor, views", R["rules"]["min_views"]), ("chatgpt hot", A["chatgpt"]["hot"]), ("chatgpt kept", A["chatgpt"]["kept"]), ("claude hot", A["claude"]["hot"]),
          ("winner hot", A["local-ai"]["hot"]), ("trades hot", A["trades"]["hot"]), ("trades kept", A["trades"]["kept"]),
          ("laptop hot videos", lap["videos"]), ("laptop small channel wins", lap["small_channel_wins"]), ("small channel line", 100000), ("counts", 1),
          ("weeks", R["rules"]["days"] // 7)]
ok(f"the script says {len(EXPECT)} numbers", len(runs) == len(EXPECT), f"heard {[r[2] for r in runs]}")
for (name, want), (i0, i1, got) in zip(EXPECT, runs):
    ok(f"spoken '{' '.join(words[i0:i1 + 1])}' = {name} ({want})", got == want, f"got {got}")
txt = " ".join(takes)
ok("'triple' is the file's ratio of 3", "triple" in txt and R["rules"]["ratio"] == 3.0)
ok("'two weeks' is the file's 14 days", R["rules"]["days"] == 14)
ok("no digits, $, % or & in the voice", not re.search(r"[0-9$%&]", txt))
ok("no em or en dash in the script", not re.search("[\u2013\u2014]", open(os.path.join(HERE, "voice", "script.md")).read()))

# 4. the captions: one or two words, the script's own words, each number the number said
caps = json.loads(re.sub(r"//.*", "", open(os.path.join(HERE, "video", "captions.js")).read()).split("window.CAPTIONS = ", 1)[1].rsplit("]", 1)[0].rstrip().rstrip(",") + "]")
ok("captions cover every spoken word once", sum(n for _, n in caps) == len(words), f"{sum(n for _, n in caps)} of {len(words)}")
ok("never more than two words on screen", all(len(t.split()) <= 2 for t, _ in caps))
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
bad, i, by_word = [], 0, {r[0]: r for r in runs}
for t, n in caps:
    span = words[i:i + n]; said = []
    j = i
    while j < i + n:
        if j in by_word: said.append(str(by_word[j][2])); j = by_word[j][1] + 1
        else: said.append(words[j]); j += 1
    if j != i + n or norm("".join(said)) != norm(t): bad.append((t, " ".join(span)))
    i += n
ok("every caption is the words said (numbers as digits)", not bad, str(bad[:4]))
ok("no dash in the captions", not re.search("[\u2013\u2014]", " ".join(t for t, _ in caps)))

# 5. the scene draws its numbers from data.js, and the captures are the repo's files
scene = open(os.path.join(HERE, "video", "scene.js")).read()
strings = re.findall(r"'([^'\n]*)'", scene)
typed = [s for s in strings if re.search(r"\b(23|21|11|16|62|529|148|20,?000|100,?000)\b", s) and s != '"videos": 529']   # that one string only measures a character's width
ok("no heat number is typed into scene.js", not typed, str(typed))
ok("no dash in the scene's words", not re.search("[\u2013\u2014]", scene))
for name, pg in SH["pages"].items():
    ok(f"the {name} capture showed the same text as the repo's {pg['file']}", pg["same_as_repo_file"] is True)
    png = os.path.join(HERE, "video", "shots", name + ".png")
    if os.path.exists(png):
        import hashlib
        ok(f"the {name} capture on disk is the one shots.js names", hashlib.sha256(open(png, "rb").read()).hexdigest() == pg["sha256"])
keys = set(re.findall(r"\['(\w+)', \d+, '(?:amber|red|teal)'\]", scene)) | set(re.findall(r"top: '(\w+)'", scene))
allb = {k for pg in SH["pages"].values() for k in pg["boxes"]}
ok(f"every line the scene points at ({len(keys)}) was found in a capture", keys <= allb, str(keys - allb))
ok("D.winner, D.second, D.chatgpt, D.trades in data.js are the file's", D["winner"]["hot"] == A["local-ai"]["hot"] and D["second"]["hot"] == A["claude"]["hot"] and D["chatgpt"]["hot"] == A["chatgpt"]["hot"] and D["trades"]["hot"] == A["trades"]["hot"] and D["per_area"] == 40 and D["areas"] == 16)

fails = [c for c in checks if not c[1]]
for name, good, detail in checks:
    if not good or "-v" in sys.argv: print(("PASS " if good else "FAIL ") + name + (f": {detail}" if detail and not good else ""))
print(f"verify: {'PASS' if not fails else 'FAIL'} {len(checks) - len(fails)} of {len(checks)}")
sys.exit(1 if fails else 0)
