# Script check: 2026-10-30-markup-margin, payoff-first rebuild (Lead Clinic v2, _shared/voice.md 12 points)

Scored Oct 29, 2026 on script.md and the real words.json (take 2 re-voiced twice: Whisper heard "half is" as "half his";
reworded to "half the price is margin", flags 0). The payoff-first test reorders the v2 beats (drop-in, the answer at
once, the usual way, why and the formula, proof, button); the 12 points are the same.

1 drop-in: PASS 10 words ("This job costs you a thousand. What do you quote?"), "job" and "you", no percent, source or call-out; said by 2.98 s
2 on-screen hook: PASS 6 words ("$1,000 job. What do you quote?"), settled on frame 0, held 0 to 3.56 s across three shots, inside the safe area
3 one idea: PASS 11 words ("to get a 40% margin, divide your cost by 0.6"); every beat serves it
4 acted: PASS the usual way rung up on the register (cost, +50%, $1,500, the price split in thirds), not explained to camera
5 facts: PASS 14 on-screen numbers resolve from facts.json (`anim.py data`); JLC and Xero re-read Oct 29; facts and facts-captions gates PASS
6 artifact: PASS the answer "$1,000 / 0.6 = $1,666.67, 40% margin" spoken 3.56 to 8.22 s and on screen 3.56 to 8.99 s (the payoff-first variable); the formula Price = Cost / (1 - margin) held 26.62 to 31.00 s (4.4 s), done by 68% of the runtime (the answer card at 8%)
7 proof: PASS one sourced number after the fix (a 50% margin takes a 100% markup, $2,000 on $1,000), tag "Math: JLC" on screen while said
8 length: PASS 120 words; 45.7 s with the end card (40 to 50)
9 talk test: PASS a contraction and "you" in takes 1, 2 and 4, "you" in all five; 0 banned words; 0 dashes; longest sentence 17 words
10 voice markup: PASS 2, 1, 1, 1, 1 tags, all on the list; 1 CAPS word (DOUBLE, take 4); no digits, $, %, / or & in the voice
11 no tail: PASS no turn line, no honest note, no spoken send, save, like, follow or comment ask
12 button: PASS last sentence "So when a job costs you a thousand, quote from the margin you want, not the markup." repeats "job", "costs", "thousand", "quote"; SCENE.sendLine "Send this to whoever sets your prices."

Pace: takes at 159, 185, 160, 177, 198 wpm (voice.md band 150 to 200; take 1 carries the payoff and was kept rather than re-rolled at 159).
Result: 12 of 12.
