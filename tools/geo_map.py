#!/usr/bin/env python3
"""Interactive Chicago community area map for the free pages (Todd, live chat, Oct 27, 2026: "Interactive maps. This
should be available for both free and paid products"). The paid members' apps keep their Leaflet street maps
(tools/leads_app.py, rest_app.py, lic_app.py, seat_app.py); this is the free side's map: one inline SVG built here at
page-build time from site/geo/chicago-community-areas.json (tools/chicago_geo.py), so it loads with the page, needs no
map tiles, no outside script and no cookies, and shows its colors even with scripts off.

What a visitor can do: color the map by any metric the page passes in, tap or hover a community area to read its
numbers, pick a neighborhood from a list (the keyboard path; the table on the page stays the full text alternative),
zoom in and out and drag to move around when zoomed.

Usage as a library:
    import geo_map
    html = geo_map.choropleth(values, metrics, uid="rat")      # values {area number: {key: number}}
Usage: python3 tools/geo_map.py --selftest
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEO = os.path.join(ROOT, "site", "geo", "chicago-community-areas.json")
W = 600            # viewBox width; the height follows the city's shape
TOL = 0.55         # simplify tolerance in viewBox units (about 30 meters on the ground)
K = math.cos(math.radians(41.84))   # east-west shrink at Chicago's latitude (equirectangular projection)


def E(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def load(path=GEO):
    return json.load(open(path, encoding="utf-8")) if os.path.isfile(path) else None


def _dp(pts, tol):
    if len(pts) < 4:
        return pts
    keep = [False] * len(pts)
    keep[0] = keep[-1] = True
    st = [(0, len(pts) - 1)]
    while st:
        a, b = st.pop()
        (x1, y1), (x2, y2) = pts[a], pts[b]
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        best, at = -1.0, -1
        for i in range(a + 1, b):
            x, y = pts[i]
            d = abs(dy * x - dx * y + x2 * y1 - y2 * x1) / L if L else math.hypot(x - x1, y - y1)
            if d > best:
                best, at = d, i
        if at > 0 and best > tol:
            keep[at] = True
            st += [(a, at), (at, b)]
    return [p for p, k in zip(pts, keep) if k]


def _area(r):
    return sum(r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1] for i in range(len(r))) / 2


def _centroid(r):
    a = _area(r)
    if not a:
        return (sum(p[0] for p in r) / len(r), sum(p[1] for p in r) / len(r))
    cx = sum((r[i - 1][0] + r[i][0]) * (r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1]) for i in range(len(r))) / (6 * a)
    cy = sum((r[i - 1][1] + r[i][1]) * (r[i - 1][0] * r[i][1] - r[i][0] * r[i - 1][1]) for i in range(len(r))) / (6 * a)
    return (cx, cy)


def _inside(x, y, r):
    c = False
    for i in range(len(r)):
        (x1, y1), (x2, y2) = r[i], r[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / ((y2 - y1) or 1e-12) + x1:
            c = not c
    return c


def _anchor(r):
    """A point inside the ring for a label: the centroid when it is inside, else the middle of the widest inside run
    across the ring at the centroid's height (O'Hare and other odd shapes)."""
    cx, cy = _centroid(r)
    if _inside(cx, cy, r):
        return (cx, cy)
    best = None
    for dy in (0, 2, -2, 4, -4, 8, -8):
        y = cy + dy
        xs = sorted((x1 + (y - y1) * (x2 - x1) / ((y2 - y1) or 1e-12)) for (x1, y1), (x2, y2) in zip(r, r[1:] + r[:1]) if (y1 > y) != (y2 > y))
        for a, b in zip(xs[0::2], xs[1::2]):
            if best is None or b - a > best[0]:
                best = (b - a, (a + b) / 2, y)
    return (best[1], best[2]) if best else (cx, cy)


def _n(v):
    t = f"{v:.1f}"
    t = t[:-2] if t.endswith(".0") else t
    return "0" if t in ("-0", "-0.0") else t.replace("0.", ".", 1) if t.startswith("0.") else t.replace("-0.", "-.", 1)


def outline(geo=None, width=W, tol=TOL):
    """{"w", "h", "areas": [{"n", "name", "d", "x", "y"}], "project": f(lon, lat)} in viewBox units."""
    geo = geo or load()
    if not geo:
        return None
    pts = [p for a in geo["areas"] for poly in a["polys"] for ring in poly for p in ring]
    lon0, lon1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lat0, lat1 = min(p[1] for p in pts), max(p[1] for p in pts)
    pad = 4
    s = (width - 2 * pad) / ((lon1 - lon0) * K)
    h = round((lat1 - lat0) * s + 2 * pad)
    proj = lambda lon, lat: ((lon - lon0) * K * s + pad, (lat1 - lat) * s + pad)
    out = []
    for a in geo["areas"]:
        parts, big = [], None
        for poly in a["polys"]:
            for j, ring in enumerate(poly):
                r = _dp([proj(x, y) for x, y in ring], tol)
                if len(r) < 4 or abs(_area(r)) < 1.5:
                    continue
                if r[0] == r[-1]:
                    r = r[:-1]
                if j == 0 and (big is None or abs(_area(r)) > abs(_area(big))):
                    big = r
                x0, y0 = r[0]
                seg = [f"M{x0:.1f} {y0:.1f}"]
                px, py = round(x0, 1), round(y0, 1)
                for x, y in r[1:]:
                    x, y = round(x, 1), round(y, 1)
                    seg.append(_n(x - px) + " " + _n(y - py))
                    px, py = x, y
                parts.append(seg[0] + "l" + " ".join(seg[1:]) + "z")
        if not parts:
            raise SystemExit(f"community area {a['n']} has no outline left after simplifying")
        ax, ay = _anchor(big)
        out.append({"n": a["n"], "name": a["name"], "d": "".join(parts), "x": round(ax, 1), "y": round(ay, 1)})
    return {"w": width, "h": h, "areas": out, "project": proj, "source": geo.get("source") or {}}


def nice_breaks(vals, k=5):
    """k-1 cut points for k classes from the data's quantiles, rounded to easy numbers and kept strictly rising."""
    v = sorted(x for x in vals if x is not None)
    if not v:
        return []
    def nice(x):
        if x <= 10:
            return round(x)
        m = 10 ** (len(str(int(x))) - 1)
        step = m / 2 if x / m < 3 else m
        return int(round(x / step) * step) or 1
    cuts = []
    for i in range(1, k):
        q = v[min(len(v) - 1, int(len(v) * i / k))]
        c = nice(q)
        if cuts and c <= cuts[-1]:
            c = cuts[-1] + 1
        cuts.append(c)
    while cuts and cuts[-1] > v[-1]:   # a class nobody falls in is dropped
        cuts.pop()
    return cuts


def klass(x, cuts):
    return sum(1 for c in cuts if x >= c)


CSS = ("<style>"
       ".gm{--gm0:#fbe9e1;--gm1:#f3c0aa;--gm2:#e48d6a;--gm3:#c8502f;--gm4:#8a3017;--gmn:#ece8e1;"
       "--gmd0:#1e4c48;--gmd1:#7fb5ae;--gmd2:#e4e0d8;--gmd3:#eeab90;--gmd4:#b4401f;--gmedge:#fff;"
       "margin:12px 0 8px;padding:14px 14px 12px;background:var(--card);border:1px solid var(--line);border-radius:12px}"
       "@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .gm{--gm0:#2e2a2c;--gm1:#5c3a30;--gm2:#94472d;--gm3:#d4653f;--gm4:#f6a383;--gmn:#262c38;"
       "--gmd0:#7fd0c5;--gmd1:#2f5a56;--gmd2:#394050;--gmd3:#7f3d2b;--gmd4:#f0906d;--gmedge:#1b2130}}"
       ":root[data-theme=dark] .gm{--gm0:#2e2a2c;--gm1:#5c3a30;--gm2:#94472d;--gm3:#d4653f;--gm4:#f6a383;--gmn:#262c38;"
       "--gmd0:#7fd0c5;--gmd1:#2f5a56;--gmd2:#394050;--gmd3:#7f3d2b;--gmd4:#f0906d;--gmedge:#1b2130}"
       ".gm-bar{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:end;justify-content:space-between;margin:0 0 10px}"
       ".gm-seg{display:flex;flex-wrap:wrap;gap:6px;border:0;margin:0;padding:0;min-width:0}"
       ".gm-seg legend{font-size:13px;font-weight:700;color:var(--muted);margin:0 0 6px;padding:0}"
       ".gm-seg label{position:relative;display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border:1px solid var(--line);border-radius:999px;"
       "font-size:14.5px;font-weight:600;color:var(--ink2);cursor:pointer;background:var(--card)}"
       ".gm-seg input{position:absolute;opacity:0;inset:0;margin:0;cursor:pointer}"
       ".gm-seg label:has(input:checked){background:var(--ink);border-color:var(--ink);color:var(--card)}"
       ".gm-seg label:has(input:focus-visible){outline:3px solid var(--focus);outline-offset:2px}"
       ".gm-find{display:grid;gap:6px;font-size:13px;font-weight:700;color:var(--muted);min-width:min(100%,240px)}"
       ".gm-find select{min-height:44px;font:600 15px/1.2 inherit;color:var(--ink);background:var(--card) var(--sel-arrow) no-repeat right 14px center;"
       "border:1px solid var(--line);border-radius:10px;padding:0 38px 0 12px;appearance:none;-webkit-appearance:none}"
       ".gm-find select:focus-visible{outline:3px solid var(--focus);outline-offset:2px}"
       ".gm-main{display:grid;gap:12px}@media(min-width:860px){.gm-main{grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);align-items:start}}"
       ".gm-stage{position:relative;border-radius:10px;overflow:hidden;background:var(--canvas2);touch-action:none}"
       ".gm-stage svg{display:block;width:100%;height:auto;max-height:78vh;user-select:none;-webkit-user-select:none}"
       ".gm-stage.zoomed{cursor:grab}.gm-stage.dragging{cursor:grabbing}"
       ".gm-a path{stroke:var(--gmedge);stroke-width:.7;stroke-linejoin:round;vector-effect:non-scaling-stroke;fill:var(--gmn);transition:fill .25s}"
       "@media (prefers-reduced-motion:reduce){.gm-a path{transition:none}}"
       ".gm-a path.q0{fill:var(--gm0)}.gm-a path.q1{fill:var(--gm1)}.gm-a path.q2{fill:var(--gm2)}.gm-a path.q3{fill:var(--gm3)}.gm-a path.q4{fill:var(--gm4)}"
       ".gm-a path.d0{fill:var(--gmd0)}.gm-a path.d1{fill:var(--gmd1)}.gm-a path.d2{fill:var(--gmd2)}.gm-a path.d3{fill:var(--gmd3)}.gm-a path.d4{fill:var(--gmd4)}"
       ".gm-a path.nx{fill:url(#gm-hatch)}"
       ".gm-a path:hover{stroke:var(--ink);stroke-width:1.6}.gm-a path.sel{stroke:var(--ink);stroke-width:2.6}"
       ".gm-lab text{font:700 11px system-ui,sans-serif;fill:var(--muted);paint-order:stroke;stroke:var(--canvas2);stroke-width:3px;pointer-events:none;letter-spacing:.02em}"
       ".gm-lab text.gm-lake{font-weight:600;font-style:italic;fill:var(--muted);stroke:none}"
       ".gm-zoom{position:absolute;right:8px;top:8px;display:grid;gap:6px}"
       ".gm-zoom button{width:44px;height:44px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--ink);font:700 20px/1 system-ui,sans-serif;cursor:pointer;box-shadow:var(--shadow-soft)}"
       ".gm-zoom button:focus-visible{outline:3px solid var(--focus);outline-offset:2px}.gm-zoom button[hidden]{display:none}"
       ".gm-info{padding:14px 16px;border:1px solid var(--line);border-radius:10px;background:var(--canvas2)}@media(min-width:860px){.gm-info{min-height:190px}}"
       ".gm-info h3{margin:0 0 4px;font-size:19px;color:var(--ink)}.gm-info p{margin:6px 0 0;color:var(--ink2);font-size:15px}"
       ".gm-info .gm-hint{color:var(--muted);font-size:14px}.gm-info b{color:var(--ink);font-variant-numeric:tabular-nums}"
       ".gm-info dl{display:grid;grid-template-columns:auto 1fr;gap:6px 14px;margin:10px 0 0;font-size:15px}"
       ".gm-info dt{color:var(--muted)}.gm-info dd{margin:0;color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}"
       ".gm-side{display:grid;gap:12px;align-content:start}"
       ".gm-leg{padding:12px 16px;border:1px solid var(--line);border-radius:10px}.gm-legt{margin:0 0 8px;font-size:13.5px;font-weight:700;color:var(--muted)}"
       ".gm-leg ul{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px 14px;margin:0;padding:0;list-style:none;font-size:14px;color:var(--ink2)}"
       ".gm-leg li{display:flex;align-items:center;gap:8px}.gm-leg i{flex:none;display:inline-block;width:22px;height:14px;border-radius:4px;border:1px solid var(--line)}"
       ".gm figcaption{margin-top:8px;font-size:13px;color:var(--muted)}"
       "</style>")


JS = r"""<script>(function(){var R=document.getElementById("__UID__");if(!R)return;var D=JSON.parse(document.getElementById("__UID__-data").textContent);
var svg=R.querySelector("svg"),G=R.querySelector(".gm-a"),info=R.querySelector(".gm-info"),sel=R.querySelector(".gm-find select"),leg=R.querySelector(".gm-leg"),st=R.querySelector(".gm-stage");
var P={};G.querySelectorAll("path").forEach(function(p){P[p.dataset.n]=p;});var M=D.metrics[0].key,pick=null;
function fmt(n){return (n||0).toLocaleString("en-US");}
function paint(){var m=D.metrics.filter(function(x){return x.key===M;})[0];
Object.keys(P).forEach(function(n){var c=(D.cls[M]||{})[n];P[n].setAttribute("class",(c||"")+(pick===n?" sel":""));var a=D.areas[n];
var t=P[n].querySelector("title");if(t&&a)t.textContent=a.name+": "+(a.say[M]||"");});
leg.innerHTML='<p class="gm-legt">'+m.legendTitle+'</p><ul>'+m.legend.map(function(l){return '<li><i style="background:'+l[1]+'"></i>'+l[2]+'</li>';}).join("")+'</ul>';}
function show(n){var a=D.areas[n];if(!a){info.innerHTML=D.hint;return;}info.innerHTML='<h3>'+a.name+'</h3>'+a.html;}
function choose(n,from){if(pick&&P[pick])P[pick].classList.remove("sel");pick=n||null;if(n&&P[n]){P[n].classList.add("sel");G.appendChild(P[n]);}
if(from!=="select")sel.value=n||"";show(n);}
G.addEventListener("pointerover",function(e){var n=e.target.dataset&&e.target.dataset.n;if(n&&!drag.moved&&e.pointerType==="mouse")show(n);});
G.addEventListener("pointerleave",function(){show(pick);});
G.addEventListener("click",function(e){var n=e.target.dataset&&e.target.dataset.n;if(!n||drag.moved)return;choose(pick===n?null:n);});
sel.addEventListener("change",function(){choose(sel.value,"select");if(sel.value)focusOn(sel.value);});
R.querySelectorAll(".gm-seg input").forEach(function(i){i.addEventListener("change",function(){M=i.value;paint();show(pick);});});
var vb0=svg.viewBox.baseVal,W0=vb0.width,H0=vb0.height,vb={x:0,y:0,w:W0,h:H0};
function setvb(){vb.w=Math.min(W0,Math.max(W0/8,vb.w));vb.h=vb.w*H0/W0;vb.x=Math.min(W0-vb.w,Math.max(0,vb.x));vb.y=Math.min(H0-vb.h,Math.max(0,vb.y));
svg.setAttribute("viewBox",vb.x.toFixed(1)+" "+vb.y.toFixed(1)+" "+vb.w.toFixed(1)+" "+vb.h.toFixed(1));var z=vb.w<W0-1;st.classList.toggle("zoomed",z);R.querySelector(".gm-zr").hidden=!z;
var f=vb.w/W0;R.querySelectorAll(".gm-lab text").forEach(function(t){t.style.fontSize=(11*f).toFixed(2)+"px";t.style.strokeWidth=(3*f).toFixed(2)+"px";});}
function zoom(f,cx,cy){cx=cx==null?vb.x+vb.w/2:cx;cy=cy==null?vb.y+vb.h/2:cy;var nw=Math.min(W0,Math.max(W0/8,vb.w*f));vb.x=cx-(cx-vb.x)*nw/vb.w;vb.y=cy-(cy-vb.y)*nw/vb.w;vb.w=nw;setvb();}
function focusOn(n){var a=D.areas[n];if(!a)return;vb.w=W0/3;vb.h=H0/3;vb.x=a.x-vb.w/2;vb.y=a.y-vb.h/2;setvb();}
R.querySelector(".gm-zi").addEventListener("click",function(){zoom(.6);});R.querySelector(".gm-zo").addEventListener("click",function(){zoom(1/.6);});
R.querySelector(".gm-zr").addEventListener("click",function(){vb={x:0,y:0,w:W0,h:H0};setvb();});
var drag={on:false,moved:false};function pt(e){var r=svg.getBoundingClientRect();return {x:vb.x+(e.clientX-r.left)/r.width*vb.w,y:vb.y+(e.clientY-r.top)/r.height*vb.h,px:e.clientX,py:e.clientY};}
st.addEventListener("pointerdown",function(e){if(e.target.closest(".gm-zoom"))return;drag={on:true,moved:false,s:pt(e),x:vb.x,y:vb.y,id:e.pointerId};});
st.addEventListener("pointermove",function(e){if(!drag.on||vb.w>=W0-1)return;var r=svg.getBoundingClientRect(),dx=(e.clientX-drag.s.px)/r.width*vb.w,dy=(e.clientY-drag.s.py)/r.height*vb.h;
if(Math.abs(e.clientX-drag.s.px)+Math.abs(e.clientY-drag.s.py)>6){drag.moved=true;st.classList.add("dragging");try{st.setPointerCapture(drag.id);}catch(_){}}
if(drag.moved){vb.x=drag.x-dx;vb.y=drag.y-dy;setvb();}});
function end(){setTimeout(function(){drag.moved=false;},0);drag.on=false;st.classList.remove("dragging");}st.addEventListener("pointerup",end);st.addEventListener("pointercancel",end);
st.addEventListener("dblclick",function(e){var p=pt(e);zoom(.6,p.x,p.y);});
paint();show(null);})();</script>"""


def choropleth(areas, metrics, uid="gm", title="Map", hint="", landmarks=True, geo=None, caption=""):
    """areas: {area number: {"say": {metric key: short plain line}, "html": info panel html (already escaped)}}.
    metrics: [{"key", "label", "legendTitle", "cls": {area number: css class}, "legend": [(css class, css background, label)]}];
    the first metric is the one painted before any script runs. Returns the figure markup with its data and script."""
    o = outline(geo)
    if not o:
        return ""
    first = metrics[0]
    names = {a["n"]: a["name"] for a in o["areas"]}
    paths = "".join(f'<path data-n="{a["n"]}" class="{E(first["cls"].get(a["n"], ""))}" d="{a["d"]}">'
                    f'<title>{E(a["name"])}: {E(((areas.get(a["n"]) or {}).get("say") or {}).get(first["key"], ""))}</title></path>'
                    for a in o["areas"])
    labs = ""
    if landmarks:
        pj = o["project"]
        lx, ly = pj(-87.585, 41.93)
        labs = (f'<text class="gm-lake" x="{min(lx, o["w"] - 58):.0f}" y="{ly:.0f}">Lake Michigan</text>'
                + "".join(f'<text x="{a["x"]:.0f}" y="{a["y"] + 4:.0f}" text-anchor="middle">{E(a["name"].replace("O" + chr(39) + "Hare", "O" + chr(8217) + "Hare"))}</text>'
                          for a in o["areas"] if a["n"] in (32, 76, 41, 22, 6, 25)))
    opts = "".join(f'<option value="{n}">{E(nm)}</option>' for n, nm in sorted(names.items(), key=lambda x: x[1]))
    seg = "".join(f'<label><input type="radio" name="{uid}-m" value="{E(m["key"])}"{" checked" if i == 0 else ""}>{E(m["label"])}</label>'
                  for i, m in enumerate(metrics))
    leg = (f'<p class="gm-legt">{E(first["legendTitle"])}</p><ul>'
           + "".join(f'<li><i style="background:{v}"></i>{E(t)}</li>' for c, v, t in first["legend"]) + "</ul>")
    data = {"metrics": [{"key": m["key"], "legendTitle": E(m["legendTitle"]), "legend": [[c, v, E(t)] for c, v, t in m["legend"]]} for m in metrics],
            "cls": {m["key"]: {str(k): v for k, v in m["cls"].items()} for m in metrics},
            "areas": {str(a["n"]): {"name": E(a["name"]), "x": a["x"], "y": a["y"], "html": (areas.get(a["n"]) or {}).get("html", ""),
                                    "say": {k: E(v) for k, v in ((areas.get(a["n"]) or {}).get("say") or {}).items()}} for a in o["areas"]},
            "hint": f'<p class="gm-hint">{hint}</p>'}
    js = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (f'<figure class="gm" id="{uid}" aria-labelledby="{uid}-t">'
            f'<div class="gm-bar"><fieldset class="gm-seg"><legend>Color the map by</legend>{seg}</fieldset>'
            f'<label class="gm-find">Find a community area<select><option value="">Pick one</option>{opts}</select></label></div>'
            f'<div class="gm-main"><div class="gm-stage">'
            f'<svg viewBox="0 0 {o["w"]} {o["h"]}" role="img" aria-labelledby="{uid}-t" xmlns="http://www.w3.org/2000/svg">'
            f'<title id="{uid}-t">{E(title)}</title>'
            '<defs><pattern id="gm-hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="6" height="6" fill="var(--gmn)"/><line x1="0" y1="0" x2="0" y2="6" stroke="var(--muted)" stroke-width="1.2" opacity=".45"/></pattern></defs>'
            f'<g class="gm-a">{paths}</g><g class="gm-lab" aria-hidden="true">{labs}</g></svg>'
            '<div class="gm-zoom"><button type="button" class="gm-zi" aria-label="Zoom in">+</button><button type="button" class="gm-zo" aria-label="Zoom out">&minus;</button>'
            '<button type="button" class="gm-zr" aria-label="Show the whole city" hidden><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg></button></div></div>'
            f'<div class="gm-side"><div class="gm-info" aria-live="polite"><p class="gm-hint">{hint}</p></div>'
            f'<div class="gm-leg" aria-hidden="true">{leg}</div></div></div>'
            + (f'<figcaption>{caption}</figcaption>' if caption else "")
            + f'</figure><script type="application/json" id="{uid}-data">{js}</script>' + JS.replace("__UID__", uid))


def selftest():
    sys.path.insert(0, HERE)
    import rodents_chicago as R
    # a planted city: 77 squares on an 11 x 7 grid
    areas = []
    for i, (n, nm) in enumerate(sorted(R.AREAS.items())):
        x, y = -87.9 + (i % 11) * 0.03, 41.7 + (i // 11) * 0.04
        sq = [[x, y], [x + 0.03, y], [x + 0.03, y + 0.04], [x, y + 0.04], [x, y]]
        areas.append({"n": n, "name": nm, "polys": [[sq]]})
    geo = {"source": {}, "areas": areas}
    o = outline(geo)
    assert len(o["areas"]) == 77 and o["w"] == W and 600 < o["h"] < 1200, "77 shapes, city taller than wide"
    a1 = next(a for a in o["areas"] if a["n"] == 1)
    assert a1["d"].startswith("M") and a1["d"].endswith("z") and "l" in a1["d"], "relative path"
    assert nice_breaks([1, 2, 3, 50, 60, 70, 100, 150, 200, 300]) == sorted(set(nice_breaks([1, 2, 3, 50, 60, 70, 100, 150, 200, 300]))), "rising"
    cuts = nice_breaks(list(range(0, 250)))
    assert len(cuts) == 4 and all(b > a for a, b in zip(cuts, cuts[1:])), cuts
    assert klass(0, cuts) == 0 and klass(249, cuts) == 4, "classes 0 to 4"
    U = _anchor([(0, 0), (10, 0), (10, 10), (8, 10), (8, 2), (2, 2), (2, 10), (0, 10)])   # a U: centroid falls outside
    assert _inside(U[0], U[1], [(0, 0), (10, 0), (10, 10), (8, 10), (8, 2), (2, 2), (2, 10), (0, 10)]), "label inside odd shapes"
    m = [{"key": "a", "label": "A", "legendTitle": "A", "cls": {n: "q1" for n in R.AREAS}, "legend": [("q1", "var(--gm1)", "1 to 2")]}]
    html = choropleth({1: {"say": {"a": "3 things"}, "html": "<p>x</p>"}}, m, uid="t", title="T", hint="Tap", geo=geo)
    assert html.count("<path data-n=") == 77 and 'class="q1"' in html and "Rogers Park: 3 things" in html, "paths painted"
    assert "</script" not in html.split('id="t-data">')[1].split("</script>")[0], "data cannot close its script"
    assert "—" not in html and "–" not in html, "no dashes"
    print("geo_map selftest: ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
