# video-studio (daily lesson: post, make, improve; 7:46 am Central)

One job: post yesterday's gated lesson to four platforms, make tomorrow's, and ship one improvement. Todd, Oct 28, 2026, 3:04 pm: "start publishing 1 video per day on Tik Tok, Instagram, FB, and YouTube. Constantly try to improve" (coo/DECISIONS-2026-10-28.md; standing video post rule, CONSTITUTION 2). "stop videos" in any chat halts it (video/config.json stop).

## Inputs (Reads)
- video/studio/CLAUDE.md, CONTEXT.md, stages/*/CONTEXT.md, _shared/*.md, POSTING.md, IMPROVE.md, queue.json, research/IDEAS.md and KNOWLEDGE.md, the last lesson folder as the pattern (videos/<latest>/).
- video/prompts/*.md as gate references; design/DESIGN_DIRECTOR.md.

## Process (Executes)
1. Date, preflight `video-studio`, config stop: tell Todd, end.
2. Post: `anim.py next`. A lesson waiting: follow POSTING.md for each missing platform (Claude in Chrome). Chrome unreachable or a stop condition: skip posting, tell Todd one line, go on to 3.
3. Mondays: research run by research/README.md (fresh agent, opus), then read each posted lesson's numbers in Chrome (views, average watch, shares, saves) into research/metrics/<slug>.json; rank IDEAS.md by them.
4. Make: next idea from IDEAS.md (the top one not made; mix topics across follow-up, pricing, bids, marketing, reviews, numbers). Slug <date>-<words>. Stages 01 to 05 by their contracts:
   - brief.md and facts.json: every number re-read on its source page today; numbers block; `anim.py data`.
   - script.md as talk (_shared/voice.md hook rules), 45 to 75 s, one stat hook, a copyable takeaway, a send line.
   - `speak`, push (check_repo first), wait for the Studio voice workflow (pull every minute, up to 15 min), `fetch`; flags 0 and pace 160 to 195 or re-roll that take once. takes.json credits left under 3,000: tell Todd.
   - cues.md (rooms, one beat every 2 to 4 s), `cues`; scene.js from the last lesson's pattern and the kit, motion rules in _shared/looks.md; `stills`, read the sheets, fix; `render`, `check`.
   - captions.json: per platform from _shared/captions.md (descriptions, keywords, tags).
5. Gates, each a fresh agent (model opus) that never saw the build, results in 05_render/reviews/<gate>.json: facts (brief, script, transcript, scene.js text, captions.json), render critic, buyer, design (no score under 4, average 4.61), golden. One fix round per gate; a gate's second FAIL holds the lesson for Todd. All PASS: `anim.py ready <slug>` (it posts tomorrow).
6. Improve: one IMPROVE.md item in the shared runtime, proven on stills of today's lesson and lesson 1 before step 4's render; log it under Done.
7. Push after check_repo exits 0 (never force). Scoreboard rows (video engine todos, agents/video-studio), counts only. coo/HANDOFF.md one line only when state changes.
8. Send Todd one message: posted (4 links), made (gate lines PASS/FAIL with values), improved (one line), held (why).

## Outputs (Writes)
- video/studio/videos/<slug>/ (text and JSON; audio and MP4 stay off main), reviews, queue.json via anim.py, IMPROVE.md, research files.
- Never: post a lesson that is not in the queue or whose fingerprints changed, post twice, boost, spend, reply, change a profile or setting, enter a password, delete a post, post to another platform or account; print or log the ElevenLabs key.
