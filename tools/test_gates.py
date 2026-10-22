#!/usr/bin/env python3
"""Planted failures for the four downstream-pipeline gates (Context, Timing Moat, Two-Entity Schema and Inbox, Outreach
Copy). Every planted bad case must be caught and every planted good case must pass, or this exits 1. tools/check_repo.py
runs it as the gate-selftest check, so a gate that silently stops catching something turns the code gate red.

Usage: python3 tools/test_gates.py
"""
import copy
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pnf_rules as R  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
results = []


def expect(name, problems, should_fail):
    caught = bool(problems)
    results.append((name, caught == should_fail, problems[:1]))


LEAD = {"lead_id": "chi-1", "city": "chicago", "permit_id": "1", "stage": "Partial Occupancy Approved",
        "stage_source": "CERTIFICATE OF OCCUPANCY PENDING (TEMPORARY OR PARTIAL OCCUPANCY APPROVED)", "issue_date": "2026-03-02",
        "address": "4100 N Hampton Dr", "address_key": "4100 N HAMPTON DR", "valuation": 45000000, "gc_company": "Bartlett Cocke, LLC",
        "signals": [{"type": "co_pending", "dataset": "ydr8-5enu", "record_id": "9", "date": None, "detail": "x"}],
        "source_url": "https://example.invalid/x", "site_contact": None, "scope": "New school building"}
PROSPECT = {"prospect_id": "cc-sparkleco-example", "product": "chicago-construction", "business": "Sparkle Co", "website_domain": "sparkleco.example",
            "city": "chicago", "first_name": "Dana", "last_name": "Reyes", "title": "Owner", "email": "dana@sparkleco.example",
            "email_source": "apollo", "email_status": "verified", "do_not_email": False}
BODY = ("Hi Dana,\n\nNoticed Bartlett Cocke is at partial occupancy approved on the $45M school build on N Hampton Dr. "
        "That is usually when the final clean gets bid.\n\n"
        "Mind if I send over the general contractor's direct contact details?")
SUBJECT = "Bartlett Cocke on N Hampton Dr"


def moat_cases():
    expect("moat: good downstream lead passes", R.validate_gc_lead(LEAD), False)
    expect("moat: upstream permit issued fails", R.validate_gc_lead(dict(LEAD, stage="Permit Issued", stage_source="PERMIT ISSUED (FEE DUE)")), True)
    expect("moat: austin permit issued fails", R.validate_gc_lead(dict(LEAD, city="austin", stage="Inspections Under Way", stage_source="Permit issued")), True)
    expect("moat: no adjacent signal fails", R.validate_gc_lead(dict(LEAD, signals=[])), True)
    expect("moat: unknown signal type fails", R.validate_gc_lead(dict(LEAD, signals=[{"type": "rumor", "dataset": "x", "record_id": "1"}])), True)
    expect("moat: CO issued (past handover) fails", R.validate_gc_lead(dict(LEAD, stage_source="CERTIFICATE OF OCCUPANCY ISSUED")), True)
    expect("moat: groundbreaking scope fails", R.validate_gc_lead(dict(LEAD, scope="Crews broke ground in May")), True)
    expect("moat: under 500k fails", R.validate_gc_lead(dict(LEAD, valuation=250000)), True)
    expect("moat: phone in scope fails", R.validate_gc_lead(dict(LEAD, scope="call 312-555-0100")), True)
    expect("moat: site contact in public file fails", R.validate_gc_lead(dict(LEAD, site_contact={"name": "A Person"})), True)
    expect("moat: file with stale generatedAt fails",
           R.validate_gc_file({"schema": "pnf.gc_lead.v1", "generatedAt": "2026-01-01T00:00:00Z", "leads": [LEAD]}, max_age_days=8), True)


def inbox_cases():
    expect("inbox: named work email passes", R.validate_prospect(PROSPECT), False)
    for local in ("info", "contact", "sales", "admin", "office", "dispatch", "estimating", "bids", "support", "hello", "info.chicago", "office2"):
        expect(f"inbox: {local}@ fails", R.validate_prospect(dict(PROSPECT, email=f"{local}@sparkleco.example")), True)
    for local in ("infoteam", "contactus", "salesteam", "officemanager", "frontoffice", "customercare", "inquiry", "projects", "sam"):
        expect(f"inbox: {local}@ fails", R.validate_prospect(dict(PROSPECT, email=f"{local}@sparkleco.example")), True)
    for local in ("dreyes", "dana.reyes", "reyes", "danar"):
        expect(f"inbox: {local}@ passes", R.validate_prospect(dict(PROSPECT, email=f"{local}@sparkleco.example")), False)
    expect("inbox: Crew Manager title fails", R.validate_prospect(dict(PROSPECT, title="Crew Manager")), True)
    expect("moat: zero-lead file fails", R.validate_gc_file({"schema": "pnf.gc_lead.v1", "generatedAt": "2026-10-20T12:00:00Z", "leads": []}), True)
    expect("moat: future generatedAt fails", R.validate_gc_file({"schema": "pnf.gc_lead.v1", "generatedAt": "2099-01-01T00:00:00Z", "leads": [LEAD]}, max_age_days=8), True)
    expect("inbox: free mail fails", R.validate_prospect(dict(PROSPECT, email="dana.reyes@gmail.com")), True)
    expect("inbox: other domain fails", R.validate_prospect(dict(PROSPECT, email="dana@othersite.example")), True)
    expect("inbox: non decision-maker title fails", R.validate_prospect(dict(PROSPECT, title="Cleaner")), True)
    expect("inbox: undeliverable status fails", R.validate_prospect(dict(PROSPECT, email_status="invalid")), True)
    expect("inbox: missing first name fails", R.validate_prospect(dict(PROSPECT, first_name="")), True)
    expect("inbox: wrong city for product fails", R.validate_prospect(dict(PROSPECT, city="austin")), True)
    expect("inbox: do-not-email fails", R.validate_prospect(dict(PROSPECT, do_not_email=True)), True)
    two = [PROSPECT, dict(PROSPECT, prospect_id="cc-2", email="sam@sparkleco.example", first_name="Sam")]
    expect("inbox: two contacts at one business fails", R.validate_prospect_file({"schema": "pnf.prospect.v1", "prospects": two}), True)
    many = [dict(PROSPECT, prospect_id=f"cc-{i}", website_domain=f"b{i}.example", email=f"dana@b{i}.example",
                 email_status="accept_all" if i < 2 else "verified") for i in range(10)]
    expect("inbox: catch-all over 10% fails", R.validate_prospect_file({"schema": "pnf.prospect.v1", "prospects": many}), True)
    expect("schema: GC lead file rejected as prospect file", R.validate_prospect_file({"schema": "pnf.gc_lead.v1", "leads": [LEAD]}), True)
    expect("schema: prospect file rejected as GC lead file", R.validate_gc_file({"schema": "pnf.prospect.v1", "prospects": [PROSPECT]}), True)


def copy_cases():
    ok = R.copy_problems(SUBJECT, BODY, "Dana", LEAD)
    expect("copy: target example passes", ok, False)
    long_body = "Hi Dana,\n\n" + " ".join(["word"] * 70) + " Bartlett Cocke partial occupancy approved, mind if I send it?"
    expect("copy: 75 words or more fails", R.copy_problems(SUBJECT, long_body, "Dana", LEAD), True)
    for bad in ("http://x.example", "https://x.example", "www.example", "proofnotfluff.com", "gumroad", "Gumroad link"):
        expect(f"copy: {bad!r} fails", R.copy_problems(SUBJECT, BODY.replace("Mind if", f"See {bad}. Mind if"), "Dana", LEAD), True)
    expect("copy: link in subject fails", R.copy_problems("See proofnotfluff.com", BODY, "Dana", LEAD), True)
    for bad in ("broke ground", "breaking ground"):
        expect(f"copy: {bad!r} fails", R.copy_problems(SUBJECT, BODY.replace("is at", f"{bad} and is at"), "Dana", LEAD), True)
    expect("copy: subscription pitch fails", R.copy_problems(SUBJECT, BODY.replace("Mind if", "It is $29 a month. Mind if"), "Dana", LEAD), True)
    expect("copy: em dash fails", R.copy_problems(SUBJECT, BODY.replace(". That", " \u2014 That"), "Dana", LEAD), True)
    expect("copy: generic greeting fails", R.copy_problems(SUBJECT, BODY.replace("Hi Dana,", "Hi Sparkle Co team,"), "Dana", LEAD), True)
    expect("copy: no permission question fails", R.copy_problems(SUBJECT, BODY.rstrip("?") + ".", "Dana", LEAD), True)
    expect("copy: missing GC fails", R.copy_problems(SUBJECT, BODY.replace("Bartlett Cocke", "the builder"), "Dana", LEAD), True)
    expect("copy: missing stage fails", R.copy_problems(SUBJECT, BODY.replace("partial occupancy approved", "progress"), "Dana", LEAD), True)
    expect("copy: wrong valuation fails", R.copy_problems(SUBJECT, BODY.replace("$45M", "$90M"), "Dana", LEAD), True)
    expect("copy: wrong street fails", R.copy_problems(SUBJECT, BODY.replace("N Hampton Dr", "S Fake St"), "Dana", LEAD), True)
    for bad in ("proofnotfluff dot com", "acme.ai", "leads.app", "acme.biz", "pnf.info", "proofnotfluff . com"):
        expect(f"copy: {bad!r} fails", R.copy_problems(SUBJECT, BODY.replace("Mind if", f"See {bad}. Mind if"), "Dana", LEAD), True)
    expect("copy: 'Inc. in' is not a link", R.copy_problems(SUBJECT, BODY.replace("That is", "Cocke Inc. in town. That is"), "Dana", LEAD), False)
    for name in ("Henry Bros.Co.", "Acme L.L.C.", "Dunn Co. Inc.", "Ace Corp."):
        lead = dict(LEAD, gc_company=name)
        body = BODY.replace("Bartlett Cocke", R.gc_display(name))
        expect(f"copy: GC name {name!r} is not a link", R.copy_problems(SUBJECT, body, "Dana", lead), False)
    bg = dict(LEAD, gc_company="Breaking Ground Contractors Inc")
    expect("copy: a builder named Breaking Ground is not an upstream phrase",
           R.copy_problems(SUBJECT, BODY.replace("Bartlett Cocke", "Breaking Ground Contractors"), "Dana", bg), False)
    expect("copy: 'acme.co' still fails", R.copy_problems(SUBJECT, BODY.replace("Mind if", "See acme.co. Mind if"), "Dana", LEAD), True)
    expect("copy: 'St.com' style still fails", R.copy_problems(SUBJECT, BODY.replace("Mind if", "See main.net now. Mind if"), "Dana", LEAD), True)
    expect("street display drops building and unit passes",
           [] if R.street_display("8201 E Riverside Dr Bldg 6 Unit 650") == "E Riverside Dr" else ["wrong street"], False)
    expect("copy: leftover brace fails", R.copy_problems(SUBJECT, BODY.replace("Dana,\n", "Dana,\n{street} "), "Dana", LEAD), True)
    drafts = {"schema": "pnf.draft.v1", "drafts": [{"prospect_id": PROSPECT["prospect_id"], "lead_id": "chi-1", "to": "info@sparkleco.example",
                                                    "subject": SUBJECT, "body": BODY}]}
    expect("copy: draft to a role inbox fails", R.validate_drafts(drafts, {"chi-1": LEAD}, {PROSPECT["prospect_id"]: PROSPECT}), True)
    good = copy.deepcopy(drafts)
    good["drafts"][0]["to"] = PROSPECT["email"]
    expect("copy: valid draft file passes", R.validate_drafts(good, {"chi-1": LEAD}, {PROSPECT["prospect_id"]: PROSPECT}), False)
    dup = copy.deepcopy(good)
    dup["drafts"].append(dup["drafts"][0])
    expect("copy: two drafts to one prospect fail", R.validate_drafts(dup, {"chi-1": LEAD}, {PROSPECT["prospect_id"]: PROSPECT}), True)
    expect("copy: draft off its validated match fails",
           R.validate_drafts(good, {"chi-1": LEAD}, {PROSPECT["prospect_id"]: PROSPECT}, {PROSPECT["prospect_id"]: "chi-9"}), True)


def context_cases():
    """Runs tools/context_gate.py on a throwaway copy of the live layers with one planted change each."""
    def run(mutate):
        tmp = tempfile.mkdtemp(prefix="pnf-ctx-")
        try:
            os.makedirs(os.path.join(tmp, "tools"))
            os.makedirs(os.path.join(tmp, "coo"))
            shutil.copy(os.path.join(ROOT, "tools", "context_gate.py"), os.path.join(tmp, "tools"))
            shutil.copy(os.path.join(ROOT, "CLAUDE.md"), tmp)
            shutil.copy(os.path.join(ROOT, "coo", "HANDOFF.md"), os.path.join(tmp, "coo"))
            shutil.copytree(os.path.join(ROOT, ".claude", "skills"), os.path.join(tmp, ".claude", "skills"))
            mutate(tmp)
            r = subprocess.run([sys.executable, os.path.join(tmp, "tools", "context_gate.py")], capture_output=True, text=True)
            return [l for l in r.stdout.splitlines() if l.startswith("ERROR")] or ([] if r.returncode == 0 else ["exit 1"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def append(rel, text):
        def f(tmp):
            with open(os.path.join(tmp, rel), "a", encoding="utf-8") as fh:
                fh.write(text)
        return f

    def legacy_file(tmp):
        os.makedirs(os.path.join(tmp, "areas"))
        open(os.path.join(tmp, "areas", "digital-products-plan.md"), "w").write("old ledger\n")

    def drop_section(tmp):
        p = os.path.join(tmp, ".claude", "skills", "outreach-drafter", "SKILL.md")
        open(p, "w", encoding="utf-8").write(open(p, encoding="utf-8").read().replace("## Outputs (Writes)", "## Outputs"))

    def budget(tmp):
        # the per-file caps alone keep the sum near 9.2 KB, so the budget check is planted with oversized layers and
        # this case passes only when the budget line itself is reported
        append("coo/HANDOFF.md", "y" * 3000)(tmp)
        append("CLAUDE.md", "z" * 3000)(tmp)

    expect("context: live layers pass", run(lambda t: None), False)
    expect("context: CLAUDE.md over 2 KB fails", run(append("CLAUDE.md", "x" * 2100)), True)
    expect("context: HANDOFF.md over 2 KB fails", run(append("coo/HANDOFF.md", "x" * 2100)), True)
    expect("context: SKILL.md over 5 KB fails", run(append(".claude/skills/permit-ingestion/SKILL.md", "x" * 5200)), True)
    expect("context: missing Outputs section fails", run(drop_section), True)
    expect("context: legacy ledger file in an active path fails", run(legacy_file), True)
    expect("context: active layer reading the legacy ledger fails", run(append("CLAUDE.md", "\nRead /areas/digital-products.md first.\n")), True)
    expect("context: em dash in a layer fails", run(append("coo/HANDOFF.md", "\nlive \u2014 state\n")), True)
    expect("context: L0 + L1 + one skill over 10 KB fails", [l for l in run(budget) if "the budget is under 10240" in l], True)


def legacy_cases():
    import crm_prospects as CP
    expect("legacy: Oct 19 batch blocked", [] if CP.legacy_batch({"batch": "2026-10-19"}) else ["not blocked"], False)
    expect("legacy: Oct 20 first send blocked", [] if CP.legacy_batch({"firstSentAt": "2026-10-20T14:02:00Z"}) else ["not blocked"], False)
    expect("legacy: a later batch is not blocked", ["blocked"] if CP.legacy_batch({"batch": "2026-10-26"}) else [], False)


def trade_cases():
    """Trade verticals (Todd, Oct 22): exterior_turnkey gets only Chicago Partial Occupancy Approved leads, every vertical
    needs a template that passes the copy gate, and a record with no vertical is commercial_cleaning."""
    import copy_gate as CG
    import enrich_ci as EC
    ext = dict(PROSPECT, prospect_id="cc-washco-example", website_domain="washco.example", email="dana@washco.example",
               trade_vertical="exterior_turnkey")
    insp = dict(LEAD, lead_id="chi-2", stage="Inspections Under Way", stage_source="INSPECTIONS")
    aus = dict(LEAD, lead_id="aus-1", city="austin", stage="Inspections Under Way", stage_source="Near finish")
    expect("trade: exterior_turnkey Chicago prospect passes", R.validate_prospect(ext), False)
    expect("trade: record with no vertical is commercial_cleaning and passes",
           [] if R.trade_of(PROSPECT) == "commercial_cleaning" and not R.validate_prospect(PROSPECT) else ["not default"], False)
    expect("trade: unknown vertical fails", R.validate_prospect(dict(ext, trade_vertical="locksmith")), True)
    expect("trade: exterior_turnkey on Austin fails", R.validate_prospect(dict(ext, product="austin-construction", city="austin")), True)
    expect("trade: exterior_turnkey on the restaurant product fails", R.validate_prospect(dict(ext, product="chicago-restaurant")), True)
    leads = {"chi-1": LEAD, "chi-2": insp, "aus-1": aus}
    pros = {ext["prospect_id"]: ext, PROSPECT["prospect_id"]: PROSPECT}
    m = lambda pid, lid: {"schema": "pnf.match.v1", "matches": [{"prospect_id": pid, "lead_id": lid, "reason": "x"}]}
    expect("trade: exterior match to Partial Occupancy Approved passes", R.validate_matches(m(ext["prospect_id"], "chi-1"), leads, pros), False)
    expect("trade: exterior match to Inspections Under Way fails", R.validate_matches(m(ext["prospect_id"], "chi-2"), leads, pros), True)
    expect("trade: cleaning match to Inspections Under Way passes", R.validate_matches(m(PROSPECT["prospect_id"], "chi-2"), leads, pros), False)

    ts = {(tr, st): (s, b) for _n, s, b, st, tr in CG.templates(CG.TEMPLATES)}
    s, b = ts.get(("exterior_turnkey", "Partial Occupancy Approved"), ("", ""))
    fields = dict(CG.FIXTURE_FIELDS, first="Dana", gc="Bartlett Cocke", value="$45M", kind="school", street="N Hampton Dr")
    subj, body = CG.fill(s, fields), CG.fill(b, fields)
    expect("trade: exterior template renders and passes the copy gate",
           R.copy_problems(subj, body, "Dana", LEAD) if body else ["no exterior template"], False)
    expect("trade: live templates file passes", CG.check_templates(CG.TEMPLATES)[0], False)
    draft = lambda lid, bd: {"schema": "pnf.draft.v1", "drafts": [{"prospect_id": ext["prospect_id"], "lead_id": lid, "to": ext["email"],
                                                                   "subject": subj, "body": bd}]}
    expect("trade: exterior draft on its Partial Occupancy lead passes", R.validate_drafts(draft("chi-1", body), leads, pros), False)
    expect("trade: exterior draft on an Inspections lead fails", R.validate_drafts(draft("chi-2", body), leads, pros), True)
    expect("trade: exterior draft with a link fails",
           R.validate_drafts(draft("chi-1", body.replace("Want the", "See washco.com. Want the")), leads, pros), True)
    expect("trade: exterior draft at 75 words fails",
           R.validate_drafts(draft("chi-1", body.replace("Want the", " ".join(["more"] * 40) + " Want the")), leads, pros), True)
    expect("trade: exterior draft to a role inbox fails",
           R.validate_drafts({"schema": "pnf.draft.v1", "drafts": [dict(draft("chi-1", body)["drafts"][0], to="info@washco.example")]},
                             leads, {ext["prospect_id"]: dict(ext, email="info@washco.example")}), True)
    expect("trade: exterior draft with a generic greeting fails",
           R.validate_drafts(draft("chi-1", body.replace("Hi Dana,", "Hi there,")), leads, pros), True)

    def planted(fn):
        tmp = tempfile.mkdtemp(prefix="pnf-trade-")
        try:
            path = os.path.join(tmp, "templates.md")
            open(path, "w", encoding="utf-8").write(fn(open(CG.TEMPLATES, encoding="utf-8").read()))
            return CG.check_templates(path)[0]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    head = "### T4 exterior turnkey"
    expect("trade: a vertical with no template fails", planted(lambda x: x[:x.index(head)]), True)
    expect("trade: exterior template on Inspections Under Way fails",
           planted(lambda x: x.replace("Trade: exterior_turnkey\nStage: Partial Occupancy Approved", "Trade: exterior_turnkey\nStage: Inspections Under Way")), True)
    expect("trade: template with an unknown Trade fails", planted(lambda x: x.replace("Trade: exterior_turnkey", "Trade: locksmith")), True)
    expect("trade: second template for one vertical and stage fails", planted(lambda x: x + "\n" + x[x.index(head):]), True)
    expect("trade: exterior template over 75 words fails",
           planted(lambda x: x.replace("before final sign-off.", "before final sign-off. " + " ".join(["more"] * 40))), True)

    biz = lambda **k: {"schema": "pnf.business.v1", "businesses": [dict({"prospect_id": "cc-washco-example", "product": "chicago-construction",
                                                                         "business": "Wash Co", "website": "washco.example"}, **k)]}
    expect("trade: business row with exterior_turnkey passes", EC.validate_businesses(biz(trade_vertical="exterior_turnkey")), False)
    expect("trade: business row with an unknown vertical fails", EC.validate_businesses(biz(trade_vertical="locksmith")), True)
    expect("trade: Austin business row with exterior_turnkey fails",
           EC.validate_businesses(biz(product="austin-construction", trade_vertical="exterior_turnkey")), True)


def ladder_cases():
    """Enrichment ladder (Todd, Oct 22, 2026): the owner-read inbox exception is narrow, and pending means unverified."""
    city = dict(PROSPECT, email="info@sparkleco.example", email_source="site", owner_source="city_owner_record")
    expect("ladder: info@ for a City-named owner, published on the site, passes", R.validate_prospect(city), False)
    expect("ladder: office@ for an owner named on the business's own site passes",
           R.validate_prospect(dict(city, email="office@sparkleco.example", owner_source="site_about")), False)
    expect("ladder: info@ for a Hunter-named owner fails", R.validate_prospect(dict(city, owner_source="hunter")), True)
    expect("ladder: info@ not published on the site fails", R.validate_prospect(dict(city, email_source="hunter")), True)
    expect("ladder: info@ with no owner source fails", R.validate_prospect(dict(city, owner_source="")), True)
    for local in ("jobs", "careers", "billing", "noreply", "estimating"):
        expect(f"ladder: {local}@ fails even for a City-named owner", R.validate_prospect(dict(city, email=f"{local}@sparkleco.example")), True)
    expect("ladder: info@ on free mail fails", R.validate_prospect(dict(city, email="info@gmail.com")), True)
    expect("ladder: unknown owner source fails", R.validate_prospect(dict(PROSPECT, owner_source="guess")), True)
    pend = dict(city, email_status="unverified")
    expect("ladder: unverified address passes as pending", R.validate_prospect(pend, pending=True), False)
    expect("ladder: unverified address fails as ready", R.validate_prospect(pend), True)
    expect("ladder: verified address fails as pending", R.validate_prospect(city, pending=True), True)
    two = {"schema": "pnf.prospect.v1", "prospects": [PROSPECT], "pending": [dict(pend, prospect_id="cc-x")]}
    expect("ladder: pending second contact at a business fails", R.validate_prospect_file(two), True)
    d = lambda pr: {"schema": "pnf.draft.v1", "drafts": [{"prospect_id": pr["prospect_id"], "lead_id": "chi-1", "to": pr["email"],
                                                         "subject": SUBJECT, "body": BODY}]}
    expect("ladder: draft to info@ for a City-named owner passes", R.validate_drafts(d(city), {"chi-1": LEAD}, {city["prospect_id"]: city}), False)
    hun = dict(city, owner_source="hunter")
    expect("ladder: draft to info@ for a Hunter-named owner fails", R.validate_drafts(d(hun), {"chi-1": LEAD}, {hun["prospect_id"]: hun}), True)


def main():
    moat_cases()
    inbox_cases()
    copy_cases()
    context_cases()
    legacy_cases()
    trade_cases()
    ladder_cases()
    bad = [(n, p) for n, good, p in results if not good]
    for n, p in bad:
        print(f"FAIL {n} {p}")
    if bad:
        print(f"test_gates: {len(bad)} of {len(results)} planted cases wrong")
        sys.exit(1)
    print(f"test_gates: {len(results)} planted cases right ({sum(1 for n, g, p in results if 'passes' in n)} pass, the rest caught)")
    sys.exit(0)


if __name__ == "__main__":
    main()
