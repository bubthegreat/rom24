"""End-to-end smoke test: boot the world, run real combat, round-trip a player save.

This is the machine-checkable proof of "playable parity": the game boots its full
world, the combat engine deals damage and resolves a death, and a player character
survives a save/load round-trip. It is intentionally one broad smoke test, not a
coverage suite.
"""
import os
import random

import pytest


def _make_fighter(vnum, level=None):
    from rom24 import instance, object_creator, merc

    template = instance.npc_templates[vnum]
    mob = object_creator.create_mobile(template)
    if level is not None:
        mob.level = level
    mob.position = merc.POS_STANDING
    return mob


def test_world_booted(booted_world):
    """Boot loaded a non-trivial world."""
    from rom24 import instance

    assert len(instance.npc_templates) > 100
    assert len(instance.item_templates) > 100
    assert len(instance.rooms) > 100


def test_combat_deals_damage_and_kills(booted_world):
    """The combat engine lands hits, reduces HP, and resolves a death."""
    from rom24 import instance, fight, merc

    # Put two mobs in the School entrance room.
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]

    vnum = next(iter(instance.npc_templates))
    attacker = _make_fighter(vnum, level=30)
    victim = _make_fighter(vnum, level=1)
    # Give the attacker a decisive edge so a kill is reached in bounded rounds.
    attacker.hitroll = 40
    attacker.damroll = 40

    room.put(attacker)
    room.put(victim)

    start_hp = victim.hit
    fight.set_fighting(attacker, victim)
    fight.set_fighting(victim, attacker)

    killed = False
    for _ in range(500):
        fight.multi_hit(attacker, victim, merc.TYPE_UNDEFINED)
        if victim.position == merc.POS_DEAD or victim.hit < 0:
            killed = True
            break

    assert victim.hit < start_hp, "combat dealt no damage"
    assert killed, "victim never died after 500 rounds"


def test_player_save_load_roundtrip(booted_world, tmp_path):
    """A player character survives a save/load round-trip."""
    from rom24 import handler_pc, settings

    # Redirect player saves to a temp dir so the test leaves no residue.
    orig_dir = settings.PLAYER_DIR
    settings.PLAYER_DIR = str(tmp_path)
    try:
        name = "Zsmoketest"
        pc = handler_pc.Pc(name)
        pc.level = 7
        pc.save(force=True)

        loaded = handler_pc.Pc.load(name)
        assert loaded is not None
        assert loaded.name == name
        assert loaded.level == 7
    finally:
        settings.PLAYER_DIR = orig_dir
