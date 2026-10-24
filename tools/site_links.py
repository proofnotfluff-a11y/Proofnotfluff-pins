#!/usr/bin/env python3
"""Internal link check of the built site (Todd's go, Oct 24, 2026, coo/DECISIONS-2026-10-24.md item 4): lychee in
offline mode over docs/, run by .github/workflows/site-links.yml with lychee built from a pinned commit.

Checked: relative and root-relative links and assets, directory links (must hold an index.html), #fragments on our own
pages, and absolute links to proofnotfluff.com (remapped onto docs/, so a dead self-link is caught without the network).
Lychee skips <script src>, so a short pass here resolves every local script source the same way.
Not checked: other sites (offline mode skips them) and "#/..." routes, which the members apps handle in JavaScript.

  python3 tools/site_links.py [--lychee PATH] [--site docs]   exit 1 on any broken internal link
  python3 tools/site_links.py --selftest [--lychee PATH]      planted broken links of each kind are caught and the
                                                              planted good ones pass
Lychee comes from --lychee, $LYCHEE or PATH.
"""
import argparse, glob, json, os, re, shutil, subprocess, sys, tempfile
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lychee_bin(arg):
    b = arg or os.environ.get("LYCHEE") or shutil.which("lychee")
    if not b:
        print("ERROR site-links: lychee binary not found (--lychee, LYCHEE or PATH)")
        sys.exit(1)
    return b


def run(lychee, site):
    site = os.path.abspath(site)
    cmd = [lychee, "--offline", "--no-progress", "--format", "json", "--root-dir", site, "--index-files", "index.html",
           "--include-fragments", "--exclude", "#/",
           "--remap", rf"https://(?:www\.)?proofnotfluff\.com/(.*) file://{site}/$1",
           "--remap", rf"https://(?:www\.)?proofnotfluff\.com$ file://{site}/",
           os.path.join(site, "**", "*.html")]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=site)
    try:
        d = json.loads(p.stdout)
    except ValueError:
        print(f"ERROR site-links: lychee gave no report (exit {p.returncode}): {p.stderr.strip()[-300:]}")
        sys.exit(1)
    errors = []
    for page, items in (d.get("error_map") or d.get("fail_map") or {}).items():
        for it in items:
            url = it.get("url", "")
            status = it.get("status") or {}
            why = status.get("text") if isinstance(status, dict) else str(status)
            errors.append((os.path.relpath(page, site) if os.path.isabs(page) else page, url.replace(f"file://{site}", ""), why))
    errors += script_errors(site)
    return d, errors, p.returncode


SCRIPT_SRC = re.compile(r"""<script\b[^>]*?\bsrc\s*=\s*["']([^"']+)["']""", re.I)


def script_errors(site):
    """Local <script src> targets that do not exist (lychee does not extract script sources)."""
    out = []
    for page in glob.glob(os.path.join(site, "**", "*.html"), recursive=True):
        for src in SCRIPT_SRC.findall(open(page, encoding="utf-8", errors="ignore").read()):
            if re.match(r"(?i)^(?:[a-z][a-z0-9+.-]*:|//)", src):
                continue   # another site, a data: or blob: URL
            path = unquote(src.split("#")[0].split("?")[0])
            full = os.path.join(site, path.lstrip("/")) if path.startswith("/") else os.path.join(os.path.dirname(page), path)
            if not os.path.isfile(os.path.normpath(full)):
                out.append((os.path.relpath(page, site), src, "script file not found"))
    return out


def check(lychee, site):
    d, errors, rc = run(lychee, site)
    if errors or rc != 0:
        print(f"ERROR site-links: {len(errors)} broken internal links (lychee exit {rc})")
        for page, url, why in errors[:100]:
            print(f"  {page}: {url} ({why})")
        return 1
    if not d.get("successful"):
        print("ERROR site-links: lychee checked no links at all")
        return 1
    print(f"OK site-links ({d['successful']} internal links and assets resolve, {d.get('remaps', 0)} of them absolute "
          f"self-links; {d.get('excludes', 0)} other sites and app routes skipped)")
    return 0


def selftest(lychee):
    base = tempfile.mkdtemp(prefix="sitelinks-")
    try:
        site = os.path.join(base, "docs")
        os.makedirs(os.path.join(site, "good", "sub"))
        os.makedirs(os.path.join(site, "noindex"))
        os.makedirs(os.path.join(site, "assets"))
        open(os.path.join(site, "assets", "a.css"), "w").write("body{}")
        open(os.path.join(site, "good", "index.html"), "w").write('<h2 id="faq">FAQ</h2><a href="sub/">x</a>')
        open(os.path.join(site, "good", "sub", "index.html"), "w").write("<p>sub</p>")
        open(os.path.join(site, "noindex", "page.html"), "w").write("<p>no index here</p>")
        page = lambda body: f'<!doctype html><html><head><link rel="stylesheet" href="/assets/a.css"></head><body>{body}</body></html>'
        bad = {   # file -> the planted broken link it holds
            "p1.html": 'href="missing-page/"',
            "p2.html": 'href="/also-missing/"',
            "p3.html": 'href="good/#no-such-anchor"',
            "p4.html": 'href="https://proofnotfluff.com/gone-page/"',
            "p5.html": 'href="noindex/"',
            "p6.html": 'src="/assets/missing.png"',
            "p7.html": 'script="../assets/missing.js"',
        }
        for f, link in bad.items():
            tag = (f"<img alt=\"x\" {link}>" if link.startswith("src") else
                   f"<script src={link.split('=', 1)[1]}></script>" if link.startswith("script") else f"<a {link}>x</a>")
            open(os.path.join(site, f), "w").write(page(tag))
        open(os.path.join(site, "index.html"), "w").write(page(
            '<a href="good/">a</a><a href="/good/sub/">b</a><a href="good/#faq">c</a>'
            '<a href="https://proofnotfluff.com/good/">d</a><a href="https://example.org/anything">e</a>'
            '<a href="#/terms">f</a><a href="mailto:hello@proofnotfluff.com">g</a>'
            '<script src="assets/a.css?v=2"></script><script src="https://cdn.example.org/x.js"></script>'))
        d, errors, rc = run(lychee, site)
        caught = {page for page, _, _ in errors}
        missed = sorted(set(bad) - caught)
        false = sorted(caught - set(bad))
        if missed or false or rc == 0:
            print(f"ERROR site-links-selftest: missed {missed}, wrongly flagged {false}, lychee exit {rc}")
            return 1
        print(f"OK site-links-selftest ({len(bad)} planted broken links caught: missing page, missing root page, missing "
              f"anchor, dead self-link, folder without index.html, missing image, missing script; 9 good links, routes and scripts pass)")
        return 0
    finally:
        shutil.rmtree(base, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lychee", default="")
    ap.add_argument("--site", default=os.path.join(ROOT, "docs"))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    lychee = lychee_bin(a.lychee)
    sys.exit(selftest(lychee) if a.selftest else check(lychee, a.site))


if __name__ == "__main__":
    main()
