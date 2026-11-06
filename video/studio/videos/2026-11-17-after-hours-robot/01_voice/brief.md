# Brief: The robot is a better voicemail (the first story lesson on the new line)

Made Nov 5, 2026 in the live build run with Todd (video/studio/REBUILD.md, Order of work step 1). From the first trade
pulse (research/pulse/2026-11-05.md, problems 2 and 3) through the story desk (00_story/story.md, story retell r0 FAIL on
one line, fixed). Preview only: nothing posts until Todd watches it and says so (video/config.json stop is true).

- **Lane:** ai
- **Test:** the new line itself: a story told whole (setup, problem, proof, turn, payoff) against the old squeezed formats.
- **Format:** story
- **Shape:** owners-words
- **Story:** 00_story/story.md
- **Message:** Put the AI receptionist on after hours, where it beats voicemail, and keep a person on the daytime phone.
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts (after Todd's word).
- **Audience:** the owner of a small trade shop (HVAC, plumbing, pest, tree work) who misses calls on the job and is being
  pitched AI receptionists, on a phone.
- **The one idea:** run the AI receptionist after hours, where it beats voicemail; keep a person on the daytime phone.
- **Hook pattern:** problem-question
- **Treatment:** story
- **Example:** jobber-forum-after-hours
- **Music:** night
- **Metaphor:** none (the beep is the comparison the story already carries: at night the robot is up against a beep).
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** the forum posts as paraphrase cards with their source tags (Jobber Community, the age), the survey
  number with its tag (ACHR News, Oct 20, 2026, 782 homeowners), Jobber's help page lines as a card ("read exactly as
  written", "$29 a month, 30 conversations") with its tag (Jobber help, updated Oct 28, 2026). No usernames, no business names.
- **Do this week (on screen, held):** the setup card, 4 steps, the greeting word for word (C3), held 4 s or more.
- **End card send line:** "Send this to whoever answers your phone after hours." (SCENE.sendLine)
- **Asked by owners:** Jobber Community, about Nov 4, 2026 (thread 9584) and about Oct 16, 2026 (thread 15510).
- **Model videos:** the gurus.md compare set (first pass Nov 5, 2026).

## Five openings (viral-script step 4; storycraft.md openings)
1. "Owners keep saying it: callers hang up on the robot." (owners' words, 10)
2. "Your AI receptionist works great. Just not at two in the afternoon." (the moment plus an open loop, 12) PICKED: a busy
   owner wonders "why not two?", and the kicker answers it with the same words.
3. "Only about a third of homeowners want a robot booking them." (receipt, 11)
4. "This week an owner asked if a robot should answer her phone." (owners' words, 12)
5. "At night, the robot only has to beat a beep." (result first, 10)

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| On Jobber's owner forum, owners say few callers stay once they hear it's AI | facts.json forum.rural (and treeService, backflow) | see facts.json |
| A tree service turned it off and went back to voicemail | facts.json forum.treeService | see facts.json |
| Only 36% of 782 homeowners comfortable with AI booking or basic questions; a trade magazine's publisher, this spring | facts.json survey | ACHR News, Oct 20, 2026 |
| One owner calls it a better voicemail: after hours, takes the details | facts.json forum.rural | Jobber Community |
| Jobber's help page recommends telling callers it's AI; reads the greeting exactly as written | facts.json jobber | Jobber help, updated Oct 28, 2026 |
| After-hours-only answering is set with your phone carrier | facts.json jobber.afterHoursOnly | Jobber help |
| $29 a month, 30 conversations (setup card only) | facts.json jobber | Jobber help |
| The roof, the two pm call, the no-heat test call, the greeting | ours (EXAMPLE) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-17-after-hours-robot/01_voice/facts.json", "numbers": {
 "survey36": {"path": "survey.comfortableBooking", "shown": "36%"},
 "survey782": {"path": "survey.homeowners", "shown": "782"},
 "addon": {"path": "jobber.addonMonthly", "shown": "$29"},
 "convos": {"path": "jobber.conversations", "shown": "30"}
}}
```
