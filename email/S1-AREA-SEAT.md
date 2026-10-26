# S1: cleaning company cold email for the area seats (Chicago Construction Cleaning Leads, one company per area)

Todd's go to build and draft: Oct 26, 2026, 8:24 am (coo/DECISIONS-2026-10-26.md). Not approved for sending: these templates are not in email/approved_templates.json, so the standing send rule does not cover them and nothing sends until Todd approves the wording in a live chat and says send (email/SEND_RULES.md, CONSTITUTION 2).

Rules the gate checks (`python3 tools/copy_gate.py --seat-templates`, run by tools/check_repo.py; tools/seat_gate.py):
- Every cold email rule of the cleaning templates (pnf_rules.copy_problems): under 75 words, plain text, no link, no price or subscription pitch, no dash, opens "Hi {first},", ends with the question, names the builder, the street and the lead's downstream stage. {first} is a named decision maker (or pnf_rules owner_read_inbox); the sender appends the footer.
- The lead is a Chicago downstream lead (permits/downstream/gc_leads.json) whose community area (permits/downstream/gc_areas.json) is inside the seat area {area} names, and that seat is not held (site/area_seats.json held). A follow-up names a different lead in the same area.
- {area} is the seat's name exactly as site/area_seats.json writes it ("the Loop and South Loop area"; cold readers, Oct 26: "our" read as if we owned the neighborhood).
- {open} is that seat's open count in permits/chicago/area_week.json, and the file is at most 8 days old on the send day. No other count appears (numbers inside a builder's name, the value and the street aside).
- Copy review round 1 (Oct 26): FAIL at 4.2; its rewrites applied here ("project" for every lead, "usually" on the certificate line, a shorter second paragraph, a clearer ask, the count in the follow-ups, a last note that lets the reader go). Copy review round 2 (Oct 26): FAIL 4.45; its rewrites applied ("projects" for jobs, "Builders at this stage", no unexplained "seat" in the follow-ups, a last note that asks which area). Legal desk fix 5 (Oct 26): "we will sell that area's list to one cleaning company only" and "the only cleaning company we sell that area's list to", since the City and other sellers have the same records.
- "has taken that area yet" (T4, T5) only while that seat is not held.
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

Noticed {gc} has partial occupancy approved by the city on the {value} {kind} project on {street}. That is usually when the final clean gets bid.

It is one of {open} open projects in the {area} area this week, and we will sell that area's list to one cleaning company only.

Want the 5 newest free to look over?
```

### T2 inspections
Product: chicago-cleaning-area-seats
Step: first
Stage: Inspections Under Way
Subject: Final clean on {street}
Body:
```text
Hi {first},

Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Builders at this stage usually line up the final clean soon.

It is one of {open} open projects in the {area} area this week, and we will sell that area's list to one cleaning company only.

Want the 5 newest free to look over?
```

### T3 certificate of occupancy
Product: chicago-cleaning-area-seats
Step: first
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
Body:
```text
Hi {first},

{gc} has a certificate of occupancy pending with the city on the {value} {kind} project on {street}. Final clean crews usually get picked right about now.

It is one of {open} open projects in the {area} area this week, and we will sell that area's list to one cleaning company only.

Want the 5 newest free to look over?
```

### T4 follow-up, partial occupancy
Product: chicago-cleaning-area-seats
Step: second
Stage: Partial Occupancy Approved
Subject: Re: {first_subject}
Body:
```text
Hi {first},

One more in the {area} area: {gc} has partial occupancy approved by the city on the {value} {kind} project on {street}.

No cleaning company has taken that area yet, and this week's list has {open} open projects on it. Whoever takes it is the only cleaning company we sell that area's list to.

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

One more in the {area} area: {gc} has city inspections under way on the {value} {kind} project on {street}.

No cleaning company has taken that area yet, and this week's list has {open} open projects on it. Whoever takes it is the only cleaning company we sell that area's list to.

Should I send the 5 newest so you can see?
```

### T6 last note
Product: chicago-cleaning-area-seats
Step: third
Subject: Re: {first_subject}
Body:
```text
Hi {first},

Last note from me. If the {area} area is not where your crews work, which part of Chicago is? I can send that area's 5 newest projects free instead.

If no part of Chicago fits, no reply needed and I will leave it there. Which area should I send?
```
