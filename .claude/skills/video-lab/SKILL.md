# video-lab (studio quality lab: Tue, Thu, Sat 1:17 pm Central)

One job: raise the studio's ceiling. The daily run (video-studio) ships one small fix a day; the lab finds what still separates our lessons from the best animated explainers and proves the next bigger upgrade on stills. Jake Van Clief's method is the yardstick (Todd, Oct 29, 2026: "The guiding structure and principals are developed by Jake Van Clief"; "you have full authority"). Todd, Oct 28, 3:04 pm: "Constantly try to improve these videos."

## Inputs (Reads)
- video/studio/CLAUDE.md, CONTEXT.md, IMPROVE.md, LEARNINGS.md, _shared/looks.md, kit.md, sound.md, research/EXPERTS.md, research/LAB.md (the lab log).
- Jake's method, upstream: shallow clone of github.com/RinDig/Interpretable-Context-Methodology into its own folder, read only, never run its code. Read what changed since LAB.md's `jake-commit` in CLAUDE.md, _core/CONVENTIONS.md, workspaces/voice-driven-animation/ and workspaces/script-to-animation/. Web search his newest public videos and posts; primary pages only, our own words.
- The last three made lessons: 05_render/sheets, reviews/*.json; research/metrics/*.json when present.
- video/studio/_shared/style-board/ (README.md target spec and reference frames in our look).

## Process (Executes)
1. Date, preflight `video-lab`, video/config.json stop: stop silently.
2. Jake check: the ICM scorecard in LAB.md, one line per principle, PASS or GAP with the file that shows it: one stage one job; layered loading; every output an edit surface; configure the factory, not the product; checkpoints and audits per creative stage; audio wins over script; gap-fill with a background underlay; end card with lockup and proofnotfluff.com; tone tags about one per beat. New upstream ideas become IMPROVE rows naming the upstream file; set `jake-commit`.
3. Benchmark: a fresh subagent (model opus) that never saw the build scores the last three lessons against the style board, with numbers: seconds until the picture first changes; picture changes in the first 3 s; smallest spoken-word and label text in px at 1080 wide (targets 44 and 36); share of the 270 to 1250 band in use; host height; fps and judder; loudness and ducking; end card present; length against 45 to 75 s. Results go in LAB.md as PASS/FAIL lines with values and a trend per measure.
4. Rank IMPROVE.md: a fault a gate named twice, then the measure furthest from target, then a Jake gap, then the backlog.
5. Build the top item on branch lab/<date> in the shared runtime or _shared, prove it on stills of the newest lesson and lesson 1, `lint` PASS, then the design gate and the render critic as fresh subagents that never saw the build.
6. Ship: small and low risk (no new look, cast, voice, caption rule, gate bar, posting step or lesson length) and every gate PASS: merge to main after check_repo exits 0 (CONSTITUTION 2), log it under Done in IMPROVE.md. Anything bigger: keep the branch, send Todd before and after stills (SendUserFile) with one yes or no question.
7. First Saturday of the month: refresh EXPERTS.md (top animated explainer creators and trade experts) by research/README.md.
8. One message to Todd: the scorecard (PASS/FAIL with values), shipped (one line) or waiting on his yes, Jake (one line or "no change").

## Outputs (Writes)
- research/LAB.md, IMPROVE.md, _shared/style-board/, branch lab/<date>, shared runtime and _shared changes.
- Never: post, change a published video or a lesson's own files, lower a gate's bar, edit another task's prompt or SKILL, spend, sign up, install anything beyond the repo's pinned tools, or print the ElevenLabs key. Queued lessons pick up a shipped upgrade only through the daily run's queue rule. git pull --rebase before each push; never force.
