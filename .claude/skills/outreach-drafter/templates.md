# Outreach templates (outreach-drafter step 4 reads this; nothing loads it before a run)

Pick by the prospect's trade_vertical (blank means commercial_cleaning) and the lead's stage. A template without a Trade line is commercial_cleaning. tools/copy_gate.py renders every template here on each push and preflight; pnf_rules.TRADE_VERTICALS says which products and stages each vertical may use.

### T1 partial occupancy
Stage: Partial Occupancy Approved
Subject: Final clean on {street}
```text
Hi {first},

Noticed {gc} is at partial occupancy approved with the city on the {value} {kind} build on {street}. That is usually when the final clean gets bid.

Mind if I send over the general contractor's direct contact details?
```
### T2 inspections
Stage: Inspections Under Way
Subject: Final clean on {street}
```text
Hi {first},

Saw that {gc} has city inspections under way on the {value} {kind} project on {street}. Jobs at this stage usually line up the final clean soon.

Want me to send the general contractor's direct contact details?
```
### T3 certificate of occupancy
Stage: Certificate of Occupancy Pending
Subject: Final clean on {street}
```text
Hi {first},

The {value} {kind} job {gc} is running on {street} has its certificate of occupancy pending with the city. Final clean crews get picked right around now.

Should I send you the general contractor's direct contact details?
```
### T4 exterior turnkey
Trade: exterior_turnkey
Stage: Partial Occupancy Approved
Subject: Exterior work on {street}
```text
Hi {first},

Saw that {gc} is at partial occupancy with the city on the {value} {kind} build on {street}. That is usually when pressure washing, window washing and lot striping get bid before final sign-off.

Want the general contractor's direct contact details?
```
