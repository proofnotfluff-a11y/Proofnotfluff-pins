#!/usr/bin/env python3
"""ProofNotFluff product demo video: the product's calculator on screen from frame one, inputs typed in,
the result cell revealed, burned-in captions, music, an Etsy end card.

Usage:
  python3 make_demo.py spec.json out.mp4 [--format short|walkthrough|listing]

Formats:
  short        1080x1920, quick pace (about 10 to 15 s). YouTube Short, Instagram Reel, Pinterest video pin.
  walkthrough  1920x1080, slow pace with the "why" captions (about 35 to 60 s). A regular YouTube video that
               Shorts point to with the related-video link; its description carries the listing link.
  listing      1080x2160, quick pace, no audio, 15 s max. Etsy listing video (Etsy rules: 3 to 15 s, 1:2).

Spec (every number must come from the product's own files; the CMO checks this):
{
  "product_id": "13",
  "product": "Service Pricing Calculator",          name on the sheet and the end card
  "tab": "Hourly rate",                             optional, shown as the sheet tab
  "audience": "Cleaners, detailers, lawn care",     small line over the hook
  "hook": "A $40 hourly rate pays you about $20",   on screen from frame one (wrap the key number in <b>)
  "rows": [
    {"label": "Rate you quote per hour", "value": "$40", "input": true,
     "say": "You quote $40 an hour", "why": "Longer caption used by the walkthrough"},
    {"label": "Kept per hour worked", "value": "$20.04", "result": true, "kind": "bad",
     "say": "You keep about $20"}
  ],
  "fix": {"label": "To keep $30 an hour, bill", "value": "$57", "say": "..."},   optional second result
  "cta": {"title": "Service Pricing Calculator", "sub": "On Etsy: etsy.com/shop/ProofNotFluff"},
  "note": "Sample numbers"                          optional small line under the sheet
}
"""
import json, os, re, subprocess, sys, shutil, html as H
import make_slides as ms

HERE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
FORMATS = {
    "short":       {"W": 1080, "H": 1920, "pace": 1.0, "audio": True,  "max": 60},
    "walkthrough": {"W": 1920, "H": 1080, "pace": 2.6, "audio": True,  "max": 180},
    "listing":     {"W": 1080, "H": 2160, "pace": 0.8, "audio": False, "max": 15},
}
CTA_SUB = ms.CTA_SUB
BANNED = ["honestly", "genuinely", "straightforward", "delve", "unlock", "elevate", "seamless", "game-changer", "effortless", "supercharge"]


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
    sub = spec.get("cta", {}).get("sub", "")
    if "description" in sub.lower() or "link below" in sub.lower():
        problems.append("CTA points to an unclickable description link")
    if len(spec["rows"]) > 7:
        problems.append("more than 7 rows will not read on a phone")
    if problems:
        sys.exit("spec refused: " + "; ".join(problems))


def timeline(spec, pace, walkthrough):
    """Start times in seconds for each row, the fix, the end card, and the captions."""
    t = 1.6 if not walkthrough else 3.0          # hook and empty sheet are on screen first
    ev, caps = [], []
    if walkthrough:
        caps.append([0.0, spec.get("hook_say") or re.sub("<[^>]+>", "", spec["hook"])])
    for r in spec["rows"]:
        if r.get("input"):
            dur = 0.55 * pace + 0.04 * len(str(r["value"]))
            ev.append({"t": t, "d": dur, "kind": "input"})
            say = (r.get("why") if walkthrough else None) or r.get("say") or r["label"]
            caps.append([t - 0.15, say])
            t += dur + 0.35 * pace
        elif r.get("result"):
            t += 0.25 * pace
            ev.append({"t": t, "d": 0.9, "kind": "result"})
            say = (r.get("why") if walkthrough else None) or r.get("say") or r["label"]
            caps.append([t, say])
            t += 0.9 + 1.0 * pace
        else:  # a fixed row (shown filled from the start)
            ev.append({"t": 0, "d": 0, "kind": "fixed"})
    fix_t = None
    if spec.get("fix"):
        fix_t = t
        f = spec["fix"]
        caps.append([t, (f.get("why") if walkthrough else None) or f.get("say") or f["label"]])
        t += 1.0 + 1.3 * pace
    cta_t = t
    caps.append([t, spec.get("cta", {}).get("say", "")])
    total = t + (2.6 if not walkthrough else 5.0)
    return ev, caps, fix_t, cta_t, total


def page(spec, fmt, ev, caps, fix_t, cta_t, total):
    W, Hh = fmt["W"], fmt["H"]; wide = W > Hh
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
    cta = spec.get("cta", {})
    data = {"ev": ev, "caps": caps, "fixT": fix_t, "ctaT": cta_t, "total": total,
            "vals": [str(r["value"]) for r in spec["rows"]]}
    hook = spec["hook"]  # trusted spec text; <b> marks the key number
    layout = f"""
.wrap{{position:absolute;inset:0;display:grid;grid-template-columns:{'760px 1fr' if wide else '1fr'};align-content:{'center' if wide else 'start'};gap:{'70px' if wide else '0'};padding:{'150px 110px 120px' if wide else '200px 150px 0 70px'}}}
.left{{display:flex;flex-direction:column;{'justify-content:center' if wide else ''}}}
.sheetwrap{{{'align-self:center' if wide else 'margin-top:10px'}}}
.capslot{{height:{'auto' if wide else '120px'};margin-top:{'48px' if wide else '30px'};display:flex;align-items:{'flex-start' if wide else 'center'}}}
"""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:P;src:url(file://{F}/google-fonts/Poppins-Bold.ttf);font-weight:700}}
@font-face{{font-family:PM;src:url(file://{F}/google-fonts/Poppins-Medium.ttf)}}
@font-face{{font-family:C;src:url(file://{F}/crosextra/Carlito-Regular.ttf)}}
@font-face{{font-family:CB;src:url(file://{F}/crosextra/Carlito-Bold.ttf)}}
*{{margin:0;padding:0;box-sizing:border-box}} html,body{{width:{W}px;height:{Hh}px;overflow:hidden}}
body{{background:#1D2433;color:#fff;font-family:C;position:relative}}
.prog{{position:absolute;top:{80 if not wide else 60}px;left:80px;right:80px;height:6px;background:rgba(255,255,255,.14);border-radius:3px}} .prog i{{display:block;height:100%;width:0;background:#C8502F;border-radius:3px}}
.bars{{position:absolute;top:{110 if not wide else 84}px;left:80px;display:flex;gap:10px}} .bars i{{width:{int(52*s)}px;height:{int(10*s)}px;border-radius:5px;display:block}}
{layout}
.aud{{font-family:P;font-size:{int(30*s)}px;letter-spacing:3px;color:#E9B49F;text-transform:uppercase;margin-bottom:{int(18*s)}px}}
h1{{font-family:P;font-size:{int(84*s)}px;line-height:1.08;letter-spacing:-1px}} h1 b{{color:#F08A66}}
.sheet{{background:#FBF9F5;color:#1D2433;border-radius:{int(28*s)}px;overflow:hidden;box-shadow:0 30px 60px rgba(0,0,0,.35)}}
.bar{{display:flex;align-items:center;gap:14px;background:#2E6B66;color:#fff;padding:{int(22*s)}px {int(30*s)}px}}
.bar .t{{font-family:P;font-size:{int(34*s)}px}} .bar .tab{{margin-left:auto;font-family:PM;font-size:{int(24*s)}px;background:rgba(255,255,255,.18);padding:6px 16px;border-radius:999px}}
.grid{{padding:{int(14*s)}px {int(24*s)}px {int(20*s)}px}}
.row{{display:grid;grid-template-columns:1fr {int(330*s)}px;align-items:center;gap:{int(20*s)}px;padding:{int(14*s)}px 0;border-bottom:2px solid #ECE6DA}}
.row:last-child{{border-bottom:0}}
.row .lab{{font-size:{int(34*s)}px;line-height:1.2;color:#3A4152}}
.cell{{position:relative;height:{int(82*s)}px;border:3px solid #D9D2C3;border-radius:{int(14*s)}px;background:#fff;display:flex;align-items:center;justify-content:flex-end;padding:0 {int(22*s)}px;font-family:P;font-size:{int(44*s)}px;color:#1D2433;transition:none}}
.cell.mid{{font-size:{int(36*s)}px}} .cell.long{{font-size:{int(28*s)}px}}
.row.fixed .cell{{background:#F2EEE6;color:#4A5163}}
.row.res .cell{{background:#F2EEE6}}
.row.res.on .cell{{background:#1D2433;color:#fff;border-color:#1D2433}} .row.res.bad.on .cell{{background:#C8502F;border-color:#C8502F}} .row.res.good.on .cell{{background:#2E6B66;border-color:#2E6B66}}
.row.res.on .lab{{font-family:CB;color:#1D2433}}
.cell.act{{border-color:#C8502F;box-shadow:0 0 0 6px rgba(200,80,47,.18)}}
.caret{{display:none;width:4px;height:{int(46*s)}px;background:#C8502F;margin-left:4px}} .cell.typing .caret{{display:block}}
.fix{{margin:{int(20*s)}px {int(24*s)}px {int(24*s)}px;background:#2E6B66;color:#fff;border-radius:{int(18*s)}px;padding:{int(22*s)}px {int(26*s)}px;display:flex;align-items:center;justify-content:space-between;gap:20px;opacity:0;transform:translateY(20px)}}
.fix .lab{{font-size:{int(34*s)}px;line-height:1.2}} .fix .fv{{font-family:P;font-size:{int(64*s)}px}}
.note{{font-size:{int(24*s)}px;color:#8A91A3;margin-top:{int(14*s)}px}}
.cap{{display:inline-block;background:#fff;color:#1D2433;font-family:CB;font-size:{int(46*s) if not wide else 40}px;line-height:1.25;padding:{int(18*s)}px {int(28*s)}px;border-radius:{int(18*s)}px;box-shadow:0 10px 30px rgba(0,0,0,.25)}}
.cursor{{position:absolute;width:{int(46*s)}px;height:{int(46*s)}px;left:0;top:0;z-index:20;transform:translate(-200px,-200px)}}
.end{{position:absolute;inset:0;background:rgba(18,23,34,.94);display:flex;flex-direction:column;justify-content:center;align-items:{'center' if wide else 'flex-start'};padding:0 {int(90*s)}px;opacity:0;z-index:30;text-align:{'center' if wide else 'left'}}}
.end h2{{font-family:P;font-size:{int(80*s)}px;line-height:1.1;margin-bottom:{int(30*s)}px}}
.end .btn{{display:inline-block;background:#C8502F;color:#fff;font-family:P;font-size:{int(40*s)}px;padding:{int(24*s)}px {int(44*s)}px;border-radius:60px;margin-bottom:{int(28*s)}px}}
.end .sub{{font-size:{int(44*s)}px;color:#E8EBF1}}
.foot{{position:absolute;bottom:{70 if not wide else 50}px;left:80px;font-family:P;font-size:{int(26*s)}px;letter-spacing:1px;color:#9AA3B5;z-index:31}}
</style></head><body>
<div class="prog"><i id="pg"></i></div>
<div class="bars"><i style="background:#C8502F"></i><i style="background:#2E6B66"></i><i style="background:#6B4FA0"></i><i style="background:#2F5F9E"></i><i style="background:#8A6A1F"></i></div>
<div class="wrap">
  <div class="left"><div class="aud">{H.escape(spec.get("audience",""))}</div><h1>{hook}</h1><div class="capslot"><span class="cap" id="cap"></span></div></div>
  <div class="sheetwrap"><div class="sheet"><div class="bar"><span class="t">{H.escape(spec["product"])}</span>{f'<span class="tab">{H.escape(spec["tab"])}</span>' if spec.get("tab") else ''}</div>
  <div class="grid">{''.join(rows_html)}</div>{fix_html}</div>{f'<div class="note">{H.escape(spec["note"])}</div>' if spec.get("note") else ''}</div>
</div>
<svg class="cursor" id="cur" viewBox="0 0 24 24"><path d="M4 2l16 9.5-7 1.6-3.6 6.4z" fill="#fff" stroke="#1D2433" stroke-width="1.6" stroke-linejoin="round"/></svg>
<div class="end" id="end"><h2>{H.escape(cta.get("title", spec["product"]))}</h2><div class="btn">{H.escape(cta.get("button", "Instant download"))}</div><div class="sub">{H.escape(cta.get("sub", CTA_SUB))}</div></div>
<div class="foot">PROOFNOTFLUFF</div>
<script>
const D={json.dumps(data)};
const rows=[...document.querySelectorAll('.row')];
const ease=x=>x<0?0:x>1?1:1-Math.pow(1-x,3);
function parseNum(v){{const m=/^([^0-9]*)([0-9][0-9,]*\\.?[0-9]*)(.*)$/.exec(v);if(!m)return null;const n=parseFloat(m[2].replace(/,/g,''));const dec=(m[2].split('.')[1]||'').length;return {{pre:m[1],n,dec,post:m[3],comma:m[2].includes(',')}}}}
function fmtN(p,x){{let s=x.toFixed(p.dec);if(p.comma){{const [a,b]=s.split('.');s=a.replace(/\\B(?=(\\d{{3}})+(?!\\d))/g,',')+(b?'.'+b:'')}}return p.pre+s+p.post}}
function cellCenter(i){{const c=rows[i].querySelector('.cell').getBoundingClientRect();return [c.left+c.width*0.78,c.top+c.height*0.62]}}
window.renderAt=function(t){{
  document.getElementById('pg').style.width=Math.min(100,t/D.total*100)+'%';
  let curTarget=null,prevTarget=null,moveStart=0;
  D.ev.forEach((e,i)=>{{
    const r=rows[i],cell=r.querySelector('.cell'),v=r.querySelector('.v'),val=D.vals[i];
    cell.classList.remove('act','typing');
    if(e.kind==='input'){{
      const k=Math.max(0,Math.min(1,(t-e.t)/e.d));
      v.textContent=t<e.t?'':val.slice(0,Math.round(k*val.length));
      if(t>=e.t-0.45&&t<e.t+e.d+0.25)cell.classList.add('act');
      if(t>=e.t&&t<e.t+e.d)cell.classList.add('typing');
      if(t>=e.t-0.45){{prevTarget=curTarget;curTarget=cellCenter(i);moveStart=e.t-0.45}}
    }} else if(e.kind==='result'){{
      if(t<e.t){{v.textContent='';r.classList.remove('on')}}
      else{{r.classList.add('on');const p=parseNum(val);const k=ease((t-e.t)/e.d);v.textContent=p?fmtN(p,p.n*k):val;
        const pop=t-e.t<0.35?1+0.06*Math.sin((t-e.t)/0.35*Math.PI):1;cell.style.transform='scale('+pop+')';}}
      if(t>=e.t-0.45){{prevTarget=curTarget;curTarget=cellCenter(i);moveStart=e.t-0.45}}
    }} else {{ v.textContent=val; }}
  }});
  const fx=document.getElementById('fix');
  if(fx&&D.fixT!==null){{const k=ease((t-D.fixT)/0.6);fx.style.opacity=k;fx.style.transform='translateY('+(20*(1-k))+'px)'}}
  const cur=document.getElementById('cur');
  if(curTarget){{const k=ease((t-moveStart)/0.45);const a=prevTarget||[curTarget[0]+260,curTarget[1]+340];
    const x=a[0]+(curTarget[0]-a[0])*k,y=a[1]+(curTarget[1]-a[1])*k;cur.style.transform='translate('+x+'px,'+y+'px)'}}
  else cur.style.transform='translate(-200px,-200px)';
  let cap='';D.caps.forEach(c=>{{if(t>=c[0])cap=c[1]}});const ce=document.getElementById('cap');ce.textContent=cap;ce.style.visibility=cap?'visible':'hidden';
  const en=document.getElementById('end');en.style.opacity=Math.max(0,Math.min(1,(t-D.ctaT)/0.45));
}};
window.renderAt(0);
</script></body></html>"""


def render(page_html, fmt, total, work):
    from playwright.sync_api import sync_playwright
    fdir = os.path.join(work, "frames"); shutil.rmtree(fdir, ignore_errors=True); os.makedirs(fdir)
    hp = os.path.join(work, "demo.html"); open(hp, "w").write(page_html)
    n = int(total * FPS)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": fmt["W"], "height": fmt["H"]})
        pg.goto("file://" + hp); pg.wait_for_timeout(400)
        for i in range(n):
            pg.evaluate("t=>window.renderAt(t)", i / FPS)
            pg.screenshot(path=os.path.join(fdir, f"f{i:05d}.png"))
        b.close()
    return fdir, n


def main(spec_path, out, fmt_name="short"):
    spec = json.load(open(spec_path)); lint(spec)
    fmt = FORMATS[fmt_name]; wide = fmt_name == "walkthrough"
    ev, caps, fix_t, cta_t, total = timeline(spec, fmt["pace"], wide)
    if total > fmt["max"]:
        if fmt_name == "listing":  # Etsy's 15 s cap: shorten the end card first, then refuse
            total = min(total, fmt["max"])
            if cta_t > total - 1.2:
                sys.exit(f"listing video needs {cta_t + 1.2:.1f}s; Etsy allows 15. Use fewer input rows.")
        else:
            sys.exit(f"{total:.1f}s is over the {fmt['max']}s limit for {fmt_name}")
    work = os.path.join(HERE, "work_demo"); os.makedirs(work, exist_ok=True)
    fdir, n = render(page(spec, fmt, ev, caps, fix_t, cta_t, total), fmt, total, work)
    cmd = ["ffmpeg", "-y", "-loglevel", "error"]
    if fmt["audio"]:
        mp = os.path.join(work, "music.wav"); ms.music(total, mp)
        cmd += ["-i", mp, "-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"), "-map", "1:v", "-map", "0:a",
                "-c:a", "aac", "-b:a", "160k"]
    else:
        cmd += ["-framerate", str(FPS), "-i", os.path.join(fdir, "f%05d.png"), "-an"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-t", f"{total:.2f}", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    shutil.rmtree(fdir, ignore_errors=True)
    print(json.dumps({"out": out, "format": fmt_name, "seconds": round(total, 1), "size": [fmt["W"], fmt["H"]], "frames": n,
                      "captions": [c[1] for c in caps if c[1]]}))


if __name__ == "__main__":
    a = sys.argv[1:]; f = "short"
    if "--format" in a:
        i = a.index("--format"); f = a[i + 1]; del a[i:i + 2]
    main(a[0], a[1], f)
