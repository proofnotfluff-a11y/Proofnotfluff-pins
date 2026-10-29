You are a skeptical second reviewer. Answer in under 450 words, plain text, no em dashes. Use only what is below plus well established public facts; say "unsure" where you are.

QUESTION
Should ProofNotFluff (PNF) build and sell a trades version of "Harvey", or skip it? Give: build, skip, or a narrower variant; the 3 biggest risks; which of my claims below are wrong; and one thing I missed.

ABOUT PNF (facts, Oct 29, 2026)
- One-person business in Chicago. Audience: owners of small B2B trade businesses (post-construction and commercial cleaning, pest control, hood cleaning).
- Sells public-records lead lists: Chicago and Austin construction cleaning leads $29/month, restaurant inspection leads $39/month, a $149/month exclusive "seat" per trade and area (max 3 per area). Data: city permits, health inspections, business licenses. 719 current Chicago general-contractor permit leads.
- Its own cold email to trade owners (plain text, under 75 words, names a real permit record, asks permission): 61 sent, 0 replies, 0 payers. SPF, DKIM, DMARC pass and test mail lands in the inbox. Of 291 prospects found, 132 had only a contact form, no email.
- Rules: $0 spend without the owner's yes; nothing deceptive; no platform terms broken.

ABOUT HARVEY (read from its public GitHub repo, MIT license)
- Local Python app. You give it your website; it finds businesses (default free OpenStreetMap, paid DataForSEO, Serper etc.), reads their sites for 29 "signals" (no website, running ads, no online booking, hiring, rank), finds a contact, writes cold email, sends from your Gmail or Microsoft 365, reads replies, drafts answers, books meetings, every 15 minutes. Approval mode by default, autopilot optional. Deterministic pre-send gate, opt-out handling, warmup ramp, bounce kill switch, CAN-SPAM footer.
- Runs model calls through the user's own Claude Code or ChatGPT/Codex subscription, so no API bill.
- Needs Python 3.11, the Claude CLI logged in, a dedicated sending domain, SPF/DKIM/DMARC and 2 to 4 weeks of mailbox warmup.
- Its own README says OpenStreetMap lists under 2,000 roofers and under 2,300 plumbers in the whole US. Its scorer rates generic inboxes (info@) as poor prospects.
- Anthropic's Claude Code legal page: developers building products or services should use API keys; they may not route requests through Free, Pro or Max credentials on behalf of their users, and may not resell or intermediate Claude usage for end users.

MY FIRST-PRINCIPLES READ (critique it)
1. Harvey's signals mostly tell you who to sell marketing or software TO a trade business, not who a trade business should sell to. It is a tool for agencies, not for plumbers.
2. Residential trades win work through inbound (Google, Local Services Ads, reviews, referrals, Angi); cold emailing homeowners is not viable. Outbound only fits B2B trades selling to GCs, property managers, restaurants. That is exactly PNF's audience.
3. Trade owners will not install a Python agent, buy a domain and warm a mailbox. DIY does not sell to them.
4. The "no API bill" edge disappears for a service PNF runs for customers: it must pay API rates.
5. PNF has not yet proven cold email works for its own buyers (61 sent, 0 replies). Selling an outbound agent before that is selling a promise.
6. The real gap for a B2B trade owner is the "why now" reason and the first touch: a permit, failed inspection or new license matched to them, plus a ready-to-send message. PNF already has the records.
Proposed instead: skip the Harvey clone; add a ready-to-send first message (email, letter or call script) to each record in the existing $149 seat; borrow Harvey's MIT-licensed reply classifier and opt-out handling for PNF's own inbox work; revisit a done-for-you sending service only after PNF's own outreach gets replies.
