# ProofNotFluff research brief for Kimi (as of Oct 25, 2026)

Attach this file to every Kimi research task. It is the context the prompts assume. It holds no person's details.

## 1. What the business is
- ProofNotFluff LLC, Chicago, Illinois. One owner, no staff, run with AI agents. Site: proofnotfluff.com.
- Faceless: the brand sells, not the founder. No product may need the founder on camera, on sales calls or billing hours.
- What we sell: lead lists built from public records, sold by monthly subscription to small business-to-business service companies. A list tells a company who to call this week and why now (a new permit, a failed inspection, a new license).
- Checkout: Gumroad memberships. Delivery: a password-locked members' page with a CSV download, refreshed by code every day or week at $0.

## 2. What is live and what it has earned
| Product | Price | Buyer | Since |
|---|---|---|---|
| Chicago construction cleaning leads | $29 a month | post-construction cleaning companies | Oct 17 |
| Austin construction cleaning leads | $29 a month | same, Austin | Oct 18 |
| Chicago restaurant inspection leads | $39 a month | pest control, hood cleaning and other restaurant vendors | Oct 18 |
| Chicago new business licenses | $29 a month, 7-day trial | vendors that sell to new businesses | Oct 22 |
| Chicago pest daily list, founding seat | $149 a month, 3 seats | pest control companies | Oct 24 |
| Free pages: weekly samples, a "New in Chicago" page, question pages, two calculators | free | traffic | Oct 17 to 24 |

Results to date: 0 paying customers, 0 replies to cold email. Older experiments: an Etsy shop of $2.99 downloads (32 listings, 0 orders, paused) and a $79 cash flow workbook on Gumroad (0 sales).

Channels we can use: cold email from our own domain under approved templates (about 25 a day per sender, plain text, no links, to a business inbox or a named decision-maker at a business), free sample pages and search, daily organic posts on Instagram and Facebook. Not allowed: paid ads without the owner's approval, posting on Reddit or forums, buying lists, any spam.

## 3. The goal
$1,000 net in one calendar month by Jan 31, 2027. That is about 7 seats at $149, or about 38 subscribers at $29, or a mix. A new idea matters only if a first payer is plausible by mid-December 2026 without an existing audience.

## 4. What we are good at
- Code that pulls open data (Socrata, ArcGIS, CKAN, CSV and Excel downloads, simple web pages) on a schedule, cleans it, joins datasets, removes duplicates and builds a members' page, all at $0.
- AI that turns messy public records into clean rows: classifying free-text permit descriptions, reading PDF agendas and scanned notices, matching a record to the business behind it.
- Domain knowledge the founder brings: corporate finance and planning, e-commerce finance (Amazon, Shopify, TikTok Shop, retail), and running two short-term rental homes.

## 5. Hard limits (an idea that breaks one is out)
- Business-level records only. Never homeowners, residents, tenants, voters, eviction defendants, named private people, or skip tracing.
- Never medical, legal filing, immigration or investment advice products.
- No health, wellness, supplement or longevity products or buyers before September 2027.
- The data's terms must allow commercial reuse.
- $0 spend to test. Nothing deceptive, nothing against a platform's terms.

## 6. Already built, tried or dropped (do not propose again without a genuinely new angle, and say what is new)
- Built: construction permits for cleaning companies (Chicago, Austin); restaurant inspections for pest and hood vendors (Chicago); new business licenses (Chicago); a daily pest list (Chicago).
- Spec only: Chicago elevator citations, Chicago exterior repair citations. Parked: Seattle permits, NYC restaurant pest citations, NYC liquor license applications, truck insurance cancellations (FMCSA), OSHA inspections, federal alcohol permits (TTB).
- Dropped Oct 23, with the reason:
  - New trucking companies (FMCSA): competitors at $39 to $49 ship phone, email and officer fields we will not ship; free tiers exist.
  - Colorado new business filings: the State gives the same data free; a rival sends it daily for $49.
  - NYC unsafe facade filings: only 35 to 50 a month, work awarded through engineers and board bids, data free on the City's site, a richer rival at $199.
- Lesson so far: raw public data is a commodity (national permit data sells from $599 a month; scrapers on Apify cost a few dollars per 1,000 rows). Ideas die when the agency's own free portal or a richer competitor already serves the buyer. Our edge has to be the packaging: a narrow buyer, fresher than anyone, the "why call now" signal, and work AI makes cheap that others still do by hand.

## 7. How your findings will be used
Every source you cite is opened again by a second AI before anything is built. Ideas go through our scorer and three independent reviewers (demand, data and legal, red team). Invented links, numbers or quotes waste a round and get the whole reply set aside, so leave out anything you cannot point to.

## 8. Evidence rules (every round)
1. Open every page you cite. If a page will not open, do not cite it; name the site under BLOCKED.
2. Every source is {"url": "...", "date": "YYYY-MM-DD"}: the date it was posted or published, or the day you read it when it has no date.
3. Quotes are 15 words or fewer. No usernames, and no person's name, email or phone, ever.
4. For Schema C (R3, R4), every source date must be within the last 12 months (terms of use pages: 10 years), or our scorer gives that factor 0. For Schemas A, B, D and E, prefer the last 24 months and mark older sources "old".
5. Count, never estimate: a count is a number a page states or a query you ran (for Socrata portals, a $select=count(*) URL with a date filter; put that URL in recordsSource.url and paste the exact value the portal returned, such as [{"count":"412"}], in kimi.observed). If you could not run the query, the count is null, with the reason.
6. Label claims OBSERVED (a source states it) or INFERRED (your reasoning).
7. Read only. Never post, comment, sign up, download software or message anyone. Skip any site whose terms forbid automated collection.
8. Honest beats hopeful. Fewer real findings beat many padded ones. "Not found" is a useful answer.
9. Plain words, no em or en dashes, valid JSON (double quotes, no trailing commas, no comments).

## 9. Output schemas (copy the keys exactly)

Schema E, live buyers (round R0):
```json
{"round": "R0", "buyers": [
 {"buyer": "one of the four live buyers in section 2",
  "paysFor": [{"form": "per lead|monthly list|pay on close|bid service|ads|none found", "seller": "", "price": "as the source states it, or null", "url": "", "date": ""}],
  "channels": [{"channel": "how a seller reached them: cold email, search, trade show, association, marketplace, referral, phone", "url": "", "date": "", "label": "OBSERVED"}],
  "wants": "the offer form they say they want, in your words",
  "evidence": [{"url": "", "date": "", "quote": "15 words or fewer", "kind": "forum|review|video|article|job post", "label": "OBSERVED"}],
  "diagnosis": "wrong buyer|wrong offer form|wrong channel|wrong price|unclear", "why": "two sentences", "change": "the one change most likely to get a first payer", "confidence": "high|medium|low"}]}
```

Schema A, pains (round R1):
```json
{"round": "R1", "pains": [
 {"id": "p1", "buyer": "the trade in plain words", "pain": "one line in your words", "threads": 0,
  "paysNow": {"amount": "one figure with its unit, as the source states it, or null", "for": "what they buy", "source": {"url": "", "date": ""}},
  "jobValue": {"amount": "typical job size", "source": {"url": "", "date": ""}},
  "publicRecord": "the record that would solve it, or none",
  "evidence": [{"url": "", "date": "", "quote": "15 words or fewer", "kind": "forum|review|video|article|job post", "label": "OBSERVED"}],
  "confidence": "high|medium|low"}]}
```
`threads` must equal the number of entries in `evidence`: one entry per thread or review you opened, each with its own URL. A thread you did not open does not count.

Every example value in these schemas is a placeholder. Replace it or use null.

Schema B, products and gaps (round R2):
```json
{"round": "R2", "products": [
 {"name": "", "url": "", "sells": "one line", "dataSource": "", "buyer": "", "price": "$ a month or one time",
  "traction": [{"what": "verified revenue, review count, years trading", "url": "", "date": ""}],
  "acquisition": "how it gets customers (OBSERVED or INFERRED)",
  "complaints": [{"url": "", "date": "", "quote": "15 words or fewer"}],
  "verdict": "landing|flat|failing|dead|unknown", "gap": "what a narrower, faster seller could take"}],
 "gaps": [{"id": "g1", "gap": "one line", "buyer": "", "why": "one line", "products": ["names above"], "confidence": "high|medium|low"}]}
```

Schema C, ideas (rounds R3 and R4; this is our scorer's own format, so every key matters):
```json
{"round": "R3", "ideas": [
 {"schema": "pnf.opportunity.v1", "slug": "lowercase-words-with-hyphens", "name": "buyer-facing product name", "status": "new",
  "addedAt": "YYYY-MM-DD", "pitch": "one line: what list, for whom, why now", "categories": ["trade words"],
  "provenAbroad": [{"what": "the same model sold in another place or market", "url": "", "date": ""}],
  "buyer": {"who": "the trade that pays", "count": null, "countSource": {"url": "the page that shows the number itself (a Census table URL with NAICS and county, or a roster search result), not a landing page", "date": ""},
            "reach": "how we reach an owner by email", "reachSource": {"url": "", "date": ""}},
  "price": {"monthly": 29, "reason": "why this price, inside $29 to $199",
            "competitors": [{"name": "", "monthly": 0, "url": "", "date": "", "richer": false}],
            "freeSubstitute": {"note": "the agency's own free alert, search or download, if any", "url": "", "date": ""}},
  "demand": {"searchQueries": [{"q": "", "url": "", "date": ""}],
             "aiQueries": [{"q": "a buyer's real question in public, 15 words or fewer", "url": "", "date": ""}]},
  "data": {"publisher": "", "dataset": "", "subject": "what one record describes (a business, a building, a project)",
           "url": "", "apiUrl": "", "cadence": "daily|weekly|monthly", "lastUpdated": "YYYY-MM-DD",
           "recordsPerMonth": null, "recordsSource": {"url": "", "date": ""}, "apiStable": true,
           "license": {"commercialUse": "allowed|forbidden|unclear", "url": "the terms page itself, not the dataset page", "date": "", "note": "the clause that allows or forbids commercial reuse, quoted, 15 words or fewer"}},
  "build": {"days": 0, "maintHoursMonth": 0, "reuses": []},
  "fit": {"samePortal": false, "existingTools": [], "sameBuyerTypes": false},
  "overlap": "a product in section 6 this touches, or empty",
  "kimi": {"round": "R3", "whyNow": "the line a buyer reads", "aiAngle": "what AI does that is hard by hand, or none",
           "freeSubstituteSearched": ["the searches you ran"], "smallestTest": "a $0 test inside section 5 that shows demand in 14 days",
           "killRisk": "the strongest reason this makes $0", "observed": ["claims a source states"], "inferred": ["your reasoning"]}}]}
```
`richer` is true when a competitor ships fields we will not (personal contacts, owner names). `build.days` is your honest guess for one coder with AI; say so in `inferred`.

Schema D, red team verdicts (round R5):
```json
{"round": "R5", "verdicts": [
 {"slug": "", "verdict": "PASS|FAIL", "reasons": ["the three strongest reasons it makes $0"], "numberDoubted": "the number in our file you trust least, and why",
  "freeSubstitute": {"note": "", "url": "", "date": ""}, "rival": {"name": "", "monthly": 0, "url": "", "date": ""},
  "buyerWords": [{"url": "", "date": "", "quote": "15 words or fewer"}],
  "test": "cheapest $0 test inside our rules", "passMark": "the number that means yes"}]}
```
