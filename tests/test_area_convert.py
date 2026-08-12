import json
import os

from rom24 import area_convert, instance


def test_convert_writes_area_folders(booted_world, tmp_path):
    out = str(tmp_path)
    summary = area_convert.convert_all(out)
    assert summary["areas"] == len(instance.area_templates)
    assert summary["rooms"] == len(instance.room_templates)
    assert summary["mobiles"] == len(instance.npc_templates)
    assert summary["objects"] == len(instance.item_templates)

    dirs = [d for d in os.listdir(out) if d != "_global"]
    assert dirs, "no area folders written"
    sample = os.path.join(out, dirs[0])
    for fname in ("area.json", "rooms.json", "mobiles.json", "objects.json", "resets.json", "shops.json"):
        assert os.path.isfile(os.path.join(sample, fname)), fname

    assert os.path.isfile(os.path.join(out, "_global", "helps.json"))
    assert os.path.isfile(os.path.join(out, "_global", "socials.json"))

    with open(os.path.join(sample, "mobiles.json")) as fp:
        assert isinstance(json.load(fp), list)
