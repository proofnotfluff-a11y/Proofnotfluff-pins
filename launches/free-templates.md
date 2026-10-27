# Launch record: free price increase letter and job estimate templates (Oct 26, 2026)

Decided: Todd, live chat, Oct 26, 2026, 8:28 pm: "let's get it live and the other items you suggest. Building traffic is paramount." (coo/DECISIONS-2026-10-26.md). Free downloads given for an email address, to bring owners to the site and build a list we can write to without cold email. The invoice template was left out (flat search interest, a crowded field).

Drafts until each page has its Kit form: noindex, off the sitemap, the index and the calculator cards (site/extras.json entries carry no kitForm yet). The download files sit at docs/downloads/ and nothing links to them.

## What is built
- Price increase letter: engines/price-increase-letter/build.py writes docs/downloads/price-increase-letter-template.docx and .pdf (5 pages: how to send it, 3 letters, Terms) and the letter preview on docs/free-price-increase-letter-template/.
- Job estimate: engines/job-estimate-template/build.py writes docs/downloads/job-estimate-template.xlsx (Start Here, Estimate, Terms; totals by formula, protected, prints on one page) and .pdf (blank estimate, how to use, Terms) and the worked example on docs/free-job-estimate-template/. The example's three prices are the pressure washing calculator's own example quotes.

## Gates
- Builder checks (Oct 26, after each round): legal_scan 0 findings on the 4 files, the site-wide Terms flag on the 2 page folders (same as the live cheat sheet page); LibreOffice recalc 26 formulas, 0 errors; worked example 760.00 less 76.00 plus 34.20 = 718.20, deposit 179.55, balance 538.65; blank and capped extreme copies 0 errors, no "###"; axe 0 violations on 8 renders, no sideways scroll; 0 dashes; check_repo 0.
- Legal desk (fresh reviewer): CLEARED WITH FIXES. Letter Medium tier, estimate High tier (a form a customer signs). Fixes 1 to 4 applied (deposit and cancelling caution, acceptance line, FAQ wording that names no law); fix 5 is the go-live condition below.
- Design director: round 1 FAIL 4.57 and 4.57 (closing band, phone button padding, docx highlights, estimate row fill and terms wrap), fixes applied; round 2 (fresh reviewer) FAIL 4.57 and 4.57 (punctuation gap after fields, open icons, text widths, outline hero button, input caps, card spacing, sentence case), fixes applied and each confirmed in a fresh render. Two FAILs: under DESIGN_DIRECTOR.md this goes to the live session, not a third loop. Not judged again after round 2 fixes. Left alone (site-wide, not this page): the 28 px logo tap height and an on-this-page bar.

## Go live (per page)
1. Todd makes the Kit form (below) and sends its number.
2. The session puts the number in place of KITFORM_TBD, removes the robots meta line, adds kitForm to the extras.json entry, runs tools/make_site.py, sends one test signup, checks the redirect opens the file, logs one line in seo/RESULTS.md.

### Kit forms (Todd, about 5 minutes each)
Grow, Landing Pages & Forms, Create new, Form, Inline, any template. Settings, Incentive: "Send incentive email" ON (double opt-in). Sender ProofNotFluff, footer address the LLC mailbox. Settings, General, "After subscribing": Redirect to the same thanks page as below, so the files open at once as the page promises. Copy the number from the form's address bar.
- Name: Price increase letter template. Subject: Confirm to get your price increase letter template. Button: Get the template. After confirming, redirect to https://proofnotfluff.com/free-price-increase-letter-template/thanks/ (both files)
- Name: Job estimate template. Subject: Confirm to get your job estimate template. Button: Get the template. After confirming, redirect to https://proofnotfluff.com/free-job-estimate-template/thanks/ (both files)
