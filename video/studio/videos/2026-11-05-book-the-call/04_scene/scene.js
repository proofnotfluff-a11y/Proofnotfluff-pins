// Scene: one function per top-level cue in 03_cues/cues.md. Draw with the kit (k); numbers only from k.data.
window.SCENE = {
  look: 'clean',
  images: [],
  sections: {
    hook: (k, T) => {
      k.title('Replace me', 320);
      return {hostPose: k.talking() ? 'talk' : 'stand'};
    },
  },
};
