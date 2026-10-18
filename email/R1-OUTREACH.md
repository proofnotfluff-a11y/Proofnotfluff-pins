# R1: Chicago Restaurant Inspection Leads outreach (drafted Oct 2026, nothing sent)

Product: Chicago Restaurant Inspection Leads, $39 a month (launches/chicago-restaurant-inspection-leads.md). Nothing in this file is sent until every box of design/LAUNCH_CHECKLIST.md is ticked and Todd says go.

## Who
- Chicago-area pest control companies, kitchen hood and exhaust cleaners, and grease trap and drain companies whose own websites advertise commercial or restaurant work.
- The prospect list lives in the private CRM (coo/LEADS_DESK.md), never in this public repo: business name, website, a business email or contact form read on the company's own website (never a directory), the page it was read on and the date. No person's name, and no personal-looking address (an address that is a person's name goes to the contact form instead).

## Rules (same legal base as email/A1-OUTREACH.md)
- Sending (Todd, Oct 18: "You send after my yes"): the outreach run sends each checked batch from hello@proofnotfluff.com in Gmail on the web, only after Todd says send in chat for that batch (coo/LEADS_DESK.md). Follow-up (Todd, Oct 18: "Yes, one follow-up"): one short follow-up 5 business days after the first email, in the same thread, never to anyone who replied, opted out or bounced. Nothing more after it.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, the postal address "1718 Capitol Ave, Cheyenne, WY 82001" in the footer, and a working opt-out (reply "no thanks"); honor it and never email that address again.
- Every fact comes from that morning's members' list (tools/rest_leads.py on the City's Food Inspections data). {fields} are filled the morning the drafts are made from permits/inspections-chicago/rest-sample.json counts and examples (the table under "The emails"); a draft with a leftover brace, or a number that differs from the list, is not made.
- The example record gives the facility type, community area, the City's result, date, inspection type and violation code, and never the business name or street address (the same line as the free page): never "dirty", "unsafe", "infested" or any judgment. Pick an example whose newest City result is still the one quoted (if the place passed a re-inspection since, pick another).
- No invented people, no fake urgency, no claim that any business works with us.
- For a contact-form prospect, paste the whole body, including "ProofNotFluff", the postal address and the opt-out sentence, and give the ProofNotFluff mailbox as the reply address. Skip any form that says it is not for sales, solicitations or vendors.
- Any reply that asks to stop, in any words, is an opt-out. Set doNotEmail true on the business in the CRM (coo/LEADS_DESK.md) within 10 business days, and check it before every send.

## The emails (one template for all three trades; {fields} from that Monday's permits/inspections-chicago/rest-sample.json)

Fields by trade:

| Trade | {service} (opener) | {count} | {cited} | {trade_line} | {service_ad} |
|---|---|---|---|---|---|
| Pest control | do commercial pest control | counts.byCat.pests | pests | {count} places had a pest violation in the last 30 days | commercial pest control |
| Hood and exhaust cleaning | clean commercial kitchen hoods | counts.byCat.hood | hood or exhaust | {count} places were cited for a hood, filter, exhaust or grease problem in the last 30 days | kitchen hood cleaning |
| Grease trap and drains | service restaurant grease traps | counts.byCat.drain | grease trap or drain | {count} places were cited for waste water or a grease trap or drain problem in the last 30 days | grease trap service |

A trade whose {count} is under 2 gets no batch that week (the subject and trade line would read wrong); its prospects wait for the next Monday.

- {opening} = counts.opening.
- {example}: `a {type in lower case, or "food business" when type is "Not given"} in {area} that {"failed" when result is Fail, "passed with conditions" when Pass w/ Conditions} a {inspection type in plain words} on {date as Oct 16}, cited for {trade phrase}{", plus " and the other categories in lower case joined as "a and b", when there are any}`. Trade phrase: "pests", "a hood or exhaust problem", "a grease trap or drain problem". Inspection type in plain words: Canvass = "routine inspection", Complaint and Short Form Complaint = "complaint inspection", any Re-Inspection = "re-inspection", License = "license inspection", else the City's words in lower case followed by "inspection". Example: "a restaurant in South Lawndale that failed a complaint inspection on Oct 14, cited for a hood or exhaust problem, plus pests and cleaning". The first record in examples.flagged, then examples.repeat, whose categories match the trade. Never a name or address: these places failed or passed with conditions.
- {opening_example}: `{name}, {address}, {area}, passed its license inspection on {date as Oct 16}`. From examples.opening only (Pass results, which the free page already names). Never a place with a failed result.
- Follow-up fields come from the newest Monday file on the day it is sent: that week's {trade_line}, and the first examples.opening record the first email did not name ({name}, {address}, {area}, {date}).

Subject:
```
{count} Chicago places cited for {cited}
```

Body:
```
Hi {Company} team,

Your site says you {service} in the Chicago area. On this week's list of City food inspections, {trade_line}.

One was {example}. Members get its name and address.

{opening} places also had the inspection Chicago does before it issues a food license, and many may be picking vendors now. One: {opening_example}.

Every Monday the list names every place, with its address, inspection history, a map, an Excel file and a call script. It is $39 a month, cancel any time.

This week's free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is an advertisement for ProofNotFluff's paid list, sent to businesses that advertise {service_ad}. We send at most one follow-up. Not interested? Reply "no thanks" and we won't email you again.
```
{service_ad}: commercial pest control, kitchen hood cleaning or grease trap service.

## Follow-up (Todd, Oct 18: "Yes, one follow-up")
Sent once, 5 business days after the first email, as a reply in the same thread, only to businesses that have not replied, opted out or bounced. Fields from that Monday's file, as above. Contact-form prospects get no follow-up (there is no thread).

Body:
```
Hi {Company} team,

One more from Monday's Chicago list, a place that just passed its license inspection: {name}, {address}, {area}, on {date as Oct 16}. A new license often means vendors are being picked for the first time.

On the list, {trade_line}, and every place is named with its address and City inspection history. It updates every Monday and is $39 a month. Free sample: https://proofnotfluff.com/chicago-restaurant-inspection-leads/

If it isn't a fit, reply "no thanks" and we won't email you again.

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is an advertisement for ProofNotFluff's paid list. This is our last email unless you write back.
```


## Review verdicts
(email/COPY_REVIEW.md; newest last)
- Oct 18, 2026, round 1 (fresh reviewer): FAIL, 3.40. Filler opener, an unnamed failed place gave the reader nothing to act on, two links, a bump-only follow-up, a sample example that matched no record. Rewritten as one template for all three trades with a named, passing license-inspection place, one link, and a follow-up with a new record.
- Oct 18, 2026, round 2 (fresh reviewer): FAIL, 4.35. Applied: a natural example line ("a restaurant in Lake View that failed a complaint inspection on Oct 16, with pests and cleaning cited"), the follow-up leads with a named place that just passed its license inspection and states the price, {service_ad} per trade, no batch for a trade under 2. Open: tools/rest_leads.py must carry each example's latest result so the "newest result still the one quoted" rule can be checked; the builder run does it before the first restaurant batch (Oct 26).
- Oct 18, 2026, round 3 (fresh reviewer): FAIL, 4.40, nothing under 4. Applied: a shorter body (about 135 words), a shorter subject, the example cited for the trade first in plain inspection words, the follow-up from the newest Monday file. Next: a fresh reviewer re-checks items 4, 6, 7 and 10 before the first restaurant batch (Oct 26).
