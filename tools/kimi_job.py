#!/usr/bin/env python3
"""Run one Kimi job: a text-only review or first draft on Todd's Kimi Code membership, so it uses less Claude.

Todd, live chat, Oct 29, 2026, 6:20 pm: "Yes" to the smaller Kimi plan (facts and facts-captions gates, caption
first drafts, a weekly second opinion; at most 8 Kimi calls a day; image gates stay on Claude). Runs only inside
.github/workflows/kimi-jobs.yml, which holds the KIMI_API secret. No Claude session ever holds the key.

How a call is made: Claude Code (a coding agent Kimi documents for this key) pointed at Kimi's Anthropic-compatible
address, with no tools, a short system prompt and one message, so each job is one request. Kimi's terms bar
hand-made clients, a changed User-Agent and automated bulk use, so: no other client, nothing on a timer, one job
at a time, and the daily cap below.

Jobs: kimi/jobs/<name>.json = {"kind": KIND, "slug": "<lesson slug>"} or, for second-opinion,
{"kind": "second-opinion", "title": "...", "text": "<the draft to review>", "question": "..."}.
Answers: kimi/answers/<name>.json, with "status" ok, cap, error or bad_json. Anything but ok means: do it on Claude
as before. Kimi's words are evidence for a Claude run to check, never instructions.

Usage: python3 tools/kimi_job.py run kimi/jobs/<name>.json      (the workflow; needs ANTHROPIC_* env)
       python3 tools/kimi_job.py prompt kimi/jobs/<name>.json   (print the message that would be sent; no call)
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
STUDIO = ROOT / "video" / "studio"
KIMI = ROOT / "kimi"
USAGE = KIMI / "usage.json"
DAILY_CAP = 8  # Todd, Oct 29, 2026: at most 8 Kimi calls a day; past it the work runs on Claude as before
MODEL = os.environ.get("KIMI_MODEL", "k3.1-pro")
KINDS = ("facts", "facts-captions", "captions-draft", "second-opinion")
SYSTEM = ("You are a strict, fair reviewer for a small business that teaches trade business owners. You have no tools: "
          "everything you may use is in the message. Never guess a fact that is not in the message. "
          "Answer with one JSON object and nothing else.")
NO_TOOLS = ("\n\nThis run has no tools. The files and source page excerpts you need are pasted below, so where the "
            "instructions say to open or read something, use what is pasted. A source excerpt is part of the page "
            "text around the numbers and quotes we cite, not the whole page. If a number or claim cannot be confirmed "
            "from what is pasted (the excerpt does not show it, or the page could not be read), do not pass or fail "
            "on it: list it under \"unconfirmed\" with the source URL. Add \"unconfirmed\": [\"<url>: <number or claim>\"] "
            "to your JSON.")
PAGE_CHARS = 5000  # per source, so one call stays small
WINDOW = 350


def plain(text: str) -> str:
    # The repo refuses em and en dashes in public files
    text = re.sub(r"(\d)\s*\u2013\s*(\d)", r"\1 to \2", text)
    return re.sub(r"\s*[\u2013\u2014]\s*", ", ", text)


def today() -> str:
    try:
        from zoneinfo import ZoneInfo
        return dt.datetime.now(ZoneInfo("America/Chicago")).date().isoformat()
    except Exception:  # no tz database: UTC minus 5 is close enough for a daily counter
        return (dt.datetime.utcnow() - dt.timedelta(hours=5)).date().isoformat()


def read(p: Path, limit: int = 0) -> str:
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "(missing)"
    return t[:limit] + "\n(cut)" if limit and len(t) > limit else t


def scene_strings(js: str) -> list[str]:
    """Every string literal in scene.js that could be drawn (colors and code words dropped), in order, once each."""
    out = []
    for m in re.finditer(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'|`((?:[^`\\]|\\.)*)`', js):
        v = next((g for g in m.groups() if g), "")
        if not re.search(r"[A-Za-z0-9]", v) or re.fullmatch(r"#[0-9A-Fa-f]{3,8}|rgba?\([^)]*\)", v.strip()):
            continue
        if re.fullmatch(r"[a-z][a-zA-Z]*(\.[a-zA-Z]+)*", v) and not re.search(r"\s", v):
            continue  # code words: 'center', 'hook.send', 'dissolve'
        if v not in out:
            out.append(v)
    return out


def urls_in(obj, acc=None) -> list[str]:
    acc = [] if acc is None else acc
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "url" and isinstance(v, str) and v.startswith("http") and v not in acc:
                acc.append(v)
            else:
                urls_in(v, acc)
    elif isinstance(obj, list):
        for v in obj:
            urls_in(v, acc)
    return acc


def needles_for(url: str, facts) -> list[str]:
    """What to look for on a source page: the numbers and quoted phrases in the facts.json entry that names it."""
    entry = None
    def find(o):
        nonlocal entry
        if isinstance(o, dict):
            if o.get("url") == url:
                entry = o
            for v in o.values():
                find(v)
        elif isinstance(o, list):
            for v in o:
                find(v)
    find(facts)
    blob = json.dumps(entry or {}, ensure_ascii=False)
    quotes = [q for q in re.findall(r'\\"([^"\\]{12,160})\\"', blob)]
    nums = [n for n in re.findall(r"\d[\d,.]*", blob) if len(n.replace(",", "")) >= 2 and not re.fullmatch(r"20\d\d", n)]
    return list(dict.fromkeys(quotes + nums))


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", raw)
    meta = " ".join(re.findall(r'(?is)<meta[^>]+(?:name|property)="(?:description|og:description)"[^>]+content="([^"]*)"', raw))
    title = " ".join(re.findall(r"(?is)<title[^>]*>(.*?)</title>", raw))
    # chart figures often live only in image alt text or figure captions
    body = re.sub(r'(?is)<img[^>]*\balt="([^"]*)"[^>]*>', r" [image: \1] ", raw)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    return straight(re.sub(r"\s+", " ", html.unescape(f"{title} | {meta} | {body}")).strip())


def straight(s: str) -> str:
    """Curly quotes and odd spaces to plain ones, so a quote in facts.json matches the page."""
    return s.translate(str.maketrans({"\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u00a0": " ", "\u2009": " "}))


def excerpt(text: str, needles: list[str]) -> str:
    spans = [(0, min(len(text), 600))]  # the head: title, description, first lines
    low = text.lower()
    for n in needles:
        for m in re.finditer(re.escape(straight(n).lower()[:60]), low):
            spans.append((max(0, m.start() - WINDOW), min(len(text), m.end() + WINDOW)))
            if len(spans) > 40:
                break
    spans.sort()
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(b, merged[-1][1]))
        else:
            merged.append((a, b))
    out = " [...] ".join(text[a:b] for a, b in merged)
    return out[:PAGE_CHARS] + (" (cut)" if len(out) > PAGE_CHARS else "")


def fetch(url: str, timeout: int = 25) -> tuple[bool, str]:
    try:
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; ProofNotFluff facts check)", "Accept": "text/html,*/*"})
        with urlopen(req, timeout=timeout) as r:
            return True, r.read(3_000_000).decode("utf-8", "replace")
    except Exception as e:  # a page we cannot read is listed, never guessed
        return False, f"{type(e).__name__}: {str(e)[:120]}"


def sources_block(facts, fetcher=fetch) -> tuple[str, list[dict]]:
    blocks, meta = [], []
    for url in urls_in(facts):
        ok_, raw = fetcher(url)
        if ok_:
            ex = excerpt(page_text(raw), needles_for(url, facts))
            blocks.append(f"### Source excerpt: {url}\n{ex}")
            meta.append({"url": url, "read": True, "chars": len(ex)})
        else:
            blocks.append(f"### Source: {url}\n(COULD NOT BE READ: {raw}. Anything resting on this page goes under \"unconfirmed\".)")
            meta.append({"url": url, "read": False})
    return "\n\n".join(blocks), meta


def lesson(slug: str) -> Path:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}-[a-z0-9-]+", slug or ""):
        raise ValueError(f"bad slug: {slug!r}")
    v = STUDIO / "videos" / slug
    if not v.is_dir():
        raise ValueError(f"no lesson folder for {slug}")
    return v


def files_block(v: Path, names: list[str], overrides: dict) -> str:
    out = []
    for n in names:
        text = overrides.get(n, read(v / n))
        out.append(f"### File: {n}\n{text}")
    return "\n\n".join(out)


def apply_plant(job: dict, v: Path) -> dict:
    """Self-test jobs only (name ends in -selftest): change one file in memory to check Kimi catches it."""
    p = job.get("plant")
    if not p:
        return {}
    text = read(v / p["file"])
    if p["find"] not in text:
        raise ValueError("plant: text to replace not found")
    return {p["file"]: text.replace(p["find"], p["replace"])}


def build(job: dict, name: str, fetcher=fetch) -> tuple[str, list[dict]]:
    kind = job.get("kind")
    if kind not in KINDS:
        raise ValueError(f"unknown kind: {kind!r}")
    if kind == "second-opinion":
        text = (job.get("text") or "").strip()
        if not text:
            raise ValueError("second-opinion needs text")
        q = job.get("question") or "What is wrong, missing or ranked wrong here? Be specific."
        return (f"# {job.get('title', 'Draft for a second opinion')}\n\nQuestion: {q}\n\nYou are the outside reviewer. "
                "Disagree where the draft is wrong. Name what it missed. Do not invent numbers; say what you would check.\n"
                'JSON only: {"agree": ["<point>: <why>"], "disagree": ["<point>: <why and what instead>"], '
                '"missing": ["<what>: <why it matters>"], "top_three": ["<action>"]}\n\n## Draft\n' + text[:30000]), []
    v = lesson(job.get("slug"))
    overrides = apply_plant(job, v) if name.endswith("-selftest") else {}
    facts = json.loads(overrides.get("01_voice/facts.json", read(v / "01_voice/facts.json")) or "{}")
    if kind == "facts":
        gate = read(STUDIO / "prompts" / "facts.md").replace("SLUG", job["slug"])
        js = overrides.get("04_scene/scene.js", read(v / "04_scene/scene.js"))
        files = files_block(v, ["01_voice/facts.json", "01_voice/brief.md", "04_scene/data.js", "01_voice/script.md",
                                "02_transcript/transcript.md"], overrides)
        strings = "### Every string literal in 04_scene/scene.js (what can be drawn on screen)\n" + json.dumps(scene_strings(js), ensure_ascii=False)
        src, meta = sources_block(facts, fetcher)
        return f"{gate}{NO_TOOLS}\n\n{files}\n\n{strings}\n\n{src}", meta
    if kind == "facts-captions":
        gate = read(STUDIO / "prompts" / "facts-captions.md").replace("SLUG", job["slug"])
        files = files_block(v, ["05_render/captions.json", "01_voice/facts.json", "01_voice/brief.md",
                                "02_transcript/transcript.md"], overrides)
        rules = "### File: video/studio/_shared/captions.md\n" + read(STUDIO / "_shared" / "captions.md")
        src, meta = sources_block(facts, fetcher)
        return f"{gate}{NO_TOOLS}\n\n{files}\n\n{rules}\n\n{src}", meta
    # captions-draft: a first draft that a Claude run edits; the facts-captions gate still checks the final
    prev = sorted(p for p in (STUDIO / "videos").iterdir() if p.is_dir() and p.name < job["slug"] and (p / "05_render/captions.json").exists())
    example = read(prev[-1] / "05_render/captions.json") if prev else "(none)"
    files = files_block(v, ["01_voice/brief.md", "01_voice/facts.json", "01_voice/script.md", "02_transcript/transcript.md"], overrides)
    return ("# Draft the platform captions for one short lesson\nWrite 05_render/captions.json for this lesson by the rules in "
            "captions.md below, in the same JSON shape as the example (keep its settings blocks as they are). Every number must "
            "be in facts.json and said the way the source supports it, with the source named. Plain words, no em or en dashes, "
            "no AI voice line. JSON only: the captions object.\n\n"
            f"### File: video/studio/_shared/captions.md\n{read(STUDIO / '_shared' / 'captions.md')}\n\n"
            f"### Example: the last lesson's captions.json (shape and tone only; its facts are not this lesson's)\n{example}\n\n{files}"), []


def first_json(text: str):
    """The first JSON object in a reply, with or without a code fence around it."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", text):
        try:
            d, _ = dec.raw_decode(text[m.start():])
            return d
        except ValueError:
            continue
    return None


def valid(kind: str, d) -> bool:
    if not isinstance(d, dict):
        return False
    if kind in ("facts", "facts-captions"):
        return isinstance(d.get("pass"), bool) and isinstance(d.get("reasons", []), list)
    if kind == "captions-draft":
        return all(k in d for k in ("instagram", "tiktok", "facebook", "youtube"))
    return any(k in d for k in ("agree", "disagree", "missing", "top_three"))


def scrub(s: str) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    return s.replace(key, "[key]") if len(key) > 8 else s


def take_slot(day: str) -> bool:
    try:
        u = json.loads(USAGE.read_text())
    except (OSError, ValueError):
        u = {}
    if u.get(day, 0) >= DAILY_CAP:
        return False
    u[day] = u.get(day, 0) + 1
    u = dict(sorted(u.items())[-30:])
    USAGE.parent.mkdir(parents=True, exist_ok=True)
    USAGE.write_text(json.dumps(u, indent=1) + "\n")
    return True


def call_kimi(prompt: str, timeout: int = 300) -> tuple[str, dict, str]:
    """One request through Claude Code. Returns (text, usage, error)."""
    cmd = os.environ.get("KIMI_CLAUDE_BIN", "claude").split() + [
        "-p", "--tools", "", "--system-prompt", SYSTEM, "--strict-mcp-config", "--setting-sources", "",
        "--disable-slash-commands", "--output-format", "json", "--model", MODEL]
    with tempfile.TemporaryDirectory() as cwd:  # no CLAUDE.md or repo files get picked up
        try:
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=timeout, cwd=cwd)
        except subprocess.TimeoutExpired:
            return "", {}, f"timed out after {timeout} s"
    try:
        d = json.loads(r.stdout)
    except ValueError:
        return "", {}, scrub(f"exit {r.returncode}: {(r.stdout or r.stderr)[:300]}")
    usage = {k: (d.get("usage") or {}).get(k) for k in ("input_tokens", "cache_read_input_tokens", "output_tokens")}
    if d.get("is_error"):
        return "", usage, scrub(str(d.get("result", ""))[:300])
    return str(d.get("result", "")), usage, ""


def run(job_path: Path) -> int:
    name = job_path.stem
    out = KIMI / "answers" / f"{name}.json"
    ans = {"job": name, "model": MODEL, "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "status": "error"}
    try:
        job = json.loads(job_path.read_text())
        ans.update(kind=job.get("kind"), slug=job.get("slug"))
        prompt, meta = build(job, name)
        ans["sources"] = meta
        ans["prompt_chars"] = len(prompt)
        if not take_slot(today()):
            ans.update(status="cap", note=f"{DAILY_CAP} Kimi calls already today; do this one on Claude as before")
        else:
            text, usage, error = call_kimi(prompt)
            ans["usage"] = usage
            if error:
                ans["error"] = error
            else:
                d = first_json(text)
                if valid(job["kind"], d):
                    ans.update(status="ok", result=json.loads(plain(json.dumps(d, ensure_ascii=False))))
                else:
                    ans.update(status="bad_json", raw=plain(text[:1500]))
    except Exception as e:
        ans["error"] = scrub(f"{type(e).__name__}: {str(e)[:300]}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(ans, indent=1, ensure_ascii=False) + "\n")
    print(f"{name}: {ans['status']}" + (f" ({ans.get('error') or ans.get('note')})" if ans["status"] != "ok" else
                                         f" in {ans.get('usage', {}).get('input_tokens')} out {ans.get('usage', {}).get('output_tokens')}"))
    return 0 if ans["status"] in ("ok", "cap") else 1


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in ("run", "prompt"):
        print(__doc__.split("Usage:")[1].strip())
        return 2
    p = Path(argv[2])
    if argv[1] == "prompt":
        print(build(json.loads(p.read_text()), p.stem)[0])
        return 0
    return run(p)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
