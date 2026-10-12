# Hook library (CMO)

Every spec and slate video carries a hookId from this file; the promote runs write it into scoreboard shorts/<slug>. Score = YouTube views per Short tagged with the pattern, from the YouTube Data API (videos.list statistics). Rescored every Monday. A pattern with 3+ pieces under the median of all our Shorts is retired. Benchmark: the $40 hourly rate Short (1,002 views on Oct 6).

Last scored: Tue Oct 6, 2026, 5:30 am (first build; 11 Shorts, median 39 views). Pieces before Oct 6 were tagged after the fact by the CMO from their titles.

| id | pattern | example in our voice (real product numbers) | platforms | pieces | views per piece | status |
|---|---|---|---|---|---|---|
| H01 | Your price pays less than you think: a rate, visit or night, then the smaller number it really keeps | "Every 2 weeks at $245? Only $18.61 is profit" (#14 Quote Builder) | YT Short, Reel, pin | 2 (svc-40-hourly 1,002; str-fee 36) | 519 | active, lead pattern |
| H02 | The lowball correction: name the low price, show the loss or the real rate | "Charging $150 for a 2.5-hour clean? You lose $33.79" (#13 Quote Builder) | YT Short, Reel | 1 (cleaning-22-vs-55 903) | 903 | active, lead pattern |
| H03 | The cost nobody quotes: one hidden cost line and what it adds to a job | "A 20-mile round trip adds $52 to the job" (#13) | YT Short, pin | 1 (svc-20-mile 717) | 717 | active |
| H04 | Guess vs math on one named trade job | "Full sedan detail: the guess says $96. The math says $345" (#13) | YT Short, Reel | 2 (detail-sedan 1; lawn-spring-cleanup 39) | 20 | watch: trade-specific framing lost to the generic H01 to H03 on Oct 5; one more under the median retires it |
| H05 | Rule of thumb with a count ("takes 51 pieces", "112 units", "90 seconds") | "A $150 booth fee takes 51 pieces to break even" (#12) | pin | 3 (booth-51 3; reorder-112 11; star-90s 30) | 15 | RETIRED Oct 6 (3 pieces under the median 39) |
| H06 | The rule people get wrong (myth plus the document that settles it) | "Your will does not control your 401(k)" (#11) | YT Short, pin | 1 (binder-401k 61) | 61 | active, families only |
| H07 | Small change, big saving | "Shrink the box 2 inches, pay $11.57 instead of $21.15" (#7) | YT Short, pin | 1 (ship-dim-weight 64) | 64 | active |
| H08 | Contrarian rule: reject a pricing rule sellers repeat, show the numbers (from FEED.md) | "The 3x rule says $450 on a $150 booth. Your costs may say more" (#12, after its mileage fix) | YT Short, Reel | 0 | not recorded | new, test |
| H09 | Guess the price: show the job, ask for a guess, reveal last (from FEED.md) | "1,800 sq ft, 3 bed, 2.5 bath, every 2 weeks. What would you charge? The kit says $245" (#14) | Reel, YT Short | 0 | not recorded | new, test on Instagram (comments) |
| H10 | Big total in frame one (from FEED.md) | "$38,154.87 of debt, $1,100 a month: debt-free in 40 months" (#16 sample) | YT Short, pin | 0 | not recorded | new, test |
| H11 | Cost vs value gap: what it costs to make next to what it must sell for (from FEED.md) | "$6.10 of materials, $8 profit wanted: list it at $22.01" (#5 Pricing tab) | pin, Reel | 0 | not recorded | new, test |
| H12 | Cross-niche overlap: one number for two buyer groups (from FEED.md) | "Airbnb hosts: the 15.5% fee takes $4,625 a year at 200 nights" aimed at hosts who also run a cleaning side business | pin | 0 | not recorded | new, low priority |

## Audience scope rule (Optimizer, Sun Oct 11, 9:10 pm; YouTube Data API videos.list pulled the same night)
Evidence, every Short published Oct 5 to Oct 11 (views as of Oct 11, 9:15 pm):
- Narrow trade named in the hook (detailing 9, lawn 40, driveway wash 18, junk 60-mile 17, junk half load 0, paver drive 7, junk $62.36 11): 7 Shorts, 102 views, median 11.
- Broad money hook (biweekly clean 4, $150 clean 41, debt 46, rent kept $550 155, bill $74.65 keep $52.08 7, $40 an hour $29,940 short 97, $60 an hour $12,660 short 13 at under 1 day): 7 Shorts, 363 views, median 41.
- The three Shorts past 700 views (Oct 3 and 4: $40 hourly 1,001; 20-mile trip 717; $22 vs $55 clean 901) all named a rate or a job, never a niche trade.
- R&D (meta/shop.rnd.flagshipPhrases, Oct 8): pressure washing and junk removal phrases are all under 20 US searches; the audience is small on YouTube too.

Rule, binding from the Oct 12 slates until the CMO's Monday rescore shows otherwise with 6+ new pieces:
1. A Short for #22 or #23 opens with the money in frame one for anyone who quotes a job ("your hourly price", "a $350 job"), and names the trade only in the product line and CTA. Title and hook_say follow the same rule.
2. When a slate has one Short slot and no broad hook for #22 or #23 passes the cold-viewer review, the slot goes to #20 (broad by nature, 97 views on Oct 10) and #22 and #23 keep the pins.
3. Tag each Short with scope "broad" or "trade" in shorts/<slug> and the spec, so the Monday rescore can keep or kill this rule on our own numbers.

Draft broad hooks for Oct 12, numbers copied from already verified specs (re-check against the product file before the slate is approved):
- #23 (spec 2026-10-11-junk-62-break-even): "$25 an hour looks fine. Break-even is $62.36." hook_say: "$60,000 a year over 2,400 hours looks like $25 an hour. Count only the hours customers pay for, plus tax and costs, and break-even is $62.36."
- #23 (spec 2026-10-09-pm-junk-350): "A $350 job that loses $59.62" hook_say: "Two people, an hour and a half, $350. Break-even is $409.62, so this job loses $59.62."
- #22 (spec 2026-10-10-paver-drive-203): "The drive to a job can cost $203.44" hook_say: "Two people, a van and a 40-mile round trip cost $203.44 before any work starts."

## Rules for using this file
- New scripts are original, in our voice, built from our products' own numbers, and pass VERIFY BEFORE POSTING. FEED.md gives mechanisms only; nothing a competitor's video shows or says is copied.
- Pins carry the pattern in the headline but are scored on Pinterest outbound clicks, not views, once the Pinterest API reports them (Oct 5 data was still processing).
- Instagram Reels cannot be scored yet: the app lacks the insights permission (Oct 6 GET returned "Application does not have permission"). Score Reels once that is fixed.
