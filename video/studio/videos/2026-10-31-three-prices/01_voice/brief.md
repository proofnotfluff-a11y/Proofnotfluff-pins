# Brief: Three prices on every quote

Lesson 4, segment Quote Clinic. Planned Oct 28, 2026 from the script playbook's example 3 (research/runs/2026-10-28-script-playbook.md); rebuilt the same evening on Todd's word (trade evidence only, new scenery and motion): the restaurant menu study is gone, and its beat now rests on Housecall Pro's homeowner survey. Every fact re-read on its source page on Oct 28, 2026 (evening).

- **Where:** Instagram Reel, 9:16, about 85 s (a worked example earns the longer slot), then TikTok, Facebook, YouTube Shorts.
- **Audience:** a trades or home-service owner (plumber, electrician, HVAC, roofer) who writes their own quotes and usually sends one price.
- **The one idea:** put three prices on every quote: good, better, best. (9 words)
- **Taught by:** Joe Crisara (premium, mid-range, economy, written down; ServiceTitan Toolbox for the Trades, Nov 3, 2020), Tommy Mello ("options, not ultimatums"; Home Service Expert, May 26, 2026), Danielle Putnam (menu pricing). Their own percentages are coach claims and are not used (research/runs/2026-10-28-trades-insights.md, section 4).
- **Shape:** hook (top shops usually quote three) -> stakes (ServiceTitan: 57% vs 41% of home jobs) -> why (Housecall Pro: 68% of homeowners get more quotes when a price is higher than expected; one surprise price sends them shopping, three puts the cheaper option on your own quote) -> the artifact (the Good / Better / Best card, held big) -> the survey (ACCA: 4+ options closed 52% vs 42% for 1 to 3) -> the turn (that survey can't show three beats one) -> close (one price is a yes or no; three is a choice).
- **Worlds (each section its own; none from lesson 9's versus, calendar, flaps or boss):**
  hook = the storefront counter (`k.sets.counter`): the price tag on the toolbox flips from one price to three, the hook on a card hung on the counter front;
  stakes = the arcade high-score table (`k.sets.scores`): TOP 10% and THE REST rows, NEW RECORD on the habit line;
  why = our own piece, a street of 100 houses: the quote lands, 68 of them light up and send out extra quote envelopes; then one quote with three prices, the cheaper one glowing;
  card = our own piece, a quote clipboard on a truck tailgate at dusk: the three rows stamp in as said;
  survey and caveat = the slot machine (`k.sets.slots`): the lever pulls on "four or more options", the reels land 5 2 %, a second pull lands 4 2 % for 1 to 3 options; then the 1, 2 and 3 reels get bracketed as one group, and "Start with three" lands 3 3 3;
  close = the storefront again: the tag flips to three prices as it is said, the send line on the counter.
- **Voice:** Todd's clone in `_shared/voice.md`. Takes 1, 2, 4, 5, 6 and 7 kept; take 3 re-voiced (new words).
- **Close:** "Send this to whoever writes your quotes." Brand chip, send line.
- **Trust notes:** ServiceTitan's top performers are the 90th revenue percentile in their trade and market (said as "top ten percent", shown as "Top 10% by revenue"); vendor data, correlational, so the script says "habit", never "this made them top". Housecall Pro is a vendor survey of more than 1,100 U.S. homeowners; said as "over eleven hundred homeowners", shown "1,100+ homeowners"; "go get more quotes" is the source's "seek additional quotes". "One price that surprises them can send them shopping" restates that finding ("can", not "will"); "the cheaper option is already on your quote" describes the three-price quote, not a finding. The ACCA survey groups 1, 2 and 3 options together: never claim three beats one on close rate; the turn says so out loud and the caveat sits on screen. HVAC sample, said as "a heating and cooling trade group", shown "1,000+ HVAC contractors". Good / Better / Best wording is our advice, labeled "example".

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Top 10% (90th revenue percentile in trade and market) offered good-better-best on 57% of residential jobs; the rest on 41%; trailing 12 months through January 2026 | ServiceTitan, State of the Trades, Top Performer Profile (May 19, 2026) | https://www.servicetitan.com/toolbox/state-of-the-trades/trends/top-performer-profile |
| More than 1,100 U.S. homeowners; 68% seek additional quotes when pricing comes in higher than expected | Housecall Pro, The State of Home Service Spending (May 13, 2026) | https://www.housecallpro.com/resources/home-service-spending-report-2026-release/ |
| More than 1,000 contractors; 4 or more options: 52% close rate; 1, 2 or 3 options: 42%; only 10% offer 4 or more | ACCA and Farmington Consulting Group, Contractor of the Future (ACHR News, Feb 10, 2026) | https://www.achrnews.com/articles/165799-survey-reveals-strategies-to-boost-hvac-close-rates-by-double-digits |
| Good = the job done right; Better = what you'd pick for your own house; Best = plus upgrades (longer warranty, faster start date) | ours (advice) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-10-31-three-prices/01_voice/facts.json", "numbers": {
 "topPct": {"path": "servicetitan.topPct", "shown": "10%"},
 "topGbb": {"path": "servicetitan.topGbbPct", "shown": "57%"},
 "restGbb": {"path": "servicetitan.restGbbPct", "shown": "41%"},
 "stMonths": {"path": "servicetitan.windowMonths", "shown": "12"},
 "stYear": {"path": "servicetitan.windowEndYear", "shown": "2026"},
 "hcpN": {"path": "housecallpro.homeowners", "shown": "1,100"},
 "hcpShop": {"path": "housecallpro.seekMorePct", "shown": "68%"},
 "hcpYear": {"path": "housecallpro.year", "shown": "2026"},
 "accaN": {"path": "acca.contractors", "shown": "1,000"},
 "manyOpt": {"path": "acca.manyOptions", "shown": "4"},
 "manyClose": {"path": "acca.manyClosePct", "shown": "52%"},
 "fewMax": {"path": "acca.fewMaxOptions", "shown": "3"},
 "fewClose": {"path": "acca.fewClosePct", "shown": "42%"},
 "accaShare": {"path": "acca.shareManyPct", "shown": "10%"},
 "accaYear": {"path": "acca.year", "shown": "2026"},
 "tiers": {"path": "gbb.tiers", "shown": "3"},
 "single": {"path": "gbb.single", "shown": "1"}
}}
```
