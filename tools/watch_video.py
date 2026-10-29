#!/usr/bin/env python3
"""Ask Google's Gemini to watch one video and answer a question about it.

Adapted for ProofNotFluff from bradautomates/claude-video v0.3.2 (MIT, Bradley Bonanno),
skills/watch/scripts/gemini.py. Kept: the Gemini adapter (key sent only as a request header,
scrubbed from every error, uploads deleted after the answer). Removed: yt-dlp downloads, ffmpeg,
WhisperX and Groq/OpenAI transcription, the installer, the session hook, and reading keys from
a config file or the working folder's .env.

Inputs: a public YouTube link (sent to Google by link, nothing downloaded) or a local video file
(uploaded to Google's Files API, then deleted). Standard library only.
"""
from __future__ import annotations

import argparse
import json
import math
import mimetypes
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = 'https://generativelanguage.googleapis.com'
INTERACTIONS = f'{API}/v1beta/interactions'
DEFAULT_MODEL = 'gemini-3.8-flash'  # gemini-3.7-flash, the upstream default, is deprecated and routed here.
YOUTUBE = re.compile(
    r'^https?://(?:(?:www\.|m\.)?youtube\.com/(?:watch\?\S*\bv=|shorts/|live/)|youtu\.be/)[^\s]+$', re.I)
HINTS = {
    'auth': 'the GEMINI_API_KEY was refused; Todd may need to create a new one',
    'quota': 'the key is rate limited or out of free quota; wait, or turn on billing for its project',
    'rejected': 'Gemini refused this request; the video may be private, unlisted, unsupported or too long',
    'service': 'Gemini had a server error; retry shortly',
    'network': 'could not reach generativelanguage.googleapis.com',
    'response': 'Gemini returned something this script cannot read',
    'upload': 'the file could not be uploaded to or processed by the Gemini Files API',
}
DEFAULT_QUESTION = ('Give a thorough summary of this video: what is shown, any on-screen text, '
                    'and what is said, in order.')
SUFFIX = ('\n\nCite an MM:SS timestamp for every claim about a specific moment. Separate what is seen '
          'from what is heard when it matters. If the video does not show or say something needed to '
          'answer, say so plainly instead of guessing.')


class GeminiError(Exception):
    def __init__(self, category: str, detail: str):
        super().__init__(f'Gemini {category}: {HINTS[category]}. Detail: {detail or "none"}')
        self.category = category


def is_youtube(source: str) -> bool:
    return bool(YOUTUBE.match(source or ''))


def _clean(text: str, key: str) -> str:
    text = str(text or '').strip()[-600:]
    return text.replace(key, '[redacted]') if key else text


def _message(body: bytes) -> str:
    text = body.decode('utf-8', errors='replace')
    try:
        data = json.loads(text)
        if isinstance(data, list) and data:
            data = data[0]
        return str(data['error']['message'])
    except (ValueError, KeyError, TypeError):
        return text


def _call(method, url, key, *, data=None, headers=None, timeout=60.0):
    request = Request(url, data=data, method=method, headers={'x-goog-api-key': key, **(headers or {})})
    try:
        with urlopen(request, timeout=timeout) as response:
            return dict(response.headers), response.read()
    except HTTPError as exc:
        message = _message(exc.read())
        category = ('auth' if exc.code in (401, 403) or 'api key' in message.lower() else
                    'quota' if exc.code == 429 else 'service' if exc.code >= 500 else 'rejected')
        raise GeminiError(category, _clean(f'HTTP {exc.code}: {message}', key)) from None
    except (URLError, TimeoutError, OSError) as exc:
        raise GeminiError('network', _clean(f'{type(exc).__name__}: {getattr(exc, "reason", exc)}', key)) from None


RUNNING = {'in_progress', 'queued', 'pending', 'running'}


def _json(body: bytes, key: str) -> dict:
    try:
        data = json.loads(body)
    except ValueError:
        data = None
    if not isinstance(data, dict):
        raise GeminiError('response', _clean(body[:300].decode('utf-8', errors='replace'), key))
    return data


def ask(video: dict, question: str | None, *, key: str, model: str, processing='agentic', timeout=600.0,
        poll=5.0, sleep=time.sleep) -> dict:
    # Background mode: one long request was dropped by Google's side in the first live run (Oct 29,
    # "Remote end closed connection"), so start the job, then poll it until it finishes.
    payload = {'model': model, 'background': True,
               'input': [{'type': 'video', **video, 'processing': processing},
                         {'type': 'text', 'text': ((question or '').strip() or DEFAULT_QUESTION) + SUFFIX}]}
    _, body = _call('POST', INTERACTIONS, key, data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'})
    data = _json(body, key)
    waited = 0.0
    while str(data.get('status', '')).lower() in RUNNING:
        if not data.get('id'):
            raise GeminiError('response', 'a running interaction came back without an id')
        if waited >= timeout:
            raise GeminiError('service', f'no answer after {int(timeout)}s (status {data.get("status")})')
        sleep(poll)
        waited += poll
        data = _json(_call('GET', f"{INTERACTIONS}/{data['id']}", key)[1], key)
    if str(data.get('status', '')).lower() in ('failed', 'cancelled', 'canceled', 'incomplete'):
        error = data.get('error') or {}
        detail = (error.get('message') if isinstance(error, dict) else error) or json.dumps(data)[:400]
        raise GeminiError('rejected', _clean(f"status {data['status']}: {detail}", key))
    try:
        parts = [p['text'] for step in data['steps'] if step.get('type') == 'model_output'
                 for p in step.get('content', []) if p.get('type') == 'text' and p.get('text')]
        tokens = (data.get('usage') or {}).get('total_tokens')
    except (KeyError, TypeError, AttributeError):
        raise GeminiError('response', _clean(json.dumps(data)[:300], key)) from None
    if not parts:
        raise GeminiError('response', f'no answer text (status {data.get("status")})')
    return {'text': '\n'.join(parts).strip(), 'tokens': tokens if isinstance(tokens, int) else None,
            'processing': processing}


def ask_link(url: str, question: str | None, *, key: str, model: str, timeout=600.0) -> dict:
    # generateContent with file_data is Google's long-standing YouTube path. The Interactions API ran
    # 18 minutes on a public link and failed with no reason in both modes (live run, Oct 29).
    payload = {'contents': [{'parts': [{'file_data': {'file_uri': url}},
                                       {'text': ((question or '').strip() or DEFAULT_QUESTION) + SUFFIX}]}]}
    _, body = _call('POST', f'{API}/v1beta/models/{model}:generateContent', key,
                    data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'},
                    timeout=timeout)
    data = _json(body, key)
    try:
        candidate = (data.get('candidates') or [{}])[0]
        parts = [p['text'] for p in (candidate.get('content') or {}).get('parts', []) if p.get('text')]
        tokens = (data.get('usageMetadata') or {}).get('totalTokenCount')
    except (KeyError, TypeError, AttributeError, IndexError):
        raise GeminiError('response', _clean(json.dumps(data)[:300], key)) from None
    if not parts:
        reason = candidate.get('finishReason') or (data.get('promptFeedback') or {}).get('blockReason')
        raise GeminiError('rejected', f'no answer text (reason {reason or "none given"})')
    return {'text': '\n'.join(parts).strip(), 'tokens': tokens if isinstance(tokens, int) else None,
            'processing': 'generateContent'}


def upload(path: Path, key: str, *, poll=2.0, max_wait=900.0, sleep=time.sleep) -> dict:
    size = path.stat().st_size
    if size == 0:
        raise GeminiError('upload', f'{path.name} is empty')
    guessed = mimetypes.guess_type(path.name)[0] or ''
    mime = guessed if guessed.startswith('video/') else 'video/mp4'
    headers, _ = _call('POST', f'{API}/upload/v1beta/files', key,
                       data=json.dumps({'file': {'display_name': 'watch-video-upload'}}).encode('utf-8'),
                       headers={'X-Goog-Upload-Protocol': 'resumable', 'X-Goog-Upload-Command': 'start',
                                'X-Goog-Upload-Header-Content-Length': str(size),
                                'X-Goog-Upload-Header-Content-Type': mime, 'Content-Type': 'application/json'})
    session = {k.lower(): v for k, v in headers.items()}.get('x-goog-upload-url')
    if not session:
        raise GeminiError('upload', 'no upload session URL came back')
    with path.open('rb') as stream:
        _, body = _call('POST', session, key, data=stream, timeout=3600.0,
                        headers={'Content-Length': str(size), 'X-Goog-Upload-Offset': '0',
                                 'X-Goog-Upload-Command': 'upload, finalize'})
    try:
        info = json.loads(body)['file']
        waited = 0.0
        while info.get('state') == 'PROCESSING':
            if waited >= max_wait:
                delete(info['name'], key)
                raise GeminiError('upload', f'still processing after {int(max_wait)}s')
            sleep(poll)
            waited += poll
            info = json.loads(_call('GET', f"{API}/v1beta/{info['name']}", key)[1])
        if info.get('state') != 'ACTIVE':
            delete(info['name'], key)
            raise GeminiError('upload', f"file state {info.get('state')}")
        return {'name': info['name'], 'uri': info['uri'], 'mime_type': info.get('mimeType') or mime}
    except (ValueError, KeyError, TypeError):
        raise GeminiError('upload', 'unreadable Files API response') from None


def delete(name: str, key: str) -> str | None:
    try:
        _call('DELETE', f'{API}/v1beta/{name}', key)
        return None
    except Exception:  # Cleanup never hides the real result.
        return f'Could not delete the upload {name}; Google removes it on its own within 48 hours.'


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog='watch_video', description=__doc__.splitlines()[0])
    ap.add_argument('source', help='A public YouTube link, or a local video file path')
    ap.add_argument('--question', default=None, help='What to ask about the video')
    ap.add_argument('--upload-ok', action='store_true',
                    help='Required to upload a local file. Use only for video that is already public, '
                         'or when the key is on a paid (billed) project.')
    ap.add_argument('--model', default=os.environ.get('WATCH_GEMINI_MODEL', DEFAULT_MODEL))
    ap.add_argument('--timeout', type=float, default=600.0)
    args = ap.parse_args(argv)

    key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not key:
        print('watch_video: GEMINI_API_KEY is not set in this run. Todd adds it himself; never ask for it in chat.',
              file=sys.stderr)
        return 3
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        ap.error('--timeout must be a positive number')

    uploaded, note, sent = None, None, 'link sent to Google'
    try:
        if is_youtube(args.source):
            try:
                result = ask_link(args.source, args.question, key=key, model=args.model, timeout=args.timeout)
            except GeminiError as exc:
                if exc.category != 'network':
                    raise
                # One retry when the long request is dropped; uses the background Interactions path.
                result = ask({'uri': args.source}, args.question, key=key, model=args.model,
                             processing='static', timeout=args.timeout)
        elif re.match(r'^[a-z][a-z0-9+.-]*://', args.source, re.I):
            print('watch_video: only public YouTube links can be sent by link. TikTok, Instagram, Facebook and '
                  'other sites are not downloaded; save the video file first if it may be used.', file=sys.stderr)
            return 2
        else:
            path = Path(args.source).expanduser().resolve()
            if not path.is_file():
                print(f'watch_video: file not found: {path}', file=sys.stderr)
                return 2
            if not args.upload_ok:
                print('watch_video: uploading a local file needs --upload-ok (public video, or a billed key).',
                      file=sys.stderr)
                return 2
            uploaded = upload(path, key)
            sent = 'file uploaded to Google, deleted after the answer'
            result = ask({'uri': uploaded['uri'], 'mime_type': uploaded['mime_type']}, args.question,
                         key=key, model=args.model, timeout=args.timeout)
    except GeminiError as exc:
        print(f'# Video answer\n\n- Source: {args.source} ({sent})\n\n## Unavailable\n\n- {exc}')
        return 1
    finally:
        if uploaded:
            note = delete(uploaded['name'], key)

    print('# Video answer')
    print()
    print(f'- Source: {args.source} ({sent})')
    print(f"- Model: {args.model} ({result['processing']})")
    if result['tokens'] is not None:
        print(f"- Gemini tokens: {result['tokens']}")
    if note:
        print(f'- Cleanup: {note}')
    print()
    print("## Answer (Gemini's observations, not frames Claude viewed)")
    print()
    print(result['text'])
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
