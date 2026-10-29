# 05_render: render, gates, queue

**Reads:** `04_scene/scene.js`, `03_cues/cues.json`, `02_transcript/words.json`, the voice audio, `_shared/sound.md`, `_shared/captions.md`
**Makes:** `05_render/<slug>.mp4` (not committed), `05_render/sheet.jpg`, `05_render/qa.json`, `05_render/captions.json`, `05_render/reviews/*.json`, a queue entry

1. `anim.py lint <slug>`: the layout check in code (text off the safe area, text under the host, the dialog box or other
   text). Fix every ERROR before rendering; it is cheaper than a gate round.
2. `anim.py render <slug>`: every frame in Chromium at 30 fps; voice, music bed and cue sounds mixed to -14 LUFS, true
   peak at or under -1.5 dBTP; H.264 and AAC. `anim.py check <slug>`: length 45 to 75 s (end card included), loudness, black, frozen, file.
3. `captions.json` from `_shared/captions.md` (Instagram, TikTok, Facebook, YouTube: keyword line, proof, takeaway,
   send line, tags; no AI voice line, Todd Oct 29).
4. `anim.py stills <slug>` and `anim.py gatepack <slug>`, then the gates in `video/studio/prompts/` (README there): facts,
   facts-captions, render critic, buyer, design, golden, each a fresh agent (model opus). One fix round per gate; a
   gate's own second FAIL holds the lesson for Todd.
5. All PASS: commit the lesson, then `anim.py ready <slug>` (it pins the commit), commit and push. It posts on the next
   daily run (POSTING.md). Nothing posts that is not in the queue.
