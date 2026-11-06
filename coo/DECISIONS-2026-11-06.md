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
- Todd's own step: remove unused connectors from each PNF scheduled task (USAGE.md A5). Withdrawn 11:10 am: tasks can't drop connectors one by one (USAGE.md A5 closed).

## Grid-down access and offline library (live chat, 12:56 to 1:07 pm)
- [stated] Owns an EcoFlow DELTA 3 Classic (1,024 Wh) with a 220 W panel ("I have this"), the battery for the GEEKOM in an outage.
- [stated] "Let's do lean but also add maps and khan academy - let's also add anything else you think might be useful in a blackout. Can this be packaged so once I get a powerful portable laptop we could migrate it over at some point?"
- Chosen: the lean build over Project NOMAD (NOMAD's AI searches uploaded files only and has no login). The GEEKOM becomes the stay-at-home offline library and AI; this replaces the Nov 5 line "Project NOMAD stays separate". Plan of record: the architecture doc, section "Grid-down mode and the offline library" (contents, power, outage Wi-Fi, portable /srv/offline package, guards, build order).
- Guards: /srv/offline outside backups; downloads 11 pm to 7 am, speed-capped; shutdown only on a dead Deco cable; every install through skill-security-check; no Docker.
- Open: Todd's internet data cap; Todd plugs the box in through the station.

## Studio task moved so runs reach the local box (live chat, 1:34 to 2:09 pm)
- Cause: "PNF video studio: record and make" was a Chat-type scheduled task, which has no repository setting, so runs could not clone or push the private lane pnf-local-jobs.
- Todd made a Claude Code task, "PNF video studio: record and make (code)" (trig_01DQgwhpsSPXrcejNQm9xg1L), with both repos attached, the same prompt plus one line (if the lane is refused, carry on without the box and say so), 9:33, 12:33, 17:33, 21:33 Central, Opus 5.5. He turned the old task (trig_014GCfsTDTXDmRRbYUMBbDyL) off; nothing deleted.
- [stated] "all tasks done. go"
- First check: the 5:33 pm run's local box line.

## Pivot rule: owned IP, no time sold (live chat, 3:08 to 3:19 pm)
- Asked for an objective look, the live session recommended pivoting from building to selling Todd's finance expertise. Todd rejected that: "The last thing I want to do is sell my time. I don't want to become a consultant." He wants IP that sells and scales without him in front of people (digital product, physical product, system, app, faceless content, affiliate).
- [stated] "Yes, let's park the back office demo and let's do a fresh chat and dive into this because we need to figure out where the pivot needs to go."
- Changed: launches/back-office-demo.md marked parked. Next, in a new chat: score candidates on six tests (self-serve purchase, a channel we own without a face, zero work per sale, near-zero support, Todd's edge built in, compounds over time), with review mining first, including ways to monetize the video engine (community, audience, affiliate). Top 3 to Todd; nothing built until he picks.
