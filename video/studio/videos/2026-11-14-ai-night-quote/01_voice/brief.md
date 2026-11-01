# Brief: The 11 pm quote request, answered with a free AI app (AI lane)

Made Nov 1, 2026 in the scheduled morning record and make run (cloud). AI lane lesson 1 of the Nov 1 to Nov 8 test
(_shared/lanes.md; Todd, Nov 1, 9:01 am: "go with your recommendation"). Rebuilds the held 2026-11-08-after-hours-reply
(held Oct 30, "too thin") with a real run: the reply on screen is the exact text Gemini returned on Nov 1, 2026.

- **Lane:** ai
- **Format:** fix-this (_shared/formats.md: 25 to 42 s, 60 to 100 words: the reply to fix, read it, the beat to guess, the rewrite word for word, the button)
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** the owner of a small residential cleaning company who answers quote requests between jobs, on a phone.
- **The one idea:** a free AI app drafts your quote reply in seconds; you add the price, cut extra questions, send. (18 words; said short: "every quote reply needs a price and one question")
- **Do this week (on screen, held):** the four-line prompt, word for word, on an ITEM GET card held 4 s or more.
- **Shape:** result first (0 to 3 s: the 11 pm request and the real reply already written, "Real reply, Gemini 3.6 Flash (API), Nov 1, 2026"; open loop "one thing's wrong") -> the reply to fix (the owner's usual lunch reply, EXAMPLE: "Hey, prices vary, give me a call.") -> the guess and why (no price, no question, so nothing to text back; the work order with two empty boxes) -> the stake (Jobber: 26% of cleaning businesses reply within an hour) -> the rewrite (paste their text into Gemini, free; the prompt held as the save card) -> the honest check, answering the loop at about 70% (it asked two questions, not one: cut one, add your price, send it yourself) -> button (every quote reply needs a price and one question; send it before your first job).
- **Cover line:** "11 pm quote. / Reply in 7 seconds." (plate; the run took 6.6 s, said as "under seven seconds")
- **Hook pattern:** result-first
- **Treatment:** copy-this
- **Example:** gemini-night-quote-reply
- **Music:** night
- **Metaphor:** a work order with two boxes, PRICE and QUESTION (a trade object every owner fills in): the usual reply leaves both empty, the fixed one ticks both. On screen for the guess beat and ticked again at the button.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** the real reply (run.json, word for word) on a phone card labelled "Real reply, Gemini 3.6 Flash (API), Nov 1, 2026"; Gemini's own plan page cropped to "Free, $0/ month with a Google Account" with its address "gemini.google/subscriptions"; the Gemini app's start screen with "Gemini is AI and can make mistakes." (gemini.google.com); Jobber's 26% on a gauge with its source tag.
- **Worlds (_shared/sets.md):** `chat` (the night request in the dash phone, cover), our own work order card (the metaphor), `gauge` (Jobber's 26%), the Gemini page shots on a phone frame, the ITEM GET prompt card, `levelup` (the button: PRICE and ONE QUESTION as perks). Not the lesson before's (missed-call-text: workbench, boss, register, scores).
- **End card send line:** "Send this to whoever answers your quote requests." (SCENE.sendLine)
- **Asked by owners:** thin, like the lessons before. Public search on Nov 1 returned owner-facing pages written this year on the same problem, not forum threads: "why am i losing house cleaning jobs to competitors just because i don't reply fast", https://skipcalls.com/cleaning-company/why-am-i-losing-house-cleaning-jobs-to-competitors-just-because-i-don-t-reply-fa ; "Cleaning Leads: Reply in 1 Hour to Win 7x in 2026", https://ustechautomations.com/resources/blog/why-cleaning-teams-stop-losing-leads-to-slow-followup-2026 (vendor pages, not evidence; the lesson's number is Jobber's). Reddit snapshots surfaced but were not read.
- **Model videos:** three read (see "Model video notes" below): qUo1OiaLCts, 0TBNBkU8__I, -keganwBIp8.
- **Trust notes:** The reply is Gemini's own text from one run (run.json), shown and read word for word in its quoted parts, labelled with the model and date; we never say it books jobs. "Under seven seconds" is the run's own measured 6.6 s of model time on GitHub's machine (tools/ai_demo.py, `seconds`); typing the prompt takes the owner longer, so the voice says the reply took that, not the whole job. The run went through Google's Gemini API, not the app, and answered as gemini-3.6-flash, so the card says "Real reply, Gemini 3.6 Flash (API), Nov 1, 2026". The free plan gives Flash-Lite (plan page, Nov 1), so an owner's reply in the free app will read differently; the captions say so. "Free" is the plan page's "$0/ month with a Google Account", read Nov 1. "It asked two questions" is checked against the reply itself. Jobber's 26% is a vendor survey of owners (1,050, December 2025, Conjointly), self-reported, said as Jobber's. The 11 pm request, the lunch reply and the 7 am time are ours, EXAMPLE on screen. No price is shown ([your price] stays a slot). Gemini's own line "Gemini is AI and can make mistakes." backs "send it yourself".

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| This reply took under seven seconds | run.json, seconds 6.6, Nov 1, 2026 | video/studio/demos/out/2026-11-14-ai-night-quote-4/run.json |
| The reply text on screen | same run.json, text | same |
| It asked about the oven and fridge, then what day: two questions | same run.json, text (two asks) against the prompt's "Ask one question" | same |
| Gemini is free | Gemini plans page, "Free ... $0/ month with a Google Account", shot Nov 1, 2026 | https://gemini.google/subscriptions/ |
| Twenty-six percent of cleaning businesses reply within an hour, Jobber says | Jobber, Blue Collar Strong: The 2026 Home Service Trends Report, read Oct 29, 2026 | https://www.getjobber.com/home-service-trends-report/ |
| The customer's text, the usual reply, 11 pm | ours (example story) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-14-ai-night-quote/01_voice/facts.json", "numbers": {
 "hourPct": {"path": "jobber.cleaningWithinHourPct", "shown": "26%"},
 "owners": {"path": "jobber.sampleOwners", "shown": "1,050"},
 "under": {"path": "demo.underSeven", "shown": "7"},
 "secs": {"path": "demo.seconds", "shown": "6.6"},
 "words": {"path": "demo.replyWords", "shown": "45"},
 "limit": {"path": "demo.promptWordLimit", "shown": "50"},
 "asked": {"path": "demo.questionsAsked", "shown": "2"},
 "wanted": {"path": "demo.questionsWanted", "shown": "1"},
 "free": {"path": "gemini.freePrice", "shown": "$0"},
 "night": {"path": "story.requestHour", "shown": "11"},
 "lunch": {"path": "story.lunchHour", "shown": "12"},
 "beds": {"path": "story.beds", "shown": "2"},
 "baths": {"path": "story.baths", "shown": "1"}
}}
```

## Model video notes
Watched Nov 1 with the watch-video skill (Gemini; view counts not readable here, so not ranked by views). (a) GNVLXwXVh5E failed (Gemini refused); first tries of (b) and (c) hit Gemini 503 and were retried.
1. https://www.youtube.com/shorts/qUo1OiaLCts (answer: video/watch/answers/2026-11-01-night-quote-b-r2.md): a 44 s talking head, "a customer texts at midnight, the AI books the job", then a vendor's auto-reply feature list. No prompt, no reply shown, nothing to check; every claim asserted. What we take: the midnight text is the moment owners feel; we show the real reply and the thing to check instead of asserting.
2. https://www.youtube.com/watch?v=0TBNBkU8__I (answer: ...-c-r2.md): an 11 minute ChatGPT walkthrough for cleaning owners, opening on the audience call-out, the finished posts shown at 01:25 before the how. What we take: the result before the how (our C5), without the call-out opening.
3. https://www.youtube.com/watch?v=-keganwBIp8 (answer: ...-d.md): a 16 minute vendor tutorial of an AI auto-reply inside a field service app, with a "Review Before Sending" setting and live test scenarios. What we take: review before sending is the setting even vendors ship; ours is "send it yourself".
Our words only; no line, shot or script taken.
