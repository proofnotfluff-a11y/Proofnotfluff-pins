# AI avatar and AI video platforms for realistic talking-presenter / UGC video: state of the art, costs, automation (as of Oct 15, 2026)

Research date: 2026-10-15. All "seen" dates are the dates the cited page reported checking prices, or the page's own date. Official vendor pages are labelled "(official)". Everything else is third-party, and many of those sources are competitors (Creatify, Argil, HeyGen and Hooked all publish comparison pages that rank themselves). No signup or login was done. Several official pricing pages could not be read (HeyGen's API pricing modal is rendered by JavaScript and returned nothing), so some prices are second-hand and flagged.

---

## 1. Which platforms lead for realistic avatars and AI UGC in 2026, and how they compare

### Takeaway
There are three groups in late 2026:
- **Dedicated avatar platforms with real APIs.** HeyGen (Avatar IV / Avatar V), Synthesia (Express-3), Creatify (Aurora 2.0), Tavus (Phoenix-4.5), Argil, D-ID and Mirage/Captions (Mirage Avatar X). These make lip-synced talking presenters from a script or audio, at roughly $1 to $9 per output minute through the API.
- **UGC-ad apps.** Arcads, Topview, Higgsfield and the Captions app. These are mostly app-first, with API access that is custom, unpublished or limited.
- **General video models with native speech.** Veo 3.1, Kling 3.0 and Runway Gen-4.5. They are very realistic but make short clips (8 to 15 s per generation) that you have to stitch together. **OpenAI's Sora 2 is gone**: the app shut on Apr 26, 2026 and the API on Sep 24, 2026.

For realism, HeyGen Avatar V (launched Apr 8, 2026) is the most-cited digital-twin model. All of the vendor quality numbers are self-reported.

### Cited Findings

**HeyGen (Avatar III / IV / V, digital twins, API)**
- Avatar V was announced and launched Apr 8, 2026. A digital twin is made from a single 15-second phone clip looking at the camera, with about 90 s of processing and no calibration step. HeyGen claims coherence up to 10 minutes; the reviewer tested up to 4 minutes and saw no identity drift. LSE-C lip-sync score is 8.97 and Face Similarity 0.840; these are HeyGen-internal benchmarks repeated by the reviewer. Gestures and head motion are driven by the audio and script and are "restrained". Poor lighting in the seed clip degrades the output. French lip sync trails Synthesia slightly. Less suited to high-emotion delivery. Review published Apr 15, 2026, updated Jul 30, 2026 — [ThePlanetTools hands-on review](https://theplanettools.ai/blog/heygen-avatar-v-tested-hands-on-review-2026)
- API pay-as-you-go prices (HeyGen's own blog, "Last Updated October 12th, 2026", prices "verified October 2026"):
  - Avatar III Digital Twin: $0.0167/s (~$1/min)
  - Avatar IV Photo Avatar: $0.05/s (~$3/min)
  - **Avatar V Digital Twin: $0.0667/s (~$4/min)**
  - Avatar Realtime: $0.05/s
  - Same rate at 720p and 1080p.
  - $5 prepaid wallet minimum, no subscription. Photo avatar creation costs $1 per call.
  - **Custom Digital Twin creation via API is Enterprise-only.**
  - 10 concurrent API videos on pay-as-you-go.
  - Credits expire after 12 months. Free API credits ended Feb 2026.

  Source: [HeyGen blog: Best AI avatar / talking-head APIs (2026)](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)
- Third-party API table seen Sep 4, 2026: Avatar III ~$1/min ($1.20 at 4K); Avatar IV Photo $3/min ($4 at 4K); Avatar IV Digital Twin/Studio $4/min ($5 at 4K). It said Avatar V API pricing was "not listed" as of Sep 4. HeyGen's Oct 12 page now lists it at $4/min — [diyai.io HeyGen pricing](https://diyai.io/ai-tools/video-generation/heygen-pricing/)
- In-app credit burn per minute (seen Sep 4, 2026): Avatar III Video 4, Avatar III Photo 7, Avatar IV Photo 16, Avatar IV Video 31, **Avatar V Video 48** — [diyai.io](https://diyai.io/ai-tools/video-generation/heygen-pricing/)
- Web plans (official pricing page, no effective date shown, © 2026):
  - Free: 1-min max video.
  - Creator: $29/mo ($24/mo billed annually), 600 credits, 30-min max, 1080p.
  - Pro: from $49/mo, 1,000 credits (tiers up to 100,000 credits for $4,300), 4K.
  - Business: $149/mo + $20/seat, 1,500 credits, 60-min max.
  - Watermark removal on paid plans.
  - Commercial terms are not stated explicitly except "commercial terms" listed under Enterprise.

  Source: [HeyGen pricing (official)](https://www.heygen.com/pricing?nb=01)
- The free plan's output is watermarked — [ThePlanetTools](https://theplanettools.ai/blog/heygen-avatar-v-tested-hands-on-review-2026)
- Zapier integration (official docs):
  - Actions: "Create an Avatar Video (Scene)", "Create an Avatar Video (Generate)", Create WebM Avatar Video, Translate a Video, Retrieve Video Status, Retrieve Shareable Link, Upload an Asset.
  - Trigger: "Avatar Video Success".
  - The generate action has a captions setting and a dimensions setting.
  - Renders typically take 2 to 5 minutes.

  Source: [HeyGen docs: Zapier](https://docs.heygen.com/docs/create-an-avatar-video-with-zapier.md)

**Synthesia (Express-1/2/3, API)**
- Express-2, announced Sep 4, 2025 (older): full-body avatars with "natural hand and body gestures", 1080p at 30fps, "no limit on video duration", plus controls for movement and intensity — [Synthesia blog (official)](https://www.synthesia.io/post/express-2-is-synthesias-next-chapter-for-full-body-expressive-ai-avatars)
- Express-3 is described as "our most lifelike avatar yet":
  - Clearer faces, more precise lip sync, fewer eye-gaze problems, body motion matched to the script's sentiment, up to 2x faster renders.
  - "Live for every user on every plan", replacing Express-2.
  - Release date and API availability are not stated on the page.
  - The site footer says its AI content is labelled under EU AI Act Article 50.

  Source: [Synthesia updates: Express-3 (official)](https://www.synthesia.io/updates/express-3)
- Plans (official pricing page as fetched Oct 15, 2026; layout partly garbled):
  - Basic: $0, 10 free minutes, Synthesia watermark.
  - Starter: $29/mo, 1,250 credits, logo removed.
  - Pro/"Creator": $89/mo, 6,000 credits. API usage is capped at "up to 360 min/year", deducted from usage.
  - Express-1 personal avatars are a $1,000/yr add-on on annual plans only.
  - About 100 credits per video minute.
  - 1080p MP4. Aspect ratios not listed.

  Source: [Synthesia pricing (official)](https://www.synthesia.io/pricing)
- Conflicting figures:
  - HeyGen's comparison says API access starts at Creator $89/mo, there is no API on Basic, and the rate is 120 credits per standard minute, so Creator's 3,600 credits ≈ 30 min — [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)
  - Argil (Feb 2026) lists Starter $29 ($18 annual) with 1,200 credits and Creator $89 ($64 annual) with 3,600 credits — [Argil blog](https://www.argil.ai/blog/how-do-leading-ai-avatar-services-compare-on-pricing-in-2026)
  - Treat the credit counts as unverified.

**Captions / Mirage (Mirage Studio app, Mirage Avatar X API)**
- API pricing (official docs):
  - Mirage Avatar X ("expressive human video generation", image or video + audio → video): **$0.15 per output second**, billed in 6-s increments.
  - Add Captions: $0.15 per input minute, rounded up.

  Source: [Captions API pricing (official)](https://www.captions.ai/help/docs/api/pricing)
- API spec (official docs):
  - Inputs are an audio clip plus one image or one video reference. **No script/TTS input**: you bring your own audio.
  - Audio length 1 to 60 s per request; longer videos are made by stitching segments.
  - 9:16 or 16:9 at 720p. MP4 output.
  - **"Every output includes non-removable provenance metadata."**
  - Reference media is not kept as a reusable identity.

  Source: [Captions API video generation (official)](https://captions.ai/help/docs/api/video-generation)
- App plans (third-party, a competitor, seen Sep 25, 2026; iOS prices):
  - Basic $9.99, 200 credits; watermark on AI Creator and AI Edit exports.
  - Max $24.99, 500 credits, no watermark.
  - Frontier $69.99, 1,400 credits.
  - Frontier 2x $139.99; Frontier 4x $279.99, 5,600 credits.
  - Mirage video costs 8 credits per second. Free tier Mirage videos are capped at 15 s.

  Source: [Hooked: Captions pricing](https://www.hooked.so/compare/captions-ai-pricing)

**Creatify (AI Avatar, Aurora 2.0, API)**
- API plans (official billing docs):
  - API Starter $99/mo, 500 credits (~$0.198/credit).
  - API Pro $299/mo, 2,000 credits (~$0.15/credit).
  - Credit costs:
    - AI Avatar: 5 credits per 30 s (30-s increments).
    - URL-to-Video and AI Shorts: 5 credits per 30 s.
    - Aurora 1.0: 1 credit/s. Aurora 1.0 Fast: 0.5 credits/s.
    - Aurora 2.0: 0.4 credits/s (480p), 0.7 (720p, default), 1.4 (1080p), 2.8 (2K).
    - Text to speech: 1 credit per 30 s.

  Source: [Creatify API billing (official)](https://docs.creatify.ai/billing.md)
- API changelog (official):
  - Aurora 2.0 (`aurora_v2`) added Oct 2026, up to 59.7 s of audio.
  - Aurora price cut in May 2026.
  - The "boreal" model was added to AI Avatar v1/v2 in Sep 2026 at 10 credits per 30 s.
  - Failed tasks are auto-refunded (Oct 2026).
  - Asset Generator prices were halved from Oct 11, 2026.

  Source: [Creatify API changelog (official)](https://docs.creatify.ai/api-reference/changelog.md)
- App plans (as of June 2026, third-party):
  - Free: 10 credits/mo, watermark.
  - Starter: $39/mo, 100 credits, 2-min max length, 300 avatars.
  - Pro: $99/mo, 300 credits, 10-min max, 1,500+ avatars + 3 custom.
  - A 30-s ad ≈ 5 credits.
  - Realism: "works well in 15–30 s clips", but longer scripts show lip-sync drift, unnatural head movement and "glossy skin".

  Source: [Fast.io Creatify review 2026](https://www.fast.io/resources/creatify-ai-review-2026.md)
- A pricing tracker headline says Creatify's Pro price "doubled" on 2026-06-30. I did not open it, so this is unverified — [usagepricing.com](https://usagepricing.com/blueprint/activity/creatify-2026-06-30-pro-price-doubled)

**Arcads (AI UGC actors)**
- Arcads publishes no pricing page. Reviewers report:
  - Starter $110/mo for 10 videos; Creator $220/mo for 20 videos (~$11 per finished video).
  - Pro is custom priced and **API is included only in Pro**.
  - Max length 120 s.
  - A small edit means re-rendering, which costs another credit.

  Source (Jun 16, 2026): [eesel.ai Arcads pricing](https://www.eesel.ai/en/blog/arcads-ai-pricing)
- Further reported details (page updated Sep 5, 2026):
  - API needs "a customized offer". Public API docs were announced Apr 2026.
  - Models named: Seedance 2.5, Sora 2 Pro, Kling, Nano Banana, GPT Image.
  - Help center: Starter 8,000 credits/mo, Creator 16,000. Credits do not roll over.

  Source: [yespress.io Arcads](https://yespress.io/products/arcads.md)
- Note: Sora 2 Pro is listed, but the Sora API shut on Sep 24, 2026, so that page may be stale.

**Argil**
- Plans (Argil's own blog, Feb 9, 2026, modified Sep 28, 2026):
  - Pro $25/mo: all avatar models, watermark removal, full resolution.
  - Business $50/mo: Director workflow.
  - "API for plug and play integration". Credit counts not stated.

  Source: [Argil blog](https://www.argil.ai/blog/how-do-leading-ai-avatar-services-compare-on-pricing-in-2026)
- API pricing (official docs):
  - Video 160 credits/min. Voice 20 credits/min, **free if you link your own ElevenLabs account**.
  - 20-credit royalty per video for Argil stock (v1) avatars; none for custom avatars.
  - B-roll: 10 credits (AI image) or 20 (stock video).
  - Classic plan or above required. The dollar price per credit is not shown.

  Source: [Argil API pricing (official)](https://docs.argil.ai/resources/api-pricings.md)

**Tavus (Phoenix-4.5)**
- Developer plans (official page, conflicting tables, undated, © 2026):
  - Starter $22/mo: 15 video min, $1/min overage, 1 custom face slot, no watermark.
  - Builder $59/mo: 50 min, 3 custom faces.
  - Growth $397/mo: ~250 min, ~$0.80/min overage, 7 custom faces.
  - Business $975/mo.
  - The Free tier appears to be watermarked.
  - An older table on the same page shows Starter $59 with 10 min and replica training overage of $65 / $40.
  - Tier mapping is partly inferred because the table was garbled.

  Source: [Tavus pricing (official)](https://www.tavus.io/pals/pricing)
- REST API for replicas, personas, conversations and video generation. HIPAA, SOC 2 Type II and GDPR listed — [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)

**D-ID**
- Studio plans (Feb 2026, competitor source):
  - Lite: $5.90/mo, 10 min, D-ID logo on every clip.
  - Pro: $29/mo, 15 min, "AI" watermark.
  - Advanced: $196/mo, 100 min, custom logo instead of the watermark.

  Source: [Argil blog](https://www.argil.ai/blog/how-do-leading-ai-avatar-services-compare-on-pricing-in-2026)
- API plans: Build (16 min, personal use only), Launch (45 min), Scale (200 min). No dollar figures given. "V4 Expressive" avatars — [HeyGen blog, Oct 2026](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)

**Hedra (Character-3)**
- Studio rate is 6 credits/s; credits do not roll over. The developer API is priced separately and its rate is not published — [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)
- Plan range moved from $15–$75 to $20–$100/mo on Sep 27, 2026; the top tier went from $75 to $100 — [CostBench](https://costbench.com/changelog/hedra-api-price-increase-2026-09/)

**Higgsfield**
- Official pay-as-you-go API at cloud.higgsfield.ai with a Python SDK, gateway to 50+ models:
  - Kling 3.0: $0.112/s. Kling 2.5: $0.042/s. Seedance 2.5: $0.0738/s. Wan 3.0: $0.20/s.
  - Failed generations refunded. Balance expires after 1 year.
  - Talking-avatar/UGC models are not mentioned.
  - Source is a competitor; updated Oct 3, 2026.

  Source: [Apiframe Higgsfield API guide](https://apiframe.ai/guides/higgsfield-api-guide)
- App from $9/mo, credit-based (competitor page, Apr 7, 2026) — [videoai.me](https://videoai.me/compare/higgsfield-vs-topview)

**Topview**
- Pro: $16/mo billed annually ($31 monthly), 960 credits per year. Business: $40/mo annually ($76 monthly), 3,000 credits per year.
- "Avatar 4" model; Product Avatar (holds a product or shows an app, from one image).
- 2,000+ stock avatars and voices. Voice clones: 5 on Pro, 30 on Business.
- "API available", but no API pricing found.

Source: [EveryDev Topview](https://www.everydev.ai/tools/topview-ai)

**Google Veo 3.1 (Gemini API)**
- Specs (official docs):
  - Clips of 4, 6 or 8 s. **9:16 supported.**
  - 720p default; 1080p and 4K only for 8-s clips.
  - **Native audio always on**; put dialogue in quotes in the prompt.
  - Extension adds 7 s at a time, up to 148 s total, 720p only, not on Lite.
  - Up to 3 reference images (3.1 and Fast).
  - **Every Veo video carries a SynthID watermark.**
  - In the EU, UK, CH and MENA only `allow_adult` person generation is allowed.
  - Latency ~11 s to 6 min.

  Source: [Gemini API Veo docs (official)](https://ai.google.dev/gemini-api/docs/veo?hl=ja)
- Prices (read from Google's page on 2026-10-13):
  - Veo 3.1: $0.40/s (720p/1080p), $0.60/s (4K).
  - Veo 3.1 Fast: $0.10 / $0.12 / $0.30.
  - Veo 3.1 Lite: $0.05 / $0.08.

  Source: [BenchLM Veo pricing](https://benchlm.ai/media-pricing/veo)
- Google's docs now name "Gemini Omni Flash" as the default video model, with Veo 3.1 recommended for extension and last-frame control — [Gemini API video docs (official)](https://ai.google.dev/gemini-api/docs/video?hl=it)

**OpenAI Sora 2**
- Shutdown: web/app closed Apr 26, 2026; **API closed Sep 24, 2026**. Reason: compute moved to coding and enterprise — [The Decoder](https://the-decoder.com/openai-sets-two-stage-sora-shutdown-with-app-closing-april-2026-and-api-following-in-september/)
- Historical prices: sora-2 $0.10/s (720p); sora-2-pro $0.30 to $0.70/s — [BenchLM Sora](https://benchlm.ai/md/media-pricing/sora.md)

**Kling 3.0**
- Kling 3.0 launched Feb 5, 2026: native audio with lip sync, up to 15 s per clip, up to 4K. Kling 3.0 Turbo launched Jun 17, 2026 with improved talking-head and dialogue.
- Via the Atlas Cloud reseller: $0.084/s (Std image-to-video) to $0.112/s (Pro text-to-video).
- Turbo official list price: ¥0.8/s at 720p, ¥1/s at 1080p (~$0.11 and $0.14).
- Article dated Jul 14, 2026; competitor/reseller source.

Source: [Atlas Cloud](https://www.atlascloud.ai/blog/guides/kling-3.0-turbo-vs-kling-3.0)

**Runway**
- Plans (Jun 5, 2026, edited Aug 31, 2026):
  - Standard ~$15/mo, 625 credits. Pro ~$35/mo, 2,250 credits. Max ~$95/mo, 9,500 credits.
  - Gen-4.5 costs 12 credits/s (Pro ≈ 187 s per month). Gen-4 Turbo costs 5 credits/s.
  - Act-Two (performance capture) and lip sync are included from Standard; custom voices from Pro.
  - Credits are charged even for failed generations.
  - API price per credit not found.

  Source: [eesel.ai Runway pricing](https://www.eesel.ai/en/blog/runway-ai-pricing)

**Platform-added disclosure and regulation**
- Platform-added marks, as found above:
  - Mirage: non-removable provenance metadata.
  - Veo: SynthID on all output.
  - D-ID: logo or "AI" watermark on lower tiers.
  - HeyGen, Synthesia, Creatify and Captions Basic: watermark on free tiers.
  - Synthesia: labels its content under EU AI Act Art. 50.
- **EU AI Act Article 50**: transparency obligations, including deepfake disclosure, applied from Aug 2, 2026. Systems already on the market have until Dec 2, 2026 to add machine-readable marking. The Digital Omnibus delayed the high-risk deadlines but not Art. 50 — [FEDIL](https://fedil.lu/en/publications/ai-act-update-enforcement-begins-as-the-digital-omnibus-reshapes-the-timeline/?pdf=1)
- Social platforms and US law (secondary compilation, Jul 2026):
  - TikTok reads C2PA Content Credentials (since Jan 2025) and auto-labels AI content. It says the label "is not a distribution signal". It removed 51,618 unlabelled synthetic videos in H2 2025.
  - YouTube requires a label on realistic synthetic content, including cloned voices.
  - New York's Synthetic Performer law (signed Dec 11, 2025) requires disclosure of AI avatars in commercial ads, effective mid-2026.

  Source: [Kapwing statistics roundup](https://www.kapwing.com/resources/55-ai-generated-video-statistics-disclosure-detection-and-trust/)

### Inferences
- For "passes as a real person in a vertical Reel", the strongest automatable candidates are HeyGen Avatar V or IV (digital twin or photo avatar), Creatify Aurora 2.0, Mirage Avatar X and Tavus Phoenix-4.5. Veo 3.1 and Kling 3.0 can look more cinematic. But 8 to 15 s clip limits, no persistent identity across clips (only reference images) and SynthID make them weaker for a recurring presenter.
- Every option now leaves some machine-readable trace (C2PA metadata, SynthID) or will need one under EU Art. 50 by Dec 2026. Platforms such as TikTok can auto-label from these. Expect "AI-generated" labels on many posts whatever the realism.
- Sora-based UGC pipelines and tutorials published before Sep 2026 are now broken.

### Gaps
- HeyGen's official API pricing modal could not be read (JavaScript). The Avatar V $4/min figure comes from HeyGen's own blog, not its price sheet.
- Not confirmed:
  - Whether a digital twin made in HeyGen's web app can be used through the pay-as-you-go API (API *creation* is Enterprise-only).
  - Whether HeyGen's API output aspect ratio supports 9:16.
- No official 2026 prices found for: the D-ID API in dollars, Hedra's API, Topview's API, Runway's API per credit, Argil's price per credit, Arcads (unpublished).
- I did not read commercial-license clauses in the terms of service for any vendor; only plan-page statements were checked. HeyGen, Creatify and Argil license terms are unverified.
- Meta/Instagram's current AI-label rules were not checked.
- Synthesia's Express-3 release date and API support were not stated on the page I read.
- Synthesia's credits per minute conflict: ~100 (official page as fetched) vs 120 (HeyGen's comparison).

---

## 2. Realistic cost of about 2 short (30–45 s) vertical videos a day via API

### Takeaway
Two 30 to 45 s videos a day is about 60 videos and 30 to 45 output minutes a month (call it ~40 min). The cheapest credible realistic-avatar API paths:
- HeyGen Avatar III at ~$40/mo
- Tavus Builder at $59/mo
- HeyGen Avatar IV Photo at ~$120/mo
- HeyGen Avatar V twin at ~$160/mo
- Creatify API at $99 to $299/mo

Higher-cost paths are Mirage Avatar X (~$270 to $405/mo), Veo 3.1 (~$260/mo on Fast, ~$1,000+ on standard) and Arcads (~$660/mo, and no API below its custom tier). Voice adds roughly $0 to $22/mo. These are my calculations from the cited rates and exclude retries and rejected takes.

### Cited Findings (rates used)
- HeyGen API: Avatar III $1/min, Avatar IV Photo $3/min, Avatar V Digital Twin $4/min, $5 minimum wallet — [HeyGen blog, Oct 12, 2026](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)
- Mirage Avatar X: $0.15/s in 6-s increments. Captions: $0.15/min — [Captions API pricing (official)](https://www.captions.ai/help/docs/api/pricing)
- Creatify API: Starter $99 / 500 credits, Pro $299 / 2,000 credits. AI Avatar 5 credits per 30 s. Aurora 2.0 0.7 credits/s at 720p. Aurora 1.0 1 credit/s — [Creatify billing (official)](https://docs.creatify.ai/billing.md)
- Tavus: Starter $22 with 15 min, $1/min overage. Builder $59 with 50 min. Tier mapping partly inferred — [Tavus pricing (official)](https://www.tavus.io/pals/pricing)
- Synthesia: Creator/Pro $89/mo. API capped at ~360 min/year (~30 min/mo) — [Synthesia pricing (official)](https://www.synthesia.io/pricing)
- Arcads: ~$11/video. API only on the custom Pro plan — [eesel.ai](https://www.eesel.ai/en/blog/arcads-ai-pricing)
- Veo 3.1: $0.40/s; Fast $0.10/s at 720p; Lite $0.05/s. Extensions only at 720p — [BenchLM](https://benchlm.ai/media-pricing/veo), [Veo docs](https://ai.google.dev/gemini-api/docs/veo?hl=ja)
- Kling 3.0: $0.084 to $0.112/s (resellers); via the Higgsfield API $0.112/s — [Atlas Cloud](https://www.atlascloud.ai/blog/guides/kling-3.0-turbo-vs-kling-3.0), [Apiframe](https://apiframe.ai/guides/higgsfield-api-guide)
- Runway: Max ~$95/mo = 9,500 credits = ~791 s of Gen-4.5 per month — [eesel.ai](https://www.eesel.ai/en/blog/runway-ai-pricing)
- Argil: 160 credits/min of video + 20/min voice (voice free with your own ElevenLabs key) — [Argil API pricing (official)](https://docs.argil.ai/resources/api-pricings.md)

### Inferences (my cost model: 60 videos/mo, 30–45 s each = 1,800–2,700 s/mo)

| Option | Unit rate | Est. monthly cost for ~60 videos | Notes |
|---|---|---|---|
| HeyGen Avatar III (API) | $1/min | ~$30–45 | Lowest realism tier |
| HeyGen Avatar IV Photo (API) | $3/min | ~$90–135 | Photo of a person; no footage needed |
| HeyGen Avatar V Digital Twin (API) | $4/min | ~$120–180 | Needs a twin; API creation is Enterprise-only (see Gaps) |
| Tavus Phoenix-4.5 | Builder $59 incl. 50 min | ~$59 (or Starter $22 + ~$25 overage ≈ $47) | Mapping of minutes to tiers uncertain |
| Creatify AI Avatar (standard) | 5 cr per 30 s | 300–600 cr → API Starter $99 (or Pro if over 500) | 45-s videos bill as 60 s (10 cr) |
| Creatify Aurora 2.0 720p | 0.7 cr/s | ~1,260–1,890 cr → API Pro $299 | Higher-realism model |
| Synthesia API | $89/mo plan | $89 if ≤30 API min/mo; ~40 min likely exceeds cap | May need Enterprise |
| Argil API | ~107–120 cr/video | ~6,400–7,200 cr/mo; $ unknown | Price per credit not published |
| Mirage Avatar X + Captions API | $0.15/s + $0.15/min | ~$270–405 + ~$9 captions + TTS | Needs separate TTS |
| Veo 3.1 Fast (720p, extended) | $0.10/s | ~$180–270 | 8-s base + 7-s extensions; retries extra |
| Veo 3.1 standard | $0.40/s | ~$720–1,080 | — |
| Kling 3.0 (via API gateway) | ~$0.084–0.112/s | ~$150–300 | 15-s clips stitched |
| Runway Max plan | 12 cr/s Gen-4.5 | Max $95 covers only ~13 min/mo | Not enough for ~40 min |
| Arcads | ~$11/video | ~$660 (plan tiers of 10/20 videos insufficient) | API custom only |
| Captions app (Max) | 8 cr/s | Max's 500 cr ≈ 62 s/mo | App plans far too small |

- Retries, regenerations and rejected takes multiply these figures. Arcads reviewers estimate four tests per keeper — [eesel.ai](https://www.eesel.ai/en/blog/arcads-ai-pricing). Creatify refunds failed tasks ([changelog](https://docs.creatify.ai/api-reference/changelog.md)); Runway charges for failures ([eesel.ai](https://www.eesel.ai/en/blog/runway-ai-pricing)).
- Add TTS if the platform's built-in voice isn't used: roughly $0.03 to $0.06 per 40-s script on ElevenLabs (see Q4).

### Gaps
- Live dollar prices for D-ID API, Hedra API, Topview API, Argil credits and the Runway API were not found.
- Tavus minutes per tier are ambiguous on its page.
- Not checked: whether HeyGen pay-as-you-go API charges more for 9:16, or adds caption burn-in costs.

---

## 3. Which are scriptable end to end (script in, finished captioned vertical video out) with no human step

### Takeaway
Fully API-scriptable, with script plus avatar ID in and an MP4 out:
- HeyGen (API and Zapier actions with a captions option)
- Creatify (AI Avatar / AI Shorts endpoints)
- Synthesia API (Creator+)
- Argil API
- Tavus API

Mirage needs your own TTS audio first, then a second call for captions; that is still fully automatable. Veo 3.1 and Kling are scriptable but need stitching of 8 to 15 s clips and captioning, for example with ffmpeg in the sandbox. Arcads (custom API only), the Captions app, Hedra Studio, Higgsfield's UGC features and Topview are effectively human-in-app for this budget. Every custom digital twin needs a one-time human step: recording footage of yourself and giving consent.

### Cited Findings
- HeyGen Zapier: Google Sheets new-row trigger → Create Avatar Video (Scene) → Generate (captions setting, dimensions setting) → Avatar Video Success trigger → share link. Renders take 2 to 5 min — [HeyGen docs (official)](https://docs.heygen.com/docs/create-an-avatar-video-with-zapier.md)
- HeyGen custom digital twin creation via API is Enterprise-only. A twin is made from a 15-s phone clip in the app — [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis), [ThePlanetTools](https://theplanettools.ai/blog/heygen-avatar-v-tested-hands-on-review-2026)
- Creatify API includes AI Avatar, URL-to-Video, AI Shorts, AI Editing, Text to Speech and AI Scripts endpoints — [Creatify billing (official)](https://docs.creatify.ai/billing.md)
- Mirage Avatar X API:
  - Takes audio plus an image/video reference only, no script.
  - Audio 1 to 60 s. 9:16 at 720p.
  - Separate Add Captions API at $0.15/min.

  Source: [Mirage video generation docs (official)](https://captions.ai/help/docs/api/video-generation), [pricing (official)](https://www.captions.ai/help/docs/api/pricing)
- Argil API covers video, voice (or a linked ElevenLabs account) and B-roll insertion. Credits are bought in the app — [Argil API pricing (official)](https://docs.argil.ai/resources/api-pricings.md)
- Synthesia API is available from Creator; there is no API on Basic — [HeyGen blog](https://www.heygen.com/blog/best-ai-avatar-talking-head-apis)
- Arcads API requires a "customized offer" — [yespress.io](https://yespress.io/products/arcads.md)
- Veo 3.1 clip limits:
  - 8 s per clip, extension in 7-s steps at 720p.
  - Generated videos are stored only 2 days on Google's side.
  - Latency up to 6 min at peak.

  Source: [Veo docs (official)](https://ai.google.dev/gemini-api/docs/veo?hl=ja)
- Higgsfield has an official REST API and Python SDK for its model catalog. Its UGC and avatar app features are not documented as API endpoints — [Apiframe](https://apiframe.ai/guides/higgsfield-api-guide)
- The Captions app is priced for iOS and none of its plans mention an API — [Hooked](https://www.hooked.so/compare/captions-ai-pricing)

### Inferences
- A no-GPU Linux sandbox can drive all of the API options over HTTPS. Polling and webhooks are needed because renders take 2 to 6 minutes. Caption burn-in and clip stitching can be done locally with CPU ffmpeg.
- A Zapier-only path exists natively for HeyGen. For the others, Zapier "Webhooks by Zapier" or direct HTTPS would be needed. Native Zapier apps for Creatify, Tavus, Argil and Mirage were not verified.

### Gaps
- Not verified: native Zapier/Make apps for Creatify, Synthesia, Argil, Tavus, D-ID and Mirage.
- Not verified: whether HeyGen's API captions are burned in or delivered as a separate subtitle file, and whether they are styled for Reels.

---

## 4. Voice-only options (ElevenLabs and competitors) for pairing with our own visuals

### Takeaway
ElevenLabs is still the expressiveness leader:
- API rates: $0.10 per 1k characters (Multilingual v2/v3) and $0.05 per 1k (Flash/Turbo).
- Commercial rights from Starter (~$6/mo). Instant voice clone from Starter; professional clone from Creator.
- A 40-s script is ~600 characters, so ~$0.03 to $0.06 per video and ~$2 to $4 per month at 60 videos.

Cheaper credible alternatives:
- Cartesia: Pro $5/mo with instant cloning and a commercial license.
- OpenAI gpt-4o-mini-tts: ~$0.015/min, but no custom cloning.
- Google Chirp 3 HD: $30 per 1M characters.

### Cited Findings
- ElevenLabs official pricing page (seen Oct 15, 2026):
  - Free: 10k credits, no commercial use.
  - Starter: 30k credits; intro $1 "until Oct 18" (otherwise ~$6).
  - Creator: 121k credits; $11 intro / $22.
  - Pro $99 (600k), Scale $299 (1.8M), Business $990 (6M).
  - Professional voice cloning from Creator (1 voice); Scale 3, Business 10.
  - Free/Starter audio is 128 kbps; 192 kbps from Creator.

  Source: [ElevenLabs pricing (official)](https://elevenlabs.io/pricing)
- ElevenLabs API: Multilingual v2/v3 $0.10/1k chars; Flash/Turbo $0.05/1k. Commercial rights start at Starter $6/mo. Free-tier audio can't be used commercially. Updated Jun 23, 2026 — [Puter ElevenLabs API pricing](https://developer.puter.com/tutorials/elevenlabs-api-pricing/)
- Competitors (all from one article, Jul 16, 2026; the vendor has a conflict of interest):
  - ElevenLabs: Flash first audio ~75 ms; cloned voices cannot be exported.
  - Cartesia: Free 20k credits; Pro $5/mo (100k, instant clone, commercial license); Startup $49 (1.25M, professional clone); Scale $299 (8M) ≈ $37 per 1M.
  - OpenAI gpt-4o-mini-tts: ~$0.015/min, preset voices only, no cloning.
  - Google: Chirp 3 HD $30/1M, Neural2 $16/1M, Studio $160/1M; custom voice gated.
  - Azure: Neural HD $22/1M (cut from $30 in Mar 2026); Custom Neural Voice access gated.
  - PlayHT: Creator ~€31/mo with 10 instant clones.
  - Murf: API $30/1M standard, $10 Falcon.
  - Open-source: Chatterbox (MIT) and Orpheus can clone and are commercial-safe; XTTS-v2 is non-commercial. All need a GPU.

  Source: [Fora Soft ElevenLabs alternatives](https://www.forasoft.com/blog/article/elevenlabs-alternatives)
- Argil waives voice credits if you link your own ElevenLabs account. Creatify's TTS is 1 credit per 30 s — [Argil (official)](https://docs.argil.ai/resources/api-pricings.md), [Creatify (official)](https://docs.creatify.ai/billing.md)
- YouTube's disclosure policy covers AI-cloned voices in realistic content — [Kapwing](https://www.kapwing.com/resources/55-ai-generated-video-statistics-disclosure-detection-and-trust/)

### Inferences
- 60 scripts × ~600 characters ≈ 36k characters a month. That slightly exceeds ElevenLabs Starter's 30k credits, so it means Creator ($22) or Starter plus pay-as-you-go. Cartesia Pro's 100k credits at $5 would cover it.
- The open-source cloning models are not practical in a no-GPU sandbox unless hosted GPU is rented.

### Gaps
- Fish Audio, MiniMax Speech, Hume and Inworld prices were not verified (not in the fetched source).
- ElevenLabs' API terms on voice-clone consent were not read.

---

## 5. Independent quality comparisons and blind tests (2025–2026)

### Takeaway
Recent large tests show people are close to chance at telling modern AI video from real:
- Runway's Turing Reel (1,043 people): 57.1% accuracy; faces and hands were the most detectable categories.
- The DF26 benchmark of talking-person videos (Sep 2026): human accuracy 52.6%, the best detector 69.7% AUROC.

These are general video-model tests, not avatar-platform tests. I found no independent blind test that compares HeyGen, Synthesia, Creatify and similar avatar platforms head to head.

### Cited Findings
- Runway "The Turing Reel":
  - 1,043 randomly sampled participants. Each saw 20 five-second clips (10 real, 10 Gen-4.5 image-to-video from the same first frame, no cherry-picking).
  - Overall accuracy 57.1% (real 58.0%, generated 56.1%). Only 9.5% met the 15/20 significance bar.
  - Human categories (faces, hands, actions) were easiest at 58 to 65%. Animals and architecture fell below chance (45 to 47%).
  - Dated "Thursday, January 22" with no year. This is a vendor study.

  Source: [Runway research (official)](https://runway.com/research/theturingreel)
- DF26 benchmark (arXiv 2609.07369; authors from Ukrainian Catholic University, CTU Prague and Hover Inc.):
  - 271 real and 2,420 synthetic videos of one person speaking to camera, in official-statement or interview settings.
  - Generators: Veo 3.1, Kling 3.0, Wan 2.6, Grok Imagine 1.0, LTX 2.3 and others.
  - 232 human labelling sessions. Human accuracy 52.6% on DF26, vs 74.5% on the older CelebDF++. Only 25.2% on LTX 2.3 output, i.e. worse than chance.
  - Best detector GenD-PE: 69.7% AUROC, down from 89.9% on CelebDF++.

  Source: [AI Weekly summary](https://aiweekly.co/editors-blog/found-first-ai-video-fools-humans-at-52-6-near-chance-best-detector-tops-out-at)
- Kapwing roundup (Jul 2026, secondary, many uncited figures):
  - University of Florida researchers found AI detectors are at chance on AI video, while humans manage ~two-thirds accuracy.
  - A 2026 Gartner survey says 50% of US consumers prefer brands that don't use generative AI in customer-facing content.
  - 52% report lower engagement with content they believe is AI-made.
  - A *Journal of Advertising Research* study (DOI 10.1080/00218499.2025.2498830) found well-made, disclosed synthetic ads produced purchase intentions comparable to original ads.

  Source: [Kapwing](https://www.kapwing.com/resources/55-ai-generated-video-statistics-disclosure-detection-and-trust/)
- Vendor-internal avatar metrics only: HeyGen Avatar V LSE-C 8.97 and Face Similarity 0.840 — [ThePlanetTools](https://theplanettools.ai/blog/heygen-avatar-v-tested-hands-on-review-2026)
- Qualitative reviewer note: Creatify avatars are convincing in 15 to 30 s clips but show drift and "glossy skin" in longer ones — [Fast.io](https://www.fast.io/resources/creatify-ai-review-2026.md)

### Inferences
- The Turing Reel year is most likely 2026 (Gen-4.5 is described as Runway's latest model), but that is not stated.
- For 30 to 45 s presenter clips, the studies suggest most casual viewers can't reliably tell. Faces and hands are where tells remain, and longer clips raise the drift risk. Provenance metadata and watermarks (C2PA, SynthID) make *platform* detection more likely than *human* detection.

### Gaps
- A 2026 CESCG paper, "Real or Rendered: A Comparative Study of Fidelity in AI-Generated Avatars" ([CESCG](https://cescg.org/cescg_submission/real-or-rendered-a-comparative-study-of-fidelity-in-ai-generated-avatars/)), was found but not read. Its results are unknown.
- I found no independent, dated blind test comparing the avatar platforms themselves (HeyGen vs Synthesia vs Creatify vs Tavus).
- I did not read the DF26 primary arXiv paper. The figures come from a secondary summary.
