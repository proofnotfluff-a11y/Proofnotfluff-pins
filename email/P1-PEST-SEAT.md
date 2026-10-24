# P1: pest control cold email for the founding seat (Chicago Pest Daily List, $149 a month, 3 seats)

Todd's go: Oct 23, 2026, 2:56 pm (the merged template), Oct 24, 10:40 am (subject "{n} Chicago restaurant inspections cited pests this week"; {n} the 7-day count only, never the daily file's total). Kill rule: 0 seats from 100 delivered emails plus 2 follow-ups by Nov 30 (coo/DECISIONS-2026-10-24.md). Nothing sends without Todd's "send" in a live chat (email/SEND_RULES.md).

Rules the copy gate checks (`python3 tools/copy_gate.py --pest-templates` and `--pest data/work/pest_drafts.json`):
- {n} is `pestLast7.restaurantInspections` in permits/inspections-chicago/daily.json: failed or conditional inspections at places the City types Restaurant, dated in the 7 days ending on the newest date the City has published. Never `counts.places`, `counts.pests`, the 14-day chart total or `seat.places14`. The file must be at most 1 day old on the draft day.
- {neighborhood} is one of `pestLast7.areas` (community areas with such an inspection in those 7 days).
- n = 1 uses the singular template of each step (Variant S); n = 0 holds the email to a morning with a count of 1 or more.
- {neighborhood} reads "the Loop" for the Loop (the gate maps it back to the City's area name).
- Copy review round 1 (Oct 24): FAIL at 4.0; its rewrites applied here with "no lock-in" in place of "no contract" (Todd, Oct 24, 11:52 am). "Recorded", not "posted": the count is by the City's inspection date.
- "all 3 seats are open" only while site/pages.json seat.taken is 0; "most of them" only while seat.coverage14 is 50% or more.
- Body under 75 words, plain text, no link, no price, no business named, no dash, opens "Hi {first},", ends with the question. The sender appends the footer (tools/pnf_rules.py FOOTER).
- Wording: "with a pest violation" (Oct 24 build session and Legal desk): on Oct 24, 7 of the 22 inspections carried City code 38 for a door gap, a propped door or an incomplete pest log, with no insect or rodent noted, so "cited rodents or insects" would overstate it. Legal desk fix 13 recommends the subject "{n} Chicago restaurant inspections with a pest violation this week" for the same reason; the approved subject stays until Todd decides.

What a yes gets: one free morning of the named list, sent by Todd as a reply under the Legal desk's conditions and exact header, row and footer text (legal/reviews/2026-10-24-pest-seat.md, "Free test day"). Nothing named goes out before that review is cleared and Todd says send.

### T1
Product: chicago-pest-seat
Step: first
Variant: A
Subject: {n} Chicago restaurant inspections cited pests this week
Body:
```text
Hi {first},

This week the City of Chicago recorded {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

Each morning I put the new ones on a private page by name and street, with a listed phone number for most of them. I'm opening seats on that daily list to at most 3 Chicago pest companies, and all 3 seats are open.

Want tomorrow's list free to test?
```

### T1S
Product: chicago-pest-seat
Step: first
Variant: S
Subject: 1 Chicago restaurant inspection cited pests this week
Body:
```text
Hi {first},

This week the City of Chicago recorded 1 failed or conditional restaurant inspection with a pest violation, in {neighborhood}.

Each morning I put the new ones on a private page by name and street, with a listed phone number for most of them. I'm opening seats on that daily list to at most 3 Chicago pest companies, and all 3 seats are open.

Want tomorrow's list free to test?
```

### T2
Product: chicago-pest-seat
Step: followup1
Variant: A
Subject: Re: {first_subject}
Body:
```text
Hi {first},

A fresh count: in the last 7 days the City recorded {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

The list also shows each place's City violation codes and how many times it failed in the last 90 days, so you know which ones to call first. All 3 seats are still open, no lock-in.

Want tomorrow's list free to test?
```

### T2S
Product: chicago-pest-seat
Step: followup1
Variant: S
Subject: Re: {first_subject}
Body:
```text
Hi {first},

A fresh count: in the last 7 days the City recorded 1 failed or conditional restaurant inspection with a pest violation, in {neighborhood}.

The list also shows each place's City violation codes and how many times it failed in the last 90 days, so you know which ones to call first. All 3 seats are still open, no lock-in.

Want tomorrow's list free to test?
```

### T3
Product: chicago-pest-seat
Step: followup2
Variant: A
Subject: Re: {first_subject}
Body:
```text
Hi {first},

Last note from me. In the last 7 days the City recorded {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

Miss a morning and nothing is lost: the list keeps the last 14 days. If it's not a fit, no need to reply and you won't hear from me again.

Want tomorrow's list free to test?
```

### T3S
Product: chicago-pest-seat
Step: followup2
Variant: S
Subject: Re: {first_subject}
Body:
```text
Hi {first},

Last note from me. In the last 7 days the City recorded 1 failed or conditional restaurant inspection with a pest violation, in {neighborhood}.

Miss a morning and nothing is lost: the list keeps the last 14 days. If it's not a fit, no need to reply and you won't hear from me again.

Want tomorrow's list free to test?
```

## Review verdicts
- Copy review round 1, Oct 24, 2026: FAIL, average 4.0 (value before the ask 3, follow-up 3). Rewrites applied as above; round 2 pending.
