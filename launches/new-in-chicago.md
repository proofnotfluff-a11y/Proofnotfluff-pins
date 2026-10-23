# Launch record: New in Chicago (free traffic page), LIVE Oct 23, 2026

Todd's traffic layer (coo/DECISIONS-2026-10-23.md): free page locals search for, sending vendors to Chicago New Business Licenses and locals to a free weekly email. Todd's go: "Yes do it all - you have my confirmation" (Oct 23).

- Page: https://proofnotfluff.com/new-in-chicago/ (tools/newin_site.py, site/pages.json kind "newin"); data: permits/licenses-chicago/sample.json "week" (tools/licenses_chicago.py), rebuilt by .github/workflows/licenses-chicago.yml every Monday.
- Gates: newin_site and licenses selftests (planted Fail, food check not run, plain labels, Kit form); check_repo 0 errors; axe WCAG 2.1 AA 0 violations at 390 and 1280 px, light and dark; Legal desk CLEARED WITH FIXES, all applied (legal/reviews/new-in-chicago-2026-10-23.md); design director: round 1 FAIL 3.86, round 2 FAIL 4.29, round 3 FAIL 4.43, round 4 FAIL 4.57, round 5 FAIL 4.57, round 6 PASS 4.71 (each a fresh reviewer from fresh renders; every change list applied), then its last nits applied.
- Linked from: the sitemap (IndexNow on push), /go/, and the Chicago New Business Licenses free sample section.
- Left for Todd: make the Kit form "New in Chicago" (inline, double opt-in, from hello@, confirmation subject "Confirm your New in Chicago email", after confirming open https://proofnotfluff.com/new-in-chicago/) and send its number; a session puts it in site/pages.json "kitForm". Each weekly email send needs Todd's word.
