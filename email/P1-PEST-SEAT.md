# P1: pest control cold email for the founding seat (Chicago Pest Daily List, $149 a month, 3 seats)

Todd's go: Oct 23, 2026, 2:56 pm (the merged template), Oct 24, 10:40 am (subject "{n} Chicago restaurant inspections cited pests this week"; {n} the 7-day count only, never the daily file's total). Kill rule: 0 seats from 100 delivered emails plus 2 follow-ups by Nov 30 (coo/DECISIONS-2026-10-24.md). Nothing sends without Todd's "send" in a live chat (email/SEND_RULES.md).

Rules the copy gate checks (`python3 tools/copy_gate.py --pest-templates` and `--pest data/work/pest_drafts.json`):
- {n} is `pestLast7.restaurantInspections` in permits/inspections-chicago/daily.json: failed or conditional inspections at places the City types Restaurant, dated in the 7 days ending on the newest date the City has published. Never `counts.places`, `counts.pests`, the 14-day chart total or `seat.places14`. The file must be at most 1 day old on the draft day.
- {neighborhood} is one of `pestLast7.areas` (community areas with such an inspection in those 7 days).
- n = 1 uses the singular template (T1 Variant S).
- "all 3 seats are open" only while site/pages.json seat.taken is 0; "most of them" only while seat.coverage14 is 50% or more.
- Body under 75 words, plain text, no link, no price, no business named, no dash, opens "Hi {first},", ends with the question. The sender appends the footer (tools/pnf_rules.py FOOTER).
- Wording: "with a pest violation" (Oct 24 build session): on Oct 24, 1 of the 22 inspections was a City code 38 citation for a door gap with no rodents or insects seen, so "cited rodents or insects" would overstate it. The subject's "cited pests" names the City's pest code and stays.

What a yes gets: one free morning of the named list, sent by Todd as a reply after the Legal desk's conditions (legal/reviews/2026-10-24-pest-seat.md, "Free test day"). Nothing named goes out before that review is cleared and Todd says send.

### T1
Product: chicago-pest-seat
Step: first
Variant: A
Subject: {n} Chicago restaurant inspections cited pests this week
Body:
```text
Hi {first},

This week the City of Chicago posted {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

Each morning I pull the new ones, with a listed phone number for most of them. I'm opening that daily list to at most 3 Chicago pest companies, and all 3 seats are open.

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

This week the City of Chicago posted 1 failed or conditional restaurant inspection with a pest violation, in {neighborhood}.

Each morning I pull the new ones, with a listed phone number for most of them. I'm opening that daily list to at most 3 Chicago pest companies, and all 3 seats are open.

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

A fresh count: in the last 7 days the City posted {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

The daily list still has all 3 seats open. A free morning of it costs you nothing and shows the names, streets and phones.

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

Last note from me. This week the City posted {n} failed or conditional restaurant inspections with a pest violation, including one in {neighborhood}.

If a free morning of the named list would help, reply yes and it's yours. If not, no reply needed and I won't write again.
```


## Review verdicts
