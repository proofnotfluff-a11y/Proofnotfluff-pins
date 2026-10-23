# Launch record: Chicago New Business Licenses ($29 a month planned, price and go are Todd's), NOT LAUNCHED

Status Oct 22, 2026, 9:21 pm: LIVE at $29 a month with a 7-day free trial (Todd, 8:50 pm: "Please finish everything yourself based on your recommendation. create the product with a 7 day free trial"). Gumroad: https://proofnotfluff.gumroad.com/l/chicago-new-business-licenses. Left: Todd's $0 trial test (step 6) and the outreach-drafter wiring before the first batch (step 7).

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box is ticked with proof and Todd says go. Built by the leads desk builder run (coo/LEADS_DESK.md Run 4), product 4 in the LEADS FOCUS line (coo/PIVOT.md).

## Todd's decisions, Oct 22, 2026 (live chat, growth follow-up)
- [stated] 1. "Licenses: go. The product-builder may build Chicago New Business Licenses at $29 a month for commercial cleaning and pest control buyers. Every gate in launches/chicago-new-business-licenses.md still runs first (self-checks, two holdouts, design director, Legal desk). Price and go, Gumroad, the members' secret, the buyer test and outreach go stay with me." This answers the licenses versus violations question: licenses.
- [stated] 2. "Copy gate extension for license and citation signals: approved." Built Oct 22: pnf_rules.signal_copy_problems (every permit copy rule, plus the street as street_display gives it, no house number, the City date exactly ("Oct 16"), inside 30 days on the send day, the license words, the shown business name), lead schemas pnf.license_lead.v1 and pnf.citation_lead.v1, copy_gate --signal-templates, --signal-live and --signal, planted cases in tools/test_gates.py. The permit gate is unchanged.
- [stated] 4. "Restaurant product: pause its outreach. No template and no batch until the licenses product is live; then we decide again, since both sell to the same pest, hood and grease buyers. The product and its weekly data keep running."
- [stated] 5. "Sign-off: no sender name. Emails stay faceless, the footer is the only signature. No change during copy test 1."

## The product
- Members' web app: tools/lic_app.py (overview by trade, list with map, filters by trade, City record, date, area, license type, food license inspection and follow-up, search, CSV, business page, pitch kit, Terms readable before the password, workbook download). Encrypted with the password in the GitHub Actions secret LIC_LEADS_PASSWORD; built only in the runner, at docs/chicago-new-business-licenses-members/, once the secret exists.
- Workbook: tools/lic_xlsx.py (Start Here, one tab per trade, Pitch kit, Terms with the City's Data Terms of Use word for word). The runner builds it from the same list and checks app and workbook rows against it field by field.
- Free sample page: docs/chicago-new-business-licenses/ (site/pages.json "licleads", draft, noindex, no price, no checkout).
- Storefront: launches/chicago-new-business-licenses/cover-1280x720.png and thumb-600x600.png (from cover.html and thumb.html).
- This week's list (pulled Thursday, Oct 22, 2026): 230 businesses, 51 this week; food and drink 74, shops and services 97, salons 40, venues 3, auto 13, day care 3; first license 138, new site 38, added license 17, relicensed 37; 70 food rows with a license inspection in the 120 days before the license.

## The product, as planned Oct 20
- Buyers: vendors who sell to a business in its first months (POS and payments, signs, insurance, bookkeeping and payroll, commercial cleaning, pest control, hood cleaning, waste, uniforms and supplies).
- What members get each Monday: every new business license the City issued in the last 30 days at a Chicago business site, one row per business and address, sorted by trade (restaurants and food shops; salons, barbers, spas and fitness; auto shops; day care; venues and lodging; shops, offices and other services), with license type, business activity, issue date, address and community area.
- Left out on purpose (planted cases in `tools/licenses_chicago.py --selftest`): renewals and changes, cancelled or revoked licenses, licenses held by a person or for an event or season (peddler, special event, pop-up, tow truck, home-sharing, home occupation, home repair, mobile food), apartment or unit addresses, sites outside Chicago, and any business whose shown name could be a person's name (two to four plain words with no business word; "Golden Dragon" is left out too, on purpose: a wrong omission costs less than printing a person's name). The legal name is read only to judge that and is never written out.
- Data: City of Chicago Data Portal, Business Licenses (r5kz-chrr), weekly in .github/workflows/licenses-chicago.yml (Mondays 6:40 am Central). Committed: permits/licenses-chicago/sample.json (free sample, last 7 days, up to 10 per trade), profile.json (column names and counts), probe.json (counts by license type and activity), source-terms.txt (the City's data terms page). The members' full list stays in the runner.
- Probe of Oct 17 (6 weeks of new licenses): about 850 issued, top types Limited Business License 191, Pop-Up Retail 106, Retail Food 94, Regulated Business 85, Special Event Food 66, Peddler 37. After the person-held and event licenses come out, expect roughly 80 to 120 a week citywide. Thin for one trade; the product sells as all trades in one list.
- Overlap: "Retail Food Establishment" also feeds the restaurant product's "new license inspection" list. This product reaches the business when the license is issued; the restaurant product when it is inspected. Name it in the copy so a restaurant-product member is not sold the same rows twice.

## Build log
- Oct 20, 2026 (builder run 1): tools/licenses_chicago.py (data rules, 12 planted name cases, 14 planted licenses, selftest ok), workflow licenses-chicago.yml, this record.
- Oct 20, first real pull (run 39456350920, commit 8758804): 711 new licenses fetched for 37 days; kept 247 in 30 days, 71 in the last 7 (food 33, shops and services 28, beauty 5, venues 3, auto 2). Left out: 226 person-held or event licenses, 134 outside the window, 62 names that could be a person's, 24 outside Chicago, 15 second licenses at one site, 2 cancelled, 1 apartment. Fixed after reading it: "Computer Automated Design" no longer reads as auto (word match), "La Casa de las Flores" casing; both planted. Open for the gates: suite numbers in addresses ("2 202", "4 412") may be home offices in apartment buildings; the 62 person-name exclusions include real businesses like two-word names; a holdout should judge both.
- Oct 20, rule added from the probe's activity counts: the City marks some activities "(Home Based Business)" or "Other Home Based Businesses"; those rows are left out as home addresses, and street performers, flea market vendors, event organizers, vacation rentals and scavenger vehicles named only in the activity are left out with the person-held licenses. Planted cases 15 and 16.
- Oct 22, 2026 (builder run 2): free page as a draft: tools/lic_site.py (page kind "licleads", selftest with a planted sample), site/pages.json entry with "draft": true and no checkout or price (noindex, off the index and sitemap, "Tell me when it opens" to hello@), docs/chicago-new-business-licenses/. The licenses workflow now rebuilds the site after each pull so the page follows the Monday sample. For the holdouts, seen on the Oct 20 sample: "1655 S Blue Island Ave 2 100" (suite or home office?), "32 W Randolph St 13-14" (address with a range), and a possessive name ("Julie's Salon and Spa") kept by the person-name rule as designed. Next: members' app and workbook, then outreach templates (a non-permit signal needs Todd's OK for a copy gate extension first, coo/HANDOFF.md).

## Decision evidence, Oct 22, 2026 (growth-research Phase B, live session; Todd decides)
- Recommendation: licenses next, ahead of building violations.
- Real counts: the Oct 22 pull kept 232 new businesses in 30 days and 61 in the last 7 (food 91, shops and services 96, beauty 32, auto 8, venues 4).
- Violations counted the same day (probes/exterior-chicago-2026-10-22.json): exterior citations hit 358 buildings in 30 days, but only 59 sit at an address with an active business license; the rest are homes or apartment buildings, which we will not sell. Elevator citations (122 buildings) suit a different buyer: launches/chicago-elevator-violations.md.
- Buyers already in the CRM: 132 Chicago cleaning companies and 83 Chicago restaurant vendors (pest, hood, grease) can buy this list without a new enrichment segment.
- Proposed first buyers and price: commercial cleaning and pest control, $29 a month. First email drafts and the copy gate extension they need: the growth research doc.

## 1. Gates (all agent gates passed Oct 22, 2026)
- [x] Built to standard: members' app on the tools/leads_app.py pattern, workbook on WORKBOOK_STANDARD v3 (tools/leads_xlsx.py and rest_xlsx.py card helpers), free page draft, storefront copy, cover and thumbnail.
- [x] Outreach email file: done Oct 22. email/L1-OUTREACH.md, cleaning (T11 to T13) and pest control (T14 to T16): a first email and two follow-ups each, variant A, faceless. Gated: copy_gate --signal-templates passes 6 of 6; --signal-live renders all 28 sample leads through all 6 (168 renders) and passes. Outreach go stays with Todd.
- [x] Self-checks: licenses_chicago --selftest (17 planted names, 13 planted trades, 27 planted licenses, 2 planted removals, 5 planted histories, 2 planted food inspections), lic_xlsx, lic_app (node checks), lic_site; runner check: app and workbook rows match the runner's list 230 of 230 field by field; render_xlsx ERROR VALUES: 0 on screen and print; Playwright at 390 and 1280: every view, no console errors, no horizontal scroll, axe WCAG 2.1 AA 0 violations, CSV and back button; free page PASS at 390 and 1280 (noindex, 0 checkout links, no price); workbook and PNG metadata say ProofNotFluff only; check_repo 0 errors on a clean checkout before every push.
- [x] Holdout 1 and Holdout 2 (fresh agents, never opened tools/ or tests): Holdout 2 PASS in round 5 (601 of 601 City rows accounted for, 0 misses, 0 wrong reasons, no false promise); Holdout 1 PASS in round 6 (seed 673018965: fields 30/30, City record 30/30, food 6/6, left out 25/25, every count true). Every earlier finding fixed with a planted case. After the holdouts, Legal's round 1 added three left-out activities (dog walking, pet sitting, residential real estate developer; planted cases 26 and 27) and one do-not-list address: 4 rows out, nothing else changed.
- [x] Design director: round 1 FAIL 4.00, round 2 FAIL 4.14, round 3 FAIL 4.14 (every change list applied: commits 9f93ee6, 61fd098, 224c564, 065bb46); the round 3 reviewer judged again from fresh renders: PASS 4.71, then its two last items applied (b32c21e) and re-judged: PASS 5.00, every score 5. Live session's calls the reviewer accepted: the app lands on Overview; full-page screenshots draw the sticky map once.
- [x] Legal desk: CLEARED WITH FIXES (legal/reviews/chicago-new-business-licenses-2026-10-22.md). Round 1 FIX (5 medium, 6 low), round 2 FIX (1 medium, 4 low), round 3 two low fixes; every fix applied as worded. City Data Terms of Use word for word in the Terms and the required disclaimer on every surface; 0 person's full names in 230 rows; overlap with the restaurant product stated plainly. The live City terms page would not load for the reviewer; the runner fetches it every week and stops the members' list if it differs from the Legal desk's snapshot (passed on every Oct 22 run).
- Still open for Todd, from Legal (no wording change): counsel on (1) the City data terms' indemnity and duty to defend, (2) the Illinois Automatic Contract Renewal Act and federal ROSCA for a monthly Gumroad membership, (3) the call and email scripts under the Telemarketing Sales Rule (2024 changes), Illinois telephone solicitation rules and CAN-SPAM templates members send. Four rows a reviewer flagged as maybe residential were kept (office tower suites and a second floor over shops; no rule fits): Todd can add any to the do-not-list.
- The crew's gate key is removed: the runner no longer seals a copy of the members' list (the private key lived only in the build session).

## 2. Todd's steps, in order
1. [x] Price and go: $29 a month with a 7-day free trial (Oct 22, 8:50 pm). Take the three open Legal items to counsel first if you want.
2. [x] (Oct 22, Todd) GitHub: add the Actions secret LIC_LEADS_PASSWORD (Settings, Secrets and variables, Actions), 12 characters or more. Never in this repo or in chat.
3. [x] (Oct 22, run 39887328304; the published app opens with the password in a Playwright run, and #/terms opens without it on the live site) Tell a session. It runs the licenses workflow once so the members' app is published at https://proofnotfluff.com/chicago-new-business-licenses-members/, and checks that #/terms opens without the password.
4. [x] (Oct 22, the session in the built-in browser; Todd typed the password line; product apgisz, slug chicago-new-business-licenses, trial 1 week, cover and thumbnail uploaded, published 9:21 pm; the trial line from legal/reviews/2026-10-22-monday-email-and-trial.md item 12 is in the Description) Gumroad: new Membership product, tier `Monthly` at $29, monthly, no trial. Paste Name, Summary and Description from "Gumroad copy" below. Cover: launches/chicago-new-business-licenses/cover-1280x720.png. Thumbnail: launches/chicago-new-business-licenses/thumb-600x600.png. Post-purchase content: the members' link and the same password. Publish, then send the checkout link to the session.
5. [x] (Oct 22, commit 70ebfdc: trial button, the note by it, the full trial disclosure and a trial FAQ; page indexable; shop card added) The session puts the checkout link on the free page (site/pages.json "checkout"), drops "draft", and rebuilds the site.
6. [ ] Todd: start one 7-day trial on your own card ($0), check the receipt shows the trial and the charge date and that the password opens the app and workbook, then cancel in your Gumroad library and confirm no charge is scheduled.
7. [x] Outreach go given Oct 22 (meta/products chicago-licenses outreachGo true). Before the first batch, a session wires the outreach-drafter for licenses (signal leads from the Monday list, copy_gate --signal). Outreach: cleaning T11 to T13 and pest control T14 to T16 (email/L1-OUTREACH.md); restaurant outreach stays paused until then (decision 4).

## Removal requests
- A business that asks to be left out (or a row Todd judges to be a home) goes on permits/licenses-chicago/do_not_list.json (salted keys, no names): `python3 tools/licenses_chicago.py --dnl-add --license N` (the License number from the business page or the workbook), commit, and the next build leaves it out of every list and the sample.

## Gumroad copy (paste as is)

Name:
```
Chicago New Business Licenses
```

Summary:
```
Every Monday: new business licenses the City of Chicago issued in the last 30 days, sorted by trade, each marked first license, new site, added license or relicensed.
```

Description:
```
A weekly lead list for Chicago commercial cleaning and pest control companies, and for any vendor who sells to new businesses and new locations.

Each Monday we pull the City of Chicago's business license records (and its food inspection records, for food rows) and keep the new licenses the City issued in the last 30 days at Chicago business sites, one row per business and site, sorted by trade: food and drink; shops and services; salons, spas and fitness; venues and lodging; auto shops; day care.

For each business: the license type, the business activity, the issue date, the address and community area, and what the City's earlier records say about it: its first Chicago license, a new site of a business already licensed elsewhere, a new license type at a site it already has, or the same license type again at a site it held before (most often a new owner, or the same business licensing the site again).

What you get:
- A members' web app: pick a trade, filter by date, community area, license type and City record, see the businesses on a map (a few City records have no map point), open its page, mark who you called and keep private notes (saved only in your own browser), and export any view to CSV.
- The same list as an Excel file that also opens in Google Sheets, one tab per trade.
- A pitch kit: a short call opener and an email for commercial cleaning, pest control and other vendors.

If you also have Chicago Restaurant Inspection Leads: food businesses usually get a City food license inspection within three weeks before their food license is issued, and that product lists those inspections as Opening soon. Every food row here with one in the 120 days before its license is marked, and one click hides them, so you can skip the food businesses you may already have seen there. Nearly all shops, salons, venues, auto shops and day care centers are only on this list.

What it is not: a license shows the City issued it on that date. It does not say a business is open or buying anything, and no business listed has endorsed or works with ProofNotFluff. Renewals, event licenses, licenses for one person's own work or for work away from a fixed site, home and mail-drop addresses, and businesses whose name could be a person's full name are left out on purpose; the full rule is in the Terms. You make your own calls and emails.

$29 a month. Cancel any time from the link in your Gumroad receipt or from your Gumroad library (if you have a Gumroad account); cancelling stops future charges. Your membership renews monthly until you cancel.

Terms of Use, readable before you buy: https://proofnotfluff.com/chicago-new-business-licenses-members/#/terms

This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one’s own risk.

ProofNotFluff is not affiliated with or endorsed by the City of Chicago. Licensed to one business for its own prospecting.

Made with AI assistance and reviewed and tested by the shop owner.
Information and planning tool only, not legal, tax, financial or other professional advice.
Digital membership: a web app and an Excel file. Nothing ships.
No refunds on a month already delivered. If a list doesn't arrive or a file won't open, we fix it or refund that month: https://proofnotfluff.com/refunds/
```

Tier name: `Monthly`. Price: `$29`.

