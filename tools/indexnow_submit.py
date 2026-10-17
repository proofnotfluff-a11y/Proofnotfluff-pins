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

def diagnose(last):
    """One plain line on why the key file failed, so the log says what to fix (optimizer, Oct 17)."""
    try:
        body = urllib.request.urlopen("http://" + HOST + "/" + KEY + ".txt", timeout=20).read().decode().strip()
        http_ok = body == KEY
    except Exception:
        http_ok = False
    if http_ok and ("CERTIFICATE" in last.upper() or "SSL" in last.upper()):
        return ("DIAGNOSIS: the site serves over http but https fails its certificate check: GitHub Pages has not "
                "issued the certificate. Fix (repo admin): Settings, Pages, remove the custom domain, retype it, Save, "
                "then tick Enforce HTTPS once it shows (docs.github.com, Securing your GitHub Pages site with HTTPS).")
    if http_ok:
        return "DIAGNOSIS: http serves the key file but https does not answer; check the Pages certificate and DNS."
    return "DIAGNOSIS: the key file is not served over http either; check docs/CNAME, DNS and the Pages deploy."

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
    last = "no answer"
    for i in range(20):
        try:
            body = urllib.request.urlopen(KEY_URL, timeout=20).read().decode().strip()
            if body == KEY: break
            last = "served, but the body is not the key"
        except Exception as e:
            last = type(e).__name__ + ": " + str(getattr(e, "reason", e))[:200]
        time.sleep(30)
    else:
        print("Key file not live at", KEY_URL)
        print("Last https error:", last)
        print(diagnose(last))
        return 1
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
