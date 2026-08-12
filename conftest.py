"""Repo-root pytest config: one world boot shared across every test tree.

``boot_db`` is not idempotent (a second call collides on instance ids from the
first), so the world must boot exactly once per session. This fixture lives at
the repo root — not under ``tests/`` — so the ``tests/`` suite and the per-area
tests under ``src/areas/<name>/tests/`` share the single boot instead of each
trying to boot their own. It also puts the gameplay helpers on ``sys.path`` so
area tests can ``from helpers import ...`` the same way the gameplay suite does.
"""
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "tests", "gameplay"))


@pytest.fixture(scope="session")
def booted_world():
    """Boot the ROM database exactly once for the entire test session.

    ``init_monitoring`` loads every command and spell module, binding the
    ``do_*`` methods onto ``Living`` (see ``interp.cmd_type``) — the live server
    does this in ``pyom()`` before the game loop, so tests must too.
    """
    from rom24 import db
    from rom24.hotfix import init_monitoring

    random.seed(1234)
    init_monitoring()
    db.boot_db()
    return db
