# 05_render: render, gates, preview

**Reads:** `04_scene/scene.js`, `03_cues/cues.json`, `02_transcript/words.json`, the voice audio, `_shared/sound.md`
**Makes:** `05_render/<slug>.mp4` (on `video-renders`), `05_render/sheet.jpg`, `05_render/qa.json`, `05_render/caption.txt`

1. `python3 video/studio/anim.py render <slug>`: every frame drawn in Chromium at 30 fps, the voice, the music bed and
   the cue sounds mixed to -14 LUFS with the true peak at or under -1.5 dBTP, H.264 and AAC.
2. `python3 video/studio/anim.py check <slug>`: length 45 to 60 s, loudness, no black or frozen stretch outside the end
   card, the file decodes; writes `qa.json`.
3. Fresh reviewers (Agent, model opus, each sees only its inputs): facts (`video/prompts/facts.md` on the brief, the
   script and the data file), render critic (`video/prompts/render-critic.md` on the sheets and transcript), buyer
   (`video/prompts/buyer.md` on the script and caption), design (`video/prompts/design.md` on the sheet and frame one),
   then the golden review (`video/prompts/golden.md`) before Todd sees anything.
4. Preview to Todd: the MP4, the sheet, the caption in a code block, the gate lines, the fingerprints. He says "post" or gives a fix note.

One fix round per gate; a gate's own second FAIL stops the video and goes to Todd. No agent overrides a FAIL.
