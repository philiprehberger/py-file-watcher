# philiprehberger-file-watcher

[![Tests](https://github.com/philiprehberger/py-file-watcher/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-file-watcher/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-file-watcher.svg)](https://pypi.org/project/philiprehberger-file-watcher/)
[![License](https://img.shields.io/github/license/philiprehberger/py-file-watcher)](LICENSE)
[![Sponsor](https://img.shields.io/badge/sponsor-GitHub%20Sponsors-ec6cb9)](https://github.com/sponsors/philiprehberger)

Filesystem event watcher with decorator-based callbacks.

## Installation

```bash
pip install philiprehberger-file-watcher
```

## Usage

```python
from philiprehberger_file_watcher import Watcher

watcher = Watcher("./src")

@watcher.on("created", pattern="*.py")
def on_new_python_file(event):
    print(f"New file: {event.path}")

@watcher.on("modified", pattern="*.css")
def on_css_change(event):
    print(f"CSS changed: {event.path}")

@watcher.on("any")
def on_anything(event):
    print(f"{event.type}: {event.path}")

# Blocking
watcher.start()

# Or background mode
watcher.start(background=True)
# ... do other work ...
watcher.stop()
```

## Event Types

`"created"`, `"modified"`, `"deleted"`, `"moved"`, `"any"`

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `recursive` | True | Watch subdirectories |
| `debounce` | 0.5 | Debounce interval in seconds |


## API

| Function / Class | Description |
|------------------|-------------|
| `Watcher(path, recursive, debounce)` | Watch a directory for filesystem changes with decorator-based event handlers |
| `FileEvent` | A filesystem event with `type`, `path`, `is_directory`, and `dest_path` fields |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## License

MIT
