# Script check: 2026-11-11-lsa-missed-calls (two-shops; viral-script human test and the 12-point check in _shared/voice.md)

Scored Oct 30, 2026 by the builder on script.md (119 words, 6 takes, 18 sentences) before the voice. Timing lines are
re-measured on the real words.json below. The script gate should re-score it blind.

## The human test (viral-script step 8)
- Read-aloud: PASS longest sentence 11 words; 17 of 18 sentences (94%) 10 words or fewer (bar 60%).
- Owner words: PASS 0 banned words; trade nouns in the opening: "call", "shops".
- Specific: PASS "Seven at night" and "two shops" in line 1; every number (7 pm, 9, 5, 15 days, 20 seconds, 1 and 0
  charged) has a facts.json key (example.* or google.*).
- Sameness: PASS opening "Seven at night. Same" differs from the last 6 openings ("Trade owners, top shops", "HVAC
  owners, most of", "Estimate's done, and they", "A move-out clean quote", "The demo says an", "This deep clean quote").
- Do this week: PASS four steps an owner can do this week, on screen and held (ad schedule only while a person answers;
  missed rings to a second phone; text back every missed call; Fridays, the Leads page's Charge Status).
- Ear test: PASS every sentence fits one breath (average 6.6 words); `anim.py script` PASS (2 tags, no "about").

## The 12-point check (format bands from _shared/formats.md: two-shops 35 to 52 s, 85 to 125 words)
1 drop-in: PASS 11 words ("Seven at night. Same call to two shops. Nobody picks up."), trade nouns "call" and "shops", no percent, no source, no call-out, no greeting
2 on-screen hook: PASS planned 6 words ("7 PM. Same call. Two shops."), settled on frame 0, held through the first two cuts to about 3.4 s, inside the safe area (measured by `anim.py hook` after the scene)
3 one idea: PASS 14 words in brief.md ("run your Local Services ads only in the hours someone answers the phone"); every beat serves it
4 acted: PASS shop one's path is acted on its half of the split screen (the phone rings, the ring bar runs past 20, voicemail, CHARGED stamps), not explained to camera
5 facts: PASS every number and rule maps to facts.json (google.missedSeconds 20, google.followUpDays 15, the ad schedule and voicemail rules, the four charge statuses; the shops, 7 pm, 9, 5, 1 and 0 are example.*, EXAMPLE on screen); page re-read Oct 30
6 artifact: PASS the four steps, each on screen as it is said (takes 3 and 4) and together on the close card, held 3 s or more
7 proof: PASS one sourced number after the fix (twenty seconds), the tag "Source: Google, How leads work" on screen while it is said
8 length: PASS 119 words (85 to 125); runtime measured after the voice (35 to 52 s)
9 talk test: PASS contractions in takes 2, 4 (That's, aren't) and "you" or "your" in takes 2, 4, 5; 0 banned words; 0 em or en dashes; no sentence over 20 words. Takes 1, 3 and 6 are the moment, shop two and the rule, written short on purpose
10 voice markup: PASS 2 tags ([matter-of-fact], [confident]), none soft; 0 CAPS words; no digits, $, %, / or & in the voice
11 no tail: PASS no turn line, no honest note, no spoken send, save, like, follow or comment ask
12 button: PASS last sentence "Run the ads only when somebody picks up." repeats "picks up" from the hook; SCENE.sendLine "Send this to whoever pays for your Google ads."

Result: 12 of 12 before the voice.

## After the voice (Oct 30, 2026, three Studio voice runs; flags 0 on each)
- Run 1 (all 6 takes): file wpm 146, 156, 160, 147, 184, 159. Takes 1, 2, 4, 6 under 160.
- Run 2 (re-roll of takes 1, 2, 4, 6, same words): 149, 156, 160, 149, 184, 154 (spoken, without the silent tail:
  158, 166, 169, 157, 192, 161).
- Run 3 (takes 1 and 4 rewritten as talk, voice.md "under 150: rewrite the take"; take 1 "Seven at night, same call,
  two shops." with commas, take 4 joined into two sentences): 133, 156, 160, 151, 184, 154 (spoken 139, 166, 169, 163,
  193, 161). Take 4 now clears the 150 floor; take 1 got slower.
- Held here: take 1 (the hook) failed the pace check three times (146, 149, 133 wpm on the file). The run's rule (a
  step that fails twice stops the run) holds the lesson at stage 02. Runtime on the current words 49.9 s with the end
  card (two-shops band 35 to 52); `anim.py cues` matches all 18 cues; `script` and `variety` PASS.
- Next for take 1: go back to the run 2 wording ("Seven at night. Same call to two shops. Nobody picks up.", 149 file,
  158 spoken), or a hook that flows as one sentence and still lands inside 9 to 12 words, then `speak --take 1` once.
  Takes 2 and 6 (156, 154 on the file; 166 and 161 spoken) sit under the 160 target only because of their silent tails
  (IMPROVE 00e).
