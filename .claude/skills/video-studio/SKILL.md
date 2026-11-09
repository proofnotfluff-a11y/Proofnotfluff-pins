# video-studio (post, make, learn; slots in video/config.json "posting")

Each run: post the next gated lesson on four platforms, make one v4 lesson, learn. Up to 3 a day by the buffer rule (`anim.py next`), queue first (coo/constitution/video.md). Engine v4 from Nov 9, 2026 (Todd: "Make all the necessary changes"). "stop videos" halts it (video/config.json stop); "makePaused" stops making only.

## Inputs (Reads)
By step; paths under video/studio/.
- All: coo/constitution/video.md, PRINCIPLES.md, LEARNINGS.md ("Rules learned", last 10 lines).
- 2 POSTING.md (that platform); 3 research/PERFORMANCE.md "Real time", research/TEST-2026-11-23.md; 4 _shared/formats.md "v4" only, _templates/v4-*, the newest v4 lesson's scene.js; 5 prompts/README.md "v4".
- Never: the formats.md sections above "v4", IMPROVE.md (frozen to Nov 23), research/IDEAS.md, KNOWLEDGE.md, research/runs/, archive/, coo/history/.

## Process (Executes)
1. Date, preflight `video-studio`, config stop: tell Todd, end.
2. Post: `anim.py next`, then `anim.py postcopy <slug>` (renders its gated commit). POSTING.md for each missing platform (Claude in Chrome): Instagram, TikTok, YouTube, Facebook last; a failed Facebook step never blocks. AI labels as captions.json settings say for a v4 lesson. Chrome unreachable or a stop condition: skip posting, tell Todd one line, go on.
3. Every run: one line per lesson under 72 h in PERFORMANCE.md's log, against the bars in TEST-2026-11-23.md. Evening: the deep read. No rule, gate or format change before Nov 23 (the freeze); findings go to LEARNINGS.md.
4. Make while fewer than 6 wait and makePaused is unset: first a v4 lesson built but not queued; else one new v4 lesson, its format the one TEST-2026-11-23.md names for the day. `anim.py new <date>-<words>` copies the v4 templates. Stages:
   - Story: a real, public trade dispute, price fight or phone story (the box's pulse, press, public posts), read today. brief.md: Format, The one idea, Pull (conflict, dollars, send: all yes), breadth (a tech or a homeowner would stop too), Source. facts.json: every number and claim with the source's own words. No person or business named.
   - script.md: 45 to 95 words, the fight in the first sentence, "he says" on anything the source could not verify, the owner's rule as the reason, a closing question that splits the room. Facts gate on script.md before any voice.
   - `speak`, push (check_repo first), wait for the Studio voice workflow (pull each minute, 15 min max), `fetch`. Credits under 3,000: tell Todd, make nothing.
   - cues.md (every row on screen written exactly; one cue marked `[payoff]` by 40%), `cues`; scene.js from `_templates/v4-verdict.scene.js`: change the rows, the place and the cue words, keep the helpers; `stills`, read the sheet, fix; `lint` PASS (safe area, size 132 rows, no hold over 4 s, no flicker, labels); `render`, `check`, `gatepack`. Aim for one render.
   - captions.json per formats.md "v4" (the dilemma, one question, a Source line; labels: Instagram, Facebook, TikTok on, YouTube off).
5. Gates (prompts/README.md "v4"): fresh opus reviewers who never saw the build: render-critic, viewer (two steps), facts on transcript, screen and captions. Results in 05_render/reviews/<gate>.json, earlier rounds in reviews/r<n>/. At most 2 fix rounds a gate, then `anim.py shelve` and take the next story. All PASS: commit, push, `anim.py ready <slug>`.
6. Cloud recorder only, after the post log is recorded: `anim.py missed`; MISSED or INCOMPLETE goes first in the end message. Push after check_repo exits 0 (never force). coo/HANDOFF.md one line only when state changes.
7. Send Todd one message: posted (4 links), made (gate lines PASS/FAIL with values, renders used), read (each lesson against its bar), held (why).

## Outputs (Writes)
- video/studio/videos/<slug>/ (text and JSON; audio and MP4 stay off main), reviews, queue.json via anim.py, research files, LEARNINGS.md.
- Never: post a lesson that is not in the queue or whose fingerprints changed, post twice, boost, spend, reply, change a profile or setting, enter a password, delete a post, post to another platform or account; print or log the ElevenLabs key; change a rule, a gate or anim.py during the freeze.
