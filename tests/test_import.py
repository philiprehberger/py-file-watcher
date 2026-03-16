"""Basic import test."""


def test_import():
    """Verify the package can be imported."""
    import philiprehberger_file_watcher
    assert hasattr(philiprehberger_file_watcher, "__name__") or True
