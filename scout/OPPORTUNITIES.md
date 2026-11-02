# Opportunity list (radar, scored 2026-11-02)

Written by tools/opportunity_score.py from scout/candidates/ and scout/reviews/. Do not edit by hand; edit a candidate file and rerun.
Goal: $1000 net in one month by 2027-01-31. January net is the expected dollars from this product alone at the desk's outreach cap,
at 0.25%, 0.75% and 2.00% of first emails becoming paying members (assumptions until a payer exists).

| # | Idea | Status | Score | Jan net (low / likely / high) | Confidence | First $ | Price | Why |
|---|---|---|---|---|---|---|---|---|
| 1 | NYC Restaurant Pest Citations | todd | 79 | $30 / $91 / $244 | medium | 2026-12-09 | $49 | second FAIL (redteam: Same product, buyer and motion as the Chicago restaurant list, which has 0 payers and 0 replies and paused outreach; a second city does not change the conversion rate.) |
| 2 | New Federal Alcohol Permits Weekly | parked | 58 | $18 / $53 / $142 | medium | 2026-12-09 | $29 | code score 58 under the review floor 60 |
| 3 | Chicago Commercial Building Sales Weekly | parked | 48 | $30 / $91 / $244 | low | 2026-12-09 | $49 | code score 48 under the review floor 60 |
| 4 | Austin New Businesses Weekly | parked | 46 | $0 / $0 / $0 | medium | 2026-12-09 | $29 | code score 46 under the review floor 60 |
| 5 | Truck Insurance Cancellations by State | dropped | 81 | $28 / $84 / $224 | medium | 2026-12-13 | $49 | Dropped Oct 26 after demand FAIL 2 and red team FAIL 2 on the offer itself: a competitor sells real-time cancellation alerts with insurer, phone and email from $49 with a trial, a weekly file is stale when the carrier must refile within days, and Motus was reported in Sept 2026 to mark replaced filings wrongly, so cancelled-and-not-replaced cannot be promised. Data-legal PASS 4. |
| 6 | New Trucking Companies by State | dropped | 77 | $17 / $51 / $137 | medium | 2026-12-11 | $29 | Dropped Oct 23 after demand and red team FAIL with no honest fix: competitors at $39 to $49 ship the phone, email and officer fields our privacy rule strips, Carrier Hunt has a free tier and Apify sells contact-rich rows at about $5 per 1,000; the real reachable buyer is truck insurance agencies (dozens shown), not 37,000 P&C agencies. Data and legal PASS. |
| 7 | Colorado New Business Filings | dropped | 71 | $18 / $53 / $142 | medium | 2026-12-09 | $29 | Dropped Oct 23 after demand and red team FAIL with no honest fix: the State says the same data is free on its portal, FreshFilings sends it daily for $49 with a trial, many addresses are registered-agent offices or homes, and the only accountant thread found had 0 of 11 willing to pay. Data and legal PASS. |
| 8 | New OSHA Inspections and Citations by State | dropped | 71 | $16 / $47 / $126 | medium | 2026-12-15 | $29 | Dropped Oct 26 after demand FAIL 2 and red team FAIL 2 on the offer itself: OSHA's own search is free by state and date, an incumbent sells the same weekly state list at $29 with a free tier, an Apify actor sells the rows at $3.50 per 1,000, and citations post about 30 days after the employer gets them. Data-legal PASS 3. |
| 9 | NYC Unsafe Facade Filings | dropped | 68 | $20 / $59 / $157 | medium | 2026-12-10 | $99 | Dropped Oct 23 after demand and red team FAIL with no honest fix: fresh Initial Unsafe filings are about 35 to 50 a month, the work is awarded through the engineer of record and board bids, the feed is free on NYC Open Data and DOB NOW, and BuildDocket sells a richer version at $199. Data and legal PASS. |
| 10 | NYC New Liquor License Applications | dropped | 67 | $8 / $25 / $66 | medium | 2026-12-09 | $39 | Dropped Oct 26 without a second review: the Oct 23 red team FAIL is on the offer itself (67 NYC hood cleaners on the FDNY list, one pass burns the pool, no field separates a new kitchen from an ownership change, likely January net $25), which no better source can fix. Demand PASS 3, data-legal PASS 4. |
| 11 | Chicago Storefront Sign Leads | dropped | 50 | $33 / $98 / $261 | low | 2026-12-08 | $79 | Oct 26 reviews: demand FAIL 2 and red team FAIL 2 on the offer itself, which no better source can fix: the free City export already carries the community area, a paid feed sells the same filtered rows at about 2 cents a lead, a license usually comes after the sign is ordered, and only 4 areas clear 10 storefronts a month (ceiling $316 a month). Data-legal PASS 3. |

Factor scores (0 to 5): buyer, pay, demand, data, license, effort, speed, fit.

- nyc-restaurant-pest-citations: buyer 5, pay 5, demand 5, data 0, license 5, effort 4, speed 5, fit 3
- ttb-new-alcohol-permits: buyer 5, pay 0, demand 2, data 3, license 5, effort 4, speed 5, fit 0
- chicago-commercial-building-sales: buyer 5, pay 2, demand 0, data 1, license 0, effort 4, speed 5, fit 3
- austin-new-business-permits: buyer 0, pay 2, demand 1, data 3, license 2, effort 4, speed 5, fit 3
- fmcsa-insurance-cancellations: buyer 5, pay 5, demand 3, data 4, license 5, effort 3, speed 5, fit 2
- fmcsa-new-trucking-companies: buyer 5, pay 5, demand 5, data 0, license 5, effort 4, speed 5, fit 2
- colorado-new-business-entities: buyer 5, pay 4, demand 4, data 0, license 5, effort 4, speed 5, fit 2
- osha-inspection-leads: buyer 5, pay 5, demand 5, data 0, license 5, effort 3, speed 5, fit 0
- nyc-facade-unsafe-filings: buyer 3, pay 5, demand 4, data 0, license 5, effort 4, speed 5, fit 2
- nyc-liquor-license-applications: buyer 4, pay 5, demand 4, data 0, license 2, effort 4, speed 5, fit 3
- chicago-storefront-sign-leads: buyer 4, pay 2, demand 0, data 0, license 2, effort 5, speed 5, fit 4
