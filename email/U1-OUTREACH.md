# U1 outreach: Austin construction cleaning leads (Oct 18, 2026)

Todd, Oct 18, 4:24 pm: "Yes email outreach is our best marketing tactic and should prioritize. Ensured emails are independently reviewed as well and are crafted to convert at the highest quality using best practices." This file binds the outreach run (coo/LEADS_DESK.md Run 2) for the CRM product `austin-construction`. Every version of the copy below passes email/COPY_REVIEW.md before it is used; the review verdicts are at the end of this file.

## Who and what
- Who: Austin-area companies whose own sites advertise post-construction, construction, builder or final cleans (the list lives in the private CRM, never in this public repo; opt-outs are its doNotEmail field).
- Offer: the full weekly list at $29 a month, cancel any time, this week's list right after checkout (members' app and Excel file), then every Monday. Checkout is on the free sample page.
- Judge (plan file LEADS FOCUS): paying subscribers. 0 payers after 3 outreach weeks (about 120 emails) means rework or drop.

## Rules
- Sending: Claude sends each checked batch from hello@proofnotfluff.com in Gmail on the web, only after Todd says send in chat for that batch (coo/LEADS_DESK.md). One follow-up 5 business days later in the same thread, never to anyone who replied, opted out or bounced. Nothing more after it.
- CAN-SPAM: honest subject, the sender is ProofNotFluff, the postal address in the footer, the ad notice, and a working opt-out (reply "no thanks"), honored for good.
- Plain text only: no images, no tracking pixels, no link shorteners, no attachments, and one link per email (the free sample page, which carries the checkout).
- Every fact comes from that Monday's permits/austin/sample.json, read the morning the drafts are made. A draft with a leftover brace, or a number or project that differs from that file, is not made.
- No invented people, no fake urgency, no claim that any builder works with us, no person's name anywhere.

## Fields (all from that Monday's permits/austin/sample.json)
- {Company}: the business name as its own site prints it, without "LLC", "Inc." and the like.
- {projects}: counts.kept.
- {underway}: counts.byStage["Work under way"] plus counts.byStage["Near finish"] (projects past the permit-issued stage).
- {example}: one project, picked by the rule below, written on one line as:
  `{address}, {ZIP}: {type in lower case}{, N homes when units is set}, {valuation} in City valuation, general contractor {builder}, {stage in lower case}.`
  Valuation as the free page writes it, in words: "$365 million" from $100 million up, "$71.0 million" or "$4.0 million" (one decimal) under $100 million, "$1.25 billion" (two decimals) for billions. The builder is the first name in the project's gc list, as printed. The address is printed without any "(+N more)".
  Example: `2915 E Cesar Chavez St, 78702: new construction, 309 homes, $100 million in City valuation, general contractor JLB Builders, LLC, work under way.`
- {zip}: the example project's ZIP code.

### Picking {example}
From the projects and nearFinish arrays of that Monday's file (one list, de-duplicated by permit):
1. Leave out any "Remodel or addition" or "Finish-out" over $100 million (Austin repeats a campus or tower valuation on each building's or floor's permit; it reads as a mistake in a cold email) and any project whose valuation ends in a stray digit (counts.oddCosts).
2. Keep the projects on the prospect's side of the metro, by the project's ZIP and the prospect's own town or neighborhood (CRM `area`):
   - North: 78613, 78626, 78628, 78634, 78641, 78660, 78664, 78665, 78681, 78717, 78726, 78727, 78728, 78729, 78730, 78750, 78753, 78757, 78758, 78759 (Round Rock, Cedar Park, Leander, Pflugerville, Georgetown, Hutto, north Austin)
   - Central: 78701, 78703, 78705, 78722, 78723, 78731, 78751, 78752, 78756 (downtown, central Austin)
   - East: 78702, 78721, 78724, 78725, 78653, 78621, 78617 (east Austin, Manor, Elgin, Del Valle)
   - South: 78704, 78741, 78744, 78745, 78747, 78748, 78749, 78610, 78640, 78666, 78602, 78676 (south Austin, Buda, Kyle, San Marcos, Bastrop, Wimberley)
   - West: 78620, 78732, 78733, 78734, 78735, 78736, 78738, 78746 (west Austin, Lakeway, Bee Cave, Dripping Springs)
   A prospect whose area fits none of these, or whose side has no project, uses Central.
3. On that side: Near finish first, then Work under way, then Permit issued; within a stage, the largest valuation.
4. The follow-up uses the next project on the same ordered list, never the one in the first email (the CRM's `firstExample` field holds the first email's master permit). If the prospect's side has no next project, the follow-up uses the first Central project not already sent to that prospect.

## First email

Subject:
```
Austin job in {zip} that will need a final clean
```

Body:
```
Hi {Company} team,

Your site lists post-construction cleaning, so here is an Austin job that will need a final clean:

{example}

It is one of {projects} open Austin commercial and apartment projects of $500,000 or more on this week's list, each with its general contractor. {underway} already have work under way.

Every Monday we turn the City of Austin's building permits into that list, closest to a final clean first, in a web app and an Excel file with a ZIP code filter. It is $29 a month, cancel any time.

This week's free sample: https://proofnotfluff.com/austin-construction-cleaning-leads/

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is an advertisement for ProofNotFluff's paid list, sent to businesses that advertise post-construction cleaning. We send at most one follow-up. Not interested? Reply "no thanks" and we won't email you again.
```

## Follow-up (one, 5 business days later, as a reply in the same thread)

Fields from that Monday's file; {example} is the next project per the picking rule, different from the first email's.

Body:
```
Hi {Company} team,

One more from this week's Austin list, in case it helps:

{example}

The list has {projects} open projects with the general contractor on each, closest to a final clean first. It updates every Monday and is $29 a month. Free sample: https://proofnotfluff.com/austin-construction-cleaning-leads/

If it isn't a fit, reply "no thanks" and we won't email you again.

ProofNotFluff
1718 Capitol Ave, Cheyenne, WY 82001

This is an advertisement for ProofNotFluff's paid list. This is our last email unless you write back.
```

## Contact-form version (no follow-up)
The first email's body without the "Hi {Company} team," line, the footer kept, sent from the business's own contact form with "ProofNotFluff" and hello@proofnotfluff.com.

## Review verdicts
(email/COPY_REVIEW.md; newest last)
- Oct 18, 2026, round 1 (fresh reviewer): FAIL, 4.60 (bar: above 4.6). Fixed: subject names the job's ZIP, tower and campus finish-outs and remodels over $100 million left out as examples, paragraphs 3 and 4 shortened, one-decimal valuations under $100 million, no "near you" when the prospect's side has no job.
- Oct 18, 2026, round 2 (fresh reviewer): PASS, 4.75. Applied: the subject says why a cleaner cares, the follow-up states the price, a West prospect's follow-up falls back to Central.
