"""Tests for OLC format loading in data_loader.py"""

from rom24 import data_loader, instance, world_classes


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
