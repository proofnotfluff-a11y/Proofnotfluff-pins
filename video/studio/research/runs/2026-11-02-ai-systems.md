# Run 2026-11-02: AI lane systems (Monday research run, cloud lunch)

Brief: 5 new AI lane lesson ideas, each a system a small trade owner sets up in under 30 minutes, no code, free tier or a
tool he already pays for (lanes.md "Systems, not tricks"); 2 YouTube Shorts outliers for FORMULA.md. Every page below was
read on Nov 2, 2026 (date from bash, America/Chicago). Prices are as printed on the maker's own page that day. Forum
threads: business owners only, no names. Nothing here was run end to end yet: each lesson still needs its real run
(lanes.md item 3) before a script uses it.

Checked against IDEAS.md so nothing repeats: missed-call text-back, AI receptionist, quote from your price list, review
ask and review replies, quote follow-up, after-hours reply, notes to quote and the morning owner briefing are already
there. These five are new jobs.

## 1. unknown-caller-screen: the phone asks a stranger why he is calling (iPhone, free)

- **Trigger:** a call from a number not in Contacts.
- **Tool:** iPhone Phone app, Screen Unknown Callers, Ask Reason for Calling (built in).
- **Setting path:** Settings > Apps > Phone > Screen Unknown Callers > Ask Reason for Calling (Apple Support, Manage
  unknown callers on iPhone).
- **What happens:** the caller is asked who they are and why they are calling before the phone rings; the owner sees the
  answer as text and picks up, declines or asks for more (Apple page; MacRumors how-to for the on-screen part).
- **Where it lands:** on his lock screen, as text, while the caller holds.
- **The one thing he checks:** that every customer, supplier and crew number is saved in Contacts, since saved contacts
  always ring through (Apple page). Also: no screening while roaming (Apple page).
- **Price:** free, part of the iPhone Phone app; Apple's page says standard calling and data rates may apply. Read Nov 2,
  2026: https://support.apple.com/111106
- **Version:** Apple's page names no minimum version for this option. Third party (MacRumors) says iOS 26:
  https://www.macrumors.com/how-to/iphone-ask-someone-calling-before-pick-up . Say "on a recent iPhone update" unless the
  Apple page says more on the day of the lesson. Android (Pixel Call Screen) not checked this run.
- **Owner asking for it:** Contractor Talk, "What do you have to do to stop home adviser and angies list calling you?":
  lead-seller calls from changing numbers, three or four a week despite the Do Not Call list; another contractor answers
  every call to the office so the junk calls cost him time. https://www.contractortalk.com/posts/2126015 (no post date
  shown on the page).
- **Honest catch to say:** a real customer may hang up on a robot question. KNOWLEDGE row 11 (Hiya: 86% of unidentified
  calls unanswered) is the other side of the same coin; pair this lesson with the missed-call text-back, not instead of it.

## 2. rain-day-check: a scheduled ChatGPT task reads the week's weather against your outdoor jobs

- **Trigger:** a schedule, for example every Sunday at 6 pm.
- **Tool:** ChatGPT scheduled tasks.
- **Setting path:** ChatGPT sidebar > Scheduled > new task, pick the time (web and mobile); or type the ask in a chat.
  Manage all tasks: Settings > Notifications > Manage tasks (OpenAI help, Scheduled tasks in ChatGPT).
- **Prompt (draft, our words):** "Every Sunday at 6 pm: check the forecast for [town, zip] for Monday to Saturday. List
  each day with rain chance, wind and low temperature. Flag any day with rain chance at or over [50]% or a low under
  [50] F, because I paint exteriors. Name the forecast source you used." Numbers in brackets are his own limits.
- **Where it lands:** push, email or both, set in ChatGPT web Notifications (OpenAI help).
- **The one thing he checks:** the source it names and the day it flagged, against his own weather app, before he moves a
  customer. Not verified this run: that a scheduled task reads a live forecast. The real run must show it.
- **Price:** OpenAI help lists scheduled tasks for Plus, Pro, Business and Enterprise (Go with a 3 task limit; Plus 5
  active tasks). ChatGPT Plus "$20/month" on OpenAI's own help page: https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus
  Tasks help: https://help.openai.com/en/articles/10291617 . The pricing page https://chatgpt.com/pricing?hsLang=en
  printed no dollar amounts in the fetched text and marks scheduled tasks "No" for Free. Read Nov 2, 2026. Go price not read.
- **Owner asking for it:** ArboristSite, "When to make the decision to postpone a job due to weather": an owner called off
  a crane job the night before for forecast storms, the day came clear, and he asks how others decide.
  https://www.arboristsite.com/threads/when-to-make-the-decision-to-postpone-a-job-due-to-weather.345540/
  Also a Jobber Community reply on non-stop rain and jobs that need dry ground (thread parent could not be opened):
  https://community.getjobber.com/discussions/green-and-exterior-services/what-to-do-when-it-wont-stop-raining-and-all-your-upcoming-jobs-rely-on-dry-weat/11179/replies/11198

## 3. supplier-price-watch: every supplier invoice goes into one ChatGPT project that flags price changes

- **Trigger:** a new supplier invoice (paper photo or PDF).
- **Tool:** a ChatGPT Project holding his price sheet, with project instructions.
- **Setting path:** sidebar > New project > name it "Supplier prices"; three dots, top right > project instructions;
  upload his current price sheet as a file (OpenAI help, Using projects in ChatGPT).
- **Instructions (draft, our words):** "When I upload a supplier invoice, list every line whose unit price differs from my
  price sheet: item, old price, new price, percent change. Then list items not on my sheet. Do not guess a price you
  cannot read; say unreadable."
- **Where it lands:** in the chat, then he updates his price sheet and his quote template.
- **The one thing he checks:** each flagged line against the paper invoice; a misread digit is the likely error.
- **Price:** Projects are on all plans including Free; Free holds 5 files per project, Go and Plus 25 (OpenAI help, read
  Nov 2, 2026): https://intercom.help/openai/en/articles/10169521-using-projects-in-chatgpt . Free plan: $0 (no paid plan
  needed for this setup). On Free, keep one price sheet file and upload invoices into the chat, not the project.
- **Owner asking for it:** CompanyCam Community, "How have you implemented AI into your business?" (Nov 2025): a
  remodeler uses AI daily for material list reviews and material price checks. https://community.companycam.com/posts/456
  Jobber Community, "ChatGPT with Jobber": an owner already turns wholesaler invoices into price-free lists and asks what
  else works. https://community.getjobber.com/discussions/operations-forum/chatgpt-with-jobber/226

## 4. manual-desk: a Claude project that answers only from the manuals you load

- **Trigger:** a tech on site texts "what does this error code mean on the X unit" or "what clearance does this need".
- **Tool:** a Claude Project with the maker's install and service manuals as project knowledge, and project instructions.
- **Setting path:** Claude > Projects > create a project; upload the PDFs to the project's knowledge; set project
  instructions (Claude Help Center, What are projects?). Exact menu labels to be read on screen in the real run.
- **Instructions (draft, our words):** "Answer only from the manuals in this project. Give the manual name and page for
  every answer. If the manuals do not say, answer: not in the manual, call the maker's tech line."
- **Where it lands:** in the Claude app on his phone; he forwards the answer with its page number to the tech.
- **The one thing he checks:** the page it cites, opened in the manual, before anyone acts on it. Code and safety rules
  still win over a manual summary.
- **Price:** Claude Free "$0", Pro "$17" a month billed annually ("$200 billed up front") or "$20 if billed monthly";
  Free gets up to 5 projects. https://claude.com/pricing and https://support.claude.com/en/articles/9517075-what-are-projects
  read Nov 2, 2026. File size limits not printed on that page.
- **Owner asking for it:** Heating Help, "ChatGPT, AI" (Feb 4, 2026): a tradesman says a new apprentice got a wrong
  answer from ChatGPT and asks if anyone uses AI for installation steps; a reply says keep it to maker sources.
  https://forum.heatinghelp.com/discussion/comment/1886204 . Jobber Community "ChatGPT with Jobber" (link above): an
  owner uploads long technical manuals and asks about specific equipment.

## 5. money-monday: ask Jobber AI the same three money questions every Monday

- **Trigger:** Monday morning, a phone reminder.
- **Tool:** Jobber AI chat, inside Jobber (sparkle icon), which he already pays for. Jobber calls it Beta.
- **Setting path:** no setting to turn on; open Jobber AI with the sparkle icon. Business questions and actions are for
  admin users only (Jobber Help, Jobber AI Voice and Chat (Beta)).
- **Prompt (draft, our words):** "Which invoices are past due, oldest first, with amounts? Which quotes sent over 7 days
  ago have no answer? How much did I invoice last week compared with the week before?" The real run must show which of
  these it can answer; Jobber's pages do not list example questions.
- **Where it lands:** in the Jobber app, with the clients to call that day.
- **The one thing he checks:** one total against Jobber's own report before he chases anyone.
- **Price:** Jobber help: "Jobber AI is available on all plans." Jobber pricing page, Core 1 user: $49/mo no commitment,
  $29/mo billed annually; AI Receptionist add-on $29/mo listed separately. https://help.getjobber.com/en/articles/jobber-ai-voice-and-chat-beta/
  and https://getjobber.com/pricing-plans/ read Nov 2, 2026. Say "in beta".
- **Owner asking for it:** Jobber Community "ChatGPT with Jobber" (link above): the owner exports Jobber CSV reports into
  ChatGPT to read them; this does the same inside Jobber with no export.

## YouTube Shorts outliers: not found this run

Goal: 2 public Shorts (trade owners or AI for small business) whose page prints far more views than the channel's usual.
- YouTube pages fetched (for example https://www.youtube.com/shorts/NRqPuxTJAF8 , found by search for AI receptionist
  plumbing Shorts) return only the page shell: no views, channel or subscriber counts. Same as the Nov 1 run.
- Direct requests to YouTube and to third-party count services from the shell were blocked by the proxy or the
  environment's safety check; not pushed further.
- Text sources tried: vidIQ channel stats (plumberparts: 386K subscribers, 93,561,234 total views, stats dated Aug 8,
  2025, no per-Short counts) https://vidiq.com/youtube-stats/channel/UCwF8vOEatNvJUiXXJtDx-zA ; vuela.ai weekly breakout
  AI Shorts table (week of Nov 2, 2026; prints views, subscribers and URLs, but every entry is AI entertainment, none trade
  or small business) https://vuela.ai/data-studies/viral-ai-shorts ; HomePros News viral contractor videos (Apr 16, 2026;
  Instagram and TikTok only, no YouTube) https://homepros.news/7-hvac-and-plumbing-contractor-videos-that-went-viral/
- Next try: Todd reads two Shorts in the YouTube app (views on the Short against the channel's Shorts tab) and sends
  screenshots, as the Instagram references were filed Nov 1.

## Could not open (permission prompt timed out)
- https://chatgpt.com/pricing (opened with ?hsLang=en instead), https://claude.com/pricing first try (later opened),
  https://www.getjobber.com/pricing/ (opened https://getjobber.com/pricing-plans/ instead), the Jobber Community rain
  thread parent page.
