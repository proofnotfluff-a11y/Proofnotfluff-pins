# Decisions, Oct 30, 2026

## Video studio: three a day (Todd, live chat, about 8:40 am)
- [stated] "I want to switch to 3 posts per day on each platform. Ensure that the videos are unique and not following a cookie cutter template so we do not get flagged by the platforms for mass produced AI content."
- [stated] "For new videos, study what is going viral in our niche and craft videos based on that." "Use the videos already produced in the queue first and then start producing new videos." "Develop a skill so the scripts sound human and are structured on how the most viral videos succeed in this niche." "Consistently monitor video performance and learn from each video." "Schedule the 3 video releases each day based on when it will give use the best performance."
- Supersedes the Oct 29 step-up plan (one a day, then two on TikTok and YouTube, then three).
- Built: six formats with their own bands and a rotation rule (video/studio/_shared/formats.md, anim.py variety), the viral-script skill, research/PERFORMANCE.md (daily numbers read, diagnosis), slots in video/config.json "posting" (11:37 am, 4:41 pm, 8:13 pm Central; evidence research/runs/2026-10-30-cadence.md), make while fewer than 9 wait, CONSTITUTION 2 amendment.
- Open for Todd: push access for the scheduled runs (blocked Oct 30, 7:46 am run); ElevenLabs credits (about 15,781 left, 3 a day uses about 23,000 a week).

## Video posting: scheduled runs and AI labels, 12:06 to 12:36 pm (live chat)
- [stated] Todd, 12:06 pm: "please get this fixed ASAP and run a test. So the first to see if the lunch video can post everywhere."
- Cause found: every post that worked ran in a live chat linked to Todd's PC; scheduled runs start in the cloud and cannot reach Claude in Chrome unless the task requires his computer. Todd turned on "Require this computer" on the three studio post tasks (12:10 pm). The fired lunch test then reached the PC but had no add_repo tool and got a 403 on push, so it held.
- Test done in the live chat instead: markup-margin posted to Instagram, TikTok, the Facebook Page and YouTube (links in video/studio/queue.json).
- [stated] Todd, 12:22 pm: "why are we adding the AI label if it only applies to photo realistic images? We are using retro gaming graphics."
- [stated] Todd, 12:36 pm: "off for all future posts"
- So: AI labels off on every platform (POSTING.md, _shared/captions.md, _shared/voice.md); YouTube's AI-use question answered No, since none of its listed uses applies. The three post task prompts still say the label stays on; they change with Todd's approval on the linked computer.

## Video depth, scheduled-run fix and script voice, 1:29 to 4:01 pm (live chat)
- [stated] 1:29 pm: "Please rewrite the tasks to fix this" (scheduled PC runs could not push). Done: the three PC post tasks post only and write each post to the scoreboard post log (ArtifactData `videoposts`); new cloud task "PNF video studio: record and make" (12:33, 5:33, 9:33 pm) commits the log and does all making (POSTING.md). Test run posted close-rate to all four (Instagram, TikTok, Facebook, YouTube).
- 3:37 pm: markup-margin showed square on Instagram (posted from a live chat with a 1:1 crop). POSTING.md now requires crop "Original" and a JS tall-preview check.
- [stated] 3:43 pm: "I feel like these videos aren't really deep enough... why aren't we doing more videos about in depth about how, you know, tradespeople can gather leads by doing X, Y, and Z, or how they can implement AI into their businesses". Research: video/studio/research/topics-2026-10-30.md.
- [stated] 4:01 pm: "go with your recommendation on everything. Drive this hard, and let's get real good videos out." Applied: review-replies, price-raise, receptionist-myth, after-hours-reply and notes-to-quote held (`anim.py hold`); IDEAS.md Depth bank on top; new formats playbook (3-part series) and case (70 to 92 s); script rules: no soft or staging tags, 2 tags a script, no "about" before an exact number (`anim.py script` checks); voice settings stability 0.7, similarity 0.7.
