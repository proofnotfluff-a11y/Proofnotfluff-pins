"""r1. Every number the trial video shows, worked out again from the statement file, and checked against what the AI wrote
in the one-question run (run/answer.md). The video's own text is read from scene.js and data.js."""
import csv, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE)
rows = list(csv.DictReader(open("demo/statement.csv"))); ans = open("run/answer.md").read().replace("**", ""); scene = open("video/scene.js").read()
data = json.loads(open("video/data.js").read().split("=", 1)[1].rstrip(";\n"))
A = lambda r: float(r["amount"]); month = lambda r: r["date"][:7]
checks = []
def ok(name, cond, detail=""): checks.append((name, bool(cond), detail))
ok("159 rows in the file", len(rows) == 159, len(rows)); ok("3 months", sorted({month(r) for r in rows}) == ["2026-08", "2026-09", "2026-10"])
by = {}
for r in rows: by.setdefault(r["description"], []).append(r)
# the nine the AI listed under Subscriptions: each must be a real monthly charge (once in each month, same day), at its latest price
listed = re.search(r"Subscriptions \(card\)\n(.*?)\n\nThat's \$([\d.]+) a month", ans, re.S)
names = [re.match(r"- (.+?):", l).group(1) for l in listed.group(1).splitlines()]
ok("the AI listed 9 subscriptions", len(names) == 9, names); ok("the AI's total is $167.89 a month", listed.group(2) == "167.89", listed.group(2))
key = lambda s: re.sub(r"[^a-z]", "", s.lower())
mine = {}
for n in names:
    hit = [d for d in by if key(d).startswith(key(n)[:8])]
    ok(f"listed name is in the file: {n}", len(hit) == 1, hit)
    if len(hit) == 1:
        rs = sorted(by[hit[0]], key=lambda r: r["date"]); mine[hit[0]] = -A(rs[-1])
        ok(f"{hit[0]} is charged once a month on one day", len(rs) == 3 and len({month(r) for r in rs}) == 3 and len({r['date'][8:] for r in rs}) == 1)
tot = round(sum(mine.values()), 2)
ok("my own total of those nine is $167.89", tot == 167.89, tot); ok("x 12 is $2,014.68", round(tot * 12, 2) == 2014.68, round(tot * 12, 2)); ok("rounded for the caption: $2,015", round(tot * 12) == 2015)
ok("the video's nine are the AI's nine, at my prices", data["subs"] == mine, (sorted(data["subs"]), sorted(mine)))
ok("the video's month and year", data["monthly"] == 167.89 and data["yearly"] == 2014.68, (data["monthly"], data["yearly"]))
ok("the video marks exactly those nine in the ledger", {r[1] for r in data["rows"] if r[3]} == set(mine))
ok("the video's rows are this statement", [[r["date"], r["description"], float(r["amount"])] for r in rows] == [r[:3] for r in data["rows"]])
hb = [r for r in rows if r["description"] == "HOMEBASE HARDWARE" and r["date"] == "2026-10-16"]
ok("double charge: two of $86.42 on Oct 16", len(hb) == 2 and all(A(r) == -86.42 for r in hb)); ok("the AI flagged it", "Two charges of $86.42 on October 16" in ans)
cb = [-A(r) for r in sorted(by["CLOUDBOX STORAGE"], key=lambda r: r["date"])]
ok("price: $2.99 then $9.99, $9.99", cb == [2.99, 9.99, 9.99], cb); ok("3.3x", f"{cb[1] / cb[0]:.1f}" == "3.3"); ok("the AI said so", "from $2.99 in August to $9.99" in ans and "more than three times" in ans)
dd = {m: [-A(r) for r in rows if r["description"] == "DASHDISH DELIVERY" and month(r) == m] for m in ("2026-08", "2026-09", "2026-10")}
ok("delivery orders 6, 9, 12", [len(v) for v in dd.values()] == [6, 9, 12] == data["orders"]); ok("delivery $212, $301, $394", [round(sum(v)) for v in dd.values()] == [212, 301, 394] and [round(x) for x in data["delivery"]] == [212, 301, 394])
ok("orders doubled: 12 is 2 x 6", len(dd["2026-10"]) == 2 * len(dd["2026-08"])); ok("the AI said so", "6 orders ($212.01)" in ans and "9 ($301.01)" in ans and "12 ($393.98)" in ans)
ok("DashDish is the only delivery merchant in the file", not [d for d in by if re.search("DELIVER|EATS|DASH", d) and d != "DASHDISH DELIVERY"])
secs = float(re.search(r"\(([\d.]+) s after the ask\)", open("run/runlog.txt").read()).group(1))
ok("the run took under a minute (written answer)", secs < 60, secs); ok("the clock on screen is the run's time", data["run"]["seconds_to_answer"] == secs, (data["run"]["seconds_to_answer"], secs))
ok("the question on screen is the one the run was asked", data["run"]["question"] == ["What am I paying for every month?", "Anything look off?"])
ok("the opening caption credits the AI with no figure", "'An AI read one sample statement.'" in scene and "An AI found" not in scene)
ok("the yearly caption is the rounded x 12", '"That\'s " + YR + \' a year.\'' in scene)
for cap in ["'With no bank link.'", "'Ask Claude one question.'", "'159 transactions.'", "'Under a minute.'", "SUBS.length + ' subscriptions.'", "'It also flagged a double charge.'", "'A price that tripled.'", "'Delivery orders doubled.'"]:
    ok(f"caption present: {cap}", cap in scene)
ok("no em or en dash anywhere", not re.search("[" + chr(0x2013) + chr(0x2014) + "]", scene + ans + open("video/lib.js").read()))
bad = [c for c in checks if not c[1]]
for n, o, d in checks: print(("PASS " if o else "FAIL ") + n + ("" if o else f"  got {d}"))
print(f"verify: {len(checks) - len(bad)} of {len(checks)}"); sys.exit(1 if bad else 0)
