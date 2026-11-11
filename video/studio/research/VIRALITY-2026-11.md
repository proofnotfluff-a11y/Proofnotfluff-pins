# The virality equation, our engine scored against it, and ten moves (Nov 11, 2026)

Asked by Todd, live chat, Nov 10, 2026: "I want fable to explore ways we can step up our social media game. I want fable to unlock leveled up videos and content for the social media engine. The end goal is to achieve consistent virality. I want fable to research and master the virality equation and apply it to our engine." Fable ran this one research job on his word and sits on no gate and no reviewer role.

Research and proposals only. The rules are frozen to Nov 23 (coo/constitution/video.md, item 6). Nothing in `_shared/`, the gates, the prompts, anim.py, the cadence or any scheduled task was changed. Nothing was made, rendered, posted or pushed. No platform was signed in to. No ElevenLabs call.

Read in this run: CLAUDE.md, coo/CONSTITUTION.md, coo/constitution/video.md, coo/HANDOFF.md, PRINCIPLES.md, the studio CLAUDE.md and CONTEXT.md, `_shared/` formats (v4), formula, hooks, storycraft and standard, research/ viral-science-2026-11-01, STUDY-2026-11-08, PROVEN, FORMULA, PERFORMANCE, TEST-2026-11-23, niche/2026-11-09-results.json, LEARNINGS, IMPROVE, every file in research/metrics/, and the scoreboard's videometrics docs for the newest lesson (they match the repo; no read newer than the Nov 10 evening run exists). Builds on those files and does not repeat them.

## The short answer

1. **One blocker comes before every move.** video/config.json still has `makePaused` (set Nov 9, 2:11 pm). No v4 lesson has been made since the first one. The 14-day test started Nov 9, READ 1 is Nov 15 and the freeze ends Nov 23, and the test has exactly one v4 post. Unless making restarts, both reads will be on one lesson and will show nothing.
2. **The biggest gap is the send.** Across every lesson where the number was visible, Instagram shows 1 send in 3,946 people reached. TikTok shows 0 shares in 3,303 views. Facebook 0 in 1,046. The best lesson we have (turned-down-8k) reached 1,066 people on Instagram and not one of them sent it. Instagram's head names sends per reach as the signal that matters most for reaching people who do not follow you, and we have 4 followers, so every viewer is that kind of viewer.
3. **The 8k lesson won on stop, hold and finish, not on send.** It is the only lesson that broke out on two platforms at once. Its measurable edge: Facebook 3 second hold 32.6% (the other lessons with 200 or more Facebook views: 16.7%, 3.8%), TikTok average watch 51.1% of runtime (median 24.1%), TikTok watched in full 18.2% (median 5.0%, next best 8.4%). Sends, saves and follows: 0, 0, 0.
4. **Three walls show in our own numbers.** Instagram: a post either stays near 110 to 165 views or steps to about 1,300 and stops (three posts: 1,289, 1,295, 1,411). YouTube: under 200, or about 1,000 to 1,600 (four posts). TikTok: every one of 22 lessons sits between 86 and 440 views, and the 8k lesson's doubled watch time moved TikTok views not at all (287).
5. **Honest size of the claim.** One v4 lesson is one data point. It beat the old best by 9% on Instagram and 23% on YouTube. That is a lead, not virality. The next rung is 10,000, and nothing in our data shows we can reach it yet.

## Part 1: the equation

### How reach is built (all four platforms)

A post is shown to a small first audience. If that audience responds well it is shown to a larger one, and so on, until a wave responds badly and the post stops.

`Reach = first audience x (pass wave 1) x (pass wave 2) x ...`

- PROVEN (YouTube staff, Todd Sherman, Creator Insider, Aug 23, 2023; read Nov 11, 2026 through [S6]): a Short is shown to a seed group, reach grows if they watch and tapers if they do not. He called a new channel's early views exploratory, and said a Short that stalls at a few hundred or a few thousand views is a test result.
- Our data fits it: each wave is about 10 times the one before (Instagram 110 to 165, then about 1,300; YouTube under 200, then 1,000 to 1,600). No post of ours has passed a second wave.

### What decides whether a wave passes

`Pass score = Stop + Hold + Finish + Send + Keep and React + Follow, minus Drag`

No platform publishes weights. The weight classes below are ours: heavy, medium, light. The order comes from the sources. Anything that claims an exact weight is folklore.

| Term | What it measures | Where we read it |
|---|---|---|
| Stop | did the viewer stay past the first seconds | YouTube "viewed vs swiped away"; Instagram skip rate (first 3 s); Facebook 3 s views per view |
| Hold | how much of the video they watched | average watch as a share of runtime (TikTok, Instagram), average percentage viewed (YouTube) |
| Finish | watched to the end, or again | TikTok "watched full video"; Instagram views per viewer |
| Send | sent it to someone | Instagram shares per reach; TikTok shares per view |
| Keep and React | saves, likes, comments | per reach or per view |
| Follow | followed after watching | follows per 1,000 reached |
| Drag | things that cut reach whatever the rest says | wrong audience match, repeat or unoriginal flags, AI rules broken, "not interested" taps |

### One line per platform

**Instagram Reels: Hold (heavy) + Send (heavy) + Stop (heavy) + Like (light for strangers) + the rest (light).**
- PROVEN: the three signals that matter most are watch time, likes and sends, read in Insights as average watch time, likes per reach and sends per reach (Adam Mosseri, Jan 22, 2025, [S1]). Likes count a little more with followers, sends a little more with people who do not follow you ([S1], [S3]).
- PROVEN: in a 2024 Q&A he said sends per reach track overall reach more than anything else in his experience ([S2]).
- PROVEN: skip rate is Instagram's own Insights metric since Aug 2025: the share of views skipped in the first 3 seconds ([S4]). STRONG: the average skip rate is 60.5% to 65.5% across 9,771,822 brand Reels, Jan to Jun 2026 ([S4]). Our two Instagram reads were 26.0% and 29.1%, and both are among our three Instagram breakouts.
- PROVEN: Reels over 3 minutes are not recommended to non-followers; accounts that mostly post work they did not make lose recommendations (Apr 30, 2026); a profile showing an AI-made person without the label loses reach (Aug 31, 2026), and labeling it does not cut reach ([S3]). We show no AI person, we label each post, and every render is our own.
- STRONG: Reels of 30 to 60 s have the best reach rate in the same 9.77M Reel set (5.60% against 5.20% under 30 s and 3.50% over 120 s) ([S4]).
- FOLKLORE: "sends weigh 3 to 5 times a like". No primary source. "Instagram ranks skip rate first": one creator's reading of an Insights screenshot ([S5]).

**YouTube Shorts: Stop (heavy) + Hold (heavy) + viewer surveys (medium) + likes and shares (light).**
- PROVEN: Shorts are chosen by swipe, not by click, so the choice YouTube reads first is viewed against swiped away. YouTube Help defines "How many chose to view" as the share of viewers who viewed rather than swiped ([S6], [S7]). Staff called it a great metric and said watch time is a stand-in for "valued watch time", which is partly estimated from surveys ([S6b]).
- PROVEN: since Mar 31, 2025 a Shorts view counts when the Short starts or replays, with no minimum watch. The old stricter count is "engaged views" ([S6b]). So our YouTube view counts are starts. 1,600 views at 63.8% stayed is about 1,020 people who chose to watch.
- PROVEN (staff): there is no ideal length because recommendations adjust for duration; posting time is not something YouTube optimizes for; there is no bonus for a number of Shorts a day; likes and shares feed the models but are sparser than watch signals ([S6b]).
- PROVEN: from Oct 1, 2026 YouTube says it puts original content first on Shorts and cuts reach for re-uploads ([S6], [S6b]).
- STRONG: in 5,400 Shorts, viewed vs swiped under 60% rarely did well and 70% to 90% did best (Paddy Galloway, Apr 2023, via research/viral-science-2026-11-01.md and [S12]). Our ten reads: median 54.8%, best with 200 or more views 66.3% and 63.8%.
- FOLKLORE on YouTube: "build a loop, replays boost ranking". Staff say they do not optimize for two loops ([S6b]).

**TikTok: Finish (heavy) + Hold (heavy) + shares, comments, follows (named, no weights) + Stop.**
- PROVEN: TikTok's own explanation says a strong sign of interest, such as finishing a longer video from start to end, counts for more than a weak one such as viewer and creator being in the same country (TikTok Newsroom, Jun 18, 2020, [S8]). It names likes, shares, comments and follows as signals and gives no weights.
- PROVEN: since Nov 2025 viewers can turn AI-made content down in their For You feed with a slider ([S9]). Our TikTok posts carry the AI label, as its rules require. We cannot see how many viewers have turned it down.
- STRONG: in 2.39M popular TikToks (1,000 likes or more, Oct 3, 2026), faceless videos had a median of 198,000 views against 105,000 for videos with a person, 16 to 30 s had the best median (141,000), and the whole set earned 0.50% shares per view ([S11]). It is a set of winners, so it shows what winners look like, not our odds.
- FOLKLORE: the "300 to 500 view test batch", the "5 second qualified view", the "11 to 18 second sweet spot", "70% completion goes viral", "the first comment matters", trending sounds and hashtags as boosts. Guru pages state them. None cites TikTok.

**Facebook Reels: Match (heavy) + Stop and Hold (medium) + original work (medium).**
- PROVEN: Meta's engineers wrote on Jan 14, 2026 that watch time, likes and shares are noisy. Facebook Reels now also asks random viewers how well a video matches their interests, predicts that answer for every viewer, gives a modest boost to videos predicted to match and demotes ones predicted not to. They say it favors niche, good work over generic popular work, and that match covers audio, production style, mood and motivation ([S10]).
- PROVEN: Meta redefined "original" in Mar 2026 as filmed or produced by the creator and cuts reach for reposts ([S13]).
- Facebook is our smallest platform (median 25.5 views). It is useful as the one place a 3 second hold is shown for every lesson.

### What moves each term

| Term | What moves it | Label |
|---|---|---|
| Stop | the stake readable on frame 0, a picture change inside the first second, the spoken hook done early, a topic a stranger cares about | PROVEN that the first seconds are the choice ([S6], [S4]); our Facebook hold: 32.6% for the v4 frame against 16.7% and 3.8% |
| Hold | a story with a question open, each beat following from the last, no stretch where nothing changes | STRONG (storycraft sources in `_shared/storycraft.md`); ours: old formats 15.9% to 36% on Instagram, the verdict 62.3% |
| Finish | a reason to stay after the payoff, a short enough runtime, an ending that hands back to the start | PROVEN that finishing is a strong sign on TikTok ([S8]); how to cause it is craft, not proven |
| Send | the viewer knows one person this is for or about, a feeling worth passing on, something that says "this is us" | PROVEN that sends matter most for strangers on Instagram ([S1], [S2]); what causes a send: STRONG from text studies only (Berger and Milkman 2012; Cosme et al. 2025, both via research/viral-science-2026-11-01.md, not re-read at the source in this run) |
| Keep and React | a thing worth copying, a question with two real sides | light everywhere; comments are not in Instagram's top three ([S1]) |
| Follow | a show a viewer wants the next one of | no evidence found either way (as on Nov 1) |
| Drag | reposts, repeats, AI rules broken, the wrong audience | PROVEN ([S3], [S6b], [S9], [S13]) |

### Outliers: what faceless work wins, and what of it can be drawn

Read from our own Nov 9 niche pull (YouTube Data API, counts and ids only, research/niche/2026-11-09-results.json), not re-watched: YouTube pages cannot be read from a cloud run, the same wall PROVEN.md and FORMULA.md hit.

- STRONG: among Shorts at the 100K and 5x bar, the trades-owner niche has 0 faceless hits out of 14. The homeowners, HOAs and contractors niche has 18 faceless hits out of 20, from 12 creators. Landlords and tenants: 12 of 31. Pay fights at work: 4 of 11.
- STRONG: those faceless hits are long. Homeowner niche: median 161 s, 13 of 18 over 2 minutes. Landlord niche: median 166 s, 7 of 12 over 2 minutes. A few are 6 to 7 s.
- STRONG (research/PROVEN.md, STUDY-2026-11-08.md): 9 of 14 owner lessons at the bar are about money between two people.
- What this means: the faceless format that repeatedly wins on YouTube is a narrated dispute between a contractor, landlord or boss and the person across from them, told at story length. Our 8k lesson is that kind of story at 30 s. No faceless winner was found doing owner advice.

Can be drawn or animated: two numbers set against each other, a dispute with two sides acted by the cast, a bill built line by line, a phone call or text thread, a one-line caption that states the fight before a word is spoken, a closing question the viewer answers. Cannot: a real roof to judge (hail-or-wear, held), real demolition footage, a real person's face or charisma.

## Part 2: our engine against the equation

### Every posted lesson (latest visible read; n/s = we cannot see this number)

"n/s" is not "low". A number is "low" only where a platform showed it.

| Lesson | Format | Length s | IG views | IG skip % | IG watch % | TT views | TT watch % | TT full % | YT views | YT stayed % | FB views | FB 3 s hold % | Sends | Saves | Follows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| first-reply | v1 | 88.7 | 114 | n/s | n/s | 121 | 4.7 | 0 | 13 | n/s | 40 | 15 | 0 | 0 | 0 |
| quote-revive | v1 | 72.2 | 115 | n/s | n/s | 92 | n/s | n/s | 36 | n/s | 7 | n/s | n/s | n/s | n/s |
| markup-margin | v2 | 45.7 | 129 | n/s | n/s | 180 | 56 | 2.1 | 29 | n/s | 210 | 16.7 | 0 | 0 | 0 |
| three-prices | v1 | 74.6 | 111 | n/s | n/s | 98 | 10.5 | 1 | 30 | n/s | 34 | 2.9 | 0 | 2 | 0 |
| close-rate | v1 | 73.5 | 115 | n/s | n/s | 89 | 4.7 | 1.1 | 39 | n/s | 14 | n/s | 0 | 1 | 0 |
| book-the-call | v1 | 77.5 | 14 | n/s | n/s | 86 | 6 | 2.1 | 16 | n/s | 113 | 2.7 | 0 | 0 | 0 |
| let-me-think | v2 | 42.5 | 103 | n/s | n/s | 130 | 18.5 | 6.3 | 5 | n/s | 13 | n/s | 0 | 0 | 0 |
| lsa-missed-calls | two-shops | 50.1 | 1,289 | 29.1 | 36 | 290 | n/s | n/s | 85 | n/s | 58 | n/s | 0 | 0 | 0 |
| missed-call-text | clinic | 54.8 | 121 | n/s | n/s | 440 | n/s | n/s | 1,292 | n/s | 19 | n/s | n/s | n/s | n/s |
| count-before-ai | playbook | 51.7 | 139 | n/s | n/s | 183 | n/s | n/s | 33 | n/s | 4 | n/s | n/s | n/s | n/s |
| ai-night-quote | fix-this | 40.7 | 122 | n/s | n/s | 159 | n/s | n/s | 18 | n/s | 39 | n/s | n/s | n/s | n/s |
| three-fixes | quick-math | 32.2 | 135 | n/s | n/s | 228 | 26.8 | 8.2 | 78 | 56.6 | 32 | n/s | 0 | 0 | 0 |
| price-list-quote | two-shops | 50.6 | 144 | n/s | n/s | 287 | 31.4 | 8.4 | 182 | 66.3 | 1 | n/s | 0 | 0 | 0 |
| after-hours-robot | story | 87.6 | 1,295 | 26 | 33.1 | 262 | 24.1 | 5.2 | 67 | 76.6 | 15 | n/s | 1 | 1 | 0 |
| lsa-max-bid | story | 69.3 | 118 | n/s | 15.9 | 140 | 21.1 | 4.9 | 32 | n/s | 6 | n/s | 0 | 0 | 0 |
| ask-chatgpt | story | 62.4 | 118 | n/s | 19.2 | 272 | 18.7 | 4.7 | 11 | n/s | 3 | n/s | 0 | 1 | 2 |
| lsa-reports-short | short | 29.7 | 164 | n/s | 23.6 | 168 | 26.3 | 3.6 | 1,100 | 54.6 | 67 | 23.9 | 0 | 0 | 0 |
| angi-four-pros | proven | 50.3 | 136 | n/s | 23.9 | 209 | 27.3 | 5.9 | 2 | n/s | 26 | 30.8 | 0 | 0 | 0 |
| after-hours-greeting | proven | 57.6 | 111 | n/s | 17.4 | 262 | 26 | 5.6 | 1,000 | 46 | 22 | 13.6 | 0 | 0 | 0 |
| pay-before-you-leave | proven | 54.5 | 133 | n/s | 33 | 207 | 20.6 | 5.5 | 45 | 52.1 | 25 | 16 | 0 | 0 | 0 |
| damage-or-not | proven | 57.1 | 151 | n/s | 35 | 277 | 30.3 | 5 | 96 | 55 | 237 | 3.8 | 0 | 1 | 0 |
| turned-down-8k | v4 verdict | 30.5 | 1,411 | n/s | 62.3 | 287 | 51.1 | 18.2 | 1,600 | 63.8 | 221 | 32.6 | 0 | 0 | 0 |

Notes on the table. Views are the latest read (YouTube's are 7-day and K-rounded where Studio showed them that way). Watch % is average watch seconds divided by the rendered length in qa.json. Sends, saves and follows add Instagram and TikTok where shown; YouTube never showed shares, and showed subscribers gained once (3, on after-hours-greeting). markup-margin's 56% TikTok watch sits beside 2.1% watched in full on 180 views, so read it with care. Facebook hold is shown only at 20 or more views, YouTube stayed only at 20 or more. Twelve more lessons in videos/ have no metrics file (not posted, or held).

Medians over the 22: Instagram 125.5 views, TikTok 195, YouTube 37.5, Facebook 25.5. TikTok watch 24.1% and watched in full 5.0% (17 reads). YouTube stayed 54.8% (10 reads). Total: about 17,770 views on 88 posts.

Pooled, where each number was visible: Instagram 1 send, 4 saves, 0 follows, 1 comment, 45 likes on 3,946 reached. TikTok 0 shares, 2 saves, 2 new followers on 3,303 views. Facebook 0 shares on 1,046 views.

Is 1 send in 3,946 just chance? On Nov 1 the answer was yes, at a few hundred views. It is no longer. If our true send rate were 0.4% (one creator's own "not great" Reel, [S5]) we would expect about 16 sends, and seeing 1 or fewer would happen a few times in a million. Even at a true rate of 0.1% we would expect about 4, and seeing 1 or fewer happens about 1 time in 10. So our send rate is almost surely under 0.4% and likely under 0.1%. That is a real gap now, not a small-sample blank.

### The biggest gap, platform by platform

| Platform | Biggest gap we can see | Evidence | What we cannot see |
|---|---|---|---|
| Instagram | **Send.** | 0 sends on 1,066 reached (8k) and 1 on 1,122 (after-hours-robot): both posts stopped near 1,300. Stop and Hold were good on the two posts where skip was shown (26.0%, 29.1% against a 60% to 65% norm) | skip rate on 20 of 22 lessons (phone app only), no retention curve on file, sends split from other shares, share of reach that was non-followers |
| TikTok | **Reach does not respond to anything we changed.** Inside the equation: Finish. | 22 of 22 lessons between 86 and 440 views. Watch went from a 24.1% median to 51.1% and full watches from 5.0% to 18.2% on the 8k lesson, and views stayed at 287. The 20% full-watch bar in TEST-2026-11-23 is still unmet | account status (never read: "hidden" on all 8 health reads), the retention curve, the traffic source on 21 of 22 lessons, how many viewers have AI content turned down |
| YouTube | **Stop.** | stayed-to-watch median 54.8%; the 8k lesson 63.8%; the STRONG bar is 70% | shares (never shown), average percentage viewed on 20 of 22, engaged views, shown in feed |
| Facebook | **Stop**, on a tiny base. | 3 second hold median 16% over 15 reads; 32.6% on the 8k lesson | follower and non-follower split |

One more thing the YouTube rows show: at our size YouTube views do not track stayed-to-watch. Our four Shorts near 1,000 or more had 46%, 54.6%, 63.8% and no read; the Short with the best stay (76.6%) got 67 views. With ten reads this says little, but it warns against reading any single YouTube view count as a verdict.

### Each term and the lever that controls it

| Term | Lever | Where it lives |
|---|---|---|
| Stop | the story pick (would a stranger stop) | brief.md `Pull` and `Audience` (`_templates/v4-brief.md`); `_shared/formats.md` "v4" story pick |
| Stop | frame 0 and the first second | `_shared/formats.md` "v4" ("Frame 0 is the fight"), `_shared/hooks.md`, stage 04 scene.js from `_templates/v4-verdict.scene.js` |
| Stop | the first spoken sentence | stage 01 script.md, `_shared/voice.md` |
| Stop (YouTube) | the title | captions.json, `_shared/captions.md` |
| Hold | story shape, the payoff cue, no words standing over 4 s | `_shared/storycraft.md`, stage 03 cues.md (`[payoff]`), `_shared/formats.md` "v4" |
| Hold | length | `_shared/formats.md` "v4" (18 to 35 s), `anim.py check` |
| Finish | the last line and the last frame | `_shared/formats.md` "v4" (the closing question), stage 03 cues, stage 04 scene |
| Send | who it is for, said in the story | brief.md `Pull: send`, the last line in script.md, the caption send line in captions.json |
| Send | whether a stranger would pass it on | the viewer gate (prompts/viewer.md) |
| Keep and React | the closing question, the title question | script.md, captions.json |
| Follow | a recognizable show | `_shared/formats.md` "v4" (each format is a named show), `_shared/sound.md`, the pinned comment and bio link (TEST-2026-11-23 "Money") |
| Drag | AI labels | captions.json settings (`V4_LABELS`), `_shared/captions.md` |
| Drag | repeats | `_shared/formats.md` variety rules, `anim.py variety` |
| Drag | how we post and read | video/studio/POSTING.md, coo/constitution/video.md item 8 (still open: Todd's call) |
| Weak lever | posting time | video/config.json slots. YouTube staff say they do not optimize for it ([S6b]); we have one slot now, so it cannot be tested anyway |
| No lever on reach | the gates | they stop bad posts; gate scores do not track views (design score against views r = 0.10, STUDY-2026-11-08) |

### Why the 8k lesson worked: each guess tested against the other lessons

| Guess | Test against the others | Verdict |
|---|---|---|
| It is short (30.5 s) | three-fixes (32.2 s) and lsa-reports-short (29.7 s) are the same length: TikTok watch 26.8% and 26.3%, full 8.2% and 3.6% | Not enough on its own. Short helped finish only with the story |
| The frame 0 stake in big type, whole frame, close on the people | Facebook 3 s hold with 200 or more views: 32.6% against 16.7% (markup-margin) and 3.8% (damage-or-not) | Supported, on one platform |
| A dispute a stranger can judge, not advice for owners | damage-or-not also asks the viewer to judge, at 57 s with the host explaining: TikTok 30.3%, full 5.0%, Instagram 151 views | The judge question alone did not do it. The dispute with money and no lecture did |
| Two numbers against each other ($8,000 and $200) | no other posted lesson opens on two numbers (worth-without-you does, and is not posted yet) | Untested. The next verdicts can test it |
| A reason to stay after the payoff (why did he say no, then you decide) | full watches 18.2% against a best of 8.4% in 16 other reads | Supported. This is the number most unlike the rest |
| A wider audience than owners | every earlier lesson spoke to owners only; this one got the only comment on record and 28 YouTube likes against 0 to 9 on the others | Supported, and tied up with the format (one bundle, as TEST-2026-11-23 warns) |
| It got lucky with the first audience | five old lessons also reached 990 to 1,299 on one platform. None did it on two at once, and none has the watch numbers | Luck cannot be ruled out on views. The watch numbers are not luck |
| Better hook on YouTube | stayed 63.8%: third of our ten reads and under the 70% bar | Not the reason. The YouTube opening is still a gap |

What it did not do: it earned no send, no save and no follow, and it did not move TikTok reach.

## Part 3: ten moves, ranked (on paper; nothing ships before Nov 23)

Before the moves: making is paused (`makePaused`). With no new v4 lessons, none of these can be tested and TEST-2026-11-23 cannot be read. Restarting is Todd's word (paste the v4 make prompt, video/studio/schedule/record-and-make.txt). It is not a rule change.

Every bar below is set now, before any result. Quality bars count only where a platform shows 200 views or more, as in TEST-2026-11-23. "Lead" is over 1,300 views on one platform in 72 hours.

### 1. Build the send into the story
- **Term:** Send (Instagram first).
- **Evidence:** PROVEN that sends per reach matter most for strangers ([S1], [S2]). Ours: under 0.1%, and both Instagram posts with full reads stopped near 1,300 with 0 and 1 sends. Today the send line is only in the Instagram caption.
- **The move:** (a) the story pick must name a sender, a receiver and the reason in one line ("a roofer sends it to the partner who always gives the discount, to say I told you so"); (b) the last line of the voice says who to send it to, in the story's own words, in under 2 s; (c) the last frame shows the two sides as two kinds of people the viewer knows.
- **Expected effect:** the first sends we have ever earned on purpose. If Instagram's own account of its ranking holds, this is what opens the wave after 1,300.
- **Cost:** no build. One line in the brief, one in the script, two labels on the last frame. No extra voice beyond 2 s.
- **Files it would touch after Nov 23:** `_templates/v4-brief.md` (a `Send:` line), `_shared/formats.md` "v4" (last line and last frame), prompts/viewer.md (the stranger must name who they would send it to).
- **Test:** the next 5 v4 lessons carry it. PASS: pooled Instagram sends per reach of 0.2% or more over at least 3,000 reached (6 sends or more), or any one lesson at 0.5% (the TEST-2026-11-23 bar). KILL: 1 send or fewer over 3,000 reached. HOLD: anything between.

### 2. See the numbers we are blind to
- **Term:** all of them. Stop on Instagram most.
- **Evidence:** Instagram skip rate is "hidden: app only" on 20 of 22 lessons, including the 8k lesson. TikTok account status has never been read. Without them we cannot tell an opening problem from a middle problem on Instagram, or a content problem from an account problem on TikTok.
- **Corrected the same day (see Part 4, change 2):** the official Instagram feed carries skip rate and shares, so the fix is that feed, not screenshots. Only TikTok's account status still needs a weekly look on the phone.
- **The move as first written:** once a week, from his phone, Todd screenshots the Instagram insights of that week's v4 lessons (skip rate, the retention chart, shares) and the account status page in the TikTok and Instagram apps. About 3 minutes. It is the one job only he can do. The evening run already reads everything a browser can.
- **Expected effect:** none on reach directly. It turns "we cannot see" into "low" or "fine" for the heaviest Instagram term.
- **Cost:** 3 minutes of Todd a week. No usage.
- **Files:** research/metrics/<slug>.json gets the numbers; video/studio/research/PERFORMANCE.md "daily read" gets one line.
- **Done when:** every v4 lesson has an Instagram skip rate and a sends count by 72 hours, and each account's status is on file once a week.

### 3. Two reveals, not one
- **Term:** Finish (TikTok first), Hold.
- **Evidence:** PROVEN that finishing is a strong sign on TikTok ([S8]). Ours: 18.2% full against a 20% bar, and average watch 15.6 s of 30.5 s, so the average viewer is gone by the midpoint, soon after the payoff. LEARNINGS, Nov 9: "the two lower bids were the most interesting fact and the voice skipped them".
- **The move:** keep the answer by 40% of the runtime. Hold back the second best fact until 70% to 85%, say it aloud and show it (a second number, what happened next, what the other side said). Then the closing question. Every number on screen is spoken.
- **Expected effect:** full watches over the 20% bar; average watch from about 51% toward 60%.
- **Cost:** none in build. A second marked cue.
- **Files:** `_shared/formats.md` "v4" (a `[twist]` cue beside `[payoff]`), `_templates/v4-cues.md`, `_shared/storycraft.md` (the turn).
- **Test:** 3 lessons with it. PASS: TikTok watched in full 25% or more and average watch 55% or more on 2 of 3. KILL: all 3 under 18.2% full. HOLD: between.

### 4. Win the first second
- **Term:** Stop (YouTube first).
- **Evidence:** STRONG bar of 70% stayed; ours 63.8%. The 8k lesson opens on two sentences, 17 words. hooks.md already holds a 12 word, 3.6 s rule for proven lessons; the v4 section sets no spoken hook rule.
- **The move:** this sharpens the opening test already planned for days 8 to 9 of TEST-2026-11-23. Frame 0 stays a settled cover (LEARNINGS) and shows two numbers against each other. The first change lands by 0.6 s, not 1 s (the stamp lands, a face reacts). The spoken hook is 8 words or fewer and ends by 2.5 s; the second sentence carries the detail.
- **Expected effect:** YouTube stayed from 64% to 70% or more. That is the range where the 5,400 Short study saw reach open up.
- **Cost:** none in build; the template already draws plates and stamps.
- **Files:** `_shared/formats.md` "v4", `_shared/hooks.md`, `_templates/v4-verdict.scene.js` timings.
- **Test:** PASS: YouTube stayed 70% or more on 2 of 3 lessons and Facebook 3 s hold 40% or more wherever Facebook shows 200 views. KILL: all 3 under 60%.

### 5. Pick every story from the pool where faceless wins
- **Term:** Stop, Send, Match.
- **Evidence:** STRONG: 18 of 20 homeowner and contractor hits at the 100K bar are faceless, against 0 of 14 for trades-owner advice (our Nov 9 pull). 9 of 14 owner hits are money between two people. The 8k lesson is that kind of story.
- **The move:** add two checks to the story pick. Two numbers that can stand against each other. A split a stranger would argue about: if nearly everyone takes the same side it is a rant, not a verdict. Homeowner and contractor money fights first. This also informs the niche pick Todd still has open (HANDOFF): the 8k result came from the homeowner and contractor pool.
- **Expected effect:** more lessons reach the second wave. This is the consistency lever.
- **Cost:** none.
- **Files:** `_shared/formats.md` "v4" story pick, `_templates/v4-brief.md` `Pull`.
- **Test:** PASS: 3 of the next 5 v4 lessons reach Lead. KILL: none of 5 passes 500 on any platform.

### 6. Find out what caps TikTok
- **Term:** Drag.
- **Evidence:** 22 of 22 lessons between 86 and 440 views; doubled watch time changed nothing. A vendor study of 375,462 accounts says TikTok gives the smallest accounts the most views per video of the three platforms ([S14]), so a flat line here is odd. The audit already read the Chrome posting route as against the platforms' terms (constitution annex, item 8, open).
- **The move:** one test, two posts. Todd uploads two v4 lessons to TikTok by hand from his phone, label on, same caption. Everything else stays the same. It also bears on item 8.
- **Expected effect:** unknown. It splits "TikTok does not like the videos" from "TikTok does not like how they arrive".
- **Cost:** about 2 minutes of Todd, twice.
- **Files:** video/studio/POSTING.md (a note); item 8 stays his call.
- **Test:** route is the cap if a hand-posted lesson passes 1,000 TikTok views in 72 h while Chrome-posted v4 lessons of the same week stay under 450. No difference shown if both stay under 450. Two posts can only show a large difference.

### 7. A long cut for YouTube only
- **Term:** Hold (YouTube).
- **Evidence:** STRONG: faceless hits in the dispute niches run long (median 161 s and 166 s). PROVEN (staff): YouTube adjusts for length, so a long Short is not marked down for being long ([S6b]). Against it: our old long lessons held 16% to 33%, but they were lectures.
- **The move:** one verdict told twice from the same brief: the 30 s cut everywhere, and a 75 to 100 s full case on YouTube with the back and forth and both sides' best argument.
- **Expected effect:** unknown, possibly high on YouTube.
- **Cost:** high. A second script, voice (about 3 times the characters, and ElevenLabs bills about 1.7 times the characters sent per LEARNINGS), cues and render. v4 caps length at 35 s, so this needs Todd's yes as a format change.
- **Files:** `_shared/formats.md` "v4" length, `anim.py check` band, a second scene.
- **Test:** PASS: the long cut holds 50% or more average percentage viewed and beats the 30 s cut's YouTube views at 72 h, on 2 of 2 stories. KILL: under 35% viewed on both.

### 8. One show a stranger would follow
- **Term:** Follow.
- **Evidence:** none found that a series lifts follows (Nov 1 and now). Where shown, 88 posts earned 2 TikTok followers and 3 YouTube subscribers. YouTube added a way to group Shorts into a series on Sep 23, 2026 ([S6]); that a feature exists is not evidence it works.
- **The move:** keep every case its own story (the v4 rule). Give the verdict show one name, one 1 second sound sting on the stamp and the same closing words every time, so the second verdict a viewer meets is recognized. No numbering, no part 2.
- **Cost:** low. One sound in the bank, one line in the template.
- **Files:** `_shared/formats.md` "v4", `_shared/sound.md`, `_templates/v4-verdict.scene.js`.
- **Test:** PASS: 2 follows or more per 1,000 Instagram reach pooled over 5 lessons. KILL: 0 over 5,000 reached.

### 9. Say and show the words people search
- **Term:** Match.
- **Evidence:** PROVEN that Facebook ranks on predicted interest match ([S10]). FOLKLORE to STRONG elsewhere: search pages say on-screen text and captions feed TikTok and Instagram search; no primary source read this run.
- **The move:** the trade and the fight in plain words inside the first on-screen plate and the first caption line ("roofer", "discount", "$8,000"). v4 captions already do the second half.
- **Cost:** none.
- **Files:** `_shared/captions.md`, `_templates/v4-brief.md`.
- **Test:** not separable at our size. Log it and read traffic source where a platform shows one.

### 10. Sound: two silences and one hit
- **Term:** Hold, and Match on Facebook.
- **Evidence:** weak. Meta says audio is part of interest match ([S10]). No source shows sound design lifting reach. Design score does not track our views (r = 0.10).
- **The move:** the cheapest version only, already in IMPROVE 00a-7: a 0.4 s near-silence before the answer and before the twist, and the biggest sound of the lesson right after.
- **Cost:** low.
- **Files:** `_shared/sound.md`, IMPROVE.md 00a-7.
- **Test:** none of its own. It rides with move 3.

### The areas Todd asked about, in one table

| Area | Verdict | Why |
|---|---|---|
| Visuals | Spend only on frame 0 and the first second | Stop is where a picture pays (Facebook hold 32.6%). Design scores do not track views |
| Motion | First second yes, more polish in the middle no | same; STUDY-2026-11-08 found r = 0.10 |
| Sound design | The cheap version only (move 10) | no evidence it lifts reach |
| Pacing | Two reveals (move 3) | half of viewers leave near the payoff |
| Hooks | Two numbers, 8 words, done by 2.5 s (move 4) | YouTube stayed is under the bar |
| Loops and rewatch | Test the loop ending as planned for days 12 to 13; expect it to help TikTok and Instagram counts, not YouTube | YouTube staff say they do not optimize for loops |
| Captions and on-screen text | Keep the v4 rules; add the search words (move 9) | already big enough since the 132 size rule |
| Series without cookie cutters | One named show, new case each time (move 8) | no evidence a numbered series helps |
| Comment bait that stays honest | A real two-sided question, or "what would you have charged?" Never "comment X and I will send it" (we never reply; Instagram says engagement bait cuts reach) | comments are a light term: 1 comment in 88 posts, and not in Instagram's top three |
| New v4-style formats | Two on paper below | |

### Two new formats on paper (not built; each would need Todd's yes as a format change)
- **quote duel:** two prices for the same job side by side ($3,100 and $150). The viewer guesses which is right before the reveal. Brief 2 below is written to work as a call today and as a quote duel later.
- **text thread:** the fight as a text thread on a phone screen, typed as it is read. Reads with the sound off, and needs no second voice. A reenactment is said once.

### What "consistent" should mean, as a number
Old formats: 0 of 21 lessons reached Lead; 5 of 21 passed 990 on one platform. v4: 1 of 1 reached Lead, on two platforms. A fair bar for "consistent" by Dec 15: half or more of v4 lessons reach Lead, and the median best-platform views of v4 lessons is 1,000 or more. Viral (100,000) is not supported by anything in our numbers yet. Saying otherwise would be a guess.

## Part 4: changes to the engine's architecture (added Nov 11, 4:30 pm, on Todd's follow-up ask)

Todd, same chat: "recommend changes to our architecture and the video social media video engine to ensure that we have the highest probability of virality." On paper only. Nothing can ensure virality; these raise the odds.

First principles. Going viral is a selection problem, not a polish problem. The odds are: how many truly different stories we post from the right pool, times the chance each one passes a wave, and how fast we learn which is which. Today the engine is built to polish one video through gates whose scores do not track views. It is weak on all three: making is paused, the gates judge quality and not pull, and the read misses the heaviest numbers.

Correction to move 2. Our browser reads say Instagram's skip rate is "app only". Meta's developer reference lists a Reels skip rate metric beside shares, saves, reach and average watch time in the official Instagram insights feed ([S15]). So the fix for the blind spot is the official feed, not weekly screenshots. On a very small post the skip field can come back empty ([S16]).

| # | Change | What it fixes | Where | Needs |
|---|---|---|---|---|
| 1 | **A case bank ahead of the make line.** Story scouting runs every night on the box and keeps 20 verified dispute stories ready, each scored on the four terms (stop, hold, finish, send) before anything is built | making never waits on a story; the pick is made on pull, from many candidates, not from the one story at hand | story desk (.claude/skills/story-desk), research/STORIES.md, `_shared/nightshift.md` box jobs | Todd's yes after Nov 23. Nothing the box writes posts unchecked (annex item 7) |
| 2 | **The official numbers feed.** The evening read moves from Chrome to Instagram's and YouTube's own data feeds | skip rate, sends, saves and reach on every lesson; the terms risk in annex item 8 | research/PERFORMANCE.md "daily read", the evening task, a small tool in tools/ | Todd's sign-ins once. It is his item 8 call, so it does not wait for the freeze |
| 3 | **Posting by an allowed route.** YouTube and Meta through their own posting feeds. TikTok by hand from Todd's phone for now | the same terms risk; and it runs the TikTok ceiling test (move 6) for free | video/studio/POSTING.md, the posting task | TikTok keeps every post from an unaudited app private, and its audit turns down apps built only for the maker's own use ([S17]). So we cannot build our own TikTok poster. A paid scheduler is the other way and would need a review of user reviews first and Todd's word |
| 4 | **The viewer gate gives a forecast, not only a pass.** The stranger scores each term 1 to 5 and names who they would send it to and why. The forecast is filed and later set beside the real numbers | we learn which forecasts are worth trusting; a lesson nobody would send goes back before a render | prompts/viewer.md, `anim.py ready`, research/FORMULA.md | Todd's yes after Nov 23 (a gate change). No new gate is added |
| 5 | **A scorecard the recorder fills by itself.** One row a lesson, one column a term and platform, "cannot see" kept apart from "low", pooled rates by format | the table in Part 2 becomes a daily output, not a research job | the recorder step of the make task, research/metrics/, the scoreboard | Todd's yes after Nov 23 (a prompt change) |
| 6 | **One variable a lesson, pooled reads.** Each lesson names one test and its bar in the brief; reads pool lessons by term | small samples stop producing empty reads | `_shared/formula.md` (already says one change a lesson), research/TEST files | none: it is the standing rule, applied to v4 |
| 7 | **One story, a cut per platform.** After move 7 passes its test: the 30 s cut for Instagram, TikTok and Facebook, a longer case for YouTube | the platforms reward different lengths | stage 01 script, `anim.py check` length band, a second scene | Todd's yes (a format change), and voice credits |
| 8 | **Cadence follows the hit rate.** One a day until half of v4 lessons reach Lead; then two a day, each a different story | more draws only once each draw is worth making. YouTube staff say volume earns no bonus | video/config.json posting | Todd's word |

Not recommended: more motion polish or a new look (scores do not track views); another gate; Instagram Trial Reels for hook tests (one scheduler's help page says they need 1,000 followers, and Instagram's own posts give no number; we have 4) ([S18]).

The pool decision is architecture too. The faceless winners are in contractor and customer money fights (18 of 20). That audience is mostly homeowners and techs. They are not the buyers of our lead products, so reach there may not move the $1,000 month. The tagged link read in TEST-2026-11-23 "Money" is what tells us, and it should stay on every post.

Order. (1) Restart making. (2) Todd's item 8 call and sign-ins: changes 2 and 3. (3) After Nov 23: the send line (move 1), the viewer forecast (change 4), the scorecard (change 5). (4) The case bank (change 1). (5) The long YouTube cut, only after its test.

## Adopted Nov 11 (Todd, live chat, 4:26 pm: "Go with your recommendations on everything. Keep iteratively looking at the results, and based on those results, make improvements.")

Live from the first v4 lesson made after Nov 11 (formats.md "v4", "Level-ups, Nov 11"). The make run reads these every night, pools the lessons made under each, and keeps or drops by the bar. Quality bars count only where a platform shows 200 views or more. The TEST-2026-11-23 levels (Lead, Breakout, Viral) and its scale and stop rules stand; its week 2 variable plan is replaced by these four.

| Level-up | Read on | PASS (keep) | KILL (take it out) | Anything else |
|---|---|---|---|---|
| Send line | first 5 lessons, Instagram, pooled | 6 sends or more over at least 3,000 reached, or one lesson at 0.5% sends per reach | 1 send or fewer over 3,000 reached | keep reading; decide at 5,000 reached |
| Two reveals | first 3 lessons, TikTok | watched in full 25% or more and average watch 55% or more on 2 of 3 | all 3 under 18.2% watched in full | keep, read 3 more |
| First second | first 3 lessons, YouTube and Facebook | YouTube stayed 70% or more on 2 of 3 | all 3 under 60% stayed | keep, read 3 more |
| Story pick checks | first 5 lessons, best platform | 3 of 5 reach Lead (over 1,300 in 72 h) | none of 5 passes 500 on any platform | keep, read 5 more |

Where Instagram's send count or skip rate is still hidden, the row says "cannot see" and no bar is called on it.

### Next builds (for the Opus runs and the box; none is a rule change by itself)
1. The official numbers feed (Part 4, change 2): a small read-only tool for Instagram's and YouTube's own insights. Waits on Todd's sign-ins, in a live chat.
2. A way to hand Todd each lesson's file on his phone, for TikTok by hand (Part 4, change 3).
3. The scorecard (Part 4, change 5): the Part 2 table written by the recorder each night.
4. The case bank on the box (Part 4, change 1): 20 verified dispute stories, scored on the four terms.
5. Lint for the level-ups once they pass their bars (the 8 word hook, the twist cue's place, the send line's length).

## What this run could not do
- Watch any outlier. YouTube and TikTok pages do not load in a cloud run. Outlier claims rest on our Nov 9 API pull (counts, lengths and a format label read from covers, titles and channel descriptions) and on PROVEN.md.
- Read three primary pages in full. Social Media Today's Mosseri report, TikTok's Newsroom post and Meta's Reels ranking card were blocked to the fetch tool; their key lines were read as search excerpts and are marked so below.
- Split which part of v4 moved which number. It is one bundle on one lesson.

## Sources (all read Nov 11, 2026)
- [S1] Social Media Today, "Instagram shares algorithm insights" (Mosseri, Jan 22, 2025). Excerpt only. https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/
- [S2] Social Media Today, "Instagram chief shares insights into its algorithms" (2024 Q&A; sends per reach). Excerpt only. https://www.socialmediatoday.com/news/instagram-chief-shares-insights-into-its-algorithms-creator-monetization/718540/
- [S3] Secondary reports of Instagram's own posts: creatorflow.so "Instagram Algorithm 2026" (3 minute limit, Apr 30, 2026 originality rule, sends and likes by audience) https://creatorflow.so/blog/instagram-algorithm/ ; techwyse.com on the Aug 31, 2026 Instagram Creators post about AI-generated profiles https://www.techwyse.com/?p=78112 . Excerpts.
- [S4] Socialinsider, "Instagram Reels Statistics for 2026" (9,771,822 Reels, Jan to Jun 2026; skip rate and reach by length), Jun 24, 2026. Page read. https://socialinsider.io/blog/instagram-reels-statistics/ . Skip rate definition and Aug 2025 date: babbleboxx.com, excerpt.
- [S5] The Wealthy Creator newsletter, May 14, 2026 (one creator's Insights screenshot; his own 59.5% skip and 0.4% share rate). Page read. https://advantage.beehiiv.com/p/instagram-just-told-us-exactly-how-to-get-more-views
- [S6] OutlierKit, "How the YouTube Shorts Algorithm Works in 2026, in YouTube's Words" (built on the Aug 23, 2023 Creator Insider transcript; dated list of changes). Page read. https://outlierkit.com/resources/youtube-shorts-algorithm/
- [S6b] Fliki, "YouTube Shorts algorithm" (each claim tied to a YouTube source and marked confirmed or staff statement). Page read. https://fliki.ai/blog/youtube-shorts-algorithm
- [S7] YouTube Help, "Understand your YouTube content performance" ("How many chose to view"). Excerpt. https://support.google.com/youtube/answer/12220281
- [S8] TikTok Newsroom, "How TikTok recommends videos #ForYou", Jun 18, 2020. Excerpt only. https://newsroom.tiktok.com/en-us/how-tiktok-recommends-videos-for-you
- [S9] TechCrunch and Social Media Today on TikTok's AI content slider, Nov 2025. Excerpts. https://www.socialmediatoday.com/news/tiktok-adds-option-to-limit-ai-content-in-your-for-you-feed/805952/
- [S10] Engineering at Meta, "Adapting the Facebook Reels RecSys AI Model Based on User Feedback", Jan 14, 2026. Page read. https://engineering.fb.com/2026/01/14/ml-applications/adapting-the-facebook-reels-recsys-ai-model-based-on-user-feedback/
- [S11] Revid, "Short-Form Video Statistics 2026" (its own index of 2.39M TikToks with 1,000 likes or more, Oct 3, 2026). Page read. Vendor data. https://www.revid.ai/short-form-video-statistics
- [S12] Vaizle on Paddy Galloway's Shorts study (70% to 90% viewed did best). Excerpt; the figures as filed in research/viral-science-2026-11-01.md.
- [S13] TechCrunch, "Facebook makes it easier for creators to report impersonators", Mar 13, 2026 (the new definition of original). Excerpt. https://techcrunch.com/2026/03/13/facebook-makes-it-easier-for-creators-to-report-impersonators/
- [S14] Metricool, "The State of Short-Form Social Media in 2026" (375,462 accounts; TikTok leads views for accounts under 2,000 followers; no per-video figures given). Page read. Vendor data. https://metricool.com/the-state-of-short-form-social-media/
- [S15] Meta for Developers, "Instagram Media Insights" (lists `reels_skip_rate`, `shares`, `saved`, `reach`, `ig_reels_avg_watch_time`). Excerpt. https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights/ ; Supermetrics change log adding "Reels skip rate" to its Instagram Insights fields. Excerpt. https://docs.supermetrics.com/docs/instagram-insights-updates
- [S16] Storrito, "How Instagram marketing API metrics work" (skip rate can return nothing on low-reach Reels). Excerpt. Vendor page. https://storrito.com/resources/how-instagram-marketing-api-metrics-work/
- [S17] TikTok for Developers, "Content Posting API: Direct Post" (posts from unaudited clients are private) https://developers.tiktok.com/doc/content-posting-api-reference-direct-post ; Ayrshare on the audit and internal-use apps https://www.ayrshare.com/tiktok-api.md . Excerpts.
- [S18] Publer help, "How to schedule Instagram Trial Reels" (1,000 follower minimum) https://publer.com/help/en/article/how-to-schedule-instagram-trial-reels-1mgvthp/ ; makeinfluence.com notes Meta's own posts state no number. Excerpts.
- Ours: research/metrics/*.json (reads through Nov 10, 2026, 8:45 pm Central), videos/*/05_render/qa.json (lengths), research/niche/2026-11-09-results.json, research/PROVEN.md, research/STUDY-2026-11-08.md, research/TEST-2026-11-23.md, LEARNINGS.md.

With this file: VIRALITY-2026-11-DECISIONS.md (the decision page) and VIRALITY-2026-11-briefs/ (three sample briefs).
