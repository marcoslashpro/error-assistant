import watchdog as wd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time
import os
import pickle
import re

from langchain_text_splitters import Language
from watchdog.observers import Observer
from watchdog.utils.dirsnapshot import DirectorySnapshot
import pathspec

from error_assistant.error_assistant_config.config import Config
from error_assistant.vectorizer.Vectorizer import Vectorizer


config: Config = Config()


class CodeBaseHandler(FileSystemEventHandler, Vectorizer):
	def __init__(self) -> None:
		FileSystemEventHandler.__init__(self)
		Vectorizer.__init__(self)

		self.gitignore_path: str = config.config['paths']['gitignore_path']
		assert self.gitignore_path, f'Please provide a .gitignore file path in the config file'

		if not os.path.exists(self.gitignore_path):
			raise FileNotFoundError(f'Please provide a valid path for the .gitignore file, got {self.gitignore_path}')

		self.files_to_observe: str = config.config['observer']['files_to_observe']
		self.ignore_pattern = self.setup_ignore_patterns()


	def on_created(self, event):
		if not event.is_directory:
			if not self.ignores(event.src_path) and event.src_path in self.files_to_observe:

				for record in self.prepare_records(event.src_path):
					self.upsert_record(record)
					print(f'{event.src_path} created in the vector-store')



	def on_modified(self, event):
		if not event.is_directory:
			if not self.ignores(event.src_path) and event.src_path in self.files_to_observe:

				for record in self.prepare_records(event.src_path):
					self.upsert_record(record)
					print(f'{event.src_path} modified in the vector-store')


	def on_moved(self, event):
		if not event.is_directory:
			if not self.ignores(event.src_path) and event.src_path in self.files_to_observe:
					
				#if the file name has been changed, we have to delete the old records before upserting the new
				if not os.path.basename(event.src_path) == os.path.basename(event.dest_path):
					self.delete_records(event.src_path)

				for record in self.prepare_records(event.dest_path):
					self.upsert_record(record)
					print(f'{event.src_path} is now {event.dest_path} in the vector store')



	def on_deleted(self, event):
		if not event.is_directory:
			if not self.is_ignored(event.src_path) and event.src_path in self.files_to_observe:

				self.delete_records(event.src_path)


	def setup_ignore_patterns(self):
		with open(self.gitignore_path, 'r') as f:
		    spec = pathspec.GitIgnoreSpec.from_lines(f.read().splitlines())
		    
		return spec


	def ignores(self, file_path: str) -> bool:
		return self.ignore_pattern.match_file(file_path)