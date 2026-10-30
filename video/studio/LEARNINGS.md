# Learnings: what the gates caught, and what changed so it can't happen again

The studio learns in three loops (Todd, Oct 28, 2026, 3:43 pm: "make this video engine completely self-evolving"):
1. **Every run:** each gate fault goes here as one line (date, lesson, gate, kind, fix). A fault the code could have
   caught becomes a `lint` rule or a kit default the same day; a fault seen twice becomes a rule in the stage contract.
2. **Every run:** one IMPROVE.md item ships (visuals, motion, sound), proven on stills.
3. **Mondays:** the numbers (views, average watch, sends, saves per lesson) and a research run re-rank IDEAS.md and the
   hook formulas in research/runs/2026-10-28-script-playbook.md; what wins gets written into _shared/voice.md.

## Rules learned (newest first)
- Oct 30: Tune rebuilds (five waiting lessons). A design override covers only the build it was given on: the four tune-only rebuilds failed design at round 0 because round-1 asks waived on Oct 29 had never landed; fixing them passed all four at round 1 (4.71 to 4.86). A scene-side hex the arcade look doesn't hold is snapped to the nearest palette colour (#2B6CB0 rendered #3B82C4), so check colour on the mp4 and pick palette colours. A boss defeat or VICTORY is a claim: name the boss for the problem the line solves (SURPRISE BILL, PROMISE KEPT), never the customer's reaction a source doesn't show. Whisper flags a source name at a sentence start ("Jobber" heard "Jobbers"): the name rule skips sentence-start capitals, so put the name mid-sentence.
- Oct 29: Hook rebuilds (seven lessons). The design gate found new polish each round and landed at 4.57 on four lessons (2, 3, 4, 8), just under the 4.61 bar with no score under 4; consider splitting faults (must fix) from polish (logged). ElevenLabs bills about 1.7x the characters sent (786 credits for 462). A rebase onto a newer runtime changes what posting renders (the queue pins the commit), so re-check a gated lesson after a runtime change before `ready`. A worktree rebase makes its lab branch non-fast-forward: push the result to a new branch name, never force.
- Oct 28: Voice take numbers start at 1 ("--take 0" only re-transcribes). Whisper hears an s across a word boundary ("Quote still" as "quotes", "texts beat" as "text beat"): reword the line rather than re-roll. anim.py display() lowercases all-caps stress words, so trade acronyms go in its ACRONYMS set (ACHR, HVAC showed lowercase in a bubble). Hook cards need motion before 1.0 s or the freeze check fails at 0.0 to 1.03 s.
- Oct 28: Posting via Chrome: upload the copy at videos/<slug>/05_render/<slug>-post.mp4 (the session can read the repo path; /mnt/user-data/outputs is refused). Export keeps a render under 9.5 MB as is and two-passes anything bigger to under 9.9 MB. TikTok's first post asks "Ready to post?" to collect face and voice information: that is consent, so it holds for Todd's word (he said "accept tiktok" for lesson 1). After posting, TikTok shows Only me while the video is under review.
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
- 2026-10-29 AI lane round 0 (after-hours-reply, receptionist-myth, notes-to-quote): facts, an example message drawn
  in the hook close-up and the chat set with no EXAMPLE mark -> every story surface carries the gold tag. Critic and
  golden, a stamp placed by y alone landed on a desk card (oven) -> a stamp sits on its own plate inside the card it
  speaks to. Critic, set and card text past x 930 (inventory stat at 945, quote cells to 1057) while lint's edge is
  x 950 -> lint edge to 930 is an IMPROVE candidate. A W() lookup searches 1.1 s back, so /^price/ caught an earlier
  "price" and the blinds flag showed 2 s early -> anchor a lookup on a nearby unique word. Design 4.14 to 4.29:
  hero numbers at readout size, empty set areas, low-contrast heads -> a 198 px hero slot (gauge readout kept quiet
  and drawn over), a dark band under board lines. Body sizes 30 and 39 render the same (one pixel scale): only the
  display sizes (66, 132, 198) read larger; the dialog floor stays a runtime item (00b).
- 2026-10-29 book-the-call rebuild (queue rule, end card runtime): every gate PASS at round 0. Polish named: end card
  holds 2.5 s (aim 3+), card wants the game frame; boss -30 under the dither (named twice now: fix next rebuild); host
  arrives at 7.6 s; dialog words 38 to 40 px (lint type floor is IMPROVE 00b).
- 2026-10-29 monthly-first (lesson 10): voiced before the queue rule landed (7 lessons waiting), parked at words: takes 2
  and 3 slow (150, 143 wpm), 82.8 s over the 75 s aim; tighten takes 2 and 3 and re-roll before cues when it is made.
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
- 2026-10-28 book-the-call: Whisper skipped a whole take on the full file -> transcribe take by take. Proper names
  ("ServiceTitan", "Invoca") misheard -> a close spelling of a capitalized name counts as heard. The hook cover held
  still 2.8 s -> pings and sparks after frame 0 until the first number is said.
- 2026-10-28 three-prices rebuild (Todd: trades-only evidence, new scenery and motion): the restaurant menu beat (take 3)
  -> Housecall Pro's homeowner survey (68% get more quotes when a price is higher than expected); scenery -> counter,
  scores, slots and two pieces of our own (a 100-house street, a tailgate clipboard). The settled hook card read as frozen
  1.0 to 3.4 s at -70 dB even with shines on it -> the card swings a pixel on its strings from 0.6 s, sparks every 0.6 s.
- 2026-10-30 AI lane gates: the last YouTube tag in every lesson is a deliberate misspelling (captions.md); a fix round
  "corrected" it and facts-captions failed -> never fix the misspelled tag. A 2-line size-66 label under the 198 hero
  pushes the scope tag under the host and dialog -> one-line hero label, scope in the board's source tag. Design scores
  vary about 0.15 between fresh reviewers on the same render; type stays capped at 4 until the runtime dialog font rises
  (IMPROVE 00b), so 11-08 and 11-10 held on design at 4.43 and 4.29.
- 2026-10-30 markup-margin payoff-first: the split-flap board's hinge line cuts the middle stroke of 6, so 6 reads as
  S or $ (golden r0 must-fix) -> redraw landed letters whole with hinge notches at the cell edges; a redraw over a
  linted letter needs lint false. A 12-column board has no room for 'DIVIDE BY 0.6' -> 'DIVIDE 0.6'. Design held at
  4.43 r1 on the type cap again (third lesson); IMPROVE 00b is the blocker, not the scenes.
- Oct 30: the 7:46 am run could not render markup-margin: `ready` had pinned f9e92d86, a commit a later pull --rebase rewrote (7cef77c6, all 12 fingerprints equal), so it never reached origin. `ready` now refuses a commit origin does not have.
- Oct 30 lunch: rebuild held: 2026-10-30-markup-margin. Rebuilt on today's runtime with the night tune (classic was shared with the lesson next to it in line): lint PASS, check PASS, render critic 0 faults, buyer PASS (stop, send, save, follow yes), golden post as is, Kimi facts PASS with JLC (HTTP 403) and Xero lines unconfirmed, facts-captions unconfirmed on the same pages; design FAIL 4.43 r0 (type 4 on the size-30 labels, IMPROVE 00b; end card 2.8 s; small $1,666.67 on the NEXT QUOTE monitor; host 270 px). No fix round: the type cap is runtime-wide and failed this lesson twice before. Its old pin still posts; skip it in later rebuilds.
- 2026-10-30 lunch rebuild, markup-margin: design r0 FAIL 4.43 (hook 'quote?' on the panel border, '$1,000' tape tag on the border, gauge needle through the '50', lesson 1's sawhorse and lumber set in the hook); fixed in scene.js, r1 PASS 4.86. Open: the glint is a one-letter white slice that reads as broken letters on a paused frame (shared runtime; IMPROVE candidate). Lint did not catch music 'classic' shared with the lesson before until this run; rebuilt on 'sunny'.
- Oct 30, 12:40 pm (live chat): instagram.com's web uploader showed no Trial option, so markup-margin posted as a normal reel. Facebook's Reel button opens a native file picker that freezes the tab for screenshots; set the file on the page's video-only input instead. The device-bound lunch test run had no add_repo tool and got a 403 on push.
- Oct 30 lunch post, close-rate (instagram): Instagram web uploader showed no Trial option under Advanced settings, so close-rate went up as a normal reel.
- Oct 30 lunch post, close-rate (tiktok): two Chromes are connected; only the one Todd picks with switch_browser is signed in to TikTok. Browser 1 was signed out.
- Oct 30 lunch post, close-rate (youtube): YouTube's AI use question came up pre-set to Yes on upload; check it reads No before Publish.
