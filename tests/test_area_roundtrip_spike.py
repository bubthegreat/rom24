import json

from rom24 import instance


def _roundtrip(obj):
    js = json.dumps(obj, default=instance.to_json)
    return json.loads(js, object_hook=instance.from_json)


def test_npc_template_roundtrips(booted_world):
    vnum = next(iter(instance.npc_templates))
    tmpl = instance.npc_templates[vnum]
    saved = getattr(tmpl, "pShop", None)
    tmpl.pShop = None  # back-ref rebuilt from shops on load; strip for the spike
    try:
        back = _roundtrip(tmpl)
    finally:
        tmpl.pShop = saved
    assert back.vnum == tmpl.vnum
    assert back.name == tmpl.name
    assert back.short_descr == tmpl.short_descr
    assert back.level == tmpl.level
    assert back.instance_id is None
    assert back._race == tmpl._race


def test_item_template_roundtrips(booted_world):
    vnum = next(iter(instance.item_templates))
    tmpl = instance.item_templates[vnum]
    back = _roundtrip(tmpl)
    assert back.vnum == tmpl.vnum
    assert back.item_type == tmpl.item_type
    assert list(back.value) == list(tmpl.value)
    assert back.instance_id is None


def test_room_template_roundtrips(booted_world):
    vnum = next(iter(instance.room_templates))
    tmpl = instance.room_templates[vnum]
    back = _roundtrip(tmpl)
    assert back.vnum == tmpl.vnum
    assert back.name == tmpl.name
    assert back.sector_type == tmpl.sector_type
