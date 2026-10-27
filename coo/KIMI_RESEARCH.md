# Kimi research rounds (Oct 25, 2026)

Todd, Oct 25, 2026, live chat: turn Kimi K3.1 Pro into a research master that finds where the market opportunity sits and where ProofNotFluff can fill the gaps: forums and reviews, what digital products and services land and what does not, white space, public databases beyond the City of Chicago, and places AI takes things to the next level.

Kimi is run by hand only (Plus plan, personal interactive use; coo/KIMI_AUDIT.md). It never builds, posts, spends or edits anything. Its job is the front end of the radar: find evidence and candidates. Our own gates still decide (scout/RUBRIC.md: scorer, then the demand, data-legal and redteam reviewers, then Todd's go).

## Why it is aimed this way
Our scout already finds public-data ideas; the reviewers kill most of them for a free substitute or a richer rival, and the live products have 0 payers and 0 replies. More ideas are not the gap. Evidence of buyer pain and willingness to pay, and data nobody packages yet, are. So the rounds start with the buyers we already have (R0: why 0 replies, the wrong buyer, offer form, channel or price), then buyer pain (R1), the market (R2), data (R3, R4), and a cross-model kill pass last (R5). R0 is the round most likely to move the first payer.

## The rounds
| Round | Asks | Output (brief section 9) | Lands in |
|---|---|---|---|
| R0 | For our four live buyers: who pays anyone for leads today, in what form, through which channel, and why we get 0 replies | Schema E, live buyers | coo/DECISIONS proposal to Todd; nothing changes without his word |
| R1 | Which small B2B trades complain in public about finding work, what they pay now, which public record would fix it | Schema A, pains | research_notes/kimi-<date>-r1.md (our summary) |
| R2 | Which public-data and lead products actually sell, how they get customers, what their customers complain about | Schema B, products and gaps | research_notes/kimi-<date>-r2.md |
| R3 | County, state and federal datasets with a business event a trade would pay for, Cook County and Illinois first | Schema C, ideas | scout/candidates after verification |
| R4 | Public records locked in PDFs, agendas and free text that AI can now turn into a list | Schema C, ideas | scout/candidates after verification |
| R5 | Red team: kill our top-ranked ideas | Schema D, verdicts | advisory objections for the fix round |

Repeat R3 and R4 every two weeks with a new Focus line (another metro, another record type). R5 runs after the scorer ranks the new candidates.

## How Todd runs it (about 10 minutes of his time a round, the rest is Kimi's)
1. In Kimi, start a new task with web search on. Attach coo/kimi/RESEARCH_BRIEF.md.
2. Paste R0. When it finishes, paste R1 in the same task, then R2.
3. Start a second Kimi task with the brief attached. Paste the SUMMARY lines of R0 to R2 and the SKIP LIST from R1 at the top of your message, then R3. When it finishes, paste R4 in that task. (Long replies crowd a single chat, so the heavy rounds get a fresh one.)
4. Copy each reply whole into one Claude chat with "Kimi R0 reply" (R1, ...) on top.
5. For R5, Claude sends a candidates file; attach it with the brief in a new Kimi task and paste R5.

## Lessons from R0 to R6 (Oct 25 to 26)
- Attachments did not always reach Kimi Work (R6). Write each prompt self-contained: the context, the evidence rules and the schema pasted in, the brief only as a backup.
- Kimi is strong on seller, pricing and program pages (R0, R2, R6 kept) and weak on owners' own words: R1 cited shifting Trustpilot list pages and was set aside. Ask for each review's own link, or skip owner voices.
- The trust check runs per round (intake step 7). A site that blocks our fetcher counts as unproven, not invented.
- No paid channels (Todd, Oct 26, 7:09 pm). Research may list prices, but proposals stay at $0 unless Todd says otherwise.

## What Claude does with a reply (intake)
1. Save the reply to data/work/kimi/<date>/<round>.txt and run `python3 tools/kimi_intake.py read <file>`. It parses the JSON, normalizes dashes, drops quotes over 15 words, refuses emails, phones and usernames, runs the scorer's own schema and kill rules (K1 to K5) on every idea, flags duplicates of our products and candidates, and writes the URL list to check.
2. Open every URL on that list with WebFetch in the same chat, and record each with `kimi_intake.py mark <date> ok|dead|mismatch <url> ...`. A source that is dead or does not say what Kimi says is a mismatch. The rubric's rule stands: every source is fetched and read by us, this run.
3. `kimi_intake.py promote <date> <slug>` copies an idea into scout/candidates/<slug>.json only when every one of its URLs is marked ok, no kill rule fires and the slug is new. Ideas with a dead or mismatched source are fixed with our own sources or left out.
4. `python3 tools/opportunity_score.py`, then the radar's reviewers (.claude/skills/radar/SKILL.md step 4) on the top ideas; Decide rows go to Todd as usual.
5. R1 and R2 become one research note each in our own words (no quotes over 15 words, no usernames), and their pains and gaps are cited in candidate files where they apply.
6. R5 verdicts do not vote. Each FAIL reason becomes an objection the fix round must answer with sources.
7. A round with 2 or more dead or mismatched sources in its first 10 checked (at least 5 checked; a site that refuses our fetcher does not count) is set aside whole, noted in the log, and the prompt is tightened before the next round.

## R0, why our live buyers have not replied

```
Round: R0, our live buyers. Read the attached brief first; it binds this task, including its evidence rules (section 8) and output schemas (section 9).
Focus: the four buyers we already sell to: post-construction cleaning companies, pest control companies, vendors to restaurants (hood cleaning, grease trap, POS), and vendors to newly licensed businesses. Chicago and Austin first, then anywhere in the US.

The question: do these exact trades pay anyone for leads today; in what form (per lead, a monthly list, pay on close, a bid service, ads); through which channel did the seller reach them; and so, is our 0 replies on about 57 cold emails most likely the wrong buyer, the wrong offer form, the wrong channel or the wrong price?

How to work:
1. For each buyer, find sellers that sell leads, lists, bid feeds or appointments to that trade, and open their pricing pages. Record the form and the price as the page states it.
2. Find how those sellers reach the trade: trade associations and their vendor programs, trade shows, Facebook-style groups that are public, marketplaces, search pages that rank, cold email, phone teams, software the trade already uses (field service and route software with built-in lead or marketplace features).
3. Read the trade's own words (forums, reviews of lead sellers, trade magazine articles) on buying leads: what made them pay, what made them cancel, whether they read cold email at all, and what they want instead.
4. For each buyer, give a diagnosis with evidence and the one change most likely to get a first payer. Our options include a different buyer inside the same data, a different form (pay per lead, a one-time list, a free week), a different channel inside our rules, or a different price.

Do not tell us what we want to hear. If these trades do not buy leads in any form, say it.

Reply in exactly this shape:

R0 | DATE: (today) | SEARCHES RUN: n | PAGES OPENED: n | BLOCKED: sites that refused you

SUMMARY: four plain sentences, one per buyer: their diagnosis and the change.

Then one fenced json block in Schema E.
```

## R1, buyer pain mining

```
Round: R1, buyer pain mining. Read the attached brief first; it binds this task, including its evidence rules (section 8) and output schemas (section 9).
Focus: small business-to-business service companies in the US that win work by reaching the right building, project or business at the right moment.

The question: which small-business buyers say, in their own words and in public, that finding good jobs or customers is painful and expensive; what do they pay today to solve it; and which of those pains could a public record solve better than what they use now?

How to work:
1. Start wide. Run searches like these, swapping the trade (commercial cleaning, pest control, hood cleaning, grease trap, fire protection, elevator, roofing, restoration, pressure washing, parking lot striping, signage, commercial HVAC, security systems, commercial insurance, equipment leasing, POS and payments, linen and uniform, waste hauling):
   - "where do you get your commercial leads" [trade]
   - "[lead seller] leads waste of money" or "cancelled [lead seller]" (Angi, Thumbtack, HomeAdvisor, Yelp Ads, Bark, Networx, BuildZoom, ConstructConnect, Dodge, Construction Monitor, Shovels, Apollo, ZoomInfo, Data Axle)
   - "how do I find new restaurants before they open", "how to find new construction projects to bid", "how to get commercial contracts" [trade]
2. Read where owners talk: Reddit (r/sweatystartup, r/smallbusiness, trade subreddits), ContractorTalk, trade association forums, Quora, BiggerPockets, Indie Hackers. Read reviews of the lead sellers above on Trustpilot and BBB. Skip G2 and Capterra unless you can open the page and their terms allow it; if you skip them, say so under BLOCKED. Read only.
3. Owners' own words are the point of this round: open at least 25 pages, and make at least 15 of them forum threads or reviews written by owners, not seller pages. Go deep on the 6 to 10 trades with the strongest signal. For each: the pain, how many separate threads show it, what they pay now (per lead, per month, per job), the typical job size, and what they wish existed.
4. For each pain, name the public record that would answer it (a permit, an inspection, a license, a filing, a violation, a contract award, a registration), or write "none".
5. Look for the opposite too: trades that say referrals give them all the work they can handle. They are not buyers; list them so we skip them.

Do not tell us what we want to hear. If the evidence says small operators will not pay for leads, say it plainly. Stop at 10 pains.

Reply in exactly this shape:

R1 | DATE: (today) | SEARCHES RUN: n | PAGES OPENED: n | BLOCKED: sites that refused you

SUMMARY: five plain sentences: which buyers hurt most, what they pay now, where public records fit, and the one finding that surprised you.

SKIP LIST: trades that do not need leads, one line each with a URL.

Then one fenced json block in Schema A.
```

## R2, what is selling and what is not

```
Round: R2, what is selling and what is not. The attached brief binds this task, including sections 8 and 9. If R1 is earlier in this conversation, use its pains.
Focus: paid products and small services built on public records or open data and sold to small businesses, plus the low-priced lead and data tools those same buyers already pay for.

The question: which of these have real paying customers, how did they get them, what do their own customers complain about, and where is a gap a one-person shop could take?

How to work:
1. List 12 to 15 sellers, each with its pricing page open. If R0 is earlier in this conversation, its sellers count toward the list only once you add their traction; spend the rest of the round on sellers R0 did not find. Search TrustMRR, Indie Hackers, Acquire.com, Microns, Flippa, Product Hunt, and the G2 and Capterra categories for sales leads, construction leads and permit data, plus searches like "building permit leads subscription", "new business leads list monthly", "health inspection leads", "liquor license leads", "UCC filing leads", "government contract award leads", "new LLC filings list", "public records leads for contractors".
2. For each seller, open its own pricing page. Record the list or tool, the public source it rests on, the buyer, the price, and traction you can verify: revenue shown on TrustMRR or Indie Hackers, a sale listing with revenue on Acquire or Flippa, review counts, a stated customer count, years trading. Write "no traction found" when that is the truth.
3. For the ones with traction, find how they get customers: cold email, search, a marketplace, an app store, partners, a community. Use their blog, their pages that rank, their affiliate program, their founders' own growth posts.
4. Read their reviews and any shutdown or sale posts. What do customers complain about (stale data, wrong contacts, too broad, too expensive, hard to cancel)? Why did the failed ones fail?
5. Name the gaps: a buyer served badly, a city or county nobody covers, a freshness gap (weekly where a daily signal exists), a missing "why now" field, a price gap, or a format gap (a raw dump where the buyer wants a call list).

Reply in exactly this shape:

R2 | DATE: | SEARCHES RUN: n | PAGES OPENED: n | BLOCKED:

SUMMARY: five plain sentences: what is landing, what is not, how the winners get customers, and the clearest gap.

Then one fenced json block in Schema B.
```

## R3, public data white space

```
Round: R3, public data white space. The attached brief binds this task, including sections 5, 6, 8 and 9. If R1 and R2 are earlier in this conversation, tie every idea to their pains and gaps.
Focus: Cook County and the State of Illinois only. Other metros come in later runs with their own Focus line.

The question: which public datasets record a business event that a specific trade would pay to hear about within days, and that nobody packages well for that trade yet?

A dataset qualifies only if all of these hold:
- One record is a business, a commercial building or a project, never a private person or a home.
- It records a dated event: filed, issued, failed, cited, awarded, registered, cancelled, expired or approved.
- It refreshes at least weekly and has at least 100 events a month in the area we would sell.
- The event creates a job or a sale for someone within weeks (a failed fire inspection needs a fire protection contractor; a new liquor license needs POS, insurance, signage and linen vendors; a county contract award needs subcontractors and suppliers).
- Its terms allow commercial reuse.

Places to start (open each and check; do not trust this list): Cook County open data and offices (Assessor, Treasurer, Clerk, Board of Review, Department of Public Health, procurement and contract awards, Land Bank); Illinois Secretary of State business data, Liquor Control Commission, Department of Public Health, Department of Financial and Professional Regulation, Illinois EPA, Office of the State Fire Marshal (elevators, boilers, storage tanks), Capital Development Board, Illinois Procurement Bulletin, IDOT lettings; federal records filtered to a county (SAM.gov and USAspending awards, SBA loans, OSHA, EPA ECHO, FCC, Census business formation).

Before you include an idea:
1. Count the events with a query URL or a page that states the number. Cannot count it: null, and say why.
2. Search for the free substitute (the agency's own alert, search or download a buyer would actually use). Record the URL or the searches you ran.
3. Search for competitors selling it, with prices, and say whether they ship richer fields than we would.
4. Find the buyer count from a primary source (a state license roster, Census County Business Patterns, a trade association) and how we would reach an owner by email.
5. Write the "why call now" line a buyer would read.
6. Say, in kimi.inferred, whether the list could be sold to one company per area of the county, and how many areas the monthly event count would support at 10 or more events per area. Buyers pay for exclusive leads; a list every rival also gets is the weak spot of our current products.

Reply in exactly this shape:

R3 | DATE: | FOCUS: | DATASETS OPENED: n | BLOCKED:

SUMMARY: five plain sentences, best idea first, and the richest area you did not have time to finish.

REJECTED: one line per dataset you checked and threw out, with the reason (free substitute, too few events, person-level, terms, rival). This list matters as much as the ideas.

Then one fenced json block in Schema C, at most 5 ideas, best first, round "R3".
```

## R4, the AI unlock

```
Round: R4, the AI unlock. The attached brief binds this task, including sections 5, 6, 8 and 9. If earlier rounds are in this conversation, use their pains and gaps and do not repeat their ideas.
Focus: public records that are free but locked in PDFs, scans, meeting agendas, free-text fields or one-record-at-a-time search pages; Illinois first, then anywhere in the US.

The question: where is valuable business information public but unusable without a person reading it, so nobody sells it cleanly yet, and AI can now turn it into a clean weekly list a trade would pay for?

Where to look (check each yourself):
- Agendas and minutes of zoning boards, plan commissions, city councils, liquor commissions, county boards, school boards and park districts: special uses, variances, new liquor licenses, approved developments, awarded contracts.
- Bid and award notices posted as PDFs by cities, counties, school districts, transit and water agencies: who won, what was bought, when it renews.
- Public notices where the subject is a business or a project (never foreclosures on homes or anything about a private person).
- Free-text fields inside open datasets (permit work descriptions, inspection comments, violation narratives) where a classifier finds a trade's jobs that keyword filters miss.
- Scanned filings and slow search portals that show one record at a time.
Check each source's terms. If it forbids automated collection, drop it and say so.

For each idea also answer, inside kimi.aiAngle and kimi.inferred:
- What exactly the AI does (read a PDF table, classify a description, match a name to a business, pull a date), how accurate it must be, and how we would check it.
- How many useful records a month, counted from real pages you opened (for example, the items on the last 4 agendas).
- Why nobody has done it: too small, too messy, or already done (search for it and say what you found).

Reply in exactly this shape:

R4 | DATE: | FOCUS: | SOURCES OPENED: n | BLOCKED:

SUMMARY: five plain sentences.

REJECTED: one line per source thrown out, with the reason.

Then one fenced json block in Schema C, at most 4 ideas, round "R4" at the top level and in kimi.round, with kimi.aiAngle filled in for every idea.
```

## R5, red team (after our scorer ranks the new ideas)

```
Round: R5, red team. Two files are attached: our brief (it binds this task, including sections 8 and 9) and a candidates file with the ideas our scorer ranked highest and our sources.

Your job is to kill these ideas. For each one, argue as hard and as honestly as you can that it makes $0 by Jan 31, 2027, then say whether your best argument holds.

For each idea:
1. Open its data source and terms yourself. Is the count real, is the cadence real, is reuse allowed?
2. Search for a free substitute the buyer would actually use, and for any competitor cheaper than our price or richer in fields. Use at least five different phrasings.
3. From the buyer's own words in public (forums, reviews), not from our file, would they pay our price?
4. Name the one number in our file you trust least, and why.
5. If it survives, name the cheapest test inside our rules (no ads, no forum posts, no spend) that would show demand in 14 days, and the pass mark.

Reply: R5 | DATE: | IDEAS REVIEWED: n, then one fenced json block in Schema D.
```

## R6, channel map for our buyers (Todd, Oct 26, 5:58 pm: "let's do number 1")

Why: rounds R0 to R4 point at the channel, not the data. R6 maps where our buyers can be reached without ads or forum posts. Intake as above; a channel becomes a proposal to Todd, never an action (joining, listing, sponsoring or attending needs his word, and anything with spend is a quest with the price).

```
Round: R6, channel map. Read the attached brief first; it binds this task, including sections 2, 5, 8 and 9 (Schema F).
Focus: Chicago and Illinois first, then national channels that reach Chicago firms. Buyers: pest control companies, post-construction and commercial cleaning companies, and vendors to restaurants (hood cleaning, grease trap).

The question: where can a small faceless data business reach the owners of these firms, other than cold email, ads or forum posts, and what does each channel cost in money and in the owner's time?

Look in this order, and open each page yourself:
1. App and partner marketplaces inside the software these trades already run on. Pest: FieldRoutes, PestPac and WorkWave, GorillaDesk, Briostack, ServiceTitan. Cleaning: Jobber, Housecall Pro, Swept, Janitorial Manager, ServiceTitan. Restaurants: Toast and Square partner or integration programs. For each: is there a public marketplace or integrations directory, can a data or lead provider list there, what does applying take (an API integration, a fee, a review), and are any lead or data sellers already listed?
2. Trade associations with vendor, allied or supplier memberships: National Pest Management Association, the Illinois pest control association, ISSA, BSCAI (Building Service Contractors Association International), IKECA (kitchen exhaust cleaning), BOMA Chicago, the Illinois Restaurant Association. For each: member count as stated, how many in Illinois, the vendor membership cost, and what it includes (directory listing, member email, newsletter ad, event table).
3. Trade media and newsletters these owners read (pest, cleaning and kitchen exhaust trade magazines and their e-newsletters): readership as stated, sponsored-content or classified rates, and whether a small vendor can buy a single placement.
4. Events in the next 120 days in Illinois or national events that Chicago firms attend: dates, vendor cost, and whether a person must attend.
5. Referral and partner programs at businesses that already sell to these trades and might resell or bundle a lead list (equipment and chemical suppliers, insurance agencies for contractors, franchise systems).

Rules for this round:
- Count only what a page states. Member and reader counts are bare numbers or null.
- Mark needsAPerson true when someone must attend, present or sign in their own name; we are faceless, so those rank lower but stay on the list.
- Mark needsSpend true for any cost; list it anyway with the price.
- Name any lead or data seller already present in a channel (rivalsThere): it proves the channel works for sellers like us.
- Do not sign up, apply, message or post anywhere.

Reply in exactly this shape:

R6 | DATE: | CHANNELS OPENED: n | BLOCKED:

SUMMARY: five plain sentences: the best three channels by reach per dollar and per hour of the owner's time, what each would cost to try, and the one surprise.

REJECTED: one line per channel checked and thrown out, with the reason (closed to vendors, too costly for the reach, no Illinois members, needs a person every time).

Then one fenced json block in Schema F, at most 15 channels, best first, with top3 filled in.
```
