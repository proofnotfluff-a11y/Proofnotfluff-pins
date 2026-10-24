# Legal desk: pest seat role inboxes (Oct 24, 2026)

Question: Todd, live chat, Oct 24, about 4:20 pm: "Allow info@ inboxes (Recommended)", put to him as: for the Chicago pest seat cold email only, a role inbox the pest control company publishes on its own site counts without a named owner, greeting "Hi there,", Legal desk checks it first.

legal.status: cleared with fixes. An AI risk review, not legal advice. Every pest batch still needs Todd's "send" (P1 is not a standing-rule template).

Findings (sources read Oct 24, 2026):
- CAN-SPAM has no business-to-business exception; a role inbox is treated like any address. Our footer (postal address, "This is a sales email.", opt-out), true header and subject already meet it. FTC CAN-SPAM compliance guide: https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business
- The harvested-address aggravation (15 U.S.C. 7704(b)(1)) only adds to a message that already breaks 7704(a), and needs an address gathered by automated means from a site with a no-transfer notice, or a guessed or generated address. Fixes 1 and 2 keep both conditions from arising. https://www.law.cornell.edu/uscode/text/15/7704
- Illinois 815 ILCS 511/10 requires "ADV:" in the subject, but CAN-SPAM preempts it (15 U.S.C. 7707(b)(1)) except its bans on false headers and misleading subjects, which we meet. https://www.law.cornell.edu/uscode/text/15/7707 and https://ilga.gov/legislation/ilcs/documents/081505110K10.htm

Fixes, all applied Oct 24:
1. tools/pnf_rules.py pest_role_inbox(): exact local part info, office, contact, hello, mail, team, admin, general, inquiry or sales; product chicago-restaurant and CRM trade pest control; email_source site; the address on the business's own website domain; the page it was read from stored as emailSourceUrl on that domain. A pattern or guessed address never qualifies.
2. Site notice: an address is used only when CRM siteNotice is "none": the page's robots.txt allows it and the site has no no-solicitation, no-unsolicited-email, do-not-collect or no-share notice. A site with one gets doNotEmail with reason "site notice" and is listed for Todd.
3. Gates: validate_prospect waives first name, last name and title only under fix 1; the pest copy gate requires "Hi there," when no name is stored and "Hi {first}," otherwise (pest_fill fills "there"). Planted cases in tools/test_gates.py pest_role_cases.
4. One first email per business, ever: tools/crm_prospects.py --crm-trade skips a business when any CRM record on the same website domain (any product, inbox or batch) has firstSentAt or doNotEmail.
5. Free test day reply (legal/reviews/2026-10-24-pest-seat.md, "Free test day"): for a role inbox the header opens "Hi there," and condition 1 reads "a yes reply from the company's inbox".
6. Rule text updated: CLAUDE.md invariant 4 and email/P1-PEST-SEAT.md name the pest seat exception.
