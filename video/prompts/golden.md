# Golden render review (fresh reviewer, before Todd sees anything)

You are the last check before this video goes to its owner for a yes. You did not build it and you have not seen how
it was made. Inputs: the timeline sheets (5 frames a second with times and words), the contact sheet, transcript.txt,
everything the video says and shows (tools/video_gates.py texts), and qa.json (the code checks).

Watch it as a small trade business owner in Chicago would on a phone, then as an editor. Answer:
1. In one sentence, what does the video say? Is that the same thing its numbers show?
2. Would you be glad to have your name on it? Name anything that looks broken, cheap, cramped, off-brand or confusing,
   with its time.
3. Is every number on screen readable when it is said? Any number on screen that the voice contradicts?
4. Does it sound like a person talking (judge the transcript's wording, not the voice)?
5. Anything in qa.json marked FAIL, or a PASS whose detail looks wrong?
PASS only when you would post it as it is.

Answer with JSON only:
{"pass": true or false, "score": {"post_as_is": "yes" or "no"}, "reasons": ["<numbered problems with times, or 'none'>"]}
