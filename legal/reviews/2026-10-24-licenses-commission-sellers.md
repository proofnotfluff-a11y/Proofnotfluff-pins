# Legal desk review: license count emails to commission sellers (Oct 24, 2026)

**Scope:** email/L2-COMMISSION.md T21 to T26 and what a yes gets (as the file stood after its second revision on Oct 24, {m} in its own sentence), the launch record's public terms and Gumroad copy, .claude/skills/prospect-matching/sources.md (commission sellers section), the contact storage scope in legal/reviews/2026-10-22-b2b-contact-storage.md, the phone step changes in tools/phones.py, and permits/licenses-chicago/phones.json. Fresh reviewer, read only. This is a risk checklist written by an AI, not legal advice. Nothing here is "approved".

**Verdict: CLEARED WITH FIXES.** No batch goes until fixes 4 and 5 are done and the weekly file carries `licensePlaces` (item 3). All fixes applied in the same chat (see "Fixes applied").

## Cold emails T21 to T26
1. PASS. Header and subject. From "ProofNotFluff" at sales@getproofnotfluff.com. The first subject states the week's count and the body backs it up; it leaves out "at least", which only understates. "Re:" subjects sit in our own earlier thread.
2. PASS. Ad label, postal address and reply opt-out come from the footer (email/SEND_RULES.md, tools/pnf_rules.py FOOTER). The sales@ queue also sends a List-Unsubscribe mailto header and reads opt-outs in any wording (email/sender/Code.gs).
3. CHECK. `counts.licensePlaces` was not yet in permits/inspections-chicago/sample.json; copy_gate reads it with no fallback, so every count email fails until the weekly build writes it. That is the right default. Both files cover Oct 17 to Oct 24.
4. FIX, low. The {m} count leaves out schools, hospitals and mobile vendors, and license inspections with results such as No Entry or Out of Business. The true number is higher, so say "at least", as {n} does: "It logged at least {m} food businesses at their license inspection, which usually comes before a food license."
5. PASS. Each claim is true against the data: "at least {n}" (one row per business and site, licenses left out on purpose), {food} is segmentsWeek.food, "usually comes before a food license" is hedged and matches the launch record, T22's leave-out list and four markers and T25's "license type and business activity" match the product, "The City issued" claims no City count or endorsement. POS emails never say insurance and insurance emails never say POS. No business, street, price or phone.
6. PASS. City data terms: the emails carry derived counts, not an application; the City's required disclaimer is on the free sample page and in the Gumroad copy. Indemnity stays on the attorney list.
7. FIX, low. T23 and T26 promise "you won't hear from me again": after the second follow-up the prospect is closed for every product (CRM doNotEmail true, reason "promised no further email").

## What a yes gets
8. FIX, medium. The yes reply needs fixed text, with the trial's full disclosure and the footer, sent only on Todd's word and only after launch step 6 (Todd's $0 trial test). Text now in email/L2-COMMISSION.md. It matches the sample page and legal/reviews/2026-10-22-monday-email-and-trial.md item 12.
9. FIX, low, plus CHECK. The launch record's Gumroad copy had no trial line and step 4 said "no trial" while the status line says the trial is live. Trial line added to the price paragraph; step 4 now says "1-week free trial". CHECK (Todd): a text read of the live Gumroad page found no trial or renewal wording; the page draws its text with scripts, so this proves nothing either way. Check it by eye before the first yes reply.

## Prospect sources and storage
10. PASS. Prospects come from business websites, the Illinois Department of Insurance lookup used one business at a time with nothing stored; the contact is an owner or principal named on the business's own site, with the work address it publishes on its own domain. Producers and account managers are excluded.
11. FIX, low. Address harvesting (15 U.S.C. 7704(b)(1)): skip any site that says its email addresses may not be collected, sold or used for unsolicited email.
12. FIX. Storage scope widened to independent POS and merchant services resellers (agents or ISOs) and independent commercial insurance agencies serving Chicago businesses; the Illinois Department of Insurance producer lookup added to the official lists that identify the business only.

## Phone step (against legal/reviews/2026-10-23-phone-sources.md)
13. PASS, with a low FIX. The contact page sits inside condition 3 (home page and one contact page per business per 30 days): read only when the home page shows no number, same-site link only (other domains, mailto, tel and file links skipped; off-site redirects read nothing), robots.txt must allow it, 5 seconds after the home page, the same no-bots terms check, one logged read per site per 30 days across both lists. FIX: condition 6 says store the number's source URL, so a contact-page number cites the contact page as phoneRef.
14. FIX, medium. The street address check is unchanged and still required, which keeps this inside condition 5. But the run-together test accepted any prefix ("Marias" matched "Mariascos Mexican", "Thai Ruby" matched "Thai Rubyfruit Cafe"; both could be two businesses in one building). Rule: the shorter name run together must equal the longer name's first words run together, ending where one of its words ends, at 6 letters or more, with a word that is not a generic trade word or stop word. Both pairs planted as no-match cases.
15. PASS. phones.json holds counts only (rows 236, withPhone 54, coverage 22.9, source split, reason counts); no name, number or domain. At 22.9% coverage the emails are right not to mention phones.

## Attorney items
1. A route that finds a new business's own website by web search and reads a phone only when that page shows the City's street address and the business name: still "the business's own website" under the Oct 23 review, or a new source needing its own conditions (which domains count as own, a search engine's terms, lookalike or reseller sites)?
2. Do the Illinois Department of Insurance producer lookup's terms allow lookups to qualify sales prospects?
3. Illinois Insurance Code 215 ILCS 5/500-80 (not read today): confirm a flat $29 subscription not tied to any policy sold is not compensation to an unlicensed person, and that no Illinois rule on insurance lead sellers applies to commercial lines.
4. Carried over: the City data terms' indemnity and duty to defend, and the CAN-SPAM label question.

## Sources read (Oct 24, 2026)
legal/README.md; legal/reviews 2026-10-22-step2-buyer-types, 2026-10-24-cold-email-ad-label, 2026-10-22-b2b-contact-storage, 2026-10-23-phone-sources, 2026-10-22-monday-email-and-trial, 2026-10-24-pest-seat (claims lines); email/L2-COMMISSION.md; email/SEND_RULES.md; email/sender/Code.gs (opt-out and header lines); launches/chicago-new-business-licenses.md; permits/licenses-chicago sample.json, source-terms.txt, city-terms.json, phones.json; permits/inspections-chicago sample.json, profile.json, source-terms.txt; docs/chicago-new-business-licenses/index.html; site/pages.json; .claude/skills/prospect-matching/sources.md; .claude/skills/outreach-drafter/SKILL.md (reply rule); tools/phones.py (name_score, match, site_phone, contact_link, fill); tools/inspections_chicago.py and tools/copy_gate.py (licensePlaces lines); proofnotfluff.gumroad.com/l/chicago-new-business-licenses (text read). 15 U.S.C. 7704 and the FTC CAN-SPAM guide as read in the Oct 24 ad-label review.

## Fixes applied (build session, Oct 24, 2026)
- 3: the inspections workflow now writes counts.licensePlaces (36 on Oct 24, window Oct 17 to Oct 24); the gate passes on it.
- 4: T21 and T24 say "It logged at least {m} food businesses at their license inspection"; the gate requires that phrase ("Chicago" dropped from the first sentence to stay under 75 words).
- 7: L2 Follow-ups rule closes the prospect after the second follow-up.
- 8: the fixed yes reply is in L2 "What a yes gets".
- 9: trial line and "1-week free trial" in launches/chicago-new-business-licenses.md. Todd's eye check of the live Gumroad page stays open.
- 11: sources.md Contact line.
- 12: legal/reviews/2026-10-22-b2b-contact-storage.md Who and Also lines.
- 13: a contact-page number's phoneRef is the contact page URL (planted case).
- 14: whole-word run-together rule in tools/phones.py name_score (planted cases).

legal.status: cleared with the fixes above for the L2 count emails (sales@ only), the commission-seller prospect sources and contact storage, and the phone step changes.
