# Spec: Chicago Restaurant Radar (built Nov 2, 2026; private preview, waiting on Todd's go)

Todd, live chat, Nov 2, 2026, about 1:30 pm, after the New Home Radar reel teardown
(video/studio/research/runs/2026-11-02-new-home-radar-reel.md), picked "Both, restaurants first": build a Radar on our
own data, restaurants first, the homeowner version after the Legal desk. Major under CONSTITUTION 2 (new product and
page type): every step below goes to Todd before it publishes.

## What it is
A members' app that follows every Chicago food business from build-out to opening and tells a vendor who to reach this
week, in a rule they type in plain English. The engine he showed, on records we already pull, business fields only.

## The record's path (the spine of the app and of the reel)
| Stage | City record we already have | Tool |
|---|---|---|
| Permitted | Building permit at the address (build-out, kitchen, signs) | permits/chicago, tools/permit_ingestion and the downstream workflow |
| Licensed | New business license, application type Issue (r5kz-chrr) | tools/licenses_chicago.py (food segment: 90 in the 30 days to Nov 2) |
| Inspected | License (pre-opening) food inspection and its result (4ijn-s7e5) | tools/inspections_chicago.py |
| Open | First routine inspection passed, or 30 days after a passed license inspection | same |
Join on normalized address plus license number where the inspection carries it. Each stage shows its date and a link to the
City's own record.

## Screens
1. Today: counters (food businesses moving toward open, new this week by stage), the community area map (tools/geo_map.py),
   newest first table: business, area, stage, last date.
2. One business: the timeline of its city records, then the first letter or email for the chosen trade, filled for it.
3. Rules: a box for plain English ("pest control, within 3 miles of 60631, licensed or inspected, newest first"). Parsed in
   the browser by a fixed grammar (trade, place and radius, stage, type of food business, order) into chips the member can
   see and remove; words it can't read are shown, never guessed. No AI call and no cost per query. Miles, not drive time:
   drive time needs a routing service (spend, Todd's yes).
4. Trade switch: pest, hood and exhaust, grease trap, commercial cleaning, POS, signs, insurance. Same rows, the letter changes.

## Out of v1 (each needs Todd's yes)
Printing and mailing letters (a print-and-mail service costs money); drive time; a price (today's restaurant leads are $39;
PLAN V2 band $29 to $199).

## Rules it keeps
Business fields only; licenses already drop home addresses and names that could be a person's; the existing do-not-lists;
inspector names and comments never shown. Letters pass the copy gate. Ships through design/LAUNCH_CHECKLIST.md: Legal desk,
check_repo, verify_site, axe WCAG 2.1 AA, design director.

## Then the reel
A studio lesson in a new "radar" demo shape after the app is live: one real restaurant's path from permit to license to
inspection, the letter a pest owner would send it, a rule typed in plain English, the trade switch. Business records only.
Beats from the teardown; our own scenes and look.

## Phase 2: New Homeowner Radar (waits on Todd and the Legal desk)
Cook County Assessor Parcel Sales (datacatalog.cookcountyil.gov, dataset wvhk-k5uv, updated about twice a month) names the
buyer on most sales. Homeowners are private people, so this needs: Todd's change to CONSTITUTION 4 (today only business
decision-makers may be stored), a Legal desk review (Illinois and federal rules on mail marketing to new owners, an opt-out
list, no names on any public page or video), and a print-and-mail budget.

## Comment-to-DM (Todd: "Allow it", Nov 2)
Not active until Todd picks a tool and plan and the CONSTITUTION line is written in a live chat. Price notes (secondary
sources; manychat.com was blocked from the cloud session): ManyChat's free plan fell to 25 active contacts on Mar 2, 2026,
Essential from $14 a month billed yearly for 250, Pro from $29; Inro's free plan lists 100 active contacts. Recheck on the
vendors' own pages before Todd decides.

## Build record, Nov 2, 2026 (live session; major under CONSTITUTION 2: nothing on proofnotfluff.com, no price, nothing sent)
- Code: tools/radar_chicago.py (the join, runner only), .github/workflows/radar-chicago.yml (dispatch or push; seals the list to
  permits/radar-chicago/radar-seal.pub.pem, commits counts-only match.json), tools/radar_letters.py (7 trade letters, one source),
  tools/copy_gate.py --radar-templates and --radar-live, tools/radar_app.py (Today, One business, Rules, Trades, Terms; preview or
  encrypted build). The private key that opens list.sealed.json stayed with the live session; a new session makes a new key pair
  (one commit of the .pub.pem) and reruns the workflow.
- Real order of the City's records: the pre-opening license inspection comes before the license (320 of 322), so the stages run
  Permitted, Inspected, Licensed, Open.
- Join (run of Nov 2, 4:30 pm): 339 new food licenses in 180 days; 322 (95.0%) to their license inspection by license number; 128
  (37.8%) to a permit at the address, 86 (25.4%) whose text names food work; 125 (36.9%) all three. Plus 102 inspected with no license
  yet and 49 food build-out permits for a new place. 490 businesses, 232 not open yet. Open: 17 by a routine City inspection, 241 by
  our 30-day rule (labelled). Left out: relicenses and existing businesses (49 same name inspected here before, 55 relicensed, 67
  added a license), 106 permits for work at a place already there, 18 sites with a current food license.
- Gates: copy gate PASS (3,430 live letters, 490 x 7); holdout PASS 5 of 5 on round 3 (rounds 1 and 2 failed and were fixed: Express
  permits, relicenses, one row per business, shared addresses, repair permits); 10 typed rules read as planted; verify_site PASS
  (6 of 6, flow 22 of 22 at 390 and 1280); axe WCAG 2.1 AA 0 violations on 9 screens at 390 and 1280; design director rounds
  3.29, 3.86, 3.86, 4.57, then PASS 4.71 on round 5 (no score under 4); its last polish notes applied after.
- Before go: Todd's look and word; Legal desk (the three datasets' terms, the letters' CAN-SPAM lines); a RADAR_PASSWORD secret
  only Todd adds; a price inside PLAN V2; then the members' build and the free page through make_site.py.

