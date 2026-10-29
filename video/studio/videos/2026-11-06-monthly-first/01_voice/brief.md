# Brief: Lead with the monthly payment

Lesson 10, segment Quote Clinic. Made Oct 29, 2026 by the daily studio run from the trades-first bank's lesson 2
(research/runs/2026-10-28-trades-insights.md). Trade evidence only: the ACHR News report of the ACCA and Farmington
Consulting Group survey, re-read with WebFetch on Oct 29, 2026.

- **Where:** Instagram Reel, 9:16, about 70 to 80 s (217 words), then TikTok, Facebook, YouTube Shorts.
- **Audience:** an HVAC (or plumbing, electrical) owner who quotes replacements and says the full price first.
- **The one idea:** on a replacement quote, say the monthly payment first, the full price right under it. (16 words; the 12-point check counts the rule as "Monthly payment first, full price right under it", 8 words)
- **Shape:** hook (most of you say the big number first; monthly-first contractors get twice the share financed; here's the line) -> stakes (ACCA survey of 1,000+ HVAC contractors: 72% lead with the overall price; monthly-first 42% of system sales financed vs 21%) -> why (monthly shops sold fewer entry-level systems, 34% vs 42%; our take: a monthly number sits next to bills they already pay) -> the artifact (the quote line, held big, EXAMPLE) -> the turn (every job, not just the big ones; only 37% offer it on every job; never hide the total) -> the honest note (a survey, not proof; only quote a plan you offer) -> close (the rule; send line; "Don't lead with the big number").
- **Voice:** Todd's clone in `_shared/voice.md`.
- **Real screens:** the survey's numbers with the source (ACHR News, Feb 10, 2026, ACCA survey of 1,000+ HVAC contractors); the quote line as a card (marked EXAMPLE).
- **Close:** "Send this to whoever writes your quotes." Brand plate, send line.

## Who teaches it (creators, from the bank entry; read Oct 28, 2026)
- **Joe Crisara** and **Tommy Mello**: financing as the first offer ([The Home Service Expert podcast, May 26, 2026](https://www.audioscrape.com/podcast/the-home-service-expert-podcast/episode/the-sales-reframe-that-changes-how-every-technician-thinks-about-their-job-18580)).
- ServiceTitan's financing content. None of their own figures is used; the numbers are ACCA's, via ACHR News.

## Worlds (none from lesson 9, book-the-call: versus, calendar, boss, flaps; none from lesson 8, close-rate: gauge, inventory, dispatch)
1. **hook and artifact: the storefront counter** (`k.sets.counter`). A big price tag hangs from the awning: FULL PRICE
   (no number, the brief has none), and it flips to PER MONTH on "monthly payment". The hook card hangs on the counter
   front: "Most HVAC owners say the big number first." with the 72% and the source. In the artifact section the chalk
   board carries the header and a cream quote card (EXAMPLE) types the line as it is said; the tag flips to PER MONTH
   on "a month", and the "$X a month" line gets the gold sweep on "Monthly line on top".
2. **stakes: the arcade high-score table** (`k.sets.scores`), titled SALES FINANCED: MONTH 42% (the hi row, gold) and
   TOTAL 21% (teal); NEW RECORD reads 2X THE SHARE. The source types under the table; the 72% lead line lands first.
3. **why: the slot machine** (`k.sets.slots`), entry-level mix: the reels land 3 4 % for monthly-first (label
   MONTHLY FIRST: ENTRY-LEVEL MIX), then 4 2 % for total-first; no jackpot (win false): the lower number is the
   point, the tray says "fewer entry-level systems". Then "our take" in the tray.
4. **turn and note: the street** (`k.sets.street`): the van drives job to job; the sky line says EVERY JOB, then
   "Only 37% offer it on every job." The van parks at a small job on "not just the big ones". The honest note rides
   the same street, parked, in the sky panel.
5. **close: LEVEL UP** (`k.sets.levelup`): the bar fills on the rule, LEVEL UP stamps on "monthly number first";
   perks: "Monthly first", "Full price under it"; the send line lands in the perks area.

## Trust notes
- ACHR News, Feb 10, 2026 (Chris Gray): "A survey conducted by the Air Conditioning Contractors of America Association
  and Farmington Consulting Group of more than 1,000 contractors nationwide". ACCA's own blog says more than 1,000 HVACR
  contractors; said "over a thousand HVAC contractors", shown "1,000+ HVAC contractors".
- 72%: "most contractors (72%) tend to lead with the overall price of the job." Said "Seventy-two percent lead with the
  overall price"; the hook says "most of you say the big number first" (72% of the surveyed contractors, addressed to
  HVAC owners).
- 42% vs 21%: of new or replacement system sales financed, monthly-first vs overall-price-first. "Twice the share
  financed" is 42 / 21. Correlation: "contractors who lead with", never "leading with it makes".
- 34% vs 42%: the entry-level equipment mix, monthly-first vs overall-first. Said "sold fewer entry-level systems,
  thirty-four percent of sales instead of forty-two".
- 37%: "only 37% are offering it on every job." The page's base is the surveyed contractors' financing; said "in that
  survey, only thirty-seven percent offer it on every job" and shown the same way, with no wider base.
- "Your customer weighs a monthly number against bills they already pay" is our take, said as "Our take".
- The quote line and its blanks ($X, $Y) are an example (tagged EXAMPLE); no price or term is suggested.
- Close rates 38% vs 49% (with financing offered) are caption context only.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| 72% lead with the overall price; monthly-first 42% of system sales financed vs 21%; entry-level mix 34% vs 42%; only 37% offer it on every job; 1,000+ contractors | ACHR News, Feb 10, 2026, on the ACCA and Farmington Consulting Group survey | https://www.achrnews.com/articles/165799-survey-reveals-strategies-to-boost-hvac-close-rates-by-double-digits |
| HVAC contractors (the survey's trade) | ACCA, "Inside the Contractor of the Future study" | https://hvac-blog.acca.org/inside-the-contractor-of-the-future-study-key-findings-from-1000-contractors/ |
| The quote line; never hide the total; only quote a plan you offer; customers weigh a monthly number against bills | ours (advice; bank lesson 2 takeaway) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-06-monthly-first/01_voice/facts.json", "numbers": {
 "lead": {"path": "acca.overallLeadPct", "shown": "72%"},
 "mFin": {"path": "acca.monthlyFinancedPct", "shown": "42%"},
 "tFin": {"path": "acca.overallFinancedPct", "shown": "21%"},
 "ratio": {"path": "acca.ratio", "shown": "2"},
 "mEntry": {"path": "acca.monthlyEntryPct", "shown": "34%"},
 "tEntry": {"path": "acca.overallEntryPct", "shown": "42%"},
 "every": {"path": "acca.everyJobPct", "shown": "37%"},
 "n": {"path": "acca.contractors", "shown": "1,000"},
 "year": {"path": "acca.year", "shown": "2026"}
}}
```
