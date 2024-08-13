# philiprehberger-file-watcher

[![Tests](https://github.com/philiprehberger/py-file-watcher/actions/workflows/publish.yml/badge.svg)](https://github.com/philiprehberger/py-file-watcher/actions/workflows/publish.yml)
[![PyPI version](https://img.shields.io/pypi/v/philiprehberger-file-watcher.svg)](https://pypi.org/project/philiprehberger-file-watcher/)
[![Last updated](https://img.shields.io/github/last-commit/philiprehberger/py-file-watcher)](https://github.com/philiprehberger/py-file-watcher/commits/main)

Filesystem event watcher with decorator-based callbacks.

## Installation

```bash
pip install philiprehberger-file-watcher
```

## Usage

### Basic Watching

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

### Batch Event Collection

```python
watcher = Watcher("./uploads")

def handle_batch(events):
    print(f"Received {len(events)} files at once")
    for event in events:
        print(f"  {event.path}")

# Fire callback when 50 events collected or after 3 seconds
watcher.on_batch("created", handle_batch, batch_size=50, timeout=3.0)

watcher.start(background=True)
```

### Event Types

`"created"`, `"modified"`, `"deleted"`, `"moved"`, `"any"`

## API

| Function / Class | Description |
|------------------|-------------|
| `Watcher(path, recursive, debounce)` | Watch a directory for filesystem changes with decorator-based event handlers |
| `FileEvent` | A filesystem event with `type`, `path`, `is_directory`, and `dest_path` fields |
| `Watcher.on(event_type, pattern)` | Decorator to register a single-event callback |
| `Watcher.add_listener(event_type, callback, pattern)` | Programmatically add an event listener |
| `Watcher.on_batch(event_type, callback, batch_size, timeout)` | Register a batch callback that fires on size or timeout |
| `Watcher.start(background)` | Start watching (blocking or background) |
| `Watcher.stop()` | Stop watching |

## Development

```bash
pip install -e .
python -m pytest tests/ -v
```

## Support

If you find this project useful:

⭐ [Star the repo](https://github.com/philiprehberger/py-file-watcher)

🐛 [Report issues](https://github.com/philiprehberger/py-file-watcher/issues?q=is%3Aissue+is%3Aopen+label%3Abug)

💡 [Suggest features](https://github.com/philiprehberger/py-file-watcher/issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)

❤️ [Sponsor development](https://github.com/sponsors/philiprehberger)

🌐 [All Open Source Projects](https://philiprehberger.com/open-source-packages)

💻 [GitHub Profile](https://github.com/philiprehberger)

🔗 [LinkedIn Profile](https://www.linkedin.com/in/philiprehberger)

## License

[MIT](LICENSE)
