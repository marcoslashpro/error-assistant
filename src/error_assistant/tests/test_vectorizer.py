import unittest
from timeit import timeit

from error_assistant.vectorizer.Vectorizer import Vectorizer
from error_assistant.vector_store.Retriever import Retriever
from error_assistant.vectorizer.NewVectorizer import NewVectorizer


class TestVectorizer(unittest.TestCase):
	def test_new_vectorizer(self) -> None:
		self.maxDiff = None

		vector = Vectorizer()
		new_vect = NewVectorizer()

		self.assertEqual(
			[v for v in vector.prepare_code_records('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/tests/test_code_base.py')],
			[v for v in new_vect.prepare_records('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/tests/test_code_base.py')]
			)

		timeit(vector.prepare_code_records('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/tests/test_code_base.py'))
		timeit(new_vect.prepare_records('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/tests/test_code_base.py'))



if __name__ == '__main__':
	unittest.main()