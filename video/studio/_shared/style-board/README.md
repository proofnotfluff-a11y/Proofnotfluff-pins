# Style board (the bar the lab and the design gate measure against)

The design gate (prompts/design.md) grades every lesson against this board from Oct 29, 2026 (Todd: "go with rec"): a missed type floor, a slow hook or a missing end card caps that score at 4. The pass bar itself (no score under 4, average 4.61) is unchanged.

Started Oct 29, 2026 (IMPROVE 000). Six frames from our own best lessons, cropped from their contact sheets (324x576, a 0.3 scale of the 1080x1920 output), plus board.jpg with all six. Each frame names what to keep and what to push. Replace a frame when a newer lesson beats it, and say so in research/LAB.md. Outside work we admire goes in as notes with its source page, never as copied art.

## The frames
- 01-hook-stat (lesson 1, 0.00 s). Keep: one number, huge, in accent; the source on the card. Push: the picture must change by 1 s and the host must be on screen by 3 s (this card holds still for 3.5 s).
- 02-host-with-prop (lesson 1, 7.12 s). Keep: host beside the thing being explained, a live timer badge, a sticky note that pops. This is the target for a scene: host, prop and one number together.
- 03-data-bars (lesson 1, 24.52 s). Keep: two bars that grow, the answer bar in accent, the study named at the top. Push: the label text (about 27 px at full size) up to the floor below.
- 04-dials (lesson 1, 45.34 s). Keep: two dials that compare at a glance, the result in an accent pill. Push: the bottom 40% of the frame is empty floor.
- 05-gauge (lesson 3, 45.06 s). Keep: the gauge needle as the hero, cost chips that add up to the quote. Push: the lower third is dead space.
- 06-calendar-script (lesson 9, 44.00 s). Keep: a real week, the booked slots filling in, the script lines numbered. Push: host is small and the floor below is empty; the script text is under the floor.

## Target spec (full-size px at 1080x1920)
- Palette (pixel look, _runtime/looks.js): bg #1B1420, bg2 #2B2033, ink #F4E6D3, accent #F2A541, accent2 #F7C873, teal #6FB7A8, cap #E2633B, jacket #2F6F67, bubble #FFF7EA, tag #7A3442. Text on its background at 4.5:1 or better (WCAG).
- Type floor: spoken words 44 px, labels and sources 36 px, the hero number 160 px or more.
- Layout: content in the band y 270 to 1250; nothing in the platform UI zones (top 210, bottom 320, left 60, right 120). Use the band: no more than a third of it empty for longer than 2 s.
- Host: on screen by 3 s, at least 360 px tall, pointing at or touching the thing being explained.
- Motion: the picture changes within the first second and at least twice in the first 3 s; something moves every 2 s; host body on twos, mouth on ones.
- Close: an end card for the last 3 to 5 s with the ProofNotFluff lockup and proofnotfluff.com, silent or music only (Jake Van Clief's end-card pattern).
- Length 45 to 75 s.

Sources: research/runs/2026-10-28-animation-sound.md (safe zones, contrast, hook timing, animating on twos); Jake Van Clief's ICM voice-driven-animation workspace (end card); prompts/design.md (the band).
