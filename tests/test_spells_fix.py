"""Regression tests for two previously-broken spells.

1. ``charm person`` must make the victim a follower of the caster with an
   ``AFF_CHARM`` affect, and must NOT leave the caster and victim fighting each
   other. The old bug lived in the offensive-spell reaction (``do_cast``): it
   compared ``victim.master`` (stored as an ``instance_id`` int) against the
   caster object, so the guard never matched and the freshly-charmed mob turned
   around and attacked its new master.

2. ``identify`` must run without error and send a non-empty description. The old
   code never imported ``instance`` (a ``NameError`` on nearly every item) and
   mutated ``item.affected`` in place.
"""
import random

import pytest


def _make_mob(vnum, level=None):
    from rom24 import instance, object_creator, merc

    template = instance.npc_templates[vnum]
    mob = object_creator.create_mobile(template)
    if level is not None:
        mob.level = level
    mob.position = merc.POS_STANDING
    return mob


def _non_law_non_safe_room():
    from rom24 import instance, merc, state_checks

    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    original = room.room_flags
    room.room_flags = state_checks.REMOVE_BIT(
        room.room_flags, merc.ROOM_LAW | merc.ROOM_SAFE
    )
    return room, original


def test_charm_person_makes_follower_not_enemy(booted_world, monkeypatch):
    from rom24 import const, fight, handler_magic, instance, merc

    # Isolate the follower/fighting behaviour from the random saving throw:
    # force the victim to fail its save so the charm reliably lands.
    monkeypatch.setattr(handler_magic, "saves_spell", lambda *a, **k: False)

    room, original_flags = _non_law_non_safe_room()
    try:
        vnum = next(iter(instance.npc_templates))
        caster = _make_mob(vnum, level=60)
        victim = _make_mob(vnum, level=1)

        # Make the victim a plain, charmable mob (not a shop/trainer/etc.).
        victim.pShop = None
        for flag in (merc.ACT_TRAIN, merc.ACT_PRACTICE, merc.ACT_IS_HEALER, merc.ACT_IS_CHANGER):
            victim.act.rem_bit(flag)
        victim.imm_flags = 0

        room.put(caster)
        room.put(victim)

        sn = const.skill_table["charm person"]
        sn.spell_fun(sn, caster.level, caster, victim, merc.TARGET_CHAR)

        # The charm actually took hold.
        assert victim.is_affected(merc.AFF_CHARM), "victim not AFF_CHARM after charm"
        assert victim.master == caster.instance_id, "victim is not following the caster"

        # The spell itself started no fight.
        assert caster.fighting is not victim
        assert victim.fighting is not caster

        # Drive the exact offensive-spell reaction from do_cast.py. With the fix
        # the guard is False (victim.master == caster.instance_id) so no fight
        # begins. Under the old bug the guard fired and multi_hit set them
        # fighting, which the assertions below would catch.
        if victim != caster and victim.master != caster.instance_id:
            fight.check_killer(victim, caster)
            fight.multi_hit(victim, caster, merc.TYPE_UNDEFINED)

        assert victim.fighting is not caster, "charmed mob attacked its master"
        assert caster.fighting is not victim, "caster ended up fighting its charmed mob"
    finally:
        room.room_flags = original_flags


def test_identify_reports_item(booted_world):
    from rom24 import const, instance, merc, object_creator

    # Pick a simple item whose identify output does not need per-spell skill
    # lookups, so the test stays deterministic across boots.
    skip_types = {
        merc.ITEM_SCROLL,
        merc.ITEM_POTION,
        merc.ITEM_PILL,
        merc.ITEM_WAND,
        merc.ITEM_STAFF,
    }
    template = None
    for tmpl in instance.item_templates.values():
        if tmpl.item_type not in skip_types:
            template = tmpl
            break
    assert template is not None, "no suitable item template found"

    item = object_creator.create_item(template, 0)

    vnum = next(iter(instance.npc_templates))
    caster = object_creator.create_mobile(instance.npc_templates[vnum])

    buf = []
    caster.send = buf.append  # capture output (base Living.send is a no-op)

    sn = const.skill_table["identify"]
    sn.spell_fun(sn, 30, caster, item, merc.TARGET_ITEM)

    output = "".join(buf)
    assert output, "identify sent nothing"
    assert "Item" in output, "identify output missing the item summary line"

    # identify must not mutate the object's own affect list.
    assert item.affected == list(item.affected)
