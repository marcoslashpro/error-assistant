import os
from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config

import pinecone
import sys


config = Config()


class PineconeVectorStore:
	def __init__(self) -> None:
		self.api_key: str = config.get('pinecone', 'api_key')
		assert self.api_key, 'To use the Pinecone VectorStore, you must provide an api_key'
		self._pc: pinecone.Pinecone = pinecone.Pinecone(api_key=self.api_key)

		self.index_name: str = config.get('pinecone', 'code-index_name', default='base-index')

		self.namespace: str = config.config['pinecone']['code_namespace']['name']

		self.hosting_cloud: str = config.get('pinecone', 'hosting-cloud', default='aws')

		self.hosting_region: str = config.get('pinecone', 'hosting-region', default='us-east-1')


		self.vector_store: pinecone.data.index.Index = self.access_vector_store()


	def access_vector_store(self) -> pinecone.data.index.Index:
		if not self._pc.has_index(self.index_name):
			self.create_vector_store()

		try:
			vector_store: pinecone.data.index.Index = self._pc.Index(self.index_name)
			return vector_store
		except pinecone.exceptions.PineconeException as e:
			print(f'Something went wrong while accessing the vector store:')
			raise


	def create_vector_store(self):
		self.embedding_model: str = config.get('pinecone', 'embedding-model', default='llama-text-embed-v2')

		try:
			vector_store: pinecone.data.index.Index = self._pc.create_index_for_model(
					name=self.index_name,
					cloud=self.hosting_cloud,
					region=self.hosting_region,
					embed={
						'model': self.embedding_model,
						'field_map': {'text': 'chunk_text'}
					}
				)
			return vector_store
		except pinecone.exceptions.PineconeException as e:
			print('Error while creating the vector store: ')
			raise