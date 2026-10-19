# A1 pre-sale: Chicago construction cleaning leads (Oct 17, 2026)

Why: Gemini's red team (Oct 17) and the COO agree that waiting for traffic is the bottleneck. This tests whether cleaning companies pay, not whether they join a waitlist. Todd, Oct 17, 2:22 pm: "let's move on what will make you confident. Let's not waste time on things that don't work."

## The test
- Who: 36 Chicago-area companies whose own sites advertise post-construction or construction cleaning (the list lives in the private CRM, coo/LEADS_DESK.md, never in this public repo; opt-outs are its doNotEmail field).
- Offer: the full weekly list at $29 a month (the price on the leads page), cancel any time, this week's list right after checkout (members' page and Excel file), then every Monday.
- Pass: 2 or more paying companies within 10 days of the send. Fail: under 2. A fail kills the paid version and the page stays a free sample.
- Market check (read Oct 17): Chicago Cityscape sells Chicago permit newsletters with builder contacts at $125 a month; ConstructConnect Starter $129 a month per market (third-party guide, Oct 6, 2026); Dodge, Construction Monitor and BuildZoom are quote only.

## Rules
- Sending (Todd, Oct 18: "You send after my yes"): the outreach run sends each checked batch from hello@proofnotfluff.com in Gmail on the web, only after Todd says send in chat for that batch (coo/LEADS_DESK.md). Follow-up (Todd, Oct 18: "Yes, one follow-up"): one short follow-up 5 business days after the first email, in the same thread, never to anyone who replied, opted out or bounced. Nothing more after it.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, a valid postal address in the footer: "680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611" (Todd's iPostal1 mailbox, a private mailbox at a USPS-registered commercial mail receiving agency, Oct 19, 2026; it replaced the Oct 17 Cheyenne, WY address), and a working opt-out (reply "no thanks"); honor it, and never email that address again.
- Every fact in the email comes from the week's members' list (the City of Chicago Building Permits dataset as filtered by tools/permits_chicago.py). {Company}, {projects}, {near} and {example} are filled from that list on the morning the drafts are made; every draft is checked for leftover braces, and the drafts are not made if any number differs from the list (Holdout QC, Oct 17: the first draft carried last week's numbers).
- No invented people, no fake urgency, no claim that any builder works with us.

## Reach plan (Todd, Oct 17, 4:19 pm, asked how to reach only the people who would buy; chose "Expand to every Chicagoland cleaner")
- The prospect list grows from 36 to every Chicago-area company whose own site advertises post-construction or construction cleaning, found from their public sites (no bought lists, no scraped personal emails: only a business address the company publishes, else its contact form).
- Each email names one near-finish or newest permit in or near the prospect's own part of town, checked against the week's list, so every message carries a real lead the reader can use.
- Weekly batches of about 40, made as Gmail drafts in hello@proofnotfluff.com and sent as the Sending line says, with the one follow-up; no adjacent-trade pages and no paid ads for now.
- Nothing sends until the launch checklist (launches/chicago-construction-cleaning-leads.md) is complete and Todd says go.

## The email (one per company; {fields} filled from the list)

Fields, all from that Monday's permits/chicago/sample.json: {projects} = counts.kept and {near} = counts.nearFinish, written with a thousands comma ("1,134"); {area} = the example's community area.
{example}, one line: `{address}, {area}: {type in lower case}{, N homes when units is set}, {cost} reported cost, general contractor {first name in gc}, {stage}.` Cost in words: "$850,000" under $1 million, one decimal under $100 million ("$6.3 million", "$71.0 million"), whole millions from $100 million ("$245 million"), two decimals for billions ("$1.25 billion"). Stage words: "Certificate Of Occupancy Pending (...)" = partial occupancy approved; "Inspections (...)" or "Inspections" = inspections under way; "Permit Issued (...)" = permit issued.
Picking {example}: from the nearFinish array, the project in the prospect's own community area (CRM `area`), else the largest; the follow-up uses the next one on that list, never the first email's (CRM `firstExample` holds its permit number).
Example: `250 E Superior St, Near North Side: renovation, $6.3 million reported cost, general contractor Berglund Construction Company, partial occupancy approved.`

Subject:
```
Who to call for a final clean in {area}
```

Fields for the job block, from the {example} pick: {address}, {area}, {builder} (first name in gc), {stage} (the stage words above), {work} = `{type in lower case}{, N homes when units is set}, {cost} reported cost`. {fetched} = counts.fetched with a thousands comma; {topGC} and {topGCJobs} = counts.topGCs[0].name and .projects.

Body:
```
Hi {Company} team,

You advertise post-construction cleaning, so here is a lead from Chicago's building permits:

Job: {address}, {area}
Work: {work}
Stage: {stage}
Who to call: {builder}, the general contractor

Not a job from us or a bid invite: you call the builder's office and ask to bid the final clean.

Every Monday we cut {fetched} permit records to the {projects} open commercial and apartment jobs of $500,000 or more, each with its builder, the {near} with partial occupancy on their own tab. One builder, {topGC}, has {topGCJobs} of them. Web app, Excel file, and a pitch kit with an email for builders. $29 a month, cancel any time.

This week's free sample: https://proofnotfluff.com/chicago-construction-cleaning-leads/

ProofNotFluff
680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611

This is an advertisement for ProofNotFluff's paid list, sent to businesses that advertise post-construction cleaning. We send at most one follow-up. Not interested? Reply "no thanks" and we won't email you again.
```

## What the buyer gets (the crew builds it before the first send)
- Every open project that passes the filter (Excel and Google Sheets): address, community area, type, scope, reported cost, units, stage, issue date and general contractor; new permits since last week flagged; near-finish projects on their own tab.
- The pitch kit from the page: a one-page capability sheet template and an email to builders they can adapt.
- The City of Chicago data disclaimer the City's terms require.

## Follow-up (Todd, Oct 18: "Yes, one follow-up")
Sent once, 5 business days after the first email, as a reply in the same thread, only to businesses that have not replied, opted out or bounced. {projects} = counts.kept and {near} = counts.nearFinish in that Monday's permits/chicago/sample.json (counts, never the short projects or nearFinish arrays). Contact-form prospects get no follow-up (there is no thread).

Body:
```
Hi {Company} team,

Another lead from this week's Chicago list:

Job: {address}, {area}
Work: {work}
Stage: {stage}
Who to call: {builder}, the general contractor

Same idea: call the builder's office and ask to bid the final clean, or send the short builder email from the pitch kit.

The list has {projects} jobs like this, {near} with partial occupancy approved, updated every Monday, $29 a month. Free sample: https://proofnotfluff.com/chicago-construction-cleaning-leads/

If it isn't a fit, reply "no thanks" and we won't email you again.

ProofNotFluff
680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611

This is an advertisement for ProofNotFluff's paid list. This is our last email unless you write back.
```


## Review verdicts
(email/COPY_REVIEW.md; newest last)
- Oct 18, 2026, round 1 (fresh reviewer): FAIL, 3.50. The example sat at the end of a long paragraph with no format or picking rule, two links, a filler opener, a bump-only follow-up. Rewritten: the job first, one link, a format and picking rule for {example}, a follow-up with a new job.
- Oct 18, 2026, round 2 (fresh reviewer): PASS, 4.75. Applied: subject without "A" (vowel areas), thousands commas, a full cost-wording rule, the CRM area field named, the follow-up states the price.
- Oct 19, 2026 (Todd asked whether readers can tell these are leads to pursue): two cold-reader tests on the filled emails both read the subject and opener as a job or bid invite and would delete. An independent B2B cold-email marketer scored clarity 2 of 5 and objection handling 1 of 5, and rewrote: subject "Who to call for a final clean in ...", the job as labeled lines with "Who to call", an explicit "Not a job from us or a bid invite" line, and the scale line that answers "permits are free" and "I have my GCs". Applied as written; fresh cold readers re-test before the batch.
- Oct 19, 2026, re-test: two fresh cold readers on the rewritten emails both answered "No" to reading it as a job offer and both named the next step (call the builder's office and ask to bid the final clean). PASS on clarity. Every reader in both rounds questioned the Cheyenne, WY address on a local list; Todd replaced it the same morning with his iPostal1 Chicago mailbox (footer updated).
