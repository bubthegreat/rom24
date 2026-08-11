"""Regression tests for NPC command dispatch via ``do_switch`` / ``do_force``.

Both immortal commands ultimately drive a mobile through ``interpret``. Before
the fix, ``interpret`` lived only on ``Pc`` so any NPC victim raised
``AttributeError``. These tests boot the full world and prove an ``Npc`` can now
dispatch a command through its own ``interpret`` method.
"""
import random

import pytest


def _make_mob(vnum):
    from rom24 import instance, object_creator, merc

    template = instance.npc_templates[vnum]
    mob = object_creator.create_mobile(template)
    mob.position = merc.POS_STANDING
    return mob


def _room(booted_world):
    from rom24 import instance, merc

    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    return instance.global_instances[room_id]


def test_npc_interpret_dispatches_known_command(booted_world):
    """An Npc can run a real command through its own interpret without raising."""
    room = _room(booted_world)
    vnum = next(iter(booted_world_npcs()))
    mob = _make_mob(vnum)
    room.put(mob)

    captured = []
    mob.send = lambda text: captured.append(text)

    # A known command ("look", level 0, POS_RESTING) must dispatch, not fall
    # through to the "Huh?" unknown-command path.
    mob.interpret("look")
    assert "Huh?\n" not in captured, "known command was treated as unknown"


def test_npc_interpret_unknown_command(booted_world):
    """An unknown command sends 'Huh?' instead of raising or dispatching."""
    room = _room(booted_world)
    vnum = next(iter(booted_world_npcs()))
    mob = _make_mob(vnum)
    room.put(mob)

    captured = []
    mob.send = lambda text: captured.append(text)

    mob.interpret("zzzznotacommand")
    assert "Huh?\n" in captured


def test_do_force_on_npc_victim_does_not_raise(booted_world):
    """do_force targeting an NPC dispatches to victim.interpret without AttributeError."""
    from rom24.commands import do_force

    room = _room(booted_world)
    npc_vnums = list(booted_world_npcs())
    ch = _make_mob(npc_vnums[0])
    victim = _make_mob(npc_vnums[1])
    # Give the forcing char maximum trust so no level guard blocks the force.
    ch.trust = 60
    room.put(ch)
    room.put(victim)

    victim_dispatched = []
    orig_interpret = victim.interpret
    victim.interpret = lambda arg: (victim_dispatched.append(arg), orig_interpret(arg))[1]

    # First keyword of the victim's name is how do_force locates it in the room.
    target = victim.name.split()[0]
    do_force.do_force(ch, "%s look" % target)

    assert victim_dispatched, "do_force never reached victim.interpret"
    # do_force passes the remaining argument verbatim (leading space intact);
    # interpret strips it. The point is the NPC's interpret was reached.
    assert victim_dispatched[0].strip() == "look"


def booted_world_npcs():
    from rom24 import instance

    return instance.npc_templates
