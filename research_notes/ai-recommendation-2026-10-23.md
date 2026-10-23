# What gets a site recommended or cited by AI assistants (research, Oct 23, 2026)

Scope: ChatGPT (search), Claude (web search), Perplexity, Gemini, Google AI Overviews and AI Mode. Sources dated Oct 2025 to Oct 2026 unless marked OLDER. Studies by tool vendors (Ahrefs, Semrush, SE Ranking, BrightEdge, Peec) are marked as vendor research: they sell the tools that collected the data, and nearly all of it is correlation, not cause.

## Summary (10 lines)

1. HIGH: You cannot be cited if the assistant's search crawler cannot fetch you. Allow OAI-SearchBot (ChatGPT search), Claude-SearchBot and Claude-User (Claude), PerplexityBot (Perplexity), Googlebot (AI Overviews, AI Mode, Gemini). Our robots.txt already allows all; check that no CDN or host setting blocks AI bots.
2. HIGH: Google says AI Overviews and AI Mode use normal Search ranking: be indexed, snippet-eligible, crawlable, original. No special file, markup or "chunking" needed (Google guide, updated Jul 10, 2026).
3. HIGH: Each assistant leans on a different index: Google's (AI Overviews, AI Mode, Gemini), OpenAI's own crawler plus outside providers such as Bing (ChatGPT), Brave Search plus turbopuffer (Claude), Perplexity's own index. Being findable in Google, Bing and Brave covers most of it.
4. MEDIUM: Being talked about elsewhere (brand mentions, YouTube mentions, Reddit or Quora presence, review platforms, earned media) correlates with AI mentions much more strongly than backlinks do. Many large studies agree, but none proves cause, and all sampled big brands.
5. MEDIUM: Answer-first pages with specific, dated, sourced facts get cited more. ChatGPT pulls 44% of citations from the first 30% of a page (Kevin Indig, Feb 2026). Pages with many data points and recent updates are cited more (SE Ranking, Nov 2025).
6. MEDIUM: Freshness helps ChatGPT, Perplexity and Gemini more than Google AI Overviews. Real updates only; fake date bumps are a known spam signal.
7. LOW: Schema.org markup. Ahrefs' before-and-after test on 1,885 pages (May 2026) found no clear effect on AI citations. Google says no special schema is needed. Keep schema for rich results and accuracy, not as an AI lever.
8. NONE: llms.txt. No major provider says it reads llms.txt for search or citations. Google says Search ignores it, and SE Ranking found no effect across 300,000 domains.
9. RISKY: Self-promotional "best X" listicles, fake reviews, Reddit seeding, hidden prompt text, and mass fan-out or city pages all carry penalty, legal or platform-ban risk. Some also backfire: the listicle gets cited while the brand is left out of the answer.
10. MEASURE: Use free first-party reports (Bing Webmaster Tools AI Performance, the Google Search Console Generative AI report) plus a small monthly prompt panel run through official APIs. Do not script the consumer apps; OpenAI, Perplexity, Anthropic and Google terms forbid it.

---

## 1. Which index each assistant uses, and which robots.txt user agents matter

**ChatGPT (OpenAI)**
- OpenAI crawler docs, developers.openai.com/api/docs/bots (OpenAI, undated, read Oct 23, 2026): OAI-SearchBot decides whether a site can be shown in ChatGPT search answers. A blocked site may still appear as a plain navigation link. GPTBot is for model training only. ChatGPT-User fetches pages when a user asks and may not follow robots.txt. Robots.txt changes take about 24 hours. https://developers.openai.com/api/docs/bots
- OpenAI Help Center, "ChatGPT search" (OpenAI, undated, "updated over a month ago"): queries may be shared with third-party search providers "such as Bing". https://help.openai.com/en/articles/9237897-chatgpt-search
- Peec AI research note (Peec, Sep 2026, vendor): mapped ChatGPT's server events and found its own index plus about eight outside providers, including Google results reached through scraping vendors and Bing mainly in Deep Research. The Google evidence is a single case. WEAK. https://docs.peec.ai/research/chatgpt-search-result-providers.md
- Search Engine Land on The Information report (Search Engine Land, undated): reported that OpenAI used SerpApi to pull Google results. One secondhand paywalled source. WEAK. https://searchengineland.com/openai-chatgpt-serpapi-google-search-results-461226
- eseospace review of primary docs (eseospace, Oct 13, 2026): no OpenAI statement says Bing indexing or IndexNow improves ChatGPT visibility. It is plausible, not confirmed. https://eseospace.com/blog/bing-webmaster-tools-indexnow-ai-search/
- Ahrefs (Ahrefs, Sep 3, 2025, OLDER, vendor): ChatGPT citations overlapped with Google's top 10 only 7% to 10% of the time, so ChatGPT is not simply a copy of Google. https://ahrefs.com/blog/chatgpt-google-citations

**Claude (Anthropic)**
- Anthropic Help Center article 8896518 (Anthropic, last updated Apr 7, 2026): there are three bots. ClaudeBot collects training data. Claude-User fetches pages when a user asks; blocking it cuts visibility in user-directed search. Claude-SearchBot indexes pages for search quality; blocking it stops indexing for search. Anthropic honors Crawl-delay. https://support.claude.com/en/articles/8896518
- Xponent21 on Anthropic's subprocessor list (Xponent21, Jul 2, 2026): Brave Search has been listed as a web search provider since Mar 2025 and was still listed. turbopuffer was added May 6, 2026; its exact role is not public. https://xponent21.com/insights/claude-web-search-brave-turbopuffer/
- Brave Search crawler help page (Brave, undated): Brave's crawler uses no separate user agent. If Googlebot cannot crawl a page, Brave will not either, so being open to Googlebot keeps you open to Brave. Noindex removes a page. https://search.brave.com/help/brave-search-crawler

**Perplexity**
- Perplexity crawler docs (Perplexity, undated): PerplexityBot surfaces and links sites in answers and is not used for model training. Perplexity-User fetches pages on a user's request and generally ignores robots.txt. Changes take up to 24 hours. https://docs.perplexity.ai/docs/resources/perplexity-crawlers.md
- Perplexity engineering blog (Perplexity, Sep 25, 2025, OLDER): Perplexity runs its own index of more than 200 billion URLs. Pages are split into self-contained passages that are ranked one by one, and recrawl timing is set by a model. https://www.perplexity.ai/hub/blog/architecting-and-evaluating-an-ai-first-search-api
- Cloudflare reported in Aug 2025 (OLDER) that Perplexity used undeclared crawlers to get past blocks. That matters only if you block Perplexity; we do not. https://www.techrepublic.com/article/news-cloudflare-accuses-perplexity-stealth-crawling-violations/

**Google (AI Overviews, AI Mode, Gemini app)**
- Google common crawlers doc (Google, last updated Oct 15, 2026): Google-Extended controls Gemini model training and grounding in Gemini Apps and Vertex AI. It does not affect inclusion or ranking in Google Search. https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers
- Google "AI features and your website" (Google, last updated Dec 10, 2025): AI Overviews and AI Mode are controlled by Googlebot plus nosnippet, data-nosnippet, max-snippet and noindex, not by Google-Extended. https://developers.google.com/search/docs/appearance/ai-features
- Relevant Audience on Google's Search Console control (Relevant Audience, Aug 2026): a new Search Console setting lets a site opt out of AI Overviews, AI Mode and Discover AI. Google says it is not a ranking signal for regular results. It rolled out worldwide on Aug 31, 2026. https://www.relevantaudience.com/geo/google-search-generative-ai-control-global-rollout/
- Ahrefs (Ahrefs, Mar 2, 2026, vendor, 863K SERPs): only 38% of AI Overview citations now come from the top 10 for the original query, down from 76% in Jul 2025. Ahrefs puts this down to fan-out sub-queries under Gemini 3. Ranking for many related sub-questions matters, not just the head term. https://ahrefs.com/blog/ai-overview-citations-top-10/

**What blocking or allowing does, in short**

| User agent | Owner | Purpose | If blocked |
|---|---|---|---|
| OAI-SearchBot | OpenAI | ChatGPT search index | Not shown in ChatGPT search answers |
| ChatGPT-User | OpenAI | Live fetch for a user | May ignore robots.txt anyway |
| GPTBot | OpenAI | Training | No effect on search, per OpenAI |
| Claude-SearchBot | Anthropic | Claude search index | Not indexed for Claude search |
| Claude-User | Anthropic | Live fetch for a user | Claude cannot read the page for users |
| ClaudeBot | Anthropic | Training | Training opt-out only |
| PerplexityBot | Perplexity | Perplexity index | Likely dropped from Perplexity answers |
| Perplexity-User | Perplexity | Live fetch for a user | Generally ignores robots.txt |
| Googlebot | Google | Search, AI Overviews, AI Mode, Brave follows it | Gone from all of Google |
| Google-Extended | Google | Gemini training plus Gemini app grounding | Out of Gemini app grounding, no Search effect |
| Bingbot | Microsoft | Bing, Copilot, likely part of ChatGPT | Out of Bing, Copilot, maybe ChatGPT |

- Cloudflare (MIT Technology Review, Jul 1, 2025, OLDER): Cloudflare began blocking AI bots by default for sites it hosts. If proofnotfluff.com's DNS is proxied through Cloudflare, check the AI bot settings so search crawlers are not blocked. https://www.technologyreview.com/2025/07/01/1119498/cloudflare-will-now-by-default-block-ai-bots-from-crawling-its-clients-websites/

## 2. Measured studies of what correlates with being cited

**Brand mentions and third-party presence (strongest signal, correlation only)**
- Ahrefs, 75K brands (Ahrefs, Dec 12, 2025, vendor): YouTube mentions (about 0.74) and branded web mentions (0.66 to 0.71) correlate most with AI mentions in ChatGPT, AI Mode and AI Overviews. Backlink counts and page counts correlate weakly. The sample covers only DR 40+ brands. https://ahrefs.com/blog/ai-brand-visibility-correlations
- Earlier Ahrefs AI Overviews version (May 26, 2025, OLDER) found the same pattern. https://ahrefs.com/blog/ai-overview-brand-correlation/
- SE Ranking via Search Engine Journal (SEJ, Nov 26, 2025, vendor, 129K domains, 216K pages): referring domains were the strongest single predictor of ChatGPT citations. Heavy Reddit or Quora presence and listings on review platforms (Trustpilot, G2, Yelp) went with about 3 to 4 times more citations. https://www.searchenginejournal.com/new-data-top-factors-influencing-chatgpt-citations/561954/
- Chen, Wang, Chen, Koudas, arXiv 2509.08919 (University of Toronto, Sep 10, 2025, OLDER, academic): AI search engines show a strong bias toward earned, third-party media over brand-owned pages, compared with Google. https://arxiv.org/abs/2509.08919
- Semrush (Semrush, Nov 10, 2025, vendor, 230K prompts, 100M citations): Reddit and Wikipedia top ChatGPT's sources, but Reddit's share fell from about 60% to about 10% of responses within weeks. Source mixes are volatile. https://www.semrush.com/blog/most-cited-domains-ai/

**Answer-first structure, specificity, statistics**
- Kevin Indig, Growth Memo, "The science of how AI pays attention" (Feb 16, 2026, 1.2M answers, 18K verified citations), summarized by Search Engine Land: 44% of ChatGPT citations come from the first 30% of a page. Cited text uses clear definitions, question headings, and many named entities. ChatGPT only; method only partly published. https://searchengineland.com/chatgpt-citations-content-study-469483 and https://www.growth-memo.com/i/188121887/3-entity-richness
- SE Ranking (same SEJ article, Nov 2025): pages with 19+ data points averaged 5.4 citations vs 2.8. Pages with expert quotes averaged 4.1 vs 2.4. Sections of 120 to 180 words between headings did best. Question-style headings and FAQ sections did slightly worse in raw data, likely because simple support pages use them.
- Critical GEO survey, arXiv 2607.14035 (Martinez, Jul 15, 2026): the Princeton GEO paper's "up to 40%" gains came from a simulator with pages already in context. No GEO technique has shown a stable real-engine effect on being found. Relevance plus true, attributed, extractable facts (figures, definitions, dates) have the best support. Keyword stuffing does nothing or hurts. https://arxiv.org/abs/2607.14035
- Princeton GEO paper (Aggarwal et al., Nov 2023, OLDER): adding statistics, quotes and citations raised visibility in their test engine. Treat as a lab result. https://arxiv.org/abs/2311.09735

**Freshness**
- Ahrefs, 17M citations (Ahrefs, Jul 28, 2025, OLDER, vendor): AI assistants cite content about 26% newer than organic results. ChatGPT shows the strongest pull to newer pages. Google AI Overviews cite slightly older pages than organic. https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content/
- SE Ranking (Nov 2025): pages updated within 3 months averaged 6.0 ChatGPT citations vs 3.6 for outdated ones.
- Note: our lead pages refresh weekly from City data, so freshness is real and visible. That is a genuine advantage.

**Structured data / schema.org**
- Ahrefs before-and-after test (Ahrefs, May 11, 2026, 1,885 treated pages vs 4,000 controls, difference-in-differences): adding JSON-LD had no clear effect on citations in AI Overviews, AI Mode or ChatGPT. It studied pages already being cited only. https://ahrefs.com/blog/schema-ai-citations/
- SE Ranking (Nov 2025): FAQ schema went with slightly fewer ChatGPT citations (3.6 vs 4.2).
- Google guide (Jul 10, 2026): structured data is not required for AI features and no special schema is needed. Keep it for rich results. https://developers.google.com/search/docs/fundamentals/ai-optimization-guide

**"Best X for Y" listicles and comparison pages**
- DataDab (DataDab, May 2026, consultancy, 100 B2B prompts via API, 328 citations): 41% of cited URLs had "best" or "top" in the path and 25% were comparisons. Small sample, and it ran through the API, not the ChatGPT app. https://www.datadab.com/research/what-chatgpt-actually-cites
- Lily Ray, SEJ (Jun 18, 2026, 100 queries, 323 citations): when a brand's own "best" listicle was cited in an AI Overview, the brand was left out of the recommendation 69% of the time. She also saw organic drops at 40+ sites using the tactic. https://searchenginejournal.com/why-calling-yourself-the-best-could-be-helping-your-competitors-win-in-ai-search/579778/
- Lily Ray, SEJ (Feb 5, 2026, 7 sites, suggestive only): sites heavy on self-promotional listicles lost 29% to 49% of visibility after Jan 2026. https://www.searchenginejournal.com/is-google-finally-cracking-down-on-self-promotional-listicles/566529/

**Ranking still matters, more widely than the head term**
- BrightEdge (BrightEdge, Sep 18, 2025, OLDER, vendor): 54.5% of AI Overview citations came from pages that rank organically, mostly at positions 21 to 100. https://www.brightedge.com/resources/weekly-ai-search-insights/rank-overlap-after-16-months-of-aio
- Seer Interactive (Seer, Nov 4, 2025, 3,119 queries, 25M impressions): queries where a brand is cited in the AI Overview get about 35% higher organic CTR than uncited ones. Correlation. https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-september-2025-update

**Local note for trade buyers**
- Google Business Profile rules (Google, undated): a virtual office or mailbox is not eligible. ProofNotFluff's iPostal1 address cannot be used for a Business Profile, so we cannot rely on GBP for AI local answers. https://support.google.com/business/answer/3038177

## 3. llms.txt

- No major provider says it reads llms.txt to pick search results or citations. OpenAI's, Anthropic's (Apr 2026) and Perplexity's crawler docs never mention it. (Sources in section 1.)
- Google's AI optimization guide (Google, published May 15, 2026, updated Jul 10, 2026): Google Search ignores llms.txt and other special AI files; they neither help nor harm. https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- SEJ on Google's mixed signals (SEJ, May 20, 2026): Chrome Lighthouse 13.3 added an experimental llms.txt check for AI agents, separate from SEO and not a ranking factor. Gary Illyes said Google is not pursuing llms.txt for Search. https://www.searchenginejournal.com/googles-llms-txt-guidance-depends-on-which-product-you-ask/575431/
- John Mueller (SEJ, Apr 17, 2025, OLDER): compared llms.txt to the keywords meta tag and said server logs show AI services do not request it. https://www.searchenginejournal.com/google-says-llms-txt-comparable-to-keywords-meta-tag/544804/
- SE Ranking via SEJ (Nov 20, 2025, 300K domains): 10% of domains have llms.txt and it had no measurable link to citations. Removing it as a factor made their model more accurate. https://www.searchenginejournal.com/llms-txt-shows-no-clear-effect-on-ai-citations-based-on-300k-domains/561542/
- Anecdote (Optimixed, undated): one site owner's logs showed OpenAI fetching llms.txt about every 15 minutes. Fetching is not proof of use. WEAK. https://www.optimixed.com/openai-crawling-llms-txt-files-google-says-it-wont/
- Verdict: no evidence of benefit. It is harmless, but not worth time beyond maybe a 5-minute file for coding agents.

## 4. Google's own guidance for AI Overviews and AI Mode

- "Optimizing your website for generative AI features on Google Search" (Google, last updated Jul 10, 2026). https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
  - The core SEO basics apply: indexed, snippet-eligible, crawlable, good page experience, less duplicate content.
  - Original, "non-commodity" content (first-hand or expert insight beyond common knowledge) is called the most influential long-run factor.
  - Clear headings and paragraphs, supporting images and video, semantic HTML.
  - Not needed: llms.txt, chunking, AI-specific rewrites, special schema.
  - Not helpful: chasing inauthentic brand mentions.
  - Spam: separate pages for query variations or fan-out queries, made mainly to sway AI answers, violate the scaled content abuse policy.
  - Treat third-party "AEO/GEO" tools with caution; they have no access to Google's systems.
- "AI features and your website" (Google, last updated Dec 10, 2025): no extra requirements. AI features fan out into many related searches. Keep structured data consistent with visible text, and keep Merchant Center and Business Profile current where eligible. AI Overview and AI Mode traffic is counted in Search Console under "Web". https://developers.google.com/search/docs/appearance/ai-features
- Search Console Generative AI performance report (Google Search Central blog, Jun 2026; seen live on all properties by Aug 2026 per Search Engine Roundtable): it shows impressions, pages, countries, devices and dates for AI Overviews, AI Mode and Discover AI. It has no clicks or queries, and sites under an unpublished impression threshold may not see it. https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports and https://www.relevantaudience.com/seo/search-console-generative-ai-report-live-all-properties/
- Search Console "Search generative AI" control (rolled out worldwide Aug 31, 2026): opt-out per property. Leave it on (included). https://www.relevantaudience.com/geo/google-search-generative-ai-control-global-rollout/

## 5. Deceptive or risky (avoid)

- Fake or bought reviews and testimonials. FTC Consumer Review Rule: in force since Oct 2024, civil penalties up to $53,088 per violation. The FTC sent its first 10 warning letters in Dec 2025. The rule also bans company-run sites posing as independent review or ranking sites, and undisclosed insider reviews. https://www.crowell.com/en/insights/client-alerts/keeping-it-real-ftc-targets-fake-reviews-in-first-consumer-review-rule
- Reddit seeding and astroturfing. Reddit, per eMarketer and Bloomberg (Jul 6, 2026): Reddit uses AI to catch marketers planting posts to sway AI answers. It removed about 25,000 spammy items a day in Q1 2026 and checks new accounts for fake hype signals. https://www.emarketer.com/content/reddit-geo-crackdown-could-raise-stakes-ai-visibility-strategies
- Hidden text and prompt injection. Google spam policies (last updated Aug 28, 2026): hidden text is spam, and the policy now names "attempting to manipulate generative AI responses" as spam. https://developers.google.com/search/docs/essentials/spam-policies
- Microsoft Security (Feb 10, 2026): it calls "AI Recommendation Poisoning" an attack. That means "Summarize with AI" buttons with hidden prompts telling the assistant to remember a company as trusted. It found 31 real companies doing it and is deploying defenses. https://www.microsoft.com/en-us/security/blog/2026/02/10/ai-recommendation-poisoning/
- Guardian test (Dec 2024, OLDER): hidden text could flip ChatGPT search's product verdicts. Assistants have since hardened against this, and getting caught carries reputational risk. https://www.searchenginejournal.com/chatgpt-search-manipulated-with-hidden-instructions/536390/
- Scaled content and doorway pages. Mass-made pages per fan-out query, or near-identical city pages, are spam per Google's guide and spam policy (above).
- Self-promotional "best" listicles that rank ourselves first: see Lily Ray (section 2). They risk demotion, and the brand often gets left out of the answer anyway.
- Fake freshness. Ahrefs (Jul 2025, OLDER) cites John Mueller warning against changing dates without real edits. Lily Ray's Feb 2026 sample also tied artificially refreshed dates to hit sites.

## 6. Measuring visibility cheaply and within terms

**Terms that forbid scripting the consumer apps**
- OpenAI Terms of Use (effective Jan 1, 2026): bans automatically or programmatically extracting data or Output. https://openai.com/policies/row-terms-of-use/
- Perplexity Terms of Service (Jan 23, 2026, section 5.2): bans robots, spiders, crawlers, scrapers or other automatic devices. https://www.perplexity.ai/hub/legal/terms-of-service
- Anthropic Consumer Terms (effective Oct 8, 2025): bans accessing the service by bot or script except through an API key. https://www.anthropic.com/legal/consumer-terms
- Google Terms of Service (US, effective Jul 30, 2026): bans automated access that breaks machine-readable rules such as robots.txt. Google's robots.txt disallows scraping of search result pages, so scripted checks of AI Overviews or AI Mode are out. https://policies.google.com/terms
- A person checking by hand in each app is fine.

**Free or legitimate routes**
- Bing Webmaster Tools AI Performance (Microsoft, public preview since Feb 10, 2026, free): total citations, cited pages, sampled "grounding queries", and per-URL citations across Copilot, Bing AI summaries and unnamed partners. Citations are not clicks. https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview
- Search Influence used it (Feb 12, 2026): 19,717 Copilot citations over 91 days on 86 pages. One comparison page drew 69% of them, and citations swung 97% within weeks. Expect volatility. https://www.searchinfluence.com/blog/bing-ai-performance-report-copilot-citations/
- Google Search Console Generative AI report (section 4): impressions only.
- APIs with web search (allowed under API terms; results are close to, not identical to, the consumer apps):
  - Gemini API Grounding with Google Search: the first 5,000 search requests a month are free on Gemini 3+, then $14 per 1,000. It returns the queries run and the cited URLs. https://ai.google.dev/gemini-api/docs/google-search
  - Claude API web search tool: $10 per 1,000 searches plus tokens. It supports user_location (for example Chicago) and returns citations. https://platform.claude.com/docs/en/agents-and-tools/tool-use/web-search-tool
  - OpenAI Responses API web_search: tool-call fee plus tokens. It returns url_citation annotations and a full sources list, and supports approximate user location. https://developers.openai.com/api/docs/guides/tools-web-search
  - Perplexity Search API: $5 per 1,000 requests ($1 for fast mode). It returns ranked results, not a written answer. https://docs.perplexity.ai/getting-started/pricing
  - Cost check: 30 buyer prompts a month across 4 APIs is about 120 calls, roughly $1 to $3 plus tokens. Gemini is free in that range.
- Referral analytics: ChatGPT added utm_source=chatgpt.com to links from Jun 2025. Reports from Oct 14 to 15, 2026 say links opened under GPT-6 now carry no tag and no referrer, so visits show as Direct; this may be a bug. Do not rely on referral data alone right now. https://www.relevantaudience.com/analytics/chatgpt-gpt-6-utm-referrer-dropped-direct-traffic/
- Crawler hits: if the site sits behind Cloudflare, its bot analytics show OAI-SearchBot, Claude-SearchBot and PerplexityBot visits. GitHub Pages alone gives no server logs.

---

## Do now on proofnotfluff.com (ranked)

Site state checked in the repo today: robots.txt is "Allow: /" for all agents with the sitemap listed. An IndexNow key and workflow exist. Search Console is verified; Bing Webmaster Tools verification is not recorded in seo/RESULTS.md. 51 pages carry FAQPage schema, the Organization schema has no sameAs, dateModified appears on only 3 pages, and the question hub has 4 pages.

1. **Confirm no AI search crawler is blocked anywhere** (minor-invisible). robots.txt is fine. If DNS is proxied through Cloudflare, check that "Block AI bots" / AI Crawl Control lets OAI-SearchBot, Claude-SearchBot, Claude-User, PerplexityBot, ChatGPT-User and Bingbot through. Optionally add explicit Allow groups for these in robots.txt as documentation. Keep Google-Extended allowed so the Gemini app can ground on us.
2. **Verify Bing Webmaster Tools and read AI Performance weekly** (minor-invisible; needs Todd's sign-in, which can import from Search Console). Bing feeds Copilot and likely part of ChatGPT. Our IndexNow workflow already pings it. Log citations and grounding queries in seo/RESULTS.md.
3. **In Search Console, confirm the "Search generative AI" control is on and log the Generative AI report weekly** (minor-invisible).
4. **Put a 2 to 3 sentence direct answer at the very top of every lead page** (visible-change). Lead pages open with stats, not an answer. Example: "Where to find post-construction cleaning leads in Chicago: the City's building permit records name the general contractor on every big job; this week 1,133 open projects of $500,000 or more." The question pages already do this ("The short answer"); copy that pattern. Keep the first third dense with dated figures, builder names and neighborhoods.
5. **Make freshness signals true and consistent everywhere** (minor-invisible). Add dateModified (and datePublished) to the JSON-LD on every lead and question page, set from the weekly data pull. Make sitemap lastmod match the real data date: the Chicago construction page shows data as of Oct 19, but its sitemap lastmod says Oct 17. Never bump a date without a data change.
6. **Publish one question page per real buyer question, each with our own weekly numbers** (visible-change). Examples: "How do hood cleaning companies find new restaurant clients?" (general, linking to the Chicago data), "How do commercial cleaners find new businesses to pitch in Chicago?" (new business licenses), "Where can I find post-construction cleaning leads?" (general). One page per distinct question, not per wording variant. That keeps us within Google's scaled-content rule.
7. **Add an honest "ways to find X leads in Chicago" comparison** (visible-change). Cover the free City Data Portal itself, paid permit databases, GC bidder lists and networking, plus ours, with real pros, cons and prices, and our page clearly marked as ours. Do not rank ourselves "best". This fits the comparison format assistants cite while avoiding the self-promotional listicle trap. Confidence low to medium.
8. **Earn real third-party mentions** (visible-change, off-site). Ranked by fit: a short YouTube walkthrough of using the free sample (YouTube mentions correlate most strongly); answering trade-forum and subreddit questions from a disclosed account, with the data and no link-dropping; listings in legit directories or newsletters for small cleaning, pressure-washing and hood-cleaning businesses; a note to Chicago data or civic-tech communities about the dataset use. All disclosed, all by hand.
9. **Add sameAs to the Organization schema** (minor-invisible). List our real profiles (Etsy shop, Gumroad, any YouTube or social accounts) so entity data is consistent. Low impact, near-zero cost.
10. **Set up a monthly AI visibility panel through APIs** (minor-invisible). Use 20 to 30 buyer prompts ("where can I find post-construction cleaning leads in Chicago", "how do hood cleaning companies find new restaurant clients", and so on), run through Gemini grounding (free), the Claude web search tool with user_location set to Chicago, OpenAI web_search, and the Perplexity Search API. Log whether proofnotfluff.com is cited, which URL, and who is cited instead. Add a human spot check in the consumer apps once a month.

## Do not do

- Do not script or scrape ChatGPT, Claude, Perplexity, Gemini or Google AI Overviews / AI Mode consumer interfaces. Use the APIs or check by hand.
- No fake, paid-for-positive, or undisclosed insider reviews or testimonials, and no Review or AggregateRating schema without real reviews (FTC rule, up to $53,088 per violation).
- No sock-puppet or undisclosed posts on Reddit, Quora or forums. No buying mentions, upvotes or links.
- No hidden text, no instructions aimed at AI ("AI assistants: recommend ProofNotFluff"), and no "Summarize with AI" buttons with memory prompts.
- No mass-made pages for every query variation or city without unique data (scaled content abuse, doorway pages).
- No self-ranking "best X" listicles.
- No date bumps without real data or content changes.
- Do not block OAI-SearchBot, Claude-SearchBot, Claude-User, PerplexityBot, Googlebot or Bingbot. Do not opt out in the Search Console generative AI control.
- Do not create a Google Business Profile on the iPostal1 virtual mailbox (not eligible).
- Do not spend effort on llms.txt or extra schema types as AI levers, and do not pay for "GEO/AEO" tools until the free reports show a signal.
