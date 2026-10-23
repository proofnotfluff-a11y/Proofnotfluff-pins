# Legal desk review: New in Chicago (free public page), Oct 23, 2026

Risk-control checklist review by an AI, not legal advice. Reviewer: fresh Legal desk subagent; it read legal/README.md, CONSTITUTION 2 and 4, the Oct 22 licenses review, the City terms snapshot and the 40 rows of permits/licenses-chicago/sample.json "week".

Verdict: CLEARED WITH FIXES. All fixes applied before the page went live (commit on Oct 23):
1. "Every new business" removed from the description, card and OG image ("New business licenses the City issued this week").
2. Lede and headings say new licenses, not new businesses opening; the method names first licenses, new sites, added licenses and relicensed sites.
3. The 30-day count is labeled as the full business list, not a citywide total (later moved off the stat line; the vendor banner carries it).
4. Footer names both sources: Business Licenses and Food Inspections, linked.
5. Removal route: anyone whose business, home or name appears can email hello@; taken off before the next weekly page and kept off the email and the business list (permits/licenses-chicago/do_not_list.json).
6. "A business can be missing for many reasons, and being listed or missing says nothing about its inspections, quality or standing." on the page and in the footer.
7. Wording matches the data rules (one person's own work; a person's full name; an address our checks show as a business site).
8. "Children's classes and care" replaces "Day care".
9. Kept, no rule fits, Todd may add to the do-not-list: Operaxions (420 W Grand Ave 1b), Cmplex Studios (3301 W 47th Pl A), Cti (4616 W Augusta Blvd). The members' preview on this page never shows a row with a unit number.
10. Email box marked "Starting soon", a mailto until a Kit form exists, privacy line and the Privacy page now names the New in Chicago email.
11. When the Kit form is added: privacy line naming Kit under the form; every email with a true From and subject, the postal address, one-click unsubscribe, stops honored within 10 business days, the City disclaimer, non-affiliation line and the same exclusions.
12. Weekly refresh guard: the data layer leaves out food rows with a Fail on file, and the page drops every food row if the food inspection check did not run, so a refresh cannot name a business with a failed record. The Kit form swap and each email send still need Todd's word.
13. Cadence: "Updated every week" with the pull date shown (the Monday cron rebuilds the page; manual pulls can land other days).
Open for the attorney: the City's indemnity clause (Oct 22 review, item 1) covers this page too.
