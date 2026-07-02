"""Phase 2 Task 5 acceptance test: boot_db() boots KBK end-to-end."""
import logging
import os
import types

import pytest

from rom24 import const, db, instance, merc, settings


def test_boot_db_boots_kbk(clear_instance):
    db.boot_db()
    assert len(const.guild_table) == 13
    assert len(instance.area_templates) >= 85
    assert merc.ROOM_VNUM_SCHOOL in instance.room_templates
    # school room must be instanced (creation drops new chars there)
    assert instance.instances_by_room.get(merc.ROOM_VNUM_SCHOOL)
    # world persistence: nothing written outside players/ + instance counter
    assert not os.path.exists(os.path.join(settings.SOURCE_DIR, "data", "world", "areas"))


def test_boot_db_warns_on_unknown_spec_funs(clear_instance, caplog):
    """boot_db must warn (not crash) when KBK areas use unimplemented spec functions.

    KBK areas reference many spec_ functions not yet implemented in special.py
    (e.g. spec_flurry, spec_monk, spec_rager…).  Before the object_creator fix,
    create_mobile crashed with KeyError on the first unknown spec_fun encountered
    during area_update.  Now it logs a WARNING per unknown spec and continues.
    """
    with caplog.at_level(logging.WARNING, logger="rom24.object_creator"):
        db.boot_db()

    warnings = [
        r.getMessage()
        for r in caplog.records
        if r.levelname == "WARNING" and "unknown spec_fun" in r.getMessage()
    ]
    # KBK areas include spec_flurry and many others not in special.spec_table;
    # at least one warning must have been emitted.
    assert len(warnings) > 0, "expected WARNING(s) for unknown spec_fun, got none"
