# video-studio (post, make, learn; slots in video/config.json "posting")

Each run: post the next gated lesson on four platforms, make one `told` lesson, learn. One a day from Nov 10, evening slot (Todd, Nov 9, 5:10 pm; `anim.py next`), queue first (coo/constitution/video.md). Engine v4 from Nov 9, 2026 (Todd: "Make all the necessary changes"). "stop videos" halts it (video/config.json stop); "makePaused" stops making only.

## Inputs (Reads)
By step; paths under video/studio/.
- All: coo/constitution/video.md, PRINCIPLES.md, LEARNINGS.md ("Rules learned", last 10 lines).
- 2 POSTING.md (that platform); 3 research/PERFORMANCE.md "Real time", research/TEST-2026-11-23.md; 4 _shared/formats.md "v4" only (its "Case" and "Told"), _shared/storycraft.md, research/STORIES.md bank, _templates/v4-*, the newest v4 lesson's scene.js; 5 prompts/README.md "v4".
- Never: the formats.md sections above "v4", IMPROVE.md, research/IDEAS.md, KNOWLEDGE.md, research/runs/, archive/, coo/history/.

## Process (Executes)
1. Date, preflight `video-studio`, config stop: tell Todd, end.
2. Post: `anim.py next`, then `anim.py postcopy <slug>` (renders its gated commit). POSTING.md for each missing platform (Claude in Chrome): Instagram, TikTok, YouTube, Facebook last; a failed Facebook step never blocks. AI labels as captions.json settings say for a v4 lesson. Chrome unreachable or a stop condition: skip posting, tell Todd one line, go on.
3. Every run: one line per lesson under 72 h in PERFORMANCE.md's log, against the bars in TEST-2026-11-23.md. Evening: the deep read; findings go to LEARNINGS.md.
4. Make while fewer than 6 wait and makePaused is unset: first a lesson built but not queued; else one new `told` lesson (Todd, Nov 18; formats.md "Told") from the top Ready row of the bank in research/STORIES.md, its sources read again today; no row passes the story test: make nothing, say so. `anim.py new <date>-<words>` copies the templates. Stages:
   - Story: brief.md: Story test (six answers from the source, 12 or more claims rows), Ending (result or question), The one idea, Source. facts.json: every number and claim with the source's own words. No person or business named.
   - script.md: 110 to 240 words, written whole as speech (storycraft.md); `anim.py script` PASS (readcheck, 1 sentence in 3 short at most, no "Reenactment", story test, Ending). Then facts, read-aloud, pick on script.md before any voice; a marked line is rewritten in the same voice, never cut.
   - `speak`, push (check_repo first), wait for the Studio voice workflow (pull each minute, 15 min max), `fetch`. Credits under 3,000: tell Todd, make nothing.
   - cues.md (a cue every 6 s on average, none over 8 s apart; one `[payoff]` cue at 60% or later: the result, or the closing question), `cues`; scene.js from `_templates/v4-verdict.scene.js`, cards only for numbers, names and the Reenactment label on the first acted frame; `stills`, read the sheet, fix; `lint` PASS; `render`, `check`, `gatepack`.
   - captions.json per formats.md "v4" (labels: Instagram, Facebook, TikTok on, YouTube off).
5. Gates (`anim.py gates_for`; prompts/README.md "v4"): fresh opus reviewers who never saw the build: after the render, render-critic, viewer (two steps), facts on transcript, screen and captions. Results in 05_render/reviews/<gate>.json, earlier rounds in reviews/r<n>/. At most 2 fix rounds a gate, then `anim.py shelve` and take the next story. All PASS: commit, push, `anim.py ready <slug> --first`.
6. Cloud recorder only, after the post log is recorded: `anim.py missed`; MISSED or INCOMPLETE goes first in the end message. Push after check_repo exits 0 (never force). coo/HANDOFF.md one line only when state changes.
7. Send Todd one message: posted (4 links), made (gate lines PASS/FAIL with values, renders used), read (each lesson against its bar), held (why).

## Outputs (Writes)
- video/studio/videos/<slug>/ (text and JSON; audio and MP4 stay off main), reviews, queue.json via anim.py, research files, LEARNINGS.md.
- Never: post a lesson that is not in the queue or whose fingerprints changed, post twice, boost, spend, reply, change a profile or setting, enter a password, delete a post, post to another platform or account; print or log the ElevenLabs key; change the constitution, a gate's honesty checks or anim.py outside a live chat with Todd.
