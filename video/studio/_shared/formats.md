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
- A new lesson is not the same format as the lesson before it in line, and no format fills more than 2 of the 6 lessons
  around it. At 3 a day: no format twice in a posting day.
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

Honesty in every format: a fix-this example is labeled "Example" on screen and is ours, never a real customer's words; a
scenario is told as "picture this" and never as something that happened; every number still comes from facts.json.

## What else must change from lesson to lesson (the build checks these, the design gate judges them)
- Opening frame: never the lesson before's composition (set, camera distance, who is on screen).
- On-screen text style follows the format (board math, split screen, phone screen, myth stamp, counter), not one style for all.
- Tune: `anim.py tunes` (already a rule). Pace: quick-math runs fast (185 to 195 wpm), scenario calm (160 to 170).
- End card: the same lockup is fine (YouTube allows a shared intro and outro when the body differs); the send line names a
  different role each time.
