# Decisions, Nov 6, 2026

## Videos back on the new line (live chat, 7:15 am)
- [stated] After watching the review page of 2026-11-17-after-hours-robot (the first story lesson, built in the Nov 5 build run, video/studio/REBUILD.md step 1): "The new video is so much better. Go with you recommendations. Let's bump to 3 posts per day. start with the one I just watched this morning."
- The video posts first. Its compare gate FAILED (stop 3 of 4, understand 3, follow 2: the opening is an argument, not a moment) and was shown on the review page; Todd chose to post. His words are its override in 05_render/reviews/compare.json. Every other gate passed: code QA, facts (r6, 23 claims, 0 mismatches), facts on captions (r0, 0 mismatches), render critic, retell, read-aloud, send, design (4.71).
- 3 a day: video/config.json posting perDay 3, slots lunch 11:37, end of day 16:41, evening 20:13 Central (the Oct 30 cadence slots). CONSTITUTION 2 amended; video-studio SKILL reads 3 a day.
- Recommendation 1, round 2 opens on two short scenes before the claim: video/studio/_shared/storycraft.md (Openings), LEARNINGS.md.
- Recommendation 2, CONSTITUTION 2's gate list for story lessons: retell, read-aloud and compare replace buyer and golden (anim.py STORY_GATES; prompts/README.md). The 6 lessons held since Nov 2 keep the old gates and stay held.
- Recommendation 3, the ai and core lane test ends early: video/config.json lanes mode off. Every lesson now comes from the trade pulse and the story desk.
- stop set to false (video/config.json stopNote quotes him). "stop videos" in any chat still halts it.

## Local box jobs (live chat, 7:49 am)
- [stated] Asked whether the local model helps with the grunt work on the videos, and shown the four shadow results (pulse grouping 38% off, story draft 3 faults, retell 3 of 3, read-aloud 2 of 3): "ok go with your rec".
- Changed: trade-pulse SKILL step 3 (the extract job lists unplaced items and keeps each why whole), storycraft.md "For the engine" step 4 (a new shadow job for the five openings). Still shadow only: nothing local reaches a video.
