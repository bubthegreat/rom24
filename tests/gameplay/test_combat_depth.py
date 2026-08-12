"""Tier 1: combat depth — damage lands, kills reward xp, flee escapes.

test_combat.py only checks a kill leaves a corpse. These assert the numbers
behind combat: a hit lowers the victim's hp, a kill grants experience, and
'flee' ends the fight.
"""
from helpers import make_pc, spawn_mob, run
from rom24 import merc, instance, fight


def test_hit_reduces_hp(booted_world):
    """A violence round lowers the victim's hit points."""
    pc = make_pc(name="Hitter", level=30, room_vnum=3001)
    room = pc.in_room
    victim = spawn_mob(3068, room, level=1)   # a cityguard
    victim.hit = victim.max_hit = 200
    run(pc, "kill cityguard")
    fight.multi_hit(pc, victim, merc.TYPE_UNDEFINED)
    assert victim.hit < 200, "combat round did not reduce victim hp"


def test_kill_grants_xp(booted_world):
    """Killing a mob increases the player's experience."""
    pc = make_pc(name="Xpgainer", level=20, room_vnum=3005)
    room = pc.in_room
    victim = spawn_mob(3068, room, level=2)
    victim.hit = 5
    exp0 = pc.exp
    run(pc, "kill cityguard")
    for _ in range(30):
        if victim.position == merc.POS_DEAD or victim.instance_id not in instance.characters:
            break
        fight.multi_hit(pc, victim, merc.TYPE_UNDEFINED)
    assert pc.exp > exp0, "killing a mob granted no experience (%d -> %d)" % (exp0, pc.exp)


def test_flee_stops_fighting(booted_world):
    """'flee' ends combat (and normally moves the fleer to another room)."""
    pc = make_pc(name="Fleer", level=10, room_vnum=3005)
    room = pc.in_room
    spawn_mob(3068, room)
    run(pc, "kill cityguard")
    assert pc.fighting, "kill did not start a fight"
    for _ in range(10):
        run(pc, "flee")
        if not pc.fighting:
            break
    assert not pc.fighting, "still fighting after repeated flee attempts"
