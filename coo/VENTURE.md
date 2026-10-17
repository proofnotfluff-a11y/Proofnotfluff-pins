# The venture engine (Todd, Oct 17, 2026, 1:02 pm)

Todd's ask, in his words: "write and implement a self evolving algorithm ... go off on your own and evolve this strategy to build out this business ... We don't need to limit scope to etsy digital products ... Think outside the box and evolve. We need to win." His answers the same hour, recorded as [stated] in the ledger: every lane below may be probed with cheap tests; the engine spends $0 on its own and asks for every dollar; the first win is a $1,000 month by Jan 31, 2027; Gemini scores the plan as a red team; prediction markets run on paper, and he does not mind staking a couple hundred dollars of his own once the paper record shows how it works.

This file extends coo/EVOLUTION.md (the loop) and sits inside coo/CONSTITUTION.md (the fixed rules, amended by Todd today in section 6). Where coo/PIVOT.md and this file differ, this file wins for probes and the e-commerce ladder keeps its own rules.

## 1. What the engine optimizes
The first win: $1,000 of revenue in one calendar month by Jan 31, 2027, net of platform fees, from any lane. Until money arrives, the leading indicator for every probe is demand it can count: waitlist sign-ups per 100 visits, visits (Cloudflare Web Analytics, once the ProofNotFluff account is readable; quest cloudflare-member), then the first dollar. The paper tracker's P&L counts as $0 revenue until Todd stakes real money himself; only realized net gains then count.

Why the loop has produced $0 so far, so nobody repeats it: the feedback signal was starved (no visits readable, no checkout that can publish, no services channel) and the search space was one platform. A loop can only evolve on the feedback it gets. The engine's first job is feedback, its second is breadth.

## 2. The lanes (all four approved Oct 17; the e-commerce ladder continues)
- A. Public-data products. Public records packaged for one trade, sold as a weekly list or a feed at $29 to $99 a month. The Chicago construction leads page is probe A1 (live Oct 17, verdict Dec 1). Agent-buildable end to end; Todd's part is the checkout. Next candidates come from the same mechanism: a dataset a city or state publishes openly, a trade that sells to the entities in it, a price the trade already pays for leads. Each candidate needs one official source for the data and one for the buyer's willingness to pay (a competing list with public pricing, or a trade forum's stated spend), checked in the run.
- B. Micro-tools with monthly billing. A calculator that shows use becomes a saved-state tool at $29 a month, the floor of the constitution's off-Etsy band (Gumroad memberships for billing; Todd's upload); a lower monthly price needs Todd's words in chat. Probe B1 waits for visit data: the most-visited calculator gets a "Pro" waitlist block. Keepwell joins this lane only when Todd puts it in.
- C. Prediction markets, paper. tools/pm_tracker.py follows the top Polymarket wallets with paper money every 6 hours (GitHub Actions, public Data API, no key, no account). Probe C1: verdict Dec 12 (8 weeks). Rules in section 6.
- D. Asset arbitrage and imported models (Todd's own angles, Oct 2026). Research-first: one case every two weeks in coo/OPPORTUNITIES.md with real listings, quotes and prices as sources, the capital it needs, Todd's hours, and the smallest test. These need money and people, so the verdict is Todd's go or no-go on a quest; no agent leases, buys or signs anything.
- E. The e-commerce ladder (coo/PIVOT.md) runs as it is; its Nov 12 check stands.

## 3. The probe (one scoreboard experiments/<slug> doc, kind "probe")
Fields, on top of EVOLUTION.md section 2: lane, buyer (who pays and why now), evidence (two sources, dated, official where possible), smallest test (a page with a waitlist, a paper tracker, or a research case), fitness metric, cost ($0; anything else is a quest first), verdictAt (45 days at most; 56 for the paper tracker), killRule, scaleRule, toddParts (the steps only he can do, with minutes).
- Cap: 3 live probes plus the paper tracker. A fourth waits. One new probe a week at most, picked on evidence, not on enthusiasm.
- Every probe page states the planned price, that it launches only with enough demand, and what happens to the email (Kit). No fake urgency, no invented testimonials, no "spots left".
- Kill: under 20 sign-ups, or under 50 visits, or $0 at the verdict date (an experiment with under 50 visits is inconclusive, never kept). Scale: 50+ sign-ups or the first dollar: the COO prices the paid version inside the constitution's off-Etsy band and queues the build; Todd's parts become quests with the expected revenue on each.
- A killed probe stays as a free page if it is useful to visitors, with its feed or waitlist removed.

## 4. Cadence
- Daily (COO 5:00 am): read each live probe's fitness (Kit subscriber counts through the Kit API once a key exists, else the Kit UI count Todd reports; Cloudflare visits once readable; pm/equity.csv through the raw URL), kill on the dates, log one line.
- Monday deep run: verdicts, one new probe at most, the red-team round (section 5), the memo, and Todd's queue sorted by expected value per minute of his time.
- The paper tracker runs itself every 6 hours; the COO reads it, never edits pm/config.json except by a commit that names the reason.

## 5. The red team (Gemini, Todd's Oct 17 choice)
- Route: Zapier, Google AI Studio (Gemini), action send_prompt with Google Search grounding on, model gemini-2.5-pro (flash if pro is unavailable). It needs Todd's Gemini API key connected once in Zapier (quest connect-gemini). Until then the red team is a Claude subagent with the same prompt and the memo says so.
- Monday: the COO sends the memo's strategy section plus each live probe's case and asks for: the three strongest reasons this fails, one number it doubts and why, what it would test instead, and a 1 to 5 confidence that the plan reaches $1,000 in a month by Jan 31. The answer is stored as memos/<date>.redteam {model, score, objections:[...], suggestion}. The COO answers every objection in the memo (accept, with the change made; or reject, with the number). An objection accepted twice becomes a rule in STRATEGY.md "What we know".
- The red team reads and scores. It never builds, posts, spends or edits a prompt.

## 6. Prediction markets: the rules (Todd, Oct 17: "paper only" plus "a couple hundred $'s ... to see how you can build it")
- No agent ever places a bet, opens an account, holds a wallet or key, or moves money. The tracker reads public data only and the workflow holds no secret.
- Paper first. Verdict Dec 12 by tools/pm_tracker.py's rule: kept only if equity is above the starting bankroll after modeled fees and slippage with 100+ closed positions and a positive mean per position; otherwise killed or inconclusive. The modeled fees (2% each way) and slippage (1 cent) are conservative stand-ins and are named in pm/config.json.
- If the verdict is "kept", the COO writes a case: the edge with its confidence interval, the drawdown, what slippage at real size would do, fees on each platform, and the legal position of each platform for a US resident from the platform's own pages and the CFTC's, dated. Todd decides whether to stake up to about $200 of his own money, places every bet himself, and reads the tracker as data. No agent recommends individual bets, and nothing here is investment advice.
- Any paper strategy change (a different cohort rule, a different window) is a new experiments doc, not an edit to a live one.

## 7. Money and accounts
$0 autonomous spend (Todd, Oct 17). Every dollar is a quest with the vendor's price and the expected effect; Todd says yes to each. Accounts, keys, terms and payouts are his, as the constitution says. Todd's parts are listed on every probe with minutes, and the Monday memo ranks them by expected value so his time goes where it pays.

## 8. Honesty
A metric not recorded is "not recorded". A probe with no visit data is judged on sign-ups alone and says so. The memo states the week's revenue in dollars first, every week, including $0.
