#!/usr/bin/env python3
"""Etsy listing video from a Short spec: 3 slides, 1080 x 2160 (1:2), about 13.8 s, no audio.

Etsy's rules (help.etsy.com article 360053206073, checked Oct 4, 2026): 3 to 15 seconds,
audio removed on upload, 100 MB max, at least 500 px (1080 recommended), 2:1 or 1:2,
up to 2 videos per listing.

Usage: python3 make_listing_video.py spec.json out.mp4 [--slides 0,2,4]
Default slides: the hook, the first stat or compare slide (else fix), and the CTA.
"""
import json, os, subprocess, sys, shutil
import make_slides as ms

W, H, SLIDE = 1080, 2160, 4.6
MAX_SECONDS, MAX_BYTES = 15.0, 100 * 1024 * 1024


def pick(slides, override=None):
    if override:
        return [slides[i] for i in override]
    hook = next((s for s in slides if s["type"] == "hook"), slides[0])
    mid = next((s for s in slides if s["type"] in ("stat", "compare")), None) or next((s for s in slides if s["type"] == "fix"), None)
    cta = next((s for s in slides if s["type"] == "cta"), slides[-1])
    return [s for s in (hook, mid, cta) if s is not None]


def main(spec_path, out, override=None):
    spec = ms.fix_cta(json.load(open(spec_path)))
    spec["slides"] = pick(spec["slides"], override)
    for s in spec["slides"]:
        if s["type"] == "cta":  # the buyer is already on Etsy, so no shop address here
            s["sub"] = spec.get("listing_cta_sub", "Instant digital download")
    ms.W, ms.H, ms.SLIDE = W, H, SLIDE  # the slide renderer reads these module globals
    total = len(spec["slides"]) * SLIDE
    if not 3 <= total <= MAX_SECONDS:
        sys.exit(f"duration {total:.1f}s is outside Etsy's 3 to 15 second window")
    work = os.path.join(ms.HERE, "work_lv"); os.makedirs(work, exist_ok=True)
    fdir = ms.render(ms.html(spec), int(total * ms.FPS), work)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(ms.FPS), "-i", os.path.join(fdir, "f%05d.png"),
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p", "-an",
                    "-t", f"{total:.2f}", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    size = os.path.getsize(out)
    if size > MAX_BYTES:
        sys.exit(f"{size} bytes is over Etsy's 100 MB limit")
    print(json.dumps({"out": out, "seconds": round(total, 1), "width": W, "height": H, "bytes": size, "slides": [s["type"] for s in spec["slides"]]}))


if __name__ == "__main__":
    args = sys.argv[1:]
    ov = None
    if "--slides" in args:
        i = args.index("--slides"); ov = [int(x) for x in args[i + 1].split(",")]; del args[i:i + 2]
    main(args[0], args[1], ov)
