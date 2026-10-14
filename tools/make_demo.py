#!/usr/bin/env python3
"""ProofNotFluff product demo video: the product's calculator on screen from frame one, the hook spoken over it,
inputs typed in, the result revealed on the music's lift, burned-in captions, an Etsy end card with the sonic logo.

Usage:
  python3 make_demo.py spec.json out.mp4 [--format short|walkthrough|listing] [--voice <name|none>]

Formats:
  short        1080x1920. YouTube Short, Instagram and Facebook Reel, TikTok, Pinterest video pin. Everything that
               matters sits between y=270 and y=1250 (the band no app covers): headline, the sheet under a camera
               that follows the active row, captions under the sheet.
  walkthrough  1920x1080, slower, with the "why" captions (about 35 to 60 s). A regular YouTube video that
               Shorts point to with the related-video link; its description carries the listing link.
  listing      1080x2160, quick pace, no audio, 15 s max. Etsy listing video (Etsy rules: 3 to 15 s, 1:2).

Spec (every number must come from the product's own files; the CMO checks this):
{
  "product_id": "13",
  "product": "Service Pricing Calculator",          name on the sheet and the end card
  "tab": "Hourly rate",                             optional, shown as the sheet tab
  "audience": "Cleaners, detailers, lawn care",     small line over the hook
  "hook": "A $40 hourly rate pays you about $20",   on screen from frame one (wrap the key number in <b>)
  "hook_say_short": "A $40 rate pays you about $20", optional: what the Short says over frame one (default: the
                                                    headline, or its first sentence when the whole one runs past 4 s)
  "hook_say": "...",                                optional: the walkthrough's spoken opening
  "mood": "tension",                                optional: calm, upbeat, playful, driving or tension; picks the
                                                    music (default: any track, the one used longest ago)
  "music": "red-ink",                               optional: one track id from tools/music/library.json
  "palette": "ink",                                 optional: ink, night or plum (default: rotates)
  "rows": [
    {"label": "Rate you quote per hour", "value": "$40", "input": true,
     "say": "You quote $40 an hour", "why": "Longer caption used by the walkthrough"},
    {"label": "Kept per hour worked", "value": "$20.04", "result": true, "kind": "bad",
     "say": "You keep about $20"}
  ],
  "fix": {"label": "To keep $30 an hour, bill", "value": "$57", "say": "..."},   optional second result
  "cta": {"title": "Service Pricing Calculator", "sub": "On Etsy: proofnotfluff.etsy.com"},
  "note": "Sample numbers"                          optional small line under the sheet
}

The key reveal is the result row that shows the headline's <b> number (else the first "bad" result, else the last
result). The music's lift lands on it, every reveal lands on a beat, and the music's ending chord and the sonic logo
land right after the spoken close. Sound choices and their sources: tools/soundtrack.py.
"""
import json, math, os, re, subprocess, sys, shutil, html as H
import make_slides as ms

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
VOICE = None   # --voice <name|none> on the command line beats the spec's "voice" and PNF_VOICE; default am_michael (Todd, Oct 7)
FORMATS = {
    "short":       {"W": 1080, "H": 1920, "pace": 1.0, "audio": True,  "max": 60},
    "walkthrough": {"W": 1920, "H": 1080, "pace": 2.6, "audio": True,  "max": 180},
    "listing":     {"W": 1080, "H": 2160, "pace": 0.8, "audio": False, "max": 15},
}
GAP = {"short": 0.3, "walkthrough": 0.45, "listing": 0.0}      # pause between narration lines
RING = 1.6                                                       # seconds the ending chord and the logo ring before the cut
SPEED = {"short": 1.12, "walkthrough": 1.0, "listing": 1.0}    # narration speed (Kokoro)
CTA_SUB = ms.CTA_SUB
BANNED = ["honestly", "genuinely", "straightforward", "delve", "unlock", "elevate", "seamless", "game-changer", "effortless", "supercharge"]
MOODS = ["calm", "upbeat", "playful", "driving", "tension"]
# Three looks in one family (fonts, layout, and the red/green meaning stay fixed): YouTube's inauthentic-content
# policy names videos that "look like they're made with a template", so the background and sheet bar rotate.
PALETTES = {
    "ink":   {"bg": "#1D2433", "end": "#121722", "bar": "#2E6B66", "hook": "#F08A66", "mark": "rgba(240,138,102,.30)", "aud": "#E9B49F"},
    "night": {"bg": "#13213A", "end": "#0C1628", "bar": "#2F5F9E", "hook": "#F4B860", "mark": "rgba(244,184,96,.30)", "aud": "#A9C6EC"},
    "plum":  {"bg": "#221A2F", "end": "#16101F", "bar": "#5E4596", "hook": "#F08A66", "mark": "rgba(240,138,102,.30)", "aud": "#D2C3F0"},
}
GLOW = {"bad": "200,80,47", "good": "46,107,102", "": "29,36,51"}


def lint(spec):
    """Refuse specs that would ship something sloppy."""
    text = json.dumps(spec, ensure_ascii=False)
    problems = []
    if "—" in text or "–" in text:
        problems.append("em or en dash in the spec")
    for w in BANNED:
        if re.search(r"\b" + re.escape(w) + r"\b", text, re.I):
            problems.append(f"banned word: {w}")
    if not any(r.get("result") for r in spec["rows"]):
        problems.append("no result row: the demo must reveal an answer")
    if not any(r.get("input") for r in spec["rows"]):
        problems.append("no input rows")
    csay = spec.get("cta", {}).get("say", "")
    if "workbook" in csay.lower() and not spec.get("cta", {}).get("what"):
        problems.append("the close says 'workbook' but cta.what is missing: the end card must say what it is, e.g. 'The full workbook for Excel and Google Sheets'")
    sub = spec.get("cta", {}).get("sub", "")
    if "description" in sub.lower() or "link below" in sub.lower():
        problems.append("CTA points to an unclickable description link")
    if len(spec["rows"]) > 7:
        problems.append("more than 7 rows will not read on a phone")
    if spec.get("mood") and spec["mood"] not in MOODS:
        problems.append(f"mood '{spec['mood']}' is not one of {', '.join(MOODS)}")
    if spec.get("palette") and spec["palette"] not in PALETTES:
        problems.append(f"palette '{spec['palette']}' is not one of {', '.join(PALETTES)}")
    # Plain words for a stranger (Todd, Oct 9: "Debts on tab 2: 5 debts" made no sense on TikTok).
    jargon = re.compile(r"\b(tab|tabs|cell|cells|sheet|column|preset)\b|\b[A-Z]{1,2}[0-9]{1,3}\b", re.I)
    if re.match(r"\s*[0-9]", str(spec.get("tab", ""))):
        problems.append(f"tab chip '{spec['tab']}' carries the workbook's tab number: name what it is, e.g. 'Quote Builder'")
    rows = spec["rows"] + ([spec["fix"]] if spec.get("fix") else [])
    for r in rows:
        lab, val = str(r.get("label", "")), str(r.get("value", ""))
        if jargon.search(lab) or jargon.search(val):
            problems.append(f"workbook jargon a viewer cannot read: '{lab}: {val}' (say what it is, not where it lives)")
        if re.search(r"[0-9.]+ ?h, ?[0-9]", val):
            problems.append(f"squeezed code value '{val}': write it out, e.g. '2 people, 1.5 hrs'")
        if r is not spec.get("fix") and len(lab) > 34:
            problems.append(f"label over 34 characters wraps on a phone: '{lab}'")
    if problems:
        sys.exit("spec refused: " + "; ".join(problems))


def strip(h):
    return re.sub(r"<[^>]+>", "", h or "").strip()


def key_row(spec):
    """The result row the headline is about: its <b> number, else the first 'bad' result, else the last result."""
    res = [i for i, r in enumerate(spec["rows"]) if r.get("result")]
    m = re.search(r"<b>(.*?)</b>", spec.get("hook", ""))
    if m:
        want = re.sub(r"[^0-9.]", "", m.group(1))
        for i in res:
            if want and want in re.sub(r"[^0-9.]", "", str(spec["rows"][i]["value"])):
                return i
    bad = [i for i in res if spec["rows"][i].get("kind") == "bad"]
    return bad[0] if bad else res[-1]


def spoken_hook(spec, fmt_name, spoken):
    if fmt_name == "walkthrough":
        return spec.get("hook_say") or strip(spec["hook"])
    if spec.get("hook_say_short"):
        return spec["hook_say_short"]
    full = strip(spec["hook"])
    if spoken(full) <= 4.0:
        return full
    return re.split(r"(?<=[.!?])\s+", full)[0]   # say the first sentence; the headline still shows the rest


def timeline(spec, fmt_name, speech=None):
    """Start times in seconds for each row, the fix, the end card and the narration lines.
    speech(text) returns a line's spoken length when a voice is on; a row then stays on screen at least as long
    as its line is spoken. Returns a dict (see the end)."""
    walk = fmt_name == "walkthrough"
    pace = FORMATS[fmt_name]["pace"]
    read = lambda txt: len(txt or "") / 15.0       # seconds a caption needs on screen (about 15 characters a second)
    spoken = speech or (lambda txt: 0.0)
    gap = GAP[fmt_name] if speech else 0.0
    hold = lambda txt: max(read(txt) + 0.3 if walk else 0.0, spoken(txt) + gap if spoken(txt) else 0.0)
    line = lambda t, txt, cap=True: {"t": t, "text": txt, "dur": spoken(txt), "cap": cap}
    ev, lines = [], []
    key = key_row(spec)
    t = 1.6
    if walk:
        hs = spoken_hook(spec, fmt_name, spoken)
        lines.append(line(0.0, hs)); t = max(3.0, read(hs) + 0.6, spoken(hs) + 0.5)
    elif speech:                     # the Short says its hook over frame one; the headline is its caption
        hs = spoken_hook(spec, fmt_name, spoken)
        lines.append(line(0.0, hs, cap=False)); t = max(1.2, spoken(hs) + gap + 0.12)
    for i, r in enumerate(spec["rows"]):
        say = (r.get("why") if walk else None) or r.get("say") or r["label"]
        if r.get("input"):
            dur = (0.55 if walk else 0.5) * pace + 0.035 * len(str(r["value"]))
            ev.append({"t": t, "d": dur, "kind": "input", "row": i})
            lines.append(line(t - 0.12, say))
            t += max(dur + 0.3 * pace, hold(say))
        elif r.get("result"):
            t += 0.2 * pace
            lead = 0.6 if (i == key and speech) else 0.0   # the number and the music's lift land first, then the voice
            ev.append({"t": t, "d": 0.9, "kind": "result", "row": i, "key": i == key, "glow": GLOW.get(r.get("kind", ""), GLOW[""])})
            lines.append(line(t + lead, say))
            t += max(0.9 + 0.9 * pace, lead + hold(say) + (0.2 if walk else 0))
        else:  # a fixed row: shown from the start, or counted up once the inputs above it are in
            last_in = [e for e in ev if e["kind"] == "input"]
            if last_in:
                ev.append({"t": last_in[-1]["t"] + last_in[-1]["d"] + 0.15, "d": 0.5, "kind": "derived", "row": i})
            else:
                ev.append({"t": 0, "d": 0, "kind": "fixed", "row": i})
    fix_t = None
    if spec.get("fix"):
        fix_t = t
        f = spec["fix"]
        fsay = (f.get("why") if walk else None) or f.get("say") or f["label"]
        lines.append(line(t + 0.15, fsay))
        t += max(1.0 + 1.2 * pace, 0.15 + hold(fsay) + (0.2 if walk else 0))
    cta_t = t
    csay = spec.get("cta", {}).get("say", "")
    lead = 0.35 if speech else 0.0                     # the whoosh into the end card, then the voice
    lines.append(line(t + lead, csay))
    if spoken(csay):   # the music keeps going under the close; its ending chord and the logo land after the last word
        button = t + lead + spoken(csay) + 0.2
        end_hold = max(2.4 if not walk else 5.0, button - t + RING)
    else:
        button, end_hold = t, (2.4 if not walk else 5.0)
    return {"ev": ev, "lines": lines, "fix_t": fix_t, "cta_t": cta_t, "button": button, "end_hold": end_hold,
            "total": cta_t + end_hold, "key": key}


def sync(tl, beat, min_gap=0.15):
    """Put every reveal (each result, the fix, the end card) on the music's beat grid. Each one moves to the
    nearest beat, or the next one when moving earlier would cut into the line before it; everything after it moves
    with it, so nothing overlaps. The first reveal sets the grid."""
    ev, lines = tl["ev"], tl["lines"]
    hits = [("ev", i) for i, e in enumerate(ev) if e["kind"] == "result"]
    if tl["fix_t"] is not None:
        hits.append(("fix", None))
    hits.append(("cta", None))
    when = lambda h: ev[h[1]]["t"] if h[0] == "ev" else (tl["fix_t"] if h[0] == "fix" else tl["cta_t"])
    hits.sort(key=when)
    phase = None
    for h in hits:
        T = when(h)
        if phase is None:
            phase = T
            continue
        prev_voice = max([l["t"] + l["dur"] for l in lines if l["t"] < T - 1e-6] + [0.0])
        own = min([l["t"] - T for l in lines if l["t"] >= T - 1e-6], default=0.0)
        prev_vis = max([e["t"] + e["d"] for e in ev if e["t"] < T - 1e-6 and e["kind"] != "fixed"] + [0.0])
        earliest = max(prev_voice + min_gap - own, prev_vis + 0.12)
        cand = phase + round((T - phase) / beat) * beat
        if cand < earliest - 1e-9:
            cand = phase + math.ceil((earliest - phase) / beat - 1e-9) * beat
        d = cand - T
        if abs(d) < 1e-9:
            continue
        for e in ev:
            if e["t"] >= T - 1e-6 and e["kind"] != "fixed":
                e["t"] += d
        for l in lines:
            if l["t"] >= T - 1e-6:
                l["t"] += d
        if tl["fix_t"] is not None and tl["fix_t"] >= T - 1e-6:
            tl["fix_t"] += d
        tl["cta_t"] += d
    close = [l for l in lines if l["t"] >= tl["cta_t"] - 1e-6 and l["dur"]]
    if close:   # the ending chord on the first beat after the closing line
        end_voice = max(l["t"] + l["dur"] for l in close)
        tl["button"] = phase + math.ceil((end_voice + 0.12 - phase) / beat - 1e-9) * beat
        tl["total"] = max(tl["cta_t"] + 2.4, tl["button"] + RING)
    else:
        tl["button"] = tl["cta_t"]
        tl["total"] = tl["cta_t"] + tl["end_hold"]
    tl["beat"] = beat
    return tl


def camera_plan(tl):
    """When the camera moves and what it frames: the whole sheet, a row, or the fix card."""
    plan = [[0.0, "over"]]
    for e in tl["ev"]:
        if e["kind"] in ("input", "result"):
            plan.append([max(0.05, round(e["t"] - 0.45, 3)), e["row"]])
            if e.get("key") and tl["fix_t"] is None:
                plan.append([round(e["t"] + 1.5, 3), "over"])   # step back so the whole model is seen with its answer
    if tl["fix_t"] is not None:   # the fix opens under the sheet while the camera pulls back: problem and fix in one frame
        plan.append([round(tl["fix_t"] - 0.4, 3), "over"])
    plan.sort(key=lambda p: p[0])
    out = []
    for i, p in enumerate(plan):
        nxt = plan[i + 1][0] if i + 1 < len(plan) else tl["cta_t"]
        if i > 0 and p[1] == "over" and nxt - p[0] < 1.1:
            continue
        out.append(p)
    return out


def cap_html(txt):
    """Caption text, escaped, with the numbers in bold so the eye finds them."""
    s = H.escape(txt or "", quote=False)      # quote=False: an apostrophe stays a character, never "&#x27;" for the regex to split
    return re.sub(r"(\$?\d[\d,]*(?:\.\d+)?%?)", r"<b>\1</b>", s)


def page(spec, fmt_name, tl, palette="ink"):
    fmt = FORMATS[fmt_name]
    W, Hh = fmt["W"], fmt["H"]; wide = W > Hh; short = fmt_name == "short"
    P = PALETTES[palette]
    F = ms.FONTS
    s = 1.0 if not wide else 0.78
    rows_html = []
    for i, r in enumerate(spec["rows"]):
        cls = "inp" if r.get("input") else ("res " + r.get("kind", "") if r.get("result") else "fixed")
        val = H.escape(str(r["value"])) if not (r.get("input") or r.get("result")) else ""
        ln = len(str(r["value"])); size = "" if ln <= 8 else (" mid" if ln <= 12 else " long")
        rows_html.append(f'<div class="row {cls}" id="r{i}"><div class="lab">{H.escape(r["label"])}</div>'
                         f'<div class="cell{size}"><span class="v">{val}</span><span class="caret"></span></div></div>')
    fix_html = ""
    if spec.get("fix"):
        f = spec["fix"]
        fix_html = (f'<div class="fix" id="fix"><div class="lab">{H.escape(f["label"])}</div>'
                    f'<div class="fv">{H.escape(str(f["value"]))}</div></div>')
        if short:
            fix_html = f'<div class="fixwrap" id="fixwrap">{fix_html}</div>'
    cta = spec.get("cta", {})
    caps = [[round(l["t"], 3), cap_html(l["text"])] for l in tl["lines"] if l["cap"]]
    data = {"ev": tl["ev"], "caps": caps, "fixT": tl["fix_t"], "ctaT": tl["cta_t"], "total": tl["total"],
            "vals": [str(r["value"]) for r in spec["rows"]], "cam": camera_plan(tl), "hookMax": 160 if short else 0,
            "capMax": 152 if short else (0 if wide else 104), "buttonT": tl.get("button", tl["cta_t"]),
            "pad": 18, "halo": 58}
    hook = spec["hook"]  # trusted spec text; <b> marks the key number
    tab_html = '<span class="tab">' + H.escape(spec["tab"]) + '</span>' if spec.get("tab") else ""
    sheet = (f'<div class="sheet"><div class="bar"><span class="t">{H.escape(spec["product"])}</span>{tab_html}</div>'
             f'<div class="grid">{"".join(rows_html)}</div>{fix_html}</div>')
    note = '<div class="note">' + H.escape(spec["note"]) + '</div>' if spec.get("note") else ""
    say_html = '<div class="say e">' + H.escape(cta["say"]) + '</div>' if cta.get("say") else ""
    what_html = '<div class="what e">' + H.escape(cta["what"]) + '</div>' if cta.get("what") else ""
    end = (f'<div class="end" id="end"><div class="endin">{say_html}'
           f'<h2 class="e">{H.escape(cta.get("title", spec["product"]))}</h2>{what_html}'
           f'<div class="btn e">{H.escape(cta.get("button", "Instant download"))}</div>'
           f'<div class="sub e">{H.escape(cta.get("sub", CTA_SUB))}</div></div></div>')
    bars = ('<span class="bars"><i style="background:#C8502F"></i><i style="background:#2E6B66"></i><i style="background:#6B4FA0"></i>'
            '<i style="background:#2F5F9E"></i><i style="background:#8A6A1F"></i></span>')
    common = f"""
@font-face{{font-family:P;src:url(file://{F}/google-fonts/Poppins-Bold.ttf);font-weight:700}}
@font-face{{font-family:PM;src:url(file://{F}/google-fonts/Poppins-Medium.ttf)}}
@font-face{{font-family:C;src:url(file://{F}/crosextra/Carlito-Regular.ttf)}}
@font-face{{font-family:CB;src:url(file://{F}/crosextra/Carlito-Bold.ttf)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{W}px;height:{Hh}px;overflow:hidden}}
body{{background:{P['bg']};color:#fff;font-family:C;position:relative}}
.prog{{position:absolute;height:6px;background:rgba(255,255,255,.14);border-radius:3px;z-index:32}} .prog i{{display:block;height:100%;width:0;background:#C8502F;border-radius:3px}}
.aud{{font-family:P;letter-spacing:3px;color:{P['aud']};text-transform:uppercase}}
h1{{font-family:P;line-height:1.08;letter-spacing:-1px}}
h1 b{{color:{P['hook']};background-image:linear-gradient(transparent 66%,{P['mark']} 66%,{P['mark']} 94%,transparent 94%);background-repeat:no-repeat;background-size:0% 100%}}
.sheet{{background:#FBF9F5;color:#1D2433;border-radius:{int(28*s)}px;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,.35)}}
.bar{{display:flex;align-items:center;gap:14px;background:{P['bar']};color:#fff;padding:{int(22*s)}px {int(30*s)}px}}
.bar .t{{font-family:P;font-size:{int(34*s)}px}} .bar .tab{{margin-left:auto;font-family:PM;font-size:{int(24*s)}px;background:rgba(255,255,255,.18);padding:6px 16px;border-radius:999px}}
.grid{{padding:{int(14*s)}px {int(24*s)}px {int(20*s)}px}}
.row{{display:grid;grid-template-columns:1fr {int(330*s)}px;align-items:center;gap:{int(20*s)}px;padding:{int(14*s)}px 0;border-bottom:2px solid #ECE6DA}}
.row:last-child{{border-bottom:0}}
.row .lab{{font-size:{int(34*s)}px;line-height:1.2;color:#3A4152}}
.cell{{position:relative;height:{int(82*s)}px;border:3px solid #D9D2C3;border-radius:{int(14*s)}px;background:#fff;display:flex;align-items:center;justify-content:flex-end;padding:0 {int(22*s)}px;font-family:P;font-size:{int(44*s)}px;color:#1D2433}}
.cell.mid{{font-size:{int(36*s)}px}} .cell.long{{font-size:{int(28*s)}px}}
.row.inp .cell{{background:#FFF4CC;color:#1F4E9E}}
.row.fixed .cell{{background:#F2EEE6;color:#4A5163}}
.row.res .cell{{background:#F2EEE6}}
.row.res.on .cell{{background:#1D2433;color:#fff;border-color:#1D2433}} .row.res.bad.on .cell{{background:#C8502F;border-color:#C8502F}} .row.res.good.on .cell{{background:#2E6B66;border-color:#2E6B66}}
.row.res.on .lab{{font-family:CB;color:#1D2433}}
.cell.act{{border-color:#C8502F;box-shadow:0 0 0 6px rgba(200,80,47,.18)}}
.caret{{display:none;width:4px;height:{int(46*s)}px;background:#C8502F;margin-left:4px}} .cell.typing .caret{{display:block}}
.fix{{background:#2E6B66;color:#fff;border-radius:{int(18*s)}px;padding:{int(22*s)}px {int(26*s)}px;display:flex;align-items:center;justify-content:space-between;gap:20px}}
.fix .lab{{font-size:{int(34*s)}px;line-height:1.2}} .fix .fv{{font-family:P;font-size:{int(64*s)}px}}
.note{{font-size:{int(24*s)}px;color:#8A91A3}}
.cap{{display:inline-block;background:#fff;color:#1D2433;font-family:CB;line-height:1.24;box-shadow:0 10px 30px rgba(0,0,0,.25);visibility:hidden;text-wrap:balance}} .cap b{{color:#C8502F}}
.cursor{{position:absolute;width:{int(58*s)}px;height:{int(58*s)}px;left:0;top:0;z-index:21;transform:translate(-300px,-300px);filter:drop-shadow(0 4px 6px rgba(0,0,0,.35))}}
.halo{{position:absolute;left:0;top:0;width:{int(58*s)}px;height:{int(58*s)}px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.34) 0,rgba(255,255,255,.12) 55%,rgba(255,255,255,0) 72%);z-index:20;transform:translate(-300px,-300px)}}
.ripple{{position:absolute;left:0;top:0;border:4px solid #C8502F;border-radius:50%;z-index:20;opacity:0}}
.end{{position:absolute;inset:0;background:{P['end']};display:flex;flex-direction:column;justify-content:center;opacity:0;z-index:30}} .endin{{transform-origin:0 50%}}
.end h2{{font-family:P;font-size:{int(80*s)}px;line-height:1.1;margin-bottom:{int(30*s)}px}}
.end .btn{{display:inline-block;background:#C8502F;color:#fff;font-family:P;font-size:{int(40*s)}px;padding:{int(24*s)}px {int(44*s)}px;border-radius:60px;margin-bottom:{int(28*s)}px}}
.end .sub{{font-size:{int(44*s)}px;color:#E8EBF1}}
.end .say{{font-family:CB;font-size:{int(48*s)}px;line-height:1.25;color:#F2A385;margin-bottom:{int(36*s)}px}}
.end .what{{font-size:{int(42*s)}px;line-height:1.3;color:#E8EBF1;margin-bottom:{int(34*s)}px}}
.foot{{position:absolute;font-family:P;font-size:{int(26*s)}px;letter-spacing:1px;color:#9AA3B5;z-index:31;display:flex;align-items:center;gap:18px}}
.bars{{display:flex;gap:8px}} .bars i{{width:{int(40*s)}px;height:{int(9*s)}px;border-radius:5px;display:block}}
"""
    if short:
        layout = """
.prog{top:226px;left:70px;right:150px}
.aud{position:absolute;left:70px;right:150px;top:274px;font-size:26px}
h1{position:absolute;left:70px;right:110px;top:310px;font-size:72px}
.view{position:absolute;left:70px;top:482px;width:860px;height:576px;overflow:hidden}
.view.scroll{-webkit-mask-image:linear-gradient(to bottom,transparent 0,#000 10px,#000 calc(100% - 10px),transparent 100%)}
.cam{position:absolute;left:0;top:0;width:860px;transform-origin:0 0}
.row{padding:9px 0} .cell{height:70px} .grid{padding:10px 24px 12px}
.fixwrap{overflow:hidden} .fix{margin:6px 24px 20px;padding:16px 26px} .fix .fv{font-size:58px}
.capband{position:absolute;left:70px;width:860px;top:1066px;height:152px;display:flex;align-items:center;justify-content:center;text-align:center}
.cap{font-size:48px;padding:14px 28px;border-radius:18px;max-width:860px}
.note{position:absolute;left:70px;right:150px;top:1226px}
.end{padding:300px 180px 690px 90px}
.foot{left:70px;top:1272px}
"""
        body = (f'<div class="prog"><i id="pg"></i></div><div class="aud">{H.escape(spec.get("audience", ""))}</div><h1>{hook}</h1>'
                f'<div class="view" id="view"><div class="cam" id="cam">{sheet}</div></div>'
                f'<div class="capband"><span class="cap" id="cap"></span></div>{note}')
    else:
        layout = f"""
.prog{{top:{80 if not wide else 60}px;left:80px;right:80px}}
.wrap{{position:absolute;inset:0;display:grid;grid-template-columns:{'760px 1fr' if wide else '1fr'};align-content:{'center' if wide else 'start'};gap:{'70px' if wide else '0'};padding:{'150px 110px 120px' if wide else '150px 150px 0 70px'}}}
.left{{display:flex;flex-direction:column;{'justify-content:center' if wide else ''}}}
.aud{{font-size:{int(30*s)}px;margin-bottom:{int(18*s)}px}}
h1{{font-size:{int(84*s) if wide else 76}px}}
.sheetwrap{{{'align-self:center' if wide else 'margin-top:10px'}}}
.capslot{{height:{'auto' if wide else '104px'};margin-top:{'48px' if wide else '22px'};display:flex;align-items:{'flex-start' if wide else 'center'}}}
.cap{{font-size:{40 if wide else int(46*s)}px;padding:{int(18*s)}px {int(28*s)}px;border-radius:{int(18*s)}px}}
.fix{{margin:{int(20*s)}px {int(24*s)}px {int(24*s)}px;opacity:0;transform:translateY(20px)}}
.note{{margin-top:{int(14*s)}px}}
.endin{{transform-origin:{'50% 50%' if wide else '0 50%'}}}
.end{{align-items:{'center' if wide else 'flex-start'};padding:{'0 '+str(int(90*s))+'px' if wide else '0 160px 0 '+str(int(90*s))+'px'};text-align:{'center' if wide else 'left'}}}
.foot{{bottom:{70 if not wide else 50}px;left:80px}}
{'' if wide else '.row{padding:9px 0} .cell{height:70px} .grid{padding:10px 24px 12px} .fix{margin:12px 24px 18px;padding:16px 26px} .fix .fv{font-size:58px} .foot{bottom:330px}'}
"""
        body = (f'<div class="prog"><i id="pg"></i></div><div class="wrap"><div class="left"><div class="aud">{H.escape(spec.get("audience", ""))}</div>'
                f'<h1>{hook}</h1><div class="capslot"><span class="cap" id="cap"></span></div></div>'
                f'<div class="sheetwrap">{sheet}{note}</div></div>')
    cursor = ('<div class="halo" id="halo"></div><div class="ripple" id="rip"></div>'
              '<svg class="cursor" id="cur" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6-3.6 6.4z" fill="#fff" stroke="#1D2433" stroke-width="1.6" stroke-linejoin="round"/></svg>')
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{common}{layout}</style></head><body>'
            f'{body}{cursor}{end}<div class="foot">{bars}PROOFNOTFLUFF</div>'
            f'<script>{JS.replace("__DATA__", json.dumps(data))}</script></body></html>')


JS = r"""
const D=__DATA__;
const $=id=>document.getElementById(id);
const rows=[...document.querySelectorAll('.row')];
const ease=x=>x<0?0:x>1?1:1-Math.pow(1-x,3);
const easeIO=x=>x<0?0:x>1?1:(x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2);
const view=$('view'),cam=$('cam'),fixwrap=$('fixwrap'),fx=$('fix'),cur=$('cur'),halo=$('halo'),rip=$('rip'),capEl=$('cap'),endEl=$('end');
const hookB=document.querySelector('h1 b');
const endItems=[...document.querySelectorAll('.end .e')];
function parseNum(v){const m=/^([^0-9]*)([0-9][0-9,]*\.?[0-9]*)(.*)$/.exec(v);if(!m)return null;const n=parseFloat(m[2].replace(/,/g,''));const dec=(m[2].split('.')[1]||'').length;return {pre:m[1],n,dec,post:m[3],comma:m[2].includes(',')}}
function fmtN(p,x){let s=x.toFixed(p.dec);if(p.comma){const [a,b]=s.split('.');s=a.replace(/\B(?=(\d{3})+(?!\d))/g,',')+(b?'.'+b:'')}return p.pre+s+p.post}
let fixH=0,VW=0,VH=0,ready=false;
function init(){   // measured on the first frame, after the fonts have loaded (render() waits for them)
  if(D.hookMax){const h=document.querySelector('h1');let fs=parseFloat(getComputedStyle(h).fontSize);while(h.scrollHeight>D.hookMax&&fs>50){fs-=2;h.style.fontSize=fs+'px'}}
  if(fixwrap){fixH=fixwrap.scrollHeight;fixwrap.style.height='0px'}
  if(view){VW=view.clientWidth;VH=view.clientHeight}
  ready=true;
}
function seg(t){let k=0;for(let i=0;i<D.cam.length;i++)if(t>=D.cam[i][0])k=i;return k}
function edges(){   // sheet-space y of every edge between blocks: the sheet top, each row's top and bottom, the sheet bottom
  const b=[0,rows[0].offsetTop];rows.forEach(r=>b.push(r.offsetTop+r.offsetHeight));b.push(cam.offsetHeight);
  return [...new Set(b.map(v=>Math.round(v)))].sort((x,y)=>x-y);
}
function target(f){
  const Hs=cam.offsetHeight+(fixwrap&&D.fixT!==null?fixH-fixwrap.offsetHeight:0);   // the height the sheet ends at, so a pull-back never stalls
  if(f==='over')return {s:Math.min(1,(VH-D.pad)/Hs),cy:cam.offsetHeight/2};
  // a row: grow the window by whole blocks around it until it fills the view, so no row is ever cut through its text
  const E=edges(),r=rows[f],mid=r.offsetTop+r.offsetHeight/2;
  let top=Math.round(r.offsetTop),bot=Math.round(r.offsetTop+r.offsetHeight);
  for(let g=0;g<40&&bot-top<VH;g++){
    const up=E.filter(v=>v<top).pop(),dn=E.find(v=>v>bot);
    if(up===undefined&&dn===undefined)break;
    if(dn===undefined||(up!==undefined&&mid-top<=bot-mid))top=up;else bot=dn;
  }
  return {s:Math.min(1,VH/(bot-top)),cy:(top+bot)/2};
}
function drift(k,t){
  if(k===0){const T1=D.cam.length>1?D.cam[1][0]:D.total;return 0.965+0.035*Math.min(1,t/Math.max(0.5,T1))}
  return 1+0.012*ease((t-D.cam[k][0]-0.45)/3);
}
function camera(t){
  if(!view)return;
  const k=seg(t);const c=target(D.cam[k][1]);let s,cy;
  if(k===0){s=c.s*drift(0,t);cy=c.cy}
  else{const p=target(D.cam[k-1][1]);const ps=p.s*drift(k-1,D.cam[k][0]);const u=easeIO((t-D.cam[k][0])/0.45);
    if(u>=1){s=c.s*drift(k,t);cy=c.cy}else{s=ps+(c.s-ps)*u;cy=p.cy+(c.cy-p.cy)*u}}
  const Hs=cam.offsetHeight;
  if(s*Hs>VH){const half=VH/(2*s);cy=Math.max(half,Math.min(Hs-half,cy))}else cy=Hs/2;
  const cx=cam.offsetWidth/2;
  cam.style.transform='translate('+(VW/2-s*cx)+'px,'+(VH/2-s*cy)+'px) scale('+s+')';
  view.classList.toggle('scroll',s*Hs>VH+2);
}
function opFor(f,i){return f==='over'?1:(f===i?1:0.42)}
function dim(t){
  const k=seg(t);const f=D.cam[k][1];const pf=k>0?D.cam[k-1][1]:'over';const u=ease((t-D.cam[k][0])/0.3);
  rows.forEach((r,i)=>{r.style.opacity=opFor(pf,i)+(opFor(f,i)-opFor(pf,i))*u});
}
function cellPoint(i){const c=rows[i].querySelector('.cell').getBoundingClientRect();return [c.left+c.width*0.78,c.top+c.height*0.62]}
function sheetAt(t){
  let tgt=null,prev=null,moveStart=0,clickT=null,lastRes=null,doneT=null;
  D.ev.forEach((e,i)=>{
    const r=rows[i],cell=r.querySelector('.cell'),v=r.querySelector('.v'),val=D.vals[i];
    cell.classList.remove('act','typing');cell.style.transform='';cell.style.filter='';cell.style.boxShadow='';
    if(e.kind==='input'){
      const k=Math.max(0,Math.min(1,(t-e.t)/e.d));
      v.textContent=t<e.t?'':val.slice(0,Math.round(k*val.length));
      if(t>=e.t-0.45&&t<e.t+e.d+0.25)cell.classList.add('act');
      if(t>=e.t&&t<e.t+e.d)cell.classList.add('typing');
      if(t>=e.t-0.45){prev=tgt;tgt=i;moveStart=e.t-0.45;clickT=e.t;lastRes=null;doneT=e.t+e.d+0.35}
    }else if(e.kind==='result'){
      if(t<e.t){v.textContent='';r.classList.remove('on')}
      else{r.classList.add('on');const p=parseNum(val);const k=ease((t-e.t)/e.d);v.textContent=p?fmtN(p,p.n*k):val;
        const a=t-e.t;const amp=e.key?0.13:0.06;
        cell.style.transform='scale('+(a<0.38?1+amp*Math.sin(a/0.38*Math.PI):1)+')';
        if(a<0.3)cell.style.filter='brightness('+(1+0.45*(1-a/0.3))+')';
        if(e.key){const g=Math.min(1,a/0.7);cell.style.boxShadow='0 0 0 '+(4+20*ease(g))+'px rgba('+e.glow+','+(0.5*(1-g)+0.16)+')'}}
      if(t>=e.t-0.45){prev=tgt;tgt=i;moveStart=e.t-0.45;clickT=null;lastRes=e;doneT=null}
    }else if(e.kind==='derived'){
      if(t<e.t)v.textContent='';else{const p=parseNum(val);const k=ease((t-e.t)/e.d);v.textContent=p?fmtN(p,p.n*k):val;}
    }else{v.textContent=val}
  });
  if(fx&&D.fixT!==null){const k=ease((t-D.fixT)/0.5);
    if(fixwrap){fixwrap.style.height=(fixH*k)+'px';fx.style.opacity=k;fx.style.transform='translateY('+(16*(1-k))+'px)';
      const a=t-D.fixT;fx.style.filter=(a>=0&&a<0.35)?'brightness('+(1+0.35*(1-a/0.35))+')':''}
    else{fx.style.opacity=k;fx.style.transform='translateY('+(20*(1-k))+'px)'}}
  return {tgt,prev,moveStart,clickT,doneT,hide:lastRes!==null&&t>=lastRes.t+0.3};
}
function pointer(t,c){
  const off='translate(-300px,-300px)';
  if(c.tgt===null||c.hide||t>=D.ctaT){cur.style.transform=halo.style.transform=off;rip.style.opacity=0;return}
  const b=cellPoint(c.tgt);const k=ease((t-c.moveStart)/0.45);const a=c.prev!==null?cellPoint(c.prev):[b[0]+260,b[1]+340];
  const x=a[0]+(b[0]-a[0])*k,y=a[1]+(b[1]-a[1])*k,hs=D.halo;
  cur.style.transform='translate('+x+'px,'+y+'px)';halo.style.transform='translate('+(x-hs/2)+'px,'+(y-hs/2)+'px)';
  const fade=c.doneT!==null&&t>c.doneT?1-ease((t-c.doneT)/0.2):1;cur.style.opacity=halo.style.opacity=fade;
  if(c.clickT!==null&&t>=c.clickT&&t<c.clickT+0.4){const g=(t-c.clickT)/0.4;const r=10+38*ease(g);rip.style.opacity=0.75*(1-g);
    rip.style.width=rip.style.height=(2*r)+'px';rip.style.transform='translate('+(x-r)+'px,'+(y-r)+'px)'}else rip.style.opacity=0;
}
function caption(t){
  let k=-1;D.caps.forEach((c,i)=>{if(t>=c[0])k=i});
  if(k<0||t>=D.ctaT||!D.caps[k][1]){capEl.style.visibility='hidden';return}
  if(capEl.dataset.k!==String(k)){capEl.innerHTML=D.caps[k][1];capEl.dataset.k=String(k);capEl.style.fontSize='';
    const room=D.capMax;let fs=parseFloat(getComputedStyle(capEl).fontSize);   // long lines shrink to fit their band
    while(room&&capEl.offsetHeight>room-2&&fs>28){fs-=2;capEl.style.fontSize=fs+'px'}}
  const u=ease((t-D.caps[k][0])/0.14);capEl.style.visibility='visible';capEl.style.opacity=0.5+0.5*u;capEl.style.transform='translateY('+(8*(1-u))+'px)';
}
const endIn=document.querySelector('.end .endin');
function endcard(t){
  const a=t-D.ctaT;endEl.style.opacity=Math.max(0,Math.min(1,a/0.2));
  if(endIn)endIn.style.transform='scale('+(1+0.03*Math.max(0,Math.min(1,a/Math.max(1,D.total-D.ctaT))))+')';
  endItems.forEach((el,i)=>{const u=ease((a-0.05-0.07*i)/0.35);el.style.opacity=u;
    let tr='translateY('+(26*(1-u))+'px)';
    if(el.classList.contains('btn')){const b=t-D.buttonT-0.26;if(b>0&&b<0.32)tr+=' scale('+(1+0.07*Math.sin(b/0.32*Math.PI))+')'}
    el.style.transform=tr});
}
window.renderAt=function(t){
  if(!ready)init();
  $('pg').style.width=Math.min(100,t/D.total*100)+'%';
  if(hookB)hookB.style.backgroundSize=(100*ease((t-0.15)/0.45))+'% 100%';
  const c=sheetAt(t);
  camera(t);
  dim(t);
  pointer(t,c);
  caption(t);
  endcard(t);
};
"""


def render(page_html, fmt, total, work):
    from playwright.sync_api import sync_playwright
    fdir = os.path.join(work, "frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    hp = os.path.join(work, "demo.html"); open(hp, "w").write(page_html)
    n = int(total * FPS)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": fmt["W"], "height": fmt["H"]})
        pg.goto("file://" + hp); pg.evaluate("() => document.fonts.ready.then(() => document.fonts.size)"); pg.wait_for_timeout(300)
        for i in range(n):
            pg.evaluate("t=>window.renderAt(t)", i / FPS)
            pg.screenshot(path=os.path.join(fdir, f"f{i:05d}.png"))
        if fmt["W"] == 1080 and fmt["H"] == 1920:   # Shorts: no end-card text in the right 150 px the app buttons cover
            right = pg.evaluate("""() => Math.max(0, ...[...document.querySelectorAll('.end .e')].flatMap(e => {
                const r = document.createRange(); r.selectNodeContents(e); return [...r.getClientRects()].map(q => q.right)}))""")
            if right > fmt["W"] - 150:
                b.close()
                raise SystemExit(f"end card text reaches x={right:.0f}, inside the right 150 px: shorten cta.say, cta.what or cta.title")
        b.close()
    return fdir, n


def sfx_events(spec, tl):
    """Light keystrokes while a value types, a pop on each reveal, a chime on the fix, a whoosh into the end card."""
    out = []
    for e in tl["ev"]:
        if e["kind"] == "input":
            val = str(spec["rows"][e["row"]]["value"])
            for k, ch in enumerate(val):
                if ch != " ":
                    out.append(("tick", e["t"] + e["d"] * (k + 0.5) / len(val)))
        elif e["kind"] == "result":
            out.append(("pop", e["t"]))
    if tl["fix_t"] is not None:
        out.append(("chime", tl["fix_t"]))
    out.append(("whoosh", tl["cta_t"]))
    return out


def choose_palette(spec, fmt_name, key):
    if spec.get("palette"):
        return spec["palette"]
    if fmt_name == "listing":
        return "ink"
    import soundtrack as st
    log = st.used_log()
    for u in reversed(log):
        if u.get("spec") == key and u.get("palette") in PALETTES:
            return u["palette"]          # the same spec keeps its look between the review render and the posted one
    last = {}
    for i, u in enumerate(log):
        if u.get("palette") and u.get("spec") != key:
            last[u["palette"]] = i
    import hashlib
    return min(PALETTES, key=lambda p: (last.get(p, -1), hashlib.sha1((key + p).encode()).hexdigest()))


def main(spec_path, out, fmt_name="short"):
    spec = json.load(open(spec_path)); lint(spec)
    fmt = FORMATS[fmt_name]
    if fmt_name == "listing":  # the buyer is already on Etsy: no shop address, no call to leave
        spec.setdefault("cta", {})["sub"] = spec.get("listing_cta_sub", "Instant digital download")
        spec["cta"]["say"] = ""

    voice = VOICE if VOICE is not None else spec.get("voice", os.environ.get("PNF_VOICE", "am_michael"))
    if fmt_name == "listing":
        voice = "none"
    work = os.path.join(HERE, "work_demo"); os.makedirs(work, exist_ok=True)
    key = os.path.splitext(os.path.basename(spec_path))[0]
    st = track = None
    if fmt["audio"] or voice != "none":
        import soundtrack as st
        st.ensure()
    if fmt["audio"]:
        track = st.pick(spec.get("mood"), spec.get("music"), key=key)
    clips = {}
    speech = None
    if voice != "none":
        import voice as vo
        vdir = os.path.join(work, "voice"); shutil.rmtree(vdir, ignore_errors=True); os.makedirs(vdir)
        speed = float(spec.get("voice_speed", SPEED[fmt_name]))
        def speech(txt):
            if not txt:
                return 0.0
            if txt not in clips:
                path = os.path.join(vdir, f"c{len(clips):02d}.wav")
                vo.say(txt, path, voice=voice, speed=speed)
                clips[txt] = (path, st.prepare(path))
            return clips[txt][1]
    tl = timeline(spec, fmt_name, speech)
    if track:
        tl = sync(tl, 60.0 / track["bpm"])
    total = tl["total"]
    if total > fmt["max"]:
        if fmt_name == "listing":  # Etsy's 15 s cap: shorten the end card first, then refuse
            total = tl["total"] = min(total, fmt["max"])
            if tl["cta_t"] > total - 1.2:
                sys.exit(f"listing video needs {tl['cta_t'] + 1.2:.1f}s; Etsy allows 15. Use fewer input rows.")
        else:
            sys.exit(f"{total:.1f}s is over the {fmt['max']}s limit for {fmt_name}")
    palette = choose_palette(spec, fmt_name, key)
    fdir, n = render(page(spec, fmt_name, tl, palette), fmt, total, work)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    sound = {}
    if fmt["audio"]:
        wav = os.path.join(work, "mix.wav")
        lines = [(l["t"], clips[l["text"]][0]) for l in tl["lines"] if l["text"] in clips]
        key_t = tl["ev"][tl["key"]]["t"]
        sound = st.mix(track, total, key_t, tl["cta_t"], wav, voice=lines, sfx=sfx_events(spec, tl), button=tl["button"])
        st.record(track["id"], out, spec.get("mood"), palette, key)
        cmd += ["-i", wav, "-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"), "-map", "1:v", "-map", "0:a",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    else:
        cmd += ["-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"), "-an"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print(json.dumps({"out": out, "format": fmt_name, "seconds": round(total, 1), "size": [fmt["W"], fmt["H"]], "frames": n,
                      "voice": voice, "music": track["id"] if track else None, "mood": spec.get("mood") or "any",
                      "palette": palette, "sound": sound,
                      "moments": {"hook_spoken_to": round(tl["lines"][0]["dur"] if tl["lines"] and tl["lines"][0]["t"] == 0.0 else 0.0, 2),
                                  "key_reveal": round(tl["ev"][tl["key"]]["t"], 2),
                                  "fix": round(tl["fix_t"], 2) if tl["fix_t"] is not None else None,
                                  "end_card": round(tl["cta_t"], 2), "ending": round(tl["button"], 2)},
                      "spoken": [l["text"] for l in tl["lines"] if l["text"] and l["text"] in clips],
                      "captions": [l["text"] for l in tl["lines"] if l["text"] and l["cap"]]}))


if __name__ == "__main__":
    a = sys.argv[1:]; f = "short"
    if "--format" in a:
        i = a.index("--format"); f = a[i + 1]; del a[i:i + 2]
    if "--voice" in a:
        i = a.index("--voice"); VOICE = a[i + 1]; del a[i:i + 2]
    main(a[0], a[1], f)
