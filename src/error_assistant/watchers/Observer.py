from error_assistant.watchers.CodeBaseHandler import CodeBaseHandler
from error_assistant.error_assistant_config.config import Config
from error_assistant.error_assistant_config.log_config import create_logger

import time
import pickle
import os

from watchdog.observers import Observer
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent


config: Config = Config()
logger = create_logger(__name__)


class CodeWatcher():
	def __init__(self, CodeBaseHandler) -> None:
		self.observer = Observer()
		self.handler = CodeBaseHandler()
		self.path = config.config['paths']['code_base_path']

		self.snapshot_path = config.config['paths']['snapshot_path']
		assert self.snapshot_path.endswith('.p'), f'The snapshot path must lead to a pickle file, got {os.path.splitext(self.snapshot_path)[-1]}'

	def setup(self) -> None:
		self.start_observer()
		self.checkpoint = self.open_snapshot()
		self.new_snapshot = self.take_snapshot()

		if self.checkpoint:
			snap_diff = DirectorySnapshotDiff(self.checkpoint, self.new_snapshot)
			self.update_vector_store(snap_diff)
			return

		#if we don't have a checkpoint, we'll just upload the entirety of the new snapshot
		for path in self.new_snapshot.paths:
			if not self.handler.ignores(path) and os.path.splitext(path)[-1] in self.handler.files_to_observe:
				for record in self.handler.prepare_records(path):
					logger.info(f'Upserting {path} into vectorstore')
					self.handler.upsert_record(record)

	def close(self) -> None:
		#take a new snapshot of the directory
		new_snapshot = self.take_snapshot()

		#save it to file
		self.save_snapshot(new_snapshot)

		#stop and join the observer
		self.stop_observer()

	def start_observer(self) -> None:
		self.observer.schedule(self.handler, self.path, recursive=True)
		self.observer.start()
		print(f'Observer started...')

	def stop_observer(self) -> None:
		self.observer.stop()
		self.observer.join()
		print('Observer stopped.')

	def take_snapshot(self) -> DirectorySnapshot:
		'''
		Takes a snapshot of the observed directory and saves it.
		'''
		snapshot: DirectorySnapshot = DirectorySnapshot(self.path)
		return snapshot #save the snapshot

	def save_snapshot(self, snapshot) -> None:
		'''
		Saves the DirectorySnapshot into a .p file
		'''
		pickle.dump(snapshot, open( self.snapshot_path, 'wb' ))

	def open_snapshot(self) -> DirectorySnapshot | None:
		if os.path.exists(self.snapshot_path):
			dirSnapshot: DirectorySnapshot = pickle.load(open( self.snapshot_path, "rb" ))
			return dirSnapshot

	def update_vector_store(self, diff: DirectorySnapshotDiff) -> None:
			"""
			Given a DirectorySnapshotDiff, calls the appropriate handler method
			(on_created, on_modified, etc.) for each changed file.
			"""
			event_handlers = [
					(diff.files_created, FileCreatedEvent, self.handler.on_created),
					(diff.files_modified, FileModifiedEvent, self.handler.on_modified),
					(diff.files_moved, FileMovedEvent, self.handler.on_moved),
					(diff.files_deleted, FileDeletedEvent, self.handler.on_deleted),
			]

			for paths, event_cls, handler in event_handlers:
					for path in paths:
							try:
									event = event_cls(path)
									handler(event)
							except Exception as e:
									print(f"Failed to process {event_cls.__name__} for path {path}: {e}")
