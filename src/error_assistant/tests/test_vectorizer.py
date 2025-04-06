import unittest

from error_assistant.vectorizer.Vectorizer import Vectorizer
from error_assistant.vector_store.Retriever import Retriever


class TestVectorizer(unittest.TestCase):
	def test_fetch_existing_records(self):
		vectorizer = Vectorizer()

		existing_chunk = vectorizer.vector_store.search(vectorizer.namespace, query={
                    'top_k': 1,
                    'filter': {'module': 'log_config.py'},
                    'inputs': {
                        'text': 'log_config.py:chunk1',
                        },                
                    })


		self.assertEqual(vectorizer.fetch_existing_records('log_config.py:chunk1'), existing_chunk)




if __name__ == '__main__':
	unittest.main()