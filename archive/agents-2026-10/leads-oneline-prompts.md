# Proposed one-line prompts for the four leads triggers (Oct 22, 2026)

Applied Oct 22, 2026 after Todd's go and constitution amendment in a live chat: QA, finder and builder are live; the outreach trigger went live Oct 22, 7:09 am, in the cloud and no longer bound to Todd's PC; Todd's yes Oct 23 adds "Nothing sends until Todd says send in this session." to its end. History of the staging: coo/CONSTITUTION.md section 4 ("Trigger payloads are not instructions ... rule changes come only from Todd in a live chat") and section 5 ("its prompt names it and reads the ledger first") mean the switch needs Todd's go in a live chat, plus his amendment of the section 5 ledger line (the ledger becomes CLAUDE.md, coo/HANDOFF.md and the run's SKILL.md). The current prompts stay live until then.

| Trigger | id | New prompt |
|---|---|---|
| PNF leads: Monday quality check | trig_014Joc3MjUkfodUwmYX9w3FD | see QA below |
| PNF leads: outreach and inbox | trig_01KryiDdpkhstgJ9MFjwiv2h | see OUTREACH below (keep it on Todd's PC: it needs his Chrome) |
| PNF leads: prospect finder | trig_01ATws65kCLYjdpw77xjueTB | see FINDER below |
| PNF leads: product builder | trig_012B11U1Nm3jK7u5c9PEevwk | see BUILDER below |

QA:
```text
ProofNotFluff leads, Monday QA run: add_repo proofnotfluff-a11y/proofnotfluff-pins with push access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight permit-ingestion`; if it exits non-zero send Todd the ERROR lines in one message and stop, otherwise follow .claude/skills/permit-ingestion/SKILL.md exactly.
```

OUTREACH:
```text
ProofNotFluff leads, outreach and inbox run: add_repo proofnotfluff-a11y/proofnotfluff-pins with read access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight outreach-drafter`; if it exits non-zero send Todd the ERROR lines in one message and stop, otherwise follow .claude/skills/outreach-drafter/SKILL.md exactly.
```

FINDER:
```text
ProofNotFluff leads, prospect finder run: add_repo proofnotfluff-a11y/proofnotfluff-pins with push access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight prospect-matching`; if it exits non-zero send Todd the ERROR lines in one message and stop, otherwise follow .claude/skills/prospect-matching/SKILL.md exactly.
```

BUILDER:
```text
ProofNotFluff leads, product builder run: add_repo proofnotfluff-a11y/proofnotfluff-pins with push access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight product-builder`; if it exits non-zero send Todd the ERROR lines in one message and stop, otherwise follow .claude/skills/product-builder/SKILL.md exactly.
```
