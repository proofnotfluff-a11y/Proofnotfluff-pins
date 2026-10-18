# Launch record: Chicago Restaurant Inspection Leads ($39 a month), NOT LAUNCHED

Checklist: design/LAUNCH_CHECKLIST.md. Nothing is published, linked, emailed or promoted until every box below is ticked with proof and Todd says go. Status as of Oct 17, 2026 (list of Oct 17, City records through Oct 16).

## The product
- Members' web app: tools/rest_app.py (overview by trade, three lists with map, filters by category, result, area, date and facility type, search, CSV, place page with the 24-month City inspection history, pitch kit, Terms, workbook download). Published path once the secret exists: docs/chicago-restaurant-leads-members/ (built only by the inspections workflow; nothing is committed there before then).
- Workbook: tools/rest_xlsx.py (Start Here, 1 Failed or conditional, 2 Opening soon, 3 Failed more than once, 4 Inspection history, 5 Pitch kit, Terms).
- Free sample page: docs/chicago-restaurant-inspection-leads/ (site/pages.json kind "restleads", draft, noindex, off the index and sitemap; failed places are never named on it).
- Data: tools/rest_leads.py on the City's Food Inspections dataset (4ijn-s7e5), weekly in .github/workflows/inspections-chicago.yml.
- This week's list: 117 failed or conditional (81 pests, 23 hood, 12 grease trap and drains, 93 cleaning; 98 with a Fail), 130 opening soon (92 passed the license inspection), 23 failed more than once, 52 places new this week, 245 places in all. Left out: 70 schools, colleges, day care, hospitals, senior sites and mobile vendors, 4 places named after a person, 1 out of business.

## 1. The product
- [x] Built to standard (WORKBOOK_STANDARD v3 card language from tools/leads_xlsx.py; the app reuses the construction app's stylesheet and encryption).
- [x] Self-checks: rest_leads --selftest (38 category cases on the City's real titles, 39 name cases, 18 planted inspections), rest_xlsx, rest_app (node checks of dates, CSV guard and result classes), rest_site, rest_seal; check_repo 0 errors with 29 planted failures caught; render_xlsx ERROR VALUES: 0 on screen and print, every tab opened; Playwright at 390 and 1280 on every view (gate, Terms before password, wrong password, overview, trade memory, three lists, filters, CSV, map pins, place page, notes, back button, pitch kit, Terms, workbook download, filter sheet): all pass, no console errors, no horizontal scroll; axe-core 4.10.2 WCAG 2.1 AA 0 violations on every view and on the free page; 44 px touch targets on phone.
- [ ] Holdout PASS: round 1 FAIL (59/60 notes naming another code, ordinance numbers read as codes, duplicate reports across licenses, row codes from the 30-day union, person names, ordinal casing, "soiled", new by own date, colleges). All fixed with planted cases. Round 2: two narrow misses (the one-word "GREASETRAPS" spelling, and "(38)" right after an ordinance number); fixed with planted cases and rebuilt Oct 18, with one shared sentence for who is left out on the workbook, app Terms and free page. Final re-check pending.
- [x] Design director PASS on the app, workbook, free page, cover and thumbnail: round 2 PASS at 4.74, nothing under 4. Fail pins and every key use one square (live session's decision). Round 3 polish items A1 to E1 applied and rebuilt Oct 18.
- [x] Legal desk: CLEARED WITH FIXES; fixes 1 to 10 applied as worded, plus the rodent bait rule (planted case). Open questions for counsel stay with Todd (City indemnity, LLC on the Terms version line, members' TCPA and CAN-SPAM duties).

## 2. The storefront (Gumroad, Todd's account)
- [ ] Product created by Todd (Membership, monthly tier, $39), copy below pasted, cover and thumbnail uploaded (launches/chicago-restaurant-inspection-leads/cover-1280x720.png and thumb-600x600.png, no weekly numbers on either).
- [ ] Post-purchase content: the members' link https://proofnotfluff.com/chicago-restaurant-leads-members/ and the password (Todd has it from the live session; it is never in this repo).
- [ ] The REST_LEADS_PASSWORD Actions secret added (Settings, Secrets and variables, Actions), then the inspections workflow run once so the members' app exists.

## 3. Buy and delivery path
- [ ] Checkout link on the free page (site/pages.json "checkout", then drop "draft").
- [ ] Delivery tested as a buyer: receipt, password, app, workbook in Excel and Google Sheets.

## 4. Outreach
- [ ] Drafts filled from the live list (email/R1-OUTREACH.md; prospects outside the repo) and Todd's go.

## Gumroad copy (paste as is)

Name:
```
Chicago Restaurant Inspection Leads
```

Summary:
```
Every Monday: Chicago restaurants with a failed or conditional City inspection, sorted by pests, hood, grease trap and cleaning violations, plus places about to open.
```

Description:
```
A weekly lead list for Chicago pest control, kitchen hood cleaning, grease trap and commercial kitchen cleaning companies, and for vendors who sell to new restaurants.

Each Monday we pull the City of Chicago's food inspection records and sort them into three lists:

Failed or conditional: places whose inspection in the last 30 days came back Fail or Pass w/ Conditions, with the violation categories you work on (pests and rodents, hood and exhaust, grease trap and drains, cleaning) and the City's violation codes for each.

Opening soon: places that had the license inspection Chicago does before a food license is issued, so many are weeks from opening or just opened, and may be choosing vendors.

Failed more than once: places with two or more failed inspections in 90 days.

What you get:
- A members' web app: pick your trade, filter by category, result, neighborhood and date, see every place on a map, open its 24-month City inspection history, mark who you called and keep private notes, and export any view to CSV.
- The same list as an Excel file that also opens in Google Sheets.
- A pitch kit: a short call opener and an email for each trade.

What it is not: the list repeats the City's recorded result, date and violation codes. It does not say whether any place is clean, safe or open today, and no business listed has endorsed or works with ProofNotFluff. Schools, day care and other children's sites, hospitals, senior sites, mobile vendors and businesses named after a person are left out. You make your own calls and emails.

$39 a month. Cancel any time from your Gumroad library; cancelling stops future charges. Your membership renews monthly until you cancel.

Terms of Use, readable before you buy: https://proofnotfluff.com/chicago-restaurant-leads-members/#/terms

This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk.

ProofNotFluff is not affiliated with or endorsed by the City of Chicago. Licensed to one business for its own prospecting.

Made with AI assistance and reviewed and tested by the shop owner.
```

Tier name: `Monthly`. Price: `$39`.

Paste the "Terms of Use, readable before you buy" line only after the inspections workflow has published the members' app and that link opens the Terms without a password (the app's #/terms view opens before the password; Legal desk fix 9).
