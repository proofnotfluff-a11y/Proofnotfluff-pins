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
00a. Hook motion: the picture changes within 1 s and twice in the first 3 s, host on screen by 3 s (lesson 9 holds one
   card 0 to 7.6 s; style board 01).
00b. Type floor in `lint`: spoken words 44 px, labels 36 px at 1080 wide (lesson 9 runs about 20 to 27 px).
00c. Length in `lint`: fail a lesson over 75 s (6 of 9 lessons run 76 to 87 s).
00d. Fill the frame: y 1250 to 1600 is bare floor in most rooms (style board 04 to 06); set dressing or a lower band
   edge there, and a bigger host.
00. Motion: 60 fps renders (double render time) for smoother slides; Snow walk-ins, a point-at-board pose and a reaction
   pose on big numbers; squash and stretch on landings and 1-frame smears on fast moves (Todd, Oct 28: "better animation").
0. Captions lint in code: line 1 under 100 characters on all four, a send line on all four, hashtag counts per platform,
   the AI voice line, no em or en dashes (facts-captions caught two of these on lesson 4).
1. Sound: a short music bed per room (four tiny loops made in code, same key), ducked under the voice.
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
