#!/usr/bin/env python3
"""ElevenLabs narration for make_demo.py (Todd bought ElevenLabs Starter on Oct 15, 2026; it is connected in Zapier).

The cloud runs reach ElevenLabs only through the Zapier MCP tool, so a render takes three steps:

  1. python3 tools/el_voice.py lines spec.json
       prints the lines make_demo will speak, in order, as JSON [{"i", "text", "tts"}]. "text" is the caption; "tts"
       is what to send to ElevenLabs (the spec's optional "tts" field on the hook, a row, the fix or the cta, which may
       carry ElevenLabs v3 audio tags such as [sighs] or [short pause]; else the caption text).
  2. For each line, call the Zapier ElevenLabs action "Convert Text to Speech" (selected_api App226160CLIAPI,
       tool_name elevenlabs_convert_text_to_speech) with text=<tts>, voice_id=<spec "el_voice">, model_id=<spec
       "el_model", default eleven_v3>, output_format mp3_44100_128. Save {"<i>": "<audio_url>"} to a JSON file.
  3. python3 tools/el_voice.py fetch spec.json urls.json
       downloads every clip into tools/work_demo/el/<spec name>/ and writes manifest.json {caption text: file}.
       Then render with: python3 tools/make_demo.py spec.json out.mp4 --format short --voice files:<that folder>

The audio comes back on zapier-dev-files.s3.amazonaws.com, which the sandbox must be allowed to reach (Todd's
network settings). If the download is refused, fall back to the Kokoro voice in the spec and say so in the slate.
Voices on the account (premade, Oct 15): Chris iP95p4xoKVk53GoZ742B, Roger CwhRBWXzGAHq8TQ4Fs17, Eric
cjVigY5qzO86Huf0OWal, Matilda XrExE9yKIg1WjnnlVkGX, Bill pqHfZKP75CvOlQylNhV4 (cmo/CONTENT_PLAYBOOK.md section 9).
"""
import json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))


def lines(spec, fmt="short"):
    """The spoken lines in make_demo's order for the short format, with their ElevenLabs text."""
    out = []
    hook = spec.get("hook_say_short") or ""
    if hook:
        out.append((hook, spec.get("hook_tts") or hook))
    for r in spec.get("rows", []):
        say = r.get("say") or r.get("label")
        out.append((say, r.get("tts") or say))
        if r.get("ask"):
            out.append((r["ask"], r.get("ask_tts") or r["ask"]))
    if spec.get("fix"):
        f = spec["fix"]; say = f.get("say") or f.get("label")
        out.append((say, f.get("tts") or say))
    pt = spec.get("pitch") or {}
    if pt.get("say"):
        out.append((pt["say"], pt.get("tts") or pt["say"]))
    c = spec.get("cta", {})
    if c.get("say"):
        out.append((c["say"], c.get("tts") or c["say"]))
    return [{"i": i, "text": t, "tts": s} for i, (t, s) in enumerate(out)]


def fetch(spec_path, urls_path):
    spec = json.load(open(spec_path)); urls = json.load(open(urls_path))
    key = os.path.splitext(os.path.basename(spec_path))[0]
    d = os.path.join(HERE, "work_demo", "el", key); os.makedirs(d, exist_ok=True)
    man = {}
    for ln in lines(spec):
        u = urls.get(str(ln["i"]))
        if not u:
            sys.exit(f"no audio url for line {ln['i']}: {ln['text']}")
        f = os.path.join(d, f"l{ln['i']:02d}.mp3")
        urllib.request.urlretrieve(u, f)
        man[ln["text"]] = os.path.basename(f)
    json.dump(man, open(os.path.join(d, "manifest.json"), "w"), indent=1)
    print(d)


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "lines":
        print(json.dumps(lines(json.load(open(sys.argv[2]))), indent=1, ensure_ascii=False))
    elif len(sys.argv) >= 4 and sys.argv[1] == "fetch":
        fetch(sys.argv[2], sys.argv[3])
    else:
        sys.exit(__doc__)
