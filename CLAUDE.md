# ProofNotFluff router (Layer 0)

Read this, then coo/HANDOFF.md, then only the one SKILL.md your run names. Nothing else loads before the run starts.

## Topology
- .claude/skills/<job>/SKILL.md: stage contracts (Inputs, Process, Outputs). One stage, one job.
- tools/: deterministic code. Fetching, paging, joins, dedup, schemas and copy checks run here, never in a model.
- permits/downstream/gc_leads.json: Entity A, GC leads in downstream stages (public, business fields only), written by the downstream-leads workflow.
- data/ (gitignored): Entity B prospects and per-run work files. Named people, never committed.
- CRM https://claude.ai/artifact/De189P4AXgWVC6o8LYbxdB and scoreboard https://claude.ai/artifact/N9eKZy7Pv39njSe4izVgbE (ArtifactData).
- coo/, email/, design/, legal/, launches/: reference, read only when a SKILL lists it. archive/: never read by a run.

## Invariants
0. Date from bash: `TZ=America/Chicago date`. Never guess it.
1. First: `python3 tools/check_repo.py --preflight <job>`. Exit 1 stops the run; report the ERROR lines to Todd. Never edit a gate to pass.
2. coo/CONSTITUTION.md binds every run.
3. Nothing is sent, bought, published or submitted without Todd's word in chat for that batch.
4. Cold email: plain text, under 75 words, no links, a named decision-maker, a downstream stage, asks permission.
5. No person's data in the repo, scoreboard or logs. Prospects live in the CRM and data/.
6. No em or en dashes. Plain words. No invented people, numbers or claims.
7. Push: check_repo exits 0, git push origin HEAD:main, never force.
