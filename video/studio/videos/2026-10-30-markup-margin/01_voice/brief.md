# Brief: Markup vs margin, payoff first (the payoff-first test)

Lesson 3, segment Run the Numbers, rebuilt Oct 29, 2026 as the payoff-first test (Todd, Oct 29, 2026, 7:42 pm: "Build it
for tomorrow"). Sources re-read Oct 29, 2026 (JLC and Xero, every line in facts.json found on the page).

- **Format:** v2 (Lead Clinic v2, `_shared/voice.md`: 40 to 50 s with the end card, 100 to 135 words).
- **Test:** payoff-first. The one variable changed against the v2 baseline (videos/2026-11-07-let-me-think): the answer
  (the exact number and action a trade owner can use) is spoken and on screen inside the first 8 seconds, instead of at
  12 to 26 s. Everything else stays v2: drop-in, the usual way, why, one sourced proof, a button that echoes the hook, the
  end card send line, the AI label, 40 to 50 s. Baseline (Instagram insights Todd sent Oct 29): lesson 5 (v2) 103 views,
  9 s average watch, 59.6% skip; lesson 1 114 views, 8 s, 67.3%; lesson 9 9 views, 9 s, 66.7%; 0 real likes, saves or
  shares on any; views flatten near 100 to 110 within 3 hours. Read on Instagram after 48 hours: average watch over 9 s,
  skip rate, saves and shares against those numbers. Test note: video/studio/research/tests/2026-10-30-payoff-first.md.
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** a trades or home-service owner (plumber, electrician, HVAC, remodeler) who prices jobs as cost plus a markup.
- **The one idea (15 words max):** to get a 40% margin, divide your cost by 0.6. (11 words)
- **Shape (payoff first):** drop-in (a $1,000 job: what do you quote?) -> the answer at once (divide by 0.6, about $1,667,
  a 40% margin; the card held on screen) -> play it out (the usual 50% markup quotes $1,500, and the $500 is a third of the
  price) -> why (markup on cost, margin on price; the formula Price = Cost / (1 - margin)) -> proof (a real 50% margin needs a
  100% markup, JLC tag on screen) -> button (quote from the margin, echoing "costs", "thousand", "quote").
- **Hook pattern:** object-number
- **Treatment:** math-board
- **Example:** markup-1000-to-1500
- **Metaphor:** none. The register, the gauge and the job-site planks carry it.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** none needed; the math is the real thing. The answer card ($1,000 / 0.6 = $1,666.67, 40% margin) and the
  formula card are the copyable artifacts, each held 3 s or more.
- **End card send line:** "Send this to whoever sets your prices." (SCENE.sendLine)
- **Trust notes:** says "margin", never "profit" (gross margin does not take out overhead, Xero). "About sixteen sixty-seven"
  for $1,666.67. The 40% example is arithmetic from Xero's margin formula; facts.json carries each formula so the gate can
  recompute it. Example figures are an example, not a real job. "A third" for 33.3%.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Cost 1,000, a 50% markup adds 500, price 1,500; a 50% markup is a 33% margin | Sal Alfano, "Markup vs. Margin", JLC (undated page) | https://www.jlconline.com/business/markup-vs-margin_o/ |
| A 50% markup gives a 33.3% margin; Margin = (Revenue - COGS) / Revenue; Markup = (Revenue - COGS) / COGS | Xero glossary, "Margin vs markup" (July 23, 2026) | https://www.xero.com/us/glossary/margin-vs-markup/ |
| Markup is measured on cost, margin on the price | Xero glossary | https://www.xero.com/us/glossary/margin-vs-markup/ |
| Margin is not take-home pay: gross margin leaves out rent, salaries and other operating costs | Xero glossary ("Gross margin only accounts for the direct cost of goods sold...") | https://www.xero.com/us/glossary/margin-vs-markup/ |
| A real 50% margin needs a 100% markup: double the cost (1,000 -> 2,000) | JLC ("a 100% markup gives a 50% margin"; "you must double the direct cost") | https://www.jlconline.com/business/markup-vs-margin_o/ |
| Price = Cost / (1 - margin); 40% margin: divide by 0.6; 1,000 -> 1,666.67, and 666.67 / 1,666.67 = 40% | Rearranged from Xero's margin formula; Xero's Markup = Margin / (1 - Margin) gives the same 66.7% markup | https://www.xero.com/us/glossary/margin-vs-markup/ |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-10-30-markup-margin/01_voice/facts.json", "numbers": {
 "cost": {"path": "inputs.cost", "shown": "$1,000"},
 "markupPct": {"path": "inputs.markupPct", "shown": "50%"},
 "markupUsd": {"path": "computed.markupUsd.value", "shown": "$500"},
 "price": {"path": "computed.priceUsd.value", "shown": "$1,500"},
 "marginPct": {"path": "computed.marginPct.value", "shown": "33.3%"},
 "thirds": {"path": "computed.priceOverMarkup.value", "shown": "3"},
 "doubleMarkupPct": {"path": "inputs.doubleMarkupPct", "shown": "100%"},
 "doublePrice": {"path": "computed.doublePriceUsd.value", "shown": "$2,000"},
 "doubleMarginPct": {"path": "computed.doubleMarginPct.value", "shown": "50%"},
 "targetMarginPct": {"path": "inputs.targetMarginPct", "shown": "40%"},
 "divisor": {"path": "computed.divisor.value", "shown": "0.6"},
 "targetPrice": {"path": "computed.targetPriceUsd.value", "shown": "$1,666.67"},
 "targetMarginUsd": {"path": "computed.targetMarginUsd.value", "shown": "$666.67"},
 "targetCheck": {"path": "computed.targetMarginCheckPct.value", "shown": "40%"}
}}
```
