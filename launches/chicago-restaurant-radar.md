# Spec: Chicago Restaurant Radar (planned Nov 2, 2026; not built)

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
