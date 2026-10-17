#!/usr/bin/env python3
"""The members' page for Chicago Construction Cleaning Leads (A1 pre-sale, email/A1-OUTREACH.md).

This repo is public, so the paid list is never committed in the clear. The permits workflow builds the
workbook (tools/leads_xlsx.py), then this script encrypts the week's list and workbook with AES-256-GCM
under a key derived (PBKDF2-SHA256, 250,000 rounds) from the members' password, held only as the
LEADS_PASSWORD Actions secret and in the Gumroad product's post-purchase content. The page decrypts in
the buyer's browser (WebCrypto); the repo holds only ciphertext.

Design: v2 after the design director review of Oct 17, 2026 (design/DESIGN_DIRECTOR.md): compact header,
stat tiles, cards that lead with the money and the builder, counted tabs with a Builders view, a sort
control, a styled gate and the pitch kit on the page. Status chips, money and date formats match the
free sample page and the workbook.

Usage: LEADS_PASSWORD=... python3 tools/leads_page.py chicago-full.json leads.xlsx docs/chicago-leads-members/index.html
       python3 tools/leads_page.py --selftest
"""
import base64, collections, datetime as dt, json, os, re, sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROUNDS = 250_000
FREE_PAGE = "https://proofnotfluff.com/chicago-construction-cleaning-leads/"

# The pitch kit: one source of truth, the workbook's Pitch kit tab (tools/leads_xlsx.py). [Brackets] are the parts to fill in.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from leads_xlsx import BUILDER_EMAIL, CAPABILITY_SHEET  # noqa: E402


def encrypt(password, payload: bytes):
    salt, iv = os.urandom(16), os.urandom(12)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ROUNDS).derive(password.encode())
    ct = AESGCM(key).encrypt(iv, payload, None)
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "kdf": "PBKDF2-SHA256", "rounds": ROUNDS, "salt": b(salt), "iv": b(iv), "ct": b(ct)}


def decrypt(password, box):
    d = lambda x: base64.b64decode(x)
    key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=d(box["salt"]), iterations=box["rounds"]).derive(password.encode())
    return AESGCM(key).decrypt(d(box["iv"]), d(box["ct"]), None)


def pretty_date(d):
    return f"{d.strftime('%b')} {d.day}, {d.year}"


def _esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;"))


def _ph(s):
    """Escape, then mark [placeholders] so the member sees what to fill in."""
    return re.sub(r"\[([^\]]+)\]", r'<span class="ph">[\1]</span>', _esc(s))


def pitch_html():
    sheet = "".join(f"<li><b>{_esc(k)}</b><span>{_esc(v)}</span></li>" for k, v in CAPABILITY_SHEET)
    sheet_txt = "\n".join(f"{k}: {v}" for k, v in CAPABILITY_SHEET)
    email = "".join(f"<p>{_ph(x)}</p>" for x in BUILDER_EMAIL)
    email_txt = "\n\n".join(BUILDER_EMAIL)
    return (f'<section class="lm-pitch" aria-labelledby="pk"><p class="lm-eye">Pitch kit</p><h2 id="pk">What to send a builder</h2>'
            f'<div class="lm-pk-grid"><div class="lm-pk"><div class="lm-pk-head"><h3>Your one-page capability sheet</h3>'
            f'<button type="button" class="lm-copy" data-copy="{_esc(sheet_txt)}">Copy</button></div><ul class="lm-sheet">{sheet}</ul></div>'
            f'<div class="lm-pk lm-pk-mail"><div class="lm-pk-head"><h3>An email to a builder <span>(send after you call)</span></h3>'
            f'<button type="button" class="lm-copy" data-copy="{_esc(email_txt)}">Copy</button></div>'
            f'<p class="lm-pk-eye">Copy, then fill in the blue parts</p>{email}</div></div></section>')


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Members: Chicago Construction Cleaning Leads | ProofNotFluff</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/pnf.css">
<style>
:root{--blue:#2f5f9e;--note:#4a5163;--hair:#e2ddd3}
.lm{padding-bottom:40px}
.lm-eye{font-size:13px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--note);margin:26px 0 6px}
.lm h1{font-size:36px;line-height:1.12;margin:0 0 18px}
@media(max-width:600px){.lm h1{font-size:28px}}
.num,.lm-money,.tile .val,.lm-bt td.n{font-variant-numeric:tabular-nums}
/* gate */
.lm-gate{background:#fff;border:1px solid var(--hair);border-radius:14px;padding:22px;max-width:640px;margin:8px 0 18px}
.lm-gate label{display:block;font-weight:700;font-size:15px;margin:0 0 8px}.lm-gate label span{font-weight:400;color:var(--note)}
.lm-row{display:flex;gap:10px;align-items:stretch}
.lm-pw{position:relative;flex:1 1 360px;max-width:360px}
.lm-pw input{width:100%;height:48px;font:inherit;font-size:16px;padding:0 50px 0 14px;border:1px solid #c9c3b6;border-radius:12px;background:#fff;color:var(--ink)}
.lm-pw input:focus{outline:3px solid rgba(46,107,102,.35);outline-offset:1px;border-color:var(--teal)}
.lm-eyebtn{position:absolute;right:4px;top:4px;width:40px;height:40px;border:0;background:transparent;border-radius:8px;cursor:pointer;color:var(--note);display:grid;place-items:center}
.lm-eyebtn:hover{background:#f3f1ec}.lm-eyebtn:focus-visible{outline:3px solid rgba(46,107,102,.45)}
.lm-go{height:48px;padding:0 22px;border:0;border-radius:12px;background:var(--accent);color:#fff;font:inherit;font-size:16px;font-weight:700;cursor:pointer;white-space:nowrap}
.lm-go:hover{background:var(--accent-ink)}.lm-go:focus-visible{outline:3px solid rgba(200,80,47,.4);outline-offset:2px}
.lm-err{color:#a63e21;font-weight:700;font-size:15px;margin:10px 0 0}.lm-err:empty{margin:0}
.lm-links{margin:14px 0 0;padding:0;list-style:none;font-size:14px;color:var(--note)}.lm-links li{margin:4px 0}
.lm-links a{color:var(--blue);font-weight:600}
@media(max-width:600px){.lm-row{flex-direction:column}.lm-pw{max-width:none;flex:none}.lm-go{width:100%}}
.lm-legal{border-top:1px solid var(--hair);margin:32px 0 0;padding-top:16px;max-width:640px;font-size:13px;line-height:1.55;color:var(--note)}
/* tiles and download */
.lm-tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:0 0 18px}
@media(max-width:720px){.lm-tiles{grid-template-columns:repeat(2,minmax(0,1fr))}}
.lm-tiles .tile .lab{color:var(--note)}.lm-tiles .tile.key .lab{color:#c9cfdb}
.lm-dl{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;margin:0 0 22px}
.lm-dl .lm-go{display:inline-flex;align-items:center;gap:8px;text-decoration:none}
.lm-dl small{display:block;font-size:13px;color:var(--note)}
/* tabs and tools */
.lm-tabs{display:flex;gap:8px;overflow-x:auto;scrollbar-width:none;padding:2px 2px 6px;margin:0 -16px 10px;padding-left:16px;padding-right:16px;
  -webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 28px),transparent)}
.lm-tabs::-webkit-scrollbar{display:none}
@media(min-width:721px){.lm-tabs{margin:0 0 10px;padding-left:2px;padding-right:2px;-webkit-mask-image:none;mask-image:none}}
.lm-tabs button{flex:0 0 auto;font:inherit;font-size:15px;font-weight:700;height:40px;padding:0 16px;border-radius:999px;border:1px solid var(--hair);background:#fff;color:var(--ink);cursor:pointer;white-space:nowrap}
.lm-tabs button .c{font-weight:600;color:var(--note);margin-left:6px}
.lm-tabs button[aria-selected=true]{background:var(--ink);color:#fff;border-color:var(--ink)}.lm-tabs button[aria-selected=true] .c{color:#c9cfdb}
.lm-tabs button:focus-visible,.lm-sel select:focus-visible{outline:3px solid rgba(46,107,102,.45);outline-offset:1px}
.lm-tools{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;margin:4px 0 16px}
.lm-sel label{display:block;font-size:13px;font-weight:700;color:var(--note);margin:0 0 4px}
.lm-sel select{appearance:none;-webkit-appearance:none;height:40px;font:inherit;font-size:15px;font-weight:700;color:var(--ink);background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' fill='none' stroke='%231d2433' stroke-width='2'/%3E%3C/svg%3E") no-repeat right 14px center;
  border:1px solid var(--hair);border-radius:999px;padding:0 38px 0 14px;max-width:100%;cursor:pointer}
.lm-shown{margin:0 0 0 auto;font-size:14px;color:var(--note);height:40px;display:flex;align-items:center}
@media(max-width:600px){.lm-tools{display:grid;grid-template-columns:minmax(0,1fr);gap:10px}.lm-sel select{width:100%}.lm-shown{grid-column:1/-1;margin:0;height:auto}}
.lm-tiles .tile .val{font-size:clamp(26px,13cqi,36px)}
/* cards */
.lm-list{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}
@media(max-width:820px){.lm-list{grid-template-columns:minmax(0,1fr)}}
.lm-card{background:#fff;border:1px solid var(--hair);border-radius:14px;padding:20px;display:flex;flex-direction:column;gap:8px;min-width:0}
.lm-chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-block;font-size:12.5px;font-weight:700;line-height:1;padding:6px 10px;border-radius:999px}
.st-near{color:#2e6b66;background:#e3efed}.st-insp{color:#2f5f9e;background:#e6edf6}.st-iss{color:#3a4152;background:#ece6da}.chip.new{color:#fff;background:#2e6b66}
.lm-money{font-family:Poppins,system-ui,sans-serif;font-weight:700;font-size:22px;line-height:1.2;color:var(--ink)}
.lm-money span{font-family:inherit;font-weight:400;font-size:14px;color:var(--note);margin-left:8px}
.lm-card h3{font-family:inherit;font-size:16px;font-weight:700;margin:0;letter-spacing:0}
.lm-card h3 span{font-weight:400;font-size:15px;color:var(--note)}
.lm-desc{font-size:15px;color:#3a4152;margin:0;overflow-wrap:anywhere}
.lm-meta{display:grid;grid-template-columns:72px minmax(0,1fr);gap:4px 12px;margin:4px 0 0;padding-top:12px;border-top:1px solid #efebe3}
.lm-meta dt{font-size:11.5px;font-weight:700;letter-spacing:.07em;color:var(--note);padding-top:2px}
.lm-meta dd{margin:0;font-size:14px;color:var(--note);overflow-wrap:anywhere}.lm-meta dd.b{font-size:16px;font-weight:700;color:var(--ink)}
.lm-more{display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:18px 0 0;font-size:14px;color:var(--note)}
.lm-ghost{height:44px;padding:0 18px;border-radius:12px;border:1.5px solid var(--ink);background:#fff;color:var(--ink);font:inherit;font-size:15px;font-weight:700;cursor:pointer}
.lm-ghost:hover{background:#f3f1ec}
.lm-none{background:#fff;border:1px dashed var(--hair);border-radius:14px;padding:22px;color:var(--note)}
/* builders */
.lm-bt{width:100%;border-collapse:separate;border-spacing:0;background:#fff;border:1px solid var(--hair);border-radius:14px;overflow:hidden;font-size:15px}
.lm-bt th{text-align:left;font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--note);font-weight:700;padding:12px 14px;border-bottom:1px solid var(--ink);background:#faf8f4}
.lm-bt td{padding:11px 14px;border-bottom:1px solid #efebe3;vertical-align:top}.lm-bt tr:last-child td{border-bottom:0}
.lm-bt th.n,.lm-bt td.n{text-align:right;white-space:nowrap}.lm-bt td.nm{font-weight:700}.lm-bt td.z{color:#8a8f9a}
.lm-bt .bar{display:block;height:6px;border-radius:3px;background:#2e6b66;margin-top:6px;min-width:4px}
@media(max-width:720px){.lm-bt thead{display:none}.lm-bt,.lm-bt tbody,.lm-bt tr,.lm-bt td{display:block}.lm-bt tr{padding:12px 16px;border-bottom:1px solid #efebe3}
  .lm-bt td{padding:0;border:0}.lm-bt td.n,.lm-bt td.z,.lm-bt td.ar{display:none}.lm-bt td.nm{font-size:15px}.lm-bt td.sum{display:block;font-size:14px;color:var(--note);margin-top:2px}}
@media(min-width:721px){.lm-bt td.sum{display:none}}
/* pitch kit */
.lm-pitch{margin:40px 0 0}.lm-pitch h2{font-size:24px;margin:0 0 14px}
.lm-pk-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;align-items:start}@media(max-width:820px){.lm-pk-grid{grid-template-columns:minmax(0,1fr)}}
.lm-pk{background:#fff;border:1px solid var(--hair);border-radius:14px;padding:20px;min-width:0}
.lm-pk-mail{background:#fff6d6;border-color:#e3c978}
.lm-pk-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin:0 0 10px}
.lm-pk h3{font-family:inherit;font-size:16px;margin:0;letter-spacing:0}.lm-pk h3 span{font-weight:400;color:var(--note)}
.lm-copy{flex:0 0 auto;height:36px;padding:0 14px;border-radius:10px;border:1.5px solid var(--ink);background:#fff;color:var(--ink);font:inherit;font-size:14px;font-weight:700;cursor:pointer;min-width:84px}
.lm-copy.done{background:#2e6b66;border-color:#2e6b66;color:#fff}
.lm-sheet{list-style:none;margin:0;padding:0}.lm-sheet li{display:grid;grid-template-columns:118px minmax(0,1fr);gap:12px;padding:9px 0;border-top:1px solid #efebe3;font-size:15px;color:#3a4152}
.lm-sheet li b{color:var(--ink)}
@media(max-width:420px){.lm-sheet li{grid-template-columns:minmax(0,1fr);gap:2px}}
.lm-pk-mail .lm-pk-eye{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#6d5410;margin:0 0 8px}
.lm-pk-mail p{font-size:15px;color:#3a4152;margin:0 0 10px}.ph{color:#1f4e9e;font-weight:700}
.lm-foot{border-top:1px solid var(--hair);margin:40px 0 0;padding-top:16px;font-size:14px;color:var(--note)}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
</style></head><body class="lm-page">
<header class="top"><div class="wrap"><div><a class="brand" href="../">ProofNotFluff</a><div class="bars"><i></i><i></i><i></i><i></i><i></i></div></div></div></header>
<main class="wrap lm">
<p class="lm-eye">Members &middot; List of __ASOF__</p>
<h1>Chicago Construction Cleaning Leads</h1>
<form class="lm-gate" id="gate" novalidate>
<label for="pw">Members' password <span>(on your Gumroad purchase page)</span></label>
<div class="lm-row"><div class="lm-pw"><input id="pw" type="password" autocomplete="current-password" required aria-describedby="err">
<button type="button" class="lm-eyebtn" id="eye" aria-label="Show password" aria-pressed="false"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/><path id="eyeslash" d="M3 3l18 18" hidden/></svg></button></div>
<button class="lm-go" type="submit">Open this week's list</button></div>
<p class="lm-err" id="err" role="alert"></p>
<ul class="lm-links"><li>Lost the password? It is on your Gumroad purchase page, linked from your receipt email. <a href="https://gumroad.com/library">Open your Gumroad library</a></li>
<li>Not a member yet? <a href="__FREE__">Get the full list: $29 a month</a></li></ul>
</form>
<div id="app" hidden></div>
<p class="lm-legal">Public City of Chicago permit records, as of __ASOF__. This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk. No builder listed has endorsed or works with ProofNotFluff. Licensed to one business for its own prospecting; no reselling or republishing. Provided as is, without warranties of any kind, to the extent the law allows, and ProofNotFluff's total liability for any claim is limited to the amount you paid for the most recent month of your membership. Made with AI assistance. Full terms are on the Terms tab of the Excel file.</p>
<template id="pitch">__PITCH__</template>
<footer class="lm-foot">List of __ASOF__. Questions about your membership? Reply to your Gumroad receipt.</footer>
</main>
<script>
const BOX=__BOX__;
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function unlock(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const int=n=>Math.round(+n||0).toLocaleString("en-US");
function money(n){n=+n||0;if(n>=99.95e6)return "$"+int(n/1e6)+"M";if(n>=999.5e3)return "$"+(n/1e6).toFixed(1)+"M";return "$"+Math.round(n/1e3)+"K";}
function bigMoney(n){return n>=1e9?"$"+(n/1e9).toFixed(1)+" billion":money(n);}
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
function day(s){const m=/^(\\d{4})-(\\d{2})-(\\d{2})/.exec(s||"");return m?MON[+m[2]-1]+" "+(+m[3])+", "+m[1]:esc(s);}
const ST={"Partial occupancy approved":"st-near","Inspections under way":"st-insp","Permit issued":"st-iss"};
const ORDER={"Partial occupancy approved":0,"Inspections under way":1,"Permit issued":2};
const SORTS={clean:(a,b)=>(ORDER[a.stage]??3)-(ORDER[b.stage]??3)||b.cost-a.cost,big:(a,b)=>b.cost-a.cost,newest:(a,b)=>(b.issued||"").localeCompare(a.issued||"")||b.cost-a.cost};
function card(p,inNear){const kind=[esc(p.type),p.units?int(p.units)+" homes":""].filter(Boolean).join(" &middot; ");
const chips=(inNear?"":`<span class="chip ${ST[p.stage]||"st-iss"}">${esc(p.stage)}</span>`)+(p.new?'<span class="chip new">New</span>':"");
return `<article class="lm-card">${chips?`<div class="lm-chips">${chips}</div>`:""}
<div class="lm-money">${money(p.cost)}<span>${kind}</span></div>
<h3>${esc(p.address)}${p.communityArea?` <span>&middot; ${esc(p.communityArea)}</span>`:""}</h3>
<p class="lm-desc">${esc(p.scope)}</p>
<dl class="lm-meta"><dt>BUILDER</dt><dd class="b">${esc((p.gc||[]).join("; "))}</dd><dt>PERMIT</dt><dd>${esc(p.permit)}, issued ${day(p.issued)} &middot; reported&nbsp;$${int(p.cost)}</dd></dl></article>`;}
function render(d){const app=document.getElementById("app");const st={view:"near",area:"",sort:"clean",shown:100};
const tabs=[["near","Near finish",d.near],["new","New this week",d.newCount],["all","All projects",d.rows.length],["builders","Builders",d.builders.length]];
const areas=[...new Set(d.rows.map(r=>r.communityArea).filter(Boolean))].sort();
const total=d.rows.reduce((s,r)=>s+(+r.cost||0),0);
app.innerHTML=`<div class="lm-tiles">
<div class="tile key"><div class="lab">Open permits</div><div class="val">${int(d.rows.length)}</div><div class="sub">${bigMoney(total)} reported</div></div>
<div class="tile"><div class="lab">Addresses</div><div class="val">${int(d.addresses)}</div><div class="sub">big jobs carry several permits</div></div>
<div class="tile"><div class="lab">Near finish</div><div class="val">${int(d.near)}</div><div class="sub">partial occupancy approved</div></div>
<div class="tile"><div class="lab">New this week</div><div class="val">${int(d.newCount)}</div><div class="sub">issued in the last 7 days</div></div></div>
<div class="lm-dl"><button class="lm-go" type="button" id="dl"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11M7 10l5 5 5-5M5 20h14"/></svg>Download this week's Excel file</button><small>Opens in Excel or Google Sheets &middot; list of ${esc(d.asOf)}</small></div>
<div class="lm-tabs" role="tablist" aria-label="Lists">${tabs.map(([k,t,c])=>`<button type="button" role="tab" data-v="${k}" aria-selected="${k===st.view}">${t}<span class="c">${int(c)}</span></button>`).join("")}</div>
<div class="lm-tools" id="tools"><div class="lm-sel"><label for="ar">Community area</label><select id="ar"><option value="">All areas</option>${areas.map(a=>`<option value="${esc(a)}">${esc(a)}</option>`).join("")}</select></div>
<div class="lm-sel"><label for="so">Sort</label><select id="so"><option value="clean">Closest to clean first</option><option value="big">Biggest first</option><option value="newest">Newest first</option></select></div>
<p class="lm-shown" id="shown" aria-live="polite"></p></div>
<div id="list"></div>` + document.getElementById("pitch").innerHTML;
const list=document.getElementById("list"),shown=document.getElementById("shown"),tools=document.getElementById("tools");
function rowsNow(){let r=d.rows.filter(x=>st.view==="all"||(st.view==="near"?x.stage==="Partial occupancy approved":x.new));if(st.area)r=r.filter(x=>x.communityArea===st.area);return r.slice().sort(SORTS[st.sort]);}
function draw(){app.querySelectorAll(".lm-tabs button").forEach(b=>{const on=b.dataset.v===st.view;b.setAttribute("aria-selected",String(on));if(on&&b.scrollIntoView)b.scrollIntoView({block:"nearest",inline:"nearest"});});
if(st.view==="builders"){tools.hidden=true;const max=Math.max(1,...d.builders.map(b=>b.n));
list.innerHTML=`<table class="lm-bt"><caption class="sr">Builders with open permits</caption><thead><tr><th>Builder</th><th class="n">Open permits</th><th class="n">Reported cost</th><th class="n">Near finish</th><th class="n">New</th><th>Where most are</th></tr></thead><tbody>${
d.builders.map(b=>`<tr><td class="nm">${esc(b.name)}<span class="bar" style="width:${Math.max(4,Math.round(b.n/max*100))}%" aria-hidden="true"></span></td><td class="sum">${int(b.n)} open ${b.n===1?"permit":"permits"} &middot; ${money(b.cost)}${b.near?` &middot; ${b.near} near finish`:""}${b.area?` &middot; ${esc(b.area)}`:""}</td><td class="n">${int(b.n)}</td><td class="n">${money(b.cost)}</td><td class="n${b.near?"":" z"}">${b.near}</td><td class="n${b.new?"":" z"}">${b.new}</td><td class="ar">${esc(b.area)}</td></tr>`).join("")}</tbody></table>
<p class="lm-more">A permit with two builders counts for each. The workbook's Builders tab has the same table.</p>`;return;}
tools.hidden=false;const rows=rowsNow();const n=Math.min(st.shown,rows.length);
shown.textContent=rows.length===n?`${int(rows.length)} shown`:`${int(n)} of ${int(rows.length)} shown`;
list.innerHTML=rows.length?`<div class="lm-list">${rows.slice(0,n).map(p=>card(p,st.view==="near")).join("")}</div>${n<rows.length?`<div class="lm-more"><button type="button" class="lm-ghost" id="more">Show ${int(Math.min(100,rows.length-n))} more</button><span>The workbook has all ${int(rows.length)}.</span></div>`:""}`
:`<p class="lm-none">None ${st.area?"in "+esc(st.area)+" ":""}on this list this week.</p>`;
const m=document.getElementById("more");if(m)m.onclick=()=>{st.shown+=100;draw();};}
app.querySelectorAll(".lm-tabs button").forEach(b=>b.onclick=()=>{st.view=b.dataset.v;st.shown=100;draw();});
document.getElementById("ar").onchange=e=>{st.area=e.target.value;st.shown=100;draw();};
document.getElementById("so").onchange=e=>{st.sort=e.target.value;st.shown=100;draw();};
document.getElementById("dl").onclick=()=>{const blob=new Blob([b64(d.xlsx)],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=d.fileName;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),4000);};
app.querySelectorAll(".lm-copy").forEach(b=>b.onclick=async()=>{try{await navigator.clipboard.writeText(b.dataset.copy);b.textContent="Copied";b.classList.add("done");}
catch(e){b.textContent="Select and copy";}setTimeout(()=>{b.textContent="Copy";b.classList.remove("done");},2200);});
draw();app.hidden=false;}
const pw=document.getElementById("pw"),eye=document.getElementById("eye");
eye.onclick=()=>{const show=pw.type==="password";pw.type=show?"text":"password";eye.setAttribute("aria-pressed",String(show));eye.setAttribute("aria-label",show?"Hide password":"Show password");document.getElementById("eyeslash").hidden=!show;pw.focus();};
document.getElementById("gate").onsubmit=async e=>{e.preventDefault();const err=document.getElementById("err");
if(!pw.value.trim()){err.textContent="Type the password from your Gumroad purchase page.";return;}err.textContent="Opening...";
try{const d=await unlock(pw.value.trim());err.textContent="";document.getElementById("gate").hidden=true;render(d);window.scrollTo(0,0);}
catch(x){err.textContent="That password didn't open the list. Check your Gumroad purchase page, or reply to your receipt for help.";}};
</script></body></html>
"""


def builders_table(rows):
    """Every builder on the list: open permits, reported cost, near finish, new, and the community area with most of them.
    A permit with two builders counts for each (the workbook's Builders tab does the same)."""
    agg = {}
    for p in rows:
        for g in p.get("gc") or []:
            k = re.sub(r"[^a-z0-9]", "", g.lower())
            b = agg.setdefault(k, {"name": g, "n": 0, "cost": 0, "near": 0, "new": 0, "areas": collections.Counter()})
            b["n"] += 1
            b["cost"] += p.get("cost") or 0
            b["near"] += p.get("stage") == "Partial occupancy approved"
            b["new"] += bool(p.get("new"))
            if p.get("communityArea"):
                b["areas"][p["communityArea"]] += 1
    out = []
    for b in agg.values():
        top = sorted(b["areas"].items(), key=lambda kv: (-kv[1], kv[0]))
        out.append({"name": b["name"], "n": b["n"], "cost": round(b["cost"]), "near": b["near"], "new": b["new"], "area": top[0][0] if top else ""})
    return sorted(out, key=lambda b: (-b["n"], -b["cost"], b["name"]))


SLIM = ("address", "communityArea", "type", "scope", "cost", "units", "issued", "gc", "permit", "stage", "new")


def build_html(rows, fetched, xlsx_bytes, password):
    """The members' page for prepared rows (each with a stage and a new flag), the list date and the workbook bytes."""
    slim = [{k: p.get(k) for k in SLIM} for p in rows]
    as_of = pretty_date(fetched)
    payload = {"rows": slim, "addresses": len({p.get("address") for p in rows}),
               "near": sum(p.get("stage") == "Partial occupancy approved" for p in rows), "newCount": sum(bool(p.get("new")) for p in rows),
               "builders": builders_table(slim), "asOf": as_of,
               "fileName": f"chicago-construction-cleaning-leads-{fetched.isoformat()}.xlsx",
               "xlsx": base64.b64encode(xlsx_bytes).decode()}
    box = encrypt(password, json.dumps(payload, separators=(",", ":")).encode())
    return (PAGE.replace("__BOX__", json.dumps(box)).replace("__ASOF__", as_of).replace("__FREE__", FREE_PAGE)
            .replace("__PITCH__", pitch_html()))


def build(full, xlsx_path, out, password):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from leads_xlsx import prep
    rows = [prep(p) for p in full["projects"]]
    fetched = dt.datetime.fromisoformat(full["source"]["fetchedAt"]).date()
    html = build_html(rows, fetched, open(xlsx_path, "rb").read(), password)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(html)
    return {"rows": len(rows), "bytes": len(html)}


def selftest():
    box = encrypt("correct horse", b"hello")
    assert decrypt("correct horse", box) == b"hello"
    try:
        decrypt("wrong", box)
        raise AssertionError("wrong password decrypted")
    except AssertionError:
        raise
    except Exception:
        pass
    rows = [{"address": "1 N Main St", "communityArea": "Loop", "type": "Renovation", "scope": "Interior <b>alterations</b>", "cost": 1988677,
             "units": None, "issued": "2025-12-01", "gc": ["Acme Builders LLC", "Beta Electric Inc"], "permit": "101000001",
             "stage": "Partial occupancy approved", "new": False},
            {"address": "2 N Main St", "communityArea": "Loop", "type": "New construction", "scope": "Erect", "cost": 600000, "units": 40,
             "issued": "2026-10-14", "gc": ["Acme Builders LLC"], "permit": "101000002", "stage": "Permit issued", "new": True}]
    b = builders_table(rows)
    assert b[0] == {"name": "Acme Builders LLC", "n": 2, "cost": 2588677, "near": 1, "new": 1, "area": "Loop"}, b[0]
    assert len(b) == 2 and b[1]["n"] == 1
    html = build_html(rows, dt.date(2026, 10, 17), b"PK", "correct horse battery")
    assert "<b>alterations</b>" not in html, "row data must stay inside the ciphertext"
    assert "List of Oct 17, 2026" in html and "noindex" in html and "one's own risk" in html
    for page in (PAGE, html):
        assert "\u2014" not in page, "em dash"
        for w in ("honestly", "genuinely", "straightforward", "delve", "unlock ", "elevate", "seamless", "game-changer", "effortless", "supercharge"):
            assert w not in page.lower(), w
    box = json.loads(re.search(r"const BOX=(\{.*?\});", html).group(1))
    data = json.loads(decrypt("correct horse battery", box))
    assert data["near"] == 1 and data["newCount"] == 1 and data["addresses"] == 2 and data["builders"][0]["n"] == 2
    print("selftest ok")


def write_review(full, out, password):
    """The filter's review set (every open candidate with the City's raw text), encrypted like the members' list,
    so the crew can test the filter offline without the paid list sitting in a public repo in the clear."""
    box = encrypt(password, json.dumps(full.get("review", []), separators=(",", ":")).encode())
    json.dump(box, open(out, "w"))
    return len(full.get("review", []))


if __name__ == "__main__":
    if sys.argv[1:2] == ["--review"]:
        pw = os.environ.get("LEADS_PASSWORD", "")
        if len(pw) < 12:
            raise SystemExit("LEADS_PASSWORD missing; review not written")
        print("review rows", write_review(json.load(open(sys.argv[2])), sys.argv[3], pw))
    elif sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        pw = os.environ.get("LEADS_PASSWORD", "")
        if len(pw) < 12:
            raise SystemExit("LEADS_PASSWORD missing or shorter than 12 characters; nothing written")
        print(build(json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], pw))
