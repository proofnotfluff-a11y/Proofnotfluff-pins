# Brief: Know your close rate

Lesson 8, segment Numbers Clinic. Planned Oct 28, 2026 from the topic bank's topic 4 and Brief 4 (research/runs/2026-10-28-topic-bank.md), the source page re-read the same day.

- **Where:** Instagram Reel, 9:16, about 71 s (a worked example earns the longer slot; 75 s cap, end card included), then TikTok, Facebook, YouTube Shorts.
- **Audience:** a trades or home-service owner (plumber, electrician, HVAC, roofer) who gives estimates and has never worked out a close rate.
- **The one idea:** close rate is jobs sold divided by estimates given; know yours, track it weekly. (15 words)
- **Shape:** hook ("Do you know your close rate? Here's the one-line math.", then the regional median close rates, 31% to 38%, ServiceTitan customers, May to July 2026) -> stakes (the top 25% by close rate: medians 70% to 73%; you can't close a gap you never measured) -> the artifact (close rate = jobs sold / estimates given, same month) -> the worked example (example: 40 estimates, 14 sold, 35%) -> the turn (ServiceTitan doesn't say how it counts a close, and its customers aren't every shop, so beat your own last month first) -> what to track weekly (every Friday: estimates given, jobs sold) -> close (the formula again, send line, "you'll know your close rate"). Oct 29 rebuild for the 75 s cap and the 3 s hook: the dollar close rate (dollars sold over dollars quoted) is cut, a second idea the lesson didn't need.
- **Metaphor:** none. The shop whiteboard carries the weekly habit.
- **Voice:** Todd's clone in `_shared/voice.md`.
- **Real screens:** the ServiceTitan medians as a range bar (31% to 38%) beside the top 25% range (70% to 73%), the source on screen while its number is; the formula card; a worked example card marked "example"; the Friday whiteboard with two rows (also the hook's close-up).
- **Close:** "Send this to whoever writes your estimates." Brand plate, send line.
- **Trust notes:** the medians are regional (31% Northeast to 38% West), for the most recent quarter (May to July 2026), over an aggregated sample of ServiceTitan customer accounts; the page says it is not representative of the whole trades industry: said in take 1 ("ServiceTitan's data on its own customers") and in the turn. The page does not define close rate, so the formula is ours, never "ServiceTitan calculates it as". The top 25% is ranked by close rate in each region (said so); no tactic is credited for their number and nothing claims cause. The 40 / 14 / 35% example is ours and labeled "example" on screen and in the voice.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Regional median close rates range from 31% in the Northeast to 38% in the West; May through July 2026; aggregated sample of ServiceTitan customer accounts, not representative of the whole trades industry | ServiceTitan, Trades Industry Trends: Call Booking, Close Rates & Off-Hours Calls, Oct 22, 2026 | https://www.servicetitan.com/toolbox/state-of-the-trades/trends/quarterly-industry-trends |
| Among the top 25% of businesses by close rate in each region, medians range from 70% to 73% | same | same |
| The page does not define close rate | same (read Oct 28, 2026) | same |
| Close rate = jobs sold / estimates given, same month | ours (the lesson's formula) | n/a |
| Example: 40 estimates, 14 sold, 35% | ours (worked example, labeled) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-04-close-rate/01_voice/facts.json", "numbers": {
 "medLow": {"path": "servicetitan.medianLowPct", "shown": "31%"},
 "medHigh": {"path": "servicetitan.medianHighPct", "shown": "38%"},
 "topShare": {"path": "servicetitan.topSharePct", "shown": "25%"},
 "topLow": {"path": "servicetitan.topLowPct", "shown": "70%"},
 "topHigh": {"path": "servicetitan.topHighPct", "shown": "73%"},
 "stYear": {"path": "servicetitan.windowYear", "shown": "2026"},
 "exEst": {"path": "example.estimates", "shown": "40"},
 "exSold": {"path": "example.sold", "shown": "14"},
 "exRate": {"path": "example.ratePct", "shown": "35%"}
}}
```
