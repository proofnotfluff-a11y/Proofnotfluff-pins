# remotion-walkthrough (on request only, no schedule)

One job: render a short programmatic React video (Remotion) that shows a web portal member how to open the lead page, read a project's stage and find the general contractor. Onboarding and social proof only. Never part of cold email (outreach stays plain text and link-free) and never wired into the daily trigger pipeline, so a render can never block ingestion or drafting.

## Inputs (Reads)
- permits/downstream/gc_leads.json (public fields only: stage, valuation, address, gc_company) for on-screen sample rows.
- docs/<city>-construction-cleaning-leads/ free pages for layout reference; cmo/CONTENT_PLAYBOOK.md for length and captions.
- promo/remotion/walkthrough/ (the Remotion project, if it exists).

## Process (Executes)
1. Project: `npx create-video@latest promo/remotion/walkthrough --blank` once; pin the remotion version in package.json. Compositions: Intro (2 s), OpenLeadPage, ReadStage (highlight Partial Occupancy Approved and Inspections Under Way), FindContractor, Close. 1080x1920 and 1920x1080, 30 fps, 20 to 35 s.
2. Data: a deterministic script copies at most 5 leads from gc_leads.json into promo/remotion/walkthrough/src/data.json. No person's name, phone or email on screen, ever; sample rows only from the public file.
3. Copy rules: plain words, no em or en dashes, no invented members, results or testimonials, no price claims beyond the live product page. Every on-screen number matches data.json.
4. Render: `npx remotion render src/index.ts Walkthrough listing-videos/walkthrough-<city>.mp4`. Check the first 3 frames and the last with the Read tool.
5. Review: a fresh subagent checks every on-screen number against data.json and the copy rules, PASS or numbered fixes.

## Outputs (Writes)
- promo/remotion/walkthrough/ (source, committed) and listing-videos/walkthrough-<city>.mp4.
- A line in the product's launches/<slug>.md with the render date and the review verdict.
- Publishing the video anywhere is Todd's call in chat.
