# Legal desk: construction role inboxes (Oct 29, 2026)

Question: Todd, live chat, Oct 29, 1:01 pm: "go with your rec" on "Should construction trades count an info@ inbox with no named owner, like pest?" (recommendation: yes). For chicago-construction cold email, a role inbox the business publishes on its own site counts without a named owner; the email opens "Hi there,".

legal.status: cleared on the Oct 24 pest findings. An AI risk review, not legal advice.

Findings: the Oct 24 review (legal/reviews/2026-10-24-pest-role-inbox.md) does not depend on the trade. CAN-SPAM has no business-to-business exception and treats a role inbox like any address; our footer, true header and subject meet 15 U.S.C. 7704(a). The harvested-address aggravation (7704(b)(1)) cannot arise while the address is read by hand from the business's own site with no no-transfer notice and is never guessed. Illinois 815 ILCS 511/10 "ADV:" is preempted (7707(b)(1)).

Fixes, applied Oct 29 (same as the pest seat's 1 to 4):
1. tools/pnf_rules.py construction_role_inbox(): exact local part info, office, contact, hello, mail, team, admin, general, inquiry or sales; product chicago-construction; email_source site; address on the business's own website domain; emailSourceUrl on that domain. A pattern or guessed address never qualifies.
2. Site notice: only when CRM siteNotice is "none" (robots.txt allows the page; no no-solicitation, no-unsolicited-email, do-not-collect or no-share notice).
3. Gates: validate_prospect waives name and title only under fix 1; validate_drafts requires "Hi there," for such a prospect (greeting_name). Planted cases in tools/test_gates.py construction_role_cases.
4. One first email per business, ever: tools/crm_prospects.py skips a construction role inbox when any CRM record on the same domain has firstSentAt or doNotEmail.
5. First batch of role-inbox emails goes to Todd for his yes before it sends, so he sees the "Hi there," version first.
