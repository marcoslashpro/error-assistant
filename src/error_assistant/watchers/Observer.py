from error_assistant.watchers.CodeBaseHandler import CodeBaseHandler
from error_assistant.error_assistant_config.config import Config


import time
import pickle
import os

from watchdog.observers import Observer
from watchdog.utils.dirsnapshot import DirectorySnapshot, DirectorySnapshotDiff
from watchdog.events import FileCreatedEvent, FileDeletedEvent, FileMovedEvent, FileModifiedEvent, FileSystemEvent


config: Config = Config()


class CodeWatcher():
	def __init__(self, CodeBaseHandler) -> None:
		self.observer = Observer()
		self.handler = CodeBaseHandler()
		self.path = config.config['paths']['code_base_path']

		self.snapshot_path = config.config['paths']['snapshot_path']
		assert self.snapshot_path.endswith('.p'), f'The snapshot path must lead to a pickle file, got {os.splitext(self.snapshot_path)[-1]}'


	def setup(self) -> None:
		self.start_observer()
		self.checkpoint = self.open_snapshot()
		self.new_snapshot = self.take_snapshot()

		if self.checkpoint:			
			snap_diff = DirectorySnapshotDiff(self.checkpoint, self.new_snapshot)
			self.update_vectorStore(snap_diff)
			return			

		#if we don't have a checkpoint, we'll just upload the entirety of the new snapshot
		for path in self.new_snapshot.paths:
			for record in self.handler.prepare_records(path):
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
		Saves the DirectorySnapshot into a .pkl file
		'''
		pickle.dump(snapshot, open( self.snapshot_path, 'wb' ))


	def open_snapshot(self) -> None:
		if os.path.exists(self.snapshot_path):
			dirSnapshot: DirectorySnapshot = pickle.load(open( self.snapshot_path, "rb" ))
			return dirSnapshot


	def update_vectorStore(self, directoryDiff: DirectorySnapshotDiff) -> None:
		'''
		Given the difference between an old directory and a new one,
		We upsert into the vectorStore via the Handler.
		'''	
		event_map: dict[str, FileSystemEvent] = {
			'files_created': {'event': FileCreatedEvent, 'method': self.handler.on_created},
			'files_modified': {'event': FileModifiedEvent, 'method': self.handler.on_modified},
			'files_moved': {'event': FileMovedEvent, 'method': self.handler.on_moved},
			'files_deleted': {'event': FileDeletedEvent, 'method': self.handler.on_deleted}
		}

		try:
			for event in event_map:
				#extract it
				diff: list[str] = getattr(directoryDiff, event)
				#check if it has something inside
				if diff:
					#if it does, we create that specific FileSystemEvent
					for d in diff:
						file_event: FileSystemEvent = event_map[event]['event']
						diffEvent = file_event(d)
						#we then execute the specific handler method
						handler_method = event_map[event]['method']
						handler_method(diffEvent)

		except Exception as e:
			pass