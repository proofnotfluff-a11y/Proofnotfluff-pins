# L1: Chicago New Business Licenses outreach (written Oct 22, 2026, nothing sent)

Product: Chicago New Business Licenses, $29 a month (launches/chicago-new-business-licenses.md), for commercial cleaning and pest control companies (Todd, Oct 22, 2026, live chat: "Licenses: go"). Nothing in this file is sent until every gate in the launch record has passed and Todd says go for outreach; outreach go stays with Todd.

## Rules
- Same base as the permit emails (CLAUDE.md invariant 4, email/SEND_RULES.md): plain text, under 75 words, no link, no price, a named decision-maker (an owner-read inbox only per pnf_rules.owner_read_inbox), and a permission question at the end.
- Faceless (Todd, Oct 22, 2026, live chat: "no sender name"): no name signs the email. The fixed footer the sender appends (pnf_rules.FOOTER: ProofNotFluff, the Chicago mailbox address and the "no thanks" opt-out) is the only signature.
- Every fact comes from one validated lead (schema pnf.license_lead.v1 in data/work/signal_leads.json, built from that Monday's members' list): {business} is the City's shown business name as the list prints it, {street} is pnf_rules.street_display of the lead's address (no house number; members get the address), {date} is pnf_rules.date_display of the issue date ("Oct 16"). The lead must be dated inside the last 30 days on the send day.
- Never "cited", "violation" or any judgment of the business. A new license is the only fact.
- Gate: `python3 tools/copy_gate.py --signal data/work/signal_drafts.json --leads data/work/signal_leads.json` (schema pnf.signal_draft.v1, `variant` on every draft). Templates are checked on every push by `--signal-templates` and against the live sample by `--signal-live`.
- Follow-ups (Todd, Oct 22: two follow-ups): at most two, each 5 business days after the last email, in the same thread, each naming a new business the prospect was never sent. Never after a reply, an opt-out or a bounce. Gated with `--matches ''`.
- Overlap: restaurant-product buyers (pest, hood, grease) are the same people. The restaurant product's outreach is paused until this product is live (Todd, Oct 22, decision 4), so nobody gets both.

## Templates
One arm (A) for now; copy test 1 runs on the permit templates only. A new letter goes in as a full set (first and both follow-ups).

### T11 licenses, commercial cleaning, first email
Product: chicago-licenses
Kind: license
Trade: commercial_cleaning
Step: first
Variant: A
Subject: New business on {street}
```text
Hi {first},

{business} on {street} got its new City business license on {date}. New places often line up their cleaning crew in the first few weeks.

Want the address, plus the other new businesses the City licensed this month?
```
### T12 licenses, commercial cleaning, follow-up 1
Product: chicago-licenses
Kind: license
Trade: commercial_cleaning
Step: followup1
Variant: A
Subject: Another new business on {street}
```text
Hi {first},

One more from the City's records: {business} on {street} got its new business license on {date}.

Should I send you the list of new Chicago businesses for this month?
```
### T13 licenses, commercial cleaning, follow-up 2
Product: chicago-licenses
Kind: license
Trade: commercial_cleaning
Step: followup2
Variant: A
Subject: New business on {street}
```text
Hi {first},

Last one from me: {business} on {street} got its new business license on {date}. If new businesses are not a fit for your cleaning crew, no need to reply.

Would the list of this month's new Chicago businesses help?
```
### T14 licenses, pest control, first email
Product: chicago-licenses
Kind: license
Trade: pest_control
Step: first
Variant: A
Subject: New business on {street}
```text
Hi {first},

{business} on {street} got its new City business license on {date}. New places often pick a pest control company in the first few weeks.

Want the address, plus the other new businesses the City licensed this month?
```
### T15 licenses, pest control, follow-up 1
Product: chicago-licenses
Kind: license
Trade: pest_control
Step: followup1
Variant: A
Subject: Another new business on {street}
```text
Hi {first},

One more from the City's records: {business} on {street} got its new business license on {date}.

Should I send you the list of new Chicago businesses for this month?
```
### T16 licenses, pest control, follow-up 2
Product: chicago-licenses
Kind: license
Trade: pest_control
Step: followup2
Variant: A
Subject: New business on {street}
```text
Hi {first},

Last one from me: {business} on {street} got its new business license on {date}. If new businesses are not a fit for your pest control work, no need to reply.

Would the list of this month's new Chicago businesses help?
```

## Source
Drafted from the "Licenses, to a cleaning owner" first email in the Claude Doc "ProofNotFluff growth research, Oct 22, 2026" (Phase A pattern: one observation, one honest why-now line, one permission question). One change from the doc: "licensed in Chicago this week" became "the City licensed this month", because the list covers 30 days and a lead can be up to 30 days old.
