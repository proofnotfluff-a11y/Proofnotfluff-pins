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
