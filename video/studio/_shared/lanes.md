# Lanes: the AI for trades test (Nov 1 to Nov 8, 2026)

Todd, live chat, Nov 1, 2026, 8:41 am: "what do you think about pivoting into specifically focusing and purposing new AI
innovations for tradespeople and their businesses?" ... "I feel like these videos are not really going anywhere".
9:01 am: "go with your recommendation". The recommendation: a 7-day test, 2 of the 4 daily posts in the AI lane and 2 in
the core lane, then switch all 4 to AI if it wins.

Why: through Oct 31 the core lessons drew 2,662 views, 0 shares, 0 follows, 0 comments, 3 saves (`anim.py lanes`).
People share what makes them look smart or helps a friend; a lesson on close rate reads as homework. An owner seeing a
tool do a real job for him is something he sends on. Trade owners want this and have not started: 74% call AI an
efficiency engine, about 25% use it (ServiceTitan 2026 Residential State of the Trades, via phcppros.com), and 40% say
clearer return on investment would get them to adopt (distributionstrategy.com, Sep 2026). Proof is our name.

## The rule (code: `anim.py lanes`, `lane_problems` in `anim.py variety`)
- brief.md names one lane: `- **Lane:** ai` or `core` (no line reads core).
- video/config.json "lanes" mode "alternate": a new lesson is never the same lane as the lesson before it in line, so the
  posting line runs AI, core, AI, core. `anim.py lanes` prints the lane to make next. Mode "ai": every new lesson is AI.
- No series still holds (Oct 31): every AI lesson stands alone. The lane is a subject, not a part 1 and part 2.
- Format rotation, the bar (_shared/standard.md) and every gate still apply to both lanes.

## An AI lane lesson
1. One tool, one real job an owner has this week: reply to a 1-star review, turn voicemail notes into a quote, answer
   an after-hours text, write the follow-up to a quote that went quiet, read a supplier invoice. Never a "5 tools" list.
2. A tool an owner can try in 10 minutes, free or with its price said: Gemini, ChatGPT, Claude, the AI built into Google
   Business Profile, Jobber, Housecall Pro or ServiceTitan, a phone carrier's text-back. A GitHub repo only if it runs in
   a browser with no setup; a plumber will not install code.
3. Real proof, never a made-up screen. The reply on screen is the exact text a real run returned: commit
   `video/studio/demos/jobs/<slug>-<n>.json` and the studio-ai-demo workflow (tools/ai_demo.py) commits the model's
   reply and phone shots of public pages to `video/studio/demos/out/`. On screen: the prompt card, the reply card labelled
   "Real reply, <model>, <date>", and the tool's own help or pricing page with its address (S2). A tool we cannot run
   there (one behind a sign-in) is shown only through its own public pages, with no reply we did not get.
4. Say what it costs, how long it took, and one thing it got wrong or the owner must check. Honest beats hype.
5. The prompt is the save card (C3): the exact words to paste, held 3 s, readable on a phone.
6. The result on screen by 3 s (both lanes; through Oct 31 most core lessons lost TikTok viewers by 4 to 8 s): open on
   the finished reply or the time saved, then show how.
7. Facts gate: every price, plan, feature and limit read on the maker's own page the day the lesson is made, with the
   date; a feature that is "rolling out" is said that way or left out.

First candidates (held Oct 30 as too thin; rebuild in the AI lane with real runs): 2026-11-08-after-hours-reply,
2026-11-10-notes-to-quote, 2026-11-03-review-replies, then IDEAS.md "Owed first".

## Judging (Nov 8, the evening run's diagnosis)
`anim.py lanes` on the lessons posted Nov 1 to Nov 8. AI at twice core or better on shares + saves + follows per 1,000
views: set lanes mode "ai" (Todd's go, Nov 1, 9:01 am) and tell him with the numbers. Otherwise send him both lanes'
numbers and one next step; nothing else changes without his word.
