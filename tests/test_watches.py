"""Tests for unwatch() and watched_paths()."""

from pathlib import Path

from philiprehberger_file_watcher import Watcher


def test_watched_paths_empty_before_start(tmp_path: Path) -> None:
    """A Watcher that has not been started reports no watched paths."""
    watcher = Watcher(str(tmp_path))
    assert watcher.watched_paths() == []


def test_watched_paths_populated_after_start(tmp_path: Path) -> None:
    """After start(), the resolved path appears in watched_paths()."""
    watcher = Watcher(str(tmp_path))
    watcher.start(background=True)
    try:
        resolved = str(Path(tmp_path).resolve())
        assert resolved in watcher.watched_paths()
    finally:
        watcher.stop()


def test_unwatch_removes_path(tmp_path: Path) -> None:
    """unwatch() returns True and removes the path from watched_paths()."""
    watcher = Watcher(str(tmp_path))
    watcher.start(background=True)
    try:
        resolved = str(Path(tmp_path).resolve())
        assert resolved in watcher.watched_paths()
        assert watcher.unwatch(str(tmp_path)) is True
        assert resolved not in watcher.watched_paths()
    finally:
        watcher.stop()


def test_unwatch_unknown_path_returns_false(tmp_path: Path) -> None:
    """unwatch() returns False for a path that is not being watched."""
    watcher = Watcher(str(tmp_path))
    watcher.start(background=True)
    try:
        assert watcher.unwatch("/nonexistent/path/that/is/not/watched") is False
    finally:
        watcher.stop()


def test_unwatch_before_start_returns_false(tmp_path: Path) -> None:
    """unwatch() returns False when no watches are registered yet."""
    watcher = Watcher(str(tmp_path))
    assert watcher.unwatch(str(tmp_path)) is False
