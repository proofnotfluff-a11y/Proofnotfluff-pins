# Lab: the 3D look test

Todd, live chat, Nov 9, 2026, 10:38 pm: "Go" (to one 20 to 30 second 3D version of a story; coo/DECISIONS-2026-11-09.md).
A lab, not the engine: nothing here posts, and no v4 rule, gate or format changes because of it until Todd says so.

- `film.py`: the turned-down-8k story as a Blender film written in code (Blender's free Python module, `pip install bpy`).
  Every object, light and camera is a function of film seconds, so any slice of frames renders on its own.
- `assemble.py`: puts the lesson's voice and the big v4 captions on the silent render.
- `jobs/<name>.json`: pushing one makes the workflow `.github/workflows/studio-render3d.yml` render the film in parallel
  slices on GitHub's runners (CPU only, no secrets) and publish `film-silent.mp4` and `log.txt` to the `video-renders`
  branch under `studio/lab3d/<name>/`.
- `fonts/`: Poppins Bold and Medium (SIL Open Font License 1.1, Indian Type Foundry; free to bundle and use).

Preview a sheet locally: `python3 film.py --res 360 --spp 8 --jpg --out /tmp/prev --times 0.5,5.6,13.6,18.8,24.1,27.5`.
