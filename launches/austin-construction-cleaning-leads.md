# Launch record: Austin Construction Cleaning Leads ($29 a month), NOT LAUNCHED

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box below is ticked with proof and Todd says go. Status as of Oct 18, 2026 (list of Oct 18, City of Austin data pulled 10:55 am Central).

## The product
- Data: tools/permits_austin.py on the City of Austin's Issued Construction Permits (dataset 3syk-w9eu), weekly in .github/workflows/permits-austin.yml (Mondays). Every commercial building permit issued in the last 24 months is pulled and checked against the City's own row count (never a capped page), plus every building permit of the same master permits.
- Members' web app: tools/leads_app.py, the same code as Chicago's v2 app, by city through tools/leads_cities.py. Published path: docs/austin-leads-members/ (https://proofnotfluff.com/austin-leads-members/), built and encrypted in Actions only when the AUSTIN_LEADS_PASSWORD secret exists. Nothing is committed there before then; the paid list is never committed in the clear.
- Workbook: tools/leads_xlsx.py, the same code as Chicago's (Start Here, 1 Near finish, 2 New this week, 3 All projects, 4 Builders, 5 Pitch kit, Terms).
- Free sample page: docs/austin-construction-cleaning-leads/ (site/pages.json, draft, noindex, no checkout).
- Storefront images: launches/austin-construction-cleaning-leads/cover-1280x720.png and thumb-600x600.png (cover.html, thumb.html, style.css; examples from the Oct 18 list, no builder or person named).
- This week's list (Oct 18, Actions build 7d46475): 158 projects, 362 open building permits, $6,242,314,201 total valuation (about $6.24 billion), 1 near finish, 108 builders (one spelling per entity), 104 new construction, 12 finish-outs, 42 remodels or additions, at least 8,303 homes in new buildings, 138 of 158 on the map (54 pinned by the US Census Bureau geocoder). 8,760 City rows read. Valuations filed a few dollars over a round figure ($26,668,001; $18,000,001) are footnoted as filed. Confirmed against the City's own rows (probes/austin-confirm.json): 6801 River Place Blvd is $1,525,000,000 as filed on permit 2026-025330; 610 Davis St carries the tower's $180,000,000 on every floor's finish-out, and only the Level 55 permit is in the window.

## The rules (tools/permits_austin.py; planted cases in --selftest)
1. Window: building permits issued in the last 24 months, counted inclusively from the Central date of the pull (a pull on Oct 18, 2026 keeps permits issued on or after Oct 18, 2024), status Active and not past the City's expiry date.
2. Real clean-up work: commercial and multifamily buildings only. Out: class 329 structures (carports, pergolas, canopies, enclosures, pools, EV chargers), class 321 parking garages, houses, duplexes and three-unit buildings, shell-only, interior demolition, repairs, small accessory structures and garages, and roof, equipment, generator, fuel, solar, sign, elevator, fence, site and exterior-only work.
3. Projects: building permits grouped by master permit; one development under two master permits (same address, valuation and builder) is one project. Valuation is the largest valuation on the project's kept permits (open, in the window, real clean-up work), counted once; valuations on finaled, shell, garage or older permits of the same master never count, and the $500,000 floor uses the same figure. Homes: the City's housing units on residential buildings (classes 104 to 106) and on finish-outs or remodels of homes, blank on non-residential work; when the other permits of a project repeat the same number it counts once, and class 104 permits (one 3 or 4 home building each) always add up. "New homes" on the free page counts only new buildings (classes 104 to 106, work class New).
4. Builder: the General Contractor the City lists on the kept permits. The City's company name is a business unless it is the contractor's own name in the City record (the full name is read only for this test and never written) or two plain words starting with a common first name and no business word (holdout D, Oct 18: Gordon Highlander); no phone, applicant or owner field is read. Cleaning companies out. One builder per legal entity, spelled one way everywhere: punctuation, "(Main)" tags and Co or Company never split a builder, a name with no entity type joins the one typed entity of its name, an LLC and an Inc of one name stay two.
5. Stage: Near finish (a building permit of the project issued in the window is Final), Work under way (the City pushed an expiry date past the first 180 days), else Permit issued. New this week: the project's first kept building permit was issued in the last 7 days.
6. Rulings on the holdout's borderline cases (Oct 18): 13686134 (interior renovation of an industrial facility with exterior equipment, a wet scrubber and an emergency generator) is out, as process-equipment work like Chicago's rule; 13351047 (airport baggage claim system reconfiguration) is out, as equipment; 13501889 (Gordon Highlander) is out (holdout D: the builder name is a person's name with no business word); 13604598 is out (the City lists "*MAIN" as contractor, no business); 13347837 (Schaffer Construction, a new 9,566 sq ft convenience store with its fuel canopy, class 327) is in.

## 1. Gates
- [x] Built to standard: the Chicago app and workbook code, by city. Chicago unchanged: workbook cell for cell identical, app payload identical, rendered app identical on 22 routes at 390 and 1280 px (Playwright DOM compare, Oct 18).
- [x] Self-checks: permits_austin --selftest (77 planted permits, 11 window cases, 22 builder cases, 14 scope cases, 10 planted projects, 13 builder groupings, twin merge, 12 addresses); leads_xlsx, leads_app, leads_page selftests; check_repo 0 errors; render_xlsx ERROR VALUES: 0; Chicago workbook identical cell for cell and Chicago app DOM identical on 22 routes at 390 and 1280 px.
- [x] Real app built in Actions (AUSTIN_LEADS_PASSWORD set): tools/leads_check.py on docs/austin-leads-members/ 67 checks, 0 failures at 390 and 1280 px, run in Actions on every build (probes/austin-app-check.txt, 7d46475); screenshots captured there into docs/assets/leads/austin/ (members-list.png, members-list-phone.png, workbook.png, workbook-phone.png).
- [x] Holdout PASS: rounds A to D (Oct 18); holdout D's four items fixed and re-checked on the Actions build 7d46475 (13604598 and 13501889 out, Flynn Construction without its tag, 13347837 in), plus the round 4 findings (Austin Bridge and Jordan Foster are businesses; work under way from any open permit of a project).
- [x] Design director PASS: round 3 failed at 4.14; round 4 re-check of the 20 items 4.58 (FAIL, phone images cropped); round 4 fixes re-checked at 4.70, no item under 4 (bar: none under 4, average above 4.6). Open nit for a later pass: the All projects stat strip's first gap is about 1.5 times the others (scored 4).
- City of Austin Open Data Terms of Use read Oct 18, 2026 (https://data.austintexas.gov/stories/s/ranj-cccq, read in Todd's browser by the live session): the data is public domain and "offered free and without restriction"; no indemnity; attribution should credit the City of Austin and the source department (we credit "City of Austin, Austin Development Services" on the free page, the app, the workbook and Gumroad); the City logo is not used and must not be; the City "may require the termination of any and all displays, distribution, or other use"; Confidentiality: users "will not take any measures to re-identify the data or to contact individuals whose information is represented by the data" and "shall not combine the data with data from any other datasets for the purpose of re-identification of individuals". Applied: the Austin Terms (app #/terms, workbook Terms tab) carry a "Businesses only" clause and the City's right to stop or change the feed; the Gumroad description says the same. Recorded in permits/austin/source-terms.txt (tools/permits_austin.py writes it every run).
- [x] Legal desk cleared per the live session's Oct 18 reading of the City of Austin Open Data Terms (handoff: "Legal: CLEAR"); the only copy change since is the stage name Near finish. (the City of Austin disclaimer is the dataset's own text, word for word; the Open Data Terms of Use page is linked; its PDF text could not be extracted in the runner, so Legal reads it at https://data.austintexas.gov/stories/s/ranj-cccq).

## 2. Todd's steps, in order
1. [x] GitHub: add the Actions secret AUSTIN_LEADS_PASSWORD (Settings, Secrets and variables, Actions) with the password the live session gives you. It is never in this repo.
2. [x] Tell the session. It runs the Austin permits workflow once, so the members' app is published at https://proofnotfluff.com/austin-leads-members/, and runs tools/leads_check.py on it.
3. [ ] Gumroad: new Membership product, tier `Monthly` at $29. Paste Name, Summary and Description below. Cover and thumbnail from launches/austin-construction-cleaning-leads/. Post-purchase content: the members' link and the password. Publish, then send the checkout link to the session.
4. [ ] The session puts the checkout link on the free page (site/pages.json "checkout"), drops "draft", and rebuilds the site.
5. [ ] Buy once as a buyer (then refund): receipt, password, app, workbook in Excel and Google Sheets.

## Promises the product makes (for the holdout)
- Every open Austin commercial and apartment project valued at $500,000 or more with a business as general contractor, from building permits issued in the last 24 months that are still Active; updated every Monday.
- Projects are the City's building permits grouped by master permit; valuation is the largest valuation on the project's open building permits on the list, counted once (finaled, shell and garage permits do not count).
- Left out: houses, duplexes, three-unit buildings, structures that are not buildings, parking garages, small accessory structures, shell-only, interior demolition, repairs, roof, equipment, sign, elevator, site and exterior-only work; cleaning companies listed as contractor.
- The general contractor on each project, a business only; no person's name, phone or email anywhere. No builder phone numbers or emails are promised.
- Closest to a final clean first; stages Permit issued, Work under way, Near finish as defined above; new this week = first building permit issued in the last 7 days.
- Members' app: overview, project list with stage, ZIP code, valuation, building type, new and follow-up filters, map, project page with every building permit (up to 40), builder pages, private contacted marks and notes, CSV export with an All builders column, pitch kit, Terms view readable before the password, the workbook download.
- Excel file that also opens in Google Sheets; dates in Central time; $29 a month, cancel any time.

## Gumroad copy (paste as is)

Name:
```
Austin Construction Cleaning Leads
```

Summary:
```
Every Monday: Austin's open commercial and apartment building projects valued at $500,000 or more, the general contractor on each, closest to a final clean first.
```

Description:
```
A weekly lead list for Austin post-construction cleaning, window cleaning and pressure washing companies.

Each Monday we pull the City of Austin's Issued Construction Permits records and keep the projects worth a call: commercial and apartment building projects with building permits issued in the last 24 months that are still active, valued at $500,000 or more, with a business listed as general contractor. Austin issues a building permit for each building and often for each floor of finish-out, so we group them into projects by the City's master permit.

What you get:
- A members' web app: projects closest to a final clean first, filters by stage, ZIP code, valuation and building type, every project on a map, a page for each project with the building permits behind it, a page for each builder with all their open projects, private contacted marks and notes, and CSV export of any view.
- The same list as an Excel file that also opens in Google Sheets.
- A pitch kit: a one-page capability sheet outline and an email to builders you can adapt.

Stages come from the City's own permit fields: Permit issued; Work under way, when the City has pushed a permit's expiry date past the first 180 days, which it does when an inspection passes or an extension is granted; and Near finish, when part of the project is marked Final while the rest is open.

What it is not: valuation is the largest valuation filed on a project's open City building permits on the list, not a contract value or a budget. The list names the general contractor the City lists; it does not include builder phone numbers or emails, and you make your own calls and emails. No builder listed has endorsed or works with ProofNotFluff. Houses, duplexes, carports, pergolas, parking garages, shell-only buildings, demolition, and roof, equipment, sign and site work are left out; the full rule is on the free sample page and in the Excel file. Free sample: https://proofnotfluff.com/austin-construction-cleaning-leads/

$29 a month. Cancel any time from your Gumroad library; cancelling stops future charges. Your membership renews monthly until you cancel.

Terms of Use, readable before you buy: https://proofnotfluff.com/austin-leads-members/#/terms

Source data: City of Austin, Austin Development Services, published on data.austintexas.gov, used under the City of Austin Open Data Terms of Use and modified by ProofNotFluff. Austin Development Services Data Disclaimer: 1. The data provided are for informational use only and may differ from official department data. 2. Austin Development Services’ database is continuously updated, so reports run at different times may produce different results. Care should be taken when comparing against other reports as different data collection methods and different data sources may have been used. 3. Austin Development Services does not assume any liability for any decision made or action taken or not taken by the recipient in reliance upon any information or data provided.

ProofNotFluff is not affiliated with or endorsed by the City of Austin. Licensed to one business for its own prospecting of businesses: as the City's terms require, don't use the list to identify or contact individual people, or combine it with other data to do so. The City may stop or change its data feed at any time.

Made with AI assistance and reviewed and tested by the shop owner.
```

Tier name: `Monthly`. Price: `$29`.

Members' link for the post-purchase content: https://proofnotfluff.com/austin-leads-members/ (with the password). Paste the Terms line and the members' link only after step 2: the app and its #/terms view exist only once the workflow has built them.
