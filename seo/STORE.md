# Store and question-page engine

Todd's brief, Oct 22, 2026: turn proofnotfluff.com into a store built to convert and add a question-page engine, same domain, generator (tools/make_site.py, site/*.json, docs/) and host. Phases 0 to 2 time-boxed to one week.

## Phase 0 (done Oct 22)

Todd, Oct 22, 2026, 2:20 pm [stated]: "I'm a go on the plan." Todd, 2:23 pm [stated]: "refund ok" (wording below) and the publishing rule now in coo/CONSTITUTION.md section 2.

Refund wording (Todd's ok, Oct 22): "No refunds on lead lists or the workbook, because you get the data the moment you pay. Cancel a list any time and you won't be charged again. If a list doesn't arrive or a file won't open, email hello@proofnotfluff.com and we'll fix it or refund that month."

Design: Claude Design canvas https://claude.ai/artifact/LqgDbvVYjWCetbybrZ9JiY (home, shop, lead product page, question page; desktop 1280, phone 390, dark), built on the ProofNotFluff design system.

### Baseline, Oct 22, 2026
- Search Console (URL property https://proofnotfluff.com/ under proofnotfluff@gmail.com, 28 days, data Oct 16 to 20): FAIL 0 clicks, 5 impressions, average position 5, queries hidden (too few). Indexed 1 page, 1 crawled not indexed (report Oct 15). Sitemap read Oct 21: Success, 49 discovered.
- Cloudflare Web Analytics, last 7 days: 172 visits, 190 page views. By page (API, sampled 1 in 10, Oct 15 to 22): / 160, chicago-construction-cleaning-leads 20, austin-construction-cleaning-leads 20, hourly-rate-calculator 20, etsy-fee-calculator 10, chicago-restaurant-inspection-leads 10, estate-cleanout-cost-calculator 10. Referrers: all direct. Real-user LCP p75 1,436 ms, CLS 100% good.
- Lighthouse mobile (PageSpeed Insights, Lighthouse 13.5.0, Moto G Power, slow 4G), targets 95+, LCP under 2.0 s, CLS under 0.05:
  - Home: FAIL 96/85/100/100, LCP 2.3 s, CLS 0.001 (contrast; headings skip h2)
  - hourly-rate-calculator: FAIL 96/95/100/100, LCP 2.3 s, CLS 0.001 (contrast)
  - chicago-restaurant-inspection-leads: FAIL 96/100/100/100, LCP 2.3 s, CLS 0.001
  - chicago-hood-cleaning-first-restaurant-clients (draft): FAIL 94/100/100/66, LCP 2.4 s, CLS 0 (SEO 66 is the draft noindex)
  - Cause on all four: the Google Fonts stylesheet blocks render, about 1.5 s estimated saving.
- Schema and meta (repo): Product 0 of 4 pages, Article 0, Breadcrumb 0, og:image 0 of all pages, canonical 4 of 4 PASS, dark mode none.

### Funnel map, today
- Every page's header: "Free calculators" and "Etsy shop". No shop, no lead lists, no refund page anywhere.
- 0 of 45 calculator pages link to a paid product; each sends its two exits to Etsy ($2.99). Only /go/ links all four products.
- Home: h1 sells calculators; the three lead lists sit among 30+ calculator cards, the restaurant list last; the kit appears only as its free calculator.
- Chicago construction ($29): lead page to Gumroad is 2 taps, but its hero puts "$29 a month" before the sample; Kit form 10059700 asks "keep me posted" (new cities), not the weekly sample. Links out to 4 calculators; none link back.
- Austin construction ($29): same path, no Kit form; near-finish shows 1 project this week.
- Chicago restaurant ($39): no Kit form, no calculator link, nothing links in except home and the draft question page.
- 13-Week cash flow kit ($79): CTA only at the bottom of the free calculator, beside "All ProofNotFluff tools" which leaves for Etsy; no email capture; the inventory, shipping, P&L and break-even calculators never mention it.
- Chicago new business licenses: noindex, mailto button instead of a form.
- Three question pages: drafts, noindex, so 0 entry traffic.

### Phase 1 plan (on Todd's store go)
- make_site.py HEAD and FOOT: nav Shop, Free calculators, Questions; Etsy to the footer; refund link on every page.
- Self-host Poppins with preload (the site already self-hosts Inter): target LCP under 2.0 s.
- pnf.css: dark tokens under prefers-color-scheme; muted #5f6573 and accent-ink eyebrows for AA contrast; home heading order.
- New pages from site/pages.json: /shop/, /refunds/, /questions/.
- Lead pages: sample first (restaurant gets trade tabs), sticky subscribe bar on phones, a Kit form per product that sends the sample weekly.
- site/links.json: a "find customers" card per calculator to the matching paid product (cleaning, window and pressure washing calculators to the construction lists; contractor hourly rate to restaurant leads; inventory, shipping, P&L and break-even to the kit).
- JSON-LD: Product with Offer on the 4 products, Article and FAQ on question pages, BreadcrumbList everywhere; og:image per page.
- Two-tap rule as built: any page to the product page (opens on the sample), then Gumroad checkout.

### Publishing rule (Todd, Oct 22)
Minor changes publish once every gate passes and get one line in seo/RESULTS.md; major ones go to Todd first, any day. Definitions: coo/CONSTITUTION.md section 2. The store build (Phase 1) is major.

## Next step
Phase 1 build on branch store-v1, then the Phase 2 checks, then Todd's go on the store.
