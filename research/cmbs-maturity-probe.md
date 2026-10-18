# CMBS maturity probe (Oct 17, 2026)

Question: can we rebuild the "loans maturing soon that may not refinance" list from a creator video (28,000 loans scanned, over $3 billion maturing by year end, 255 unlikely to refinance) from free SEC data, accurately, and would anyone pay us for it?

Short answer: yes, the list can be rebuilt, and our scan matched the video's 28,000 almost exactly. Don't build it as a lead product. Chicago is too thin, the buyers need borrower contacts we won't supply, and paid tools that include contacts start at $145 a month. Rank it 5th, behind the four queued products.

Data: `probes/cmbs-2026-10-18.json` (run on Oct 18, 2026 UTC, counts plus 282 property-level rows, 130 KB). Code: `tools/cmbs_probe.py`, `.github/workflows/cmbs-probe.yml` (manual dispatch only).

## How the pull ran

- The cloud sandbox could not reach sec.gov (`CONNECT tunnel failed, response 403` for www.sec.gov and efts.sec.gov), so the pull ran in GitHub Actions. Each run took about 5 minutes and sent about 1,700 requests at 6 a second at most. The User-Agent was `ProofNotFluff hello@proofnotfluff.com`.
- EDGAR fair access rules: "Current max request rate: 10 requests/second", a User-Agent naming the company and an admin contact email, and "Download only what you need". https://www.sec.gov/os/accessing-edgar-data
- One correction to the brief: the loan file is Exhibit 102 to **Form ABS-EE**, which is filed alongside the 10-D, not attached to the 10-D itself. https://www.sec.gov/oit/announcement/regabii-asset-level-requirements-compliance.html
- Asset-level data covers commercial mortgage deals registered with the SEC, with compliance due no later than Nov 23, 2016. Private 144A deals were left out of the rule (single-borrower SASB deals are mostly 144A). So this data does not cover pre-2017 conduit deals or most SASB loans. https://www.federalregister.gov/documents/2014/09/24/2014-21375/asset-backed-securities-disclosure-and-registration
- Method:
  1. Read EDGAR's full-index `form.idx` for Q3 and Q4 2026.
  2. Keep each ABS-EE filer's latest filing since Aug 24.
  3. Open the XML and keep it only if its namespace is `absee/cmbs`.
  4. Parse every `<assets>` row and join property rows to their loan by asset number.
  5. Treat a loan as active if its period-end actual balance is above zero.
  6. Use the post-modification maturity date when there is one (741 loans).
  7. Drop defeased loans: defeasance code, property type SE, or a property named "Defeased".
  8. Annualize the latest NOI when it covers less than a year (535 of the tested loans).
- The same big loan often sits in several trusts as separate pieces (pari passu notes). We count a loan once by property name, city, state and maturity, and we add up the trusts' pieces. Whole-loan size is estimated as the trusts' notes divided by their share of debt service. That share is this trust's original monthly payment times 12, divided by NOI at securitization over DSCR at securitization. 223 tested loans are split loans like this.

## 1. Coverage

| Measure | Count |
|---|---|
| ABS-EE filers with a filing since Aug 24, 2026 | 666 (375 CMBS, 253 auto loan, 38 auto lease) |
| CMBS trusts read (latest month each, mostly September period data) | 375 |
| Asset rows in those files | 28,178 |
| Rows with a live balance (loan pieces) | 16,204 |
| Distinct loans after joining split pieces | 12,825 |
| Active balance in these trusts | $297.1 billion |
| Past maturity and still outstanding | 159 pieces, $3.61 billion |

The video's "28,000 loans" matches our 28,178 rows. But 10,852 of those rows carry an asset number and property fields with no balance, rate or maturity: they are paid off or otherwise inactive. About 12,800 live loans remain.

## 2. Maturing Oct 18, 2026 to Jun 30, 2027

National: 1,377 loan pieces, **964 distinct loans, $23.89 billion**. From now through Dec 31, 2026: 231 loans, $5.18 billion (the video said over $3 billion). That total includes 266 defeased pieces worth $3.04 billion, which are already backed by Treasuries and will pay off.

| Month | Pieces | Balance ($B) |
|---|---|---|
| 2026-11 | 159 | 3.02 |
| 2026-12 | 156 | 2.16 |
| 2027-01 | 158 | 3.34 |
| 2027-02 | 142 | 2.29 |
| 2027-03 | 144 | 2.54 |
| 2027-04 | 153 | 1.94 |
| 2027-05 | 181 | 2.79 |
| 2027-06 | 284 | 5.81 |

By property type ($B): office 7.50 (241), retail 4.52 (319), hotel 2.91 (153), not coded 2.81 (225, mostly defeased), mixed use 2.36 (88), multifamily 1.08 (86), securities/defeased 1.02 (72), self storage 0.59 (70), industrial 0.47 (40), other 0.62.

Payment status of the maturing pieces: 1,271 current ($20.97B), 44 late under 30 days, 6 at 30 to 59 days, 33 at 90+ days ($0.92B), 21 blank.

**Illinois: 23 distinct loans, $739.2 million.** By month ($M): Nov 67.8 (6), Dec 233.2 (8), Jan 228.2 (4), Feb 28.5, Mar 14.8, Apr 8.4, May 6.3, Jun 151.9 (7). By type ($M): office 332.0 (6), retail 157.9 (9), hotel 136.8 (6), industrial 45.2, warehouse 23.8, mixed use 22.3, multifamily 21.1.

**Chicago metro (Cook, DuPage, Lake, Will, Kane, McHenry): 20 distinct loans, $712.4 million.** By month ($M): Nov 64.6 (5), Dec 233.2 (8), Jan 211.0 (3), Feb 28.5, Mar 14.8, Apr 8.4, Jun 151.9 (7). By type ($M): office 332.0 (6), retail 137.4 (7), hotel 136.8 (6), industrial 45.2, warehouse 23.8, mixed use 22.3, multifamily 14.8. Across all maturity dates, Illinois has 578 active pieces.

## 3. Refinance gap (an estimate from public figures, not a prediction)

Stated rule: the new loan is the lower of 65% of the latest valuation and the amount current NOI supports at a 1.25 DSCR, on a 7% rate with 30-year amortization (annual debt constant 0.0798, so about 10 times NOI). Gap = estimated whole-loan balance minus that new loan. Each distinct, non-defeased loan maturing in the window is tested once.

| Result | Loans | Gap |
|---|---|---|
| Tested | 903 (12 missing NOI and value) | |
| **Gap under the stated rule** | **339** | **$4.73 billion** (on $13.88B of whole-loan debt) |
| Gap, maturing by Dec 31, 2026 | 67 | $1.06 billion |
| Gap under a lighter rule (70% of value, 1.20x DSCR, 6.25%, 30-yr) | 257 | $3.94 billion |
| Fails the NOI test alone / the value test alone | 241 / 218 | |
| In special servicing now / of those with a gap | 93 / 56 | |

The lighter rule's 257 is close to the video's 255, so the creator probably used something near market terms.

Gap by type: office 91 loans, $2.39B; retail 118, $1.00B; hotel 44, $0.59B; mixed use 20, $0.54B; multifamily 26, $0.11B; others under $0.05B each.

Debt yield (annualized NOI over whole-loan balance): 12%+ for 506 loans, 10 to 12% for 136, 8 to 10% for 126, 6 to 8% for 59, under 6% for 57.

Illinois: 22 loans tested, 7 show a gap totaling $248.2M. Chicago metro: 18 tested, 5 show a gap totaling $239.5M. One suburban office loan already in special servicing with negative NOI makes up $226M of that. So the Chicago "list" is about five properties.

Why the estimate needs flags on every row:
- **Stale valuations.** For 748 of the 903 loans, the latest valuation is still the one from securitization. 716 are 8 or more years old, and only 59 are under 2 years old (mostly new appraisals on specially serviced loans). The 65% value test is therefore mostly a 2016 to 2017 appraisal.
- **NOI age.** For 159 loans the only NOI is from securitization, and 18 have financials more than 18 months old. A stale "no gap" is also possible: one Chicago office loan in special servicing passes the test only because its file still carries 2019 figures.
- **Partial-year NOI.** Most files report a quarter or year to date. Annualizing that changed the result a lot: the gap count fell from 574 to 339 after the fix. Any product has to do this.
- **Whole-loan size is our estimate** for split loans. It is not reported directly.
- **What the data leaves out.** It does not show extension options, reserves, sponsor equity or payoffs already arranged.

## 4. Who is behind each loan and how to reach them

- The file has no borrower. The usual borrower is a single-purpose LLC.
- The file gives the primary servicer name and the date of transfer to special servicing. It does not name the special servicer; that is in the 10-D and the deal documents.
- The route a buyer would take, property by property:
  1. Match the address to a county parcel (PIN).
  2. Get the taxpayer mailing name and address from the assessor. Cook County publishes this as open data, updated semi-monthly, but says "owner name and mailing address is, to our knowledge, only intermittently updated". https://catalog.data.gov/dataset/assessor-parcel-addresses (landing page https://datacatalog.cookcountyil.gov/d/3723-97qp)
  3. Pull the recorded mortgage, which names the borrower entity. The Cook County Clerk's online search covers 1985 to the present, and an electronic copy costs $5 (per the Clerk's fee list as summarized at https://www.deeds.com/recorder/illinois/cook/; Clerk page https://www.cookcountyclerkil.gov/recordings).
  4. Look the LLC up with the Secretary of State for its manager or registered agent.
  5. For hotels, malls and office towers, use the property's own website, which names the management or leasing company.
  6. For specially serviced loans, the decision maker is the special servicer, named in the trust's 10-D.
- Difficulty: hard. It takes roughly 15 to 30 minutes of manual lookups per property, and many trails end at a registered agent or a person's name. Even LoanBase, whose business is this, claims verified borrower contacts on only about 55% of loans (https://www.credaily.com/reviews/loanbase-2025-review-details-pricing-features/).
- Under our rules, we would stop at the property, the servicer and a link to the county PIN page. We would never store a private person's name or contact. That leaves the buyer to do the expensive step.

## 5. Buyers and what incumbents charge

- **Buyers:** commercial mortgage brokers (refinance mandates), debt funds and bridge lenders (rescue capital), note buyers (specially serviced loans), CRE investors (distressed purchases), and property tax appeal firms (falling NOI and occupancy).
- **Prices.** cred-iq.com, loanbase.com and trepp.com could not be opened from this session, so some prices below come from CRE Daily reviews and are marked as such.

| Vendor | Price | What it includes | Source |
|---|---|---|---|
| LoanBase | $95 per deal + 0.15% origination fee; Starter $145/seat/mo (10 deals); Pro $295/seat/mo (30 deals); Power Broker $1,000/mo ($795 early access); 20% off annual | Loans maturing in the next 18 months, borrower contacts on about 55% of loans, 25,000+ lenders | CRE Daily review: https://www.credaily.com/reviews/loanbase-2025-review-details-pricing-features/ |
| CRED iQ | Solo $625/mo ($7,500/yr), Starter $1,250/mo, Professional $3,850/mo, billed annually | CMBS, SASB, CRE CLO and agency loans; maturity filters; borrower and owner contacts | CRE Daily review: https://www.credaily.com/reviews/cred-iq-review/ |
| Reonomy | "plans start at $400/mo"; annual saves 30% | Debt search by maturity date (90 days to 10 years), lender, owners | Own pages: https://www.reonomy.com/pricing/ and https://www.reonomy.com/property-debt-research |
| Crexi Intelligence | "Pricing for all paid plans is available upon request"; annual subscription | "loan maturity dates, CMBS data, lender history" | https://credaily.com/reviews/crexi-review |
| Trepp | No public price; demo request | All US CMBS properties and loans | https://cherre.com/vendors/trepp |

- **Free competition:** Trepp's 2026 hard-maturity total ($76.6 billion) and CRE Daily's monthly maturity write-ups are free to read. https://therealdeal.com/data/national/2026/cmbs-hard-maturity-wall-hits-77b-in-2026/ and https://www.credaily.com/?p=220892

## 6. Rules

- **Reuse is allowed.** SEC: "Information presented on sec.gov is considered public information and may be copied or further distributed". The SEC asks to be cited as the source. Don't use the SEC seal, logos or artwork. "EDGAR" is an SEC trademark, so keep it out of any product name or domain. https://www.sec.gov/privacy
- **Access.** Follow the fair access limits above, and pull only the latest ABS-EE per trust.
- **Naming a property next to an estimated gap.** The risk is the implication, not the figures. The guide below says truth is a strong defense, opinion is protected, and a fair report of a public document is privileged if the document is named as the source and reported accurately (general information, varies by state). https://www.dmlp.org/node/1820
- Wording that stays on the safe side:
  - Column name: "Estimated refinance gap under the stated rule".
  - Print the rule and the source filing with its period date on every page.
  - Show the valuation date and the NOI date next to every row.
  - Never use "distressed", "will default", "unlikely to refinance", "failing" or "in trouble".
  - Footer: "Figures as reported by the servicer in the trust's SEC filing for the period shown; they may be out of date. This is arithmetic on public figures, not a statement about any borrower's finances or intentions."
  - No borrower or person names.
- Hotel and store names in property names (for example a brand inn) are used only to identify the property.

## 7. Verdict

**Don't build it now. It ranks 5th, after (1) Chicago restaurant inspection leads, (2) Austin construction leads, (3) Chicago new business licenses and (4) Seattle permits.**

Why:
- The data is free and accurate enough, and rebuilding the list takes about 5 minutes a month in Actions. But the value buyers pay for is the borrower contact, which we won't supply, and the tools that have it start at $145 a seat a month (LoanBase) to $625 a month (CRED iQ).
- Chicago first is not viable: 20 loans maturing in 8.5 months, 5 with a gap, one of which is most of the dollars. That can't carry a monthly subscription or 40 outreach emails a week that each name a real record.
- The buyers are CRE finance professionals. That is a different audience from the local trades our queue reaches, so none of our outreach or pages carry over.
- Coverage is only post-2016 public conduit deals ($297B active). Trepp's 2026 hard-maturity total is $76.6B, against our $5.2B from now to year end, so a pro will see the gaps in coverage quickly.

If it is ever built:
- National first.
- One monthly XLSX of every loan maturing in the next 9 months (about 950), with the stated-rule estimate, the lighter-rule estimate, valuation and NOI dates, servicer and special servicing status, and a county PIN lookup link for Illinois.
- About $49 per monthly edition, or $29 a month.
- Test it as a free sample page first.
- A cheaper side use: a free "CMBS maturity calendar" page as content that draws traffic.
