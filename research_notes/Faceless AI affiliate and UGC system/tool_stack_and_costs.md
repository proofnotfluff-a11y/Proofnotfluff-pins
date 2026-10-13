# Tool stack and costs for an agentic faceless AI content system (product, UGC-style and affiliate video), as of Oct 13, 2026

Evidence tags used below: [M] measured by a named tester or benchmark; [C] community or forum report (single user, not verified); [V] vendor claim; [3P] third-party claim or estimate with no stated method; [Calc] my arithmetic from cited inputs. Every price carries the date the source says it was read or published. Many 2026 pricing pages are published by competitors; that is flagged where it applies. Note on method: the shared web-search budget ran out partway through, so a few items below are listed as gaps rather than researched.

## 1. Which open-weight video models are current, what hardware do they need, how fast are they, and what do their licenses allow?

### Takeaway
LTX-2.5 (Lightricks, 22B, open weights Aug 11, 2026) is the strongest open model for this use case: native audio, native multishot, image-to-video, up to 4K, and free for organizations under $10M revenue. In practice it needs 24 to 32 GB for the official checkpoints; 16 GB works only through community GGUF quants plus 32 GB+ system RAM, and 8 GB is not practical. Wan 2.2 (Jul 2025, Apache 2.0) is still the newest Wan you can download. It holds identity better in image-to-video but has no audio and is roughly 5 to 6x slower than LTX. HunyuanVideo 1.5 (8.3B) is a mid option that excludes EU, UK and South Korea use, and the new MiniMax H3 open weights exclude the US entirely.

### Cited Findings

#### LTX-2.5 (Lightricks): release, architecture, variants
- Open weights released Aug 11, 2026, with day-one ComfyUI support (ComfyUI v0.32.0 the same day). It is a 22B "asymmetric dual-stream diffusion transformer" that generates video and audio jointly. The text encoder is Gemma 4 12B. Tasks: text-to-video, image-to-video, video-to-video, text-to-audio and audio-to-video ([ComfyUI Wiki, Aug 11, 2026](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release); [OpenClawDC, read Sept 24, 2026](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)).
- Official files: a dev BF16 transformer and a distilled (few-step) BF16 transformer. Official ComfyUI quantizations are int8 "convrot" and NVFP4, both for the distilled transformer. The Gemma encoder ships in BF16 and int8. There are separate video and audio VAEs, 2x spatial and 2x temporal latent upscalers, a distilled LoRA and a "duration head" patch. No official fp8 is listed ([ComfyUI Wiki](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release)). A community FP8 e4m3fn build is listed on Hugging Face (repo title seen in search, not opened) ([HF guillaume127/LTX-2.5-FP8](https://huggingface.co/guillaume127/LTX-2.5-FP8)).
- [V] Features: native multishot (wide, medium and close-up in one generation) with character, environment, lighting and voice consistency across cuts. Other features: clip length predicted automatically from the described action, native 4K HDR, official ComfyUI templates for T2V, I2V and first/last-frame-to-video, and wrapper examples for IC-LoRA inpaint/outpaint, motion tracking, union control and text-to-audio ([ComfyUI Wiki](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release)). LoRAs trained for LTX-2.3 must be retrained for 2.5 ([AlphaSignal, Aug 12, 2026](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time)).
- Output limits (API variants): "Fast" goes up to 4K and "Pro" tops out at 1080p, with no visible watermark ([AlphaSignal](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time)). On the LTX API, Fast allows about 20 s per clip at 24/25 fps and Pro about 10 s ([AIReiter, Aug 13, 2026](https://aireiter.com/blog/ltx-2-5-api-pricing-guide)). LTX-2.5 is also available inside Runway's existing credit plans ([AlphaSignal](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time)).

#### LTX-2.5: VRAM (official numbers conflict)
- Lightricks itself publishes two different figures. The model page says "Min VRAM: 16GB", which assumes LTX Desktop with cloud text encoding by default. The official system-requirements page for the Python pipeline says "minimum 32GB+ VRAM" and recommends an 80 GB A100 or H100 ([OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)). AlphaSignal repeats "runs locally on any GPU with 16GB+ VRAM" ([AlphaSignal](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time)).
- No fetched source states a CUDA requirement for LTX-2.5. For LTX-2.3, InVideo lists Python 3.12+ and CUDA newer than 12.7 ([InVideo, Aug 6, 2026](https://invideo.io/blog/ltx-ai-video-generator/)). The brief's "CUDA 13.2+" could not be confirmed.
- Official on-disk sizes: transformer NVFP4 distilled 18.72 GB, INT8 convrot distilled 21.50 GB, BF16 distilled 42.02 GB; Gemma 4 encoder INT8 15.37 GB, BF16 26.26 GB. Sums: NVFP4 plus INT8 encoder about 34.09 GB, INT8 plus INT8 about 36.87 GB, BF16 plus BF16 about 68.28 GB.
- [3P, derived from file sizes, not measured] LTXWorkflow's tiers from those sizes: "No official LTX 2.5 checkpoint fits 16 GB". 16 GB means GGUF only; 24 GB means official INT8 or NVFP4 (tight) or GGUF Q6_K/Q8_0; 32 GB runs official INT8/NVFP4 comfortably, or BF16 with offloading; 48 GB+ runs BF16 fully resident ([LTXWorkflow, Sept 9, 2026](https://ltxworkflow.com/guide/ltx-2-5-vram-requirements)).
- NVFP4 needs Blackwell (RTX 50-series and newer) for native FP4. On older cards, ComfyUI says sampling "may actually be up to 2x slower than fp8" ([OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)).

#### LTX-2.5: community GGUF builds (the brief's agosh repo)
- Repo: agosh/LTX-2.5-Comfy-GGUF. File sizes from metadata: Q2_K 7.33 GB, Q3_K_S 9.45 GB, Q4_K_M 12.2 GB, Q5_K_M 14.8 GB, Q6_K 17.6 GB, Q8_0 22.7 GB (the card's own table differs slightly).
- Recommended VRAM including context: Q2_K 10-12 GB, Q3_K_S 12-16 GB, Q4_K_M 16-20 GB, Q5_K_M 20-24 GB, Q6_K 24 GB, Q8_0 32 GB+. Generation needs another 4-8 GB beyond the weights.
- Uploader's quality notes: Q2/Q3 give "poor quality results" (prototyping only); Q4_K_M is the best balance with minor loss; Q6_K is very close to BF16; Q8_0 is visually indistinguishable.
- Other details: no upload date is shown, and the card had 3,552 downloads last month. It is internally inconsistent (21B vs 22B). The license passes through the LTX-2.x Community License (free under $10M revenue) ([HF agosh/LTX-2.5-Comfy-GGUF](https://huggingface.co/agosh/LTX-2.5-Comfy-GGUF)).
- These quants cover the transformer only. The Gemma 4 encoder also needs a GGUF: Q4_K_M 8.41 GB, Q5_K_M 9.51 GB, Q2_K 5.96 GB (elix3r repo).
- Another distilled set (Abiray) lists Q3_K_S 12.65 GB, Q4_K_M 15.69 GB, Q6_K 18.62 GB and Q8_0 23.60 GB. The same quant level differs by repo ([LTXWorkflow](https://ltxworkflow.com/guide/ltx-2-5-vram-requirements)).

#### LTX-2.5: speed
- [C] Community reports collected by OpenClawDC:
  - RTX 5090 32 GB, distilled BF16 with offloading: 8 s 720p image-to-video in about 80 s (Aug 12, 2026).
  - RTX 5090, INT8 convrot: about 10 s at 720p works; 15 s text-to-video ran out of memory.
  - RTX 5060 Ti 16 GB, NVFP4 plus INT8 encoder: 1344x768 at 24 fps, a ~4.4 s clip in ~170 s, with system RAM above 92% (Aug 15, 2026).
  - MacBook Pro M4 Max 36 GB: "worked just fine", no timing given.
  - Laptop GPUs: no results. Intel and AMD: no data ([OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)).
- [C] Official Hugging Face repo thread (Aug 12-14, 2026):
  - RTX 3090 with 128 GB RAM: 5 s image-to-video in about 2.5 min without SageAttention. 10 s clips hung at VAE decode until the tile size was cut from 768 to 512.
  - RTX 5090 with 192 GB RAM: 720x1280, 15 s first/last-frame clip took about 1.5 min to generate plus about 1.5 min to decode, with SageAttention.
  - Lightricks staff: the diffusion VAE decoder needs "about 500x more tokens" for a 1080p, 121-frame video and can dominate total time. A faster convolution VAE decoder ships alongside it. There is no official int8 diffusion VAE yet ([HF Lightricks/LTX-2.5 discussion #15](https://huggingface.co/Lightricks/LTX-2.5/discussions/15)).
- [V] Lightricks claims:
  - A 10 s 720p clip in 6.8 s on 2x NVIDIA GB200 "at steady state", and 23.7 s via the LTX API.
  - "7.6x faster than the nearest closed-model competitor", citing these competitor timings (sources not identified): Veo 3.1, Grok 1.5 and "Omni Flash" at 52-70 s; Seedance 2.0 196 s; Kling 3.0 Pro 398 s ([AlphaSignal](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time)).
  - "6 to 8 seconds" for 10 s from one image on NVIDIA superchips with the distilled model ([ComfyUI Wiki](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release)).
  - No independent H100 or A100 timing was found.

#### LTX license (applies to LTX-2, 2.3, 2.5)
- Free under $10M in "total annual company revenue, measured across your organization"; a commercial license is required above that. "No usage caps, no seat fees" ([ltx.io license page](https://ltx.io/model/license)).
- Creative AI News says the $10M threshold includes affiliates and that there is no territory limit ([Creative AI News, Sept 30, 2026](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/)).
- Magic Hour notes that commercial use above the threshold without that agreement is "strictly prohibited", so LTX is "not open source" under strict definitions ([Magic Hour, Jul 24, 2026](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)).
- Summaries say you must include the license when redistributing weights or derivatives, fine-tuning is allowed, and there is no trademark grant ([CanIRun.ai](https://canirun.ai/license/ltx-2-community/)).
- No AI-labeling clause appears in any summary. The full LICENSE text was not read.

#### Earlier LTX releases
- Release history:
  - LTX-Video: Nov 21, 2024 (768x512 at 24 fps).
  - 0.9.5: Mar 2025. 0.9.7: May 2025 (13B). 0.9.8: Jul 2025 (generation up to 60 s).
  - LTX-2: Oct 23, 2025.
  - LTX-2.3: early 2026. 22B, dev and 8-step distilled, up to native 4K and 50 fps, about 10 s documented, native synchronized audio. LTX-2/2.3 use the LTX-2 Community License; 0.9.5+ was OpenRail-M ([InVideo](https://invideo.io/blog/ltx-ai-video-generator/)).
  - LTX-2.3 open weights: Mar 2026 ([Creative AI News](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/)).
- Conflict: a promotional DEV post calls LTX-Video "700M, Apache 2.0, 8 GB" ([DEV Community](https://dev.to/jondavis/open-source-ai-video-generators-in-2026-a-developers-benchmark-stack-guide-54i3)). Treat it as unreliable.
- [V] NVIDIA's LTX-2 guide (Jan 5, 2026):
  - 8-16 GB GPUs: 4 s clips at 540p24, 20 steps. 12 GB+: 3 s at 540p. 16 GB+: 4 s at 720p. 24 GB: 4 s at 720p24.
  - RTX 5090: 4 s 720p24 in "about 25 seconds". An 8 s clip takes about 3 min because it exceeds 32 GB and triggers weight streaming.
  - NVFP8 is about 30% smaller and "up to 2x faster" on RTX 40-series and newer ([NVIDIA GeForce, Jan 5, 2026](https://www.nvidia.com/pt-br/geforce/news/rtx-ai-video-generation-guide/)).
- [M] Magic Hour hosted test (one prompt, 5 s 720p): LTX-2.3 finished in 27-43 s and Wan 2.2 in 232-247 s. LTX output was 1296x720 at 24 fps (with audio, no extra credits); Wan was 1280x720 at 16 fps, silent. Host-config maximums: LTX-2.3 1080p/30 s, Wan 2.2 1080p/15 s ([Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)).
- [C] Users report that:
  - Wan holds face and body identity better in image-to-video, while LTX "really seems to struggle with not totally changing subjects in i2v".
  - LTX shows eye/eyelid degradation in multi-person scenes and has prompt-adherence complaints.
  - A 6 GB user ran 720p 10 s LTX-2.3 clips where Wan capped at 480p/5 s ([Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)).

#### Wan (Alibaba)
- Wan 2.2 (Jul 28, 2025, Apache 2.0) "is still the newest Wan that anyone outside Alibaba can download":
  - Wan 2.5-Preview (Sept 24, 2025), Wan 2.6 (Dec 16, 2025), Wan 2.7 (Apr 2026) and Wan 3.0 (public beta Aug 2026) have no public weights.
  - The Hugging Face Wan-AI organization has 27 repos, all Wan 2.1/2.2 variants or auxiliaries: Wan2.2-Animate-2-14B (Aug 2026, Apache 2.0) and Wan-Dancer-14B (Jul 2026, Apache 2.0).
  - A Hugging Face search for "Wan2.7" returns nothing ([HowAIWorks, Sept 6, 2026](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)).
  - RunPod agrees that Wan 2.7 "is available through Alibaba's own API surfaces only" ([RunPod, updated Sept 13, 2026](https://www.runpod.io/articles/guides/wan-2-7-runpod)).
  - Contradicted by RunAIHome, which says Wan 2.7 weights are on Hugging Face under Apache 2.0 (released Apr 22, 2026) ([RunAIHome, Jun 3, 2026](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)). MindStudio's title also calls Wan 2.6 "open source" without naming a license ([MindStudio, Feb 12, 2026](https://mindstudio.ai/blog/what-is-wan-2-6-video-open-source)). The later, evidence-backed sources are more credible.
- Wan 2.2 variants and VRAM:
  - TI2V-5B: 720p at 24 fps on one RTX 4090; 480p on a 12 GB card ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)). The official minimum is 24 GB with offloading; ComfyUI says native offloading fits it in about 8 GB ([Hivenet, Aug 17, 2026](https://www.hivenet.com/post/wan-2-2-cloud-gpu-comfyui)).
  - 14B T2V/I2V: a mixture-of-experts model (27B total, 14B active). Needs 54-65 GB at full precision ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)); the official single-GPU script asks for 80 GB ([Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)). GGUF Q4/Q5 shrinks the model to about 8-8.5 GB. With T5 on CPU: about 6-8 GB at 480p and 12-16 GB at 720p. On 16 GB at 720p with FP8 plus offload, peak is about 12-14 GB ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)).
  - Wan 2.1 1.3B: 8.19 GB ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)).
  - S2V-14B is audio-driven, and Animate is part of the family ([HowAIWorks](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)).
- [M] SaladCloud benchmark of Wan 2.1 T2V-14B (5 s clip, full precision, official script):

  | GPU | 480p | 720p |
  |---|---|---|
  | H100 SXM | 85 s | 284 s |
  | A100 SXM | 170 s | 523 s |
  | A40 | 501 s | 1,083 s |
  | RTX 4090 | 281 s | out of memory |

  ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/))
- [M] Wan 2.2-Animate on an RTX 3090: about 7 s per frame at 640x480 (about 9-10 min per 81-frame clip) and about 18 s per frame at 720p ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)).
- [3P] Wan 2.2 14B on RTX 4090: 4 min 20 s per 5 s clip. [C] An RTX 5090 owner: 9 min for a 10 s 720p Wan clip at FP8, vs 2.5 min for LTX at BF16. [V] TI2V-5B: a 5 s 720p clip "in under nine minutes" on a single consumer GPU ([Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2); [Hivenet](https://www.hivenet.com/post/wan-2-2-cloud-gpu-comfyui)).
- [3P, no method] Tier claims: RTX 4060 8 GB with Wan 1.3B, 5 s 480p in ~4-6 min; RTX 4070 12 GB with 14B GGUF at 480p, 18-22 min; RTX 4060 Ti 16 GB at 720p, 4-7 min; RTX 4090 with Wan 2.2 at 720p, 3-5 min ([RunAIHome](https://runaihome.com/blog/wan-video-local-ai-gpu-guide-2026/)).
- Wan 2.2 has no generated audio. Its README says Alibaba claims no rights over generated content ([Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)). Apache 2.0, with no territory limit or revenue cap ([Creative AI News](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/)).
- API-only Wan 2.6 features, for reference: 480p/720p/1080p at 24 fps, 5/10/15 s clips, single-pass audio, multi-shot via temporal markers ("Shot 1 [0-3s]") and up to three references for reference-to-video ([MindStudio](https://mindstudio.ai/blog/what-is-wan-2-6-video-open-source)).

#### HunyuanVideo 1.5 (Tencent)
- 8.3B parameters, native 720p (upscalable to 1080p), text-to-video and image-to-video, runs on "consumer GPUs (24GB VRAM)" ([Comfy blog](https://blog.comfy.org/p/hunyuanvideo-15-native-support)). About 14 GB with offloading; open weights Nov 2025 ([Creative AI News](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/); [Magic Hour](https://magichour.ai/blog/ltx-2-3-vs-wan-2-2)).
- Tencent Hunyuan Community License: commercial use is allowed, but the license "does not apply in the European Union, United Kingdom or South Korea". You must credit Tencent Hunyuan and follow Tencent's acceptable-use policy ([CanIRun.ai](https://canirun.ai/license/tencent-hunyuan-community/)). A separate license is needed above 100M monthly active users ([Creative AI News](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/)).

#### Other open models in 2026
All from [Creative AI News, Sept 30, 2026](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/) unless noted:
- MiniMax H3 (open weights Aug 2026, 33B): up to 2K, 15 s, native stereo audio. The license requires the UI to show "MiniMax H3", excludes the US, EU, UK and South Korea, and needs authorization above $20M revenue.
- LongCat-Video (Meituan, Oct 2025): MIT.
- Kandinsky 5.0 Video (Sept 2025): MIT.
- MOVA (Jan 2026): Apache 2.0.
- MAGI-2 preview (Aug 2026): Apache 2.0, 114B total / 6B active, needs eight Hopper GPUs (307 GB download), 10 s clips up to 1080p with audio.
- SANA-Video 2.0 (Aug 2026): 5B, Apache 2.0.
- SkyReels V3 (Jan 2026): Skywork Community license.
- Cosmos3 Image2Video (May 2026): aimed at robotics.
- Six of these families lack ComfyUI core support.
- MOVA-720p detail: about 48 GB VRAM (about 12 GB with layerwise offload), up to 720p, 8 s clips, joint audio and video. [V] Its scores (LSE-D 7.094, LSE-C 7.452, arena ELO about 1113.8) are unverified by third parties ([Creeta, Jul 9, 2026](https://news.creeta.com/en/open-source-lip-sync-models-2026/)).

### Inferences
- **16 GB laptop (e.g., an RTX 4090 Laptop):** LTX-2.5 is borderline. Expect GGUF Q3_K/Q4_K plus a Q4/Q5 Gemma encoder, 32 GB+ system RAM, and roughly 3-6 min per 4-5 s clip at about 720p, extrapolating from the desktop 5060 Ti 16 GB report (4.4 s in ~170 s). Laptop parts run at lower power, so they may be slower. LTX-2/2.3 at 720p for 4 s, and Wan 2.2 14B GGUF or 5B, are safer.
- **8 GB laptop (typical RTX 4060/4070 Laptop):** LTX-2.5 is not practical; even Q2_K wants 10-12 GB and is "poor quality". Usable options: LTX-2/2.3 at 540p for 3-4 s (NVIDIA guidance), Wan 2.2 5B with ComfyUI offload (~8 GB), Wan 2.1 1.3B, and the lip-sync models in section 2.
- **What 24 GB adds:** the official LTX-2.5 INT8 convrot checkpoint (21.5 GB transformer, tight) or GGUF Q6_K/Q8_0 near-BF16 quality; Wan 2.2 14B FP8 at 720p without crippling offload; LatentSync 1.6 (18 GB); HunyuanVideo 1.5 without heavy offload. It still does not allow 15 s LTX-2.5 single clips (even 32 GB ran out of memory at 15 s with INT8).
- **Model choice for product image-to-video:** where packaging, label and logo fidelity matters, Wan 2.2 is the safer open choice. LTX-2.5 is the volume and speed choice and the only open option that adds native audio and multishot. Plan an A/B quality gate per product.
- **Licensing:** a small operator like ProofNotFluff is well under LTX's $10M threshold, so LTX is commercially usable. Wan 2.2, LongCat-Video, Kandinsky 5, MOVA and SANA-Video are permissive with no threshold. HunyuanVideo 1.5 is usable in the US with attribution. MiniMax H3 open weights are not usable by a US operator.

### Gaps
- No independent measured LTX-2.5 timing on H100 or A100, and no timing at all on laptop RTX 4060/4070/4080/4090 GPUs.
- The official LTX-2.5 Hugging Face model card and LICENSE could not be fetched directly (provenance blocked), so the CUDA 13.2+ claim, any AI-disclosure clause and output-use clauses are unverified.
- No timings for Wan 2.2 with 4-step speed LoRAs (lightx2v/CausVid), which likely change the Wan cost picture materially.
- No Artificial Analysis video-arena ranks or Elo captured; the search budget was exhausted before this.

## 2. Which open-source talking-avatar, lip-sync, TTS and voice-cloning models are commercially usable, and what hardware do they need?

### Takeaway
For commercial lip-sync, LatentSync (Apache 2.0; 8 GB for v1.5, 18 GB for v1.6) and MuseTalk (MIT; 4 GB minimum, 256 px face) are the safe re-dub tools. LongCat-Video-Avatar 1.5 (MIT), MOVA (Apache 2.0) and daVinci-MagiHuman (Apache 2.0) are newer full-generation avatar models that want rented GPUs. Wav2Lip is non-commercial. For voice, Kokoro (Apache 2.0, runs on CPU) remains the right default. XTTS-v2 and F5-TTS weights are non-commercial. Chatterbox (MIT) is the permissive voice-cloning option.

### Cited Findings

#### Lip-sync and avatar models
- **LatentSync (ByteDance):** Apache 2.0 with no carve-out. v1.5 needs 8 GB for inference; v1.6 needs 18 GB and was trained at 512x512 "to mitigate the blurriness problem". It expects 25 fps video and 16 kHz audio; last code push was 2025-06-20 ([Creative AI News lip-sync, Sept 16, 2026](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/)). v1.6 was released Jun 11, 2025, is recommended on RTX 4090/A10-class GPUs, and is [3P] the highest-fidelity of the re-dub options ([Creeta, Jul 9, 2026](https://news.creeta.com/en/open-source-lip-sync-models-2026/)).
- **MuseTalk 1.5:** MIT, with a dependency manifest (sd-vae-ft-mse, Whisper and face-parsing are MIT; DWpose is Apache-2.0). Tested at 4 GB minimum on an RTX 3050 Ti laptop in fp16, where an 8 s video took about 5 minutes. [V] The README claims "real-time inference with 30fps+" on a Tesla V100. Face region is 256x256 ([Creative AI News lip-sync](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/)). About 8 GB is typical; released Mar 28, 2025 ([Creeta](https://news.creeta.com/en/open-source-lip-sync-models-2026/)).
- **Wav2Lip:** the README says "any form of commercial use is strictly prohibited", and the weights were trained on the LRS2 dataset. **SadTalker:** Apache 2.0 "except for the third-party components"; last push 2024-06-26 ([Creative AI News lip-sync](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/)).
- **LongCat-Video-Avatar 1.5 (Meituan):** MIT; created 2026-05-21; outputs 480P or 720P; 8-step inference via DMD2 distillation; INT8 quantization offered. No VRAM figure is published, and the setup example uses two GPUs ([Creative AI News lip-sync](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/)).
- **MOVA-720p (OpenMOSS):** released Jan 29, 2026; about 48 GB (about 12 GB with layerwise offload); up to 720p, 8 s clips; Apache 2.0. It generates new video and audio together rather than re-dubbing existing footage ([Creeta](https://news.creeta.com/en/open-source-lip-sync-models-2026/)).
- **daVinci-MagiHuman:** Apache 2.0. [V/3P] Distilled talking-head generation on one H100 takes about 2 s for 5 s at 256p, about 8 s at 540p and about 38.4 s at 1080p. Worked example: 75 minutes of 540p output needs about 2 H100-hours, roughly $5.82-5.96 at August rates ([Spheron, Aug 7, 2026, updated Sept 30](https://www.spheron.network/blog/self-host-ai-avatar-generator-heygen-alternative-2026/)).
- **Duix-Avatar:** an offline GUI cloning toolkit. Recommended spec: RTX 4070, 32 GB RAM, about 130 GB storage. Free global commercial use up to 100,000 users or $10M annual revenue ([Spheron](https://www.spheron.network/blog/self-host-ai-avatar-generator-heygen-alternative-2026/)).
- **Others, qualitative only** ([Pixazo, updated Sept 9, 2026](https://www.pixazo.ai/blog/best-open-source-ai-lip-sync-models)):
  - Hallo3: stable for "minutes at a time" (most models fail near 30 s); best on frontal portraits.
  - LivePortrait: real-time, but identity drifts on long clips.
  - Sonic: needs an A10/RTX 4090-class GPU.
  - Sync 1.9 Beta: "Free for individual and non-commercial use".
  - No license names or VRAM figures are given for these.
- **InfiniteTalk:** image-to-video and video-dubbing modes (including two speakers), 480p/720p, output "as long as the audio". Hosted through WaveSpeed at $0.03-0.06/s ($0.15 per 5 s); a "Fast" variant is $0.015/s ([MindStudio, undated](https://www.mindstudio.ai/models/wavespeed-ai-infinitetalk)). MindStudio calls it "by WaveSpeed", but a search listing attributes it to MeiGen-AI ([PixelSham listing, not opened](https://www.pixelsham.com/?p=25678)).
- **Wan2.2-S2V-14B** turns an audio track into video; it is part of the Apache 2.0 Wan 2.2 family ([HowAIWorks](https://howaiworks.ai/blog/alibaba-wan-open-weights-stopped-at-2-2)). **LTX-2.5** includes audio-to-video and multishot "voice consistency" natively ([ComfyUI Wiki](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release)).

#### TTS and voice cloning
- **Kokoro:** 82M parameters, Apache 2.0, no voice cloning, covers 11 languages. [V] "nearly 100x faster than real-time on a GPU" ([TTS.ai, Mar 21, 2026](https://tts.ai/blog/open-source-text-to-speech-guide-2026/?lang=or)). Runs on CPU with 1-2 GB. [3P] First audio in about 80 ms on CPU (about 50 ms on an RTX 4070); MOS about 4.0 ([PromptQuorum, updated Jul 15, 2026](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)).
- **XTTS v2:** licensed under the Coqui Public Model License (CPML), which is non-commercial. Coqui Inc shut down in January 2024, so "no commercial license is for sale". About 2x real-time on an RTX 4070; 4 GB minimum; 6 s reference audio recommended ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)).
- **F5-TTS:** code is MIT, but weights are CC-BY-NC-4.0 because of the Emilia dataset. The maintainer says the base model "cannot be used commercially also after finetuning". About 3 GB VRAM, RTF 0.15, English and Chinese primary ([Vantaige, May 10, 2026](https://vantaige.io/ai-tool/f5-tts)). About 3-5x real-time on an RTX 4070 ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)).
- **Chatterbox:** MIT, "no commercial restrictions", voice cloning supported, quality [3P] "Excellent" ([TTS.ai](https://tts.ai/blog/open-source-text-to-speech-guide-2026/?lang=or)).
- **Other permissive models:** CosyVoice2 (Apache 2.0, voice cloning), Dia (1.6B, Apache 2.0) and Sesame CSM (Apache 2.0). Orpheus uses the Llama 3.2 license and requires "Built with Llama" attribution ([TTS.ai](https://tts.ai/blog/open-source-text-to-speech-guide-2026/?lang=or)).
- **Other notes** ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)):
  - StyleTTS 2: MIT, no cloning, MOS about 4.3 in English.
  - Piper: CPU-only, real-time on a Raspberry Pi 5. The article contradicts itself on the license (GPL-3.0-or-later since 2025 vs MIT).
  - Tortoise: Apache 2.0, very slow.
- Voice cloning requires the speaker's authorization whatever the software license says. Rankings are deferred to the Artificial Analysis TTS leaderboard ([OfflineTTS, updated Sept 30, 2026](https://offlinetts.com/blog/tts-arena-leaderboard-2026/)).
- **Hosted TTS on fal (per 1,000 characters):**

  | Model | Price |
  |---|---|
  | ElevenLabs Multilingual v2 | $0.10 |
  | ElevenLabs v3 | $0.10 |
  | ElevenLabs Turbo v2.5 | $0.05 |
  | MiniMax Speech 2.8 HD | $0.10 |
  | MiniMax Speech 2.8 Turbo | $0.06 |
  | Gemini 3.1 Flash TTS | $0.05 |
  | xAI TTS v1 | $0.015 |

  ([fal.ai pricing, read Oct 13, 2026](https://fal.ai/pricing))

### Inferences
- **Narration:** keep Kokoro on the CPU cloud agent ($0). For a cloned recurring "brand voice", evaluate Chatterbox (MIT). Avoid XTTS-v2 and F5-TTS for monetized output because their weights are non-commercial.
- **Talking-head UGC on an 8 GB laptop:** MuseTalk re-dubbing a licensed presenter clip is feasible but slow (about 5 min per 8 s at 4 GB) and soft at 256 px. LatentSync 1.5 (8 GB) is the fidelity step up; LatentSync 1.6 needs a 24 GB card. Full-generation avatars (LongCat-Avatar, MOVA, MagiHuman) belong on rented GPUs.
- **Cost:** if MagiHuman's vendor numbers hold, open avatar generation on a rented H100 costs cents per output minute at 540p. That is orders of magnitude below HeyGen's API (about $10-20 per minute, section 3), but quality is unverified.

### Gaps
- InfiniteTalk's license, VRAM and speed were not verified from the MeiGen-AI repo. EchoMimic V3, OmniAvatar, HuMo, FantasyTalking, MultiTalk and Hallo3 licenses were not captured.
- Chatterbox VRAM, CPU speed and newer variants (Turbo, Multilingual) were not captured. Licenses and quality for VibeVoice, IndexTTS2, Qwen3-TTS and Higgs Audio were not captured.
- No TTS Arena or Artificial Analysis TTS ranks were captured.

## 3. What do hosted video, avatar, pay-per-use API and GPU rental options cost per unit, and what does a 10-second clip cost on rented GPUs?

### Takeaway
In Aug-Oct 2026, per-second API prices span:
- about $0.01/s for budget Wan 2.2 hosts,
- $0.02/s for Pruna P-Video at 720p,
- $0.05/s for Veo 3.1 Lite (720p) and Grok Imagine 1.0,
- $0.40/s for full Veo 3.1,
- $0.70/s for Sora 2 Pro at 1080p.

Self-hosting LTX-2.5 on a rented RTX 5090 costs about $0.02-0.04 of warm GPU time per 10 s 720p clip, versus $1.30-1.70 on LTX's own API. Wan 2.2 14B at 720p without speed LoRAs costs about $0.50-0.75 per 10 s on rented A100/H100, or about $0.05-0.13 on a rented RTX 4090. Avatar SaaS ranges from about $1.65 per 15 s video (Creatify Pro) to about $11 per video (Arcads).

### Cited Findings

#### Closed model APIs (per second of output)
- **Google Veo 3.1 (Gemini API, audio included):**

  | Model | 720p | 1080p | 4K |
  |---|---|---|---|
  | Veo 3.1 | $0.40 | $0.40 | $0.60 |
  | Veo 3.1 Fast | $0.10 | $0.12 | $0.30 |
  | Veo 3.1 Lite | $0.05 | $0.08 | not listed |

  ([BenchLM, read Sept 11, 2026](https://benchlm.ai/md/media-pricing/veo.md); [InVideo, Aug 2026](https://invideo.io/blog/ai-video-model-pricing)). Atlas Cloud lists an 8 s maximum for Veo 3.1 ([Atlas Cloud](https://www.atlascloud.ai/blog/cheapest-ai-video-generation-api-2026)).
- **OpenAI Sora 2 API:** sora-2 at 720p is $0.10/s ($0.05 batch). sora-2-pro is $0.30/s at 720p, $0.50 at 1024p and $0.70 at 1080p; batch is half price ([BenchLM Sora, read Sept 11, 2026](https://benchlm.ai/md/media-pricing/sora.md)).
- **Kling 3.0 official API:** $0.112/s at 1080p without audio, $0.168/s with native audio. One unit is $0.14; the smallest package is $700 for 5,000 units, valid 180 days ([Hooked, checked Sept 25, 2026](https://www.hooked.so/compare/kling-ai-pricing)). Kling 3.0 Turbo at 720p is ¥0.8/s, about $0.11 ([InVideo](https://invideo.io/blog/ai-video-model-pricing)). On fal: Kling v3 Pro $0.14/s; Kling 2.5 Turbo Pro image-to-video $0.07/s ([fal.ai](https://fal.ai/pricing)).
- **Kling consumer plans** ([Hooked](https://www.hooked.so/compare/kling-ai-pricing)):

  | Plan | Monthly | Yearly (per month) | Credits/month |
  |---|---|---|---|
  | Standard | $8.80 | $6.60 | 660 |
  | Pro | $32.56 | $24.42 | 3,000 |
  | Premier | $80.96 | $60.72 | 8,000 |
  | Ultra | $159.99 | $119.17 | 26,000 |

  Kling 3.0 costs 12 credits/s at 1080p and 9 at 720p with audio, or 8 and 6 without. Clips run 3-15 s. Free Basic output is "not for commercial use".
- **MiniMax / Hailuo:** MiniMax-H3 is $0.13/s at 2K with native stereo on MiniMax's own platform ([InVideo](https://invideo.io/blog/ai-video-model-pricing)). On fal: H3 Max $0.05/s, H3 Max Turbo $0.025/s ([fal.ai](https://fal.ai/pricing)). Older Hailuo models are priced per video: $0.28 for 6 s at 768p, $0.49 for 6 s at 1080p, $0.56 for 10 s at 768p ([InVideo](https://invideo.io/blog/ai-video-model-pricing)).
- **ByteDance Seedance:** billed by tokens. BytePlus at 720p charges $7.00 per million tokens without video input and $4.30 with it. InVideo's planning approximation is about $0.14/s at 1080p-class settings and about $0.022/s for Seedance Mini ([InVideo](https://invideo.io/blog/ai-video-model-pricing)). fal charges $0.014 per 1,000 tokens ([fal.ai](https://fal.ai/pricing)). Atlas Cloud lists Seedance 2.0 Fast at $0.11 per 5 s and Pro at $1.23 per 5 s, but that page has several internal inconsistencies ([Atlas Cloud, Jun 2026](https://www.atlascloud.ai/blog/cheapest-ai-video-generation-api-2026)).
- **Runway API:** $0.01 per credit (minimum $10). Gen-4 Turbo 5 credits/s ($0.05/s); Gen-4.5 12 credits/s ($0.12/s); Aleph 28 credits/s (56-credit minimum); Veo 3.1 via Runway 40 credits/s with audio (20 without); Veo 3.1 Fast 15/10. Web-app credits and API credits are not interchangeable ([CostBench, verified Aug 24, 2026](https://costbench.com/software/ai-media-apis/runway-api/)).
- **LTX API:**
  - LTX-2.5: Fast $0.13/s at 1080p, $0.19 at 1440p, $0.30 at 4K; Pro $0.17/s at 1080p (Pro caps at 1080p) ([AIReiter, Aug 13, 2026](https://aireiter.com/blog/ltx-2-5-api-pricing-guide)).
  - LTX-2.3: Fast $0.06/$0.12/$0.24 and Pro $0.08/$0.16/$0.32 (1080p/1440p/4K). Retake, extend and audio-to-video are $0.10/s ([InVideo LTX](https://invideo.io/blog/ltx-ai-video-generator/)).
- **Others:** Grok Imagine Video 1.0 $0.05/s and 1.5 $0.08/s (up to 1080p, one-pass audio); Pruna P-Video $0.02/s at 720p and $0.04/s at 1080p with audio; Alibaba HappyHorse ¥0.9/s at 720p (about $0.125) and ¥1.6/s at 1080p ([InVideo](https://invideo.io/blog/ai-video-model-pricing)).
- **Closed Wan versions:** Wan 2.6 on Alibaba Cloud is $0.10/s at 720p and $0.15/s at 1080p, with 50 s of free quota for new users ([MindStudio, Feb 2026](https://mindstudio.ai/blog/what-is-wan-2-6-video-open-source)). RunPod's managed endpoints start at $0.10/s for Wan 2.6 and $0.25 per 5 s for Wan 2.5 image-to-video ([RunPod](https://www.runpod.io/articles/guides/wan-2-7-runpod)).

#### Pay-per-use hosts for open models
- **Wan 2.2 (reviewed Oct 11, 2026; the page has no author disclosure and recommends 8Scale):**

  | Provider / variant | 480p | 720p | 1080p |
  |---|---|---|---|
  | fal A14B image-to-video Standard | $0.04/s | $0.08/s | n/a |
  | fal A14B Turbo image-to-video | $0.05/video | $0.10/video | n/a |
  | CFLabs Turbo | $0.005/s | $0.010/s | $0.018/s |
  | CFLabs Standard | $0.015/s | $0.030/s | $0.040/s |
  | WaveSpeed Ultra Fast | $0.01/s (5 s minimum) | not listed | n/a |
  | Kie.ai | not confirmed | $0.08/s | n/a |
  | SiliconFlow | $0.29/video | $0.29/video | n/a |

  fal Turbo clip duration is unconfirmed. Replicate appears only as historical July 2025 prices ($0.05 per 480p video, $0.10 per 720p) ([AIIDEList](https://aiidelist.com/blog/cheapest-wan-2-2-api-pricing-2026.md)).
- **fal serverless GPUs:** H100 $4.50/h list (as low as $2.49); H200 $6.00 ($2.99); B200 $7.99 ($5.49); RTX PRO 6000 96 GB $4.00 ($1.99). The page shows no date ([fal.ai, read Oct 13, 2026](https://fal.ai/pricing)).

#### Avatar and UGC SaaS
- **HeyGen** (via Arcade, a competitor, Sept 22, 2026) ([Arcade](https://www.arcade.software/post/heygen-pricing)):

  | Plan | Price | Credits | Avatar IV | Notes |
  |---|---|---|---|---|
  | Free | $0 | 3 videos/month, 1 min max | not stated | watermark, 720p |
  | Creator | $29/mo | 600 | 30 min/month | |
  | Pro | $49/mo | 1,000 | 50 min/month | 4K |
  | Business | $149/mo + $20/extra seat | 1,500 | 75 min/seat/month | |

  The API costs $0.50-0.99 per credit, and Avatar IV uses about 20 credits per minute, which is about $10-20 per API minute.
- **Arcads** (Jun 16, 2026): Starter $110/mo for 10 videos; Creator $220/mo for 20 videos. That is about $11 per video, up to 120 s each. API access only on the custom Pro plan. Arcads publishes no pricing page; these figures come from in-app paywall screenshots ([eesel](https://www.eesel.ai/en/blog/arcads-ai-pricing)).
- **Creatify** (via Shhots, a competitor, verified Aug 9, 2026) ([Shhots](https://shhots.ai/blog/creatify-pricing/)):

  | Plan | Monthly | Credits |
  |---|---|---|
  | Free | $0 | 10 per month (watermark, 9:16 only) |
  | Starter | $39 | 100 |
  | Pro | $99 | 300 |
  | API Starter | $99 | 500 |
  | API Pro | $299 | 2,000 |

  In the app, avatar and ad videos cost 5 credits per 15 s. On the API, URL-to-video and AI avatar cost 5 credits per 30 s, and Aurora costs 1 credit/s. That works out to about $1.95 (Starter) or $1.65 (Pro) per 15 s app video.
- **Captions / Mirage** (via Hooked, a competitor, checked Sept 25, 2026; iOS prices) ([Hooked Captions](https://www.hooked.so/compare/captions-ai-pricing)):

  | Plan | Monthly | Credits/month | Notes |
  |---|---|---|---|
  | Basic | $9.99 | 200 | AI Creator output watermarked |
  | Max | $24.99 | 500 | no watermark |
  | Frontier | $69.99 | 1,400 | |
  | Frontier 2x | $139.99 | 2,800 | |
  | Frontier 4x | $279.99 | 5,600 | |

  Mirage video costs 8 credits per second. No API is mentioned.
- **Higgsfield:** Higgsfield's own page lists Starter at $15/mo billed annually (200 credits) and Plus at $39/mo billed annually (1,000 credits, "20 percent" off monthly), with Kling 3.0 at about 33 videos on Starter. "365-Day Unlimited" covers Seedream 5.0 Lite and Flux.2 Pro, and may be throttled ([Higgsfield page, undated](https://geo.higgsfield.ai/task/blog/understanding-higgsfield-ai-pricing-plans)).
  - Conflict: Creatify (a competitor) says Plus is $34/mo, Ultra is $84/mo for 3,000 credits, Teams is $49/seat, the free plan gives 10 credits/day, and premium video models (Veo 3.1, Kling 3.0) cost "40-70 credits per generation". That is roughly ten times Higgsfield's own implied cost of about 6 credits per Kling video ([Creatify](https://creatify.ai/blog/higgsfield-pricing-%282026%29-plans-and-what-you-ll-actually-pay)).

#### GPU rental
- **RunPod pricing page** (updated Oct 8, 2026; one price per GPU, tier not labeled):

  | GPU | VRAM | Price/hour |
  |---|---|---|
  | RTX 3090 | 24 GB | $0.50 |
  | RTX 4090 | 24 GB | $0.89 |
  | RTX 5090 | 32 GB | $1.19 |
  | A40 | 48 GB | $0.59 |
  | L4 | 24 GB | $0.59 |
  | RTX A6000 | 48 GB | $0.59 |
  | L40S | 48 GB | $1.09 |
  | RTX PRO 6000 | 96 GB | $2.49 |
  | A100 PCIe / SXM | 80 GB | $1.79 |
  | H100 PCIe | 80 GB | $2.89 |
  | H100 NVL | 94 GB | $3.19 |
  | H100 SXM | 80 GB | $3.99 |
  | H200 | 141 GB | $5.29 |
  | B200 | 180 GB | $7.99 |

  Container disk is $0.10/GB-month; network storage is $0.07/GB-month under 1 TB ([RunPod](https://www.runpod.io/gpu-cloud/pricing)).
  - Conflict: RunPod's own guide (Sept 13, 2026) lists Community Cloud "from" $0.34 (4090), $0.69 (5090), $0.79 (L40S), $1.19 (A100 PCIe) and $1.99 (H100 PCIe) ([RunPod guide](https://www.runpod.io/articles/guides/wan-2-7-runpod)).
  - Serverless is billed per second, including the model-load cold start, with a default 5 s idle timeout ([RunPod docs](https://docs.runpod.io/serverless/pricing)).
- **Modal:** the Starter plan is $0/month plus compute, with $30/month of included free credits; Team is $250/month with $100 of credits. Per-second GPU rates work out to: H100 about $3.95/h, A100 80 GB about $2.50/h, A100 40 GB about $2.10/h, L40S about $1.95/h, A10 about $1.10/h, L4 about $0.80/h, T4 about $0.59/h ([Modal, read Oct 13, 2026](https://modal.com/pricing)).
- **Vast.ai and Lambda:** Vast.ai RTX 4090 about $0.15/h (spot, interruptible marketplace); RunPod 4090 about $0.44/h (secure); Lambda H100 about $3.29/h (all "approximate July 2026") ([PromptQuorum, Jul 2, 2026](https://www.promptquorum.com/prompt-bites/cloud-gpu-cost-per-hour)). Conflict: Spheron reports Lambda H100 on-demand at about $2.49/h, checked Jul 20, 2026 ([Spheron](https://www.spheron.network/blog/lambda-cloud-h100-pricing-2026/)).
- **Other providers:** Spheron H100 $4.20 on-demand / $2.77 spot, RTX 4090 $0.48 ([Spheron avatar post](https://www.spheron.network/blog/self-host-ai-avatar-generator-heygen-alternative-2026/)); Hivenet RTX 5090 €0.75/GPU-hour, billed per second ([Hivenet](https://www.hivenet.com/post/wan-2-2-cloud-gpu-comfyui)).

### Inferences
- **[Calc] Worked GPU cost per 10 s clip (warm GPU time only):** these figures exclude cold start, model download (LTX-2.5 official INT8 files total about 37 GB), failed or rejected takes, and idle time. A 2x multiplier for real-world overhead is a reasonable planning assumption.

  | Model / setting | GPU and basis | GPU time per 10 s | Cost per 10 s |
  |---|---|---|---|
  | LTX-2.5 distilled, 720p | RTX 5090 [C]: 8 s in ~80 s, or 15 s in ~180 s including decode | ~100-120 s | $0.033-0.040 at $1.19/h; $0.019-0.023 at $0.69/h; about €0.02-0.025 at Hivenet €0.75/h |
  | LTX-2.5, 720p | RTX 3090 [C]: 5 s in ~150 s | ~300 s | ~$0.04 at $0.50/h |
  | LTX-2.5, ~720p | 16 GB RTX 5060 Ti, local [C]: 4.4 s in ~170 s | ~6.4 min | electricity only; 10 s may not fit |
  | Wan 2.x 14B, 720p, full precision, no LoRA | H100 SXM [M, Wan 2.1 proxy]: 284 s per 5 s | ~568 s | $0.63 at RunPod $3.99/h; $0.62 at Modal $3.95/h |
  | Wan 2.x 14B, 720p | A100 SXM [M]: 523 s per 5 s | ~1,046 s | $0.52 at RunPod $1.79/h; $0.73 at Modal $2.50/h |
  | Wan 2.x 14B, 480p | H100 [M]: 85 s per 5 s | ~170 s | about $0.19 |
  | Wan 2.2 14B, quantized, 720p | RTX 4090 [3P]: 4 min 20 s per 5 s | ~520 s | $0.13 at $0.89/h; $0.05 at $0.34/h; ~$0.02 at Vast spot $0.15/h |
  | Wan 2.2 TI2V-5B, 720p | RTX 4090 [V]: under 9 min per 5 s | ~18 min | ≤$0.27 at $0.89/h; ≤$0.10 at $0.34/h |

  Renting an H100 for LTX-2.5 only pays off if it runs at least 2.4x (PCIe, $2.89) to 3.4x (SXM, $3.99) faster than a $1.19/h RTX 5090. No measurement exists, so default to a 5090 or a 48 GB L40S/A40/A6000.
- **[Calc] Hosted reference prices per 10 s:**

  | Option | Cost per 10 s |
  |---|---|
  | Wan 2.2, CFLabs Turbo 720p | $0.10 |
  | Pruna P-Video 720p | $0.20 |
  | MiniMax H3 Max Turbo on fal | $0.25 |
  | Veo 3.1 Lite 720p | $0.40 per 8 s clip |
  | Grok Imagine 1.0 | $0.50 |
  | LTX-2.3 Fast 1080p | $0.60 |
  | fal Wan 2.2 A14B 720p | $0.80 |
  | Veo 3.1 Fast 720p | $0.80 per 8 s |
  | Sora 2 720p | $1.00 ($0.50 batch) |
  | Wan 2.6 720p (Alibaba) | $1.00 |
  | Kling 3.0 1080p | $1.12 without audio, $1.68 with |
  | LTX-2.5 Fast 1080p | $1.30 |
  | LTX-2.5 Pro | $1.70 |
  | Veo 3.1 full | $3.20 per 8 s |
  | Sora 2 Pro 1080p | $7.00 |

- **Self-hosting vs API:** self-hosting LTX-2.5 is about 30-60x cheaper per clip than LTX's own API at 720p. The API wins only at low volume, where setup time and idle billing dominate.
- **Modal's free credits:** the $30/month Starter credit buys about 15 L40S-hours or about 7.6 H100-hours per month. That is enough for hundreds of LTX/Wan b-roll clips at a $0 cash tier, if the workload is batched to limit cold starts. L40S timings were not measured.
- **Avatar unit costs [Calc]:**

  | Option | Cost per unit |
  |---|---|
  | Creatify API Starter (500 credits per $99, 5 credits per 30 s) | ~$0.99 per 30 s video |
  | Creatify app, Pro | ~$1.65 per 15 s |
  | HeyGen Creator (30 Avatar IV minutes per $29) | ~$0.97 per minute |
  | Captions Max (500 credits per $24.99, 8 credits/s) | ~62 s of Mirage video per month, ~$0.40/s |
  | HeyGen API | ~$10-20 per minute |
  | Arcads | ~$11 per video |

### Gaps
- Not captured: Together AI video pricing, current Replicate per-second prices for Wan/LTX, Hailuo and Seedance consumer plans, Higgsfield's commercial-use terms, Kling's paid-plan commercial terms, and any Veo free tier.
- No measured LTX-2.5 timing on H100/A100/L40S, and no Wan speed-LoRA timings, so the A100/H100 Wan row likely overstates the cost of an optimized pipeline.
- RunPod's official page and its own guide disagree on 4090 and 5090 rates (likely Secure vs Community Cloud; the page does not label which).

## 4. What production and automation glue fits (ComfyUI, Remotion, ffmpeg, n8n/Make/Zapier, schedulers, posting APIs), and what limits apply to TikTok, YouTube and Instagram posting?

### Takeaway
The glue layer can stay near $0:
- Remotion is free for teams of up to 3 people.
- n8n Community Edition self-hosts for free.
- Postiz (AGPL) self-hosts with a full API on 2 vCPU and 2 GB.
- Buffer's new GraphQL API is included on the Free plan.
- YouTube now allows about 100 API uploads per day by default.
- Instagram allows 50-100 API posts per 24 hours.

The binding constraints are Zapier Free's 100 tasks/month (two-step Zaps only) and TikTok's audit, which keeps every direct-API post private until the app passes. Routing TikTok through the existing Buffer connection avoids that audit.

### Cited Findings
- **ComfyUI:** LTX-2.5 has official ComfyUI templates (T2V, I2V, first/last frame) and a ComfyUI-LTXVideo wrapper ([ComfyUI Wiki](https://comfyui-wiki.com/fr/news/2026-08-11-ltx-2-5-open-weights-release)); ComfyUI v0.32.0 added LTX 2.5 on Aug 11, 2026 ([OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)). HunyuanVideo 1.5 has native support ([Comfy blog](https://blog.comfy.org/p/hunyuanvideo-15-native-support)). LongCat-Video, MOVA, MAGI-2, SkyReels V3, SANA-Video 2.0 and Cosmos3 lack ComfyUI core support ([Creative AI News](https://www.creativeainews.com/articles/best-open-source-ai-video-models-2026/)).
- **Intel Arc:**
  - ComfyUI's XPU backend on an Arc B580 (12 GB) with Wan 2.2: "fp64 operations not supported", kernel compilation errors in the T5 or WanVideoSampler steps, fp8 and int8 models only partly working with out-of-memory errors at 960x544+, and inconsistent 640x352 results. CPU fallback is "20-60+ minutes per short video". Intel gave no technical fix in the thread (Feb 17-22, 2026) ([Intel Community](https://community.intel.com/t5/Graphics/Feature-Request-Enhance-Wan-2-2-Video-Model-Support-on-Intel-Arc/m-p/1737555)).
  - LTX Desktop does not list Intel or AMD GPUs for local generation ([OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)).
  - A search listing headline puts the Arc 140V "on par with GTX 1650" in CompuBench ([Wccftech listing, not opened](https://wccftech.com/intel-arc-140v-xe2-gpu-compubench-faster-radeon-780m-on-par-gtx-1650/amp/)).
- **Remotion:** free for individuals and companies of up to 3 people, with unlimited commercial use. Company License: "Creators" $25/month per seat; "Automators" $0.01 per render with a $100/month minimum. The render definition is not stated ([Tooliverse, verified Sept 20, 2026](https://tooliverse.ai/tools/remotion)).
- **n8n:** Community Edition is self-hosted, "genuinely free and imposes no vendor execution limit", and source-available. Cloud plans (billed annually): Starter €20/month (2,500 executions, concurrency 5), Pro €50/month (10,000), Business €667/month (40,000; also sold as a self-hosted license). One execution is one full workflow run, regardless of step count ([Jetadmin, Sept 26, 2026](https://www.jetadmin.io/blog/n8n-pricing/)).
- **Zapier vs Make** ([Jetadmin, Sept 29, 2026, prices checked Sept 26](https://www.jetadmin.io/blog/zapier-vs-make/)):
  - Zapier: Free is 100 tasks/month with "two-step Zaps only"; Professional $29.99/month ($19.99 annual); Team $103.50 ($69 annual). Each successful action is a task; Filters, Paths and Formatter are free.
  - Make: Free is 1,000 credits/month, 2 active scenarios, 15-min minimum interval; Core $10.59 ($9 annual) for 10,000 credits; Pro $18.82; Teams $34.12. Iterators use one credit per item.
- **Postiz:**
  - AGPL-3.0. Self-hosting is free and includes the API, MCP and AI features. Requires Postgres, Redis and Temporal (since v2.12.0). Official minimum is 2 vCPU and 2 GB RAM (4 GB+ for multiple users; 4 vCPU/8 GB recommended).
  - Cloud: $29/month for 5 channels, $39 for 10, $49 for 30, $99 for 100; 7-day trial ([Blotato, updated Sept 28, 2026](https://www.blotato.com/blog/mixpost-vs-postiz)).
  - Supports Instagram, YouTube, TikTok, Pinterest and others. Self-hosters must "create your OWN OAuth/developer application on each platform" ([DEV Community, mid-2026](https://dev.to/vikasprogrammer/buffer-wanted-100mo-so-i-self-host-postiz-for-15-dfa)). The API creates about 90 posts/hour self-hosted ([Upload-Post](https://www.upload-post.com/best-social-media-apis)).
- **Mixpost:** Lite is free and MIT-licensed but supports only Facebook Pages, X and Mastodon. Pro is $299 one-time and Enterprise $1,199 one-time, each with one year of updates. Instagram and the REST API are Pro-only. Self-host only, on PHP 8.3, MySQL, Redis and FFmpeg ([Blotato](https://www.blotato.com/blog/mixpost-vs-postiz)).
- **Posting APIs** (Upload-Post's own comparison, checked Sept 29, 2026) ([Upload-Post](https://www.upload-post.com/best-social-media-apis)):

  | API | Entry price | Free tier / notes |
  |---|---|---|
  | Upload-Post | $24/mo ($16 annual) | 10 uploads/month free |
  | Zernio (formerly Late) | $6/account/mo for accounts 3-10 | first 2 accounts free |
  | Outstand | $19/mo | 3,000 posts included, then $0.007/post |
  | Post for Me | $10/mo | up to 1,000 posts |
  | bundle.social | $100/mo (Pro) | 20 posts/month and 3 accounts free |
  | Buffer API | $5/channel/mo (Essentials, 7,500 requests) | 3 channels, 1 API key, 3,000 requests/month free |
  | Blotato | $29/mo | |
  | Post Bridge | $39/mo | |
  | Ayrshare | $149/mo | |

- **Ayrshare's own page** (modified Oct 12, 2026): Premium $149/month (up to 14 accounts), Launch $299, Business from $599. Unlimited posts and API calls; no free plan, 28-day trial ([Ayrshare](https://www.ayrshare.com/pricing.md)). getlate.dev now redirects to zernio.com (observed Oct 13, 2026); a competitor confirms Late is now Zernio and bills per connected account ([Ayrshare vs Zernio, Jun 20, 2026](https://www.ayrshare.com/compare/ayrshare-vs-zernio/)).
- **Buffer:** "Buffer's API is available on every Buffer plan, including Free". It is GraphQL, with OAuth fully managed, plus an MCP server and CLI (May 27, 2026) ([Buffer](https://buffer.com/resources/buffer-api-is-here/)). The legacy REST API is "being fully retired on February 1, 2027" (page title, not opened) ([Buffer](https://buffer.com/resources/legacy-rest-api-retired/)).
- **TikTok Content Posting API** (official docs, read Oct 13, 2026) ([TikTok for Developers](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post)):
  - "All content posted by unaudited clients will be restricted to private viewing mode."
  - Each user access token is limited to "6 requests per minute".
  - A per-creator daily post cap (`spam_risk_too_many_posts`) and a per-client daily active-user cap exist, but their values are unpublished.
  - Optional disclosure fields: `is_aigc` labels the video "Creator labeled as AI-generated"; `brand_content_toggle` marks a paid partnership for a third party; `brand_organic_toggle` marks promotion of the creator's own business.
- **TikTok audit:** stage 1 (product access) takes "Days"; stage 2 (content audit) takes "Weeks, and variable". Posts made while unaudited stay private even after the audit passes. The demo must show login, the consent screen, a composer built from `creator_info` and a confirmation screen; one-click publishing fails the audit ([bundle.social, Aug 4, 2026](https://bundle.social/blog/tiktok-api-approval)).
- **YouTube Data API:** the default is 10,000 units/day, plus separate 100-call/day buckets for `videos.insert` and `search.list`. Per Phyllo, the cost of `videos.insert` fell from about 1,600 units to about 100, effective Dec 4, 2025; the old default allowed about six uploads per day. Quota extensions need the audit form and take "several weeks to several months" ([Phyllo, Jun 25, 2026](https://www.getphyllo.com/post/is-the-youtube-api-free-in-2026-quota-limits-costs-when-to-pay); [bundle.social, Aug 4, 2026](https://bundle.social/blog/youtube-api-quota-exceeded-limits-fixes)). Google's own documentation was not fetched.
- **Instagram:** "Instagram accounts are limited to 100 API-published posts within a 24-hour moving period", and a carousel counts as one post. The same page's carousel section says 50 per 24 hours, an internal conflict. Usage can be checked via `content_publishing_limit`. Trial reels (shown only to non-followers) are supported through `trial_params` ([Meta for Developers, read Oct 13, 2026](https://developers.facebook.com/documentation/instagram-platform/content-publishing)).

### Inferences
- **Zapier throughput:** at roughly one task per post, Zapier Free's 100 tasks/month caps output at about 100 posts/month across all platforms. Posting 3 times a day to 4 platforms (about 360/month) needs one of:
  - Make Core ($10.59),
  - Zapier Professional ($29.99),
  - n8n self-hosted (free, but needs an always-on host),
  - direct APIs: YouTube and Instagram are cheap at this volume; TikTok can go through Buffer.
- **Schedulers on cloud agents:** ephemeral cloud agents cannot host Postiz or n8n schedulers. That needs a persistent VPS or the owner PC. The owner PC's Arc 140V is fine for CPU glue (Kokoro, ffmpeg, Remotion, Playwright) but is not a dependable video-diffusion node given the Intel XPU problems.
- **Disclosure fields:** the TikTok API's `is_aigc` and branded-content flags map directly onto AI and affiliate disclosure. The framework should set them per post; whether affiliate links require `brand_content_toggle` is a policy question outside this note.

### Gaps
- ComfyUI's HTTP/WebSocket API specifics and Comfy Cloud pricing were not captured (search budget exhausted).
- The n8n Sustainable Use License text, Pinterest API limits, and whether YouTube forces uploads from unverified API projects to private were not captured.
- No numeric TikTok per-creator daily cap is published.

## 5. What do product and trend research tools for TikTok Shop and Amazon cost, and which have free tiers?

### Takeaway
EchoTik is the only TikTok Shop tool here with a real free tier (50 searches/day per type, all regions); its paid plans start at $9.90-13.90/month. Kalodata (no free tier, 7-day trial, about $46-130/month) and FastMoss (about $49-139/month, trial only) are the paid standards. On Amazon, Helium 10 has a limited free plan, and Jungle Scout starts at $29/month billed annually.

### Cited Findings
- **Kalodata:** no permanent free tier; a 7-day free trial, "No credit card needed". App Store prices: US Basic $45.99/month, UK Basic $45.99, Starter $49.99, Global Standard $61.99, UK Standard $89.99, US Standard $99.99, Professional $129.99. Modules: Category, Shop, Product, Creator, Video & Ad, Livestream. [V] Claims 200M+ product records and 1,000 days of history, but says its figures are modeled estimates ([Koala Apps, a competitor, Aug 10, 2026](https://koala-apps.io/blog/kalodata-everything-you-need-to-know/)). EchoTik (a vendor) lists Kalodata at about $45/month Starter, $100+/month Full Premium, "No Free Tier", covering the US, UK and Southeast Asia ([EchoTik](https://api.echotik.live/guides/echotik-vs-kalodata)).
- **FastMoss** ([Delzonic, a competitor, Sept 14, 2026](https://delzonic.com/blogs/fastmoss-pricing-2026/)):

  | Plan | Monthly | First month | Annual (per month) |
  |---|---|---|---|
  | Basic | $49 | $29 | $47 ($558/yr) |
  | Pro | $89 | $53 | $72 |
  | Ultimate | $139 | $99 | $91 |

  History window 90 / 180 / 1,200 days; detail views per day 150 / 500 / unlimited. No permanent free plan (trial only).
- **EchoTik** ([Delzonic, Sept 14, 2026](https://delzonic.com/blogs/echotik-pricing-2026/)):
  - Free: $0, 50 searches per day per type, leaderboards capped at the top 100, no exports, all regions.
  - Basic $13.90/month ($9.90 annual); Pro $29 ($19.10); Enterprise $57 ($29.10).
  - History 30 / 90 / unlimited days; 7-day refund.
  - EchoTik's own page lists Basic at $10.19 and Pro at $19.1 ([EchoTik](https://api.echotik.live/guides/echotik-vs-kalodata)).
- **Jungle Scout and Helium 10** ([EcomCrew, updated Mar 24, 2026](https://www.ecomcrew.com/helium10-vs-junglescout/)):
  - Jungle Scout: Starter $49/month ($29 annual), Growth Accelerator $79 ($49), Brand Owner + CI $149 ($129). 7-day money-back guarantee, no free plan.
  - Helium 10: free plan with limited core tools, no card needed; Platinum $129 ($99 annual); Diamond $359 ($279). Its Starter plan was retired for new users in early 2026.
  - In the article's own test of 25 ASINs and 25 keywords, Jungle Scout's keyword volumes were closer to actual (-15.6% vs -53.8%), while Helium 10's sales estimates were closer.

### Inferences
- **$0 tier:** EchoTik Free plus Helium 10 Free, with a Kalodata 7-day trial for a one-off research sprint.
- **$50 tier:** EchoTik Basic or Pro ($9.90-29).
- **$150+ tiers:** FastMoss Basic ($47-49) or Kalodata Basic (about $46) once TikTok Shop creator and video-level data drives what gets made.
- **Amazon validation:** Jungle Scout Starter ($29/month annual) is the cheap paid option. Both Amazon tools are built for sellers, not affiliates.

### Gaps
- Kalodata's annual prices, FastMoss's trial length, API access for agent-driven data pulls (EchoTik, Kalodata, FastMoss), and affiliate-specific Amazon tools were not captured.

## 6. Which stack fits each budget tier ($0, about $50, $150 and $500 a month), what runs where, and what is the quality ceiling?

### Takeaway
- **$0:** CPU-native production (Playwright demos, Remotion templates, Kokoro voice, ffmpeg) plus Modal's $30/month free GPU credits for open-model b-roll.
- **About $50:** adds either pay-per-use API b-roll (Veo 3.1 Lite, P-Video or budget Wan hosts) or rented-GPU LTX-2.5 at cents per clip, plus a cheap TikTok research plan.
- **$150:** adds an avatar UGC subscription (Creatify, HeyGen or Captions) and a paid TikTok Shop research tool.
- **$500:** reaches near-frontier closed models with native audio (Veo 3.1, Kling 3.0, Sora 2 Pro) and premium UGC actors (Arcads) for proven winners.

The gaming laptop matters mainly for iteration speed and privacy, not cost. At 8 GB it runs LTX-2/Wan 5B and the lip-sync models; at 16 GB it runs quantized LTX-2.5; at 24 GB it runs official LTX-2.5 INT8.

### Cited Findings
Key inputs, all cited in sections 1-5:
- Kokoro: Apache 2.0, runs on CPU ([PromptQuorum](https://www.promptquorum.com/power-local-llm/local-tts-voice-cloning-piper-coqui-xtts)).
- Remotion: free for up to 3 people ([Tooliverse](https://tooliverse.ai/tools/remotion)).
- Modal: $30/month free credits ([Modal](https://modal.com/pricing)).
- Zapier Free: 100 tasks, two-step Zaps only ([Jetadmin](https://www.jetadmin.io/blog/zapier-vs-make/)).
- Buffer API: free on every plan ([Buffer](https://buffer.com/resources/buffer-api-is-here/)).
- TikTok direct API: private-only until audited ([TikTok for Developers](https://developers.tiktok.com/docs/en/content-posting-api-reference-direct-post)).
- YouTube: 100 uploads/day ([Phyllo](https://www.getphyllo.com/post/is-the-youtube-api-free-in-2026-quota-limits-costs-when-to-pay)).
- Veo 3.1 Lite: $0.05/s ([BenchLM](https://benchlm.ai/md/media-pricing/veo.md)).
- Pruna P-Video: $0.02/s ([InVideo](https://invideo.io/blog/ai-video-model-pricing)).
- CFLabs Wan 2.2 Turbo: $0.010/s at 720p ([AIIDEList](https://aiidelist.com/blog/cheapest-wan-2-2-api-pricing-2026.md)).
- RunPod RTX 5090: $1.19/h ([RunPod](https://www.runpod.io/gpu-cloud/pricing)).
- Creatify Pro $99 and API Starter $99 ([Shhots](https://shhots.ai/blog/creatify-pricing/)).
- HeyGen Creator $29 / Pro $49 ([Arcade](https://www.arcade.software/post/heygen-pricing)).
- Captions Max $24.99 ([Hooked](https://www.hooked.so/compare/captions-ai-pricing)).
- Kling Pro $32.56 / Premier $80.96 ([Hooked](https://www.hooked.so/compare/kling-ai-pricing)).
- Arcads $110 for 10 videos ([eesel](https://www.eesel.ai/en/blog/arcads-ai-pricing)).
- EchoTik, FastMoss and Kalodata prices ([Delzonic](https://delzonic.com/blogs/echotik-pricing-2026/); [Delzonic](https://delzonic.com/blogs/fastmoss-pricing-2026/); [Koala Apps](https://koala-apps.io/blog/kalodata-everything-you-need-to-know/)).
- NVIDIA LTX-2 VRAM tiers ([NVIDIA](https://www.nvidia.com/pt-br/geforce/news/rtx-ai-video-generation-guide/)).
- LTX-2.5 VRAM tiers ([LTXWorkflow](https://ltxworkflow.com/guide/ltx-2-5-vram-requirements); [OpenClawDC](https://openclawdc.com/blog/can-i-run-ltx-2-5-locally/)).
- MuseTalk at 4 GB and LatentSync at 8/18 GB ([Creative AI News lip-sync](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/)).
- Intel Arc XPU issues ([Intel Community](https://community.intel.com/t5/Graphics/Feature-Request-Enhance-Wan-2-2-Video-Model-Support-on-Intel-Arc/m-p/1737555)).

### Inferences

#### Where each piece runs (all tiers)
- **Cloud CPU agents** (2 CPUs, 7 GB RAM, no GPU): orchestration, scripting, Kokoro TTS, Playwright product demos, Remotion rendering (headless Chrome on CPU), ffmpeg assembly and captions, and calls to hosted APIs and posting APIs. They cannot run any video-diffusion or lip-sync model.
- **Owner PC** (Intel Arc 140V): the same CPU-class jobs, plus hosting persistent services (n8n Community or self-hosted Postiz) if it stays on. It is not a reliable diffusion node: no CUDA, Intel XPU errors with Wan, and no Intel support in LTX Desktop.
- **Gaming laptop** (NVIDIA, 8-16 GB):
  - 8 GB: LTX-2/2.3 at 540p for 3-4 s, Wan 2.2 5B with offload, MuseTalk, LatentSync 1.5.
  - 16 GB: LTX-2.5 GGUF Q3/Q4 (needs 32 GB+ system RAM), Wan 2.2 14B FP8 at about 720p.
  - 24 GB (desktop 3090/4090 class): official LTX-2.5 INT8, GGUF Q6/Q8, LatentSync 1.6, HunyuanVideo 1.5.
- **Rented GPU:** an RTX 5090 or 48 GB L40S/A40/A6000 for batched LTX-2.5 runs, Wan 14B at 720p and avatar models (MagiHuman, LongCat-Avatar, MOVA).

#### Tier $0 per month
- **Production:** Playwright product demos plus Remotion templates (free at 3 people or fewer), Kokoro voice-over, ffmpeg captions and assembly, all on the cloud agent.
- **Open-model b-roll:** generated in batches on Modal's free $30/month (about 15 L40S-hours). The operator must create the Modal account. If the laptop exists, it covers local LTX-2/Wan 5B b-roll and MuseTalk lip-sync.
- **Posting:** the existing Zapier Free plan (watch the 100-task cap), the Buffer API on the free plan for TikTok (avoids the TikTok audit), and direct YouTube and Instagram APIs.
- **Research:** EchoTik Free, Helium 10 Free and a Kalodata trial.
- **Avoid:** free tiers of closed generators for monetized posts (Kling Free output is "not for commercial use"; Creatify and Captions free output is watermarked).
- **Quality ceiling:** screen-capture and product-page demos, kinetic text, synthetic voice, short 540-720p AI b-roll inserts. No believable on-camera humans.

#### Tier about $50 per month (pick one generation path)
- **Path A, hosted API, no GPU work:** about $35-40 of credits. That buys about 90-100 Veo 3.1 Lite 8 s clips at $0.40 each with native audio, or about 175-200 P-Video 10 s clips at $0.20, or about 350-400 Wan 2.2 10 s clips at about $0.10 from budget hosts. Add EchoTik Basic ($9.90-13.90), and Make Core ($10.59) only if Zapier's cap binds.
- **Path B, rented GPU:** about $25-35 of RunPod/Vast/Hivenet time for LTX-2.5 at about $0.02-0.08 per 10 s 720p clip including overhead, which is effectively hundreds of clips. Add about $3/month of network storage for about 40 GB of weights, plus EchoTik.
- **Quality ceiling:** 720p (Veo Lite) or 720p-1080p (LTX-2.5) AI b-roll and product image-to-video with native audio; talking heads limited to MuseTalk/LatentSync re-dubs.

#### Tier about $150 per month
- Add one avatar UGC tool: Creatify Pro or API Starter ($99), HeyGen Creator ($29) or Pro ($49), or Captions Max ($24.99, only about 62 s of Mirage video per month).
- Add FastMoss Basic ($47-49) or Kalodata Basic (about $46), and keep about $20-40 of API or GPU spend for b-roll. Kling Pro ($32.56, about 250 s of 3.0 1080p with audio) is an alternative b-roll source.
- **Quality ceiling:** avatar-presenter UGC ads at 1080p (4K on HeyGen Pro), plus 1080p b-roll with audio. Still recognizably "AI presenter" rather than real-creator authenticity.

#### Tier about $500 per month
- **Avatar:** HeyGen Pro or Business ($49-149) plus Arcads Starter ($110 for 10 premium UGC videos), reserved for proven products.
- **Frontier b-roll:** Kling Premier ($80.96, about 667 s of 3.0 1080p with audio [Calc: 8,000 credits / 12 per second]) or Veo 3.1 Fast at $0.12/s for 1080p hero shots, with full Veo 3.1 at $0.40/s and Sora 2 Pro at $0.70/s only for flagship clips.
- **Research:** Kalodata US Standard ($99.99) or FastMoss Pro ($72-89).
- **Volume:** about $50 of rented GPU for LTX-2.5 volume and LoRA fine-tunes for character and product consistency.
- **Posting and automation:** Upload-Post ($24) or Zernio (about $6/account), and n8n Cloud Pro (€50) if self-hosting is unwanted.
- **Quality ceiling:** near-frontier 1080p-4K clips with native audio and multishot (Veo 3.1, Kling 3.0, Sora 2 Pro, LTX-2.5), plus high-realism avatar UGC. Content volume then becomes the limit, not quality.

#### Cross-tier rules for the framework
- Prefer permissive or threshold licenses (Wan 2.2 Apache 2.0; LTX under $10M revenue; MuseTalk MIT; LatentSync Apache 2.0; Kokoro Apache 2.0; Chatterbox MIT).
- Never use Wav2Lip, XTTS-v2, F5-TTS weights, Sync 1.9 free tier or Kling Free output commercially.
- Do not use MiniMax H3 open weights from the US.
- Set TikTok's `is_aigc` flag on AI-generated posts.

### Gaps
- Unverified items behind the tier math:
  - Real-world throughput of LTX-2.5 on Modal's L40S, so the "hundreds of free clips" estimate needs a pilot.
  - Wan speed-LoRA economics.
  - Laptop-GPU timings, since the laptop's model and VRAM are unknown.
  - Higgsfield's true credit cost per premium video (sources differ about tenfold).
  - Commercial-use terms for paid Higgsfield, Kling, Captions and Creatify output.
- Quality comparisons rest on vendor claims and user anecdotes, not a controlled benchmark. The Artificial Analysis video and TTS leaderboards could not be retrieved (search budget exhausted).
