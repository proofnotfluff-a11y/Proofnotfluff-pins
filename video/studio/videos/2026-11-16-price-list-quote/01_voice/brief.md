# Brief: The price list prompt (AI lane)

Made Nov 1, 2026 in the scheduled evening record and make run (cloud). AI lane lesson of the Nov 1 to Nov 8 test
(_shared/lanes.md; `anim.py lanes`: make next ai). Rebuilds the held 2026-11-10-notes-to-quote, widened as research/topics-2026-10-30.md
asked (Depth bank #4, "Make ChatGPT quote from YOUR price list", with #10's notes), as a system the owner keeps
running (lanes.md "Systems, not tricks", Todd, Nov 1, 9:17 pm). The reply on screen is the exact text Gemini returned on
Nov 1, 2026 (demos/out/2026-11-16-price-list-quote-1/run.json).

- **Lane:** ai
- **Test:** turn by 5 s with a side (_shared/formula.md queued test 2): the belief "AI makes prices up" is said at about 4 s and flipped at once ("This time it stuck to your list"), the side taken is "your list sets the price", and the stake is free work in the first line ("This stair railing almost got painted for free"; no dollar figure we could source, no invented price). Test 1 (a spoken send line) was skipped: `anim.py script` refuses a spoken send line by rule, and gates are never edited to pass.
- **Format:** two-shops (_shared/formats.md: 35 to 52 s, 85 to 125 words: same job to two shops, each path step by step, the scoreboard, the one difference in one line)
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** the owner of a small residential painting company who walks a home, then quotes it from his notes, on a phone.
- **The one idea:** keep your price list in a note with one prompt on top, and AI turns any walkthrough into quote lines and flags what you never priced.
- **The system (lanes.md):** starts when a walkthrough ends; the tool is the free Gemini app; the setting is the phone note (price list plus the prompt on top, made once); the result lands in the chat as quote lines and flags; the one check is to price every flag and read every line before it goes out.
- **Do this week (on screen, held):** the setup card, 4 numbered steps with the prompt word for word, held 3 s or more (C3).
- **Shape:** the stake object on the cover (our railing with a $0 tag under the plate), the result by 0.8 s (the real reply's FLAGGED line, "Real reply, Gemini 3.8 Flash (API), Nov 1, 2026"; "This whole stair railing almost got painted for free") -> the turn by 5 s ("You'd think AI makes prices up. This time it stuck to your list.") and the loop ("So what happens to the railing?") -> painter one (10 pm, from memory, the railing missing, FREE WORK) -> painter two (the phone note: list, prompt, notes, pasted in the driveway) -> mechanism and the real reply (the prompt says use only his list; the railing is not on it, so Gemini flagged it; four quote lines, one flag) -> the honest check, answering the loop at about 75% (free; it didn't price the railing; he does, and checks every line) -> button (your list prices the job; you price the railing).
- **Cover line:** "Make AI flag / what you never priced." (plate; the Nov 2 facts script gate: "AI won't guess" promised more than one run shows)
- **Hook pattern:** result-first
- **Treatment:** steps
- **Example:** gemini-price-list-railing
- **Music:** quest
- **Metaphor:** the price list is the tool belt (inventory set): the AI can only work with what's on the belt; the railing is the tool that isn't there, so it gets flagged instead of faked. On screen for the mechanism beat.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** the real reply (run.json, every word, markdown marks and the warning sign left out) on a phone card labelled "Real reply, Gemini 3.8 Flash (API), Nov 1, 2026"; Gemini's own plan page cropped to "Free, $0/ month with a Google Account" with its address "gemini.google/subscriptions".
- **Worlds (_shared/sets.md):** our own night garage (painter one, the one room-and-panel section), `street` (painter two in the driveway), `inventory` (the price list as the tool belt, the metaphor), the real reply card, the setup card (the save card, with a step counter), `boss` (FREE WORK as the boss, beaten at the button: the native move, M7). Not the two lessons before's (three-fixes: counter, chat, scores; ai-night-quote: flaps, gauge, versus).
- **End card send line:** "Send this to your painter who still quotes from memory." (SCENE.sendLine; the Nov 2 buyer script gate: an owner who writes his own quotes had no one to send "whoever writes your quotes at night" to)
- **Asked by owners:** Jobber's own owner forum: "I've been using Chat GPT to help with my quotes as most of them are custom." (a reply about 22 days old on Nov 1, 2026: https://community.getjobber.com/discussions/quoting/challenges-getting-accurate--competitive-quotes-%E2%80%94-anyone-else/13386/replies/13934); and "ChatGPT with Jobber", "Anyone doing anything cool with this ?" (about 11 months old: https://community.getjobber.com/discussions/operations-forum/chatgpt-with-jobber/226). Read Nov 1, 2026.
- **Model videos:** see "Model video notes" below.
- **Trust notes:** The reply is Gemini's own text from one run (run.json), every word shown as returned, the markdown stars, the ruler line and the warning sign left out (the pixel font has none), labelled with the model, (API) and the date. It ran through Google's Gemini API on GitHub's machine, not the app; the free app may run another model, so an owner's reply will read differently (captions say so). We never say it always flags: one run, and "check every line" is the rule. "Free" is the plan page's "$0/ month with a Google Account", shot by the same run. Gems are not used: Google's help page says they go away on personal accounts starting November 2026, so the setup is a plain phone note pasted in. The painters, the 10 pm, the living room, the notes and the railing are ours, EXAMPLE on screen. No price appears anywhere ([my price] stays a slot). "He paints it for free" is the story's cost, acted, not a finding. The API call took 90 s on GitHub's machine; no speed is claimed.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| Gemini flagged this stair railing instead of guessing; it didn't price the railing | run.json, the flagged item: "This item is not on your price list. A custom price is needed." | video/studio/demos/out/2026-11-16-price-list-quote-1/run.json |
| Four quote lines, one flag; his notes say railing, not on the list, so Gemini flagged it | same run.json (4 quote lines, 1 flagged item) | same |
| The prompt on screen | same run.json, prompt | same |
| Gemini's free | Gemini plans page, "Free ... $0/ month with a Google Account", phone shot Nov 1, 2026 by the same run | https://gemini.google/subscriptions/ |
| The painters, the notes, 10 pm, the railing | ours (example story) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-16-price-list-quote/01_voice/facts.json", "numbers": {
 "lines": {"path": "demo.quoteLines", "shown": "4"},
 "flags": {"path": "demo.flagged", "shown": "1"},
 "items": {"path": "demo.listItems", "shown": "4"},
 "doors": {"path": "demo.doors", "shown": "2"},
 "free": {"path": "gemini.freePrice", "shown": "$0"},
 "steps": {"path": "setup.steps", "shown": "4"},
 "painters": {"path": "story.painters", "shown": "2"},
 "late": {"path": "story.typingHour", "shown": "10"},
 "railing": {"path": "story.railingPaid", "shown": "$0"}
}}
```

## Model video notes
Asked Nov 1 (evening run) with the watch-video skill; 1 of 3 answers read, so the script is a DRAFT (viral-script step 2 wants 2 or more before writing; the next run reads the retries first and rewrites if they change it).
1. https://www.youtube.com/watch?v=aVtVdnHMblw (answer: video/watch/answers/2026-11-01-price-list-quote-b.md): a 5.7 minute talking-head "ChatGPT for your construction business" by a business coach; marketing copy, templates and proofreading shown as real ChatGPT output; no estimate or price list step and no warning to check prices. What we take: nothing on quoting (the gap is ours to fill); real output on screen beats describing it.
2. https://www.youtube.com/watch?v=ZDy1YcLxpxA and 3. https://www.youtube.com/watch?v=9Jw8OKT5uDo: Gemini free-tier quota hit (HTTP 429, 20 requests a day used; "retry in about 4 h"). Retry as -r2 jobs after 8 am UTC Nov 2.
Our words only; no line, shot or script taken.

Nov 2 (lunch run): the a-r2 retry answered (video/watch/answers/2026-11-02-price-list-quote-a-r2.md): a 5.5 minute ChatGPT quantity takeoff video (bricks, cement bags), real ChatGPT output on screen, no price list step and no warning to check prices. So 2 answers read (b and a-r2); c-r2 got a Gemini 503. Both models show real output on screen and neither teaches quoting from your own list or checking the flags: our gap to fill, unchanged. Script rewritten after the script gates (buyer: the opener read as the AI failing, "Not off your list" unclear, the notes gap; facts: "anything new gets flagged" and "It won't price" promised more than one run shows).
