#!/usr/bin/env python3
"""Chicago Restaurant Radar v1: the members' app (launches/chicago-restaurant-radar.md; Todd, live chat, Nov 2, 2026).

Follows every Chicago food business along the City's own records (tools/radar_chicago.py: build-out permit, pre-opening
food license inspection, new license, open) and tells a vendor who to reach this week.

Screens (hash routes, so a view can be bookmarked and the back button works):
  #/              Today: counters by stage, the community area map, the newest-first table
  #/b/<id>        One business: its timeline of City records, each linked to the City's own record, and the first letter
                  for the chosen trade, filled in for it (tools/radar_letters.py is the one source of the letters)
  #/rules?q=...   Rules: plain English read in the browser by a fixed word list (GRAMMAR_JS below) into chips the member can
                  see and remove; words it cannot read are shown, never guessed. No AI call, no cost per search. Miles as
                  the crow flies from a ZIP's or a community area's center; never drive time (that needs a paid routing service).
  #/trade?t=...   Trade switch: the same rows, the letter changes
  #/terms         The City's disclaimer word for word and ours

Same parts as the members' apps we already ship: tools/leads_app.py's stylesheet (read from it, never edited), its
encryption (tools/leads_page.py: AES-256-GCM under a PBKDF2-SHA256 key, 250,000 rounds, decrypted in the buyer's
browser; the repo holds only ciphertext) and the community area outline of tools/geo_map.py. A preview build (no
password) is only for Todd's private review link; it never goes to docs/.

Usage: python3 tools/radar_app.py --preview FULL.json OUT.html        the private preview (no password gate)
       RADAR_PASSWORD=... python3 tools/radar_app.py FULL.json OUT.html  the members' build (encrypted)
       python3 tools/radar_app.py --selftest
"""
import datetime as dt, json, math, os, re, subprocess, shutil, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import geo_map  # noqa: E402
import leads_app  # noqa: E402  (stylesheet only)
import radar_chicago as RC  # noqa: E402
import radar_letters as RL  # noqa: E402
from leads_page import decrypt, encrypt  # noqa: E402
from leads_xlsx import CITY_DISCLAIMER  # noqa: E402

PRODUCT = "Chicago Restaurant Radar"
LEGAL = ("Public City of Chicago building permit, food inspection and business license records, as of __ASOF__. " + CITY_DISCLAIMER +
         " ProofNotFluff is not affiliated with or endorsed by the City of Chicago, and no business listed has endorsed or works with "
         "ProofNotFluff. A stage repeats what the City's records show; it does not say a business is open, safe or buying anything. "
         "You make your own calls, letters and emails and are responsible for following the law when you do. Licensed to one business "
         "for its own prospecting; no reselling or republishing. Made with AI assistance. Read the Terms of Use.")
TERMS_LINK = "Terms of Use"
LETTER_RULES = ["Name the City's record and its date, and stop there. Don't say the business is open, new to Chicago or in need of "
                "your service unless it tells you so, and never repeat an inspection result.",
                "Keep every claim about your company true, and never say you work with the City.",
                "One letter or email per business. Every email needs a true subject line, your real name and company, a plain line "
                "saying it is a sales email, your business street address and a way to say stop, and a stop request must be honored "
                "within 10 business days (the federal CAN-SPAM Act covers business email; source: FTC, CAN-SPAM Act: A Compliance "
                "Guide for Business, ftc.gov)."]
STAGE_HELP = {"permitted": "A building permit for food work at the address, no license inspection yet",
              "inspected": "The City's pre-opening food license inspection, no license issued yet",
              "licensed": "A new food license issued, no sign of opening on the City's records yet",
              "open": "A routine City inspection passed after the license, or 30 days since the license (our rule)"}

# neighborhood names people type, each mapped to the community area it sits in (the chip says both)
ALIASES = {"pilsen": "Lower West Side", "little village": "South Lawndale", "wicker park": "West Town", "ukrainian village": "West Town",
           "east village": "West Town", "bucktown": "Logan Square", "andersonville": "Edgewater", "wrigleyville": "Lake View",
           "boystown": "Lake View", "lakeview": "Lake View", "chinatown": "Armour Square", "river north": "Near North Side",
           "gold coast": "Near North Side", "streeterville": "Near North Side", "west loop": "Near West Side", "fulton market": "Near West Side",
           "south loop": "Near South Side", "bronzeville": "Douglas", "back of the yards": "New City", "the loop": "Loop", "downtown": "Loop",
           "ohare": "O'Hare", "o hare": "O'Hare", "ravenswood": "Lincoln Square", "printers row": "Loop", "greektown": "Near West Side",
           "little italy": "Near West Side", "old town": "Near North Side", "humboldt": "Humboldt Park"}


def base_css():
    return re.search(r"<style>(.*?)</style>", leads_app.PAGE, re.S).group(1)


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def area_centers(geo=None):
    """{community area name: [lat, lon]}: the center of each area's largest outer ring (its shape's own centroid)."""
    geo = geo or geo_map.load()
    out = {}
    for a in geo["areas"]:
        ring = max((poly[0] for poly in a["polys"]), key=lambda r: abs(geo_map._area(r)))
        cx, cy = geo_map._centroid(ring)
        out[a["name"]] = [round(cy, 5), round(cx, 5)]
    return out


def vocab(zips, areas):
    """The fixed word list the rule box reads. Every phrase is a list of words; the longest phrase at a spot wins."""
    T = lambda s: s.split()
    trades = {"pest": ["pest control", "pest", "pests", "exterminator", "exterminators", "exterminating"],
              "hood": ["hood and exhaust cleaning", "hood and exhaust", "hood cleaning", "exhaust cleaning", "kitchen exhaust", "hood", "hoods", "exhaust"],
              "grease": ["grease trap service", "grease trap", "grease traps", "grease", "interceptor", "interceptors"],
              "clean": ["commercial cleaning", "cleaning", "janitorial", "cleaners", "cleaner"],
              "pos": ["point of sale", "pos", "payments", "card payments"],
              "signs": ["signs", "sign", "signage"], "insurance": ["insurance", "insurer", "coverage"]}
    stages = {"permitted": ["permitted", "permit", "permits", "build out", "buildout", "build outs", "building permit", "building permits", "under construction", "construction"],
              "inspected": ["inspected", "inspection", "inspections", "pre opening", "preopening", "license inspection", "pre opening inspection"],
              "licensed": ["licensed", "license", "licenses", "newly licensed"],
              "open": ["open", "opened", "now open", "already open"],
              "notopen": ["not open", "not open yet", "not yet open", "opening soon", "about to open", "before opening", "moving toward open", "on the way"]}
    kinds = {"restaurant": ["restaurant", "restaurants", "dining"],
             "coffee": ["coffee", "coffee shop", "coffee shops", "cafe", "cafes", "tea", "juice", "juice bar", "juice bars"],
             "bakery": ["bakery", "bakeries", "dessert", "desserts", "ice cream", "donut", "donuts", "pastry"],
             "bar": ["bar", "bars", "tavern", "taverns", "brewery", "breweries", "pub", "pubs"],
             "grocery": ["grocery", "groceries", "grocery store", "grocery stores", "market", "markets", "supermarket"],
             "liquor": ["liquor store", "liquor stores", "liquor", "package goods"],
             "catering": ["caterer", "caterers", "catering", "shared kitchen", "shared kitchens", "ghost kitchen"]}
    orders = {"newest": ["newest first", "latest first", "most recent first", "newest", "latest", "most recent"],
              "oldest": ["oldest first", "oldest"], "closest": ["closest first", "nearest first", "closest", "nearest", "by distance"],
              "name": ["by name", "a to z", "alphabetical"]}
    fill = ("and or with that are is the a an for me show find all only any businesses business places place spots food who which "
            "have has been just new in at of to from please list leads lead give get my i want those these them first me").split()
    norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("'", "")).split()
    area_ph = [[norm(n), n] for n in areas] + [[norm(k), v] for k, v in ALIASES.items()]
    return {"trades": [[T(p), k] for k, ps in trades.items() for p in ps], "stages": [[T(p), k] for k, ps in stages.items() for p in ps],
            "kinds": [[T(p), k] for k, ps in kinds.items() for p in ps], "orders": [[T(p), k] for k, ps in orders.items() for p in ps],
            "fill": fill, "areas": area_ph, "areaCenter": areas, "zips": {z: v[:2] for z, v in zips.items()},
            "tradeLabel": {t["key"]: t["label"] for t in RL.TRADES}, "kindLabel": RC.KIND_LABEL,
            "stageLabel": dict(RC.STAGE_LABEL, notopen="Not open yet"), "aliases": {" ".join(norm(k)): v for k, v in ALIASES.items()}}


def payload(full):
    o = geo_map.outline()
    proj = o["project"]
    biz = []
    for b in full["businesses"]:
        rec = RL.pick_record(b["events"])
        x = y = None
        if b.get("lat") and b.get("lon"):
            x, y = proj(b["lon"], b["lat"])
        biz.append({"id": b["id"], "n": b["name"], "a": b["address"], "z": b.get("zip") or "", "ar": b.get("area") or "", "lat": b.get("lat"), "lon": b.get("lon"),
                    "x": None if x is None else round(x, 1), "y": None if y is None else round(y, 1), "k": b["kind"], "s": b["stage"], "sd": b["stageDate"],
                    "ob": b.get("openBy") or "", "lt": b.get("licenseType") or "", "ot": b.get("otherTypes") or [], "ac": b.get("activity") or "",
                    "hi": b.get("history") or "", "sh": bool(b.get("shared")), "li": b.get("lics") or [], "f": b["first"], "l": b["last"],
                    "st": RL.street_of(b["address"]), "rec": {"t": rec["t"], "d": rec["d"], "ty": rec.get("type") or ""} if rec else None,
                    "ev": [{k: v for k, v in e.items() if v not in (None, "", False)} for e in b["events"]]})
    zips = full.get("zips") or {}
    centers = area_centers()
    return {"asOf": full["asOf"], "window": full["window"], "biz": biz, "source": full["source"], "match": {k: full["match"].get(k) for k in ("byStage", "licensedFood")},
            "vocab": vocab(zips, centers), "map": {"w": o["w"], "h": o["h"], "areas": [{"n": a["n"], "name": a["name"], "d": a["d"]} for a in o["areas"]]}}


def letters_json():
    return {"trades": RL.TRADES, "record": RL.RECORD_LINE, "open": RL.OPEN, "sign": RL.SIGN, "stop": RL.STOP, "subjectWords": RL.SUBJECT_NAME_WORDS,
            "rules": LETTER_RULES}


def legal_html():
    """Two paragraphs: the City's records and its disclaimer word for word, then ours."""
    assert LEGAL.count(TERMS_LINK) == 1 and LEGAL.count(CITY_DISCLAIMER) == 1
    cut = LEGAL.index(CITY_DISCLAIMER) + len(CITY_DISCLAIMER)
    a, b = LEGAL[:cut], LEGAL[cut:].strip()
    return f"<p>{_esc(a)}</p><p>" + _esc(b).replace(TERMS_LINK, f'<a href="#/terms">{TERMS_LINK}</a>') + "</p>"


def as_of_text(iso):
    d = dt.date.fromisoformat(iso)
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def build_html(full, password=None):
    """password=None builds the private preview (data in the page, no gate); otherwise the data travels encrypted."""
    data = json.dumps(payload(full), separators=(",", ":"), ensure_ascii=False)
    asof = as_of_text(full["asOf"])
    if password:
        box = json.dumps(encrypt(password, data.encode()))
        boot = f"const BOX={box};const PREVIEW=null;"
    else:
        boot = "const BOX=null;const PREVIEW=" + data.replace("</", "<\\/") + ";"
    js = lambda o: json.dumps(o, ensure_ascii=False).replace("</", "<\\/")
    return (PAGE.replace("__BASECSS__", base_css()).replace("__GMCSS__", re.search(r"<style>(.*?)</style>", geo_map.CSS, re.S).group(1))
            .replace("__BOOT__", boot).replace("__LETTERS__", js(letters_json())).replace("__GRAMMAR__", GRAMMAR_JS).replace("__LETTERJS__", LETTER_JS)
            .replace("__STAGEHELP__", js(STAGE_HELP)).replace("__CITY__", js(CITY_DISCLAIMER)).replace("__LEGAL__", legal_html())
            .replace("__ASOF__", asof).replace("__PREVIEWCLASS__", "" if password else " preview"))


def build(full_path, out, password=None):
    full = json.load(open(full_path, encoding="utf-8"))
    html = build_html(full, password)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    return {"businesses": len(full["businesses"]), "bytes": len(html), "encrypted": bool(password)}


# ---------------------------------------------------------------- the rule reader (pure; the selftest runs it in node)
GRAMMAR_JS = r"""
const RULE_NUM={one:1,two:2,three:3,four:4,five:5,six:6,seven:7,eight:8,nine:9,ten:10,a:1,half:0.5};
function ruleTokens(text){const out=[];const re=/[\p{L}\p{N}]+(?:[.'’][\p{L}\p{N}]+)*/gu;let m;
while((m=re.exec(text))){const w=m[0].normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/['’]/g,"");out.push({w,s:m.index,e:m.index+m[0].length});}return out;}
function longest(tokens,i,list){let best=null;for(const [ph,val] of list){if(ph.length&&(!best||ph.length>best.n)&&i+ph.length<=tokens.length){let ok=true;for(let j=0;j<ph.length;j++)if(tokens[i+j].w!==ph[j]){ok=false;break;}if(ok)best={n:ph.length,val};}}return best;}
function placeAt(tokens,i,V){const t=tokens[i];if(!t)return null;
if(/^\d{5}$/.test(t.w))return V.zips[t.w]?{n:1,val:{type:"zip",zip:t.w,center:V.zips[t.w],label:"ZIP "+t.w}}:{n:1,bad:"ZIP "+t.w+" is not a Chicago ZIP on the City's license records"};
const a=longest(tokens,i,V.areas);if(a){const name=a.val;const typed=tokens.slice(i,i+a.n).map(x=>x.w).join(" ");
const plain=x=>x.toLowerCase().replace(/^the /,"").replace(/[^a-z0-9 ]/g,"");const shown=tokens.raw?tokens.raw.slice(tokens[i].s,tokens[i+a.n-1].e):typed;
return {n:a.n,val:{type:"area",area:name,center:V.areaCenter[name],label:V.aliases[typed]&&plain(typed)!==plain(name)?name+" ("+shown+")":name}};}
return null;}
function numAt(tokens,i){const t=tokens[i];if(!t)return null;if(/^\d+(?:\.\d+)?$/.test(t.w))return +t.w;if(t.w in RULE_NUM&&tokens[i+1]&&/^(mile|miles|mi)$/.test(tokens[i+1].w))return RULE_NUM[t.w];return null;}
function radiusAt(tokens,i,V){let j=i;if(tokens[j]&&/^(within|inside|under)$/.test(tokens[j].w))j++;const n=numAt(tokens,j);
if(n===null||!tokens[j+1]||!/^(mile|miles|mi)$/.test(tokens[j+1].w))return null;let k=j+2;if(tokens[k]&&/^(of|from|around)$/.test(tokens[k].w))k++;
const p=placeAt(tokens,k,V);if(!p||p.bad||!(n>0)||n>30)return {n:k-i,bad:true};
return {n:k-i+p.n,val:{type:"radius",miles:n,center:p.val.center,zip:p.val.zip,area:p.val.area,label:"Within "+n+" mi of "+p.val.label}};}
function timeAt(tokens,i){const w=k=>tokens[i+k]?tokens[i+k].w:"";
if(w(0)==="this"&&w(1)==="week")return {n:2,days:7,label:"This week"};if(w(0)==="this"&&w(1)==="month")return {n:2,days:30,label:"This month"};
if(w(0)==="today")return {n:1,days:1,label:"Today"};
if(/^(last|past)$/.test(w(0))){if(/^(week)$/.test(w(1)))return {n:2,days:7,label:"Last 7 days"};if(w(1)==="month")return {n:2,days:30,label:"Last 30 days"};
const n=/^\d+$/.test(w(1))?+w(1):(RULE_NUM[w(1)]||null);if(n&&/^(day|days)$/.test(w(2)))return {n:3,days:n,label:"Last "+n+" day"+(n===1?"":"s")};
if(n&&/^(week|weeks)$/.test(w(2)))return {n:3,days:7*n,label:"Last "+(7*n)+" days"};if(n&&/^(month|months)$/.test(w(2)))return {n:3,days:30*n,label:"Last "+(30*n)+" days"};}
return null;}
function parseRule(text,V){const tk=ruleTokens(text||"");tk.raw=text||"";const chips=[],unread=[];const f={stages:[],kinds:[],trade:"",place:null,days:0,order:""};
const span=(i,n)=>[tk[i].s,tk[i+n-1].e];let i=0;
while(i<tk.length){let r;
if((r=radiusAt(tk,i,V))){if(r.bad){for(let j=i;j<i+r.n;j++)unread.push({w:tk[j].w,s:tk[j].s,e:tk[j].e,hint:"place"});if(r.n===0){unread.push({w:tk[i].w,s:tk[i].s,e:tk[i].e,hint:"place"});i++;}else i+=r.n;continue;}
f.place=r.val;chips.push({cat:"place",label:r.val.label,span:span(i,r.n)});i+=r.n;continue;}
if((r=placeAt(tk,i,V))){if(r.bad){unread.push({w:tk[i].w,s:tk[i].s,e:tk[i].e,hint:"zip",note:r.bad});i++;continue;}
f.place=r.val;chips.push({cat:"place",label:(r.val.type==="zip"?"In ":"In ")+r.val.label,span:span(i,r.n)});i+=r.n;continue;}
if((r=timeAt(tk,i))){f.days=r.days;chips.push({cat:"time",label:r.label,span:span(i,r.n)});i+=r.n;continue;}
const cands=[["orders",longest(tk,i,V.orders)],["stages",longest(tk,i,V.stages)],["trades",longest(tk,i,V.trades)],["kinds",longest(tk,i,V.kinds)]].filter(x=>x[1]);
if(cands.length){cands.sort((a,b)=>b[1].n-a[1].n);const [cat,m]=cands[0];const sp=span(i,m.n);
if(cat==="orders"){f.order=m.val;chips.push({cat:"order",label:{newest:"Newest first",oldest:"Oldest first",closest:"Closest first",name:"By name"}[m.val],span:sp});}
else if(cat==="stages"){const add=m.val==="notopen"?["permitted","inspected","licensed"]:[m.val];if(!chips.some(c=>c.cat==="stage"&&c.val===m.val)){f.stages=[...new Set(f.stages.concat(add))];chips.push({cat:"stage",val:m.val,label:V.stageLabel[m.val],span:sp});}else chips.find(c=>c.cat==="stage"&&c.val===m.val).more=(chips.find(c=>c.cat==="stage"&&c.val===m.val).more||[]).concat([sp]);}
else if(cat==="trades"){const same=chips.find(c=>c.cat==="trade"&&c.val===m.val);if(same)same.more=(same.more||[]).concat([sp]);else{f.trade=m.val;chips.push({cat:"trade",val:m.val,label:V.tradeLabel[m.val],span:sp});}}
else{if(!f.kinds.includes(m.val)){f.kinds.push(m.val);chips.push({cat:"kind",val:m.val,label:V.kindLabel[m.val],span:sp});}else chips.find(c=>c.cat==="kind"&&c.val===m.val).more=(chips.find(c=>c.cat==="kind"&&c.val===m.val).more||[]).concat([sp]);}
i+=m.n;continue;}
if(V.fill.includes(tk[i].w)){i++;continue;}
unread.push({w:tk[i].w,s:tk[i].s,e:tk[i].e,hint:tk[i].w==="near"?"near":""});i++;}
return {chips,unread,f};}
function miles(a,b){const R=3958.8,r=x=>x*Math.PI/180;const dLa=r(b[0]-a[0]),dLo=r(b[1]-a[1]);const h=Math.sin(dLa/2)**2+Math.cos(r(a[0]))*Math.cos(r(b[0]))*Math.sin(dLo/2)**2;return 2*R*Math.asin(Math.sqrt(h));}
function addDays(iso,n){const d=new Date(iso+"T12:00:00Z");d.setUTCDate(d.getUTCDate()+n);return d.toISOString().slice(0,10);}
function applyRule(rows,f,asOf){let out=rows.slice();const notes=[];
if(f.stages.length)out=out.filter(b=>f.stages.includes(b.s));
if(f.kinds.length)out=out.filter(b=>f.kinds.includes(b.k));
if(f.days){const from=addDays(asOf,-(f.days-1));out=out.filter(b=>b.sd>=from);}
const ctr=f.place&&f.place.center;
if(f.place){if(f.place.type==="radius"){const no=out.filter(b=>b.lat==null).length;out=out.filter(b=>b.lat!=null&&miles(ctr,[b.lat,b.lon])<=f.place.miles);if(no)notes.push(no+" without a map point on the City's record left out");}
else if(f.place.type==="zip"){const no=out.filter(b=>!b.z).length;out=out.filter(b=>b.z===f.place.zip);if(no)notes.push(no+" without a ZIP on the City's record (permit only rows) left out");}
else out=out.filter(b=>b.ar===f.place.area);}
if(ctr)for(const b of out)b._mi=b.lat==null?null:miles(ctr,[b.lat,b.lon]);
const o=f.order||"newest";
if(o==="closest"&&!ctr)notes.push("Closest first needs a place, so the list stays newest first");
if(o==="closest"&&ctr)out.sort((a,b)=>(a._mi??1e9)-(b._mi??1e9));
else if(o==="oldest")out.sort((a,b)=>a.sd.localeCompare(b.sd)||a.id.localeCompare(b.id));
else if(o==="name")out.sort((a,b)=>(a.n||"~"+a.st).localeCompare(b.n||"~"+b.st));
else out.sort((a,b)=>b.sd.localeCompare(a.sd)||b.id.localeCompare(a.id));
return {rows:out,notes};}
"""

# ---------------------------------------------------------------- the letter (pure; the selftest checks it against radar_letters.fill)
LETTER_JS = r"""
const L_MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function lDate(iso){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(iso||"");return m?L_MON[+m[2]-1]+" "+(+m[3]):"";}
function lFmt(t,o){return t.replace(/\{(\w+)\}/g,(_,k)=>o[k]??"");}
function letterFor(b,trade,me,LT){const t=LT.trades.find(x=>x.key===trade);const r=b.rec;if(!t||!r)return null;
const name=b.n||"";const who=name?name+" team":"there";
const rec=lFmt(LT.record[r.t],{licenseType:(r.ty||b.lt||"").trim()||"food",street:b.st,date:lDate(r.d)});
const nw=(name.match(/[A-Za-z0-9$][A-Za-z0-9$'.,%-]*/g)||[]).length;const subject=lFmt(t.subject,{name:!name?"the new space on "+b.st:nw<=LT.subjectWords?name:"your space on "+b.st});
const body=[lFmt(LT.open,Object.assign({who},me)),rec,t.offer,t.ask].join(" ");
return {subject,body,sign:lFmt(LT.sign,me),stop:lFmt(LT.stop,me)};}
"""

PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#1D2433">
<title>Chicago Restaurant Radar | ProofNotFluff</title>
<style>__BASECSS__
__GMCSS__
/* ---- Restaurant Radar ---- */
:root{--s-permitted:#2F5F9E;--s-permitted-bg:#E6EDF6;--s-inspected:#7A5A12;--s-inspected-bg:#F6EDD5;--s-licensed:#2E6B66;--s-licensed-bg:#E3EFED;--s-open:#1D2433;--s-open-bg:#E4E2EC;--warn:#8A4B0F;--warn-bg:#FCEEDD}
.bnav{grid-template-columns:repeat(3,1fr)!important}
.pvw{display:none}.preview .pvw{display:block;background:#FCEEDD;color:#5B3A0C;border-bottom:1px solid #EBD3B4;font-size:13.5px;font-weight:600}
.pvw p{max-width:1320px;margin:0 auto;padding:8px 16px}
.eyebrow{margin:0 0 8px;font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--accent-ink)}
.ph h1{max-width:900px}
.sp{display:inline-flex;align-items:center;gap:6px;height:26px;padding:0 10px;border-radius:999px;font-size:12.5px;font-weight:700;white-space:nowrap;line-height:1}
.sp i{width:8px;height:8px;border-radius:50%;background:currentColor;flex:none}
.sp.permitted{color:var(--s-permitted);background:var(--s-permitted-bg)}.sp.inspected{color:var(--s-inspected);background:var(--s-inspected-bg)}
.sp.licensed{color:var(--s-licensed);background:var(--s-licensed-bg)}.sp.open{color:var(--s-open);background:var(--s-open-bg)}
.sp.lg{height:32px;padding:0 14px;font-size:14px}
/* stage counters */
.stg{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 22px}
@media(max-width:1000px){.stg{grid-template-columns:repeat(2,minmax(0,1fr))}}
.sc{position:relative;display:flex;flex-direction:column;padding:16px 16px 14px;border-radius:var(--r);background:#fff;border:1px solid var(--line);box-shadow:var(--sh);text-decoration:none;color:var(--ink);min-width:0;border-top:4px solid var(--c)}
.sc .n{font:700 34px/1 var(--head);letter-spacing:-.02em;margin:4px 0 6px;font-variant-numeric:tabular-nums}
.sc .t{display:flex;align-items:center;gap:8px;font-weight:700;font-size:15px}.sc .t .ar{margin-left:auto;color:var(--muted)}
.sc .w{font-size:13.5px;color:var(--muted)}.sc .w .nt{display:inline-block;padding:1px 7px;border-radius:6px;background:var(--paper2);color:var(--ink);font-weight:700;font-size:12.5px;margin-right:2px}
.sc.open{background:#F7F5F0;box-shadow:none}.sc.open .n{font-size:26px;margin:8px 0 8px}
.ph.hero{align-items:flex-end}.cta{min-height:48px;padding:0 20px;font-size:15.5px;white-space:nowrap}
@media(max-width:700px){.ph.hero .cta{width:100%}}
@media(min-width:1021px){.stick{position:sticky;top:76px;align-self:start}}
.next{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 20px;margin:24px 0 0;padding:18px 20px;border-radius:var(--r);background:#fff;border:1px dashed #D8CFBE}
.next p{margin:0;font-weight:600;color:var(--ink2)}
@media(max-width:600px){.next .btn{width:100%}}
.foot-legal p{max-width:720px;font-size:13px;margin:0 0 10px}
.sec-h.wrap{flex-wrap:wrap}
.fbar select,.mfind select{appearance:none;-webkit-appearance:none;height:44px;border-radius:10px;padding:0 38px 0 12px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%231D2433' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") no-repeat right 14px center;cursor:pointer}
.fbar select:focus-visible,.mfind select:focus-visible{outline:none;box-shadow:var(--focus);border-color:var(--blue)}
.to{margin:14px 0 8px;font-size:14px;color:var(--ink2)}.to b{color:var(--ink)}
.cpn{margin:8px 0 0;font-size:13px;color:var(--muted)}
#cp[aria-disabled=true]{opacity:.6}
.terms{max-width:820px;margin:0 auto}.terms .tx p{max-width:none}
.sc .h{font-size:13px;color:var(--muted);margin:8px 0 0;line-height:1.4}
.sc[aria-current=true]{background:var(--ink);border-color:var(--ink);color:#fff;border-top-color:var(--c)}.sc[aria-current=true] .w,.sc[aria-current=true] .h,.sc[aria-current=true] .t .ar{color:#C9CFDB}.sc[aria-current=true] .w b{color:#F7B9A5}
@media(hover:hover){.sc:hover .t span{text-decoration:underline;text-underline-offset:3px}}
@media(max-width:600px){.stg{gap:8px}.sc{padding:12px 12px 10px}.sc .n{font-size:26px}.sc .h{display:none}.sc .t{font-size:14px}}
.sc.permitted{--c:var(--s-permitted)}.sc.inspected{--c:#B88A1E}.sc.licensed{--c:var(--s-licensed)}.sc.open{--c:#6B6E7E}
/* today layout */
.tdy{display:grid;grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:20px;align-items:start}
@media(max-width:1020px){.tdy{grid-template-columns:minmax(0,1fr)}}
.fbar{display:flex;flex-wrap:wrap;gap:10px 12px;align-items:center;padding:0 20px 14px}
.fbar .seg{border-color:var(--line)}
.fbar select{height:44px;padding:0 36px 0 12px;border:1px solid var(--field);border-radius:10px;background:#fff;font-weight:600;font-size:14.5px;max-width:100%}
.clr{border:0;background:none;color:var(--blue);font-weight:600;font-size:14px;min-height:44px;padding:0 6px;cursor:pointer;text-decoration:underline;text-underline-offset:3px}
table.rt{width:100%;border-collapse:collapse;font-size:14.5px}
.rt th{text-align:left;font-size:12.5px;font-weight:700;color:var(--muted);padding:10px 12px;border-top:1px solid var(--line2);border-bottom:1px solid var(--line2);background:#FBFAF7;white-space:nowrap}
.rt th:first-child,.rt td:first-child{padding-left:20px}.rt th:last-child,.rt td:last-child{padding-right:20px}
.rt td{padding:12px;border-bottom:1px solid var(--line2);vertical-align:top}
.rt tr:hover td{background:#FBFAF7}
.rt .bn{font:700 15.5px/1.3 var(--head);color:var(--ink);text-decoration:none}
.rt .bn:hover{text-decoration:underline;text-underline-offset:3px}

.rt .sub{display:block;color:var(--muted);font-size:13px;margin-top:2px}
.rt .dt{white-space:nowrap;font-variant-numeric:tabular-nums}.rt .dt small{display:block;color:var(--muted);font-size:12.5px}
.rt .mi{font-variant-numeric:tabular-nums;white-space:nowrap;color:var(--ink2)}
@media(max-width:700px){table.rt thead{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
 table.rt,table.rt tbody,table.rt tr,table.rt td{display:block;width:100%}
 table.rt tr{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:4px 10px;padding:12px 16px;border-bottom:1px solid var(--line2)}
 .rt td{padding:0!important;border:0}.rt td.c-b{grid-column:1 / -1}.rt td.c-a{grid-column:1;grid-row:2;color:var(--ink2);font-size:14px;align-self:center}
 .rt td.c-s{grid-column:2;grid-row:2;justify-self:end}.rt td.c-d{grid-column:1 / -1;grid-row:3;color:var(--muted);font-size:13.5px}.rt td.c-m{grid-column:1 / -1}
 .rt .dt small{display:inline;margin-left:6px;font-size:13px}.rt .bn{font-size:16px}}
.more{display:flex;justify-content:center;padding:14px 20px 18px}
.cnt{color:var(--muted);font:600 14px var(--body);margin-left:8px}
/* map */
.rmap{padding:0 16px 16px;--gm0:#fbe9e1;--gm1:#f3c0aa;--gm2:#e48d6a;--gm3:#c8502f;--gm4:#8a3017;--gmn:#ece8e1;--gmedge:#cfc6ba;--gmbg:#e6ecef}
.rmap .gm-stage{border-radius:10px;overflow:hidden;background:var(--gmbg,#e6ecef)}
.rmap svg{display:block;width:100%;height:auto;max-height:560px}
.rmap .gm-a path{fill:var(--gmn);stroke:var(--gmedge);stroke-width:.7;vector-effect:non-scaling-stroke}
.rmap .gm-a path.q0{fill:var(--gm0)}.rmap .gm-a path.q1{fill:var(--gm1)}.rmap .gm-a path.q2{fill:var(--gm2)}.rmap .gm-a path.q3{fill:var(--gm3)}.rmap .gm-a path.q4{fill:var(--gm4)}
.rmap .gm-a path.sel{stroke:var(--ink);stroke-width:2.5}
.rmap .gm-a path:hover{stroke:var(--ink);stroke-width:1.6}
.rmap .gm-a path{cursor:pointer}
.rmap .dots circle{stroke:#fff;stroke-width:.8;pointer-events:none}
.rmap .dots .permitted{fill:var(--s-permitted)}.rmap .dots .inspected{fill:#B88A1E}.rmap .dots .licensed{fill:var(--s-licensed)}.rmap .dots .open{fill:#6B6E7E}
.mleg{display:flex;flex-wrap:wrap;gap:6px 14px;margin:10px 2px 0;font-size:13px;color:var(--ink2)}
.mleg span{display:inline-flex;align-items:center;gap:6px}.mleg i{width:10px;height:10px;border-radius:50%;display:inline-block}
.mleg .scale{gap:0}.mleg .scale i{border-radius:2px;width:16px;margin:0}.mleg .scale i:last-of-type{margin-right:6px}
.mfind{display:grid;gap:4px;margin:0 0 10px;font-size:12.5px;font-weight:700;color:var(--muted)}
.mfind select{height:44px;padding:0 12px;border:1px solid var(--field);border-radius:10px;background:#fff;font-weight:600;font-size:14.5px;color:var(--ink)}
.mtop{list-style:none;margin:12px 0 0;padding:0;display:grid;gap:2px}
.mtop button{display:flex;width:100%;align-items:center;gap:10px;min-height:44px;padding:0 10px;border:0;border-radius:8px;background:none;font-size:14.5px;cursor:pointer;color:var(--ink);text-align:left}
.mtop button:hover{background:var(--paper)}.mtop button b{margin-left:auto;font-variant-numeric:tabular-nums}
.mtop .bar2{flex:0 0 90px;height:8px;border-radius:4px;background:var(--paper2);overflow:hidden}.mtop .bar2 i{display:block;height:100%;background:var(--accent)}
/* business page */
.bh{display:flex;flex-wrap:wrap;align-items:flex-start;justify-content:space-between;gap:12px 20px;margin:0 0 18px}
.bh h1{font-size:30px}@media(max-width:600px){.bh h1{font-size:24px}}
.bh .ad{margin:6px 0 0;color:var(--ink2);font-size:15.5px}.bh .ad .u{color:var(--muted)}
.steps4{list-style:none;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:0;margin:0 0 20px;padding:16px 20px;counter-reset:s}
.steps4 li{position:relative;padding:22px 8px 0 0;font-size:14px;color:var(--muted)}
.steps4 li::before{content:"";position:absolute;left:0;right:0;top:7px;height:3px;background:var(--line);border-radius:2px}
.steps4 li::after{content:"";position:absolute;left:0;top:0;width:17px;height:17px;border-radius:50%;background:#fff;border:2px solid var(--line);box-sizing:border-box}
.steps4 li.done::before{background:var(--c)}.steps4 li.done::after{background:var(--c);border-color:var(--c)}
.steps4 li.now::after{box-shadow:0 0 0 4px color-mix(in srgb,var(--c) 22%,transparent)}
.steps4 li b{display:block;color:var(--ink);font-size:14.5px;margin:4px 0 2px}.steps4 li.none b{color:var(--muted);font-weight:600}
.steps4 li.permitted{--c:var(--s-permitted)}.steps4 li.inspected{--c:#B88A1E}.steps4 li.licensed{--c:var(--s-licensed)}.steps4 li.open{--c:#6B6E7E}
@media(max-width:600px){.steps4{grid-template-columns:minmax(0,1fr);padding:12px 16px}.steps4 li{padding:0 0 14px 30px}.steps4 li::before{left:7px;right:auto;top:20px;bottom:0;width:3px;height:auto}.steps4 li:last-child::before{display:none}.steps4 li b{margin:0 0 2px}}
.bg2{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.05fr);gap:20px;align-items:start}
@media(max-width:1020px){.bg2{grid-template-columns:minmax(0,1fr)}}
.tl2{list-style:none;margin:0;padding:4px 20px 12px}
.tl2>li{position:relative;padding:0 0 18px 28px}
.tl2>li::before{content:"";position:absolute;left:6px;top:20px;bottom:-2px;width:2px;background:var(--line)}
.tl2>li:last-child::before{display:none}
.tl2 .dot{position:absolute;left:0;top:5px;width:14px;height:14px;border-radius:50%;border:3px solid var(--c);background:#fff}
.tl2 li.permit{--c:var(--s-permitted)}.tl2 li.linsp{--c:#B88A1E}.tl2 li.license{--c:var(--s-licensed)}.tl2 li.routine{--c:#6B6E7E}
.tl2 .hd{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}.tl2 .hd b{font-size:15px}.tl2 .hd .d{color:var(--muted);font-size:14px;font-variant-numeric:tabular-nums}
.tl2 p{margin:4px 0 0;font-size:14px;color:var(--ink2)}
.tl2 .res{display:inline-block;font-weight:700;font-size:12.5px;padding:2px 8px;border-radius:6px;background:var(--paper);color:var(--ink2);margin-left:2px}
.tl2 a.src{display:inline-flex;align-items:center;gap:6px;min-height:44px;margin:-6px 0 -10px;font-size:14px;font-weight:600}
.jl{display:none!important}@media(max-width:1020px){.jl{display:inline-flex!important}}
#lH{scroll-margin-top:calc(var(--bar-h) + 12px)}
.facts2{display:grid;grid-template-columns:auto minmax(0,1fr);gap:8px 16px;margin:0;padding:4px 20px 18px;font-size:14.5px}
.facts2 dt{color:var(--muted);font-weight:600}.facts2 dd{margin:0;color:var(--ink)}
.note2{margin:0 20px 18px;padding:10px 12px;border-radius:8px;background:var(--paper);font-size:13.5px;color:var(--ink2)}
/* letter */
.ltr{padding:0 20px 20px}
.tsw{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 14px}
.tsw button{display:inline-flex;align-items:center;min-height:44px;padding:0 14px;border-radius:999px;border:1px solid var(--line);background:#fff;color:var(--ink);font-weight:600;font-size:14px;cursor:pointer}
.tsw button[aria-pressed=true]{background:var(--ink);border-color:var(--ink);color:#fff}
@media(max-width:600px){.tsw{gap:6px}.tsw button{min-height:44px;padding:0 12px;font-size:13.5px}}
.paper{border:1px solid var(--line);border-radius:10px;background:#FFFEFB;padding:18px 18px 16px;font-size:15.5px;line-height:1.6;color:var(--ink)}
.paper .sj{margin:0 0 12px;padding:0 0 10px;border-bottom:1px solid var(--line2);font-size:14px;color:var(--ink2)}.paper .sj b{color:var(--ink)}
.paper p{margin:0 0 12px}.paper .sg{font-size:14.5px;color:var(--ink2)}.paper .st{font-size:13px;color:var(--muted);margin:0}
.paper .fl{background:#FCEEDD;color:#5B3A0C;border-radius:4px;padding:0 2px;font-weight:600;box-shadow:inset 0 -1px 0 #E3C9A6}
.lacts{display:flex;flex-wrap:wrap;gap:10px;margin:14px 0 0}
details.me{margin:14px 0 0;border:1px solid var(--line);border-radius:10px;background:#fff}
details.me summary{display:flex;align-items:center;min-height:48px;padding:0 14px;cursor:pointer;font-weight:600;font-size:14.5px;list-style:none}
details.me summary::-webkit-details-marker{display:none}
details.me summary::after{content:"";width:8px;height:8px;margin-left:auto;border-right:2px solid currentColor;border-bottom:2px solid currentColor;transform:rotate(45deg)}
details.me[open] summary::after{transform:rotate(-135deg)}
.mef{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px 12px;padding:0 14px 14px}
@media(max-width:600px){.mef{grid-template-columns:minmax(0,1fr)}}
.mef label{display:grid;gap:4px;font-size:12.5px;font-weight:700;color:var(--muted)}
.mef input{height:44px;padding:0 12px;border:1px solid var(--field);border-radius:10px;font-size:15px;color:var(--ink);background:#fff}
.mef input:focus{outline:none;box-shadow:var(--focus);border-color:var(--blue)}
.lrules{margin:14px 0 0;padding:0 0 0 18px;font-size:13.5px;color:var(--ink2)}.lrules li{margin:0 0 6px}
/* rules */
.rbox{padding:20px}
.rbox label.big{display:block;font:600 15px var(--body);margin:0 0 8px}
.rin{display:flex;gap:10px}
@media(max-width:600px){.rin{flex-direction:column}.rin input{flex:none;width:100%;height:52px;font-size:16px}.rin .btn{width:100%}}
.rin input{flex:1 1 auto;min-width:0;height:52px;padding:0 16px;border:1px solid var(--field);border-radius:12px;font-size:17px;background:#fff;color:var(--ink)}
.rin input:focus{outline:none;box-shadow:var(--focus);border-color:var(--blue)}
.rin .btn{height:52px}
.rhelp{margin:10px 0 0;font-size:13.5px;color:var(--muted)}
.exs{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0 0}
.exs button{min-height:44px;padding:6px 12px;border-radius:10px;border:1px dashed #CFC8BB;background:#FBFAF7;color:var(--ink2);font-size:13.5px;cursor:pointer;text-align:left}
.read{margin:18px 0 0;display:grid;gap:10px}
.read h3{font:700 12.5px var(--body);letter-spacing:.04em;text-transform:uppercase;color:var(--muted);margin:0}
.chips{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:0;padding:0}
.rc{display:inline-flex;align-items:center;gap:8px;min-height:40px;padding:0 4px 0 12px;border-radius:999px;font-size:14px;font-weight:600;border:1px solid}
.rc .k{font-size:11.5px;font-weight:700;letter-spacing:.04em;text-transform:uppercase;opacity:.8}
.rc button{display:grid;place-items:center;width:32px;height:32px;border-radius:50%;border:0;background:transparent;color:inherit;cursor:pointer}
.rc button:hover{background:rgba(29,36,51,.08)}
.rc.trade{background:#EFE9F7;border-color:#D9CCEB;color:#4B3577}.rc.stage{background:var(--s-licensed-bg);border-color:#B9D6D1;color:#1E4C48}
.rc.kind{background:#FBEAE4;border-color:#EFC9BB;color:#7E2E17}.rc.place{background:var(--s-permitted-bg);border-color:#C3D3E8;color:#23497A}
.rc.time{background:#F6EDD5;border-color:#E6D3A3;color:#5E450D}.rc.order{background:#ECE6DA;border-color:#D8CFBE;color:#3A4152}
.rc.no{background:var(--warn-bg);border-color:#EBC9A2;color:var(--warn);border-style:dashed;padding-right:12px}
.nohint{margin:0;font-size:13.5px;color:var(--warn)}
.rres{margin:20px 0 0}
.rres .sec-h{padding-top:16px}
.notes{margin:0 20px 12px;font-size:13.5px;color:var(--muted)}
.saved{list-style:none;margin:0;padding:0 20px 16px;display:grid;gap:6px}
.saved li{display:flex;align-items:center;gap:8px}.saved a{flex:1;min-width:0;display:flex;align-items:center;min-height:44px;padding:0 12px;border-radius:8px;background:var(--paper);color:var(--ink);text-decoration:none;font-size:14.5px}
.saved a:hover{text-decoration:underline}
.saved button{min-height:44px;min-width:44px;border:0;background:none;color:var(--muted);cursor:pointer;border-radius:8px}
/* trades */
.tgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:12px;padding:0 0 18px}
.tl3{list-style:none;margin:0;padding:0}
.tl3 li{padding:14px 20px;border-top:1px solid var(--line2)}
.tl3 .top{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 10px}.tl3 .top a{font:700 15.5px var(--head);color:var(--ink)}
.tl3 .top .sub{color:var(--muted);font-size:13.5px}
.tl3 .lp{margin:8px 0 0;padding:10px 12px;border-radius:8px;background:#FFFEFB;border:1px solid var(--line2);font-size:14px;color:var(--ink2)}
.tl3 .lp{max-width:72ch}.tl3 .lp b{color:var(--ink)}.tl3 .lp .fl{background:#FCEEDD;color:#5B3A0C;border-radius:4px;padding:0 2px;font-weight:600}
.tl3 .la{display:flex;gap:8px;margin:8px 0 0}
.terms .tx{padding:0 20px 18px}.terms .tx p{margin:0 0 10px}
</style></head><body class="__PREVIEWCLASS__">
<a class="skip" href="#app" id="skip">Skip to main content</a>
<header class="bar"><div class="bar-in">
<a class="brand" href="#/"><b>ProofNotFluff</b><span class="marks" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span><small>Chicago Restaurant Radar</small></a>
<nav class="tabs" id="tabs" aria-label="Sections" hidden></nav>
<span class="bar-sp"></span>
</div></header>
<div class="pvw" id="pvw"><p>Private preview. Not on proofnotfluff.com, no price, nothing sent. Data as of __ASOF__.</p></div>
<main id="gateView" class="gate" hidden>
<form class="gate-card" id="gate" novalidate>
<h1>Chicago Restaurant Radar</h1>
<p class="sub">Food businesses on their way to opening, from the City of Chicago's own records. Data as of __ASOF__.</p>
<label for="pw">Members' password</label>
<div class="pw"><input id="pw" type="password" autocomplete="current-password" autocapitalize="off" spellcheck="false" required aria-describedby="err"></div>
<button class="btn pri" type="submit" id="go">Open the radar</button>
<p class="err" id="err" role="alert"></p>
</form>
</main>
<main id="app" class="page" hidden tabindex="-1"></main>
<footer class="foot-legal" id="appLegal" hidden>__LEGAL__</footer>
<nav class="bnav" id="bnav" aria-label="Sections" hidden></nav>
<div class="toast" id="toast" role="status" aria-live="polite"></div>
<p class="sr" id="live" aria-live="polite"></p>
<script>
"use strict";
__BOOT__
const LT=__LETTERS__;
const STAGE_HELP=__STAGEHELP__;
const CITY=__CITY__;
__GRAMMAR__
__LETTERJS__
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const int=n=>Math.round(+n||0).toLocaleString("en-US");
const MON=L_MON;
function day(s){const m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s||"");return m?MON[+m[2]-1]+" "+(+m[3])+", "+m[1]:"";}
const dayShort=lDate;
const STAGES=["permitted","inspected","licensed","open"];
const SL={permitted:"Permitted",inspected:"Inspected",licensed:"Licensed",open:"Open"};
const EV={permit:"Building permit",linsp:"Food license inspection",license:"New license",routine:"Routine inspection"};
const sp=(s,lg)=>`<span class="sp ${s}${lg?" lg":""}"><i aria-hidden="true"></i>${SL[s]}</span>`;
const I={home:'<path d="M3 10.5 12 4l9 6.5V20a1 1 0 0 1-1 1h-5v-6h-6v6H4a1 1 0 0 1-1-1z"/>',rule:'<path d="M4 6h16M4 12h10M4 18h7"/><circle cx="18" cy="16" r="3"/><path d="m20.2 18.2 1.8 1.8"/>',
trade:'<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',back:'<path d="M15 18l-6-6 6-6"/>',x:'<path d="M6 6l12 12M18 6 6 18"/>',
ext:'<path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/>',copy:'<path d="M9 9h11v11H9z"/><path d="M5 15V5a1 1 0 0 1 1-1h9"/>',chev:'<path d="m9 6 6 6-6 6"/>'};
const ico=(n,c)=>`<svg class="ico${c?" "+c:""}" viewBox="0 0 24 24" aria-hidden="true">${I[n]}</svg>`;
function toast(t){const el=$("#toast");el.textContent=t;el.classList.add("on");clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove("on"),2600);}
function say(t){const el=$("#live");el.textContent="";setTimeout(()=>{el.textContent=t;},60);}
const store={get(k,d){try{const v=localStorage.getItem("radar."+k);return v==null?d:JSON.parse(v);}catch(e){return d;}},set(k,v){try{localStorage.setItem("radar."+k,JSON.stringify(v));}catch(e){}}};
async function copyText(t){try{await navigator.clipboard.writeText(t);return true;}catch(e){const a=document.createElement("textarea");a.value=t;a.setAttribute("readonly","");a.style.position="fixed";a.style.opacity="0";document.body.appendChild(a);a.select();let ok=false;try{ok=document.execCommand("copy");}catch(x){}a.remove();return ok;}}
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function openBox(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}

let D=null,BY={},V=null;
function prep(d){D=d;V=d.vocab;BY={};for(const b of d.biz)BY[b.id]=b;}
const ASOF=()=>D.asOf;
const weekFrom=()=>addDays(D.asOf,-6);
function trade(){const t=store.get("trade","pest");return LT.trades.some(x=>x.key===t)?t:"pest";}
function setTrade(t){store.set("trade",t);}
function me(){const m=store.get("me",{});return {me:m.me||"",company:m.company||"",phone:m.phone||"",companyAddress:m.companyAddress||""};}
const ME_LABEL={me:"Your name",company:"Company",phone:"Phone",companyAddress:"Company street address"};
function title(b){return b.n||("Food build-out on "+b.st);}


function parse(){const h=(location.hash||"#/").slice(1);const [p,qs]=h.split("?");return {parts:p.split("/").filter(Boolean),q:new URLSearchParams(qs||"")};}
function go(h){location.hash=h;}
function setNav(v){const items=[["today","#/","Today","home"],["rules","#/rules","Rules","rule"],["trade","#/trade","Trades","trade"]];
const html=items.map(([k,h,t,i])=>`<a href="${h}"${k===v?' aria-current="page"':""}>${ico(i)}${t}</a>`).join("");$("#tabs").innerHTML=html;$("#bnav").innerHTML=html;}
function route(){const {parts,q}=parse();const v=parts[0]||"today";let nav=v;
if(v==="b"&&BY[parts[1]]){viewBiz(BY[parts[1]]);nav="";}
else if(v==="rules")viewRules(q);
else if(v==="trade")viewTrade(q);
else if(v==="terms"){viewTerms();nav="";}
else{viewToday(q);nav="today";}
setNav(nav);window.scrollTo(0,0);const h=$("#app h1");if(h&&route.ready){h.setAttribute("tabindex","-1");h.focus({preventScroll:true});}route.ready=true;}

/* ---------- Today ---------- */
const stageOk=(b,st)=>!st||(st==="moving"?b.s!=="open":b.s===st);
function viewToday(q){const st=q.get("s")||"",ar=q.get("ar")||"",wd=+(q.get("w")||0),n=+(q.get("n")||40);
const all=D.biz,moving=all.filter(b=>b.s!=="open");const wk=weekFrom();
document.title="Today | Chicago Restaurant Radar";
const cnt={};for(const s of STAGES){const r=all.filter(b=>b.s===s);cnt[s]={n:r.length,w:r.filter(b=>b.sd>=wk).length};}
const wf=wd?addDays(D.asOf,-(wd-1)):"";let rows=all.filter(b=>stageOk(b,st)&&(!ar||b.ar===ar)&&(!wf||b.sd>=wf));rows.sort((a,b)=>b.sd.localeCompare(a.sd)||b.id.localeCompare(a.id));
const thisWeek=moving.filter(b=>b.sd>=wk).length;
const href=(o)=>{const p=new URLSearchParams();const s2=o.s??st,a2=o.ar??ar,w2=o.w??wd;if(s2)p.set("s",s2);if(a2)p.set("ar",a2);if(+w2)p.set("w",w2);if(o.n)p.set("n",o.n);const t=p.toString();return "#/"+(t?"?"+t:"");};
const areas=[...new Set(all.map(b=>b.ar).filter(Boolean))].sort();
$("#app").innerHTML=`<div class="ph hero"><div><p class="eyebrow">Chicago Restaurant Radar</p><h1>${int(moving.length)} Chicago food businesses moving toward opening</h1>
<p>From the City of Chicago's building permits, food inspections and business licenses, ${esc(day(D.window.from))} to ${esc(day(D.asOf))}. Each one sits in the furthest stage its City records reach.</p></div>
<a class="btn pri cta" href="#/?s=moving&w=7">See this week's ${int(thisWeek)}</a></div>
<nav class="stg" aria-label="Stages">${STAGES.map(s=>`<a class="sc ${s}" href="${href({s:st===s?"":s,w:0,n:0})}"${st===s?' aria-current="true"':""}><span class="t"><span>${SL[s]}</span>${ico("chev","s ar")}</span><span class="n">${int(cnt[s].n)}</span>
<span class="w">${cnt[s].w?`<span class="nt">${int(cnt[s].w)} new</span> this week`:"none new this week"}</span><span class="h">${esc(STAGE_HELP[s])}</span></a>`).join("")}</nav>
<div class="tdy"><section class="panel" aria-labelledby="tH"><div class="sec-h"><h2 id="tH">${st||ar||wd?int(rows.length)+" match, newest first":"All "+int(rows.length)+", newest first"}</h2><a href="#/rules">Write a rule</a></div>
<div class="fbar"><label class="sr" for="fs">Stage</label><select id="fs"><option value="">All stages</option><option value="moving"${st==="moving"?" selected":""}>Not open yet</option>${STAGES.map(s=>`<option value="${s}"${s===st?" selected":""}>${SL[s]}</option>`).join("")}</select>
<label class="sr" for="fa">Community area</label><select id="fa"><option value="">All community areas</option>${areas.map(a=>`<option${a===ar?" selected":""}>${esc(a)}</option>`).join("")}</select>
<label class="sr" for="fw">Reached the stage</label><select id="fw"><option value="0">Any time</option><option value="7"${wd===7?" selected":""}>New this week</option><option value="30"${wd===30?" selected":""}>Last 30 days</option></select>
${st||ar||wd?`<button class="clr" type="button" id="clr">Clear filters</button>`:""}</div>
${rowsTable(rows.slice(0,n),false)}${rows.length>n?`<div class="more"><a class="btn" href="${href({n:n+40})}">Show ${int(Math.min(40,rows.length-n))} more</a></div>`:""}</section>
<section class="panel stick" aria-labelledby="mH"><div class="sec-h"><h2 id="mH">Where they are</h2></div><div class="rmap">${mapHtml(all.filter(b=>stageOk(b,st)),ar)}</div></section></div>
<section class="next"><p>Sell to one trade? Type it once and the radar keeps your list.</p><a class="btn pri" href="#/rules">Write a rule</a></section>`;
$("#fs").onchange=e=>go(href({s:e.target.value,n:0}));$("#fa").onchange=e=>go(href({ar:e.target.value,n:0}));$("#fw").onchange=e=>go(href({w:e.target.value,n:0}));
if($("#clr"))$("#clr").onclick=()=>go("#/");
wireMap(href);}
function rowsTable(rows,dist){if(!rows.length)return `<p class="empty">No businesses match. Clear a filter or a chip to see more.</p>`;
return `<table class="rt"><thead><tr><th scope="col">Business</th><th scope="col">Community area</th>${dist?'<th scope="col">Miles</th>':""}<th scope="col">Stage</th><th scope="col">Reached the stage</th></tr></thead><tbody>${rows.map(b=>{const e=stageEv(b);
return `<tr><td class="c-b"><a class="bn${b.n?"":" np"}" href="#/b/${esc(b.id)}">${esc(title(b))}</a><span class="sub">${esc(V.kindLabel[b.k])}</span></td><td class="c-a">${esc(b.ar||"Area not on record")}</td>${dist?`<td class="c-m mi">${b._mi==null?"":b._mi.toFixed(1)+" mi"}</td>`:""}<td class="c-s">${sp(b.s)}</td><td class="c-d dt">${esc(dayShort(b.sd))}<small>${esc(e)}</small></td></tr>`;}).join("")}</tbody></table>`;}
function stageEv(b){if(b.s==="open")return b.ob==="rule"?"30 days after license":"Routine inspection";return {permitted:"Building permit",inspected:"Food license inspection",licensed:"New license"}[b.s];}
function mapHtml(rows,sel){const M=D.map;const by={};for(const b of rows)if(b.ar)by[b.ar]=(by[b.ar]||0)+1;const mx=Math.max(1,...Object.values(by));
const cls=()=>"";
const top=Object.entries(by).sort((a,b)=>b[1]-a[1]).slice(0,6);
return `<label class="mfind">Community area<select id="mf"><option value="">Whole city</option>${M.areas.map(a=>a.name).sort().map(n=>`<option${n===sel?" selected":""}>${esc(n)}</option>`).join("")}</select></label>
<div class="gm-stage"><svg viewBox="0 0 ${M.w} ${M.h}" role="img" aria-labelledby="mT"><title id="mT">Map of Chicago community areas with a dot for each business, colored by stage</title>
<g class="gm-a">${M.areas.map(a=>`<path data-a="${esc(a.name)}" class="${cls(by[a.name])}${a.name===sel?" sel":""}" d="${a.d}"><title>${esc(a.name)}: ${int(by[a.name]||0)}</title></path>`).join("")}</g>
<g class="dots">${rows.filter(b=>b.x!=null).map(b=>`<circle class="${b.s}" cx="${b.x}" cy="${b.y}" r="2.6"/>`).join("")}</g></svg></div>
<div class="mleg" aria-hidden="true">${STAGES.map(s=>`<span><i class="lg-${s}"></i>${SL[s]}</span>`).join("")}</div>
<ul class="mtop" aria-label="Community areas with the most businesses">${top.map(([n,c])=>`<li><button type="button" data-a="${esc(n)}"><span>${esc(n)}</span><span class="bar2" aria-hidden="true"><i style="width:${Math.round(100*c/mx)}%"></i></span><b>${int(c)}</b></button></li>`).join("")}</ul>`;}
function wireMap(href){const pick=a=>go(href({ar:a,n:0}));const f=$("#mf");if(f)f.onchange=e=>pick(e.target.value);
document.querySelectorAll(".rmap .gm-a path").forEach(p=>p.addEventListener("click",()=>pick(p.dataset.a===parse().q.get("ar")?"":p.dataset.a)));
document.querySelectorAll(".mtop button").forEach(b=>b.onclick=()=>pick(b.dataset.a));
document.querySelectorAll(".mleg i[class^=lg-]").forEach(i=>{const s=i.className.replace("lg-","");i.style.background=s==="inspected"?"#B88A1E":s==="open"?"#6B6E7E":`var(--s-${s})`;});}

/* ---------- One business ---------- */
function viewBiz(b){document.title=title(b)+" | Chicago Restaurant Radar";
const first=t=>b.ev.find(e=>e.t===t);const steps=[["permitted",first("permit"),"No permit found at this address"],["inspected",first("linsp"),b.li.length&&first("license")?"None in the 150 days before the license":"No license inspection on record"],["licensed",first("license"),"No license issued yet"],["open",b.s==="open"?{d:b.sd}:null,"Not on the City's records yet"]];
const idx=STAGES.indexOf(b.s);
const evAll=b.ev.slice().reverse();const evHtml=evAll.map((e,i)=>{let det="";
if(e.t==="permit")det=`<p>${esc(e.type||"")}${e.scope?": "+esc(e.scope):""}</p>`;
else if(e.t==="license")det=`<p>${esc(e.type||b.lt)}${b.ac?". "+esc(b.ac):""}</p>`;
else det=`<p>${esc(e.type||"")}${b.li.length>1&&e.lic?" under license "+esc(e.lic):""}. City result: <span class="res">${esc(e.result||"not given")}</span></p>`;
return `<li class="${e.t}"${i>=5?" hidden":""}><span class="dot" aria-hidden="true"></span><div class="hd"><b>${esc(EV[e.t])}</b><span class="d">${esc(day(e.d))}</span></div>${det}<a class="src" href="${esc(e.link)}" target="_blank" rel="noopener">${ico("ext","s")}The City's record<span class="sr"> for this ${esc(EV[e.t].toLowerCase())} (opens in a new tab)</span></a></li>`;}).join("");
const facts=[["Type",V.kindLabel[b.k]],["License",b.lt?(b.lt+(b.ot.length?" (also "+b.ot.join(", ")+")":"")):""],["License number",b.li.join(", ")],["City history",{first:"First license on the City's record for this business",site:"A new site for a business licensed elsewhere in Chicago",added:"A new license at a site where it already held one",relicensed:"Held this license type at this site before"}[b.hi]||""],["ZIP",b.z]].filter(x=>x[1]);
$("#app").innerHTML=`<a class="back" href="#/" id="back">${ico("back")}Back</a>
<div class="bh"><div><p class="eyebrow">${esc(V.kindLabel[b.k])}${b.ar?" · "+esc(b.ar):""}</p><h1>${esc(title(b))}</h1><p class="ad">${esc(b.a)}</p></div>${sp(b.s,1)}</div>
<ol class="steps4 panel" aria-label="Stages">${steps.map(([s,e,none],i)=>`<li class="${s}${e?" done":" none"}${i===idx?" now":""}"${i===idx?' aria-current="step"':""}><span class="sr">${e?"On record: ":i<idx?"No record, later stage reached: ":"Not reached: "}</span><b>${SL[s]}</b>${e?esc(day(e.d))+(s==="open"&&b.ob==="rule"?" (our 30-day rule)":s==="open"?" (routine inspection passed)":""):esc(none)}</li>`).join("")}</ol>
<div class="bg2"><section class="panel" id="recP" aria-labelledby="rH"><div class="sec-h"><h2 id="rH">The City's records<span class="cnt">${b.ev.length}</span></h2><a href="#ltr" id="toL" class="jl">First letter</a></div><ol class="tl2" id="evs">${evHtml}</ol>
${b.ev.length>5?`<div class="more" style="padding-top:0"><button class="btn sm" type="button" id="allEv">Show all ${b.ev.length} records</button></div>`:""}
${b.sh?`<p class="note2">Two or more food businesses share this address, so only a permit whose own text names food work is linked here.</p>`:""}
<dl class="facts2">${facts.map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join("")}</dl></section>
<section class="panel" aria-labelledby="lH"><div class="sec-h"><h2 id="lH">First letter</h2></div><div class="ltr" id="ltr"></div></section></div>
${nextBiz(b)}`;
$("#back").onclick=e=>{e.preventDefault();history.length>1?history.back():go("#/");};
if($("#allEv"))$("#allEv").onclick=()=>{document.querySelectorAll("#evs li[hidden]").forEach(li=>li.hidden=false);$("#allEv").parentNode.remove();document.querySelectorAll("#evs li")[5].querySelector("a").focus();};
$("#toL").onclick=e=>{e.preventDefault();const t=$("#lH");t.scrollIntoView({behavior:"smooth",block:"start"});t.setAttribute("tabindex","-1");t.focus({preventScroll:true});};
drawLetter(b);stickIfShort($("#recP"));}
function nextBiz(b){const L=D.biz.filter(x=>x.s!=="open").sort((x,y)=>y.sd.localeCompare(x.sd)||y.id.localeCompare(x.id));const i=L.findIndex(x=>x.id===b.id);const n=L[i+1]||L[0];
return n&&n.id!==b.id?`<section class="next"><p>Next on the radar: <b>${esc(title(n))}</b>, ${esc(SL[n.s].toLowerCase())} ${esc(dayShort(n.sd))}</p><a class="btn pri" href="#/b/${esc(n.id)}">Open the next business</a></section>`:"";}
function stickIfShort(el){if(el&&window.innerWidth>1020&&el.offsetHeight<window.innerHeight-100)el.classList.add("stick");}
function drawLetter(b){const t=trade(),m=me();const L=letterFor(b,t,m,LT);const box=$("#ltr");
const show=s=>esc(s).replace(/\{\{(\w+)\}\}/g,(_,k)=>`<span class="fl">${esc(ME_LABEL[k])}</span>`);
const filled={};for(const k in m)filled[k]=m[k]||`{{${k}}}`;const Ls=letterFor(b,t,filled,LT);
const missing=Object.keys(m).filter(k=>!m[k]);
const nm=D.biz.filter(x=>x.s!=="open").length;
box.innerHTML=`<div class="tsw" role="group" aria-label="Your trade">${LT.trades.map(x=>`<button type="button" data-t="${x.key}" aria-pressed="${x.key===t}">${esc(x.label)}</button>`).join("")}</div>
<details class="me"${missing.length?" open":""}><summary>Your details${missing.length?` (${missing.length} to fill)`:" (saved on this device)"}</summary><div class="mef">${Object.keys(ME_LABEL).map(k=>`<label>${esc(ME_LABEL[k])}<input data-k="${k}" value="${esc(m[k])}" autocomplete="${{me:"name",company:"organization",phone:"tel",companyAddress:"street-address"}[k]}"></label>`).join("")}</div></details>
<p class="to"><b>Send to:</b> ${esc(b.n||"The food business")}, ${esc(b.a)}, Chicago, IL${b.z?" "+esc(b.z):""}</p>
<article class="paper" aria-label="Letter for ${esc(title(b))}"><p class="sj"><b>Subject:</b> ${esc(L.subject)}</p><p>${show(Ls.body)}</p><p class="sg">${show(Ls.sign)}</p><p class="st">${show(Ls.stop)}</p></article>
<div class="lacts"><button class="btn pri" type="button" id="cp"${missing.length?" aria-disabled=\"true\"":""} aria-describedby="cpn">${ico("copy","s")}Copy letter</button><a class="btn" href="#/trade?t=${t}">This letter for all ${int(nm)}</a></div>
<p class="cpn" id="cpn">${missing.length?`Fill your ${missing.length} detail${missing.length===1?"":"s"} above first, so the letter is complete.`:"Copies the subject, letter, sign-off and stop line."}</p>
<ul class="lrules">${LT.rules.map(r=>`<li>${esc(r)}</li>`).join("")}</ul>`;
box.querySelectorAll(".tsw button").forEach(x=>x.onclick=()=>{setTrade(x.dataset.t);drawLetter(b);box.querySelector(`.tsw button[data-t="${x.dataset.t}"]`).focus();say(LT.trades.find(y=>y.key===x.dataset.t).label+" letter");});
box.querySelectorAll(".mef input").forEach(i=>i.onchange=()=>{const s=store.get("me",{});s[i.dataset.k]=i.value.trim();store.set("me",s);const k=i.dataset.k;drawLetter(b);const d=box.querySelector("details.me");d.open=true;const n=box.querySelector(`.mef input[data-k="${k}"]`);const all=[...box.querySelectorAll(".mef input")];const nx=all[all.indexOf(n)+1];if(nx&&!nx.value)nx.focus();});
$("#cp").onclick=async()=>{const now=letterFor(b,trade(),me(),LT);if(Object.values(me()).some(v=>!v)){const d=box.querySelector("details.me");d.open=true;const f=[...box.querySelectorAll(".mef input")].find(x=>!x.value);(f||box.querySelector(".mef input")).focus();toast("Fill your details first, so the letter is complete");return;}
const ok=await copyText("Subject: "+now.subject+"\n\n"+now.body+"\n\n"+now.sign+"\n"+now.stop);toast(ok?"Letter copied":"Copy did not work. Select the text and copy it.");};}

/* ---------- Rules ---------- */
const EXAMPLES=["pest control, within 3 miles of 60631, licensed or inspected, newest first","hood cleaning restaurants in Logan Square not open yet","grease trap within 2 miles of 60614 inspected this week","POS bakeries and coffee shops licensed last 30 days"];
function viewRules(q){const text=q.get("q")||"";document.title="Rules | Chicago Restaurant Radar";
$("#app").innerHTML=`<div class="ph"><div><p class="eyebrow">Rules</p><h1>Say who you want to reach</h1><p>Type it in plain English. A fixed word list reads it right here in your browser: no AI, no cost per search. Each part it reads becomes a chip you can remove. Words it can't read are shown, never guessed.</p></div></div>
<section class="panel rbox"><form id="rf" role="search"><label class="big" for="rq">Your rule</label><div class="rin"><input id="rq" type="text" value="${esc(text)}" autocomplete="off" spellcheck="false" placeholder="pest control within 3 miles of 60631, licensed or inspected, newest first" aria-describedby="rhelp"><button class="btn pri" type="submit">Read my rule</button></div>
<p class="rhelp" id="rhelp">It reads a trade, a stage (permitted, inspected, licensed, open, not open yet), a type of food business, a ZIP or a community area (with "within 2 miles of"), a time (this week, last 30 days) and an order (newest, oldest, closest first). Miles are as the crow flies.</p></form>
<p class="rhelp" id="exH" style="margin-top:14px">Try one:</p><div class="exs" role="group" aria-labelledby="exH">${EXAMPLES.map(e=>`<button type="button" data-e="${esc(e)}">${esc(e)}</button>`).join("")}</div>
<div class="read" id="read"></div></section>
<section class="panel rres" aria-labelledby="resH" id="res"></section>
<section class="panel rres" aria-labelledby="svH" id="sv"></section>
<section class="next"><p>Found your list? Every business has a first letter for your trade.</p><a class="btn pri" href="#/trade">Open the letters</a></section>`;
const run=(t,push)=>{if(push)history.replaceState(null,"","#/rules"+(t?"?q="+encodeURIComponent(t):""));drawRule(t);};
$("#rf").onsubmit=e=>{e.preventDefault();run($("#rq").value,true);say(drawRule.last);};
let tm;$("#rq").oninput=()=>{clearTimeout(tm);tm=setTimeout(()=>run($("#rq").value,true),250);};
document.querySelectorAll(".exs button").forEach(b=>b.onclick=()=>{$("#rq").value=b.dataset.e;run(b.dataset.e,true);say(drawRule.last);});
drawRule(text);drawSaved();}
function drawRule(text){const P=parseRule(text,V);const R=applyRule(D.biz,P.f,D.asOf);if(P.f.trade)setTrade(P.f.trade);
const CAT={trade:"Trade",stage:"Stage",kind:"Type",place:"Place",time:"Time",order:"Order"};
const read=$("#read");
read.innerHTML=text.trim()?`<h3 id="rdH">Read</h3>${P.chips.length?`<ul class="chips" aria-labelledby="rdH">${P.chips.map((c,i)=>`<li class="rc ${c.cat}"><span class="k">${CAT[c.cat]}</span>${esc(c.label)}<button type="button" data-i="${i}" aria-label="Remove ${esc(CAT[c.cat])}: ${esc(c.label)}">${ico("x","s")}</button></li>`).join("")}</ul>`:`<p class="rhelp">Nothing read yet.</p>`}
${P.unread.length?`<h3 id="noH">Not read</h3><ul class="chips" aria-labelledby="noH">${P.unread.map(u=>`<li class="rc no">${esc(u.w)}</li>`).join("")}</ul><p class="nohint">${esc(hintFor(P.unread))}</p>`:""}`:"";
read.querySelectorAll(".rc button").forEach(b=>b.onclick=()=>{const c=P.chips[+b.dataset.i];const spans=[c.span].concat(c.more||[]).sort((a,b)=>b[0]-a[0]);let t=$("#rq").value;
for(const [s,e] of spans)t=t.slice(0,s)+t.slice(e);t=t.replace(/\s*,\s*,/g,",").replace(/\s{2,}/g," ").replace(/^[\s,]+|[\s,]+$/g,"");$("#rq").value=t;
history.replaceState(null,"","#/rules"+(t?"?q="+encodeURIComponent(t):""));drawRule(t);say("Removed "+c.label+". "+drawRule.last);const f=$("#read .rc button");(f||$("#rq")).focus();});
const n=R.rows.length,dist=!!(P.f.place&&P.f.place.type==="radius");
drawRule.last=`${int(n)} business${n===1?"":"es"} match`;
const t=trade();
$("#res").innerHTML=`<div class="sec-h wrap"><h2 id="resH">${int(n)} ${n===1?"business matches":"businesses match"}</h2><a href="#/trade?t=${t}&q=${encodeURIComponent(text)}">Letters for these</a></div>
${R.notes.length?`<p class="notes">${R.notes.map(esc).join(". ")}.</p>`:""}${text.trim()?`<div class="fbar"><button class="btn sm" type="button" id="save">Save this rule</button></div>`:""}${rowsTable(R.rows.slice(0,60),dist)}${n>60?`<p class="notes">Showing the first 60. Add a place or a stage to narrow it.</p>`:""}`;
if($("#save"))$("#save").onclick=()=>{const s=store.get("rules",[]);if(!s.includes(text.trim())){s.unshift(text.trim());store.set("rules",s.slice(0,12));}drawSaved();toast("Rule saved on this device");};}
function hintFor(u){if(u.some(x=>x.hint==="near"))return "\"near\" has no distance, so it is not used. Try \"within 2 miles of 60631\" or \"in Logan Square\".";
const z=u.find(x=>x.note);if(z)return z.note+".";if(u.some(x=>x.hint==="place"))return "A distance needs a ZIP or a community area after it, like \"within 3 miles of 60622\", up to 30 miles.";
return "These words are not on the word list, so the rule ignores them. Try a trade, a stage, a type of food business, a ZIP or a community area, a time or an order.";}
function drawSaved(){const s=store.get("rules",[]);const el=$("#sv");if(!s.length){el.hidden=true;return;}el.hidden=false;
el.innerHTML=`<div class="sec-h"><h2 id="svH">Saved rules</h2></div><ul class="saved">${s.map((r,i)=>`<li><a href="#/rules?q=${encodeURIComponent(r)}">${esc(r)}</a><button type="button" data-i="${i}" aria-label="Delete saved rule: ${esc(r)}">${ico("x")}</button></li>`).join("")}</ul>`;
el.querySelectorAll("button").forEach(b=>b.onclick=()=>{const s2=store.get("rules",[]);s2.splice(+b.dataset.i,1);store.set("rules",s2);drawSaved();toast("Rule deleted");});}

/* ---------- Trade switch ---------- */
function viewTrade(q){const t=LT.trades.some(x=>x.key===q.get("t"))?q.get("t"):trade();setTrade(t);const text=q.get("q")||"";const lim=+(q.get("n")||30);
document.title="Trades | Chicago Restaurant Radar";
const P=parseRule(text,V);if(P.f.trade)P.f.trade=t;let rows=applyRule(D.biz,P.f,D.asOf).rows;if(!text)rows=rows.filter(b=>b.s!=="open");
const m=me();const filled={};for(const k in m)filled[k]=m[k]||`{{${k}}}`;
const show=x=>esc(x).replace(/\{\{(\w+)\}\}/g,(_,k)=>`<span class="fl">${esc(ME_LABEL[k])}</span>`);
$("#app").innerHTML=`<div class="ph"><div><p class="eyebrow">Trades</p><h1>Same businesses, your trade's letter</h1><p>Pick your trade. The businesses stay the same; the first letter changes to fit what you sell.${text?` Showing your rule: <b>${esc(text)}</b>.`:" Showing every business not open yet, newest first."}</p></div></div>
<div class="tsw" role="group" aria-label="Your trade">${LT.trades.map(x=>`<button type="button" data-t="${x.key}" aria-pressed="${x.key===t}">${esc(x.label)}</button>`).join("")}</div>
<section class="panel" aria-labelledby="trH"><div class="sec-h"><h2 id="trH">${esc(LT.trades.find(x=>x.key===t).label)}<span class="cnt">${int(rows.length)}</span></h2>${text?`<a href="#/rules?q=${encodeURIComponent(text)}">Edit the rule</a>`:`<a href="#/rules">Write a rule</a>`}</div>
<ul class="tl3">${rows.slice(0,lim).map(b=>{const L=letterFor(b,t,filled,LT);return `<li><div class="top"><a href="#/b/${esc(b.id)}">${esc(title(b))}</a><span class="sub">${esc(b.ar||"")}</span>${sp(b.s)}</div>
<p class="lp"><b>${esc(L.subject)}</b><br>${show(L.body)}</p><div class="la"><button class="btn sm" type="button" data-cp="${esc(b.id)}">${ico("copy","s")}Copy letter</button><a class="btn sm" href="#/b/${esc(b.id)}">Open the business</a></div></li>`;}).join("")||`<li class="empty">No businesses match.</li>`}</ul>
${rows.length>lim?`<div class="more"><button class="btn" type="button" id="tmore">Show ${int(Math.min(30,rows.length-lim))} more</button></div>`:""}</section>
<section class="next"><p>Want fewer, closer businesses? Narrow the list with a rule.</p><a class="btn pri" href="#/rules">Write a rule</a></section>`;
if($("#tmore"))$("#tmore").onclick=()=>{const p=new URLSearchParams();p.set("t",t);if(text)p.set("q",text);p.set("n",lim+30);history.replaceState(null,"","#/trade?"+p.toString());const y=window.scrollY;viewTrade(p);window.scrollTo(0,y);const li=document.querySelectorAll(".tl3 li")[lim];if(li)li.querySelector("a").focus({preventScroll:true});};
document.querySelectorAll("[data-cp]").forEach(x=>x.onclick=async()=>{const mm=me();if(Object.values(mm).some(v=>!v)){toast("Add your details on any business page first, so the letter is complete");return;}
const L=letterFor(BY[x.dataset.cp],t,mm,LT);const ok=await copyText("Subject: "+L.subject+"\n\n"+L.body+"\n\n"+L.sign+"\n"+L.stop);toast(ok?"Letter copied":"Copy did not work. Open the business to select the text.");});
document.querySelectorAll(".tsw button").forEach(x=>x.onclick=()=>{const p=new URLSearchParams();p.set("t",x.dataset.t);if(text)p.set("q",text);history.replaceState(null,"","#/trade?"+p.toString());viewTrade(p);
document.querySelector(`.tsw button[data-t="${x.dataset.t}"]`).focus();say(LT.trades.find(y=>y.key===x.dataset.t).label+" letters");});}

/* ---------- Terms ---------- */
function viewTerms(){document.title="Terms of Use | Chicago Restaurant Radar";
$("#app").innerHTML=`<a class="back" href="#/">${ico("back")}Back</a><div class="ph"><div><h1>Terms of Use</h1></div></div>
<div class="terms"><section class="panel" aria-labelledby="th1"><div class="sec-h"><h2 id="th1">City of Chicago data</h2></div><div class="tx"><p>${esc(CITY)}</p><p><a href="${esc(D.source.terms)}" target="_blank" rel="noopener">City of Chicago Data Terms of Use<span class="sr"> (opens in a new tab)</span></a></p>
<p>Sources: ${Object.keys(D.source.pages).map(k=>`<a href="${esc(D.source.pages[k])}" target="_blank" rel="noopener">${esc(D.source.names[k])}<span class="sr"> (opens in a new tab)</span></a>`).join(", ")}.</p><p>${esc(D.source.modified)}</p></div></section>
<section class="panel" aria-labelledby="th2" style="margin-top:16px"><div class="sec-h"><h2 id="th2">How stages are set</h2></div><div class="tx">${STAGES.map(s=>`<p><b>${SL[s]}.</b> ${esc(STAGE_HELP[s])}.</p>`).join("")}<p>Records are joined on the street address (house number, direction, street and suffix, without the unit) and on the license number the inspection carries. A build-out with no license yet shows only permits whose own text names food work. A business the City already inspected at the same address under the same name and an earlier license is a relicense, not an opening, and is left out.</p></div></section></div>`;}

function start(d){prep(d);$("#gateView").hidden=true;$("#app").hidden=false;$("#appLegal").hidden=false;$("#tabs").hidden=false;$("#bnav").hidden=false;document.body.classList.add("in");
window.addEventListener("hashchange",route);route();}
$("#skip").onclick=e=>{e.preventDefault();const t=$("#app h1")||$("#app");t.setAttribute("tabindex","-1");t.focus();};
if(PREVIEW){start(PREVIEW);}
else{$("#gateView").hidden=false;$("#gate").onsubmit=async e=>{e.preventDefault();const pw=$("#pw"),err=$("#err"),btn=$("#go");
if(!pw.value.trim()){err.textContent="Type the members' password.";pw.focus();return;}btn.disabled=true;btn.textContent="Opening...";
try{const d=await openBox(pw.value.trim());pw.value="";start(d);}catch(x){btn.disabled=false;btn.textContent="Open the radar";err.textContent="That password did not open the radar.";pw.select();}};}
</script></body></html>
"""


# ---------------------------------------------------------------- planted data and checks
def _planted():
    """A small joined list with the shapes tools/radar_chicago.py writes (invented businesses, real City field names)."""
    rec = lambda **k: dict({"zip": "60622", "area": "West Town", "lat": 41.9, "lon": -87.67, "licenseType": "", "otherTypes": [], "activity": "",
                            "history": "", "lics": [], "shared": False, "openBy": ""}, **k)
    ev = lambda t, d, **k: dict({"t": t, "d": d, "link": RC.RECORD["permit" if t == "permit" else "license" if t == "license" else "inspection"] + "1"}, **k)
    biz = [rec(id="L101", name="Luna Tacos", address="1000 W Chicago Ave 1st", kind="restaurant", stage="open", stageDate="2026-10-15", openBy="routine",
               licenseType="Retail Food Establishment", activity="Preparation of Food and Dining on Premises With Seating", history="first", lics=["101"],
               events=[ev("permit", "2026-05-01", type="Renovation/Alteration", scope="Interior build out for new restaurant", food=True),
                       ev("linsp", "2026-09-08", type="License", result="Pass"), ev("license", "2026-09-10", type="Retail Food Establishment"),
                       ev("routine", "2026-10-15", type="Canvass", result="Pass")]),
           rec(id="I201", name="New Noodle Bar", address="6000 N Sheridan Rd", zip="60660", area="Edgewater", lat=41.99, lon=-87.655, kind="bar", stage="inspected",
               stageDate="2026-10-29", lics=["201"], events=[ev("permit", "2026-09-01", type="Renovation/Alteration", scope="Alterations for restaurant", food=True),
                                                             ev("linsp", "2026-10-29", type="License", result="Pass")]),
           rec(id="P9101", name="", address="7000 S Ashland Ave", zip="", area="West Englewood", lat=41.765, lon=-87.663, kind="bakery", stage="permitted",
               stageDate="2026-10-01", events=[ev("permit", "2026-10-01", type="Renovation/Alteration", scope="Interior alteration for new bakery and cafe", food=True)]),
           rec(id="L102", name="Sol Cafe", address="2000 W Division St", zip="60622", area="West Town", lat=41.903, lon=-87.677, kind="coffee", stage="licensed",
               stageDate="2026-10-28", licenseType="Retail Food Establishment", lics=["102"], events=[ev("license", "2026-10-28", type="Retail Food Establishment")])]
    for b in biz:
        b["first"], b["last"] = b["events"][0]["d"], b["events"][-1]["d"]
    return {"asOf": "2026-11-02", "window": {"from": "2026-05-06", "to": "2026-11-02", "days": 180}, "zips": {"60622": [41.9, -87.68, 900], "60631": [41.995, -87.81, 400], "60660": [41.99, -87.66, 300]},
            "match": {"byStage": {}, "licensedFood": 2}, "source": {"names": {"licenses": "Business Licenses"}, "pages": RC.DATASET_PAGES, "terms": RC.TERMS,
                                                                    "modified": "Joined by ProofNotFluff.", "record": RC.RECORD}, "businesses": biz}


RULE_CASES = [  # (typed rule, chips as cat:label, unread words, matching ids in order)
    ("pest control, within 3 miles of 60622, licensed or inspected, newest first",
     ["trade:Pest control", "place:Within 3 mi of ZIP 60622", "stage:Licensed", "stage:Inspected", "order:Newest first"], [], ["L102"]),
    ("hood cleaning restaurants in West Town not open yet", ["trade:Hood and exhaust cleaning", "kind:Restaurant", "place:In West Town", "stage:Not open yet"], [], []),
    ("bakeries near Pilsen", ["kind:Bakery or dessert", "place:In Lower West Side (Pilsen)"], ["near"], []),
    ("hood exhaust in the loop", ["trade:Hood and exhaust cleaning", "place:In Loop"], [], []),
    ("restaurants in wicker park", ["kind:Restaurant", "place:In West Town (wicker park)"], [], ["L101"]),
    ("signs permitted within 30 miles of 60622 oldest first", ["trade:Signs", "stage:Permitted", "place:Within 30 mi of ZIP 60622", "order:Oldest first"], [], ["P9101"]),
    ("hottest kitchen leads 60699", [], ["hottest", "kitchen", "60699"], ["I201", "L102", "L101", "P9101"]),
    ("open last 30 days", ["stage:Open", "time:Last 30 days"], [], ["L101"]),
    ("within 2 miles of nowhere", [], ["within", "2", "miles", "of", "nowhere"], ["I201", "L102", "L101", "P9101"]),
    ("POS cafés in 60622 closest first", ["trade:POS and payments", "kind:Coffee or drinks", "place:In ZIP 60622", "order:Closest first"], [], ["L102"]),
    ("insurance bars and taverns licensed or open this week", ["trade:Insurance", "kind:Bar or tavern", "stage:Licensed", "stage:Open", "time:This week"], [], []),
]


def selftest():
    import tempfile
    full = _planted()
    html = build_html(full, "correct horse battery")
    clear = re.sub(r"const BOX=\{.*?\};", "", html)
    assert "Luna Tacos" not in clear and "Sheridan" not in clear, "business data stays inside the ciphertext"
    assert 'name="robots" content="noindex' in html and "const PREVIEW=null" in html
    box = json.loads(re.search(r"const BOX=(\{.*?\});", html).group(1))
    assert box["rounds"] == 250_000 and box["kdf"] == "PBKDF2-SHA256"
    d = json.loads(decrypt("correct horse battery", box))
    assert [b["id"] for b in d["biz"]] == ["L101", "I201", "P9101", "L102"] and d["biz"][0]["st"] == "W Chicago Ave"
    assert all(b["x"] is not None for b in d["biz"]), "every planted business lands on the map"
    try:
        decrypt("wrong password", box)
        raise AssertionError("wrong password decrypted")
    except AssertionError:
        raise
    except Exception:
        pass
    prev = build_html(full, None)
    assert "const BOX=null" in prev and "Private preview" in prev and 'class=" preview"' in prev
    text_only = re.sub(r"<[^>]+>", "", html)
    assert CITY_DISCLAIMER in LEGAL and legal_html().replace("__ASOF__", "Nov 2, 2026") in html and html.count('<a href="#/terms">Terms of Use</a>') == 1 and CITY_DISCLAIMER in text_only
    for w in ("—", "–"):
        assert w not in PAGE + LEGAL + json.dumps(LETTER_RULES) + json.dumps(STAGE_HELP), "dash"
    import voice_lint
    tells = voice_lint.tells(re.sub(r"<[^>]+>|\$\{[^}]*\}", " ", PAGE + LEGAL))
    assert not tells, tells
    node = shutil.which("node")
    if not node:
        print("node not found: rule reader and letters not checked here")
        return
    V = vocab(full["zips"], area_centers())
    pay = payload(full)
    script = (GRAMMAR_JS + LETTER_JS + "\nconst V=" + json.dumps(V) + ";const ROWS=" + json.dumps(pay["biz"]) + ";const LT=" + json.dumps(letters_json())
              + ";const CASES=" + json.dumps([c[0] for c in RULE_CASES]) + ";const ME=" + json.dumps(RL.FIXTURE_ME) + ";const FX=" + json.dumps(
                  [{"n": b["name"], "st": RL.street_of(b["address"]), "lt": b.get("licenseType") or "", "rec": (lambda r: {"t": r["t"], "d": r["d"], "ty": r.get("type") or ""})(RL.pick_record(b["events"]))} for b in RL.FIXTURES])
              + ";\nconst out=CASES.map(t=>{const P=parseRule(t,V);const R=applyRule(ROWS,P.f,'2026-11-02');return {chips:P.chips.map(c=>c.cat+':'+c.label),unread:P.unread.map(u=>u.w),ids:R.rows.map(b=>b.id)};});"
              "\nconst lets=[];for(const b of FX)for(const t of LT.trades)lets.push(letterFor(b,t.key,ME,LT));console.log(JSON.stringify({out,lets}));")
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(script)
    got = json.loads(subprocess.run([node, fh.name], capture_output=True, text=True, check=True).stdout)
    for (t, chips, unread, ids), g in zip(RULE_CASES, got["out"]):
        assert g["chips"] == chips, (t, g["chips"])
        assert g["unread"] == unread, (t, g["unread"])
        assert g["ids"] == ids, (t, g["ids"])
    want = [dict(zip(("subject", "body", "sign", "stop"), RL.fill(b, t["key"], RL.FIXTURE_ME))) for b in RL.FIXTURES for t in RL.TRADES]
    assert got["lets"] == want, "the browser's letters match tools/radar_letters.py word for word"
    print(f"radar_app selftest ok ({len(RULE_CASES)} rules read as planted, {len(want)} letters match the copy-gated source)")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--selftest"]:
        selftest()
    elif args and args[0] == "--preview":
        print(build(args[1], args[2], None))
    else:
        pw = os.environ.get("RADAR_PASSWORD", "")
        if "--pw-file" in args:
            i = args.index("--pw-file")
            pw = open(args[i + 1]).read().strip()
            args = args[:i] + args[i + 2:]
        if len(pw) < 12:
            raise SystemExit("RADAR_PASSWORD missing or shorter than 12 characters; nothing written")
        print(build(args[0], args[1], pw))
