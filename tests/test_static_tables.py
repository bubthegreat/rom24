import json
import os

from rom24 import settings, static_tables


def _load(name):
    with open(os.path.join(settings.DATA_DIR, name + ".json")) as f:
        data = json.load(f)
    return {int(k) if isinstance(k, str) and k.isdigit() else k: v for k, v in data.items()} \
        if isinstance(data, dict) else data


def test_static_tables_match_json():
    for name in ("act_flags", "plr_flags", "affect_flags", "off_flags", "imm_flags",
                 "form_flags", "part_flags", "comm_flags", "exit_flags"):
        assert static_tables.FLAG_TABLES[name] == _load(name), name
    assert static_tables.POSITION_TABLE == _load("position_table")
    assert static_tables.SEX_TABLE == _load("sex_table")
    assert static_tables.SIZE_TABLE == _load("size_table")
    assert static_tables.CLAN_TABLE == _load("clan_table")
    assert static_tables.WIZNET_TABLE == _load("wiznet_table")
