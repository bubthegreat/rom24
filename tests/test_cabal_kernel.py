"""Tests for cabal kernel (Task 3 of Phase 3a).

Values pinned from kbk tables.c:42-55 (CABALS), tables.c:122-134 (MESSAGES),
merc.h:1748-1779 (vnums), merc.h:891-919 (bit letters).
"""
from rom24 import cabal


def test_cabal_table_shape():
    assert len(cabal.CABALS) == 10           # index 0 = none
    assert cabal.CABALS[1]["name"] == "ancient"
    assert cabal.CABALS[1]["item_vnum"] == 3801
    assert cabal.CABALS[2]["name"] == "knight"


def test_cabal_table_all_names():
    expected_names = [
        "",         # 0 none
        "ancient",  # 1
        "knight",   # 2
        "arcana",   # 3
        "rager",    # 4
        "outlaw",   # 5
        "empire",   # 6
        "bounty",   # 7
        "sylvan",   # 8
        "enforcer", # 9
    ]
    assert [c["name"] for c in cabal.CABALS] == expected_names


def test_cabal_table_item_vnums():
    """Spot-check item vnums transcribed verbatim from kbk tables.c:47-55."""
    expected = {
        1: 3801,   # ancient
        2: 4502,   # knight
        3: 5801,   # arcana
        4: 5701,   # rager
        5: 9902,   # outlaw
        6: 8101,   # empire
        7: 8800,   # bounty
        8: 8900,   # sylvan
        9: 4521,   # enforcer
    }
    for idx, vnum in expected.items():
        assert cabal.CABALS[idx]["item_vnum"] == vnum, (
            f"CABALS[{idx}] item_vnum: expected {vnum}, got {cabal.CABALS[idx]['item_vnum']}"
        )


def test_lookup_prefix():
    assert cabal.lookup("anc") == 1
    assert cabal.lookup("ancient") == 1
    assert cabal.lookup("kni") == 2
    assert cabal.lookup("arc") == 3
    assert cabal.lookup("rag") == 4
    assert cabal.lookup("out") == 5
    assert cabal.lookup("emp") == 6
    assert cabal.lookup("bou") == 7
    assert cabal.lookup("syl") == 8
    assert cabal.lookup("enf") == 9
    assert cabal.lookup("nosuch") == 0
    assert cabal.lookup("") == 0


def test_index_of_normalizes():
    assert cabal.index_of("knight") == 2
    assert cabal.index_of(2) == 2
    assert cabal.index_of(0) == 0
    assert cabal.index_of("") == 0
    assert cabal.index_of("ancient") == 1
    assert cabal.index_of("enf") == 9


def test_messages_shape():
    assert len(cabal.MESSAGES) == 10
    assert cabal.MESSAGES[1]["entrygreeting"] == "May the darkness conceal you."
    assert cabal.MESSAGES[2]["entrygreeting"] == "Greetings, brother Knight."
    assert cabal.MESSAGES[9]["entrygreeting"] == "Greetings, Enforcer of the Law."


def test_is_cabal_item():
    """is_cabal_item must accept any object with a .vnum attribute."""
    class FakeItem:
        def __init__(self, vnum):
            self.vnum = vnum

    assert cabal.is_cabal_item(FakeItem(3801))   # ancient item
    assert cabal.is_cabal_item(FakeItem(4502))   # knight item
    assert not cabal.is_cabal_item(FakeItem(9999))
    assert not cabal.is_cabal_item(FakeItem(1))  # index-0 placeholder


def test_citems_roundtrip(tmp_path, monkeypatch):
    from rom24 import settings
    monkeypatch.setattr(settings, "SYSTEM_DIR", str(tmp_path))
    cabal.save_items([(1, 3800), (2, 4501)])
    assert cabal.load_item_bindings() == [(1, 3800), (2, 4501)]


def test_citems_empty_missing(tmp_path, monkeypatch):
    """load_item_bindings returns [] when citems.txt is absent."""
    from rom24 import settings
    monkeypatch.setattr(settings, "SYSTEM_DIR", str(tmp_path))
    assert cabal.load_item_bindings() == []


def test_load_items_no_file(tmp_path, monkeypatch):
    """load_items() with no citems.txt is a clean no-op (no exception)."""
    from rom24 import settings
    monkeypatch.setattr(settings, "SYSTEM_DIR", str(tmp_path))
    cabal.load_items()  # must not raise
