# Site Terms of Use page, calculator line, footer link, privacy map loads (Nov 23, 2026)

Todd, live chat, Nov 23, 2026, 8:10 pm ET: "add the OpenStreetMap and cdnjs map loads to the privacy page, and add one site-wide Terms of Use page with an 'estimates only, not advice' line, linked in the footer and under every calculator ... show me both before anything goes live. No spend. Nothing removed."

Risk-control review by AI reviewers, not legal advice. Nothing here is legally approved. Status: NOT CLEARED, held for Todd (round 3 split: one PASS, one FAIL).

## Change
- New /terms/ (tools/make_site.py terms_html, store.json terms.updated), built from the clause library section 4.
- Line under all 51 calculators (calc_terms): "Estimates only, not advice. Your result depends on the numbers you enter. See the Terms of Use."
- "Terms of Use" footer link on all 250 pages with the site footer (foot_nav, plus 3 hand-made thanks pages).
- Privacy: new section "Maps in the members' apps" (Leaflet from cdnjs, OSM tiles, what those servers see), date Nov 23, 2026. Nothing removed.
- Members' apps not touched (they need the list passwords to rebuild and carry their own #/terms).

## Code gates
- check_repo: 0 errors. legal_scan (terms, privacy, one calculator): 0 high, 1 medium ("no as-of date found for figures", a product check; the site page holds no figures).
- verify_site --changed --before --flows: PASS 102 of 102; named pages run: PASS 36 of 36; after fix round: terms and privacy PASS 8 of 8. Every DIFF is the added line or link.
- Diff scope script: 249 html files changed only by the planned additions; sitemap adds only /terms/.

## Fresh reviewers (Opus, given only the finished pages, the apps' code and this file's checklist)
- Round 1: A FAIL 4.17 (Claims 3), B FAIL 4.33 (Claims 3). Fix round applied only what both proposed: list terms win where they differ, Accuracy sentence, trademark list, cdnjs wording, map squares and list details.
- Round 2: C FAIL 4.42 (no score under 4), D FAIL 4.17 (Claims 3, map accuracy 3).
- Open, raised by both C and D: (1) "no ... other details from your list" is too absolute, since map squares show a lead's area (medium); (2) OSMF's hired delivery network not named; (3) Google map and search buttons in the apps send a business name or address when tapped, not disclosed; (4) "design, text and code ... belong to ProofNotFluff" also covers Leaflet, fonts and open data; (5) "every page names the source and date" is unchecked across 51 calculators.
- Split (dropped under the two-checker rule): liability cap (C: precedence line resolves it; D: still medium); workbooks in "Lists you buy" (C only); "medical" in Information only (C only).
- Not checked: live server headers (Referrer-Policy), the free data pages, the other 50 calculators by a reviewer, the Refunds page.
- Pre-existing, outside this change: home footer says Austin data is "Public Domain U.S. Government" while the Austin app cites the City of Austin Open Data Terms; the pest app's Terms omit OpenStreetMap.

## Round 3 (Todd's pick, coo/DECISIONS-2026-11-23.md: fix the 5 shared items, fresh review)
- Fixes: map squares carve-out, OSMF delivery company, Google buttons bullet, ownership line narrowed, Accuracy reworded as an aim with a contact.
- Gates again: check_repo 0 errors; diff scope PASS 249 files; footer 250 of 250; calculator line 51 of 51; 0 dashes; verify_site terms and privacy PASS 8 of 8; legal_scan 0 high.
- E PASS 4.67 (no score under 4). F FAIL 4.33 (no score under 4; average short).
- Both E and F: the Google bullet says "name or address" but two apps send both, with the city; the "Tell us why first" Google Form link in 5 apps is not disclosed; "medical" is missing from Information only.
- F only: write the members' "most recent month" cap into the site Terms; split the long third map bullet; link the email in Accuracy; widen the meta description. E only: set a referrer meta tag in the apps.
- Both, outside this change: the pest app's own Terms omit the OpenStreetMap line. Not checked by either: live server Referrer-Policy header.

## Round 3 fixes (Todd's pick, Nov 24, 2026: fix the 3 shared items, no fourth review, his look decides)
- Google bullet: the name, the address or both, with the city, plus IP, browser and our site's address; the "Tell us why first" Google Form disclosed. "Medical" added to Information only.
- Gates: check_repo 0 errors; diff scope PASS 249 files; footer 250 of 250; calculator line 51 of 51; 0 dashes; legal_scan 0 high; verify_site terms and privacy PASS 8 of 8.
- Not done (one reviewer only, or outside this change): members' liability cap spelled out on the site Terms, bullet split, mailto link, meta description, referrer meta tag in the apps, pest app OSM line, live Referrer-Policy header check.
