# Content playbook: how ProofNotFluff makes short videos that win (from Oct 16, 2026)

Todd, Oct 15: "go with your recommendation. The key is to use your research to develop your skills and make winning social media content." This file binds the CMO and both promote runs. Read it every run, right after cmo/CONVERSION_STANDARD.md; where they differ, this file wins for videos. The evidence and sources are in reports/Short video formulas small business niche.md (Oct 15 deep research). Safety rules still sit on top: VERIFY BEFORE POSTING, no invented people, no em dashes, no banned words, no engagement bait, no AI people or faces.

## 1. What we learned (the why)
- At 0 followers every view comes from strangers. Instagram ranks those on watch time and **sends per reach** (Mosseri, Jan 2025); it measures the first 3 seconds (Skip Rate, Aug 2025). YouTube Shorts tests each Short on a small seed audience and widens it only if few swipe away.
- Our first 21 Reels got 0 likes because they were one video repeated: the same "$X looks fine, break-even is $Y" frame, the same $60,000 example, the same trade niches. YouTube's July 2025 policy names "slideshows that all have the same narration". Sameness is the failure, not the missing face or the posting volume (we already post above Buffer's best band).
- What grows in adjacent niches: a **visible stake resolved by a number** (trades transformation channels), and **one recognisable format repeated daily with fresh content inside** (Miss Excel). The format is the brand.
- Video's job is trust, follows and free-calculator visits. $2.99 sales mostly come from Etsy search and Pinterest; at a 1 to 3% Etsy conversion one sale needs about 33 to 100 listing visits.
- No realistic AI avatar: no free option runs on our stack, Instagram limits unlabeled AI-person profiles (Aug 31, 2026), AI labels lower engagement (MSI study), and YouTube will not monetize AI personas on finance topics (Jul 2026). A drawn, clearly non-human device is allowed later if Todd wants a persona.

## 2. The series: PROOF CHECK
Every video is one episode of **Proof Check**: the kicker line (spec "audience") reads `PROOF CHECK #<n> · <FORMULA NAME>` (for example `PROOF CHECK #3 · SPOT THE MISTAKE`; the reviewed examples predate the numbering, so their kickers carry no #n). n counts every Proof Check video published, kept in meta/shop.cmo.proofCheckNo (the CMO adds 1 per approved slate video; the first is #1 on Oct 16). Same kicker, same sting, same look family; different formula, numbers and topic every time.

## 3. The four formulas
Rotate them. Never the same formula twice in a row on a platform; never the same headline number twice in 14 days (check promo/ and shorts/). Weekly mix: about 4 Job Tickets or Spot the Mistakes on the flagships (am), and 3 broad pieces (pm: Myth vs Math or Spot the Mistake on #30, #29, #16 or #20 framed broadly). Worked, reviewed examples live in promo/specs/examples/ (rendered Oct 15, cold-viewer PASS).

**F1 Job Ticket** (example: f1-job-ticket-house-wash.json). One specific job priced line by line until the truth appears. "Say you quote $355 to soft wash a 2-story house. Here is where it goes." Rows are the job's real cost lines from the product's Quote Builder (time on site at the break-even rate, drive time, vehicle, supplies), then the break-even (result), then the fix: what is left at the quoted price, or the price that works. Headline may carry the payoff number. Best for #22, #23, #13, #14, #12. Sendable to "the person in your trade who quotes too low".

**F2 Spot the Mistake** (example: f2-spot-the-mistake-40-rate.json). A quote, rate or budget with one hidden error. Show the tempting math, ask "Spot the mistake?" with a held beat (row fields `"ask"` and `"pause": 1.2 to 1.5`), then name the mistake in the next spoken line ("The mistake: clients only pay for 1,152 of them") and reveal the real number. **The headline carries the setup, never the answer's explanation** ("$40 an hour. One mistake. You keep $15.66" works because the mistake itself is still hidden). There must be exactly one mistake: one thing the tempting math left out (the second crew member, or the drive), never two bundled into one line; tax and costs that follow it are named as a separate step.

**F3 Myth vs Math** (example: f3-myth-vs-math-takeout.json). One belief people repeat ("takeout wrecks the budget", "$50 an hour is plenty", "charge 3x your costs", "minimum payments are fine"), then one line of arithmetic from the product's example. **The headline states the belief and a setup number, never the answer** ("5 takeout orders: $214. Guilty?"); the `ask` beat poses the myth as a question; the reveal answers it. Name the items behind every total ("four grocery runs and one clothes order"), and say exactly what a percent is a share of. Built to be sent ("send this to whoever blames your takeout").

**F4 Run Your Numbers** (about one in four broad pieces). The free calculator filled in for one realistic case, ending on the result and the free page. Until tools/record_page.py exists (backlog below), render it with make_demo using the free page's inputs and outputs (they use the same maths as the workbook; source each number from the page's own calculation and the workbook) and say "free calculator" in the hook.

The old "$X looks fine, break-even is $Y" line may appear at most once a week, and only inside a Job Ticket.

## 4. Craft rules for every video (make_demo short format)
1. **Frame one**: the headline leads with one setup number (F1 and F2 may add the payoff number, as their reviewed examples do), readable at a glance, and the voice from 0.0 s. hook_say_short at most about 6 words and spoken by 3.0 s (make_demo prints hook_spoken_to; over 3.0 fails review).
2. **One claim, one takeaway.** Every line follows from the line before. A cold viewer must be able to redo the arithmetic from what is on screen or spoken.
3. **Labels and narration say the same thing.** If the label says "pay, tax, overhead", the voice says it too. Show the rate that produced a derived number (for example "3 hrs on site (at $64.89 an hour)").
4. **Plain words, defined terms.** No "the big five" without naming the five. "47% of everyday spending", never "47% of the month" when the sheet says everyday spending.
5. **Second person, worked examples.** "Say you quote...", "You charge...". Never a named customer, never "a client of mine" (no invented people).
6. **Length 28 to 40 seconds**, 4 to 6 rows plus at most one ask beat and one fix. Instagram's best median-views buckets run longer than 30 s and TikTok's run 16 to 30 s; until we can render two cuts, one 30 to 40 s cut serves both. Backlog: a --cut reel variant at 40 to 55 s.
7. **Sound**: rotating library bed by mood, the sonic logo fixed, master -14 LUFS (make_demo does this).
8. **One CTA, spoken once at the end:** "<verb> free at ProofNotFluff dot com." (for example "Price your own job free at ProofNotFluff dot com."). The end card shows it as proofnotfluff.com, cta.button "Free calculator", cta.sub "proofnotfluff.com", cta.what "Free online. Full workbook $2.99 on Etsy". This replaces the "Search ProofNotFluff for the free ... and the full workbook" close.
9. **Captions:** Reel caption tells the whole worked example in 2 to 4 short sentences with the product named once, ends with the ledger INSTAGRAM line, "Link in bio: proofnotfluff.etsy.com" (Todd's wording; the bio now opens the hub with the newest videos' products first), then 3 to 5 hashtags (Instagram caps at 5). Plain search words in the first line ("pricing calculator", "hourly rate", "budget tracker"): public professional posts are indexed by Google since Jul 2025. TikTok caption says "Search ProofNotFluff on Etsy" (ledger TIKTOK line). YouTube description line one stays the product short link, line two the free page.
10. **Code first, then the cold viewer.** make_demo.py refuses a short spec that breaks this file's hard rules (tools/spec_lint.py: formula, kicker, hook length, rows, the ask beat, the close and end card, captions, no em dash, no invented people), so fix the spec when it does; the code gate checks every committed spec the same way. Then the cold viewer, every video. The reviewer sees only the contact sheet and spoken lines and must explain every line and the takeaway, say who it is for, whether they would keep watching, and whether they would send it and to whom. A FAIL is fixed and re-run before approval. Lessons so far (Oct 15): headline gave the answer away; a label and its narration disagreed; a percent's base was unclear; a total's items were not named; "$14 over" lacked its budget.

## 5. Platform rules
- Upload a clean master to each platform; never a file carrying another platform's watermark.
- Instagram: up to 5 hashtags; Trial Reels through the API (trial_params) are worth one test when the CMO or COO can wire it (may need 1,000+ followers); carousels weekly once the COO adds the step (meta/shop.scoutInbox, Oct 15).
- YouTube: Shorts links never click; the path is the related-video link to the product's walkthrough (set in Studio by the shop run) and the spoken proofnotfluff.com.
- AI labels: we use AI tools, not AI people; no label is needed for the voice under Instagram's profile rule. Never present the TTS voice as a real person.

## 6. Measure and decide
- Per piece, from the APIs: YouTube views (and engaged views or Viewed vs swiped when reachable), Instagram likes, comments, saves and shares (insights permission still refused Oct 15: the COO asks Todd to reconnect with insights if it stays blocked), TikTok via Buffer when available, and proofnotfluff.com visits by referrer (Cloudflare Web Analytics, live Oct 15).
- Tag every spec and slate video with `formula` (F1 to F4) and `series` "Proof Check"; promote runs copy both into shorts/<slug>.
- After about 8 posts of a formula, retire the one that loses on both views and engagement, and try a new candidate (for example "3 costs you forgot"). After about 30 varied posts with zero follows and no site visits from social, move agent time to search channels (Pinterest, YouTube walkthroughs, the free site) and Collabs, never to a realistic avatar.
- First review Thu Oct 29 (CMO run): write the verdict at the end of this file and one line in the decision log.

## 7. Human steps (Todd)
- Instagram Settings, Account Status: check that the account can be recommended to non-followers (asked Oct 15).
- Optional later: record the hook lines in his own voice for an A/B test (faceless stays; a voice is not a face).

## 8. Tool backlog (optimizer or builder, one at a time)
1. make_demo: number count-up in frame one and a punch-in zoom on the active cell (a visible change every 1.5 to 3 s).
2. make_demo --cut reel (40 to 55 s, adds "why" depth lines) so Reels and Shorts get their own lengths; promote runs then post the reel cut to Instagram.
3. tools/record_page.py: Playwright recording of the live free calculator being filled in, for F4.
4. Instagram Private Replies (comment keyword to DM with the free page) once the messaging permission is confirmed.

## 9. Voice and script (Todd, Oct 15: "The voices sound good and lets test them all. However, you need to make the scripts sound more human")
**Voice.** ElevenLabs (Todd's Starter plan, through Zapier; tools/el_voice.py has the three steps) replaces the Kokoro voice from Oct 16 (Todd allowed zapier-dev-files.s3.amazonaws.com on Oct 15; the first full render, examples/f2 in Chris's voice, came out at 37.4 s, -14.1 LUFS). If a download is ever refused, render with Kokoro and say so in the slate. Model eleven_v3 (it reads the audio tags below). Test all five voices: rotate Chris iP95p4xoKVk53GoZ742B, Roger CwhRBWXzGAHq8TQ4Fs17, Eric cjVigY5qzO86Huf0OWal, Matilda XrExE9yKIg1WjnnlVkGX, Bill pqHfZKP75CvOlQylNhV4, a different one each video, so each gets about 3 to 4 videos over two weeks; the spec carries "el_voice" and the promote runs copy it into shorts/<slug>. Score them with the formulas (section 6) and keep the best one or two from the first verdict. Budget: Starter is about 30,000 characters a month; a script is about 500, so two videos a day fits with little room: no retakes beyond one per video, and no voice tests outside the slates.
**Script.** Write it for the ear, the way a sharp friend who prices jobs would say it out loud, then let the screen carry the exact figures:
1. Open with a reaction or a question, not a label: "Forty bucks an hour. Sounds fine, right?", "Where does a $355 house wash go?"
2. Talk to one person. Contractions always (you're, that's, don't). Short sentences, mixed with one longer one. A one-word line for the number that hurts: "Fifteen."
3. Say numbers the way people say them: "fifteen sixty-six", "sixty grand", "about a hundred ninety-five bucks", "two ninety-eight". Round the supporting numbers in speech ("about $195"); say the key number exactly once. The screen shows every exact figure.
4. Turn points: "Except...", "Nope.", "Here's the thing.", "So you're at...", "What's left...". At most one per video of each.
5. Say why in plain words once ("Quoting, driving, emails"), never a formula or a label like "Kept per hour worked".
6. The "say" field is the caption and must read naturally; the optional "tts" field (also "hook_tts", "ask_tts") is what ElevenLabs reads: the same words, with numbers spelled the way they are spoken and at most two audio tags per video ([short pause], [sighs], [chuckles]). Never put a word in "tts" that the caption does not carry.
7. No invented people, no outcome promises, no hype words; the facts still come only from the product's files.
8. Read it out loud in your head at speed: if a line would make a real person stumble, rewrite it. The cold viewer also answers "Does this sound like a person talking?" and flags any line that sounds read off a spreadsheet.
The three examples in promo/specs/examples/ carry these scripts (rewritten Oct 15).

## Verdicts
(none yet)
