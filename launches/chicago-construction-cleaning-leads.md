# Launch record: Chicago Construction Cleaning Leads ($29 a month)

Checklist: design/LAUNCH_CHECKLIST.md. Launch means the Monday outreach emails and any promotion. The Gumroad page went live Oct 17 before this checklist existed (no traffic and no emails yet); it stays unpromoted until every box below is ticked.

Status as of Oct 17, 2026, 4:10 pm Chicago.

## 1. The product
- [x] Built to standard: workbook rebuilt to WORKBOOK_STANDARD v3 (commit fa2a832); free and members' pages rebuilt to the director's list.
- [x] Self-checks: check_repo 0 errors; permits_chicago --selftest (41 planted cases), leads_xlsx --selftest, leads_page --selftest; render_xlsx ERROR VALUES: 0 on screen and print (design/v3 renders).
- [ ] Holdout PASS on this week's live list (round 4 running; round 3 PASSED with fixes, all applied).
- [ ] Design director PASS on workbook, free page, members' page, cover and thumbnail (re-judge running; round 1 FAILED all three).
- [ ] Legal desk: City of Chicago disclaimer word for word on Terms, Start Here, the free page and the members' page; one Legal desk pass on the rebuilt surfaces.

## 2. The storefront (Gumroad, Todd's account)
- [x] Name, price ($29 a month), description: checked live Oct 17, 3:16 pm.
- [ ] Cover (1280 x 720) and thumbnail (600 x 600): files sent to Todd 4:08 pm; director re-judge running; Todd uploads (quest a1-gumroad-cover).
- [ ] Seller name shows ProofNotFluff, not a person's name (currently shows "Rob").
- [ ] Post-purchase content: members' page link and password, checked against the live members' page.

## 3. Buy and delivery path
- [x] Site checkout links open https://proofnotfluff.gumroad.com/l/vpnaoq with utm tags (make_site build, Oct 17).
- [x] Members' page opens with the password and the download produces the workbook (Playwright, Oct 17, design/v3 renders).
- [x] Google Sheets: every formula and number format the workbook uses (COUNTIF across the numbered tab, SUM, MAX, ROUND, REPT, IFERROR, the $M and billion formats) converted and matched expected values in Sheets (Drive file 1miNdC8aFRtokywMQx2vPIIhKi4Z1sZDHEpeeaL1y68I, Oct 17, 4:06 pm).
- [ ] One end-to-end look at the Gumroad receipt content as a buyer sees it (Todd's view or a $0 test the store allows).

## 4. Outreach
- [ ] Email values filled from this week's live list and checked by the holdout.
- [ ] Todd has seen the finished product and storefront and said go in chat.
