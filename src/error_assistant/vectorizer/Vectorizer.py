import json
import os
import sys
import hashlib
import re
from typing import *

from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config
from error_assistant.code_base.code_base import CodeBase
from error_assistant.vector_store.VectorStore import PineconeVectorStore

from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
import pinecone

import logging

logger = logging.getLogger(__name__)
log_config(logger)

config: Config = Config()


class Vectorizer(CodeBase, PineconeVectorStore):
    def __init__(self) -> None:
        CodeBase.__init__(self)
        PineconeVectorStore.__init__(self)


    def prepare_code_records(self, path: str | None = None) -> list[dict[str, str]]:
        path = path if path else self.path
        
        code_records: list[dict[str, str]] = []
        
        # Map file extensions to corresponding languages
        file_extensions: dict[str, Language] = {
            '.py': Language.PYTHON,
            '.js': Language.JS,
            '.html': Language.HTML
        }

        for n, code in enumerate(self.generate_code_base(path)):
            file_ext: str = os.path.splitext(code.get('module'))[-1]
            file_content: str = code.get('file_content')
            module = code.get('module')

            # Choose text splitter based on file type
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

            splitted_file_content: list[str] = splitter.split_text(file_content)

            for j, split in enumerate(splitted_file_content):
                chunk_id = f'{code.get("module")}:chunk{j+1}'
                chunk_hash = hashlib.md5(split.encode()).hexdigest()
                chunk_path = code.get('path')

                # Fetch existing chunks to avoid unnecessary upserts
                existing_chunks = self.fetch_existing_records(code.get('module'))

                existing_chunk = existing_chunks.get(chunk_id)
                if existing_chunk:
                    # If the hash or the path has changed, we need to update the record
                    if existing_chunk['hash'] != chunk_hash or existing_chunk['path'] != chunk_path:
                        print(f"Updating chunk {chunk_id} due to content or path change")

                    else: 
                        print(f'Records for {chunk_id} already in the vector store')
                        continue  # No need to update

                # Otherwise, update or insert
                new_record = {
                    '_id': f'{code.get("module")}:chunk{j+1}',
                    'chunk_text': split,
                    'path': code.get('path'),
                    'module': code.get('module'),
                    'hash': chunk_hash
                }

                code_records.append(new_record)
                self.upsert_record([new_record])

        return code_records

    def upsert_record(self, record: list[dict[str, str]]) -> None:
        try:
            self.vector_store.upsert_records(self.namespace, record)
            record_id = record[0]['_id']
            logger.info(f'Upserting of record {record_id} successfull')
        except pinecone.exceptions.PineconeException as e:
            print('Error while upserting the records:')
            raise

    def update_records(self) -> None:
        pass

    def fetch_existing_records(self, module: str) -> dict[str, str]:
        """
        Fetch existing records for a given module from Pinecone.
        Returns a dictionary mapping chunk IDs to their hashes and paths.
        """
        existing_chunks = {}

        try:
            # Query Pinecone to fetch records for this module
            response = self.vector_store.search(self.namespace, query={
                    'top_k': 1,
                    'filter': {'module': module},
                    'inputs': {
                        'text': module,
                        },                
                    })


            if response['result']['hits']:
                for record in response['result']['hits']:
                    chunk_id = record.get('_id')
                    chunk_hash = record['fields'].get('hash')
                    chunk_path = record['fields'].get('path')

                    if chunk_id and chunk_hash:
                        existing_chunks[chunk_id] = record['fields']
            else:
                print(f"No records found for module: {module}")

        except Exception as e:
            print(f"Error fetching existing records for module {module}: {str(e)}")

        return existing_chunks