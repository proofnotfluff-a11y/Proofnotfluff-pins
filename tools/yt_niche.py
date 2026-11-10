#!/usr/bin/env python3
"""Niche research reader for the video engine (YouTube Data API v3, official, read only).

Todd, live chat, Nov 9, 2026, 4:00 pm: "The questions is what community should I target?"; 4:28 pm, the niche research
chat: for each candidate community, Shorts at 100,000+ views and 5x their channel's usual, and their top comments.
For every niche in video/studio/research/niche/queries.json: each search query (most viewed videos under 4 minutes from
the last 365 days), the Shorts among the results (180 s or less) at 100,000 views or more, each one's channel typical
(median views of the Shorts in its newest 50 uploads, the same rule as tools/yt_outliers.py), and for the ones at 5x or
more: the top comments by relevance and the cover image the API names.

Two outputs, both written to --out (the yt-niche workflow pushes that folder to the throwaway branch niche-results,
never to main):
  summary.json   counts and ids only: no title, no channel name, no comment.
  sealed.json    titles, channel names, comment text (never a commenter's name, handle or id) and cover images, sealed
                 with tools/data_box.py under a one-time passphrase that is wrapped to the RSA public key in the config.
                 Only the chat that made the key pair can open it; other people's words never sit readable in this
                 public repo (CLAUDE.md 5).
  search-cache.json   query to video ids, so a second run spends no search quota on a query already read.

    python3 tools/yt_niche.py --out DIR [--cache FILE]     needs YOUTUBE_API_KEY (only the yt-niche workflow has it)
    python3 tools/yt_niche.py --open sealed.json --key private.pem --out DIR     (in the chat that holds the key)
    python3 tools/yt_niche.py --selftest                    planted cases, no network

Quota (10,000 units a day): search.list 100 a call; everything else 1. The run stops searching at --max-units and still
writes what it has. Nothing is posted or changed anywhere.
"""
import argparse, base64, datetime as dt, json, os, re, sys, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_outliers import ApiError, Client, analyze, chunks, scrub, seconds, video_rows  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG = os.path.join(ROOT, "video", "studio", "research", "niche", "queries.json")
RULES = {"ratio": 5.0, "min_views": 100000, "max_seconds": 180, "max_age_days": 365, "min_shorts": 8, "newest": 50}
SLUG = re.compile(r"^[a-z][a-z0-9-]{1,30}$")


def uploads_id(cid):
    """A channel's uploads playlist is its id with UC swapped for UU (saves one API call a channel)."""
    return "UU" + cid[2:] if re.fullmatch(r"UC[\w-]{22}", cid or "") else None


def config_problems(cfg):
    out = []
    niches = cfg.get("niches")
    if not isinstance(niches, dict) or not niches:
        return ["niches must be a non-empty object"]
    for slug, n in niches.items():
        if not SLUG.match(slug):
            out.append(f"niche slug {slug!r} is not lower-case words and dashes")
        qs = n.get("queries") if isinstance(n, dict) else None
        if not (isinstance(qs, list) and 1 <= len(qs) <= 8 and all(isinstance(q, str) and 3 <= len(q) <= 80 for q in qs)):
            out.append(f"{slug}: queries must be 1 to 8 strings of 3 to 80 characters")
    if "BEGIN PUBLIC KEY" not in cfg.get("pubkey_pem", ""):
        out.append("pubkey_pem is missing: nothing with other people's words can be written without it")
    if "PRIVATE" in json.dumps(cfg):
        out.append("a private key is in the config")
    return out


def english(sn):
    lang = (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "").lower()
    return not lang or lang.startswith("en")


def candidate_rows(client, ids):
    """Full rows for search hits: counts for the summary, words and the cover link for the sealed part."""
    rows = []
    for part in chunks(ids):
        d = client.get("videos", part="statistics,contentDetails,snippet", id=",".join(part), maxResults=50)
        for it in d.get("items", []):
            st, sn = it.get("statistics", {}), it.get("snippet", {})
            th = sn.get("thumbnails", {})
            rows.append({"video": it["id"], "channel": sn.get("channelId"), "published": (sn.get("publishedAt") or "")[:10],
                         "seconds": seconds(it.get("contentDetails", {}).get("duration")),
                         "views": int(st["viewCount"]) if "viewCount" in st else None,
                         "likes": int(st["likeCount"]) if "likeCount" in st else None,
                         "comments": int(st["commentCount"]) if "commentCount" in st else None,
                         "english": english(sn),
                         "_title": sn.get("title", "")[:160], "_description": sn.get("description", "")[:300],
                         "_tags": (sn.get("tags") or [])[:10],
                         "_thumb": (th.get("high") or th.get("medium") or th.get("default") or {}).get("url")})
    return rows


def keep(row, today, rules=RULES):
    cut = (today - dt.timedelta(days=rules["max_age_days"])).isoformat()
    return (row["seconds"] is not None and row["seconds"] <= rules["max_seconds"] and row["views"] is not None
            and row["views"] >= rules["min_views"] and row["published"] >= cut and row["english"])


def judge(row, typical, rules=RULES):
    """Adds typical and ratio; at_bar is the proven lane's bar: 100,000+ views and 5x the channel's typical."""
    ratio = round(row["views"] / typical, 1) if typical else None
    return dict(row, typical=typical, ratio=ratio,
                at_bar=bool(ratio is not None and ratio >= rules["ratio"] and row["views"] >= rules["min_views"]))


def channel_typical(client, cid, today):
    up = uploads_id(cid)
    if not up:
        return None, None
    pl = client.get("playlistItems", part="contentDetails", playlistId=up, maxResults=RULES["newest"])
    ids = [i["contentDetails"]["videoId"] for i in pl.get("items", [])]
    n, typical, _ = analyze(video_rows(client, ids), today, RULES)
    return n, typical


def comment_rows(d):
    """Top-level comments: the words, likes and reply count only. No author name, handle, channel or id is kept."""
    out = []
    for it in d.get("items", []):
        s = it.get("snippet", {})
        c = s.get("topLevelComment", {}).get("snippet", {})
        text = (c.get("textOriginal") or c.get("textDisplay") or "").strip()
        if text:
            out.append({"text": text[:500], "likes": c.get("likeCount", 0), "replies": s.get("totalReplyCount", 0)})
    return out


def public(row):
    return {k: v for k, v in row.items() if not k.startswith("_")}


def wrap(payload, pubkey_pem):
    """Seal with tools/data_box.py under a fresh passphrase; wrap the passphrase to the RSA public key."""
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import data_box
    phrase = base64.b64encode(os.urandom(32)).decode()
    box = data_box.seal(json.dumps(payload).encode("utf-8"), phrase)
    pub = serialization.load_pem_public_key(pubkey_pem.encode())
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    return {"schema": "pnf.niche.sealed.v1", "wrapped_key": base64.b64encode(pub.encrypt(phrase.encode(), oaep)).decode(), "box": box}


def unwrap(sealed, private_pem):
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
    import data_box
    key = serialization.load_pem_private_key(private_pem.encode(), password=None)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    phrase = key.decrypt(base64.b64decode(sealed["wrapped_key"]), oaep).decode()
    return json.loads(data_box.unseal(sealed["box"], phrase).decode("utf-8"))


def fetch_image(url):
    if not (url or "").startswith("https://i.ytimg.com/"):
        return None
    try:
        with urllib.request.urlopen(url, timeout=20) as r:
            data = r.read(200_000)
        return base64.b64encode(data).decode() if data[:2] == b"\xff\xd8" else None
    except Exception:
        return None


def run(client, cfg, today, cache, max_units):
    per_niche = int(cfg.get("per_niche", 50))
    n_comment_videos = int(cfg.get("comment_videos_per_niche", 20))
    n_comments = min(int(cfg.get("comments_per_video", 40)), 100)
    n_thumbs = int(cfg.get("thumbs_per_niche", 15))
    after = (today - dt.timedelta(days=RULES["max_age_days"])).isoformat() + "T00:00:00Z"
    summary = {"schema": "pnf.niche.summary.v1", "read": today.isoformat(), "rules": RULES, "niches": {}, "errors": []}
    secret = {"read": today.isoformat(), "videos": {}, "channels": {}, "comments": {}, "thumbs": {}}
    typicals, stopped = {}, False
    for slug, n in cfg["niches"].items():
        hits = {}
        for q in n["queries"]:
            if q not in cache:
                if stopped or client.units + 100 > max_units:
                    stopped = True
                    summary["errors"].append(f"{slug}: query skipped at the unit cap: {q}")
                    continue
                try:
                    d = client.get("search", cost=100, part="snippet", q=q, type="video", videoDuration="short", order="viewCount",
                                   publishedAfter=after, maxResults=50, relevanceLanguage="en", regionCode="US")
                except ApiError as e:
                    summary["errors"].append(str(e))
                    stopped = stopped or "quota" in str(e).lower()
                    continue
                cache[q] = {"read": today.isoformat(), "ids": [i["id"]["videoId"] for i in d.get("items", []) if i.get("id", {}).get("videoId")]}
            for vid in cache[q]["ids"]:
                hits.setdefault(vid, []).append(q)
        try:
            rows = candidate_rows(client, sorted(hits))
        except ApiError as e:
            summary["errors"].append(str(e)); rows = []
        searched = len(rows)
        rows = sorted((r for r in rows if keep(r, today)), key=lambda r: -r["views"])[:per_niche]
        judged = []
        for r in rows:
            cid = r["channel"]
            if cid not in typicals:
                try:
                    typicals[cid] = channel_typical(client, cid, today)
                except ApiError as e:
                    summary["errors"].append(str(e)); typicals[cid] = (None, None)
            j = judge(r, typicals[cid][1])
            j["channel_shorts"], j["queries"] = typicals[cid][0], hits[r["video"]]
            judged.append(j)
        bar = [j for j in judged if j["at_bar"]]
        for j in bar[:n_comment_videos]:
            try:
                d = client.get("commentThreads", part="snippet", videoId=j["video"], order="relevance", maxResults=n_comments, textFormat="plainText")
                secret["comments"][j["video"]] = comment_rows(d)
            except ApiError as e:
                secret["comments"][j["video"]] = []
                j["comments_error"] = "comments off or unavailable" if "403" in str(e) or "404" in str(e) else str(e)[:120]
        for j in bar[:n_thumbs]:
            img = fetch_image(j.get("_thumb"))
            if img:
                secret["thumbs"][j["video"]] = img
        for j in judged:
            secret["videos"][j["video"]] = {"title": j["_title"], "description": j["_description"], "tags": j["_tags"], "niche": slug}
        summary["niches"][slug] = {"label": n.get("label", slug), "searched": searched, "kept": len(judged), "at_bar": len(bar),
                                   "creators_at_bar": len({j["channel"] for j in bar}),
                                   "videos": [dict(public(j), url=f"https://www.youtube.com/shorts/{j['video']}") for j in judged]}
    cids = sorted({v["channel"] for n in summary["niches"].values() for v in n["videos"] if v["channel"]})
    for part in chunks(cids):
        try:
            d = client.get("channels", part="snippet,statistics", id=",".join(part), maxResults=50)
        except ApiError as e:
            summary["errors"].append(str(e)); continue
        for it in d.get("items", []):
            sn, st = it.get("snippet", {}), it.get("statistics", {})
            secret["channels"][it["id"]] = {"title": sn.get("title", ""), "description": sn.get("description", "")[:400],
                                            "country": sn.get("country"), "created": (sn.get("publishedAt") or "")[:10],
                                            "subs": int(st["subscriberCount"]) if "subscriberCount" in st else None,
                                            "videos": int(st["videoCount"]) if "videoCount" in st else None}
    summary["quota_units"] = client.units
    summary["stopped_at_cap"] = stopped
    return summary, secret


def selftest():
    today = dt.date(2026, 11, 9)
    mk = lambda **k: dict({"video": "v", "channel": "UC" + "a" * 22, "published": "2026-08-01", "seconds": 40, "views": 250000,
                           "english": True, "_title": "t", "_thumb": None}, **k)
    cases = [
        ("a 250,000 view Short from this year is kept", keep(mk(), today)),
        ("under 100,000 views is dropped", not keep(mk(views=99999), today)),
        ("over 180 s is dropped", not keep(mk(seconds=181), today)),
        ("older than a year is dropped", not keep(mk(published="2025-11-01"), today)),
        ("not English is dropped", not keep(mk(english=False), today)),
        ("5x the typical at 100,000+ is at the bar", judge(mk(), 50000)["at_bar"] and judge(mk(), 50000)["ratio"] == 5.0),
        ("4.9x is not at the bar", not judge(mk(views=245000), 50000)["at_bar"]),
        ("no typical means not at the bar", not judge(mk(), None)["at_bar"]),
        ("uploads playlist id", uploads_id("UC" + "a" * 22) == "UU" + "a" * 22 and uploads_id("xx") is None),
        ("a comment keeps words and counts, never who wrote it",
         comment_rows({"items": [{"snippet": {"totalReplyCount": 2, "topLevelComment": {"snippet": {
             "textOriginal": "hello", "likeCount": 3, "authorDisplayName": "SOMEONE", "authorChannelId": {"value": "UCx"}}}}}]})
         == [{"text": "hello", "likes": 3, "replies": 2}]),
        ("the summary row drops every word field", public(mk(_description="d")) == {k: v for k, v in mk().items() if k[0] != "_"}),
        ("only YouTube's image host is fetched", fetch_image("https://example.com/a.jpg") is None),
        ("the key is scrubbed from errors", "SECRET123" not in scrub("search: HTTP 403: key=SECRET123", "SECRET123")),
        ("a config with no public key is refused", any("pubkey_pem" in p for p in config_problems({"niches": {"ab": {"queries": ["abc"]}}}))),
        ("a private key in the config is refused", any("private" in p for p in config_problems(
            {"niches": {"ab": {"queries": ["abc"]}}, "pubkey_pem": "-----BEGIN PUBLIC KEY-----", "x": "-----BEGIN " + "PRIVATE KEY-----"}))),   # split so the planted case is not read as a key
    ]
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        pub = k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode()
        prv = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()).decode()
        sealed = wrap({"comments": {"v": [{"text": "planted words"}]}}, pub)
        cases.append(("the sealed file opens with the private key", unwrap(sealed, prv)["comments"]["v"][0]["text"] == "planted words"))
        cases.append(("the sealed file shows none of the words", "planted" not in json.dumps(sealed)))
    except ImportError:
        print("SKIP seal round trip: the cryptography package is not installed here")
    if os.path.exists(CONFIG):
        cases.append(("the committed config is valid", config_problems(json.load(open(CONFIG, encoding="utf-8"))) == []))
    bad = [n for n, ok in cases if not ok]
    for n_ in bad:
        print("FAIL " + n_)
    print(f"yt_niche selftest: {len(cases) - len(bad)} of {len(cases)} planted cases right")
    return 1 if bad else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None)
    ap.add_argument("--cache", default=None)
    ap.add_argument("--max-units", type=int, default=8000)
    ap.add_argument("--open", dest="open_", default=None)
    ap.add_argument("--key", default=None)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not a.out:
        sys.exit("yt_niche: --out DIR is required")
    os.makedirs(a.out, exist_ok=True)
    if a.open_:
        data = unwrap(json.load(open(a.open_, encoding="utf-8")), open(a.key, encoding="utf-8").read())
        thumbs = data.pop("thumbs", {})
        os.makedirs(os.path.join(a.out, "thumbs"), exist_ok=True)
        for vid, b64 in thumbs.items():
            if re.fullmatch(r"[\w-]{11}", vid):
                open(os.path.join(a.out, "thumbs", vid + ".jpg"), "wb").write(base64.b64decode(b64))
        json.dump(data, open(os.path.join(a.out, "opened.json"), "w", encoding="utf-8"), indent=1)
        print(f"yt_niche: opened {len(data['videos'])} videos, {len(data['channels'])} channels, "
              f"{sum(len(v) for v in data['comments'].values())} comments, {len(thumbs)} cover images")
        return
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if not key:
        sys.exit("yt_niche: no YOUTUBE_API_KEY in the environment (only the yt-niche workflow has it)")
    cfg = json.load(open(CONFIG, encoding="utf-8"))
    probs = config_problems(cfg)
    if probs:
        sys.exit("yt_niche: " + "; ".join(probs))
    cache = json.load(open(a.cache, encoding="utf-8")) if a.cache and os.path.exists(a.cache) else {}
    summary, secret = run(Client(key), cfg, dt.date.today(), cache, a.max_units)
    json.dump(summary, open(os.path.join(a.out, "summary.json"), "w", encoding="utf-8"), indent=1)
    json.dump(wrap(secret, cfg["pubkey_pem"]), open(os.path.join(a.out, "sealed.json"), "w", encoding="utf-8"))
    json.dump(cache, open(os.path.join(a.out, "search-cache.json"), "w", encoding="utf-8"), indent=1)
    print(f"yt_niche: {len(summary['niches'])} niches, "
          + ", ".join(f"{s} {n['at_bar']} at the bar from {n['creators_at_bar']} creators" for s, n in summary["niches"].items())
          + f"; {len(summary['errors'])} errors, about {summary['quota_units']} quota units")
    for e in summary["errors"][:8]:
        print("ERROR " + scrub(e, key))


if __name__ == "__main__":
    main()
