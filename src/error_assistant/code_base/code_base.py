import json
import os
import sys
from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import log_config
import logging


#Config setup
config = Config()
logger = logging.getLogger(__name__)
log_config(logger)


class CodeBase:
    def __init__(self):
        self.path: str = config.config['paths']['code_base_path']
        if not self.path:
            raise ValueError('Must provide a file path for the code base in the config file')


    def generate_code_base(self, path: str | None = None) -> list[dict[str, str]]:
        path: str = path if path else self.path

        self.directories_to_ignore: list[str] = config.config['paths']['ignores']['directories']


        if not os.path.exists(path):
            raise FileNotFoundError(f'The provided path "{path}" is not found in the system')

        # Case 1: If the path is a file, read and return its contents
        if os.path.isfile(path):
            yield self.read_file(path)

        # Case 2: If the path is a directory, walk through it and process files
        for root, dirs, files in os.walk(path):

            # Ignore specified directories
            if any(folder in root.split(os.sep) for folder in self.directories_to_ignore):
                continue

            for file in files:
                file_path: str = os.path.join(root, file)

                yield self.read_file(file_path)


    def read_file(self, file_path: str) -> str:
        """
        From a given file path it extracts the file path, module, and file content.
        Args:
            file_path, (string), the absoulute path of the file to read.
        Returns:
            file, (dict[str, str]), a dictionaty mapping:
                'path': the file path,
                'module': the file name,
                'file_content': a string representing, (line number: line content)
        """
        self.files_to_ignore: list[str] = config.config['paths']['ignores']['files']
        

        if os.path.splitext(file_path)[-1] not in self.files_to_ignore:

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.readlines()

                    return {
                        'path': os.path.dirname(file_path),
                        'module': os.path.basename(file_path),
                        'file_content': ''.join(f'line {i}: {line}' for i, line in enumerate(source_code))
                    }

            except FileNotFoundError:
                pass

            except UnicodeDecodeError:
                print(f'The given file {file_path} cannot be read with encoding utf-8')
                raise  


    def save_to_file(self) -> None:
        self.output_code_base_path: str = config.get('paths', 'output_code_base_path')
        self.code_base = [f for f in self.generate_code_base()]

        if not self.output_code_base_path:
            raise FileNotFoundError('Please provide an output path for the code base in the config file')

        elif not self.output_code_base_path.endswith('.json'):
            raise ValueError('The provided file for the output must be a .json file')

        with open(self.output_code_base_path, 'w', encoding='utf-8') as f:
            json.dump(self.code_base, f, indent=4)