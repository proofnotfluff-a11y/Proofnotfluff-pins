# Storycraft: how the best storytellers hold a listener (story desk, from Nov 5, 2026)

Todd, live chat, Nov 2, 2026, 8:49 pm (PRINCIPLES.md): "Storytelling is the most important skill for gaining followers.
We need people to trust we can guide them." and "The journalist is our prize winning storyteller and should develop this
skill by learning from the best." This file is that learning, in our own words, with where each idea comes from. The story
desk writes every story.md by it; the read-aloud and retell gates judge by it. It outranks word counts and beat timings.

## Five tools from the masters
1. **But and therefore, never "and then"** (Trey Parker and Matt Stone, NYU, 2011; transcript
   https://speakola.com/arts/tag/NYU). Write the beats on a line. If "and then" fits between two beats, the story is a list
   and the viewer leaves. Each beat must follow from the one before ("therefore") or break it ("but"). This is the single
   test the read-aloud gate runs on every sentence pair.
2. **And, But, Therefore in one breath** (Randy Olson, from the same rule; interview
   https://www.wissenschaftskommunikation.de/?p=80893). Before any script: "<what's true> AND <what else is true>, BUT
   <the problem>, THEREFORE <what to do>." If the story can't be said that way, it isn't one story yet. The ABT line is
   written at the top of story.md, and the message line comes out of its THEREFORE.
3. **The story spine** (Kenn Adams, 1991, used at Pixar; NPR, Jun 23, 2026, https://www.npr.org/transcripts/nx-s1-5750619).
   Once there was a shop. Every day it did X. But one day Y. Because of that, Z. Because of that, the cost. Until finally,
   the fix. Ever since then, the rule. "Every day" is the setup most of our old scripts skipped: the viewer needs the normal
   before the break means anything.
4. **Anecdote, then reflection** (Ira Glass, This American Life; https://www.storycenter.org/storycenter-blog/blog/2013/7/1/ira-glass-on-storytelling).
   An anecdote pulls by itself because one action leads to the next, like a train with a destination; keep raising a small
   question and answering it. But an anecdote with no moment of reflection ("here's why this matters to you") is gossip.
   Alternate: action, what it means, action, what it means.
5. **Show the paper** (our investigative standard, _shared/investigative.md). A reporter's story rests on a document. The
   receipt on screen while it's said is our "show, don't tell."

## What a story.md must have (in this order)
- **ABT line:** the one-breath version (tool 2).
- **Message line:** one sentence, 20 words or fewer, a stranger could repeat. It is what the retell gate must hear back.
- **Who:** one owner in one situation the viewer recognizes ("a two-truck HVAC shop, first cold night of the year").
  An example is labeled "Example"; a real case is a record we opened. Never a named private person or small business.
- **Every day (the setup):** what normal looks like and why it seems fine. One or two sentences.
- **But (the problem):** what breaks, with the number or the document that proves it.
- **Because of that (the cost):** what it costs this owner this month, in money, jobs or hours.
- **The turn:** the thing nobody mentions (the fine print, who pays, what the tool does not do, what the owners in the
  threads actually found). This is where trust is earned: we tell them the catch.
- **The payoff (what to do):** one setup or check they can finish this week, the exact words or steps.
- **Kicker:** a last line that echoes the opening and lands the rule.
- **Receipts:** every fact with its URL, publisher and date opened. Pulse items with their links.

## Line by line (what the read-aloud gate checks)
- Every sentence needs only what the viewer has already heard. A new word, name or number is set up before it is used.
- Same thing, same word, all the way through ("missed call" stays "missed call").
- One idea a sentence. A sentence can be long if it is one thought said the way a person talks; it fails if it is two
  thoughts glued together or a list read aloud.
- Spoken, not written: contractions, "you" and "I", a side taken. No headline grammar ("Missed call. Lost job. Big cost.")
  in a row: fragments are seasoning, three in a row is choppy.
- No jump cuts in logic: if a listener would ask "wait, why?", the answer is the next sentence, not a later one.

## Openings that respect the story
The opening is still the most important three seconds (PERFORMANCE.md: 60% left in the first 3 s on our first lessons).
Relaxed (Todd, Nov 2): the result-first opening and the 5-second turn are options, not rules. Pick the one that fits:
- **The moment:** drop into the "but one day" ("Seven forty on the first cold night, the phone rings twice.").
- **The receipt:** the surprising line from the document, on screen as it's said.
- **The owners' words:** what owners keep saying in the threads, paraphrased ("Owners keep saying the AI answering
  service books jobs they can't do.").
- **The result:** the finished thing first, then how (old C5), when the result itself is the surprise.
Whatever the opening, the setup still comes next: one line of "every day" before the problem pays off.

## The test before handing a story to the engine
Read story.md aloud, start to finish. Then answer in writing at the bottom:
1. The ABT line reads as one breath: yes or no.
2. Between every two beats the word is "but" or "therefore", never "and then": list any "and then" pair.
3. A stranger who heard only this could say the message line back: yes or no, and what they'd likely say instead.
4. The turn tells them something the vendor or the obvious answer would not: name it.
Any no goes back to the desk. The engine never fixes a broken story with motion graphics.

## For the engine (viral-script, a story lesson)
- Steps 0 and 1 are done by the story (its problem came from the pulse). Step 2 reads the gurus.md compare set first.
- Step 3 picks a Shape (brief.md `- **Shape:**`): moment, receipt, two-shops, myth-three, scenario, case, or another that
  fits. It rotates (`anim.py variety`); "story" itself never does.
- Step 4: five openings from "Openings that respect the story" above. Result-first and a turn by 5 s are options.
- Step 5 numbers are guides: a sentence that needs 18 words to make sense keeps them. Coherence beats compression.
- Keep the story whole: the setup, the turn and the payoff all reach the script; no claim story.md lacks.
- Step 8: the human-test numbers are NOTES; read-aloud then retell on script.md (fresh agents) and facts gate it before
  any voice. `anim.py script` prints guide misses as NOTE.
