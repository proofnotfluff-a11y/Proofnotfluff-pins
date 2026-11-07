# trade-pulse (desk 1, listening: what trade owners are saying now, and what the AI-for-trades teachers teach)

Todd, live chat, Nov 2, 2026, 8:49 pm (video/studio/PRINCIPLES.md): "What are people talking about right now? What problems
can we help solve? ... Look to the gurus in this space and see how we can distill this information into something useful
for trades owners." Built Nov 5, 2026 (video/studio/REBUILD.md, build run). Feeds story-desk; never makes a video itself.

## Inputs (Reads)
- video/studio/PRINCIPLES.md, video/studio/REBUILD.md, the last pulse (video/studio/research/pulse/), research/gurus.md,
  research/STORIES.md (so a story already made or killed is marked, not re-proposed).
- The web through WebSearch and WebFetch only. Where to listen, in this order:
  1. Owner forums: ContractorTalk, Plumbing Zone, Electrician Talk, HVAC-Talk; vendor communities (Jobber, ServiceTitan,
     Housecall Pro, Google Ads community for Local Services Ads).
  2. Reddit trade subs (r/HVAC, r/Plumbing, r/electricians, r/Roofing, r/Contractor, r/sweatystartup, r/CleaningBusiness,
     r/pestcontrol, r/smallbusiness) only where a thread page opens through WebFetch. Refused: say so and move on; never a
     mirror, cache, curl or scraper (Reddit blocks automated readers without an agreement).
  3. Trade press, last 60 days: ACHR News, Contractor, PHC News, Plumbing & Mechanical, Roofing Contractor, Remodeling, EC&M.
  4. YouTube comments under AI-for-trades videos, where a page shows them; the gurus in research/gurus.md.

## Process (Executes)
1. Date from bash (`TZ=America/Chicago date`). Read the last pulse so the new one reports what changed.
2. Read wide: 25 to 40 pages opened, newest first, last 90 days (older only when it is still the live complaint).
   Box first (Nov 7, Todd: the box is the workhorse): when research/pulse/night-<yesterday>.json exists
   (tools/pulse_merge.py), its items replace steps 2 and 3; read yourself only to fill a trade it missed.
3. Extract each item: the problem in an owner's plain words (our paraphrase, at most 10 quoted words), the trade, the URL
   opened, the date, the place (forum, sub, publication). Never a person's name or username, never a small business's name.
   Local first pass (Local AI architecture doc, routing table: "trade-pulse ... Local reads forums and comments, extracts
   problems in owners' words"): the box reads the pages itself (Nov 6): one `extract` job per 5 to 8 page URLs, with
   urls in place of input (`python3 tools/local_job.py fetch <job> --wait`; model fast; allowed sites: the reader's list,
   no Reddit or YouTube; a page it can't read comes back with its status, and you open only those yourself; schema: items with problem, trade, quote_under_10_words,
   url, plus unplaced: the ids of items it left out; each why is one whole sentence, up to 300 characters, never cut off;
   Nov 6 fix). From Nov 5, 2026 this job is in shadow mode: do the extraction yourself as well, compare, and log the difference
   rate in research/pulse/<date>.md "Local shadow". After 3 clean pulses it moves to local first (_shared/local.md). No answer
   in 15 minutes or a status other than ok: do it on Claude and note it.
4. Group into problems and rank them by: how many separate threads (a problem in 3+ places beats a loud single thread),
   how fresh, and how much money or time it moves for an owner this month.
5. For the top 3 problems, check the record: is there a document behind it (a vendor's pricing or terms page, a rule, a
   policy page, an earnings call)? Name it with its URL as a story lead for story-desk.
6. Verify every item you keep: the URL opens and says what the line says. An item that fails is cut, never softened.
7. Write video/studio/research/pulse/<YYYY-MM-DD>.md (template below) and one line in research/LOG.md.

## Outputs (Writes)
```
# Trade pulse, <date>
Pages opened: n. Refused or unreadable: <list>.
## What changed since the last pulse
## Top problems (ranked)
### 1. <the problem in an owner's words>
- Threads: n | trades: <list> | why money moves this month: <one line>
- <URL> | <date> | <place> | <what it says, paraphrased>
## Story leads (for story-desk)
1. <the document behind a problem> | <URL> | <the one surprising sentence>
## Local shadow
- job <name>: status, seconds; items local n, Claude n, matched n; difference rate n%; items unplaced and not listed n
```
- Never: a person's name or username, a small business's name, a quote over 10 words, a claim no opened page supports,
  a post, comment, sign-up or log-in anywhere.
