# 03_cues: the storyboard

**Reads:** `02_transcript/transcript.md`, `01_voice/brief.md`, `_shared/desk.md` (real screens), `_shared/kit.md` (what can be drawn), `_shared/sound.md`
**Don't read:** `words.json` (the command does)

1. Write `03_cues/cues.md`, one cue per visual change:
   ```
   ## map "South Chicago, the community area" [sfx: whoosh]
   The 77 areas draw in; South Chicago lights up. Snow points at it.
   ## map.count "logged forty-five" [sfx: tick]
   The 45 counts up beside the area.
   ```
   - Top-level cues are sections: each becomes one scene function. Sub-cues (`map.count`) are beats inside it.
   - The quote is 3 to 6 words copied from `transcript.md`; the cue starts on its first word. `+0.3` after the quote shifts it; `@12.5` pins a time.
   - A new beat every 2 to 5 seconds (a Reel moves faster than a lesson). Say what is on screen and what the cast does.
   - Anything the words name that exists (a number from the City's data, our map, our page) is shown for real (`_shared/desk.md`). The cast carries the idea.
   - Sound: `[sfx: name]` fires on that word (`_shared/sound.md`); `music: name 0.2` (a library bed) or `music: rooms` (the room loops, which follow each section's `Room:` line) on the first cue sets the music.
2. `python3 video/studio/anim.py cues <slug>` matches every quote and writes `cues.json` with each cue's time; a quote
   it can't find stops the run with the closest words.

**Makes:** `cues.md` (source), `cues.json` (generated, never edit)
**Check:** read the storyboard: every beat worth seeing, the story in the right order, every number on screen from the brief.
