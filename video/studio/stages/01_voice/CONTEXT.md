# 01_voice: plan, then the voice

**Reads:** the data file the video is about (for a Rat check, `permits/rodents-chicago/weekly.json`), `_shared/voice.md`, `_shared/desk.md`, `_shared/kit.md`
**Makes:** `01_voice/brief.md`, `01_voice/script.md`, then (in the workflow) `01_voice/takes.json` and the audio

1. Plan before a word of script. `brief.md` answers: where it posts (Instagram Reel, 9:16, 45 to 60 s), the audience
   (a small Chicago trade owner on a phone), the one idea, the numbers (each with its path in the data file and the
   value as shown), the real screens worth showing, the metaphor only if one earns its place, the voice.
2. Write `script.md` as talk (`_shared/voice.md`): one paragraph per take, 2 to 4 sentences each, delivery tags in
   square brackets, a stressed word in capitals at most once a paragraph. Numbers are written the way they are said
   ("forty-five", "two hundred twenty-one percent"); the brief holds the digits.
3. `python3 video/studio/anim.py speak <slug>` writes `01_voice/speak.json`; pushing it runs the Studio voice workflow
   (ElevenLabs Eleven v4, the voice in `_shared/voice.md`, one request per paragraph with the paragraphs around it as
   context). `--take N` re-rolls one take and keeps the rest.

**Check:** listen to the whole take. Every number heard as written in the brief; no take sounds clipped or rushed.
A take that sounds off is re-rolled; the script changes only when the words are wrong.
