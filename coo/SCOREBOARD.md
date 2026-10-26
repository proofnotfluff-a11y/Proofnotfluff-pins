# Scoreboard data (from Oct 17, 2026)

The scoreboard is the claude.ai artifact https://claude.ai/artifact/N9eKZy7Pv39njSe4izVgbE. Todd's words, Oct 17, 2026, 7:42 pm: "Etsy still lives but our focus is now to actually make money and win in the market." The page's first screen answers one question: are we making money, and what is moving it.

Page order: money board (month revenue against the $1,000 goal, paying subscribers, MRR, products live, emails sent, the road to the first $1,000 month, the next money move, level and XP), the product line (status, launch gates, outreach funnel), quests, pins to pick (only when a pin week is active), the crew (Active and Paused), Etsy on autopilot (deliberately quiet), the run log, how XP works. The canvas "Factory floor" view was retired in this redesign.

## Who keeps what current

- **COO (5:00 am):** keeps `meta/money` and every `leadproducts/<slug>` doc current every morning. Read each doc first and pin the write to the version you read. Never write a buyer's, prospect's or commenter's name, email or company to the scoreboard: counts only.
- **Live session:** adds a `leadproducts` doc when a new product enters the line, and updates gates as boxes in design/LAUNCH_CHECKLIST.md get ticked (the proof stays in `launches/<slug>.md`).
- Every other run keeps writing what it wrote before (days, agents, log, quests, pinweeks, shorts, stores, meta/shop). Nothing about those shapes changed.

## leadproducts/<slug> (one doc per product in the line)

Slug matches `launches/<slug>.md` where one exists. Seeded Oct 17: `chicago-construction-cleaning-leads`, `chicago-restaurant-leads`, `austin-construction-cleaning-leads`, `chicago-new-business-licenses`, `seattle-permits`.

| Field | Type | Meaning |
|---|---|---|
| name | string | Product name as buyers see it. Required: a doc without `name` is ignored. |
| city | string | "Chicago", "Austin", ... |
| buyer | string | Who pays, in plain words ("Post-construction cleaning companies"). |
| price | number | Monthly price in dollars. 0 when not set. |
| priceNote | string | Shown when price is 0 ("$29 to $49 a month, planned"). |
| status | string | `live`, `gates` (next through the launch gates), `building`, `planned`, `paused`, `dropped`. Live products get the wide card. |
| order | number | Position within the same status. |
| launchedAt | "YYYY-MM-DD" | Day it launched (every checklist box ticked). Counts as a launch for XP. |
| gumroadUrl, freePageUrl | string | Checkout page and free sample page. |
| subscribers | number | Paying subscribers now. |
| mrr | number | Monthly recurring revenue in dollars. |
| revenueMonth | number | Dollars collected this calendar month. |
| revenueTotal | number | Dollars collected since launch. |
| gates | object | `{product:[done,total], storefront:[done,total], buy:[done,total], outreach:[done,total]}` from design/LAUNCH_CHECKLIST.md: 5, 5, 3 and 2 boxes. A gate passes when done equals total. |
| outreach | object | `{prospects, drafted, sent, replies, payers, formOnly, queued, weeks, nextSend:"YYYY-MM-DD"}`. `weeks` is outreach weeks used so far (the judge rule is 3 weeks, about 120 emails). `nextSend` drives the "Next money move" line. |
| thisWeek | string | One line: this week's list or status. |
| next | string | One line: the next step and who does it. |
| updatedAt | ISO time | When the doc was last written. |

## todos/<id> (Todd's project to-do list, from Oct 23, 2026)

Todd's words, Oct 23, 9:33 am: "add a project to-do list to the artifact so I know exactly what's outstanding. With all the parallel chats going on, it's hard for me to keep track." The panel sits right under the money board, grouped by project.

Every live chat and scheduled run that finishes, starts, blocks or adds a task updates its row before it ends (ArtifactData, pinned to the version it read): set `done: true` and `doneAt` when finished, change `state` or `detail` when it moves, add a new row for new work. Never delete a row; Todd ticks his own. Plain words, no names of prospects or buyers, no em or en dashes.

| Field | Type | Meaning |
|---|---|---|
| title | string | The task, starting with a verb. Required. |
| detail | string | One or two sentences: what and why, what unblocks it. |
| project | string | Group heading ("Lead lists: sales and outreach", "New business licenses list", "Growth plan, steps 3 and 4", "Data checks and the site", "Business admin and legal"). |
| projectOrder | number | Group position. |
| owner | string | `todd` or `claude`. |
| state | string | `now`, `next`, `later` or `waiting` (blocked on an event). |
| order | number | Position within the group and state. |
| where | string | Where it happens ("Gumroad, your account", "Needs a chat from you"). |
| due | "YYYY-MM-DD" | Optional. |
| done, doneAt | bool, ISO time | Ticked off. |
| updatedAt | ISO time | Last write. |

## meta/money (one doc)

| Field | Type | Meaning |
|---|---|---|
| subscribers | number | Paying subscribers across all lead products. |
| mrr | number | Total monthly recurring revenue in dollars. |
| revenueMonth | number | All ProofNotFluff revenue collected this calendar month (Gumroad and anything else; Etsy days still add to XP separately). |
| month | "YYYY-MM" | The month `revenueMonth` belongs to. When it is not the current Chicago month, the page shows $0 and says the next run fills it in, so roll it over on the 1st. |
| revenueTotal | number | Lead-product revenue collected to date. |
| goal | number | 1000 (the first $1,000 month, VENTURE ENGINE). |
| goalDate | "YYYY-MM-DD" | "2027-01-31". |
| updatedAt | ISO time | Shown as "Money as of ...". |

If `meta/money` is missing, the page adds up the product docs instead.

## Crew: Active and Paused

The page splits `agents/<slug>` docs into Active and Paused. An agents doc with `paused: true` or `paused: false` decides it; otherwise a schedule that starts with "Paused" means paused; otherwise the Oct 17 list counts as paused (factory, rnd, shop-run, afternoon-promote, editions, redesign). When a run is turned back on, write `paused: false` on its agents doc so it moves back to Active.

## XP (money and launches first)

Paying subscriber +1,000, product launch +2,500, launch gate passed +250, every $1 of revenue +10, outreach reply +50, email sent +5. Etsy and promo work still count but small: order +100, review +50, new listing +10, favorite +5, Short +3, pin +2, visit +1, post +1, every 100 Short views +1. Quests keep their own XP. Levels: 1 Open sign (0), 2 Street team (2,000), 3 First route (5,000), 4 Corner shop (10,000), 5 Main Street (20,000), 6 City desk (35,000), 7 Two cities (55,000), 8 Regional (80,000), 9 Market leader (120,000), 10 Flagship (180,000).

## meta/traffic (website traffic, from Oct 26, 2026)

Todd's ask, Oct 26: "How do we monitor how much traffic we're actually getting into the website and how many of these calculators and features, free features, are actually bringing traffic in?" Go, 11:02 am: "Go with your recommendation". The panel "Website traffic" sits under the to-do list. The doc is seo/traffic/weekly.json exactly as tools/traffic_report.py writes it (Mondays, .github/workflows/traffic-weekly.yml), copied by the traffic-report run (.claude/skills/traffic-report/SKILL.md, Mondays 7:35 am): {ok, reason, fetchedAt, week {from, to}, totals {visits, views, prevVisits, change, search, uses, upgrades, pagesWithVisits, livePages}, sources [{label, visits}], trend [{week, visits}], pages [{slug, name, kind, published, staged, visits, views, prev, search, uses, upgrades, gImpr, gClicks, gPos}], flags {zero, new, zeroWeeks}, search {date, clicks, impressions}}. Counts only.
