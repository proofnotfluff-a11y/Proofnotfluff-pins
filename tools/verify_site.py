#!/usr/bin/env python3
"""Verify: check site work the way Todd would, by using it (Todd, live chat, Oct 27, 2026: "Ensure this is a skill we
bake into the PNF system", on Kem's verification video). The skill is .claude/skills/verify/SKILL.md; this is its CLI.

Hands and eyes, in one run:
- hands: a real Chromium (Playwright) opens each page on a phone (390 px) and a desktop (1280 px), in light and dark,
  and runs the page's flows (verify/flows/*.json): taps, typing, picking from lists, with a screenshot per step;
- eyes: every script error, console error and failed request on the page (what DevTools would show), sideways scroll,
  and the axe WCAG 2.1 AA accessibility rules;
- before and after: with --before BASE, the same shots of the committed pages at BASE (origin/main by default) and a
  pixel diff of each pair, so a change nobody meant (text gone in dark mode, a shifted button) shows up as a number and
  a picture.

Evidence lands in data/verify/<stamp>/ (gitignored): report.md, report.json, the shots, diffs and before/after pairs.
Exit 1 on any FAIL. Never edits a page; it only reads docs/.

Usage:
  python3 tools/verify_site.py chicago-trades-news chicago-rat-complaints      pages by folder under docs/ ("" = home)
  python3 tools/verify_site.py --changed                                        pages that differ from origin/main
  python3 tools/verify_site.py --changed --before origin/main                   plus before/after pixel diffs
  python3 tools/verify_site.py --flows                                          every flow in verify/flows/
  python3 tools/verify_site.py --selftest                                       planted cases, no browser
Options: --widths 390,1280  --schemes light,dark  --max 15  --out DIR  --no-axe
"""
import argparse, datetime as dt, functools, glob, http.server, json, os, re, shutil, socketserver, subprocess, sys
import tempfile, threading

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DOCS = os.path.join(ROOT, "docs")
FLOWS = os.path.join(ROOT, "verify", "flows")
CACHE = os.path.expanduser("~/.cache/pnf-verify")
AXE_VER = "4.10.2"
LEAFLET = "1.9.4"
TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]
DIFF_WARN = 0.5        # percent of pixels changed between before and after that gets called out
# requests that fail only because this machine has no open internet are not page faults (the sandbox blocks map
# tiles, analytics and fonts from other hosts); they are listed as notes, never as FAIL
EXTERNAL_OK = ("tile.openstreetmap.org", "static.cloudflareinsights.com", "cloudflareinsights.com", "fonts.googleapis.com",
               "fonts.gstatic.com", "gumroad.com", "kit.com", "convertkit.com")


# ------------------------------------------------------------------ helpers without a browser (selftested)
def page_url(base, page):
    page = page.strip("/")
    return base + "/" + (page + "/" if page and not page.endswith(".html") else page)


def changed_pages(base="origin/main", root=ROOT):
    """Folders under docs/ whose index.html differs from BASE, home as ""; members' apps and stage counters left out."""
    try:
        out = subprocess.run(["git", "-C", root, "diff", "--name-only", base, "--", "docs"], capture_output=True, text=True, check=True).stdout
        new = subprocess.run(["git", "-C", root, "ls-files", "--others", "--exclude-standard", "docs"], capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        sys.exit(f"verify: git diff against {base} failed: {e.stderr.strip()}")
    return pages_from_paths((out + new).split())


def pages_from_paths(paths):
    pages = set()
    for f in paths:
        if not f.endswith("index.html") or not f.startswith("docs/"):
            continue
        p = f[len("docs/"):-len("index.html")].strip("/")
        if p.startswith("e/") or "-members" in p or p.startswith("zz-"):
            continue
        pages.add(p)
    return sorted(pages, key=lambda p: (p != "", p))


def pick(pages, cap):
    """At most cap pages: home first, then every page in alphabetical order with an even spread when there are more."""
    if len(pages) <= cap:
        return pages
    head, rest = [p for p in pages if p == ""], [p for p in pages if p != ""]
    k = cap - len(head)
    step = len(rest) / k
    return head + [rest[int(i * step)] for i in range(k)]


def diff_images(a, b, out_diff, out_pair):
    """Percent of pixels that differ between two screenshots (any channel off by more than 16), a red overlay of the
    changes, and a side-by-side pair labeled before and after. Different sizes count the extra area as changed."""
    from PIL import Image, ImageChops, ImageDraw
    A, B = Image.open(a).convert("RGB"), Image.open(b).convert("RGB")
    W, H = max(A.width, B.width), max(A.height, B.height)
    pa, pb = Image.new("RGB", (W, H), (255, 0, 255)), Image.new("RGB", (W, H), (255, 0, 255))
    pa.paste(A, (0, 0)); pb.paste(B, (0, 0))
    d = ImageChops.difference(pa, pb).convert("L").point(lambda v: 255 if v > 16 else 0)
    hist = d.histogram()
    changed = hist[255] / (W * H) * 100
    over = pb.copy()
    red = Image.new("RGB", (W, H), (230, 40, 40))
    over.paste(red, (0, 0), d)
    over = Image.blend(pb, over, 0.65)
    over.save(out_diff)
    pair = Image.new("RGB", (W * 2 + 24, H + 40), (255, 255, 255))
    pair.paste(pa, (0, 40)); pair.paste(pb, (W + 24, 40))
    dr = ImageDraw.Draw(pair)
    dr.text((8, 12), "BEFORE", fill=(29, 36, 51)); dr.text((W + 32, 12), f"AFTER  ({changed:.2f}% of pixels changed)", fill=(29, 36, 51))
    pair.save(out_pair)
    return round(changed, 2)


# content cut off at the screen edge: visible boxes that run past the viewport outside any scroll or clip box of their
# own (pnf.css clips sideways overflow on body, so a too-wide button is cut off rather than scrolled: Kem's example)
CUT_JS = """(W) => { const out = [];
  for (const e of document.querySelectorAll('body *')) {
    const r = e.getBoundingClientRect(); if (!r.width || !r.height || r.right <= W + 1 || r.left >= W) continue;
    const cs = getComputedStyle(e);
    if (cs.position === 'fixed' || cs.visibility === 'hidden' || (cs.clip && cs.clip !== 'auto') || (cs.clipPath && cs.clipPath !== 'none')) continue;
    let a = e.parentElement, boxed = false;
    while (a && a !== document.body) { if (getComputedStyle(a).overflowX !== 'visible') { boxed = true; break; } a = a.parentElement; }
    if (boxed) continue;
    if ([...e.children].some(c => c.getBoundingClientRect().right > W + 1)) continue;
    out.push(e.tagName.toLowerCase() + (typeof e.className === 'string' && e.className ? '.' + e.className.trim().split(/\\s+/)[0] : '') + ' to ' + Math.round(r.right) + ' px');
  }
  return {w: W, scrollW: document.documentElement.scrollWidth, cut: out.slice(0, 4), n: out.length}; }"""


STEP_KINDS = {"goto", "click", "tap", "fill", "select", "press", "wait", "expect_text", "expect_count", "expect_visible",
              "expect_hidden", "expect_js", "screenshot", "scroll"}


def check_flow(flow):
    """Problems with a flow file before any browser opens."""
    bad = []
    if not isinstance(flow.get("page"), str):
        bad.append("page: the folder under docs/ the flow opens")
    for i, st in enumerate(flow.get("steps") or []):
        kind = [k for k in st if k in STEP_KINDS - {"screenshot"}] or [k for k in st if k == "screenshot"]
        if len(kind) != 1:
            bad.append(f"step {i + 1}: exactly one of {sorted(STEP_KINDS)}")
        elif kind[0] in ("fill", "select") and "value" not in st:
            bad.append(f"step {i + 1}: {kind[0]} needs a value")
        elif kind[0] == "expect_count" and not any(k in st for k in ("eq", "min", "max")):
            bad.append(f"step {i + 1}: expect_count needs eq, min or max")
    if not flow.get("steps"):
        bad.append("steps: at least one")
    return bad


# ------------------------------------------------------------------ browser, server, assets
def chromium_path():
    if os.environ.get("PNF_CHROMIUM") and os.path.isfile(os.environ["PNF_CHROMIUM"]):
        return os.environ["PNF_CHROMIUM"]
    found = sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux64/chrome"))
    return found[-1] if found else None   # None: Playwright's own download (GitHub Actions installs it)


def npm_file(pkg, ver, rel):
    """A file from an npm package, installed once into ~/.cache/pnf-verify (the npm registry is reachable everywhere
    this runs; the public CDN is not, in the cloud sandbox)."""
    f = os.path.join(CACHE, "node_modules", pkg, rel)
    if not os.path.isfile(f):
        os.makedirs(CACHE, exist_ok=True)
        r = subprocess.run(["npm", "install", "--silent", "--no-audit", "--no-fund", "--prefix", CACHE, f"{pkg}@{ver}"],
                           capture_output=True, text=True)
        if r.returncode or not os.path.isfile(f):
            return None
    return f


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(folder):
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(_Quiet, directory=folder))
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}"


def checkout_docs(base):
    """BASE's committed docs/ in a temp folder (git archive, so the working tree is untouched)."""
    tmp = tempfile.mkdtemp(prefix="pnf-verify-before-")
    tar = subprocess.run(["git", "-C", ROOT, "archive", base, "docs"], capture_output=True, check=True).stdout
    subprocess.run(["tar", "-x", "-C", tmp], input=tar, check=True)
    return tmp, os.path.join(tmp, "docs")


# ------------------------------------------------------------------ the run
class Run:
    def __init__(self, out, widths, schemes, axe=True):
        self.out, self.widths, self.schemes, self.use_axe = out, widths, schemes, axe
        self.lines, self.rows, self.fails = [], [], 0
        os.makedirs(out, exist_ok=True)
        self.axe = npm_file("axe-core", AXE_VER, "axe.min.js") if axe else None
        if axe and not self.axe:
            self.note("axe-core could not be installed from npm: accessibility rules not run")
        self.leaflet = {k: npm_file("leaflet", LEAFLET, f"dist/leaflet.{k}") for k in ("js", "css")}

    def note(self, s):
        self.lines.append("NOTE " + s)

    def result(self, ok, label, detail, row):
        self.lines.append(f"{'PASS' if ok else 'FAIL'} {label}: {detail}")
        self.rows.append(dict(row, ok=ok, label=label, detail=detail))
        self.fails += 0 if ok else 1

    async def context(self, browser, width, scheme):
        ctx = await browser.new_context(viewport={"width": width, "height": 900 if width > 600 else 844}, color_scheme=scheme,
                                        device_scale_factor=1, has_touch=width <= 600, is_mobile=width <= 600)
        lf = self.leaflet

        async def route(r):
            u = r.request.url
            m = re.search(r"cdnjs\.cloudflare\.com/ajax/libs/leaflet/" + re.escape(LEAFLET) + r"/leaflet\.(js|css)$", u)
            if m and lf.get(m.group(1)):
                body = open(lf[m.group(1)], "rb").read()   # bytes, so the page's pinned SRI hash still matches
                await r.fulfill(body=body, content_type="application/javascript" if m.group(1) == "js" else "text/css",
                                headers={"access-control-allow-origin": "*"})
            else:
                await r.continue_()
        await ctx.route("**/cdnjs.cloudflare.com/**", route)
        return ctx

    async def open(self, ctx, url):
        pg = await ctx.new_page()
        ev = {"pageerror": [], "console": [], "failed": [], "external": []}
        pg.on("pageerror", lambda e: ev["pageerror"].append(str(e)[:200]))
        pg.on("console", lambda m: ev["console"].append(m.text[:200]) if m.type == "error" else None)

        def failed(req):
            host = re.sub(r"^https?://([^/]+).*$", r"\1", req.url)
            (ev["external"] if (host.endswith(EXTERNAL_OK) or not host.startswith("127.0.0.1")) else ev["failed"]).append(req.url[:160])
        pg.on("requestfailed", failed)
        pg.on("response", lambda r: ev["failed"].append(f"{r.status} {r.url[:150]}") if r.status >= 400 and "127.0.0.1" in r.url else None)
        resp = await pg.goto(url, wait_until="networkidle", timeout=45000)
        await pg.wait_for_timeout(250)
        return pg, ev, (resp.status if resp else 0)

    async def axe_run(self, pg):
        if not self.axe:
            return []
        await pg.add_script_tag(path=self.axe)
        r = await pg.evaluate("tags => axe.run(document, {runOnly: {type: 'tag', values: tags}})", TAGS)
        return [f"{v['id']} ({v['impact']}): {', '.join(str(n['target'][0]) for n in v['nodes'][:3])}" for v in r["violations"]]

    def judge(self, label, ev, status, pg_facts, axe, row):
        problems = []
        if status != 200:
            problems.append(f"HTTP {status}")
        problems += [f"script error: {e}" for e in ev["pageerror"]]
        console = [c for c in ev["console"] if not any(h in c for h in EXTERNAL_OK) and "ERR_TUNNEL" not in c and "ERR_CONNECTION" not in c
                   and "net::ERR_FAILED" not in c and "Failed to load resource" not in c]
        problems += [f"console error: {c}" for c in console]
        problems += [f"request failed: {u}" for u in ev["failed"]]
        if pg_facts["scrollW"] > pg_facts["w"] + 1:
            problems.append(f"sideways scroll {pg_facts['scrollW']} px on a {pg_facts['w']} px screen")
        if pg_facts["n"]:
            problems.append(f"{pg_facts['n']} element(s) cut off at the {pg_facts['w']} px edge: {', '.join(pg_facts['cut'])}")
        problems += [f"axe {a}" for a in axe]
        ok = not problems
        detail = ("axe 0, 0 script errors, nothing cut off or scrolling sideways" if ok else "; ".join(problems[:6]) + (f" (+{len(problems) - 6} more)" if len(problems) > 6 else ""))
        if ev["external"]:
            row["external"] = len(ev["external"])
        self.result(ok, label, detail, row)

    async def page_check(self, browser, base, page, shots):
        for w in self.widths:
            for sc in self.schemes:
                ctx = await self.context(browser, w, sc)
                pg, ev, status = await self.open(ctx, page_url(base, page))
                if not pg.url.startswith(base):   # a /go/ link page that forwards to Etsy or Gumroad: nothing of ours to judge
                    if shots == "after" and w == self.widths[0] and sc == self.schemes[0]:
                        self.note(f"{page}: a link page that forwards off the site, not judged")
                    await ctx.close()
                    continue
                facts = await pg.evaluate(CUT_JS, w)
                axe = await self.axe_run(pg)
                name = f"{(page or 'home').replace('/', '_')}-{w}-{sc}.png"
                path = os.path.join(self.out, shots, name)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                await pg.screenshot(path=path, full_page=True)
                if shots == "after":
                    self.judge(f"{page or 'home'} {w} {sc}", ev, status, facts, axe, {"page": page, "width": w, "scheme": sc, "shot": os.path.relpath(path, self.out)})
                await ctx.close()

    async def flow(self, browser, base, name, flow):
        bad = check_flow(flow)
        if bad:
            return self.result(False, f"flow {name}", "flow file: " + "; ".join(bad), {"flow": name})
        self.base = base
        if flow.get("setup"):
            r = subprocess.run(flow["setup"], shell=True, cwd=ROOT, capture_output=True, text=True)
            if r.returncode:
                return self.result(False, f"flow {name}", "setup failed: " + (r.stderr or r.stdout).strip()[-200:], {"flow": name})
        try:
            for w in flow.get("widths") or self.widths:
                for sc in flow.get("schemes") or self.schemes[:1]:
                    ctx = await self.context(browser, w, sc)
                    pg, ev, status = await self.open(ctx, page_url(base, flow["page"]))
                    done, err = 0, ""
                    for i, st in enumerate(flow["steps"]):
                        try:
                            await self.step(pg, st, os.path.join(self.out, "flows", f"{name}-{w}-{sc}-{i + 1:02d}.png"))
                            done += 1
                        except Exception as e:   # the step's own message is the evidence
                            err = f"step {i + 1} ({json.dumps(st)[:90]}): {str(e).splitlines()[0][:160]}"
                            await pg.screenshot(path=os.path.join(self.out, "flows", f"{name}-{w}-{sc}-FAILED.png"), full_page=False)
                            break
                    axe = await self.axe_run(pg) if not err else []
                    problems = ([err] if err else []) + [f"script error: {e}" for e in ev["pageerror"]] + [f"axe {a}" for a in axe]
                    self.result(not problems, f"flow {name} {w} {sc}",
                                f"{done} of {len(flow['steps'])} steps, 0 script errors, axe 0 after the flow" if not problems else "; ".join(problems[:4]),
                                {"flow": name, "width": w, "scheme": sc})
                    await ctx.close()
        finally:
            for d in flow.get("cleanup") or []:
                p = os.path.join(ROOT, d)
                if os.path.realpath(p).startswith(os.path.realpath(DOCS) + os.sep + "zz-"):
                    shutil.rmtree(p, ignore_errors=True)

    async def step(self, pg, st, shot):
        T = 8000
        if "goto" in st:
            await pg.goto(page_url(self.base, st["goto"]), wait_until="networkidle")
        elif "click" in st or "tap" in st:
            await pg.locator(st.get("click") or st.get("tap")).first.click(timeout=T, force=bool(st.get("force")))
        elif "fill" in st:
            await pg.locator(st["fill"]).first.fill(str(st["value"]), timeout=T)
        elif "select" in st:
            await pg.locator(st["select"]).first.select_option(str(st["value"]), timeout=T)
        elif "press" in st:
            await pg.keyboard.press(st["press"])
        elif "scroll" in st:
            await pg.locator(st["scroll"]).first.scroll_into_view_if_needed(timeout=T)
        elif "wait" in st:
            await pg.wait_for_timeout(int(st["wait"]))
        elif "expect_text" in st:
            loc = pg.locator(st["expect_text"]).first
            await loc.wait_for(timeout=T)
            txt = await loc.inner_text()
            if "contains" in st and st["contains"] not in txt:
                raise AssertionError(f"text {txt[:80]!r} does not contain {st['contains']!r}")
            if "matches" in st and not re.search(st["matches"], txt):
                raise AssertionError(f"text {txt[:80]!r} does not match {st['matches']!r}")
        elif "expect_count" in st:
            n = await pg.locator(st["expect_count"]).count()
            if ("eq" in st and n != st["eq"]) or ("min" in st and n < st["min"]) or ("max" in st and n > st["max"]):
                raise AssertionError(f"{n} matches for {st['expect_count']}")
        elif "expect_visible" in st:
            await pg.locator(st["expect_visible"]).first.wait_for(state="visible", timeout=T)
        elif "expect_hidden" in st:
            await pg.locator(st["expect_hidden"]).first.wait_for(state="hidden", timeout=T)
        elif "expect_js" in st:
            if not await pg.evaluate(st["expect_js"]):
                raise AssertionError(f"false: {st['expect_js'][:80]}")
        if st.get("screenshot") or "screenshot" in st:
            os.makedirs(os.path.dirname(shot), exist_ok=True)
            await pg.screenshot(path=shot, full_page=bool(st.get("full")))
        await pg.wait_for_timeout(int(st.get("settle", 150)))

    def write(self, meta):
        rep = {"meta": meta, "fails": self.fails, "results": self.rows, "lines": self.lines}
        json.dump(rep, open(os.path.join(self.out, "report.json"), "w"), indent=1)
        md = [f"# Verify, {meta['when']}", "", f"Pages: {', '.join(p or 'home' for p in meta['pages']) or 'none'}",
              f"Flows: {', '.join(meta['flows']) or 'none'}", f"Widths {meta['widths']}, schemes {meta['schemes']}", ""]
        md += [f"- {l}" for l in self.lines]
        open(os.path.join(self.out, "report.md"), "w").write("\n".join(md) + "\n")


async def main_async(a):
    from playwright.async_api import async_playwright
    widths = [int(x) for x in a.widths.split(",")]
    schemes = a.schemes.split(",")
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out = a.out or os.path.join(ROOT, "data", "verify", stamp)
    pages = list(a.pages)
    if a.changed is not None:
        ch = changed_pages(a.changed)
        pages += ch
    pages = list(dict.fromkeys(pages))
    run = Run(out, widths, schemes, axe=not a.no_axe)
    shown = pick(pages, a.max)
    if len(shown) < len(pages):
        run.note(f"{len(pages)} pages changed; checked {len(shown)} spread across them (--max {a.max})")
    flows = []
    if a.flows or a.flow:
        for f in sorted(glob.glob(os.path.join(FLOWS, "*.json"))):
            n = os.path.basename(f)[:-5]
            if a.flows or n in a.flow:
                flows.append((n, json.load(open(f))))
    if not shown and not flows:
        print("NOTE nothing to verify (no page or flow named, nothing changed)")
        return 0
    httpd, base = serve(DOCS)
    before_tmp = None
    try:
        async with async_playwright() as p:
            exe = chromium_path()
            browser = await p.chromium.launch(**({"executable_path": exe} if exe else {}))
            for page in shown:
                await run.page_check(browser, base, page, "after")
            if a.before and shown:
                before_tmp, bdocs = checkout_docs(a.before)
                bh, bbase = serve(bdocs)
                try:
                    for page in shown:
                        if not os.path.isfile(os.path.join(bdocs, page, "index.html") if page else os.path.join(bdocs, "index.html")):
                            run.note(f"{page}: new page, nothing before it")
                            continue
                        await run.page_check(browser, bbase, page, "before")
                        for w in widths:
                            for sc in schemes:
                                n = f"{(page or 'home').replace('/', '_')}-{w}-{sc}.png"
                                if not (os.path.isfile(os.path.join(out, "before", n)) and os.path.isfile(os.path.join(out, "after", n))):
                                    continue
                                os.makedirs(os.path.join(out, "diff"), exist_ok=True)
                                pct = diff_images(os.path.join(out, "before", n), os.path.join(out, "after", n),
                                                  os.path.join(out, "diff", n), os.path.join(out, "diff", "pair-" + n))
                                run.lines.append(f"{'DIFF' if pct >= DIFF_WARN else 'SAME'} {page or 'home'} {w} {sc}: {pct}% of pixels changed against {a.before}")
                finally:
                    bh.shutdown()
            for n, fl in flows:
                await run.flow(browser, base, n, fl)
            await browser.close()
    finally:
        httpd.shutdown()
        if before_tmp:
            shutil.rmtree(before_tmp, ignore_errors=True)
    run.write({"when": stamp, "pages": shown, "flows": [n for n, _ in flows], "widths": widths, "schemes": schemes, "before": a.before})
    for l in run.lines:
        print(l)
    print(f"verify: {'FAIL' if run.fails else 'PASS'}, {run.fails} failing of {len(run.rows)} checks; evidence in {os.path.relpath(out, ROOT)}")
    return 1 if run.fails else 0


def selftest():
    assert page_url("http://x", "") == "http://x/" and page_url("http://x", "a/b") == "http://x/a/b/" and page_url("http://x", "404.html") == "http://x/404.html"
    paths = ["docs/index.html", "docs/chicago-trades-news/index.html", "docs/chicago-trades-news/feed.xml", "docs/e/a/use/index.html",
             "docs/chicago-pest-daily-members/index.html", "docs/zz-test/index.html", "site/pages.json", "docs/shop/index.html"]
    assert pages_from_paths(paths) == ["", "chicago-trades-news", "shop"], pages_from_paths(paths)
    many = [""] + [f"p{i:02d}" for i in range(40)]
    got = pick(many, 5)
    assert got[0] == "" and len(got) == 5 and len(set(got)) == 5, got
    assert check_flow({"page": "x/", "steps": [{"click": "#a"}, {"select": "#s", "value": "1"}, {"expect_count": ".i", "min": 1}]}) == []
    for bad in ({"steps": [{"click": "#a"}]}, {"page": "x/", "steps": []}, {"page": "x/", "steps": [{"fill": "#a"}]},
                {"page": "x/", "steps": [{"click": "#a", "tap": "#b"}]}, {"page": "x/", "steps": [{"expect_count": ".i"}]}):
        assert check_flow(bad), bad
    from PIL import Image
    d = tempfile.mkdtemp()
    a, b = os.path.join(d, "a.png"), os.path.join(d, "b.png")
    Image.new("RGB", (100, 100), (255, 255, 255)).save(a)
    im = Image.new("RGB", (100, 100), (255, 255, 255))
    for x in range(10):
        for y in range(100):
            im.putpixel((x, y), (0, 0, 0))
    im.save(b)
    pct = diff_images(a, b, os.path.join(d, "d.png"), os.path.join(d, "p.png"))
    assert pct == 10.0, pct                     # a 10 px stripe on 100 px: 10% changed
    assert diff_images(a, a, os.path.join(d, "d2.png"), os.path.join(d, "p2.png")) == 0.0
    Image.new("RGB", (100, 120), (255, 255, 255)).save(b)
    assert abs(diff_images(a, b, os.path.join(d, "d3.png"), os.path.join(d, "p3.png")) - 16.67) < 0.01   # taller page: extra rows count
    for f in sorted(glob.glob(os.path.join(FLOWS, "*.json"))):
        bad = check_flow(json.load(open(f)))
        assert not bad, (f, bad)
    shutil.rmtree(d)
    print("verify_site selftest: ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--changed", nargs="?", const="origin/main", default=None)
    ap.add_argument("--before", nargs="?", const="origin/main", default=None)
    ap.add_argument("--flows", action="store_true")
    ap.add_argument("--flow", action="append", default=[])
    ap.add_argument("--widths", default="390,1280")
    ap.add_argument("--schemes", default="light,dark")
    ap.add_argument("--max", type=int, default=15)
    ap.add_argument("--out")
    ap.add_argument("--no-axe", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    import asyncio
    sys.exit(asyncio.run(main_async(a)))
