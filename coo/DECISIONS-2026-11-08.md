# Decisions, Nov 8, 2026

## Posting burst, Nov 8 and 9 (live chat, 10:08 am)
Todd: "Just do 5 posts today and 5 tomorrow and then we can get back on track". video/config.json posting.burst: 5 a day on Nov 8 and 9, a slot run posts up to 2 (`anim.py next` prints perRun); POSTING.md and coo/constitution/video.md amended; the cadence table applies again Nov 10. Line check at 10:08 am: only 5 lessons are cleared to post (5 more sit on Todd's Nov 2 hold for videos made under the old gates), and the short chatgpt-check-short waits 24 h after ask-chatgpt, so the simulated line is 4 today and 1 tomorrow.

## Proven only, and the 100K test post (live chat, 10:15 AM)
Todd: "Actually just make new videos using the 100K+ sources - post the one you made now to test it. Going forward all videos should use this method." laneTest pattern is proven only; nextlane gives none (queue sourceprint jobs), never story, when no source at the bar is ready. pay-before-you-leave moved to the front of the posting line for the 11:37 am run. Held old-gate lessons stay held.

## Burst withdrawn (live chat, 10:15 am)
Todd: "Just keep it to 3 posts per day". posting.burst removed from video/config.json; `anim.py next` prints perRun 1 again. The burst code path stays dormant (POSTING.md: only when config sets a burst).

## Studio changes 1, 2, 4 built; hook moves and the Nov 14 test (video-lab chat, 1:35 pm on)
Todd's ask, 1:35 pm: "Build changes 1, 2 and 4 with planted test cases. Never edit a gate just to make a lesson pass." (his Nov 7, 6:59 pm go, DECISIONS-2026-11-07.md). No gate loosened; no sealed file touched.
- Change 1: every drawn string in cues.md; lint fails a missing one from lessons dated 2026-11-26; facts reads cues.md and runs a storyboard round before scene code (prompts/facts.md, README.md).
- Change 2: `anim.py fresh` and lint: cover and first hook cut layout against the two lessons before, send and close transitions; design reads 04_scene/fresh.json.
- Change 4: kit pieces with the x 930 edge, the size 52 floor, the tag row and the still hold; lint also fails scene text past x 930 for the new lessons.
- Lab-size additions (small, no gate loosened): the hook move library (_shared/hooks.md, `anim.py hookmoves`, script and lint fail a repeated opening move), `anim.py cohort` and research/TEST-2026-11-14.md, research/STUDY-2026-11-08.md. Bigger ideas go to Todd one at a time.
- Gemini quota used by the lunch run: the source study waits in video/watch/pending/ for the first run after 2 am Nov 9.
- [stated] Decision 1 (video-lab chat, about 2:55 pm), to "Should the proven lane pick its next source row by that first (money between two people, or our phone topics), before any other row at the 100K bar?": "Yes, pick by topic first (Recommended)". Built: anim.py eligible_rows orders rows by topic (PULL_TOPIC), then views; `nextlane` prints the pick order; _shared/formats.md "Pick". Every gate and the 100K bar stand.
- [stated] Decision 2 (video-lab chat, about 3:00 pm), to "For proven lessons, make it a hard check again: the source's conflict in 5 to 8 words on frame 0, and spoken in 12 words or fewer by 3.6 s?": "Yes, hard check for proven (Recommended)". Built: anim.py proven_hook_hard, script (words before voice), hook and lint (3.6 s after), lint cover (5 to 8 words on frame 0), for proven lessons dated 2026-11-26 on; the 9-word floor stays a note. Todd, 2:54 pm, while this ran: "we are using other viral videos in this niche as our reference. We are aiming to take stories and content from top performing videos (100K+ views) and transforming them into our format."
- [stated] Decision 3 (video-lab chat, about 3:05 pm), to building a second character so the next won't-pay lesson acts the conflict out, then asks the viewer what they'd do: "Yes, build it, test on 1 lesson (Recommended)". Built: kit.js k.client (homeowner and buyer roles, 7 poses, 3 moods; stills in _shared/style-board/client-poses-2026-11-08.png), kit.md, formats.md "Act it out, once", cohort marks the lesson. Every gate stands.
