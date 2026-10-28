# Sound

- **Music:** one bed from `tools/music/library.json` (our own compositions), named on the first cue: `music: quiet-math 0.18`
  (the level is the bed's gain against the voice; 0.12 to 0.22). It ducks under the voice and fades out over the last 1.8 s.
- **Effects:** `[sfx: name]` on a cue fires on its first word. Ours, made in code by `anim.py kit` (no samples, no licenses):
  `blip` (a soft UI blip), `tick` (a counter tick), `whoosh` (a section change), `pop` (something appears), `stamp` (a
  verdict lands), `chime` (the close), `squeak` (Squeak, sparingly).
- At most one effect every 1.5 s; never on top of a number being said.
- The mix: voice untouched, effects about 12 dB under the voice, then -14 LUFS integrated and a limiter so the MP4's true
  peak stays at or under -1.5 dBTP.
