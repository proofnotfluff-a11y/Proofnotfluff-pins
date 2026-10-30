// Scene: one function per top-level cue in 03_cues/cues.md. Draw with the kit (k); numbers only from k.data.
// The hook (stages/04_scene/CONTEXT.md 3): frame 0 is the cover with no host; cut to a new shot by 1 s and again before
// 3 s, host on by 3 s (anim.py hook). Lesson 3's scene.js is the worked example.
window.SCENE = {
  look: 'clean',
  images: [],
  sendLine: 'Send this to whoever pays for your Google ads.',   // the end card's send line (Lead Clinic v2: no spoken call to action)
  sections: {
    hook: (k, T) => {
      k.title('Replace me', 320);
      return {hostPose: k.talking() ? 'talk' : 'stand'};
    },
  },
};
