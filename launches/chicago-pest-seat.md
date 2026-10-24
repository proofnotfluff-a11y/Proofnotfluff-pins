# Launch record: Chicago Pest Daily List, the $149 founding seat (move 3), NOT ON SALE

Decided: Todd, Oct 23 (outside audit, move 3: "$149 a month, real cap of 3 seats per trade in Chicago, kept for good. Gumroad checkout") and Oct 24 (pest control only, hood waits; kill date; subject rule; "no lock-in" and the funnel stages). coo/DECISIONS-2026-10-23.md, coo/DECISIONS-2026-10-24.md. Scoreboard rows move3-founding-seat, move6-pest-email; leadproducts/chicago-pest-seat.

Nothing is published, sold, linked or emailed until Todd reviews the offer, creates the Gumroad product and says go.

## How a seat holder gets the list
- Every morning about 6:45 am Chicago time (11:45 UTC), .github/workflows/inspections-daily.yml pulls the City's Food Inspections data after its overnight refresh, builds the daily list (tools/rest_daily.py), fills listed phones (tools/phones.py, free sources only), seals the named list, stamps counts on permits/inspections-chicago/daily.json and builds the members' page docs/chicago-pest-daily-members/ (tools/seat_app.py), locked with the seat password.
- The page: new pest places this morning, then every pest place sent in the last 14 days by the morning it went out; name, street, ZIP, area, facility type, the City's result, type, date and codes in our words, failed visits in 90 days, listed phone with a Call button, the City record link, called marks and notes in the member's browser, a CSV download, a stale-day notice, Terms with the phone lines and license texts before the password.
- Gumroad's post-purchase content holds the page link and the seat password. Nothing for Todd day to day.
- The page is built only while the REST_SEAT_PASSWORD Actions secret exists. The password lives in the build session's scratchpad (never in the repo, a log or a commit) and is given to Todd once, at the Gumroad step.
- Shared password: when a seat ends, the session makes a new password; Todd swaps the secret and the Gumroad content, and Gumroad's update to members carries the new one.

## The offer
- On the restaurant page (site/pages.json restleads "seat", tools/rest_site.py seat_html), shown only once seat.checkout holds the Gumroad link: the cap as the headline, seats open (seat.taken), "No lock-in", the public-records line, 14 days of daily pest counts by City inspection date, exact phone coverage, what a seat gets, and the uncapped weekly list disclosed. The eyebrow, hero note, CTA title and sticky bar move from "every Monday" to daily and weekly at the same moment.
- Once seat.checkout exists, the daily workflow rebuilds the site each morning so the counts stay fresh.

## Outreach
- email/P1-PEST-SEAT.md (first email, its n = 1 form, two follow-ups), gated by tools/copy_gate.py --pest-templates (in check_repo) and --pest on each batch. Batch file data/work/pest_drafts.json (gitignored).
- Funnel (Todd, Oct 24, 11:52 am), counted in the CRM (meta/products.chicago-pest-seat.funnel; per prospect firstSentAt, repliedAt, sampleRequestedAt, yesAt, trialStartedAt, seatPaidAt) and on the scoreboard (leadproducts/chicago-pest-seat.outreach): delivered, replies, sample requests, yes replies, trials started, paid seats.
- Kill: Nov 30, 0 seats from 100 delivered emails plus 2 follow-ups. A focus decision, not proof the offer failed.

## Gates
(filled below as each verdict comes in)
- Holdout round 1 (Oct 24): 2 blockers (a hospital patient kitchen on the list; f90 label), fixed with planted cases. Round 2 (fresh checker): BLOCKERS 0, 41 of 41 places rebuilt from the City rows, every offer and email number matches.
- Legal desk (legal/reviews/2026-10-24-pest-seat.md): cleared with fixes; 1 to 12, 14 and 15 applied; 13 (subject wording) goes to Todd.
- Copy review: round 1 FAIL 4.0, rewrites applied; round 2 PASS 4.62 (fresh reviewer), its rewrites applied; changed lines re-checked PASS.
- Accessibility: browser suite 149 PASS, 0 FAIL; axe-core 4.10.2 WCAG 2.1 AA 0 violations on the offer page, the members' sign-in, list and Terms, at 390 and 1280, light and dark.
- Design director: round 1 FAIL (offer 4.00, members 3.86), fixes applied; round 2 offer PASS 4.71, members FAIL 4.57, fixes applied; round 3 members PASS 4.64; small polish applied after (tab keeps sign-in on reload, dark key tile, heading space).
- check_repo: 0 errors on every push (copy gate now runs --pest-templates).

## Gumroad copy for the seat product (Todd pastes)

Name:
```
Chicago Pest Daily List: founding seat
```

Summary:
```
Every morning: Chicago food places whose failed or conditional City inspection had a pest violation, named, with street, City codes and the listed phone when we find one. At most 3 Chicago pest control companies hold a seat at a time.
```

Description:
```
A daily lead list for Chicago pest control companies.

Each morning, after the City of Chicago's overnight update, your members' page shows the food places whose failed or conditional City inspection had a pest violation, with the last 14 days kept so a missed morning loses nothing. Each place: name, street, ZIP, community area, the City's result, inspection type, date and violation codes, a newer City result when there is one, failed visits in the last 90 days, the listed phone when the business name and address both match, and a link to the City's own record. Mark who you called, keep private notes, and download a CSV.

What it is not: the list repeats the City's recorded result and codes. A pest violation can be insects or rodents seen, or a gap or record the City says lets pests in. It does not say any place is clean, unsafe or open today, and no business listed has endorsed or works with ProofNotFluff. License inspections, schools, day care and other children's sites, hospitals, care sites, shelters, mobile vendors and places whose name is only a person's name are left out. You make your own calls and follow calling laws.

$149 a month, billed by Gumroad. Renews monthly until you cancel. No lock-in: cancel any time from your Gumroad receipt or library; cancelling stops future charges.

At most 3 Chicago pest control companies hold a seat at a time. The same City records reach the weekly Chicago Restaurant Inspection Leads list ($39 a month, not capped) each Monday.

Terms of Use, readable before you buy: https://proofnotfluff.com/chicago-pest-daily-members/#/terms

This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk.

ProofNotFluff is not affiliated with or endorsed by the City of Chicago. Licensed to one pest control business for its own prospecting.

Made with AI assistance and reviewed and tested by the shop owner.
```

Tier name: `Founding seat`. Price: `$149` monthly. Free trial: off. Sales limit: 3 if Gumroad offers it (Legal fix 8).
Post-purchase content: the members' link https://proofnotfluff.com/chicago-pest-daily-members/ and the seat password (from the build session; never in this repo).

## Todd's steps, in order (handed over Oct 24)
1. GitHub: add the Actions secret REST_SEAT_PASSWORD with the seat password from the build chat.
2. Tell the session. It runs the daily list once, so the members' page and its Terms (open without the password) go live, locked, and checks #/terms.
3. Gumroad: a new Membership product (not a tier on the $39 product, whose content holds the $39 password): copy above, tier "Founding seat" $149 monthly, free trial off, sales limit 3 if offered, content = members' link and seat password. Publish, send the link.
4. The session puts the link in site/pages.json seat.checkout (the offer and the daily/weekly headlines go live together) on Todd's go, and the daily workflow refreshes the counts each morning.
5. Outreach: CRM meta/products.chicago-pest-seat.outreachGo true only on Todd's word; batches through email/P1-PEST-SEAT.md and copy_gate --pest; nothing sends without "send".

## Open
- Subject wording (Legal fix 13): Todd's call.
- Named pest owners: 1 of 50 pest companies in the CRM has a named owner with an owner-read email (Oct 24). The kill rule needs 100 delivered first emails by Nov 30, so prospect-matching must add pest owners (and about 50 more pest companies). The Oct 24 site checks could not run: reading company sites from the prospect file needs Todd's approval in chat.
