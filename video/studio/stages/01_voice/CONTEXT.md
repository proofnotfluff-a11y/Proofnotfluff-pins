# 01_voice: plan, then the voice

**Reads:** the data file the video is about (for a Rat check, `permits/rodents-chicago/weekly.json`), `_shared/voice.md`, `_shared/desk.md`, `_shared/kit.md`
**Makes:** `01_voice/brief.md`, `01_voice/script.md`, then (in the workflow) `01_voice/takes.json` and the audio

1. Plan before a word of script. `brief.md` answers: the format (`- **Format:** v2`, Lead Clinic v2 in `_shared/voice.md`: drop-in, play it out, the fix, proof, button; 40 to 50 s), where it posts (Instagram Reel, 9:16), the audience
   (a small Chicago trade owner on a phone), the one idea, the numbers (each with its path in the data file and the
   value as shown), the real screens worth showing, the metaphor only if one earns its place, the voice.
   Evidence comes from the trades (Todd, Oct 28, 7:38 pm): pick the lesson from research/runs/2026-10-28-trades-insights.md
   (what trades creators teach that lands, each backed by trade data, trade press or a trade association). No study from
   another industry as the main evidence, and no "this isn't the trades" caveat: if the trades have no number, find one or
   teach a different lesson. The brief names the creators who teach it and the visual world (`_shared/sets.md`).
2. Write `script.md` as talk (`_shared/voice.md`): one paragraph per beat (100 to 135 words in all; `anim.py script <slug>` checks a v2 script), 2 to 4 sentences each, delivery tags in
   square brackets, a stressed word in capitals at most once a paragraph. Numbers are written the way they are said
   ("forty-five", "two hundred twenty-one percent"); the brief holds the digits.
3. `python3 video/studio/anim.py speak <slug>` writes `01_voice/speak.json`; pushing it runs the Studio voice workflow
   (ElevenLabs Eleven v4, the voice in `_shared/voice.md`, one request per paragraph with the paragraphs around it as
   context). `--take N` re-rolls one take and keeps the rest.

**Check:** listen to the whole take. Every number heard as written in the brief; no take sounds clipped or rushed.
A take that sounds off is re-rolled; the script changes only when the words are wrong.
