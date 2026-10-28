# Brief: Markup vs margin, why a 50% markup is not 50% profit

Lesson 3, segment Run the Numbers. Planned Oct 28, 2026, from research/runs/2026-10-28-script-playbook.md (example 2),
with every source re-read that day.

- **Where:** Instagram Reel, TikTok, Facebook Reel, YouTube Short; 9:16, about 60 s.
- **Audience:** a trades or home-service owner (plumber, electrician, HVAC, remodeler) who prices jobs as cost plus a markup.
- **The one idea (15 words max):** a 50% markup is a 33% margin; price from margin, not markup. (14 words)
- **Who sends it to whom:** the owner -> whoever sets the prices (often the owner).
- **Shape:** hook (50% markup is not 50% margin) -> the math on the board (cost 1,000, markup 500, price 1,500, the 500 is a third) -> why (markup on cost, margin on price; margin still has to cover overhead) -> a real 50% margin needs a 100% markup -> the turn and the formula card, Price = Cost / (1 - margin), worked at 40% -> the rule and the send line.
- **Metaphor:** none. A stacked bar carries it: the cost block, the markup slice on top, the slice measured against the whole.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** none needed; the math is the real thing. The formula card is the copyable artifact (held 3 s or more).
- **Close:** "Markup is on cost. Margin is on price." Send line: whoever sets your prices.
- **Trust notes:** the script says "margin", never "profit", for the number left after direct cost: gross margin does not
  take out overhead (Xero). "About thirty-three percent" for 33.3%. The 40% example is arithmetic from Xero's margin
  formula; facts.json carries each formula so the gate can recompute it. Example figures are an example, not a real job.

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
