# Legal desk review: step 2 buyer types (Oct 22, 2026)

**Scope:** the window_cleaning, dumpster_rental and security verticals (tools/pnf_rules.py TRADE_VERTICALS), their cold email templates T5 to T9 (.claude/skills/outreach-drafter/templates.md), where their prospects come from (.claude/skills/prospect-matching/sources.md), the Monday email changes (email/M1-MONDAY.md: the per-trade "ask who buys" line, the first-issue reply line, the shorter intro) and a proposed one-line change to the Chicago and Austin lead page lede. Todd's go: Oct 22, 2026, 10:55 pm, live chat, "Let's go with your recommendations".

**Verdict: CLEARED WITH FIXES, all fixes done in this chat.** Nothing is sent, published or switched on; outreach stays paused until Todd says otherwise. This is a risk checklist written by an AI, not legal advice.

1. PASS. CAN-SPAM basics: plain text, accurate sender, no links, the sender adds the postal footer and the reply opt-out, doNotEmail stops repeats.
2. PASS after fix. Subject lines: round 1 subjects named a service ("Window cleaning on", "Roll-offs on", "Site security on") and read like a quote request to the trade checkers. Now "The job on {street}", which matches a body about that job.
3. FIX, done. Timing on Inspections Under Way: that stage covers most of construction, so no template now says a job is near the end. Window: "likely a long way off". Dumpster: "usually keep filling cans right up to the final cleanout". Security: conditional ("Once a building is closed in").
4. FIX, done. Partial occupancy (T9): the City status can mean a whole building on a temporary certificate. Now: "The City now allows people in while work wraps up, which often changes what site security covers."
5. FIX, done. Window cleaning only on new builds of $5M or more, and never a scope that names a build-out, fit-out, finish-out or interior work (pnf_rules.TRADE_VERTICALS exclude_scope; planted tests).
6. FIX, done. {kind} for these three trades comes from code (pnf_rules.kind_display: townhouse, apartment, school, hotel, office, else building) and the draft gate fails a draft whose kind word differs. Templates say "{kind} project".
7. PASS. "Final glass clean" on a new build is a fair general statement, hedged.
8. CHECK. Official lists (Chicago CDOT licensed dumpster providers, Austin licensed haulers, IDFPR, Texas DPS TOPS) are used one business at a time to identify and confirm the business, with no bulk pulls; no person's name, phone or license number from them is stored (sources.md). Read each site's terms once on first use.
9. FIX, done. Storage scope widened in legal/reviews/2026-10-22-b2b-contact-storage.md to the three new trades and its sources line completed. Todd's quoted words cover B2B prospecting in general, so CONSTITUTION 4 stands as written.
10. CHECK, Todd decides. The lead page lede change is accurate (every buyer gets the builder, address, stage and permit of each big open project) but the list leaves out demolition, foundation and site-work-only permits, so the line claims no more than that. Naming new buyer types on a lead page is not clearly minor, so it goes to Todd first (CONSTITUTION 2).
11. PASS. Monday email: "ask who buys {buys}" reads naturally per trade, the intro matches the Builder and Stage lines, and the first-issue reply line is a request, not a claim.

## Attorney items
1. Whether the cold email counts as commercial under 15 U.S.C. 7704(a)(5) and needs a plain solicitation label, or whether the open permission ask is enough.
2. Whether the IDFPR and Texas DPS TOPS terms allow commercial use of lookup results to find prospects.
3. Hunter and Apollo reuse terms (open since Oct 22), now covering three more trades.

## Checker rounds (independent agents, as a busy owner of each trade)
- Round 1: window 3 and 4 of 10, dumpster 4 and 3, security 4 and 5. Fixed: subjects, stage phrasing, interior build-outs out of window cleaning, dumpster limited to jobs under $5M, security to new builds of $20M or more, kind words from the City scope, "(Chicago)" removed from builder names, B's first sentence.
- Round 2: window 6 and 7, dumpster 5 and 5, security 7 and 8 (PASS once fixed). Fixed: $5M floor for window cleaning, "Space turns over", window and dumpster timing lines, B sentence for haulers, townhouse and multifamily kind words, builder names ("The", a trailing city, a glued "Edwardsconstruction").
- Open for Todd: the Austin record aus-13107658 shows $830M for a 24-building multifamily job and aus-13532840 $380M for a school phase; both are the City's own figures, but they look high and are worth a check against the City record before either is named in an email.
