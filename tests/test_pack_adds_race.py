"""The payoff test: a second pack adds a playable race with no core edit.

Loads real ``packs/core`` data plus a tiny throwaway addon pack into a fresh
race table (never the global ``const.race_table``) so the session stays clean.
"""
import json
import os
import shutil

import pytest

from rom24 import settings, packs, const
from rom24.database import tracker
from rom24.database.read import read_tables as rt


def _core_dir():
    return os.path.join(settings.PACKS_DIR, "core")


def _assemble_root(tmp_path, addon_name, race_body):
    root = str(tmp_path)
    shutil.copytree(_core_dir(), os.path.join(root, "core"))
    addon = os.path.join(root, addon_name)
    os.makedirs(addon)
    with open(os.path.join(addon, "pack.json"), "w") as fp:
        json.dump(
            {"name": addon_name, "version": "1.0.0", "depends": ["core"], "data_dir": "."},
            fp,
        )
    with open(os.path.join(addon, "race_table.json"), "w") as fp:
        json.dump(race_body, fp)
    ordered = packs.resolve_load_order(packs.discover_packs(root))
    return [p.data_dir for p in ordered]


def _fresh_race_only(monkeypatch):
    """A throwaway race_table token so we never touch the global one."""
    table = {}
    tok = tracker.SaveToken("race_table", table, const.race_type)
    monkeypatch.setattr(rt, "tables", [tok])
    return table


def test_addon_pack_adds_race(tmp_path, monkeypatch):
    # race_type arity: (name, pc_race, act, aff, off, imm, res, vuln, form, parts)
    locs = _assemble_root(
        tmp_path, "zzaddon", {"testkin": ["testkin", False, 0, 0, 0, 0, 0, 0, 0, 0]}
    )
    table = _fresh_race_only(monkeypatch)
    rt.read_tables(locs=locs)
    assert "testkin" in table  # addon race present
    assert "human" in table  # core race still present
    assert table["testkin"].name == "testkin"


def test_duplicate_race_across_packs_is_rejected(tmp_path, monkeypatch):
    # Addon redefines a core race ("human") without __override__ -> hard error.
    locs = _assemble_root(
        tmp_path, "zzdupe", {"human": ["human", True, 0, 0, 0, 0, 0, 0, 0, 0]}
    )
    _fresh_race_only(monkeypatch)
    with pytest.raises(ValueError):
        rt.read_tables(locs=locs)
