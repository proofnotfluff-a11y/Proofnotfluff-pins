# MAP: how ProofNotFluff fits together (Nov 7, 2026)

CLAUDE.md is the router every run reads first; this map is for a person or a live session getting their bearings. When this map and a rule disagree, the rule wins and this map gets fixed in the same commit. The Etsy-era map is in archive/MAP-2026-10-17.md.

## Where the truth lives
| What | Where |
|---|---|
| Fixed rules (Todd only) | coo/CONSTITUTION.md (core, every run) and coo/constitution/*.md (annexes, read by the jobs they cover) |
| Todd's decisions, by day | coo/DECISIONS-<date>.md ([stated] lines are his words) |
| Where the business stands | coo/HANDOFF.md (current state only, under 2 KB) |
| One job's contract | .claude/skills/<job>/SKILL.md (Inputs, Process, Outputs) |
| Live numbers, todos, agent status | scoreboard artifact (ArtifactData), link in CLAUDE.md |
| Named prospects | CRM artifact and data/ (gitignored), never the repo |
| Research verdicts | Research Wiki (Claude Doc), filed only in live chats |
| Live task prompts | the scheduled tasks themselves; a prompt Todd pastes sits next to its work (agents/README.md) |

## Live scheduled tasks (Central time)
- Video studio, record and make: 9:33 am, 12:33, 5:33 and 9:33 pm, cloud. Posting: 11:37 am, 4:41 pm, 8:13 pm through Chrome on Todd's PC.
- Question pages: daily 7:10 am. Trades news, index request, radar: the 1st and 15th.
- Traffic report Mon 7:35 am; Monday email Mon 8:50 am; outreach and inbox Mon 9:40 am; trial offer Wed 9:50 am.
- Chief of staff: inbox sweep weekdays 7:20 am and 12:20 pm; review Sun 5 pm.
- GitHub Actions do the public-data pulls, the voice and render steps and the site checks (.github/workflows/).

## Folders that matter now
| Folder | Holds |
|---|---|
| coo/ | constitution, decisions, handoff, strategy and reviews |
| .claude/skills/ | one folder per live job; retired skills go to archive/skills/ |
| tools/ | deterministic code and every gate (tools/README.md; gate files sealed in tools/gate_seal.json) |
| video/studio/ | the video line: its own router (CLAUDE.md), stage contracts, gates (prompts/), lessons (videos/) |
| site/, docs/ | site inputs, and the published site built by tools/make_site.py (never hand-edit docs/) |
| seo/ | question pages, store gates, results log |
| permits/, prospects/, probes/ | public data pulls, sealed prospect data, data probes |
| email/, legal/, launches/, design/ | templates and send rules, Legal desk, product launch files, design standards |
| scout/, research/, kimi/ | outside research, scouting, Kimi jobs |
| archive/ | everything retired; no run reads it |

## Gates, in order, for anything a buyer sees
1. Built from the templates in tools/ or the stage contracts in video/studio/.
2. `python3 tools/check_repo.py` exits 0 (planted-failure tests included).
3. Fresh reviewers that never saw the build (facts, copy, design and the rest named in the SKILL).
4. Legal desk (legal/README.md) where the SKILL names it.
5. Todd's word in chat, except minor site changes and the standing rules in the constitution.
