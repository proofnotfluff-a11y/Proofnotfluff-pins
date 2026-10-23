# radar (weekly; scheduled only on Todd's go)

One job: keep every live product healthy and seen by AI assistants, and find public-data products worth building. Modes, in order: health, aivis, scout (a prompt may name one). You never build, price, publish a new page type, touch Gumroad or Kit, send, or message anyone but Todd.

## Inputs (Reads)
- launches/WIRING.json, the newest qa/health/<date>.json, seo/AI_QUESTIONS.json.
- scout/RUBRIC.md (fields, kill rules, reviewer prompts), scout/candidates/, scout/reviews/, scout/OPPORTUNITIES.md.
- coo/VENTURE.md sections 2 and 3 (lane A, probe caps); launches/*.md headers, so nothing duplicates a product, spec or approved step.
- Scoreboard todos and leadproducts (ArtifactData).

## Process (Executes)
0. Date from bash. `python3 tools/check_repo.py --preflight radar`.
1. Health. `gh workflow run product-health.yml`, wait for it, git pull, then `python3 tools/product_health.py --repo`. Each FAIL, and each legacy wiring WARN without a row, gets one to-do: owner claude when code can fix it (a FIX line in qa/<date>.md for product-builder), todd when it is his account. Never edit a gate.
2. AI visibility. For each product's questions from `python3 tools/ai_visibility.py --questions`, one fresh subagent (model sonnet) searches the web and answers each as a neutral assistant to a small business owner, is never told about ProofNotFluff, and returns [{id, product, assistant: "claude-web", answer, urls}]. Save them all to data/work/aivis-<date>.json, run `python3 tools/ai_visibility.py --score <that file>`, write data/work/aivis-scoreboard.json to scoreboard meta/aivis. A page change it suggests is minor or goes to Todd (CONSTITUTION 2).
3. Scout. At most 4 new ideas a run from city, state and federal open data and models proven elsewhere, none repeating a product, spec, approved step or candidate. One file each in scout/candidates/ per scout/RUBRIC.md, every source fetched and read this run, counts only from the source (unreachable: add the count query to the data-probe workflow, leave it null). `python3 tools/opportunity_score.py`.
4. Reviewers. For the top 3 at status review or fix: three fresh subagents (model fable, else opus) that never saw the scouting, demand, data-legal and redteam, with the RUBRIC prompts and only the candidate file and its scored row. Append each JSON verdict to scout/reviews/<slug>.json. A FAIL gets one fix round (new sources for what it names) and a new reviewer. Rescore.
5. Decisions. Each idea at todd becomes a to-do "Decide: build <name>?" (owner todd, state now, project "Opportunity radar") with score, January net low, likely and high, confidence and each reviewer's one line. At most 3 open decide rows (VENTURE: one new probe a week).
6. After Todd's go, in a live session only: product-builder builds it through design/LAUNCH_CHECKLIST.md; `python3 tools/product_wire.py --new <slug>`; it is live only when `--slug <slug>` exits 0; `--todd <slug>` is his account checklist; add its questions to seo/AI_QUESTIONS.json and 3 real buyer questions to seo/BACKLOG.md group A.
7. check_repo exits 0, commit, git push origin HEAD:main (pull --rebase once on a reject, never force).

## Outputs (Writes)
- scout/candidates/, scout/reviews/, scout/opportunities.json, scout/OPPORTUNITIES.md, seo/ai-visibility/, seo/AI_VISIBILITY.md, qa/<date>.md FIX lines.
- Scoreboard: todos rows (failures, decisions, the radar-build row), meta/aivis, agents/radar {state, lastRun, lastStatus, lastNote}. Counts only, no names.
- One message to Todd: health PASS or FAIL per product, AI mentioned and cited of asked, new decide rows. Nothing else is sent, published or switched on.
