"""Thank-you page for a free template sign-up (Oct 26, 2026): the Kit form sends people to one address, and each
template has two files, so the form redirects here. Permanently noindex and nofollow, never in site/extras.json or the
sitemap. Header and footer are copied from the template page itself, so the two always match.

Used by engines/price-increase-letter/build.py and engines/job-estimate-template/build.py after they build the files.
"""
import html
import os
import re

E = html.escape


def _size(path):
    n = os.path.getsize(path)
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def write(root, slug, name, files, office_line, calc):
    """files: [(filename, label, detail)], the first is the filled button. calc: (slug, link text)."""
    page = os.path.join(root, "docs", slug, "index.html")
    src = open(page, encoding="utf-8").read()
    header = re.search(r'<header class="top">.*?</header>', src, re.S).group(0).replace('href="../', 'href="../../')
    footer = re.search(r"<footer>.*?</footer>", src, re.S).group(0).replace('href="../', 'href="../../')
    h1 = re.search(r'"position": 2, "name": "([^"]+)"', src).group(1)
    btns = []
    for i, (fn, label, detail) in enumerate(files):
        size = _size(os.path.join(root, "docs", "downloads", fn))
        cls = "dl" if i == 0 else "dl ghost"
        btns.append(f'<a class="{cls}" href="../../downloads/{E(fn)}" download><span class="dl-l">{E(label)}</span>'
                    f'<span class="dl-d">{E(detail)}, {size}</span></a>')
    out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Your {E(name)} is ready</title>
<meta name="description" content="Download your free {E(name)}.">
<meta name="robots" content="noindex, nofollow">
<meta name="color-scheme" content="light dark"><link rel="icon" href="../../assets/favicon.svg" type="image/svg+xml"><link rel="icon" href="../../assets/favicon-48.png" sizes="48x48" type="image/png"><meta name="theme-color" content="#f3f1ec" media="(prefers-color-scheme: light)"><meta name="theme-color" content="#12161f" media="(prefers-color-scheme: dark)"><link rel="preload" href="../../assets/fonts/poppins-700.woff2" as="font" type="font/woff2" crossorigin><link rel="stylesheet" href="../../assets/pnf.css">
<style>
.dls{{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;max-width:560px;margin:8px 0 18px}}
.dl{{display:flex;flex-direction:column;justify-content:center;min-height:64px;padding:10px 18px;border-radius:12px;background:var(--btn);color:#fff;text-decoration:none;border:1.5px solid var(--btn)}}
.dl .dl-l{{font-weight:700;font-size:17px}}.dl .dl-d{{font-size:14px;font-weight:600}}
.dl.ghost{{background:transparent;color:var(--ink);border-color:var(--ink)}}.dl.ghost .dl-d{{color:var(--ink2);font-weight:400}}
.dl:hover .dl-l{{text-decoration:underline}}
.tk p{{max-width:560px;color:var(--ink2)}}
.tk .quiet{{display:inline-flex;align-items:center;min-height:44px}}
</style>
<script defer src="https://static.cloudflareinsights.com/beacon.min.js" data-cf-beacon='{{"token": "b40d887129c342ccb476aa67aad72034"}}'></script></head><body><a class="skip" href="#main">Skip to content</a>
{header}
<main class="wrap tk" id="main"><nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="../../">Home</a></li><li><a href="../">{E(h1)}</a></li><li aria-current="page">Download</li></ol></nav>
<p class="eyebrow">Thanks for signing up</p>
<h1>Your template is ready</h1>
<div class="dls">{''.join(btns)}</div>
<p>{E(office_line)}</p>
<p><a class="quiet" href="../../{E(calc[0])}/">{E(calc[1])}</a></p>
</main>
{footer}
</body></html>
"""
    d = os.path.join(root, "docs", slug, "thanks")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
