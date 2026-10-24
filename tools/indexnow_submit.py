#!/usr/bin/env python3
"""Tell Bing and the other IndexNow engines which proofnotfluff.com pages are new or changed.

Run by .github/workflows/indexnow.yml on GitHub's runners (the cloud sessions' proxy blocks these hosts).
No account, no cost: https://www.indexnow.org/documentation (COO, Oct 13, 2026; changed-pages version on
Todd's go, Oct 23, 2026).

What it sends, and only this:
  - pages whose docs/ file changed between --since <commit> and HEAD (docs/index.html is the home page,
    docs/<slug>/index.html is https://proofnotfluff.com/<slug>/), plus URLs newly added to docs/sitemap.xml;
  - and of those, only URLs listed in docs/sitemap.xml whose committed page carries no robots noindex tag.
    The sitemap holds cleared pages only, so drafts, members' pages and noindex pages are never sent.
  --all sends every sitemap URL that passes the same filter. --dry-run prints the list and sends nothing.

The key file docs/<key>.txt is written by tools/make_site.py (INDEXNOW_KEY). Before sending, the script waits
for GitHub Pages to finish building HEAD (so Bing reads the new page, not the old one) and for the key file to
be live. Exit 0 on HTTP 200 or 202 or when there is nothing to send; 1 on any failure, so the run shows red.
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_site import BASE, INDEXNOW_KEY as KEY  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = BASE.split("/")[2]
KEY_URL = BASE + KEY + ".txt"
ENDPOINT = "https://api.indexnow.org/indexnow"


def git(*args, check=True):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=check)


def locs(text):
    return re.findall(r"<loc>([^<]+)</loc>", text or "")


def url_to_file(url):
    """https://proofnotfluff.com/<slug>/ -> docs/<slug>/index.html; the home page -> docs/index.html."""
    path = url[len(BASE):] if url.startswith(BASE) else None
    if path is None:
        return None
    return os.path.join("docs", path, "index.html") if path else os.path.join("docs", "index.html")


def file_to_url(rel):
    """docs/<slug>/index.html -> https://proofnotfluff.com/<slug>/; other files (css, data, images) map to no page."""
    rel = rel.replace(os.sep, "/")
    if rel == "docs/index.html":
        return BASE
    m = re.fullmatch(r"docs/(.+)/index\.html", rel)
    return BASE + m.group(1) + "/" if m else None


def is_indexable(url):
    """True when the committed page exists and carries no robots noindex tag."""
    f = url_to_file(url)
    if not f or not os.path.isfile(os.path.join(ROOT, f)):
        return False
    return not has_noindex(open(os.path.join(ROOT, f), encoding="utf-8", errors="replace").read(20000))


def has_noindex(html):
    """A robots, googlebot or bingbot meta tag with noindex, in any quoting."""
    for tag in re.findall(r"<meta[^>]+>", html.lower()):
        if re.search(r"name\s*=\s*[\"']?(robots|googlebot|bingbot)\b", tag) and "noindex" in tag:
            return True
    return False


def still_live(urls):
    """Recheck against the newest main just before sending: a page made noindex or dropped from the sitemap
    by a later push is never sent. If main can't be fetched, keep this commit's answer."""
    if git("fetch", "--quiet", "--depth=1", "origin", "main", check=False).returncode != 0:
        return urls
    smap = git("show", "FETCH_HEAD:docs/sitemap.xml", check=False)
    if smap.returncode != 0:
        return urls
    live = set(locs(smap.stdout))
    keep = []
    for u in urls:
        page = git("show", "FETCH_HEAD:" + url_to_file(u).replace(os.sep, "/"), check=False)
        if u in live and page.returncode == 0 and not has_noindex(page.stdout[:20000]):
            keep.append(u)
        else:
            print("  dropped (no longer live on main)", u)
    return keep


def have_commit(sha):
    return git("cat-file", "-e", sha + "^{commit}", check=False).returncode == 0


def changed_urls(since):
    """Pages changed between `since` and HEAD, plus URLs newly added to the sitemap. None if `since` is unusable."""
    if not since or set(since) == {"0"}:
        return None
    if not have_commit(since):
        git("fetch", "--quiet", "--depth=1", "origin", since, check=False)
    if not have_commit(since):
        return None
    names = [n for n in git("-c", "core.quotepath=off", "diff", "-z", "--name-only", since, "HEAD", "--", "docs/").stdout.split("\0") if n]
    urls = [u for u in (file_to_url(n) for n in names) if u]
    old_map = git("show", since + ":docs/sitemap.xml", check=False).stdout
    added = [u for u in locs(open(os.path.join(ROOT, "docs", "sitemap.xml"), encoding="utf-8").read())
             if u not in set(locs(old_map))]
    return list(dict.fromkeys(urls + added))


def wait_for_pages(timeout=600):
    """Wait until GitHub Pages reports HEAD built. Needs GITHUB_REPOSITORY and GH_TOKEN; skipped without them."""
    repo, token = os.environ.get("GITHUB_REPOSITORY"), os.environ.get("GH_TOKEN")
    if not repo or not token:
        return "skipped (no repo token)"
    head = git("rev-parse", "HEAD").stdout.strip()
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/pages/builds/latest",
                                 headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json"})
    end, last = time.time() + timeout, "no answer"
    while time.time() < end:
        try:
            b = json.load(urllib.request.urlopen(req, timeout=20))
            last = f"{b.get('status')} at {str(b.get('commit'))[:7]}"
            built = b.get("commit") or ""
            if b.get("status") == "built" and built:
                if built == head:
                    return "built " + head[:7]
                git("fetch", "--quiet", "--depth=50", "origin", built, check=False)
                if git("merge-base", "--is-ancestor", head, built, check=False).returncode == 0:
                    return "built " + built[:7] + " (includes " + head[:7] + ")"
            if b.get("status") == "errored" and built == head:
                return "errored " + head[:7]
        except urllib.error.HTTPError as e:
            if e.code in (401, 403, 404):
                return "skipped (Pages API " + str(e.code) + ")"
            last = "HTTP " + str(e.code)
        except Exception as e:
            last = type(e).__name__
        time.sleep(20)
    return "not confirmed in time (last: " + last + ")"


def wait_for_key():
    last = "no answer"
    for _ in range(10):
        try:
            body = urllib.request.urlopen(KEY_URL, timeout=20).read().decode().strip()
            if body == KEY:
                return None
            last = "served, but the body is not the key"
        except Exception as e:
            last = type(e).__name__ + ": " + str(getattr(e, "reason", e))[:200]
        time.sleep(30)
    return last


def main(argv):
    sitemap = locs(open(os.path.join(ROOT, "docs", "sitemap.xml"), encoding="utf-8").read())
    live = set(sitemap)
    since = argv[argv.index("--since") + 1] if "--since" in argv and argv.index("--since") + 1 < len(argv) else ""
    if "--all" in argv:
        candidates, mode = sitemap, "all"
    else:
        candidates, mode = changed_urls(since), "changed since " + (since[:7] or "?")
        if candidates is None:
            print("Base commit", since[:7] or "(none)", "is not reachable; nothing sent. Fix: Actions, IndexNow submit, Run workflow with all = true (it resends every live page and resets the base).")
            return 1
    urls = [u for u in candidates if u in live and is_indexable(u)]
    skipped = [u for u in candidates if u not in urls]
    print(f"Mode: {mode}. {len(candidates)} candidate URLs, {len(urls)} to send, {len(skipped)} skipped (not in the sitemap or noindex).")
    for u in skipped:
        print("  skip", u)
    if not urls:
        print("No new or changed live URLs to submit.")
        return 0
    if "--dry-run" in argv:
        for u in urls:
            print("  would send", u)
        return 0
    print("Pages build:", wait_for_pages())
    urls = still_live(urls)
    if not urls:
        print("Nothing left to send after the recheck against main.")
        return 0
    missing = wait_for_key()
    if missing:
        print("Key file not live at", KEY_URL, "-", missing)
        return 1
    if len(urls) > 10000:
        print("More than 10,000 URLs; sending the first 10,000 (the IndexNow limit per request).")
    payload = json.dumps({"host": HOST, "key": KEY, "keyLocation": KEY_URL, "urlList": urls[:10000]}).encode()
    req = urllib.request.Request(ENDPOINT, data=payload, headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        r = urllib.request.urlopen(req, timeout=30)
        code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
        print("IndexNow HTTP", code, e.read()[:300])
    except urllib.error.URLError as e:
        print("IndexNow not reached:", str(e.reason)[:200])
        return 1
    print("IndexNow", code, "for", len(urls), "URLs")
    for u in urls:
        print("  ", u)
    return 0 if code in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
