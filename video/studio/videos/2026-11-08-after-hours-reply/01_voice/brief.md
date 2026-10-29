# Brief: The after-hours quote request

AI lead-handling lane, lesson 1 of 3 (Todd, Oct 29, 2026, 3:56 pm: "Yes, please do. Go with your recommendations for everything.";
coo/DECISIONS-2026-10-29.md). Cleaning owners first. Segment Lead Clinic.

- **Format:** v2 (Lead Clinic v2, `_shared/voice.md`: 40 to 50 s with the end card, 100 to 135 words).
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** the owner of a residential cleaning company (5 to 25 staff) who answers quote requests between jobs.
- **The one idea:** an AI chat app drafts the night quote reply; you read and send it.
- **Shape:** drop-in (a move-out clean quote request came in at eleven last night; you see it at seven) -> play it out (you start typing between jobs, rates, size, what's included; by lunch it's still a draft and they booked someone else) -> the fix (paste their message into an AI chat app with a three-line prompt, on screen as said; the drafted reply appears, marked example; you read it, fix it, send it yourself) -> proof (Jobber: 26% of cleaning businesses reply to leads within an hour, the fastest of any trade) -> button (nobody needs you up at eleven; the night quote should have your answer before your first job).
- **Hook pattern:** stuck-moment
- **Treatment:** copy-this
- **Example:** ai-after-hours-reply
- **Metaphor:** none. The night phone on the nightstand and the morning alarm carry it.
- **Voice:** Todd's clone in `_shared/voice.md`.
- **Real screens:** the customer's message in a messaging app (example); an AI chat app window (unbranded, marked example) with the prompt typed on as it is said and the drafted reply; the Jobber number on a gauge with its source tag; today's board.
- **End card send line:** "Send this to whoever answers quote requests." (SCENE.sendLine)

Trust notes: Jobber's numbers are vendor survey data, said as Jobber's. The 26% is the share of cleaning businesses that say they reply to leads within an hour, from Jobber's survey of 1,050 US home service business owners (Conjointly, December 2025, plus or minus 3 points at 90% confidence); the page does not give the cleaning subsample size. "The fastest trade" is the page's own "Cleaning businesses are the fastest responders". Descriptive survey, not a correlation, so no "Pattern, not proof." tag; the tag names the survey and its window. The 11 pm and 7 am times, the customer's message (move-out clean, two bed, one bath, before Friday), the prompt and the drafted reply are examples, shown with "EXAMPLE" on screen; we never say PNF or anyone used them on a real customer or that a tool produced a result. The owner reads, fixes and sends every reply; nothing goes to a customer by itself. No AI product is named or shown (an AI chat app). "They booked someone else" is the story's cost, acted, not a finding. The prompt asks for the owner's own rates; no price is shown (the draft says "[your rate]"). No texting rule is taught.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| "Only twenty-six percent of cleaning businesses reply to a lead within an hour. And they're the fastest trade." Page: "Cleaning businesses are the fastest responders (26% reply within an hour), while HVAC pros are the slowest." Survey of 1,050 home service business owners across the United States, conducted through Conjointly in December 2025, margin of error plus or minus 3 percentage points at the 90% confidence level | Jobber, "Blue Collar Strong: The 2026 Home Service Trends Report" (page modified Mar 25, 2026; re-read Oct 29, 2026) | https://www.getjobber.com/home-service-trends-report/ |
| The prompt: "Write a short, friendly reply to this cleaning quote request. Use my rates below. Ask one question if anything's missing." | ours (advice, an example prompt) | n/a |
| The drafted reply and the customer's message | ours (example story, not data) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-08-after-hours-reply/01_voice/facts.json", "numbers": {
 "hourPct": {"path": "jobber.cleaningWithinHourPct", "shown": "26%"},
 "owners": {"path": "jobber.sampleOwners", "shown": "1,050"},
 "surveyYear": {"path": "jobber.fieldworkYear", "shown": "2025"},
 "reportYear": {"path": "jobber.reportYear", "shown": "2026"},
 "nightHour": {"path": "story.requestHour", "shown": "11"},
 "morningHour": {"path": "story.seenHour", "shown": "7"},
 "beds": {"path": "story.beds", "shown": "2"},
 "baths": {"path": "story.baths", "shown": "1"},
 "promptLines": {"path": "prompt.lines", "shown": "3"}
}}
```
