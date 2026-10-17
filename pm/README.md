# Prediction-market paper tracker (lane C of coo/VENTURE.md)

Todd, Oct 17, 2026: "prediction markets, paper only ... I don't mind throwing in a couple hundred $'s in prediction markets to see how you can build it." This folder is the paper record. Nothing here is a bet, an account, a key or advice.

- tools/pm_tracker.py does the work; .github/workflows/pm-tracker.yml runs it every 6 hours.
- config.json: the rules. Starting paper bankroll $200 (the size Todd named), $5 a copied trade, the top 20 wallets on Polymarket's month PNL board re-picked weekly, 2% modeled fee each way, 1 cent slippage, prices under 0.05 or over 0.95 skipped, verdict Dec 12, 2026 after 100+ closed positions.
- state.json: cohort, watched wallets, open and closed paper positions, cash. equity.csv: one row per run.
- raw/: one trimmed sample of each API response, kept so the parser can be checked against the real shapes after the first run.

How to read it: equity against 200 is the whole story. Under 200 after fees at the verdict means copying the leaders with a delay loses money, which is the expected result for most copy strategies (their edge is speed and information). Over 200 with 100+ closed positions and a positive mean per position means the question deserves Todd's case in coo/VENTURE.md section 6 before any real dollar.

What this cannot tell you: fills at real size, platform fees on specific markets, or whether a US resident may trade on a given platform; those go in the case, from the platforms' own pages.
