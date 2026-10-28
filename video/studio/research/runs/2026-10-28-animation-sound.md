# Animation and sound research for the pixel explainer renderer

Date: Oct 28, 2026. Scope: vertical 1080x1920, 30 fps, 45 to 90 s, canvas drawn at 1/3 size (360x640) and snapped to a
34-color palette, bearded host, dialog box, pixel rooms, Python-synthesized sound.

Labels used below:
- **[Evidence]** a study, standard, official platform statement, or a documented number from a named source.
- **[Practice]** what working game and video people do, documented in a talk, tutorial or code sample, not a controlled study.
- **[Opinion]** my recommendation for this renderer. Parameters marked this way are starting points to tune by eye and ear.

Units: 1 frame = 33.3 ms at 30 fps. "lpx" = one low-res pixel = 3 output pixels.

## 0. What the current code does (read Oct 28, 2026)

Read from `video/studio/_runtime/player.js`, `kit.js`, `anim.py` and `_shared/sound.md`. These are the gaps the upgrades target.

- **Music does not duck.** `_shared/sound.md` says the bed "ducks under the voice", but `anim.py mix()` applies one fixed
  `volume=` to the bed, then a gentle whole-mix compressor. There is no sidechain or envelope tied to the words.
- **SFX are identical every time.** Each effect is synthesized once with a fixed random seed (`default_rng(3)`, `(7)`), at a
  fixed -13 dB. Five stamps in a video are five copies of one waveform.
- **Mouth is not driven by the voice.** `kit.js` opens the mouth with `abs(sin(T*17)*sin(T*7.3))` whenever any word is active.
- **Blink is a metronome.** `(T % 3.7) < 0.12`: exactly every 3.7 s, always the same length.
- **Shake is a fixed sine.** `sin(T*91)`, `cos(T*73)` at 7 px, linear decay over 0.32 s on every `stamp` cue, not snapped to
  the pixel grid.
- **Blinds only open.** The room cut happens with the blinds already fully shut at frame 0 of the new section; they never
  visibly close over the old room.
- Already good: zoom ladder with springy overshoot, hook card, the no-more-than-3-flashes rule, loudness to -14 LUFS with a
  limiter, one effect per 1.5 s.

---

## 1. Pixel-art animation craft

### 1.1 The principles, applied at 30 fps on a 360x640 grid

| Principle | What it means here | Parameters [Opinion unless marked] |
|---|---|---|
| Anticipation | A small move the opposite way before the main move | 3 to 4 frames (100 to 133 ms). A slammed card shrinks to 0.92 or rises 2 lpx before it drops. Host leans back 1 lpx before a point. |
| Squash and stretch | Volume-preserving scale on impact and launch | Landing: 1.20 x 0.85 for 2 frames, then 0.95 x 1.05 for 1 frame, then settle. Keep w*h near 1. "Squeeze and stretch" is item 3 in Jonasson and Purho's juice list [Practice]. |
| Follow-through and overlap | Loose parts finish after the body stops | Beard tip, cap, clipboard lag the head by 2 frames and overshoot 1 lpx. |
| Arcs | Natural motion travels on curves | Slide-ins travel on a shallow arc (8 to 16 lpx of bow over the path), not a straight line. |
| Slow in, slow out | Easing | Entrances decelerate, exits accelerate (Material motion guidance [Practice]). Use easeOutCubic in, easeInCubic out, easeOutBack (overshoot 1.2 to 1.7) for pops. |
| Timing | Frames per pose | Pixel sprites read best with holds. Host body poses on twos (15 fps) or threes (10 fps); camera, UI and text at 30 fps. [Opinion; common pixel/anime practice] |
| Exaggeration, secondary action, staging, appeal | Push poses; one focal action at a time | One moving focal element per beat; everything else idles quietly. Supports Mayer's coherence principle (section 6). |

Frame-count references [Practice]:
- Slynyrd (Raymond Schlitter): an 8-frame run at 80 ms per pose; halving to 4 frames doubles the hold to 160 ms to keep the
  same energy; "6-frame cycles work well in most cases"; 8-bit JRPGs reused a 2-frame walk as the idle.
- sprite-ai.art guide: idle/breathing 2 to 4 frames at 400 to 800 ms per frame, ping-pong; walk 4 to 6 frames at 80 to
  120 ms; attack 3 to 6 frames with slow wind-up, fast strike, slow recovery; hit reaction 2 to 3 frames, "fast flash,
  medium recoil".

### 1.2 Sub-pixel animation
At low resolution, moving a part by a whole pixel is a big, jumpy change. Sub-pixel animation changes the colors of edge
pixels instead of moving them, implying motion smaller than one pixel. Used for breathing and for parts that should look
steady (the Metal Slug Fio idle example) [Practice: Someanimatorwannabe on Ansimuz's breakdown; Saint11 has a dedicated
"Subpixel" tutorial].
- [Opinion] For the host: breathing = the shoulder/jacket top edge row alternates between the outline color and a mid tone
  (2-frame cycle), plus the chest highlight shifts by one palette step. No geometry moves. Use whole-pixel moves only for
  real actions (gestures, head bobs).

### 1.3 Smear frames
Frames inserted between key poses to fake motion blur. Types: distortion (stretch), multiples (duplicates along the path),
trailing parts, energy lines, abstract streaks. Distortion smears usually last 1 to 2 frames [Evidence: Wikipedia "Smear
frame", citing Richard Williams]. Saint11 has a "Motion Blur" pixel tutorial [Practice].
- [Opinion] When a slammed element moves more than about 10 lpx in one frame, draw it as one streak frame: the shape
  stretched along the motion vector to 1.6x its length, with 2 to 3 trailing duplicate edges at 50% and 25% using darker
  palette steps (no alpha in pixel mode; use dithered or stepped colors). Never smear text that must be read on that frame.

### 1.4 Hit-stop (sleep, hitlag) and impact frames
- Nijman's "The art of screenshake" includes "Sleep (brief pause on hitting an enemy)" at 18:06 of the talk [Practice].
  A summary of experiments based on it describes the freeze as "a frame or a couple of frames" [Practice].
- Sakurai (Smash Bros. director) on hitstop: both parties freeze briefly to emphasize impact; more damage means longer
  hitstop; there is a cap; the hit character vibrates during the freeze, and the vibration shrinks over the freeze
  [Practice, Famitsu column via Source Gaming].
- Smash Ultimate formula (SSBWiki): hitlag frames = floor((damage x 0.65 + 6) x multipliers), at 60 fps; minimum about
  6 frames (0.1 s) for any damaging hit, 15 frames (0.25 s) at 15% damage, capped at 30 frames (0.5 s) [Evidence, game data].
- [Opinion] For a teaching video: freeze the stamped element and its particles for 3 frames (100 ms, the Smash minimum
  in real time), vibrate it 1 lpx left/right on alternate frames during the freeze, then release into squash. The voice
  cannot pause, so the host and dialog keep running. Big verdicts (the one "busted myth" per video) get 5 frames (167 ms).
- Impact frame: 1 frame where the stamped object is drawn as a solid light silhouette (palette's lightest color), or the
  inverted palette on that object only. Keep it to the object so the flash area stays under 25% of the screen (see
  section 3.5).

### 1.5 Screen shake
- Nijman: screen shake, camera kick (camera moves opposite the shot direction), camera lerp, camera position, permanence
  are separate tools [Practice]. One experiment on a scaled-down pixel game: "a pixel or two" of shake already reads as
  a big effect at low resolution [Practice, Blue Tengu].
- Eiserloh (GDC 2016, "Juicing Your Cameras With Math"), as implemented in the Bevy engine example that cites it:
  trauma value 0 to 1 added by events; shake = trauma^2 (squared, so small hits barely shake and big ones shake a lot);
  smooth noise, not white random, sampled over time; separate translation and rotation channels. Bevy constants: max
  translation 20 px, max angle 10 degrees, noise speed 20, trauma decay 0.5 per second (full trauma fades in 2 s)
  [Practice]. A Godot recipe uses trauma power 2 ("use [2, 3]"), decay 0.8/s, max roll 0.1 rad, simplex noise period 4,
  2 octaves [Practice].
- Those are game values for a player in control. A teaching video should shake far less. [Opinion] trauma += 0.5 per
  stamp (0.8 for the one big verdict), shake = trauma^2, decay 3.0 per second, max offset 3 lpx (9 output px), no
  rotation in pixel mode (rotation on a pixel grid creates jaggies), value noise at 12 to 16 Hz per axis with different
  seeds, round the offset to whole lpx. Cap: one shake per 10 s (existing rule).

### 1.6 Camera moves
- Frame-rate independent smoothing: weight = 1 - exp(-rate x dt). A fixed 10% per frame lerp reaches 95.76 / 99.82 /
  100.00 after 1 s at 30 / 60 / 144 fps, while the exp form gives 99.33 at all three (rate 5) [Practice, from a code
  review citing Eiserloh's talk].
- Look-ahead: Nijman's "camera position" moves the camera toward where the action is going [Practice]. We know every cue in
  advance, so the camera can anticipate. [Opinion] Start the pan to a beat's focus point 6 frames (200 ms) before its cue,
  rate 8/s, travel at most 20% of the way to the focus (already in code), and snap the final offset to whole lpx so the
  pixel grid never swims.
- Camera kick [Opinion]: on a slam, push the camera 2 lpx in the slam direction for 1 frame, then let the damp return it.

### 1.7 Parallax
3 or 4 layers (sky, far, mid, near) give a strong sense of depth; far layers move less, near layers more [Practice,
Bugnet]. [Opinion] Factors 0.25 (far wall/window view), 0.6 (mid props), 1.0 (play plane), 1.3 (foreground lip: bench
edge, door frame). Drive them from the camera offset and zoom, each layer snapped to whole lpx.

### 1.8 Palette-shift effects (color cycling)
Color cycling rotates colors through a palette ramp; pixels never move but bands of color appear to flow. Mark Ferrari
likens it to a theater marquee. Classic uses: water, lava, blinking lights, flowing water and moving cars in SimCity 2000
[Evidence: Wikipedia "Color cycling"]. [Opinion] Ideal for room ambience at almost no cost in a palette-snapped
renderer: chalk dust shimmer (3-step ramp, 6 fps), the garage fluorescent hum (2-step flicker with random 1 to 3 s gaps,
never more than 3 changes per second), workshop welding glow (4-step warm ramp, 8 fps), dusk light through the half-built
house frame (slow 5-step ramp over 20 s).

### 1.9 Dithering for gradients
Ordered (Bayer) dithering uses a fixed threshold matrix, so the pattern is stable from frame to frame. Error diffusion
(Floyd-Steinberg) depends on neighbors, so moving content makes it crawl [technical fact; see Wikipedia "Ordered
dithering"]. [Opinion] Use a 4x4 Bayer matrix in the quantizer only for regions flagged as gradients (light cones, sky,
vignette, blackboard glow), never on text, faces, or UI. Anchor the matrix to world coordinates of the layer so it moves
with the layer instead of shimmering under it.

### 1.10 Lighting
- Hue shifting: shadows lean cool and darker, highlights lean warm and lighter, rather than only darker/lighter versions
  of one color [Practice: common pixel shading tutorials, e.g. Pixel Grimoire].
- [Opinion] One key light per room, top-left in all rooms so the host reads the same everywhere. Rim light: a 1 lpx line of
  the next-lighter palette color on the host's edge facing the room's practical light (blackboard lamp, garage tube).
  Contact shadow: a 2 lpx tall ellipse, two palette steps darker than the floor, under the feet and under every card that
  lands (it also sells the slam: the shadow grows as the card falls).

### 1.11 Idle animation
- Blinks: medical news summary of a PLOS One study reports measured conversational blinks of about 208 ms (short) and
  607 ms (long); people blink most during conversation; over 13,000 blinks a day (about 9 per minute averaged over waking
  and sleeping time, my arithmetic) [Evidence].
- [Opinion] Blink: random interval 2.5 to 6 s (uniform), 4 frames total (half lid, closed, closed, half lid = 133 ms; the
  stylized short end of 208 ms reads crisper on pixels), 15% chance of a double blink, and bias blinks to phrase ends
  (the gap between words) so they never land on a key word.
- Breathing: 2-frame sub-pixel cycle at 0.6 to 0.8 s per frame (matches the 400 to 800 ms idle timing above).
- Fidgets: after 8 to 12 s with no gesture, one fidget (beard scratch, look at board, adjust cap): 6 to 10 frames of
  motion on twos, then back to idle. Never during a number.

---

## 2. Talking-character animation

### 2.1 Cheap lip sync from loudness
- Mouth shape vocabulary (Preston Blair derived, as used by Rhubarb Lip Sync): A closed with pressure (P B M), B slightly
  open teeth together (most consonants, EE), C open (EH, AE), D wide open (AA), E slightly rounded (AO, ER), F puckered
  (UW, OW, W), plus optional G (F, V), H (L) and X (idle, relaxed closed). Rhubarb places shapes ahead of the sound and
  inserts transitional shapes (C between D and B) [Practice].
- Loudness-only sync is a known compromise (it gets open/closed right but not lip shape); a documented RMS implementation
  found: use a square-root curve to lift weak openings, judge by percentiles of real TTS audio not averages, watch the
  "saturation rate" (frames stuck at fully open; 48% to 58% looked exaggerated, 6% with the sqrt curve looked right), and
  close the mouth explicitly at the end [Practice, dev.to orca_forge, two posts].
- Animators place mouth shapes at least 2 frames before the sound (at 24 fps, about 83 ms), and 6 to 8 frames early for
  heavily emphasized sounds [Practice].
- Perception bounds: ITU-R BT.1359 detectability is 45 ms of audio lead to 125 ms of audio lag; EBU R37 asks for +40 ms /
  -60 ms end to end [Evidence]. A mouth that moves 1 to 2 frames (33 to 67 ms) before its sound equals audio lagging
  video by that amount, inside the 125 ms detectability window. A mouth that moves late is caught much sooner (45 ms).

[Opinion] Recipe for our renderer (no ML, deterministic, Python precompute to a per-frame array):
1. Voice at 48 kHz, high-pass 100 Hz, band-limit 300 to 3,400 Hz (rejects breaths and plosive thumps).
2. RMS in 40 ms windows, hop = 1 video frame (33.3 ms), in dB.
3. Gate: below (voiced 10th percentile - 6 dB) or outside a Whisper word span = X (relaxed closed).
4. Normalize voiced frames by percentiles: p20 -> 0, p95 -> 1, apply sqrt.
5. Smooth: attack fast (one-pole time constant 15 ms, effectively immediate at 30 fps), release slower (60 to 80 ms).
6. Quantize with hysteresis into 4 shapes: closed-A below 0.15, B 0.15 to 0.40, C 0.40 to 0.72, D above 0.72; a new shape
   must hold at least 2 frames unless it is A (closing for P/B/M can be 1 frame).
7. Shift the array 2 frames earlier (67 ms lead).
8. Optional cheap upgrade: when the Whisper word text contains a stressed "oo/oh/w" vowel, swap C/D for F (puckered) on
   that word; when it starts with f/v, use G for its first 2 frames.
9. Target saturation: under 10% of voiced frames in D.
Bearded host bonus: only the mouth opening and lower beard edge move. Drop the jaw (lower beard) 1 lpx in C and 2 lpx in D.

### 2.2 Head bobs, brows, gestures
- Gesture timing [Evidence]: ter Bekke, Drijvers and Holler (2024, Cognitive Science), conversational data: gestures began
  on average 644 ms before their lexical affiliate (SD 648; before it in 94% of cases); gesture strokes began on average
  193 ms before (SD 616; before it in 60% of cases).
- Eyebrows [Evidence]: Flecha-García (2006, Edinburgh thesis) on task dialogues: brow raises were more frequent and longer
  in instructions than in questions or acknowledgements; queries did NOT show more raising, contrary to the prediction;
  brow raise onsets tended to come immediately before a pitch accent; raising was more frequent and longer at the start
  of major discourse segments. So "raise brows on questions" is not supported; "raise brows at section starts and on
  instructions, just before the stressed word" is.
- [Opinion] Rules:
  - Gesture (point, open palm, count on fingers) on the cue's key word: start the preparation 600 ms (18 frames) before
    the word, hit the stroke pose 200 ms (6 frames) before the word onset, hold through the word, retract over 8 frames.
  - Brow raise: 2 lpx up, onset 4 frames before the first accented word of each section and of each instruction line
    ("Call them back within five minutes"), hold 10 to 20 frames.
  - Head bob: on accented syllables (local RMS peaks at least 4 dB above the phrase median, at least 250 ms apart),
    head 1 lpx down for 2 frames starting 1 frame before the peak, then 1 frame of 1 lpx overshoot up. No more than 2
    per second.
- Keeping a host alive (Kurzgesagt): every element is animated by hand, characters are rigged for natural movement,
  narration is recorded and re-taken first, and pacing is set by the script before visuals [Practice, production
  write-ups]. That matches the team's voice-first five stages (voice, words, storyboard, scene code, render). No public
  source I could reach documents Jake Van Clief's per-frame host rules, so nothing here is attributed to him.

---

## 3. Kinetic typography for shorts

### 3.1 Reading speed
- Netflix (official): min 5/6 s per subtitle event, max 7 s, max 2 lines [Evidence]. Widely cited Netflix adult limit
  17 characters per second, children 13 [Practice, as reported by subtitle guides]. BBC about 160 to 180 wpm [Practice,
  as reported].
- Brysbaert (2019) meta-analysis of 190 studies: average silent reading 238 wpm (236 for English-only studies), about
  4 words per second [Evidence].
- TikTok (official ads help): "We recommend displaying 5-10 words per second when using text" [Evidence of platform
  advice; note this is a pacing suggestion for ads, faster than comfortable reading, and only works when the words are
  also spoken].
- [Opinion] For text that is spoken at the same time (the dialog box): follow the voice; that is fine at the TikTok rate
  because the ear carries it. For text that is NOT spoken (labels, source lines, chips): hold = max(25 frames,
  characters / 15 s), never over 7 s. A source line of 40 characters needs at least 2.7 s.

### 3.2 Emphasis
- Mayer's signaling principle: cues that highlight organization help (28 tests, 24 positive, median d = 0.41), more so
  when signals are used sparingly [Evidence].
- [Opinion] One emphasis per phrase, by one channel: color (accent) for terms, scale pop (1.0 to 1.25 to 1.0 over 6
  frames, easeOutBack) for numbers, shake only for verdict stamps. Never animate scale on the word being read in the
  dialog box (it reflows the line); light it with the accent color instead.

### 3.3 Word-level captions: what the evidence allows
- Redundancy principle: graphics + narration beat graphics + narration + on-screen text (16 of 16 tests, median d = 0.86).
  Boundary conditions: the effect weakens or reverses when the on-screen text is short, for experienced learners, or with
  no graphics; adding a few key words next to the relevant graphic improved retention [Evidence, Mayer and Fiorella].
- Captions: Gernsbacher (2015) cites over 100 studies that captions improve comprehension, attention and memory; a
  careful critic notes many are about second-language or non-typical viewers and self-report, and one study found
  not-at-risk children recognized fewer words with captions [Evidence, contested].
- Sound-off reality: a Verizon Media and Publicis survey (April 2019, 5,616 US adults) is the usual source; Facebook
  reported captions raised view time on video ads by 12% [Evidence of platform statement, as reported by 3Play Media].
- Accessibility critique of karaoke captions: word-at-a-time display removes read-ahead, ignores phrase boundaries, and
  constant bouncing adds load; show full phrases of 1 to 2 lines with subtle, steady highlighting [Practice/advocacy].
- [Opinion] Keep the dialog box (sound-off viewers, platform norm) but show the whole phrase at once (already the case),
  light the spoken word with a steady color change rather than a bounce, and keep it compact. Put the few big key words
  (the number, the verdict) next to the graphic they describe, which is where the redundancy evidence is favorable and
  spatial contiguity applies (22 of 22 tests, median d = 1.10).

### 3.4 Safe area
No platform publishes one universal pixel safe zone for organic posts; TikTok's ads help says to keep content "within the
UI safe zone as per ad specifications" [Evidence]. Third-party conservative estimates at 1080x1920 [Practice]: TikTok top
108, bottom 320, left 60, right 120; Reels top 210, bottom 310, right 84; Shorts top 120, bottom 300, right 96.
[Opinion] Union for one master file: top 210, bottom 320, left 60, right 120 output px (70 / 107 / 20 / 40 lpx). The
dialog box (y 1060 to 1240) is inside this.

### 3.5 Contrast and flashes
- WCAG 1.4.3: 4.5:1 for normal text, 3:1 for large text (at least 18 pt, or 14 pt bold, about 24 px / 18.5 px) [Evidence].
  At 1080 px wide shown on a phone, our body text is large in pixels but small physically; aim for 4.5:1 everywhere.
- WCAG 2.3.1: nothing flashes more than 3 times in any 1 s, unless below the general and red flash thresholds. A general
  flash is a pair of opposing luminance changes of 10% or more of max relative luminance where the darker state is below
  0.80; safe if the combined flashing area stays within 25% of any 10-degree field (341 x 256 px at 1024 x 768 as a rough
  check) [Evidence]. [Opinion] Make this a gate: compute per-frame relative luminance on a 6x10 grid of cells, count
  opposing transitions over 10% per sliding 30-frame window, fail on more than 3 in any cell group covering over 25% of the
  frame. Ban saturated red full-screen flashes outright.

---

## 4. Transitions

- Durations: Material motion guidance for mobile: typical transitions about 300 ms, large full-screen ones about 375 ms,
  entering elements 225 ms, exiting 195 ms; entering decelerates, exiting accelerates [Practice]. At 30 fps: 9 to 11
  frames for a full-screen transition.
- Polished vs cheap [Opinion]:
  - Polished: the transition belongs to the world (a garage door, a chalk eraser, blinds), is motivated by the narration
    (section change), hides the cut at its midpoint, has its own sound, and is the same family every time.
  - Cheap: generic crossfades and preset 3D flips, transitions inside a thought, random variety, slow transitions
    (over 0.6 s) that delay the next word's picture (breaks temporal contiguity, median d = 1.22 [Evidence]).
- Room-matched set [Opinion], each 12 frames total: 5 frames closing (easeIn), cut, 1 frame held closed, 6 frames opening
  (easeOut):
  - Blackboard: chalk wipe, an eraser band sweeps diagonally leaving a dithered chalk-dust edge (Bayer at 50%).
  - Garage: roll-up door, horizontal slats drop from the top, each slat 1 frame behind the one above.
  - Workshop: the existing pixel blinds, but make them close over the old room first.
  - Half-built house: iris close on the host's head, then iris open (classic pixel-game iris, circle snapped to lpx).
- How often [Opinion]: only at room (section) changes, so about every 10 to 20 s in a 45 to 90 s video (3 to 6 per video).
  Inside a room use cuts, the zoom ladder, and camera moves.
- Sound: a whoosh whose peak lands on the cut frame (start it 5 frames early), pitched to the room (lower for the garage).

---

## 5. Sound design

### 5.1 Layering
A documented four-layer framework: sub (weight you feel), body (midrange that says what it is), detail (high-frequency
specifics), tail (the room, the distance). Align all transients to one frame; roll the lows off every layer except the sub;
keep detail bright, short and lower in level; let the tail run past [Practice, Morphic]. In the short "transient + body +
tail" form:

| SFX | Transient | Body | Tail [Opinion: all parameters] |
|---|---|---|---|
| stamp | 2 ms noise click, high-passed 2 kHz, -6 dB | sine 110 Hz dropping to 55 Hz over 120 ms, exp decay 90 ms | low-passed noise (1.5 kHz) 300 ms, -15 dB, plus a 40 ms "paper slap" band-pass 800 Hz |
| pop | 1 ms click | sine sweep 900 -> 420 Hz in 40 ms | 80 ms, -18 dB, tiny 30 ms slapback at -20 dB |
| slam (number lands) | 3 ms noise burst | square 80 Hz 60 ms, 12.5% duty, then triangle 55 Hz | noise 200 ms LP 2 kHz -18 dB |
| whoosh | none | band-passed noise sweeping 400 Hz -> 3 kHz -> 800 Hz, 420 ms | 150 ms tail -20 dB |
| tick (counter) | 0.5 ms click | 2.2 kHz sine 12 ms | none |

### 5.2 Variation
- Random small pitch shifts reduce repetition even when "the actual change to the pitch may not be noticeable"; rising
  combos use a multiplier of 1.06^N for N semitones [Practice, Game Developer "The power of pitch shifting"]. Round-robin
  sampling avoids the "machine gun effect" [Practice, MusicRadar].
- [Opinion] Every SFX instance gets its own seed (cue index) and: pitch +/- 40 cents (factor 2^(c/1200)), level +/- 1.5 dB,
  start offset 0 to 8 ms for non-sync sounds. Counters: each tick +1 semitone, capped at +12, reset per count; the landing
  tick is a different sound (the slam). Keep stamps within +/- 25 cents so the "verdict" sound stays recognizable.

### 5.3 Ducking the bed under the voice
- Levels and envelope [Practice, MusicVivo]: music 15 to 25 dB under the voice while speaking (explainers at the quiet end,
  about -20 to -25 dB; promos -12 to -15 dB); ducking depth 6 to 10 dB; ratio 3:1 to 6:1; attack 10 to 30 ms with 5 to
  10 ms lookahead; release 300 to 600 ms, longer if it pumps between words; music can sit at 0 to -6 dB with no speech.
- FFmpeg `sidechaincompress` example [Practice, ffmpeg-micro]: threshold 0.03 (about -30 dBFS; the 0.125 default never
  triggers on normal speech), ratio 8, attack 20 ms, release 500 ms (250 ms default pumps; use 400 to 800).
- [Opinion] We have word timings, so precompute a deterministic gain envelope instead of a compressor: bed at -18 dB
  relative to voice during speech and -10 dB in gaps over 600 ms (an 8 dB swing); ramp down over 80 ms starting 80 ms
  before each phrase onset; ramp up over 450 ms only when the gap exceeds 600 ms (shorter gaps stay ducked so it never
  pumps). Apply with ffmpeg `volume` expressions or numpy before the mix.

### 5.4 Keeping music out of the voice's way
- The band that most affects speech intelligibility is 2.5 to 5 kHz; cut the music 2 to 4 dB there and/or boost the voice
  2 to 4 dB there; lower-midrange instruments mask male voices [Practice, ProSoundWeb]. MusicVivo: broad 2 to 4 dB cut at
  2 to 3 kHz wide Q (example 3 dB at 2.5 kHz), 1 to 3 dB cut at 250 to 400 Hz if muddy, high-pass the music at 60 to 80 Hz
  for deep voices, never cut over about 6 dB [Practice].
- Square waves are rich in odd harmonics that land right in 1 to 5 kHz. [Opinion] So: on the bed bus, high-pass 90 Hz,
  -3 dB bell at 2.8 kHz (Q 0.8), -2 dB at 300 Hz (male host), low-pass 7 kHz; keep pulse-wave chords in the octave below
  middle C; the lead melody plays only in voice gaps (call and response), muted while words are active.

### 5.5 Loudness targets
- YouTube: normalizes playback to about -14 LUFS, turning loud uploads down only; widely reported with -1 dBTP ceiling
  [Practice: third-party documentation cross-checked against "Stats for nerds"; YouTube publishes no number].
- TikTok, Instagram, Facebook: no official published LUFS target; observed behavior clusters around -14 LUFS [Practice].
- AES TD1008 suggests about -18 LUFS for speech-led streaming content and -16 for music, noting speech sounds louder than
  music at the same meter reading [Evidence, standard as summarized by Forasoft].
- [Opinion] Keep the current target: -14 LUFS integrated, true peak at or below -1.5 dBTP (stricter than -1 to survive
  AAC re-encoding), loudness range under 8 LU for a phone speaker. The current limiter at -3.5 dBFS sample peak at 4x
  oversampling is conservative but fine.

### 5.6 Chiptune bed in code
- NES 2A03 voices [Evidence, NESdev wiki]: two pulse channels (duty 12.5%, 25%, 50%, 75%; 4-bit volume), one triangle (no
  volume control, only on/off; plays an octave lower than a pulse at the same period; used for bass), one noise channel
  (percussion; a "tone mode" gives pitched metallic noise).
- Composer techniques [Practice, ddrkirby NES chiptune article]: 25% duty for a bright lead that is not too nasal; vibrato
  on long notes; grace notes and slides; echo by having the second pulse repeat the melody later, quieter and slightly
  detuned; a pitched triangle "drum" sliding down for kicks; noise kick/hat/snare; tempos raised level to level (100,
  150, 180 BPM) for rising intensity.
- [Opinion] Spec for four room loops:
  - One key for the whole video (A minor / C major works with everything), 4/4, 92 to 100 BPM (8 bars at 96 BPM =
    20.0 s, a clean loop). Same tempo across rooms so room changes can crossfade on the bar line (fade 1 beat).
  - Per room, change instrumentation not key: blackboard = 12.5% pulse arpeggios (1/16 notes, triads) + triangle root
    notes; workshop = 25% pulse offbeat stabs + noise hats; garage = 50% pulse bass riff an octave down + triangle kick
    slide; half-built house = slower half-time feel, sparse plucks.
  - Arpeggio speed: 1/16 notes at 96 BPM = 156 ms per note (or 1/32 for the classic "chord" shimmer, 78 ms).
  - Vibrato on held lead notes: 5.5 Hz, +/- 20 cents, starting 150 ms into the note.
  - Echo channel: second pulse 1/8 note (312 ms) later, -9 dB, +7 cents.
  - Envelopes: pulse attack 5 ms, decay to 60% over 120 ms; noise hat 30 ms; noise snare 120 ms.
  - Synthesize band-limited: PolyBLEP squares or additive harmonics up to 16 kHz. Naive `sign(sin)` squares alias into
    audible whistles at 48 kHz, which is the main thing that makes code-made chiptune sound cheap [technical fact].
  - Bed level: -18 dB under the voice during speech (see 5.3).
- Brand sting [Opinion; the sonic-logo industry talks in about 3 s snippets, Adelphoi podcast]: 3 notes, 1.2 to 2.0 s
  total, rising to the tonic (for example E5, G5, C6 on a 25% pulse with triangle doubling an octave down, last note held
  600 ms with vibrato and a 400 ms echo). Always identical (it is a logo: no random variation), on the brand plate only.
- [Opinion] Skip the backlog's "typewriter tick per word" under the voice: it is a sound that competes with consonants in
  the 2 to 5 kHz band on every word. If kept, only on the hook card before the voice starts, at -28 dB.

---

## 6. Retention-driven motion: what the evidence does and does not say

- Platform statements [Evidence, TikTok ads help]: hook in the first 6 s; introduce the proposition in the first 3 s for
  recall; use sound; use transitions, stickers and graphics to keep people watching; text 5 to 10 words per second.
  No retention numbers are published with these. YouTube's analytics help page I reached does not define Shorts metrics.
- Pace and attention: Cutting and colleagues (2010) measured shot lengths in 150 films from 1935 to 2005; post-1980 films
  more closely follow a 1/f pattern that they suggest matches natural attention fluctuations; the link to attention is
  their hypothesis, not a measured effect [Evidence for the trend, hypothesis for the cause].
- Lang's Limited Capacity Model: edits and other structural features trigger orienting responses, and too much
  structural complexity can exceed processing capacity (Lang et al., 2000, "When an edit is an edit can an edit be too
  much?"). I could not access the abstract to quote its numeric results, so I do not report them.
- Multimedia learning (Mayer and Fiorella, Cambridge Handbook) [Evidence]:
  - Coherence: excluding extraneous material helps (23 of 23 tests, median d = 0.86), most for system-paced lessons
    (video is system-paced) and highly distracting extras.
  - Signaling: 24 of 28 tests, median d = 0.41, best when sparing.
  - Redundancy: 16 of 16, median d = 0.86, with the short-text exception (section 3.3).
  - Spatial contiguity: 22 of 22, median d = 1.10.
  - Temporal contiguity: 9 of 9, median d = 1.22 (picture and words at the same time, not one after the other).
  - Seductive details (interesting but irrelevant content, including animations and sounds) often reduce retention and
    transfer, though some studies find no harm when cognitive load is low [Evidence, mixed].
- No study I found gives an optimal "visual change every N seconds" for short vertical video. The current rule (a new beat
  every 2 to 4 s) is [Practice/Opinion]; keep it, but make every beat carry the content being said (temporal contiguity),
  and spend the motion budget on the thing that matters (signaling), not on decoration (coherence, seductive details).
- Where motion hurts [Opinion grounded in the above]: ambient motion near text being read; shake on frames with numbers
  (the existing rule is right); transitions longer than about 0.5 s that delay the picture of what is being said; more
  than one moving focal point at a time; decorative particles during a number.

---

## 7. Prioritized upgrades (15)

Ordered by (expected gain in polish and clarity) / effort, with gaps found in the current code first.

| # | Upgrade | Exact parameters | Why (source) | Effort |
|---|---|---|---|---|
| 1 | **Real voice ducking + bed EQ** (sound.md promises ducking; `mix()` has none) | Envelope from words.json: bed -18 dB re voice in speech, -10 dB in gaps over 600 ms; duck ramp 80 ms starting 80 ms before phrase; release 450 ms only after gaps over 600 ms. Bed bus: HPF 90 Hz, -3 dB @ 2.8 kHz Q 0.8, -2 dB @ 300 Hz, LPF 7 kHz. Fallback: `sidechaincompress=threshold=0.03:ratio=6:attack=20:release=500`. | Duck 6 to 10 dB, attack 10 to 30 ms, release 300 to 600 ms (MusicVivo); threshold and pumping (ffmpeg-micro); 2.5 to 5 kHz drives intelligibility (ProSoundWeb) | Small |
| 2 | **Voice-driven lip sync** | 40 ms RMS per frame on 300 to 3,400 Hz band; gate p10 - 6 dB; normalize p20..p95 + sqrt; attack 15 ms, release 70 ms; shapes A <0.15, B <0.40, C <0.72, D above; hold 2 frames min; shift 2 frames early; D under 10% of voiced frames; jaw/beard drop 1 lpx (C), 2 lpx (D). | Blair/Rhubarb shapes, shapes lead sound (Rhubarb; animators lead 2 frames); ITU-R BT.1359 tolerates 125 ms audio lag but only 45 ms lead; RMS percentile and saturation tuning (orca_forge) | Medium |
| 3 | **SFX layering and per-instance variation** | Seed per cue; pitch +/- 40 cents (stamps +/- 25), level +/- 1.5 dB; stamp = 2 ms HP click + 110 to 55 Hz body 120 ms + LP noise tail 300 ms at -15 dB; counter ticks +1 semitone each (cap +12) then a slam on landing. | Pitch variation cuts repetition; 1.06^N per semitone (Game Developer); round robin (MusicRadar); sub/body/detail/tail layering (Morphic) | Small |
| 4 | **Hit-stop + impact frame on stamps** | Freeze the stamped element and particles 3 frames (5 for the one big verdict); 1 lpx alternate-frame vibration during freeze; 1 frame light silhouette of the object only (under 25% of screen); then squash 1.20 x 0.85 for 2 frames, 0.95 x 1.05 for 1, settle over 6 with easeOutBack. Host and dialog keep running. | Nijman "sleep"; Sakurai on hitstop and vibration; Smash minimum hitlag 6 frames at 60 fps = 100 ms (SSBWiki); WCAG 2.3.1 area rule | Small |
| 5 | **Trauma shake, pixel-snapped** (replace `sin(T*91)`) | trauma += 0.5 per stamp (0.8 big verdict), shake = trauma^2, decay 3.0/s, max 3 lpx (9 px), no rotation, value noise 14 Hz with separate x/y seeds, round to whole lpx; keep the once-per-10 s cap. | Eiserloh trauma model as implemented in Bevy (trauma^2, smooth noise, decay); "a pixel or two" is a lot at low res (Blue Tengu) | Small |
| 6 | **Anticipation, smear and settle on slams and slide-ins** | Wind-up 3 frames (scale 0.92 or 2 lpx back); 1-frame streak smear when speed over 10 lpx/frame (stretch 1.6x along motion, 2 to 3 trailing edges in darker palette steps); landing squash per #4; slide-ins on an 8 to 16 lpx arc; contact shadow grows as the card falls. Never smear text on a frame it must be read. | 12 principles; smears usually 1 to 2 frames (Wikipedia/Williams); squeeze and stretch (Jonasson and Purho) | Medium |
| 7 | **Natural blinks, breathing, fidgets** | Blink every U(2.5, 6) s, 4 frames (half, closed, closed, half), 15% double blink, snapped to the nearest word gap; breathing 2-frame sub-pixel color shift at 0.7 s/frame; a fidget (6 to 10 frames on twos) after 8 to 12 s without a gesture, never on a number. | Measured conversational blinks about 208 ms and more frequent in talk (PLOS One via MNT); idle 2 to 4 frames at 400 to 800 ms (sprite-ai); sub-pixel breathing (Ansimuz example) | Small |
| 8 | **Gestures, brows and head bobs timed to words** | Gesture prep 18 frames (600 ms) before the key word, stroke 6 frames (200 ms) before; hold through the word, retract 8 frames. Brow raise 2 lpx, onset 4 frames before the first accented word of each section and instruction line, hold 10 to 20 frames. Head bob 1 lpx down 2 frames on RMS peaks over 4 dB above phrase median, max 2 per second. | Gestures start 644 ms and strokes 193 ms before the word (ter Bekke et al. 2024); brows precede pitch accents and mark instructions and segment starts, not questions (Flecha-García 2006) | Medium |
| 9 | **Anticipating, frame-rate-independent camera** | Pan toward the next beat's focus starting 6 frames before its cue; weight = 1 - exp(-8 x dt); 20% travel cap (existing); camera kick 2 lpx toward a slam for 1 frame; final offset rounded to whole lpx. | Camera lerp and camera position/look-ahead (Nijman); exp-based damping (Eiserloh, as implemented) | Small |
| 10 | **Readable on-screen text rules + flash/contrast gate** | Unspoken text holds max(25 frames, chars/15 s), max 7 s; one emphasis per phrase (color for terms, 1.0 to 1.25 pop over 6 frames for numbers); dialog word lit by color, not bounce; safe union top 210 / bottom 320 / left 60 / right 120 px; 4.5:1 contrast; automated gate: under 3 opposing luminance changes over 10% per 30 frames in any area over 25% of frame; no saturated red flashes. | Netflix min 5/6 s, max 7 s, 2 lines; 17 cps; Brysbaert 238 wpm; signaling d 0.41 (sparing); WCAG 1.4.3 and 2.3.1; karaoke caption critique | Small to medium |
| 11 | **Room-matched transitions that close before the cut** | 12 frames: 5 closing (easeIn), cut, 1 held, 6 opening (easeOut). Chalk wipe (board), roll-up door with slats 1 frame apart (garage), blinds that visibly close (workshop), iris on host head (house). Only at room changes (3 to 6 per video). Whoosh peak on the cut frame, started 5 frames early. | Full-screen transitions about 300 to 375 ms, enter decelerate / exit accelerate (Material); temporal contiguity d 1.22 argues against slow transitions | Medium |
| 12 | **Four chiptune room loops in one key** | 96 BPM, 8 bars = 20.0 s, A minor; per room instrumentation (12.5% pulse arps / 25% stabs + hats / 50% octave-down riff + triangle kick / sparse plucks); 1/16 arps 156 ms; vibrato 5.5 Hz +/- 20 cents after 150 ms; echo pulse 312 ms later at -9 dB, +7 cents; PolyBLEP band-limited squares; lead muted while words are active; crossfade 1 beat on the bar line at room changes. | NES channel roles and duty cycles (NESdev); echo, vibrato, triangle drum, tempo-as-intensity (ddrkirby); frequency carving (ProSoundWeb) | Large |
| 13 | **Brand sting** | 3 notes E5, G5, C6 on 25% pulse + triangle an octave down; notes 200 / 200 / 600 ms; last note vibrato 5.5 Hz and 400 ms echo at -9 dB; total about 1.6 s; identical every video; on the brand plate only, bed fully out 200 ms before. | Sonic logos are about 3 s snippets and getting shorter (Adelphoi podcast, opinion source) | Small |
| 14 | **Parallax and color-cycled ambience per room** | Layer factors 0.25 / 0.6 / 1.0 / 1.3 from the camera offset and zoom, each snapped to lpx; color cycles: chalk dust 3-step ramp at 6 fps, garage tube 2-step flicker with 1 to 3 s random gaps (never over 3 changes/s), welding glow 4-step at 8 fps, dusk ramp over 20 s; all ambient motion paused within 60 lpx of text being read. | 3 to 4 parallax layers (Bugnet); color cycling (Ferrari, Wikipedia); coherence principle d 0.86 for keeping ambience away from content | Medium |
| 15 | **Lighting and ordered dithering pass** | One key light top-left in every room; 1 lpx rim light on the host's side facing the room's practical light; 2 lpx contact shadows two palette steps darker; hue-shifted ramps (cool shadows, warm highlights); 4x4 Bayer dithering only in flagged gradient regions (light cones, sky, vignette, board glow), anchored to layer coordinates; never on text, faces or UI. | Hue shifting in pixel shading (pixel tutorials); ordered dithering is frame-stable, error diffusion crawls in motion (Wikipedia, ordered dithering) | Medium |

Suggested one-a-day order for the IMPROVE.md loop: 1, 3, 5, 4, 7, 9, 2, 10, 6, 8, 13, 11, 14, 15, 12.

---

## Sources

Game feel and pixel art
- [Jan Willem Nijman, "The art of screenshake", INDIGO Classes 2013 (YouTube)](https://www.youtube.com/watch?v=AJdEqssNZ-U)
- [Timestamped technique list for the talk](https://theengineeringofconsciousexperience.com/jan-willem-nijman-vlambeer-the-art-of-screenshake/)
- [Blue Tengu, experiments based on the Art of Screenshake](https://www.bluetengu.com/2014/12/12/art-of-screenshake-experiments/)
- [Juice it or lose it (Jonasson and Purho), GDC Vault](https://gdcvault.com/play/1016487/contactUs)
- [RPG Playground summary of Juice it or lose it](https://rpgplayground.com/research-making-a-juicy-game/)
- [Eiserloh, "Juicing Your Cameras With Math", GDC 2016 (Internet Archive)](https://archive.org/details/GDC2016Eiserloh)
- [Eiserloh slides (PDF)](http://www.mathforgameprogrammers.com/gdc2016/GDC2016_Eiserloh_Squirrel_JuicingYourCameras.pdf)
- [Bevy 2D screen shake example (trauma model constants)](https://bevy.org/examples/camera/2d-screen-shake/)
- [KidsCanCode Godot screen shake recipe](https://kidscancode.org/godot_recipes/3.x/2d/screen_shake/)
- [Frame-rate independent lerp rule, citing Eiserloh](https://github.com/nick-vas/Godot_TestSuite/pull/39)
- [Sakurai on hitstop (Source Gaming translation)](https://sourcegaming.info/2015/11/11/thoughts-on-hitstop-sakurais-famitsu-column-vol-490-1/)
- [SSBWiki: Hitlag](https://www.ssbwiki.com/Hitlag)
- [Saint11 (Pedro Medeiros) pixel art tutorials index](https://saint11.art/blog/pixel-art-tutorials/)
- [Saint11 subpixel tutorial post](https://x.com/saint11/status/816102966591705088)
- [Saint11 idle animation tutorial post](https://twitter.com/saint11/status/882228769230073858?lang=en)
- [Saint11 motion blur tutorial post](https://x.com/saint11/status/872098481057517568?lang=en)
- [Game Anim: MiniBoss pixel art tutorials](https://www.gameanim.com/2017/06/10/miniboss-pixel-art-tutorials/)
- [Animator Techniques: Sub-Pixel Animation](https://someanimatorwannabe.substack.com/p/animator-techniques-sub-pixel-animation)
- [Slynyrd Pixelblog 8: Intro to Animation](https://slynyrd.com/blog/2018/8/19/pixelblog-8-intro-to-animation)
- [Sprite AI: how many frames a sprite animation needs](https://www.sprite-ai.art/blog/sprite-animation-frames)
- [Wikipedia: Smear frame](https://en.wikipedia.org/wiki/Smear_frame)
- [Wikipedia: Color cycling](https://en.wikipedia.org/wiki/Color_cycling)
- [Wikipedia: Ordered dithering](https://en.wikipedia.org/wiki/Ordered_dithering)
- [Bugnet: implementing a parallax background](https://bugnet.io/blog/how-to-implement-a-parallax-background)
- [Pixel Grimoire: shading and light](https://medium.com/pixel-grimoire/how-to-start-making-pixel-art-6-a74f562a4056)
- [GameSpot: Celeste developer on game feel](https://www.gamespot.com/articles/celeste-dev-explains-how-they-made-their-game-feel/1100-6474775/)

Talking characters
- [Rhubarb Lip Sync mouth shapes](https://github.com/wzpan/rhubarb-lip-sync)
- [VRM lip sync with RMS (orca_forge)](https://dev.to/orca_forge/vrm-lip-sync-with-rms-minimal-implementation-with-aa-and-conditions-for-a-natural-look-2g68)
- [Tuning mouth opening with saturation rate and quantiles (orca_forge)](https://dev.to/orca_forge/fixing-exaggerated-vrm-lip-sync-by-tuning-mouth-opening-with-saturation-rate-and-quantiles-one)
- [Why lip sync should be two frames ahead](https://animationapprentice.blogspot.com/2022/04/why-lipsync-should-be-two-frames-ahead.html?m=0)
- [Wikipedia: Audio-to-video synchronization (ITU-R BT.1359, EBU R37)](https://en.wikipedia.org/wiki/Audio-to-video_synchronization)
- [ter Bekke, Drijvers, Holler 2024, Hand gestures have predictive potential (PDF)](https://pure.mpg.de/pubman/item/item_3565972_2/component/file_3565973/TerBekke_Drijvers_Holler_2024_hand%20gestures%20have....pdf)
- [Flecha-García 2006, Eyebrow raising in dialogue](https://era.ed.ac.uk/items/c1dfbb39-7eef-4b4d-aec0-8102dcc50453/full)
- [Medical News Today on blinking in conversation (PLOS One study)](https://www.medicalnewstoday.com/articles/323963)
- [How Kurzgesagt videos are made (production write-up)](https://gist.ly/youtube-summarizer/how-kurzgesagt-creates-videos-1200-hours-of-science-art)
- [How to make a Kurzgesagt video in 1,200 hours (transcript)](https://www.lingq.com/it/imparare-inglese/courses/689474/how-to-make-a-kurzgesagt-video-in-120-4887128/)

Typography, captions, accessibility
- [Netflix Timed Text Style Guide: General Requirements](https://partnerhelp.netflixstudios.com/hc/en-us/articles/215758617-Timed-Text-Style-Guide-General-Requirements)
- [Subtitle reading speed: CPS, WPM and limits](https://subtitle-toolset.pages.dev/guides/subtitle-reading-speed/)
- [BPS Research Digest on Brysbaert 2019 reading rate meta-analysis](https://www.bps.org.uk/research-digest/most-comprehensive-review-date-finds-average-persons-reading-speed-slower)
- [TikTok Ads: Creative best practices](https://ads.tiktok.com/help/article/creative-best-practices)
- [WCAG 2.2 Understanding 2.3.1 Three Flashes or Below Threshold](https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html)
- [WCAG 2.2 Understanding 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [Social media safe zones 2026 (third-party estimates)](https://adaptlypost.com/blog/social-media-safe-zones-2026-complete-guide)
- [Why karaoke-style captions can exclude disabled users](https://www.disabled-world.com/disability/accessibility/karaoke-captions.php)
- [Gernsbacher 2015, Video captions benefit everyone (PDF)](https://successforkidswithhearingloss.com/wp-content/uploads/2020/04/Video-Captions-Benefit-Everyone_2015.pdf)
- [Learning and the Brain: a critical look at "Video captions benefit everyone"](https://www.learningandthebrain.com/blog/video-captions-benefit-everyone-an-investigation/)
- [3Play Media on the Verizon Media and Publicis captions survey](https://www.3playmedia.com/blog/verizon-media-and-publicis-media-find-viewers-want-captions/)
- [3Play Media: captions increase Facebook video ad view time 12%](https://3playmedia.com/blog/captions-increase-viewership-for-facebook-video-ads)

Transitions and motion timing
- [Material Design (v1): Duration and easing](https://m1.material.io/motion/duration-easing.html)

Sound
- [Morphic: how to layer sound effects](https://morphic.com/resources/how-to/how-to-layer-sound-effects)
- [Game Developer: The power of pitch shifting](https://www.gamedeveloper.com/audio/the-power-of-pitch-shifting)
- [MusicRadar: avoiding the machine gun effect with round robin](https://musicradar.com/tuition/tech/how-to-avoid-the-machine-gun-effect-using-round-robin-sampling-632302)
- [MusicVivo: mixing music under voiceover](https://musicvivo.com/blog/music-under-voiceover)
- [ffmpeg-micro: FFmpeg audio ducking parameters](https://www.ffmpeg-micro.com/blog/fixed-music-volume-is-a-compromise-ffmpeg-audio-ducking-isn-t)
- [ProSoundWeb: balancing dialog in post production](https://www.prosoundweb.com/in-the-studio-balancing-dialog-in-post-production/)
- [Forasoft: LUFS targets per platform 2026 (with AES TD1008, EBU R128)](https://www.forasoft.com/learn/audio-for-video/articles-audio/lufs-targets-per-platform-2026)
- [Mr. Vocal: loudness for shorts](https://mrvocal.com/posts/loudness-for-shorts)
- [NESdev wiki: APU basics](https://nesdev.org/wiki/APU_basics)
- [ddrkirby: NES chiptunes in Unlock Everything](https://ddrkirby.com/articles/nes-chiptunes-unlock-everything/nes-chiptunes-unlock-everything.html)
- [Adelphoi Music podcast: Sonic logos, why so short?](https://www.advertisingweek360.com/?p=23563)

Attention and learning
- [Mayer and Fiorella: principles for reducing extraneous processing (PDF)](https://edtechuvic.ca/wp-content/uploads/sites/11/2022/09/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles.pdf)
- [Wikipedia: Seductive details](https://en.wikipedia.org/wiki/Seductive_details)
- [ScienceDaily on Cutting et al. 2010, shot lengths and 1/f attention](https://www.sciencedaily.com/releases/2010/02/100223121435.htm)
- [Lang et al., The effects of edits on arousal, attention, and memory (record only; abstract not accessed)](https://www.tandfonline.com/doi/abs/10.1207/s15506878jobem4401_7)
