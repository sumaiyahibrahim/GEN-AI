"""Ollama HTTP client with bounded retries, persistent caching and usage logging.

The standard library is sufficient for Week 1 and client unit tests.
There is no mock inference fallback: unavailable models produce an explicit error.
"""
import hashlib
import json
import random
import sqlite3
import time
import urllib.error
import urllib.request
from contextlib import closing
from datetime import datetime, timezone

from .config import Settings


class ModelError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, settings=None, opener=None, sleeper=time.sleep):
        self.settings = settings or Settings.from_env()
        self.opener = opener or urllib.request.urlopen
        self.sleeper = sleeper
        self.settings.runtime.mkdir(parents=True, exist_ok=True)
        self.cache_path = self.settings.runtime / 'cache.sqlite3'
        with closing(sqlite3.connect(self.cache_path)) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS cache (key TEXT PRIMARY KEY, value TEXT NOT NULL)')

    def _key(self, payload):
        raw = json.dumps({'endpoint': self.settings.base_url, 'payload': payload}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def _cached(self, key):
        with closing(sqlite3.connect(self.cache_path)) as db, db:
            row = db.execute('SELECT value FROM cache WHERE key=?', (key,)).fetchone()
        return json.loads(row[0]) if row else None

    def _save_cache(self, key, result):
        with closing(sqlite3.connect(self.cache_path)) as db, db:
            db.execute('INSERT OR REPLACE INTO cache VALUES (?,?)', (key, json.dumps(result)))

    def _open(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        req = urllib.request.Request(self.settings.base_url + path, data=data,
                                     headers={'Content-Type': 'application/json'})
        for attempt in range(self.settings.attempts):
            try:
                return self.opener(req, timeout=self.settings.timeout)
            except urllib.error.HTTPError as exc:
                detail = exc.read(2000).decode(errors='replace')
                if exc.code not in (429, 500, 502, 503, 504) or attempt + 1 == self.settings.attempts:
                    raise ModelError(f'Ollama HTTP {exc.code}: {detail}') from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                if attempt + 1 == self.settings.attempts:
                    raise ModelError('Cannot reach local Ollama. Start Ollama, pull the configured models, '
                                     'and run python -m internship.cli doctor.') from exc
            self.sleeper(min(8, 2 ** attempt) + random.uniform(0, 0.2))
        raise ModelError('Request failed after bounded retries.')

    def _json(self, path, payload=None):
        try:
            with self._open(path, payload) as response:
                result = json.loads(response.read())
        except (ValueError, KeyError) as exc:
            raise ModelError('Ollama returned an invalid JSON response.') from exc
        if not isinstance(result, dict) or result.get('error'):
            raise ModelError(str(result.get('error')) if isinstance(result, dict) else 'Invalid response object')
        return result

    def health(self):
        return self._json('/api/tags')

    def _record(self, result, elapsed, cached=False, operation='chat'):
        row = {
            'timestamp': datetime.now(timezone.utc).isoformat(), 'operation': operation,
            'model': result.get('model', self.settings.chat_model), 'cached': cached,
            'latency_seconds': round(elapsed, 4),
            'input_tokens': 0 if cached else result.get('prompt_eval_count', 0),
            'output_tokens': 0 if cached else result.get('eval_count', 0),
            'provider_charge_usd': 0,
        }
        # No prompts or document text are written to this metrics file.
        with (self.settings.runtime / 'usage.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(row) + '\n')

    def chat(self, messages, *, schema=None, tools=None, cache=True, temperature=0):
        if not messages:
            raise ValueError('At least one message is required.')
        payload = {'model': self.settings.chat_model, 'messages': messages, 'stream': False,
                   'options': {'temperature': temperature, 'num_ctx': 4096}}
        if schema is not None:
            payload['format'] = schema
        if tools:
            payload['tools'] = tools
            cache = False
        start = time.perf_counter()
        key = self._key(payload)
        result = self._cached(key) if cache else None
        if result is not None:
            self._record(result, time.perf_counter() - start, cached=True)
            return result
        failure = None
        for model in (self.settings.chat_model,) + self.settings.fallbacks:
            payload['model'] = model
            try:
                result = self._json('/api/chat', payload)
                if not isinstance(result.get('message'), dict):
                    raise ModelError('Missing message in model response.')
                break
            except ModelError as exc:
                failure = exc
        else:
            raise failure
        self._record(result, time.perf_counter() - start)
        if cache:
            self._save_cache(key, result)
        return result

    def embed(self, texts):
        if not texts or any(not t.strip() for t in texts):
            raise ValueError('Embedding input must contain nonempty text.')
        start = time.perf_counter()
        result = self._json('/api/embed', {'model': self.settings.embed_model,
                                          'input': texts, 'truncate': False})
        vectors = result.get('embeddings')
        if not isinstance(vectors, list) or len(vectors) != len(texts) or any(not v for v in vectors):
            raise ModelError('Embedding response does not match the requested inputs.')
        self._record(result, time.perf_counter() - start, operation='embed')
        return vectors

    def stream_chat(self, messages):
        payload = {'model': self.settings.chat_model, 'messages': messages, 'stream': True,
                   'options': {'temperature': 0, 'num_ctx': 4096}}
        cache_payload = dict(payload, stream=False)
        key = self._key(cache_payload)
        start = time.perf_counter()
        cached = self._cached(key)
        if cached:
            self._record(cached, time.perf_counter() - start, cached=True)
            yield cached['message'].get('content', '')
            return
        parts, finished = [], False
        try:
            with self._open('/api/chat', payload) as response:
                for line in response:
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if event.get('error'):
                        raise ModelError(str(event['error']))
                    part = event.get('message', {}).get('content', '')
                    if part:
                        parts.append(part)
                        yield part
                    if event.get('done'):
                        finished = True
                        event['message'] = {'role': 'assistant', 'content': ''.join(parts)}
                        self._record(event, time.perf_counter() - start)
                        self._save_cache(key, event)
                        break
        except (ValueError, OSError) as exc:
            raise ModelError('Streaming was interrupted; the partial answer was not cached.') from exc
        if not finished:
            raise ModelError('Streaming ended without a completion event; no answer was cached.')
