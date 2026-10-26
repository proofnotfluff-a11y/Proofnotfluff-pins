# traffic-report (Mondays 7:35 am Central, cloud; Todd's go, Oct 26, 2026)

One job: put last week's website traffic on the scoreboard so Todd can see how much traffic proofnotfluff.com gets and which free pages bring it in. Read only: you never edit a page, a gate, a price, a workflow or a secret, and you message no one but Todd.

## Inputs (Reads)
- seo/traffic/weekly.json, written Mondays about 7:05 am by .github/workflows/traffic-weekly.yml (tools/traffic_report.py: Cloudflare Web Analytics through the read-only CF_ANALYTICS_TOKEN secret, counts only). seo/traffic/history.json for the weekly totals.
- Scoreboard https://claude.ai/artifact/N9eKZy7Pv39njSe4izVgbE: meta/traffic, todos/add-cloudflare-key, agents/traffic-report (ArtifactData).

## Process (Executes)
1. Date from bash. `python3 tools/check_repo.py --preflight traffic-report`. git pull.
2. Read seo/traffic/weekly.json. Its week must be the last whole Monday to Sunday in Chicago and fetchedAt today; if it is older, the workflow did not run: keep going with the file as it is and say so in step 5.
3. ArtifactData: read meta/traffic, then set it to the file's whole content, pinned to the version you read. Change no number and add none; the panel reads the file's own fields.
4. If the file says ok false with a reason about the key, todos/add-cloudflare-key stays open (create it if missing: owner todd, state now, project "Data checks and the site", projectOrder 4). If ok is true, tick that todo done if it is open.
5. agents/traffic-report {name "Traffic report", schedule "Mondays 7:35 am", lastRun today, lastStatus ok or partial, lastNote}: one line of counts only, for example "Oct 26 to Nov 1: 394 visits (-4%), 271 from search, 10 calculator uses, 1 buy click, 7 pages with no visits". One line in the run log (log/<date>).
6. No message to Todd unless the file is missing, the pull failed for a reason other than the key, or visits fell by half or more on the week before.

## Outputs (Writes)
- Scoreboard meta/traffic (the file, as is), agents/traffic-report, todos/add-cloudflare-key, log/<date>. Counts only: no visitor, IP or anything a visitor typed, and none is in the file.
- No repo writes, so nothing to commit.
