import unittest 

from error_assistant.code_base.code_base import CodeBase


class TestCodeBase(unittest.TestCase):
	def setUp(self):
		code_base = CodeBase()


	def assertCodeBase(self, code_base):
		for code_dict in code_base:
			self.assertIsInstance(code_dict, dict)

			self.assertEqual(list(code_dict.keys()), ['path', 'module', 'file_content'])


	def test_return_type(self):
		code_base = CodeBase()

		#test on a valid path for list[dict[str, str]]
		self.assertCodeBase(code_base.generate_code_base('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/error_assistant_config/'))

		#test on a single file
		self.assertCodeBase(code_base.generate_code_base('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/error_assistant_config/log_config.py'))

		#test on .log, code_base.json, .pyc
		for code in code_base.generate_code_base('/home/tambascomarco35/TravelAssistant/logs.log'):
			self.assertIsNone(code)

		#test to ignore specific directories
		for code in code_base.generate_code_base('/home/tambascomarco35/error-assistant-mk3/src/error_assistant/code_base/__pycache__'):
			self.assertIsNone(code)


	def test_invalid_path(self):
		...


if __name__ == '__main__':
	unittest.main()