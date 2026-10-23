# Legal desk: Chicago New Business Licenses (Oct 22, 2026)

A risk-control review written by an AI under legal/README.md. Not legal advice; nothing here is "approved". Tier: Medium (a business lead list; no laws, rates or deadlines stated).

## Round 1 (fresh reviewer, never opened tools/): FIX
Nothing blocked. Checks: City Data Terms of Use quoted word for word (matched the snapshot in 4 places; the live page would not load for the reviewer, a City-hosted copy matched 23 of 23 checkable lines); 0 business names that are or start with a person's full name in the 234-row members' list and 30-row sample; overlap with Chicago Restaurant Inspection Leads stated clearly (70 of 74 food rows had a license inspection in the 120 days before the license, median 12 days); file metadata clean.

Fixes, all applied the same day (commit 61fd098 and the runner pull after it):
1. Medium: the free page counted a UTC day (pulled after 7 pm Central). Pulls are now dated in Chicago time.
2. Medium: the Food Inspections dataset is now named next to Business Licenses (Start Here sources, Terms Accuracy, free page footer and FAQ, app legal line, workbook footer, Gumroad copy).
3. Medium: pitch kit rule 3 carries the CAN-SPAM duties (true subject, real name and company, street address, a way to say stop, honored within 10 business days); every email signature adds a street address and a stop line.
4. Medium: possible homes. Dog walking, pet sitting and residential real estate developer licenses are left out as work away from a fixed site (planted cases 26 and 27); one nail services address on a residential block went on the do-not-list. Eight low-risk rows were kept for lack of a rule basis and sent to round 2.
5. Medium: the weekly runner compares the City's live terms page with the snapshot and stops the members' list if they differ (passed on every Oct 22 run).
6. to 11. Low: "person's full name" wording; Gumroad cancel route (receipt link or library); Gumroad listing block (not advice, digital membership, refund line); Terms "Information only" paragraph; cleaning call opener no longer assumes a new site; Terms refund sentence.

For the owner's attorney (no wording change can settle these):
1. The City's terms make every data user indemnify and defend the City. Can ProofNotFluff LLC pass that on to members, and what is its own exposure?
2. Do the Illinois Automatic Contract Renewal Act (815 ILCS 601) and federal negative-option rules (ROSCA) apply to a monthly membership sold to businesses through Gumroad, and are the disclosures and cancel path enough?
3. Telemarketing: the FTC Telemarketing Sales Rule's business-to-business exemption excludes calls selling nondurable office or cleaning supplies, and the 2024 amendments reach business calls. What falls on members, and what exposure comes from supplying the scripts? Any Illinois telephone solicitation rules?

Sources read by the reviewer (Oct 22, 2026): webapps1.chicago.gov/ChicagoTif/disclaimer.html; catalog.data.gov/dataset/food-inspections; gumroad.com/help/article/192 and 139; ftc.gov CAN-SPAM compliance guide; Federal Register Apr 16, 2024 (2024-07182).
