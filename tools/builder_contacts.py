#!/usr/bin/env python3
"""Builder contacts for the Chicago Construction Cleaning Leads list (Todd approved Oct 17, 2026, 8:00 pm).

Buyers are post-construction cleaning companies who call a builder's office to win the final clean, so the list
can show each general contractor's main office line, a general business inbox and the website, taken only from
the builder's OWN website (never a directory, Yelp, BBB, LinkedIn, Google listing, data broker or aggregator,
never a guessed email pattern, never a person: no names, cells, direct lines or personal emails).

The file is permits/chicago/builder_contacts.json, keyed by the product's builder key (permits_chicago.gc_key of
the name the list prints). Each entry:
  {name, website, phone, email, contactPage, source, checkedAt, status, note}
  status: verified (phone or email printed on source, a page of the builder's own site), no-site (no company site
  found), no-contact (site found but no phone or general email we could confirm), skipped (a person's name with no
  company site, or a public agency)

Import API (for tools/leads_page.py and tools/leads_xlsx.py):
  from builder_contacts import contact_for
  c = contact_for("Bulley & Andrews, L.L.C.")   # dict for a verified builder, else None
  c["phone"], c["email"], c["website"]          # "" when not printed on their site
  contact_for(name, verified_only=False)        # any entry, whatever its status

Usage:
  python3 tools/builder_contacts.py --todo [--full PATH] [--n 40]
      this week's builders missing from the file, biggest total reported cost first. Reads the paid list from
      --full (permits_chicago.py --full output) or decrypts permits/chicago/review.enc.json with LEADS_PASSWORD
      (or --pw-file). Prints builder names and totals only.
  python3 tools/builder_contacts.py --check      the file's rules (exit 1 on any problem)
  python3 tools/builder_contacts.py --selftest   planted good and bad entries
"""
import argparse, collections, datetime as dt, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from permits_chicago import BUSINESS, TRADE_GC, gc_filter, gc_key  # noqa: E402

ROOT = os.path.dirname(HERE)
FILE = os.path.join(ROOT, "permits", "chicago", "builder_contacts.json")
REVIEW = os.path.join(ROOT, "permits", "chicago", "review.enc.json")
STATUSES = {"verified", "no-site", "no-contact", "skipped"}
FIELDS = ("name", "website", "phone", "email", "contactPage", "source", "checkedAt", "status", "note")
NEAR = ("OCCUPANCY PENDING", "PARTIAL OCCUPANCY")
# never a source (Todd, Oct 17): directories, review sites, social networks, map listings, brokers, aggregators
DIRECTORY = re.compile(r"(?:^|\.)(?:yelp|bbb|linkedin|facebook|instagram|twitter|x|google|goo|bing|yellowpages|manta|zoominfo|dnb|"
                       r"buildzoom|houzz|angi|angieslist|homeadvisor|thumbtack|porch|bizapedia|opencorporates|crunchbase|apollo|rocketreach|"
                       r"signalhire|lusha|chamberofcommerce|mapquest|superpages|dexknows|citysearch|nextdoor|glassdoor|indeed|zippia|"
                       r"buzzfile|cortera|corporationwiki|bloomberg|levelset|constructconnect|dodge|bidclerk|thebluebook|blueBook|"
                       r"procore|zoominfo|wikipedia|youtube|tiktok|pinterest)\.[a-z.]+$", re.I)
# a general business inbox, never a person's (no first.last, no first name)
GENERIC_EMAIL = re.compile(r"^(?:info|information|office|offices|contact|contactus|hello|hi|mail|main|admin|administration|general|inquiries|inquiry|"
                           r"enquiries|sales|estimating|estimates|estimate|bids|bid|bidding|precon|preconstruction|projects|"
                           r"construction|service|services|marketing|reception|frontdesk|team|chicago|newbusiness|business|"
                           r"customerservice|support|build|builders|prequal|subcontractors|ask|questions|connect|work|communications)"
                           r"(?:[._-]?(?:chicago|chi|il|us|team|desk|dept|request|requests))?@", re.I)
PHONE = re.compile(r"^\(\d{3}\) \d{3}-\d{4}(?: ext\. \d{1,5})?$")


def key(name):
    """The product's builder key: the same gc_key permits_chicago.py groups builders by."""
    return gc_key(name or "")


def domain(url):
    h = urllib.parse.urlparse(url if "//" in (url or "") else "https://" + (url or "")).hostname or ""
    return h.lower().removeprefix("www.")


def same_site(a, b):
    da, db = domain(a), domain(b)
    return bool(da) and (da == db or da.endswith("." + db) or db.endswith("." + da))


def load(path=FILE):
    try:
        return json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return {}


_CACHE = {}


def contact_for(name, verified_only=True, path=FILE):
    """The builder's contact entry by the name the list prints, or None. verified_only (default) returns only entries
    whose phone or email was read on the builder's own site."""
    if path not in _CACHE:
        _CACHE[path] = load(path)
    c = _CACHE[path].get(key(name))
    if c is None or (verified_only and c.get("status") != "verified"):
        return None
    return dict(c)


def problems(data):
    """Every rule the file must keep; empty list when clean."""
    bad = []
    for k, c in data.items():
        tag = f"{k}"
        if set(c) != set(FIELDS):
            bad.append(f"{tag}: fields {sorted(set(c) ^ set(FIELDS))}"); continue
        if key(c["name"]) != k:
            bad.append(f"{tag}: key is not key(name)")
        if c["status"] not in STATUSES:
            bad.append(f"{tag}: status {c['status']!r}")
        if "\u2014" in json.dumps(c, ensure_ascii=False):
            bad.append(f"{tag}: em dash")
        for f in ("website", "contactPage", "source"):
            if c[f] and (not c[f].startswith("https://") and not c[f].startswith("http://")):
                bad.append(f"{tag}: {f} is not a URL")
            if c[f] and DIRECTORY.search(domain(c[f])):
                bad.append(f"{tag}: {f} is a directory or social site")
        if c["phone"] and not PHONE.match(c["phone"]):
            bad.append(f"{tag}: phone format")
        if c["email"] and not GENERIC_EMAIL.match(c["email"]):
            bad.append(f"{tag}: email is not a general inbox")
        try:
            dt.date.fromisoformat(c["checkedAt"])
        except (TypeError, ValueError):
            bad.append(f"{tag}: checkedAt")
        if c["status"] == "verified":
            if not (c["phone"] or c["email"]) or not c["website"] or not c["source"]:
                bad.append(f"{tag}: verified needs website, source and a phone or email")
            for f in ("source", "contactPage"):
                if c[f] and c["website"] and not same_site(c[f], c["website"]):
                    bad.append(f"{tag}: {f} is not on the builder's own site")
        elif c["status"] in ("no-site", "skipped") and (c["phone"] or c["email"]):
            bad.append(f"{tag}: {c['status']} entry carries a phone or email")
    return bad


def week_projects(full=None, password=None):
    """This week's kept projects with their builders, from the --full file or the encrypted review set."""
    if full:
        return json.load(open(full, encoding="utf-8"))["projects"]
    from leads_page import decrypt
    box = json.load(open(REVIEW, encoding="utf-8"))
    review = json.loads(decrypt(password, box))
    latest = max(r.get("issued", "") for r in review)
    week = (dt.date.fromisoformat(latest) - dt.timedelta(days=6)).isoformat()
    out = []
    for r in review:
        if not r.get("kept"):
            continue
        gcs = []
        for nm in r.get("gcRaw") or []:
            nm = (nm or "").strip()
            if nm and BUSINESS.search(nm.upper()):
                nm = gc_filter(nm)
                if nm and gc_key(nm) not in [gc_key(g) for g in gcs]:
                    gcs.append(nm)
        gcs.sort(key=lambda g: bool(TRADE_GC.search(g.upper())))
        out.append({"cost": r.get("cost") or 0, "milestone": r.get("milestone") or "", "issued": r.get("issued", ""),
                    "newThisWeek": r.get("issued", "") >= week, "gc": gcs[:2]})
    return out


def builders(projects):
    """One row per builder: name as printed, total reported cost, projects, near-finish and new counts."""
    agg = collections.OrderedDict()
    for p in projects:
        near = any(x in (p.get("milestone") or "").upper() for x in NEAR)
        for g in p.get("gc") or []:
            b = agg.setdefault(key(g), {"key": key(g), "name": g, "n": 0, "cost": 0, "near": 0, "new": 0})
            b["n"] += 1; b["cost"] += p.get("cost") or 0; b["near"] += near; b["new"] += bool(p.get("newThisWeek"))
    return sorted(agg.values(), key=lambda b: (-b["cost"], b["name"]))


def todo(rows, data, n=0):
    """Builders missing from the file: near finish and new this week first, then the rest, each by total cost."""
    miss = [b for b in rows if b["key"] not in data]
    miss.sort(key=lambda b: (not (b["near"] or b["new"]), -b["cost"], b["name"]))
    return miss[:n] if n else miss


def selftest():
    good = {"name": "Acme Builders LLC", "website": "https://www.acmebuilders.com/", "phone": "(312) 555-0100",
            "email": "info@acmebuilders.com", "contactPage": "https://www.acmebuilders.com/contact",
            "source": "https://www.acmebuilders.com/contact", "checkedAt": "2026-10-17", "status": "verified", "note": ""}
    k = key(good["name"])
    assert problems({k: good}) == [], problems({k: good})
    plants = {
        "directory source": dict(good, source="https://www.yelp.com/biz/acme"),
        "personal email": dict(good, email="john.smith@acmebuilders.com"),
        "free-mail inbox": dict(good, email="acmebuilders@gmail.com"),
        "bad phone": dict(good, phone="312.555.0100"),
        "verified without contact": dict(good, phone="", email=""),
        "source off site": dict(good, source="https://www.example.org/acme"),
        "bad status": dict(good, status="maybe"),
        "skipped with phone": dict(good, status="skipped"),
        "em dash": dict(good, note="main line \u2014 front desk"),
        "linkedin site": dict(good, website="https://www.linkedin.com/company/acme", source="https://www.linkedin.com/company/acme",
                              contactPage="", email=""),
    }
    for label, c in plants.items():
        assert problems({k: c}), f"selftest: {label} not caught"
    assert problems({"WRONGKEY": good}), "selftest: wrong key not caught"
    assert key("BULLEY & ANDREWS, L.L.C.") == key("Bulley & Andrews, L.L.C.") == key("Bulley & Andrews LLC")
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        p = os.path.join(t, "c.json")
        json.dump({k: good, key("Nobody Inc"): dict(good, name="Nobody Inc", phone="", email="", status="no-site",
                                                    website="", contactPage="", source="")}, open(p, "w"))
        assert contact_for("ACME BUILDERS, LLC", path=p)["phone"] == "(312) 555-0100"
        assert contact_for("Nobody Inc", path=p) is None and contact_for("Nobody Inc", verified_only=False, path=p)["status"] == "no-site"
        assert contact_for("Not On File Co", path=p) is None
    rows = builders([{"cost": 5, "milestone": "Partial Occupancy", "gc": ["Acme Builders LLC"], "newThisWeek": False},
                     {"cost": 9, "milestone": "Permit Issued", "gc": ["Big Co Inc", "Acme Builders, LLC"], "newThisWeek": True},
                     {"cost": 20, "milestone": "Inspections", "gc": ["Huge Builders Inc"], "newThisWeek": False}])
    assert [b["name"] for b in rows] == ["Huge Builders Inc", "Acme Builders LLC", "Big Co Inc"] and rows[1]["cost"] == 14
    assert [b["name"] for b in todo(rows, {k: good})] == ["Big Co Inc", "Huge Builders Inc"]
    real = problems(load())
    assert not real, "builder_contacts.json: " + "; ".join(real[:5])
    print(f"builder contacts selftest ok ({len(plants) + 1} planted bad entries caught; file has {len(load())} entries, 0 problems)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--full", default="")
    ap.add_argument("--pw-file", default="")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--json", action="store_true", help="with --todo: print the rows as JSON")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if a.check:
        bad = problems(load())
        print("\n".join(bad) if bad else f"builder contacts ok ({len(load())} entries)")
        sys.exit(1 if bad else 0)
    if a.todo:
        pw = open(a.pw_file).read().strip() if a.pw_file else os.environ.get("LEADS_PASSWORD", "")
        if not a.full and len(pw) < 12:
            raise SystemExit("LEADS_PASSWORD (or --pw-file) needed to read the encrypted review set, or pass --full")
        rows = builders(week_projects(a.full or None, pw))
        data = load()
        miss = todo(rows, data, a.n)
        if a.json:
            print(json.dumps(miss, indent=0)); return
        total = sum(b["cost"] for b in rows)
        have = sum(b["cost"] for b in rows if (data.get(b["key"]) or {}).get("status") == "verified")
        print(f"{len(rows)} builders this week; {len(rows) - len(todo(rows, data))} on file; verified cover "
              f"{have / total:.0%} of ${total:,.0f} reported cost")
        for b in miss:
            flag = ("near " if b["near"] else "") + ("new" if b["new"] else "")
            try:
                print(f"${b['cost']:>13,.0f}  {b['n']:>3}  {flag:<9} {b['name']}")
            except BrokenPipeError:
                return
        return
    ap.print_help()


if __name__ == "__main__":
    main()
