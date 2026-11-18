# Decisions, Nov 18, 2026

## Video engine: story first, told like a person, characters that act
- Why it came up: Todd watched 2026-12-04-dead-or-150 (the first call, posted Nov 17) and opened a live chat at 9:07 am. His words: "the script was kind of very robotic, very uninteresting. The story wasn't very interesting as well. These are like very simplistic templates that we're putting out as videos."; "the last video says reenactment, and then there's like this short little thing"; "the animation doesn't look great either"; "make sure the stories are more interesting, the script sounds more human, and the animation is better. I want you to design this as Fable, but then we can switch over to Opus 5.5 for the build."
- What the read found (numbers from video/studio/research/metrics/, read Nov 18): the three v4 lessons with reads reached 4,093 on Instagram and 1,217 views on TikTok with 0 shares and 0 follows; the 76 s case held best (Instagram 69% of runtime, YouTube 86% average viewed) and worst on TikTok (30%); `anim.py readcheck` fails dead-or-150's script (1 choppy run) and passes the other three, and v4 does not run it; its storyboard puts 24 text cards in 34 s; 5 make runs since Nov 12 made nothing (no source readable); the viewer gate passed it at a forecast of 3, 3, 3, 2.
- The design, with the full reasoning, the script before and after, and what was not checked: https://claude.ai/artifact/BPUemKBYCWQiHNLss2NtNK. The build contract: video/studio/BUILD-2026-11-18.md.
- [stated] Todd, live chat, Nov 18, 2026, picks tapped on question cards between 9:07 and 9:15 am: length, "45 to 90 s (Recommended)"; acted scenes, "On-screen tag only (Recommended)"; the freeze, "Lift it now (Recommended)"; formats, "Story first (Recommended)".
- [stated] Todd, same chat, by 9:20 am, the split check: "Yes, only for open endings (Recommended)". Then, at 9:20 am, to the design as a whole: "Go".
- [stated] Todd, same chat, about 9:22 am, the nightly make run until the build lands: "Pause making (Recommended)".
- What each covers. Length: new story lessons run 45 to 90 s (the 18 to 35 s band of Nov 9, item 1, ends for them). Acted scenes: a small Reenactment label on the first acted frame, never spoken; acted lines only where the source reports that person's own words, otherwise the narrator tells it. Freeze: the Nov 9 to Nov 23 freeze ends for these changes; the first lesson made under them goes to Todd to watch before it posts. Story first: no format is picked first; the story's shape follows from what happened (a result is held for the end, no result ends on the question); invoice and update are parked until they earn a place. Split check: the Nov 11 "split" story check applies only to stories that end on a question. Pause: video/config.json "makePaused" is set; posting, recording, the number reads and the box queue go on; the build chat removes it as its last step.
- What it does not cover: honesty (every line of it), the AI labels, one post a day, the posting route, spend, accounts, the outreach and site lines. The four gates keep their honesty checks; the build adds checks and loosens none. No gate file in tools/gate_seal.json is touched.
- Not decided, still Todd's: the voice setting (a two-take test in the build), opening record and news sites to the cloud runs (his environment setting), TikTok by hand and the feed sign-ins (open since Nov 11).
- This design chat ran on Fable on his word above. Fable sits on no gate and no reviewer role; the build and every reviewer run on Opus 5.5.

## Bars, set Nov 18 before any lesson is made the new way
Read on the first 3 lessons made under these rules, at 72 h. A watch or swipe number counts only where the platform shows 200 views or more (research/TEST-2026-11-23.md, whose levels and 0.5% send bar stand).
| Change | Keep | Rethink | Today |
|---|---|---|---|
| Stories | 2 of 3 pass 2,600 views on one platform | none passes 1,300 | best 2,600, 1,932, 1,786 |
| Story supply | a lesson made on 6 of the first 7 days once sources open | fewer than 4 of 7 | 4 posts in 9 days |
| Scripts | Instagram average watch 60% or more and YouTube average viewed 60% or more, on 2 of 3 | all 3 under 50% on Instagram | Instagram 62%, 52%, 69%; YouTube 86% and 32% where shown |
| Animation, step 1 | Todd picks the new scene over the old, side by side | he picks the old, or cannot tell | not run |
| Animation, step 2 | YouTube swiped away 30% or lower on 2 of 3 | all 3 over 40% | 33%, 48%, 24% |
| Shares | 3 or more across the 3 lessons | 0 over 5,000 Instagram reach | 0 over 4,093 |
- Trigger, not a bar: TikTok average watch under 35% on 2 of the 3 brings the question of a short TikTok cut back to Todd.
- The viewer forecast rule (under 4 on hold or finish fails) is on trial: each forecast is filed beside the real result, and the rule comes out if after 6 lessons the higher forecasts do not hold better.
