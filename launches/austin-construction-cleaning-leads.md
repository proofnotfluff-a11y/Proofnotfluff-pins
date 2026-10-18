# Launch record: Austin Construction Cleaning Leads ($29 a month), NOT LAUNCHED

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box below is ticked with proof and Todd says go. Status as of Oct 18, 2026 (list of Oct 18, City of Austin data pulled 10:55 am Central).

## The product
- Data: tools/permits_austin.py on the City of Austin's Issued Construction Permits (dataset 3syk-w9eu), weekly in .github/workflows/permits-austin.yml (Mondays). Every commercial building permit issued in the last 24 months is pulled and checked against the City's own row count (never a capped page), plus every building permit of the same master permits.
- Members' web app: tools/leads_app.py, the same code as Chicago's v2 app, by city through tools/leads_cities.py. Published path: docs/austin-leads-members/ (https://proofnotfluff.com/austin-leads-members/), built and encrypted in Actions only when the AUSTIN_LEADS_PASSWORD secret exists. Nothing is committed there before then; the paid list is never committed in the clear.
- Workbook: tools/leads_xlsx.py, the same code as Chicago's (Start Here, 1 Near finish, 2 New this week, 3 All projects, 4 Builders, 5 Pitch kit, Terms).
- Free sample page: docs/austin-construction-cleaning-leads/ (site/pages.json, draft, noindex, no checkout).
- Storefront images: launches/austin-construction-cleaning-leads/cover-1280x720.png and thumb-600x600.png (cover.html, thumb.html, style.css; examples from the Oct 18 list, no builder or person named).
- This week's list (Oct 18): 160 projects, 416 open building permits, $6,667,343,254 total valuation (about $6.7 billion), 4 near finish (some permits finaled), 111 builders, 97 new construction, 17 finish-outs, 46 remodels or additions, 141 of 160 on the map (58 pinned by the US Census Bureau geocoder where the City gives no coordinates). 8,760 City rows read.

## The rules (tools/permits_austin.py; planted cases in --selftest)
1. Window: building permits issued in the last 24 months (from the Central date of the pull), status Active and not past the City's expiry date.
2. Real clean-up work: commercial and multifamily buildings only. Out: class 329 structures (carports, pergolas, canopies, enclosures, pools, EV chargers), class 321 parking garages, houses, duplexes and three-unit buildings, shell-only, interior demolition, repairs, small accessory structures and garages, and roof, equipment, generator, fuel, solar, sign, elevator, fence, site and exterior-only work.
3. Projects: building permits grouped by master permit; one development under two master permits (same address, valuation and builder) is one project. Homes are the City's housing units on the kept permits; "new homes" on the free page counts only new buildings (classes 104 to 106, work class New). Valuation is the largest valuation on any of its building permits, once; the project is kept at $500,000 or more.
4. Builder: the General Contractor the City lists on the kept permits, a business only (never a person's name, phone, applicant or owner), cleaning companies out, grouped by legal entity; a name filed with no legal suffix joins the one suffixed entity of the same name (Rogers Obrien Construction is Rogers-O'Brien Construction Co. Ltd), while an LLC and an Inc of the same name stay apart.
5. Stage: Some permits finaled (a building permit of the project issued in the window is Final), Work under way (the City pushed an expiry date past the first 180 days), else Permit issued. New this week: the project's first kept building permit was issued in the last 7 days.

## 1. Gates
- [x] Built to standard: the Chicago app and workbook code, by city. Chicago unchanged: workbook cell for cell identical, app payload identical, rendered app identical on 22 routes at 390 and 1280 px (Playwright DOM compare, Oct 18).
- [x] Self-checks: permits_austin --selftest (68 planted permits, 11 window cases, 8 builder cases, 11 scope cases, 5 planted projects, twin merge); leads_xlsx, leads_app, leads_page selftests (Austin cases added); check_repo 0 errors; render_xlsx ERROR VALUES: 0 on every tab; tools/leads_check.py 66 checks, 0 failures at 390 and 1280 px on an app built with the real password from the City's real rows with made-up addresses and builders (the cloud cannot reach the City's portal, so the real list is built only in Actions).
- [ ] After the secret: run the workflow, then tools/leads_check.py on the real app (both widths) and look at the screenshots.
- [ ] Holdout PASS (independent check against the City's data and every promise below).
- [ ] Design director PASS (app, workbook, free page, cover, thumbnail).
- City of Austin Open Data Terms of Use read Oct 18, 2026 (https://data.austintexas.gov/stories/s/ranj-cccq, read in Todd's browser by the live session): the data is public domain and "offered free and without restriction"; no indemnity; attribution should credit the City of Austin and the source department (we credit "City of Austin, Austin Development Services" on the free page, the app, the workbook and Gumroad); the City logo is not used and must not be; the City "may require the termination of any and all displays, distribution, or other use"; Confidentiality: users "will not take any measures to re-identify the data or to contact individuals whose information is represented by the data" and "shall not combine the data with data from any other datasets for the purpose of re-identification of individuals". Applied: the Austin Terms (app #/terms, workbook Terms tab) carry a "Businesses only" clause and the City's right to stop or change the feed; the Gumroad description says the same. Recorded in permits/austin/source-terms.txt (tools/permits_austin.py writes it every run).
- [ ] Legal desk cleared (the City of Austin disclaimer is the dataset's own text, word for word; the Open Data Terms of Use page is linked; its PDF text could not be extracted in the runner, so Legal reads it at https://data.austintexas.gov/stories/s/ranj-cccq).

## 2. Todd's steps, in order
1. [ ] GitHub: add the Actions secret AUSTIN_LEADS_PASSWORD (Settings, Secrets and variables, Actions) with the password the live session gives you. It is never in this repo.
2. [ ] Tell the session. It runs the Austin permits workflow once, so the members' app is published at https://proofnotfluff.com/austin-leads-members/, and runs tools/leads_check.py on it.
3. [ ] Gumroad: new Membership product, tier `Monthly` at $29. Paste Name, Summary and Description below. Cover and thumbnail from launches/austin-construction-cleaning-leads/. Post-purchase content: the members' link and the password. Publish, then send the checkout link to the session.
4. [ ] The session puts the checkout link on the free page (site/pages.json "checkout"), drops "draft", and rebuilds the site.
5. [ ] Buy once as a buyer (then refund): receipt, password, app, workbook in Excel and Google Sheets.

## Promises the product makes (for the holdout)
- Every open Austin commercial and apartment project valued at $500,000 or more with a business as general contractor, from building permits issued in the last 24 months that are still Active; updated every Monday.
- Projects are the City's building permits grouped by master permit; valuation is the largest on any of the project's building permits, counted once.
- Left out: houses, duplexes, three-unit buildings, structures that are not buildings, parking garages, small accessory structures, shell-only, interior demolition, repairs, roof, equipment, sign, elevator, site and exterior-only work; cleaning companies listed as contractor.
- The general contractor on each project, a business only; no person's name, phone or email anywhere. No builder phone numbers or emails are promised.
- Closest to a final clean first; stages Permit issued, Work under way, Some permits finaled as defined above; new this week = first building permit issued in the last 7 days.
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

Stages come from the City's own permit fields: Permit issued; Work under way, when the City has pushed a permit's expiry date past the first 180 days, which it does when an inspection passes or an extension is granted; and Some permits finaled, when part of the project is marked Final while the rest is open.

What it is not: valuation is the largest valuation filed on a project's City building permits, not a contract value or a budget. The list names the general contractor the City lists; it does not include builder phone numbers or emails, and you make your own calls and emails. No builder listed has endorsed or works with ProofNotFluff. Houses, duplexes, carports, pergolas, parking garages, shell-only buildings, demolition, and roof, equipment, sign and site work are left out; the full rule is on the free sample page and in the Excel file. Free sample: https://proofnotfluff.com/austin-construction-cleaning-leads/

$29 a month. Cancel any time from your Gumroad library; cancelling stops future charges. Your membership renews monthly until you cancel.

Terms of Use, readable before you buy: https://proofnotfluff.com/austin-leads-members/#/terms

Source data: City of Austin, Austin Development Services, published on data.austintexas.gov, used under the City of Austin Open Data Terms of Use and modified by ProofNotFluff. Austin Development Services Data Disclaimer: 1. The data provided are for informational use only and may differ from official department data. 2. Austin Development Services’ database is continuously updated, so reports run at different times may produce different results. Care should be taken when comparing against other reports as different data collection methods and different data sources may have been used. 3. Austin Development Services does not assume any liability for any decision made or action taken or not taken by the recipient in reliance upon any information or data provided.

ProofNotFluff is not affiliated with or endorsed by the City of Austin. Licensed to one business for its own prospecting of businesses: as the City's terms require, don't use the list to identify or contact individual people, or combine it with other data to do so. The City may stop or change its data feed at any time.

Made with AI assistance and reviewed and tested by the shop owner.
```

Tier name: `Monthly`. Price: `$29`.

Members' link for the post-purchase content: https://proofnotfluff.com/austin-leads-members/ (with the password). Paste the Terms line and the members' link only after step 2: the app and its #/terms view exist only once the workflow has built them.
