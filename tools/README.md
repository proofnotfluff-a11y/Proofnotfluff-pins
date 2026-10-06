# Shorts tool

`python3 tools/make_slides.py spec.json out.mp4` builds a 1080x1920 YouTube Short in the slideshow style: five full-screen slides of text, each on screen for two bars of a soft generated music track (5.3 seconds), no voiceover. Every frame is rendered with Playwright at 30 fps, so motion is smooth. Needs numpy, ffmpeg, the pre-installed Playwright Chromium, and the Poppins Bold and Carlito fonts. About 75 seconds per video.

Spec: `theme` ("ink" or "paper"), `footer`, and `slides`, a list of five in this order:

1. `hook`: `kicker`, `title_html` (one `<span>` around the accent number)
2. `compare`: `kicker`, `left` and `right` as `{label, value, kind}`, `note`
3. `stat`: `kicker`, `label`, `value`, `kind` ("" or "bad" or "good"), `sub`
4. `fix`: `kicker`, `title`, `formula`, `sub`
5. `cta`: `title`, `button` (the product name), `sub` ("On Etsy: etsy.com/shop/ProofNotFluff", typed out because searching the shop name on Etsy only shows a small "did you mean the shop" link. Never point to the description: YouTube made Shorts description links unclickable in 2023. The tool rewrites any CTA that does.)

See example-slides-spec.json. Each slide teaches one number from the day's first pin; the product is named once, on the last slide. No em dashes anywhere.

Upload: commit the mp4 as shorts/YYYY-MM-DD-slug.mp4, confirm with curl that the raw URL returns video/mp4, then run the Zapier YouTube "Upload Video" action with the raw URL as the video, privacy public, category Education, tags from the pin, and description = the pin description, the listing link on its own line, then "#Shorts".

## Etsy listing videos: make_listing_video.py

`python3 make_listing_video.py <short-spec>.json out.mp4 [--slides 0,2,4]`

Turns a Short's spec into an Etsy listing video: the hook, the first stat or compare slide (else the fix), and the CTA, 4.6 s each (13.8 s), 1080 x 2160 (1:2), no audio track. The CTA line becomes "Instant digital download" (set `listing_cta_sub` in the spec to change it), since the viewer is already on Etsy. Content sits in the middle third, so it still reads when Etsy crops the gallery frame.

Etsy's rules, checked Oct 4, 2026 (help.etsy.com, "How to Add Listing Videos"): 3 to 15 seconds, sound removed, 100 MB max, 1080 px recommended, 2:1 or 1:2, up to 2 videos per listing. The script refuses output that breaks the length or size limit.

## Product demo videos: make_demo.py (the main promo format from Oct 4, 2026)

`python3 make_demo.py spec.json out.mp4 --format short|walkthrough|listing`

Shows the product's calculator on screen from frame one, types the inputs in, reveals the result cell (count-up), then an optional "fix" result and an Etsy end card. Captions are burned in; music from make_slides. Every frame is rendered from a timeline, so motion is exact.

- `short`: 1080x1920, about 10 to 15 s. YouTube Short, Instagram Reel, Pinterest video pin. Text stays out of the right 150 px and the bottom band where the platform buttons and titles sit.
- `walkthrough`: 1920x1080, paced to reading speed (about 15 characters a second), uses each row's `why` caption. Upload as a regular YouTube video; every Short's related-video link points to it, and line one of its description is the listing URL.
- `listing`: 1080x2160, no audio, 15 s max, end card says "Instant digital download". Etsy listing video.

Spec fields are documented at the top of make_demo.py; an example is promo/specs/demo-13-hourly-rate.json. The tool refuses specs with em dashes, banned words, no result row, more than 7 rows, or a CTA that points to an unclickable link. Every number must come from the product's own files and the CMO review checks this before anything posts.

## legal_scan.py (Legal desk first pass)

```
python3 tools/legal_scan.py <product.zip | folder> [--listing listing.md] [--tier high|medium|low]
```
Unpacks nested zips and checks every file for: Todd's personal details in text or metadata, promise wording ("guarantee", "pass any ATS", "IRS-approved"), words to read in context ("certified", "official"), em dashes and banned words, review comments and tracked changes, hidden sheets, cached error cells, a missing short notice or Terms of Use, no as-of date, and (with --listing) the required listing lines. Exit code 1 means a high finding. It never clears a product by itself: the reviewer still reads every page against legal/README.md.

## etsy_oauth.py (Etsy API connection; cloud session on the Default environment only)

`link` prints the approval URL; Todd approves; `exchange CODE STATE` stores the refresh token in the private vault repo (`/home/claude/proofnotfluff-vault/etsy.json`); `me` is the read-only test and records user_id and shop_id; `refresh` rotates the token (commit and push the vault after every refresh). The keystring comes from the ETSY_KEYSTRING environment variable and the x-api-key header is added by the environment's API credential, so neither appears in the repo or the output. If openapi.etsy.com is taken off that credential (it appeared to drop the Bearer token, Oct 5, 2026), set ETSY_SHARED_SECRET in the environment and the script sends `x-api-key: keystring:secret` itself.

## etsy_list.py (list a packed product through the Etsy API; Default environment only)

`inspect` and `taxonomy` and `show` are read-only. `check listing.md` validates the builder's listing.md (title length, 13 tags of 20 characters, price ladder, AI disclosure and digital-download lines, no em dashes, category in the ledger rule) without calling Etsy. `create listing.md product.zip img1..img5 [--video mp4] [--publish]` makes a draft, uploads images, the digital file and the optional video, and publishes only with `--publish`. who_made, when_made and the other required fields are copied from the newest live listing so new listings match what Etsy already accepted. The scheduled API lister (agents/api-lister.md) runs it after each Legal desk run.

## wb_style.py and render_xlsx.py (workbook design system, Oct 6)
- `tools/wb_style.py` builds every Excel and Google Sheets product to `design/WORKBOOK_STANDARD.md` (Arial, paper canvas, yellow inputs with blue numbers, ink result card, Start Here first and Terms last, validation and no-password protection on every input). Call `audit(wb)` before saving; it must return an empty list.
- `python3 tools/render_xlsx.py <file.xlsx> <out_dir> [--print] [--keep-pdf]` recalculates the workbook in LibreOffice, reports error values (exit 1 if any) and writes one PNG per sheet (or per printed page with --print). Open every PNG with the Read tool before shipping. `--print --keep-pdf` also gives per-sheet PDFs (the Start Here PDFs in a download come from this).
- Reference build: `engines/hourly-rate-quick-calculator/build_xlsx.py`.
- `tools/pnf_dash.py` (v3, Oct 6): the dashboard layer on top of wb_style: page_header, answer tiles, Card (title, eyebrow, input, calc, bar, text, close), frame, status_rule, highlight_rule. Every working tab uses it (design/WORKBOOK_STANDARD.md section 0).

## compare_xlsx.py, pack_product.py, listing_images.py (v3 rollout, Oct 6)
- `compare_xlsx.py old.xlsx new.xlsx map.json`: proves a redesign does the same maths. The map names each input and output cell in both files and the cases to try; it recalculates both in LibreOffice and prints a match table. Deliberate fixes are declared under "intended". Example: engines/hourly-rate-quick-calculator/compare_map.json.
- `pack_product.py product.xlsx LICENSE.txt out_dir --tier medium [--listing listing.md]`: Letter and A4 Start Here PDFs from the workbook's own print setup, ProofNotFluff metadata, the zip, legal_scan, the base64 text for the shelf and the sha256. out_dir must be new.
- `listing_images.py spec.json out_dir`: five 2000 x 2000 Etsy images built from real renders (cover on ink with the dashboard, detail shots with "trim": true for one-card crops and optional accent marks, a what's-inside image with tab thumbnails and a checklist). Example spec: engines/hourly-rate-quick-calculator/listing_images.json (its "base" is where the renders live; pass a copy with "base" set).
