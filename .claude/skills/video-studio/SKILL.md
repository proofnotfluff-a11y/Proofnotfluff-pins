# video-studio (post, make, learn; slots in video/config.json "posting")

Each run: post the next gated lesson on four platforms, make one, learn. Up to 3 a day by the buffer rule (`anim.py next`: 3 at 6+ waiting, 2 at 3 to 5, 1 at 1 or 2; Todd, Nov 7), queue first, each unique (CONSTITUTION 2). "stop videos" halts it (video/config.json stop).

## Inputs (Reads)
- video/studio/CLAUDE.md, CONTEXT.md, stages/*/CONTEXT.md, _shared/*.md, POSTING.md, IMPROVE.md, LEARNINGS.md, prompts/, queue.json, research/IDEAS.md, KNOWLEDGE.md, PERFORMANCE.md, the last lesson as the pattern.
- design/DESIGN_DIRECTOR.md; research/runs/2026-10-28-script-playbook.md (script template) and 2026-10-28-topic-bank.md (sourced briefs).

## Process (Executes)
1. Date, preflight `video-studio`, config stop: tell Todd, end.
2. Post: `anim.py next`, then `anim.py postcopy <slug>` (renders its gated commit). POSTING.md for each missing platform (Claude in Chrome): Instagram (normal reel), TikTok, YouTube, Facebook last; a failed Facebook step is skipped, never blocking. A refused upload: use postcopy's path. Chrome unreachable or a stop condition: skip posting, tell Todd one line, go on to 3.
3. Every run: diagnosis (research/PERFORMANCE.md, Real time). Evening: the deep read (PERFORMANCE.md). Mondays (lunch): research run by research/README.md (fresh agent, opus), then each posted lesson's numbers in Chrome (views, average watch, shares, saves) into research/metrics/<slug>.json; rank IDEAS.md by them; `anim.py recuts` and add an IDEAS.md re-cut line for each due top-third lesson (POSTING.md).
4. Queue rule: `anim.py waiting`. Make while fewer than 6 wait (Todd, Nov 7), in order: a lesson or short built but not queued; a short for the newest queued story lesson with none (_shared/formats.md "Short"); the next Ready story (REBUILD.md, research/STORIES.md). Never from IDEAS.md or the old lanes (Nov 6). 6 or more: make none, ship step 6. Slug <date>-<words>; each lesson its own worlds (_shared/sets.md). Stages 01 to 05 by their contracts:
   - brief.md and facts.json: every number re-read on its source page today; numbers block; `anim.py data`.
   - brief.md's Hook pattern, Treatment, Example and Music lines: `anim.py variety <slug>` PASS before `speak` (a rebuild keeps its example; change the hook pattern if it fails). Music: a tune the lessons before and after it in line do not play (`anim.py tunes <slug>`; _shared/sound.md); cues.md says `music: rooms <tune>`, and a rebuild picks a free tune the same way.
   - script.md by viral-script (bands in _shared/formats.md), held to _shared/standard.md. Send moment (Todd, Nov 7): brief.md `- **Send:** <who>: <thing>`, end card names who, one `[send]` cue held 2.5 s before half (formats.md); story 50 to 65 s, 70 s cap; `sendcheck` PASS.
   - `speak`, push (check_repo first), wait for the Studio voice workflow (pull each minute, 15 min max), `fetch`; flags 0 and pace 160 to 195 or re-roll that take once. takes.json credits left under 3,000: tell Todd once and make no new lesson until they reset.
   - cues.md (`music: rooms <tune>`, rooms, one beat every 2 to 4 s), `cues`; scene.js from the last lesson's pattern and the kit, motion rules in _shared/looks.md; `stills`, read the sheets, fix; `lint` PASS; `render`, `check`, `gatepack`.
   - captions.json: per platform from _shared/captions.md (descriptions, keywords, tags). First draft from Kimi: send the captions-draft job with the facts job right after `fetch` (.claude/skills/kimi-jobs/SKILL.md), then edit it yourself.
5. Gates from video/studio/prompts/ (README: order and bars), fresh opus agents that never saw the build, results in 05_render/reviews/<gate>.json. Facts and facts-captions go to Kimi first (kimi-jobs skill, Claude checks); cap, error or no answer: opus. Fix rounds go on until all pass (design bar 4.50 after 2 FAILs; Todd, Oct 31); finish unqueued ones first, in `anim.py tomake` order (prompts/story.md). Faults go in LEARNINGS.md; a lint-catchable one becomes a lint rule. All PASS: commit, `anim.py ready <slug>` (push first).
6. Every slot: one IMPROVE.md item in the shared runtime, proven on stills of today's lesson and lesson 1 before step 4's render; log it under Done.
7. Cloud recorder only, after the post log is recorded: `anim.py missed`; MISSED or INCOMPLETE goes first in the end message (slot, lesson, likely cause: laptop asleep, Chrome signed out, extension dropped). Push after check_repo exits 0 (never force). Scoreboard rows (video engine todos, agents/video-studio), counts only. coo/HANDOFF.md one line only when state changes.
8. Send Todd one message: posted (4 links), made (gate lines PASS/FAIL with values), improved (one line), held (why).

## Outputs (Writes)
- video/studio/videos/<slug>/ (text and JSON; audio and MP4 stay off main), reviews, queue.json via anim.py, IMPROVE.md, research files.
- Never: post a lesson that is not in the queue or whose fingerprints changed, post twice, boost, spend, reply, change a profile or setting, enter a password, delete a post, post to another platform or account; print or log the ElevenLabs key.
