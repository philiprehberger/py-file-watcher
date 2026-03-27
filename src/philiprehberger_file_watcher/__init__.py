"""Filesystem event watcher with decorator-based callbacks."""

from __future__ import annotations

import fnmatch
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Literal

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

__all__ = ["Watcher", "FileEvent"]

EventType = Literal["created", "modified", "deleted", "moved", "any"]


@dataclass
class FileEvent:
    """A filesystem event."""

    type: str
    path: str
    is_directory: bool
    dest_path: str | None = None


class _Handler(FileSystemEventHandler):
    def __init__(self, watcher: Watcher) -> None:
        self._watcher = watcher
        self._debounce_map: dict[str, float] = {}

    def _should_process(self, path: str) -> bool:
        now = time.monotonic()
        debounce = self._watcher._debounce_seconds
        if debounce > 0:
            last = self._debounce_map.get(path, 0)
            if now - last < debounce:
                return False
            self._debounce_map[path] = now
        return True

    def _dispatch(self, event_type: str, event: FileSystemEvent) -> None:
        if not self._should_process(event.src_path):
            return

        file_event = FileEvent(
            type=event_type,
            path=event.src_path,
            is_directory=event.is_directory,
            dest_path=getattr(event, "dest_path", None),
        )

        for pattern, callback in self._watcher._listeners.get(event_type, []):
            if pattern is None or fnmatch.fnmatch(Path(event.src_path).name, pattern):
                callback(file_event)

        for pattern, callback in self._watcher._listeners.get("any", []):
            if pattern is None or fnmatch.fnmatch(Path(event.src_path).name, pattern):
                callback(file_event)

    def on_created(self, event: FileSystemEvent) -> None:
        self._dispatch("created", event)

    def on_modified(self, event: FileSystemEvent) -> None:
        self._dispatch("modified", event)

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._dispatch("deleted", event)

    def on_moved(self, event: FileSystemEvent) -> None:
        self._dispatch("moved", event)


class Watcher:
    """Watch a directory for filesystem changes."""

    def __init__(
        self,
        path: str | Path,
        recursive: bool = True,
        debounce: float = 0.5,
    ) -> None:
        self._path = str(Path(path).resolve())
        self._recursive = recursive
        self._debounce_seconds = debounce
        self._listeners: dict[str, list[tuple[str | None, Callable[[FileEvent], None]]]] = {}
        self._observer: Observer | None = None
        self._running = False

    def on(
        self,
        event_type: EventType,
        pattern: str | None = None,
    ) -> Callable:
        """Decorator to register an event handler.

        Args:
            event_type: Type of event to listen for.
            pattern: Optional glob pattern to filter filenames.
        """
        def decorator(fn: Callable[[FileEvent], None]) -> Callable[[FileEvent], None]:
            self._listeners.setdefault(event_type, []).append((pattern, fn))
            return fn
        return decorator

    def add_listener(
        self,
        event_type: EventType,
        callback: Callable[[FileEvent], None],
        pattern: str | None = None,
    ) -> None:
        """Programmatically add an event listener."""
        self._listeners.setdefault(event_type, []).append((pattern, callback))

    def start(self, background: bool = False) -> None:
        """Start watching.

        Args:
            background: If True, run in a background thread.
        """
        handler = _Handler(self)
        self._observer = Observer()
        self._observer.schedule(handler, self._path, recursive=self._recursive)
        self._observer.start()
        self._running = True

        if not background:
            try:
                while self._running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()

    def stop(self) -> None:
        """Stop watching."""
        self._running = False
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def on_batch(
        self,
        event_type: EventType,
        callback: Callable[[list[FileEvent]], None],
        batch_size: int = 10,
        timeout: float = 2.0,
    ) -> None:
        """Register a batch callback for efficient bulk event processing.

        Collects events matching *event_type* into a buffer and fires
        *callback* with the buffered list when either *batch_size* is reached
        or *timeout* seconds have elapsed since the first buffered event.

        Args:
            event_type: Type of event to listen for.
            callback: Called with a list of collected ``FileEvent`` objects.
            batch_size: Maximum number of events to buffer before flushing.
            timeout: Seconds to wait after the first buffered event before
                flushing regardless of batch size.
        """
        buffer: list[FileEvent] = []
        lock = threading.Lock()
        timer: list[threading.Timer | None] = [None]

        def _flush() -> None:
            with lock:
                if buffer:
                    batch = list(buffer)
                    buffer.clear()
                    if timer[0] is not None:
                        timer[0] = None
                    callback(batch)

        def _on_event(event: FileEvent) -> None:
            with lock:
                buffer.append(event)
                if len(buffer) >= batch_size:
                    if timer[0] is not None:
                        timer[0].cancel()
                        timer[0] = None
                    batch = list(buffer)
                    buffer.clear()
                    callback(batch)
                elif len(buffer) == 1:
                    # First event in a new batch — start timeout
                    t = threading.Timer(timeout, _flush)
                    t.daemon = True
                    timer[0] = t
                    t.start()

        self.add_listener(event_type, _on_event)

    @property
    def is_running(self) -> bool:
        return self._running
