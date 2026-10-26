# Launch record: Unattended Agent Kit (side test, step 1: evidence, offer, draft page, waitlist), Oct 26, 2026

Decided: Todd, Oct 26, 12:38 pm ("Let's build number one. Write the prompt"; coo/DECISIONS-2026-10-26.md; the reopened case in coo/OPPORTUNITIES.md). Scoreboard todo agent-kit-test. A new product, page type and price, so nothing is published, linked, posted or emailed until Todd says go in a live chat (coo/CONSTITUTION.md 2). No kit build in step 1.

## 1. Evidence, re-checked Oct 26 (primary sources, this run)
Verdict: FAIL against the case's Oct 23 evidence. The worry is real; paying for guardrails is not shown.
- Proven seller: ClaudeKit, $99 one time (docs.claudekit.cc FAQ, read by the research agent). Its trustmrr revenue (https://trustmrr.com/startup/claudekit) could not be re-read: the fetch needed a permission no one was there to grant. UNVERIFIED today. It sells a broad agents-and-commands framework, not guardrails.
- Paid kits and tools, prices and visible sales (trustmrr figures are processor-verified):
  - CC Assist (chat history and cost viewer), $4.99 a month or $49.99 lifetime: $7,486 all time, $492 last 30 days (https://trustmrr.com/startup/claude-code-and-codex-assist-history-diff-viewer-chat-manager.md).
  - Redlight Greenlight (approve Claude Code permission requests remotely): $209 all time, $0 last 30 days (https://trustmrr.com/startup/redlight-greenlight-for-claude-code.md). The only permissions product with verified revenue, and it is stalled.
  - ClockedCode (CLAUDE.md master prompt), $39: $123 all time, $0 last 30 days (https://trustmrr.com/startup/clockedcode.md).
  - Claude Code Guardrails Pack, $19: hooks against rm, writes outside the repo and commits before tests, settings presets; no unattended or spend angle; no sales shown (https://lucaberton.com/claude-code-guardrails-pack/, opened this run).
  - The Claude Code Safety Audit, $49 minimum, $59 suggested: 50 points including autonomous operation and cost sections; no student count (https://leanpub.com/c/claude-code-safety-audit, opened this run).
  - getclaudekit.com kits $49 to $199; Claude Code courses $129 to $179 (leanpub) and $149 (gumroad); small kits at $4.99 and $9 show no sales.
- Free competition: cc-safe-setup (8 default hooks, about 700 examples, aimed at autonomous runs), Boucle-framework (124 stars, unattended loop runner with guards), awesome-claude-code-hooks (22 stars, lists 10+ guardrail repos).
- Public worry, with each post's own link:
  - https://news.ycombinator.com/item?id=47278720 : Claude Code ran a Terraform command that wiped a production database; 145 points, 158 comments, about 6 months ago (opened this run).
  - https://news.ycombinator.com/item?id=47550282 : agents getting around soft rules; filesystem limits belong at the OS level; 635 points, 329 comments, about 6 months ago (opened this run).
  - https://news.ycombinator.com/item?id=46268419 : replies under "Claude CLI deleted my home directory", tactics traded (separate users, hooks, snapshots).
  - GitHub issues on anthropics/claude-code, read through a mirror, not opened on GitHub this run: #37686 (scheduled `claude -p` runs billed an API account over $1,800 in two days), #76938 (unwatched loop, about $245 in API calls), #22638 and #45382 (CLAUDE.md rules ignored, work lost), #10077 (home directory deleted), #90629 (17-hour unattended job shipped with bugs).
- What changed since Oct 23: "no one sells guardrails" is false now ($19 pack, $49 to $59 audit, free hook packs), and none of them shows sales. The one angle no seller owns is scheduled and unattended runs (bills from cron runs, runaway overnight jobs, rules that drift between runs).

## 2. The offer (proposed, for Todd's call)
- Name: Unattended Agent Kit, by ProofNotFluff. Faceless: the brand sells it.
- Promise: Let your agent run while you are away, with rules it reads first and checks that stop the run when one fails. (Not "cannot break your rules": no file can promise what a model does; the Legal desk line is below.)
- Price: $79 one time, the founding price for the waitlist. Bottom of the $79 to $99 band because the closest safety products sell at $19 to $59 with no sales shown, and ClaudeKit's $99 buys a much broader framework.
- Inside (planned; the page says it is in build): the layered layout with templates (router, handoff, constitution, decisions log), the constitution template (money, accounts, sending, deleting, secrets, stop words), the preflight and gates (context budget, send approval, secrets and personal-data scan, delete guard), planted-failure tests for every gate, Claude Code permission presets and a blocking hook, one scheduled job end to end, a setup guide.
- Not for: people who want a hard sandbox, who watch every step, who want spending or sending without review, who need a certification, or who will not edit a rules file.
- Free lite version (the proof): launches/agent-kit/lite.tar.gz, MIT. Router, handoff, constitution and decisions templates, an example skill, the preflight, the context gate (its budget set to 8,192 bytes so it binds below the three caps) and 9 planted-failure tests. Python 3.8 or later, nothing to install. Leak scan: 0 findings (see gates).
- Credit: the Interpretable Context Methodology, Jake Van Clief and David McDermott, MIT, arXiv 2603.16021, https://github.com/RinDig/Interpretable-Context-Methodology-ICM (title, authors and license read from the paper this run; the GitHub page could not be opened).

## 3. The draft page
- docs/unattended-agent-kit/ from site/pages.json kind "agentkit" (tools/agentkit_site.py, its --selftest reruns the lite kit and fails if a terminal line on the page no longer matches). Draft: noindex, off the sitemap, index, hub and search, linked from nowhere.
- Waitlist: shows "Waitlist opens soon" until the spec has kitForm (Todd makes the Kit form). Lite link shows only once the spec has liteUrl.

## Gates
(filled as each verdict comes in)

## 4. Channels (inside our rules; nothing runs before Todd's go on the page)
- No word needed after the page go: question pages on proofnotfluff.com for the questions buyers search, each through the question-page gates, each ending on the waitlist. First five: how to run Claude Code on a schedule safely; how to stop Claude Code deleting files; why a scheduled claude -p run bills your API account and how to cap it; CLAUDE.md rules ignored, and what enforces them; what --dangerously-skip-permissions turns off.
- Needs Todd's go once: the free lite repo published on GitHub under the brand's account (a public repo with topics and a README that ends on the waitlist).
- Needs Todd's word each time (posts in the brand's name on someone else's site): a pull request to the awesome-claude-code-hooks list and similar lists; a Show HN post; a Product Hunt launch; a dev.to write-up. No Reddit, no ads, no spend.
- Not proposed: the trades audience on our Instagram and Facebook carousels, the Monday email and the lead pages (wrong buyer).

## 5. Kill rule (proposed)
- Clock starts the day the page and the lite repo both go live (Todd's go). Day 21: 30 or more confirmed waitlist sign-ups (Kit double opt-in) means build the kit; under 30 means park the case again with the counts. A count from any paid or forum post is reported apart from search and GitHub.
- After a build: 10 sales at $79 within 30 days of the kit going on sale, or it is retired from the shop.

## Open before anything sells
- The paid kit's source is already public: this repo (proofnotfluff-pins) is public and holds the full system the kit is built from. Selling it means the repo goes private first, which means the site moves off GitHub Pages (coo/OPPORTUNITIES.md, Plan v2 item 6).
- launches/WIRING.json covers lead products only; the kit needs an entry or a written "na" per piece before its checkout goes on the page.
