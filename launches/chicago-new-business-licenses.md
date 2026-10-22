# Launch record: Chicago New Business Licenses (price not set), NOT LAUNCHED

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box is ticked with proof and Todd says go. Built by the leads desk builder run (coo/LEADS_DESK.md Run 4), product 4 in the LEADS FOCUS line (coo/PIVOT.md).

Open question for Todd (coo/HANDOFF.md item 4): the live session suggested Chicago building violations for exterior trades instead of this product. Until Todd answers, the builder follows the stated order and builds this one. If he picks violations, this record and tools/licenses_chicago.py stay as they are and the builder switches.

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

## 1. Gates (none run yet)
- [ ] Built to standard: data rules done; free page draft done Oct 22; members' app (tools/leads_app.py pattern), workbook (tools/leads_xlsx.py pattern), free page (site/pages.json, "draft": true, noindex, no checkout), storefront copy and images, outreach email file with one follow-up: to do.
- [ ] Self-checks.
- [ ] Holdout 1 and Holdout 2 (fresh agents; never open tools/ or tests): random sample against the City's records and every written promise.
- [ ] Design director (no score under 4, average above 4.6).
- [ ] Legal desk (legal/README.md; the City's data terms word for word).

## 2. Todd's steps (after every gate passes)
1. [ ] Price and go.
2. [ ] GitHub Actions secret for the members' app password (name set when the app is built; never in this repo).
3. [ ] Gumroad product, cover and thumbnail, post-purchase content.
4. [ ] Buyer test, then outreach go.
