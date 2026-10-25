# outreach-drafter (Mondays 9:40 am)

One job: on Mondays, or on any weekday when Todd asks for a batch in a live chat (Oct 22), draft permission-based first emails to named decision-makers. Reply status belongs to the chief-of-staff sweep (Todd, Oct 25); this run never writes it. A batch sends only under the standing send rule (CONSTITUTION 2) or on Todd's send in this session.

## Inputs (Reads)
- CRM prospects (ArtifactData list, out_dir data/crm), meta/products, meta/desk.
- permits/downstream/gc_leads.json (Entity A, at most 2 days old).
- data/prospects/prospects.json, data/work/matches.json (written by tools/crm_prospects.py).
- email/SEND_RULES.md and email/approved_templates.json, at step 6.
- .claude/skills/outreach-drafter/templates.md, at step 4 only.

## Process (Executes)
1. Inbox check (Todd, Oct 25): the chief-of-staff sweep, weekdays 7:20 am and 12:20 pm, is the only writer of reply, bounce, opt-out, yes and customer status. Before a batch, CRM meta/desk.lastInbox must be under 3 hours old and scoreboard meta/inbox.ok true; else run the sweep (.claude/skills/chief-of-staff/SKILL.md, sweep) first, and if it fails, no batch: tell Todd one line.
2. Batch day (Monday, or Todd's live ask): delete last batch's unsent drafts (back to ready). `python3 tools/crm_prospects.py data/crm`; check every address in data/prospects/verify.json with Bouncer (email/SEND_RULES.md step 2 outcomes: Deliverable sets emailStatus deliverable, Accept all catch_all, Undeliverable bounced-precheck and doNotEmail, Risky or Unknown waits), then list the CRM and run crm_prospects.py again; then `python3 tools/validate_leads.py gc --max-age-days 2` and `python3 tools/validate_leads.py prospects`. Exit 1 on either: no batch; tell Todd the exact ERROR lines. Only products with meta/products live and outreachGo true and the latest qa/<date>.md, at most 7 days old, with no FIX line for it; at most 40 first emails per product, oldest checkedAt first.
3. Match (semantic, the only judgment): each prospect without a current match gets one lead in its city, same side of town when its area says so, Partial Occupancy Approved first, then larger valuation, never its firstExample; the lead must fit the prospect's trade_vertical (pnf_rules.trade_fits, enforced by validate_leads matches: exterior_turnkey only Chicago Partial Occupancy Approved; window_cleaning a new build of $5M or more at partial occupancy or under inspection, never an interior fit-out; dumpster_rental a job under $5M under inspection; security a new build of $20M or more at either stage). Append to data/work/matches.json with a one-line reason. Run `python3 tools/validate_leads.py matches`.
4. Draft: `python3 tools/copy_gate.py --assign` prints each match's template id (trade, stage and the prospect's fixed test arm, Todd Oct 22); fill exactly that template in templates.md, fixed words unchanged. Fields come only from the two validated files: {first}, {gc} (pnf_rules.gc_display), {value} (pnf_rules.value_display), {kind} (window_cleaning, dumpster_rental, security: pnf_rules.kind_display of the City scope; every other vertical: one word that matches the scope, school, office, hotel or apartment, none fits, pick another lead), {street} (pnf_rules.street_display). Write data/work/drafts.json with `variant` = that id.
5. `python3 tools/copy_gate.py`. Exit 1: fix wording only, rerun once, else drop the draft.
6. Send: a batch that qualifies under the standing send rule (email/SEND_RULES.md) sends with no ask, then one line to Todd; else one review page with every draft and the reason, and ask Todd "Reply send". Follow SEND_RULES exactly. Sender appends the footer.
- Follow-ups (Todd, Oct 22: "Yes, two follow-ups"): at most two, each 5 business days after the last email, same thread, the prospect's recorded variant for a lead it was never sent (`--assign` on the follow-up matches), gated with `python3 tools/copy_gate.py data/work/followups.json --prospects data/prospects/followups.json --matches ''`. Never after a reply, never to the Oct 19 and 20 batches (crm_prospects.py LEGACY_BATCHES).
- License and pest seat emails (Todd, Oct 24): steps in email/L2-COMMISSION.md (sales@) and email/P1-PEST-SEAT.md.
- A yes (the sweep sets it): the monday-email stage owns that prospect.

## Outputs (Writes)
- data/work/drafts.json, schema pnf.draft.v1: {schema, drafts:[{prospect_id, lead_id, to, subject, body, variant}]}.
- CRM prospects: status drafted, batch, matchedLeadId, firstExample, variant (the arm letter); meta/desk.lastOutreach (one sentence).
- Scoreboard agents/leads-outreach idle with lastNote; one message to Todd only when a batch or a failure needs him.
