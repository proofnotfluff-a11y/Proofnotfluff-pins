#!/usr/bin/env python3
"""Planted failures for every video engine gate, plus the artifact contracts (Todd, Oct 27, 2026: "Planted failures
for every gate, run by check_repo like tools/test_gates.py"). Each tool's own --selftest plants its failures and must
catch every one; this file runs them all, then validates every committed video artifact against its JSON Schema in
video/schema/, lints every committed spec, checks the ledger and looks for dashes. check_repo.py runs it as the video
check. A gate that stops catching a planted failure turns every run red: tell Todd, never edit the gate to clear it.

  video_story     planted story picked, tiny base skipped, stale file refused, missing field, novelty, ties, 3-week plan
  video_gates     gates 1 to 3 and the number recompute: wrong number (screen and evidence), em dash, AI phrase,
                  personal detail, promise, rats found, close twice, digits heard, hooks, voice, AI line, address
  video_layout    text under 42 px, outside the safe band, in the right 150 px, overlaps (layout before rendering)
  video_render    timeline, captions, 45 to 60 s, frame one shows the number, caption number timing
  video_qa        length, loudness, black, frozen, hook timing and silence at the start, wrong number on screen, caption
                  below the band, a face, file and fingerprint, a check that cannot run counts as a FAIL
  video_pairwise  pair lists, splits as ties, the send test rule
  video_ledger    lock, stale lock, moves, wrong prior state, fingerprints bound to the yes, double post, tampering
  video_voice     word timings, segment order, no key stops the run

Usage: python3 tools/test_video_gates.py [--fast]     --fast skips video_qa's clips (about 25 s)
"""
import glob, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SELFTESTS = ["video_story", "video_gates", "video_layout", "video_render", "video_pairwise", "video_ledger", "video_voice", "video_qa"]
ARTIFACTS = [("video/specs/*.json", "spec"), ("video/candidates/*.json", "candidates"), ("video/renders/*/*/manifest.json", "manifest"),
             ("video/renders/*/*/qa.json", "qa"), ("video/reviews/*/*.json", "review"), ("video/metrics/*.json", "metrics"),
             ("video/fixtures/spec-example.json", "spec"), ("video/fixtures/candidates-example.json", "candidates")]


def artifacts(root=ROOT, tracked=None):
    """Every video artifact validated against its schema; every committed spec through the Rat check lint."""
    import jsonschema
    sys.path.insert(0, os.path.join(root, "tools"))
    import spec_lint, video_ledger
    out, n = [], 0
    schemas = {os.path.basename(f).split(".")[0]: json.load(open(f)) for f in glob.glob(os.path.join(root, "video", "schema", "*.schema.json"))}
    for name, sc in schemas.items():
        jsonschema.Draft202012Validator.check_schema(sc)
        ex = os.path.join(root, "video", "schema", "examples", f"{name}.example.json")
        if not os.path.exists(ex):
            out.append(f"schema {name} has no worked example")
            continue
        for e in jsonschema.Draft202012Validator(sc).iter_errors(json.load(open(ex))):
            out.append(f"example {name}: {e.message[:120]}")
        n += 1
    for pat, name in ARTIFACTS:
        for f in sorted(glob.glob(os.path.join(root, pat))):
            rel = os.path.relpath(f, root)
            if tracked is not None and rel not in tracked:
                continue
            try:
                doc = json.load(open(f, encoding="utf-8"))
            except ValueError as e:
                out.append(f"{rel}: does not parse"); continue
            for e in jsonschema.Draft202012Validator(schemas[name]).iter_errors(doc):
                out.append(f"{rel}: {e.message[:120]}")
            n += 1
            if name == "spec" and rel.startswith("video/specs/"):
                for p in spec_lint.rat_check_problems(doc, rel):
                    out.append(f"{rel}: {p}")
    led = os.path.join(root, "video", "LEDGER.md")
    if os.path.exists(led):
        for p in video_ledger.check(led):
            out.append(f"video/LEDGER.md: {p}")
        for r in video_ledger.read(led)["rows"]:
            for e in jsonschema.Draft202012Validator(schemas["ledger_row"]).iter_errors(r):
                out.append(f"ledger row {r.get('videoId')}: {e.message[:120]}")
            n += 1
    for f in glob.glob(os.path.join(root, "video", "**", "*"), recursive=True):
        if "node_modules" in f or not os.path.isfile(f) or not re.search(r"\.(md|json|jsx|js|txt)$", f):
            continue
        rel = os.path.relpath(f, root)
        if tracked is not None and rel not in tracked:
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        if "—" in t or "–" in t:
            out.append(f"{rel}: an em or en dash")
    return out, n


def main():
    fast = "--fast" in sys.argv
    bad = []
    for t in SELFTESTS:
        if fast and t == "video_qa":
            continue
        r = subprocess.run([sys.executable, os.path.join(HERE, f"{t}.py"), "--selftest"], capture_output=True, text=True, timeout=900, cwd=ROOT)
        last = [l for l in r.stdout.splitlines() if "selftest" in l]
        if r.returncode:
            bad.append(f"{t}: " + "; ".join(l[5:] for l in r.stdout.splitlines() if l.startswith("FAIL"))[:300] or (r.stderr[-200:]))
        else:
            print(f"OK {last[-1] if last else t}")
    probs, n = artifacts()
    for p in probs:
        bad.append(p)
    for b in bad:
        print("FAIL", b)
    ran = len(SELFTESTS) - (1 if fast else 0)
    print(f"video gates: {'ok' if not bad else str(len(bad)) + ' failed'} ({ran} planted selftests, {n} artifacts against their schemas)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
