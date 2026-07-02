"""Phase 2 acceptance test: rom24 boots and plays as KBK.

Asserts that every major KBK table, world-size, and file-layout constraint
is satisfied by a full boot_db() run.
"""
import glob
import os

import pytest

from rom24 import const, db, instance, settings


def test_kbk_is_the_game(clear_instance):
    db.boot_db()

    # --- class table is KBK (13 guilds, exact names) -------------------------
    assert set(const.guild_table) == {
        "warrior", "thief", "zealot", "paladin", "anti-paladin", "ranger", "druid",
        "channeler", "assassin", "necromancer", "elementalist", "bard", "healer",
    }

    # --- race / skill / group sizes ------------------------------------------
    assert len(const.pc_race_table) == 23
    assert len(const.skill_table) == 636
    assert len(const.group_table) == 35

    # --- world loaded (area templates count) ---------------------------------
    assert len(instance.area_templates) >= 85

    # --- no JSON tables remain on disk ---------------------------------------
    assert not glob.glob(os.path.join(settings.SOURCE_DIR, "data", "*.json"))

    # --- stock areas gone, 100 KBK .are files present -----------------------
    assert not glob.glob(os.path.join(settings.SOURCE_DIR, "area", "*.are"))
    assert len(glob.glob(os.path.join(settings.SOURCE_DIR, "area", "kbk", "*.are"))) == 100

    # --- stub spells registered (>200 skills with no implementation yet) ----
    assert sum(1 for s in const.skill_table.values() if s.spell_fun is None) > 200
