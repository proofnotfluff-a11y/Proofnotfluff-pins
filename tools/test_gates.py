#!/usr/bin/env python3
"""Planted failures for the four downstream-pipeline gates (Context, Timing Moat, Two-Entity Schema and Inbox, Outreach
Copy). Every planted bad case must be caught and every planted good case must pass, or this exits 1. tools/check_repo.py
runs it as the gate-selftest check, so a gate that silently stops catching something turns the code gate red.

Usage: python3 tools/test_gates.py
"""
import copy
import re
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
           R.validate_drafts(draft("chi-1", body.replace("Want me", "See washco.com. Want me")), leads, pros), True)
    expect("trade: exterior draft at 75 words fails",
           R.validate_drafts(draft("chi-1", body.replace("Want me", " ".join(["more"] * 40) + " Want me")), leads, pros), True)
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


def step2_cases():
    """Step 2 buyer types (Todd, Oct 22, 2026, 10:55 pm): window_cleaning gets partial occupancy and new builds under
    inspection; dumpster_rental only jobs under inspection; security only new builds of $5M or more; none of them serves
    the restaurant product; each has an A and B template that passes the copy gate on a lead it may use."""
    import copy_gate as CG
    import enrich_ci as EC
    new = dict(LEAD, work_type="New construction")
    insp_new = dict(new, lead_id="chi-3", stage="Inspections Under Way", stage_source="INSPECTIONS")
    insp_reno = dict(insp_new, lead_id="chi-4", work_type="Renovation")
    aus_new = dict(insp_new, lead_id="aus-2", city="austin", stage_source="Work under way")
    small_new = dict(insp_new, lead_id="chi-5", valuation=2_000_000)
    small_reno = dict(insp_reno, lead_id="chi-6", valuation=2_000_000)
    expect("step2: window on a new build at partial occupancy fits", [] if R.trade_fits("window_cleaning", new) else ["no"], False)
    expect("step2: window on an interior renovation at partial occupancy fails",
           R.trade_problems("chicago-construction", "window_cleaning", dict(LEAD, work_type="Renovation")), True)
    expect("step2: window on a new build under inspection fits", [] if R.trade_fits("window_cleaning", insp_new) else ["no"], False)
    expect("step2: window on a renovation under inspection fails", R.trade_problems("chicago-construction", "window_cleaning", insp_reno), True)
    expect("step2: window on a floor build-out the City tags as new construction fails",
           R.trade_problems("chicago-construction", "window_cleaning", dict(insp_new, scope="First time build out of 23rd floor office space")), True)
    expect("step2: window on an Austin new build fits", [] if R.trade_fits("window_cleaning", aus_new) else ["no"], False)
    expect("step2: dumpster on a $2M renovation under inspection fits", [] if R.trade_fits("dumpster_rental", small_reno) else ["no"], False)
    expect("step2: dumpster on a $45M job under inspection fails", R.trade_problems("chicago-construction", "dumpster_rental", insp_reno), True)
    expect("step2: security on a $19M new build fails",
           R.trade_problems("chicago-construction", "security", dict(insp_new, valuation=19_000_000)), True)
    expect("step2: dumpster on partial occupancy fails", R.trade_problems("chicago-construction", "dumpster_rental", new), True)
    expect("step2: security on a $45M new build fits", [] if R.trade_fits("security", insp_new) else ["no"], False)
    expect("step2: security on a $2M new build fails", R.trade_problems("chicago-construction", "security", small_new), True)
    expect("step2: security on a renovation fails", R.trade_problems("chicago-construction", "security", dict(insp_reno)), True)
    expect("step2: security on a lead with no work type fails", R.trade_problems("chicago-construction", "security", LEAD), True)
    for tr in ("window_cleaning", "dumpster_rental", "security"):
        pr = dict(PROSPECT, prospect_id=f"cc-{tr}-example", trade_vertical=tr)
        expect(f"step2: {tr} Chicago prospect passes", R.validate_prospect(pr), False)
        expect(f"step2: {tr} Austin prospect passes", R.validate_prospect(dict(pr, product="austin-construction", city="austin")), False)
        expect(f"step2: {tr} on the restaurant product fails", R.validate_prospect(dict(pr, product="chicago-restaurant")), True)
        expect(f"step2: {tr} business row passes", EC.validate_businesses({"schema": "pnf.business.v1", "businesses": [
            {"prospect_id": pr["prospect_id"], "product": "austin-construction", "business": "X Co", "website": "xco.example",
             "trade_vertical": tr}]}), False)
    pros = {f"cc-{tr}-example": dict(PROSPECT, prospect_id=f"cc-{tr}-example", trade_vertical=tr)
            for tr in ("window_cleaning", "dumpster_rental", "security")}
    leads = {x["lead_id"]: x for x in (new, insp_new, insp_reno, small_new, small_reno)}
    m = lambda pid, lid: {"schema": "pnf.match.v1", "matches": [{"prospect_id": pid, "lead_id": lid, "reason": "x"}]}
    expect("step2: security match to a $2M build fails", R.validate_matches(m("cc-security-example", "chi-5"), leads, pros), True)
    expect("step2: dumpster match to a $2M renovation under inspection passes",
           R.validate_matches(m("cc-dumpster_rental-example", "chi-6"), leads, pros), False)
    expect("step2: window match to a renovation under inspection fails",
           R.validate_matches(m("cc-window_cleaning-example", "chi-4"), leads, pros), True)
    ts = CG.variant_templates(CG.TEMPLATES)
    f = dict(CG.FIXTURE_FIELDS)
    for scope, want in (("New 6-story building with 110 dwelling units", "apartment"), ("New middle school", "school"),
                        ("Core and shell for a one story quantum facility", "building"), ("Office and apartments", "apartment"), ("Multi Family Res with a Leasing Office", "apartment"),
                        ("Full building for 5 new 3-story townhouses (R-2)", "townhouse"), ("New office and school", "building"),
                        ("New Construction of Sports Facility to Include Admin Building with offices", "building")):
        expect(f"step2: kind of {scope!r} is {want}", [] if R.kind_display({"scope": scope}) == want else [R.kind_display({"scope": scope})], False)
    apt = dict(insp_new, lead_id="chi-7", scope="New 6-story building with 110 dwelling units")
    wpid = "cc-window_cleaning-example"
    arm = R.assign_variant(wpid, CG.slot_letters(ts, "window_cleaning", "Inspections Under Way"))
    t6 = next(t for t in ts if t["trade"] == "window_cleaning" and t["stage"] == "Inspections Under Way" and t["letter"] == arm)
    kd = lambda k: {"drafts": [{"prospect_id": wpid, "lead_id": "chi-7", "variant": t6["id"],
                                "subject": CG.fill(t6["subject"], dict(f, kind=k)), "body": CG.fill(t6["body"], dict(f, kind=k))}]}
    wpros = {wpid: dict(PROSPECT, prospect_id=wpid, trade_vertical="window_cleaning")}
    expect("step2: draft with the kind from the City scope passes", CG.variant_problems(kd("apartment"), ts, {"chi-7": apt}, wpros), False)
    expect("step2: draft calling an apartment build an office fails", CG.variant_problems(kd("office"), ts, {"chi-7": apt}, wpros), True)
    for tr, ld in (("window_cleaning", new), ("window_cleaning", insp_new), ("dumpster_rental", small_reno),
                   ("security", insp_new), ("security", new)):
        slot = [t for t in ts if t["trade"] == tr and t["stage"] == ld["stage"]]
        expect(f"step2: {tr} {ld['stage']} has A and B", [] if sorted(t["letter"] for t in slot) == ["A", "B"] else ["slot"], False)
        f = dict(CG.FIXTURE_FIELDS, value=R.value_display(ld["valuation"]))
        for t in slot:
            expect(f"step2: {t['id']} renders and passes", R.copy_problems(CG.fill(t["subject"], f), CG.fill(t["body"], f), "Dana", ld), False)
        a, b = (next((t for t in slot if t["letter"] == x), None) for x in "AB")
        if a and b:
            ab, bb = a["body"].split("\n\n"), b["body"].split("\n\n")
            same = len(ab) == len(bb) and ab[0] == bb[0] and ab[2:] == bb[2:] and bb[1].endswith(ab[1]) and bb[1] != ab[1]
            expect(f"step2: {a['id'][:2]} A and B differ only in B's first sentence", [] if same else ["differ"], False)


def variant_cases():
    """Variants (Todd, Oct 22, 2026, live chat: "A and B, test 1", gate change approved): one template per vertical, stage
    and letter; every draft names its template id, uses the prospect's arm and the template's fixed words; a follow-up
    keeps the recorded arm and never repeats a lead the prospect was sent."""
    import copy_gate as CG
    ts = CG.variant_templates(CG.TEMPLATES)
    expect("variant: live templates carry A and B for every slot passes",
           [] if all(sorted(CG.slot_letters(CG.firsts(ts), t["trade"], t["stage"])) == ["A", "B"] for t in CG.firsts(ts)) else ["a slot lacks A or B"], False)
    ids = [f"cc-test{i}" for i in range(400)]
    arms = [R.assign_variant(i, ["B", "A"]) for i in ids]
    expect("variant: the split is fixed and even passes",
           [] if arms == [R.assign_variant(i, ["A", "B"]) for i in ids] and 160 <= arms.count("A") <= 240 else ["split moved or lopsided"], False)

    def planted(fn):
        tmp = tempfile.mkdtemp(prefix="pnf-var-")
        try:
            path = os.path.join(tmp, "templates.md")
            open(path, "w", encoding="utf-8").write(fn(open(CG.TEMPLATES, encoding="utf-8").read()))
            return CG.check_templates(path)[0]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    expect("variant: two B templates in one slot fail", planted(lambda x: x.replace("Variant: A\nStage: Inspections", "Variant: B\nStage: Inspections")), True)
    expect("variant: a lowercase Variant letter fails", planted(lambda x: x.replace("Variant: B", "Variant: b", 1)), True)

    insp = dict(LEAD, lead_id="chi-2", stage="Inspections Under Way", stage_source="INSPECTIONS")
    insp3 = dict(insp, lead_id="chi-3")
    leads = {"chi-1": LEAD, "chi-2": insp, "chi-3": insp3}
    t2 = {t["letter"]: t for t in ts if t["trade"] == "commercial_cleaning" and t["stage"] == "Inspections Under Way"}
    arm = R.assign_variant(PROSPECT["prospect_id"], list(t2))
    other = "A" if arm == "B" else "B"
    f = dict(CG.FIXTURE_FIELDS, first="Dana")
    mk = lambda letter, lid="chi-2", **k: {"schema": "pnf.draft.v1", "drafts": [dict({
        "prospect_id": PROSPECT["prospect_id"], "lead_id": lid, "to": PROSPECT["email"], "variant": t2[letter]["id"],
        "subject": CG.fill(t2[letter]["subject"], f), "body": CG.fill(t2[letter]["body"], f)}, **k)]}
    pros = {PROSPECT["prospect_id"]: PROSPECT}
    expect("variant: draft on its arm's template passes", CG.variant_problems(mk(arm), ts, leads, pros), False)
    expect("variant: draft on the other arm fails", CG.variant_problems(mk(other), ts, leads, pros), True)
    expect("variant: draft with no variant fails", CG.variant_problems(mk(arm, variant=""), ts, leads, pros), True)
    expect("variant: draft whose fixed words changed fails",
           CG.variant_problems(mk(arm, body=CG.fill(t2[arm]["body"], f).replace("usually", "always")), ts, leads, pros), True)
    expect("variant: draft naming a template for another stage fails",
           CG.variant_problems(mk(arm, lead_id="chi-1"), ts, leads, pros), True)
    # Follow-ups (Todd, Oct 29, 2026, task thread: "Yes" to the two wrappers): T17-A then T18-A, each with the A job sentence.
    fus = {t["step"]: t for t in ts if t["step"] in CG.FOLLOWUP_STEPS}
    expect("followup: one wrapper per step passes", [] if sorted(fus) == ["followup1", "followup2"] else ["missing a step"], False)
    fu = {PROSPECT["prospect_id"]: dict(PROSPECT, variant=other, first_example="chi-2")}
    fu2 = {PROSPECT["prospect_id"]: dict(PROSPECT, variant=other, first_example="chi-2", followup_examples=["chi-3"])}
    fu3 = {PROSPECT["prospect_id"]: dict(PROSPECT, variant=other, first_example="chi-2", followup_examples=["chi-3", "chi-1"])}
    first_subj = "Re: " + CG.fill(t2[other]["subject"], f)
    fd = lambda step, lid="chi-3", **k: {"schema": "pnf.draft.v1", "drafts": [dict({
        "prospect_id": PROSPECT["prospect_id"], "lead_id": lid, "to": PROSPECT["email"], "variant": fus[step]["id"],
        "subject": first_subj, "body": CG.fill(CG.followup_template(fus[step], t2["A"]), f)}, **k)]}
    expect("followup: first follow-up on T17 with the A job sentence passes", CG.variant_problems(fd("followup1"), ts, leads, fu, followup=True), False)
    expect("followup: second follow-up on T18 with a new lead passes",
           CG.variant_problems(fd("followup2", lid="chi-1"), ts, {**leads, "chi-1": dict(insp, lead_id="chi-1")}, fu2, followup=True), False)
    expect("followup: resending the first email's template as a follow-up fails",
           CG.variant_problems(mk(other, lid="chi-3"), ts, leads, fu, followup=True), True)
    expect("followup: T18 as the first follow-up fails", CG.variant_problems(fd("followup2"), ts, leads, fu, followup=True), True)
    expect("followup: a third follow-up fails", CG.variant_problems(fd("followup2", lid="chi-1"), ts, leads, fu3, followup=True), True)
    expect("followup: the B who-and-why sentence in place of the A job sentence fails",
           CG.variant_problems(fd("followup1", body=CG.fill(CG.followup_template(fus["followup1"], t2["B"]), f)), ts, leads, fu, followup=True), True)
    expect("followup: changed fixed words fail",
           CG.variant_problems(fd("followup1", body=CG.fill(CG.followup_template(fus["followup1"], t2["A"]), f).replace("another", "a great")),
                               ts, leads, fu, followup=True), True)
    expect("followup: a subject without Re: fails",
           CG.variant_problems(fd("followup1", subject=CG.fill(t2[other]["subject"], f)), ts, leads, fu, followup=True), True)
    expect("followup: repeating the first email's lead fails", CG.variant_problems(fd("followup1", lid="chi-2"), ts, leads, fu, followup=True), True)
    expect("followup: second follow-up repeating the first follow-up's lead fails",
           CG.variant_problems(fd("followup2", lid="chi-3"), ts, leads, fu2, followup=True), True)
    expect("followup: a wrapper with a second field fails",
           planted(lambda x: x.replace("one more job your team could chase. {obs}", "one more job your team could chase. {obs} {gc}")), True)
    expect("followup: a wrapper whose subject is not Re: {first_subject} fails",
           planted(lambda x: x.replace("Step: followup2\nSubject: Re: {first_subject}", "Step: followup2\nSubject: Quick note")), True)
    expect("followup: a missing second step fails", planted(lambda x: x.replace("Step: followup2", "Step: followup9")), True)


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


def expect_reason(name, problems, why):
    """A planted bad case that must be caught for the right reason: some problem line carries `why`."""
    hit = any(why.lower() in x.lower() for x in problems)
    results.append((name, hit, problems[:1] or ["nothing caught"]))


def signal_cases():
    """Signal leads (Todd, Oct 22, 2026, live chat, decision 2: gate extension for license and citation signals). Every
    permit copy rule still applies to a signal email, and each new rule is caught for its own reason."""
    import copy_gate as CG
    LIC = dict(CG.SIGNAL_FIXTURES["license"])
    ELV = dict(CG.SIGNAL_FIXTURES["citation"])
    EXT = dict(ELV, lead_id="cit-ext", bureau="CONSERVATION", description="REPAIR EXTERIOR WALL", address="2210 W Division St",
               community_area="West Town")
    SEND = "2026-10-19"
    lb = ("Hi Dana,\n\nStew Kitchen on N Mozart St got its new City business license on Oct 16. New places often line up "
          "their cleaning crew in the first few weeks.\n\nWant the address, plus the other new businesses the City licensed this month?")
    ls = "New business on N Mozart St"
    eb = ("Hi Dana,\n\nThe City cited the elevator at a building on W 63rd St on Oct 16 to maintain or repair it. An open "
          "citation has to be fixed and reinspected.\n\nWant the address, plus the other buildings cited this month?")
    xb = eb.replace("the elevator at a building on W 63rd St", "a business building on W Division St").replace(
        "to maintain or repair it", "to repair its exterior wall").replace("fixed", "repaired").replace("buildings cited", "business buildings cited")
    sc = lambda b, lead=LIC, s=ls, send=SEND, first="Dana": R.signal_copy_problems(s, b, first, lead, send)

    expect("signal: license email passes", sc(lb), False)
    expect("signal: elevator citation email passes", sc(eb, ELV, "Elevator citation on W 63rd St"), False)
    expect("signal: exterior wall citation email passes", sc(xb, EXT, "Exterior wall citation on W Division St"), False)
    expect("signal: food license on a food license type passes", sc(lb.replace("City business license", "City food license")), False)
    expect("signal: a business named Discount Tire is a name, not a pitch, and passes",
           sc(lb.replace("Stew Kitchen", "Discount Tire"), dict(LIC, business="Discount Tire")), False)
    expect("signal: lead dated on the send day passes", sc(lb, send="2026-10-16"), False)
    expect("signal: lead dated 30 days before the send day passes", sc(lb, send="2026-11-15"), False)
    for raw, want in (("495-499 N Milwaukee Ave Basement, 1, Mezz.", "495 N Milwaukee Ave"), ("4329 N Mozart St 1f", "4329 N Mozart St"),
                      ("1600 W 63rd St", "1600 W 63rd St"), ("1200 N Broadway 2 P105", "1200 N Broadway"), ("800 N St Louis Ave Ste 2", "800 N St Louis Ave")):
        expect(f"signal: address {raw!r} gives {want!r} passes", [] if R.signal_address(raw) == want else [R.signal_address(raw)], False)

    # every existing copy rule, on a signal email
    expect_reason("signal: 75 words or more fails", sc(lb.replace("Want the", " ".join(["more"] * 40) + " Want the")), "words, the limit")
    expect_reason("signal: a link fails", sc(lb.replace("Want the", "See proofnotfluff.com. Want the")), "link or domain")
    expect_reason("signal: a link inside the business name still fails",
                  sc(lb.replace("Stew Kitchen", "Stewkitchen.com"), dict(LIC, business="Stewkitchen.com")), "link or domain")
    expect_reason("signal: a price pitch fails", sc(lb.replace("Want the", "It is $29 a month. Want the")), "pitches the paid product")
    expect_reason("signal: an em dash fails", sc(lb.replace(". New", " — new")), "em or en dash")
    expect_reason("signal: a generic greeting fails", sc(lb.replace("Hi Dana,", "Hi there,")), "must open with")
    expect_reason("signal: no first name fails", sc(lb, first=""), "first name")
    expect_reason("signal: no permission question fails", sc(lb.rstrip("?") + "."), "permission question")
    expect_reason("signal: a leftover placeholder fails", sc(lb.replace("Hi Dana,\n", "Hi Dana,\n{street} ")), "placeholder")

    # the new rules
    expect_reason("signal: wrong street fails", sc(lb.replace("N Mozart St", "S Fake St")), "does not name the lead's street")
    expect_reason("signal: house number in the email fails", sc(lb.replace("on N Mozart St", "at 4329 N Mozart St")), "house number")
    expect_reason("signal: missing date fails", sc(lb.replace(" on Oct 16", " recently")), "does not state the lead's date")
    expect_reason("signal: wrong date fails", sc(lb.replace("Oct 16", "Oct 9")), "the City record says")
    expect_reason("signal: date written another way fails", sc(lb.replace("Oct 16", "10/16")), "does not state the lead's date")
    expect_reason("signal: lead 31 days old on the send day fails", sc(lb, send="2026-11-16"), "outside the 30-day window")
    expect_reason("signal: lead dated after the send day fails", sc(lb, send="2026-10-15"), "after the send day")
    expect_reason("signal: no send day fails", sc(lb, send=""), "send day")
    expect_reason("signal: license email without license words fails", sc(lb.replace("new City business license", "City approval")),
                  "does not name the signal")
    expect_reason("signal: food license on a non-food license fails",
                  sc(lb.replace("business license", "food license"), dict(LIC, license_type="Limited Business License")), "food license")
    expect_reason("signal: license email with citation words fails", sc(lb.replace("got its", "was cited and got its")), "another signal")
    expect_reason("signal: license email without the business name fails", sc(lb.replace("Stew Kitchen", "A new place")),
                  "does not name the shown business name")
    expect_reason("signal: elevator email without 'elevator' fails", sc(eb.replace("the elevator at a building", "a building"), ELV,
                  "Citation on W 63rd St"), "does not say 'elevator'")
    expect_reason("signal: elevator email naming an exterior repair fails",
                  sc(eb.replace("to maintain or repair it", "to repair its exterior wall"), ELV, "Elevator citation on W 63rd St"), "exterior repair")
    expect_reason("signal: exterior email without the cited repair fails", sc(xb.replace("exterior wall", "building"), EXT,
                  "Citation on W Division St"), "does not name the cited repair")
    expect_reason("signal: exterior email naming a repair not cited fails",
                  sc(xb.replace("exterior wall", "exterior wall and roof"), EXT, "Citation on W Division St"), "did not cite")
    expect_reason("signal: exterior email saying elevator fails", sc(xb.replace("business building", "elevator building"), EXT,
                  "Citation on W Division St"), "says 'elevator'")
    expect_reason("signal: closed citation fails", sc(eb, dict(ELV, open=False), "Elevator citation on W 63rd St"), "not open")
    expect_reason("signal: citation email with license words fails",
                  sc(eb.replace("Want the address", "Want the business license list"), ELV, "Elevator citation on W 63rd St"), "another signal")
    expect_reason("signal: unknown bureau fails", sc(eb, dict(ELV, bureau="PLUMBING"), "Elevator citation on W 63rd St"), "bureau")
    expect_reason("signal: unknown lead kind fails", sc(lb, dict(LIC, kind="rumor")), "unknown signal kind")

    # lead schemas (business-level fields only)
    expect("signal: license lead passes the schema", R.validate_signal_lead(LIC), False)
    expect("signal: citation lead passes the schema", R.validate_signal_lead(EXT), False)
    expect_reason("signal: an owner field on a lead fails", R.validate_signal_lead(dict(LIC, owner_name="x")), "not a business-level field")
    expect_reason("signal: an address with a unit fails", R.validate_signal_lead(dict(LIC, address="4329 N Mozart St 1f")), "units and suites")
    expect_reason("signal: a business name that could be a person's fails", R.validate_signal_lead(dict(LIC, business="Maria Lopez")),
                  "could be a person's")
    expect_reason("signal: a phone number in a lead fails", R.validate_signal_lead(dict(LIC, business="Stew Kitchen 312-555-0100")), "phone")
    expect_reason("signal: missing issue date fails", R.validate_signal_lead(dict(LIC, issue_date="")), "issue_date")
    expect_reason("signal: unreadable citation date fails", R.validate_signal_lead(dict(ELV, citation_date="10/16/2026")), "citation_date")
    expect_reason("signal: citation open not true or false fails", R.validate_signal_lead(dict(ELV, open="yes")), "open must be")
    expect_reason("signal: wrong dataset fails", R.validate_signal_lead(dict(LIC, dataset="ydr8-5enu")), "dataset")
    expect_reason("signal: lead file with a permit schema fails",
                  R.validate_signal_file({"schema": "pnf.gc_lead.v1", "leads": [LIC]}), "schema must be")
    expect_reason("signal: duplicate lead ids fail", R.validate_signal_file({"schema": "pnf.license_lead.v1", "leads": [LIC, LIC]}), "duplicate")
    expect_reason("signal: citation lead in a license file fails",
                  R.validate_signal_file({"schema": "pnf.license_lead.v1", "leads": [ELV]}), "a citation lead in")

    # prospects and drafts for a signal product; the permit product paths stay closed to it
    pest = dict(PROSPECT, prospect_id="lp-bugsco-example", product="chicago-licenses", website_domain="bugsco.example",
                email="dana@bugsco.example", trade_vertical="pest_control")
    clean = dict(PROSPECT, prospect_id="lc-sparkleco-example", product="chicago-licenses")
    expect("signal: pest_control prospect on the licenses product passes", R.validate_prospect(pest), False)
    expect("signal: cleaning prospect on the licenses product passes", R.validate_prospect(clean), False)
    expect_reason("signal: pest_control on a permit product fails", R.validate_prospect(dict(pest, product="chicago-construction")),
                  "unknown trade_vertical")
    expect_reason("signal: exterior_turnkey on the licenses product fails",
                  R.validate_prospect(dict(pest, trade_vertical="exterior_turnkey")), "does not serve product")
    expect_reason("signal: licenses prospect matched to a permit lead fails",
                  R.validate_matches({"schema": "pnf.match.v1", "matches": [{"prospect_id": clean["prospect_id"], "lead_id": "chi-1", "reason": "x"}]},
                                     {"chi-1": LEAD}, {clean["prospect_id"]: clean}), "does not serve product")
    ts = CG.signal_templates(os.path.join(ROOT, "email", "L1-OUTREACH.md"))
    t11 = next(t for t in ts if t["id"] == "T11-A")
    f = CG.signal_fields(LIC)
    leads = {LIC["lead_id"]: LIC, "lic-2": dict(LIC, lead_id="lic-2", business="Pearl Club", address="495 N Milwaukee Ave"),
             ELV["lead_id"]: ELV}
    pros = {clean["prospect_id"]: clean, pest["prospect_id"]: pest}
    sd = lambda t, lid=LIC["lead_id"], pr=clean, **k: {"schema": "pnf.signal_draft.v1", "drafts": [dict({
        "prospect_id": pr["prospect_id"], "lead_id": lid, "to": pr["email"], "variant": t["id"],
        "subject": CG.fill(t["subject"], CG.signal_fields(leads[lid])), "body": CG.fill(t["body"], CG.signal_fields(leads[lid]))}, **k)]}
    expect("signal: valid signal draft passes", R.validate_signal_drafts(sd(t11), leads, pros, SEND) + CG.signal_variant_problems(sd(t11), ts, leads, pros), False)
    expect_reason("signal: draft to a role inbox fails",
                  R.validate_signal_drafts(sd(t11, to="info@sparkleco.example"), leads, {clean["prospect_id"]: dict(clean, email="info@sparkleco.example")}, SEND),
                  "role-based inbox")
    expect_reason("signal: draft for a permit-product prospect fails",
                  R.validate_signal_drafts(sd(t11), leads, {clean["prospect_id"]: PROSPECT | {"prospect_id": clean["prospect_id"]}}, SEND),
                  "not a signal product")
    expect_reason("signal: draft on a citation lead for the licenses product fails",
                  R.validate_signal_drafts(sd(t11, lead_id=ELV["lead_id"], body=eb, subject="Elevator citation on W 63rd St"), leads, pros, SEND),
                  "does not sell")
    expect_reason("signal: permit-schema draft file fails", R.validate_signal_drafts(dict(sd(t11), schema="pnf.draft.v1"), leads, pros, SEND),
                  "pnf.signal_draft.v1")
    expect_reason("signal: draft whose fixed words changed fails",
                  CG.signal_variant_problems(sd(t11, body=CG.fill(t11["body"], f).replace("often", "always")), ts, leads, pros), "fixed words")
    expect_reason("signal: cleaning draft on the pest template fails",
                  CG.signal_variant_problems(sd(next(t for t in ts if t["id"] == "T14-A")), ts, leads, pros), "is not a chicago-licenses commercial_cleaning")
    fu1 = next(t for t in ts if t["trade"] == "commercial_cleaning" and t["step"] == "followup1")
    fu2 = next(t for t in ts if t["trade"] == "commercial_cleaning" and t["step"] == "followup2")
    expect_reason("signal: first email on a follow-up template fails", CG.signal_variant_problems(sd(fu1), ts, leads, pros), "followup1 template")
    sent1 = {clean["prospect_id"]: dict(clean, variant="A", first_example=LIC["lead_id"])}
    expect("signal: follow-up 1 on a new lead passes", CG.signal_variant_problems(sd(fu1, lid="lic-2"), ts, leads, sent1, followup=True), False)
    expect_reason("signal: follow-up repeating the first email's lead fails",
                  CG.signal_variant_problems(sd(fu1), ts, leads, sent1, followup=True), "repeats a lead")
    expect_reason("signal: follow-up 1 when follow-up 2 is due fails",
                  CG.signal_variant_problems(sd(fu1, lid="lic-2"), ts, leads, {clean["prospect_id"]: dict(sent1[clean["prospect_id"]], followup_examples=["lic-9"])},
                                             followup=True), "this draft is the followup2")
    expect("signal: follow-up 2 on a new lead passes",
           CG.signal_variant_problems(sd(fu2, lid="lic-2"), ts, leads, {clean["prospect_id"]: dict(sent1[clean["prospect_id"]], followup_examples=["lic-9"])},
                                      followup=True), False)
    expect_reason("signal: a third follow-up fails",
                  CG.signal_variant_problems(sd(fu2, lid="lic-2"), ts, leads, {clean["prospect_id"]: dict(sent1[clean["prospect_id"]], followup_examples=["lic-8", "lic-9"])},
                                             followup=True), "the limit is 2")

    # the outreach file itself, planted in a throwaway copy
    def planted(fn):
        tmp = tempfile.mkdtemp(prefix="pnf-sig-")
        try:
            path = os.path.join(tmp, "L1.md")
            open(path, "w", encoding="utf-8").write(fn(open(os.path.join(ROOT, "email", "L1-OUTREACH.md"), encoding="utf-8").read()))
            return CG.check_signal_templates({"chicago-licenses": path})[0]
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    expect("signal: live outreach file passes", CG.check_signal_templates()[0], False)
    expect("signal: live sample renders through the license templates and passes", CG.check_signal_live()[0], False)
    expect_reason("signal: a trade with no follow-up 2 fails", planted(lambda x: x[:x.index("### T16")]), "has no followup2 template")
    expect_reason("signal: a citation template for the licenses product fails", planted(lambda x: x.replace("Kind: license", "Kind: citation", 1)),
                  "is not one chicago-licenses sells")
    expect_reason("signal: an unknown Step fails", planted(lambda x: x.replace("Step: followup1", "Step: followup3", 1)), "is not one of")
    expect_reason("signal: a template over 75 words fails",
                  planted(lambda x: x.replace("in the first few weeks.", "in the first few weeks. " + " ".join(["more"] * 40), 1)), "words, the limit")
    expect_reason("signal: a second template for one slot fails", planted(lambda x: x + "\n" + x[x.index("### T14"):x.index("### T15")].replace("T14", "T19")),
                  "a second pest_control first template")
    expect_reason("signal: a template id taken by a permit template fails", planted(lambda x: x.replace("### T11", "### T1", 1)), "a second template with id")
    expect_reason("signal: a template with an unknown field fails", planted(lambda x: x.replace("{business} on", "{owner} on", 1)), "unknown fields")

    # one more kind is one more entry: a planted inspection kind, then removed
    R.SIGNAL_KINDS["inspection"] = dict(R.SIGNAL_KINDS["license"], schema="pnf.inspection_lead.v1", dataset="4ijn-s7e5",
                                        date_field="inspection_date",
                                        fields=tuple(x if x != "issue_date" else "inspection_date" for x in R.SIGNAL_KINDS["license"]["fields"]),
                                        words=lambda lead, low: [] if "inspection" in low else ["body does not say 'inspection'"],
                                        forbid=re.compile(r"\belevators?\b", re.I))
    try:
        ins = dict({k: v for k, v in LIC.items() if k != "issue_date"}, kind="inspection", dataset="4ijn-s7e5", inspection_date="2026-10-16")
        ib = lb.replace("got its new City business license", "passed its City inspection")
        expect("signal: a planted third kind (inspection) works as one more entry and passes", sc(ib, ins), False)
        expect_reason("signal: the planted inspection kind still checks its words", sc(ib.replace("inspection", "visit"), ins), "inspection")
    finally:
        R.SIGNAL_KINDS.pop("inspection", None)


def pest_role_cases():
    """Pest seat role inboxes (Todd, Oct 24; Legal desk fixes 1 to 3): the exact conditions, each broken once."""
    base = {"prospect_id": "cr-acmepest-com", "product": "chicago-restaurant", "business": "Acme Pest", "website_domain": "acmepest.com",
            "city": "chicago", "first_name": "", "last_name": "", "title": "", "email": "info@acmepest.com", "email_source": "site",
            "email_status": "unverified", "owner_source": "", "crm_trade": "pest control",
            "email_source_url": "https://www.acmepest.com/contact/", "site_notice": "none", "trade_vertical": "commercial_cleaning"}
    expect("pest role: info@ on its own site passes", R.validate_prospect(dict(base), pending=True), False)
    for name, change in (("info.chicago@ fails", {"email": "info.chicago@acmepest.com"}),
                         ("another domain fails", {"email": "info@acme-mail.com"}),
                         ("no source page fails", {"email_source_url": ""}),
                         ("a source page elsewhere fails", {"email_source_url": "https://directory.example.com/acme"}),
                         ("a site notice fails", {"site_notice": "no solicitations"}),
                         ("not checked for a notice fails", {"site_notice": ""}),
                         ("another trade fails", {"crm_trade": "hood cleaning"}),
                         ("another product fails", {"product": "austin-construction", "city": "austin", "prospect_id": "ca-acmepest-com"}),   # chicago-construction has its own role rule since Oct 29
                         ("support@ fails", {"email": "support@acmepest.com"}),
                         ("a guessed source fails", {"email_source": "pattern"})):
        x = dict(base); x.update(change)
        expect("pest role: " + name, R.validate_prospect(x, pending=True), True)


def construction_role_cases():
    """Construction role inboxes (Todd, Oct 29): the pest seat's conditions on a chicago-construction prospect, each broken
    once, and the draft must open "Hi there,"."""
    base = {"prospect_id": "cc-acmeclean-com", "product": "chicago-construction", "business": "Acme Clean", "website_domain": "acmeclean.com",
            "city": "chicago", "first_name": "", "last_name": "", "title": "", "email": "info@acmeclean.com", "email_source": "site",
            "email_status": "unverified", "owner_source": "", "crm_trade": "post-construction cleaning",
            "email_source_url": "https://www.acmeclean.com/contact/", "site_notice": "none", "trade_vertical": "commercial_cleaning"}
    expect("construction role: info@ on its own site passes", R.validate_prospect(dict(base), pending=True), False)
    expect("construction role: greeting is there", [] if R.greeting_name(base) == "there" else ["greeting " + R.greeting_name(base)], False)
    for name, change in (("info.chicago@ fails", {"email": "info.chicago@acmeclean.com"}),
                         ("another domain fails", {"email": "info@acme-mail.com"}),
                         ("no source page fails", {"email_source_url": ""}),
                         ("a source page elsewhere fails", {"email_source_url": "https://directory.example.com/acme"}),
                         ("a site notice fails", {"site_notice": "no solicitations"}),
                         ("not checked for a notice fails", {"site_notice": ""}),
                         ("austin fails", {"product": "austin-construction", "city": "austin"}),
                         ("support@ fails", {"email": "support@acmeclean.com"}),
                         ("a guessed source fails", {"email_source": "pattern"})):
        x = dict(base); x.update(change)
        expect("construction role: " + name, R.validate_prospect(x, pending=True), True)
    named = dict(base, first_name="Dana", last_name="Reyes", title="Owner", owner_source="site_about")
    expect("construction role: a named owner keeps Hi Dana", [] if R.greeting_name(named) == "Dana" else ["greeting " + R.greeting_name(named)], False)
    lead = {"lead_id": "chi-fixture", "city": "chicago", "stage": "Inspections Under Way", "work_type": "New construction",
            "valuation": 45_000_000, "gc_company": "Bartlett Cocke", "address": "100 N Hampton Dr", "scope": "new office building"}
    pr = dict(base, email_status="deliverable")
    body = ("Hi there,\n\nSaw that Bartlett Cocke has city inspections under way on the $45M office project on N Hampton Dr. "
            "Jobs at this stage usually line up the final clean soon.\n\nWant me to send you jobs like this free each Monday?")
    doc = lambda b: {"schema": "pnf.draft.v1", "drafts": [{"prospect_id": pr["prospect_id"], "lead_id": "chi-fixture", "to": pr["email"],
                                                         "subject": "Final clean on N Hampton Dr", "body": b}]}
    expect("construction role: a Hi there draft passes", R.validate_drafts(doc(body), {"chi-fixture": lead}, {pr["prospect_id"]: pr}), False)
    expect("construction role: a Hi Dana draft to info@ fails",
           R.validate_drafts(doc(body.replace("Hi there,", "Hi Dana,")), {"chi-fixture": lead}, {pr["prospect_id"]: pr}), True)


def main():
    moat_cases()
    inbox_cases()
    copy_cases()
    context_cases()
    legacy_cases()
    trade_cases()
    step2_cases()
    variant_cases()
    ladder_cases()
    signal_cases()
    pest_role_cases()
    construction_role_cases()
    bad =[(n, p) for n, good, p in results if not good]
    for n, p in bad:
        print(f"FAIL {n} {p}")
    if bad:
        print(f"test_gates: {len(bad)} of {len(results)} planted cases wrong")
        sys.exit(1)
    print(f"test_gates: {len(results)} planted cases right ({sum(1 for n, g, p in results if 'passes' in n)} pass, the rest caught)")
    sys.exit(0)


if __name__ == "__main__":
    main()
