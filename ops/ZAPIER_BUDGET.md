# Zapier task budget

Written by the nightly optimizer, Sat Oct 17, 2026, after the 4:10 pm promote lost both pins to "Task limits for this account have been reached" and a probe at 9:15 pm got the same reply. Every cloud reach channel except Typefully (X, LinkedIn) runs through Zapier, so while the limit holds the crew has no YouTube, Instagram, TikTok, Pinterest or ElevenLabs.

## Facts (checked Oct 17, 2026)

- Each successful Zapier MCP tool call uses 2 tasks; failed calls use none; listing tools, auth and setup do not count; reads that query an app (search, API GET) do count. When the limit is reached, calls stop "until your billing cycle resets" unless pay-per-task billing is on. Source: https://docs.zapier.com/mcp/overview/usage
- Free plan: 100 tasks a month. Paid plans start at $19.99 a month (Professional) with task tiers chosen at checkout; pay-per-task overage exists on paid plans at a higher per-task rate. Source: https://zapier.com/pricing
- The account's plan, current usage and reset date are visible only in Todd's Zapier dashboard (Plan Tasks counter); no cloud run can read them.

## What the crew spends (calls a day, from the prompts and the Oct 15 to 17 logs)

| run | Zapier calls | tasks |
|---|---|---|
| CMO, ElevenLabs narration (one clip per spoken line, about 9 a video) | 9 | 18 |
| Morning promote: 3 pins, YouTube upload, Reel, TikTok via Buffer | 6 | 12 |
| Afternoon promote: 2 pins (no pm video under the one-video cut) | 2 | 4 |
| Short views refresh (tools/short_views.py, one GET for up to 50 Shorts) | 1 | 2 |
| Total, a normal day | 18 | 36 |

About 36 tasks a day is about 1,080 a month, before live sessions, Gemini red-team rounds, Kit or Sheets calls. A plan under about 1,200 tasks a month runs out before the month does.

## Value per task (scoreboard, Oct 6 to 17)

- Pinterest: 0 outbound clicks across the logged windows (144, 88 and 97 impressions). 10 tasks a day, the second-biggest spend, no clicks yet.
- YouTube Shorts: Proof Check #1 50 views, #2 8, #3 0 at last read; old-format peaks 1,001, 902, 717. The only channel with measurable reach.
- Instagram Reels: 0 likes, 0 comments, 0 followers on 21+ Reels (Oct 15 baseline).
- Etsy visits: 0 on Oct 16 and 0 on Oct 17 final reads.

## Rule for every run that calls Zapier (optimizer proposal; pins stay under Todd's weekly pick until he says otherwise)

1. Make the run's most valuable Zapier call first. A failed call is free, so it doubles as the probe.
2. If any call returns "Task limits for this account have been reached": stop every Zapier call for the rest of the run, never retry, never loop. Write scoreboard meta/shop.zapier {status:"limit", since, lastProbe, by}. Finish the parts that need no Zapier (specs, renders without narration stay unpublished, Typefully drafts, repo work) and say "Zapier task limit" in lastNote with status "partial".
3. A later run reads meta/shop.zapier first. While status is "limit" it makes exactly one probe call (its most valuable one); on success it sets status "ok" and goes on, on failure it follows step 2.
4. Order of spend when tasks are short (highest first): YouTube upload of an approved Short; its ElevenLabs narration; Instagram Reel; TikTok via Buffer; Short views refresh (at most once a day); pins; Gemini red team; anything else.
5. Never publish a narrated video in the Kokoro voice to save tasks (cmo/CONTENT_PLAYBOOK.md section 9 still holds): a video blocked by the limit waits, and the CMO carries its approved slate forward.

## Todd's decision (quest zapier-task-limit)

Check the Plan Tasks counter and reset date in the Zapier dashboard, then pick one: wait for the reset (reach is off until then); move to a paid tier that covers about 1,200 tasks a month (money, his call); or keep the plan and cut the pins (10 tasks a day, 0 clicks so far), which brings a normal day to about 26 tasks.
