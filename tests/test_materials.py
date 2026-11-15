import json
import unittest
from internship.config import ROOT
from internship.documents import load_chunks


class MaterialTests(unittest.TestCase):
    def test_sample_corpus_is_readable_and_explicitly_fictional(self):
        files = sorted((ROOT / 'data/sample_docs').glob('*.md'))
        self.assertEqual(len(files), 12)
        self.assertTrue(all('Fictional training example.' in p.read_text(encoding='utf-8') for p in files))
        chunks = load_chunks(files)
        self.assertEqual(len({c.source for c in chunks}), 12)

    def test_evaluation_cases_have_existing_source_documents(self):
        cases = json.loads((ROOT / 'data/evaluation_cases.json').read_text())
        self.assertEqual(len(cases), 10)
        self.assertEqual(sum(c['source'] is None for c in cases), 2)
        for case in cases:
            if case['source']:
                self.assertTrue((ROOT / 'data/sample_docs' / case['source']).is_file())

    def test_weekly_entrypoints_and_required_delivery_documents_exist(self):
        from internship.exercises import WEEKS
        for folder in WEEKS.values():
            self.assertTrue((ROOT / folder / 'run.py').is_file())
            self.assertTrue((ROOT / folder / 'README.md').is_file())
        for filename in ['Dockerfile', 'compose.yaml', 'LOG.md', 'MY_PROGRESS.md',
                         'week8_hardened/CAPSTONE_PROPOSAL.md', 'week7_finetuning/COMPARISON_ANALYSIS.md',
                         'capstone/TESTS.md', 'capstone/DEPLOYMENT.md', 'capstone/PRESENTATION_OUTLINE.md']:
            self.assertTrue((ROOT / filename).is_file(), filename)
