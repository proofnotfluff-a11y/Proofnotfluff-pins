#!/usr/bin/env python3
"""Free Monday email and trial offer (Todd, Oct 22, 2026, 7:57 pm, live chat: the new funnel). Design and wording:
email/M1-MONDAY.md, whose Issue, Lead, Footer and Trial blocks this tool fills. Code picks the leads and checks the
copy; nothing here sends anything.

Usage:
  python3 tools/monday_email.py --city chicago [--name Dana] [--avoid lead_id,...] [--prev OLD_gc_leads.json]
      picks this week's 2 or 3 fresh leads for the city and prints the subject and body (exit 3: fewer than 2 fresh
      leads, no email this week)
  python3 tools/monday_email.py --trial --city chicago --sent-n 9 [--name Dana]
      prints the trial offer email
  python3 tools/monday_email.py --check
      renders both cities' issue and trial from the live files, gates them, and runs the planted selftest
      (check_repo runs this as its "monday" check)
  python3 tools/monday_email.py --gate data/work/monday_drafts.json
      gates a draft file (schema pnf.monday_draft.v1: {schema, drafts:[{prospect_id, to, kind, city, week, subject,
      body, lead_ids}]}) before Todd sees it
  python3 tools/monday_email.py --record --city chicago --week 2026-10-26 --leads id,id,id
      after Todd's send: appends the issue's lead ids to email/monday/sent.json (lead ids only, no people)

Freshness: a lead is fresh when its id was not in the previous edition (at least 3 days older, from git history or
--prev), when its stage moved up, or when it has a dated City signal in the last 7 days. With no earlier edition the
tool falls back to the closest-to-finish stage or a dated signal in the last 45 days, and prints that it did.
"""
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPEC = os.path.join(ROOT, "email", "M1-MONDAY.md")
GC = os.path.join(ROOT, "permits", "downstream", "gc_leads.json")
SENT = os.path.join(ROOT, "email", "monday", "sent.json")
PAGES = os.path.join(ROOT, "site", "pages.json")
CITIES = {"chicago": {"City": "Chicago", "slug": "chicago-construction-cleaning-leads", "sample": "permits/chicago/sample.json",
                      "permit_label": "Permit"},
          "austin": {"City": "Austin", "slug": "austin-construction-cleaning-leads", "sample": "permits/austin/sample.json",
                     "permit_label": "Master permit"}}
ISSUE_MAX, TRIAL_MAX = 200, 140   # words above the fixed footer, which is compliance, not copy
STAGE_RANK = {"Inspections Under Way": 1, "Final Inspection Scheduled": 2, "Certificate of Occupancy Pending": 3,
              "Partial Occupancy Approved": 4}
BANNED_ISSUE = re.compile(r"\$\s?\d+\s*(?:a|per|/)\s*mo|\btrial\b|\bsubscri\w*|\bcheckout\b|\bdiscount\b|\bpric(?:e|ing)\b", re.I)


# ------------------------------------------------------------------ templates
def spec(path=SPEC):
    """{name: (subject or '', body)} for the ### blocks in email/M1-MONDAY.md."""
    text = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r"^### (\w+)\n(.*?)(?=^### |^## |\Z)", text, re.S | re.M):
        subj = re.search(r"^Subject:\s*(.+)$", m.group(2), re.M)
        body = re.search(r"```text\n(.*?)```", m.group(2), re.S)
        if body:
            out[m.group(1)] = (subj.group(1).strip() if subj else "", body.group(1).rstrip("\n"))
    return out


def fill(t, **kw):
    return re.sub(r"\{(\w+)\}", lambda m: str(kw[m.group(1)]) if m.group(1) in kw else m.group(0), t)


# ------------------------------------------------------------------ data
def load(path):
    return json.load(open(path, encoding="utf-8"))


def page(slug):
    return next(p for p in load(PAGES)["pages"] if p.get("slug") == slug)


def gen_date(doc):
    return dt.date.fromisoformat(str(doc.get("generatedAt", ""))[:10])


def previous_edition(cur):
    """The newest committed gc_leads.json at least 3 days older than cur, or None (shallow clone, first week)."""
    try:
        revs = subprocess.run(["git", "log", "--format=%H", "--", "permits/downstream/gc_leads.json"], cwd=ROOT,
                              capture_output=True, text=True, timeout=60).stdout.split()
    except Exception:
        return None
    for rev in revs:
        r = subprocess.run(["git", "show", f"{rev}:permits/downstream/gc_leads.json"], cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            continue
        try:
            d = json.loads(r.stdout)
            if (gen_date(cur) - gen_date(d)).days >= 3:
                return d
        except (ValueError, KeyError):
            continue
    return None


def sent_ids(city, path=SENT):
    if not os.path.exists(path):
        return set()
    return {i for x in load(path).get("issues", []) if x.get("city") == city for i in x.get("lead_ids", [])}


def dated(lead):
    ds = [s["date"] for s in lead.get("signals", []) if s.get("date")]
    return max(ds) if ds else ""


def near_finish(lead):
    return lead.get("stage") == "Partial Occupancy Approved" or str(lead.get("stage_source", "")).startswith("Near finish")


def pick(leads, city, today, prev=None, sent=(), avoid=(), n=3):
    """(picks, mode) for one city: fresh leads, closest to the final clean first, one per builder."""
    mine = [x for x in leads if x.get("city") == city and x["lead_id"] not in set(sent) and x["lead_id"] not in set(avoid)]
    if prev is not None:
        old = {x["lead_id"]: x for x in prev.get("leads", [])}
        # new this week, or its stage moved up; a dated food inspection alone never makes a lead fresh (Oct 22 checker:
        # at a big building it can belong to another tenant)
        fresh = [x for x in mine if x["lead_id"] not in old
                 or STAGE_RANK.get(x["stage"], 0) > STAGE_RANK.get(old[x["lead_id"]]["stage"], 0)
                 or (near_finish(x) and not near_finish(old[x["lead_id"]]))]
        mode = "compared with the previous edition"
    else:
        fresh = list(mine)
        mode = "first edition: no earlier file to compare, so closest to finish, then size"
    # closest to the final clean, then size; a dated signal only breaks ties
    fresh.sort(key=lambda x: (near_finish(x), float(x.get("valuation") or 0), dated(x)), reverse=True)
    out, gcs = [], set()
    for x in fresh:
        g = R.gc_display(x.get("gc_company")).lower()
        if g in gcs:
            continue
        gcs.add(g)
        out.append(x)
        if len(out) == n:
            break
    return out, mode


# ------------------------------------------------------------------ rendering
def nice_date(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def stage_line(x):
    src = str(x.get("stage_source") or "")
    if x["city"] == "austin":
        if src.startswith("Near finish"):
            return "near finish, some of its building permits already finaled by the City"
        co = any(s.get("type") == "co_flag" and "=Yes" in str(s.get("detail")) for s in x.get("signals", []))
        return "work under way after City inspections" + (", certificate of occupancy required" if co else "")
    if x["stage"] == "Partial Occupancy Approved":
        return "partial occupancy approved by the City"
    if "REQUIRED" in src.upper():
        return "City inspections under way, certificate of occupancy required"
    return "City inspections under way"


def scope_line(s, limit=12):
    parts = [x.strip() for x in re.split(r"(?<=[A-Za-z0-9)])[.;](?:\s|$)", (s or "").strip().rstrip(".")) if x.strip()]
    s = next((x for x in parts if len(x.split()) >= 3), parts[0] if parts else "")   # skip City stubs like 'Incluced.'
    if s.isupper():
        s = s.capitalize()
    w = s.split()
    cut = len(w) > limit or (s or "").endswith("...")
    s = " ".join(w[:limit]).rstrip(",.:;") + ("..." if cut else "")
    return s.replace("\u2014", ",").replace("\u2013", " to ")


def lead_block(t, i, x, office=None):
    c = CITIES[x["city"]]
    b = fill(t, i=i, value=R.value_display(x.get("valuation")), work=str(x.get("work_type") or "project").lower(),
             address=x["address"], gc=R.gc_display(x.get("gc_company")), stage=stage_line(x),
             permit_label=c["permit_label"], permit=x.get("master_permit_id") or x["permit_id"].replace(" BP", ""),
             issued=nice_date(x["issue_date"]), scope=scope_line(x.get("scope")))
    extra = []
    if office:
        extra.append(f"   Builder's office: {office} (from the builder's own website)")
    return "\n".join([b] + extra)


def office_for(x):
    """The builder's verified main office line, only when the members' password is set (send time), else None."""
    if x["city"] != "chicago" or not os.environ.get("LEADS_PASSWORD"):
        return None
    try:
        import builder_contacts as B
        c = B.contact_for(x.get("gc_company") or "")
        return (c or {}).get("phone") or None
    except Exception:
        return None


def footer(sp):
    return sp["Footer"][1]


def issue(city, picks, sp=None, name="", with_office=False):
    sp = sp or spec()
    c = CITIES[city]
    total = load(os.path.join(ROOT, c["sample"]))["counts"]["kept"]
    leads = "\n\n".join(lead_block(sp["Lead"][1], i + 1, x, office_for(x) if with_office else None) for i, x in enumerate(picks))
    subj = fill(sp["Issue"][0], n=len(picks), City=c["City"])
    body = fill(sp["Issue"][1], name=(" " + name) if name else "", n=len(picks), City=c["City"], leads=leads,
                total=f"{total:,}") + "\n\n" + footer(sp)
    return subj, body


def build_issue(city, picks, sp=None, name="", with_office=False, sent=()):
    """(subject, body, picks, problems): 3 leads, or the best 2 when 3 run over the word cap."""
    sp = sp or spec()
    s, b = issue(city, picks, sp, name, with_office)
    probs = issue_problems(s, b, picks, sp, sent)
    if len(picks) == 3 and any("words, the limit" in x for x in probs):
        picks = picks[:2]
        s, b = issue(city, picks, sp, name, with_office)
        probs = issue_problems(s, b, picks, sp, sent)
    return s, b, picks, probs


def trial_link(city):
    url = page(CITIES[city]["slug"])["checkout"]
    return re.sub(r"utm_campaign=[^&]+", "utm_campaign=trial-email", url).replace("utm_medium=site", "utm_medium=email")


def trial(city, sent_n, sp=None, name=""):
    sp = sp or spec()
    c = CITIES[city]
    total = load(os.path.join(ROOT, c["sample"]))["counts"]["kept"]
    subj = fill(sp["Trial"][0], City=c["City"])
    body = fill(sp["Trial"][1], name=(" " + name) if name else "", sent_n=sent_n, City=c["City"], total=f"{total:,}",
                link=trial_link(city), price=page(c["slug"])["price"]) + "\n\n" + footer(sp)
    return subj, body


# ------------------------------------------------------------------ gate
def copy_words(body, sp):
    return len(R.words(body[:-len(footer(sp))] if body.endswith(footer(sp)) else body))


def common(subject, body, sp):
    p = []
    for d in R.DASHES:
        if d in subject or d in body:
            p.append("an em or en dash")
    if re.search(r"[{}\[\]<>]", subject + body):
        p.append("a leftover placeholder bracket")
    if not body.endswith(footer(sp)):
        p.append("the footer is missing or changed (mailing address and stop line, byte for byte)")
    if 'Reply "stop"' not in footer(sp) or "said yes" not in footer(sp):
        p.append("the footer must say why they get it and how to stop (Reply \"stop\")")
    addr = R.FOOTER.split("\n")[1]
    if addr not in body:
        p.append("the mailing address is not the one in pnf_rules.FOOTER")
    if not re.match(r"^Hi(?: [A-Z][\w'-]*)?,\n", body):
        p.append("body must open 'Hi <first name>,' or 'Hi,'")
    try:
        import voice_lint
        p += [f"AI-sounding phrase ({w.strip()!r})" for _, w in voice_lint.tells(subject + "\n" + body)]
    except ImportError:
        pass
    return p


def issue_problems(subject, body, picks, sp, sent=()):
    p = common(subject, body, sp)
    n = copy_words(body, sp)
    if n >= ISSUE_MAX:
        p.append(f"issue is {n} words, the limit is under {ISSUE_MAX}")
    m = R.URL_RE.search(R.link_safe(body) if hasattr(R, "link_safe") else body)
    if m:
        p.append(f"issue carries a link ({m.group(0)!r}); the Monday email has none")
    m = BANNED_ISSUE.search(subject + "\n" + body)
    if m:
        p.append(f"issue talks price or trial ({m.group(0)!r}); the offer comes only after the third Monday")
    if not 2 <= len(picks) <= 3:
        p.append(f"issue has {len(picks)} leads, it needs 2 or 3")
    if len(re.findall(r"^\d\. ", body, re.M)) != len(picks):
        p.append("the numbered lead blocks do not match the picked leads")
    gcs = [R.gc_display(x.get("gc_company")).lower() for x in picks]
    if len(set(gcs)) != len(gcs):
        p.append("two leads from the same builder")
    for x in picks:
        if x["lead_id"] in set(sent):
            p.append(f"{x['lead_id']} was already sent in an earlier issue")
        for want in (R.value_display(x.get("valuation")), x["address"], R.gc_display(x.get("gc_company"))):
            if want not in body:
                p.append(f"{x['lead_id']}: {want!r} missing from the body")
        c = CITIES[x["city"]]
        for want, what in ((f'{c["permit_label"]} {x.get("master_permit_id") or x["permit_id"].replace(" BP", "")}, issued {nice_date(x["issue_date"])}', "permit and issue date"),
                           (f"Stage: {stage_line(x)}", "stage")):
            if want not in body:
                p.append(f"{x['lead_id']}: {what} do not match the City record ({want!r} missing)")
        if x.get("site_contact"):
            p.append(f"{x['lead_id']}: carries a site contact (a person); leads are business fields only")
    for v in re.findall(r"\$\d+(?:\.\d+)?[MB]\b", body):
        if v not in {R.value_display(x.get("valuation")) for x in picks}:
            p.append(f"body states {v}, which is no picked lead's valuation")
    return p


def trial_problems(subject, body, city, sp):
    p = common(subject, body, sp)
    n = copy_words(body, sp)
    if n >= TRIAL_MAX:
        p.append(f"trial email is {n} words, the limit is under {TRIAL_MAX}")
    links = re.findall(r"https?://\S+", body)
    if links != [trial_link(city)]:
        p.append(f"trial email needs exactly one link, the product's Gumroad checkout ({len(links)} found)")
    price = page(CITIES[city]["slug"])["price"]
    for want, why in ((f"${price} a month", "the monthly price"), ("7 days", "the trial length"), ("card", "that the card goes in at signup"),
                      ("Cancel", "how to cancel"), ("charges nothing", "that nothing is charged at signup"), ("offer", "that it is an offer")):
        if want not in body:
            p.append(f"trial email does not state {why} ({want!r})")
    return p


# ------------------------------------------------------------------ selftest
def selftest(sp, leads, today):
    cases, ok = [], 0
    picks, _ = pick(leads, "chicago", today)
    if len(picks) < 2:
        return ["selftest: fewer than 2 Chicago picks in the live file, cannot plant"], 0, 0
    s, b = issue("chicago", picks, sp, name="Dana")
    t_s, t_b = trial("chicago", 9, sp, name="Dana")
    plant = [
        ("issue: an em dash", lambda: issue_problems(s, b.replace("Builder:", "Builder \u2014", 1), picks, sp)),
        ("issue: a link", lambda: issue_problems(s, b.replace("To use one:", "See proofnotfluff.com. To use one:"), picks, sp)),
        ("issue: price talk", lambda: issue_problems(s, b.replace("every Monday.", "every Monday for $29 a month."), picks, sp)),
        ("issue: free trial mention", lambda: issue_problems(s, b.replace("To use one:", "Start a free trial. To use one:"), picks, sp)),
        ("issue: footer stop line removed", lambda: issue_problems(s, b.replace('Reply "stop" and you won\'t get another one.', ""), picks, sp)),
        ("issue: mailing address changed", lambda: issue_problems(s, b.replace("Suite 110-2964", "Suite 110"), picks, sp)),
        ("issue: one lead only", lambda: issue_problems(s, b, picks[:1], sp)),
        ("issue: wrong valuation", lambda: issue_problems(s, b.replace(R.value_display(picks[0]["valuation"]), "$99M", 1), picks, sp)),
        ("issue: lead already sent", lambda: issue_problems(s, b, picks, sp, sent={picks[0]["lead_id"]})),
        ("issue: same builder twice", lambda: issue_problems(s, b, [picks[0], dict(picks[1], gc_company=picks[0]["gc_company"])] + picks[2:], sp)),
        ("issue: wrong permit number", lambda: issue_problems(s, b.replace(picks[0]["permit_id"], "100000001", 1), picks, sp)),
        ("issue: wrong stage", lambda: issue_problems(s, b.replace("Stage: " + stage_line(picks[0]), "Stage: permit issued"), picks, sp)),
        ("issue: a person as site contact", lambda: issue_problems(s, b, [dict(picks[0], site_contact={"name": "x"})] + picks[1:], sp)),
        ("issue: over the word cap", lambda: issue_problems(s, b.replace("To use one:", " ".join(["word"] * 240) + " To use one:"), picks, sp)),
        ("issue: AI phrase", lambda: issue_problems(s, b.replace("To use one:", "This is a game changer. To use one:"), picks, sp)),
        ("issue: no greeting", lambda: issue_problems(s, b.replace("Hi Dana,", "Hello there", 1), picks, sp)),
        ("trial: no price", lambda: trial_problems(t_s, t_b.replace("$29 a month", "monthly"), "chicago", sp)),
        ("trial: no link", lambda: trial_problems(t_s, t_b.replace(trial_link("chicago"), ""), "chicago", sp)),
        ("trial: a second link", lambda: trial_problems(t_s, t_b.replace("either way.", "either way. https://proofnotfluff.com/"), "chicago", sp)),
        ("trial: card line removed", lambda: trial_problems(t_s, t_b.replace("asks for your card when you start and ", ""), "chicago", sp)),
        ("trial: cancel line removed", lambda: trial_problems(t_s, re.sub(r"Cancel in your Gumroad.*?nothing\.", "", t_b), "chicago", sp)),
        ("trial: not marked as an offer", lambda: trial_problems(t_s, t_b.replace("This one is an offer, so skip it if the free email is enough. ", ""), "chicago", sp)),
    ]
    expect = {"an em dash": "dash", "a link": "link", "price talk": "price or trial", "free trial mention": "price or trial",
              "footer stop line removed": "footer", "mailing address changed": "mailing address", "one lead only": "needs 2 or 3",
              "wrong valuation": "valuation", "lead already sent": "already sent", "same builder twice": "same builder",
              "a person as site contact": "site contact", "over the word cap": "words, the limit", "AI phrase": "AI-sounding",
              "no greeting": "must open", "wrong permit number": "permit and issue date", "wrong stage": "stage do not match",
              "no price": "monthly price", "no link": "exactly one link", "a second link": "exactly one link",
              "card line removed": "card goes in", "cancel line removed": "how to cancel", "not marked as an offer": "an offer"}
    for label, fn in plant:
        got = fn()
        want = expect[label.split(": ", 1)[1]]
        if any(want in g for g in got):
            ok += 1
        else:
            cases.append(f"selftest: planted '{label}' was not caught by its own rule ({want!r})")
    if issue_problems(s, b, picks, sp) or trial_problems(t_s, t_b, "chicago", sp):
        cases.append("selftest: the clean render fails its own gate")
    return cases, ok, len(plant)


# ------------------------------------------------------------------ CLI
def run_check():
    sp = spec()
    for k in ("Issue", "Lead", "Footer", "Trial"):
        if k not in sp:
            print(f"ERROR monday: email/M1-MONDAY.md has no {k} block")
            return 1
    cur = load(GC)
    today = gen_date(cur)
    prev = previous_edition(cur)
    probs, lines = [], []
    for city in CITIES:
        picks, mode = pick(cur["leads"], city, today, prev, sent_ids(city))
        if len(picks) < 2:
            lines.append(f"{city}: {len(picks)} fresh leads, no issue this week ({mode})")
        else:
            s, b, picks, ip = build_issue(city, picks, sp, sent=sent_ids(city))
            probs += [f"{city} issue: {x}" for x in ip]
            lines.append(f"{city}: {len(picks)} leads, {copy_words(b, sp)} words ({mode.split(':')[0]})")
        ts, tb = trial(city, 9)
        probs += [f"{city} trial: {x}" for x in trial_problems(ts, tb, city, sp)]
    bad, ok, n = selftest(sp, cur["leads"], today)
    probs += bad
    caught = f"{ok} of {n} planted cases caught"
    if probs:
        print("ERROR monday: " + "; ".join(probs)[:900])
        return 1
    print(f"OK monday ({'; '.join(lines)}; trial emails pass; {caught})")
    return 0


def run_gate(path):
    sp, doc = spec(), load(path)
    leads = {x["lead_id"]: x for x in load(GC)["leads"]}
    rows = doc.get("drafts") if isinstance(doc, dict) else None
    if not isinstance(doc, dict) or doc.get("schema") != "pnf.monday_draft.v1" or not isinstance(rows, list):
        print("ERROR monday-gate: schema must be pnf.monday_draft.v1 with a drafts list")
        return 1
    probs = []
    for d in rows:
        pid, kind, city = d.get("prospect_id"), d.get("kind"), d.get("city")
        if city not in CITIES or kind not in ("issue", "trial"):
            probs.append(f"{pid}: city and kind must be one of {sorted(CITIES)} and issue or trial")
            continue
        if kind == "issue":
            picks = [leads[i] for i in d.get("lead_ids", []) if i in leads]
            if len(picks) != len(d.get("lead_ids", [])):
                probs.append(f"{pid}: a lead id is not in the live file")
            probs += [f"{pid}: {x}" for x in issue_problems(d.get("subject", ""), d.get("body", ""), picks, sp, sent_ids(city))]
        else:
            probs += [f"{pid}: {x}" for x in trial_problems(d.get("subject", ""), d.get("body", ""), city, sp)]
    for x in probs:
        print("ERROR", x)
    print(f"monday-gate: {len(rows)} drafts, {len(probs)} problem{'s' if len(probs) != 1 else ''}")
    return 1 if probs else 0


def run_record(city, week, ids):
    doc = load(SENT) if os.path.exists(SENT) else {"schema": "pnf.monday_sent.v1", "issues": []}
    if any(x["city"] == city and x["week"] == week for x in doc["issues"]):
        print(f"ERROR record: {city} {week} is already recorded")
        return 1
    doc["issues"].append({"city": city, "week": week, "lead_ids": ids})
    os.makedirs(os.path.dirname(SENT), exist_ok=True)
    json.dump(doc, open(SENT, "w", encoding="utf-8"), indent=1)
    print(f"recorded {city} {week}: {len(ids)} leads")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--city", choices=sorted(CITIES))
    ap.add_argument("--name", default="")
    ap.add_argument("--avoid", default="")
    ap.add_argument("--prev")
    ap.add_argument("--require-prev", action="store_true", help="a real Monday run: exit 4 when no earlier edition is found")
    ap.add_argument("--trial", action="store_true")
    ap.add_argument("--sent-n", type=int, default=0)
    ap.add_argument("--office", action="store_true", help="add verified builder office lines (send time, needs LEADS_PASSWORD)")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--gate")
    ap.add_argument("--record", action="store_true")
    ap.add_argument("--week")
    ap.add_argument("--leads", default="")
    a = ap.parse_args()
    if a.check:
        sys.exit(run_check())
    if a.gate:
        sys.exit(run_gate(a.gate))
    if a.record:
        sys.exit(run_record(a.city, a.week, [x for x in a.leads.split(",") if x]))
    if not a.city:
        ap.error("--city is required")
    sp = spec()
    if a.trial:
        s, b = trial(a.city, a.sent_n, sp, a.name)
        probs = trial_problems(s, b, a.city, sp)
    else:
        cur = load(GC)
        prev = load(a.prev) if a.prev else previous_edition(cur)
        if prev is None and a.require_prev:
            print("# no earlier edition found (shallow clone?): run git fetch --depth=50 origin main or pass --prev", file=sys.stderr)
            sys.exit(4)
        picks, mode = pick(cur["leads"], a.city, gen_date(cur), prev, sent_ids(a.city), [x for x in a.avoid.split(",") if x])
        print(f"# {mode}; data {cur['generatedAt']}; leads {', '.join(x['lead_id'] for x in picks)}", file=sys.stderr)
        if len(picks) < 2:
            print(f"# {len(picks)} fresh leads: no Monday email for {a.city} this week", file=sys.stderr)
            sys.exit(3)
        s, b, picks, probs = build_issue(a.city, picks, sp, a.name, a.office, sent_ids(a.city))
    print(f"Subject: {s}\n\n{b}")
    for x in probs:
        print("ERROR", x, file=sys.stderr)
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
