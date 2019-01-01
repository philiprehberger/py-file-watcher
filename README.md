# philiprehberger-file-watcher

Filesystem event watcher with decorator-based callbacks.

## Install

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

## License

MIT
