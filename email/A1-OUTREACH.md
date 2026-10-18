# A1 pre-sale: Chicago construction cleaning leads (Oct 17, 2026)

Why: Gemini's red team (Oct 17) and the COO agree that waiting for traffic is the bottleneck. This tests whether cleaning companies pay, not whether they join a waitlist. Todd, Oct 17, 2:22 pm: "let's move on what will make you confident. Let's not waste time on things that don't work."

## The test
- Who: 36 Chicago-area companies whose own sites advertise post-construction or construction cleaning (list kept privately in the live session's scratchpad and in Drive, never in this public repo).
- Offer: the full weekly list at $29 a month (the price on the leads page), cancel any time, this week's list right after checkout (members' page and Excel file), then every Monday.
- Pass: 2 or more paying companies within 10 days of the send. Fail: under 2. A fail kills the paid version and the page stays a free sample.
- Market check (read Oct 17): Chicago Cityscape sells Chicago permit newsletters with builder contacts at $125 a month; ConstructConnect Starter $129 a month per market (third-party guide, Oct 6, 2026); Dodge, Construction Monitor and BuildZoom are quote only.

## Rules
- Sending (Todd, Oct 18: "You send after my yes"): the outreach run sends each checked batch from hello@proofnotfluff.com in Gmail on the web, only after Todd says send in chat for that batch (coo/LEADS_DESK.md). Follow-up (Todd, Oct 18: "Yes, one follow-up"): one short follow-up 5 business days after the first email, in the same thread, never to anyone who replied, opted out or bounced. Nothing more after it.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, a valid postal address in the footer (Todd, Oct 17, 2:39 pm: "you can use 1718 Capitol Ave Cheyenne, WY 82001"), and a working opt-out (reply "no thanks"); honor it, and never email that address again.
- Every fact in the email comes from the week's members' list (the City of Chicago Building Permits dataset as filtered by tools/permits_chicago.py). {Company}, {permits}, {addresses}, {near} and {example} are filled from that list on the morning the drafts are made; every draft is checked for leftover braces, and the drafts are not made if any number differs from the list (Holdout QC, Oct 17: the first draft carried last week's numbers).
- No invented people, no fake urgency, no claim that any builder works with us.

## Reach plan (Todd, Oct 17, 4:19 pm, asked how to reach only the people who would buy; chose "Expand to every Chicagoland cleaner")
- The prospect list grows from 36 to every Chicago-area company whose own site advertises post-construction or construction cleaning, found from their public sites (no bought lists, no scraped personal emails: only a business address the company publishes, else its contact form).
- Each email names one near-finish or newest permit in or near the prospect's own part of town, checked against the week's list, so every message carries a real lead the reader can use.
- Weekly batches of about 40, made as Gmail drafts in hello@proofnotfluff.com and sent as the Sending line says, with the one follow-up; no adjacent-trade pages and no paid ads for now.
- Nothing sends until the launch checklist (launches/chicago-construction-cleaning-leads.md) is complete and Todd says go.

## The email (one per company; {fields} filled from the list)

Subject:
```
Chicago construction permits and their builders, every Monday
```

Body:
```
Hi {Company} team,

Your site says you do post-construction cleaning in the Chicago area, so this may be worth a minute.

Each week we pull the City of Chicago's building permits and list the open apartment and commercial jobs with a reported cost of $500,000 or more, with the general contractor on each. This week's list has {permits} open permits at {addresses} addresses. {near} of them already have partial occupancy approved by the City, which usually means the work under that permit is close to done. One example: {example}.

Free sample: https://proofnotfluff.com/chicago-construction-cleaning-leads/

The full list is $29 a month, cancel any time. You get this week's list right after checkout, then a new one every Monday:
https://proofnotfluff.gumroad.com/l/vpnaoq

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is a one-time advertisement for ProofNotFluff's paid list, sent to businesses that advertise post-construction cleaning. Not interested? Reply "no thanks" and we won't email you again.
```

## What the buyer gets (the crew builds it before the first send)
- Every open project that passes the filter (Excel and Google Sheets): address, community area, type, scope, reported cost, units, stage, issue date and general contractor; new permits since last week flagged; near-finish projects on their own tab.
- The pitch kit from the page: a one-page capability sheet template and an email to builders they can adapt.
- The City of Chicago data disclaimer the City's terms require.
