#!/usr/bin/env python3
"""Etsy OAuth 2.0 (PKCE) helper for ProofNotFluff. Runs only in a cloud session on the Default environment,
where ETSY_KEYSTRING is set and the agent proxy adds the x-api-key credential to Etsy requests.
It never prints the keystring, the shared secret or any token.

  python3 tools/etsy_oauth.py link            new verifier + state (saved in ~/.etsy/state.json), prints the approval URL
  python3 tools/etsy_oauth.py exchange CODE STATE   swaps the code for tokens; refresh token goes to the vault file
  python3 tools/etsy_oauth.py refresh         new access token from the vault's refresh token (rotates it, saves the new one)
  python3 tools/etsy_oauth.py me              GET /users/me (read-only test); also records user_id and shop_id in the vault
  python3 tools/etsy_oauth.py token           prints nothing; exits 0 when a valid access token is available (refreshes if needed)

Vault file: $ETSY_VAULT (default /home/claude/proofnotfluff-vault/etsy.json), in the private repo proofnotfluff-vault.
Commit and push that file after exchange and after every refresh (the refresh token rotates each time).
"""
import base64, hashlib, json, os, secrets, sys, time, urllib.parse, urllib.request

REDIRECT = "https://proofnotfluff-a11y.github.io/Proofnotfluff-pins/etsy-callback.html"
SCOPES = "listings_r listings_w shops_r transactions_r"
TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
API = "https://openapi.etsy.com/v3/application"
VAULT = os.environ.get("ETSY_VAULT", "/home/claude/proofnotfluff-vault/etsy.json")
LOCAL = os.path.expanduser("~/.etsy"); os.makedirs(LOCAL, exist_ok=True)
STATE = os.path.join(LOCAL, "state.json"); ACCESS = os.path.join(LOCAL, "access.json")

def die(msg): print(msg, file=sys.stderr); sys.exit(1)
def keystring():
    k = os.environ.get("ETSY_KEYSTRING", "").strip()
    if not k: die("ETSY_KEYSTRING is not set in this session (run this in a cloud session on the Default environment)")
    return k
def call(url, data=None, headers=None, method=None):
    r = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=30) as resp: return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e: return e.code, e.read().decode()
def load_vault():
    return json.load(open(VAULT)) if os.path.exists(VAULT) else {}
def save_vault(d):
    os.makedirs(os.path.dirname(VAULT), exist_ok=True); json.dump(d, open(VAULT, "w"), indent=1); os.chmod(VAULT, 0o600)
def save_access(d):
    json.dump({"access_token": d["access_token"], "exp": time.time() + int(d.get("expires_in", 3600)) - 90}, open(ACCESS, "w")); os.chmod(ACCESS, 0o600)
def token_request(body):
    c, t = call(TOKEN_URL, urllib.parse.urlencode(body).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
    if c != 200: die(f"token endpoint HTTP {c}: {t[:300]}")
    return json.loads(t)

def cmd_link():
    v = secrets.token_urlsafe(64)[:96]; st = secrets.token_urlsafe(16)
    ch = base64.urlsafe_b64encode(hashlib.sha256(v.encode()).digest()).rstrip(b"=").decode()
    json.dump({"verifier": v, "state": st, "t": time.time()}, open(STATE, "w")); os.chmod(STATE, 0o600)
    print("https://www.etsy.com/oauth/connect?" + urllib.parse.urlencode({"response_type": "code", "redirect_uri": REDIRECT,
          "scope": SCOPES, "client_id": keystring(), "state": st, "code_challenge": ch, "code_challenge_method": "S256"}))

def cmd_exchange(code, state):
    s = json.load(open(STATE))
    if state.strip() != s["state"]: die("state does not match the link that was generated; run link again")
    d = token_request({"grant_type": "authorization_code", "client_id": keystring(), "redirect_uri": REDIRECT, "code": code.strip(), "code_verifier": s["verifier"]})
    vault = load_vault(); vault.update({"refresh_token": d["refresh_token"], "user_id": d["access_token"].split(".")[0], "scopes": SCOPES,
                                        "saved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    save_vault(vault); save_access(d); os.remove(STATE)
    print("ok: tokens saved; user_id", vault["user_id"], "; commit and push the vault file now")

def cmd_refresh():
    vault = load_vault()
    if not vault.get("refresh_token"): die("no refresh token in the vault; run link and exchange first")
    d = token_request({"grant_type": "refresh_token", "client_id": keystring(), "refresh_token": vault["refresh_token"]})
    vault["refresh_token"] = d["refresh_token"]; vault["saved"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_vault(vault); save_access(d); print("ok: refreshed; commit and push the vault file (the refresh token rotated)")

def access_token():
    if os.path.exists(ACCESS):
        a = json.load(open(ACCESS))
        if a.get("exp", 0) > time.time(): return a["access_token"]
    cmd_refresh(); return json.load(open(ACCESS))["access_token"]

def get(path):
    h = {"Authorization": f"Bearer {access_token()}"}
    # When openapi.etsy.com is not on the environment's API credential, send x-api-key ourselves (keystring:shared_secret).
    sec = os.environ.get("ETSY_SHARED_SECRET", "").strip()
    if sec: h["x-api-key"] = f"{keystring()}:{sec}"
    c, t = call(f"{API}{path}", headers=h)
    return c, t

def cmd_me():
    c, t = get("/users/me")
    if c != 200: die(f"GET /users/me HTTP {c}: {t[:300]}")
    me = json.loads(t); vault = load_vault(); vault["user_id"] = str(me.get("user_id")); vault["shop_id"] = str(me.get("shop_id"))
    save_vault(vault); print(json.dumps({"user_id": me.get("user_id"), "shop_id": me.get("shop_id")}))

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: die(__doc__)
    if a[0] == "link": cmd_link()
    elif a[0] == "exchange": cmd_exchange(a[1], a[2])
    elif a[0] == "refresh": cmd_refresh()
    elif a[0] == "me": cmd_me()
    elif a[0] == "token": access_token()
    else: die(__doc__)
