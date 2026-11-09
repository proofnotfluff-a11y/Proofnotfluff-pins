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

Honesty in every format: a fix-this example is labeled "Example" on screen and is ours, never a real customer's words; a
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
- **Match the source** (Todd, live chat, Nov 8, 2026, 8:25 pm: "let's not keep strict rules or a standard template. We need to experiment to see what works."): brief.md `- **Match:** source` and `- **Source length:** N s` make a proven lesson take its source's structure: length within 20% (plus the end card), beat order, voice or none, answer or none. Off for it: the send card and gate, the hard hook, the 50 to 65 s band, the opening rotation, the 3 new sets. Kept: facts, EXAMPLE tags, the copy check, our own words and art. Only what we cannot copy changes (their footage and words). Where our pipeline forces a change (every picture is timed to a voice), say so in brief.md.
- **Act it out, once** (Todd, video-lab chat, Nov 8, 2026, decision 3: "Yes, build it, test on 1 lesson"): the next
  proven lesson made from a two-person money row (a customer who won't pay, a lowball buyer: `nextlane` pick order) plays
  the source's conflict as a scene with `k.client` facing the viewer as if the viewer is the tech or the seller (her
  lines in bubbles, EXAMPLE), then Snow brings the fix and the send card, and the last line asks the viewer what they
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

