#!/usr/bin/env python3
"""Listed business phone on each lead row, free route only (move 2, Todd, Oct 23, 2026).

Where a number comes from, in order:
  1 Overture Maps places (open data, read anonymously from the Overture S3 bucket in the runner). Its upstream
    sources carry CDLA Permissive 2.0, Apache 2.0 or CC0 licenses; the Legal desk review is
    legal/reviews/2026-10-23-phone-sources.md, and the attribution line is ATTRIBUTION below.
  2 The business's own website, when Overture gives a website but no usable phone: the home page is read once (robots.txt
    respected), and a number is taken only from a tel: link, a schema.org telephone field, or the one phone number the
    page shows. Chain sites (a domain shared by 3 or more Chicago places) and listing sites (Yelp, delivery apps, social)
    are never read, because their number is not the location's own.
No paid lookup and no API key (Todd, Oct 23: no spend without his yes). OpenStreetMap is not used (share-alike terms,
see the review).

Where a number goes: only into the members' files (the sealed daily list, the members' license app and workbook).
Never into a public file, a page, a commit in clear text or a log. Logs and the public file get counts only.

How a row is matched (no guessing; an unsure match leaves the phone empty):
  - a place within 120 m whose name scores 0.75 or more, or within 60 m at 0.6 or more, or at the same street number
    and street within 300 m (or with no coordinates) at 0.5 or more;
  - the best match must beat every other candidate with a different number clearly, or the row stays empty;
  - places Overture marks closed are skipped; toll-free and invalid numbers are never used.

Usage (runner):
  python3 tools/phones.py --release                         the newest Overture release name
  python3 tools/phones.py --extract OUT.json [--release R]  Chicago places with a phone or a website (needs duckdb)
  python3 tools/phones.py fill ROWS.json PLACES.json [--key items|records] [--public daily.json] [--no-web]
  python3 tools/phones.py --probe REST_DATA.json LICENSES_FULL.json PLACES.json   coverage counts only
  python3 tools/phones.py --selftest
"""
import collections, concurrent.futures, difflib, html, json, math, os, re, sys, urllib.parse, urllib.request, urllib.robotparser

BUCKET = "overturemaps-us-west-2"
LIST_URL = f"https://{BUCKET}.s3.us-west-2.amazonaws.com/?list-type=2&prefix=release/&delimiter=/"
FALLBACK_RELEASE = "2026-10-21.0"
BBOX = (-87.95, 41.63, -87.51, 42.03)     # Chicago, with a margin (lon min, lat min, lon max, lat max)
ATTRIBUTION = ("Phone numbers: Overture Maps Foundation places data (overturemaps.org), from sources under CDLA Permissive 2.0, "
               "Apache 2.0 and CC0 licenses, or the business's own website. A phone is the number the business lists publicly; "
               "it can be out of date.")
UA = "ProofNotFluffBot/1.0 (+https://proofnotfluff.com; business phone lookup, one page per site)"
WEB_CAP, WEB_TIMEOUT, WEB_BYTES, CHAIN_DOMAIN = 80, 8, 1_500_000, 3
NOT_OWN_SITE = re.compile(r"(?:^|\.)(?:facebook|fb|instagram|yelp|doordash|grubhub|ubereats|uber|seamless|postmates|tripadvisor|google|goo|"
                          r"linktr|toasttab|opentable|resy|tock|exploretock|chownow|slicelife|menufy|allmenus|menupages|zmenu|beyondmenu|"
                          r"tiktok|twitter|x|yellowpages|mapquest|foursquare|squareup|clover)\.(?:com|ee|gl|co|net|io|site)$", re.I)
TOLL_FREE = {"800", "833", "844", "855", "866", "877", "888"}
LEGAL = {"INC", "LLC", "L", "C", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "THE", "AND", "OF", "DBA", "A"}
GENERIC = {"RESTAURANT", "RESTAURANTS", "GRILL", "BAR", "CAFE", "KITCHEN", "PIZZA", "PIZZERIA", "TAQUERIA", "FOOD", "FOODS", "MART",
           "STORE", "SHOP", "CHICAGO", "EXPRESS", "LOUNGE", "TAVERN", "BAKERY", "DELI", "MARKET", "GROCERY", "COFFEE", "HOUSE", "BBQ",
           "SUSHI", "TACOS", "TACO", "THAI", "CHINESE", "MEXICAN", "ITALIAN", "PUB", "BISTRO", "EATERY", "INN", "SALON", "STUDIO",
           "SERVICES", "SERVICE", "CENTER", "GROUP", "BURGER", "BURGERS", "CHICKEN", "WINGS", "LIQUOR", "LIQUORS", "FOODMART", "TEA",
           "DONUTS", "JUICE", "NAIL", "NAILS", "BEAUTY", "BARBER", "AUTO", "SPA", "FITNESS", "STREET", "ST", "AVE", "AVENUE", "N", "S", "E", "W"}
DIRS = {"N", "S", "E", "W", "NORTH", "SOUTH", "EAST", "WEST"}


# ---------------------------------------------------------------- phone numbers
def norm_phone(s):
    """A US business number as (312) 555-0199, or "" when it is not a valid, local (not toll-free) number."""
    d = re.sub(r"\D", "", str(s or ""))
    if len(d) == 11 and d[0] == "1":
        d = d[1:]
    if len(d) != 10 or d[0] in "01" or d[3] in "01" or d[1:3] == "11" or d[4:6] == "11":
        return ""
    if d[:3] in TOLL_FREE or d[3:6] == "555" or d == d[0] * 10:
        return ""
    return f"({d[:3]}) {d[3:6]}-{d[6:]}"


# ---------------------------------------------------------------- names and addresses
def tokens(name):
    s = html.unescape(str(name or "")).upper().replace("&", " AND ").replace("'", "").replace("’", "")
    s = re.sub(r"[^A-Z0-9 ]", " ", s)
    return [t for t in s.split() if t not in LEGAL]


def name_score(a, b):
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    if "".join(ta) == "".join(tb):
        return 1.0
    seq = difflib.SequenceMatcher(None, " ".join(ta), " ".join(tb)).ratio()
    da, db = set(ta) - GENERIC, set(tb) - GENERIC
    if da and db:
        ov = len(da & db) / min(len(da), len(db))
        # a distinctive word glued differently ("MC DONALDS" and "MCDONALDS") still counts
        if ov < 1 and ("".join(sorted(da)) in "".join(tb) or "".join(sorted(db)) in "".join(ta)):
            ov = max(ov, 0.9)
    else:
        ov = 0.8 * len(set(ta) & set(tb)) / min(len(set(ta)), len(set(tb)))
    return round(max(seq, ov), 3)


def addr_key(addr):
    """"1234 W Main St" and "1234 West Main Street, Chicago" give the same key: (1234, "MAIN")."""
    t = re.sub(r"[^A-Z0-9 -]", " ", str(addr or "").upper()).split()
    if not t:
        return None
    m = re.match(r"^(\d+)", t[0])
    if not m:
        return None
    rest = [x for x in t[1:] if x not in DIRS]
    return (int(m.group(1)), rest[0]) if rest else None


def dist_m(a_lat, a_lon, b_lat, b_lon):
    if None in (a_lat, a_lon, b_lat, b_lon):
        return None
    k = math.cos(math.radians((a_lat + b_lat) / 2))
    return math.hypot((a_lat - b_lat) * 111_195, (a_lon - b_lon) * 111_195 * k)


def domain(url):
    try:
        h = urllib.parse.urlparse(url if "//" in url else "http://" + url).hostname or ""
    except ValueError:
        return ""
    h = h.lower()
    return h[4:] if h.startswith("www.") else h


# ---------------------------------------------------------------- the places index
class Places:
    def __init__(self, places):
        self.p = [x for x in places if (x.get("status") or "open") in ("open", "", None)]
        self.grid, self.by_addr = collections.defaultdict(list), collections.defaultdict(list)
        self.domains = collections.Counter()
        for i, x in enumerate(self.p):
            if x.get("lat") is not None and x.get("lon") is not None:
                self.grid[(int(x["lat"] / 0.002), int(x["lon"] / 0.002))].append(i)
            k = addr_key(x.get("address"))
            if k:
                self.by_addr[k].append(i)
            for w in x.get("websites") or []:
                if domain(w):
                    self.domains[domain(w)] += 1

    def near(self, lat, lon):
        if lat is None or lon is None:
            return []
        gi, gj = int(lat / 0.002), int(lon / 0.002)
        return [i for di in (-2, -1, 0, 1, 2) for dj in (-2, -1, 0, 1, 2) for i in self.grid.get((gi + di, gj + dj), [])]

    def match(self, name, address, lat, lon):
        """(place, score, metres) or (None, reason)."""
        ak = addr_key(address)
        cand = set(self.near(lat, lon)) | set(self.by_addr.get(ak, []) if ak else [])
        good = []
        for i in cand:
            x = self.p[i]
            d = dist_m(lat, lon, x.get("lat"), x.get("lon"))
            s = name_score(name, x.get("name"))
            same_addr = ak is not None and addr_key(x.get("address")) == ak
            ok = (d is not None and ((d <= 120 and s >= 0.75) or (d <= 60 and s >= 0.6))) or \
                 (same_addr and s >= 0.5 and (d is None or d <= 300))
            if ok:
                good.append((s + (0.1 if same_addr else 0) - (d or 0) / 2000, s, d, i))
        if not good:
            return None, "no match"
        good.sort(reverse=True)
        best = good[0]
        bphone = first_phone(self.p[best[3]])
        for other in good[1:]:
            if first_phone(self.p[other[3]]) != bphone and other[0] > best[0] - 0.08:
                return None, "two close matches"
        return (self.p[best[3]], best[1], best[2]), ""


def first_phone(x):
    for ph in x.get("phones") or []:
        if norm_phone(ph):
            return norm_phone(ph)
    return ""


# ---------------------------------------------------------------- the business's own site
def _get(url, cap):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    with urllib.request.urlopen(req, timeout=WEB_TIMEOUT) as r:
        if "html" not in (r.headers.get("Content-Type") or "html"):
            return ""
        return r.read(cap).decode(r.headers.get_content_charset() or "utf-8", "replace")


def page_phone(text):
    """The site's own number: a tel: link, a schema.org telephone field, else the one number the page shows."""
    found = collections.Counter()
    for m in re.finditer(r"""href\s*=\s*["']tel:([^"']+)""", text, re.I):
        found[norm_phone(urllib.parse.unquote(m.group(1)))] += 1
    for m in re.finditer(r""""telephone"\s*:\s*"([^"]+)"|itemprop=["']telephone["'][^>]*?(?:content=["']([^"']+)|>([^<]+))""", text, re.I):
        found[norm_phone(next(g for g in m.groups() if g))] += 1
    found.pop("", None)
    if not found:
        plain = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", text, flags=re.S | re.I)
        nums = {norm_phone(m.group(0)) for m in re.finditer(r"\(?\b[2-9]\d{2}\)?[\s.-]?[2-9]\d{2}[\s.-]\d{4}\b", plain)} - {""}
        return nums.pop() if len(nums) == 1 else ""
    top = found.most_common(2)
    return top[0][0] if len(top) == 1 or top[0][1] > top[1][1] else ""


def site_phone(url, fetch=_get):
    """("(312) ...", domain) or ("", reason). One robots.txt read and one page read per site."""
    url = url if "//" in url else "https://" + url
    dom = domain(url)
    if not dom or NOT_OWN_SITE.search(dom):
        return "", "listing site"
    base = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.parse(fetch(base + "/robots.txt", 200_000).splitlines())
        if not rp.can_fetch(UA, url):
            return "", "robots.txt"
    except Exception:
        pass                                   # no robots.txt (or unreadable): the usual rule is that the page may be read
    try:
        ph = page_phone(fetch(url, WEB_BYTES))
    except Exception:
        return "", "site unreachable"
    return (ph, dom) if ph else ("", "no number on page")


# ---------------------------------------------------------------- filling rows
def fill(rows, places, web=True, fetch=_get, name_field=None):
    """Sets phone and phoneSource on each row (rows need a name or business, address, lat, lon). Returns counts only."""
    idx = places if isinstance(places, Places) else Places(places)
    c = collections.Counter(rows=len(rows))
    todo = []
    for r in rows:
        r["phone"], r["phoneSource"] = "", ""
        nm = r.get(name_field) if name_field else (r.get("name") or r.get("business"))
        hit, why = idx.match(nm, r.get("address"), r.get("lat"), r.get("lon"))
        if not hit:
            c["noMatch" if why == "no match" else "unsure"] += 1
            continue
        x = hit[0]
        c["matched"] += 1
        ph = first_phone(x)
        if ph:
            r["phone"] = ph
            r["phoneSource"] = "Overture Maps places" + (f" ({', '.join(x['sources'])})" if x.get("sources") else "")
            c["overture"] += 1
            continue
        sites = [w for w in x.get("websites") or [] if domain(w) and idx.domains[domain(w)] < CHAIN_DOMAIN]
        if web and sites:
            todo.append((r, sites[0]))
        else:
            c["noPhoneListed"] += 1
    c["noPhoneListed"] += len(todo[WEB_CAP:])       # past the cap, a row keeps an empty phone rather than a slow run
    todo = todo[:WEB_CAP]
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for (r, site), (ph, src) in zip(todo, ex.map(lambda t: site_phone(t[1], fetch), todo)):
            if ph:
                r["phone"], r["phoneSource"] = ph, f"business website ({src})"
                c["website"] += 1
            else:
                c["noPhoneListed"] += 1
    c["withPhone"] = c["overture"] + c["website"]
    c["coverage"] = round(100 * c["withPhone"] / c["rows"], 1) if c["rows"] else 0.0
    return dict(c)


def stamp_public(path, counts):
    """Counts only on the public daily file: how many of today's rows carry a phone. Never a number or a name."""
    pub = json.load(open(path))
    pub["phones"] = {"rows": counts["rows"], "withPhone": counts["withPhone"], "coverage": counts["coverage"]}
    if pub.get("history"):
        pub["history"][-1]["withPhone"] = counts["withPhone"]
    json.dump(pub, open(path, "w"), indent=1)


# ---------------------------------------------------------------- Overture (runner only)
def latest_release():
    try:
        req = urllib.request.Request(LIST_URL, headers={"User-Agent": UA})
        xml = urllib.request.urlopen(req, timeout=30).read().decode()
        rels = sorted(re.findall(r"<Prefix>release/(\d{4}-\d{2}-\d{2}\.\d+)/</Prefix>", xml))
        return rels[-1] if rels else FALLBACK_RELEASE
    except Exception as e:
        print(f"phones: release list unreadable ({type(e).__name__}); using {FALLBACK_RELEASE}", file=sys.stderr)
        return FALLBACK_RELEASE


def extract(out, release):
    import duckdb
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
    src = f"read_parquet('s3://{BUCKET}/release/{release}/theme=places/type=place/*', hive_partitioning=1)"
    cols = {r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {src}").fetchall()}
    status = "operating_status" if "operating_status" in cols else "NULL"
    x0, y0, x1, y1 = BBOX
    q = f"""SELECT names.primary, (bbox.ymin + bbox.ymax) / 2, (bbox.xmin + bbox.xmax) / 2, phones, websites,
                   addresses[1].freeform, addresses[1].postcode, confidence, {{lam}}, {status}
            FROM {src}
            WHERE bbox.xmin BETWEEN {x0} AND {x1} AND bbox.ymin BETWEEN {y0} AND {y1}
              AND (len(phones) > 0 OR len(websites) > 0) AND names.primary IS NOT NULL"""
    try:                                      # DuckDB 1.4 and later: lambda syntax; older releases: the arrow
        rows = con.execute(q.replace("{lam}", "list_transform(sources, lambda s: s.dataset)")).fetchall()
    except duckdb.Error:
        rows = con.execute(q.replace("{lam}", "list_transform(sources, s -> s.dataset)")).fetchall()
    places = [{"name": n, "lat": round(la, 6), "lon": round(lo, 6), "phones": list(ph or []), "websites": list(w or []),
               "address": a or "", "zip": (z or "")[:5], "confidence": round(c or 0, 3),
               "sources": sorted(set(s or [])), "status": st or "open"} for n, la, lo, ph, w, a, z, c, s, st in rows]
    json.dump({"release": release, "bbox": BBOX, "places": places}, open(out, "w"))
    print(json.dumps({"release": release, "places": len(places), "withPhone": sum(1 for p in places if p["phones"])}))


def load_places(path):
    d = json.load(open(path))
    return d["places"] if isinstance(d, dict) else d


# ---------------------------------------------------------------- coverage probe (counts only)
def probe(rest_path, lic_path, places_path):
    import datetime as dt
    data, idx = json.load(open(rest_path)), Places(load_places(places_path))
    through = dt.date.fromisoformat(data["through"])
    since = (through - dt.timedelta(days=13)).isoformat()
    rows = []
    for pk in data["lists"]["flagged"]:
        p = data["places"][pk]
        x = data["inspections"][p["flaggedIds"][0]]
        if x["d"] >= since and ({"pests", "hood"} & set(x["c"])):
            rows.append({"name": p["name"], "address": p["address"], "lat": p.get("lat"), "lon": p.get("lon")})
    lic = json.load(open(lic_path))["records"]
    lrows = [{"business": r["business"], "address": r["address"], "lat": r.get("lat"), "lon": r.get("lon")} for r in lic]
    a, b = fill(rows, idx), fill(lrows, idx)
    print(json.dumps({"dailyPestHood14d": a, "licenses30d": b}))


# ---------------------------------------------------------------- planted cases
def selftest():
    P = lambda name, lat, lon, phones=(), web=(), addr="", st="open", src=("meta",): {
        "name": name, "lat": lat, "lon": lon, "phones": list(phones), "websites": list(web), "address": addr, "status": st,
        "sources": list(src)}
    assert norm_phone("+13125550199") == "", "555 exchange used"
    assert norm_phone("+1 (312) 207-4410") == "(312) 207-4410" and norm_phone("773.555.0100") == ""
    assert norm_phone("18005551234") == "" and norm_phone("8885551234") == "" and norm_phone("(877) 432-1234") == "", "toll-free used"
    assert norm_phone("312-207-441") == "" and norm_phone("112-207-4410") == "" and norm_phone("312-107-4410") == "" and norm_phone("911") == ""
    assert addr_key("1234 W Main St") == addr_key("1234 WEST MAIN STREET, Chicago, IL") == (1234, "MAIN")
    assert addr_key("1234-1236 N Clark St") == (1234, "CLARK") and addr_key("Suite 4") is None
    assert name_score("MCDONALD'S", "McDonalds") == 1.0 and name_score("Mc Donalds", "McDonald's") == 1.0
    assert name_score("Acme Tacos Inc", "ACME TACOS") == 1.0
    assert name_score("Lou Malnati's Pizzeria", "Lou Malnatis") >= 0.9
    assert name_score("Pizza Palace", "Pizza Hut") < 0.75, name_score("Pizza Palace", "Pizza Hut")
    assert name_score("Golden Dragon", "Dunkin") < 0.5
    places = [
        P("Acme Tacos", 41.88010, -87.63010, ["+13122074410"], addr="1234 W Main St"),          # 1: near, same name
        P("Pizza Hut", 41.88200, -87.63000, ["+13122074411"]),                                  # 2: near, other pizza place
        P("Golden Wok Restaurant", 41.89000, -87.64000, [], ["https://goldenwokchi.com"]),       # 3: site only
        P("Subway", 41.90000, -87.65000, ["+17735550000", "+17732109999"]),                     # 4: first phone invalid
        P("Subway", 41.90030, -87.65000, ["+17732108888"]),                                     # 4: second Subway 33 m away
        P("Closed Diner", 41.91000, -87.66000, ["+13122070001"], st="permanently_closed"),      # 5: closed
        P("Taqueria El Sol", 41.92000, -87.67000, ["+13122070002"], addr="500 N State St"),     # 6: same address, far coords
        P("Big Chain Burger", 41.93000, -87.68000, [], ["https://bigchain.com/loc/1"]),         # 7: chain domain
        P("Big Chain Burger", 41.94000, -87.69000, [], ["https://bigchain.com/loc/2"]),
        P("Big Chain Burger", 41.95000, -87.70000, [], ["https://bigchain.com/loc/3"]),
        P("Yelp Only Cafe", 41.96000, -87.71000, [], ["https://www.yelp.com/biz/x"]),           # 8: listing site
        P("Toll Free Grill", 41.97000, -87.72000, ["+18885551234"]),                            # 9: toll-free only
        P("Robots Bistro", 41.98000, -87.73000, [], ["https://robotsbistro.com"]),              # 10: robots says no
    ]
    pages = {"https://goldenwokchi.com/robots.txt": "", "https://goldenwokchi.com":
             '<html><a href="tel:+1-773-281-6060">Call</a> Reservations (773) 281-6060 <script>"x":"312-200-1111"</script></html>',
             "https://robotsbistro.com/robots.txt": "User-agent: *\nDisallow: /", "https://robotsbistro.com": '<a href="tel:3122003333">'}

    def fake(url, cap):
        if url not in pages:
            raise OSError("not planted")
        return pages[url]
    rows = [
        {"name": "ACME TACOS", "address": "1234 W Main St", "lat": 41.88000, "lon": -87.63000},          # 1 -> Overture
        {"name": "PIZZA PALACE", "address": "9 W Elm St", "lat": 41.88190, "lon": -87.63000},            # 2 -> no match
        {"name": "GOLDEN WOK", "address": "77 N Oak St", "lat": 41.89010, "lon": -87.64000},              # 3 -> website
        {"name": "SUBWAY", "address": "1 N Pine St", "lat": 41.90015, "lon": -87.65000},                  # 4 -> unsure (two Subways)
        {"name": "CLOSED DINER", "address": "2 N Pine St", "lat": 41.91000, "lon": -87.66000},            # 5 -> no match
        {"name": "TAQUERIA EL SOL INC", "address": "500 N State St", "lat": None, "lon": None},           # 6 -> by address
        {"name": "BIG CHAIN BURGER", "address": "3 N Pine St", "lat": 41.93000, "lon": -87.68000},        # 7 -> no phone (chain)
        {"business": "Yelp Only Cafe", "address": "4 N Pine St", "lat": 41.96000, "lon": -87.71000},      # 8 -> no phone (listing site)
        {"name": "TOLL FREE GRILL", "address": "5 N Pine St", "lat": 41.97000, "lon": -87.72000},         # 9 -> no phone
        {"name": "ROBOTS BISTRO", "address": "6 N Pine St", "lat": 41.98000, "lon": -87.73000},           # 10 -> no phone (robots)
    ]
    c = fill(rows, places, fetch=fake)
    got = [(r["phone"], r["phoneSource"].split(" (")[0]) for r in rows]
    want = [("(312) 207-4410", "Overture Maps places"), ("", ""), ("(773) 281-6060", "business website"), ("", ""), ("", ""),
            ("(312) 207-0002", "Overture Maps places"), ("", ""), ("", ""), ("", ""), ("", "")]
    assert got == want, got
    assert rows[0]["phoneSource"] == "Overture Maps places (meta)" and rows[2]["phoneSource"] == "business website (goldenwokchi.com)"
    assert c == {"rows": 10, "matched": 7, "overture": 2, "website": 1, "noMatch": 2, "unsure": 1, "noPhoneListed": 4,
                 "withPhone": 3, "coverage": 30.0}, c
    # no web pass: the site row stays empty
    rows2 = [dict(rows[2])]
    assert fill(rows2, places, web=False, fetch=fake)["withPhone"] == 0 and rows2[0]["phone"] == ""
    # page rules: two different tel links with no majority give nothing; JSON-LD counts; two plain numbers give nothing
    assert page_phone('<a href="tel:3122001111"></a><a href="tel:3122002222"></a>') == ""
    assert page_phone('<script type="application/ld+json">{"telephone": "+1 312-200-1111"}</script>') == "(312) 200-1111"
    assert page_phone("<p>Call 312-200-1111 or 773-200-2222</p>") == "" and page_phone("<p>Call 312-200-1111</p>") == "(312) 200-1111"
    assert site_phone("https://order.toasttab.com/x", fake)[0] == "" and site_phone("https://www.facebook.com/x", fake)[1] == "listing site"
    # the public stamp carries counts only
    import tempfile
    tf = os.path.join(tempfile.mkdtemp(), "daily.json")
    json.dump({"history": [{"asOf": "2026-10-24", "places": 10}], "examples": []}, open(tf, "w"))
    stamp_public(tf, c)
    blob = open(tf).read()
    assert json.load(open(tf))["phones"] == {"rows": 10, "withPhone": 3, "coverage": 30.0} and "207" not in blob and "Acme" not in blob
    for t in (__doc__ or "", ATTRIBUTION):
        assert chr(0x2014) not in t and chr(0x2013) not in t
    print("phones selftest ok (10 planted rows: name and address matching, two close matches, closed, toll-free, chain and "
          "listing sites, robots.txt, website tel links, counts-only public stamp)")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a == ["--release"]:
        print(latest_release())
    elif a[:1] == ["--extract"] and len(a) in (2, 4):
        extract(a[1], a[3] if len(a) == 4 and a[2] == "--release" else latest_release())
    elif a[:1] == ["--probe"] and len(a) == 4:
        probe(a[1], a[2], a[3])
    elif a[:1] == ["fill"] and len(a) >= 3:
        rows_path, places_path = a[1], a[2]
        key = a[a.index("--key") + 1] if "--key" in a else "items"
        pub = a[a.index("--public") + 1] if "--public" in a else None
        try:
            places = load_places(places_path)
        except Exception as e:                  # the list still ships, with empty phones, if the places file is missing
            print(f"phones: places file unreadable ({type(e).__name__}); phones left empty")
            places = []
        doc = json.load(open(rows_path))
        counts = fill(doc[key], places, web="--no-web" not in a)
        doc["phoneNote"] = ATTRIBUTION
        tmp = rows_path + ".tmp"                 # written whole, then moved, so a crash never leaves a half file to seal
        json.dump(doc, open(tmp, "w"), indent=1)
        os.replace(tmp, rows_path)
        if pub:
            stamp_public(pub, counts)
        print(json.dumps(counts))              # counts only: never a number or a name in the log
    else:
        raise SystemExit(__doc__)
