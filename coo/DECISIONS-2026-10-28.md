# Decisions, Oct 28, 2026 (live chat with Todd)

## Video engine spec gaps, 3:43 am

- [stated] Todd: "Go with recs" (to the four open questions from the video engine build chat, each sent with a recommendation).
- So: (1) story type D's floor is 20 complaints, like A and C (video/config.json floors). (2) The date a video names is the rat file's own window.to, the last whole day counted, never the post date. (3) The golden South Chicago render (video/specs/2026-10-27-rats-a.json) is the reference for the first send test and is never posted; the first post is Monday Nov 2 from that week's data. (4) A gate rerun forced by another gate's fix starts that gate at round 0 again (review "rerunAfter"); a gate's own second FAIL still drops the video.
- Still open: the narration route needs Todd's ELEVENLABS_API_KEY repo secret ("key added").
