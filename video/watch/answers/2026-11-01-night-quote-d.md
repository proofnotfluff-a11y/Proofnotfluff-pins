# Video answer

- Source: https://www.youtube.com/watch?v=-keganwBIp8 (link sent to Google)
- Model: gemini-3.8-flash (generateContent)
- Gemini tokens: 95995

## Answer (Gemini's observations, not frames Claude viewed)

### Video Hook (00:00 to 00:10)

* **Heard (00:00 to 00:09):** The host states: "QuoteIQ, the best field service management software built specifically for home service contractors, just released a brand new AI feature inside of their business phone system, Client Hub."
* **Seen (00:00 to 00:02):** The presenter talks directly to the camera in front of an office background.
* **Seen (00:02 to 00:04):** An animated QuoteIQ logo appears on screen.
* **Seen (00:04 to 00:06):** A 3D render of an iPhone rotating into view.
* **Seen (00:06 to 00:10):** Three iPhone mockups display QuoteIQ app screens (mapping estimate, financial dashboard, and inspection form), followed by a zoom-in on the "Client Hub" screen featuring a phone number and "Call Forwarding" button.

---

### Video Beats and Timestamps

* **00:00 to 00:56:** Introduction to QuoteIQ, Client Hub, and the announcement of the "AI Auto-Reply" feature.
* **00:56 to 01:40:** High-level summary of the four actions the AI performs (Replies, Books, Drafts, Routes).
* **01:40 to 02:25:** Agenda overview (Part 1: Setup from scratch; Part 2: Six real-time customer testing scenarios).
* **02:25 to 11:41:** Part 1: Walkthrough of configuration settings inside QuoteIQ (Status and Review, Smart Level, Reply Timing, Reply Tone, Custom Instructions, AI Permissions, Escalation, Excluded Topics, Reply Cap).
* **11:41 to 14:50:** Part 2: Testing six live customer scenarios (General quote request, Appointment booking, Pricing query, Negative sentiment escalation, Excluded topic escalation, Reply cap handoff).
* **14:50 to 16:23:** Summary of key benefits, viewer discussion questions, and channel sign-off.

---

### Steps Taught in Order

The video does not demonstrate a standalone or free AI chat app (such as ChatGPT or Claude). It teaches how to configure the proprietary AI Auto-Reply system inside QuoteIQ's Client Hub through the following sequential steps:

1. **Access Settings (02:29 to 02:44):** Navigate to "Client Hub" on the desktop interface, click the "Configure" button, and select "AI Auto-Reply" from the dropdown.
2. **Status and Review (03:16 to 04:28):** Toggle on "Enable Auto-Reply". Decide whether to activate "Review Before Sending" (queues replies for manual approval) or "After Hours Only" (limits replies to non-business hours), then click "Save".
3. **Smart Level (04:29 to 05:25):** Select the AI intelligence depth from three tiers: "Acknowledge" (simple confirmation), "Contextual" (reads conversation and customer history), or "Full Service" (accesses past quotes, jobs, and account details).
4. **Reply Timing (05:25 to 05:54):** Select how quickly the AI sends responses: "Immediately", "5 minutes", "30 minutes", or "2 hours".
5. **Reply Tone (05:55 to 06:31):** Choose the voice persona: "Professional", "Friendly", "Casual", or "Match Customer".
6. **Custom Instructions (06:31 to 08:11):** Enter specific company guidelines, sales rules, or phrasing requirements into the freeform text box, then click "Save Instructions".
7. **AI Permissions (08:12 to 08:59):** Choose which actions the AI can independently execute by toggling any of five permissions: "Create deals", "Book appointments", "Draft estimates", "Draft invoices", or "Set reminders".
8. **Escalation Guardrails (09:21 to 10:05):** Under the "Escalation" menu, turn on "Smart Escalation" and toggle triggers for "Negative sentiment" (anger or complaints) and "Urgent requests" (emergencies or leaks).
9. **Excluded Topics (10:06 to 10:41):** Under "Excluded Topics", type and add specific sensitive subjects (such as refunds or legal issues) that the AI must never handle autonomously.
10. **Reply Cap (10:42 to 11:11):** Under "Reply Cap", select the maximum number of automated message turns allowed per customer thread (1, 2, 3, 5, 10, or unlimited) before routing to a human.

---

### Exact Wording of Prompts and Example Replies

#### Custom Instructions Prompt (07:11 to 07:16)
The presenter types the following text into the "Custom Instructions" input field:
> "Always mention that we're licensed and insured. If you're asked about pricing for a job or service, direct them to request an estimate."

*(Note: At 06:36, the placeholder text in the box reads: `e.g. "Always mention our 10% spring discount"`)*

#### Scenario 1: Quote Request (12:00 to 12:12)
* **Customer Message:** "Hey, looking for a quote on pressure washing my driveway and front walkway"
* **AI Reply:** "As Acme Company is licensed and insured, we'd be happy to provide a quote for pressure washing your driveway and front walkway. Please reply with 'YES' to confirm if you'd like to proceed with a draft estimate."

#### Scenario 2: Booking Request (12:33 to 12:47)
* **Customer Message:** "Can you come in Friday at 2PM?"
* **AI Reply:**  
  "Quick confirm before I send this to the owner:  
  - Service: pressure washing driveway and front walkway  
  - Service Address: 23 Crestwood Drive Savannah, Georgia 31405  
  - Time: Friday at 2:00 PM - 3:00 PM  
  - Name: Jimmy Johnson  
  - Phone: +1 [redacted]  
  Reply YES to confirm, or NO to change."
* **Customer Message:** "YES"
* **AI Reply:** "Great! I've sent your appointment request for pressure washing on 2026-05-22 at 2:00 PM to the owner for final approval. They'll confirm shortly."

#### Scenario 3: Pricing Question (13:09 to 13:22)
* **Customer Message:** "How much do you charge for a 1,500 square foot house wash?"
* **AI Reply:** "We'd be licensed and insured, and I can have someone get in touch with you to provide a quote for a 1,500 square foot house wash. Would you like to have the owner contact you?"

#### Scenario 4: Angry Customer Escalation (13:38 to 13:54)
* **Customer Messages:** "THIS IS RIDICULOUS! NO ONE HAS CALLED ME BACK ABOUT MY LAST APPOINTMENT! PATHETIC!", "I AM ANGRY", and "SOMEONE ANSWER OR IM GETTING ANGRIER"
* **System Notification Seen on Phone (13:50 to 13:54):**  
  "Auto-reply needs your help  
  Message from +19123086793 - Negative sentiment - owner needs to handle"

#### Scenario 5: Excluded Topic (14:12 to 14:20)
* **Customer Message:** "I want a refund on the last service"
* **System Notification Seen on Phone (14:16 to 14:20):**  
  "Auto-reply needs your help  
  Message from +19123086793 - Excluded topic detected: 'Refunds'"

#### Scenario 6: Reply Cap Conversation (14:36 to 14:44)
* **Customer Turn 1:** "Hello id like to get an estimate please"
* **AI Reply 1:** "Hello! We'd be interested in getting an estimate, Mr. Rogers! Our team would be happy to help with that. Since we're licensed and insured, we can promise a thorough and accurate estimate for your specific needs. Please reply with the best time and phone number to reach you, and our team will get in touch to discuss details."
* **Customer Turn 2:** "Are you available next week?"
* **AI Reply 2:** "We have availability next week, Mr. Rogers! Our business hours are Monday-Friday from 8 AM to 5 PM. Would you like to schedule something for one of those days?"
* **Customer Turn 3:** "Is every day open? Or is there anything on the schedule?"
* **AI Reply 3:** "We currently don't have open availability for appointments on Thursday, May 21st, Friday, May 22nd, Monday, May 25th, Tuesday, May 26th, and Wednesday, May 27th. All between 3:00 PM and 5:00 PM. Would you like to schedule an appointment during one of those times, Mr. Rogers?"
* **Customer Turn 4:** "yes" (The AI stops sending automated replies because the cap of 3 was reached, leaving the thread open for a human).

---

### What It Says to Check Before Sending

At 03:39 to 03:56, the presenter discusses the **"Review Before Sending"** setting:
* **Heard (03:41 to 03:48):** "When this is toggled on, every reply that the AI generates gets queued up for your first approval. You see the message, you approve it, and then it goes out."
* **Seen (03:44 to 03:48):** The on-screen tooltip states: "Review Before Sending: Drafts every reply and waits for you to approve, edit, or reject it from the Activity tab. Nothing goes to the customer until you tap Send. Use this when you want the AI to draft never auto-send."

---

### How the Video Ends (16:05 to 16:23)

* **Heard (16:05 to 16:17):** The host asks viewers to comment below explaining how they would configure the tool for their business, whether they find it useful, what custom instructions they would write, and which permissions they would enable first.
* **Heard (16:17 to 16:23):** "Thank you guys so much for watching Service Business Academy, I will see you in the next one."
* **Seen (16:17 to 16:23):** The presenter points both hands toward the camera, smiles, and the video ends.

---

### Evidence Shown vs. Claims Only Asserted

#### Claims Backed by Visual Evidence
* **System configuration workflow:** Demonstrates the QuoteIQ web interface, options, toggles, and saving process (02:29 to 11:38).
* **Adherence to custom prompts:** Verifies on screen that incoming quotes prompt replies mentioning "licensed and insured" and steering customers toward formal estimates (12:08 to 12:24, 13:14 to 13:24).
* **Calendar appointment booking:** Confirms an appointment requested via SMS creates an entry on the calendar grid at Friday at 2:00 PM (12:39 to 12:56).
* **Escalations and guardrails:** Displays live mobile push alerts triggered when a customer message registers negative sentiment ("I AM ANGRY") or an excluded keyword ("Refunds") (13:48 to 13:55, 14:15 to 14:20).
* **Reply cap limit:** Demonstrates that the AI ceases auto-replying after the third automated exchange (14:36 to 14:45).

#### Claims Asserted Without Evidence
* **Product superiority:** Asserts QuoteIQ is "the best field service management software" (00:00 to 00:03).
* **Business performance claims:** Claims that contractors who do not respond first are "bleeding leads to faster competitors" (02:15 to 02:19).
* **Financial return:** Claims that the automated booking feature "actually pays for itself in the first week of using this feature" (13:01 to 13:06).
* **Competitive impact:** Asserts that this feature "is going to eat your competitors who don't use it" and allows small operations to rival large companies (15:40 to 16:04).
* **Topic clarification:** The video does not show, test, or mention any free standalone AI chat apps (e.g., ChatGPT); it only showcases QuoteIQ's built-in, proprietary tool.
