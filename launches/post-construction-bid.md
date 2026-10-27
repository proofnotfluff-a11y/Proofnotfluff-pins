# Launch record: free post-construction cleaning bid calculator and the seat "Price this job" panel (Oct 27, 2026)

Decided: Todd, live chat, Oct 27, 2026, 9:08 am: "Let's go with your recommendation." (coo/DECISIONS-2026-10-27.md; research_notes/kimi-2026-10-27-r9.md). A separate paid bid writer was ruled out (CleanGuru $79, GetCleanBid free, BidLoom $19); nobody starts a cleaning bid from a building permit, which the seats hold.

## What is built
- Calculator: docs/post-construction-cleaning-bid-calculator/ (draft, noindex, unlinked), math in docs/assets/pnf-calc.js (PNF.bidPrice, PNF.bidPrint), styles docs/assets/pnf-bid.css; proposal template download docs/downloads/post-construction-cleaning-proposal-template.docx and .pdf (engines/post-construction-proposal/build.py) behind a Kit form (KITFORM_TBD), thanks page at /post-construction-cleaning-bid-calculator/thanks/. Guide ranges shown as dated ranges from three named sources, never as a market rate.
- Seat panel: tools/leads_app.py, in seat apps only; prices from the holder's own rates and the size they type; proposal pre-filled with builder, address and work (editable), no City stage on the proposal. Seat Terms Version 3, Oct 27, 2026 (tools/area_seats.py). Reaches seat apps on the next Monday rebuild.

## Gates
- Holdout (fresh): BLOCKERS 1 (rate and job saves shared one timer), fixed with planted tests; 13 hand-worked cases match page and print; live $29 and Austin apps unchanged.
- Legal desk (fresh): CLEARED WITH FIXES, High tier (a form the builder signs); fixes 1 to 8 applied (sample-form line, no City stage on the proposal, editable builder and address, no seat name or members' URL in the print, Terms line, PDF and Word match).
- Design director: round 1 FAIL 4.57 (calculator) and 4.29 (seat); round 2 (fresh) FAIL 4.57 and 4.14. Two FAILs: the live session decided (Oct 27) to apply round 2's list and check it itself rather than loop; applied, each item confirmed in a render (numbers never wrap, plausibility notes, greyed results on a bad field, Ctrl+P prints the proposal only, seat breakdown under the total, neutral first prompt).
- Session's own check after round 2: calculator tests 664 pass; live calculators give the same results as before the shared parser change (house cleaning $220, price increase $162, snow $80, cleaning per sq ft $0.113, missed calls $488); check_repo 0.
- Shared changes that reach other pages: the parser now reads trailing units ("30/hr", "12,000 sq ft"); the site-wide footer line "Calculators run in your browser; nothing you type in them is sent anywhere."; one wording change in the shared leads app ("See this builder's project").

## Go live
1. Todd makes the Kit form: name "Post-construction cleaning proposal template", subject "Confirm to get your proposal template", button "Get the template", both redirects to https://proofnotfluff.com/post-construction-cleaning-bid-calculator/thanks/.
2. The session puts the number in place of KITFORM_TBD, removes the draft flag, rebuilds, one test sign-up, one line in seo/RESULTS.md. The lead page link and related-calculator cards appear then.
