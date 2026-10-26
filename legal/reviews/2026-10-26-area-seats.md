# Legal desk: Chicago Construction Cleaning Leads, area seats (Oct 26, 2026)

A risk-control checklist written by an AI under legal/README.md, not legal advice; nothing here is "approved". Reviewer: a fresh subagent (fable) that never saw the build. Tier: Medium. Publishing the seats is a major change under CONSTITUTION 2 (new product, price, checkout and a change to a live product's scope): this review does not replace Todd's go.

Verdict: **CLEARED WITH FIXES.**

## Fixes and where each stands (build session, Oct 26)
1. LLC in the seat Terms version line: applied (tools/leads_xlsx.py terms_text for seats).
2. Seat Terms help and cancel paragraph: hello@proofnotfluff.com, no minimum term, the seat stays yours to the end of the paid month, then the area is offered again: applied (tools/area_seats.py seatHelp). The app footer's help line on seat pages points to hello@ too.
3. "Your seat" paragraph says which copies exist outside the seat (shared-list members before you joined, free samples) and that they cannot be recalled; adds the free Monday email: applied (seatClause).
4. Volume sentence in the seat Terms (months vary, the area's average, low and high, some months under 10): applied (seatVolume, from permits/chicago/area_counts.json).
5. Cold emails: "we will sell that area's list to one cleaning company only" (T1 to T3) and "the only cleaning company we sell that area's list to" (T4, T5): applied (email/S1-AREA-SEAT.md).
6. Gumroad summaries: "Open apartment and commercial projects of $500,000 or more in <area>, Chicago, with a business as general contractor and the builder on each": applied (launch record).
7. Gumroad description: what is left out, and the volume sentence: applied (launch record).
8. Map alt text counts match the cards: applied (tools/area_site.py).
9. Footnote "passed the list's rules when issued, whatever their status today": applied.
10. Description cancel line with end-of-month timing: applied.
11. The $29 product:
   1. Gumroad line ("Areas held by an area seat holder are left out of this list from the Monday after the seat begins; the product page shows which areas are held, and you can cancel any time."): Todd's paste, before the seat offer goes on the page.
   2. $29 members' Terms "Held areas" paragraph: built (tools/leads_xlsx.py HELD_AREAS); it appears on the $29 app and workbook automatically once any seat has its checkout in site/pages.json.
   3. $29 page copy and counts once any seat is held: built (hero and FAQ say "in the areas no seat holder has taken", a "Which areas are held?" FAQ, and the free sample's counts recomputed on the shared list by tools/area_seats.py --shared-sample).
   4. Email notice to current $29 members at least 5 days before the first Monday an area leaves: Todd sends it (a relationship message, postal footer kept). Today there are 0 members.
   5. The one-month refund for a $29 member whose area is taken is a deviation from "no refunds on lead lists" and touches /refunds/: Todd's call as part of his go. If he declines, the last sentence of HELD_AREAS comes out and item 1 stays as worded.
12. Sales limit 1 on each seat product (Todd sets it if Gumroad offers it for memberships); otherwise the seat is marked held in site/area_seats.json the moment it sells and a second buyer is refunded the same day and never gets the password. A seat that ends is resold only after the paid month and a password rotation. "Areas open" counts a cancelled member inside the paid month as holding the seat.
13. The 5-newest sample only for an area no seat holds: applied on the offer section; the reply handler checks the area is not held before Todd sends.

Checks for Todd (not wording): the pitch kit is in each seat's app (confirmed: the Pitch kit tab is in the seat app); each "Take this area" button opens its own Gumroad membership product (monthly, no fixed length, free trial off, sales limit 1); one Seat Terms link with the line "(the same for every area apart from the area named)" (applied); each seat's Terms page opens without the password before its checkout link goes on the page; the description paragraphs survive Gumroad's editor.

## The free 5-newest sample (conditions, verbatim from the review)
1. Only for an area no seat holds on the send day.
2. Only after a yes from the named decision maker or a request to hello@ from a business address; once per company per area; never to an opted-out or bounced company, a seat holder or a current member; CRM sampleSentAt; no names in logs or the scoreboard.
3. Sent by Todd from hello@proofnotfluff.com as a plain-text reply in the thread, no attachment, no tracking, links only to the City's permit record and the proofnotfluff.com Terms page.
4. Content: that area's 5 newest qualifying permits from this Monday's list: City permit number, issue date, work type, reported cost, street address and community area, City stage, builder name as the City lists it, the builder's office phone or general email only where tools/builder_contacts.py has it verified on the builder's own site with the date read (never a person; do-not-list builders blank), the City record link. Never inspector notes, owner names, coordinates or a person's contact.
5. Header:
```text
Hi <first name>,

Here are the 5 newest projects on our <area name> list, free as promised: open apartment and commercial permits of $500,000 or more with a business as general contractor, from the list of <Mon D, YYYY> (City records as of that date).

This copy is for <company name>'s own sales calls only. Please don't forward, post or share it, or load it into another list or tool. Each line repeats the City's public permit record on that date; reported cost is the figure filed with the City, not a contract value. No builder listed has endorsed or works with ProofNotFluff, and a listing is not an invitation to bid. You make your own calls and emails and follow the law when you do.
```
6. Footer:
```text
Builder office phones and general email addresses are read on each builder's own website on the date shown; they are not City data and builders change them.

City of Chicago data notice: This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk.
ProofNotFluff is not affiliated with or endorsed by the City of Chicago.

If you want this area every Monday: an area seat is $149 a month, one cleaning company per area, no lock-in, and we sell that area's list to the seat holder only. Reply "seat" and I'll send the checkout link. Full Terms: https://proofnotfluff.com/chicago-cleaning-area-members/<slug>/#/terms

ProofNotFluff
680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611
This email ends with a sales offer. Not interested? Reply "no thanks" and we will not email you again.
```

## Passed lines (summary)
Scope, disclaimers and Terms, the City disclaimer word for word (the City's text has a curly apostrophe in "one's"; ours is straight, typographic only), outcome claims hedged, "exclusive" described truthfully on the page and in the Terms, numbers on the cards, IP, privacy (business office contacts only), price inside the band, renewal and cancel lines by the button, CAN-SPAM points on the cold emails (the sender appends the postal address, the sales label and the opt-out), the email gate, and the standing send rule (the templates are not approved, so nothing sends without Todd's word).

## For the owner's attorney
1. The City's indemnity and duty to defend, whether it passes to members, and whether a disclaimer inside a sample email meets "at the site".
2. Selling exclusivity over a public record: whether the disclosures keep "exclusive" from being read as more under Illinois consumer fraud law and the FTC Act, for business buyers.
3. Shrinking a live $29 subscription mid-term by notice: Illinois Automatic Contract Renewal Act (815 ILCS 601), ROSCA and California AB 2863, and whether the notice and refund route are enough.
4. Enforceability of the seat licence when Gumroad's checkout links the Terms rather than showing them, and of the sample email's "don't forward" line with no acceptance.
5. Republishing builder office contacts read from builders' own websites: website terms or scraping exposure, and any data broker registration duty.
6. Whether to state that the price can change on notice.

Sources the reviewer could not open today: www.chicago.gov data_disclaimer.html (site error; the Oct 26 snapshot in permits/chicago/source-terms.txt was checked), gumroad.com help article 192 (permission not answered) and article 82 (table of contents only).
