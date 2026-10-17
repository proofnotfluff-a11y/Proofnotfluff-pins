# Launch record: Chicago Construction Cleaning Leads ($29 a month)

Checklist: design/LAUNCH_CHECKLIST.md. Launch means the Monday outreach emails and any promotion. The Gumroad page went live Oct 17 before this checklist existed (no traffic and no emails yet); it stays unpromoted until every box below is ticked.

Status as of Oct 17, 2026, 4:10 pm Chicago.

## 1. The product
- [x] Built to standard: workbook rebuilt to WORKBOOK_STANDARD v3 (commit fa2a832); free and members' pages rebuilt to the director's list.
- [x] Self-checks: check_repo 0 errors; permits_chicago --selftest (41 planted cases), leads_xlsx --selftest, leads_page --selftest; render_xlsx ERROR VALUES: 0 on screen and print (design/v3 renders).
- [x] Holdout PASS (round 5, Oct 17, 4:30 pm; verify5/holdout-report.md): 0 of 632 clear wasted calls, all counts agree, the two round 4 homes errors fixed, no person's name.
- [x] Design director: members' page 4.86, cover 4.4, thumbnail 4.6 PASS; free page 4.57 and workbook 4.29 failed twice on polish, so under the gate rules the live session decided: screenshot loading confirmed in a desktop browser (both images load, 1064 and 1200 px), workbook polish items fixed (step layout, card row heights, stat strips spread, Builders header and bars) and checked from fresh renders. Hyperlink color is set to 2F5F9E in the file; LibreOffice draws links in its own color.
- [x] Legal desk: CLEARED WITH FIXES (verify5/legal-review.md); repo fixes 1, 2, 3b, 5, 6, 7, 8 applied (commit a083c2c). Gumroad wording fixes 3a and 4 are Todd's (his account). Attorney note: the City's terms require users to indemnify the City.

## 2. The storefront (Gumroad, Todd's account)
- [x] Legal wording on Gumroad (Legal desk fixes 3a and 4): checked on the live product page Oct 17, 4:40 pm (non-affiliation, AI line, City disclaimer, 12-month and $500,000-or-more scope, renewal line, tier named Monthly). Cover reworded to "of $500,000 or more" to match; Todd swaps it.
- [x] Name, price ($29 a month), description: checked live Oct 17, 3:16 pm.
- [x] Cover (1280 x 720, no weekly numbers) and thumbnail (600 x 600) uploaded by Todd; both passed the design director.
- [x] Seller name shows ProofNotFluff (Todd, Oct 17, 4:16 pm screenshot).
- [x] Post-purchase content: members' page link https://proofnotfluff.com/chicago-leads-members/ and the password match the build (Todd's Content tab screenshot, Oct 17, 4:38 pm).

## 3. Buy and delivery path
- [x] Site checkout links open https://proofnotfluff.gumroad.com/l/vpnaoq with utm tags (make_site build, Oct 17).
- [x] Members' page opens with the password and the download produces the workbook (Playwright, Oct 17, design/v3 renders).
- [x] Google Sheets: every formula and number format the workbook uses (COUNTIF across the numbered tab, SUM, MAX, ROUND, REPT, IFERROR, the $M and billion formats) converted and matched expected values in Sheets (Drive file 1miNdC8aFRtokywMQx2vPIIhKi4Z1sZDHEpeeaL1y68I, Oct 17, 4:06 pm).
- [x] Buyer view checked: the Content tab is what Gumroad shows after purchase; the password opens the live members' page and the workbook downloads (Playwright, Oct 17).

## 4. Outreach
- [x] Email values filled from this week's live list (632 permits, 563 addresses, 9 near finish; holdout round 5) and each email's example permit taken from that list.
- [x] Todd said go in chat (Oct 17, 4:44 pm: "Go: make the drafts"). Drafts in the ProofNotFluff Gmail; Todd sends Monday after changing the Gmail sender name to ProofNotFluff.
