# Gate: send test (fresh reviewer)
Why (Todd, live chat, Nov 1, 2026, 4:35 pm: "Do both", to a review gate that names who a viewer would send it to): on
Instagram, sends count most for people who don't follow us (Mosseri, Jan 2025), and people share what feels relevant to
them and to someone they know (Cosme et al., PNAS Nexus, Jan 2025). research/viral-science-2026-11-01.md has the rest.
The send moment (Todd, live chat, Nov 7, 2026, 9:27 am: "Write the next prompt to make adjustments and fix so the next
video improves", his yes to the send moment; coo/DECISIONS-2026-11-07.md): after-hours-robot and lsa-missed-calls held
viewers and stalled near 1,280 views with 0 or 1 share. From then on every story lesson and short puts one forwardable
thing on screen (the exact text to send back, the call script, the setting to change) for a named person in the owner's
shop, held still to screenshot, and this gate FAILS unless you can name both the person and the thing from the video alone.

You own a small trade business (pick the trade the lesson's example uses). The lesson just played in your feed. You get
only what a viewer gets from the video itself: V/02_transcript/transcript.md (ignore the pace table) and the timeline
sheets in V/05_render/gates/ (the end card is on the last one). Open no other file: not the brief, not the captions.

Be honest: most videos are never sent. A good tip you would keep for yourself is a save, not a send.
1. Would you send this to one real person in your life? Name them by role and tie ("my brother-in-law who runs a
   two-truck HVAC shop", "the partner who answers our phones"), never a group ("other contractors", "my network").
2. The line that makes you send it, quoted exactly from the transcript.
3. What sending it does for you: helps them with a problem you know they have, makes you look sharp, gets a laugh, or
   says "this is us". Pick one and say why in a sentence.
4. The feeling it carries: surprise, anger at a shared problem, amusement, relief, or none.
5. Would that person thank you, or read it as an ad or a lecture?
6. The end card's send line: does it point at the person you named or someone close to them? If not, write a better one
   in the lesson's plain voice ("Send this to ..."), under 12 words.
7. The thing on screen you would screenshot and forward: what it is in a few words, the exact on-screen text you can read
   on the sheets (quote it), and the sheet time where it sits still long enough to screenshot. "none" if nothing on
   screen is held still and readable as a thing to forward.
8. Who in the owner's shop the video itself says that thing is for (the role the voice or the screen names: whoever
   answers the phones, the office manager, a partner). "none" if the video never says.
PASS only when 1 names one person by role and tie, 2 quotes a real line, 3 is more than "it's useful", 4 is not none, 5
is thanks, 7 names a thing quoted from a sheet and held still, and 8 names one role. Otherwise FAIL with the line or frame
to change and a better one. Code then checks your 7 and 8 against what the lesson meant to send (`anim.py sendcheck`).
Do not edit files. JSON only: {"pass": bool, "score": {"person": "<role named in 8, or none>", "tie": "<role and tie from 1, or none>", "thing": "<what it is, then the quoted on-screen text from 7, or none>", "held_at": "<sheet time, or none>", "line": "<quote>", "gain": "helps|looks sharp|laugh|this is us|none", "feeling": "<one word>", "thanks": "yes|no", "send_line_fits": "yes|no"}, "reasons": ["<answers, then each problem with its line and a fix>"]}
