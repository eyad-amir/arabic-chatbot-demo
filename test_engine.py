import json
import tempfile
import unittest
from pathlib import Path
from engine import answer_from_knowledge_base, load_knowledge_base, normalize_arabic, FALLBACK_MESSAGE

class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.entries = load_knowledge_base(Path(__file__).with_name('knowledge_base.json'))['knowledge_base']

    def test_every_faq_and_alternative(self):
        for entry in self.entries:
            for question in entry['question'].split('/'):
                with self.subTest(question=question):
                    self.assertEqual(answer_from_knowledge_base(question, self.entries), entry['answer'])

    def test_unknown_and_generic_queries(self):
        for query in ['', '؟', 'هل', 'ما هي', 'هل تبيعون سيارات', 'ما هي أسعار السيارات', 'كم سعر تذكرة الطيران', 'هل يوجد توصيل إلى القمر']:
            with self.subTest(query=query):
                self.assertEqual(answer_from_knowledge_base(query, self.entries), FALLBACK_MESSAGE)

    def test_normalization(self):
        self.assertEqual(normalize_arabic('أَهْلاً!'), 'اهلا')

    def test_malformed_knowledge_base(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            path = Path(directory) / 'data.json'
            path.write_text('{"knowledge_base": []}', encoding='utf-8')
            with self.assertRaises(ValueError):
                load_knowledge_base(path)

if __name__ == '__main__':
    unittest.main()
