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
