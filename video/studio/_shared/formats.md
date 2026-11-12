# Formats: six skeletons, so no two days look alike

Todd, live chat, Oct 30, 2026: "I want to switch to 3 posts per day on each platform. Ensure that the videos are unique and
not following a cookie cutter template so we do not get flagged by the platforms for mass produced AI content."

Why this file exists: by Oct 30 every queued lesson was the same skeleton (Lead Clinic, five beats, 40 to 50 s, same
opening rhythm, same end). Hook patterns, tunes and sets already rotate (`anim.py variety`), but the shape did not.
YouTube's inauthentic content policy names "templated storylines" and "AI-generated content made with generic or
unoriginal templates" (support.google.com/youtube/answer/1311392). What keeps us clear is real variety in what the
viewer sees and hears: a different shape, length, opening and payoff, each built on its own real example.

## The rule (code: `anim.py variety`, `format_rotation_problems`)
- brief.md names one format: `- **Format:** <name>`. Lessons gated before Oct 30 say `v2` (read as clinic) and keep their place.
- A new lesson is not the same format as the lesson before it in line, no format twice in the last 4 in line (one
  posting day at 4 a day) and no format in more than 2 of the last 8 (Todd, Oct 31, 2026, 11:58 am: "put measures in
  place to mitigate those risks as much as possible").
- Also checked by `anim.py variety` (same date): no set piece from either of the two lessons before; the first 3 words of
  the Instagram and TikTok captions and the YouTube title differ from the last 4 posted lessons and the queue.
- Each format has its own length and word band (`check` and `script` hold them). All keep the v2 script rules in
  `_shared/voice.md`: open on a moment, nothing after the answer, the last line echoes the hook.

## The six

| Format | Length | Words | Beats | Best for |
|---|---|---|---|---|
| clinic | 40 to 55 s | 100 to 135 | drop-in, play it out, the fix, proof, button | a line to say to a customer |
| quick-math | 20 to 34 s | 45 to 80 | the number problem (0 to 3 s), the answer most give (3 to 8 s), the right math built on the board (8 to 24 s), the rule that loops back to the opening line | pricing, margin, cost of a missed call |
| fix-this | 25 to 42 s | 60 to 100 | "What's wrong with this?" over a real-looking text, quote or reply (0 to 3 s), read it (3 to 10 s), a beat to guess (10 to 13 s), the rewrite word for word (13 to 32 s), the button | texts, quote follow-ups, review replies, voicemail |
| two-shops | 35 to 52 s | 85 to 125 | same call to two shops side by side (0 to 3 s), each path step by step on a split screen, the scoreboard, the one difference in one line | speed, follow-up, booking on the call |
| myth-three | 30 to 48 s | 75 to 115 | the claim most owners believe (0 to 3 s), three fast myth then fact cards, one source each, the rule | habits backed by trade data |
| scenario | 42 to 62 s | 110 to 160 | "Picture this" moment, the small choice, what it costs over a month (counter on screen), the turn, the lesson line | a habit whose cost builds up |

| playbook | 40 to 58 s | 100 to 150 | one setup step, standing alone (no part numbers, Oct 31): the step, the exact thing to copy on screen and held (text, setting, prompt), the check that it worked, the button naming the next part | missed-call text-back, follow-up, anything with setup steps |
| case | 70 to 92 s | 180 to 245 | one real setup end to end: before (the problem with its number), the setup step by step, the cost, after (the number), the rule | a real owner's setup we can source |
| dispatch | 45 to 70 s | 115 to 180 | the lede with its document on screen (0 to 3 s), the nut (by 8 s), two or three receipts with source tags, the other side, the setup card held, the kicker echoing the lede (_shared/investigative.md) | a documented story from research/STORIES.md (AI lane; hook pattern receipt) |

| story | 40 to 70 s, aim 50 to 65 | 110 to 175 (a guide) | the story desk's story.md told whole: an opening from storycraft.md, the setup, the problem with its proof, the turn, the send card (before half the runtime), the cost, the kicker | every new-line lesson from Nov 5, 2026 (REBUILD.md); rotates on its brief.md Shape line |

| proven | 50 to 65 s (hard) | 120 to 170 (a guide) | our own version of a research/PROVEN.md pattern: opens on the moment, the send card before half, one checked number, the rule | brief.md `- **Format:** proven`, `- **Source:** <link>` ("Proven" below) |

| short | 18 to 35 s | 45 to 95 (a guide) | one fix from a queued story lesson: the moment in one line, the send card (the fix, held 2.5 s, before half), the check that it worked, the button | brief.md `- **Derived from:** <parent slug>` |

Relaxed for the new line (Todd, live chat, Nov 2, 2026, 8:49 pm, PRINCIPLES.md: "We can elaborate more and relax
restrictions on number of words"; REBUILD.md): for a story lesson the word band, the spoken hook's length, the drop-in rules
and the echo are guides printed as NOTE by `anim.py script`, `hook` and `lint`; the retell and read-aloud gates judge the
story. Length stays a hard band (70 s ceiling from Nov 7; 90 s before) and every honesty, voice-markup and safe-area rule
stays an error. The 50 to 65 s aim is a NOTE (`anim.py hook` and `lint`).

## The send moment and the shorter middle (Todd, live chat, Nov 7, 2026, 9:27 am: "Write the next prompt to make adjustments and fix so the next video improves")
Why: after-hours-robot (IG skip 26%) and lsa-missed-calls (skip 29%) held viewers and both stalled near 1,280 views with 0
or 1 share and 0 follows; Instagram weighs sends per reach most for reach beyond followers. after-hours-robot ran 87.6 s
and was watched 29 s (33%). Both fixes apply to every story lesson and short dated from 2026-11-19 on (`anim.py` SEND_FROM);
queued lessons keep their pins (lsa-max-bid, 66.2 s of voice, stays).
- **One send moment.** One forwardable thing on screen, made for a named person in the owner's shop (whoever answers the
  phones, the office manager, a partner): the exact text to send back, the call script, the setting to change. brief.md
  carries `- **Send:** <who it goes to>: <the thing on screen>`. The end card's send line names that same person, word for
  word ("Send this to whoever answers the phones."). cues.md marks the cue where the card goes up with `[send]`.
- **Held to screenshot.** The card sits still 2.5 s or more with no motion over it (no snow, cursor or slide across it).
  From 2026-11-29 (Todd, live chat, Nov 9, 2026, 7:33 am, "Recs", call 5: damage-or-not's card sat 13.5 s while the voice read it, and the stranger left there):
  it builds line by line as each line is spoken (`k.sendCard` linesOn), holds about 3 s once full (lint: 2.5 to 4.0 s
  still), then the video moves on, and the end card shows it again (`SCENE.endSend`) for a screenshot.
- **Payoff early.** The send cue starts before half the runtime (end card included). What follows it is the why and the
  kicker, kept short.
- **Code checks** (`anim.py sendcheck`, `lint`, `ready`, planted cases in `anim.py selftest`): the Send line and its two
  parts, the person is one role (never a group or the viewer), the end card names the person, exactly one `[send]` cue
  running 2.5 s or more, the measured still hold, before halfway, and after the send gate that its reviewer, who never saw
  the brief, named the same person and thing from the video alone (prompts/send.md).

Depth (Todd, Oct 30, 2026, 4:01 pm: "Drive this hard, and let's get real good videos out"; research/topics-2026-10-30.md):
every lesson hands the owner something to do this week: the exact words, setting, prompt or steps, on screen. A definition
plus another company's percentage is not a lesson.

No series (Todd, live chat, Oct 31, 2026, 7:29 pm: "we probably shouldn't do multi part videos if we are not organized to
do it"). Every lesson stands alone: no "Part X of Y" and no promise of a next part on screen, in the voice or in the
captions. A playbook lesson teaches one setup step end to end on its own. The one exception is the part 2 that
count-before-ai already promised (research/IDEAS.md "Owed first").

Honesty in every format: a made-up example is said once (the voice sets it up, "Say a homeowner tells you...", or one small
MADE-UP EXAMPLE line on its first frame; Todd, live chat, Nov 9, 2026, 7:33 am, "Recs", call 2), an EXAMPLE tag sits only beside a made-up number, and it is ours,
never a real customer's words; a
scenario is told as "picture this" and never as something that happened; every number still comes from facts.json.

## What else must change from lesson to lesson (the build checks these, the design gate judges them)
- Opening frame: never the lesson before's composition (set, camera distance, who is on screen).
- On-screen text style follows the format (board math, split screen, phone screen, myth stamp, counter), not one style for all.
- Tune: `anim.py tunes` (already a rule). Pace: quick-math runs fast (185 to 195 wpm), scenario calm (160 to 170).
- End card: the same lockup is fine (YouTube allows a shared intro and outro when the body differs); the send line names a
  different role each time.

## Proven (Todd, live chat, Nov 7, 2026, 12:08 pm: "Go", to the proven idea lane)
Todd, 11:58 am: "We can find what is actually working out there and create our own videos based on that." Why: a reported
story took up to 28 script rounds a lesson; faceless channels grow by making their own version of what already works.
Ideas and formats aren't owned; words, footage and art are. Our edge is the version: made for trade owners, one checked
number, our pixel style, the send moment.
- **Every new lesson is proven** (Todd, live chat, Nov 8, 2026: "Going forward all videos should use this method."); no story lessons.
- **Viewer check** (Todd, live chat, Nov 8, 2026, 9:51 pm: "When ideating these videos, take a step back and ask if it makes sense from the viewers perspective. Find viral videos that will work in the context of a faceless animated videos that we are creating"): before a row is picked, name what made it work. It must be something we can draw or animate (a number reveal, math on a board, a list, a line to say, an acted conflict with k.client); real footage as evidence or a real person's face or story is not. Then watch our version in your head as a stranger scrolling: what do they get? brief.md `- **Key ingredient:**` and `- **Viewer check:**`, required from lessons dated 2026-11-29 (copycheck and ready). Why: hail-or-wear copied row 3's structure, but a drawn roof gave the viewer nothing real to judge; Todd: "I watched the video but I don't get it."
- **Match the source** (Todd, live chat, Nov 8, 2026, 8:25 pm: "let's not keep strict rules or a standard template. We need to experiment to see what works."): brief.md `- **Match:** source` and `- **Source length:** N s` make a proven lesson take its source's structure: length within 20% (plus the end card), beat order, voice or none, answer or none. Off for it: the send card and gate, the hard hook, the 50 to 65 s band, the opening rotation, the 3 new sets (a minimum gone for every lesson from 2026-11-29). Kept: facts, the made-up label (said once, call 2), the copy check, our own words and art. Only what we cannot copy changes (their footage and words). Where our pipeline forces a change (every picture is timed to a voice), say so in brief.md.
- **Act it out, once** (Todd, video-lab chat, Nov 8, 2026, decision 3: "Yes, build it, test on 1 lesson"): the next
  proven lesson made from a two-person money row (a customer who won't pay, a lowball buyer: `nextlane` pick order) plays
  the source's conflict as a scene with `k.client` facing the viewer as if the viewer is the tech or the seller (her
  lines in bubbles, the scene set up once as made up), then Snow brings the fix and the send card, and the last line asks the viewer what they
  would do. One lesson only; `anim.py cohort` marks it, and the Nov 14 read compares it with the narrated ones.
- **The hook is hard** for proven lessons dated 2026-11-26 on (Todd, video-lab chat, Nov 8, 2026, decision 2): the source's conflict in 5 to 8 words on frame 0, spoken in 12 words or fewer by 3.6 s (_shared/hooks.md).
- **Pick** a row of research/PROVEN.md at the bar, 100,000 views or more and 5x its channel's typical (Todd, live chat,
  Nov 7, 2026, 7:17 pm: "We need to change this standard to 100K+ views"; code fails a brief under it, `nextlane`
  says story when none is left), that has a sourceprint (research/proven/<id>.json). A row with no print: queue a watch-video job with `"sourceprint": true` (the workflow hashes Gemini's
  transcript and commits no words; Todd, Nov 7, 2:45 pm). Topic first (Todd, video-lab chat, Nov 8, 2026: "Yes, pick by topic first"): take the first row `anim.py nextlane` prints in its pick order, money between two people or our phone topics before any other row at the bar, then the most views and build it the next run, or in a live chat read the words
  into a file under data/ and run `anim.py sourceprint <link> <file> <how>`; never commit the source's words.
- **Refresh** (tools/yt_outliers.py, Sundays, official YouTube Data API): research/outliers.json lists every Short at
  5x its channel's typical and 100,000 views or more. When every row is used, add the top unbanked outlier that fits (a business lesson an owner
  can act on; no ad, meme or skit about a real person) as a PROVEN.md row, labeled by business name or a plain
  description, and queue its sourceprint job.
- **brief.md**: `- **Format:** proven`, `- **Source:** <link>`, `- **Started:** <YYYY-MM-DD HH:MM Central>`, a Shape
  (rotation reads it), Send, Hook pattern, Treatment, Example, Music, and the claims table. No Story or Test score, no
  second-source bar.
- **Script** (viral-script SKILL, "A proven lesson"): our own words to a trade owner; the pattern's topic and move, never
  its lines; an opening worded differently from the source's; it opens on the moment (storycraft.md, Openings); one number,
  re-read on its own source page today (facts.json, facts gate); never the source's own numbers or results unless we read
  their source; the send moment ("The send moment" above); 50 to 65 s with the end card.
- **Copy check** (`anim.py copycheck`, gate `copy`; `ready` runs it again): fails on any run of 6 or more words shared with
  the source, 15% or more of our 3-word runs in the source or 25% or more of its in ours, an opening sharing a 4-word run
  or a third of its 3-word runs with the source's first 25 words, or a caption with a 6-word run. Planted cases in
  `anim.py selftest`. Never edit it to pass: rewrite the line.
- **Gates** (`anim.py` PROVEN_GATES): code QA, facts, facts on captions, render critic, send, design, copy; every one a
  fresh opus reviewer except copy, which is code. `anim.py readcheck` still runs.
- **The test** (video/config.json laneTest; `anim.py nextlane`): Nov 7 to 14, 2 of every 3 new lessons from this lane and
  1 from the story lane, counted by brief.md Started lines (shorts don't count; when the lane due has nothing to make, take
  the other and say so). Verdict Nov 14 beside the shorts verdict, on the deep reads: median views at 48 h, sends (shares)
  per 1,000 reached, and follows per lesson, proven against story. Keep the lane that wins two of the three; tell Todd with
  the numbers. Fewer than 2 of either read by Nov 14: the verdict waits until 2 are.

## Short (Todd, live chat, Nov 7, 2026, 8:33 am: "Go", to the social engine audit's recommendation 3)
Why: one story lesson costs several runs, so 3 a day needs a second, cheaper post per story. A short is not a re-upload:
it is a new video that teaches the one thing an owner can do this week from the parent's story.
- Made only from a lesson already queued with every gate passed (its parent), by the same or a later studio run. One short
  per parent. Slug `<date>-<words>-short`; brief.md: `- **Format:** short`, `- **Derived from:** <parent slug>`, its own
  Hook pattern (never the parent's: `variety` fails it), Treatment and Example (it may share the parent's example).
- Its own script (45 to 95 words, a guide) and its own voice takes; its own cues and its own opening frame. It may reuse the
  parent's scenes, props and facts.json numbers, each number re-read for the short's own facts gate.
- Gates (`anim.py` SHORT_GATES): code QA, facts, facts on captions, render critic, send, design. The story gate drops (no
  arc to retell); `anim.py readcheck` still runs in code.
- Posting: queue order, never on its parent's first day and never sooner than 24 h after the parent went up (`anim.py
  next` skips it until then); at most one short in a posting day (rotation).
- The test: 7 days, verdict Nov 14 by the recorder. Keep shorts if their average watch as a share of length is at least
  the median of the story lessons posted the same week on TikTok and YouTube (the deep read), and their skip rate on
  Instagram is no worse. Otherwise stop making them and tell Todd with the numbers. Fewer than 3 shorts read by Nov 14:
  the verdict waits until 3 are.


## v4 (Todd, live chat, Nov 9, 2026, 2:11 pm: "Make all the necessary changes"; coo/constitution/video.md)
Every new lesson from 2026-11-30 on. Why: 80 posts earned 12,842 views and 1 share; owner lessons reach owners only; viewers
gave every lesson 3 to 29 s whatever its length; no gate score moved views (the audit, coo/DECISIONS-2026-11-09.md). A v4
video is a short story a stranger can judge, with the owner's rule as its payoff. The sections above bind only the
old-format lessons already made.

Four formats (brief.md `- **Format:**`), each a named show with a new case every time (never a series):
| Format | What the viewer sees | Payoff for the owner |
|---|---|---|
| `verdict` | a real dispute between a tradesperson and a customer, acted by the cast, ending on "you decide" | the rule that prevents it |
| `invoice` | a bill or quote built line by line: where the money goes | how to say the price so it sticks |
| `call` | a phone call as captions and two speakers, said once to be a reenactment | what to say or send |
| `case` | a real dispute with a public result (a ruling, a sentence, a refund, a fine), told in order, the result held for the end (rules: "Case" below) | the legal route that would have paid |

Pick the story (brief.md `- **Pull:**`, all three yes): two sides in conflict; a dollar figure; someone specific to send it
to. Then breadth: would a tech or a homeowner stop too? An owner-only lesson is a site page, not a video. Sources: a
publicly reported or publicly posted trade story, read that run (facts.json), told in our own words as the person's own
account ("he says"), no person or business named, the source named in every caption. A made-up or acted scene says so once.

The build (anim.py holds each line: `lint`, `check`, `ready`):
- 18 to 35 s, 45 to 95 spoken words (a note). Ends 1 s after the last word; no end card, no send card, no host, no level bar.
- Every word on screen is size 132 or larger (66 px caps; size 66 reads 33 px, which the first render critic failed as
  too small for a phone). The platform shows the handle, so the frame does not.
- scene.js sets `v4: true, host: false, endCard: false` and draws the whole frame. Words stay inside x 40 to 1040 and
  y 250 to 1170; the captions own y 1184 to 1382 (the player draws them: two or three big words, the spoken one lit);
  below y 1440 and the top 250 px belong to the platform. Right of x 930 is clear only above y 1040.
- Frame 0 is the fight: the stake in 2 to 8 words, as big as fits, the people in it close. The picture changes by 1 s and
  twice by 3 s. Close shots (waist up, faces between y 700 and 1100, plates above them) carry the story; one wide shot sets the place.
- cues.md marks one cue `[payoff]`: the outcome or the answer, by 40% of the runtime.
- No set of words stands unchanged over 4 s. Plain cuts only.
- The last line is a question that splits the room, then the send line (Level-ups below); the last frame shows both sides, each with its case.
- captions.json: line 1 the dilemma (under 100 characters), one question, a `Source:` line, 3 to 5 hashtags (2 to 3 on
  Facebook and YouTube); the YouTube title is the dilemma in 70 characters or fewer with a question or a dollar figure.
  AI label on for Instagram, Facebook and TikTok, off on YouTube (`V4_LABELS`).
- Start from `_templates/v4-verdict.scene.js` (the plate, stampPlate, yard and cast helpers): a new lesson changes the
  rows, the cue times and the place, not the machinery. Aim for one render.

Level-ups, Nov 11 (Todd, live chat, Nov 11, 2026, 4:26 pm: "Go with your recommendations on everything"; why and the bars: research/VIRALITY-2026-11.md "Adopted Nov 11"; the make run keeps or drops each one by its bar). Guides the script, the cues and the viewer gate hold; no lint error yet:
- Story pick, two more checks: two numbers that stand against each other; and a split (a stranger could fairly take either side: if nearly everyone takes one side it is a rant, not a verdict). brief.md `- **Send:**` names the sender, the receiver and why in one line.
- The first second: frame 0 stays a settled cover and shows the two numbers, or the number and the refusal. The first change lands by 0.6 s. The spoken hook is 8 words or fewer and ends by 2.5 s; the next sentence carries the detail.
- Two reveals: the answer still lands by 40% (`[payoff]`). The second best fact is held for a cue named `twist` that starts at 70% to 85% of the runtime, said aloud and shown. Every number on screen is spoken.
- The send line: after the closing question, one spoken line of 2 s or less says who to send it to, in the story's own words; the last frame labels the two sides as two kinds of people the viewer knows. The caption keeps its send line.

Case (Todd, live chat, Nov 12, 2026, 10:03 am: "can we make the necessary changes so we rectify our weaknesses?"; why: research/WATCH-2026-11-11.md, 8 watched faceless dispute winners against ours; bar and days: research/TEST-2026-11-23.md "Case test"). A `case` keeps every v4 line above except these, and anim.py holds the first three (`lint`, `selftest`):
- Length: 55 to 95 s, 120 to 240 spoken words, about 150 to 165 words a minute with a breath before the result.
- The result is held: the one cue marked `[payoff]` is the public result and starts at 60% of the runtime or later (the winners: 67% to 90%). The by-40% rule and the `twist` cue do not apply. Nothing before it gives the result away, on screen or in the caption's first line.
- A beat every few seconds: one cue for every 6 s on average and no stretch over 8 s between two cue starts. Each cue is a new shot, a close shot or a new place (`k.cut`, `k.cam`, `SCENE.rooms`), never the same frame with new words only.
- The story must have: a real dispute, a dollar figure, and a result a public source reports (court, police, a licensing board, the press quoting them). No result on the record means it is a verdict, not a case.
- The wrong comes first: frame 0 and the first sentence show what one side did to the other, with the two numbers. Then the story in order: what was agreed, what broke, what each side did, what the law did.
- One acted line a side, at most two a side: the narrator speaks as that person over a close shot, and the first one carries "Reenactment" on screen. Each line says in our own words what the source reports that side said or did; it adds no new claim and never reads as an exact quote.
- The owner's rule comes after the result, as what the legal route was (the lien, small claims, the notice), with its number from a source read that run.
- The end: the result, the rule in one sentence, one closing question that still splits the room (was it fair, who was more wrong), then the send line. The send line names someone a homeowner or a tech could send it to, not only an owner.
- Cues start from `_templates/v4-case-cues.md` (copy it over 03_cues/cues.md after `anim.py new`).

Gates, in order (prompts/README.md "v4"): facts on script.md before any voice; after the render: render critic, viewer,
then facts once more on the transcript, screen and captions. Two fix rounds a gate at most, then shelve it.
