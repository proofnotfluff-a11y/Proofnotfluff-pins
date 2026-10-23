# Radar rubric: how a public-data idea is written, scored and reviewed

Todd, Oct 23, 2026 (live chat): "an agent that's always on the lookout for new opportunities with regard to aggregating public data and creating a new product if that product has a strong demand potential", with independent reviewers so "whatever is being thought about or produced is quality and has a good shot of actually bringing in a substantial return". The code is tools/opportunity_score.py; the stage contract is .claude/skills/radar/SKILL.md. This file is the field list and the reviewer prompts.

## One idea, one file: scout/candidates/<slug>.json

Business-level facts only: no person's name or email anywhere. Every source is `{"url": "...", "date": "YYYY-MM-DD"}` (the date it was published, or read when undated). A factor without a dated source scores 0.

```
{"schema": "pnf.opportunity.v1", "slug": "...", "name": "Buyer-facing product name", "status": "new",
 "addedAt": "YYYY-MM-DD", "pitch": "one line: what list, for whom, why now",
 "categories": ["trade words"],
 "provenAbroad": [{"what": "the same model sold elsewhere", "url": "...", "date": "..."}],
 "buyer": {"who": "the trade that pays", "count": 0, "countSource": {}, "reach": "how we reach an owner (their own site, a state roster)", "reachSource": {}},
 "price": {"monthly": 29, "reason": "why this price inside $29 to $199", "competitors": [{"name": "...", "monthly": 0, "url": "...", "date": "...", "richer": false}],
           "freeSubstitute": {"note": "the source's own free export or a free tier, if one exists", "url": "...", "date": "..."}},
 "demand": {"searchQueries": [{"q": "...", "url": "...", "date": "..."}], "aiQueries": [{"q": "a question a buyer asked in public", "url": "...", "date": "..."}]},
 "data": {"publisher": "...", "dataset": "...", "subject": "what one record describes (a business, a building, a carrier)", "url": "...", "apiUrl": "...",
          "cadence": "daily|weekly|monthly|quarterly|yearly|static", "lastUpdated": "YYYY-MM-DD", "recordsPerMonth": 0, "recordsSource": {},
          "apiStable": true, "license": {"commercialUse": "allowed|forbidden|unclear", "url": "...", "date": "...", "note": "the terms in our words"}},
 "build": {"days": 0, "maintHoursMonth": 0, "reuses": ["tools/socrata.py"]},
 "fit": {"samePortal": false, "existingTools": [], "sameBuyerTypes": false},
 "overlap": "an existing product, spec or approved step this touches, or empty"}
```

`recordsPerMonth` is counted from the source (a SoQL count URL, a file row count), never estimated. When the cloud cannot reach the portal, leave it null and add the dataset to the probe workflow; the factor loses points until it is counted.

## Kill rules (code, final)
K1 no buyer we can name and reach. K2 terms forbid commercial use. K3 a never-sell category (medical, legal filing, immigration, investment advice). K4 longevity or supplement products before Sept 21, 2027 (Todd's non-compete with Cata-Kor). K5 private people as the subject (homes, residents, named individuals).

## Scores
Eight factors, 0 to 5, weighted to 100: buyer 15, pay 15, demand 15, data 15, license 10, effort 10, speed 10, fit 10. Under 60 is parked without review. A sourced free substitute caps pay at 2, and a competitor at up to twice our price marked richer (it ships fields we cannot, such as contacts we strip) caps it at 1: the first run's reviewers dropped every idea with one, and the scout records both before scoring. January net dollars assume 40 first emails a week from launch and 0.25%, 0.75% or 2% of them becoming paying members; first dollar is build days plus 5 days of gates plus 28 days of free Mondays and the 7-day trial. These are assumptions until a payer exists, so confidence tops out at medium.

## Reviewers (each a fresh Agent subagent, model fable else opus, that never saw the scouting)
Each gets the candidate file and the scorer's row only, checks the sources itself, and returns JSON: `{"reviewer", "verdict": "PASS|FAIL", "score": 1-5, "round", "date", "reasons": ["..."]}`. The run appends it to scout/reviews/<slug>.json.
- **demand**: "You own a small {buyer.who} business. Would you pay ${price} a month for this list? Check every competitor price and question URL. FAIL if the buyer already gets this free, the counts are too thin to pay back the price, or the evidence is not what the file says."
- **data-legal**: "Open the dataset and its terms. Is commercial resale or repackaging allowed, word for word? Does any field name a private person? Is the cadence real (last update date)? Any rule in coo/CONSTITUTION.md 2 or legal/README.md it breaks? FAIL on any of these."
- **redteam**: "Argue this makes $0 by Jan 31, 2027. Name the three strongest reasons and one number in the file you doubt. PASS only if your best argument does not hold."

A FAIL whose objection no honest fix can answer (the offer itself, not the evidence) sets the candidate's status to dropped with a dropReason, without a second review. One fix round: the run fixes what a FAIL names (better sources, a narrower buyer, a lower build estimate it can show) and a new subagent reviews again. A second FAIL drops the idea, or sends it to Todd with the reason when the code score is 75 or more. Ideas with three PASS become a to-do row "Decide: build <name>?" for Todd. Nothing is built without his go on that idea.
