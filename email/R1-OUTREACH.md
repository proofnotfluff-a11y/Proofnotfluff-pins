# R1: Chicago Restaurant Inspection Leads outreach (drafted Oct 2026, nothing sent)

Product: Chicago Restaurant Inspection Leads, $39 a month (launches/chicago-restaurant-inspection-leads.md). Nothing in this file is sent until every box of design/LAUNCH_CHECKLIST.md is ticked and Todd says go.

## Who
- Chicago-area pest control companies, kitchen hood and exhaust cleaners, and grease trap and drain companies whose own websites advertise commercial or restaurant work.
- The prospect list lives outside this public repo (the live session's scratchpad, rest-prospects.csv): business name, website, a business email or contact form read on the company's own website (never a directory), the page it was read on and the date. No person's name, and no personal-looking address (an address that is a person's name goes to the contact form instead).

## Rules (same legal base as email/A1-OUTREACH.md)
- Sending (Todd, Oct 18: "You send after my yes"): the outreach run sends each checked batch from hello@proofnotfluff.com in Gmail on the web, only after Todd says send in chat for that batch (coo/LEADS_DESK.md). Follow-up (Todd, Oct 18: "Yes, one follow-up"): one short follow-up 5 business days after the first email, in the same thread, never to anyone who replied, opted out or bounced. Nothing more after it.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, the postal address "1718 Capitol Ave, Cheyenne, WY 82001" in the footer, and a working opt-out (reply "no thanks"); honor it and never email that address again.
- Every fact comes from that morning's members' list (tools/rest_leads.py on the City's Food Inspections data). {fields} are filled the morning the drafts are made; a draft with a leftover brace, or a number that differs from the list, is not made.
- The example record gives the facility type, community area, the City's result, date, inspection type and violation code, and never the business name or street address (the same line as the free page): never "dirty", "unsafe", "infested" or any judgment. Pick an example whose newest City result is still the one quoted (if the place passed a re-inspection since, pick another).
- No invented people, no fake urgency, no claim that any business works with us.
- For a contact-form prospect, paste the whole body, including "ProofNotFluff", the postal address and the opt-out sentence, and give the ProofNotFluff mailbox as the reply address. Skip any form that says it is not for sales, solicitations or vendors.
- Any reply that asks to stop, in any words, is an opt-out. Add the address and the company to a do-not-email column in rest-prospects.csv within 10 business days, and check that column before every send.

## The emails ({fields} from the list)

### Pest control
Subject:
```
Chicago restaurants with pest violations this month, every Monday
```
Body:
```
Hi {Company} team,

Your site says you do commercial pest control in the Chicago area, so this may be worth a minute.

Each week we pull the City of Chicago's food inspection records and list the restaurants and food stores whose inspection failed or passed with conditions, sorted by what the inspector cited. In the last 30 days, {pests} places had a pest violation (City violation 38 or a note naming pests), {pests_new} of them new on the list this week. One example from the list: {example}.

Free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

The full list is $39 a month, cancel any time: every place named, with its address, its City inspection history, a map, an Excel file and a short call script.
{checkout}

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is a one-time advertisement for ProofNotFluff's paid list, sent to businesses that advertise commercial pest control. Not interested? Reply "no thanks" and we won't email you again.
```

### Hood and exhaust cleaning
Subject:
```
Chicago restaurants cited for hood and ventilation this month
```
Body:
```
Hi {Company} team,

Your site says you clean commercial kitchen hoods in the Chicago area, so this may be worth a minute.

Each week we pull the City of Chicago's food inspection records and list the restaurants whose inspection failed or passed with conditions, sorted by what the inspector cited. In the last 30 days, {hood} places were cited for a hood, filter, exhaust or grease problem, most under City violation 56 (ventilation). We also list the {opening} places that had a City license inspection in the same 30 days, the inspection Chicago does before it issues a food license. One example: {example}.

Free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

The full list is $39 a month, cancel any time: every place named, with its address, its City inspection history, a map, an Excel file and a short call script.
{checkout}

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is a one-time advertisement for ProofNotFluff's paid list, sent to businesses that advertise kitchen hood cleaning. Not interested? Reply "no thanks" and we won't email you again.
```

### Grease trap and drains
Subject:
```
Chicago restaurants cited for grease traps and drains, every Monday
```
Body:
```
Hi {Company} team,

Your site says you service restaurant grease traps in the Chicago area, so this may be worth a minute.

Each week we pull the City of Chicago's food inspection records and list the restaurants whose inspection failed or passed with conditions, sorted by what the inspector cited. In the last 30 days, {drain} places were cited for waste water (City violation 52) or a grease trap or drain, and we list the {opening} places that had the license inspection Chicago does before it issues a food license. One example: {example}.

Free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

The full list is $39 a month, cancel any time: every place named, with its address, its City inspection history, a map, an Excel file and a short call script.
{checkout}

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is a one-time advertisement for ProofNotFluff's paid list, sent to businesses that advertise grease trap service. Not interested? Reply "no thanks" and we won't email you again.
```

{example} reads like: "a restaurant in West Elsdon, City result Fail on Oct 15, 2026, canvass inspection, violation 38 cited. Members see its name and address". {checkout} is the Gumroad link with utm tags, filled once Todd has created the product.

## Follow-up (Todd, Oct 18: "Yes, one follow-up")
Sent once, 5 business days after the first email, as a reply in the same thread, only to businesses that have not replied, opted out or bounced. {trade_line} matches the business's trade and comes from that Monday's permits/inspections-chicago/rest-sample.json: pest control "{pests} places had a pest violation in the last 30 days", hood and exhaust cleaning "{hood} places were cited for a hood, filter, exhaust or grease problem in the last 30 days", grease trap and drains "{opening} places had a City license inspection in the last 30 days".

Body:
```
Hi {Company} team,

Following up once on my note last week. Each Monday we list the Chicago restaurants and food stores whose City inspection failed or passed with conditions, sorted by what the inspector cited. On this week's list, {trade_line}.

Free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

If it isn't useful, reply "no thanks" and we won't email you again.

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001
```
