# Improve: one better thing every run

Todd, Oct 28, 2026, 3:04 pm: "Constantly try to improve these videos. Look for new ways to enhance visuals, motion
animations, sound, etc." Every daily run ships exactly one item from the backlog below (or a better one it found), in the
shared runtime (`_runtime/kit.js`, `player.js`, `looks.js`, `_shared/`), proves it on stills of today's lesson and lesson 1,
and logs it. One change a day keeps a bad change easy to find. Gates judge the result like any other change.

Order of pick: a fault a gate named twice in the last week, then the item most likely to raise watch time or sends (the
weekly numbers), then the top of the backlog. Research runs (Mondays) add items with their source.
The lab (Tue, Thu, Sat) ranks this list from its benchmark against _shared/style-board/ and builds the bigger items.

## Backlog (most promising first)
000. End card: the last 3 to 5 s show the ProofNotFluff lockup and proofnotfluff.com, music only (Jake Van Clief's
   voice-driven-animation end card; the buyer gate answered follow_or_link "no" on lessons 1 and 8).
00s. Sound effects from earshot's code bank (Todd, live chat, Oct 31, 2026: "Let's include these skills", on a reel naming
   earshot, Real SFX and Openverse). Vetted Oct 31 in a live chat: github.com/Leonxlnx/earshot, MIT, pinned commit
   591fa3e; `earshot sfx list` shows 252 sounds made in code (no recordings, no models, no network; only numpy, scipy,
   soundfile, soxr); whoosh_fast/tight and click/soft rendered and passed `earshot sfx check` (clean). Copy only
   earshot/forge (bank, sfx, kit, dsp, fx and their json) and LICENSE into tools/earshot/ at that commit; never pip
   install the package (it pulls torch and transformers) and never use its llm, mcp or models code. Map our 7 effect names
   to 2 to 3 bank ids each so takes vary across lessons (our variety rule), keep every rule in _shared/sound.md (levels,
   1.5 s spacing, never on a number, the sting stays ours), and A/B one lesson's mix with `anim.py check` before the switch.
   Also from Real SFX (github.com/Bodila51/opus-sound-layer, MIT, 52ac266): add its idea to `anim.py check`, each effect
   within 2 frames of the picture change it marks. Its sample downloader and the Openverse API stay out (recordings with
   varying licenses; "No samples, no licenses" in _shared/sound.md).
00t. Grow the set catalog: one new set piece a week in _shared/sets.md (16 on Oct 31). At 4 a day a set comes back
   every day or two, and the variety rule now bars the last two lessons' sets (Todd, Oct 31, 2026, 11:58 am: "put
   measures in place to mitigate those risks as much as possible", on mass-produced flags).
00b. Type floor (the design gate caps type at 4 under 44 px spoken words or 36 px labels at 1080 wide). Spoken words:
   done Oct 29 (Done, below): the arcade dialog box is size 66 now. Left: labels, tags and sources under 36 (size 30 or 39,
   about 21 to 27 px caps; lesson 9's prompt card, the HUD and k.chip tags) still cap type at 4. Not changed on purpose
   for now; next: a `lint` check that names every label drawn under size 36, then raise them scene by scene.
00e. Trim each voice take's silent tail to about 0.3 to 0.5 s in the voice pipeline: lesson 3's take 5 left a 1.39 s
   tail (1.71 s of dead air at 59.9 s) and read 147 wpm on file length though it was spoken at 161; lesson 5's take 6
   reads 148 on the file and 155 spoken. The pace check measures the file, so a long tail is a false slow flag.
00g. Lint the on-screen hook hold (2.5 to 4.0 s) and the segment name on screen: two lessons failed the script gate on
   these on Oct 29; lint does not check them.
00h. Variety lint looks back two lessons only; the design gate caught set repeats three to four lessons back (shared
   drawer-shop set, cream note sheet, flaps on lesson 9 next to lesson 8). Look back four.
00d. Fill the frame: y 1250 to 1600 is bare floor in most rooms (style board 04 to 06); set dressing or a lower band
   edge there, and a bigger host.
00. Motion: 60 fps renders (double render time) for smoother slides; Snow walk-ins, a point-at-board pose and a reaction
   pose on big numbers; squash and stretch on landings and 1-frame smears on fast moves (Todd, Oct 28: "better animation").
0. Captions lint in code: line 1 under 100 characters on all four, a send line on all four, hashtag counts per platform,
   no AI voice line (Todd, Oct 29), no em or en dashes (facts-captions caught two of these on lesson 4).
1. Sound: a short music bed per room (done Oct 28), now in six tunes (done Oct 29, below). Next: a tune per lesson
   picked from the hook's mood, and a two-bar fill on the last bar before each room change.
2. Motion: a squash and stretch landing on every slammed number (scale 1.15 x 0.9 for 2 frames, then 1).
3. Host: lip shapes matched to the voice's loudness (open, half, closed) instead of a fixed talk cycle.
4. Visual: a one-frame white flash and a 2 px offset (impact frame) on stamps only; never more than once in 10 s.
5. Motion: the camera pans to the element being spoken about (focus points from the cue text, not hand-set).
6. Sound: a typewriter tick per word in the dialog box at low level, off during numbers.
7. Visual: a cover frame for each platform (the hook card at full size, ProofNotFluff mark) exported as a still.
8. Motion: transitions that match the room (blinds for the workshop, chalk wipe for the board, garage door roll-up).
9. Host: idle actions between lines (look at the board, adjust cap, check phone) so he is never frozen.
10. Visual: on-screen captions of key phrases (two to four words) in the safe area, for viewers with the sound off.
11. Sound: a two-note sting on the brand plate at the end (our own, made in code).
12. Visual: a seasonal touch per week (snow outside the half-built house in winter, leaves in fall).

## Done (newest first: date, item, what changed, proof)
- 2026-10-30 (lunch run, 11:37 slot): qa frozen window to the end card (00i). `check` now checks frozen stretches up to
  the end card (last word + 0.1 s, as player.js END_T) instead of the close cue, so the close room is checked. Proof:
  markup-margin rebuild, window 37.75 s -> 42.67 s, frozen PASS (0 stretches; the only freeze, 44.4 to 45.67 s, is the
  card); stills of markup-margin read and lint PASS. Lesson 1 not re-rendered this run (its MP4 is on video-renders).
- 2026-10-30 (lunch run): dialog pages follow sentences (00h). buildPhrases in player.js gives a sentence's last word or
  two back to its own page when it fits, else carries the sentence's last words over with it (from a comma when there is
  one); a page no longer ends on the first word of the next sentence. Proof: dialog pages of all 13 built lessons, lone
  words 10 -> 0, pages opening on the sentence before's last word 29 -> 2 (both whole short sentences: "That's it.",
  "Forty-one."); stills of lesson 1 ("to them tonight.", "The exact text is in the caption." whole) and markup-margin
  (its 23 pages unchanged); lint lines the same with and without the change. Queued pins render their own commit.
- 2026-10-29 (Todd, 8:11 pm: "different tunes for each video"): six room tunes of our own. `anim.py sound` builds
  classic (A minor 96, unchanged byte for byte) plus sunny (C major 120), quest (D minor 108), night (E Phrygian 88),
  chase (F major 132) and bounce (G Mixolydian 112, swung), each its own chords, lead and room patterns, to
  `_runtime/music/<tune>/<room>.wav` (15.4 MB, RMS 0.12, seams under the loops' own steps, room crossfades 1.5 to 1.7 dB
  like classic's 1.58). cues.md says `music: rooms <tune>`; the crossfade is one beat of the tune; `variety` fails a
  tune shared with the lesson before or after in line (`tunes SLUG` names the free ones). Every new tune keeps C, E and
  G natural, so the sting never rubs. Proof: mixes of 11-08 on four tunes (-15.9 LUFS without a voice, as classic).
- 2026-10-29 (Todd, 8:08 pm: "Go with your recommendation"): spoken words bigger (00b). The arcade dialog box draws its
  words at size 66 in the display pixel font (33 px caps, was 39 in the body font, 21 px), two rows, line height 78,
  same box; `buildPhrases` cuts pages with the box's own pixel widths, so every page fits two rows at 66; a page with one
  word wider than a row steps down to 39 on three rows; the more arrow moved under the second row. Proof: the real
  player.js and kit.js code run on all 14 lessons' words: 0 pages over two rows, 0 step-downs, ink right edge 897 of 902;
  11-08 goes from 19 pages to 22. Stills and lint not run (no Chromium in that session): run them on the next build.
- 2026-10-29 (Todd: yes): end card up for the last 3.0 s. `cues` tail 2.9 s -> 3.1 s and the card drops 0.1 s after the
  last word (was 0.35 s), so it held 2.3 to 2.5 s before. Proof: the six waiting lessons rebuilt on it (lint, check).
- 2026-10-29 (Todd: "get this fixed today"): hook motion (00a) and the 75 s cap (00c). anim.py `hook` measures the
  first 3 s (a change = 8% or more of the frame, first change by 1.0 s, two by 3 s, host by 3 s) and the spoken hook
  (9 to 12 words, said by 3.6 s); `lint` runs it and `check` fails over 75 s; scene contract, looks and template carry
  the rule. Proof: all seven waiting lessons failed it before; rebuilds pass it: lesson 3 (changes 0.8, 2.07 s; 74.6 s,
  re-queued), lesson 7 (0.53, 1.87; 74.76 s), lesson 8 (0.8, 2.33; 73.28 s), lesson 4 (0.53, 1.93; 74.45 s), lesson 2
  (0.67, 1.87; 72.0 s), lesson 6 (0.8, 2.6; 74.51 s). Gate results per lesson in their reviews/ on lab/hooks-<slug>.
- 2026-10-29 (daily run): end card (backlog 000). player.js draws a plum plate that drops in on whole pixels 0.35 s after
  the last word: ProofNotFluff, proofnotfluff.com (underline draws on), "Lessons for trade owners", Snow waving on a floor
  strip, a corner twinkle every 8 frames; host and dialog step out, lint counts only the card's words. `cues` tail 1.9 s
  -> 2.9 s. Proof: stills of lesson 9 (77.2 s) and lesson 1 (88.4 s); lesson 9 rebuilt and re-gated on it, every gate
  PASS (buyer follow_or_link yes; design 4.71 asks for 3 s or more and the double game frame on the card: next).
- 2026-10-29: style reference board (backlog 000) in _shared/style-board/ (six of our best frames, keep and push notes,
  the target spec); the lab (.claude/skills/video-lab, Tue Thu Sat) benchmarks against it. Queue rule: `ready` keeps a
  rebuilt lesson's place, `waiting` lists unposted lessons, the daily run rebuilds instead of making when 3 or more wait.
- 2026-10-28 (evening): steady pixel camera (no fractional zoom), shapes, text and rooms on whole low-res pixels. Proof:
  lesson 1 floor moved in 17 of 150 frames (4 to 9 s), now 0; lint PASS.
- 2026-10-28 (overdrive): room music loops ducked under the voice and a sting on the send line (backlog 1, 11); lip
  shapes from the voice (3); room transitions incl. wooden slats (8); idle blinks and fidgets (9); `lint` layout check;
  pinned post queue (`ready`, `next`, `postcopy`); respell reads digits as words (`rewords`). Proof: lesson 1 gates
  (critic 0 faults, design 4.86, golden post as is), lessons 2 to 4 stills.
- 2026-10-28 (round 2): pixel font trimmed to ink (even letter and word spacing), typed messages keep their width and
  grow down, wedge clocks, slide-ins fade and travel less, one-word dialog phrases joined, host can step back (hostScale),
  scenes can hide the dialog box, post copy under 10 MB (`export`). Proof: lesson 1 stills and gates.
- 2026-10-28: open pixel s (Poppins 15 px cut), seamless pixel rows under zoom, hook card first frame, dialog box holds
  the last line between takes, chalk smudges off the text, a compressor in the mix (loudness -14.7 LUFS). Proof: lesson 1
  stills and gates.
