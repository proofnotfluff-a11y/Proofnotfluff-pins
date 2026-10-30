# viral-script (write a lesson script that sounds like a person and is built the way niche winners are built)

Todd, live chat, Oct 30, 2026: "Develop a skill so the scripts sound human and are structured on how the most viral videos
succeed in this niche." Used by the video-studio SKILL at stage 01 for every new lesson. It writes brief.md's Format, Hook
pattern and Treatment lines and script.md; the existing gates still judge the result.

## Inputs (Reads)
- video/studio/_shared/voice.md (the voice rules and the 12-point check), _shared/formats.md (the six formats).
- video/studio/research/viral-formats-2026-10.md (18 1M+ shorts read on their pages) and research/PERFORMANCE.md (what our
  own posts say: the newest diagnosis wins over outside research when they disagree).
- research/IDEAS.md, KNOWLEDGE.md and the lesson's facts.json.

## Process (Executes)
0. **Depth first** (Todd, Oct 30, 2026: "aren't really deep enough"; "Drive this hard"). Take the next lesson from
   IDEAS.md's Depth bank (research/topics-2026-10-30.md). It hands the owner one thing to do this week (exact words,
   setting, prompt or steps, on screen); a definition or someone else's percentage alone fails.
1. **Pick the problem, not the topic.** One problem an owner loses money on this month, said in their words ("they ghost
   after the quote", "I'm too cheap", "the phone rings while I'm under a sink"). Read IDEAS.md's top line, then check that
   people are asking it now: a public web search for the problem in owner forums or video comments from the last 90 days.
   No sign of anyone asking: take the next idea. Note the evidence link in brief.md (`- **Asked by owners:**`).
2. **Study what is winning on it this week.** Public pages only, no sign-in: search YouTube Shorts for the problem and
   read 3 recent videos with the most views (title, hook words, length, how it ends). Write one line in brief.md
   (`- **Niche check:**`) naming the angle they used and how ours differs. Never copy a script, a line or a shot.
3. **Pick the format** from _shared/formats.md that fits the problem and passes rotation (`anim.py variety <slug>` after
   brief.md exists). The fix is a line to say: clinic. A number: quick-math. A text or reply: fix-this. Speed or process:
   two-shops. A belief: myth-three. A habit that adds up: scenario.
4. **Write the first 3 seconds first,** and write five. The opening is 9 to 12 words, a moment or an object with a number,
   never a percent, a source or "trade owners,". Read each aloud at speaking pace; keep the one a busy owner would not
   scroll past. Our own numbers (PERFORMANCE.md) set the bar: 60% of viewers left in the first 3 s on our first lessons.
5. **Write it as talk.** Tell it to one owner across a tailgate. Contractions. Short sentences, one aside. Say "you".
   Plain trade words (call, quote, truck, homeowner, callback), never marketing words (leverage, funnel, optimize,
   pipeline, game-changer, unlock, secret, hack). Numbers said the way a person says them: money as owners say it
   ("a thousand bucks", "two grand"), an exact figure plainly, a rounded one flagged ("call it"), never "about" before
   an exact figure. Say the viewer's wrong first guess out loud, then correct it. Average sentence under 12 words, at
   least 3 fragments of 1 to 3 words, one idea a sentence, no sentence with more than two numbers. Same key words all the
   way through. No AI tells: no staged run-ups ("Here's the thing"), no lists of three for rhythm, at most one "not X,
   it's Y". Tags: two a script, sounds only, open with none or `[conversational]` (_shared/voice.md).
6. **Make the middle earn the watch.** Every 3 to 4 seconds a new fact, a turn or a picture change. Show it acted, not
   explained. One open question set in the opening and answered late.
7. **End on the answer.** The last line is the rule, echoing a hook word. No "follow", no "save this", nothing after it.
   The send line lives on the end card and in the caption.
8. **The human test** (write the results in `01_voice/script-check.md`, PASS or FAIL with the number):
   - Read-aloud: no sentence over 20 words; 60%+ of sentences 10 words or fewer.
   - Owner words: 0 banned words; at least 1 trade noun in the opening.
   - Specific: at least 1 concrete number or object in the first 2 lines; no claim without a facts.json key.
   - Sameness: the opening's first 4 words differ from the last 6 lessons' openings (`grep` their script.md).
   - Do this week: the lesson names one action an owner can take this week and shows the thing to copy on screen.
   - Ear test: read it aloud at speaking pace; every sentence fits one breath; `anim.py script` PASS (tags, "about").
   - Then the 12-point check in _shared/voice.md with the format's own bands.

## Outputs (Writes)
- brief.md lines: Format, Hook pattern, Treatment, Example, Asked by owners, Niche check; script.md; script-check.md.
- Never: a quote over 15 words from anyone's video, a real customer's words, an invented story told as true, a number
  not in facts.json, em or en dashes.
