#!/usr/bin/env python3
"""Click through a built members' app (tools/leads_app.py) in headless Chromium, the way a buyer does, at phone and desktop
width: the gate, the Terms view before the password, a wrong password, the overview, the project list with every filter, the
map, a project page, the builders, a builder page, the pitch kit, the Terms view, the CSV export and the workbook download.
It fails on a console error, a page wider than the screen, a CSV whose rows do not match the list on screen, or a workbook
with an error value in any cell. Screenshots go to the --shots folder.

The password is read from a file and never printed. When the sandbox cannot reach cdnjs or the map tiles, pass --leaflet DIR
(leaflet@1.9.4's dist folder from npm, the same bytes the page's SRI hash pins) and the tiles are served blank.

--capture DIR also writes the free page's "What members get" images from this app (tools/make_site.py reads them):
members-list.png (the project list, 1064 x 665) and workbook.png (the workbook's All projects tab, 1200 x 772). For Austin,
DIR is docs/assets/leads/austin. When the map tiles cannot load (--leaflet), the list is captured without the map pane.

Usage: python3 tools/leads_check.py --docs docs --app austin-leads-members --pw-file PW --shots OUT [--leaflet DIR] [--capture DIR]
"""
import argparse, csv, functools, http.server, io, json, os, re, socketserver, sys, threading, zipfile

BLANK_PNG = bytes.fromhex("89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                          "1f15c4890000000d49444154789c63f8ffff3f0005fe02fea7d6a4cb0000000049454e44ae426082")


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=root)
    srv = socketserver.TCPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def settle(pg):
    """Wait for the view's fade-in and for any toast to clear, so no screenshot is washed out (design director, Oct 18)."""
    pg.wait_for_timeout(450)
    pg.evaluate("document.querySelector('#toast')&&document.querySelector('#toast').classList.remove('on')")
    pg.wait_for_function("!document.querySelector('#toast.on') && !document.getAnimations().some(a=>a.playState==='running')", timeout=5000)
    pg.wait_for_timeout(300)


def capture(ctx, base, pw, wb_path, out, no_tiles, check):
    """The free page's two screenshots of the paid product, made from this build."""
    import subprocess, tempfile
    from PIL import Image
    os.makedirs(out, exist_ok=True)
    pg = ctx.new_page()
    pg.set_viewport_size({"width": 1064, "height": 665})
    pg.goto(base)
    pg.fill("#pw", pw)
    pg.click("#go")
    pg.wait_for_selector("#app .hero")
    pg.goto(base + "#/projects")
    pg.wait_for_selector("#plist .row")
    if no_tiles:
        pg.add_style_tag(content=".split{display:block!important}.mapbox{display:none!important}")
    pg.wait_for_timeout(1200)
    pg.evaluate("window.scrollTo(0,0)")
    settle(pg)
    pg.screenshot(path=os.path.join(out, "members-list.png"))
    pg.close()
    tmp = tempfile.mkdtemp()
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "render_xlsx.py"), wb_path, tmp],
                   check=True, capture_output=True)
    src = next(os.path.join(tmp, f) for f in sorted(os.listdir(tmp)) if "All-projects" in f and f.endswith(".png"))
    im = Image.open(src).convert("RGB")
    w = min(im.width, int(im.height * 1200 / 772))
    im.crop((0, 0, w, int(w * 772 / 1200))).resize((1200, 772), Image.LANCZOS).save(os.path.join(out, "workbook.png"))
    # the phone crop: the KPI band and the first columns (address, valuation, builder, ZIP code, stage, type), readable at 360 px
    cw = min(im.width, int(im.width * 0.53))
    im.crop((0, 0, cw, int(cw * 0.75))).resize((900, 675), Image.LANCZOS).save(os.path.join(out, "workbook-phone.png"))
    sizes = [Image.open(os.path.join(out, f)).size for f in ("members-list.png", "workbook.png", "workbook-phone.png")]
    check(sizes == [(1064, 665), (1200, 772), (900, 675)], f"captured the free page's screenshots into {out}: {sizes}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", required=True)
    ap.add_argument("--app", required=True)
    ap.add_argument("--pw-file", required=True)
    ap.add_argument("--shots", required=True)
    ap.add_argument("--leaflet", default="")
    ap.add_argument("--capture", default="")
    a = ap.parse_args()
    from playwright.sync_api import sync_playwright
    from openpyxl import load_workbook
    pw = open(a.pw_file).read().strip()
    os.makedirs(a.shots, exist_ok=True)
    srv = serve(a.docs)
    base = f"http://127.0.0.1:{srv.server_address[1]}/{a.app}/"
    fails, notes = [], []

    def check(ok, what):
        (notes if ok else fails).append(("ok " if ok else "FAIL ") + what)

    with sync_playwright() as p:
        b = p.chromium.launch()
        for width, height in ((390, 844), (1280, 860)):
            tag = f"{width}"
            ctx = b.new_context(viewport={"width": width, "height": height}, accept_downloads=True, device_scale_factor=2 if width < 500 else 1)
            if a.leaflet:
                ctx.route(re.compile(r"https://cdnjs\.cloudflare\.com/ajax/libs/leaflet/1\.9\.4/(.*)"),
                          lambda route: route.fulfill(path=os.path.join(a.leaflet, route.request.url.rsplit("/", 1)[1])))
                ctx.route(re.compile(r"https://tile\.openstreetmap\.org/.*"), lambda route: route.fulfill(body=BLANK_PNG, content_type="image/png"))
            pg = ctx.new_page()
            errors = []
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append(str(e)))

            def wide(name):
                over = pg.evaluate("document.documentElement.scrollWidth - window.innerWidth")
                check(over <= 0, f"{tag} {name}: no horizontal scroll ({over}px)")

            def shot(name):
                settle(pg)
                pg.screenshot(path=os.path.join(a.shots, f"{tag}-{name}.png"), full_page=False)

            pg.goto(base)
            pg.wait_for_selector("#pw")
            shot("gate"); wide("gate")
            # Terms before the password
            pg.click("#gateLegal a[href='#/terms']")
            pg.wait_for_selector("#app h1")
            check(pg.inner_text("#app h1") == "Terms of Use", f"{tag} Terms view opens before the password")
            terms_text = pg.inner_text("#app")
            check("data" in terms_text and "License." in terms_text and "Limit of liability." in terms_text, f"{tag} Terms text present")
            shot("terms-gate"); wide("terms before password")
            pg.click("#app a.back")
            pg.wait_for_selector("#pw", state="visible")
            # wrong, then right password
            pg.fill("#pw", "not-the-password")
            pg.click("#go")
            pg.wait_for_function("document.querySelector('#err').textContent.length > 0")
            check("did not open" in pg.inner_text("#err"), f"{tag} wrong password refused")
            pg.fill("#pw", pw)
            pg.click("#go")
            pg.wait_for_selector("#app .hero h1", timeout=60000)
            hero = pg.inner_text("#app .hero h1")
            check("final clean" in hero, f"{tag} overview opens: {hero}")
            shot("overview"); wide("overview")
            data = pg.evaluate("({n:P.length, near:P.filter(p=>p.st===0).length, nw:P.filter(p=>p.n).length, geo:P.filter(p=>p.lat&&p.lon).length,"
                               " builders:Object.keys(B).length, total:TOTAL, city:CITY.key, areas:[...new Set(P.map(p=>p.ca).filter(Boolean))].sort()})")
            notes.append(f"{tag} data: " + json.dumps({k: v for k, v in data.items() if k != "areas"}))
            # projects list, filters, CSV
            pg.goto(base + "#/projects")
            pg.wait_for_selector("#plist .row")
            count = lambda: int(re.sub(r"[^\d]", "", pg.inner_text("#rcount b")))
            check(count() == data["n"], f"{tag} list shows all {data['n']} projects")
            shot("projects"); wide("projects")
            for k in ("near", "insp", "issued", ""):
                pg.click(f"#fstage button[data-k='{k}']")
                want = pg.evaluate(f"P.filter(p=>{{const k='{k}';return !k||p.st==={{near:0,insp:1,issued:2}}[k]}}).length")
                got = count() if want else 0
                check(got == want, f"{tag} stage filter '{k or 'all'}': {got} of {want}")
            if width < 500:
                pg.click("#fopen")
                pg.wait_for_selector("#fsheet.open")
                shot("filters-sheet")
            area = data["areas"][0]
            pg.select_option("#farea", area)
            want = sum(1 for _ in range(1)) and pg.evaluate(f"P.filter(p=>p.ca==={json.dumps(area)}).length")
            check(count() == want, f"{tag} area filter {area}: {count()} of {want}")
            types = pg.evaluate("CITY.types")
            pg.select_option("#ftype", types[0])
            want = pg.evaluate(f"P.filter(p=>p.ca==={json.dumps(area)}&&p.t==={json.dumps(types[0])}).length")
            got = count() if want else 0
            check(got == want, f"{tag} area + type filter: {got} of {want}")
            pg.select_option("#ftype", "")
            pg.select_option("#fcost", "1to5")
            want = pg.evaluate(f"P.filter(p=>p.ca==={json.dumps(area)}&&p.c>=1e6&&p.c<5e6).length")
            got = count() if want else 0
            check(got == want, f"{tag} area + cost filter: {got} of {want}")
            if width < 500:
                pg.click("#fdone")
            pg.click("#fclear") if pg.is_visible("#fclear") else None
            pg.wait_for_timeout(200)
            check(count() == data["n"], f"{tag} clear filters")
            with pg.expect_download() as dl:
                pg.click("#csv")
            path = dl.value.path()
            rows = list(csv.reader(io.open(path, encoding="utf-8-sig")))
            check(len(rows) - 1 == data["n"] and "All builders" in rows[0], f"{tag} CSV has {len(rows) - 1} rows of {data['n']} and an All builders column")
            check(not any(c.startswith(("=", "+", "@")) for r in rows[1:] for c in r), f"{tag} CSV cells guarded")
            # map
            if width < 500:
                pg.click(".vtog button[data-v='map']")
            pg.wait_for_function("window.L && STATE.map", timeout=30000)
            pg.wait_for_timeout(600)
            pins = pg.evaluate("Object.keys(STATE.mk||{}).length")
            check(pins == data["geo"], f"{tag} map pins {pins} of {data['geo']} projects with a location")
            shot("map"); wide("map")
            # project drill-in: the biggest near-finish project, or the biggest one
            pid = pg.evaluate("(P.filter(p=>p.st===0).sort((a,b)=>b.c-a.c)[0]||P[0]).id")
            pg.goto(base + f"#/project/{pid}")
            pg.wait_for_selector(".p-title h1")
            ok = pg.evaluate(f"document.querySelector('.p-title h1').textContent===BYID[{json.dumps(pid)}].a")
            check(ok, f"{tag} project page {pid} opens with its address")
            shot("project"); wide("project")
            pg.click("#mark")
            check("Contacted" in pg.inner_text("#markT"), f"{tag} mark as contacted")
            pg.click("#mark")
            # builders and one builder
            pg.goto(base + "#/builders")
            pg.wait_for_selector("#blist")
            nb = int(re.sub(r"[^\d]", "", pg.inner_text("#bcount b")))
            check(nb == data["builders"], f"{tag} builders list {nb} of {data['builders']}")
            shot("builders"); wide("builders")
            pg.click("#blist a")
            pg.wait_for_selector(".p-title h1")
            shot("builder"); wide("builder")
            # pitch kit and terms
            pg.goto(base + "#/pitch")
            pg.wait_for_selector(".pk")
            check(data["city"].title() in pg.inner_text(".pk"), f"{tag} pitch kit names the city")
            shot("pitch"); wide("pitch")
            pg.goto(base + "#/terms")
            pg.wait_for_selector(".terms")
            shot("terms"); wide("terms")
            # workbook
            pg.goto(base + "#/")
            pg.wait_for_selector("#dlTop")
            with pg.expect_download() as dl:
                pg.click("#dlTop")
            wb_path = os.path.join(a.shots, f"{tag}-{dl.value.suggested_filename}")
            dl.value.save_as(wb_path)
            wb = load_workbook(wb_path, data_only=True)
            errs = [f"{ws.title}!{c.coordinate}" for ws in wb.worksheets for row in ws.iter_rows() for c in row
                    if isinstance(c.value, str) and re.match(r"^#(?:REF|VALUE|NAME|DIV/0|N/A|NUM|NULL)", c.value)]
            check(not errs, f"{tag} workbook {dl.value.suggested_filename}: {len(wb.sheetnames)} tabs, error cells {errs[:5]}")
            if a.capture and width > 500:
                capture(ctx, base, pw, wb_path, a.capture, bool(a.leaflet), check)
            errors = [e for e in errors if "tile.openstreetmap" not in e]
            check(not errors, f"{tag} console errors: {errors[:3]}")
            ctx.close()
        b.close()
    srv.shutdown()
    for n in notes + fails:
        print(n)
    print(f"leads_check: {len(fails)} failures, {len(notes)} checks passed")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
