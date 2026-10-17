# A1 pre-sale: Chicago construction cleaning leads (Oct 17, 2026)

Why: Gemini's red team (Oct 17) and the COO agree that waiting for traffic is the bottleneck. This tests whether cleaning companies pay, not whether they join a waitlist. Todd, Oct 17, 2:22 pm: "let's move on what will make you confident. Let's not waste time on things that don't work."

## The test
- Who: 36 Chicago-area companies whose own sites advertise post-construction or construction cleaning (list kept privately in the live session's scratchpad and in Drive, never in this public repo).
- Offer: the full weekly list at $29 a month (the price on the leads page), cancel any time, first list within 2 days of joining, then every Monday.
- Pass: 2 or more paying companies within 10 days of the send. Fail: under 2. A fail kills the paid version and the page stays a free sample.
- Market check (read Oct 17): Chicago Cityscape sells Chicago permit newsletters with builder contacts at $125 a month; ConstructConnect Starter $129 a month per market (third-party guide, Oct 6, 2026); Dodge, Construction Monitor and BuildZoom are quote only.

## Rules
- Todd sends every email himself from proofnotfluff@gmail.com (no agent sends a message on his behalf). One email per company, no follow-up sequence unless Todd says so.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, a valid postal address in the footer (Todd, Oct 17, 2:39 pm: "you can use 1718 Capitol Ave Cheyenne, WY 82001"), and a working opt-out (reply "no thanks"); honor it, and never email that address again.
- Every fact in the email comes from the City of Chicago Building Permits dataset as pulled into permits/chicago/sample.json (refresh the numbers and the example on the Monday before sending).
- No invented people, no fake urgency, no claim that any builder works with us.

## The email (one per company; {fields} filled from the list)

Subject:
```
Chicago projects that need a final clean soon
```

Body:
```
Hi {Company} team,

Your site says you do post-construction cleaning{ in Area}, so this may be worth a minute.

Every Monday we pull the City of Chicago's building permits and list the open apartment and commercial projects over $500,000, with the general contractor on each. This week's list has 763 open projects. 8 of them already have partial occupancy approved by the City, which means the building is close to done. One example: a $2.5 million office renovation at 227 W Monroe St in the Loop, general contractor JC Anderson.

Free sample: https://proofnotfluff.com/chicago-construction-cleaning-leads/

The full list is $29 a month, cancel any time. Your first list arrives within 2 days, then every Monday:
{checkout link}

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is a one-time email to businesses that advertise post-construction cleaning. Not interested? Reply "no thanks" and we won't email you again.
```

## What the buyer gets (the crew builds it before the first send)
- Every open project that passes the filter (Excel and Google Sheets): address, community area, type, scope, reported cost, units, stage, issue date and general contractor; new permits since last week flagged; near-finish projects on their own tab.
- The pitch kit from the page: a one-page capability sheet template and an email to builders they can adapt.
- The City of Chicago data disclaimer the City's terms require.
