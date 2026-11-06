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

## Trial model (live chat, 9:53 am)
- [stated] "Let's do that and test out the better model. We should be constantly tinkering and finding the best solutions out there. Let me know what you need from me to make it happen"
- Qwen3.8-27B (unsloth UD-Q4_K_XL, 17.6 GB, Apache 2.0) runs beside workhorse and fast until Nov 13, shadow only: tools/local_trial.json makes tools/local_job.py send every job a twin named trial-<name>. Box step: pnf-local-jobs scripts/add-trial-qwen38.sh, run once by Todd with sudo (download checked against two checksums, every change backed up, any failed test puts it all back).

## Shorter local testing (live chat, 10:34 am)
- [stated] "Start leaning on delivery and a lot faster. We're burning through cloud usage really, really quickly. I'm not sure we can afford 2 weeks of shadow. We'll probably need to reduce the testing period. Because, practically speaking, we really need to find a way to make this hardware investment worthwhile."
- Changed: video/studio/_shared/local.md, a 3-rung ladder (shadow, local first, spot check) on 3 clean comparisons in a row instead of two weeks. Retell and read-aloud move to local pre-checks now (the Opus gates run only after the local check passes and still decide). Trial model judged after 3 twin comparisons per job kind.

## Back Office demo, roofing (live chat, 10:32 am)
- Todd shared a screen recording of the joebrunner.ai "Insane custom roofing CRM" reel and asked whether PNF could build something like it, better, and market it the same way. The live session's answer: no full CRM (crowded and cheap, needs accounts and support we lack); build the back-office slice (morning list of drafted messages, quoted against spent, who still owes, leads in, export) as a demo on labeled sample data.
- [stated] Offered A (the slice), B (full CRM) or C (park): "Let's go with A"
- Spec: launches/back-office-demo.md (roofing first, the session's call; sample data rules for invariant 6; reel, 5 owner calls and price each wait on Todd). Wiki: Research Wiki Sources and Decisions, Nov 6.

## Usage cuts (live chat, 10:54 am)
- [stated] "Go with your rec", to: the box reads forum and trade press pages itself, and retell, read-aloud and compare merge into one Opus reviewer.
- Changed: video/studio/prompts/story.md and anim.py STORY_GATES (one story gate, same three bars, two turns so the listener never sees the message line early); CONSTITUTION 2 amended; tools/local_job.py fetch; trade-pulse SKILL step 3; the page reader (pnf-local-jobs scripts/fetcher.py and add-fetcher.sh: https only, allowlisted sites, robots.txt respected, page text never leaves the box). Box step: Todd runs add-fetcher.sh once.
- Todd's own step: remove unused connectors from each PNF scheduled task (USAGE.md A5).
