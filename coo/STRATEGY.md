# COO strategy (rewritten every run; this version Sat Oct 17, 2026, 5:45 am, daily run on Opus)

Plan: coo/PIVOT.md (Todd's "Go", Oct 15, 9:55 pm). One audience (e-commerce and consumer brands), one ladder (free calculators on proofnotfluff.com, the $79 13-week kit on Gumroad, Fiverr gigs at $60 to $550), Etsy on autopilot, one video a day on e-commerce cash topics, judged Nov 12 (scoreboard experiments/ecom-ladder-pivot).

## What changed since yesterday
- proofnotfluff.com serves over HTTPS (Todd re-added the domain and ticked Enforce HTTPS Oct 16 evening); IndexNow accepted all 44 sitemap URLs (202). One of the three discovery blockers is gone; Search Console and Bing verification are still Todd's.
- Hub swap (site/DOMAIN.md step 5): https://proofnotfluff.com/go/ is now the hub in cmo/CONVERSION_STANDARD.md, agents/cmo.md and the ledger FUNNEL line. The promote prompts still print github.io short links until the redirect is confirmed: .github/workflows/link-check.yml checks old links from GitHub's runner (the cloud sandbox cannot reach either host).
- Product engine (PIVOT.md, Oct 17 COO line): the builder needs a rework-in-place path for the three page upgrades (payout gap, PO cash, channel profit). Written in agents/cloud-builder.md and passed the constitution review, but update_trigger was refused by this run's permission check. The stored builder prompt is unchanged, so the upgrades are not queued (queueing them around the refused update would be a workaround). Same refusal leaves the stored CMO prompt without its Oct 16 ElevenLabs lines; the promote runs' own ElevenLabs fallback still narrates every video, so nothing ships in the robotic voice.
- Ads swap did not run: the Oct 16 shop run's toggle click was refused by the PC permission check. Todd's clicks: #23 off, #29 on, Savings Tracker off (it was never in the approved set).
- Rule desk's first Haiku run (Oct 16, 6:32 am): ok, 13 official sources checked, no value changes, no Opus subagent needed (Oct 15 on Opus checked 17; the rotation varies by day).
- Plan file 48.7 to 44.4 KB, ledger 46.5 to 46.0 KB (superseded lines moved verbatim to archive-3); ElevenLabs purchase now on the ledger Spend line.

## Goal ladder (off-Etsy first since the pivot)
| Rung | Status | What has to be true |
|---|---|---|
| First dollar off Etsy | not reached; target Nov 12 | Gumroad payout method (kit built, cleared, waiting) or the Fiverr account open; 1 sale |
| First $100 off Etsy | not started | 2 kit sales at $79, or 1 Fiverr gig at $100+ |
| $1,000 a month | target Jan 31, 2027 | about 13 kit sales, or 3 to 5 Fiverr orders at $200 to $550 a month |
| $10,000 a month | no date | a hosted cash-flow tool with 300+ subscribers at $29, or 20+ service orders a month |
| $100,000 a month | no date | not reachable faceless on today's evidence |
| Etsy first order (background) | not reached: 0 orders on 36 visits since Sep 27 | autopilot only |

Honest distance: $1M a year is 35 sales a day at $79, or about 920 a day at $2.99. Today: $0 off Etsy, 0 products live off Etsy, 0 Etsy orders, about 1.7 Etsy visits a day.

## Net profit this week (EVOLUTION.md section 1; Oct 10 to 16)
Revenue $0. Etsy fees $0. Listing fees $1.00 (5 new listings). Etsy Ads spend $0.16 (1 click on #23). Cloud runs: about 18 ProofNotFluff runs a day, about 126 for the week. Cost per run: not set. Net: minus $1.16 before agent cost. Leading indicator optimized: visits to the e-commerce free pages (Cloudflare Web Analytics; no read route from the cloud yet), then clicks to the kit and gigs.

## The constraint this week
Availability, unchanged: the kit cannot sell without the Gumroad payout method and the gigs cannot sell without the Fiverr account; both are Todd's steps (3 and 30 minutes). Discovery moved one step (HTTPS and IndexNow done); Search Console and Bing remain. Nothing the crew builds moves the first-dollar rung until one switch flips.

## Scorecard (Oct 9 to 15 vs Oct 2 to 8; Oct 16 not final until today's shop run)
| Metric | now | before |
|---|---|---|
| Etsy listings live | 32 | 26 |
| Listings added | 7 | 14 |
| Etsy visits | 12 | 12 |
| Visits per listing per day | 0.05 | 0.07 |
| Etsy search visits | not recorded | not recorded |
| Favorites, orders, revenue | 0, 0, $0 | 0, 0, $0 |
| Etsy Ads (30 days to Oct 16) | 3 views, 1 click, $0.16 | not running |
| Shorts | 12 | 17 |
| Pins | 29 (0 outbound clicks recorded) | 40 |
| Posts | 28 | 18 |
| Free-page visits (Cloudflare) | not recorded (no cloud read route) | none |
| Off-Etsy sales | 0 (nothing live) | 0 |

## Unit economics
- Etsy: 32 listings x 0.05 visits a day x unknown conversion x $2.99. At 2% that is about one order every 30 days; a $2.99 sale nets about $2.26. Etsy served 3 ad views in 30 days at $5 a day. Autopilot stays right.
- Ladder: price is the factor with headroom (26x per sale at $79, up to 180x at $550). Conversion and traffic are unmeasured because nothing is live to convert. Binding factor: availability (0 of 2 sales switches on).
- Path to the first $100 off Etsy: roughly 100 to 200 e-commerce page visitors for 1 or 2 kit sales at a 1% page-to-purchase rate (assumption, unconfirmed); that is the Nov 12 target of 100+ visits in 14 days.

## Experiments in flight
| slug | started | metric now vs baseline | check | owner |
|---|---|---|---|---|
| ecom-ladder-pivot | Oct 15 (Todd) | 0 of 2 sales switches on; $0 off Etsy; HTTPS and IndexNow done; page visits not read | Nov 12 | coo |
| free-calculator-site | Oct 6 | 44 pages submitted to IndexNow Oct 16; not in Google yet | Nov 4 | coo |
| plan-v2-demand-test | Oct 7 | kit cleared at $79, unpublished (payout method) | Nov 4, extend to Nov 30 if published after Oct 15 | coo |
| etsy-ads-test | Oct 13 (Todd) | 3 views, 1 click, $0.16 in 30 days; swap waits on Todd's clicks | Oct 27 | todd |
| sales-first | Oct 8 (Todd) | superseded by the pivot for CTAs | Nov 1 | todd |
| price-299 | Oct 6 (Todd) | 0 orders on 12 visits this week | Nov 3 | todd |
| permit-leads-pilot | Oct 14 (Todd) | parked until the Kit form exists | 45 days after go-live | todd |

## What we know
- A1: title format under 15 words, noun first; judged Nov 7.
- C6: Short descriptions are not clickable; broad money hooks beat narrow trade hooks (median 41 vs 11 views). Proof Check #1 drew 50 views in 17 hours vs 4 for the old format the same day (one data point).
- D1: Pinterest is a 90-day channel (judge Jan 3); 0 outbound clicks so far.
- Etsy Ads: a new shop with no sales gets almost no paid placement (3 views in 30 days at $5 a day).
- Crew fact (Oct 17): the permission check can refuse scheduled-task writes from this run; a prompt change then waits for Todd, and nothing routes around it.
- Crew fact (Oct 16): a prompt edit must change the review gate too, or the reviewer blocks the new behavior.
- Crew fact (Oct 14): the account usage limit is shared across every task; when it hits, the shop run (the only Etsy numbers) goes dark.

## Crew health (Oct 17, 5:45 am)
- Scout's Wed Oct 14 run failed on the usage limit; next run Sun Oct 18.
- Shop run partial Oct 15 and 16 (PC permission check refused the ads toggle and Publish clicks; file swaps and KDP #8 wait on a connected PC folder). Legal desk partial Oct 16 (#32 zip not in Drive, quest legal-32-files).
- Factory (3 runs a day, still on Fable) and R&D lab (2 a day) produce nothing under the pivot; both are PC-bound, so only Todd can slow them. Builder had no work in its last 3 runs (site queue empty).
- All other runs ok. Schedule: about 18 ProofNotFluff runs a day of the 24 budget. Edition and redesign desks off.

## What we stopped and why
- Premium evidence reads for home services and STR: held by the pivot; lines moved to archive-3 (the Oct 20 decision is moot).
- demand-gate-v2 stopped by the pivot (3 search visits in 30 days, under the 50-visit floor).
- Instagram carousel step: deferred to the Oct 29 zero-click review.

## Open questions for Todd (ranked by expected profit, minutes)
1. upload-premium-ecom-13-week-cash-flow (3 min): Gumroad payout method. Turns on the only built product priced for real money ($79).
2. open-fiverr-account (30 min): the $60 to $550 gigs are built and waiting.
3. Etsy Ads swap (2 min, Etsy Ads in Shop Manager): #23 off, #29 on, Savings Tracker off; budget stays $5.
4. verify-search-console (10 min): Search Console plus the Bing import; HTTPS is now live, so nothing blocks it.
5. Apply two reviewed prompt updates (1 min in a live chat: "apply the COO's Oct 17 builder and CMO prompts"): unlocks the three page upgrades and the CMO's committed ElevenLabs renders.
6. kit-form (15 min), share-save-bio-links, switch-pc-models-opus (factory still Fable), pc-shop-run-folder, legal-32-files, apply-erank-affiliate. Oct 5 quests (messages-24h, note-to-buyers-browser, legal-returns-policy) retire Oct 19 if unticked.

## Next run (Sun Oct 18, 5:00 am)
Read the link-check result; if old links land on proofnotfluff.com, swap the promote prompts' short links when prompt writes are allowed. Oct 16 final Etsy line; whether any switch flipped; whether the prompt updates were applied (then queue the three page upgrades). Monday deep run Oct 19.
