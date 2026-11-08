# Hook moves: the opening library

Todd, video-lab chat, Nov 8, 2026: "Find ways to improve the hooks ... a hook move library with variety checks in code."
A move is the kind of first line, not its words. `anim.py hookmoves` lists the last 8 lessons' moves and the free ones.
From lessons dated 2026-11-26, `anim.py script` (before any voice) and `lint` fail an opening whose move repeats either
of the two lessons before or is already in 2 of the 5 before, whose first three words open one of the 6 before, or that
shares half its content words with one of them. The code reads script.md's first sentence, not the brief's label: on
Nov 6 to 8 four of seven lessons opened on a clock moment under four different Hook pattern labels.

## What the evidence shows, and what it does not
- Our 16 lessons with reads (research/metrics, Oct 31 to Nov 8): the top four (1,251 to 1,879 views across platforms)
  are all the phone cluster (missed calls, after hours) and three open on a concrete moment with a time. The bottom six
  (229 to 278) are sales-technique topics and three open on a quiz question about the owner's numbers. Topic and
  opening move go together in this set, so it cannot say which one did the work. Shares are 0 or 1 on every lesson.
- The 100K sources (research/PROVEN.md, research/outliers.json): openings name the viewer's money or moment, accuse
  ("You're losing...", "You're running a daycare..."), set two numbers against each other ($3.4M asked, $450K offered),
  or ask the viewer to judge ("What would you do?"). None opens on a statistic's source. Lengths run 20 to 111 s
  (median about 80 s). These are mostly people on camera; we have not tested whether an animated host carries the same
  move as well. The Gemini study (video/watch/pending, runs after the 2 am quota reset) reads the top 8 frame by frame.

## The moves (pick one the code says is free; a proven lesson keeps its source's move only if it is free)
| Move (code) | The line does | Evidence | How we draw it |
|---|---|---|---|
| clock-moment | a time and a place, something just went wrong ("ten to seven, her furnace dies") | our top 3; PROVEN row 7 | the clock on the cover, the moment by 1 s |
| you-scene | puts the viewer in the act ("You open your ad report...") | rows 14, 16, 17 titles accuse the owner directly | the owner's screen or truck, Snow points at the leak |
| money | a dollar amount the viewer is losing or paying now | rows 2, 16, 19 | the number as the cover hero, the loss counting |
| question | asks the viewer to judge a scene ("Would you take the check?") | rows 1, 3, 13, 21 (comments carry them). Ours: all 4 quiz questions about the owner's numbers ("Do you know your close rate?") are in our bottom half (250 to 359 views); a judge-this question is untested by us | the choice as two cards, the viewer's pick is the payoff; never a quiz about the owner's own numbers |
| source-says | a named source said something surprising | our sources lane; none of the 100K open this way | use when the source is the surprise, not the number |
| short-line | five words or fewer that set a scene ("The job's done.") | PROVEN row 1's one-line caption | one big line on the cover, the scene cuts in |
| claim | a contrarian or insider claim ("An AI receptionist can earn its keep. Just not...") | after-hours-robot (1,634, best TikTok watch 21 s); row 15 "90% don't know this math" | the claim on the cover, the turn by 3 s |

## Rules every move keeps (from the sources and the gates)
- Proven lessons from 2026-11-26 (Todd, Nov 8, decision 2: "Yes, hard check for proven"): the source's conflict in 5 to 8 words on the cover (frame 0; the source line and EXAMPLE aside), and the spoken hook (whole sentences to 9 or more words) 12 words or fewer, ending by 3.6 s. `anim.py script` checks the words before voice; `hook` and `lint` check the time after.
- Say the stake in the first sentence: the viewer's money, time or job, not the topic.
- One payoff, landed before half the runtime (the send rule), then stop. No pitch at the end.
- The cover (frame 0) states the same stake in 5 to 8 words; k.coverBoard draws it inside the frame rules.
- A proven lesson's opening never copies its source (anim.py copycheck) and now also never repeats our own last lessons.
