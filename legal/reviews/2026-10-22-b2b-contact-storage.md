# Legal desk log: B2B decision-maker contact storage (Oct 22, 2026)

**Decision:** approved by Todd Millen, owner, in a live chat on Oct 22, 2026. His words:
"Effective immediately, the 'no person's name' rule is amended for ProofNotFluff B2B prospecting. You are authorized to store business decision-maker full names, job titles, and corporate work email addresses in the PNF pipeline and CRM."

## Scope
- Who: the owner, founder, president, partner, director or general manager of a local commercial cleaning, pressure washing, window cleaning, dumpster (roll-off) rental, construction site security or pest control business in the Chicago or Austin market that ProofNotFluff emails about its own product (widened Oct 22, 2026 for step 2, legal/reviews/2026-10-22-step2-buyer-types.md item 9; pest control added Oct 24, 2026, legal/reviews/2026-10-24-pest-seat.md fix 15).
- What: first name, last name, job title and the corporate work email on the business's own domain. Never a personal or free-mail address, a phone number, a home address or anything else about the person.
- Sources: Hunter or Apollo through their APIs (GitHub Actions secrets), or CSV exports Todd provides.
- Also: the City's owner record and the business's own website. Official lists (Chicago CDOT licensed dumpster providers, Austin licensed haulers, IDFPR, Texas DPS TOPS) identify the business only; no person, phone or license number from them is stored.

## Where the data may be
- The private CRM artifact.
- data/ on a run's own disk (gitignored).
- prospects/enriched.sealed.json, sealed with PNF_DATA_KEY (tools/data_box.py).

## Where it may never be
- This public repo in the clear.
- The scoreboard, the ledger, logs or messages.

## Controls in code
- tools/pnf_rules.py Inbox Gate: named work address on the business's domain, decision-maker title, no role inbox, no free mail.
- check_repo `schema`: no prospect file tracked in the clear; the box must be sealed.

## Email law
CAN-SPAM rules stand for every email:
- an honest subject,
- the ProofNotFluff postal footer,
- opt-out by reply, honored for good (doNotEmail),
- no purchased lists of personal addresses.

## Open items for Todd's attorney
1. Each data vendor's terms (Hunter, Apollo) on reuse for cold email.
2. Whether any prospect is outside the US. The current product scope is Chicago and Austin only, so the GDPR and CASL rules for B2B email would not apply unless that changes.
