# Promo automation and AI video tools for an agent-run Etsy digital-products shop (as of Oct 4, 2026)

Notes conventions: every bullet ends with its source. "Zapier check (live)" means the Zapier MCP connector's app catalog was queried in this session on 2026-10-04 via `discover_zapier_actions`; it confirms an app exists and how many actions it exposes, not what each action does. "Session tool schema" means the tool definition exposed to the agents by the already-connected Canva or Adobe MCP connector in this session. Third-party pricing roundups are marked as such; where only a roundup was available, treat the number as UNVERIFIED against the vendor page.

## 1. Template/programmatic video APIs (Creatomate, Shotstack, JSON2Video, Remotion, Plainly, Canva, Adobe Express, CapCut)

### Takeaway
The shop's current self-rendered stack (HTML slides + Playwright + ffmpeg) is already equivalent to Remotion's free tier and costs $0; paid template APIs mainly buy a visual template editor and hosted rendering, which an agent pipeline does not strictly need. If one is added, Creatomate ($29/mo, Zapier app, about $0.23 per 30s vertical 1080p video) or Shotstack ($39/mo or pay-as-you-go, Zapier app, $0.20 to $0.30 per rendered minute) are the realistic choices; the Canva and Adobe MCP connectors the agents already have can produce or post-process video at no extra cost beyond existing plans.

### Cited Findings
**Creatomate**
- Plans: Essential $29/mo, Growth $99/mo, Beyond $299/mo (third-party listing, "verified Sep 2026"; UNVERIFIED on vendor page because creatomate.com/pricing did not render USD figures for the fetcher). [Toolradar](https://toolradar.com/tools/creatomate/pricing)
- Essential = 2,000 credits/month ("200+ videos"), 5 GB storage; Growth = 10,000 to 40,000 credits; Beyond = 50,000 to 200,000 credits; annual billing gives 2 months free; free trial of 50 credits, no card; API on all plans; docs link Zapier, Make, Pabbly and n8n integrations. [Creatomate pricing](https://creatomate.com/pricing)
- Credit formula: (width x height x fps x seconds) / 100,000,000; a 30s 1080x1920 25fps video = 15.55 credits; images always 1 credit; transcription free at 720p and above. [Creatomate docs: how credits are calculated](https://creatomate.com/docs/account/how-are-credits-calculated)
- "One minute of video at 720p (25 fps) is about 14 credits." [Creatomate pricing](https://creatomate.com/pricing)
- Zapier check (live): Creatomate app exists ("automatically create videos & banners from templates"), 1 read + 2 write actions. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/creatomate/integrations)

**Shotstack**
- Pay-as-you-go: $0.30/min, e.g. $75 for 250 credits (1 credit = 1 rendered minute), credits valid 1 year; packs of 25/50/100 also offered. Subscription: $0.20/min, from $39/mo for 200 credits, rollover up to 3x monthly allowance. Free sandbox: 10 credits valid 30 days. 1080p on standard plans (4K only on High Volume). "Make & Zapier Integration" listed on all plans; no watermark mentioned on paid. No date on page. [Shotstack pricing](https://shotstack.io/pricing/)
- Zapier check (live): Shotstack app exists, 2 write + 2 search actions. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/shotstack/integrations)

**JSON2Video**
- Free plan: 600 non-renewable credits, 1080p max, 60s max, watermark, no commercial use. Paid monthly plans (Hobby 3,000 credits about 50 min Full HD; Professional 12,000 about 200 min; Startup 30,000 about 500 min; Enterprise 78,000 about 1,300 min), no watermark, commercial use. Prepaid non-expiring packs of 7,200 and 15,600 credits. USD prices not shown in the docs page. [JSON2Video docs: plans](https://json2video.com/docs/v2/pricing/plans)
- Homepage advertises built-in text-to-speech voices alongside the JSON-to-video API. [JSON2Video](https://json2video.com/)
- Zapier check (live): search for "JSON2Video" returned no app. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps)

**Remotion (React-based, self-rendered)**
- Free License for individuals and companies of up to 3 people, unlimited videos, commercial use allowed. Company License for 4+ people: $25 per developer seat, $100/mo minimum. Enterprise from $500/mo. [Remotion license page (mirror)](https://scriptagc.wasmer.app/https_remotion_pro/license)
- Automators (render-based) license: $0.01 per render with $100/mo minimum (third-party review; not confirmed on vendor page). License trigger is headcount, not revenue. Rendering works by opening a React app in a headless browser, capturing frames, and stitching with FFmpeg; requires real React skill. [Spotsaas review](https://www.spotsaas.com/blog/remotion-review)

**Plainly (After Effects templates via API)**
- Listed on Capterra/Software Advice for 2026, but no pricing page was retrievable in this session. [Capterra: Plainly](https://www.capterra.com/p/10026817/Plainly/)

**Canva (Connect API, Autofill, MCP)**
- Canva's developer docs say Autofill and brand templates are available on Canva Pro, Teams and Enterprise (not Enterprise-only), and state "Only image assets can be used for autofill. Video assets are currently not supported." Usage limits "will be introduced in the future." [Canva Autofill guide](https://www.canva.dev/docs/connect/autofill-guide/)
- Contradiction: the Canva MCP connector already attached to the agents exposes `autofill-design` accepting `text`, `image`, `video` and `chart` field types, and `export-design` supports `mp4` (with quality such as `horizontal_1080p`) as well as png/jpg/gif/pdf/pptx. So video field fill and MP4 export appear available through the MCP even though the public Connect docs say video autofill is unsupported. [Session tool schema: Canva MCP `autofill-design`, `export-design`](https://www.canva.dev/docs/connect/autofill-guide/)
- Canva's launch post for Connect API general availability. [Canva dev blog](https://canva.dev/blog/developers/launching-to-all-connect-api)

**Adobe Express / Adobe for creativity (MCP, already connected)**
- `animate_design`: "Animate an Express design with motion effects"; works only on Express designs. [Session tool schema: Adobe for creativity MCP](https://www.adobe.com/express/)
- `video_create_quick_cut`: AI highlight reel picking "the most engaging moments" using visual engagement metrics, explicitly not speech/content-aware cutting. [Session tool schema: Adobe for creativity MCP](https://www.adobe.com/express/)
- `video_render`: renders a video from a JSON timeline (tracks, clips, gain, fit/fill, rotation) using uploaded asset IDs, max 10 minutes; also `video_resize`, `video_metadata`, `video_render_frame`, and `media_enhance_speech` are exposed. [Session tool schema: Adobe for creativity MCP](https://www.adobe.com/express/)

**CapCut**
- Searches returned only CapCut template gallery pages and unofficial GitHub "CapCut API" projects; no official public CapCut developer/render API was found. [CapCut templates help](https://www.capcut.com/th-th/help/new-templates); [unofficial cutauto repo listing](https://gitblind.noratr.app/Hommy-master/cutauto)

### Inferences
- Unit economics for a 30s 1080x1920 Short: Creatomate Essential about $29 / (2,000 / 15.55) = about $0.23/video, about 128 videos/month; Shotstack about $0.10 to $0.15/video if billed per fractional minute (rounding rule not verified). Both are cheap per video but carry a monthly floor that only pays off if the template editor saves meaningful agent or owner time.
- Remotion offers nothing the current Playwright + ffmpeg stack lacks for a 1 to 3 person shop, but its React composition model plus free license makes it the strongest "upgrade in place" if the HTML slide renderer becomes hard to maintain. Running it needs only npm (allowlisted registries), so it fits the container constraint.
- Canva MCP is the most interesting no-new-spend option: build a few branded vertical video brand templates once, then agents autofill text and product images and export MP4. Worth a hands-on test because the docs and the MCP schema disagree on video support.
- CapCut is not automatable for this pipeline; ignore.

### Gaps
- Creatomate USD prices not confirmed directly from the vendor page (rendered client-side); annual price not captured.
- JSON2Video USD prices not captured; JSON2Video Zapier presence not found (could exist under a different name).
- Plainly pricing and API details not retrieved.
- Shotstack per-render rounding (per second vs per minute) not confirmed.
- Whether Canva MCP video autofill/MP4 export requires a paid Canva plan, and any rate limits, untested.

## 2. AI voiceover (ElevenLabs, OpenAI TTS, others)

### Takeaway
ElevenLabs Starter ($5/mo, about 30 min of TTS, commercial rights, API) is the clear quality-per-dollar pick for short promo voiceovers, and it is reachable through either a Zapier app or ElevenLabs' hosted MCP server. OpenAI's gpt-4o-mini-tts is cheaper (about 1.5 cents per minute) but would need an approved API path because the containers cannot reach api.openai.com directly.

### Cited Findings
- ElevenLabs plans (Mar 24, 2026 roundup): Free $0, 10,000 credits (about 10 min), no commercial rights, attribution required; Starter $5, 30,000 credits (about 30 min), commercial rights, API; Creator $22, 100,000 credits (about 100 min); Pro $99, 500,000 credits; Scale $330; Business $1,320. Multilingual v2: 1 credit per character; Flash/Turbo: 0.5 credit per character. Annual billing about 17% off. Third-party source; UNVERIFIED against elevenlabs.io/pricing (fetch blocked). [BIGVU ElevenLabs pricing 2026](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/)
- Official ElevenLabs MCP server exists; the local `uvx elevenlabs-mcp` version is deprecated "in favor of the ElevenLabs hosted MCP server" at `https://api.elevenlabs.io/v1/mcp`. Tools include text_to_speech, voice design/clone, speech_to_text, isolate_audio, sound effects, and compose_music. Requires an API key. [Glama: ElevenLabs MCP](https://glama.ai/mcp/servers/elevenlabs/elevenlabs-mcp)
- Zapier check (live): ElevenLabs app exists with 2 write actions. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/elevenlabs/integrations)
- OpenAI gpt-4o-mini-tts: $0.60 per 1M text input tokens and $12 per 1M audio output tokens, about 1.5 cents per minute of audio; a forum user reported occasional trailing silence that is still billed (Mar 2025 post; pricing may have changed since). [OpenAI community: TTS pricing](https://community.openai.com/t/new-tts-api-pricing-and-gotchas/1150616)
- JSON2Video bundles TTS voices inside its render API. [JSON2Video](https://json2video.com/)
- Adobe MCP exposes `media_enhance_speech` (cleanup, not generation). [Session tool schema: Adobe for creativity MCP](https://www.adobe.com/express/)

### Inferences
- A 30s promo VO script is about 70 to 80 words, roughly 400 to 500 characters. On Starter that is about 60 VOs/month on Multilingual v2 or about 120 on Flash, comfortably above a daily Shorts cadence. Cost per VO about $0.04 to $0.08.
- The ElevenLabs hosted MCP also offers `compose_music`, which could replace the current generated-music step if quality is better; credits would be shared.
- Integration path ranking for the agents: (1) add ElevenLabs hosted MCP as a connector (clean, returns audio files), (2) Zapier ElevenLabs action (works today without new connectors, but file handoff back into the container goes through Zapier/Drive), (3) OpenAI TTS only if an approved API path exists.
- Voiceover materially helps retention and accessibility on Reels/TikTok/Shorts, but the source set here does not quantify that for this niche (see Gaps).

### Gaps
- No vendor-page confirmation of ElevenLabs 2026 prices or of what the 2 Zapier write actions return (audio URL vs file).
- Current (Oct 2026) OpenAI TTS pricing not confirmed on OpenAI's own pricing page.
- No credible data found comparing VO vs no-VO performance for faceless product promos.

## 3. AI avatar/presenter (HeyGen, Synthesia, Captions) vs faceless

### Takeaway
Avatars are the most expensive line item ($19 to $29/mo minimum for usable output, $2 to $6 per API minute) and add little for a $5 to $15 digital-download shop whose value is best shown by the product itself; a faceless screen-demo with voiceover is the better fit. HeyGen and Synthesia both have Zapier apps if a test is ever wanted.

### Cited Findings
- HeyGen (Aug 2026 roundup): Free $0, 1 min watermarked; Creator $29/mo, 600 credits (about 30 min of Avatar IV/V); Pro $49 and up; Business $149 + $20/seat. Credit costs: Avatar III 3 credits/min, Avatar IV/V 20 credits/min, Video Agent 30 credits/min. API: Video Agent prompt-to-video about $0.0333/s (about $2/min); Avatar IV about $0.05 to $0.10/s (about $3 to $6/min). Article says Zapier integration is on Business plans. Third-party; UNVERIFIED on heygen.com. [Creatify: HeyGen pricing 2026](https://creatify.ai/blog/heygen-pricing-(2026)-plans-and-what-you-ll-actually-pay)
- Zapier check (live): HeyGen app exists with 6 read + 32 write actions (the richest of any tool checked). [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/heygen/integrations)
- Synthesia (2026 roundup): Basic free, 1,200 credits/mo (about 10 min); Starter $19/mo ($168/yr), downloads and logo removal; Creator $89/mo ($708/yr), adds API access; standard video 120 credits/min; credits do not roll over. Third-party; UNVERIFIED. [Creatify: Synthesia pricing 2026](https://creatify.ai/blog/synthesia-pricing-(2026)-plans-credits-and-what-you-ll-actually-pay)
- Zapier check (live): Synthesia app exists (1 read + 2 write actions), positioned around personalized videos in transactional email. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/synthesia/integrations)

### Inferences
- Synthesia's API needs the $89/mo Creator tier, which fails the "clearly earns its cost" bar. HeyGen's Zapier app is the only avatar path that could be tested with existing connectors.
- For spreadsheet/template products, a recorded demo of the actual file plus a voiceover communicates more than a talking head, and avoids the "AI avatar" credibility hit that a brand named ProofNotFluff would want to avoid. This is judgment, not sourced data.

### Gaps
- Captions app (captions.ai) pricing and API status not researched in this session.
- No source quantified avatar vs faceless performance for Etsy/digital-download promos.

## 4. Clipping/captioning (Opus Clip, Submagic, Descript, Captions) without long-form source

### Takeaway
Clippers are built for long-form source and bill by source minutes, so they are a poor fit here. Captioning is the only useful function, and the pipeline can burn captions itself (it writes the script, so timings are known; or use free transcription on a TTS track). None of the clippers checked have a Zapier app.

### Cited Findings
- OpusClip (Aug 22, 2026 roundup): Free 60 credits/mo, Starter $15, Pro $29 (300 credits/mo), Business custom. 1 credit per minute of source footage processed. API: none on Free/Starter, limited on Pro, full on Business. Explicitly for repurposing "existing long-form recordings." [Creatify: OpusClip pricing 2026](https://creatify.ai/blog/opusclip-pricing-plans-and-what-you-ll-actually-pay-in-2026)
- Submagic (verified Jun 13, 2026 by CostBench, "80% confidence"): Starter $19/mo (15 videos, max 2 min), Pro $39/mo (40 videos, max 5 min), Business + API $69/mo (100 videos, API access); Magic Clips add-on +$19/mo; annual discounts of 37 to 41%. [CostBench: Submagic](https://costbench.com/software/ai-video-editing-saas/submagic/)
- Zapier check (live): no app found for "Submagic" or "Opus Clip". [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps)
- Creatomate transcription (auto-captions) is free for renders at 720p and above. [Creatomate docs: credits](https://creatomate.com/docs/account/how-are-credits-calculated)

### Inferences
- Submagic's API starts at $69/mo, far above budget for a function the pipeline can do in-house (ASS/SRT subtitles burned with ffmpeg, word-level timing from the script or from ElevenLabs speech_to_text).
- Adobe `video_create_quick_cut` is the only "clipper" available at no added cost, and only useful if a longer demo recording is produced first.

### Gaps
- Descript and Captions app pricing/API not researched.
- ElevenLabs TTS timestamp (alignment) output availability via MCP/Zapier not confirmed.

## 5. Stock/b-roll and screen-recording automation (spreadsheet demos)

### Takeaway
Playwright's built-in video recording can capture a spreadsheet demo programmatically at a custom size, output as WebM to be re-encoded by ffmpeg. Recording live Google Sheets or Excel Online is likely blocked by the container's network allowlist and login requirements, so the practical route is recording a locally served replica of the product.

### Cited Findings
- Playwright Python: `record_video_dir` and `record_video_size`; "The video size defaults to the viewport size scaled down to fit 800x800"; video is saved only when the context closes; output WebM. [Playwright docs: Videos (Python)](https://playwright.dev/python/docs/videos)
- A Playwright 1.59 "Screencast API for AI agents" is referenced in a 2026 guide's description, but the article body was not retrievable, so features (cursor overlay, annotations) are UNVERIFIED. [QASkills: Playwright 1.59 screencast guide](https://qaskills.sh/blog/playwright-1-59-screencast-api-guide-2026)
- A community Claude Code skill packages Playwright recording for video production. [Skillselion: playwright-recording](https://skillselion.com/skills/digitalsamba/claude-code-video-toolkit/playwright-recording)
- Adobe MCP exposes `asset_license_and_download_stock` (Adobe Stock) for b-roll/stills. [Session tool schema: Adobe for creativity MCP](https://www.adobe.com/express/)

### Inferences
- Set the viewport and `record_video_size` both to 1080x1920 (or record 1080x1350 and pad) to avoid the 800x800 default downscale.
- An animated cursor is easy without a tool: inject a CSS-styled div that follows scripted `page.mouse.move` steps, plus a click-ripple element. Typing into cells with `page.keyboard.type(delay=...)` gives a natural demo.
- For spreadsheet products, render the workbook to an HTML grid locally (or use an open-source in-browser spreadsheet component installed via npm) so the agent never needs Google/Microsoft auth.
- Stock b-roll adds little for this niche; the product itself is the visual.

### Gaps
- Whether docs.google.com or office.com is reachable from the containers was not tested.
- Adobe Stock licensing cost under the connected Adobe plan not confirmed.

## 6. Scheduling/repurposing (Buffer, Later, Metricool, Repurpose.io, Tailwind, Pinterest API)

### Takeaway
The current Zapier + Typefully setup misses TikTok: Zapier has no native TikTok publishing app. Buffer (free for 3 channels, $6/mo per channel on Essentials, has a Zapier app and a beta API) or Metricool (free 1 brand / 20 posts per month, Zapier app) are the cheapest ways to add TikTok. Tailwind is Pinterest/Instagram/Facebook only and not worth paying for when Pinterest already posts via Zapier.

### Cited Findings
- Zapier check (live): searching "TikTok" returns only TikTok Lead Generation and TikTok Conversions, no publishing app. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps)
- Buffer (May 13, 2026 roundup): Free $0, 1 user, up to 3 channels, 10 queued posts per channel; Essentials $6/mo per channel; Team $12/mo per channel. Supports TikTok, YouTube, Instagram, Pinterest, Facebook, LinkedIn, X, Threads, Bluesky, Mastodon, Google Business Profile. GraphQL API in beta, included in plans (100 to 500 requests/24h). Third-party; UNVERIFIED on buffer.com. [Zernio: Buffer pricing 2026](https://zernio.com/blog/buffer-pricing)
- Zapier check (live): Buffer app exists, 9 read + 3 write actions. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/buffer/integrations)
- Metricool (2026 roundup): Free $0, 1 brand, 20 posts/month, 30-day analytics, no LinkedIn/X; Starter $20 to $36/mo (annual) unlimited posting; Advanced $53+/mo adds API; X costs $10/mo per account extra. [SocialPilot: Metricool pricing](https://www.socialpilot.co/insights/metricool-pricing)
- Zapier check (live): Metricool app exists, 8 read + 5 write actions. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps/metricool/integrations)
- Tailwind: Free 5 posts/mo, Pro $29.99/mo (150 posts), Advanced $54.99, Max $99.99; supports only Pinterest, Instagram, Facebook; no TikTok/YouTube. [PostPlanify: Tailwind pricing](https://postplanify.com/tailwind-pricing)
- Pinterest API v5 video pins: register media (`POST /v5/media`), upload to presigned S3, poll status, then `POST /v5/pins` with `video_id`. Trial access pins are "visible only to the account that made it"; Trial = 300 org_write calls/day; Standard access requires app review. (Aug 23, 2026) [bundle.social: Pinterest Pin API](https://bundle.social/blog/pinterest-pin-api)
- Zapier check (live): no app found for "Repurpose.io" or for Later (search "Later" returned unrelated apps). [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps)
- Typefully MCP (connected) covers X, LinkedIn, Threads, Bluesky, Mastodon and Substack, with post analytics; not TikTok, Instagram, YouTube or Pinterest. [Session MCP server instructions: Typefully](https://typefully.com/)

### Inferences
- Buffer free (3 channels: TikTok + 2 others) is the $0 way to add TikTok, but the 10-queued-posts cap means the agent must schedule no more than about 10 days ahead per channel. Whether Buffer's Zapier "create" action supports video uploads to TikTok needs a test.
- Direct Pinterest API is not worth building: it needs app review to leave sandbox, and Zapier already posts pins.
- Typefully could absorb Threads and Bluesky at no extra cost, widening reach for text posts.

### Gaps
- Later and Repurpose.io pricing not captured (Repurpose.io pricing page fetch failed; Later not researched).
- Buffer Zapier action capabilities (video, TikTok) not inspected.
- Analytics depth per scheduler not compared.

## 7. Integration availability summary (Zapier / MCP / needs new integration)

### Takeaway
Already reachable today: Canva (MCP), Adobe Express (MCP), Typefully (MCP), plus via Zapier: Creatomate, Shotstack, ElevenLabs, HeyGen, Synthesia, Buffer, Metricool. Would need a new integration: JSON2Video, Submagic, Opus Clip, Repurpose.io, native TikTok posting, OpenAI TTS, direct Pinterest API. ElevenLabs is the one tool worth adding as its own MCP connector.

### Cited Findings
- Zapier apps found (live, 2026-10-04): Creatomate (1R/2W), Shotstack (2W/2S), ElevenLabs (2W), HeyGen (6R/32W), Synthesia (1R/2W), Buffer (9R/3W), Metricool (8R/5W). Not found: JSON2Video, Submagic, Opus Clip, Repurpose.io, Later, TikTok publishing. [Zapier MCP catalog, queried 2026-10-04](https://zapier.com/apps)
- ElevenLabs hosted MCP endpoint: `https://api.elevenlabs.io/v1/mcp`. [Glama: ElevenLabs MCP](https://glama.ai/mcp/servers/elevenlabs/elevenlabs-mcp)
- Remotion installs from npm and renders locally with FFmpeg, so it needs no external API. [Spotsaas review](https://www.spotsaas.com/blog/remotion-review)

### Inferences
- Zapier task usage is an unpriced cost: every render and every post consumes Zapier tasks on the owner's plan. Keep rendering in-container where possible and use Zapier only for posting.

### Gaps
- Zapier plan/task limits for this account not checked.

## 8. Recommended best-value stacks ($0, about $30, about $100 per month)

### Takeaway
At $0, keep the in-house renderer and add burned-in captions, a Playwright product demo segment, Canva MCP templated variants, and Buffer free for TikTok. At about $30, add ElevenLabs Starter ($5) for voiceover and either Buffer Essentials for more TikTok capacity or Creatomate Essential ($29) only if template variety is the bottleneck. At about $100, the only additions that plausibly earn their cost are ElevenLabs Creator ($22) and Metricool Starter or Buffer paid channels; avatars and clippers still do not.

### Cited Findings
- Price inputs: ElevenLabs Starter $5 / Creator $22 [BIGVU](https://bigvu.tv/blog/elevenlabs-pricing-2026-plans-credits-commercial-rights-api-costs/); Creatomate Essential $29 [Toolradar](https://toolradar.com/tools/creatomate/pricing); Shotstack $39/mo or $0.30/min PAYG [Shotstack](https://shotstack.io/pricing/); Buffer Free / $6 per channel [Zernio](https://zernio.com/blog/buffer-pricing); Metricool Free / Starter $20+ [SocialPilot](https://www.socialpilot.co/insights/metricool-pricing); Remotion free for up to 3 people [Remotion license](https://scriptagc.wasmer.app/https_remotion_pro/license); HeyGen Creator $29 [Creatify](https://creatify.ai/blog/heygen-pricing-(2026)-plans-and-what-you-ll-actually-pay); Submagic API $69 [CostBench](https://costbench.com/software/ai-video-editing-saas/submagic/).

### Inferences
- **$0/month**: Current HTML + Playwright + ffmpeg renderer (optionally migrate to Remotion, free under 4 people); Playwright `record_video` product demo clips at 1080x1920 with a scripted CSS cursor; ffmpeg-burned captions from the script; Canva MCP brand templates + MP4 export for variant looks; Adobe MCP `video_resize` for aspect variants; ElevenLabs Free only for testing (no commercial rights, so not for published promos); Buffer Free for TikTok (3 channels, 10 queued each); Typefully for X/LinkedIn plus Threads/Bluesky; existing Zapier for YouTube/Pinterest/Instagram.
- **About $30/month**: everything above + ElevenLabs Starter $5 (commercial VO, about 60 to 120 short VOs/mo, hosted MCP or Zapier) + Buffer Essentials for TikTok and 1 to 2 more channels at $6 each (about $12 to $18). Total about $17 to $23. Swap in Creatomate Essential ($29) instead of Buffer paid only if the HTML templates are the quality bottleneck.
- **About $100/month**: ElevenLabs Creator $22 (more VO, voice cloning for a consistent brand voice) + Creatomate Essential $29 or Shotstack subscription $39 (hosted renders and a template editor the owner can tweak) + Metricool Starter about $20 (analytics across TikTok/IG/Pinterest/YouTube in one place, Zapier app) + Buffer channels as needed. About $75 to $100. Still exclude avatars (HeyGen/Synthesia) and clippers (Opus/Submagic): no long-form source and no evidence they lift sales for low-ticket downloads.
- Every paid add should be gated on a measurable test (e.g. 2 weeks VO vs no-VO on the same product, compare views and Etsy click-throughs) before it stays in the stack.

### Gaps
- Owner's existing Canva, Adobe and Zapier plan tiers (which determine whether the "$0" options are truly zero marginal cost) were not checked.
