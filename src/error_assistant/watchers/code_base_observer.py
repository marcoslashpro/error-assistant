import watchdog as wd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time

from error_assistant.error_assistant_config.config import Config

config: Config = Config()


class CodeBaseHandler(FileSystemEventHandler):
    def __init__(self, vectorizer) -> None:
        """Initialize separate Vectorizer instance and track last upsert times."""
        self.vectorizer = vectorizer  # Use the vectorizer passed during initialization
        self.last_upsert = {}  # Track last upsert time for each file

    def upsert_event(self, event_path: str) -> None:
        """Avoid redundant upserts within a short time window (e.g., 2 sec)."""
        now = time.time()

        # Skip if it was upserted recently
        if event_path in self.last_upsert and now - self.last_upsert[event_path] < 2:
            return  # Skip event if upserted recently

        self.last_upsert[event_path] = now  # Update timestamp
        
        # Skip .swp and .git files
        if not event_path.endswith('.swp') and not event_path.endswith('.git'):
            print(f'Processing file: {event_path}')
            self.vectorizer.prepare_code_records(event_path)

    def on_created(self, event: FileSystemEvent) -> None:
        """Handles new file creation events."""
        if not event.is_directory:
            print(f'New file created: {event.src_path}')
            self.upsert_event(event.src_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handles file modifications (avoids duplicates)."""
        if not event.is_directory:
            print(f'File modified: {event.src_path}')
            self.upsert_event(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        """Handles file renames/moves."""
        if not event.is_directory:
            print(f'File moved from {event.src_path} to {event.dest_path}')
            self.upsert_event(event.dest_path)