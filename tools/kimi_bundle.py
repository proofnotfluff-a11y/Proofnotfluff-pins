#!/usr/bin/env python3
"""Build one text file of the repo's key files for a by-hand Kimi audit (coo/KIMI_AUDIT.md).

Kimi Work uploads single files, not folders, so this packs the audit's reading list into one file.
Each file starts with a "===== FILE: <path> =====" line and every line carries its own line number,
so a finding can cite path:line and Claude can check it against the repo.

Usage: python3 tools/kimi_bundle.py [out_path]   (default: data/kimi_bundle.md, data/ is gitignored)

Never packs data/, archive/, members pages or sealed boxes. Stops if a packed line holds an email
address that is not ours (proofnotfluff.com, proofnotfluff Gmail,
mail-tester) or a phone number, so no person's details leave in the bundle.
"""
import glob, html, os, re, subprocess, sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CORE = ["CLAUDE.md", "coo/CONSTITUTION.md", "coo/HANDOFF.md"]
AFTER = ["coo/PIVOT.md", "coo/LEADS_DESK.md", "coo/STRATEGY.md", "coo/VENTURE.md", "coo/SCOREBOARD.md",
         "seo/STORE.md", "design/LAUNCH_CHECKLIST.md"]
GLOBS = [".claude/skills/*/SKILL.md", ".claude/skills/outreach-drafter/templates.md", "launches/*.md",
         "email/*.md"]
SKIP = {"email/KIT-SETUP.md"}
LEGAL_SINCE = "2026-10-24"
PAGES = ["index.html", "shop/index.html", "store/index.html", "chicago-construction-cleaning-leads/index.html",
         "austin-construction-cleaning-leads/index.html", "chicago-restaurant-inspection-leads/index.html",
         "chicago-new-business-licenses/index.html"]

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
PHONE = re.compile(r"(?<![\d.])\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.out, self.skip = [], 0
    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript", "svg"): self.skip += 1
        if tag in ("p", "li", "h1", "h2", "h3", "h4", "tr", "br", "div", "section", "button", "a"): self.out.append("\n")
    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript", "svg") and self.skip: self.skip -= 1
    def handle_data(self, data):
        if not self.skip: self.out.append(data)


def page_text(path):
    p = Text(); p.feed(open(path, encoding="utf-8", errors="replace").read())
    lines = [re.sub(r"\s+", " ", html.unescape(l)).strip() for l in "".join(p.out).split("\n")]
    return "\n".join(l for l in lines if l) + "\n"


def tracked():
    out = subprocess.run(["git", "-C", ROOT, "ls-files"], capture_output=True, text=True, check=True).stdout
    return set(out.split())


def reading_list():
    files = tracked()
    decisions = sorted(f for f in files if re.fullmatch(r"coo/DECISIONS-\d{4}-\d\d-\d\d\.md", f))[-3:][::-1]
    legal = sorted(f for f in files if f.startswith("legal/reviews/")
                   and (re.search(r"(\d{4}-\d\d-\d\d)", f) or [None, ""])[1] >= LEGAL_SINCE)
    picks = CORE + decisions + AFTER
    for g in GLOBS:
        picks += sorted(f for f in files if glob.fnmatch.fnmatch(f, g))
    picks += legal
    seen, out = set(), []
    for f in picks:
        if f in files and f not in seen and f not in SKIP and not f.startswith(("data/", "archive/")) and "sealed" not in f:
            seen.add(f); out.append(f)
    pages = [f"docs/{p}" for p in PAGES if f"docs/{p}" in files]
    return out, pages


def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "data", "kimi_bundle.md")
    files, pages = reading_list()
    head = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%h %cd", "--date=format:%Y-%m-%d %H:%M"],
                          capture_output=True, text=True).stdout.strip()
    guide = open(os.path.join(ROOT, "coo", "KIMI_AUDIT.md"), encoding="utf-8").read()
    prompt = re.search(r"```\n(.*?)```", guide, re.S).group(1).strip()
    parts = [f"# ProofNotFluff audit bundle (repo commit {head})\n\n"
             "## Audit instructions\n\n" + prompt + "\n\n## About this file\n\n"
             "One file standing in for the repo folder. Each file begins with a '===== FILE: <path> =====' line and "
             "every line starts with its line number in that file. Cite findings as path:line. Site pages (docs/) "
             "are packed as their visible text, so cite them as path:line of the text shown here.\n\n"
             "Files packed:\n" + "".join(f"- {f}\n" for f in files + pages) + "\n"]
    problems = []
    for f in files + pages:
        full = os.path.join(ROOT, f)
        text = page_text(full) if f.endswith(".html") else open(full, encoding="utf-8", errors="replace").read()
        body = []
        for n, line in enumerate(text.splitlines(), 1):
            for m in EMAIL.finditer(line):
                local, dom = m.group(0).split("@")[0].lower(), m.group(1).lower()
                if not (dom.endswith("proofnotfluff.com") or local.startswith("proofnotfluff")
                        or dom.endswith("mail-tester.com")):
                    problems.append(f"{f}:{n} email address outside proofnotfluff.com")
            if PHONE.search(line):
                problems.append(f"{f}:{n} phone number")
            body.append(f"{n:>4}  {line}")
        parts.append(f"===== FILE: {f} =====\n" + "\n".join(body) + "\n\n")
    if problems:
        print("kimi_bundle: STOP, personal details would leave in the bundle:")
        print("\n".join(problems[:40]))
        sys.exit(1)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    data = "".join(parts)
    open(out_path, "w", encoding="utf-8").write(data)
    print(f"kimi_bundle: {len(files)} files and {len(pages)} pages, {len(data):,} bytes, about {len(data)//4:,} tokens -> {out_path}")


if __name__ == "__main__":
    main()
