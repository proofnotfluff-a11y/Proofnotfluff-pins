#!/usr/bin/env python3
"""Proof Check spec lint: the content playbook's hard rules for a short video spec, checked in code before any model
reviews the video (cmo/CONTENT_PLAYBOOK.md sections 2 to 4). Rule from Todd's Oct 15 notes on agent pipelines: code
decides wherever it can, and the fresh reviewer (the cold viewer) judges only what code cannot, such as whether a
stranger understands the story or whether each number matches the product.

Who runs it:
  make_demo.py   on every --format short render: a spec that breaks a rule is refused before rendering
  check_repo.py  as the video-specs check on every committed spec in promo/specs/ (CI and the nightly optimizer)

Rules (a spec with a "formula" key; from Oct 16, 2026 every dated short spec must have one):
  formula one of the four, series "Proof Check", the kicker (spec "audience") "PROOF CHECK #<n> . <NAME>"
  hook_say_short at most 8 words; the headline holds 1 or 2 numbers; 4 to 6 rows; at most one ask beat, its pause
  1.2 to 1.5 s; F2: the ask is "Spot the mistake?" and the next line starts "The mistake"; F3: the ask is a question;
  F4: the hook says "free calculator"; the close "<verb> free at ProofNotFluff dot com." spoken exactly once; end card
  button "Free calculator", sub "proofnotfluff.com", what "Free online. Full <thing> $2.99 on Etsy"; no em dash;
  no invented people; no AI-sounding phrase (tools/voice_lint.py); Reel caption with "Link in bio: proofnotfluff.etsy.com" and 3 to 5 hashtags; TikTok caption
  with "Search ProofNotFluff on Etsy".

Usage: python3 tools/spec_lint.py spec.json [spec.json ...]    one line per problem, exit 1 if any
"""
import json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

FORMULAS = {"F1 Job Ticket": "F1", "F2 Spot the Mistake": "F2", "F3 Myth vs Math": "F3", "F4 Run Your Numbers": "F4"}
START = "2026-10-16"  # from this date every dated short spec is a Proof Check episode
NUM = re.compile(r"\$?\d[\d,]*(?:\.\d+)?%?")
KICKER = re.compile(r"^PROOF CHECK(?: #\d+)? · [A-Z0-9][A-Z0-9 ,'&?-]*$")
CTA_SAY = re.compile(r"^[A-Z][A-Za-z' ]+ free at ProofNotFluff dot com\.$")
CTA_WHAT = re.compile(r"^Free online\. Full [a-z ]+ \$2\.99 on Etsy$")
PEOPLE = re.compile(r"client of mine|a client I|\bI once\b|my customers? (?:told|said)|a shop owner I know|a friend of mine", re.I)
HASHTAG = re.compile(r"(?<![\w&])#[A-Za-z]\w*")


def strip(text):
    return re.sub(r"<[^>]+>", "", text or "")


def spoken(spec):
    lines = [spec.get("hook_say_short", ""), spec.get("hook_say", "")]
    for r in spec.get("rows", []):
        lines += [r.get("say", ""), r.get("ask", "")]
    lines += [(spec.get("fix") or {}).get("say", ""), (spec.get("cta") or {}).get("say", "")]
    return [l for l in lines if l]


def problems(spec, path=""):
    """Every rule the spec breaks, as short lines. An undated or older spec without a formula is not checked."""
    out = []
    formula = spec.get("formula")
    dated = re.match(r"(\d{4}-\d{2}-\d{2})-", os.path.basename(path or ""))
    if not formula:
        if dated and dated.group(1) >= START:
            out.append(f"no formula: from {START} every short is a Proof Check episode (add formula and series, "
                       "cmo/CONTENT_PLAYBOOK.md section 2)")
        return out
    code = FORMULAS.get(formula)
    if not code:
        out.append(f"formula {formula!r} is not one of {', '.join(FORMULAS)}")
    if spec.get("series") != "Proof Check":
        out.append(f"series is {spec.get('series')!r}, not 'Proof Check'")
    if not KICKER.match(spec.get("audience", "")):
        out.append(f"kicker (audience) {spec.get('audience')!r} must read 'PROOF CHECK #<n> · FOR <WHO>'")
    # Todd, Oct 15, watching Proof Check #1: "I don't understand what the product is and what use case it's for".
    if not re.search(r"· FOR [A-Z]", spec.get("audience", "")):
        out.append("kicker must say who it is for: 'PROOF CHECK #<n> · FOR <WHO>' (e.g. FOR FREELANCERS, FOR CLEANING BUSINESSES)")
    if not (spec.get("pitch") or {}).get("say"):
        out.append("no pitch: the end card needs one spoken line saying what the product is and what you do with it")
    if not spec.get("cta", {}).get("use"):
        out.append("no cta.use: the end card needs one plain line saying what the product does for the viewer")
    hss = spec.get("hook_say_short", "")
    if not hss:
        out.append("no hook_say_short: frame one needs its spoken line")
    elif len(hss.split()) > 8:
        out.append(f"hook_say_short is {len(hss.split())} words (at most 8, said by 3 s): {hss!r}")
    nums = NUM.findall(strip(spec.get("hook", "")))
    if not 1 <= len(nums) <= 2:
        out.append(f"the headline holds {len(nums)} numbers {nums} (it leads with one setup number, at most one more)")
    rows = spec.get("rows", [])
    if not 4 <= len(rows) <= 6:
        out.append(f"{len(rows)} rows (4 to 6, plus at most one ask beat and one fix)")
    asks = [i for i, r in enumerate(rows) if r.get("ask")]
    if len(asks) > 1:
        out.append(f"{len(asks)} ask beats (at most one)")
    for i in asks:
        p = rows[i].get("pause")
        if not isinstance(p, (int, float)) or not 1.2 <= p <= 1.5:
            out.append(f"row {i + 1}: the ask's pause is {p!r} (1.2 to 1.5 s)")
    if code == "F2":
        if len(asks) != 1 or rows[asks[0]].get("ask") != "Spot the mistake?":
            out.append("F2 needs exactly one ask, 'Spot the mistake?'")
        elif asks[0] + 1 >= len(rows) or not rows[asks[0] + 1].get("say", "").startswith("The mistake"):
            out.append("F2: the line after the ask must name it, starting 'The mistake'")
    if code == "F3" and (len(asks) != 1 or not rows[asks[0]].get("ask", "").rstrip().endswith("?")):
        out.append("F3 needs exactly one ask that poses the myth as a question")
    if code == "F4" and "free calculator" not in " ".join([strip(spec.get("hook", "")), hss, spec.get("hook_say", "")]).lower():
        out.append("F4: the hook must say 'free calculator'")
    cta = spec.get("cta") or {}
    if not CTA_SAY.match(cta.get("say", "")):
        out.append(f"the close {cta.get('say')!r} must read '<verb> free at ProofNotFluff dot com.'")
    if cta.get("button") != "Free calculator":
        out.append(f"end card button {cta.get('button')!r} must be 'Free calculator'")
    if cta.get("sub") != "proofnotfluff.com":
        out.append(f"end card sub {cta.get('sub')!r} must be 'proofnotfluff.com'")
    if not CTA_WHAT.match(cta.get("what", "")):
        out.append(f"end card what {cta.get('what')!r} must read 'Free online. Full <workbook or tracker> $2.99 on Etsy'")
    said = sum(l.count("ProofNotFluff dot com") for l in spoken(spec))
    if said != 1:
        out.append(f"the close is spoken {said} times (exactly once, at the end)")
    text = json.dumps(spec, ensure_ascii=False)
    if "—" in text:
        out.append("an em dash")
    m = PEOPLE.search(text)
    if m:
        out.append(f"an invented person ({m.group(0)!r}): examples are worked examples, 'Say you...'")
    import voice_lint  # direct, human words (Todd's standing rule): tells of AI-written copy, in code
    shown = spoken(spec) + [strip(spec.get("hook", ""))] + [str(v) for v in (spec.get("post") or {}).values()]
    for name, words in voice_lint.tells("\n".join(shown)):
        out.append(f"AI-sounding phrase: {name} ({words.strip()!r})")
    post = spec.get("post") or {}
    reel = post.get("reel_caption", "")
    if "Link in bio: proofnotfluff.etsy.com" not in reel:
        out.append("the Reel caption lacks 'Link in bio: proofnotfluff.etsy.com'")
    tags = HASHTAG.findall(reel)
    if not 3 <= len(tags) <= 5:
        out.append(f"the Reel caption has {len(tags)} hashtags (3 to 5)")
    if "Search ProofNotFluff on Etsy" not in post.get("tiktok_caption", ""):
        out.append("the TikTok caption lacks 'Search ProofNotFluff on Etsy'")
    return out


def main():
    bad = 0
    for p in sys.argv[1:]:
        try:
            spec = json.load(open(p, encoding="utf-8"))
        except Exception as e:
            print(f"{p}: does not parse ({str(e)[:80]})"); bad += 1; continue
        for line in problems(spec, p):
            print(f"{p}: {line}"); bad += 1
    print(f"spec_lint: {bad} problem{'s' if bad != 1 else ''}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
