# Legacy memory (archived Oct 22, 2026)

The three monolithic ledger files (digital-products, digital-products-plan, digital-products-rules; about 101 KB
together) that every scheduled run used to load were moved out of the active memory path on Oct 22, 2026, in the
restructure "one model, one folder".

They were moved verbatim on Oct 22, 2026 (Todd's go in a live chat) to Todd's private memory store under `/archive/legacy-memory/`, not to this public repo:
they carry Drive folder ids, account details and Etsy operating history that do not belong in a public repository.
No scheduled run reads them. The leads rules they held now live in CLAUDE.md (invariants), coo/HANDOFF.md (state) and
the stage contracts in .claude/skills/. The Etsy shop rules stay readable in the archive for the day Etsy work resumes.

tools/context_gate.py fails the code gate if any of those files reappears in an active path.
