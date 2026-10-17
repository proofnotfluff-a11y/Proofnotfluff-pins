#!/usr/bin/env python3
"""The members' page for Chicago Construction Cleaning Leads (A1 pre-sale, email/A1-OUTREACH.md).

This repo is public, so the paid list is never committed in the clear. The permits workflow builds the
workbook (tools/leads_xlsx.py), then this script encrypts the week's list and workbook with AES-256-GCM
under a key derived (PBKDF2-SHA256, 250,000 rounds) from the members' password, held only as the
LEADS_PASSWORD Actions secret and in the Gumroad product's post-purchase content. The page decrypts in
the buyer's browser (WebCrypto); the repo holds only ciphertext.

Usage: LEADS_PASSWORD=... python3 tools/leads_page.py chicago-full.json leads.xlsx docs/chicago-leads-members/index.html
       python3 tools/leads_page.py --selftest
"""
import base64, datetime as dt, json, os, sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

ROUNDS = 250_000


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


PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex, nofollow"><title>Members: Chicago Construction Cleaning Leads | ProofNotFluff</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../assets/pnf.css">
<style>
.lm-gate{max-width:440px;margin:24px 0}.lm-gate input{width:100%;font:inherit;padding:12px 14px;border:1px solid var(--line,#ccc);border-radius:10px;margin:8px 0 12px;box-sizing:border-box}
.lm-err{color:var(--accent,#c4542f);min-height:1.4em}.lm-tabs{display:flex;gap:8px;flex-wrap:wrap;margin:18px 0 10px}
.lm-tabs button{font:inherit;padding:8px 14px;border-radius:999px;border:1px solid var(--line,#ccc);background:#fff;cursor:pointer}
.lm-tabs button[aria-pressed=true]{background:var(--ink,#1d2433);color:#fff;border-color:var(--ink,#1d2433)}
.lm-tools{display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin:6px 0 14px}.lm-tools select{font:inherit;padding:8px 10px;border-radius:10px;border:1px solid var(--line,#ccc)}
.lm-list{display:grid;gap:10px}.lm-card{background:#fff;border:1px solid var(--line,#e2ded6);border-radius:12px;padding:14px 16px}
.lm-card h3{margin:0 0 4px;font-size:1.02rem}.lm-meta{color:var(--note,#5d6472);font-size:.88rem;margin:2px 0}
.lm-tag{display:inline-block;font-size:.75rem;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--teal-tint,#e3efec);margin-right:6px}
.lm-tag.new{background:#fde8df;color:var(--accent,#c4542f)}.lm-small{font-size:.85rem;color:var(--note,#5d6472)}
</style></head><body>
<header class="top"><div class="wrap"><div><a class="brand" href="../">ProofNotFluff</a><div class="bars"><i></i><i></i><i></i><i></i><i></i></div></div></div></header>
<main class="wrap"><section class="block">
<p class="eyebrow">Members</p><h1>Chicago Construction Cleaning Leads</h1>
<p class="lede">This week's full list: every open apartment and commercial permit in Chicago with a reported cost of $500,000 or more, the builder on each, and the ones closest to a final clean. Updated every Monday.</p>
<form class="lm-gate" id="gate"><label for="pw"><b>Members' password</b> (in your Gumroad receipt)</label>
<input id="pw" type="password" autocomplete="current-password" required><button class="btn" type="submit">Open this week's list</button>
<p class="lm-err" id="err" role="alert"></p></form>
<div id="app" hidden></div>
<p class="lm-small">Public City of Chicago permit records, as of __ASOF__. This site provides applications using data that has been modified for use from its original source, www.cityofchicago.org, the official website of the City of Chicago. The City of Chicago makes no claims as to the content, accuracy, timeliness, or completeness of any of the data provided at this site. The data provided at this site is subject to change at any time. It is understood that the data provided at this site is being used at one's own risk. No builder listed has endorsed or works with ProofNotFluff. Licensed to one business for its own prospecting.</p>
</section></main>
<script>
const BOX=__BOX__;
const b64=s=>Uint8Array.from(atob(s),c=>c.charCodeAt(0));
async function open(pw){const k0=await crypto.subtle.importKey("raw",new TextEncoder().encode(pw),"PBKDF2",false,["deriveKey"]);
const key=await crypto.subtle.deriveKey({name:"PBKDF2",salt:b64(BOX.salt),iterations:BOX.rounds,hash:"SHA-256"},k0,{name:"AES-GCM",length:256},false,["decrypt"]);
const pt=await crypto.subtle.decrypt({name:"AES-GCM",iv:b64(BOX.iv)},key,b64(BOX.ct));return JSON.parse(new TextDecoder().decode(pt));}
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const usd=n=>n?"$"+Math.round(n).toLocaleString("en-US"):"";
function card(p){return `<div class="lm-card"><h3>${esc(p.address)}${p.communityArea?" <span class=lm-meta>· "+esc(p.communityArea)+"</span>":""}</h3>
<p>${p.new?'<span class="lm-tag new">New</span>':""}<span class="lm-tag">${esc(p.stage)}</span>${esc(p.type)}${p.units?" · "+p.units+" homes":""} · ${usd(p.cost)} reported</p>
<p class="lm-meta">${esc(p.scope)}</p><p class="lm-meta"><b>Builder:</b> ${esc((p.gc||[]).join("; "))} · Permit ${esc(p.permit)} · issued ${esc(p.issued)}</p></div>`;}
function render(d){const app=document.getElementById("app");let view="near",area="";
const areas=[...new Set(d.rows.map(r=>r.communityArea).filter(Boolean))].sort();
const draw=()=>{let rows=d.rows.filter(r=>view==="all"||(view==="near"?r.stage==="Partial occupancy approved":r.new));if(area)rows=rows.filter(r=>r.communityArea===area);
app.innerHTML=`<p><b>${d.rows.length.toLocaleString("en-US")}</b> open permits at <b>${d.addresses.toLocaleString("en-US")}</b> addresses · <b>${d.near}</b> near finish · <b>${d.newCount}</b> new this week</p>
<p><a class="btn" id="dl" href="#">Download the workbook (Excel, opens in Google Sheets)</a></p>
<div class="lm-tabs">${[["near","Near finish"],["new","New this week"],["all","All projects"]].map(([k,t])=>`<button type="button" data-v="${k}" aria-pressed="${k===view}">${t}</button>`).join("")}</div>
<div class="lm-tools"><label for="ar">Community area</label><select id="ar"><option value="">All areas</option>${areas.map(a=>`<option${a===area?" selected":""}>${esc(a)}</option>`).join("")}</select><span class="lm-small">${rows.length} shown</span></div>
<div class="lm-list">${rows.slice(0,400).map(card).join("")||"<p>None this week.</p>"}</div>${rows.length>400?"<p class=lm-small>Showing the 400 biggest; the workbook has all of them.</p>":""}`;
app.querySelectorAll(".lm-tabs button").forEach(b=>b.onclick=()=>{view=b.dataset.v;draw();});
document.getElementById("ar").onchange=e=>{area=e.target.value;draw();};
document.getElementById("dl").onclick=e=>{e.preventDefault();const blob=new Blob([b64(d.xlsx)],{type:"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"});
const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download=d.fileName;document.body.appendChild(a);a.click();a.remove();};};
draw();app.hidden=false;}
document.getElementById("gate").onsubmit=async e=>{e.preventDefault();const err=document.getElementById("err");err.textContent="Opening...";
try{const d=await open(document.getElementById("pw").value.trim());err.textContent="";document.getElementById("gate").hidden=true;render(d);}
catch(x){err.textContent="That password didn't open the list. Check your Gumroad receipt, or reply to it for help.";}};
</script></body></html>
"""


def build(full, xlsx_path, out, password):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from leads_xlsx import prep
    rows = [prep(p) for p in full["projects"]]
    from leads_xlsx import sort_key
    rows.sort(key=sort_key)
    fetched = dt.datetime.fromisoformat(full["source"]["fetchedAt"]).date()
    slim = [{k: p.get(k) for k in ("address", "communityArea", "type", "scope", "cost", "units", "issued", "gc", "permit", "stage", "new")} for p in rows]
    payload = {"rows": slim, "addresses": len({p.get("address") for p in rows}), "near": sum(p["stage"] == "Partial occupancy approved" for p in rows), "newCount": sum(p["new"] for p in rows),
               "fileName": f"chicago-construction-cleaning-leads-{fetched.isoformat()}.xlsx",
               "xlsx": base64.b64encode(open(xlsx_path, "rb").read()).decode()}
    box = encrypt(password, json.dumps(payload, separators=(",", ":")).encode())
    html = PAGE.replace("__BOX__", json.dumps(box)).replace("__ASOF__", f"{fetched.strftime('%b')} {fetched.day}, {fetched.year}")
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
    assert "—" not in PAGE
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    else:
        pw = os.environ.get("LEADS_PASSWORD", "")
        if len(pw) < 12:
            raise SystemExit("LEADS_PASSWORD missing or shorter than 12 characters; nothing written")
        print(build(json.load(open(sys.argv[1])), sys.argv[2], sys.argv[3], pw))
