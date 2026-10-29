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
- Close: one line that tells them where to look ("See your own neighborhood free at proofnotfluff dot com slash rats.").

## The hook (research run 2026-10-28-viral)
- The first 3 seconds decide it (Instagram's skip rate). Spoken hook: 9 to 12 words, said by 3.6 s (`anim.py hook`; 9 words
  take about 3.3 s at our fastest natural pace, so keep it to short words and one breath, and open on the stake). On-screen hook: 5 to 8 words, up in the
  first second, held 2.5 to 4 s, inside the safe area (not the top 14% or bottom 35% of the frame).
- Patterns that work: a question about their own number, a value promise ("One text that..."), "If you..., watch this",
  a real customer question, a myth with a sourced bust, a top shops vs everyone else gap. The source rides on screen.
- Views are not leads: speak to owners who can buy, and keep the host and a scene on screen (Instagram holds back
  Reels that are mostly text).

## The lesson shape and the 12-point check (research/runs/2026-10-28-script-playbook.md)
Template: hook (0 to 3 s, 9 to 12 words, "you", a stake, a promise) / stakes (a sourced number by 12 s) / teach (one idea,
the why) / artifact (the exact text, formula or line, shown and held 3 s or more) / turn ("Here's the part people skip",
between 55% and 75% of the runtime) / close (the rule in one line, a send line naming a role, last words echo the hook).
45 s = 120 to 145 words, 60 s = 160 to 195, 75 s = 200 to 240; the payoff is complete by 70% of the runtime.
The script gate scores the playbook's 12 points PASS or FAIL; a lesson goes to voice only on 12 of 12. Segments that
recur: The Text, Run the Numbers, Proof Check, Quote Clinic. No like, follow, tag or "comment YES" asks.

## Pace
- Target 160 to 195 words a minute per take (a Reel runs a little quicker than a lesson).
- Under 150: rewrite the take as talk. Over 200: give it a landing beat (a short sentence or `[short pause]`), re-roll.
- The whole lesson runs 45 to 75 seconds, end card included, so the last word lands by 72 s (IMPROVE 00c; Todd's yes Oct 29,
  10:26 am, "get this fixed today"; it replaces the Oct 28 45 to 90 s). `lint` and `check` fail anything longer.

## Rules that never bend
- A count is complaints to 311, never rats found. No building, block, business or person named. Nothing sells pest control.
- No AI voice line in the caption (Todd, Oct 29); the platform AI labels stay on.
