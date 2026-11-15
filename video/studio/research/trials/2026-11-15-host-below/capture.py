#!/usr/bin/env python3
"""usage: capture.py. Real captures of our own two public files, as a browser shows them (the raw file pages on GitHub),
plus where each line the video points at sits in the capture. Nothing is typed, signed in to or changed.
Writes video/shots/<name>.png and video/shots.js (sizes, the address, the time, each target's box in capture pixels)."""
import datetime, hashlib, json, os
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "video", "shots"); os.makedirs(OUT, exist_ok=True)
RAW = "https://raw.githubusercontent.com/proofnotfluff-a11y/proofnotfluff-pins/main/video/studio/research/heat/"
CSS_W, DSF = 430, 3
# name -> [after this text, the text to box]: the box is the first match of the second string after the first
PAGES = {
    "results": ("2026-11-13-results.json", {
        "min_views": ['"rules"', '"min_views": 20000'], "ratio": ['"rules"', '"ratio": 3.0'], "days": ['"rules"', '"days": 14'],
        "searches": ['"rules"', '"searches": 62'], "videos": ['"rules"', '"videos": 529'], "hot": ['"videos": 529', '"hot": 148'],
        "claude": ['"areas"', '"claude"'], "claude_hot": ['"claude": {', '"hot": 21'],
        "small": ['"areas"', '"small-business"'], "small_hot": ['"small-business": {', '"hot": 2'],
        "trades": ['"areas"', '"trades"'], "trades_kept": ['"trades": {', '"kept": 40'], "trades_hot": ['"trades": {', '"hot": 2'],
        "local": ['"areas"', '"local-ai"'], "local_kept": ['"local-ai": {', '"kept": 40'], "local_hot": ['"local-ai": {', '"hot": 23'],
        "laptop": ['"topics"', '"giant-model-on-laptop"'], "laptop_videos": ['"giant-model-on-laptop"', '"videos": 12'],
        "laptop_small": ['"giant-model-on-laptop"', '"small_channel_wins": 7']}),
    "queries": ("queries.json", {
        "trades_q": ['"trades"', '"AI for contractors"'], "local_q": ['"local-ai"', '"run AI on your own computer"'], "first_q": ['"areas"', '"AI agent automate my job"']}),
}
JS = """([pairs]) => { const pre = document.querySelector('pre'); const node = pre.firstChild; const text = node.textContent; const out = {};
  for (const [k, [after, needle]] of Object.entries(pairs)) { const a = text.indexOf(after); const i = a < 0 ? -1 : text.indexOf(needle, a); if (i < 0) { out[k] = null; continue; }
    const r = document.createRange(); r.setStart(node, i); r.setEnd(node, i + needle.length); const b = r.getClientRects();
    out[k] = Array.from(b).map((q) => [q.left + scrollX, q.top + scrollY, q.width, q.height]); }
  return {boxes: out, w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight, bytes: text.length}; }"""
doc = {"captured": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "dsf": DSF, "pages": {}}
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None,
                           proxy={"server": os.environ["HTTPS_PROXY"]} if os.environ.get("HTTPS_PROXY") else None, args=["--no-sandbox"])
    for name, (file, pairs) in PAGES.items():
        pg = b.new_page(viewport={"width": CSS_W, "height": 900}, device_scale_factor=DSF)
        r = pg.goto(RAW + file, wait_until="load", timeout=60000)
        if r.status != 200:
            raise SystemExit(f"capture: {file} answered {r.status}")
        info = pg.evaluate(JS, [pairs])
        miss = [k for k, v in info["boxes"].items() if not v]
        if miss:
            raise SystemExit(f"capture: not on the page: {miss}")
        local = open(os.path.join(HERE, "..", "..", "heat", file), encoding="utf-8").read()
        same = pg.evaluate("document.querySelector('pre').textContent") == local
        if not same:
            raise SystemExit(f"capture: the page's text is not the repo's {file}")
        png = os.path.join(OUT, name + ".png"); pg.screenshot(path=png, full_page=True)
        doc["pages"][name] = {"url": RAW + file, "file": file, "w": info["w"] * DSF, "h": info["h"] * DSF, "same_as_repo_file": same,
                              "sha256": hashlib.sha256(open(png, "rb").read()).hexdigest(),
                              "boxes": {k: [[round(v * DSF, 1) for v in q] for q in qs] for k, qs in info["boxes"].items()}}
        print(name, info["w"] * DSF, "x", info["h"] * DSF, "px,", len(pairs), "targets, same text as the repo file:", same, os.path.getsize(png) // 1024, "KB")
        pg.close()
    b.close()
open(os.path.join(HERE, "video", "shots.js"), "w").write("window.SHOTS = " + json.dumps(doc) + ";\n")
