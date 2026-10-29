"""Offline tests for kimi_job.py: a fake Claude Code binary, fake source pages, no network, no key."""
import json
import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import kimi_job as kj  # noqa: E402

SLUG = "2026-10-29-quote-revive"
PAGE = ("<html><head><title>Follow-Ups 101</title><script>var x=1</script></head><body><p>Lots of words here. "
        "ServiceTitan data shows only 37% convert immediately, which leaves the majority of opportunities dependent on "
        "follow-up.</p></body></html>")


def fake_fetch(url):
    return (True, PAGE) if "servicetitan" in url else (False, "HTTPError: 403")


def fake_bin(tmp_path, body, code=0):
    p = tmp_path / "claude"
    p.write_text("#!/bin/sh\ncat > /dev/null\ncat <<'EOF'\n" + body + "\nEOF\nexit %d\n" % code)
    p.chmod(p.stat().st_mode | stat.S_IEXEC)
    return str(p)


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(kj, "KIMI", tmp_path / "kimi")
    monkeypatch.setattr(kj, "USAGE", tmp_path / "kimi" / "usage.json")
    monkeypatch.setattr(kj, "fetch", fake_fetch)
    jobs = tmp_path / "kimi" / "jobs"
    jobs.mkdir(parents=True)
    return tmp_path


def job(sandbox, name, body):
    p = sandbox / "kimi" / "jobs" / f"{name}.json"
    p.write_text(json.dumps(body))
    return p


def answer(sandbox, name):
    return json.loads((sandbox / "kimi" / "answers" / f"{name}.json").read_text())


def test_facts_prompt_has_gate_files_strings_and_sources():
    prompt, meta = kj.build({"kind": "facts", "slug": SLUG}, "t", fetcher=fake_fetch)
    assert "Gate: facts" in prompt and "This run has no tools" in prompt
    assert "### File: 02_transcript/transcript.md" in prompt and "string literal in 04_scene/scene.js" in prompt
    assert "37% convert immediately" in prompt and "var x=1" not in prompt
    assert "COULD NOT BE READ" in prompt
    assert [m["read"] for m in meta] == [True, False, False]


def test_scene_strings_drop_colors_and_code_words():
    s = kj.scene_strings("k.text('Send this text.', {color: '#FFF7EA', align: 'center', fx: 'hook.send', bg: 'rgba(1,2,3,0.2)'})")
    assert s == ["Send this text."]


def test_unknown_kind_bad_slug_and_plant_outside_selftest():
    with pytest.raises(ValueError):
        kj.build({"kind": "post", "slug": SLUG}, "t")
    with pytest.raises(ValueError):
        kj.build({"kind": "facts", "slug": "../../etc"}, "t", fetcher=fake_fetch)
    plant = {"kind": "facts", "slug": SLUG, "plant": {"file": "01_voice/script.md", "find": "thirty-seven", "replace": "forty-seven"}}
    assert "forty-seven" not in kj.build(plant, "live-job", fetcher=fake_fetch)[0]
    assert "forty-seven percent" in kj.build(plant, "x-selftest", fetcher=fake_fetch)[0]


def test_page_text_keeps_alt_text_and_straightens_quotes():
    t = kj.page_text('<p>If you haven\u2019t heard back, close the file.</p><img src="c.png" alt="59% expect text updates">')
    assert "59% expect text updates" in t
    assert "haven't heard back" in kj.excerpt(t, ["If you haven\u2019t heard back"])


def test_first_json_and_validation():
    assert kj.first_json('Sure.\n```json\n{"pass": false, "reasons": ["x {y}"]}\n```') == {"pass": False, "reasons": ["x {y}"]}
    assert kj.first_json("no json") is None
    assert kj.valid("facts", {"pass": True, "reasons": []}) and not kj.valid("facts", {"ok": True})
    assert not kj.valid("captions-draft", {"instagram": {}})


def test_daily_cap(sandbox):
    assert all(kj.take_slot("2026-10-29") for _ in range(kj.DAILY_CAP))
    assert not kj.take_slot("2026-10-29")
    assert kj.take_slot("2026-10-30")


def test_run_ok_bad_json_error_and_cap(sandbox, monkeypatch):
    reply = {"type": "result", "is_error": False, "result": '```json\n{"pass": true, "score": {"numbers": 3, "mismatches": 0}, "reasons": ["fine — ok"]}\n```',
             "usage": {"input_tokens": 900, "output_tokens": 50}}
    monkeypatch.setenv("KIMI_CLAUDE_BIN", fake_bin(sandbox, json.dumps(reply)))
    assert kj.run(job(sandbox, "a", {"kind": "facts", "slug": SLUG})) == 0
    a = answer(sandbox, "a")
    assert a["status"] == "ok" and a["result"]["pass"] is True and "—" not in json.dumps(a, ensure_ascii=False)
    monkeypatch.setenv("KIMI_CLAUDE_BIN", fake_bin(sandbox, json.dumps({"is_error": False, "result": "I think it passes"})))
    assert kj.run(job(sandbox, "b", {"kind": "facts", "slug": SLUG})) == 1 and answer(sandbox, "b")["status"] == "bad_json"
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-kimi-FAKEKEY1234567890")
    err = {"is_error": True, "result": "API Error: 401 key sk-kimi-FAKEKEY1234567890 invalid"}
    monkeypatch.setenv("KIMI_CLAUDE_BIN", fake_bin(sandbox, json.dumps(err)))
    assert kj.run(job(sandbox, "c", {"kind": "facts", "slug": SLUG})) == 1
    c = answer(sandbox, "c")
    assert c["status"] == "error" and "FAKEKEY" not in json.dumps(c)
    used = json.loads((sandbox / "kimi" / "usage.json").read_text())
    assert list(used.values()) == [3]
    for i in range(kj.DAILY_CAP - 3):
        kj.take_slot(kj.today())
    assert kj.run(job(sandbox, "d", {"kind": "facts", "slug": SLUG})) == 0 and answer(sandbox, "d")["status"] == "cap"


def test_second_opinion_needs_text():
    with pytest.raises(ValueError):
        kj.build({"kind": "second-opinion", "text": ""}, "t")
    p, _ = kj.build({"kind": "second-opinion", "title": "Audit", "text": "Rank: email first."}, "t")
    assert "Rank: email first." in p and '"top_three"' in p
