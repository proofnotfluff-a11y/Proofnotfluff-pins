# Learnings: what the gates caught, and what changed so it can't happen again

The studio learns in three loops (Todd, Oct 28, 2026, 3:43 pm: "make this video engine completely self-evolving"):
1. **Every run:** each gate fault goes here as one line (date, lesson, gate, kind, fix). A fault the code could have
   caught becomes a `lint` rule or a kit default the same day; a fault seen twice becomes a rule in the stage contract.
2. **Every run:** one IMPROVE.md item ships (visuals, motion, sound), proven on stills.
3. **Mondays:** the numbers (views, average watch, sends, saves per lesson) and a research run re-rank IDEAS.md and the
   hook formulas in research/runs/2026-10-28-script-playbook.md; what wins gets written into _shared/voice.md.

## Rules learned (newest first)
- Each lesson its own world (Todd, Oct 28): `lint` fails a lesson whose stock rooms fill over 40% of the runtime, that
  reuses the last lesson's set pieces, or that has fewer than 3 set pieces new against the two before (04_scene/worlds.json).
- Trades first (Todd, Oct 28): the main evidence comes from the trades; the facts gate fails other-industry studies.
- Frame 0 is the cover: no sheen, sparks or reveal on it (the shine waits until 1 s).
- The freeze check flags only truly stuck pictures (qa.freezeNoiseDb -70, Todd's word): small crisp motion counts.
- A number's base stays the source's: "points of share" is not "points of all orders" (facts caught lesson 4).
- A trade-specific sample says its trade in every caption ("1,000+ HVAC contractors").
- Pixel art never scales by a fraction: the arcade camera holds still (a 1.03x push-in made the tile lines swell and thin,
  Todd saw it); offsets snap to whole low-res pixels. Motion lives in the elements, not the camera.
- The close is one column with one left edge (x 120), the host small at the side; the send box is the one filled element.
- A board never sits empty more than 1 s: the next line lands on the beat's first word, not the cue's last.
- Strike a number only after it has been read (0.4 s), and with a thin line that leaves it legible.
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
- 2026-10-28 quote-revive: facts-captions, study line without its population ('In hiring experiments') -> fixed.
  Design 4.43: the fix line was the faintest text, a tag over the phone edge and the hat, three left edges on the close,
  empty board while the header waits -> hero line big, one left edge, text in on the beat's first word.
- 2026-10-28 markup-margin: QA loudness -15.1 (the limiter ate the gain) -> the mix adds the gap back and limits again.
  Design 4.57: formula box empty 3.5 s, close cards on three edges with the host's hand on one, a room prop through the
  title, a strike that hid the number it struck -> card lands at once, one left edge, host to the side, strike after 0.4 s.
- 2026-10-28 three-prices round 1: facts (base of the 5 points) and captions (HVAC) second FAIL, design 4.43 and golden
  (menu card over the citation) second FAIL -> all fixed, held for Todd's word.
- 2026-10-28 first-reply on the new art: critic 0 faults, design 4.71, golden post as is (sheen on frame 0 fixed after).
- 2026-10-28 book-the-call: lint variety saw no set pieces (worlds.json empty): its spy assigned over k.sets, a getter, and
  the assignment was dropped -> the spy redefines the property. Board text hidden under a card still counts for lint, so
  occluded set text is not drawn (a 7-day calendar week, versus stats off in the close).
