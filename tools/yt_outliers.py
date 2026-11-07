#!/usr/bin/env python3
"""Weekly outlier finder for the proven idea lane (YouTube Data API v3, official, read only).

Todd, live chat, Nov 7, 2026, 12:08 pm: "Go", to the proven idea lane; 2:45 pm: "key added", the YouTube Data API key
saved as the repo secret YOUTUBE_API_KEY (video/studio/research/PROVEN.md). For every channel in
video/studio/research/proven-channels.json: its newest 50 uploads, the Shorts among them (180 s or less), the median
views of those Shorts (the channel's typical), and every Short with 5x that median or more, 1,000 views or more, posted
in the last 365 days. Then the search queries in the same file (Shorts, last 30 days, most viewed) to surface channels
we don't follow yet, listed by channel ID only. Writes video/studio/research/outliers.json; a run of the studio's
proven lane reads it when every PROVEN.md row with a sourceprint is used (_shared/formats.md "Proven").

    python3 tools/yt_outliers.py [--out PATH]      needs YOUTUBE_API_KEY in the environment (only the workflow has it)
    python3 tools/yt_outliers.py --selftest        planted cases, no network

Quota (default 10,000 units a day): channels.list, playlistItems.list and videos.list cost 1 unit a call (50 ids a
call); search.list costs 100. A run of 35 channels and 8 searches spends about 1,000. Standard library only. The key
is sent only as a query parameter to googleapis.com and scrubbed from every error; nothing is posted or changed.
"""
import argparse, datetime as dt, json, os, re, statistics, sys, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHANNELS = os.path.join(ROOT, "video", "studio", "research", "proven-channels.json")
OUT = os.path.join(ROOT, "video", "studio", "research", "outliers.json")
API = "https://www.googleapis.com/youtube/v3/"
RULES = {"ratio": 5.0, "min_views": 1000, "max_seconds": 180, "max_age_days": 365, "min_shorts": 8, "newest": 50}


class ApiError(Exception):
    pass


class Client:
    def __init__(self, key):
        self.key, self.units = key, 0

    def get(self, path, cost=1, **params):
        q = urllib.parse.urlencode(dict(params, key=self.key))
        self.units += cost
        try:
            with urllib.request.urlopen(API + path + "?" + q, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise ApiError(scrub(f"{path}: HTTP {e.code}: {body}", self.key)) from None
        except urllib.error.URLError as e:
            raise ApiError(scrub(f"{path}: {e.reason}", self.key)) from None


def scrub(text, key):
    return text.replace(key, "<key>") if key else text


def seconds(iso):
    """ISO 8601 duration (PT1M5S) to seconds."""
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", iso or "")
    if not m:
        return None
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def chunks(xs, n=50):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def video_rows(client, ids):
    rows = []
    for part in chunks(ids):
        d = client.get("videos", part="statistics,contentDetails,snippet", id=",".join(part), maxResults=50)
        for it in d.get("items", []):
            st, sn = it.get("statistics", {}), it.get("snippet", {})
            rows.append({"video": it["id"], "channel": sn.get("channelId"), "title": sn.get("title", "")[:120],
                         "published": (sn.get("publishedAt") or "")[:10], "seconds": seconds(it.get("contentDetails", {}).get("duration")),
                         "views": int(st["viewCount"]) if "viewCount" in st else None})
    return rows


def analyze(rows, today, rules=RULES):
    """rows: one channel's newest uploads. Returns (shorts count, typical views or None, outliers)."""
    shorts = [r for r in rows if r["seconds"] is not None and r["seconds"] <= rules["max_seconds"] and r["views"] is not None]
    if len(shorts) < rules["min_shorts"]:
        return len(shorts), None, []
    typical = statistics.median(r["views"] for r in shorts)
    cut = (today - dt.timedelta(days=rules["max_age_days"])).isoformat()
    out = [dict(r, typical=typical, ratio=round(r["views"] / typical, 1)) for r in shorts
           if typical > 0 and r["views"] >= rules["ratio"] * typical and r["views"] >= rules["min_views"] and r["published"] >= cut]
    return len(shorts), typical, sorted(out, key=lambda r: -r["ratio"])


def channel_report(client, cid, label, today):
    d = client.get("channels", part="contentDetails", id=cid)
    items = d.get("items", [])
    if not items:
        return {"id": cid, "label": label, "error": "not found"}, []
    up = items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = client.get("playlistItems", part="contentDetails", playlistId=up, maxResults=RULES["newest"])
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
    n, typical, outs = analyze(video_rows(client, ids), today)
    for o in outs:
        o["label"], o["url"] = label, f"https://www.youtube.com/shorts/{o['video']}"
    return {"id": cid, "label": label, "shorts": n, "typical": typical}, outs


def run(client, cfg, today):
    report = {"schema": "pnf.studio.outliers.v1", "read": today.isoformat(), "rules": RULES, "channels": [], "outliers": [],
              "new_channels": [], "errors": []}
    known = {c["id"] for c in cfg["channels"]}
    for c in cfg["channels"]:
        try:
            row, outs = channel_report(client, c["id"], c["label"], today)
            report["channels"].append(row); report["outliers"] += outs
        except ApiError as e:
            report["errors"].append(str(e))
    after = (today - dt.timedelta(days=30)).isoformat() + "T00:00:00Z"
    found = {}
    for q in cfg.get("searches", []):
        try:
            d = client.get("search", cost=100, part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                           publishedAfter=after, maxResults=25, relevanceLanguage="en", regionCode="US")
        except ApiError as e:
            report["errors"].append(str(e)); continue
        for it in d.get("items", []):
            cid = it.get("snippet", {}).get("channelId")
            if cid and cid not in known:
                found.setdefault(cid, set()).add(q)
    for cid, qs in sorted(found.items(), key=lambda kv: -len(kv[1]))[:20]:
        try:
            row, outs = channel_report(client, cid, "not yet labeled", today)
        except ApiError as e:
            report["errors"].append(str(e)); continue
        row["queries"] = sorted(qs); row["outliers"] = len(outs)
        report["new_channels"].append(row)
        for o in outs:
            o["new_channel"] = True
        report["outliers"] += outs
    report["outliers"].sort(key=lambda r: -r["ratio"])
    report["quota_units"] = client.units
    return report


def selftest():
    today = dt.date(2026, 11, 7)
    mk = lambda v, s=40, p="2026-10-20": {"video": f"v{v}", "channel": "c", "title": "", "published": p, "seconds": s, "views": v}
    base = [mk(100 + i) for i in range(10)]
    cases = []
    n, t, o = analyze(base + [mk(5000)], today)
    cases.append(("a 5x Short is found", [x["views"] for x in o] == [5000]))
    n, t, o = analyze(base + [mk(520)], today)
    cases.append(("under 1,000 views is not an outlier", o == []))
    n, t, o = analyze(base + [mk(9000, s=600)], today)
    cases.append(("a long video is not a Short", o == [] and n == 10))
    n, t, o = analyze(base + [mk(9000, p="2025-10-01")], today)
    cases.append(("older than a year is left out", o == []))
    n, t, o = analyze(base[:5] + [mk(9000)], today)
    cases.append(("too few Shorts gives no typical", t is None and o == []))
    n, t, o = analyze([mk(200 + i) for i in range(10)] + [mk(999)], today)
    cases.append(("4.6x is not 5x", o == []))
    cases.append(("durations parse", (seconds("PT1M5S"), seconds("PT45S"), seconds("PT1H"), seconds("P0D"), seconds("x")) == (65, 45, 3600, 0, None)))
    cases.append(("the key is scrubbed from errors", "SECRET123" not in scrub("videos: HTTP 403: key=SECRET123 bad", "SECRET123")))
    cfg = json.load(open(CHANNELS, encoding="utf-8"))
    ids = [c["id"] for c in cfg["channels"]]
    cases.append(("channel file: ids only, unique", len(ids) == len(set(ids)) and all(re.fullmatch(r"UC[\w-]{22}", i) for i in ids)))
    bad = [n for n, ok in cases if not ok]
    for n_ in bad:
        print("FAIL " + n_)
    print(f"yt_outliers selftest: {len(cases) - len(bad)} of {len(cases)} planted cases right")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        sys.exit("yt_outliers: no YOUTUBE_API_KEY in the environment (only the yt-outliers workflow has it)")
    cfg = json.load(open(CHANNELS, encoding="utf-8"))
    rep = run(Client(key), cfg, dt.date.today())
    json.dump(rep, open(a.out, "w", encoding="utf-8"), indent=1); open(a.out, "a").write("\n")
    print(f"yt_outliers: {len(rep['channels'])} channels, {len(rep['outliers'])} outliers, {len(rep['new_channels'])} new channels, "
          f"{len(rep['errors'])} errors, about {rep['quota_units']} quota units")
    for e in rep["errors"][:5]:
        print("ERROR " + e)
    if rep["errors"] and not rep["channels"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
