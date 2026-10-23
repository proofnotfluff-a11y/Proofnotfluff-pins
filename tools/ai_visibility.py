#!/usr/bin/env python3
"""AI visibility check (radar, Todd, Oct 23, 2026: "a new leading form of search is no longer Google search, but it's
people inquiring about these products on AI").

seo/AI_QUESTIONS.json holds the questions our buyers ask, a few per live product. Each week the radar run asks every
question to an assistant that can search the web (a fresh Claude subagent with web search that is never told about
ProofNotFluff), and saves each raw answer with the URLs it cited to data/work/aivis-<date>.json (gitignored: answers can
name other businesses). This tool scores those answers in code and keeps only booleans and domains:
  mentioned  the answer names ProofNotFluff or proofnotfluff.com
  cited      a cited URL is on proofnotfluff.com
  domains    the cited domains, so we see who the assistants send our buyers to
Assistants we cannot ask within their terms (automated use of the ChatGPT, Perplexity and Gemini apps is not allowed;
Google AI Overviews has no API) are recorded as "not measured", never guessed.

Writes seo/ai-visibility/<date>.json, a trend line in seo/AI_VISIBILITY.md and data/work/aivis-scoreboard.json (the
scoreboard meta/aivis doc the run writes with ArtifactData).

Usage: python3 tools/ai_visibility.py --questions          print the questions to ask, as JSON
       python3 tools/ai_visibility.py --score data/work/aivis-<date>.json
       python3 tools/ai_visibility.py --selftest
"""
import argparse, datetime as dt, json, os, re, sys, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QFILE = os.path.join(ROOT, "seo", "AI_QUESTIONS.json")
OUTDIR = os.path.join(ROOT, "seo", "ai-visibility")
TREND = os.path.join(ROOT, "seo", "AI_VISIBILITY.md")
BOARD = os.path.join(ROOT, "data", "work", "aivis-scoreboard.json")
NAME = re.compile(r"proof\s*not\s*fluff|proofnotfluff\.com", re.I)
NOT_MEASURED = {"chatgpt": "OpenAI's terms bar automated use of ChatGPT; no free web-search API",
                "perplexity": "Perplexity's terms bar automated queries of its app; its API is paid",
                "gemini": "the free Gemini key has search grounding off, so it cannot show citations",
                "google-ai-overviews": "no API; Search Console does not split AI Overview clicks out"}


def domain(u):
    try:
        h = urllib.parse.urlparse(u).hostname or ""
    except ValueError:
        return ""
    return h[4:] if h.startswith("www.") else h


def score(rows):
    out = []
    for r in rows:
        urls = [u for u in (r.get("urls") or []) if isinstance(u, str)]
        doms = sorted({domain(u) for u in urls if domain(u)})
        out.append({"id": r.get("id"), "product": r.get("product"), "assistant": r.get("assistant", "claude-web"),
                    "mentioned": bool(NAME.search(r.get("answer") or "")) or "proofnotfluff.com" in doms,
                    "cited": "proofnotfluff.com" in doms, "domains": doms})
    return out


def summarize(scored, date):
    asked = len(scored)
    by = {}
    for s in scored:
        b = by.setdefault(s["product"], {"asked": 0, "mentioned": 0, "cited": 0})
        b["asked"] += 1
        b["mentioned"] += s["mentioned"]
        b["cited"] += s["cited"]
    doms = {}
    for s in scored:
        for d in s["domains"]:
            doms[d] = doms.get(d, 0) + 1
    top = sorted(doms.items(), key=lambda x: -x[1])[:8]
    return {"schema": "pnf.aivis.v1", "date": date, "asked": asked, "mentioned": sum(s["mentioned"] for s in scored),
            "cited": sum(s["cited"] for s in scored), "byProduct": by, "topDomains": [{"domain": d, "answers": n} for d, n in top],
            "measured": sorted({s["assistant"] for s in scored}), "notMeasured": NOT_MEASURED}


def write(rows, date):
    scored = score(rows)
    summ = summarize(scored, date)
    os.makedirs(OUTDIR, exist_ok=True)
    json.dump({**summ, "answers": scored}, open(os.path.join(OUTDIR, f"{date}.json"), "w", encoding="utf-8"), indent=1)
    head = ["# AI visibility (radar)", "", "Each week the radar run asks the questions in seo/AI_QUESTIONS.json to Claude with web search and tools/ai_visibility.py",
            "scores the answers: mentioned (names us) and cited (links us). ChatGPT, Perplexity, Gemini and Google AI Overviews are not measured",
            "(reasons in each seo/ai-visibility/<date>.json). Newest last.", "",
            "| Date | Asked | Mentioned | Cited | Top cited domains |", "|---|---|---|---|---|"]
    old = open(TREND, encoding="utf-8").read().splitlines() if os.path.exists(TREND) else head
    rows_md = [l for l in old if l.startswith("| 20") and not l.startswith(f"| {date} ")]
    line = f"| {date} | {summ['asked']} | {summ['mentioned']} | {summ['cited']} | {', '.join(d['domain'] for d in summ['topDomains'][:4])} |"
    open(TREND, "w", encoding="utf-8").write("\n".join(head + rows_md + [line]) + "\n")
    trend = [{"date": l.split("|")[1].strip(), "asked": int(l.split("|")[2]), "mentioned": int(l.split("|")[3]), "cited": int(l.split("|")[4])}
             for l in rows_md + [line]][-12:]
    os.makedirs(os.path.dirname(BOARD), exist_ok=True)
    json.dump({k: summ[k] for k in ("date", "asked", "mentioned", "cited", "byProduct", "topDomains", "measured")} |
              {"notMeasured": list(NOT_MEASURED), "trend": trend, "updatedAt": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")},
              open(BOARD, "w", encoding="utf-8"), indent=1)
    return summ


def questions():
    q = json.load(open(QFILE, encoding="utf-8"))
    return [x for x in q["questions"] if x.get("active", True)]


def selftest():
    rows = [{"id": "q1", "product": "a", "answer": "Try ProofNotFluff's weekly list.", "urls": ["https://proofnotfluff.com/a/"]},
            {"id": "q2", "product": "a", "answer": "Use BuildZoom.", "urls": ["https://www.buildzoom.com/x", "https://www.buildzoom.com/y"]},
            {"id": "q3", "product": "b", "answer": "Proof Not Fluff has a sample page.", "urls": []},
            {"id": "q4", "product": "b", "answer": "No idea.", "urls": ["not a url"]}]
    s = score(rows)
    summ = summarize(s, "2026-10-23")
    cases = [("cited by link", s[0]["cited"] and s[0]["mentioned"]), ("not mentioned", not s[1]["mentioned"] and not s[1]["cited"]),
             ("www stripped", s[1]["domains"] == ["buildzoom.com"]), ("mentioned by name with spaces", s[2]["mentioned"] and not s[2]["cited"]),
             ("bad url ignored", s[3]["domains"] == []), ("totals", (summ["asked"], summ["mentioned"], summ["cited"]) == (4, 2, 1)),
             ("by product", summ["byProduct"]["a"] == {"asked": 2, "mentioned": 1, "cited": 1}),
             ("no answer text kept", "answer" not in json.dumps(s)), ("not measured listed", "chatgpt" in summ["notMeasured"])]
    bad = [c for c, ok in cases if not ok]
    for c in bad:
        print("FAIL", c)
    print(f"{'OK' if not bad else 'ERROR'} ai_visibility selftest: {len(cases) - len(bad)} of {len(cases)} planted cases right")
    return not bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", action="store_true")
    ap.add_argument("--score")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(0 if selftest() else 1)
    if a.questions:
        print(json.dumps(questions(), indent=1))
        return
    if a.score:
        rows = json.load(open(a.score, encoding="utf-8"))
        date = re.search(r"(\d{4}-\d{2}-\d{2})", a.score)
        summ = write(rows, date.group(1) if date else dt.date.today().isoformat())
        print(f"OK aivis {summ['date']}: asked {summ['asked']}, mentioned {summ['mentioned']}, cited {summ['cited']}; "
              f"top domains {', '.join(d['domain'] for d in summ['topDomains'][:5])}")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
