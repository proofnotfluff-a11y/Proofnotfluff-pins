# Launch record: Chicago New Business Licenses ($29 a month planned, price and go are Todd's), NOT LAUNCHED

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box is ticked with proof and Todd says go. Built by the leads desk builder run (coo/LEADS_DESK.md Run 4), product 4 in the LEADS FOCUS line (coo/PIVOT.md).

## Todd's decisions, Oct 22, 2026 (live chat, growth follow-up)
- [stated] 1. "Licenses: go. The product-builder may build Chicago New Business Licenses at $29 a month for commercial cleaning and pest control buyers. Every gate in launches/chicago-new-business-licenses.md still runs first (self-checks, two holdouts, design director, Legal desk). Price and go, Gumroad, the members' secret, the buyer test and outreach go stay with me." This answers the licenses versus violations question: licenses.
- [stated] 2. "Copy gate extension for license and citation signals: approved." Built Oct 22: pnf_rules.signal_copy_problems (every permit copy rule, plus the street as street_display gives it, no house number, the City date exactly ("Oct 16"), inside 30 days on the send day, the license words, the shown business name), lead schemas pnf.license_lead.v1 and pnf.citation_lead.v1, copy_gate --signal-templates, --signal-live and --signal, planted cases in tools/test_gates.py. The permit gate is unchanged.
- [stated] 4. "Restaurant product: pause its outreach. No template and no batch until the licenses product is live; then we decide again, since both sell to the same pest, hood and grease buyers. The product and its weekly data keep running."
- [stated] 5. "Sign-off: no sender name. Emails stay faceless, the footer is the only signature. No change during copy test 1."

## The product (planned)
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

## 1. Gates (none run yet)
- [ ] Built to standard: data rules done; free page draft done Oct 22; members' app (tools/leads_app.py pattern), workbook (tools/leads_xlsx.py pattern), storefront copy and images: to do.
- [x] Outreach email file: done Oct 22. email/L1-OUTREACH.md, cleaning (T11 to T13) and pest control (T14 to T16): a first email and two follow-ups each, variant A, faceless. Gated: copy_gate --signal-templates passes 6 of 6; --signal-live renders all 28 sample leads through all 6 (168 renders) and passes. Outreach go stays with Todd.
- [ ] Self-checks.
- [ ] Holdout 1 and Holdout 2 (fresh agents; never open tools/ or tests): random sample against the City's records and every written promise.
- [ ] Design director (no score under 4, average above 4.6).
- [ ] Legal desk (legal/README.md; the City's data terms word for word).

## 2. Todd's steps (after every gate passes)
1. [ ] Price and go.
2. [ ] GitHub Actions secret for the members' app password (name set when the app is built; never in this repo).
3. [ ] Gumroad product, cover and thumbnail, post-purchase content.
4. [ ] Buyer test, then outreach go.
