import os
import sys
import hashlib
from typing import NewType, Iterable
import logging

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import create_logger
from error_assistant.vector_store.VectorStore import PineconeVectorStore

from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
import pinecone


logger = create_logger(__name__)

config: Config = Config()

Record = NewType('Record', dict[str, str])


class Vectorizer(PineconeVectorStore):
	def __init__(self) -> None:
		PineconeVectorStore.__init__(self)

	def prepare_records(self, file_path: str) -> Iterable[list[Record]]:
		"""
		Analyzes a given file path, from which it generates a Record
		"""
		try:
			if os.path.isfile(file_path):
				with open(file_path, 'r') as f:
					file_ext: str = os.path.splitext(file_path)[-1]
					file_content: str = ''.join(f'line {i}: {line}' for i, line in enumerate(f.readlines()))

				#split the file based on the file extension (langchain.text_splitter.Language)
				for j, chunk_content in enumerate(self.split_file(file_content, file_ext)):

					#create a Record from the given file path
					yield self.create_record(file_path, chunk_content, j)

		except UnicodeDecodeError:
			pass

		except Exception as e:
			print(e)
			raise


	def create_record(self, file_path: str, chunk_content: str, chunk_idx: int) -> list[Record]:
		"""
		Creates a valid Pinecone Record to upsert in the vector_store.
		Args:
			file_path: (str), the file path;
			chunk_content: (str), the content of a given chunk.
			chunk_idx: (int), the idx of the given chunk, part of abigger collection of chunks, to use for VectorStore indexing

		Returns:
			A single Record wrapped in a list, ready to be upserted into the PineconeVectorStore.
		"""
		file_name: str = os.path.basename(file_path)

		record: Record = Record({
						'_id': f'{file_name}:chunk{chunk_idx}',
						'path': os.path.dirname(file_path),
						'module': file_name,
						'chunk_text': chunk_content,
					})

		return [record]


	def split_file(self, file_content: str, file_ext: str) -> list[str]:
		"""
		Splits the file content and returns the content of each chunk.
		Args:
			file_content: (str), the content of the file to chunk;
			file_ext: (str), the file type, used to determine which charatcter splitter to use.
		"""

		file_extensions: dict[str, Language] = {
			'.py': Language.PYTHON,
			'.js': Language.JS,
			'.c': Language.C,
			'.cs': Language.CSHARP,
			'.html': Language.HTML,
			'.md': Language.MARKDOWN,
			'.java': Language.JAVA
		}

		if file_ext in file_extensions:
				language: Language = file_extensions[file_ext]
				splitter = RecursiveCharacterTextSplitter.from_language(
					language=language, 
					chunk_size=500, 
					chunk_overlap=100
				)

		elif file_ext == '.css':
			splitter = RecursiveCharacterTextSplitter(
				separators=['}', '\n'], 
				chunk_size=500, 
				chunk_overlap=100
			)

		else:
			splitter = RecursiveCharacterTextSplitter(
				chunk_size=500, 
				chunk_overlap=100
			)


		return splitter.split_text(file_content)

	def upsert_record(self, record: list[Record]) -> None:
		"""
		Decides if a given record should:
			1. be upserted, if it is a new file, or a modified one,
			2. be skipped, if it already exists,
			3. be updated if the file path and/or file name has changed since last upsert.
		"""
		try:
			self.vector_store.upsert_records(self.namespace, record)  # type: ignore[call-args]

			record_id = record[0]['_id']
			#logger.info(f'Upserting of record {record_id} successfull')

		except pinecone.exceptions.PineconeException as e:
			(f'Error while upserting the record: ')
			raise e

	def delete_records(self, file_path: str) -> None:
		"""
		Deletes all of the documents in the vector-store associated with a specific path file
		"""
		while True:
				response = self.vector_store.search(self.namespace, query={  # type: ignore[call-args] 
						'top_k': 1,
						'filter': {
						'path': os.path.dirname(file_path),
						'module': os.path.basename(file_path)	
						},
					'inputs': {
						'text': file_path,
						},
					})

				if response['result']['hits']:
					for record in response['result']['hits']:

						record_id = record.get('_id')
						record_path = record['fields'].get('path')
						record_module = record['fields'].get('module')

						if os.path.join(record_path, record_module) == file_path:
							self.vector_store.delete(record_id, namespace=self.namespace)

						else:
							#logger.info(f'Removed all of the existing records for {file_path}')
							break

				print(f'{file_path} removed from the vector-store')
				break
