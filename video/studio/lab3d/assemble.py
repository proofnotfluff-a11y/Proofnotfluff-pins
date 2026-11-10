"""Lab: put the voice and the big captions on a silent 3D render.

  python3 assemble.py <silent.mp4 or frames dir> <audio file> <words.json> <out.mp4> [--fps 24]

Captions follow the v4 rule: one row of big words low in the frame, the spoken word in gold.
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GOLD, CREAM, DARK = "&H73C8F7&", "&HEAF7FF&", "&H00181014"


def pages(words, max_chars=11, max_words=3):
    out, cur = [], []
    for i, w in enumerate(words):
        txt = w["w"].strip()
        n = sum(len(x["w"].strip()) for x in cur) + len(cur) + len(txt)
        gap = w["start"] - cur[-1]["end"] if cur else 0
        if cur and (n > max_chars or len(cur) >= max_words or cur[-1]["w"].strip()[-1] in ".?!" or gap > 0.6):
            out.append(cur); cur = []
        cur.append(w)
    if cur: out.append(cur)
    return out


def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return "%d:%02d:%05.2f" % (h, m, s)


def ass(words, path, y=1284, size=128):
    pg = pages(words)
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: cap,Poppins,%d,%s,%s,%s,&H96000000,-1,0,0,0,100,100,0,0,1,10,3,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" % (size, CREAM, CREAM, DARK)
    lines = []
    for pi, p in enumerate(pg):
        nxt = pg[pi + 1][0]["start"] if pi + 1 < len(pg) else None
        end_page = p[-1]["end"] + 0.35
        if nxt is not None: end_page = min(end_page, nxt)
        for i, w in enumerate(p):
            a = w["start"]; b = p[i + 1]["start"] if i + 1 < len(p) else end_page
            parts = []
            for k, x in enumerate(p):
                c = GOLD if k == i else CREAM
                parts.append("{\\c%s}%s" % (c, x["w"].strip()))
            lines.append("Dialogue: 0,%s,%s,cap,,0,0,0,,{\\pos(540,%d)}%s" % (ts(a), ts(b), y, " ".join(parts)))
    open(path, "w").write(head + "\n".join(lines) + "\n")
    return len(pg)


def main():
    src, audio, wj, out = sys.argv[1:5]
    fps = int(sys.argv[sys.argv.index("--fps") + 1]) if "--fps" in sys.argv else 24
    words = json.load(open(wj)); words = words["words"] if isinstance(words, dict) else words
    cap = out + ".ass"; n = ass(words, cap)
    vin = ["-framerate", str(fps), "-pattern_type", "glob", "-i", os.path.join(src, "f*.png")] if os.path.isdir(src) else ["-i", src]
    vf = "scale=1080:1920:flags=lanczos,subtitles=%s:fontsdir=%s" % (cap.replace(":", "\\:"), os.path.join(HERE, "fonts"))
    cmd = ["ffmpeg", "-loglevel", "error", "-y", *vin, "-i", audio, "-map", "0:v", "-map", "1:a", "-vf", vf, "-r", str(fps),
           "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", out]
    subprocess.check_call(cmd); print("captions pages", n, "->", out)


if __name__ == "__main__":
    main()
