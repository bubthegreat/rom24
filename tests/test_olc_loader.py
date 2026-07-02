"""Tests for OLC format loading in data_loader.py"""

from rom24 import data_loader, instance, world_classes


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
