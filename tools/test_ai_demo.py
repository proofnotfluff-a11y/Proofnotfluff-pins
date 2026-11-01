"""Offline tests for tools/ai_demo.py: no network, no key."""
import json

import ai_demo as A
import watch_video as W


def fake_call(reply, model="gemini-test-001"):
    def call(method, url, key, **kw):
        assert method == "POST" and url.endswith(":generateContent")
        body = json.loads(kw["data"])
        assert body["contents"][0]["parts"][0]["text"]
        return {}, json.dumps({"candidates": [{"content": {"parts": [{"text": reply}]}}],
                               "modelVersion": model, "usageMetadata": {"totalTokenCount": 42}}).encode()
    return call


def test_reply_kept_and_dashes_counted(tmp_path):
    job = tmp_path / "j1.json"
    job.write_text(json.dumps({"prompt": "Write a reply to this review."}))
    code = A.run(job, tmp_path / "out", key="k", call=fake_call("Thanks for the note — we will fix it."))
    out = json.loads((tmp_path / "out" / "j1" / "run.json").read_text())
    assert code == 0 and out["model"] == "gemini-test-001" and out["dashes"] == 1
    assert "—" not in out["text"] and out["text"].startswith("Thanks for the note")
    assert out["prompt"] == "Write a reply to this review." and out["tokens"] == 42


def test_no_text_is_an_error(tmp_path):
    def call(*a, **k):
        return {}, json.dumps({"candidates": [{"finishReason": "SAFETY"}]}).encode()
    job = tmp_path / "j2.json"
    job.write_text(json.dumps({"prompt": "x"}))
    assert A.run(job, tmp_path / "out", key="k", call=call) == 1
    assert "SAFETY" in (tmp_path / "out" / "j2" / "error.txt").read_text()


def test_bad_pages_refused(tmp_path):
    job = tmp_path / "j3.json"
    job.write_text(json.dumps({"pages": ["http://plain.example.com", "file:///etc/passwd"]}))
    assert A.run(job, tmp_path / "out", key="", shooter=lambda p, o: []) == 2
    assert A.check_job({"pages": ["https://a.example.com/x"] * 5}) == "at most 4 pages"


def test_pages_recorded(tmp_path):
    job = tmp_path / "j4.json"
    job.write_text(json.dumps({"pages": ["https://help.example.com/x"]}))
    rows = [{"n": 1, "url": "https://help.example.com/x", "title": "Help"}]
    assert A.run(job, tmp_path / "out", key="", shooter=lambda p, o: rows) == 0
    assert json.loads((tmp_path / "out" / "j4" / "pages.json").read_text())[0]["title"] == "Help"


def test_key_never_in_errors():
    try:
        A.generate("x", key="SECRETKEY", model="m",
                   call=lambda *a, **k: (_ for _ in ()).throw(W.GeminiError("auth", W._clean("bad SECRETKEY", "SECRETKEY"))))
    except W.GeminiError as e:
        assert "SECRETKEY" not in str(e)
