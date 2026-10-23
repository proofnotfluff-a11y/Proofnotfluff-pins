#!/usr/bin/env python3
"""Listed business phone on each lead row, free route only (move 2, Todd, Oct 23, 2026).

Where a number comes from, in order:
  1 Overture Maps places (open data, read anonymously from the Overture S3 bucket in the runner). Its upstream
    sources carry CDLA Permissive 2.0, Apache 2.0 or CC0 licenses; the Legal desk review is
    legal/reviews/2026-10-23-phone-sources.md, and the attribution line is ATTRIBUTION below.
  2 The business's own website, when Overture gives a website but no usable phone: the home page is read at most once
    in 30 days (robots.txt read fresh, 5 seconds between requests, a page whose terms ban bots left alone), and a number is taken only from a tel: link, a schema.org telephone field, or the one phone number the
    page shows. Chain sites (a domain shared by 3 or more Chicago places) and listing sites (Yelp, delivery apps, social)
    are never read, because their number is not the location's own.
No paid lookup and no API key (Todd, Oct 23: no spend without his yes). OpenStreetMap is not used (share-alike terms,
see the review).

Where a number goes: only into the members' files (the sealed daily list, the members' license app and workbook).
Never into a public file, a page, a commit in clear text or a log. Logs and the public file get counts only.

How a row is matched (Legal desk condition, Oct 23: a phone only when the name AND the address match; an unsure
match leaves the phone empty):
  - a place at the same street number and street, within 300 m of the City's point (or with no point), whose name
    scores 0.5 or more on the business's own words (not "pizza" or "grill");
  - the best match must beat every other candidate with a different number clearly, or the row stays empty;
  - places Overture marks closed are skipped; toll-free and invalid numbers are never used;
  - a business that asks to drop its phone (permits/phone-optout.json, hashed) keeps its row with an empty phone.
Each row carries phoneSource (overture:<provider> or website), phoneRef (the Overture release or the site) and
phoneDate. The members' delivery ships legal/licenses/phone-sources.txt and the attribution lines with the list.

Usage (runner):
  python3 tools/phones.py --release                         the newest Overture release name
  python3 tools/phones.py --extract OUT.json [--release R]  Chicago places with a phone or a website (needs duckdb)
  python3 tools/phones.py fill ROWS.json PLACES.json [--key items|records] [--public daily.json] [--sites LOG.json] [--no-web]
  python3 tools/phones.py --optout-add "BUSINESS NAME" "STREET ADDRESS"
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
                          r"tiktok|twitter|x|yellowpages|mapquest|foursquare|squareup|clover|ezcater|trycaviar|caviar|business|square|"
                          r"online|order)\.(?:com|ee|gl|co|net|io|site|online)$", re.I)
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


# Words that never identify a business on their own (articles, titles, colors and "lucky" words), on top of GENERIC.
STOP = {"EL", "LA", "LAS", "LOS", "LE", "DE", "DEL", "DI", "DA", "MR", "MRS", "MS", "NEW", "OLD", "GOLDEN", "BIG", "LITTLE", "ROYAL",
        "GRAND", "KING", "STAR", "LUCKY", "HAPPY", "ORIGINAL", "BEST", "GOOD", "SUN"}


def name_score(a, b):
    """1.0 when one name's words all appear in the other and at least one of them is the business's own word (not
    "pizza", "golden" or "el"); 0.0 otherwise. Different numbers ("Pho 777", "Pho 888") never match. Strict on purpose:
    a wrong number costs more than an empty one (independent check, Oct 23)."""
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    if "".join(ta) == "".join(tb):
        return 1.0
    na, nb = {t for t in ta if t.isdigit()}, {t for t in tb if t.isdigit()}
    if na and nb and not (na & nb):
        return 0.0
    st = lambda t: t[:-1] if len(t) > 3 and t.endswith("S") else t
    sa, sb = {st(t) for t in ta if not t.isdigit()}, {st(t) for t in tb if not t.isdigit()}
    short, long_ = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
    if not (short - {st(g) for g in GENERIC} - STOP):
        return 0.0
    return 1.0 if short <= long_ else 0.0


def addr_key(addr):
    """"1234 W Main St" and "1234 West Main Street, Chicago" give the same key: (1234, "MAIN"). The direction is kept
    apart (addr_dir) so "2 N State" and "2 S State" never match."""
    t = re.sub(r"[^A-Z0-9 -]", " ", str(addr or "").upper()).split()
    if not t:
        return None
    m = re.match(r"^(\d+)", t[0])
    if not m:
        return None
    rest = [x for x in t[1:] if x not in DIRS]
    return (int(m.group(1)), rest[0]) if rest else None


def addr_dir(addr):
    t = re.sub(r"[^A-Z0-9 -]", " ", str(addr or "").upper()).split()
    d = t[1] if len(t) > 1 and t[1] in DIRS else ""
    return d[:1]


def dist_m(a_lat, a_lon, b_lat, b_lon):
    if None in (a_lat, a_lon, b_lat, b_lon):
        return None
    k = math.cos(math.radians((a_lat + b_lat) / 2))
    return math.hypot((a_lat - b_lat) * 111_195, (a_lon - b_lon) * 111_195 * k)


def domain(url):
    url = str(url or "")
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

    def match(self, name, address, lat, lon, strict=True):
        """(place, score, metres) or (None, reason). strict (the Legal desk rule, Oct 23): the name AND the street
        address must both match the City record. Not strict: a close name nearby is enough (kept only to measure)."""
        ak = addr_key(address)
        cand = set(self.near(lat, lon)) | set(self.by_addr.get(ak, []) if ak else [])
        good = []
        for i in cand:
            x = self.p[i]
            d = dist_m(lat, lon, x.get("lat"), x.get("lon"))
            s = name_score(name, x.get("name"))
            ad, xd = addr_dir(address), addr_dir(x.get("address"))
            same_addr = ak is not None and addr_key(x.get("address")) == ak and (not ad or not xd or ad == xd)
            by_addr = same_addr and s >= 0.5 and (d is None or d <= 300)
            ok = by_addr if strict else by_addr or (d is not None and ((d <= 120 and s >= 0.75) or (d <= 60 and s >= 0.6)))
            if ok:
                good.append((s + (0.1 if same_addr else 0) - (d or 0) / 2000, s, d, i))
        if not good:
            return None, "no match"
        good.sort(key=lambda g: g[0], reverse=True)
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
def _get(url, cap, html_only=True):
    """One page. A redirect to another domain or a listing site gives "" (the business's own site only)."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html" if html_only else "text/plain"})
    with urllib.request.urlopen(req, timeout=WEB_TIMEOUT) as r:
        final = domain(r.geturl())
        if final != domain(url) or NOT_OWN_SITE.search(final):
            if not html_only:
                raise OSError("robots.txt redirected off the site")   # read as unreachable: nothing is read
            return ""
        if html_only and "html" not in (r.headers.get("Content-Type") or "html"):
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


NO_BOTS = re.compile(r"(?:automated|robots?|bots?|spiders?|crawl\w*|scrap\w*)[^.]{0,80}\b(?:prohibit\w*|not (?:permitted|allowed)|forbidden|may not|must not)|"
                     r"\b(?:prohibit\w*|may not|must not)[^.]{0,60}(?:automated (?:means|access)|scrap\w*|crawl\w*|spiders?|robots?)", re.I)


def site_phone(url, fetch=_get, pause=None):
    """("(312) ...", domain) or ("", reason). Legal desk conditions (Oct 23): the business's own domain only, robots.txt
    read fresh each time, the home page only, 5 seconds between the two requests, nothing bypassed, and a page whose
    text bans automated access is left alone."""
    import time
    pause = pause or time.sleep
    url = url if "//" in url else "https://" + url
    dom = domain(url)
    if not dom or NOT_OWN_SITE.search(dom):
        return "", "listing site"
    import urllib.error
    base = f"{urllib.parse.urlparse(url).scheme}://{urllib.parse.urlparse(url).netloc}"
    url = base + "/"                           # the home page only, whatever deeper page Overture lists
    try:
        robots = fetch(base + "/robots.txt", 200_000, html_only=False)
    except urllib.error.HTTPError as e:
        if e.code >= 500:
            return "", "robots.txt unavailable"   # RFC 9309: a server error means read nothing
        robots = ""                               # no robots.txt (4xx): the page may be read
    except Exception:
        return "", "robots.txt unreachable"
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(robots.splitlines())
    if not rp.can_fetch(UA, url):
        return "", "robots.txt"
    pause(5)
    try:
        text = fetch(url, WEB_BYTES, html_only=True)
    except Exception:
        return "", "site unreachable"
    if not text:
        return "", "not the business's own page"
    if NO_BOTS.search(re.sub(r"<[^>]+>", " ", text)):
        return "", "site terms ban automated access"
    ph = page_phone(text)
    return (ph, dom) if ph else ("", "no number on page")


# ---------------------------------------------------------------- filling rows
def fill(rows, places, web=True, fetch=_get, name_field=None, strict=True, release="", sites=None, today=None, optout=None,
         pause=None, used=None):
    """Sets phone, phoneSource, phoneRef and phoneDate on each row (rows need a name or business, address, lat, lon).
    sites: the 30-day log of website reads (domain: {"date", "phone"}), read and updated in place. used: a set that
    collects the Overture providers behind the numbers (for the attribution lines). Returns counts only."""
    import datetime as dt
    idx = places if isinstance(places, Places) else Places(places)
    today = today or dt.date.today().isoformat()
    sites = {} if sites is None else sites
    used = set() if used is None else used
    c = collections.Counter(rows=len(rows))
    todo = []
    for r in rows:
        r["phone"], r["phoneSource"], r["phoneRef"], r["phoneDate"] = "", "", "", ""
        nm = r.get(name_field) if name_field else (r.get("name") or r.get("business"))
        if optout and optout_key(nm, r.get("address")) in optout:
            c["optedOut"] += 1
            continue
        hit, why = idx.match(nm, r.get("address"), r.get("lat"), r.get("lon"), strict=strict)
        if not hit:
            c["noMatch" if why == "no match" else "unsure"] += 1
            continue
        x = hit[0]
        c["matched"] += 1
        ph = first_phone(x)
        if ph:
            src = [s.lower() for s in x.get("sources") or []] or ["unknown"]
            r["phone"], r["phoneSource"], r["phoneRef"], r["phoneDate"] = ph, "overture:" + "+".join(src), release, release[:10]
            used.update(src)
            c["overture"] += 1
            continue
        own = [w for w in x.get("websites") or [] if domain(w) and idx.domains[domain(w)] < CHAIN_DOMAIN]
        if web and own:
            todo.append((r, own[0]))
        else:
            c["noPhoneListed"] += 1
    # A site read in the last 30 days is not read again (Legal desk): its logged result is used, number or none.
    cut = (dt.date.fromisoformat(today) - dt.timedelta(days=30)).isoformat()
    fresh = lambda dom: dom in sites and sites[dom].get("date", "") >= cut
    need = list(dict.fromkeys(domain(u) for _, u in todo if not fresh(domain(u))))
    skipped = set(need[WEB_CAP:])                  # past the cap, a row keeps an empty phone rather than a slow run
    urls = {domain(u): u for _, u in todo}
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        for dom, (ph, _) in zip(need[:WEB_CAP], ex.map(lambda d: site_phone(urls[d], fetch, pause), need[:WEB_CAP])):
            sites[dom] = {"date": today, "phone": ph}
    for r, u in todo:
        dom = domain(u)
        hit = sites.get(dom) if dom not in skipped else None
        if hit and hit.get("phone"):
            r["phone"], r["phoneSource"], r["phoneRef"], r["phoneDate"] = hit["phone"], "website", f"https://{dom}/", hit["date"]
            c["website"] += 1
        else:
            c["noPhoneListed"] += 1
    c["withPhone"] = c["overture"] + c["website"]
    c["coverage"] = round(100 * c["withPhone"] / c["rows"], 1) if c["rows"] else 0.0
    return dict(c)


PROVIDERS = {"meta": "Meta", "microsoft": "Microsoft", "pinmeto": "PinMeTo", "krick": "Krick", "renderseo": "RenderSEO", "dac": "DAC",
             "brightquery": "BrightQuery", "birdeye": "Birdeye", "uberall": "Uberall", "opentravel": "OpenTravel Alliance",
             "opentravel alliance": "OpenTravel Alliance", "foursquare": "Foursquare", "alltheplaces": "AllThePlaces",
             "msft": "Microsoft", "fsq": "Foursquare", "atp": "AllThePlaces"}
LICENSES_FILE = "legal/licenses/phone-sources.txt"
TERMS_LINES = [
    "Phone numbers are the number each business lists publicly (from Overture Maps data or the business's own website). "
    "We do not verify who answers, and some may be cell phones.",
    "You must follow all calling laws, including do-not-call rules and Illinois calling hours, never use an autodialer, "
    "prerecorded or AI voice without the consent the law requires, and never say or imply you call for the City."]


def attribution(used, release):
    """The Overture attribution lines (docs.overturemaps.org/attribution, read Oct 23, 2026) for the providers used."""
    out = []
    for k in sorted(used):
        name = PROVIDERS.get(k)
        if name == "Foursquare":
            out += ["Data from Foursquare. Copyright 2024 Foursquare Labs, Inc. All rights reserved. Available under Apache 2.0.",
                    "Foursquare data was transformed to the Overture schema."]
        elif name == "AllThePlaces":
            out.append("Data from AllThePlaces. Available under CC0 1.0.")
        elif name:
            out.append(f"Data from {name}. Available under CDLA Permissive 2.0.")
        else:
            out.append(f"Data from {k} through Overture Maps (see {LICENSES_FILE}).")
    if used:
        out.append(f"Overture Maps Foundation Open Map Data (release {release}) was accessed on {release[:10]} from "
                   "https://registry.opendata.aws/overture.")
    return out


OPTOUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "permits", "phone-optout.json")
OPTOUT_SALT = "proofnotfluff-phone-optout-v1"


def optout_key(name, address):
    import hashlib
    return hashlib.sha256(f"{OPTOUT_SALT}|{' '.join(tokens(name))}|{addr_key(address)}".encode()).hexdigest()[:24]


def optout_load(path=OPTOUT):
    return set(json.load(open(path)).get("keys", [])) if os.path.exists(path) else set()


def optout_add(name, address, path=OPTOUT):
    """A business that asks for its phone to be dropped (Legal desk: within 5 business days). Its name and address are
    stored only as a hash; the row stays on the list with an empty phone."""
    keys = optout_load(path) | {optout_key(name, address)}
    _save({"about": "Businesses that asked us to drop their phone number, as SHA-256 keys of name and street "
                    "(tools/phones.py). No names, no numbers.", "salt": OPTOUT_SALT, "keys": sorted(keys)}, path, indent=1)


def _save(obj, path, **kw):
    """Written whole to a side file, then moved: a crash never leaves a half file to commit, cache or seal."""
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(obj, f, **kw)
    os.replace(tmp, path)


def stamp_public(path, counts):
    """Counts only on the public daily file: how many of today's rows carry a phone. Never a number or a name."""
    pub = json.load(open(path))
    pub["phones"] = {"rows": counts["rows"], "withPhone": counts["withPhone"], "coverage": counts["coverage"]}
    if pub.get("history"):
        pub["history"][-1]["withPhone"] = counts["withPhone"]
    _save(pub, path, indent=1)


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
    _save({"release": release, "bbox": BBOX, "places": places}, out)
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
    out = {}
    for mode in (True, False):
        tag = "nameAndAddress" if mode else "nameNearby"
        out[tag] = {"dailyPestHood14d": fill([dict(r) for r in rows], idx, strict=mode, pause=lambda s: None),
                    "licenses30d": fill([dict(r) for r in lrows], idx, strict=mode, pause=lambda s: None)}
    print(json.dumps(out))


# ---------------------------------------------------------------- planted cases
def selftest():
    import tempfile
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
    same = [("Lou Malnati's Pizzeria", "Lou Malnatis"), ("Subway #4521", "Subway"), ("Golden Wok", "Golden Wok Restaurant"),
            ("La Pasadita", "La Pasadita Restaurant Inc"), ("J & J Fish", "J&J Fish and Chicken"), ("Dunkin", "Dunkin Donuts"),
            ("7-Eleven", "7 Eleven"), ("Starbucks Coffee #2345", "Starbucks"), ("La Michoacana", "La Michoacana Premium")]
    other = [("Pizza Palace", "Pizza Hut"), ("Golden Dragon", "Dunkin"), ("Taqueria El Rey", "Taqueria El Sol"),
             ("Golden Dragon", "Golden Nugget"), ("Mr Beef", "Mr. Brown's Lounge"), ("New China", "China King"),
             ("Golden House", "Golden Wok"), ("Pho 777", "Pho 888"), ("Cafe 23", "Cafe 32"), ("Taqueria El Rey", "Taqueria"),
             ("Pizza", "Pizza Hut"), ("Mexican Restaurant", "Restaurant"), ("Mario", "Maria"), ("Little Caesars", "Little Italy"),
             ("Lou Malnatis", "Lou Mitchells"), ("Kim Bap", "Kim Chi"), ("Thai Spoon", "Thai Basil"), ("Cafe Mexico", "Cafe Lucci")]
    assert all(name_score(a, b) == 1.0 for a, b in same), [(a, b) for a, b in same if name_score(a, b) < 1]
    assert all(name_score(a, b) < 0.5 for a, b in other), [(a, b) for a, b in other if name_score(a, b) >= 0.5]
    assert addr_dir("2 N State St") == "N" and addr_dir("2 North State Street") == "N" and addr_dir("2 State St") == ""
    places = [
        P("Acme Tacos", 41.88010, -87.63010, ["+13122074410"], addr="1234 W Main St"),          # 1: name and address
        P("Pizza Hut", 41.88200, -87.63000, ["+13122074411"], addr="9 W Elm St"),               # 2: same address, other name
        P("Golden Wok Restaurant", 41.89000, -87.64000, [], ["https://goldenwokchi.com"], addr="77 N Oak St"),   # 3: site only
        P("Subway", 41.90000, -87.65000, ["+17735550000", "+17732109999"], addr="1 N Pine St"), # 4: first phone invalid
        P("Subway", 41.90030, -87.65000, ["+17732108888"], addr="1 N Pine St"),                 # 4: second Subway, same address
        P("Closed Diner", 41.91000, -87.66000, ["+13122070001"], addr="2 N Pine St", st="permanently_closed"),   # 5: closed
        P("Taqueria El Sol", 41.92000, -87.67000, ["+13122070002"], addr="500 N State St"),     # 6: same address, no City coords
        P("Big Chain Burger", 41.93000, -87.68000, [], ["https://bigchain.com/loc/1"], addr="3 N Pine St"),       # 7: chain domain
        P("Big Chain Burger", 41.94000, -87.69000, [], ["https://bigchain.com/loc/2"]),
        P("Big Chain Burger", 41.95000, -87.70000, [], ["https://bigchain.com/loc/3"]),
        P("Yelp Only Cafe", 41.96000, -87.71000, [], ["https://www.yelp.com/biz/x"], addr="4 N Pine St"),         # 8: listing site
        P("Toll Free Grill", 41.97000, -87.72000, ["+18885551234"], addr="5 N Pine St"),        # 9: toll-free only
        P("Robots Bistro", 41.98000, -87.73000, [], ["https://robotsbistro.com"], addr="6 N Pine St"),            # 10: robots says no
        P("Near Name Cafe", 41.99000, -87.74000, ["+13122070003"], addr=""),                    # 11: name nearby, no address
        P("No Bots Deli", 41.99500, -87.74500, [], ["https://nobotsdeli.com"], addr="8 N Pine St"),               # 12: terms ban bots
        P("Fsq Spot", 41.99800, -87.74800, ["+13122070004"], addr="9 N Pine St", src=("Foursquare",)),           # 13: Foursquare
    ]
    pages = {"https://goldenwokchi.com/robots.txt": "", "https://goldenwokchi.com/":
             '<html><a href="tel:+1-773-281-6060">Call</a> Reservations (773) 281-6060 <script>"x":"312-200-1111"</script></html>',
             "https://robotsbistro.com/robots.txt": "User-agent: *\nDisallow: /", "https://robotsbistro.com/": '<a href="tel:3122003333">',
             "https://nobotsdeli.com/robots.txt": "", "https://nobotsdeli.com/":
             '<a href="tel:3122004444"></a><p>Use of robots, spiders or scrapers on this site is prohibited.</p>'}
    calls, waits = [], []

    def fake(url, cap, **kw):
        calls.append(url)
        if url not in pages:
            raise OSError("not planted")
        return pages[url]
    row = lambda n, a, la, lo, k="name": {k: n, "address": a, "lat": la, "lon": lo}
    rows = [
        row("ACME TACOS", "1234 W Main St", 41.88000, -87.63000),          # 1 -> Overture
        row("PIZZA PALACE", "9 W Elm St", 41.88190, -87.63000),            # 2 -> no match (other name at the address)
        row("GOLDEN WOK", "77 N Oak St", 41.89010, -87.64000),             # 3 -> website
        row("SUBWAY", "1 N Pine St", 41.90015, -87.65000),                 # 4 -> unsure (two Subways)
        row("CLOSED DINER", "2 N Pine St", 41.91000, -87.66000),           # 5 -> no match
        row("TAQUERIA EL SOL INC", "500 N State St", None, None),          # 6 -> by address
        row("BIG CHAIN BURGER", "3 N Pine St", 41.93000, -87.68000),       # 7 -> no phone (chain)
        row("Yelp Only Cafe", "4 N Pine St", 41.96000, -87.71000, "business"),   # 8 -> no phone (listing site)
        row("TOLL FREE GRILL", "5 N Pine St", 41.97000, -87.72000),        # 9 -> no phone
        row("ROBOTS BISTRO", "6 N Pine St", 41.98000, -87.73000),          # 10 -> no phone (robots)
        row("NEAR NAME CAFE", "7 N Pine St", 41.99000, -87.74000),         # 11 -> no match: name and address both needed
        row("NO BOTS DELI", "8 N Pine St", 41.99500, -87.74500),           # 12 -> no phone (site terms)
        row("FSQ SPOT", "9 N Pine St", 41.99800, -87.74800),               # 13 -> Overture, Foursquare
    ]
    sites, used = {}, set()
    c = fill(rows, places, fetch=fake, release="2026-10-21.0", sites=sites, today="2026-10-24", pause=waits.append, used=used)
    got = [(r["phone"], r["phoneSource"]) for r in rows]
    want = [("(312) 207-4410", "overture:meta"), ("", ""), ("(773) 281-6060", "website"), ("", ""), ("", ""),
            ("(312) 207-0002", "overture:meta"), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""), ("", ""),
            ("(312) 207-0004", "overture:foursquare")]
    assert got == want, got
    assert rows[0]["phoneRef"] == "2026-10-21.0" and rows[0]["phoneDate"] == "2026-10-21"
    assert rows[2]["phoneRef"] == "https://goldenwokchi.com/" and rows[2]["phoneDate"] == "2026-10-24"
    assert c == {"rows": 13, "matched": 9, "overture": 3, "website": 1, "noMatch": 3, "unsure": 1, "noPhoneListed": 5,
                 "withPhone": 4, "coverage": 30.8}, c
    assert waits == [5, 5] and "https://robotsbistro.com/" not in calls and not any("yelp" in u or "bigchain" in u for u in calls), (waits, calls)
    assert sites["robotsbistro.com"]["phone"] == "" and sites["nobotsdeli.com"]["phone"] == "" and used == {"meta", "foursquare"}
    # a site read in the last 30 days is not read again; its logged result is used
    calls.clear()
    again = [dict(rows[2])]
    assert fill(again, places, fetch=fake, sites=sites, today="2026-11-10", pause=waits.append)["website"] == 1 and calls == []
    assert again[0]["phone"] == "(773) 281-6060" and again[0]["phoneDate"] == "2026-10-24"
    fill([dict(rows[2])], places, fetch=fake, sites=sites, today="2026-11-30", pause=waits.append)
    assert calls == ["https://goldenwokchi.com/robots.txt", "https://goldenwokchi.com/"], "a 30-day-old read was not refreshed"
    # a deep page Overture lists is never read: the home page is; robots.txt server errors and timeouts read nothing
    import urllib.error
    calls.clear()
    assert site_phone("https://goldenwokchi.com/locations/chicago/menu", fake, lambda s: None)[0] == "(773) 281-6060"
    assert calls == ["https://goldenwokchi.com/robots.txt", "https://goldenwokchi.com/"], calls

    def err(code):
        def f(url, cap, **kw):
            if url.endswith("robots.txt"):
                raise urllib.error.HTTPError(url, code, "x", {}, None) if code else OSError("timeout")
            return '<a href="tel:3122005555">'
        return f
    assert site_phone("https://a.com", err(503), lambda s: None) == ("", "robots.txt unavailable")
    assert site_phone("https://a.com", err(0), lambda s: None) == ("", "robots.txt unreachable")
    assert site_phone("https://a.com", err(404), lambda s: None) == ("(312) 200-5555", "a.com")
    # the real fetcher: a text/plain robots.txt is read (it was dropped as "not HTML" before), an off-domain redirect gives ""
    import email.message, io
    real_open = urllib.request.urlopen

    class Resp(io.BytesIO):
        def __init__(self, body, ctype, final):
            super().__init__(body.encode()); self._u = final
            self.headers = email.message.Message(); self.headers["Content-Type"] = ctype
        def geturl(self): return self._u
        def __enter__(self): return self
        def __exit__(self, *a): self.close()
    web = {"https://b.com/robots.txt": ("User-agent: *\nDisallow: /", "text/plain; charset=utf-8", "https://b.com/robots.txt"),
           "https://b.com/": ('<a href="tel:3122006666">', "text/html", "https://b.com/"),
           "https://c.com/robots.txt": ("", "text/plain", "https://c.com/robots.txt"),
           "https://d.com/robots.txt": ("", "text/plain", "https://elsewhere.com/robots.txt"),
           "https://c.com/": ('<a href="tel:3122007777">', "text/html", "https://www.toasttab.com/c")}
    urllib.request.urlopen = lambda req, timeout=0: Resp(*web[req.full_url])
    try:
        assert site_phone("https://b.com", _get, lambda s: None) == ("", "robots.txt"), "text/plain robots.txt ignored"
        assert site_phone("https://c.com", _get, lambda s: None) == ("", "not the business's own page"), "off-domain redirect read"
        assert site_phone("https://d.com", _get, lambda s: None) == ("", "robots.txt unreachable"), "redirected robots read as allow"
        assert site_phone("https://order.online/x", _get, lambda s: None) == ("", "listing site")
    finally:
        urllib.request.urlopen = real_open
    # opposite directions never match; a tie between a place with a point and one without does not crash the sort
    dirs = [P("Acme Tacos", 41.88010, -87.63010, ["+13122074410"], addr="2 S State St")]
    assert fill([{"name": "ACME TACOS", "address": "2 N State St", "lat": None, "lon": None}], dirs, web=False)["withPhone"] == 0
    tie = [P("Twin Grill", 41.88, -87.63, ["+13122074420"], addr="11 W Elm St"), P("Twin Grill", None, None, ["+13122074421"], addr="11 W Elm St")]
    assert fill([{"name": "TWIN GRILL", "address": "11 W Elm St", "lat": 41.88, "lon": -87.63}], tie, web=False)["unsure"] == 1
    # the looser rule (measured only) matches a close name nearby without the address
    loose = [dict(rows[10])]
    assert fill(loose, places, web=False, strict=False)["withPhone"] == 1 and fill([dict(rows[10])], places, web=False)["withPhone"] == 0
    # no web pass: the site row stays empty
    assert fill([dict(rows[2])], places, web=False, fetch=fake)["withPhone"] == 0
    # opt-out: a business that asked keeps its row and loses its phone
    tf = os.path.join(tempfile.mkdtemp(), "optout.json")
    optout_add("Acme Tacos", "1234 W. Main Street", tf)
    oo = [dict(rows[0])]
    assert fill(oo, places, optout=optout_load(tf))["optedOut"] == 1 and oo[0]["phone"] == ""
    assert "Acme" not in open(tf).read() and "Main" not in open(tf).read()
    # attribution lines: one per provider used, the AWS citation, the release
    at = attribution({"meta", "foursquare"}, "2026-10-21.0")
    assert at[0].startswith("Data from Foursquare. Copyright 2024") and "Data from Meta. Available under CDLA Permissive 2.0." in at
    assert at[-1].startswith("Overture Maps Foundation Open Map Data (release 2026-10-21.0) was accessed on 2026-10-21") and attribution(set(), "x") == []
    # page rules: two different tel links with no majority give nothing; JSON-LD counts; two plain numbers give nothing
    assert page_phone('<a href="tel:3122001111"></a><a href="tel:3122002222"></a>') == ""
    assert page_phone('<script type="application/ld+json">{"telephone": "+1 312-200-1111"}</script>') == "(312) 200-1111"
    assert page_phone("<p>Call 312-200-1111 or 773-200-2222</p>") == "" and page_phone("<p>Call 312-200-1111</p>") == "(312) 200-1111"
    assert site_phone("https://order.toasttab.com/x", fake)[0] == "" and site_phone("https://www.facebook.com/x", fake)[1] == "listing site"
    # the public stamp carries counts only
    tf = os.path.join(tempfile.mkdtemp(), "daily.json")
    json.dump({"history": [{"asOf": "2026-10-24", "places": 13}], "examples": []}, open(tf, "w"))
    stamp_public(tf, c)
    blob = open(tf).read()
    assert json.load(open(tf))["phones"] == {"rows": 13, "withPhone": 4, "coverage": 30.8} and "207" not in blob and "Acme" not in blob
    for t in (__doc__ or "", ATTRIBUTION, *TERMS_LINES, *at):
        assert chr(0x2014) not in t and chr(0x2013) not in t
    print("phones selftest ok (13 planted rows: name and address both required, two close matches, closed, toll-free, chain and "
          "listing sites, robots.txt, site terms, 5-second gap, 30-day site log, opt-out, attribution, counts-only public stamp)")

if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a == ["--release"]:
        print(latest_release())
    elif a[:1] == ["--extract"] and len(a) in (2, 4):
        extract(a[1], a[3] if len(a) == 4 and a[2] == "--release" else latest_release())
    elif a[:1] == ["--optout-add"] and len(a) == 3:
        optout_add(a[1], a[2])
        print("phones: opt-out recorded")
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
        opt = lambda f: a[a.index(f) + 1] if f in a else None
        try:
            release = json.load(open(places_path)).get("release", "")
        except Exception:
            release = ""
        sites_path = opt("--sites")
        try:
            sites = json.load(open(sites_path)) if sites_path and os.path.exists(sites_path) else {}
        except Exception:
            sites = {}                          # an unreadable log means sites are read again, never a failed step
        doc, used = json.load(open(rows_path)), set()
        counts = fill(doc[key], places, web="--no-web" not in a, release=release, sites=sites, optout=optout_load(), used=used)
        if sites_path:
            _save(sites, sites_path)
        doc["phoneNote"] = ATTRIBUTION
        doc["phoneTerms"] = TERMS_LINES
        doc["phoneAttribution"] = attribution(used, release)
        doc["phoneLicenses"] = LICENSES_FILE
        _save(doc, rows_path, indent=1)
        if pub:
            stamp_public(pub, counts)
        print(json.dumps(counts))              # counts only: never a number or a name in the log
    else:
        raise SystemExit(__doc__)
