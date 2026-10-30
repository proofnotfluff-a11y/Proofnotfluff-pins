# Brief: Google now bills you for calls you miss

Depth bank #1 (research/IDEAS.md; research/topics-2026-10-30.md, lesson 1), planned Oct 30, 2026 in the scheduled make
run. Source re-read Oct 30, 2026 (Central): Google's "How leads work - Local Services Help" (answer 7195435), every line
in facts.json found on the page that day.

- **Format:** two-shops (_shared/formats.md: 35 to 52 s, 85 to 125 words; same call to two shops, each path step by step
  on a split screen, the scoreboard, the one difference in one line).
- **Where:** Instagram Reel, 9:16, then TikTok, Facebook, YouTube Shorts.
- **Audience:** a home service owner (plumber, HVAC, electrician) who runs Google Local Services Ads and misses calls on jobs.
- **The one idea:** run your Local Services ads only in the hours someone answers the phone. (14 words)
- **Do this week (on screen, held):** 1. Ad schedule: only the hours a person answers. 2. Missed rings go to a second
  phone. 3. Text back every missed call. 4. Fridays: Leads page, Charge Status.
- **Shape:** drop-in (7 pm, the same call to two shops, nobody picks up) -> shop one (ads on till 9, the caller waits
  into voicemail: a charged lead, you paid for a ringing phone) -> shop two (ads only while a person answers, schedule
  ends at 5, so that missed call is not charged; daytime misses roll to a second phone) -> text back and Fridays (every
  missed call gets a text back, follow-ups within 15 days are not charged again; check the Charge Status column) ->
  proof (Google's help page: past 20 seconds in your hours, even voicemail counts; source tag on screen) -> scoreboard
  (shop one 1 charged lead, shop two 0) -> button ("Same call. Run the ads only when somebody picks up.").
- **Hook pattern:** two-shops
- **Treatment:** steps
- **Example:** lsa-two-shops-7pm
- **Music:** chase (free next to its neighbours in line; `anim.py tunes`)
- **Metaphor:** none. The two lit shop windows on one street carry it.
- **Voice:** Todd's own voice clone in `_shared/voice.md` (Eleven v4).
- **Real screens:** the Charge Status column's four statuses as Google's page names them (Charged, Not charged, In review,
  Credited) on a departures board; the rule's source tag "Google Local Services Help: How leads work".
- **Worlds (_shared/sets.md):** our own split-screen street at night (two shopfronts, a phone ringing in each window,
  a 20 s ring bar), `gauge` (the twenty-second line), `chat` (the text back), `flaps` (the charge statuses), `versus`
  (the scoreboard). None used by the two lessons before it (notes-to-quote: street, inventory, levelup;
  receptionist-myth: calendar, scores, boss).
- **End card send line:** "Send this to whoever pays for your Google ads." (SCENE.sendLine; no recent lesson names this role)
- **Asked by owners:** thin. No owner forum thread from the last 90 days was found on public pages (Reddit was refused
  in the Oct 30 research run; Local Search Forum's LSA threads found were from 2024). Signs that the trades are asking:
  The Pool Deck (Skimmer's community for pool service owners), "Google Will Now Charge for Missed LSA Calls: What Pool
  Companies Must Fix Before October 1", Aug 25, 2026, https://thepooldeck.getskimmer.com/news-trends-training-3/google-will-now-charge-for-missed-lsa-calls-what-pool-companies-must-fix-before-october-1-1391 ;
  Whitespark on YouTube, "Google Local Services Ads Charging for Missed Calls!", Aug 25, 2026,
  https://www.youtube.com/watch?v=LTOjxO-8GQg ; Mike Vidan (QuoteIQ), "Google Killed Local Service Ads - What Every
  Contractor Needs to Know (September 2026)", Sep 15, 2026, https://www.youtube.com/watch?v=8GtdLfDiXyQ .
- **Niche check:** view counts were not readable (YouTube's bot page). Whitespark (Aug 25) opens on the alarm ("charging
  for leads even when you don't pick up") and urges answering every call; Marketing by Data (Feb 24, 2026) teaches that
  manual disputes are gone and lead ratings train the system; Mike Vidan (Sep 15) is a migration checklist. Ours differs:
  one call acted out at two shops side by side, and the setting that decides it (the ad schedule against who answers),
  plus the weekly Charge Status check, with no "dispute" promise (the page says Google may credit, not must).
- **Trust notes:** "charged" only for a missed call in business hours and the active ad schedule with the caller on the
  line more than 20 seconds (said as "waits it out" and "past twenty seconds in your hours"). Voicemail in your hours
  counts too (the page). The ad schedule line is the page's FAQ (both the ad schedule and the business hours). Forwarding
  to a second phone and the text back are our advice, never "Google says"; the 15-day line is the page's (follow-ups on a
  charged lead are not charged again). No start date said (the page gives none). No dollar cost per lead (none sourced).
  Two shops, 7 pm, 9 and 5 are our example (EXAMPLE on screen).

## Claims and their sources
| Claim, as said | Source | URL |
|---|---|---|
| A missed call in your business hours is charged when the caller stays on the line more than 20 seconds | Google, How leads work (Local Services Help), re-read Oct 30, 2026 | https://support.google.com/localservices/answer/7195435 |
| A call that goes to voicemail in your business hours is treated as connected and charged past 20 seconds | same | same |
| Missed calls are charged only within both your active ad schedule and your business hours | same (FAQ, business hours and ad schedule) | same |
| Follow-up calls or messages on a charged lead are not charged again within 15 days | same | same |
| The Charge Status column on the Leads page shows Charged, Not charged, In review or Credited | same | same |
| Two shops, a 7 pm call, ads till 9 and till 5; shop one 1 charged lead, shop two 0 | ours (example, labeled) | n/a |
| Missed rings to a second phone; text back every missed call | ours (advice built on the page's rules) | n/a |

## Numbers on screen

```json numbers
{"file": "video/studio/videos/2026-11-11-lsa-missed-calls/01_voice/facts.json", "numbers": {
 "secs": {"path": "google.missedSeconds", "shown": "20"},
 "days": {"path": "google.followUpDays", "shown": "15"},
 "callAt": {"path": "example.callHour", "shown": "7 PM"},
 "oneUntil": {"path": "example.shopOneUntil", "shown": "9 PM"},
 "twoUntil": {"path": "example.shopTwoUntil", "shown": "5 PM"},
 "oneCharged": {"path": "example.shopOneCharged", "shown": "1"},
 "twoCharged": {"path": "example.shopTwoCharged", "shown": "0"},
 "steps": {"path": "example.stepCount", "shown": "4"}
}}
```
