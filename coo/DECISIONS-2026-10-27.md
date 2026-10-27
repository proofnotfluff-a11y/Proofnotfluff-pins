# Decisions, Oct 27, 2026 (live chat with Todd)

## Free site, ads idea, 8:58 to 9:04 am
- [stated] Todd, 8:58 am: asked about making everything on the site free (leads lists, calculators, tools, maps, dashboards, alerts, news, blog), earning from ads, and copying Chicago to new cities and trades.
- Answer given: free by default for tools and data, yes; ads as the main earner, no for now (362 views last week, 0 from search; about 50,000 views a month needed for $1,000 at a $20 RPM; Raptive needs 25,000 views and a 6 month old domain). Proposed: referral deals and one sponsor per city or trade first, lead seats and exports stay paid, a new city only after Chicago reaches 1,000 search visits a month.
- [stated] Todd, 9:04 am: "trade owners only" (audience for the site: trade owners, not homeowners).
- So: audience recorded. The free plan, referrals and city gate wait for his go. Nothing built, joined or changed.

## Bid tools, the news tip and trades news, 9:08 am (Kimi research chat)
- [stated] Todd: "Let's go with your recommendation." (to Kimi R9's read: no separate paid bid writer; build (1) a free post-construction cleaning bid calculator pricing rough, final and touch-up cleans from the owner's own rates, with a one-page proposal download for an email, and (2) a bid sheet inside the area seats, each near-finish project priced at the seat holder's own rates.)
- [stated] Todd: "Yes to the rat news tip. We should have a whole section devoted to trades news. That is already being worked on in another chat."
- So: both bid pieces are built through every gate (holdout, design director, accessibility, Legal desk) as drafts; the calculator page needs its own Kit form before it goes live; the seat change ships to the members' app after its gates (0 seat holders today). Guide price ranges show as ranges with their sources, never as what the market charges.
- The news tip: one email to ABC7 Chicago's public tips address (wls.desk@abc.com, read on abc7chicago.com Oct 26) with our 311 counts next to Orkin's Oct 13 list. Todd sends it from hello@proofnotfluff.com; the session drafts it. Trades news section: another chat's work, not this one.
- Kimi R7 set aside (2 of the first 10 sources did not hold); what it shares with our own Oct 26 pass stands on our sources: research_notes/kimi-2026-10-27-r7.md. Kimi R9 kept: research_notes/kimi-2026-10-27-r9.md.

## Trades news and maps go, 9:32 to 9:33 am (trades news chat)
- [stated] Todd, 9:32 am: "go" (to putting all three live: Chicago Trades News, the map on the rat complaints page, and the List or Map view in the pest seat members' app).
- [stated] Todd, 9:33 am: "let's refresh news daily".
- So: /chicago-trades-news/ live (footer link on every page, sitemap, site search, RSS feed); the community area map is on /chicago-rat-complaints/; the pest seat app gets its map on the next daily build (6:45 am). A daily cloud scheduled task runs .claude/skills/trades-news/SKILL.md; each refresh is a minor data change under CONSTITUTION 2 and publishes only when its facts and copy gates pass.
- [stated] Todd, 9:44 am: "Shouldn't new features like news be an option to select rather than hiding at the bottom of the page?"
- So: "Trades news" joins the header links on every page (desktop and the phone menu); the header switches to the menu below 1024 px so the links never wrap to two rows (it already wrapped at 768).

## Next Chicago builds, 10:03 am (Kimi research chat)
- [stated] Todd: "Go for all" (to: the free restaurant inspections by neighborhood page; drafting the first area seat email batch for his review; and the two seat offer fixes: pest seat records taken out of the $39 weekly list, and a 30-day money-back promise on both seats).
- So: the inspections page and the pest exclusivity change are built through every gate; the money-back line goes through the Legal desk and Gumroad's refund setting is Todd's. The area seat batch follows .claude/skills/outreach-drafter/SKILL.md; today it is blocked on Bouncer checks for the 8 named Chicago construction addresses (CRM meta/desk.lastOutreach, Oct 26), which need Todd's browser.

## Verification skill, 10:08 am (trades news chat)
- [stated] Todd, 10:08 am: "Ensure this is a skill we bake into the PNF system" (Kem at Glitch Cat Club on verification: agents check their own work by using it, with Playwright, DevTools, image diff, Storybook and Sentry, packaged as a skill with its own CLI).
- So: .claude/skills/verify/SKILL.md and its CLI tools/verify_site.py (Playwright hands at 390 and 1280 px in light and dark, DevTools eyes through Playwright's error and network events, axe, before/after pixel diff against origin/main, flow files in verify/flows/); CLAUDE.md invariant 9 makes it required for any docs/ change; question-pages, trades-news and product-builder call it; the Verify site workflow runs it on every push that touches docs/. Storybook skipped (no component library; flows cover each feature's states). Sentry on watch: it needs an account, a script on every page and a privacy change, so it waits for Todd's word and more traffic.

## Build every R10 free feature (Todd, Oct 27, 2026, 12:17 pm, live chat: "Let's do them all. Write me the necessary prompts and I'll get them all going in parallel")
- Scope: the merged R10 list (research_notes/kimi-2026-10-27-r10.md), items 1 to 14, as free pages; not the avoid list, and no free busiest contractors leaderboard (default no stands).
- Run as 9 parallel build chats plus a quarterly report and a wrap-up after them; shared rules in coo/PARALLEL_BUILDS.md.
- Plumbing (minor, no visible change): tools/make_site.py takes pages of kind "datapage" from their own modules (tools/dp_*.py), with sub-pages, lastmod, search entries, a /chicago-data/ hub and a footer link once one is live; 12 draft entries in site/pages.json render as noindex stubs until built.
- Each page goes live only after its facts, design (average over 4.6), legal, copy and verify gates pass. Email capture, checkout, outreach, accounts and scheduled tasks still need Todd's word.
