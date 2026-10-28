# Brief: The text that revives a quote that went quiet

Lesson 2, segment The Text. Planned from the script playbook (research/runs/2026-10-28-script-playbook.md, example 1), Oct 28, 2026; every source re-opened and re-read the same day.

- **Where:** Instagram Reel (and TikTok, Facebook, YouTube Shorts), 9:16, about 70 to 80 s (the 75 s slot: a worked cadence earns it).
- **Audience:** a trades or home-service owner (plumber, HVAC, electrician, roofer) who left a quote at the kitchen table and hasn't heard back.
- **The one idea (12 words):** When a quote goes quiet, text one yes-or-no question about the job.
- **Shape:** hook (quote went quiet, don't send "just checking in") -> stakes (ServiceTitan: only 37% close on the first visit) -> why "just checking in" fails (it hands them homework; Dean Jackson's one-question method) -> the text, shown big on a phone -> the turn (keep it in your own words; the Management Science bot finding) -> when to send it (Jobber: within 2 days, a week, a day or two before expiry, then close the file) -> close (one name, one job, one question; send line).
- **Metaphor:** homework (a reply they have to write vs a yes or no). Drawn as a homework sheet once, then gone.
- **Voice:** Todd's clone in `_shared/voice.md` (eleven_v4).
- **Real screens:** the "just checking in" text on a phone, stamped; the revive text typed on a phone and held; the follow-up cadence as a timeline; the sources on screen as they are said.
- **Artifact (on screen):** `Hi [name], it's [you]. Still want that water heater swapped before winter?` Placeholders, no invented names.
- **Close:** "One name, one job, one question." Send line: "Send this to whoever follows up on your quotes." Exact text in the caption.
- **Trust notes:** ServiceTitan's 37% is vendor data, method not shown: voice and screen say it is ServiceTitan's own data. Never the same page's 64% / 72% / 87% (do-not-use list). The speed study is about first replies on Fiverr plus experiments, so the voice says "fast replies", not "follow-ups". Jobber is practice advice and is said as "Jobber says". Dean Jackson is a method, no numbers.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| "only thirty-seven percent of estimates close on the first visit" (ServiceTitan's data) | ServiceTitan blog, Follow-Ups 101: Back 2 Basics, Apr 17, 2026 | https://www.servicetitan.com/blog/webinar-recap-follow-ups-101-back-2-basics |
| "most of your quotes aren't decided... The rest ride on your follow-up" | Same page: "which leaves the majority of opportunities dependent on" follow-up (63% not closed on the first visit) | same |
| One short question about what they wanted, no pitch | Dean Jackson, The 9-Word Email, Jun 9, 2026 | https://deanjackson.com/blog/the-9-word-email/ |
| Fast replies stopped helping once people thought a bot wrote them | Speed Is a Signal, Management Science, 2026 (UCSD summary, Jun 25, 2026) | https://today.ucsd.edu/story/looking-for-work-dont-worry-about-seeming-too-eager |
| Within two days, a week after, a day or two before expiry; after three, close the file | Jobber Academy, Quote Follow-Up Email Templates, updated May 28, 2026 (advice) | https://getjobber.com/academy/quote-follow-up-email-templates/ |
| "It hands them homework" | our advice, not a finding | none |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-10-29-quote-revive/01_voice/facts.json", "numbers": {
 "closePct": {"path": "firstVisit.closeFirstVisitPct", "shown": "37%"},
 "stYear": {"path": "firstVisit.year", "shown": "2026"},
 "studyYear": {"path": "speedStudy.year", "shown": "2026"},
 "firstDays": {"path": "cadence.firstWithinDays", "shown": "2 days"},
 "secondDays": {"path": "cadence.secondAfterDays", "shown": "Day 7"},
 "finalMin": {"path": "cadence.finalBeforeExpiryDaysMin", "shown": "1"},
 "finalMax": {"path": "cadence.finalBeforeExpiryDaysMax", "shown": "2 days"},
 "followUps": {"path": "cadence.followUps", "shown": "3"}
}}
```
