import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from internship.client import OllamaClient, ModelError
from internship.config import Settings
from internship.documents import load_chunks, split_text
from internship.tools import calculate, execute_tool
from internship.rag import NO_EVIDENCE, answer_messages, validate_citations
from internship.exercises import validate_invoice
from internship.agent import SupportAgent


def response(value):
    return io.BytesIO(json.dumps(value).encode())


class DocumentTests(unittest.TestCase):
    def test_chunk_limits_and_termination(self):
        text = 'word ' * 800
        pieces = list(split_text(text, 120, 20))
        self.assertGreater(len(pieces), 1)
        self.assertTrue(all(0 < len(p) <= 120 for p in pieces))
        self.assertEqual(list(split_text('', 10, 2)), [])

    def test_small_sizes_and_unbroken_text(self):
        self.assertEqual(list(split_text('abc', 1, 0)), ['a', 'b', 'c'])
        pieces = list(split_text('x' * 100, 10, 9))
        self.assertLessEqual(len(pieces), 100)
        self.assertTrue(all(len(p) <= 10 for p in pieces))

    def test_invalid_chunk_settings(self):
        for size, overlap in [(0, 0), (10, 10), (10, -1)]:
            with self.assertRaises(ValueError):
                list(split_text('hello', size, overlap))

    def test_document_metadata_and_stable_ids(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'demo.md'
            path.write_text('A real unit test document. ' * 20)
            first = load_chunks([path], 100, 10)
            self.assertEqual(first, load_chunks([path], 100, 10))
            self.assertTrue(all(c.source == 'demo.md' and c.page == 1 for c in first))
            self.assertEqual(len({c.id for c in first}), len(first))

    def test_empty_and_unsupported_documents(self):
        with tempfile.TemporaryDirectory() as folder:
            for name in ['empty.md', 'file.exe']:
                path = Path(folder) / name
                path.write_text('')
                with self.assertRaises(ValueError):
                    load_chunks([path])


class ToolTests(unittest.TestCase):
    def test_calculator(self):
        self.assertEqual(calculate('(100 + 25) * 2 / 5'), 50)
        self.assertEqual(calculate('-3 + +2'), -1)

    def test_reject_code_and_excessive_math(self):
        for text in ["__import__('os').system('whoami')", '2 ** 100000', 'True + 1', '1e999', '10' * 80]:
            with self.assertRaises((ValueError, SyntaxError)):
                calculate(text)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            calculate('10 / 0')

    def test_tool_allowlist(self):
        for name, args in [('shell', {'command': 'x'}), ('calculate', {'expression': '2', 'other': 'x'}),
                           ('calculate', {'expression': 2})]:
            with self.assertRaises(ValueError):
                execute_tool(name, args)

    def test_ticket_lookup(self):
        self.assertEqual(execute_tool('lookup_ticket', {'ticket_id': 'T-1001'})['status'], 'In progress')
        self.assertIn('error', execute_tool('lookup_ticket', {'ticket_id': 'T-9999'}))


class CitationTests(unittest.TestCase):
    def setUp(self):
        self.hits = [{'source': 'a.md', 'page': 2, 'text': 'Refunds take 7 days.'}]

    def test_valid_citations(self):
        self.assertTrue(validate_citations('Seven days [1].', self.hits)[0])

    def test_missing_or_invalid_citations(self):
        for answer in ['', 'Seven days.', 'Seven days [0].', 'Seven days [2].']:
            self.assertFalse(validate_citations(answer, self.hits)[0])

    def test_explicit_abstention(self):
        self.assertTrue(validate_citations(NO_EVIDENCE, self.hits)[0])

    def test_prompt_preserves_provenance(self):
        messages = answer_messages('When?', self.hits)
        self.assertIn('untrusted evidence', messages[0]['content'])
        self.assertIn('[1] a.md, page 2', messages[1]['content'])


class InvoiceTests(unittest.TestCase):
    def test_valid_invoice(self):
        data = {'name': 'Asha', 'date': None, 'amount': 12.5, 'currency': 'INR'}
        self.assertEqual(validate_invoice(data), data)

    def test_wrong_fields_or_types(self):
        for data in [{}, {'name': 'Asha', 'date': None, 'amount': True, 'currency': 'INR'},
                     {'name': 2, 'date': None, 'amount': 12, 'currency': 'INR'}]:
            with self.assertRaises(ValueError):
                validate_invoice(data)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.settings = Settings(runtime=Path(self.folder.name), attempts=2)
        self.message = [{'role': 'user', 'content': 'test'}]
        self.result = {'model': 'test-model', 'message': {'role': 'assistant', 'content': 'answer'},
                       'prompt_eval_count': 4, 'eval_count': 2}

    def test_caching_and_usage(self):
        calls = []
        def opener(req, **kwargs):
            calls.append(req)
            return response(self.result)
        client = OllamaClient(self.settings, opener=opener)
        self.assertEqual(client.chat(self.message), client.chat(self.message))
        self.assertEqual(len(calls), 1)
        usage = [json.loads(line) for line in (self.settings.runtime / 'usage.jsonl').read_text().splitlines()]
        self.assertEqual([r['cached'] for r in usage], [False, True])
        self.assertEqual(usage[1]['input_tokens'], 0)

    def test_cache_distinguishes_prompt_and_schema(self):
        calls = []
        def opener(req, **kwargs):
            calls.append(req)
            return response(self.result)
        client = OllamaClient(self.settings, opener=opener)
        client.chat(self.message)
        client.chat(self.message, schema='json')
        client.chat([{'role': 'user', 'content': 'different'}])
        self.assertEqual(len(calls), 3)

    def test_retries_and_backoff(self):
        attempts, sleeps = [], []
        def opener(req, **kwargs):
            attempts.append(1)
            if len(attempts) == 1:
                raise urllib.error.URLError('temporary')
            return response(self.result)
        client = OllamaClient(self.settings, opener=opener, sleeper=sleeps.append)
        client.chat(self.message)
        self.assertEqual(len(attempts), 2)
        self.assertEqual(len(sleeps), 1)

    def test_permanent_http_error_is_not_retried(self):
        attempts = []
        def opener(req, **kwargs):
            attempts.append(1)
            raise urllib.error.HTTPError(req.full_url, 400, 'bad', {}, io.BytesIO(b'bad request'))
        client = OllamaClient(self.settings, opener=opener, sleeper=lambda _: None)
        with self.assertRaises(ModelError):
            client.chat(self.message)
        self.assertEqual(len(attempts), 1)

    def test_embedding_shape_validation(self):
        client = OllamaClient(self.settings, opener=lambda *a, **k: response({'embeddings': []}))
        with self.assertRaises(ModelError):
            client.embed(['hello'])
        with self.assertRaises(ValueError):
            client.embed([''])

    def test_stream_requires_completion_before_cache(self):
        data = b'{"message":{"content":"partial"},"done":false}\n'
        client = OllamaClient(self.settings, opener=lambda *a, **k: io.BytesIO(data))
        with self.assertRaises(ModelError):
            list(client.stream_chat(self.message))
        self.assertFalse(client._cached(client._key({'model': self.settings.chat_model,
            'messages': self.message, 'stream': False, 'options': {'temperature': 0, 'num_ctx': 4096}})))

    def test_stream_collects_chunks(self):
        data = b'{"message":{"content":"hel"},"done":false}\n{"message":{"content":"lo"},"done":true}\n'
        client = OllamaClient(self.settings, opener=lambda *a, **k: io.BytesIO(data))
        self.assertEqual(''.join(client.stream_chat(self.message)), 'hello')


class AgentTests(unittest.TestCase):
    def test_actual_tool_execution_with_simulated_model_protocol(self):
        class ProtocolStub:
            def __init__(self):
                self.calls = 0
            def chat(self, messages, **kwargs):
                self.calls += 1
                if self.calls == 1:
                    return {'message': {'role': 'assistant', 'content': '', 'tool_calls': [
                        {'function': {'name': 'calculate', 'arguments': {'expression': '2 + 3'}}}]}}
                return {'message': {'role': 'assistant', 'content': 'The result is 5.'}}
        agent = SupportAgent(ProtocolStub())
        result = agent.run('Calculate 2 + 3')
        self.assertEqual(result['trace'][0]['observation'], {'result': 5})
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(agent.messages[-2]['role'], 'tool')
        self.assertNotIn('thinking', json.dumps(result))

    def test_agent_step_bound(self):
        class LoopStub:
            def chat(self, *a, **k):
                return {'message': {'role': 'assistant', 'content': '', 'tool_calls': [
                    {'function': {'name': 'lookup_ticket', 'arguments': {'ticket_id': 'T-1001'}}}]}}
        self.assertEqual(SupportAgent(LoopStub(), max_steps=2).run('status')['status'], 'step_limit')


if __name__ == '__main__':
    unittest.main()
