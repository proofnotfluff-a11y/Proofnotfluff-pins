#!/usr/bin/env python3
"""Two-at-a-time judging for the video engine (blueprint, Review rubrics): the hook pick and the send test. Each of two
fresh judges sees every pair in both orders; a judge whose two answers for a pair disagree counts as a tie for that pair.
Code builds the pair lists and does the counting, so no model adds up its own votes.

Hook pick: every pair of the 3 to 5 hooks, both orders, shuffled by the video id. A judge's pair winner earns 1 point,
a split 0.5 each; the hook with the most points over both judges wins; a tie goes to the hook written first.
Send test: this video against the reference (the best posted video so far; for the first video, the golden test render),
both orders. It FAILS only when both judges, in both orders, pick the reference.

Usage
  video_pairwise.py pairs --items N --seed VIDEO_ID         the shuffled pair list (pair n, x, y), as JSON
  video_pairwise.py hook --seed VIDEO_ID --items N J1.json J2.json      the winning hook index and the points
  video_pairwise.py send J1.json J2.json                    PASS or FAIL (pairs: 1 is video X, reference Y; 2 swapped)
  video_pairwise.py --selftest
"""
import argparse, hashlib, itertools, json, random, sys


def pairs(n, seed):
    rng = random.Random(int(hashlib.sha256(str(seed).encode()).hexdigest()[:12], 16))
    out = [(a, b) for a, b in itertools.combinations(range(n), 2)] + [(b, a) for a, b in itertools.combinations(range(n), 2)]
    rng.shuffle(out)
    return [{"pair": i + 1, "x": a, "y": b} for i, (a, b) in enumerate(out)]


def judge_prefs(plist, picks):
    """{(lo, hi): winner index or None for a split}, from one judge's picks."""
    by = {p["pair"]: p for p in picks}
    seen = {}
    for p in plist:
        k = p["pair"]
        if k not in by or by[k].get("pick") not in ("X", "Y"):
            raise ValueError(f"judge gave no X or Y for pair {k}")
        won = p["x"] if by[k]["pick"] == "X" else p["y"]
        seen.setdefault(tuple(sorted((p["x"], p["y"]))), []).append(won)
    return {k: (v[0] if len(v) == 2 and v[0] == v[1] else None) for k, v in seen.items()}


def hook_pick(n, seed, judges):
    plist = pairs(n, seed)
    pts = [0.0] * n
    for j in judges:
        for (a, b), w in judge_prefs(plist, j["picks"]).items():
            if w is None:
                pts[a] += 0.5
                pts[b] += 0.5
            else:
                pts[w] += 1
    best = max(range(n), key=lambda i: (pts[i], -i))
    return best, pts


SEND_PAIRS = [{"pair": 1, "x": 0, "y": 1}, {"pair": 2, "x": 1, "y": 0}]   # 0 = this video, 1 = the reference


def send_test(judges):
    ref_every_time = all(judge_prefs(SEND_PAIRS, j["picks"]).get((0, 1)) == 1 for j in judges)
    return (not ref_every_time), ("both judges, in both orders, picked the reference" if ref_every_time else
                                  "the reference did not win every comparison")


def selftest():
    bad = []
    p = pairs(4, "2026-11-02-rats-a")
    if len(p) != 12 or len({(x["x"], x["y"]) for x in p}) != 12:
        bad.append("4 hooks give 12 ordered pairs, each once")
    if pairs(4, "2026-11-02-rats-a") != p:
        bad.append("the same video id gives the same order")

    def picks_for(plist, favor):   # a judge who always picks `favor` when it is in the pair, else the lower index
        out = []
        for q in plist:
            w = favor if favor in (q["x"], q["y"]) else min(q["x"], q["y"])
            out.append({"pair": q["pair"], "pick": "X" if q["x"] == w else "Y"})
        return {"picks": out}

    best, pts = hook_pick(4, "v", [picks_for(pairs(4, "v"), 2), picks_for(pairs(4, "v"), 2)])
    if best != 2:
        bad.append(f"two judges who favor hook 3 pick it ({best}, {pts})")
    x_always = {"picks": [{"pair": q["pair"], "pick": "X"} for q in pairs(3, "s")]}
    best, pts = hook_pick(3, "s", [x_always, x_always])
    if pts != [2.0, 2.0, 2.0] or best != 0:
        bad.append(f"a judge who always says X is all ties, and the first hook wins the tie ({best}, {pts})")
    ref = {"picks": [{"pair": 1, "pick": "Y"}, {"pair": 2, "pick": "X"}]}
    mine = {"picks": [{"pair": 1, "pick": "X"}, {"pair": 2, "pick": "Y"}]}
    split = {"picks": [{"pair": 1, "pick": "X"}, {"pair": 2, "pick": "X"}]}
    if send_test([ref, ref])[0]:
        bad.append("send test fails when both judges pick the reference in both orders")
    if not send_test([ref, split])[0] or not send_test([ref, mine])[0]:
        bad.append("send test passes when any comparison does not go to the reference")
    try:
        hook_pick(3, "s", [{"picks": []}, x_always])
        bad.append("a judge with missing picks is refused")
    except ValueError:
        pass
    for b in bad:
        print("FAIL", b)
    print(f"video_pairwise selftest: {'ok' if not bad else str(len(bad)) + ' failed'} (pair lists, stable order, hook pick, splits as ties, "
          "send test rule, missing picks)")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", choices=["pairs", "hook", "send"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--items", type=int); ap.add_argument("--seed")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.cmd == "pairs":
        print(json.dumps(pairs(a.items, a.seed), indent=1))
    elif a.cmd == "hook":
        best, pts = hook_pick(a.items, a.seed, [json.load(open(f)) for f in a.files])
        print(json.dumps({"hook": best, "points": pts}))
    elif a.cmd == "send":
        ok, why = send_test([json.load(open(f)) for f in a.files])
        print(f"send test: {'PASS' if ok else 'FAIL'} ({why})")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
