#!/usr/bin/env python3
"""Encrypted box for Entity B data that has to cross this public repo (the GitHub Actions enrichment run hands named
decision-makers to the cloud prospect-matching run). Passphrase from the PNF_DATA_KEY environment variable (a GitHub
Actions secret and a variable in the cloud environment, set by Todd; never printed, logged or committed).
scrypt (n=2**15, r=8, p=1) derives a 256-bit key; AES-256-GCM over gzip; a fresh salt and nonce per box.

Usage: PNF_DATA_KEY=... python3 tools/data_box.py seal  data/prospects/prospects.json prospects/enriched.sealed.json
       PNF_DATA_KEY=... python3 tools/data_box.py open  prospects/enriched.sealed.json data/prospects/enriched.json
       python3 tools/data_box.py --selftest
Exit 0 on success, 1 on a missing key, a wrong key or a damaged box.
"""
import base64
import gzip
import json
import os
import sys

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

ALG = "scrypt-n32768-r8-p1+AES-256-GCM+gzip"


def _key(passphrase, salt):
    return Scrypt(salt=salt, length=32, n=2 ** 15, r=8, p=1).derive(passphrase.encode("utf-8"))


def seal(data: bytes, passphrase: str) -> dict:
    salt, nonce = os.urandom(16), os.urandom(12)
    ct = AESGCM(_key(passphrase, salt)).encrypt(nonce, gzip.compress(data, 9, mtime=0), ALG.encode())
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "alg": ALG, "salt": b(salt), "nonce": b(nonce), "ct": b(ct)}


def unseal(box: dict, passphrase: str) -> bytes:
    if box.get("alg") != ALG:
        raise ValueError("unknown box format")
    d = base64.b64decode
    return gzip.decompress(AESGCM(_key(passphrase, d(box["salt"]))).decrypt(d(box["nonce"]), d(box["ct"]), ALG.encode()))


def passphrase():
    k = os.environ.get("PNF_DATA_KEY", "")
    if len(k) < 20:
        print("ERROR box: PNF_DATA_KEY is missing or shorter than 20 characters")
        sys.exit(1)
    return k


def selftest():
    box = seal(b'{"a": 1}', "a test passphrase of enough length")
    ok = unseal(box, "a test passphrase of enough length") == b'{"a": 1}'
    try:
        unseal(box, "the wrong passphrase, also long enough")
        wrong = False
    except InvalidTag:
        wrong = True
    if not (ok and wrong):
        print("data_box selftest: FAIL")
        sys.exit(1)
    print("data_box selftest: PASS 2 checks (round trip, wrong key refused)")
    sys.exit(0)


def main():
    if sys.argv[1:] == ["--selftest"]:
        return selftest()
    if len(sys.argv) != 4 or sys.argv[1] not in ("seal", "open"):
        print(__doc__)
        sys.exit(1)
    mode, src, dst = sys.argv[1:]
    k = passphrase()
    try:
        if mode == "seal":
            out = json.dumps(seal(open(src, "rb").read(), k), indent=1)
            open(dst, "w", encoding="utf-8").write(out + "\n")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
            open(dst, "wb").write(unseal(json.load(open(src, encoding="utf-8")), k))
    except (OSError, ValueError, InvalidTag) as e:
        print(f"ERROR box: {mode} failed ({type(e).__name__})")
        sys.exit(1)
    print(f"OK box: {mode} {os.path.basename(src)} -> {dst}")
    sys.exit(0)


if __name__ == "__main__":
    main()
