# Launch record: Chicago Construction Cleaning Leads, area seats ($149 a month, one cleaning company per area, 6 areas)

Decided: Todd, live chat, Oct 26, 2026, 8:24 am: "My go on scoreboard row decide-exclusive-area: yes, build the test." Words in coo/DECISIONS-2026-10-26.md. The offer terms below (price, 6 seats, sample by reply, keep the $29 list as the cheaper tier) are the build session's proposal, sent to Todd in chat Oct 26; they become final only on his yes. Checklist: design/LAUNCH_CHECKLIST.md.

Nothing is published, sold, linked or emailed until Todd reviews the offer, the Gumroad products exist and he says go.

## The areas (site/area_seats.json, tools/area_seats.py)
Drawn from permits/chicago/area_counts.json (tools/exclusive_areas.py, GitHub Actions, Oct 26): qualifying projects as the weekly list keeps them, counted by the month the City issued the permit, every status, 12 full months Oct 2025 to Sep 2026. 878 projects, about 73 a month citywide; only the Loop clears 10 alone, so 6 is the most areas that can each average 10. Each area is one connected piece (tools/area_seats.py --selftest checks it, and that all 77 community areas sit in exactly one). This week's counts: permits/chicago/area_week.json (list of Oct 26).

| # | Area | Community areas | New a month (12-mo avg) | Slowest to busiest month | Months under 10 | Open now | New this week |
|---|---|---|---|---|---|---|---|
| 1 | Loop and South Loop | 2 | 15.9 | 8 to 20 | 1 | 170 | 3 |
| 2 | Near North and Lincoln Park | 2 | 11.4 | 3 to 23 | 5 | 191 | 1 |
| 3 | West Loop and West Side | 7 | 12.8 | 6 to 18 | 2 | 198 | 3 |
| 4 | West Town, Logan Square and Northwest | 13 | 10.5 | 4 to 17 | 5 | 184 | 2 |
| 5 | Lake View to Rogers Park | 11 | 10.3 | 5 to 18 | 6 | 179 | 0 |
| 6 | South Side | 42 | 12.2 | 5 to 22 | 3 | 206 | 4 |

- Loop and South Loop (`loop`): Loop, Near South Side
- Near North and Lincoln Park (`near-north`): Near North Side, Lincoln Park
- West Loop and West Side (`west`): Near West Side, Lower West Side, East Garfield Park, West Garfield Park, North Lawndale, South Lawndale, Austin
- West Town, Logan Square and Northwest (`northwest`): West Town, Logan Square, Humboldt Park, Avondale, Hermosa, Belmont Cragin, Portage Park, O'Hare, Dunning, Norwood Park, Jefferson Park, Montclare, Edison Park
- Lake View to Rogers Park (`north`): Lake View, North Center, Lincoln Square, Uptown, Edgewater, Rogers Park, West Ridge, North Park, Albany Park, Irving Park, Forest Glen
- South Side (`south`): Archer Heights, Armour Square, Ashburn, Auburn Gresham, Avalon Park, Beverly, Bridgeport, Brighton Park, Burnside, Calumet Heights, Chatham, Chicago Lawn, Clearing, Douglas, East Side, Englewood, Fuller Park, Gage Park, Garfield Ridge, Grand Boulevard, Greater Grand Crossing, Hegewisch, Hyde Park, Kenwood, McKinley Park, Morgan Park, Mount Greenwood, New City, Oakland, Pullman, Riverdale, Roseland, South Chicago, South Deering, South Shore, Washington Heights, Washington Park, West Elsdon, West Englewood, West Lawn, West Pullman, Woodlawn

## How a seat holder gets the list
- Every Monday the permit workflow (.github/workflows/permits-chicago.yml) pulls the City's permits, then tools/area_seats.py: `--shared` writes the full list without held areas (the $29 list's app, workbook and review file are built from it), `--shared-sample` takes held areas out of the free sample page's projects, `--week-counts` writes this week's counts per area, and `--build` (only while the AREA_SEAT_KEY Actions secret exists) builds one members' app per area at docs/chicago-cleaning-area-members/<slug>/ with only that area's projects, the $29 list's app and Excel file, and the seat clause in its Terms.
- Each seat's password comes from one secret: HMAC-SHA256(AREA_SEAT_KEY, area). The key lives in the build session's scratchpad and is given to Todd once, for the GitHub secret; each password goes into that seat's Gumroad content. A seat that ends gets a new password by adding a rotation number to its area in site/area_seats.json.
- Held areas also leave permits/downstream/gc_leads.json (tools/ingest_downstream.py), the file every cleaning email draws its example job from, so no email to another cleaning company names a held area's job.
- When a seat sells: the session adds its slug to site/area_seats.json held (on Todd's word), the next Monday list leaves it out of the shared list, the free sample and the emails, and the offer shows it as held.

## The offer (tools/area_site.py, on the Chicago Construction Cleaning Leads page, id areas)
- Shown only once a seat has its Gumroad link in site/pages.json areaSeats.checkout.<slug> (or a preview build). The live page does not change until then (checked byte for byte Oct 26).
- The map, 6 areas with their average a month, slowest and busiest month and open count, areas open, $149 a month per area, no lock-in, the public-records line, the 5-newest sample by email, the $29 list kept for areas nobody holds, Gumroad's charge and cancel lines, Seat Terms.

## Outreach
- email/S1-AREA-SEAT.md, gated by tools/copy_gate.py --seat-templates (tools/seat_gate.py, in check_repo): 3 first emails by stage, 2 follow-ups, a last note; the lead must be inside the seat named, the seat not held, the open count this week's.
- Not in email/approved_templates.json: nothing sends until Todd approves the wording in chat and says send.

## Gates
(each a fresh subagent that never saw the build; filled as each verdict comes in)
- Accessibility (axe-core 4.10.2, WCAG 2.1 AA, Oct 26): PASS, 0 violations in 16 states (offer section, seat sign-in, list and Terms; 390 and 1280; light and dark), rerun after the round 1 fixes: 0.
- Holdout A, counts against the City (Oct 26): PASS, BLOCKERS 0. 77 of 77 areas in exactly one seat, each seat connected, every number on the offer and in the launch table recomputed from the files, ours at or under the City's raw count in all 36 area-months checked (12-month City raw 1,558 against our 878), 25 of 25 sample permits in the right seat. Its wording note (an offer bullet said "Every open project") fixed.
- Holdout B, exclusivity and promises (Oct 26): BLOCKERS 2, both fixed: the email gate's fixtures were pinned to the Loop seat (now an open seat, so a sale never breaks the gate), and "held areas leave the downstream emails file" was not provable (now tools/seat_gate.py fails check_repo if any lead in permits/downstream/gc_leads.json sits in a held seat, with planted cases; permits/downstream/gc_areas.json comes from the downstream workflow). Also fixed: the seat footer licence line, one set of open counts on the map and the cards. Round 2: pending gc_areas.json.
- Legal desk (legal/reviews/2026-10-26-area-seats.md): CLEARED WITH FIXES; fixes 1 to 10 and 13 applied in code and copy; fix 11 built (shows when seats go on sale or an area is held) with Todd's paste, notice email and refund decision; fix 12 is Todd's Gumroad setting.
- Copy review round 1: FAIL 4.2 (building build, an unclear ask, a 75-word worst case, a builder-digit gate bug); rewrites and the gate fix applied, then the Legal desk wording. Cold readers (2, no product context): both read it as a lead-list offer; one would reply. Round 2: pending.
- Design director round 1: FAIL (offer 4.14, seat page 4.00, map 4.57); the fixes applied (price under the headline, stats on two lines, the sticky $29 bar steps aside, nav entry, map legend and badges, olive area 6, faint internal lines, seat chip and area in the headlines, no focus box on headlines, honest zero states, seat gate link, page depth for fonts and links). Round 2: pending.
- check_repo: 0 errors on every push (the seat email gate runs in it).

## Gumroad copy (Todd pastes; one Membership product per area, sales limit 1)
Same for all six: tier `Area seat`, `$149` monthly, free trial off, sales limit 1, seller ProofNotFluff, cover and thumbnail from the build session.

Description (all six; replace AREA, COMMUNITY AREAS, VOLUME SENTENCE and SLUG with that seat's lines below):
```
A weekly lead list for one Chicago cleaning company per area.

Every Monday, your members' page shows the open apartment and commercial building permits in AREA with a reported cost of $500,000 or more and a business as general contractor: closest to a final clean first, new permits and near-finish jobs flagged, the builder on each, and the builder's office phone or email where their own website lists one. Mark who you called, keep private notes, and download the Excel file and a CSV. What is left out: permits with no business as general contractor, owner-builder permits, houses and 2 to 3 flats, single condo units, permits marked complete, suspended or cancelled, and work that never needs a construction clean under its own permit. Your area: the City of Chicago community areas COMMUNITY AREAS.

Your seat: one cleaning company holds this area at a time. While your membership is active, ProofNotFluff sells this area's list to no other business and leaves its projects out of the shared Chicago list, the free sample page, the free Monday email and the examples and samples in its emails to other cleaning companies, starting with the first weekly list after you join. Before you joined, shared-list members had this area's projects and other companies may have had its 5 newest as a free sample; we cannot recall those copies. The permits are public City of Chicago records that anyone can read on the City's site, and other companies may sell lists made from them.

What it is not: reported cost is the figure filed with the City, not a contract value. No builder listed has endorsed or works with ProofNotFluff, and a listing is not an invitation to bid. You make your own calls and emails and follow the law when you do.

VOLUME SENTENCE

$149 a month, billed by Gumroad. Renews monthly until you cancel. No lock-in: cancel any time from your Gumroad receipt or library; cancelling stops future charges, your seat stays yours to the end of the month you paid for, and the area is offered to another company only after that. Help: write to hello@proofnotfluff.com with your Gumroad receipt.

Terms of Use, readable before you buy: https://proofnotfluff.com/chicago-cleaning-area-members/SLUG/#/terms

This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk.

ProofNotFluff is not affiliated with or endorsed by the City of Chicago. Licensed to one cleaning business, the only seat holder for this area, for its own prospecting.

Made with AI assistance and reviewed and tested by the shop owner.
```

#### 1. Loop and South Loop
Name:
```
Chicago Cleaning Leads: Loop and South Loop seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in Loop and South Loop, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 16 a month, with months from 8 to 20, and some months under 10. Nothing here promises any number of projects.`
SLUG: `loop`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/loop/ and this seat's password (from the build session, never in this repo).

#### 2. Near North and Lincoln Park
Name:
```
Chicago Cleaning Leads: Near North and Lincoln Park seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in Near North and Lincoln Park, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 11 a month, with months from 3 to 23, and some months under 10. Nothing here promises any number of projects.`
SLUG: `near-north`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/near-north/ and this seat's password (from the build session, never in this repo).

#### 3. West Loop and West Side
Name:
```
Chicago Cleaning Leads: West Loop and West Side seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in West Loop and West Side, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 13 a month, with months from 6 to 18, and some months under 10. Nothing here promises any number of projects.`
SLUG: `west`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/west/ and this seat's password (from the build session, never in this repo).

#### 4. West Town, Logan Square and Northwest
Name:
```
Chicago Cleaning Leads: West Town, Logan Square and Northwest seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in West Town, Logan Square and Northwest, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 11 a month, with months from 4 to 17, and some months under 10. Nothing here promises any number of projects.`
SLUG: `northwest`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/northwest/ and this seat's password (from the build session, never in this repo).

#### 5. Lake View to Rogers Park
Name:
```
Chicago Cleaning Leads: Lake View to Rogers Park seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in Lake View to Rogers Park, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 10 a month, with months from 5 to 18, and some months under 10. Nothing here promises any number of projects.`
SLUG: `north`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/north/ and this seat's password (from the build session, never in this repo).

#### 6. South Side
Name:
```
Chicago Cleaning Leads: South Side seat
```
Summary:
```
Open apartment and commercial projects of $500,000 or more in South Side, Chicago, with a business as general contractor and the builder on each, updated every Monday. One cleaning company holds this area at a time, and no other company we sell to gets its list.
```
VOLUME SENTENCE for this seat: `How many new permits appear each month varies with what the City issues; from Oct 2025 to Sep 2026 this area averaged about 12 a month, with months from 5 to 22, and some months under 10. Nothing here promises any number of projects.`
SLUG: `south`
Post-purchase content: the link https://proofnotfluff.com/chicago-cleaning-area-members/south/ and this seat's password (from the build session, never in this repo).

$29 product (Chicago Construction Cleaning Leads, already live): add this line to its description before the seat offer goes on the page (Legal desk fix 11):
```
Areas held by an area seat holder are left out of this list from the Monday after the seat begins; the product page shows which areas are held, and you can cancel any time.
```

## Todd's steps
(written at hand-over)
