"""Command-lookup fixtures for the tests/ suite.

The session-scoped ``booted_world`` fixture these depend on is defined in the
repo-root ``conftest.py`` so it is shared with the per-area tests too (the world
boots exactly once per session — ``boot_db`` is not idempotent).
"""
import pytest


@pytest.fixture
def command(booted_world):
    """Look up a command's function by its registered name.

    Commands live in packs/core and are loaded by file path, so they are not
    importable as ``rom24.commands.<name>``. They register into
    ``interp.cmd_table`` by name, which is how tests reach them.
    """
    from rom24 import interp

    return lambda name: interp.cmd_table[name].do_fun


@pytest.fixture
def command_source(booted_world):
    """Return the full source file text of a command (for marker regression checks)."""
    import inspect
    from rom24 import interp

    def _get(name):
        fn = interp.cmd_table[name].do_fun
        with open(inspect.getsourcefile(fn)) as fp:
            return fp.read()

    return _get
