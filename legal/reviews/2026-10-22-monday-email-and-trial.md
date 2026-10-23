# Legal desk review: free Monday email capture and the 1-week Gumroad trial (Oct 22, 2026)

**Scope:** funnel step 1 as built Oct 22 (email/M1-MONDAY.md, tools/monday_email.py, the cold email ask in .claude/skills/outreach-drafter/templates.md, the lead page changes behind the `trialDays` and `mondayForm` keys in tools/make_site.py). Todd's go on the funnel: Oct 22, 2026, 7:57 pm, live chat.

**Verdict: CLEARED WITH FIXES.** Nothing below goes live until fixes 1 to 4 are done. This is a risk checklist written by an AI, not legal advice; the attorney items at the end are for Todd's attorney.

## Email capture
1. PASS. Consent. A cold email recipient joins only by replying yes to a question that names the free Monday email; the reply stays in the inbox as the record and the CRM keeps the date. A site visitor joins only through Kit's double opt-in. Nobody is added from a bought, scraped or old list.
2. PASS. The old waitlist forms (10059700, 10083860) asked for news about new cities and features. Their subscribers are not moved to the Monday email; the Monday email gets its own forms.
3. PASS. CAN-SPAM (15 U.S.C. 7704) on every Monday and trial email: an honest subject, ProofNotFluff named as sender, our postal address (680 North Lake Shore Drive, Suite 110-2964, Chicago, IL 60611, a private mailbox, which the FTC accepts when registered under Postal Service rules), and a working reply opt-out honored before the next send, well inside the 10 business days the law allows. The tool fails any email missing the address or the stop line.
4. PASS. Advertisement label. The trial email is commercial. People asked for our email, so the label is not strictly needed, but the email says plainly "This one is an offer" anyway.
5. FIX 1 (Todd, Kit). Kit's mailing address in Settings, Email is blank, so Kit prints its own Seattle address in every footer. Set it to the address above before the first Kit broadcast.
6. FIX 2 (before the Monday form goes live). The site has no privacy page, and the Monday form collects email addresses (so do today's waitlist forms). Add a short /privacy/ page in the go-live step, shown to Todd as a major change: what we collect (email address, and first name and work email for cold email prospects), why (the email they asked for), who holds it (Kit; our CRM), that it is never sold, how to stop (reply stop or Kit's link), and a contact (hello@proofnotfluff.com). California's online privacy law expects one on any commercial site that collects email addresses from California residents.
7. PASS. Builder office lines in the free email come only from tools/builder_contacts.py entries verified on the builder's own website, never a person, and the do-not-list blocks a builder for good. They are added at send time and never printed in a check or committed.
8. PASS. Accuracy. Every lead fact is rendered by code from the City record in permits/downstream/gc_leads.json; the gate fails a value, street or builder that does not match. A food inspection at the same address is not printed, since at a big building it can belong to another tenant.

## The 1-week free trial
9. PASS. Disclosure before billing details (ROSCA, 15 U.S.C. 8403). Next to the main button the page states that the card goes in at checkout, nothing is charged for 7 days, then $29 a month until cancelled, and how to cancel; the hero line repeats the short version, and Gumroad's checkout shows the trial terms before payment and takes the consent. The trial email says the same.
10. PASS. State automatic renewal laws (for example California, Bus. and Prof. Code 17600 and following, updated July 1, 2022): terms shown before purchase, consent at checkout, Gumroad's receipt as the acknowledgment, cancellation online in the Gumroad library. California's extra reminder applies only to free trials longer than 31 days, so not to a 7-day trial.
11. PASS. The FTC's "click to cancel" rule was vacated by the Eighth Circuit in July 2025; ROSCA and the state laws above still apply and are what this review checks.
12. FIX 3 (Todd, Gumroad). Turn on the 1-week trial on each product, and add one line to each product description: "7-day free trial: your card is entered at checkout and charged $29 when the 7 days end, then monthly until you cancel. Cancel in your Gumroad library before then and you pay nothing."
13. FIX 4 (Todd, his own card, $0). Start one trial on the Chicago product, check that the receipt states the trial and the charge date, cancel in the Gumroad library, and confirm no charge is scheduled. The site and the trial email promise that cancelling inside 7 days costs nothing; this checks Gumroad does that before anyone else relies on it.
14. PASS. Nothing promises one trial per person or anything about a second trial.
15. PASS. The refund wording Todd approved Oct 22 is unchanged and does not conflict: the trial costs nothing, and the no-refund rule starts at the first charge.
16. Not in scope. Restaurant leads ($39) get no trial wording until its outreach goes live; that page stays as it is.

## Attorney items
1. Whether the reply-yes record in the inbox is enough consent evidence, or a dated confirmation email is worth adding.
2. Illinois and Texas automatic renewal rules for a 7-day trial sold to businesses, and whether B2B buyers change anything.
