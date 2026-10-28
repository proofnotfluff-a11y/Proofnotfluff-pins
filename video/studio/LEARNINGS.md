# Learnings: what the gates caught, and what changed so it can't happen again

The studio learns in three loops (Todd, Oct 28, 2026, 3:43 pm: "make this video engine completely self-evolving"):
1. **Every run:** each gate fault goes here as one line (date, lesson, gate, kind, fix). A fault the code could have
   caught becomes a `lint` rule or a kit default the same day; a fault seen twice becomes a rule in the stage contract.
2. **Every run:** one IMPROVE.md item ships (visuals, motion, sound), proven on stills.
3. **Mondays:** the numbers (views, average watch, sends, saves per lesson) and a research run re-rank IDEAS.md and the
   hook formulas in research/runs/2026-10-28-script-playbook.md; what wins gets written into _shared/voice.md.

## Rules learned (newest first)
- A hook's claim matches the number it cites: "Top shops quote 3 prices. Not 1." under a 57% stat is an overclaim; say
  "on 57% of home jobs" (facts and golden caught it on lesson 4).
- A stat box shows its rows (labels and empty tracks) as it opens; a big empty panel reads as broken.
- Count-ups start near their value (85%), so a bar never flashes the other group's figure on the way up.
- Headers on ruled boards sit on a dark band; ruled lines never run through text.
- Whisper writes numbers as digits ("$1" ",000."); respell says them as words before matching, so a number never shifts
  the words around it (lesson 3's "a thousand dollars" sat 1.4 s late). `anim.py rewords` re-times an old voice.
- Text over text, text under the host or the dialog box, text off the safe area: `anim.py lint` catches it before any
  reviewer (built Oct 28 after three gate rounds of overlaps).
- Frame 0 is the cover on most phones: the hook card is fully settled on frame 0, no reveal in progress.
- A typed message keeps its final width and grows down; it types when its words are said, not when the cue starts.
- Notes and stamps never cover the thing being discussed (the question being answered, the line being quoted).
- Board text is clipped to the board and fades in; nothing slides across a frame edge.
- The dialog box breaks pages at clause ends and never starts a page on a unit ("percent", "million", "hours").
- Captions: every study number carries its population ("in a study of 11.6M Fiverr requests"); no title promises an
  outcome no source tested ("helps you win the job"); quote the source's comparison wording exactly.
- Pixel fonts: glyphs trimmed to ink with a 1 px letter gap and a clear word gap; an s that is open.

## Fault log
- 2026-10-28 first-reply: design, type 3 (s read as e) -> font recut. Critic, overlaps x3 -> lint built. Facts-captions,
  Fiverr qualifier missing in line 1 -> rule above. Design, cramped build scene -> host can step back (hostScale).
- 2026-10-28 three-prices: facts and golden, hook overclaim ('Not 1') -> card says 'on 57% of home jobs', voice 'usually'.
  Facts, 'Why the middle wins' -> 'gains'. Facts-captions, TikTok send line missing and YouTube line 1 at 137 characters
  (fixed; a captions lint is next on IMPROVE). Design 4.14: empty stat boxes, sticker on the bar, ruled lines through
  the header, close left-aligned with a small call to action, stray $ past the card edge -> all fixed.
- 2026-10-28 markup-margin: transcript flag '$1 ,000.' was a respell miss, not the voice -> respell reads digits as words.
