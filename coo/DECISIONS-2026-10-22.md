# Todd's funnel decisions, Thu Oct 22, 2026, 7:57 pm, live chat

[stated] "Let's do all of this as you recommend." The five decisions, as recorded in that chat:

1. [stated] NEW FUNNEL (major, approved): cold email, then a yes to a free Monday email with 2 or 3 real leads, then after the 3rd free Monday a 1-week Gumroad free trial with the card entered at signup, then $29 a month ($39 for restaurant leads when it goes live). Gumroad only allows 1-week or 1-month trials; we chose 1 week.
2. [stated] NEW BUYER TYPES (approved now, overriding the HANDOFF gate that waited for exterior replies): sell the permits we already pull to more kinds of buyers, such as dumpster rental, portable toilets, window cleaning, signage, security and commercial movers.
3. [stated] MORE CITIES (approved): add cities with open permit data by reusing the Chicago and Austin scripts.
4. [stated] ONE SHORT VIDEO (approved): a 20 to 30 second screen recording of the members' app, Remotion is fine, for the product page and follow-up emails only. Never in a first cold email. No ads.
5. [stated] ADS SHELVED until about 5 paying subscribers and a known trial-to-paid rate. Any spend still needs Todd's yes.

Order of work: step 1 in the Oct 22 chat; steps 2, 3 and 4 next, in that order, one chat each. Nothing is sent, published or switched on without Todd's word in chat.

## Step 1 as built, Oct 22
- Cold email ask on all 8 test 1 templates: "Want me to send you jobs like this free each Monday?" A and B still differ only in B's first sentence. No test 1 email had gone out (CRM, Oct 22: 57 sent, all in the legacy Oct 19 and 20 batches, none with a variant), so test 1 reads cleanly on the new ask from its first send.
- Free Monday email and trial offer: email/M1-MONDAY.md, tools/monday_email.py, .claude/skills/monday-email/SKILL.md (not scheduled), first drafts email/monday/drafts-2026-10-22.md.
- Site: tools/make_site.py supports `trialDays` and `mondayForm` on a lead page; both keys are off, so the live site is unchanged.
- Legal desk: legal/reviews/2026-10-22-monday-email-and-trial.md, CLEARED WITH FIXES.

## Step 2 as built, Oct 22, 10:55 pm to midnight
- [stated] Todd, 10:55 pm: "Let's go with your recommendations and start now": build window cleaning, dumpster rental and security; skip portable toilets and commercial movers; hold signage; a drafts-only Wednesday trial run; keep the Monday cap at 200 and trim so the first-issue reply line fits.
- Limits after two checker rounds: window_cleaning new builds of $5M or more, no interior build-outs; dumpster_rental jobs under $5M under inspection; security new builds of $20M or more. Templates T5 to T9, A and B. Legal desk: CLEARED WITH FIXES, all done.
- [stated] Todd, Oct 23, 7:07 am: "Go with your recommendations": create the drafts-only Wednesday trial-offer task; hold the lead page lede for new types until the first dumpster rental or security owner says yes.
- The scheduler refused the task from the chat both times (Oct 22 and 23), so Todd creates it himself in the app: name "PNF leads: Wednesday trial offer", Wednesdays 9:50 am Central, prompt:
  ProofNotFluff leads, Wednesday trial-offer run: add_repo proofnotfluff-a11y/proofnotfluff-pins with push access, shallow clone to /home/claude/proofnotfluff-pins, git fetch origin main and git reset --hard origin/main, read CLAUDE.md, coo/HANDOFF.md and coo/CONSTITUTION.md, run `python3 tools/check_repo.py --preflight monday-email`; if it exits non-zero send Todd the ERROR lines in one message and stop. Otherwise follow .claude/skills/monday-email/SKILL.md for the trial offer only: step 4, then steps 5 and 6, then its trial Outputs (CRM trialOfferedAt after each trial email sends, scoreboard agents/monday-email lastNote with counts only). Build no Monday issue drafts. If nobody is due, set the scoreboard agents/monday-email lastNote to "Wednesday: no trial offers due" and stop without messaging Todd. Nothing sends until Todd says send in this session.
- [stated] Todd, Oct 23, 11:36 am: "Yes" to adding the trial Outputs clause above (so trialOfferedAt is set and nobody is offered twice). Task created from chat on the third try, Oct 23, 11:36 am: trig_01TghVPEuzu8eciXrFZpvDnt, Wednesdays 9:50 am Central, cloud, enabled, first run Wed Oct 28.
