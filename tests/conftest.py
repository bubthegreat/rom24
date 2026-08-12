"""Shared pytest fixtures for the rom24 test suite.

``boot_db`` is not idempotent: a second call collides on instance ids still
present in ``instance.global_instances`` from a prior boot (``instancer`` raises
"instance number already in global instances"). So the whole world is booted
exactly once per test session here, and every test that needs it requests the
session-scoped ``booted_world`` fixture instead of booting on its own.

``init_monitoring`` loads every command and spell module, which is what binds
the ``do_*`` methods onto ``Living`` (see ``interp.cmd_type``). The live server
does this in ``pyom()`` before the game loop, so tests must too or mob combat
(``fight.mob_hit`` calls ``ch.do_bash`` etc.) fails.
"""
import random

import pytest


@pytest.fixture(scope="session")
def booted_world():
    """Boot the ROM database exactly once for the entire test session."""
    from rom24 import db
    from rom24.hotfix import init_monitoring

    random.seed(1234)
    init_monitoring()
    db.boot_db()
    return db


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
