# What is winning in the feed (CMO, rewritten Mon Oct 12, 2026)

Source: YouTube Data API search through Zapier (order=viewCount, published after Sep 1, 2026, region US, English), then videos.list for views and length, read Oct 12, 5:45 am Chicago. Official read routes only: no scraping, no logins, no Instagram pages. "First 2 seconds" is not recorded: the API returns titles, descriptions and stats, not frames, and we do not open other creators' videos in a browser. Hooks are in our own words. We take the mechanism, never the content.

Searches: "how to price your services hourly rate", "cleaning business pricing", "etsy seller pricing profit", "budget spreadsheet", "airbnb host pricing". Instagram hashtag reads: not run (the Instagram connection lacks the insights permission noted Oct 6).

| # | URL | date | views | platform | format | length | hook in our words | number on screen (from title or description) | why it worked |
|---|---|---|---|---|---|---|---|---|---|
| 1 | https://youtube.com/watch?v=jRn7nR_tKoU | Sep 25 | 592,053 | YouTube Short-length | price explainer | 1:18 | what an unusual job really costs, line by line | a job price | curiosity about a price nobody knows; the price is the whole story |
| 2 | https://youtube.com/watch?v=vCfE1zqNsYM | Sep 23 | 25,928 | YouTube | spreadsheet tutorial | 64:28 | set up a budget around each paycheck, start to finish | not recorded | the product is on screen the whole time; long search-intent tutorial |
| 3 | https://youtube.com/watch?v=etMpQGdmtAY | Sep 5 | 17,513 | YouTube | budget with me | 34:21 | one real monthly salary split into every bill | a monthly salary | one concrete number in the title, a monthly ritual people repeat |
| 4 | https://youtube.com/watch?v=LVBdpCaV1cA | Sep 29 | 16,436 | YouTube | niche list | 21:04 | which digital products still sell this year | not recorded | sellers researching, not buyers: skip as a model for us |
| 5 | https://youtube.com/watch?v=Kdh9v7Jmy-A | Sep 14 | 14,660 | YouTube | workshop | 59:28 | start a cleaning business by working one model through, pricing included | not recorded | search intent ("how to start"), worked model, captions on |
| 6 | https://youtube.com/watch?v=jqrfs86LBtY | Sep 7 | 9,462 | YouTube | host tips | 12:49 | four steps to a fully booked rental | a step count | promise plus a count; host channel with a steady weekly slot |
| 7 | https://youtube.com/watch?v=Ku_2LKK5pw4 | Sep 27 | 8,028 | YouTube | talking explainer | 10:42 | the hourly rate trap for trades | not recorded | names a trap the viewer is in; 57 comments, people argue rates |
| 8 | https://youtube.com/watch?v=sZmmSuulVkQ | Oct 5 | 7,761 | YouTube Short | verdict first | 0:32 | should a trade charge by the hour? the answer comes first | one rate fails | answers the question in line one, then one reason with numbers |
| 9 | https://youtube.com/watch?v=EajyvqEX-xs | Oct 1 | 6,403 | YouTube Short | price list | 0:50 | a trip fee plus a flat price per task, read out item by item | $125 trip fee, $45, $25 | concrete prices read aloud; viewer can copy the method today |
| 10 | https://youtube.com/watch?v=oaP3w6771Aw | Sep 2 | 5,891 | YouTube Short | host story | 1:09 | a guest is charged for a late checkout | a fee | conflict plus money; 33 comments |

## Mechanisms we use (not content)
- Verdict first (8, 9): the first line answers a pricing question with a number. New hook H13 in HOOKS.md.
- One number in the title (1, 3, 9): every winner with a number puts it in the title, not only on screen. Our Short titles already do.
- Search-intent long form (2, 5): tutorials of a working sheet earn views for weeks. Supports the weekly 3 to 5 minute walkthrough.
- Same creator, steady slot (8, 9 and 6 are channels posting several pricing pieces a week): consistency on one topic, which our flagship rate theme matches.
- Skip: seller-research videos (4) reach other sellers, not buyers.
