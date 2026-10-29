# stress-test (on request; radar step 5; before any new product or price goes to Todd)

Todd, live chat, Oct 29, 2026 ("Founder: stress test"). coo/CONSTITUTION.md binds. One job: pressure-test a product or offer before Todd spends time or money on it, so a weak idea dies on paper. Adapted from 4 of the 11 MIT-licensed founder-skill skills (github.com/Jakeschincariol/founder-skill, fd9385b: board, CFO, offer, pricing). Research and files only: nothing is built, priced, published, sent or bought.

## Inputs (Reads)
- The product's own record: launches/<slug>.md, scoreboard leadproducts/<slug> and its funnel counts, scout/candidates/<slug>.json and scout/reviews/ for a new idea, legal/reviews/ for it.
- coo/VENTURE.md (the $1,000 net month by Jan 31, 2027), coo/CONSTITUTION.md section 1 (price rules), lenses.md in this folder.
- Competitors' own public price pages, fetched this run. Real objections only from CRM reply summaries (counts and our words, never a person's).

## Process (Executes)
0. Date from bash; `python3 tools/check_repo.py --preflight stress-test`; `python3 tools/stress_numbers.py --selftest`.
1. Brief: write scout/stress/<slug>/brief.md, standing on its own (subagents cannot see the chat): what it is, buyer, price, channel, funnel counts so far, cap, costs. Each fact names its file or page. Unknowns are listed as open questions, never filled in.
2. Board: three fresh subagents (model opus) in one message, one lens each from lenses.md (Offers, Monopoly, Product), given only the brief and that lens. Each writes scout/stress/<slug>/<lens>.md: Score 1 to 10, Vote FUND, FUND IF or PASS, what is strong, the top 3 things that would kill it, the questions it would ask, conditions.
3. Numbers: scout/stress/<slug>/numbers.json, every cost with a source (Gumroad 10% plus $0.50 a sale on our own links; an estimate says "estimate: <why>"). The ramp comes from real funnel rates (delivered, replies, paid) with the step shown. `python3 tools/stress_numbers.py cfo <numbers.json> --out <dir>/cfo.md`; what-ifs with --price and --volume, never guessed.
4. Offer: the obstacles between the buyer and the result, from the board memos, real objections and the legal review; each turned into a fix scored value 1 to 5 and cost 1 to 5. Value equation (outcome, belief, time, effort) before and after. No fake urgency, reviews, anchors or "only N left" unless true.
5. Price: real competitor prices with links. Optional quick panel: one fresh subagent plays 12 buyers from a profile built only from the brief, each giving buy or pass with a reason and the four price answers (too cheap, cheap, expensive, too expensive). Save answers.json with "simulated": true, run `python3 tools/stress_numbers.py price <answers.json>`. Simulated buyers pick what to test; they are never proof and never appear in copy, a listing, an email, a page or a decide row except labeled simulated.
6. Verdict: scout/stress/<slug>.md: the vote and average score, risks more than one lens raised, the merged conditions as a checklist, the numbers lines from cfo.md, then at most 3 changes ranked, each with expected effect and cost in dollars or hours, as one yes or no line for Todd. Keep disagreements. A PASS is a result: say it plainly.
7. Check: a fresh subagent that never saw steps 1 to 6 traces every number and claim in the verdict to a file, a fetched page or the tool output; anything untraced is cut. No em or en dashes, no person's name (lens authors only as sources).
8. check_repo exits 0, commit scout/stress/, git push origin HEAD:main (pull --rebase once on a reject, never force).

Radar use: before a "Decide: build" row goes to Todd, run steps 1 to 3 and 6 to 7 (board and numbers, no panel) and add the vote, average score and break-even line to the row.

## Outputs (Writes)
- scout/stress/<slug>/ (brief, three lens memos, numbers.json, cfo.md, answers.json when a panel ran) and scout/stress/<slug>.md. Counts and our words only.
- One message to Todd: the vote, the numbers in two lines, the ranked yes or no changes, and "Not financial, tax or legal advice." Any price, offer, page or product change waits for his yes in a live chat.
