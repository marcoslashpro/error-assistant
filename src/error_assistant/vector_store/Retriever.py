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
    description = 'Using semantic search, it retrieves other-wise un-accessible content from the VectorStore, which could be useful for solving the problem at hand.'
    inputs = {
        'query': {
            'type': 'string',
            'description': 'The query, in affirmative voice, used to find information inside of the VectorStore.'
        },
        'filtering_field': {
            'type': 'string',
            'nullable': True,
            'description': 'This is an optional field, and it can be used to describe the field to use in roder to filter the response from the vector store. Valid fields include: (\'timestamp\', \'module\', \'line\', to be used for log-namespace filtering) and (\'path\', \'module\', to be used for code-namespace filtering.)'
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