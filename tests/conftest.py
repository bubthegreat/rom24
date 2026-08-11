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
