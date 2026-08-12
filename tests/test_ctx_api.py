"""The ctx-style pilot commands/spells work through real registration/dispatch."""
from rom24 import instance, object_creator, merc, const, fight, state_checks


def _mob(vnum, room, level=10):
    m = object_creator.create_mobile(instance.npc_templates[vnum])
    m.position = merc.POS_STANDING
    m.level = level
    room.put(m)
    return m


def _school(booted_world):
    rid = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    return instance.global_instances[rid]


def test_armor_spell_adds_affect(booted_world):
    room = _school(booted_world)
    target = _mob(3001, room)
    assert not state_checks.is_affected(target, "armor")
    # spell_fun is the ctx shim registered by @api.spell.
    const.skill_table["armor"].spell_fun("armor", 20, target, target, merc.TARGET_CHAR)
    assert state_checks.is_affected(target, "armor")


def _generic_vnum():
    # A plain fighter template (the one the e2e combat test proves damageable).
    return next(iter(instance.npc_templates))


def test_fireball_spell_deals_damage(booted_world):
    room = _school(booted_world)
    v = _generic_vnum()
    caster = _mob(v, room, level=40)
    victim = _mob(v, room, level=5)
    fight.set_fighting(caster, victim)
    fight.set_fighting(victim, caster)
    start = victim.hit
    const.skill_table["fireball"].spell_fun("fireball", 40, caster, victim, merc.TARGET_CHAR)
    assert victim.hit < start, "fireball dealt no damage"


def test_kick_command_dispatches_and_hits(booted_world, command):
    room = _school(booted_world)
    v = _generic_vnum()
    attacker = _mob(v, room, level=30)
    victim = _mob(v, room, level=5)
    attacker.hitroll = 200  # force the skill roll and the hit to land
    attacker.learned = {"kick": 100}
    fight.set_fighting(attacker, victim)
    fight.set_fighting(victim, attacker)
    start = victim.hit
    command("kick")(attacker, "")  # ch.do_kick is the ctx shim
    assert victim.hit < start, "kick dealt no damage"


def test_say_command_emits(booted_world, command, monkeypatch):
    from rom24 import handler_game

    calls = []
    monkeypatch.setattr(handler_game, "act", lambda fmt, ch, a1, a2, to: calls.append((fmt, a2)))
    room = _school(booted_world)
    speaker = _mob(3001, room)
    command("say")(speaker, "hello world")
    assert any(a2 == "hello world" for _, a2 in calls), "say did not emit the message"
