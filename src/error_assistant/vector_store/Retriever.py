from typing import *
import os 
import logging

from smolagents import Tool
import pinecone

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config
from error_assistant.vector_store.VectorStore import PineconeVectorStore


logger = logging.getLogger(__name__)
log_config(logger)

config: Config = Config()


class Retriever(PineconeVectorStore, Tool):
    name = 'retriever'
    description = '''
Accesses a VectorStore of code snippets using semantic search.
This tool retrieves otherwise un-accessible parts of the code.
Use it to get relevant source code using error metadata (such as module and line).
Queries should be in affirmative voice, e.g.:
"Get the code in module auth.views around line 56."
'''
    inputs = {
        'query': {
            'type': 'string',
            'description': "Use 'path', 'module', or 'line' for narrowing down your search."
        },
        'filtering_field': {
            'type': 'string',
            'nullable': True,
            'description': "Use 'path', 'module', or 'line' for narrowing down your search."
        }
    }
    output_type = 'string'

    def __init__(self) -> None:
        Tool.__init__(self)
        PineconeVectorStore.__init__(self)


    def forward(self, query: str, filtering_field: Optional[str] = None) -> str:
        self.top_k: int = config.config['pinecone']['code_namespace']['top-k']

        try:
            if filtering_field:
                results = self.vector_store.search(
                    namespace=self.namespace,
                    query={
                        "inputs": {
                            'text': query,
                            'filter': {'category': filtering_field}
                        },
                        "top_k": self.top_k
                    }
                )
            else:
                results = self.vector_store.search(
                    namespace=self.namespace,
                    query={
                        "inputs": {
                            'text': query,
                        },
                        "top_k": self.top_k
                    }
                )

            response = []
            for hit in results['result']['hits']:
                response.append(
                    {
                        'id': hit['_id'],
                        'answer': hit['fields'],
                        'score': round(hit['_score'], 2)
                    }
                )
            return "\nRetrieved documents:\n" + "".join(
                [
                    f"\n\n===== Document {str(i)} =====\n" + ''.join([f"\n{k}: {v}\n" for k, v in res['answer'].items()])
                    for i, res in enumerate(response)
                ]
            )

        except pinecone.exceptions.PineconeException as e:
            print("Error during search:")
            raise