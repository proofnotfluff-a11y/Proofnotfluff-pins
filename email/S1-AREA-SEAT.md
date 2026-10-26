# S1: cleaning company cold email for the area seats (Chicago Construction Cleaning Leads, one company per area)

Todd's go to build and draft: Oct 26, 2026, 8:24 am (coo/DECISIONS-2026-10-26.md). Not approved for sending: these templates are not in email/approved_templates.json, so the standing send rule does not cover them and nothing sends until Todd approves the wording in a live chat and says send (email/SEND_RULES.md, CONSTITUTION 2).

Rules the gate checks (`python3 tools/copy_gate.py --seat-templates`, run by tools/check_repo.py; tools/seat_gate.py):
- Every cold email rule of the cleaning templates (pnf_rules.copy_problems): under 75 words, plain text, no link, no price or subscription pitch, no dash, opens "Hi {first},", ends with the question, names the builder, the street and the lead's downstream stage. {first} is a named decision maker (or pnf_rules owner_read_inbox); the sender appends the footer.
- The lead is a Chicago downstream lead (permits/downstream/gc_leads.json) whose community area (permits/downstream/gc_areas.json) is inside the seat area {area} names, and that seat is not held (site/area_seats.json held). A follow-up names a different lead in the same area.
- {area} is the seat's name exactly as site/area_seats.json writes it ("our Loop and South Loop area").
- {open} is that seat's open count in permits/chicago/area_week.json, and the file is at most 8 days old on the send day. No other count appears.
- "still open" (T5) only while that seat is not held.
- Pick the seat for the prospect's own area: the community area of the prospect's business address, else the area of most of the Chicago jobs on its website, else no seat email to that prospect.

What a yes gets: the area's 5 newest projects with the builder on each, sent by Todd as a reply only after his word in chat (named lists to people who replied yes always wait for him; CONSTITUTION 2), under the same conditions as the $29 list's free sample. Nothing named goes out before the Legal desk review of this offer is cleared.

### T1 partial occupancy
Product: chicago-cleaning-area-seats
Step: first
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
Body:
```text
Hi {first},

Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

It is one of {open} open jobs in our {area} area this week, and one cleaning company will get the only copy of that list.

Want its 5 newest free to judge it?
```

### T2 inspections
Product: chicago-cleaning-area-seats
Step: first
Stage: Inspections Under Way
Subject: Final clean on {street}
Body:
```text
Hi {first},

Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

It is one of {open} open jobs in our {area} area this week, and one cleaning company will get the only copy of that list.

Want its 5 newest free to judge it?
```

### T3 certificate of occupancy
Product: chicago-cleaning-area-seats
Step: first
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
Body:
```text
Hi {first},

The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

It is one of {open} open jobs in our {area} area this week, and one cleaning company will get the only copy of that list.

Want its 5 newest free to judge it?
```

### T4 follow-up, partial occupancy
Product: chicago-cleaning-area-seats
Step: second
Stage: Partial Occupancy Approved
Subject: Re: {first_subject}
Body:
```text
Hi {first},

One more in our {area} area: {gc} is at partial occupancy approved on the {value} {kind} build on {street}.

The seat for that area is still open. Whoever takes it is the only cleaning company we send those jobs to.

Should I send the 5 newest so you can see?
```

### T5 follow-up, inspections
Product: chicago-cleaning-area-seats
Step: second
Stage: Inspections Under Way
Subject: Re: {first_subject}
Body:
```text
Hi {first},

One more in our {area} area: {gc} has city inspections under way on the {value} {kind} project on {street}.

The seat for that area is still open. Whoever takes it is the only cleaning company we send those jobs to.

Should I send the 5 newest so you can see?
```

### T6 last note
Product: chicago-cleaning-area-seats
Step: third
Subject: Re: {first_subject}
Body:
```text
Hi {first},

Last note from me. If that area is not where your crews work, which part of Chicago is?

I can send that area's 5 newest projects instead. Worth a look?
```
