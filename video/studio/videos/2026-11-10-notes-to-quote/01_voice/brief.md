# Brief: Walkthrough notes to a quote

AI lead-handling lane, lesson 3 of 3 (Todd, Oct 29, 2026, 3:56 pm: "Yes, please do. Go with your recommendations for everything.";
coo/DECISIONS-2026-10-29.md). Cleaning owners first. Segment Quote Clinic.

- **Format:** v2 (Lead Clinic v2, `_shared/voice.md`: 40 to 50 s with the end card, 100 to 135 words).
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** the owner of a residential cleaning company (5 to 25 staff) who walks a home before quoting a deep clean.
- **The one idea:** an AI chat app turns walkthrough notes into a quote; you check every price.
- **Shape:** drop-in (the finished deep clean quote on screen first: it started as messy walkthrough notes) -> play it out (the notes sit in your car all day; you rebuild the quote at night from memory and forget the inside of the oven) -> the fix (paste the notes into an AI chat app with a three-line prompt, on screen as said; the notes turn into itemized lines; you check every line against your own rates before it goes anywhere) -> proof (Jobber's survey of 1,050 home service owners: of those who use AI, 54% use it for quoting) -> button (the AI just does the typing; you own the prices, so every quote still starts with your notes).
- **Hook pattern:** result-first
- **Treatment:** before-after
- **Example:** ai-notes-to-quote
- **Metaphor:** none. Before and after on one page: scribbles on the left, clean lines on the right.
- **Voice:** Todd's clone in `_shared/voice.md`.
- **Real screens:** the finished quote (example, items only, price column left to the owner's own list, no figure shown); the walkthrough notes (example); an AI chat app window (unbranded, marked example) with the prompt typed on as said; the Jobber number on a tool belt stat with its source tag.
- **End card send line:** "Send this to whoever writes your quotes." (SCENE.sendLine)

Trust notes: Jobber's numbers are vendor survey data, said as Jobber's. The page: "For those who've already adopted AI, usage is practical and task-focused: 54% use it for quoting, 52% for invoicing, and 51% for business writing" (base: owners who use AI; the chart caption says "among home service businesses", so we say "of the ones who use AI", the body text's base). Survey of 1,050 US home service business owners, Conjointly, December 2025, plus or minus 3 points at 90% confidence. Descriptive, not a correlation; no "Pattern, not proof." tag. Not cleaning-specific: said "home service owners". The quote, the notes, the items and the prompt are examples, shown with "EXAMPLE"; no prices are shown (the price column is the owner's own list, drawn as blank bars with "your rate"). We never say PNF used this on a real customer or that a tool produced a result. The owner checks every line and sends it. No AI product is named (an AI chat app). "Forget the inside of the oven" is the story's cost, acted, not a finding.

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| "Jobber surveyed over a thousand home service owners. Of the ones who use AI, fifty-four percent use it for quoting." Page: "52% of blue collar business owners now use AI in their day-to-day operations"; "For those who've already adopted AI, usage is practical and task-focused: 54% use it for quoting, 52% for invoicing, and 51% for business writing."; a survey of 1,050 home service business owners across the United States, conducted through Conjointly in December 2025 | Jobber, "Blue Collar Strong: The 2026 Home Service Trends Report" (page modified Mar 25, 2026; re-read Oct 29, 2026) | https://www.getjobber.com/home-service-trends-report/ |
| The prompt: "Turn these notes into an itemized quote. Use only my price list. Flag anything I didn't price." | ours (advice, an example prompt) | n/a |
| The notes and the quote lines | ours (example story, not data) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-10-notes-to-quote/01_voice/facts.json", "numbers": {
 "quotingPct": {"path": "jobber.quotingAmongAiUsersPct", "shown": "54%"},
 "owners": {"path": "jobber.sampleOwners", "shown": "1,050"},
 "surveyYear": {"path": "jobber.fieldworkYear", "shown": "2025"},
 "reportYear": {"path": "jobber.reportYear", "shown": "2026"},
 "promptLines": {"path": "prompt.lines", "shown": "3"},
 "beds": {"path": "story.beds", "shown": "3"},
 "baths": {"path": "story.baths", "shown": "2"}
}}
```
