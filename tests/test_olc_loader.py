"""Tests for OLC format loading in data_loader.py"""

from rom24 import data_loader, instance, world_classes
from rom24.database.read.read_tables import read_tables


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
    read_tables()  # populate race_table (needed for npc.race.act / flag defaults)
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
