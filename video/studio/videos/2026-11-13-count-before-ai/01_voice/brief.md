# Brief: Do you need an AI receptionist? Part 1 of 2: the count

Depth bank #3 (research/IDEAS.md; research/topics-2026-10-30.md, lesson 3: count missed calls 2 weeks, value one missed
job, then trial text-back vs a person vs AI side by side), as a playbook in two parts: part 1 the count and the math,
part 2 the side-by-side trial. Planned Oct 31, 2026 in the scheduled lunch make run (cloud). Every number is ours, a
worked example labeled EXAMPLE on screen (facts.json); no outside study or percentage is used.

- **Format:** playbook (_shared/formats.md: 40 to 58 s, 100 to 150 words; "Part 1 of 2" on screen in the first 3 s, the
  step, the exact thing to copy on screen and held, the check, the button naming the next part).
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** a solo or small-crew plumber, HVAC tech or electrician who misses calls on jobs and has an AI
  receptionist demo or quote in hand.
- **The one idea:** count your missed calls and what they're worth before you buy anything to answer them. (15 words)
- **Do this week (on screen, held):** for two weeks, mark every missed call on a calendar and circle the real jobs; then
  the board: real jobs x what you clear a job = what they're worth; hold that next to the monthly price on the quote.
- **Shape:** hook (a wall calendar, two weeks, 14 red X's; "Need an AI receptionist?") -> part 1 of 2, the usual way (the
  demo sounded great, so sign; but nobody knows what the calls are worth) -> the step (two weeks of marks on the
  calendar, 4 of the 14 circled as real jobs) -> the board (4 x $350 = $1,400 in two weeks, call it $2,800 a month,
  EXAMPLE) -> the check (that number next to the quote's monthly price: bigger price, it can't pay for itself yet;
  smaller, part 2 tries three options side by side) -> button (count the missed calls before you buy; echoes "missed
  calls").
- **Hook pattern:** problem-question
- **Treatment:** math-board
- **Example:** count-14-missed-4-jobs-350
- **Music:** quest (free next to its neighbour in line; `anim.py tunes`)
- **Metaphor:** none. The real objects: a wall calendar with marks, a chalk math board, a quote sheet.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** none outside ours; the calendar, the board and the quote are our own example (EXAMPLE on screen). No
  vendor, product or price is named or shown.
- **Worlds (_shared/sets.md):** `calendar` (the hook's two weeks and the step), our own office wall with a
  ringing desk phone and a demo screen (the usual way), our own chalk math board (the board), `levelup`-free close: the
  quote sheet on a clipboard beside the hero number (the check), `inventory` of three options greyed out as the next
  part (button). None used by the lesson before it in line (lsa-missed-calls: chat, flaps, gauge, versus).
- **End card send line:** "Send this to whoever signs the software bills." (SCENE.sendLine)
- **Asked by owners:** thin, like the lesson before. No owner forum thread from the last 90 days surfaced on public
  search (Reddit refused in the Oct 30 research run; searches on Oct 31 for contractor forum threads on AI receptionists
  returned vendor pages and software listings only). Signs it is asked now: pages written for owners this fall, e.g.
  "How an AI receptionist for contractors helps plumbers and HVAC shops stop missing calls", Finger Lakes 1, Sep 28,
  2026, https://www.fingerlakes1.com/2026/09/28/how-an-ai-receptionist-for-contractors-helps-plumbers-and-hvac-shops-stop-missing-calls/ ;
  YouTube's 2026 buyer guides for contractors (below); and the research run's pick (topics-2026-10-30.md #3).
- **Model videos:** watched Oct 31 with the watch-video skill (Gemini; view counts not readable from here, so not ranked
  by views; all three are vendor or buyer-guide channels, no owner-made one surfaced). (1)
  https://www.youtube.com/watch?v=2oo0agOyUJI , "9 BEST AI Receptionists for Contractors in 2026" (answer:
  video/watch/answers/2026-10-31-ai-recep-b.md): opens on a moment (on a ladder, phone buzzing), then a 9-tool rundown;
  its buy rule is a call volume of 20 to 30 a day, asserted, not shown. What we take: open on the owner's own moment and
  replace someone else's threshold with the owner's own count. (2) https://www.youtube.com/watch?v=NMxjyvuUSnw , "Best AI
  Receptionists for HVAC Companies (2026): 7 Compared" (answer: ...-c.md): opens on a Friday-night call nobody answers,
  compares seven by published info, ends on "test the ugly calls". What we take: the side-by-side test is our part 2;
  part 1 stays the math no tool list gives. (3) https://www.youtube.com/watch?v=zIufNTXjBHA , a vendor case study (answer:
  ...-a.md): a COO's story, no steps, no prices, ends on a demo ask. What we take: nothing to copy; it shows the gap (no
  owner is told how to decide). Our words only.
- **Trust notes:** the 14, 4, $350, $1,400 and $2,800 are ours (EXAMPLE on screen; 4 x 350 = 1,400 and 1,400 x 2 =
  2,800 checked in code; "call it" because a month runs a little over four weeks). "It can't pay for itself yet" is
  arithmetic: a monthly price bigger than what the missed jobs are worth a month is not paid back by those jobs. No
  claim that AI receptionists work or don't, no vendor named, no price for any product.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Fourteen missed calls in two weeks; four were real jobs; three fifty cleared a job | ours (example, labeled) | n/a |
| Fourteen hundred bucks in two weeks; call it twenty-eight hundred a month | ours (4 x 350; x 2, rounded) | n/a |
| Part one of two; part two tries three options side by side | ours (the series plan, topics-2026-10-30.md #3) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-13-count-before-ai/01_voice/facts.json", "numbers": {
 "missed": {"path": "example.missedCalls", "shown": "14"},
 "weeks": {"path": "example.countWeeks", "shown": "2"},
 "days": {"path": "example.countDays", "shown": "14"},
 "jobs": {"path": "example.realJobs", "shown": "4"},
 "clear": {"path": "example.clearPerJob", "shown": "$350"},
 "two": {"path": "example.twoWeekValue", "shown": "$1,400"},
 "month": {"path": "example.monthValue", "shown": "$2,800"},
 "part": {"path": "example.partNo", "shown": "1"},
 "series": {"path": "example.series", "shown": "2"},
 "next": {"path": "example.nextPart", "shown": "2"},
 "opts": {"path": "example.nextPartOptions", "shown": "3"}
}}
```
