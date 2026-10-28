# Sound

All of it is made by `anim.py` (`sound` builds the files, `render` and `remix` mix them). No samples, no licenses.

- **Music, two ways** (on the first lines of `cues.md`):
  - `music: steady-hands 0.12`: one bed from `tools/music/library.json` (our own compositions). The tracks run 36 to
    60 s, so for a longer lesson the A and B sections loop on the bar line.
  - `music: rooms`: four chiptune loops made in code, one per room (`_runtime/music/framing|blackboard|workshop|garage.wav`).
    Same key (A minor), tempo (96 BPM) and chords, 8 bars (20 s) each; the rooms change what plays under a quiet square
    lead: framing is half-time and sparse, blackboard has fast arpeggios, workshop has offbeat stabs and hats, garage
    has a pulse bass riff, kick and snare. A top-level cue whose description starts `Room: blackboard.` moves the music
    to that room; a section with no `Room:` stays where it was. Room changes crossfade over one beat.
- **Ducking:** the bed's level comes from the voice, not the cue file: about 18 dB under the voice while he talks and
  10 dB under in pauses of 600 ms or more (shorter pauses stay down, so it never pumps). It dips over 80 ms, starting
  80 ms before each phrase, and comes back up over 450 ms. The number after the track name only sets the bed when there
  is no real voice yet (estimate timings). The bed fades out over the last 1.8 s.
- **Bed EQ**, so it stays out of the voice's way: high-pass at 90 Hz, -2 dB at 300 Hz, -3 dB at 2.8 kHz (Q 0.8), low-pass
  at 7 kHz.
- **Effects:** `[sfx: name]` on a cue fires on its first word: `blip` (a soft UI blip), `tick` (a counter tick), `whoosh`
  (a section change), `pop` (something appears), `stamp` (a verdict lands: a click, a falling thump and a short tail),
  `chime` (the close), `squeak` (Squeak, sparingly). Each has four takes (slightly different pitch and level, own
  noise); the render picks them in turn, so the same cue file always sounds the same. Ticks in a row inside one section
  climb a semitone each (up to 12), so a count rises. `[sfx: stamp_2]` asks for one take by name.
- **Sting:** `[sfx: sting]` plays the brand sting (E5, G5, C6; the last note held with vibrato and an echo) on that cue,
  only if the cue is in the last section (the brand moment). Anywhere else it is left out. The bed dips 12 dB for it.
- At most one effect every 1.5 s; never on top of a number being said.
- **The mix:** voice untouched, effects about 13 dB down (the sting 12), then -14 LUFS integrated and a limiter so the
  MP4's true peak stays at or under -1.5 dBTP (`anim.py check` measures both).
