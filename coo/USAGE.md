# Usage audit, Oct 30, 2026

Todd's ask, live chat, Oct 30, 8:29 am: "audit the existing system and determine where we are wasting usage. Please adjust the system for efficiency." Counts only. Runs per week are scheduled fires, from list_triggers on Oct 30.

## Baseline
- 19 recurring PNF tasks, about 73 cloud runs a week: video daily 7, video lab 3, trades news 7, question pages 7, inbox sweep 10, brief 10, product builder 4, API lister 14, eleven weekly tasks 11.
- Each run boots fresh, clones the repo, reads CLAUDE.md, HANDOFF.md and CONSTITUTION.md (about 13 KB) and runs the preflight (5 s). Those are cheap. The waste is in runs that find nothing to do, steps that cannot succeed, and tool calls that repeat.

## Shipped Oct 30 (small, every check passes)
1. tools/check_repo.py: the video check now counts a missing brotli as a missing tool, so tools/setup_cloud.sh runs by itself. Before: a fresh run without brotli got "ERROR video" and had to debug before it could push. After: full check 0 errors in a fresh container.
2. tools/kimi_wait.py and kimi-jobs step 3: one command waits for Kimi answers. Before: one git pull per tool call, up to 15 calls per job, each carrying the whole run's context.

## Findings and Todd's answers
- A1. API lister: 14 runs a week; every recent note reads "Nothing cleared on the shelf" (Oct 30, 7:50 am). The Etsy builders stopped Oct 17 (scoreboard: factory, builder, R&D last ran Oct 17). It wakes one long-lived session, which grows each time. Constitution 5 keeps it Todd's call.
- A2. Trades news daily: 3 runs Oct 28 to 30, 1 publish (Oct 29, 2 added). Each run starts 5 or more helper agents. Mon, Wed, Fri with the 3-day lookback misses nothing.
- A3. Product builder Tue to Fri: last note "blocked", nothing built (Oct 29); step 3 cities stay parked until 3 pest seats sell (HANDOFF).
- A4. Video studio 7:46 am: 0 of the 12 recorded posts came from it. All came from live chats (Oct 28 9:25 pm, Oct 29 11:23 am and 1:43 pm). Oct 29 note: "Posted 0 of 4 (no Chrome on Todd's PC this run)"; Oct 30: no links recorded. Meanwhile it builds 1 lesson a day: 9 wait unposted, 3 posted, and rule changes rebuild the waiting ones (5 rebuilt overnight Oct 30).
- A5. Connectors: 16 of 18 PNF tasks carry 12 or 13 connectors. Skills use only Claude Docs and Claude Code Remote (the brief's list_triggers). CLAUDE.md invariant 8 bans 8 of the rest. Every connector's tool list rides along on every turn. Only Todd can remove them (each task's settings); update_trigger cannot.
- A6. The Nov 1 payoff-first compare fires even if markup-margin never posts. Its prompt can only be edited from its own thread.

## Left as is, and why
- Question pages daily: 90 of 101 inspected pages are indexed (Oct 30), search visits 0 but most pages are under 2 weeks old; judge at the Nov 7 reading.
- Chief of Staff twice a day: outreach restarted Oct 29, so replies can arrive now.
- Outlandia tasks and the app's own check-ins: not PNF, untouched (Constitution 5).

## Todd's answers, Oct 30, 8:58 am
- [stated] Picked in chat: "Pause Etsy API lister", "Trades news Mon/Wed/Fri", "Product builder Tue only". Not picked: video build cap at 5 (builds stay daily).
- [stated] On A4: "I'll leave Chrome open" (7:46 am posting stays; Todd keeps the PC awake with Chrome and the Claude extension on).
- Done: trades news Mon, Wed, Fri 6:32 am; product builder Tuesdays 11:10 am. Saves 7 runs a week.
- Open: the API lister lives in another thread, so update_trigger can't reach it (not found). Todd pauses it there or in its settings (14 runs a week). A5 connectors are Todd's (task settings).

## A4 root cause, found 9:20 am
- Not Chrome: the 7:20 am inbox sweep reached both inboxes through Chrome today (meta/inbox ok true).
- Cause 1: `anim.py ready` pinned the local commit before push; `git pull --rebase` then gave it a new id, so markup-margin's pin (f9e92d86) was never on GitHub and postcopy could not fetch it. 8 other waiting pins were fine.
- Cause 2: postcopy wrote the upload copy to /mnt/user-data/outputs, which Chrome refuses (LEARNINGS Oct 28); the live chats that posted used the repo path.
- Fixed: markup-margin re-pinned to 7cef77c6 (on main, all 12 fingerprints match, same second as its readyAt); postcopy PASS 3.9 MB, 45.67 s, 1080x1920. `ready` now refuses an unpushed commit; postcopy names a missing pin plainly and writes the upload copy to videos/<slug>/05_render/<slug>-post.mp4; POSTING.md and the skill say upload that path.
