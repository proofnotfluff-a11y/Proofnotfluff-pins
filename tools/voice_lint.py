#!/usr/bin/env python3
"""Voice lint: the common tells of AI-written copy, caught in code before anyone reads the text. Todd's standing rule
is direct, human words with no AI-sounding phrasing; the list follows the patterns catalogued in Wikipedia's "Signs of
AI writing" guide (the same source as the open humanizer skill Todd saw on Oct 15), narrowed to the ones that show up
in sales copy and scripts, and written so a pricing or landscaping product can still say "budget" or "landscape".

Used by: spec_lint.py (every spoken line and caption of a Proof Check short) and fiverr_kit.py (every pasted field).
Usage: python3 tools/voice_lint.py <file> [...]    prints each tell with its line; exit 1 if any

Add a phrase here only when it reads as machine-made in our copy and has no honest use in a product sentence.
"""
import re, sys

TELLS = [
    # vocabulary that marks generated copy
    ("delve", r"\bdelv(?:e|es|ed|ing)\b"),
    ("tapestry", r"\btapestry\b"),
    ("testament", r"\b(?:a |is a |stands as a )?testament to\b"),
    ("vibrant", r"\bvibrant\b"),
    ("bustling", r"\bbustling\b"),
    ("seamless", r"\bseamless(?:ly)?\b"),
    ("elevate", r"\belevat(?:e|es|ed|ing) your\b"),
    ("unlock", r"\bunlock(?:s|ed|ing)? (?:the|your)\b"),
    ("unleash", r"\bunleash"),
    ("game changer", r"\bgame[- ]chang(?:er|ing)\b"),
    ("cutting edge", r"\bcutting[- ]edge\b"),
    ("supercharge", r"\bsupercharg"),
    ("embark", r"\bembark"),
    ("realm", r"\brealm of\b"),
    ("landscape of", r"\b(?:the|today's|digital|business|ever-changing|evolving) landscape\b"),
    ("navigate the complexities", r"\bnavigat(?:e|ing) the (?:complexities|world|intricacies)\b"),
    ("in today's fast-paced", r"\bin today's (?:fast-paced|digital|ever)"),
    ("ever-evolving", r"\bever[- ](?:evolving|changing)\b"),
    ("pivotal", r"\bpivotal\b"),
    ("robust", r"\brobust\b"),
    ("leverage (verb)", r"\bleverag(?:e|es|ing) (?:your|the|our|this|these|AI)\b"),
    ("harness", r"\bharness(?:es|ing)? the\b"),
    ("empower", r"\bempower(?:s|ing)?\b"),
    ("transformative", r"\btransformative\b"),
    ("boasts", r"\bboasts\b"),
    ("serves as", r"\bserves as a\b"),
    ("plays a crucial role", r"\bplays? a (?:crucial|vital|key|pivotal) role\b"),
    ("crucial", r"\bcrucial\b"),
    ("meticulous", r"\bmeticulous(?:ly)?\b"),
    ("holistic", r"\bholistic\b"),
    ("synergy", r"\bsynerg"),
    ("journey", r"\b(?:your|the) (?:\w+ )?journey\b"),
    # filler, hedges and chatbot leftovers
    ("it's important to note", r"\bit(?:'s| is) (?:important|worth|crucial) (?:to note|noting|to remember)\b"),
    ("worth noting", r"\bworth noting\b"),
    ("in conclusion", r"\bin (?:conclusion|summary)\b"),
    ("furthermore", r"(?:^|[.!?]\s+)(?:Furthermore|Moreover|Additionally),"),
    ("i hope this helps", r"\bI hope this helps\b"),
    ("great question", r"\b(?:Great|Excellent) question\b"),
    ("certainly", r"(?:^|[.!?]\s+)(?:Certainly|Absolutely)!"),
    ("happy to help", r"\b(?:I'd|I would) be (?:happy|glad) to\b"),
    ("as an AI", r"\bas an AI\b"),
    ("arguably", r"\barguably\b"),
    # shapes
    ("not just X, but Y", r"\bnot (?:just|only|merely) [^.;:!?\n]{1,40}, but\b"),
    ("it's not X, it's Y", r"\bit's not (?:just )?(?:about )?[^.;:!?\n]{1,30}[,.;] it's\b"),
    ("whether you're X or Y", r"\bWhether you're an? [^,]{1,40} or an? "),
    ("emoji", "[\U0001F300-\U0001FAFF☀-➿]"),
]
COMPILED = [(name, re.compile(rx, re.I | re.M)) for name, rx in TELLS]
# Two shapes are case-sensitive on purpose: sentence starters only count at the start of a sentence.
COMPILED = [(n, re.compile(rx, re.M)) if n in ("furthermore", "certainly") else (n, c) for (n, rx), (_, c) in zip(TELLS, COMPILED)]


def tells(text):
    """Every tell in the text as (name, matched words)."""
    out = []
    for name, rx in COMPILED:
        for m in rx.finditer(text or ""):
            out.append((name, m.group(0)))
    return out


def main():
    bad = 0
    for p in sys.argv[1:]:
        for n, line in enumerate(open(p, encoding="utf-8", errors="ignore"), 1):
            for name, words in tells(line):
                print(f"{p}:{n}: {name} ({words.strip()!r})"); bad += 1
    print(f"voice_lint: {bad} tell{'s' if bad != 1 else ''}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
