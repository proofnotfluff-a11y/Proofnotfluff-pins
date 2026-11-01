# Script check: 2026-11-15-three-fixes (quick-math, core lane; Nov 1, 2026)

## Five openings (viral-script step 4), read aloud at pace
1. "Missed calls cost this shop twenty-eight hundred a month. Which fix is worth it?" KEPT (round 1, after the script
   buyer gate failed C1 on the price-only opening "Three missed-call fixes, fifteen, forty-nine and forty-nine bucks"):
   the stake in the first sentence (C1, EXAMPLE), the three price tags already on the counter by 3 s (C5), an open loop
   answered in the last line (C4). 9 words to "month." so the spoken hook lands by about 3.2 s.
2. "You missed fourteen calls. Here's what catching them costs." (leans on part 1; no price on screen by 3 s)
3. "Answering service or AI receptionist? Neither, maybe." (no number, a tease)
4. "A person costs forty-nine a month plus every minute." (one fix only; the loop is weak)
5. "Your phone rings under a sink. Three ways to catch it." (a moment, no money)
Why 1 is stronger: the model videos open on "a call nobody answers" and then talk for 6 to 15 minutes without pricing
all three; ours puts all three prices on screen by 3 s and asks the viewer to pick (which-pick), the first which-pick
since three-prices.

## Human test (viral-script step 8)
- Read-aloud: PASS. Longest sentence 17 words (bar 20); 7 of 9 sentences (78%) 10 words or fewer (bar 60%).
- Owner words: PASS. 0 banned words; trade noun in the opening: "missed calls", "shop".
- Specific: PASS. "twenty-eight hundred a month" in line 1, three prices by line 9; every number keyed in facts.json (textback, person, ai).
- Sameness: PASS. First 4 words "Missed calls cost this" differ from the last 6 lessons' openings (grep of their script.md line 3).
- Do this week: PASS. Turn on a missed-call text this week (the exact words on the save card and in every caption) and
  call every missed call back inside the hour; the price card with what each catches and misses, held 3 s or more.
- Ear test: PASS. Every sentence one breath; `anim.py script` PASS (79 words, 6 takes, 2 tags).

## The 12-point check (_shared/voice.md, quick-math bands: 20 to 34 s, 45 to 80 words, 185 to 195 wpm)
1. Drop-in: PASS. 9 words to "month.", the money object, no percent, no source, no call-out.
2. On-screen hook: PASS (planned). "$2,800 a month. Which fix is worth it?" over the three tags $19 $49 $49 at frame 0, held to 3.2 s, safe area.
3. One idea: PASS. "A text answers right away, so with a fast callback the cheapest fix is worth it." (15 words)
4. Acted: PASS (planned). The AI tag gets the gut pick (the host points); the person's meter runs, the AI sends a link, the text pings back at once.
5. Facts: PASS. $19 a month (Quo, billed monthly, the same basis as the others; $15 yearly on the card), $49 + $2.99 a
   minute (PATLive), $49 a month for 250 minutes and a booking link by text (Rosie, round 1 facts fix), all read Nov 1 on the makers' pages; spoken forms match.
6. Artifact: PASS (planned). The price card (all three) and the exact text to copy (round 1 buyer fix, C3), from about 60% held 3 s or more.
7. Proof: PASS. Each price said while its own pricing page shows with its address.
8. Length: PASS. 79 words (band 45 to 80); about 29 s with the end card at 185 wpm (band 20 to 34).
9. Talk test: PASS. Contractions ("You'd"), "you" in 3 of 6 takes and the owner's money in the rest; no banned words; no dashes.
10. Voice markup: PASS. 2 tags ([matter-of-fact], [confident]); 0 CAPS; no digits or symbols.
11. No tail: PASS. No turn line, no spoken ask; "Part 2 of 2" only on screen and in the captions.
12. Button: PASS. "Call missed calls back inside the hour, and the nineteen dollar text is worth it." repeats
    "missed calls" and "worth it" from the hook; S1 the line before: "It answers right away, so they know you'll call back.";
    sendLine names a role ("whoever answers your phone when you can't").
