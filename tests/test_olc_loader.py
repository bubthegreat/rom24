"""Tests for OLC format loading in data_loader.py"""

import logging

import pytest

from rom24 import data_loader, instance, world_classes
from rom24.content.register import register


def _make_area():
    pArea = world_classes.Area(None)
    pArea.name = "test-area"
    template = world_classes.Area(pArea)
    return template


AREADATA = """Name Midgaard~
Builders Zornath~
VNUMs 3000 3399
Credits { 5 60} KBK  Midgaard~
Security 1
End
"""


def test_load_area_data():
    instance.area_templates.clear()
    remainder, pArea = data_loader.load_area_data(AREADATA, 1)
    assert pArea.name == "Midgaard"
    assert pArea.min_vnum == 3000 and pArea.max_vnum == 3399
    assert "Midgaard" in instance.area_templates
    assert remainder.strip() == ""


ROOMDATA = """#3001
NAME The Temple Square~
DESCR You are standing in the temple square.
~
FLAGS CD
SECT 1
MHRATE 110 120
DOOR 0 ~
~
0 -1 3054
EDESC fountain~
A big fountain.
~
End
#0
"""


def test_load_rooms_new():
    instance.room_templates.clear()
    pArea = _make_area()
    data_loader.load_rooms_new(ROOMDATA, pArea)
    room = instance.room_templates[3001]
    assert room.name == "The Temple Square"
    assert room.mana_rate == 110 and room.heal_rate == 120
    assert room.exit[0].to_room_vnum == 3054
    assert room.extra_descr[0].keyword == "fountain"
    assert room.sector_type == 1


MOBDATA = """#3000
NAME wizard mud school~
SHORT the wizard of mud school~
LONG A wizard stands here, ready to teach.
~
DESCR He looks wise.
~
Race human~
ACT AB
AFF 0
ALIGN 350
GROUP 0
LEVEL 25
HROLL 5
HDICE 8 d 8 + 100
MDICE 10 d 10 + 100
DDICE 2 d 6 + 4
DTYPE crush
AC 2 2 2 -1
OFF AB
IMM 0
RES J
VULN 0
POS stand stand
SEX male
GOLD 500
FORM AHMV
PARTS ABCDEFGHIJK
SIZE medium
MATER flesh~
CABAL rager
DMOD 120
QUEST 5
End
#0
"""


def test_load_npcs_new():
    register()  # populate race_table (needed for npc.race.act / flag defaults)
    instance.npc_templates.clear()
    pArea = _make_area()
    data_loader.load_npcs_new(MOBDATA, pArea)
    npc = instance.npc_templates[3000]
    assert npc.short_descr == "the wizard of mud school"
    assert npc.level == 25
    assert npc.hit_dice == [8, 8, 100]
    assert npc.dam_dice == [2, 6, 4]
    assert npc.armor == [20, 20, 20, -10]
    assert npc.dam_mod == 120 and npc.quest_credit_reward == 5
    assert npc.cabal == "rager"


OBJDATA = """#3010
NAME sub issue sword~
SHORT a sub issue sword~
DESCR A sub issue sword lies here.
~
MAT iron~
TYPE weapon sword 1 8 slash A
WEAR AN
Extra 1 2 3 0
LEVEL 10
COST 100
COND 100
End
#3011
NAME leather vest~
SHORT a leather vest~
DESCR A leather vest lies here.
~
MAT leather~
TYPE armor 0 0 0 0 0
WEAR AC
LEVEL 30
COST 50
COND 100
AFFECT O 13 5 0
End
#3012
NAME practice shield~
SHORT a practice shield~
DESCR A practice shield lies here.
~
MAT wood~
TYPE armor 0 0 0 0 0
WEAR AJ
LEVEL 60
COST 10
COND 100
End
#0
"""


def test_load_objects_new_weapon():
    register()
    instance.item_templates.clear()
    data_loader.load_objects_new(OBJDATA, _make_area())
    sword = instance.item_templates[3010]
    assert sword.level == 10
    assert sword.value[1] == 1 and sword.value[2] == 8
    assert sword.weight > 0   # derived from material iron


def test_load_objects_new_armor_derives_ac():
    register()
    instance.item_templates.clear()
    data_loader.load_objects_new(OBJDATA, _make_area())
    vest = instance.item_templates[3011]
    # AC_PER_ONE_PERCENT_DECREASE_DAMAGE is -75.0; C math double-negates
    # (db.c:5059-5068), so derived armor values are POSITIVE protection ints
    assert vest.value[0] > 0
    assert vest.affected[0].modifier == 5


def test_load_objects_new_shield_slot_derives_ac():
    register()
    instance.item_templates.clear()
    data_loader.load_objects_new(OBJDATA, _make_area())
    shield = instance.item_templates[3012]
    assert shield.value[0] > 0
    assert shield.weight > 0


IMPROGS = """M 3000 GREET greet_wizard
* a comment line
I 3010 WEAR wear_sword
E
"""


def test_load_improgs():
    register()
    instance.npc_templates.clear()
    instance.item_templates.clear()
    pArea = _make_area()
    data_loader.load_npcs_new(MOBDATA, pArea)
    data_loader.load_objects_new(OBJDATA, pArea)
    data_loader.load_improgs(IMPROGS)
    assert ("GREET", "greet_wizard") in instance.npc_templates[3000].improgs
    assert ("WEAR", "wear_sword") in instance.item_templates[3010].improgs


# Real-data excerpt: old KBK area files (e.g. air.are) write AFF as multiple
# space-separated integers ("AFF 1 2 0 536") instead of the current letter
# format ("AFF ABCDE").  Only the first value is meaningful; the rest must be
# consumed silently so subsequent keywords are parsed correctly.
MOBDATA_OLDSTYLE_AFF = """#4000
NAME  fairy dragon~
SHORT A fairy dragon~
LONG  A fairy dragon is here.
~
DESCR
None.
~
Race human~
ACT   AGR
AFF   1 2 0 536
OFF   FU
IMM   0
RES   0
VULN  0
WSPEC 0
ALIGN 500
GROUP 0
LEVEL 5
HROLL 0
ENHA  100.00%
HDICE 2d7+46
MDICE 5d9+100
DDICE 1d5+0
DTYPE none
AC    6 6 6 8
POS   stand stand
SEX   none
GOLD  1
FORM  AHMV
PARTS ABCDEFGHIJK
SIZE  medium
MATER flesh~
DMOD  100
AMOD  0
QUEST 0
End
#0
"""


def test_load_npcs_new_oldstyle_aff(caplog):
    """Old-format multi-integer AFF line must not produce unknown-keyword warnings."""
    register()
    instance.npc_templates.clear()
    pArea = _make_area()
    with caplog.at_level(logging.WARNING, logger="rom24.data_loader"):
        data_loader.load_npcs_new(MOBDATA_OLDSTYLE_AFF, pArea)
    assert not [r for r in caplog.records if r.levelno >= logging.WARNING], (
        "load_npcs_new produced unexpected WARNING-level log records: "
        + str([r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING])
    )
    npc = instance.npc_templates.get(4000)
    assert npc is not None, "NPC 4000 should have been loaded"
    assert npc.level == 5
    # OFF field must parse correctly after the multi-value AFF line
    assert npc.off_flags is not None


# ---------------------------------------------------------------------------
# Truncation-guard tests (item 2 of final-review wave)
# ---------------------------------------------------------------------------

def test_load_area_data_truncated():
    """load_area_data raises ValueError when input ends before 'End'."""
    with pytest.raises(ValueError):
        data_loader.load_area_data("Name Midgaard~\nBuilders Zornath~\n", 1)


def test_load_rooms_new_truncated():
    """load_rooms_new raises ValueError when input ends before 'End' inside a room."""
    with pytest.raises(ValueError):
        pArea = _make_area()
        data_loader.load_rooms_new("#3001\nNAME Test Room~\n", pArea)


def test_load_improgs_truncated():
    """load_improgs raises ValueError when input ends before 'E'."""
    with pytest.raises(ValueError):
        data_loader.load_improgs("* just a comment\n")
