# Proven patterns (the proven idea lane's bank)

Todd, live chat, Nov 7, 2026, 11:58 am: "Can't we examine top performing videos on youtube shorts and make our own
variation? ... We can find what is actually working out there and create our own videos based on that."; 12:08 pm: "Go".
Rules for making a lesson from a row: _shared/formats.md "Proven". Ideas and formats aren't owned; words, footage and art
are. We take the pattern (topic, opening move, structure, length, what's on screen) and never a line, a shot or a script.

## How this bank was read (Nov 7, 2026, live chat, about 12:50 to 1:40 pm Central)
- Channels: 35 real YouTube channels found by 15 YouTube searches (trade business owners, home service marketing, AI for
  small business); 33 had a Shorts tab. For each, the newest 48 Shorts and their views from the public channel page.
- Typical views = the median of those 48. An outlier = 5x the median or more. Each row's exact views, length and date
  come from its own public watch page, read the same day.
- The bar (Todd, live chat, Nov 7, 2026, 7:17 pm: "1,225 is not viral and out bar of 1,000 is far too low. We need topics that are actually interesting. We need to change this standard to 100K+ views"; 7:20 pm: 100K+ and 5x): a proven lesson started from Nov 7, 7:17 pm takes only a row with 100,000 views or more AND 5x its channel's typical. `anim.py` reads the views column below and fails a brief under the bar; `anim.py nextlane` says story when no unused row at the bar has a sourceprint. At the bar: rows 1, 3, 4, 11, 12, 13, and rows 14 to 21 from the widened Nov 8 refresh (owner lessons from business channels, 641K to 3.3M views; sourceprint jobs queued Nov 8). Rows 2 and 7 were made before the bar (angi-four-pros, after-hours-greeting) and post as made, Todd's word.
- Kept (before the bar): business lessons a trade owner can act on, 1,000 views or more, not a paid ad. Dropped: a meme set to a trending
  song (_DSkrhfDvGk, 385,504 views, 67.6x), career advice off our topic (HSU189Hzedo, 16,651, 12.8x), and Housecall Pro's
  four TikTok outliers (23,600 to 185,700 views), which are paid free-trial ads.
- Read honestly: three rows come from small channels (typical 48 to 58 views), so their ratios are large on 1,000 to 4,400
  views. They show what an owner audience stops for, not reach we can expect.
- Route: Todd's Chrome, public pages only, read only, nothing signed into or changed. Not reachable: YouTube channel pages
  and feeds through web fetch (no view counts; the feed is closed to automated readers), TikTok profiles through web fetch
  (closed), Reddit through web fetch and through Chrome (both refused), the GEEKOM box (its lane was not attached to this
  chat). So this bank has no Reddit threads. A weekly refresh needs Chrome on Todd's PC (a PC-bound task) or a source of
  per-Short views a cloud run can read. Since Nov 7, 2:45 pm (Todd: "key added"): that source is the official
  YouTube Data API, run Sundays by .github/workflows/yt-outliers.yml into research/outliers.json (channels by ID in
  research/proven-channels.json), and transcripts come from watch-video jobs marked "sourceprint" (no words committed).
- Sourceprints: research/proven/<video id>.json holds salted hashes of the source's word runs, never its words; the copy
  check (`anim.py copycheck`) reads it. Made for rows 2, 4, 5 and 7 (whole text read in Chrome) and, the same day, rows 1, 3, 6, 8, 9 and 10 (watch-video sourceprint jobs, no words committed): all 10 rows can be built. A row without one can't be made
  until a run reads its whole transcript or on-screen text and runs `anim.py sourceprint`.

## Top 10 (views against the channel's typical; read Nov 7, 2026)

| # | Source | Views vs typical | Topic | Opening move | Structure | Length | On screen | Who an owner forwards it to | Print |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Roofing Insights, https://www.youtube.com/shorts/zQiyPFqazDg (Oct 20, 2026) | 10,000,039 vs 5,700 (1,754x); its sister skit 0Yq52oaZeio 624,905 (110x) | the homeowner who won't pay after the job is done | a one-line POV caption states the conflict before a word is said | staged skit: the job is done, the payment call, the refusal, the crew undoes the work | 91 s | live-action skit, big caption box over it | the partner who chases payments | yes |
| 2 | Phlash Consulting, https://www.youtube.com/shorts/O0BsFpqQ9uw (Oct 31, 2026) | 4,390 vs 48 (91x) | paying for leads, then missing the calls | an accusation about money the viewer already spends | claim, one shop's result, "no new ads, no new techs", the cause (missed calls), the fix (every missed, after-hours and weekend call answered), why it's urgent, the rule, a question back to the viewer | 5 s | one still social-post card over muted b-roll; the whole lesson is the card | whoever answers the phones, or the partner who pays for leads | yes |
| 3 | Roofing Insights, https://www.youtube.com/shorts/1xb3Cz8A74M (Oct 19, 2026) | 423,503 vs 5,700 (74x) | is it damage or not: the viewer judges | a question caption over raw job footage | footage only, no voice; the question asks the viewer to call it; the comments argue | 20 s | phone footage on a roof, one caption line | a tech or the estimator | yes |
| 4 | a plumbing shop owner's pricing channel, https://www.youtube.com/shorts/wHS7oI5Ld8I (Oct 19, 2026) | 376,578 vs 10,000 (37.7x) | memberships: get paid every month | a famous business's cheap price everyone knows | the famous fact, the hidden money model behind it, "if you're a plumber, do the same", the payoff line | 24 s | podcast clip, two-word punch captions | the partner or spouse who does the books | yes |
| 5 | Phlash Consulting, https://www.youtube.com/shorts/1nMFGmek1XM (Nov 1, 2026) | 1,620 vs 48 (33.8x) | reviews: hope versus a system | two numbers that don't match (revenue against review count) | the mismatch, the excuse owners give, the stakes (no reviews, no leads), a five-step system as a list, the rule | 5 s | one still social-post card | the techs, or the office manager | yes |
| 6 | Profitable Tradie, https://www.youtube.com/shorts/PozbgSSz4kU (Oct 24, 2026) | 1,170 vs 54 (21.7x) | price objections | one bold quote card over job b-roll | the line alone; the title asks owners what they say back, so the comments carry it | 7 s | panel wiring b-roll, one quote card | the partner who gives the quotes | yes |
| 7 | a one-person contractor marketing channel, https://www.youtube.com/shorts/P42-f-ouoSU (Oct 20, 2026) | 1,225 vs 58 (21.1x) | leads that come in after hours | a "quick question" naming three exact off-hours times | the question, the honest bad answer (nothing happens until Monday), a pointer to the longer video | 18 s | face to camera, title bar, burned-in captions | the office manager, or whoever answers the phones | yes |
| 8 | a plumbing education channel, https://www.youtube.com/shorts/7cOPDgfcSig (Nov 2, 2026) | 11K vs 1,100 (10x) | a cost that moved this month (diesel) | today's price and how far it moved in a year | the number, who says it stays high, what to plan or price in | 17 s | talking head, the number in a title box | the partner who sets prices | yes |
| 9 | a remodeling contractor's channel, https://www.youtube.com/shorts/ABKKpu8Z7c8 (Oct 13, 2025) | 8,186 vs 996 (8.2x) | how contractors should use AI now | an interview question | the question, practical uses (estimate from your last 10 jobs, ask what you might be forgetting), the caveat: don't take it as gospel | 86 s | interview two-shot, word-by-word captions | the estimator | yes |
| 10 | a plumbing shop owner's pricing channel, https://www.youtube.com/shorts/Ca8ppBrIOyI (Oct 26, 2026) | 62,383 vs 10,000 (6.2x) | your real hourly rate | a speed promise ("in under a minute") | whiteboard math, one step at a time, each step a number, ending on the rate to bill | 69 s | whiteboard, big numbers, captions | the partner who builds the price book | yes |
| 11 | Roofing Insights, https://www.youtube.com/shorts/Rw_tRgRvZHM (Oct 12, 2026) | 2,433,807 vs 8,356 (291x) | the customer who won't pay the junk crew | not yet read (sourceprint job queued Nov 7) | a skit | 25 s | skit footage | not yet read | no |
| 12 | Roofing Insights, https://www.youtube.com/shorts/_DSkrhfDvGk (Oct 29, 2026) | 385,578 vs 8,356 (46x) | five roofers, zero options | not yet read (sourceprint job queued Nov 7) | not yet read | 21 s | not yet read | not yet read | no |
| 13 | Roofing Insights, https://www.youtube.com/shorts/0Yq52oaZeio (Oct 23, 2026) | 626,319 vs 8,356 (75x) | job done, the homeowner won't pay (row 1's sister skit) | not yet read (sourceprint job queued Nov 7) | a skit | 103 s | skit footage | not yet read | no |
| 14 | a trades business coaching channel, https://www.youtube.com/shorts/MRg3bpv5tLI (2026-02-27) | 2,187,001 vs 68,736 (31.8x) | why good people leave a trades business | not yet read (sourceprint job queued Nov 8) | not yet read | 53 s | not yet read | not yet read | no |
| 15 | a trades business coaching channel, https://www.youtube.com/shorts/AS1Mw7crQQY (2026-02-27) | 2,113,425 vs 68,736 (30.7x) | the simple math most trades owners miss | not yet read (sourceprint job queued Nov 8) | not yet read | 54 s | not yet read | not yet read | no |
| 16 | a trades business coaching channel, https://www.youtube.com/shorts/JzWguJJSDqQ (2025-11-30) | 1,745,740 vs 68,736 (25.4x) | losing the profit on labour costs | not yet read (sourceprint job queued Nov 8) | not yet read | 111 s | not yet read | not yet read | no |
| 17 | a trades business coaching channel, https://www.youtube.com/shorts/jaAGHdXrJqI (2025-11-30) | 1,226,247 vs 68,736 (17.8x) | running a daycare, not a business (owner does everything) | not yet read (sourceprint job queued Nov 8) | not yet read | 82 s | not yet read | not yet read | no |
| 18 | a trades business coaching channel, https://www.youtube.com/shorts/wZPc6-WNsxE (2026-02-04) | 691,571 vs 68,736 (10.1x) | still working 70-hour weeks as the owner | not yet read (sourceprint job queued Nov 8) | not yet read | 73 s | not yet read | not yet read | no |
| 19 | a plumbing business channel, https://www.youtube.com/shorts/wkwQ8LyPSdA (2026-06-11) | 3,299,602 vs 68,736 (48.0x) | what a plumbing company is really worth when you sell | not yet read (sourceprint job queued Nov 8) | not yet read | 99 s | not yet read | not yet read | no |
| 20 | a trades business coaching channel, https://www.youtube.com/shorts/4O4EUb1NfbI (2026-06-11) | 1,566,432 vs 68,736 (22.8x) | AI tools for trades owners (AI lane) | not yet read (sourceprint job queued Nov 8) | not yet read | 87 s | not yet read | not yet read | no |
| 21 | a pressure washing business channel, https://www.youtube.com/shorts/jjtJQ-VUhtY (2026-07-20) | 640,992 vs 76,041 (8.4x) | what to do when clients don't pay | not yet read (sourceprint job queued Nov 8) | not yet read | 80 s | not yet read | not yet read | no |

Phone cluster: rows 2 and 7 (both under the 100K bar). At 100K+ and 5x but not owner lessons (left out): two electrician technique Shorts, RRRujPs1vFQ (384,877, 7x) and OyJgZZBaLSY (307,071, 5.6x), weekly refresh Nov 7.

## What the ten share (for the script)
- The opening names the viewer's money or the viewer's moment, never the topic ("You're paying for...", "What happens when
  someone calls at 7 pm on a Tuesday...").
- Five of ten are 24 s or under, and three are one still card or one line of text: the screenshot is the lesson. That is our
  send moment, already proven.
- Each one hands over one thing (a rule, a list, a number) and stops. None ends on a pitch.

## Made from this bank
| Date | Lesson | Row | Lane check |
|---|---|---|---|
| 2026-11-07 | 2026-11-21-angi-four-pros (Angi charges each lead when sent; up to 4 pros) | 2 | copy PASS: 0 shared 6-word runs, 0% of 3-word runs |
