"""Tests for KBK character-creation helpers in nanny.py (Task 6).

Covers:
- allowed_classes(): per-race class filter
- alignment_allowed(): KBK ALIGN_* restriction enforcement
- apply_prime_stat_boost(): null-safe attr_prime guard

nanny must be imported AFTER register.register() to avoid a circular import
in the heavy module chain (living → fight → update → db → handler_npc → living).
"""

import importlib
import types

import rom24.const as const
from rom24.content import register

# nanny is populated in setup_module after register.register() resolves the
# circular-import chain (living → fight → update → db → handler_npc → living).
nanny: types.ModuleType


def setup_module(module):
    register.register()
    module.nanny = importlib.import_module("rom24.nanny")


def test_allowed_classes_for_race():
    # dwarf: warrior=True, thief=False per content/races.py
    allowed = nanny.allowed_classes("dwarf")
    assert "warrior" in allowed and "thief" not in allowed


def test_alignment_allowed():
    # paladin.align=1 (ALIGN_G from merc.h): good only
    assert nanny.alignment_allowed(const.guild_table["paladin"], 750)
    assert not nanny.alignment_allowed(const.guild_table["paladin"], -750)
    # warrior.align=7 (ALIGN_ANY): any alignment permitted
    assert nanny.alignment_allowed(const.guild_table["warrior"], -750)


def test_alignment_allowed_zealot():
    # zealot.align=5 (ALIGN_GE from merc.h): good or evil but NOT neutral
    zealot = const.guild_table["zealot"]
    assert nanny.alignment_allowed(zealot, 750)
    assert nanny.alignment_allowed(zealot, -750)
    assert not nanny.alignment_allowed(zealot, 0)


def test_prime_stat_boost_none_safe():
    # helper applies +3 only when attr_prime is set; None must not raise
    class FakeCh:
        perm_stat = [13, 13, 13, 13, 13]

        class guild:  # noqa: N801 - stand-in
            attr_prime = None

    nanny.apply_prime_stat_boost(FakeCh)   # must not raise
    assert FakeCh.perm_stat == [13, 13, 13, 13, 13]


def test_prime_stat_boost_applies_when_set():
    # when attr_prime is a valid index, perm_stat is incremented
    class FakeCh:
        perm_stat = [13, 13, 13, 13, 13]

        class guild:
            attr_prime = 0  # STR index

    nanny.apply_prime_stat_boost(FakeCh)
    assert FakeCh.perm_stat[0] == 16
