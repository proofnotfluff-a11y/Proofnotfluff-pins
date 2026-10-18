#!/usr/bin/env python3
"""Builder contacts for the Chicago Construction Cleaning Leads list (Todd approved Oct 17, 2026, 8:00 pm).

Buyers are post-construction cleaning companies who call a builder's office to win the final clean, so the list
can show each general contractor's main office line, a general business inbox and the website, taken only from
the builder's OWN website (never a directory, Yelp, BBB, LinkedIn, Google listing, data broker or aggregator,
never a guessed email pattern, never a person: no names, cells, direct lines or personal emails).

The file is permits/chicago/builder_contacts.enc.json (Legal desk round 2, Fix 1: this repo is public, so the contacts
are stored encrypted the same way as review.enc.json: AES-256-GCM under a key derived with PBKDF2-SHA256 at 250,000
rounds from the members' password, the LEADS_PASSWORD Actions secret). A plain builder_contacts.json must never come back
into the repo (it is in .gitignore, and tools/check_repo.py fails if one is tracked). Decrypted, it is a JSON object
keyed by the product's builder key (permits_chicago.gc_key of the name the list prints). Each entry:
  {name, website, phone, email, contactPage, source, checkedAt, status, note}
  status: verified (phone or email printed on source, a page of the builder's own site), no-site (no company site
  found), no-contact (site found but no phone or general email we could confirm), skipped (a person's name with no
  company site, or a public agency)

Do-not-list: permits/chicago/builder_do_not_list.json, a JSON list of builder keys (or names). A builder who asks to be
corrected or removed goes on it and is set to no-contact within 5 business days; contact_for() never returns an entry on
it, whatever its status, so the next build cannot add it back, and --check fails if a listed builder still carries a
phone or email.

Freshness: every entry is re-read on the builder's own site at least every 90 days; --check lists entries whose
checkedAt is older than that and exits 1.

Password: the LEADS_PASSWORD environment variable (how the permits workflow passes the secret), --pw-file PATH, or
set_password() from code (tools/leads_app.py passes on the password it was given). Never print or commit it.

Import API (for tools/leads_app.py):
  from builder_contacts import contact_for
  c = contact_for("Bulley & Andrews, L.L.C.")   # dict for a verified builder, else None
  c["phone"], c["email"], c["website"]          # "" when not printed on their site
  contact_for(name, verified_only=False)        # any entry, whatever its status

Usage:
  python3 tools/builder_contacts.py --todo [--full PATH] [--n 40]
      this week's builders missing from the file, biggest total reported cost first. Reads the paid list from
      --full (permits_chicago.py --full output) or decrypts permits/chicago/review.enc.json with LEADS_PASSWORD
      (or --pw-file). Prints builder names and totals only.
  python3 tools/builder_contacts.py --check [--pw-file PATH]
      the file's rules, the do-not-list and the 90-day freshness rule (exit 1 on any problem or stale entry)
  python3 tools/builder_contacts.py --decrypt-to PATH [--pw-file PATH]
      writes the decrypted contacts to PATH (outside the repo) for editing
  python3 tools/builder_contacts.py --encrypt-from PATH [--pw-file PATH]
      checks the edited plain file and, when it passes, writes permits/chicago/builder_contacts.enc.json
  python3 tools/builder_contacts.py --selftest   planted good and bad entries (checks the real file's entries when the
      password is set, else only the encrypted box's shape)
"""
import argparse, base64, binascii, collections, datetime as dt, json, os, re, sys, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from permits_chicago import BUSINESS, TRADE_GC, gc_filter, gc_key  # noqa: E402

ROOT = os.path.dirname(HERE)
FILE = os.path.join(ROOT, "permits", "chicago", "builder_contacts.enc.json")
PLAIN = os.path.join(ROOT, "permits", "chicago", "builder_contacts.json")   # never committed (Legal desk round 2, Fix 1)
DO_NOT_LIST = os.path.join(ROOT, "permits", "chicago", "builder_do_not_list.json")
STALE_DAYS = 90
ROUNDS = 250_000   # the same as tools/leads_page.py (kept here so the box can be checked without the cryptography package)
BOX_KEYS = {"v", "kdf", "rounds", "salt", "iv", "ct"}
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


class NoPassword(RuntimeError):
    pass


_PW = {"pw": ""}


def set_password(pw):
    """Use this password for the encrypted file from now on (tools/leads_app.py passes on the one it was given)."""
    _PW["pw"] = pw or ""
    _CACHE.clear()


def password():
    return _PW["pw"] or os.environ.get("LEADS_PASSWORD", "")


def is_box(d):
    return isinstance(d, dict) and BOX_KEYS <= set(d) and d.get("kdf") == "PBKDF2-SHA256"


def box_problems(box):
    """The encrypted file's shape, checked without the password: the same box tools/leads_page.py encrypt() writes."""
    if not is_box(box):
        return ["builder_contacts.enc.json is not an encrypted box (v, kdf, rounds, salt, iv, ct)"]
    bad = []
    if set(box) != BOX_KEYS:
        bad.append(f"box has extra fields {sorted(set(box) - BOX_KEYS)}")
    if box.get("v") != 1:
        bad.append("box version is not 1")
    if box.get("rounds") != ROUNDS:
        bad.append(f"box rounds {box.get('rounds')!r}, want {ROUNDS}")
    for f, n in (("salt", 16), ("iv", 12)):
        try:
            if len(base64.b64decode(box.get(f) or "", validate=True)) != n:
                bad.append(f"box {f} is not {n} bytes")
        except (binascii.Error, TypeError, ValueError):
            bad.append(f"box {f} is not base64")
    try:
        if len(base64.b64decode(box.get("ct") or "", validate=True)) <= 16:
            bad.append("box ciphertext is empty")
    except (binascii.Error, TypeError, ValueError):
        bad.append("box ct is not base64")
    return bad


def load(path=FILE, pw=None):
    """The contacts as a dict ({} when the file is missing). An encrypted box (the repo's file) is decrypted in memory
    with the members' password; a plain JSON object (a decrypted working copy, the selftest) is read as is."""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if is_box(d):
        pw = pw or password()
        if len(pw) < 12:
            raise NoPassword("LEADS_PASSWORD (or --pw-file) is needed to read builder_contacts.enc.json")
        from leads_page import decrypt
        return json.loads(decrypt(pw, d))
    return d


def save(data, path=FILE, pw=None):
    """Encrypt the contacts into path with the members' password (refuses on any rule problem)."""
    bad = problems(data)
    if bad:
        raise SystemExit("not saved, the contacts break the rules:\n" + "\n".join(bad))
    pw = pw or password()
    if len(pw) < 12:
        raise NoPassword("LEADS_PASSWORD (or --pw-file) is needed to write builder_contacts.enc.json")
    from leads_page import encrypt
    box = encrypt(pw, json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(box, f)
        f.write("\n")
    _CACHE.clear()
    return len(data)


def do_not_list(path=DO_NOT_LIST):
    """Builder keys that must never show a contact (a builder asked to be removed). Names are turned into keys."""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return set()
    return {key(x) for x in d if isinstance(x, str) and x.strip()} if isinstance(d, list) else set()


def do_not_list_problems(path=DO_NOT_LIST):
    try:
        d = json.load(open(path, encoding="utf-8"))
    except FileNotFoundError:
        return []
    except ValueError:
        return ["builder_do_not_list.json does not parse"]
    if not isinstance(d, list) or not all(isinstance(x, str) and x.strip() for x in d):
        return ["builder_do_not_list.json must be a JSON list of builder keys"]
    return []


_CACHE = {}


def contact_for(name, verified_only=True, path=FILE, dnl_path=DO_NOT_LIST):
    """The builder's contact entry by the name the list prints, or None. verified_only (default) returns only entries
    whose phone or email was read on the builder's own site. A builder on the do-not-list is never returned."""
    if path not in _CACHE:
        _CACHE[path] = load(path)
    if key(name) in do_not_list(dnl_path):
        return None
    c = _CACHE[path].get(key(name))
    if c is None or (verified_only and c.get("status") != "verified"):
        return None
    return dict(c)


def stale(data, today=None, days=STALE_DAYS):
    """Entries whose checkedAt is more than `days` old (the Legal desk's re-read rule), oldest first."""
    today = today or dt.date.today()
    out = []
    for k, c in data.items():
        try:
            age = (today - dt.date.fromisoformat(c.get("checkedAt") or "")).days
        except (TypeError, ValueError):
            continue
        if age > days:
            out.append((age, k, c.get("status", "")))
    return sorted(out, reverse=True)


def problems(data, dnl=None):
    """Every rule the file must keep; empty list when clean. dnl: the do-not-list keys (default: the repo's list)."""
    bad = []
    dnl = do_not_list() if dnl is None else dnl
    if not isinstance(data, dict):
        return ["the contacts are not a JSON object keyed by builder"]
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
        if k in dnl and (c["status"] == "verified" or c["phone"] or c["email"]):
            bad.append(f"{tag}: on the do-not-list, so it must be no-contact with no phone or email")
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
    assert problems({k: good}, dnl={k}), "selftest: a do-not-list builder still verified not caught"
    assert not problems({k: dict(good, status="no-contact", phone="", email="")}, dnl={k})
    assert [x[1] for x in stale({k: good, "OLD": dict(good, checkedAt="2026-01-02")}, dt.date(2026, 10, 18))] == ["OLD"]
    assert not stale({k: dict(good, checkedAt="2026-07-20")}, dt.date(2026, 10, 18)), "exactly 90 days is not stale"
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        p, dnl = os.path.join(t, "c.json"), os.path.join(t, "dnl.json")
        json.dump({k: good, key("Nobody Inc"): dict(good, name="Nobody Inc", phone="", email="", status="no-site",
                                                    website="", contactPage="", source="")}, open(p, "w"))
        json.dump([], open(dnl, "w"))
        assert contact_for("ACME BUILDERS, LLC", path=p, dnl_path=dnl)["phone"] == "(312) 555-0100"
        assert contact_for("Nobody Inc", path=p, dnl_path=dnl) is None
        assert contact_for("Nobody Inc", verified_only=False, path=p, dnl_path=dnl)["status"] == "no-site"
        assert contact_for("Not On File Co", path=p, dnl_path=dnl) is None
        # a builder who asked to be removed stays removed, whatever the contacts file says (key or name both work)
        for entry in (k, "Acme Builders, L.L.C."):
            json.dump([entry], open(dnl, "w"))
            assert contact_for("Acme Builders LLC", path=p, dnl_path=dnl) is None, entry
            assert contact_for("Acme Builders LLC", verified_only=False, path=p, dnl_path=dnl) is None, entry
        assert do_not_list_problems(dnl) == []
        json.dump({"x": 1}, open(dnl, "w"))
        assert do_not_list_problems(dnl), "selftest: a do-not-list that is not a list not caught"
        # the encrypted file: a round trip with the members' helpers, a wrong password fails, the box's shape is checked
        try:
            import leads_page  # noqa: F401  (needs the cryptography package)
            have_crypto = True
        except ImportError:
            have_crypto = False
        if have_crypto:
            enc = os.path.join(t, "c.enc.json")
            save({k: good}, enc, pw="correct horse battery")
            box = json.load(open(enc))
            assert box_problems(box) == [] and "acmebuilders" not in open(enc).read().lower(), "contacts must stay inside the ciphertext"
            assert load(enc, pw="correct horse battery") == {k: good}
            try:
                load(enc, pw="the wrong password!")
                raise AssertionError("wrong password decrypted")
            except AssertionError:
                raise
            except Exception:
                pass
            try:
                load(enc, pw="short")
                raise AssertionError("short password accepted")
            except NoPassword:
                pass
            try:
                save({k: dict(good, email="john.smith@acmebuilders.com")}, enc, pw="correct horse battery")
                raise AssertionError("save wrote a file that breaks the rules")
            except SystemExit:
                pass
            for label, b in {"low rounds": dict(box, rounds=1000), "no ciphertext": dict(box, ct=""), "short iv": dict(box, iv="AAAA"),
                             "extra field": dict(box, plain="x")}.items():
                assert box_problems(b), f"selftest: box {label} not caught"
    assert box_problems({k: good}), "selftest: a plain contacts file passed as a box"
    rows = builders([{"cost": 5, "milestone": "Partial Occupancy", "gc": ["Acme Builders LLC"], "newThisWeek": False},
                     {"cost": 9, "milestone": "Permit Issued", "gc": ["Big Co Inc", "Acme Builders, LLC"], "newThisWeek": True},
                     {"cost": 20, "milestone": "Inspections", "gc": ["Huge Builders Inc"], "newThisWeek": False}])
    assert [b["name"] for b in rows] == ["Huge Builders Inc", "Acme Builders LLC", "Big Co Inc"] and rows[1]["cost"] == 14
    assert [b["name"] for b in todo(rows, {k: good})] == ["Big Co Inc", "Huge Builders Inc"]
    assert not os.path.exists(PLAIN), "a plain builder_contacts.json is back in permits/chicago/; the repo keeps only the encrypted file"
    assert not do_not_list_problems(), "builder_do_not_list.json: " + "; ".join(do_not_list_problems())
    if os.path.exists(FILE):
        shape = box_problems(json.load(open(FILE, encoding="utf-8")))
        assert not shape, "builder_contacts.enc.json: " + "; ".join(shape)
    if len(password()) >= 12 and os.path.exists(FILE):
        data = load()
        real = problems(data)
        assert not real, "builder_contacts.enc.json: " + "; ".join(real[:5])
        what = f"file has {len(data)} entries, 0 problems"
    else:
        what = "file not decrypted (no LEADS_PASSWORD), so only the encrypted box's shape was checked"
    print(f"builder contacts selftest ok ({len(plants) + 6} planted bad entries caught; {what})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--decrypt-to", default="", metavar="PATH")
    ap.add_argument("--encrypt-from", default="", metavar="PATH")
    ap.add_argument("--full", default="")
    ap.add_argument("--pw-file", default="")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--json", action="store_true", help="with --todo: print the rows as JSON")
    a = ap.parse_args()
    if a.pw_file:
        set_password(open(a.pw_file).read().strip())
    if a.selftest:
        return selftest()
    try:
        if a.check:
            data = load()
            bad = problems(data) + do_not_list_problems()
            if os.path.exists(FILE):
                bad = box_problems(json.load(open(FILE, encoding="utf-8"))) + bad
            if os.path.exists(PLAIN):
                bad.append("a plain builder_contacts.json is in permits/chicago/; keep only the encrypted file (--encrypt-from)")
            old = stale(data)
            for age, k, st in old:
                bad.append(f"STALE {k} ({st}): checked {age} days ago; re-read it on the builder's own site (every {STALE_DAYS} days)")
            print("\n".join(bad) if bad else f"builder contacts ok ({len(data)} entries, none older than {STALE_DAYS} days)")
            sys.exit(1 if bad else 0)
        if a.decrypt_to:
            out = os.path.abspath(a.decrypt_to)
            if out == PLAIN or out.startswith(ROOT + os.sep):
                raise SystemExit("write the decrypted copy outside the repo (a scratch folder), never into it")
            data = load()
            with open(out, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=1, sort_keys=True)
                f.write("\n")
            print(f"{len(data)} entries written to {out}; edit, then --encrypt-from {out}")
            return
        if a.encrypt_from:
            data = json.load(open(a.encrypt_from, encoding="utf-8"))
            if is_box(data):
                raise SystemExit("that file is already encrypted")
            print(f"{save(data)} entries encrypted into {os.path.relpath(FILE, ROOT)}")
            return
    except NoPassword as e:
        raise SystemExit(str(e))
    if a.todo:
        pw = password()
        if not a.full and len(pw) < 12:
            raise SystemExit("LEADS_PASSWORD (or --pw-file) needed to read the encrypted review set, or pass --full")
        rows = builders(week_projects(a.full or None, pw))
        try:
            data = load()
        except NoPassword as e:
            raise SystemExit(str(e))
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
