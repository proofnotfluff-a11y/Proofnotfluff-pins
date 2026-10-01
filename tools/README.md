# Shorts tool

`python3 tools/make_short.py spec.json out.mp4` builds a 1080x1920 YouTube Short: every frame rendered with Playwright (smooth 30 fps), voice from Piper TTS (voice downloads itself from the piper GitHub release on first use, about 60 MB), and a soft generated background track. Needs: `pip install --break-system-packages piper-tts numpy`, ffmpeg, the pre-installed Playwright Chromium, Poppins and Carlito fonts. About 90 seconds per video.

Spec fields: kicker, headline_html (one `<span>` for the accent number), cells (2 to 4 of label, value, kind "" | "bad" | "good"), fix, cta, footer, voice ("ryan-medium" or "lessac-medium"), voice_lines (exactly 5: headline, cells 1 and 2, cell 3, cell 4 plus fix, cta). Write numbers as words in voice_lines ("one ninety four", "fifteen and a half percent") so the voice reads them well. See example-spec.json.

Upload: commit the mp4 under shorts/, confirm the raw URL serves it, then the Zapier YouTube "Upload Video" action with the raw URL as the video, privacy public, category 27 (Education) if available, tags from the pin, description = the pin description plus the listing link on its own line and "#Shorts".
