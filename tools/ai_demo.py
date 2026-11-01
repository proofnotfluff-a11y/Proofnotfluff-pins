#!/usr/bin/env python3
"""Real proof for AI lane lessons (Todd, live chat, Nov 1, 2026, 9:01 am: "go with your recommendation", the AI for
trades lane test; video/studio/_shared/lanes.md).

A studio run cannot reach AI sites or most web pages from its own sandbox, so it commits a job and the GitHub workflow
studio-ai-demo.yml runs it on GitHub's machine:

  video/studio/demos/jobs/<name>.json
    {"prompt": "the exact words an owner would type", "model": "gemini-3.8-flash" (optional),
     "pages": ["https://public help, pricing or settings page", ...] (optional, up to 4)}

and commits video/studio/demos/out/<name>/:
  run.json      the model id, the prompt, the reply as the model returned it (dashes shown as commas, the repo refuses
                em and en dashes; "dashes" says how many), the time, the token count, and the
                seconds the model call took (wall time on GitHub's machine)
  page-<n>.png  each page as a phone shows it (430 x 932 at 3x), top of the page
  page-<n>-full.png  the whole page
  pages.json    each page's address, final address, title and time

What a lesson may show from this: the reply text exactly as run.json holds it, labelled with the model and date, and
the page shots with their address. Never an output the run did not produce, never a made-up app screen.
The key is the GEMINI_API_KEY secret, read from the environment and never printed.
"""
import argparse
import datetime as dt
import json
import os
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import watch_video as W  # noqa: E402  (the Gemini call, errors and key redaction already tested there)

DEFAULT_MODEL = W.DEFAULT_MODEL
URL = re.compile(r"^https://[^\s/]+\.[^\s/]+(/\S*)?$")
MAX_PAGES = 4


def generate(prompt, *, key, model, call=W._call):
    payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    _, body = call("POST", f"{W.API}/v1beta/models/{model}:generateContent", key,
                   data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"},
                   timeout=120.0)
    data = W._json(body, key)
    cand = (data.get("candidates") or [{}])[0]
    parts = [p["text"] for p in (cand.get("content") or {}).get("parts", []) if p.get("text")]
    if not parts:
        reason = cand.get("finishReason") or (data.get("promptFeedback") or {}).get("blockReason")
        raise W.GeminiError("rejected", f"no answer text (reason {reason or 'none given'})")
    raw = "\n".join(parts).strip()
    return {"model": data.get("modelVersion") or model, "text": W.plain(raw),
            "dashes": len(re.findall(r"[–—]", raw)),
            "tokens": (data.get("usageMetadata") or {}).get("totalTokenCount")}


def check_job(job):
    if not isinstance(job, dict):
        return "a job is a JSON object"
    if not job.get("prompt") and not job.get("pages"):
        return "a job needs a prompt, pages or both"
    pages = job.get("pages") or []
    if len(pages) > MAX_PAGES:
        return f"at most {MAX_PAGES} pages"
    bad = [u for u in pages if not URL.match(str(u))]
    return f"pages must be public https addresses: {bad}" if bad else None


def shoot(pages, out):
    from playwright.sync_api import sync_playwright
    rows = []
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 430, "height": 932}, device_scale_factor=3, is_mobile=True,
                            has_touch=True, locale="en-US")
        for n, url in enumerate(pages, 1):
            page = ctx.new_page()
            row = {"n": n, "url": url, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
            try:
                try:
                    resp = page.goto(url, wait_until="networkidle", timeout=45000)
                except Exception:  # pages with endless trackers never go idle: take the loaded page instead
                    resp = page.goto(url, wait_until="load", timeout=45000)
                    page.wait_for_timeout(3000)
                page.wait_for_timeout(1500)
                page.screenshot(path=str(out / f"page-{n}.png"))
                page.screenshot(path=str(out / f"page-{n}-full.png"), full_page=True)
                row.update({"final": page.url, "status": resp.status if resp else None, "title": page.title()})
            except Exception as e:  # a page that will not load is recorded, not guessed at
                row["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            page.close()
            rows.append(row)
        b.close()
    return rows


def run(job_path, out_root, *, key, call=W._call, shooter=shoot):
    job = json.loads(Path(job_path).read_text(encoding="utf-8"))
    err = check_job(job)
    out = Path(out_root) / Path(job_path).stem
    out.mkdir(parents=True, exist_ok=True)
    if err:
        (out / "error.txt").write_text(err + "\n", encoding="utf-8")
        return 2
    code = 0
    if job.get("prompt"):
        try:
            t0 = time.monotonic()
            res = generate(job["prompt"], key=key, model=job.get("model") or DEFAULT_MODEL, call=call)
            res["seconds"] = round(time.monotonic() - t0, 1)  # wall time of the model call, said as "took N seconds"
            res.update({"prompt": job["prompt"], "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
            (out / "run.json").write_text(json.dumps(res, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        except W.GeminiError as e:
            (out / "error.txt").write_text(str(e) + "\n", encoding="utf-8")
            code = 1
    if job.get("pages"):
        rows = shooter(job["pages"], out)
        (out / "pages.json").write_text(json.dumps(rows, indent=1) + "\n", encoding="utf-8")
        code = code or (1 if any("error" in r for r in rows) else 0)
    return code


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("job")
    ap.add_argument("--out", default="video/studio/demos/out")
    a = ap.parse_args(argv)
    key = os.environ.get("GEMINI_API_KEY", "")
    job = json.loads(Path(a.job).read_text(encoding="utf-8"))
    if job.get("prompt") and not key:
        print("ai_demo: GEMINI_API_KEY is not set", file=sys.stderr)
        return 1
    return run(a.job, a.out, key=key)


if __name__ == "__main__":
    sys.exit(main())
