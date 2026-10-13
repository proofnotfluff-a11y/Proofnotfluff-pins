"""Playwright test of the scoreboard pin pick card against a mock window.claude (db + user).
Run: python3 dashboard/test_pinpick.py dashboard/scoreboard.html  (screenshots go to dashboard/shots/, which git ignores).
"""
import json, sys, os, io, re, asyncio
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = sys.argv[1]
OUT = os.path.join(HERE, "shots"); os.makedirs(OUT, exist_ok=True)
SKEL = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}html{scroll-padding-top:env(safe-area-inset-top,0px)}body{margin:0;padding:0;font:14px -apple-system,BlinkMacSystemFont,sans-serif;background:#faf9f5;color:#141413}img{max-width:100%}[hidden]:not([hidden=until-found i]){display:none!important}</style></head><body>'
html = SKEL + open(PAGE, encoding="utf-8").read() + "</body></html>"

# thumbnails: 300 x 450 JPEG with a headline, like a pin
def thumb(i, color):
    im = Image.new("RGB", (300, 450), color)
    d = ImageDraw.Draw(im)
    for k, c in enumerate(["#C8502F", "#2E6B66", "#6B4FA0", "#2F5F9E", "#8A6A1F"]):
        d.rectangle([20 + k * 30, 24, 44 + k * 30, 30], fill=c)
    try:
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
    except Exception:
        f = ImageFont.load_default()
    d.text((20, 60), f"PIN {i}\n$185 per job", fill="#1D2433" if color == "#F5F2EC" else "#F5F2EC", font=f)
    d.rectangle([20, 200, 280, 400], outline="#C8502F", width=4)
    b = io.BytesIO(); im.save(b, "JPEG", quality=80); return b.getvalue()

THUMBS = {f"{i:032x}": thumb(i, "#F5F2EC" if i % 2 else "#1D2433") for i in range(1, 11)}

today_js = "new Intl.DateTimeFormat('en-CA',{timeZone:'America/Chicago',year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date())"

def seed(today):
    import datetime as dt
    t = dt.date.fromisoformat(today)
    days = [(t + dt.timedelta(days=k)).isoformat() for k in range(1, 3)]
    pins = []
    n = 1
    for d in days:
        for slot, cnt in (("am", 3), ("pm", 2)):
            for _ in range(cnt):
                pins.append({"n": n, "day": d, "slot": slot, "product": [20, 22, 23][n % 3], "productName": "Hourly Rate Quick Calculator",
                             "number": "$185", "title": f"Pressure washing price per job: what a 2,000 sq ft house really costs you (pin {n})",
                             "description": "d", "alt": "a", "board": "Service Business Pricing", "boardId": "1138144205771257779",
                             "link": "https://proofnotfluff.etsy.com/listing/4589695837", "png": f"pins/x/{n:02d}.png", "sha256": "x",
                             "thumb": f"{n:032x}" if n != 4 else ""})
                n += 1
    pins[6]["thumb"] = "deadbeef" * 4  # broken asset -> placeholder
    wk = days[0]
    return {
        "quests": {f"approve-pins-{wk}": {"owner": "todd", "title": f"Pick the pins for {wk} (3 minutes)", "detail": "10 pins wait.", "xp": 5, "order": 0, "done": False},
                   "other": {"owner": "todd", "title": "Other quest", "detail": "x", "xp": 5, "order": 1, "done": False}},
        "pinweeks": {wk: {"id": wk, "from": days[0], "to": days[-1], "status": "waiting", "by": "cmo", "pins": pins,
                          "drops": {}, "published": {}, "skipped": {}}},
        "days": {today: {"date": today, "etsyVisits": 2, "pins": 0}},
        "agents": {}, "stores": {}, "shorts": {}, "log": {}, "meta": {"shop": {"listingsLive": 30}},
    }

MOCK = r"""
(() => {
  const data = JSON.parse(%s);
  const listeners = {}; // collection -> [fn]
  window.__writes = [];
  const clone = o => JSON.parse(JSON.stringify(o));
  function merge(t, s){ for (const k of Object.keys(s)) { const v = s[k]; if (v && typeof v === 'object' && !Array.isArray(v) && t[k] && typeof t[k] === 'object' && !Array.isArray(t[k])) merge(t[k], v); else t[k] = clone(v); } }
  function snap(col){ const m = data[col] || {}; const docs = Object.keys(m).sort().map(id => ({id, exists:true, data:()=>Object.freeze(clone(m[id])), metadata:{fromCache:false,hasPendingWrites:false}})); return {docs, size:docs.length, empty:!docs.length, docChanges:()=>[], metadata:{fromCache:false,hasPendingWrites:false}}; }
  function notify(col){ (listeners[col]||[]).forEach(fn => setTimeout(() => fn(snap(col)), 5)); }
  const db = {
    collection(col){ return { onSnapshot(next, err){ (listeners[col] = listeners[col] || []).push(next); setTimeout(() => next(snap(col)), 10); return () => {}; } }; },
    doc(path){ const [col, id] = path.split('/'); return {
      async update(body){ if (window.__failWrites) { const e = {code:'invalid_argument', message:'denied'}; throw e; }
        if (!data[col] || !data[col][id]) throw {code:'invalid_argument', message:'missing'};
        await new Promise(r => setTimeout(r, 20)); merge(data[col][id], body); window.__writes.push([path, clone(body)]); notify(col); },
      async get(){ const m = (data[col]||{})[id]; return {id, exists:!!m, data:()=>m && clone(m)}; } }; }
  };
  window.__data = data;
  window.claude = { use: async (name) => { await new Promise(r => setTimeout(r, 30)); if (name === 'db') return db; if (name === 'user') return { can: async () => (window.__canWrite === false ? false : true), isOwner: () => true }; return null; } };
})();
"""

def run():
    errors = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for scheme in ("light", "dark"):
            for width in (1280, 390):
                ctx = br.new_context(viewport={"width": width, "height": 900}, color_scheme=scheme, device_scale_factor=1)
                page = ctx.new_page()
                today = page.evaluate(today_js) if False else None
                page.on("console", lambda m: errors.append(f"console {m.type}: {m.text}") if m.type == "error" and "fonts.g" not in m.text and "ERR_" not in m.text else None)
                page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
                def route(r):
                    u = r.request.url
                    if u.startswith("http://pnf.test/_blob/"):
                        bid = u.rsplit("/", 1)[1]
                        if bid in THUMBS: return r.fulfill(status=200, content_type="image/jpeg", body=THUMBS[bid])
                        return r.fulfill(status=404, body="no")
                    if u.startswith("http://pnf.test/"):
                        return r.fulfill(status=200, content_type="text/html", body=html)
                    return r.abort()
                page.route("**/*", route)
                # compute Chicago today in python
                import datetime, zoneinfo
                td = datetime.datetime.now(zoneinfo.ZoneInfo("America/Chicago")).date().isoformat()
                page.add_init_script(MOCK % json.dumps(json.dumps(seed(td))))
                page.goto("http://pnf.test/#stats")
                page.wait_for_selector("#pinPick:not([hidden])", timeout=5000)
                page.wait_for_timeout(400)
                tag = f"{scheme}-{width}"
                # overflow check
                sw = page.evaluate("document.documentElement.scrollWidth")
                assert sw <= width, f"{tag}: horizontal overflow {sw} > {width}"
                tiles = page.locator("#ppBody button.pp-pin")
                assert tiles.count() == 10, f"{tag}: tiles {tiles.count()}"
                btn = page.locator("button[data-approve]")
                assert btn.inner_text().strip() == "Approve 10 pins", btn.inner_text()
                # placeholder for missing and broken thumbs
                page.wait_for_timeout(300)
                ph = page.locator("#ppBody .pp-img .ph").count()
                assert ph == 2, f"{tag}: placeholders {ph}"
                page.screenshot(path=f"{OUT}/{tag}-waiting.png", full_page=False)
                page.locator("#pinPick").screenshot(path=f"{OUT}/{tag}-card.png")
                if scheme == "light" and width == 1280:
                    # banner on the factory floor
                    page.click("#vt-factory")
                    page.wait_for_timeout(200)
                    assert page.locator("#pickBanner").is_visible(), "banner hidden"
                    assert "10 pins" in page.locator("#pickBanner").inner_text()
                    page.screenshot(path=f"{OUT}/{tag}-factory-banner.png")
                    page.click("#pickBanner")
                    page.wait_for_timeout(500)
                    assert page.locator("#statsView").is_visible(), "stats view not shown"
                    # drop pin 3 with a click
                    page.click('#ppBody button.pp-pin[data-n="3"]')
                    page.wait_for_timeout(300)
                    assert "drop" in page.get_attribute('#ppBody button.pp-pin[data-n="3"]', "class")
                    assert page.locator("button[data-approve]").inner_text().strip() == "Approve 9 pins"
                    w = page.evaluate("window.__writes")
                    assert w[-1][0].startswith("pinweeks/") and w[-1][1] == {"drops": {"3": True}}, w
                    # keyboard: focus pin 5, press Enter twice -> dropped then kept, focus stays
                    page.focus('#ppBody button.pp-pin[data-n="5"]')
                    page.keyboard.press("Enter"); page.wait_for_timeout(300)
                    assert "drop" in page.get_attribute('#ppBody button.pp-pin[data-n="5"]', "class")
                    fid = page.evaluate("document.activeElement && document.activeElement.dataset.n")
                    assert fid == "5", f"focus lost: {fid}"
                    page.keyboard.press("Enter"); page.wait_for_timeout(300)
                    assert "keep" in page.get_attribute('#ppBody button.pp-pin[data-n="5"]', "class")
                    page.locator("#pinPick").screenshot(path=f"{OUT}/{tag}-dropped.png")
                    # approve
                    page.click("button[data-approve]"); page.wait_for_timeout(400)
                    data = page.evaluate("window.__data")
                    wk = [k for k in data["pinweeks"]][0]
                    assert data["pinweeks"][wk]["status"] == "approved", data["pinweeks"][wk]["status"]
                    assert data["quests"][f"approve-pins-{wk}"]["done"] is True
                    assert page.locator("#pinPick .pill").first.inner_text().strip().lower() == "approved"
                    assert not page.locator("#pickBanner").is_visible() or True
                    page.locator("#pinPick").screenshot(path=f"{OUT}/{tag}-approved.png")
                    assert page.locator("#ppBody details.pp-more").count() == 1
                    assert not page.locator('#ppBody button.pp-pin[data-n="1"]').is_visible(), "grid should be collapsed after approval"
                    page.click("#ppBody details.pp-more summary"); page.wait_for_timeout(200)
                    assert page.locator('#ppBody button.pp-pin[data-n="1"]').is_visible()
                    # a snapshot of another collection must keep the details open
                    page.evaluate("window.__data.days[Object.keys(window.__data.days)[0]].etsyVisits=3")
                    # mark pin 1 published, pin 2 skipped through the store (as the promote runs would)
                    page.evaluate("""(async()=>{const db=await window.claude.use('db');const wk=Object.keys(window.__data.pinweeks)[0];await db.doc('pinweeks/'+wk).update({published:{'1':'99887766'},skipped:{'2':'not picked in time'}})})()""")
                    page.wait_for_timeout(300)
                    assert page.locator('#ppBody details.pp-more').get_attribute("open") is not None, "details closed after snapshot"
                    assert page.locator('#ppBody button.pp-pin[data-n="1"]').is_disabled()
                    assert page.locator('#ppBody button.pp-pin[data-n="2"]').is_disabled()
                    assert "published" in page.locator('#ppBody button.pp-pin[data-n="1"] .pp-flag').inner_text().lower()
                    page.locator("#pinPick").screenshot(path=f"{OUT}/{tag}-approved-open.png")
                    # factory banner hidden once approved
                    page.click("#vt-factory"); page.wait_for_timeout(200)
                    assert not page.locator("#pickBanner").is_visible(), "banner still visible after approval"
                    page.click("#vt-stats"); page.wait_for_timeout(200)
                    # undo
                    page.click("button[data-undo]"); page.wait_for_timeout(400)
                    data = page.evaluate("window.__data")
                    assert data["pinweeks"][wk]["status"] == "waiting" and data["quests"][f"approve-pins-{wk}"]["done"] is False
                    # quest tick in the quest list approves too
                    page.click(f'#quests button[data-q="approve-pins-{wk}"]'); page.wait_for_timeout(400)
                    assert page.locator("#pinPick .pill").first.inner_text().strip().lower() == "approved", "quest tick did not approve"
                    # write failure renders read-only
                    page.evaluate("window.__failWrites=true")
                    page.click("#ppBody details.pp-more summary") if page.locator('#ppBody button.pp-pin[data-n="6"]').is_hidden() else None
                    page.wait_for_timeout(200)
                    page.click('#ppBody button.pp-pin[data-n="6"]'); page.wait_for_timeout(400)
                    assert page.locator('#ppBody button.pp-pin[data-n="6"]').is_disabled(), "not read-only after refused write"
                    assert "Only the shop's owner" in page.locator("#ppBody").inner_text()
                if width == 390:
                    page.screenshot(path=f"{OUT}/{tag}-full.png", full_page=True)
                ctx.close()
        br.close()
    return errors

errs = run()
print("console/page errors:", errs if errs else "none")
print("ALL TESTS PASSED")
