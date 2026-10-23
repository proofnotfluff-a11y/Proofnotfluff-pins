# Opportunity list (radar, scored 2026-10-23)

Written by tools/opportunity_score.py from scout/candidates/ and scout/reviews/. Do not edit by hand; edit a candidate file and rerun.
Goal: $1000 net in one month by 2027-01-31. January net is the expected dollars from this product alone at the desk's outreach cap,
at 0.25%, 0.75% and 2.00% of first emails becoming paying members (assumptions until a payer exists).

| # | Idea | Status | Score | Jan net (low / likely / high) | Confidence | First $ | Price | Why |
|---|---|---|---|---|---|---|---|---|
| 1 | NYC Restaurant Pest Citations | fix | 94 | $36 / $109 / $291 | medium | 2026-11-29 | $49 | redteam: The same product with the same buyer and motion is live for Chicago at $39 with 0 payers from 57 emails and its outreach is paused; a second city tests the city, not the product. |
| 2 | NYC Unsafe Facade Filings | review | 83 | $20 / $59 / $157 | medium | 2026-11-30 | $99 | all factors sourced |
| 3 | NYC New Liquor License Applications | review | 82 | $8 / $25 / $66 | medium | 2026-11-29 | $39 | license unclear: the data and legal reviewer reads the terms |
| 4 | Truck Insurance Cancellations by State | review | 81 | $34 / $102 / $272 | medium | 2026-12-03 | $49 | all factors sourced |
| 5 | New OSHA Inspections and Citations by State | review | 71 | $19 / $58 / $154 | medium | 2026-12-05 | $29 | stale: last update 2026-06-03 for a daily source |
| 6 | New Federal Alcohol Permits Weekly | parked | 58 | $21 / $64 / $170 | medium | 2026-11-29 | $29 | code score 58 under the review floor 60 |
| 7 | New Trucking Companies by State | dropped | 92 | $21 / $62 / $165 | medium | 2026-12-01 | $29 | Dropped Oct 23 after demand and red team FAIL with no honest fix: competitors at $39 to $49 ship the phone, email and officer fields our privacy rule strips, Carrier Hunt has a free tier and Apify sells contact-rich rows at about $5 per 1,000; the real reachable buyer is truck insurance agencies (dozens shown), not 37,000 P&C agencies. Data and legal PASS. |
| 8 | Colorado New Business Filings | dropped | 86 | $21 / $64 / $170 | medium | 2026-11-29 | $29 | Dropped Oct 23 after demand and red team FAIL with no honest fix: the State says the same data is free on its portal, FreshFilings sends it daily for $49 with a trial, many addresses are registered-agent offices or homes, and the only accountant thread found had 0 of 11 willing to pay. Data and legal PASS. |

Factor scores (0 to 5): buyer, pay, demand, data, license, effort, speed, fit.

- nyc-restaurant-pest-citations: buyer 5, pay 5, demand 5, data 5, license 5, effort 4, speed 5, fit 3
- nyc-facade-unsafe-filings: buyer 3, pay 5, demand 4, data 5, license 5, effort 4, speed 5, fit 2
- nyc-liquor-license-applications: buyer 4, pay 5, demand 4, data 5, license 2, effort 4, speed 5, fit 3
- fmcsa-insurance-cancellations: buyer 5, pay 5, demand 3, data 4, license 5, effort 3, speed 5, fit 2
- osha-inspection-leads: buyer 5, pay 5, demand 5, data 0, license 5, effort 3, speed 5, fit 0
- ttb-new-alcohol-permits: buyer 5, pay 0, demand 2, data 3, license 5, effort 4, speed 5, fit 0
- fmcsa-new-trucking-companies: buyer 5, pay 5, demand 5, data 5, license 5, effort 4, speed 5, fit 2
- colorado-new-business-entities: buyer 5, pay 4, demand 4, data 5, license 5, effort 4, speed 5, fit 2
