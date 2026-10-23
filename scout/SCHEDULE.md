# Radar schedule (waits for Todd's go in chat)

Nothing here is switched on. When Todd says go, the live session does both:

1. In .github/workflows/product-health.yml, uncomment the two schedule lines (Mondays 13:10 UTC, about 8:10 am Chicago, after the Monday data pulls), commit and push.
2. Create the scheduled task "PNF radar", Mondays 9:31 am Central (cron `CRON_TZ=America/Chicago 31 9 * * 1`), cloud, with this prompt:

```
ProofNotFluff radar, weekly run: add_repo proofnotfluff-a11y/proofnotfluff-pins with push access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight radar`; if it exits non-zero send Todd the ERROR lines in one message and stop. Otherwise follow .claude/skills/radar/SKILL.md: health, then aivis, then scout. Nothing is built, priced, published, sent or switched on; ideas that pass every reviewer become "Decide: build" rows on the scoreboard to-do list for Todd.
```

Cost: $0 (GitHub Actions minutes on the free tier, the session's own usage). If the scheduler refuses from chat, Todd creates the task in the app with the prompt above.
