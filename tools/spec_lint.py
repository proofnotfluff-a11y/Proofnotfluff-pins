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
  no invented people; no AI-sounding phrase (tools/voice_lint.py); no hype or fake urgency ("secret", "stolen",
  "last chance", "only 3 left"; playbook rule 11); Reel caption with "Link in bio: proofnotfluff.etsy.com" and 3 to 5 hashtags; TikTok caption
  with "Search ProofNotFluff on Etsy".

PIVOT (Todd's "Go", Oct 15, 9:55 pm; coo/PIVOT.md): a spec dated from Oct 16 points at the free site, not Etsy. Its
  kicker names an e-commerce audience (FOR E-COMMERCE BRANDS, FOR SHOPIFY SELLERS, FOR AMAZON SELLERS...); end card
  what "Free online. No sign-up." or, once the kit is live, "Free online. Full <thing> $<29 to 199>"; Reel caption
  with "Free calculator: link in bio (proofnotfluff.com)"; TikTok caption with "Free calculator at proofnotfluff.com";
  neither caption mentions Etsy.

HEARD (Todd, Oct 17, after Proof Check #3 said "at five-ten cost": "No one would say that. They'd say five dollars and
  ten cents ... make sure the wording sounds human and is quality checked"; cmo/CONTENT_PLAYBOOK.md section 9 rule 3):
  the lines ElevenLabs reads (each "tts", else the caption) are checked as heard, on every spec dated from Oct 18
  and every undated example:
    - every dollar amount the caption shows is said with "dollars", "bucks", "grand" or "cents";
    - no run-together number pairs ("five-ten", "six sixty-three", "two ninety-eight", "fifteen sixty-six"): a
      listener can't tell a price from a time or two numbers;
    - no digits or "$" left in a heard line (ElevenLabs reads them unpredictably; spell them as spoken);
    - at most two audio tags per video.
  Reviewers and the cold viewer get these heard lines (python3 tools/spec_lint.py --heard spec.json; make_demo.py
  prints them as "spoken"), not the captions.

Usage: python3 tools/spec_lint.py spec.json [spec.json ...]    one line per problem, exit 1 if any
       python3 tools/spec_lint.py --heard spec.json              the lines as the viewer hears them, in order
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
# The pivot (coo/PIVOT.md): from this date every dated short is for e-commerce brands and points at the free site.
PIVOT = "2026-10-16"
PIVOT_WHO = re.compile(r"· FOR [A-Z0-9 ,'&-]*(?:E-?COMMERCE|SHOPIFY|AMAZON|TIKTOK SHOP|ETSY SELLERS|WHOLESALE|RETAIL"
                       r"|ONLINE (?:SELLERS|SHOPS|STORES|BRANDS)|PRODUCT (?:BRANDS|BUSINESSES|SELLERS)"
                       r"|(?:SMALL|CONSUMER|DTC) BRANDS)")
SITE_WHAT = "Free online. No sign-up."
# ElevenLabs narration on every Proof Check from Oct 16 (cmo/CONTENT_PLAYBOOK.md section 9; Todd, Oct 16: the offline
# voice sounds robotic and every improvement must reach every task).
EL_VOICES = {"iP95p4xoKVk53GoZ742B": "Chris", "CwhRBWXzGAHq8TQ4Fs17": "Roger", "cjVigY5qzO86Huf0OWal": "Eric",
             "XrExE9yKIg1WjnnlVkGX": "Matilda", "pqHfZKP75CvOlQylNhV4": "Bill"}
PREMIUM_WHAT = re.compile(r"^Free online\. Full [a-z0-9 -]+ \$(\d{2,3})$")
REEL_SITE = "Free calculator: link in bio (proofnotfluff.com)"
TIKTOK_SITE = "Free calculator at proofnotfluff.com"
# Honest framing (cmo/CONTENT_PLAYBOOK.md rule 11): no fake secrecy, no fake urgency or scarcity.
HYPE = re.compile(r"\b(?:secrets?|stolen|leaked|they don't want you to know|last chance|act now|hurry|"
                  r"only \d+ (?:left|spots?|copies)|before it's gone|limited time)\b", re.I)


HEARD_START = "2026-10-18"  # the heard-line rules bind specs dated from here (Proof Check #3, Oct 17, is published)
_UNITS = "one two three four five six seven eight nine".split()
_TEENS = "ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
_TENS = "twenty thirty forty fifty sixty seventy eighty ninety".split()
_SMALL = rf"(?:(?:{'|'.join(_TENS)})(?:-(?:{'|'.join(_UNITS)}))?|{'|'.join(_TEENS)}|{'|'.join(_UNITS)})"
_BIG = rf"(?:(?:{'|'.join(_TENS)})(?:-(?:{'|'.join(_UNITS)}))?|{'|'.join(_TEENS)})"
# a number word run straight into another number of ten or more: "five-ten", "six sixty-three", "two ninety-eight"
RUN_TOGETHER = re.compile(rf"\b{_SMALL}[- ]{_BIG}\b", re.I)
MONEY_WORD = re.compile(r"\b(?:dollars?|bucks?|grand|cents?)\b", re.I)
TAG = re.compile(r"\[[a-z ]+\]", re.I)


def heard_lines(spec):
    """(caption, heard) for every spoken line of a short, in make_demo's order (tools/el_voice.py lines)."""
    import el_voice
    return [(x["text"], x["tts"]) for x in el_voice.lines(spec, "short")]


def heard_problems(spec):
    out = []
    pairs = heard_lines(spec)
    tags = 0
    for cap, tts in pairs:
        spoken = TAG.sub("", tts)
        tags += len(TAG.findall(tts))
        amounts = len(re.findall(r"\$\s*\d", cap))
        if amounts > len(MONEY_WORD.findall(spoken)):
            out.append(f"heard line {tts!r} drops a money word: the caption shows {amounts} dollar amount(s), so "
                       "each is said with 'dollars', 'bucks', 'grand' or 'cents' (e.g. $5.10 is 'five dollars and ten cents')")
        m = RUN_TOGETHER.search(spoken)
        if m:
            out.append(f"heard line {tts!r} runs two numbers together ({m.group(0)!r}): say it the way a person "
                       "would, e.g. 'five dollars and ten cents', 'six hundred sixty-three dollars'")
        if re.search(r"[\d$]", spoken):
            out.append(f"heard line {tts!r} still has digits or '$': spell the number the way it is spoken")
    if tags > 2:
        out.append(f"{tags} audio tags (at most two per video)")
    return out


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
    if spec.get("schema") == "pnf.video.spec.v1":   # the video engine's Rat check formula (blueprint gate 1)
        return rat_check_problems(spec, path)
    out = []
    formula = spec.get("formula")
    dated = re.match(r"(\d{4}-\d{2}-\d{2})-", os.path.basename(path or ""))
    if not formula:
        if dated and dated.group(1) >= START:
            out.append(f"no formula: from {START} every short is a Proof Check episode (add formula and series, "
                       "cmo/CONTENT_PLAYBOOK.md section 2)")
        return out
    pivot = bool(dated) and dated.group(1) >= PIVOT
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
    elif pivot and not PIVOT_WHO.search(spec.get("audience", "")):
        out.append(f"kicker {spec.get('audience')!r} must name an e-commerce audience from Oct 16 (FOR E-COMMERCE BRANDS, "
                   "FOR SHOPIFY SELLERS, FOR AMAZON SELLERS, FOR ETSY SELLERS, FOR ONLINE SELLERS...; coo/PIVOT.md)")
    if pivot and spec.get("el_voice") not in EL_VOICES:
        out.append(f"el_voice {spec.get('el_voice')!r} is not one of the five ElevenLabs voices "
                   f"({', '.join(EL_VOICES.values())}); every Proof Check is narrated by ElevenLabs (tools/el_voice.py)")
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
    what = cta.get("what", "")
    m = PREMIUM_WHAT.match(what)
    premium_ok = bool(m) and 29 <= int(m.group(1)) <= 199
    if pivot:
        if what != SITE_WHAT and not premium_ok:
            out.append(f"end card what {what!r} must read '{SITE_WHAT}' or, once the kit is live, "
                       "'Free online. Full 13-week workbook $79' (coo/PIVOT.md)")
    elif not CTA_WHAT.match(what) and what != SITE_WHAT and not premium_ok:
        out.append(f"end card what {what!r} must read 'Free online. Full <workbook or tracker> $2.99 on Etsy'")
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
    for m in HYPE.finditer("\n".join(shown)):
        out.append(f"hype or fake urgency ({m.group(0)!r}): frames stay honest, no secrecy or countdowns (cmo/CONTENT_PLAYBOOK.md rule 11)")
    post = spec.get("post") or {}
    reel = post.get("reel_caption", "")
    tiktok = post.get("tiktok_caption", "")
    if pivot:
        if REEL_SITE not in reel:
            out.append(f"the Reel caption lacks '{REEL_SITE}' (coo/PIVOT.md)")
        if TIKTOK_SITE not in tiktok:
            out.append(f"the TikTok caption lacks '{TIKTOK_SITE}' (coo/PIVOT.md)")
        for name, text in (("Reel", reel), ("TikTok", tiktok)):
            if "etsy" in text.lower():
                out.append(f"the {name} caption mentions Etsy: from Oct 16 videos send viewers to the free site (coo/PIVOT.md)")
    else:
        if "Link in bio: proofnotfluff.etsy.com" not in reel and REEL_SITE not in reel:
            out.append("the Reel caption lacks 'Link in bio: proofnotfluff.etsy.com'")
        if "Search ProofNotFluff on Etsy" not in tiktok and TIKTOK_SITE not in tiktok:
            out.append("the TikTok caption lacks 'Search ProofNotFluff on Etsy'")
    tags = HASHTAG.findall(reel)
    if not 3 <= len(tags) <= 5:
        out.append(f"the Reel caption has {len(tags)} hashtags (3 to 5)")
    if not dated or dated.group(1) >= HEARD_START:
        out += heard_problems(spec)
    return out


# ---------------------------------------------------------------------------------------------------------------------
# RAT CHECK (video engine Phase 0; PNF Video Engine Blueprint, "Story selection and the content system" and the MVP build
# spec): frame one shows the number; a hook of about 6 words spoken by 3.0 s (3 to 5 hooks written, one picked); one
# claim; numbers said the way a person says them; one call to action spoken once, "See your neighborhood free at
# proofnotfluff dot com slash rats."; the end card shows proofnotfluff.com/rats; captions per platform; never on screen a
# business, a person or an address; a count is complaints to 311, never rats found (cmo/CAROUSEL_TOPICS.md, rats).

RAT_SCENES = ["hook", "picture", "compare", "why"]
RAT_CTA = "See your neighborhood free at proofnotfluff dot com slash rats."
RATS_FOUND = re.compile(r"\b(?:rats? (?:found|seen|spotted|counted|sightings?)|rat population|number of rats|(?:more|fewer|less) rats\b|"
                        r"(?:found|saw|spotted|counted) (?:[\d,]+ )?rats\b|\d[\d,]* rats\b|"
                        r"rats (?:are|were|is) (?:up|down|rising|falling)|infest\w*)", re.I)
ADDRESS = re.compile(r"\b\d{2,5} [NSEW]\.? [A-Z][a-z]+ (?:St|Ave|Blvd|Rd|Dr|Pl|Ct)\b|\b\d{3,5} (?:North|South|East|West) ", re.I)
BUSINESS = re.compile(r"\b(?:LLC|Inc\.?|Corp\.?|Restaurant|Grill|Pizzeria|Taqueria|Exterminat\w+|Pest Control Co)\b")
SPEECH_CPS = 14.0   # spoken characters a second, about (el_voice.py's 12 runs slow for Eleven v4); length is re-measured at render


def _num_tokens(text):
    out = set()
    for tok in re.split(r"\s+", text or ""):
        tok = tok.strip(".,;:()?!\"'")
        m = re.fullmatch(r"[+\-]?(\d[\d,]*(?:\.\d+)?)%?", tok)
        if m:
            t = m.group(1).replace(",", "")
            if "." in t:
                t = t.rstrip("0").rstrip(".")
            out.add(t)
    return out


def rat_texts(spec):
    """(where, text) for everything the video shows or says, the post caption included."""
    out = []
    for i, h in enumerate(spec.get("hooks") or []):
        out += [(f"hook {i + 1}", h.get("say", "")), (f"hook {i + 1} heard", h.get("tts", ""))]
    for l in spec.get("lines") or []:
        out += [(f"line {l.get('id')}", l.get("say", "")), (f"line {l.get('id')} heard", l.get("tts", ""))]
    sc = spec.get("screen") or {}
    out += [("headline", f"{(sc.get('headline') or {}).get('number', '')} {(sc.get('headline') or {}).get('label', '')}"),
            ("area", sc.get("area", "")), ("period", sc.get("period", "")), ("eyebrow", sc.get("eyebrow", ""))]
    for k, v in (sc.get("scenes") or {}).items():
        out += [(f"{k} title", v.get("title", "")), (f"{k} number", f"{v.get('number', '')} {v.get('numberLabel', '')}")]
    ch = sc.get("chart") or {}
    for r in ch.get("rows") or []:
        out.append(("bar", f"{r.get('label', '')} {r.get('shown', '')}"))
    out += [("chart", " ".join(str(ch.get(k, "")) for k in ("firstShown", "lastShown", "fromShown", "toShown", "focusLabel")))]
    for t in ch.get("legend") or []:
        out.append(("legend", t[1]))
    for k, st in (ch.get("stats") or {}).items():
        out.append((f"map stat {k}", f"{st.get('name', '')} {st.get('big', '')} {st.get('label', '')}"))
    for r in sc.get("whyBars") or []:
        out.append(("why bar", f"{r.get('label', '')} {r.get('shown', '')}"))
    for c in (sc.get("compare") or {}).get("cards") or []:
        out.append(("compare card", f"{c.get('label', '')} {c.get('shown', '')}"))
    out += [("end card", " ".join(str((spec.get("endCard") or {}).get(k, "")) for k in ("line", "path", "sub")))]
    out += [("instagram caption", (spec.get("captions") or {}).get("instagram", ""))]
    return out


def rat_check_problems(spec, path="", allow_test=False):
    out = []
    if spec.get("template") != "rat-check":
        out.append(f"template {spec.get('template')!r} is not rat-check")
    if spec.get("storyType") not in ("A", "B", "C", "D"):
        out.append(f"storyType {spec.get('storyType')!r}")
    if spec.get("picture") not in ("map", "bars", "line"):
        out.append(f"picture {spec.get('picture')!r}")
    hooks = spec.get("hooks") or []
    if not 3 <= len(hooks) <= 5:
        out.append(f"{len(hooks)} hooks written (3 to 5, then one is picked two at a time)")
    for i, h in enumerate(hooks, 1):
        n = len(TAG.sub("", h.get("tts", "")).split())
        if n > 7:
            out.append(f"hook {i} is {n} words heard (about 6, said by 3.0 s): {h.get('tts')!r}")
    hook = spec.get("hook") or {}
    if not hook.get("say"):
        out.append("no hook picked")
    elif not any(h.get("say") == hook.get("say") and h.get("tts") == hook.get("tts") for h in hooks):
        out.append("the picked hook is not one of the hooks written")
    lines = spec.get("lines") or []
    if not 4 <= len(lines) <= 10:
        out.append(f"{len(lines)} lines (4 to 10)")
    order = [l.get("scene") for l in lines]
    seen = []
    for sc in order:
        if sc not in RAT_SCENES:
            out.append(f"scene {sc!r} is not one of {RAT_SCENES}")
            continue
        if not seen or seen[-1] != sc:
            if sc in seen:
                out.append(f"scene {sc!r} comes back after another scene (each scene once, in order)")
            seen.append(sc)
    if seen and [RAT_SCENES.index(x) for x in seen] != sorted(RAT_SCENES.index(x) for x in seen):
        out.append(f"scenes run {seen}, not in the order hook, picture, compare, why")
    if "picture" not in seen:
        out.append("no picture scene: the map, bars or line must be on screen")
    ids = [l.get("id") for l in lines]
    if len(set(ids)) != len(ids) or "hook" in ids or "cta" in ids:
        out.append("line ids must be unique and not 'hook' or 'cta'")
    cta = spec.get("cta") or {}
    if cta.get("say") != RAT_CTA or (cta.get("tts") or cta["say"]) != RAT_CTA:
        out.append(f"the close must read exactly {RAT_CTA!r}")
    ec = spec.get("endCard") or {}
    if ec.get("path") != "proofnotfluff.com/rats" or ec.get("line") != "See your neighborhood free":
        out.append("the end card must show 'See your neighborhood free' and proofnotfluff.com/rats")
    heard = [hook.get("tts") or hook.get("say", "")] + [l.get("tts") or l.get("say", "") for l in lines] + [cta.get("tts") or cta.get("say", "")]
    said = sum(h.lower().count("proofnotfluff dot com") for h in heard)
    if said != 1:
        out.append(f"the close is spoken {said} times (exactly once, at the end)")
    for h in heard + [x.get("tts", "") for x in hooks]:
        if TAG.search(h):
            out.append(f"audio tag in {h!r}: Eleven v4 audio tags are not confirmed, so none in the MVP")
        m = RUN_TOGETHER.search(h)
        if m:
            out.append(f"heard line {h!r} runs two numbers together ({m.group(0)!r})")
        if re.search(r"[\d$%]", h):
            out.append(f"heard line {h!r} still has digits, '$' or '%': spell it the way it is said")
    secs = sum(len(h) for h in heard) / SPEECH_CPS + 0.4 * len(heard)
    if not 36 <= secs <= 54:
        out.append(f"about {secs:.0f} s of speech by the character count (36 to 54, so the cut lands at 45 to 60 s); fit the script before any character is spent")
    ev = (spec.get("evidence") or {}).get("numbers") or []
    known = set()
    for x in ev:
        for sh in x.get("shown") or []:
            known |= _num_tokens(sh)
    ev_ids = {x.get("id") for x in ev}
    for l in lines:
        for i in l.get("show") or []:
            if i not in ev_ids:
                out.append(f"line {l.get('id')} shows {i!r}, which is not in the evidence bundle")
    for sc_name, v in ((spec.get("screen") or {}).get("scenes") or {}).items():
        if v.get("numberId") and v["numberId"] not in ev_ids:
            out.append(f"{sc_name} scene number {v['numberId']!r} is not in the evidence bundle")
    texts = rat_texts(spec)
    for where, text in texts:
        if where.endswith("heard"):
            continue
        for n in sorted(_num_tokens(text) - known):
            out.append(f"{where}: the number {n} is not in the evidence bundle (every number comes from the file, with its path)")
    blob = "\n".join(t for _, t in texts)
    if "\u2014" in blob or "\u2013" in blob:
        out.append("an em or en dash")
    for m in RATS_FOUND.finditer(blob):
        if re.search(r"\b(?:not|never|no)\s+$", blob[max(0, m.start() - 8):m.start()], re.I):
            continue   # "complaints, not rats found" says the rule, it does not break it
        out.append(f"{m.group(0)!r}: a count is complaints to 311, never rats found")
        break
    m = re.search(r"\b(?:rat |311 )?calls?\b", blob, re.I)
    if m:   # the facts gate, Oct 27: 311 takes requests by phone, app and web, so a count is complaints, not calls
        out.append(f"{m.group(0)!r}: the file counts 311 complaints (phone, app and web), so say 'complaints', not 'calls'")
    m = re.search(r"\b\d[\d,]* (?:of (?:the city's |Chicago's )?\d+ )?neighborhoods\b", blob)
    if m:   # the facts gate, Oct 27: the file counts 77 community areas, not neighborhoods (Chicago has about 200)
        out.append(f"{m.group(0)!r}: the rat file counts community areas; say 'community areas' with a number")
    for rx, what in ((ADDRESS, "an address"), (BUSINESS, "a business"), (PEOPLE, "an invented person")):
        m = rx.search(blob)
        if m:
            out.append(f"{what} ({m.group(0)!r}): never on screen or in the caption")
    for m in HYPE.finditer(blob):
        out.append(f"hype or fake urgency ({m.group(0)!r})")
    cap = (spec.get("captions") or {}).get("instagram", "")
    for need, why in (("proofnotfluff.com/rats", "the short path"), ("link in bio", "the bio link"), ("AI voice", "our AI narrator named as AI")):
        if need.lower() not in cap.lower():
            out.append(f"the Instagram caption lacks {need!r} ({why})")
    if "complaint" not in cap.lower():
        out.append("the Instagram caption must say these are complaints (never rats found)")
    if "etsy" in cap.lower():
        out.append("the Instagram caption mentions Etsy")
    if not 3 <= len(HASHTAG.findall(cap)) <= 5:
        out.append(f"the Instagram caption has {len(HASHTAG.findall(cap))} hashtags (3 to 5)")
    if len(cap) > 2200:
        out.append(f"the Instagram caption is {len(cap)} characters (Instagram's limit is 2,200)")
    voice = spec.get("voice") or {}
    if voice.get("model") != "eleven_v4":
        out.append(f"voice model {voice.get('model')!r} (Eleven v4 is pinned)")
    ids = voice.get("voiceIds") or []
    if not ids:
        out.append("no voice")
    for v in ids:
        if v not in EL_VOICES and not (allow_test and v == "test"):
            out.append(f"voice {v!r} is not one of the five approved Oct 15 ({', '.join(EL_VOICES.values())})")
    music = spec.get("music")
    lib = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "music", "library.json"), encoding="utf-8"))
    if music not in {t["id"] for t in lib["tracks"]}:
        out.append(f"music {music!r} is not in tools/music/library.json")
    return out


def main():
    if sys.argv[1:2] == ["--heard"]:
        for p in sys.argv[2:]:
            for cap, tts in heard_lines(json.load(open(p, encoding="utf-8"))):
                print(TAG.sub("", tts).strip())
        return
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
