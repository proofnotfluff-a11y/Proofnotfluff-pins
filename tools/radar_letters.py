#!/usr/bin/env python3
"""Chicago Restaurant Radar: the first letter or email a vendor sends a food business, one per trade, filled from that
business's newest City record (launches/chicago-restaurant-radar.md, screens 2 and 4). Same rows, the letter changes.

The members' app fills these in the buyer's browser (tools/radar_app.py embeds TRADES and the record lines as data);
this file is the one source, and tools/copy_gate.py --radar-templates / --radar-live check every trade's letter on fixture
businesses and on the live list before anything ships.

Letter rules (the pitch kit's rules, tools/lic_xlsx.py PITCH_RULES, plus the copy gate's):
  - body under 75 words; the sign-off and the sales and stop lines sit under it and are not counted;
  - no link or domain, no em or en dash, no leftover placeholder;
  - names the City record and its date exactly as the City has it ("Oct 16"), and no other date;
  - names the street, never the house number (the business knows its own address);
  - never says the business is open, new to Chicago, failed, unsafe or in need, and never repeats an inspection result;
  - only its own trade's words; ends with a question.

Usage: python3 tools/radar_letters.py --selftest
"""
import datetime as dt, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pnf_rules as R  # noqa: E402

# key, label, short, subject, what we do (one true sentence the member can edit), the question
TRADES = [
    {"key": "pest", "label": "Pest control", "short": "Pest",
     "subject": "Pest control for {name}",
     "offer": "We set food businesses up with a pest service plan and leave a dated service record after every visit.",
     "ask": "Would a visit this week work for you?"},
    {"key": "hood", "label": "Hood and exhaust cleaning", "short": "Hood",
     "subject": "Hood cleaning for {name}",
     "offer": "We clean kitchen hoods, filters and exhaust ducts and leave a dated service label after each cleaning.",
     "ask": "Could I send you a quote for a first cleaning?"},
    {"key": "grease", "label": "Grease trap service", "short": "Grease trap",
     "subject": "Grease trap service for {name}",
     "offer": "We pump and service grease traps and interceptors on a set schedule and keep a dated service log for you.",
     "ask": "Could I send you a quote?"},
    {"key": "clean", "label": "Commercial cleaning", "short": "Cleaning",
     "subject": "Cleaning for {name}",
     "offer": "We clean restaurants and food shops nightly or weekly, on a schedule that fits your hours.",
     "ask": "Is there a good day for us to walk the space?"},
    {"key": "pos", "label": "POS and payments", "short": "POS",
     "subject": "Point of sale for {name}",
     "offer": "We set food businesses up with point of sale and card payments, including menus, tips and online orders.",
     "ask": "Could I show you a short demo this week?"},
    {"key": "signs", "label": "Signs", "short": "Signs",
     "subject": "Storefront signs for {name}",
     "offer": "We design, build and install storefront and window signs for food businesses.",
     "ask": "Could I send you a few ideas for the storefront?"},
    {"key": "insurance", "label": "Insurance", "short": "Insurance",
     "subject": "Insurance quote for {name}",
     "offer": "We help food businesses set up general liability, property and workers' compensation coverage.",
     "ask": "Could I send you a quote to compare?"},
]
TRADE = {t["key"]: t for t in TRADES}

# the record a letter names: the newest of these the business has, in this order of preference
RECORD_LINE = {"license": "City of Chicago records show a new {licenseType} license for {street} on {date}.",
               "linsp": "City of Chicago records show a food license inspection for {street} on {date}.",
               "permit": "City of Chicago records show a building permit for {street} on {date}."}
RECORD_WORDS = {"license": "license", "linsp": "food license inspection", "permit": "building permit"}
OPEN = "Hi {who}, I'm {me} with {company}."
SIGN = "{me}, {company}, {phone}, {companyAddress}"
STOP = "This is a sales email from {company}. Not interested? Reply \"stop\" and I won't contact you again."

TRADE_WORDS = {"pest": r"\bpests?\b", "hood": r"\bhoods?\b|\bexhaust\b", "grease": r"\bgrease\b", "clean": r"\bclean(?:ing)?\b",
               "pos": r"\bpoint of sale\b|\bpayments?\b", "signs": r"\bsigns?\b", "insurance": r"\binsurance\b|\bcoverage\b|\bliability\b"}
SHARED_WORDS = {"hood": ("clean",)}      # "we clean kitchen hoods" is the hood trade's own sentence
FORBID = re.compile(r"\bopen(?:ed|ing|s)?\b|\bnew to chicago\b|\bfail\w*|\bviolat\w*|\bunsafe\b|\bdirty\b|\bpass(?:ed)?\b|\bconditions?\b|"
                    r"\bcited\b|\bcitation\b|\bneed(?:s)?\b|\bclosed?\b|\brodents?\b|\bmice\b|\broach\w*|\binfest\w*", re.I)


def pick_record(events):
    """The event a letter names: the newest license, else the newest license inspection, else the newest permit."""
    for t in ("license", "linsp", "permit"):
        ev = sorted((e for e in events if e.get("t") == t), key=lambda e: e.get("d") or "")
        if ev:
            return ev[-1]
    return None


def street_of(address):
    a = re.sub(r"^\s*(\d+)\s+1/2\s+", r"\1 ", address or "")      # "1046 1/2 W Argyle St" is house 1046 on W Argyle St
    return R.street_display(R.signal_address(a)) or R.street_display(a)


SUBJECT_NAME_WORDS = 6    # a longer name ("... Market and Maxwell Street BBQ") makes the subject "... for your space on <street>"


def subject_name(name, street):
    if not name:
        return "the new space on " + street
    return name if len(R.words(name)) <= SUBJECT_NAME_WORDS else "your space on " + street


def fill(b, trade, me):
    """(subject, body, sign-off, stop line) for business b (the app's record: name, address, licenseType, events) and the
    member's own details me {me, company, phone, companyAddress}."""
    t = TRADE[trade]
    ev = pick_record(b["events"])
    street = street_of(b["address"])
    name = b.get("name") or ""
    who = f"{name} team" if name else "there"
    rec = RECORD_LINE[ev["t"]].format(licenseType=(ev.get("type") or b.get("licenseType") or "").strip() or "food", street=street,
                                      date=R.date_display(ev["d"]))
    subject = t["subject"].format(name=subject_name(name, street))
    body = " ".join([OPEN.format(who=who, **me), rec, t["offer"], t["ask"]])
    return subject, body, SIGN.format(**me), STOP.format(**me)


def problems(subject, body, sign, stop, b, trade, me):
    """Everything wrong with one filled letter. [] means it passes."""
    p, s = [], subject or ""
    ev = pick_record(b["events"])
    name = b.get("name") or ""
    mask = lambda t: re.sub(re.escape(name), "Name", t, flags=re.I) if name else t
    mine = lambda t: re.sub("|".join(re.escape(v) for v in me.values() if v), " ", t)
    n = len(R.words(body))
    if n >= R.MAX_WORDS:
        p.append(f"body is {n} words, the limit is under {R.MAX_WORDS}")
    if len(R.words(s)) > R.MAX_SUBJECT_WORDS:
        p.append(f"subject is {len(R.words(s))} words, the limit is {R.MAX_SUBJECT_WORDS}")
    for label, t in (("subject", s), ("body", body), ("sign-off", sign), ("stop line", stop)):
        m = R.URL_RE.search(R.link_safe(mine(t)))
        if m:
            p.append(f"{label} carries a link or domain ({m.group(0)!r})")
        if any(d in t for d in R.DASHES):
            p.append(f"{label} carries an em or en dash")
        if re.search(r"[{}\[\]<>]", t):
            p.append(f"{label} has a leftover placeholder bracket")
    for label, t in (("subject", s), ("body", body)):
        m = FORBID.search(mask(mine(t)))
        if m:
            p.append(f"{label} says {m.group(0)!r}: name the City record and its date, and stop there")
        for k, pat in TRADE_WORDS.items():
            if k != trade and k not in SHARED_WORDS.get(trade, ()) and re.search(pat, mask(mine(t)), re.I):
                p.append(f"{label} uses another trade's words ({k})")
    if not re.search(TRADE_WORDS[trade], body, re.I):
        p.append(f"body never names the trade ({trade})")
    if name and name.lower() not in body.lower():
        p.append(f"body does not name the business {name!r}")
    street = street_of(b["address"])
    if not street or street.lower() not in body.lower():
        p.append(f"body does not name the street ({street!r})")
    house = (re.match(r"^\s*(\d+)", b["address"] or "") or [None, None])[1]
    rest = mask(mine(s + "\n" + body))
    want_date = R.date_display(ev["d"]) if ev else ""
    no_date = rest.replace(want_date, " ") if want_date else rest      # "Sep 10" is the City's date, not house number 10
    if house and re.search(r"(?<![\d$.,])%s(?![\d,%%])" % re.escape(house), no_date):
        p.append(f"letter gives the house number {house}; name the street only")
    want = R.date_display(ev["d"]) if ev else ""
    if not ev:
        p.append("business has no City record to name")
    elif want not in body:
        p.append(f"body does not state the record's date as the City has it ({want!r})")
    for m in R.DATE_IN_COPY.findall(rest):
        if m != want:
            p.append(f"letter states {m!r}, the City record says {want!r}")
    if ev and RECORD_WORDS[ev["t"]] not in body.lower():
        p.append(f"body does not name the record ({RECORD_WORDS[ev['t']]!r})")
    if not body.rstrip().endswith("?"):
        p.append("body must end with a question")
    if "sales email" not in stop.lower() or "stop" not in stop.lower():
        p.append("stop line must say it is a sales email and how to say stop")
    for k in ("me", "company", "phone", "companyAddress"):
        if me.get(k) and me[k] not in sign:
            p.append(f"sign-off is missing the member's {k}")
    return p


FIXTURE_ME = {"me": "Dana Ruiz", "company": "Northside Service Co", "phone": "(773) 555-0142", "companyAddress": "4410 N Lincoln Ave, Chicago, IL 60625"}
FIXTURES = [
    {"name": "Luna Tacos", "address": "1000 W Chicago Ave 1st", "licenseType": "Retail Food Establishment",
     "events": [{"t": "permit", "d": "2026-05-01"}, {"t": "linsp", "d": "2026-09-08"}, {"t": "license", "d": "2026-09-10", "type": "Retail Food Establishment"},
                {"t": "routine", "d": "2026-10-15"}]},
    {"name": "New Noodle Bar", "address": "6000 N Sheridan Rd", "events": [{"t": "permit", "d": "2026-09-01"}, {"t": "linsp", "d": "2026-10-25"}]},
    {"name": "", "address": "7000 S Ashland Ave", "events": [{"t": "permit", "d": "2026-10-01"}]},
    {"name": "The Open Door Cafe", "address": "3509 S Dr Martin Luther King Jr Dr 2", "events": [{"t": "license", "d": "2026-10-20", "type": "Tavern"}]},
    {"name": "Hotel Ten", "address": "10-16 S Wabash Ave", "events": [{"t": "linsp", "d": "2026-09-10"}]},          # Sep 10 at house 10
    {"name": "Garuda", "address": "1046 1/2 W Argyle St", "events": [{"t": "license", "d": "2026-05-22", "type": "Retail Food Establishment"}]},
    {"name": "Duwells Catfish and Seafood Market and Maxwell Street BBQ", "address": "617 S Pulaski Rd 1st",
     "events": [{"t": "license", "d": "2026-10-02", "type": "Retail Food Establishment"}]},
]


def check_fixtures():
    out = []
    for b in FIXTURES:
        for t in TRADES:
            s, body, sign, stop = fill(b, t["key"], FIXTURE_ME)
            out += [f"{b['name'] or b['address']} / {t['key']}: {x}" for x in problems(s, body, sign, stop, b, t["key"], FIXTURE_ME)]
    return out


def check_live(businesses):
    """(renders, problems) over every business and every trade."""
    n, out = 0, []
    for b in businesses:
        for t in TRADES:
            s, body, sign, stop = fill(b, t["key"], FIXTURE_ME)
            n += 1
            out += [f"{b.get('id')} / {t['key']}: {x}" for x in problems(s, body, sign, stop, b, t["key"], FIXTURE_ME)]
    return n, out


def selftest():
    bad = check_fixtures()
    assert not bad, bad
    b = FIXTURES[0]
    s, body, sign, stop = fill(b, "pest", FIXTURE_ME)
    assert s == "Pest control for Luna Tacos" and "Hi Luna Tacos team," in body and "W Chicago Ave on Sep 10" in body and "1000" not in body, body
    s2, body2, _, _ = fill(FIXTURES[2], "hood", FIXTURE_ME)
    assert body2.startswith("Hi there,") and "building permit for S Ashland Ave on Oct 1." in body2 and s2 == "Hood cleaning for the new space on S Ashland Ave"
    _, body3, _, _ = fill(FIXTURES[3], "signs", FIXTURE_ME)
    assert "Dr Martin Luther King Jr Dr" in body3 and not problems(*fill(FIXTURES[3], "signs", FIXTURE_ME), FIXTURES[3], "signs", FIXTURE_ME), "a business name with 'Open' is City text, not a claim"
    assert street_of("1046 1/2 W Argyle St") == "W Argyle St" and fill(FIXTURES[6], "pos", FIXTURE_ME)[0] == "Point of sale for your space on S Pulaski Rd"
    hb = FIXTURES[4]
    s4, b4, g4, t4 = fill(hb, "pest", FIXTURE_ME)
    assert not problems(s4, b4, g4, t4, hb, "pest", FIXTURE_ME) and any("house number 10" in x for x in problems(s4, b4.replace("S Wabash", "10 S Wabash"), g4, t4, hb, "pest", FIXTURE_ME))
    planted = [  # (what to change, the problem it must raise)
        (lambda t: t.replace("Sep 10", "Sep 11"), "states 'Sep 11'"), (lambda t: t.replace("W Chicago Ave", "1000 W Chicago Ave"), "house number"),
        (lambda t: t + " We saw you failed.", "says 'failed'"), (lambda t: t.replace("?", "."), "end with a question"),
        (lambda t: t + " Visit acme.com today?", "link or domain"), (lambda t: t.replace("I'm", "I—m"), "dash"),
        (lambda t: t + " Congrats on the opening?", "says 'opening'"), (lambda t: t.replace("Luna Tacos", "[business]"), "placeholder"),
        (lambda t: t + " We also clean hoods?", "another trade"), (lambda t: t + " word" * 30, "words, the limit"),
        (lambda t: t.replace("license", "permit"), "does not name the record")]
    for change, want in planted:
        got = problems(s, change(body), sign, stop, b, "pest", FIXTURE_ME)
        assert any(want in x for x in got), (want, got)
    assert any("sales email" in x for x in problems(s, body, sign, "Thanks!", b, "pest", FIXTURE_ME))
    n, live = check_live(FIXTURES)
    assert n == len(FIXTURES) * len(TRADES) and not live
    assert all("—" not in str(t) for t in TRADES)
    print(f"radar_letters selftest ok ({len(TRADES)} trades x {len(FIXTURES)} fixtures, {len(planted) + 1} planted problems caught)")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
