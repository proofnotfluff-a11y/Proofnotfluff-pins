# Usage audit, Oct 30, 2026

Todd's ask, live chat, Oct 30, 8:29 am: "audit the existing system and determine where we are wasting usage. Please adjust the system for efficiency." Counts only. Runs per week are scheduled fires, from list_triggers on Oct 30.

## Baseline
- 19 recurring PNF tasks, about 73 cloud runs a week: video daily 7, video lab 3, trades news 7, question pages 7, inbox sweep 10, brief 10, product builder 4, API lister 14, eleven weekly tasks 11.
- Each run boots fresh, clones the repo, reads CLAUDE.md, HANDOFF.md and CONSTITUTION.md (about 13 KB) and runs the preflight (5 s). Those are cheap. The waste is in runs that find nothing to do, steps that cannot succeed, and tool calls that repeat.

## Shipped Oct 30 (small, every check passes)
1. tools/check_repo.py: the video check now counts a missing brotli as a missing tool, so tools/setup_cloud.sh runs by itself. Before: a fresh run without brotli got "ERROR video" and had to debug before it could push. After: full check 0 errors in a fresh container.
2. tools/kimi_wait.py and kimi-jobs step 3: one command waits for Kimi answers. Before: one git pull per tool call, up to 15 calls per job, each carrying the whole run's context.

## Findings that need Todd (open)
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
