#!/usr/bin/env python3
"""Seal the raw Food Inspections pull for the crew's offline checks (Chicago Restaurant Inspection Leads, Oct 2026).

The cloud agents cannot reach data.cityofchicago.org, and the raw pull holds the City's inspector notes, which the
product never republishes. So the Actions runner seals the raw file to a public key (RSA-OAEP-SHA256 wrapping a
random AES-256-GCM key, over gzip) and commits only the sealed box. The private key is never in this repo; it lives
with the live session, which opens the box to build previews and to hand the holdout checker the City's own rows.

The members' pages are not built from this box: they are built in the runner from the unsealed raw file and
encrypted under the members' password (tools/rest_app.py), the same way the construction product works.

Usage: python3 tools/rest_seal.py seal raw.json permits/inspections-chicago/raw.sealed.json [--key PUB.pem]
       python3 tools/rest_seal.py open permits/inspections-chicago/raw.sealed.json OUT.json --key PRIVATE.pem
       python3 tools/rest_seal.py --selftest
"""
import base64, gzip, json, os, sys

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "permits", "inspections-chicago", "raw-seal.pub.pem")
OAEP = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


def seal(data: bytes, pub_pem: bytes):
    pub = serialization.load_pem_public_key(pub_pem)
    key, iv = AESGCM.generate_key(bit_length=256), os.urandom(12)
    ct = AESGCM(key).encrypt(iv, gzip.compress(data, 9, mtime=0), None)
    b = lambda x: base64.b64encode(x).decode()
    return {"v": 1, "alg": "RSA-OAEP-SHA256+AES-256-GCM", "gzip": True, "key": b(pub.encrypt(key, OAEP)), "iv": b(iv), "ct": b(ct)}


def unseal(box, priv_pem: bytes):
    priv = serialization.load_pem_private_key(priv_pem, password=None)
    d = lambda x: base64.b64decode(x)
    key = priv.decrypt(d(box["key"]), OAEP)
    return gzip.decompress(AESGCM(key).decrypt(d(box["iv"]), d(box["ct"]), None))


def selftest():
    from cryptography.hazmat.primitives.asymmetric import rsa
    k = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pub = k.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo)
    priv = k.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    msg = json.dumps({"rows": [{"dba_name": "ACME TACOS", "violations": "38. INSECTS - Comments: MICE"}]}).encode()
    box = seal(msg, pub)
    assert "ACME" not in json.dumps(box) and unseal(box, priv) == msg
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048).private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    try:
        unseal(box, other)
        raise AssertionError("another key opened the box")
    except AssertionError:
        raise
    except Exception:
        pass
    print("rest_seal selftest ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a == ["--selftest"]:
        selftest()
    elif a[:1] == ["seal"]:
        key = a[a.index("--key") + 1] if "--key" in a else PUB
        if not os.path.isfile(key):
            print("no public key; raw pull not sealed"); sys.exit(0)
        box = seal(open(a[1], "rb").read(), open(key, "rb").read())
        json.dump(box, open(a[2], "w"))
        print("sealed", os.path.getsize(a[2]), "bytes")
    elif a[:1] == ["open"]:
        open(a[2], "wb").write(unseal(json.load(open(a[1])), open(a[a.index("--key") + 1], "rb").read()))
        print("opened", a[2])
    else:
        raise SystemExit(__doc__)
