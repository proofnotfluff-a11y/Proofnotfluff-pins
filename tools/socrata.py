#!/usr/bin/env python3
"""Socrata (SODA 2.x) client for the City data portals, shared by the downstream lead pipeline.

Deterministic by design (Agentic Engineering rule: code fetches, pages and counts; a model never does):
- every pull pages with $limit/$offset in a stable $order until a short page arrives,
- every pull is checked against the portal's own count(*) for the same $where, so a capped or cut page is an error,
- every HTTP failure is retried with backoff and then raised as SocrataError, never swallowed.

Runs in GitHub Actions: the cloud sandbox's proxy refuses data.cityofchicago.org and data.austintexas.gov.

Usage as a library:
    from socrata import Socrata
    chi = Socrata("https://data.cityofchicago.org")
    rows = chi.pull("ydr8-5enu", where="issue_date >= '2025-01-01'", select="id,permit_", order=":id")
    cols = chi.columns("ydr8-5enu")
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "ProofNotFluff downstream leads (github.com/proofnotfluff-a11y/Proofnotfluff-pins)"}
PAGE = 5000


class SocrataError(RuntimeError):
    """Raised when a portal call fails after every retry, or when a pull comes back short of the portal's own count."""


class Socrata:
    def __init__(self, portal, tries=4, timeout=120, pause=5.0, opener=None):
        self.portal = portal.rstrip("/")
        self.tries = tries
        self.timeout = timeout
        self.pause = pause
        self.opener = opener or urllib.request.urlopen

    def _get(self, path, params=None):
        url = f"{self.portal}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        last = None
        for attempt in range(self.tries):
            try:
                with self.opener(urllib.request.Request(url, headers=UA), timeout=self.timeout) as r:
                    return json.loads(r.read().decode("utf-8", "replace"))
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
                if e.code in (400, 403, 404):
                    break  # a bad query or a missing dataset does not heal with a retry
            except Exception as e:  # network errors, timeouts, bad JSON
                last = f"{type(e).__name__}: {str(e)[:160]}"
            time.sleep(self.pause * (attempt + 1))
        raise SocrataError(f"{url[:200]} failed: {last}")

    def rows(self, dataset, **params):
        """One SODA query, as given. Use pull() for anything that may exceed one page."""
        clean = {k if k.startswith("$") else f"${k}": v for k, v in params.items() if v not in (None, "")}
        out = self._get(f"/resource/{dataset}.json", clean)
        if not isinstance(out, list):
            raise SocrataError(f"{dataset}: expected a list of rows, got {type(out).__name__}")
        return out

    def count(self, dataset, where=None):
        out = self.rows(dataset, select="count(*) AS n", where=where)
        try:
            return int(out[0]["n"])
        except (IndexError, KeyError, ValueError) as e:
            raise SocrataError(f"{dataset}: count(*) unreadable ({e})")

    def pull(self, dataset, where=None, select=None, order=":id", key=None, max_rows=200000):
        """Every row matching where, paged until a short page, de-duplicated on key when given, then checked against the
        portal's own count. Raises SocrataError when the pull is short or the result would pass max_rows."""
        if key and select and key not in [c.strip().split(" ")[0] for c in select.split(",")]:
            raise SocrataError(f"{dataset}: key {key!r} must be in select, or every row would look like a duplicate")
        want = self.count(dataset, where)
        if want > max_rows:
            raise SocrataError(f"{dataset}: {want} rows match, over the {max_rows} row ceiling; narrow the where clause")
        out, seen, offset = [], set(), 0
        while True:
            page = self.rows(dataset, select=select, where=where, order=order, limit=PAGE, offset=offset)
            for r in page:
                k = r.get(key) if key else None
                if key and k in seen:
                    continue
                if key:
                    seen.add(k)
                out.append(r)
            if len(page) < PAGE:
                break
            offset += PAGE
        if len(out) < want and not key:
            raise SocrataError(f"{dataset}: pull short, {len(out)} rows of {want} for where={str(where)[:120]}")
        if key and offset + len(page) < want:
            raise SocrataError(f"{dataset}: pull short, {offset + len(page)} rows read of {want} for where={str(where)[:120]}")
        return out

    def columns(self, dataset):
        """The dataset's column field names from its metadata view."""
        meta = self._get(f"/api/views/{dataset}.json")
        cols = [c.get("fieldName") for c in meta.get("columns", []) if c.get("fieldName")]
        if not cols:
            raise SocrataError(f"{dataset}: metadata has no columns")
        return cols

    def require_columns(self, dataset, needed):
        cols = set(self.columns(dataset))
        missing = sorted(set(needed) - cols)
        if missing:
            raise SocrataError(f"{dataset}: columns changed, missing {missing}")
        return cols


def quote(value):
    """A SoQL string literal."""
    return "'" + str(value).replace("'", "''") + "'"


def in_list(values):
    return "(" + ",".join(quote(v) for v in values) + ")"
