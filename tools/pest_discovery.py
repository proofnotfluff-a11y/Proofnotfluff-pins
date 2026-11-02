#!/usr/bin/env python3
"""Pest companies from Overture Maps places, for the pest seat list (Todd, live chat, Nov 1, 2026: "Go with your
recommendations", answering the Sunday review stretch move; scout/REPOS.md Oct 25, to-do decide-add-overture-pest).

Overture Places (the open data tools/phones.py already reads; licenses cleared in legal/reviews/2026-10-23-phone-sources.md)
has a pest control category. This finds Chicago-area places in it that list their own website, drops national chains and
franchise brands (.claude/skills/prospect-matching/sources.md "Pest seat") and domains we already hold, and counts what is
left. Count mode prints counts only: no name, address, website or phone reaches the log. The Overture emails field is never
used; an address may only ever come from the business's own site, through the prospect-matching run and its two checkers.

Usage (runner only; the cloud shell cannot reach the Overture bucket):
  python3 tools/pest_discovery.py --count [--release R]   counts only. Env PEST_EXCLUDE: comma list of 12-hex sha256
                                                           prefixes of domains already in the CRM (from --hashes)
  python3 tools/pest_discovery.py --extract OUT.json [--release R]   the new companies (business, website, address,
                                                           inCity) for sealing with tools/data_box.py; counts to the log
  python3 tools/pest_discovery.py --hashes CRM_DIR         local: the PEST_EXCLUDE value for the CRM pest domains not
                                                           already in prospects/businesses.json (hashes only)
  python3 tools/pest_discovery.py --selftest
"""
import collections, glob, hashlib, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import phones  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATEGORY = "pest_control_service"
# Chicago metro: Cook, DuPage, Lake, Will, Kane and nearby (lon min, lat min, lon max, lat max). The pest seat sells a
# Chicago list; a suburban firm fits when its own site says it serves Chicago, which the prospect-matching checkers read.
METRO_BBOX = (-88.45, 41.40, -87.50, 42.50)
CHAIN = re.compile(r"\b(orkin|terminix|rentokil|ecolab|rollins|western|aptive|arrow|clark|massey|ehrlich|anticimex)\b", re.I)  # sources.md list
WILDLIFE_ONLY = re.compile(r"\b(wildlife|raccoon|bat removal|animal removal|critter|bed ?bug dogs?|k-?9)\b", re.I)


def h12(dom):
    return hashlib.sha256(dom.encode()).hexdigest()[:12]


def known_domains(path=os.path.join(ROOT, "prospects", "businesses.json")):
    try:
        return {phones.domain(b.get("website")) for b in json.load(open(path))["businesses"]} - {""}
    except Exception:
        return set()


def own_site(websites):
    for w in websites or []:
        d = phones.domain(w)
        if d and not phones.NOT_OWN_SITE.search(d):
            return d
    return ""


def inside(p, box):
    x0, y0, x1, y1 = box
    return p.get("lat") is not None and x0 <= p["lon"] <= x1 and y0 <= p["lat"] <= y1


def count(places, known=frozenset(), exclude=frozenset()):
    """Counts only. places: [{name, lat, lon, websites, status}] already in the category and the metro box."""
    return sift(places, known, exclude)[0]


def sift(places, known=frozenset(), exclude=frozenset()):
    """(counts, new) where new maps each new own-site domain to its first place."""
    c = collections.Counter(inCategory=len(places))
    live = [p for p in places if (p.get("status") or "open") in ("open", "operating", "")]
    c["open"] = len(live)
    sited = [(p, own_site(p.get("websites"))) for p in live]
    sited = [(p, d) for p, d in sited if d]
    c["withOwnSite"] = len(sited)
    per = collections.Counter(d for _, d in sited)
    keep = {}
    for p, d in sited:
        if per[d] >= phones.CHAIN_DOMAIN or CHAIN.search(p.get("name") or "") or CHAIN.search(d.replace("-", " ")):
            c["droppedChain"] += 1
        elif WILDLIFE_ONLY.search(p.get("name") or ""):
            c["droppedWildlifeOnly"] += 1
        else:
            keep.setdefault(d, p)
    c["companies"] = len(keep)
    new = {d: p for d, p in keep.items() if d not in known and h12(d) not in exclude}
    c["alreadyHeld"] = len(keep) - len(new)
    c["new"] = len(new)
    c["newInCity"] = sum(1 for p in new.values() if inside(p, phones.BBOX))
    for k in ("droppedChain", "droppedWildlifeOnly"):
        c.setdefault(k, 0)
    return dict(c), new


def candidates(new, release):
    """The sealed hand-off for the prospect-matching run: business-level fields only, from Overture (no phone, no email)."""
    rows = [{"business": p.get("name") or "", "website": "https://" + d + "/", "address": p.get("address") or "",
             "inCity": inside(p, phones.BBOX), "source": "overture:" + release}
            for d, p in sorted(new.items(), key=lambda kv: (not inside(kv[1], phones.BBOX), kv[0]))]
    return {"schema": "pnf.pest_candidates.v1", "release": release, "count": len(rows), "candidates": rows}


def query(release):
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    src = f"read_parquet('s3://{phones.BUCKET}/release/{release}/theme=places/type=place/*', hive_partitioning=1)"
    cols = {r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()}
    # Release 2026-10-21.0 carries the leaf value in taxonomy.primary (395 in the metro box); basic_category holds a broader
    # group there (probe, Nov 1), so taxonomy.primary goes first and basic_category is the fallback.
    if "taxonomy" in cols:
        cat, used = "taxonomy.primary", "taxonomy.primary"
    elif "basic_category" in cols:
        cat, used = "basic_category", "basic_category"
    else:
        cat, used = "categories.primary", "categories.primary"
    status = "operating_status" if "operating_status" in cols else "NULL"
    x0, y0, x1, y1 = METRO_BBOX
    rows = con.execute(f"""SELECT names.primary, (bbox.ymin + bbox.ymax) / 2, (bbox.xmin + bbox.xmax) / 2, websites, {status},
                                  addresses[1].freeform
                           FROM {src}
                           WHERE bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}
                             AND {cat} = '{CATEGORY}' AND names.primary IS NOT NULL""").fetchall()
    return used, [{"name": n, "lat": la, "lon": lo, "websites": list(w or []), "status": st or "open", "address": a or ""}
                  for n, la, lo, w, st, a in rows]


def probe(release):
    """Category values only (no place data): which values near 'pest' exist in the metro box, and how many places."""
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    src = f"read_parquet('s3://{phones.BUCKET}/release/{release}/theme=places/type=place/*', hive_partitioning=1)"
    cols = sorted(r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall())
    x0, y0, x1, y1 = METRO_BBOX
    box = f"bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}"
    out = {"release": release, "columns": cols, "placesInBox": con.execute(f"SELECT count(*) FROM {src} WHERE {box}").fetchone()[0]}
    for expr in ("basic_category", "taxonomy.primary", "categories.primary"):
        try:
            rows = con.execute(f"SELECT {expr}, count(*) FROM {src} WHERE {box} AND lower(CAST({expr} AS VARCHAR)) LIKE '%pest%' "
                               f"GROUP BY 1 ORDER BY 2 DESC LIMIT 15").fetchall()
            out[expr] = [[str(v), n] for v, n in rows]
        except Exception as e:
            out[expr] = type(e).__name__
    print(json.dumps(out))


def crm_hashes(crm_dir):
    held = known_domains()
    out = set()
    for f in glob.glob(os.path.join(crm_dir, "*.json")):
        d = json.load(open(f))
        d = d.get("data", d)
        if d.get("trade") == "pest control":
            dom = phones.domain(d.get("website"))
            if dom and dom not in held:
                out.add(h12(dom))
    return ",".join(sorted(out))


def selftest():
    P = lambda n, lat, lon, w=(), st="open": {"name": n, "lat": lat, "lon": lon, "websites": list(w), "status": st}
    places = [
        P("Southside Pest Pros", 41.80, -87.65, ["https://southsidepest.com/"]),             # new, in city
        P("Southside Pest Pros", 41.81, -87.66, ["http://www.southsidepest.com/contact"]),   # same company, one domain
        P("Naperville Bug Co", 41.77, -88.15, ["naperbug.com"]),                             # new, suburb
        P("Orkin", 41.90, -87.70, ["https://orkin.com/locations/chicago"]),                  # chain by name
        P("Rid It Pest", 41.95, -87.70, ["https://ridit.com/a"]),                            # chain by shared domain x3
        P("Rid It Pest", 41.96, -87.71, ["https://ridit.com/b"]),
        P("Rid It Pest", 41.97, -87.72, ["https://ridit.com/c"]),
        P("Closed Pest", 41.85, -87.65, ["https://closedpest.com"], st="closed"),           # closed
        P("Facebook Only Pest", 41.86, -87.66, ["https://facebook.com/fbpest"]),             # no own site
        P("No Site Pest", 41.87, -87.67),                                                    # no site
        P("Held Pest", 41.88, -87.68, ["https://heldpest.com"]),                             # in businesses.json
        P("Hashed Pest", 41.89, -87.69, ["https://hashedpest.com"]),                         # in CRM, by hash
        P("Chi Wildlife Removal", 41.90, -87.69, ["https://chiwild.com"]),                   # wildlife only
    ]
    c = count(places, known={"heldpest.com"}, exclude={h12("hashedpest.com")})
    want = {"inCategory": 13, "open": 12, "withOwnSite": 10, "droppedChain": 4, "droppedWildlifeOnly": 1, "companies": 4,
            "alreadyHeld": 2, "new": 2, "newInCity": 1}
    assert c == want, c
    assert not any(isinstance(v, str) for v in c.values()), "a string in the counts"
    doc = candidates(sift(places, known={"heldpest.com"}, exclude={h12("hashedpest.com")})[1], "2026-10-21.0")
    assert [r["website"] for r in doc["candidates"]] == ["https://southsidepest.com/", "https://naperbug.com/"], doc
    assert all(set(r) == {"business", "website", "address", "inCity", "source"} for r in doc["candidates"]), "a field beyond business level"
    print("pest_discovery selftest ok (13 planted places: chain by name and by shared domain, closed, listing site, no site, "
          "held, hashed, wildlife only, one company on two pins)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a[:1] == ["--count"]:
        rel = a[a.index("--release") + 1] if "--release" in a else phones.latest_release()
        exclude = {x.strip() for x in os.environ.get("PEST_EXCLUDE", "").split(",") if re.fullmatch(r"[0-9a-f]{12}", x.strip())}
        used, places = query(rel)
        out = {"release": rel, "categoryField": used, "metroBox": METRO_BBOX, "excludeHashes": len(exclude)}
        out.update(count(places, known_domains(), exclude))
        print(json.dumps(out))
    elif a[:1] == ["--extract"] and len(a) >= 2:
        rel = a[a.index("--release") + 1] if "--release" in a else phones.latest_release()
        exclude = {x.strip() for x in os.environ.get("PEST_EXCLUDE", "").split(",") if re.fullmatch(r"[0-9a-f]{12}", x.strip())}
        used, places = query(rel)
        c, new = sift(places, known_domains(), exclude)
        json.dump(candidates(new, rel), open(a[1], "w"), indent=1)
        print(json.dumps({"release": rel, "categoryField": used, **c}))     # counts only in the log
    elif a[:1] == ["--probe"]:
        probe(a[a.index("--release") + 1] if "--release" in a else phones.latest_release())
    elif a[:1] == ["--hashes"] and len(a) == 2:
        print(crm_hashes(a[1]))
    else:
        raise SystemExit(__doc__)
