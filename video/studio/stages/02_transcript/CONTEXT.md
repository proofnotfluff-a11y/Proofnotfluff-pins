# 02_transcript: the words (our exposure sheet)

**Reads:** `01_voice/script.md`, the joined `voice.mp3` (in the workflow)
**Makes:** `02_transcript/words.json` (every word, its start and end in seconds, its take), `02_transcript/transcript.md`

1. Whisper times every word of `voice.mp3`.
2. The words are re-spelled from `script.md` (Whisper's spelling of a name or a number never wins), and every place
   the two disagree is flagged: a word the voice dropped, a word it added.
3. Pace per take in words a minute, against `_shared/voice.md`: under 150 gets "rewrite as talk", over 200 gets
   "give it a landing beat"; both re-roll that take.
4. Lip sync: `python3 video/studio/anim.py mouth <slug>` writes `02_transcript/mouth.js`, a mouth shape for every
   frame from the voice's loudness (stills, lint and render make it themselves when the voice is here). Commit it with
   the words; it is one of the fingerprints the gates pin.

**Check:** read `transcript.md`. No flags left, names and numbers right, pace in range. Fix a misheard word in
`words.json` by hand only when the audio says the script's word.
