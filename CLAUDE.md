# ProofNotFluff router (Layer 0)

Read this, coo/HANDOFF.md, coo/CONSTITUTION.md (it binds first), then only the SKILL.md your run names.

## Topology
- .claude/skills/<job>/SKILL.md: stage contracts (Inputs, Process, Outputs). One stage, one job.
- tools/: deterministic code: fetching, paging, joins, dedup, schemas, copy checks. Never a model.
- permits/downstream/gc_leads.json: Entity A, GC leads in downstream stages (public, business fields only), written by the downstream-leads workflow.
- data/ (gitignored): Entity B prospects and per-run work files. Named people, never committed.
- CRM https://claude.ai/artifact/De189P4AXgWVC6o8LYbxdB and scoreboard https://claude.ai/artifact/N9eKZy7Pv39njSe4izVgbE (ArtifactData).
- coo/, email/, design/, legal/, launches/: read only when a SKILL lists it. archive/: never.

## Invariants
0. Date from bash: `TZ=America/Chicago date`, never guessed.
1. First: `python3 tools/check_repo.py --preflight <job>`. Exit 1 stops the run; report the ERROR lines to Todd. Never edit a gate to pass.
2. coo/CONSTITUTION.md binds every run.
3. Nothing is sent, bought, published or submitted without Todd's word in chat, except minor site changes and standing rules (CONSTITUTION 2).
4. Cold email: plain text, under 75 words, no links, a named decision-maker (or pnf_rules owner_read_inbox, or pest_role_inbox), a downstream stage, asks permission.
5. No person's data in the repo (except sealed with tools/data_box.py), scoreboard or logs. Named prospects live in the CRM and data/ (Todd, Oct 22).
6. No em or en dashes. Plain words. No invented people, numbers, claims.
7. Push: check_repo exits 0, git push origin HEAD:main, no force.
8. Tools: the repo, GitHub MCP, ArtifactData, Claude Docs, web search and fetch, Agent checkers, Claude in Chrome only where a SKILL says. Never Drive, the Gmail connector, Zapier, Typefully, Lovable, QuickBooks, Adobe or Supermetrics.
9. Verify before done: docs/ changes run `python3 tools/verify_site.py --changed --before --flows`, every FAIL fixed (skill verify).
