import json
import os

import pytest

from rom24.database import tracker
from rom24.database.read import read_tables as rt


def _mini_token(monkeypatch):
    """Point the tables registry at a single throwaway dict table for the test."""
    table = {}
    tok = tracker.SaveToken("mini_table", table, None)
    monkeypatch.setattr(tracker, "tables", [tok])
    monkeypatch.setattr(rt, "tables", [tok])
    return table


def _write(dirpath, body):
    os.makedirs(dirpath, exist_ok=True)
    with open(os.path.join(dirpath, "mini_table.json"), "w") as fp:
        json.dump(body, fp)


def test_layers_merge_disjoint_keys(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"gnome": {"name": "gnome"}})
    rt.read_tables(locs=[a, b])
    assert set(table.keys()) == {"elf", "gnome"}


def test_collision_raises(tmp_path, monkeypatch):
    _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"elf": {"name": "elf2"}})
    with pytest.raises(ValueError):
        rt.read_tables(locs=[a, b])


def test_override_allows_replace(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    _write(a, {"elf": {"name": "elf"}})
    _write(b, {"elf": {"name": "elf2", "__override__": True}})
    rt.read_tables(locs=[a, b])
    assert table["elf"]["name"] == "elf2"


def test_bad_file_is_skipped_not_fatal(tmp_path, monkeypatch):
    table = _mini_token(monkeypatch)
    a, b = str(tmp_path / "a"), str(tmp_path / "b")
    os.makedirs(a, exist_ok=True)
    with open(os.path.join(a, "mini_table.json"), "w") as fp:
        fp.write("{ broken json")
    _write(b, {"gnome": {"name": "gnome"}})
    rt.read_tables(locs=[a, b])  # must not raise
    assert "gnome" in table
