# Voice: how scripts are written and spoken

**The voice:** Todd's own ElevenLabs voice clone (`W3pJy9ibur1FKUihVxzY`; Todd, Oct 28, 1:41 pm), made from his recording,
cleaned. Settings (`anim.py` VOICE_SETTINGS) lean steady and a touch warmer: "Just make me sound a bit smoother and more
confident" (Todd, Oct 28, 1:03 pm). Model: Eleven v4 (`eleven_v4`). The library voice Chris (`iP95p4xoKVk53GoZ742B`) stays
as the fallback (`speak --voice iP95p4xoKVk53GoZ742B`). Each platform's AI label is set when it posts (POSTING.md); the caption carries no AI voice line (Todd, Oct 29).

## Written as talk
- One paragraph is one take: 2 to 4 sentences, 15 to 25 seconds. A take that sounds off is re-rolled alone.
- Say it the way a person tells a friend something they just found out. Short sentences, contractions, one aside.
- One delivery tag where the energy changes, in square brackets at the start of the sentence it shapes:
  `[curious]`, `[leaning in]`, `[matter-of-fact]`, `[a little surprised]`, `[warmly]`, `[short pause]`, `[calm]`,
  `[confident]`, `[thoughtful]`, `[quickly]`, `[playful]`. At most two a take. Eleven v4 has no speed or style slider and no
  SSML pauses: pace is a writing job (short sentences, a period or `[short pause]` for a beat; never a dash).
  The voice acts the tag and does not say it; tags never carry a fact.
- One stressed word a paragraph at most, in capitals (`MORE than triple`).
- Numbers as they are said: "forty-five", "ten point two percent", "three one one". The brief holds the digits, and the
  facts gate checks the spoken form against them.
- Plain words, no hype, no em or en dashes, nothing the facts gate can't trace to the data file.
- Close (Lead Clinic v2): the last spoken line is the rule, in words that echo the hook. No spoken call to action; the send
  line rides on the end card and in the caption.

## Lead Clinic v2: the lesson format (Todd's yes, Oct 29, 2026, 12:14 pm: "Yes let's implement this immediately")
Why: research/viral-formats-2026-10.md. Of 13 spoken shorts with 1M+ views, none opened on a percentage, named a source
early or called out its audience; 10 stopped on the answer with no spoken call to action; 8 acted the lesson out; most ran
under 50 s. A lesson whose `brief.md` has the line `- **Format:** v2` follows this section, and `anim.py script`, `hook`,
`lint` and `check` hold it to it. Every new lesson is v2 (`_templates/brief.md`); lessons planned before Oct 29 keep the v1
rules at the end until they are rebuilt.

Five beats, 40 to 50 s with the end card, 100 to 135 spoken words, one take a beat:
1. **Drop-in** (0 to 3 s, 9 to 12 words): a moment on a real job, in the customer's own words or one object with a number.
   It sets the question the lesson answers. No percent, no source, no audience call-out ("Trade owners,"). The trade word
   sits inside the scene (homeowner, estimate, water heater), so the keyword is still said in the first seconds.
2. **Play it out** (3 to 12 s, 20 to 25 words): the usual way, acted by the cast, and what it costs.
3. **The fix** (12 to 26 s, 30 to 40 words): back to the moment; the right line, text or math, word for word, on screen and
   held 3 s or more.
4. **Proof** (26 to 34 s, 18 to 25 words): one sourced number in one or two sentences. The source rides on screen as a
   tag, and "Pattern, not proof." goes in the tag when the source is correlational (it is no longer said).
5. **Button** (34 to 42 s, 15 to 22 words): the rule in one line, echoing a word of the hook. The last spoken words.
Then the end card (3.1 s after the last word, the card up for the last 3.0 s): lockup, the site, and the send line from `SCENE.sendLine` ("Send this to whoever runs your
estimates.").

Hook formulas that fit (research/viral-formats-2026-10.md): the stuck moment ("The estimate's done. The homeowner says,
let me think about it."), two shops one winner, the object with a number, which would you pick, your move.
On-screen hook: 5 to 8 words up in the first second, held 2.5 to 4 s, inside the safe area (not the top 14% or bottom 35%).
Picture changes within 1 s and twice in the first 3 s; the host is on by 3 s (`anim.py hook`). Spoken hook said by 3.6 s.
Views are not leads: speak to owners who can buy, keep the host and a scene on screen.

The script check (`01_voice/script-check.md`, PASS or FAIL with the metric; 12 of 12 before voice):
1. Drop-in: 9 to 12 words, a trade noun or "you", no percent, no source name, no call-out, no greeting.
2. On-screen hook: 5 to 8 words, by 1.0 s, held 2.5 to 4.0 s, in the safe area.
3. One idea: brief.md states it in 15 words or fewer; every beat serves it.
4. Acted: beat 2 shows the usual way and its cost in the cast's actions, not explained to camera.
5. Facts: every number and named source in voice, screen and caption maps to facts.json; spoken form matches the digits.
6. Artifact: one exact line, text or formula spoken and on screen, held 3 s or more, done by 65% of the runtime.
7. Proof: one sourced number after the fix, the source tag on screen while it is said.
8. Length: 100 to 135 words; 40 to 50 s with the end card (55 s hard cap in `check`).
9. Talk test: a contraction and a "you" in most takes; no banned words (utilize, leverage, game-changer, unlock, secret,
   hack); no em or en dashes; no sentence over 20 words.
10. Voice markup: at most 2 tags a take, from the list above; at most 1 CAPS word a take; no digits, $, %, / or & in the voice.
11. No tail: no turn line ("Here's the part people skip"), no spoken "one honest note", no spoken send, save, like, follow
   or comment ask.
12. Button: the last sentence is the rule and repeats a word from the hook; `SCENE.sendLine` names a role.

## Variety across the queue (Todd, Oct 29, 2026, 3:56 pm: "Go with your recommendations for everything")
`brief.md` names its hook pattern, treatment and real example (`_templates/brief.md`). `anim.py variety SLUG` (run by `lint`
and `ready`): the example is the lesson's own; no other unposted lesson has the same hook pattern and treatment; the lessons
before and after it in line do not open on the same hook pattern. Pick a hook pattern that passes before the voice is made.
Music (Todd, Oct 29, 2026, 8:11 pm: "different tunes for each video"): a lesson's tune is not the tune of the lesson right
before or right after it in line (the last posted lesson, then the unposted queue). The tunes: classic, sunny, quest, night,
chase, bounce (`_shared/sound.md`), and a library bed counts as its own. The source of truth is cues.md's
`music: rooms <tune>` line (plain `music: rooms` is classic); until cues.md exists, brief.md's Music line stands in.
`anim.py tunes SLUG` names the free ones. Lessons pinned before the rule still post as they are; a rebuild picks a free tune.

## Pace
- Target 160 to 195 words a minute per take. Under 150: rewrite the take as talk. Over 200: give it a landing beat.
- v2 runs 40 to 50 s, end card included (`check` fails under 40 s or over 55 s).

## v1 (lessons planned before Oct 29, until rebuilt)
hook / stakes (a sourced number by 12 s) / teach / artifact / turn (between 55% and 75%) / close (rule, a send line naming
a role, last words echo the hook); 45 to 75 s, end card included (IMPROVE 00c); the 12-point check in
research/runs/2026-10-28-script-playbook.md 6b.

## Rules that never bend
- A count is complaints to 311, never rats found. No building, block, business or person named. Nothing sells pest control.
- No AI voice line in the caption (Todd, Oct 29); the platform AI labels stay on.
