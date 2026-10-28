#!/usr/bin/env python3
"""Word-timed transcript of a finished video's sound, for the render critic and the heard-hook check: faster-whisper
(MIT) on CPU, int8. The model files come from Hugging Face, so this runs only in the Video render workflow
(.github/workflows/video-render.yml), never in the cloud workspace.

Usage: python3 tools/video_transcribe.py VIDEO.mp4 --out transcript.json [--model small.en]
Writes {"schema": "pnf.video.transcript.v1", "model", "words": [{"w", "start", "end", "p"}]}.
"""
import argparse, json, sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mp4"); ap.add_argument("--out", required=True); ap.add_argument("--model", default="small.en")
    a = ap.parse_args()
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("ERROR transcribe: faster-whisper is not installed (pip install faster-whisper)")
    model = WhisperModel(a.model, device="cpu", compute_type="int8")
    segs, info = model.transcribe(a.mp4, language="en", word_timestamps=True, vad_filter=False, beam_size=5)
    words = []
    for s in segs:
        for w in s.words or []:
            words.append({"w": w.word.strip(), "start": round(w.start, 3), "end": round(w.end, 3), "p": round(w.probability, 3)})
    json.dump({"schema": "pnf.video.transcript.v1", "model": f"faster-whisper {a.model} int8", "words": words}, open(a.out, "w"), indent=1)
    print(f"transcript: {len(words)} words, first at {words[0]['start'] if words else None} s")


if __name__ == "__main__":
    main()
