# Brief: Three prices on every quote

Lesson 4, segment Quote Clinic. Planned Oct 28, 2026 from the script playbook's example 3 (research/runs/2026-10-28-script-playbook.md), every fact re-read on its source page the same day.

- **Where:** Instagram Reel, 9:16, about 75 s (a worked example earns the longer slot), then TikTok, Facebook, YouTube Shorts.
- **Audience:** a trades or home-service owner (plumber, electrician, HVAC, roofer) who writes their own quotes and usually sends one price.
- **The one idea:** put three prices on every quote: good, better, best. (9 words)
- **Shape:** hook (top shops quote three, not one) -> stakes (ServiceTitan: 57% vs 41% of home jobs) -> why (the restaurant menu study: the middle gains about 5 points) -> the artifact (the Good / Better / Best card, held big) -> the survey (4+ options closed 52% vs 42% for 1 to 3) -> the turn (that survey can't show three beats one) -> close (one price is a yes or no; three is a choice).
- **Metaphor:** the menu. Three dishes, the middle one lifts; then the same three slots on a quote.
- **Voice:** Todd's clone in `_shared/voice.md`.
- **Real screens:** a one-price quote slip vs a three-price quote card; the ServiceTitan numbers as two bars; a three-dish menu card; the survey as two close-rate bars with its caveat; each source on screen while its number is.
- **Close:** "Send this to whoever writes your quotes." Brand plate, send line.
- **Trust notes:** ServiceTitan's top performers are the 90th revenue percentile in their trade and market (said as "top ten percent", shown as "top 10% by revenue"); vendor data, correlational, so the script says "habit", never "this made them top". The menu study is a restaurant in Germany, said so. The ACCA survey groups 1, 2 and 3 options together: never claim three beats one on close rate; the turn says so out loud and the caveat sits on screen. HVACR sample, said as "a heating and cooling trade group". Good / Better / Best wording is our advice, labeled "example".

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Top 10% (90th revenue percentile in trade and market) offered good-better-best on 57% of residential jobs; the rest on 41%; trailing 12 months through January 2026 | ServiceTitan, State of the Trades, Top Performer Profile | https://www.servicetitan.com/toolbox/state-of-the-trades/trends/top-performer-profile |
| 7 years of orders (88,000+ choices) at a German restaurant; a dish that became the middle option gained on average 5 percentage points of share; bigger when the added choice was at the high end | Pinger, Ruhmer-Krell, Schumacher, Journal of Economic Behavior and Organization 128 (2016) 14 to 34 | https://www.sciencedirect.com/science/article/abs/pii/S0167268116300658 |
| More than 1,000 contractors; 4 or more options: 52% close rate; 1, 2 or 3 options: 42% | ACCA and Farmington Consulting Group, Contractor of the Future (ACHR News, Feb 10, 2026) | https://www.achrnews.com/articles/165799-survey-reveals-strategies-to-boost-hvac-close-rates-by-double-digits |
| Good = the job done right; Better = what you'd pick for your own house; Best = plus upgrades (longer warranty, faster start date) | ours (advice) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-10-31-three-prices/01_voice/facts.json", "numbers": {
 "topPct": {"path": "servicetitan.topPct", "shown": "10%"},
 "topGbb": {"path": "servicetitan.topGbbPct", "shown": "57%"},
 "restGbb": {"path": "servicetitan.restGbbPct", "shown": "41%"},
 "stMonths": {"path": "servicetitan.windowMonths", "shown": "12"},
 "stYear": {"path": "servicetitan.windowEndYear", "shown": "2026"},
 "menuYears": {"path": "menu.years", "shown": "7"},
 "menuChoices": {"path": "menu.choices", "shown": "88,000"},
 "menuGain": {"path": "menu.middleGainPts", "shown": "5"},
 "menuYear": {"path": "menu.year", "shown": "2016"},
 "accaN": {"path": "acca.contractors", "shown": "1,000"},
 "manyOpt": {"path": "acca.manyOptions", "shown": "4"},
 "manyClose": {"path": "acca.manyClosePct", "shown": "52%"},
 "fewMax": {"path": "acca.fewMaxOptions", "shown": "3"},
 "fewClose": {"path": "acca.fewClosePct", "shown": "42%"},
 "accaYear": {"path": "acca.year", "shown": "2026"},
 "tiers": {"path": "gbb.tiers", "shown": "3"},
 "single": {"path": "gbb.single", "shown": "1"}
}}
```
