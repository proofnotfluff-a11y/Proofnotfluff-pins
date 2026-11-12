# Brief: Where $100 of the bill goes (v4 invoice)

Sample brief from research/VIRALITY-2026-11.md, written Nov 11, 2026. Not planned with Todd yet and not in the queue. Rules: `_shared/formats.md` "v4"; coo/constitution/video.md. It lives in research/ so no run picks it up by accident; the make run copies it to videos/<slug>/01_voice/brief.md once Todd says go, and reads the source again that run.

- **Format:** invoice
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** anyone who has looked at a plumber's bill and thought "that all goes in his pocket", and every owner who has heard it said.
- **The one idea:** A customer thought the whole price went in the plumber's pocket; in his own example budget about $9 of every $100 is left, and about $2 once the shop is paid for: say where the money goes before they ask.
- **Pull:** conflict yes (the customer who would not approve the work, and the owner); dollars yes ($100 split line by line down to $9, then $2); send yes (an owner sends it to the customer who says the price is a rip-off; a homeowner sends it to whoever in the house pays the bills). Breadth: a homeowner stops for the reveal; a tech stops because 41 of the 100 is their pay.
- **Shape:** the accusation on frame 0, the bill built line by line, what is left, the question that splits the room.
- **Music:** bounce (the make run checks `anim.py tunes`).
- **Voice:** Todd's clone (`_shared/voice.md`).
- **Source:** PHC Pros, "How much do you keep out of each consumer dollar?", Richard DiToma, "Contractor Profit Advantage" column, Mar 1, 2022. It is his own account of his own customer, and his own example budget: one technician, one truck, run from home by a married couple, with costs he calls minimal. The percentages are rounded and he says every company's will differ. The column is from 2022. The voice says "one plumbing shop owner says" and "in his example". The video names no person or business; the caption names the source.
- **Not used:** the column's "about 3% average profit" line. It names no source, so it stays out.

## Beats (a guide for the script, not the script)
1. Frame 0, settled: a bill stamped "$100" and the customer's line in 5 words: "IT ALL GOES TO YOU." Spoken hook, 8 words: "She thought the plumber kept all of it."
2. By 3 s: one plumbing shop owner says a customer refused to approve a job until she had talked to him. She believed the whole price was his.
3. The bill builds, one line as each is said, the total left counting down from $100: the technician's pay and what goes with it, about $41. The office, about $16. The truck, about $8. Insurance, about $2. The shop's running costs, about $4. Everything else it takes to stay legal and open, about $20.
4. `[payoff]` by 40%: what is left in his example: about $9.
5. Held for 70% to 85% (level-up, move 3): and that was before paying for the space the shop works out of. Count that, and he says about $2 is left.
6. He says that once he explained it, she approved the job at the price first quoted.
7. Close: "Two dollars on a hundred. Fair, or still too much? You decide." Last frame: both sides ("$100 BILL" and "$2 LEFT").

## Level-ups (each needs Todd's yes after Nov 23; without it, build to today's v4 rules)
- **Test:** the first second (move 4): two numbers on a settled frame 0 ($100 and $2 would give the ending away, so use "$100" against "IT ALL GOES TO YOU"), the first change by 0.6 s, the spoken hook done by 2.5 s.
- The send line (move 1), if approved: "Send this to the customer who thinks it all goes in your pocket."

## Staging notes (creative direction for cues and scene; no rule changed; from the read of the first v4 lesson's sheet, Nov 11)
- Show the fight happening, not labels over two people standing still: the two face each other; something changes hands or is pushed back (the invoice, the estimate, the phone); each reacts on the beat (arms crossed, a step back, turning to leave).
- One close shot on a face at the turn, and a second place or angle before the end. Faces must read at phone size: the refusal and the relief should not look the same.
- A plate carries the number or the two or three words the picture needs. It never repeats the caption under it, and the caption does not cover a face.
- Numbers move: the price is struck and the new one lands as it is said.
- The last frame shows the two people, one a side. Never the same person twice.
- One short line may be acted for each person, in our own words, with "Reenactment" on its first frame (formats.md "v4": an acted scene says so once). Say whose account it is once in the voice near the top and once in the caption, not on every sentence, as far as the facts gate allows.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| A customer would not approve the work until she spoke to the owner, because she thought the full price went in his pocket | PHC Pros, DiToma, Mar 1, 2022: his own account | https://phcppros.com/articles/15049-how-much-do-you-keep-out-of-each-consumer-dollar |
| In his example about 41% goes to technician pay and related costs | same | same |
| About 16% to office staff pay and related costs | same | same |
| About 8% to the vehicle | same | same |
| About 2% to insurance policies | same | same |
| About 4% to shop and office costs, not counting rent | same | same |
| About 20% to other operating costs | same | same |
| About 9% is left in that example | same: expenses about 91%, profit about 9% | same |
| About 2% is left once the shop space is counted | same | same |
| She approved the work at the price first quoted | same | same |

## Numbers on screen

Dollar figures are the source's rounded percentages of a $100 bill. Each one carries "about" in the voice (`anim.py` holds the "about" rule).

```json numbers
{"file": "video/studio/videos/<slug>/01_voice/facts.json", "numbers": {"bill": 100, "technician": 41, "office": 16, "vehicle": 8, "insurance": 2, "shop": 4, "otherOperating": 20, "left": 9, "leftAfterSpace": 2}}
```
