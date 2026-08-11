"""The JSON area loader reproduces the stock world counts exactly.

Runs in a subprocess so it can drive read_tables + load_areas_json on a clean
interpreter without colliding with the session-scoped legacy boot fixture.
"""
import subprocess
import sys


def test_json_loader_matches_baseline():
    code = (
        "from rom24.hotfix import init_monitoring; init_monitoring();"
        "from rom24 import instance, area_loader_json, merc;"
        "from rom24.database.read import read_tables as rt;"
        "rt.read_tables();"
        "area_loader_json.load_areas_json();"
        "print('AREAS', len(instance.area_templates));"
        "print('NPCS', len(instance.npc_templates));"
        "print('ITEMS', len(instance.item_templates));"
        "print('ROOMS', len(instance.room_templates));"
        "print('SHOPS', len(instance.shop_templates));"
        "print('ROOMINST', len(instance.rooms));"
        "print('SOCIALS', len(merc.social_list));"
        "print('RESETS', sum(len(getattr(a,'reset_list',[]) or []) for a in instance.areas.values()));"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=120)
    out = res.stdout
    assert "AREAS 48" in out, res.stderr[-2000:]
    assert "NPCS 986" in out
    assert "ITEMS 1265" in out
    assert "ROOMS 3126" in out
    assert "SHOPS 62" in out
    assert "ROOMINST 3126" in out
    assert "SOCIALS 244" in out
    assert "RESETS 5096" in out
