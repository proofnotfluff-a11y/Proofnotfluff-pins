# Outreach templates (outreach-drafter step 4 reads this; nothing loads it before a run)

Pick by the prospect's trade_vertical (blank means commercial_cleaning), the lead's stage and the prospect's test arm. A template without a Trade line is commercial_cleaning; without a Variant line it is A. tools/copy_gate.py renders every template here on each push and preflight; pnf_rules.TRADE_VERTICALS says which products and stages each vertical may use.

Test 1 (Todd, Oct 22, 2026, live chat: "A and B, test 1"): A is the bare observation and permission ask; B adds one who-and-why sentence first. Nothing else differs. `python3 tools/copy_gate.py --assign` prints the template id (T2-B) each match must use; every draft carries it as `variant`, and the gate checks the arm and the fixed words. Evidence: the growth research doc, Oct 22.

### T1 partial occupancy
Variant: A
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
```text
Hi {first},

Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

Mind if I send over the general contractor's direct contact details?
```
### T1 partial occupancy, variant B
Variant: B
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

Mind if I send over the general contractor's direct contact details?
```
### T2 inspections
Variant: A
Stage: Inspections Under Way
Subject: Final clean on {street}
```text
Hi {first},

Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

Want me to send the general contractor's direct contact details?
```
### T2 inspections, variant B
Variant: B
Stage: Inspections Under Way
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

Want me to send the general contractor's direct contact details?
```
### T3 certificate of occupancy
Variant: A
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
```text
Hi {first},

The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

Should I send you the general contractor's direct contact details?
```
### T3 certificate of occupancy, variant B
Variant: B
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
```text
Hi {first},

I follow city building permits for commercial cleaning crews. The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

Should I send you the general contractor's direct contact details?
```
### T4 exterior turnkey
Variant: A
Trade: exterior_turnkey
Stage: Partial Occupancy Approved
Subject: Exterior work on {street}
```text
Hi {first},

Saw that {gc} is at partial occupancy with the city on the {value} {kind} build on {street}. That is usually when pressure washing, window washing and lot striping get bid before final sign-off.

Want the general contractor's direct contact details?
```
### T4 exterior turnkey, variant B
Variant: B
Trade: exterior_turnkey
Stage: Partial Occupancy Approved
Subject: Exterior work on {street}
```text
Hi {first},

I follow city building permits for exterior cleaning crews. Saw that {gc} is at partial occupancy with the city on the {value} {kind} build on {street}. That is usually when pressure washing, window washing and lot striping get bid before final sign-off.

Want the general contractor's direct contact details?
```
