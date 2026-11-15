#!/usr/bin/env python3
"""usage: stills.py OUT t1 t2 ... [--q pix=8&hs=2.5]. Full-size frames at the given seconds, to look at before a render."""
import base64, os, sys
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); a = sys.argv[1:]; qs = ""
if "--q" in a: i = a.index("--q"); qs = "?" + a[i + 1]; del a[i:i + 2]
out = a[0]; os.makedirs(out, exist_ok=True)
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None, args=["--allow-file-access-from-files", "--no-sandbox"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("file://" + os.path.join(HERE, "video", "stage.html") + qs)
    for _ in range(150):
        if pg.evaluate("window.READY === true || !!window.BOOT_ERROR"): break
        pg.wait_for_timeout(100)
    if errs or pg.evaluate("window.BOOT_ERROR"): raise SystemExit(f"stage failed: {errs} {pg.evaluate('window.BOOT_ERROR')}")
    print("duration", pg.evaluate("window.DURATION"))
    for t in a[1:]:
        url = pg.evaluate(f"(drawAt({float(t)}), document.getElementById('c').toDataURL('image/jpeg', 0.9))")
        open(os.path.join(out, f"f{float(t):06.2f}.jpg"), "wb").write(base64.b64decode(url.split(",", 1)[1]))
    b.close()
