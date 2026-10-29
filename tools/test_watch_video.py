"""Offline tests for watch_video.py: fake Google responses, no network, no key."""
import io
import json
import sys
from pathlib import Path
from urllib.error import HTTPError

import pytest

sys.path.insert(0, str(Path(__file__).parent))
import watch_video as wv  # noqa: E402

KEY = 'AIzaFAKEKEY0123456789'


class Resp:
    def __init__(self, body=b'{}', headers=None):
        self.body, self.headers, self.status = body, headers or {}, 200

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def answer(text='At 00:05 the hook appears.'):
    return Resp(json.dumps({'steps': [{'type': 'thought'}, {'type': 'model_output',
                'content': [{'type': 'text', 'text': text}]}], 'usage': {'total_tokens': 1234}}).encode())


def http_error(code, msg):
    return HTTPError('https://x.invalid', code, 'err', {}, io.BytesIO(json.dumps({'error': {'message': msg}}).encode()))


@pytest.fixture
def calls(monkeypatch):
    log, queue = [], []

    def fake(request, timeout=None, **kw):
        log.append(request)
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item
    monkeypatch.setattr(wv, 'urlopen', fake)
    monkeypatch.setenv('GEMINI_API_KEY', KEY)
    return log, queue


def classic(text='At 00:05 the hook appears.'):
    return Resp(json.dumps({'candidates': [{'content': {'parts': [{'text': text}]}, 'finishReason': 'STOP'}],
                            'usageMetadata': {'totalTokenCount': 4321}}).encode())


def test_youtube_link_sent_by_link_with_header_key(calls, capsys):
    log, queue = calls
    queue.append(classic())
    assert wv.main(['https://www.youtube.com/shorts/abc123', '--question', 'What is the hook?']) == 0
    req = log[0]
    assert req.full_url == f'{wv.API}/v1beta/models/gemini-3.8-flash:generateContent'
    assert req.get_header('X-goog-api-key') == KEY
    parts = json.loads(req.data)['contents'][0]['parts']
    assert parts[0] == {'file_data': {'file_uri': 'https://www.youtube.com/shorts/abc123'}}
    out = capsys.readouterr().out
    assert 'At 00:05 the hook appears.' in out and 'Gemini tokens: 4321' in out and KEY not in out


def test_dropped_link_request_retries_in_background(calls):
    log, queue = calls
    queue += [OSError('Remote end closed connection'), answer()]
    assert wv.main(['https://youtu.be/abc']) == 0
    body = json.loads(log[1].data)
    assert log[1].full_url == wv.INTERACTIONS and body['background'] is True
    assert body['input'][0]['processing'] == 'static'


def test_empty_answer_reports_reason(calls, capsys):
    _, queue = calls
    queue.append(Resp(json.dumps({'candidates': [{'finishReason': 'SAFETY'}]}).encode()))
    assert wv.main(['https://youtu.be/abc']) == 1
    assert 'SAFETY' in capsys.readouterr().out


def test_key_scrubbed_from_errors(calls, capsys):
    _, queue = calls
    queue.append(http_error(400, f'API key not valid: {KEY}'))
    assert wv.main(['https://youtu.be/abc']) == 1
    out = capsys.readouterr().out
    assert KEY not in out and 'Gemini auth' in out


def test_other_sites_refused_without_network(calls):
    log, _ = calls
    for url in ('https://www.tiktok.com/@a/video/1', 'https://www.instagram.com/reel/x/', 'https://vimeo.com/1'):
        assert wv.main([url]) == 2
    assert log == []


def test_missing_key(monkeypatch):
    monkeypatch.delenv('GEMINI_API_KEY', raising=False)
    assert wv.main(['https://youtu.be/abc']) == 3


def test_local_file_needs_upload_ok(calls, tmp_path):
    log, _ = calls
    f = tmp_path / 'clip.mp4'
    f.write_bytes(b'0' * 10)
    assert wv.main([str(f)]) == 2
    assert log == []


def test_local_upload_then_delete(calls, tmp_path, capsys):
    log, queue = calls
    f = tmp_path / 'clip.mp4'
    f.write_bytes(b'0' * 10)
    queue += [Resp(headers={'X-Goog-Upload-URL': 'https://upload.invalid/s'}),
              Resp(json.dumps({'file': {'name': 'files/abc', 'uri': 'https://g/files/abc', 'state': 'ACTIVE',
                                        'mimeType': 'video/mp4'}}).encode()),
              answer(), Resp()]
    assert wv.main([str(f), '--upload-ok']) == 0
    assert log[-1].get_method() == 'DELETE' and log[-1].full_url.endswith('/v1beta/files/abc')
    assert 'deleted after the answer' in capsys.readouterr().out


def test_delete_still_runs_when_answer_fails(calls, tmp_path):
    log, queue = calls
    f = tmp_path / 'clip.mp4'
    f.write_bytes(b'0' * 10)
    queue += [Resp(headers={'x-goog-upload-url': 'https://upload.invalid/s'}),
              Resp(json.dumps({'file': {'name': 'files/abc', 'uri': 'u', 'state': 'ACTIVE'}}).encode()),
              http_error(500, 'boom'), Resp()]
    assert wv.main([str(f), '--upload-ok']) == 1
    assert log[-1].get_method() == 'DELETE'


def test_background_job_is_polled_until_done(calls):
    log, queue = calls
    queue += [Resp(json.dumps({'id': 'int-1', 'status': 'in_progress'}).encode()),
              Resp(json.dumps({'id': 'int-1', 'status': 'in_progress'}).encode()), answer('Done at 00:10.')]
    naps = []
    result = wv.ask({'uri': 'https://youtu.be/abc'}, 'q', key=KEY, model='m', sleep=naps.append)
    assert json.loads(log[0].data)['background'] is True
    assert [r.get_method() for r in log] == ['POST', 'GET', 'GET']
    assert log[1].full_url == f'{wv.INTERACTIONS}/int-1' and log[1].get_header('X-goog-api-key') == KEY
    assert result['text'] == 'Done at 00:10.' and naps == [5.0, 5.0]


def test_background_job_gives_up_at_timeout(calls):
    _, queue = calls
    queue += [Resp(json.dumps({'id': 'int-2', 'status': 'in_progress'}).encode())] * 3
    with pytest.raises(wv.GeminiError) as err:
        wv.ask({'uri': 'u'}, 'q', key=KEY, model='m', timeout=10, sleep=lambda s: None)
    assert err.value.category == 'service'


def test_failed_job_reports_what_google_sent(calls):
    _, queue = calls
    queue.append(Resp(json.dumps({'id': 'i', 'status': 'failed'}).encode()))
    with pytest.raises(wv.GeminiError) as err:
        wv.ask({'uri': 'u'}, 'q', key=KEY, model='m', sleep=lambda s: None)
    assert err.value.category == 'rejected' and '"id": "i"' in str(err.value)


def test_dashes_removed_from_answers(calls, capsys):
    _, queue = calls
    queue.append(classic('Intro 00:02\u201300:04 \u2014 then trash first'))
    assert wv.main(['https://youtu.be/abc']) == 0
    out = capsys.readouterr().out
    assert '00:02 to 00:04, then trash first' in out and '\u2013' not in out and '\u2014' not in out
