# Trial: the host-below layout (Nov 15, 2026)

Not a lesson. It is not in videos/, not in the queue and cannot post: no format, gate, rule or anim.py line knows it.
Why it exists: Todd, live chat, Nov 15, 2026, about 11:19 am, picked "Yes, pixel Todd (Recommended)"; 11:29 am: "Make it look like the guy we are already using: the hat the beard etc" (coo/DECISIONS-2026-11-15.md).

## What it is
A 51.9 s video, 1080 x 1920. Bottom: the studio's own host (kit.js `k.snow`, unchanged), drawn large, saying "I" for ProofNotFluff, his mouth on the voice. Middle: one or two words at a time, on the spoken word. Top: the real thing being talked about (captures of our own results file, three frames of our own posted lessons) or a card drawn from the file's numbers. Voice: the lessons' ElevenLabs voice. Story: what the Nov 13 heat read of 529 YouTube videos found.

## Reads
- ../../heat/2026-11-13-results.json and ../../heat/queries.json: every number (make_data.py turns them into video/data.js; nothing is typed).
- voice/script.md: the words. One paragraph is one take.
- video/shots.js: where each line the video points at sits in the capture, written by capture.py from the raw file page on GitHub (the page's text is compared with the repo's file before it is kept).
- ../../../_runtime/kit.js, looks.js, pixfont.js: the host and his palette, as they are.

## Does
1. `python3 make_data.py`: the numbers.
2. Push voice/speak.json: the Studio trial voice workflow (.github/workflows/studio-trial-voice.yml) runs `voice/voice.py ci`, which reuses anim.py's voice code unchanged, and puts the audio and the heard words on the throwaway branch trial-voice. Nothing lands on main.
3. `python3 voice/voice.py words DIR`, `tighten DIR`, `mouth DIR RHUBARB`: word times; dead air cut (silence only) and the take played 1.06 times as fast; mouth shapes from Rhubarb Lip Sync 1.13.0 (MIT, run in the chat's own workspace), shut on silent frames.
4. `python3 capture.py`: the captures (video/shots/, not kept in the repo: 3 MB) and three lesson frames (video/lessons/).
5. `python3 verify.py`: works every spoken and shown number out again from the two heat files, checks the captions against the script and the captures against the repo's files (43 checks). Three planted wrong numbers were caught in a throwaway copy.
6. `python3 stills.py OUT t1 t2 ...`: full-size frames to look at before a render.
7. `python3 render.py OUT VOICE_WAV`: the MP4 (about 50 s to draw). It stays off main.
8. `python3 pack.py MP4 OUT`: what a fresh reviewer gets (frames cut from the finished MP4, the words as heard, copies of the source files) and the code checks on the MP4.

## Writes
voice/words.json, voice/transcript.md, video/words.js, video/mouth.js, video/data.js, video/shots.js, video/lessons/. Reviews: reviews/r0.json, r1.json.

## What was studied first (Nov 15)
- The studio's own reads: WATCH-2026-11-11.md (winners: the voice at 0:00, a new shot every 3 to 6 s, 1 to 4 words centered, exact numbers, a result at the end), VIRALITY-2026-11.md (a settled frame 0 with the stake on it, a first change by 0.6 s, a spoken hook of 8 words or fewer), the Nov 13 trial's three review rounds (a hook needs somebody's own stake; no end card).
- The Research Wiki rows for the creator's reels (Sources, Nov 13 and Nov 15) and Rhubarb (Tools, on watch).
- Outside reading on the day: the apps' covered areas on a 1080 x 1920 frame (top about 220 px, bottom 320 to 450 px, a right column of buttons), word-by-word captions (1 to 3 words, bold, near the middle), Rhubarb's nine mouth shapes and the rule that a mouth may lead the sound but not lag it.

## Where it stands
Two review rounds, two fails. It waits for Todd. Nothing was posted, queued or scheduled. Detail: reviews/r0.json, reviews/r1.json.

## Not checked by anyone
- Nobody has listened to the voice: the checks are Whisper's word match (no flag on the final take) and sound levels. Todd's ears are the first.
- The heat read itself (the counts in the results file, and the grouping of hot videos into topics, which was a reading of sealed titles in the Nov 13 chat).
- The three lesson frames are drawn today by the studio's player from each lesson's own files; the posted MP4s are not kept in the repo.
