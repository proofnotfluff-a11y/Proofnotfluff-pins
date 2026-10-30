# video-studio (three runs a day: post, make, learn; slots in video/config.json "posting")

Each run: post the next gated lesson on four platforms, make one, learn. Todd, Oct 30, 2026: 3 a day, queue first, each unique (coo/DECISIONS-2026-10-30.md; CONSTITUTION 2). The prompt names the slot. "stop videos" in any chat halts it (video/config.json stop).

## Inputs (Reads)
- video/studio/CLAUDE.md, CONTEXT.md, stages/*/CONTEXT.md, _shared/*.md, POSTING.md, IMPROVE.md, LEARNINGS.md, prompts/, queue.json, research/IDEAS.md, KNOWLEDGE.md, PERFORMANCE.md, the last lesson as the pattern; viral-script for scripts.
- design/DESIGN_DIRECTOR.md; research/runs/2026-10-28-script-playbook.md (script template) and 2026-10-28-topic-bank.md (sourced briefs).

## Process (Executes)
1. Date, preflight `video-studio`, config stop: tell Todd, end.
2. Post: `anim.py next`, then `anim.py postcopy <slug>` (renders it from its gated commit). Follow POSTING.md for each missing platform (Claude in Chrome): Instagram as a trial reel, then `anim.py trials` and share each due trial to followers (POSTING.md). A refused upload is a path problem, not "no Chrome": upload the path postcopy prints. Chrome unreachable or a stop condition: skip posting, tell Todd one line, go on to 3.
3. Evening: numbers read and diagnosis (research/PERFORMANCE.md). Mondays (lunch): research run by research/README.md (fresh agent, opus), then read each posted lesson's numbers in Chrome (views, average watch, shares, saves) into research/metrics/<slug>.json; rank IDEAS.md by them; then `anim.py recuts` and add an IDEAS.md re-cut line for each due top-third lesson (POSTING.md).
4. Queue rule first: after step 2, `anim.py waiting`. 9 or more listed (3 days): make no new lesson this run; rebuild the first one listed on today's runtime instead (`fetch`, `stills` and read the sheets, `lint`, `render`, `check`, `gatepack`), then step 5 with every gate fresh; `ready <slug>` keeps its place in line. A gate's second FAIL there: `git checkout -- video/studio/videos/<slug>` (its old pin still posts), log "rebuild held: <slug>" in LEARNINGS.md and skip that slug in later rebuilds. Fewer than 3: make.
   Make: next idea from IDEAS.md's Trades-first bank (top one not made), script by viral-script, format by _shared/formats.md. Trade evidence only, no other-industry studies; each lesson its own worlds from _shared/sets.md (lint fails reused scenery). Slug <date>-<words>. Stages 01 to 05 by their contracts:
   - brief.md and facts.json: every number re-read on its source page today; numbers block; `anim.py data`.
   - brief.md's Hook pattern, Treatment, Example and Music lines: `anim.py variety <slug>` PASS before `speak` (a rebuild keeps its example; change the hook pattern if it fails). Music: a tune the lessons before and after it in line do not play (`anim.py tunes <slug>`; _shared/sound.md); cues.md says `music: rooms <tune>`, and a rebuild picks a free tune the same way.
   - script.md as talk (_shared/voice.md hook rules), 45 to 75 s, one stat hook, a copyable takeaway, a send line.
   - `speak`, push (check_repo first), wait for the Studio voice workflow (pull each minute, 15 min max), `fetch`; flags 0 and pace 160 to 195 or re-roll that take once. takes.json credits left under 3,000: tell Todd once and make no new lesson until they reset.
   - cues.md (`music: rooms <tune>`, rooms, one beat every 2 to 4 s), `cues`; scene.js from the last lesson's pattern and the kit, motion rules in _shared/looks.md; `stills`, read the sheets, fix; `lint` PASS; `render`, `check`, `gatepack`.
   - captions.json: per platform from _shared/captions.md (descriptions, keywords, tags). First draft from Kimi: send the captions-draft job with the facts job right after `fetch` (.claude/skills/kimi-jobs/SKILL.md), then edit it yourself.
5. Gates from video/studio/prompts/ (README: order and bars), each a fresh agent (model opus) that never saw the build, results in 05_render/reviews/<gate>.json. Facts and facts-captions go to Kimi first by the kimi-jobs skill, with its Claude checks; cap, error or no answer: the opus agent as before (Todd, Oct 29). One fix round per gate; a gate's second FAIL holds the lesson for Todd. Faults go in LEARNINGS.md; a lint-catchable one becomes a lint rule. All PASS: commit, `anim.py ready <slug>` (pins the commit; it posts tomorrow).
6. Lunch slot only: one IMPROVE.md item in the shared runtime, proven on stills of today's lesson and lesson 1 before step 4's render; log it under Done.
7. Push after check_repo exits 0 (never force). Scoreboard rows (video engine todos, agents/video-studio), counts only. coo/HANDOFF.md one line only when state changes.
8. Send Todd one message: posted (4 links), made (gate lines PASS/FAIL with values), improved (one line), held (why).

## Outputs (Writes)
- video/studio/videos/<slug>/ (text and JSON; audio and MP4 stay off main), reviews, queue.json via anim.py, IMPROVE.md, research files.
- Never: post a lesson that is not in the queue or whose fingerprints changed, post twice, boost, spend, reply, change a profile or setting, enter a password, delete a post, post to another platform or account; print or log the ElevenLabs key.
