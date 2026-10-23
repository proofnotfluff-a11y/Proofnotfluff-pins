# Outreach templates (outreach-drafter step 4 reads this; nothing loads it before a run)

Pick by the prospect's trade_vertical (blank means commercial_cleaning), the lead's stage and the prospect's test arm. A template without a Trade line is commercial_cleaning; without a Variant line it is A. tools/copy_gate.py renders every template here on each push and preflight; pnf_rules.TRADE_VERTICALS says which products and stages each vertical may use.

Test 1 (Todd, Oct 22, 2026, live chat: "A and B, test 1"): A is the bare observation and permission ask; B adds one who-and-why sentence first. Nothing else differs. The ask (Todd, Oct 22, 7:57 pm, new funnel) is permission for the free Monday email, one line on every template, so a yes joins the Monday list (email/M1-MONDAY.md); no test 1 email went out with the old ask. `python3 tools/copy_gate.py --assign` prints the template id (T2-B) each match must use; every draft carries it as `variant`, and the gate checks the arm and the fixed words. Evidence: the growth research doc, Oct 22.

### T1 partial occupancy
Variant: A
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
```text
Hi {first},

Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

Want me to send you jobs like this free each Monday?
```
### T1 partial occupancy, variant B
Variant: B
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

Want me to send you jobs like this free each Monday?
```
### T2 inspections
Variant: A
Stage: Inspections Under Way
Subject: Final clean on {street}
```text
Hi {first},

Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

Want me to send you jobs like this free each Monday?
```
### T2 inspections, variant B
Variant: B
Stage: Inspections Under Way
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

Want me to send you jobs like this free each Monday?
```
### T3 certificate of occupancy
Variant: A
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
```text
Hi {first},

The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

Want me to send you jobs like this free each Monday?
```
### T3 certificate of occupancy, variant B
Variant: B
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

Want me to send you jobs like this free each Monday?
```
### T4 exterior turnkey
Variant: A
Trade: exterior_turnkey
Stage: Partial Occupancy Approved
Subject: Exterior work on {street}
```text
Hi {first},

Saw that {gc} is at partial occupancy with the city on the {value} {kind} build on {street}. That is usually when pressure washing, window washing and lot striping get bid before final sign-off.

Want me to send you jobs like this free each Monday?
```
### T4 exterior turnkey, variant B
Variant: B
Trade: exterior_turnkey
Stage: Partial Occupancy Approved
Subject: Exterior work on {street}
```text
Hi {first},

I follow city building permits for exterior cleaning crews. Saw that {gc} is at partial occupancy with the city on the {value} {kind} build on {street}. That is usually when pressure washing, window washing and lot striping get bid before final sign-off.

Want me to send you jobs like this free each Monday?
```

## Step 2 buyer types (Todd, Oct 22, 2026, 10:55 pm, live chat: "Let's go with your recommendations")
Same test 1 rules: A is the observation and the Monday ask, B adds one who-and-why sentence first, nothing else differs. pnf_rules.TRADE_VERTICALS limits each to its stages, work types and valuations: window_cleaning new builds of $5M or more, dumpster_rental jobs under $5M under inspection, security new builds of $20M or more. Subjects name the job, never a service, so they do not read like a quote request (checker round 1, Oct 22). {kind} is pnf_rules.kind_display of the City scope (townhouse, apartment, school, hotel, office, else building), and the gate checks it; these templates say "{kind} project" so the fallback reads "building project".

### T5 window cleaning partial occupancy
Variant: A
Trade: window_cleaning
Stage: Partial Occupancy Approved
Subject: The job on {street}
```text
Hi {first},

{gc} has partial occupancy from the city on the new {value} {kind} project on {street}. Space turns over in stages from here, so the final glass clean is close if it is not already awarded.

Want me to send you jobs like this free each Monday?
```
### T5 window cleaning partial occupancy, variant B
Variant: B
Trade: window_cleaning
Stage: Partial Occupancy Approved
Subject: The job on {street}
```text
Hi {first},

I track city building permits and pass window cleaners the jobs worth bidding. {gc} has partial occupancy from the city on the new {value} {kind} project on {street}. Space turns over in stages from here, so the final glass clean is close if it is not already awarded.

Want me to send you jobs like this free each Monday?
```
### T6 window cleaning inspections
Variant: A
Trade: window_cleaning
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

Saw the city has inspections under way on the new {value} {kind} project {gc} is running on {street}. The final glass clean is likely a long way off, but getting on the GC's list early helps.

Want me to send you jobs like this free each Monday?
```
### T6 window cleaning inspections, variant B
Variant: B
Trade: window_cleaning
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

I track city building permits and pass window cleaners the jobs worth bidding. Saw the city has inspections under way on the new {value} {kind} project {gc} is running on {street}. The final glass clean is likely a long way off, but getting on the GC's list early helps.

Want me to send you jobs like this free each Monday?
```
### T7 dumpster rental inspections
Variant: A
Trade: dumpster_rental
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

Saw the city has inspections under way on the {value} {kind} project {gc} is running on {street}. Jobs like this usually keep filling cans right up to the final cleanout.

Want me to send you jobs like this free each Monday?
```
### T7 dumpster rental inspections, variant B
Variant: B
Trade: dumpster_rental
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

I track city building permits and pass haulers the jobs worth a call. Saw the city has inspections under way on the {value} {kind} project {gc} is running on {street}. Jobs like this usually keep filling cans right up to the final cleanout.

Want me to send you jobs like this free each Monday?
```
### T8 security inspections
Variant: A
Trade: security
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

Saw the city has inspections under way on the new {value} {kind} project {gc} is running on {street}. Once a building is closed in, copper and gear start to walk, and GCs often add towers or guards.

Want me to send you jobs like this free each Monday?
```
### T8 security inspections, variant B
Variant: B
Trade: security
Stage: Inspections Under Way
Subject: The job on {street}
```text
Hi {first},

I track city building permits and pass site security companies the jobs worth a call. Saw the city has inspections under way on the new {value} {kind} project {gc} is running on {street}. Once a building is closed in, copper and gear start to walk, and GCs often add towers or guards.

Want me to send you jobs like this free each Monday?
```
### T9 security partial occupancy
Variant: A
Trade: security
Stage: Partial Occupancy Approved
Subject: The job on {street}
```text
Hi {first},

{gc} got partial occupancy approved by the city on the new {value} {kind} project on {street}. The City now allows people in while work wraps up, which often changes what site security covers.

Want me to send you jobs like this free each Monday?
```
### T9 security partial occupancy, variant B
Variant: B
Trade: security
Stage: Partial Occupancy Approved
Subject: The job on {street}
```text
Hi {first},

I track city building permits and pass site security companies the jobs worth a call. {gc} got partial occupancy approved by the city on the new {value} {kind} project on {street}. The City now allows people in while work wraps up, which often changes what site security covers.

Want me to send you jobs like this free each Monday?
```
