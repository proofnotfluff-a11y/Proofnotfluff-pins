import http.server, threading, functools, os
from playwright.sync_api import sync_playwright
h = functools.partial(http.server.SimpleHTTPRequestHandler, directory="docs")
h.log_message = lambda *a: None
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 8765), h); threading.Thread(target=srv.serve_forever, daemon=True).start()
js = open(os.path.join(os.path.dirname(__file__), "wide.js")).read()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 390, "height": 900})
    pg.goto("http://127.0.0.1:8765/chicago-construction-pipeline/"); pg.wait_for_timeout(800)
    print(pg.evaluate(js)); b.close()
