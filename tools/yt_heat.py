#!/usr/bin/env python3
"""Heat reader for the video engine: what is winning on YouTube right now, in any field (official API, read only).

Todd, live chat, Nov 13, 2026, 10:00 am: "I feel like you could gauge excitement by understanding what the topic of the
video is and seeing what level of engagement that video has"; 10:03 am, to running this pull: "Yes and don't restrict
yourself to the trades. Let's go for volume." (coo/DECISIONS-2026-11-13.md).

For every area in video/studio/research/heat/queries.json: each search query (most viewed videos of any length posted in
the last `days` days), then for the fastest ones the channel's normal (the median views of its other recent uploads of the
same kind, Short or long) and the top comments. A video is hot at `min_views` or more and `ratio` times its channel's
normal. The numbers are code; grouping videos into topics is reading, done in the chat that opens the sealed words.

Outputs go to --out (the yt-heat workflow pushes that folder to the throwaway branch heat-results, never to main):
  summary.json   counts and ids only: no title, no channel name, no comment.
  sealed.json    titles, descriptions, tags, channel names and comment text (never a commenter's name, handle or id),
                 sealed the same way as tools/yt_niche.py: only the chat that made the key pair can open it.

    python3 tools/yt_heat.py --out DIR                       needs YOUTUBE_API_KEY (only the yt-heat workflow has it)
    python3 tools/yt_heat.py --open sealed.json --key private.pem --out DIR
    python3 tools/yt_heat.py --selftest                      planted cases, no network

Quota (10,000 units a day): search.list 100 a call; everything else 1. Searching stops at --max-units.
"""
import argparse, datetime as dt, json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_niche import SLUG, comment_rows, english, public, unwrap, uploads_id, wrap  # noqa: E402
from yt_outliers import ApiError, Client, chunks, scrub, seconds  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "video", "studio", "research", "heat", "queries.json")
RULES = {"days": 14, "min_views": 20000, "ratio": 3.0, "short_seconds": 180, "min_same_kind": 5, "newest": 50}


def config_problems(cfg):
    out = []
    areas = cfg.get("areas")
    if not isinstance(areas, dict) or not areas:
        return ["areas must be a non-empty object"]
    for slug, a in areas.items():
        if not SLUG.match(slug):
            out.append(f"area slug {slug!r} is not lower-case words and dashes")
        qs = a.get("queries") if isinstance(a, dict) else None
        if not (isinstance(qs, list) and 1 <= len(qs) <= 8 and all(isinstance(q, str) and 3 <= len(q) <= 80 for q in qs)):
            out.append(f"{slug}: queries must be 1 to 8 strings of 3 to 80 characters")
    if "BEGIN PUBLIC KEY" not in cfg.get("pubkey_pem", ""):
        out.append("pubkey_pem is missing: nothing with other people's words can be written without it")
    if "PRIVATE" in json.dumps(cfg):
        out.append("a private key is in the config")
    return out


def rows_for(client, ids):
    rows = []
    for part in chunks(ids):
        d = client.get("videos", part="statistics,contentDetails,snippet", id=",".join(part), maxResults=50)
        for it in d.get("items", []):
            st, sn = it.get("statistics", {}), it.get("snippet", {})
            num = lambda k: int(st[k]) if k in st else None
            rows.append({"video": it["id"], "channel": sn.get("channelId"), "published": (sn.get("publishedAt") or "")[:19],
                         "seconds": seconds(it.get("contentDetails", {}).get("duration")), "views": num("viewCount"),
                         "likes": num("likeCount"), "comments": num("commentCount"), "english": english(sn),
                         "_title": sn.get("title", "")[:160], "_description": sn.get("description", "")[:400],
                         "_tags": (sn.get("tags") or [])[:10]})
    return rows


def age_days(published, now):
    try:
        t = dt.datetime.fromisoformat(published[:19])
    except ValueError:
        return None
    return max((now - t).total_seconds() / 86400.0, 0.0)


def kind(row, rules=RULES):
    return None if row["seconds"] is None else ("short" if row["seconds"] <= rules["short_seconds"] else "long")


def speed(row, now, rules=RULES):
    """Adds age (days) and views a day. A video under a day old is counted as one day, so a few hours cannot fake speed."""
    age = age_days(row["published"], now)
    ok = age is not None and age <= rules["days"] + 1 and row["views"] is not None and row["english"] and kind(row) is not None
    return dict(row, kind=kind(row), age_days=None if age is None else round(age, 1),
                per_day=round(row["views"] / max(age, 1.0)) if ok else None)


def normal(uploads, row, rules=RULES):
    """The channel's normal for this kind of video: the median views of its other recent uploads of the same kind."""
    same = [u["views"] for u in uploads if u["video"] != row["video"] and u["views"] is not None and kind(u) == row["kind"]]
    return statistics.median(same) if len(same) >= rules["min_same_kind"] else None


def judge(row, typical, rules=RULES):
    ratio = round(row["views"] / typical, 1) if typical else None
    return dict(row, typical=typical, ratio=ratio,
                hot=bool(ratio is not None and ratio >= rules["ratio"] and row["views"] >= rules["min_views"]))


def run(client, cfg, now, max_units):
    per_area, n_cv = int(cfg.get("per_area", 40)), int(cfg.get("comment_videos_per_area", 15))
    n_comments = min(int(cfg.get("comments_per_video", 40)), 100)
    after = (now - dt.timedelta(days=RULES["days"])).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = {"schema": "pnf.heat.summary.v1", "read": now.strftime("%Y-%m-%dT%H:%MZ"), "rules": RULES, "areas": {}, "errors": []}
    secret = {"read": summary["read"], "videos": {}, "channels": {}, "comments": {}}
    uploads, stopped = {}, False
    for slug, a in cfg["areas"].items():
        hits = {}
        for q in a["queries"]:
            if stopped or client.units + 100 > max_units:
                stopped = True
                summary["errors"].append(f"{slug}: query skipped at the unit cap: {q}")
                continue
            try:
                d = client.get("search", cost=100, part="snippet", q=q, type="video", order="viewCount", publishedAfter=after,
                               maxResults=50, relevanceLanguage="en", regionCode="US")
            except ApiError as e:
                summary["errors"].append(str(e))
                stopped = stopped or "quota" in str(e).lower()
                continue
            for i in d.get("items", []):
                if i.get("id", {}).get("videoId"):
                    hits.setdefault(i["id"]["videoId"], []).append(q)
        try:
            rows = [speed(r, now) for r in rows_for(client, sorted(hits))]
        except ApiError as e:
            summary["errors"].append(str(e)); rows = []
        searched = len(rows)
        rows = sorted((r for r in rows if r["per_day"] is not None), key=lambda r: -r["per_day"])[:per_area]
        judged = []
        for r in rows:
            cid = r["channel"]
            if cid not in uploads:
                try:
                    pl = client.get("playlistItems", part="contentDetails", playlistId=uploads_id(cid), maxResults=RULES["newest"])
                    uploads[cid] = rows_for(client, [i["contentDetails"]["videoId"] for i in pl.get("items", [])])
                except (ApiError, TypeError) as e:
                    summary["errors"].append(str(e)); uploads[cid] = []
            j = judge(r, normal(uploads[cid], r))
            j["queries"] = hits[r["video"]]
            judged.append(j)
        for j in sorted(judged, key=lambda j: (not j["hot"], -j["per_day"]))[:n_cv]:
            try:
                d = client.get("commentThreads", part="snippet", videoId=j["video"], order="relevance", maxResults=n_comments, textFormat="plainText")
                secret["comments"][j["video"]] = comment_rows(d)
            except ApiError as e:
                secret["comments"][j["video"]] = []
                j["comments_error"] = "comments off or unavailable" if "403" in str(e) or "404" in str(e) else str(e)[:120]
        for j in judged:
            secret["videos"][j["video"]] = {"title": j["_title"], "description": j["_description"], "tags": j["_tags"], "area": slug}
        summary["areas"][slug] = {"label": a.get("label", slug), "searched": searched, "kept": len(judged),
                                  "hot": sum(j["hot"] for j in judged), "creators_hot": len({j["channel"] for j in judged if j["hot"]}),
                                  "videos": [dict(public(j), url=f"https://www.youtube.com/watch?v={j['video']}") for j in judged]}
    cids = sorted({v["channel"] for a in summary["areas"].values() for v in a["videos"] if v["channel"]})
    for part in chunks(cids):
        try:
            d = client.get("channels", part="snippet,statistics", id=",".join(part), maxResults=50)
        except ApiError as e:
            summary["errors"].append(str(e)); continue
        for it in d.get("items", []):
            sn, st = it.get("snippet", {}), it.get("statistics", {})
            secret["channels"][it["id"]] = {"title": sn.get("title", ""), "description": sn.get("description", "")[:300],
                                            "subs": int(st["subscriberCount"]) if "subscriberCount" in st else None}
    summary["quota_units"], summary["stopped_at_cap"] = client.units, stopped
    return summary, secret


def selftest():
    now = dt.datetime(2026, 11, 13, 16, 0, 0)
    mk = lambda **k: dict({"video": "v", "channel": "UC" + "a" * 22, "published": "2026-11-09T16:00:00", "seconds": 40,
                           "views": 80000, "likes": 1, "comments": 1, "english": True, "_title": "t"}, **k)
    ups = [mk(video=f"u{i}", views=10000) for i in range(6)] + [mk(video=f"l{i}", views=900, seconds=600) for i in range(6)]
    s = speed(mk(), now)
    cases = [
        ("80,000 views in 4 days is 20,000 a day", s["per_day"] == 20000 and s["age_days"] == 4.0 and s["kind"] == "short"),
        ("a 3 hour old video counts as one day, not eight a day", speed(mk(published="2026-11-13T13:00:00"), now)["per_day"] == 80000),
        ("older than the window has no speed", speed(mk(published="2026-10-20T16:00:00"), now)["per_day"] is None),
        ("not English has no speed", speed(mk(english=False), now)["per_day"] is None),
        ("no length has no speed", speed(mk(seconds=None), now)["per_day"] is None),
        ("a Short is judged against the channel's Shorts", normal(ups, s) == 10000),
        ("a long video is judged against the channel's long videos", normal(ups, speed(mk(seconds=600), now)) == 900),
        ("the video itself is left out of its own normal", normal(ups + [mk(views=9_000_000)], s) == 10000),
        ("under 5 others of its kind means no normal", normal(ups[:4], s) is None),
        ("8x normal at 80,000 views is hot", judge(s, 10000)["hot"] and judge(s, 10000)["ratio"] == 8.0),
        ("2.9x is not hot", not judge(s, 27600)["hot"]),
        ("under 20,000 views is not hot at any ratio", not judge(speed(mk(views=19999), now), 100)["hot"]),
        ("no normal is not hot", not judge(s, None)["hot"]),
        ("the summary row drops every word field", "_title" not in public(s)),
        ("a config with no public key is refused", any("pubkey_pem" in p for p in config_problems({"areas": {"ab": {"queries": ["abc"]}}}))),
        ("nine queries in an area is refused", any("queries" in p for p in config_problems(
            {"areas": {"ab": {"queries": ["abc"] * 9}}, "pubkey_pem": "-----BEGIN PUBLIC KEY-----"}))),
    ]
    class Fake:   # a whole run with no network: one query, one hot Short, its channel's uploads, one comment
        units = 0
        def get(self, path, cost=1, **p):
            self.units += cost
            item = lambda vid, views: {"id": vid, "snippet": {"channelId": "UC" + "a" * 22, "publishedAt": "2026-11-09T16:00:00Z", "title": "PLANTED TITLE"},
                                       "contentDetails": {"duration": "PT40S"}, "statistics": {"viewCount": str(views)}}
            if path == "search":
                return {"items": [{"id": {"videoId": "hot"}}]}
            if path == "videos":
                return {"items": [item(v, 80000 if v == "hot" else 10000) for v in p["id"].split(",")]}
            if path == "playlistItems":
                return {"items": [{"contentDetails": {"videoId": f"u{i}"}} for i in range(6)]}
            if path == "commentThreads":
                return {"items": [{"snippet": {"totalReplyCount": 0, "topLevelComment": {"snippet": {"textOriginal": "how?", "authorDisplayName": "SOMEONE"}}}}]}
            return {"items": [{"id": "UC" + "a" * 22, "snippet": {"title": "PLANTED CHANNEL"}, "statistics": {"subscriberCount": "5"}}]}
    summ, sec = run(Fake(), {"areas": {"ab": {"queries": ["abc"]}}}, now, 7000)
    v = summ["areas"]["ab"]["videos"]
    cases += [
        ("a whole planted run finds the one hot video", len(v) == 1 and v[0]["hot"] and v[0]["ratio"] == 8.0 and v[0]["per_day"] == 20000),
        ("the summary holds no title, channel name or comment", not any(w in json.dumps(summ) for w in ("PLANTED", "how?", "SOMEONE"))),
        ("the sealed part holds the words and never the commenter", sec["comments"]["hot"] == [{"text": "how?", "likes": 0, "replies": 0}]
         and sec["videos"]["hot"]["title"] == "PLANTED TITLE" and "SOMEONE" not in json.dumps(sec)),
        ("searching stops at the unit cap", "unit cap" in run(Fake(), {"areas": {"ab": {"queries": ["abc"]}}}, now, 50)[0]["errors"][0]),
    ]
    if os.path.exists(CONFIG):
        cases.append(("the committed config is valid", config_problems(json.load(open(CONFIG, encoding="utf-8"))) == []))
    bad = [n for n, ok in cases if not ok]
    for n_ in bad:
        print("FAIL " + n_)
    print(f"yt_heat selftest: {len(cases) - len(bad)} of {len(cases)} planted cases right")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None)
    ap.add_argument("--max-units", type=int, default=7000)
    ap.add_argument("--open", dest="open_", default=None)
    ap.add_argument("--key", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.out:
        sys.exit("yt_heat: --out DIR is required")
    os.makedirs(a.out, exist_ok=True)
    if a.open_:
        data = unwrap(json.load(open(a.open_, encoding="utf-8")), open(a.key, encoding="utf-8").read())
        json.dump(data, open(os.path.join(a.out, "opened.json"), "w", encoding="utf-8"), indent=1)
        print(f"yt_heat: opened {len(data['videos'])} videos, {len(data['channels'])} channels, "
              f"{sum(len(v) for v in data['comments'].values())} comments")
        return
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        sys.exit("yt_heat: no YOUTUBE_API_KEY in the environment (only the yt-heat workflow has it)")
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    probs = config_problems(cfg)
    if probs:
        sys.exit("yt_heat: " + "; ".join(probs))
    summary, secret = run(Client(key), cfg, dt.datetime.utcnow().replace(microsecond=0), a.max_units)
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), indent=1)
    json.dump(wrap(secret, cfg["pubkey_pem"]), open(os.path.join(a.out, "sealed.json"), "w", encoding="utf-8"))
    print(f"yt_heat: {len(summary['areas'])} areas, "
          + ", ".join(f"{s} {x['hot']} hot from {x['creators_hot']} creators" for s, x in summary["areas"].items())
          + f"; {len(summary['errors'])} errors, about {summary['quota_units']} quota units")
    for e in summary["errors"][:8]:
        print("ERROR " + scrub(e, key))


if __name__ == "__main__":
    main()
