#!/usr/bin/env python3
"""Submit free-site URLs to IndexNow (Bing, Yandex, Seznam, Naver and the other IndexNow engines).

Run by .github/workflows/indexnow.yml on GitHub's runners (the cloud sessions' proxy blocks
these hosts). Submits only URLs in docs/sitemap.xml, which holds cleared pages only
(drafts stay out until the Legal desk clears them). First run (key file new) or
--all submits every URL; otherwise only URLs added since the previous commit's sitemap.
No account, no cost: https://www.indexnow.org/documentation (COO, Oct 13, 2026;
scout finding indexnow-free-site).
"""
import json, re, subprocess, sys, time, urllib.request

KEY = "cdccc9befa99e9cfa2a85549b2b1160d"
HOST = "proofnotfluff.com"
BASE = "https://proofnotfluff.com/"
KEY_URL = BASE + KEY + ".txt"

def locs(text):
    return re.findall(r"<loc>([^<]+)</loc>", text or "")

def git_show(path):
    try:
        return subprocess.run(["git", "show", "HEAD~1:" + path], capture_output=True, text=True, check=True).stdout
    except Exception:
        return None

def main():
    now = locs(open("docs/sitemap.xml").read())
    prev_key = git_show("docs/" + KEY + ".txt")
    if "--all" in sys.argv or prev_key is None:
        urls = now
    else:
        before = set(locs(git_show("docs/sitemap.xml")))
        urls = [u for u in now if u not in before]
    urls = [u for u in urls if u.startswith(BASE)]
    if not urls:
        print("No new URLs to submit."); return 0
    # wait until GitHub Pages serves the key file (deploy lag)
    for i in range(20):
        try:
            body = urllib.request.urlopen(KEY_URL, timeout=20).read().decode().strip()
            if body == KEY: break
        except Exception as e:
            pass
        time.sleep(30)
    else:
        print("Key file not live at", KEY_URL); return 1
    payload = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_URL, "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=payload,
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        print("IndexNow", r.status, "for", len(urls), "URLs")
    except urllib.error.HTTPError as e:
        print("IndexNow HTTP", e.code, e.read()[:300]); return 0 if e.code in (200, 202) else 1
    for u in urls: print(" ", u)
    return 0

if __name__ == "__main__":
    sys.exit(main())
