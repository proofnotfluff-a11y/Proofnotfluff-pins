# Sound

All of it is made by `anim.py` (`sound` builds the files, `render` and `remix` mix them). No samples, no licenses.

- **Music, two ways** (on the first lines of `cues.md`):
  - `music: steady-hands 0.12`: one bed from `tools/music/library.json` (our own compositions). The tracks run 36 to
    60 s, so for a longer lesson the A and B sections loop on the bar line.
  - `music: rooms <tune>`: four chiptune loops made in code, one per room, in one of six tunes of our own (Todd, Oct 29,
    2026, 8:11 pm: "different tunes for each video"). Plain `music: rooms` is classic. Each tune has its own key, tempo,
    8-bar chords and lead; the rooms change what plays under its quiet square lead: framing is half-time and sparse,
    blackboard has arpeggios, workshop has chord stabs and hats, garage has a pulse bass riff, kick and snare. A top-level
    cue whose description starts `Room: blackboard.` moves the music to that room; a section with no `Room:` stays where
    it was. Room changes crossfade over one beat of the tune. `anim.py tunes SLUG` lists them and the ones free for a lesson.

    | Tune | Key | BPM | Chords (one a bar) | Feel |
    |---|---|---|---|---|
    | classic | A minor | 96 | Am F C G Am F Dm E | the first tune (`_runtime/music/<room>.wav`) |
    | sunny | C major | 120 | C Am F G C Am Dm G | bright, a broken arpeggio |
    | quest | D minor | 108 | Dm Bb F C Dm Bb Gm C | adventure, an up and down arpeggio |
    | night | E minor (Phrygian) | 88 | Em F Em Dm Am G F Em | slow and dark, a hollow lead |
    | chase | F major | 132 | F C Dm Bb F C Bb C | fast, four on the floor, a thin lead |
    | bounce | G Mixolydian | 112 | G F C G Am C F G | swung, triplet arpeggios |

    The others live in `_runtime/music/<tune>/<room>.wav`; all are mono 22.05 kHz, the same loudness (RMS 0.12) and
    loop seamlessly. **Variety:** a lesson's tune is never the tune of the lesson right before or after it in the
    posting line (`anim.py variety`, `_shared/voice.md`). A library bed counts as its own tune.
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
  It is the one sound every lesson shares (the brand constant), and it lands on whatever bar is playing, so every tune
  but classic keeps C, E and G natural in all its chords and lead notes. classic's bar 8 (E major, G#) rubs a little.
- At most one effect every 1.5 s; never on top of a number being said.
- **The mix:** voice untouched, effects about 13 dB down (the sting 12), then -14 LUFS integrated and a limiter so the
  MP4's true peak stays at or under -1.5 dBTP (`anim.py check` measures both).
