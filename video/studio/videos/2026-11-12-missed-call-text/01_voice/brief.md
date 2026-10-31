# Brief: The missed-call text, part 1 of 3: the words

Depth bank #2, part 1 (research/IDEAS.md; research/topics-2026-10-30.md, lesson 2: P1 the text, P2 turn it on, P3
register the number), planned Oct 31, 2026 in the scheduled morning make run. Source read Oct 31, 2026 (Central):
Twilio's "How long can a message be?" docs page; every line in facts.json quoted from the page that day.

- **Format:** playbook (_shared/formats.md: 40 to 58 s, 100 to 150 words; one part of a 3-part setup, "Part 1 of 3" on
  screen in the first 3 s, the step, the exact thing to copy on screen and held, the check that it worked, the button
  naming the next part).
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** a solo or small-crew plumber, HVAC tech or electrician who misses calls on jobs and is about to set up a
  missed-call text-back.
- **The one idea:** your missed-call text is three short parts and fits one plain text. (13 words)
- **Do this week (on screen, held):** write the text: who you are, sorry I missed your call, one question that books it;
  count it under 160 characters, no emoji, no curly quotes.
- **Shape:** hook (the tape measure out to 160: the text's whole budget) -> part 1 of 3, the usual way (a polite
  paragraph, no name, no question: nobody answers it) -> the fix (three parts, each lands as a slot; then the exact
  text, EXAMPLE, held on a big card with its count, 102 of 160) -> proof (Twilio's table: plain 160, with an emoji or
  curly quotes 70; past that it splits and Twilio bills each piece) -> button (count yours before part two turns it on;
  the rule echoes "a hundred sixty").
- **Hook pattern:** object-number
- **Treatment:** before-after
- **Example:** sam-plumber-text-102
- **Music:** bounce (free next to its neighbour in line; `anim.py tunes`)
- **Metaphor:** a tape measure for the character budget (a trade object every viewer owns); it earns its place because
  the lesson is a length check.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** Twilio's limits as its own table states them (GSM-7 160, UCS-2 70) on a high-score table, the source
  tag "Twilio docs: How long can a message be?" on screen while it is said.
- **Worlds (_shared/sets.md):** our own tape measure on a workbench (hook and button), `street` (the usual paragraph, typed
  between jobs), `register` (the three parts ring up to 102), our own big text card with a character counter (the copy), `scores` (the
  limits). None used by the lesson before it in line (lsa-missed-calls: its own night street, gauge, chat, flaps, versus).
- **End card send line:** "Send this to whoever answers your phones." (SCENE.sendLine)
- **Asked by owners:** thin. No owner forum thread from the last 90 days surfaced on public search (Reddit refused in the
  Oct 30 research run; contractor forum searches on Oct 31 returned vendor pages only). Signs it is asked now: trade
  marketing pages written for owners this fall, e.g. "Why Plumbers and HVAC Companies Lose Calls After Hours", Copper
  Springs Digital, Oct 14, 2026, https://copperspringsdigital.com/2026/10/14/why-plumbers-and-hvac-companies-lose-calls-after-hours/ ;
  "What should a contractor missed-call text say?", https://www.shiftflow.app/playbook/contractor-missed-call-text-back-templates ;
  and the research run's pick (topics-2026-10-30.md #2).
- **Model videos:** watched Oct 31 with the watch-video skill (Gemini; view counts not readable from here, so not
  ranked by views). (1) https://www.youtube.com/watch?v=TQKoy70dkDk , "Setting up Missed Call Text Back for your
  business!" (answer: video/watch/answers/2026-10-31-missed-text-a-r2.md): opens on a desk shot and the title, then a
  settings walkthrough; its default text is the business name, "we just missed your call", "how can I help?". What we
  take: the three slots are right but "how can I help?" books nothing, so ours asks what needs fixing and when. (2)
  https://www.youtube.com/watch?v=HXgkxiQ1f4I , "How To Set Up the Missed Call Text Back Feature" (answer: ...-b-r2.md):
  a 6 s logo intro, a minute of why, then the setting; it warns not to put the caller's first name in the text, since
  a first-time caller has no name on file. What we take: open on the problem, not a logo, and keep the caller's name
  out (ours names the owner, not the caller). A third (oS-NwdP3tdc) failed twice on Gemini 503. Our words only.
- **Trust notes:** 160 and 70 are Twilio's single-segment limits for GSM-7 and UCS-2; an emoji or a curly quote switches
  the text to UCS-2 (the page). "Twilio splits it in two and bills both" is said of our 102-character example with an
  emoji (102 + 2 units over 70, 67 a segment: 2 segments; the page bills per segment). Phones put the pieces back
  together (the page says re-assembled), so we never say the customer sees two texts. Nothing about other apps' prices.
  The plumber Sam and the text are ours (EXAMPLE on screen). No percent, no claim that text-back wins jobs.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| One plain text holds 160 characters | Twilio docs, How long can a message be?, read Oct 31, 2026 | https://www.twilio.com/docs/glossary/what-sms-character-limit |
| One emoji drops the limit to 70 | same (UCS-2 switch; 70 per single segment) | same |
| Curly quotes do it too | same (curly quotation marks are UCS-2; 160 to 70) | same |
| Past that, Twilio splits it and bills each piece | same (split into 67-character segments; bills per segment) | same |
| The example text, 102 characters (who 29, sorry 26, ask 47), 3 parts; part 1 of 3, next part 2 | ours (example, labeled; length counted in code) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-12-missed-call-text/01_voice/facts.json", "numbers": {
 "plain": {"path": "twilio.gsm7Chars", "shown": "160"},
 "emoji": {"path": "twilio.ucs2Chars", "shown": "70"},
 "len": {"path": "example.textLength", "shown": "102"},
 "parts": {"path": "example.partCount", "shown": "3"},
 "part": {"path": "example.partNo", "shown": "1"},
 "series": {"path": "example.series", "shown": "3"},
 "segs": {"path": "example.withEmojiSegments", "shown": "2"},
 "next": {"path": "example.nextPart", "shown": "2"},
 "who": {"path": "example.whoLen", "shown": "29"},
 "sorry": {"path": "example.sorryLen", "shown": "26"},
 "ask": {"path": "example.askLen", "shown": "47"}
}}
```
