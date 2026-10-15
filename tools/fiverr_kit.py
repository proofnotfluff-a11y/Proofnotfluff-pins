#!/usr/bin/env python3
"""Fiverr kit checker: holds the paste-ready copy in services/fiverr/ to Fiverr's field limits and to our own rules,
so an edit by any desk cannot break a gig quietly. Only the text inside code blocks is pasted into Fiverr, so the
field rules apply to code blocks; the em dash rule applies to every line of the three files.

Fiverr limits (checked Oct 15, 2026; sources in services/fiverr/README.md):
  title            starts "I will ", at most 80 characters including "I will", none of & / " +
  search tags      5 tags, each at most 20 letters, numbers and spaces
  description      at most 1,200 characters, each line break counted as 2 to leave room for Fiverr's editor
  package          3 packages; description at most 100 characters; name at most 20 (our own cap, Fiverr's
                   limit was not confirmed); prices at least $5 and rising; delivery days never falling
  FAQ              at most 10; question at most 70 characters, answer at most 300
  requirements     each question at most 200 characters, marked Required or Optional
  profile          description 150 to 600 characters
Our rules (README "Rules" and the Legal desk):
  - every gig description carries the AI-assisted line, the not-advice line and the license line (Fiverr assigns
    all rights in a delivery to the buyer unless the Gig page says otherwise, and our templates are reused)
  - no links, web addresses, emails or phone numbers in anything pasted into Fiverr
  - no guarantee wording, no review bait (asking for a 5-star or positive review, or anything in exchange for one)
  - no off-Fiverr asks (other apps, other payment methods, "email me")

Usage: python3 tools/fiverr_kit.py [kit folder] [--stats]
  prints one line per problem and exits 1 if there is any; --stats also prints every field's length
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT = os.path.join(ROOT, "services", "fiverr")
EM = "—"
CONTACT = re.compile(r"https?://|www\.|[\w.+-]+@[\w-]+\.[a-z]{2,}|\b[\w-]+\.(?:com|net|org|io|co|us|shop|store)\b"
                     r"|\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b", re.I)
GUARANTEE = re.compile(r"\bguarantee", re.I)
REVIEW_BAIT = re.compile(r"\b(?:5|five)[- ]?stars?\b|\b(?:positive|good|great|glowing) reviews?\b|in exchange for (?:a |an |your )?review"
                         r"|reviews? (?:for|in return for) (?:a |an )?(?:discount|refund|bonus|gift)", re.I)
OFF_FIVERR = re.compile(r"whats ?app|telegram|skype|discord|signal app|zoom|google meet|paypal|venmo|zelle|cash ?app|wire transfer"
                        r"|e-?mail me|call me|text me|\bmy (?:e-?mail|phone|cell|website)\b|\bmy number\b", re.I)
TITLE_BAD = set('&/"+')
TAG_OK = re.compile(r"^[A-Za-z0-9 ]{1,20}$")
MONEY = re.compile(r"^\$(\d+(?:\.\d\d)?)$")
DAYS = re.compile(r"^(\d+) days?$")


def blocks(md):
    """Every fenced block as (heading, section, label, text): heading is the last '## ' line, section the last bold
    label (e.g. 'Title', 'FAQ'), label the last plain line before the fence (e.g. 'Basic', 'Required, free text:')."""
    out, problems = [], []
    heading = section = label = ""
    inside, buf = False, []
    for n, line in enumerate(md.splitlines(), 1):
        if line.startswith("```"):
            if inside:
                out.append((heading, section, label, "\n".join(buf)))
                buf, inside = [], False
            else:
                inside, start = True, n
            continue
        if inside:
            buf.append(line)
            continue
        s = line.strip()
        if s.startswith("## "):
            heading, section, label = s[3:].strip(), "", ""
        elif s.startswith("**"):
            m = re.match(r"\*\*(.+?)\*\*", s)
            section = label = m.group(1).strip() if m else s
        elif s and not s.startswith("|") and s != "---":
            label = s
    if inside:
        problems.append(f"a code block opened at line {start} is never closed")
    return out, problems


def table(md, heading):
    """The package table under a gig heading, as {row label: [Basic, Standard, Premium]}."""
    rows, current = {}, ""
    for line in md.splitlines():
        s = line.strip()
        if s.startswith("## "):
            current = s[3:].strip()
        elif current == heading and s.startswith("|") and not set(s) <= set("|-: "):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if cells and cells[0]:
                rows[cells[0]] = cells[1:]
    return rows


def pasted_rules(where, text, problems):
    if CONTACT.search(text):
        problems.append(f"{where}: a link, web address, email or phone number ({CONTACT.search(text).group(0)!r})")
    if GUARANTEE.search(text):
        problems.append(f"{where}: guarantee wording")
    if REVIEW_BAIT.search(text):
        problems.append(f"{where}: review bait ({REVIEW_BAIT.search(text).group(0)!r})")
    if OFF_FIVERR.search(text):
        problems.append(f"{where}: an off-Fiverr ask ({OFF_FIVERR.search(text).group(0)!r})")


def check_gigs(path, problems, stats):
    md = open(path, encoding="utf-8").read()
    found, parse_problems = blocks(md)
    problems += [f"gigs.md: {p}" for p in parse_problems]
    gigs = [h for h in dict.fromkeys(h for h, _, _, _ in found) if h.lower().startswith("gig ")]
    if not gigs:
        problems.append("gigs.md: no '## Gig' sections found")
    for g in gigs:
        name = g.split(":")[0]
        mine = [(sec, lab, t) for h, sec, lab, t in found if h == g]
        pick = lambda prefix: [(lab, t) for sec, lab, t in mine if sec.lower().startswith(prefix)]
        titles, tags, descs = pick("title"), pick("search tags"), pick("description")
        packs = [(lab, t) for lab, t in pick("packages") if lab in ("Basic", "Standard", "Premium")]
        reqs, faq = pick("requirements"), pick("faq")
        if len(titles) != 1:
            problems.append(f"{name}: {len(titles)} titles (want 1)")
        for _, t in titles:
            stats.append(f"{name} title {len(t)}/80")
            if not t.startswith("I will "):
                problems.append(f"{name}: title does not start with 'I will '")
            if len(t) > 80:
                problems.append(f"{name}: title is {len(t)} characters (max 80)")
            if TITLE_BAD & set(t):
                problems.append(f"{name}: title has {''.join(sorted(TITLE_BAD & set(t)))} (Fiverr rejects & / \" +)")
        if len(tags) != 5:
            problems.append(f"{name}: {len(tags)} search tags (want 5)")
        for _, t in tags:
            if not TAG_OK.match(t):
                problems.append(f"{name}: tag {t!r} must be at most 20 letters, numbers and spaces")
        if len({t.lower() for _, t in tags}) != len(tags):
            problems.append(f"{name}: a search tag repeats")
        if len(descs) != 1:
            problems.append(f"{name}: {len(descs)} descriptions (want 1)")
        for _, t in descs:
            n = len(t) + t.count("\n")  # a line break counted as 2, in case Fiverr's editor stores it that way
            stats.append(f"{name} description {n}/1200 (line breaks counted twice)")
            if n > 1200:
                problems.append(f"{name}: description is {n} characters with line breaks counted twice (max 1,200)")
            if "AI-assisted" not in t:
                problems.append(f"{name}: description lacks the AI-assisted line")
            if "not tax, legal or investment advice" not in t:
                problems.append(f"{name}: description lacks 'not tax, legal or investment advice'")
            if not re.search(r"licen[cs]e|stays? ProofNotFluff", t, re.I):
                problems.append(f"{name}: description lacks the license line (without it Fiverr hands the buyer all rights)")
        if [lab for lab, _ in packs] != ["Basic", "Standard", "Premium"]:
            problems.append(f"{name}: package descriptions are {[lab for lab, _ in packs]} (want Basic, Standard, Premium)")
        for lab, t in packs:
            stats.append(f"{name} {lab} {len(t)}/100")
            if len(t) > 100:
                problems.append(f"{name}: {lab} package description is {len(t)} characters (max 100)")
        rows = table(md, g)
        for row in ("Name", "Price", "Delivery", "Revisions"):
            if len(rows.get(row, [])) != 3:
                problems.append(f"{name}: package table needs a {row} row with 3 values")
        for v in rows.get("Name", []):
            if len(v) > 20:
                problems.append(f"{name}: package name {v!r} is over 20 characters")
        prices = [MONEY.match(v) for v in rows.get("Price", [])]
        if prices and all(prices):
            p = [float(m.group(1)) for m in prices]
            if min(p) < 5 or p != sorted(p) or len(set(p)) != len(p):
                problems.append(f"{name}: prices {p} must be at least $5 and rise from Basic to Premium")
        elif prices:
            problems.append(f"{name}: prices must read like $120")
        days = [DAYS.match(v) for v in rows.get("Delivery", [])]
        if days and all(days):
            d = [int(m.group(1)) for m in days]
            if d != sorted(d):
                problems.append(f"{name}: delivery days {d} fall from Basic to Premium")
        elif days:
            problems.append(f"{name}: delivery must read like '3 days'")
        if not reqs:
            problems.append(f"{name}: no requirement questions")
        for lab, t in reqs:
            if not re.match(r"(Required|Optional)\b", lab):
                problems.append(f"{name}: requirement {t[:40]!r} is not marked Required or Optional")
            if len(t) > 200:
                problems.append(f"{name}: requirement {t[:40]!r} is {len(t)} characters (max 200)")
        if len(faq) % 2:
            problems.append(f"{name}: FAQ blocks must come in question and answer pairs")
        pairs = [(faq[i][1], faq[i + 1][1]) for i in range(0, len(faq) - 1, 2)]
        if len(pairs) > 10:
            problems.append(f"{name}: {len(pairs)} FAQs (max 10)")
        for q, a in pairs:
            if len(q) > 70:
                problems.append(f"{name}: FAQ question {q[:40]!r} is {len(q)} characters (max 70)")
            if len(a) > 300:
                problems.append(f"{name}: FAQ answer to {q[:40]!r} is {len(a)} characters (max 300)")
            if not q.rstrip().endswith("?"):
                problems.append(f"{name}: FAQ question {q[:40]!r} does not end with '?'")
        for sec, lab, t in mine:
            pasted_rules(f"{name} {sec or lab}", t, problems)
    return len(gigs)


def check_profile(path, problems, stats):
    found, parse_problems = blocks(open(path, encoding="utf-8").read())
    problems += [f"profile.md: {p}" for p in parse_problems]
    desc = [t for _, sec, _, t in found if sec.lower().startswith("description")]
    if len(desc) != 1:
        problems.append(f"profile.md: {len(desc)} description blocks (want 1)")
    for t in desc:
        stats.append(f"profile description {len(t)} (150 to 600)")
        if not 150 <= len(t) <= 600:
            problems.append(f"profile.md: description is {len(t)} characters (Fiverr wants 150 to 600)")
        if "AI-assisted" not in t:
            problems.append("profile.md: description lacks the AI-assisted line")
    for _, sec, lab, t in found:
        pasted_rules(f"profile.md {sec or lab}", t, problems)


def check_replies(path, problems, stats):
    found, parse_problems = blocks(open(path, encoding="utf-8").read())
    problems += [f"replies.md: {p}" for p in parse_problems]
    if not found:
        problems.append("replies.md: no reply templates found")
    for heading, sec, lab, t in found:
        where = f"replies.md {heading or sec or lab}"
        stats.append(f"{where} {len(t)}/2500")
        if len(t) > 2500:
            problems.append(f"{where}: {len(t)} characters (max 2,500)")
        pasted_rules(where, t, problems)


def problems(kit=KIT, stats=None):
    """All problems in the kit folder, as short lines. An absent kit is not a problem."""
    out, stats = [], stats if stats is not None else []
    if not os.path.isdir(kit):
        return out
    for fname, fn in (("gigs.md", check_gigs), ("profile.md", check_profile), ("replies.md", check_replies)):
        p = os.path.join(kit, fname)
        if not os.path.exists(p):
            out.append(f"{fname} is missing")
            continue
        if EM in open(p, encoding="utf-8").read():
            out.append(f"{fname}: an em dash")
        fn(p, out, stats)
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    kit = os.path.abspath(args[0]) if args else KIT
    stats = []
    found = problems(kit, stats)
    if "--stats" in sys.argv:
        for s in stats:
            print("  " + s)
    for p in found:
        print("PROBLEM " + p)
    print(f"fiverr_kit: {len(found)} problem{'s' if len(found) != 1 else ''}")
    sys.exit(1 if found else 0)


if __name__ == "__main__":
    main()
