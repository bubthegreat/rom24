"""The prog trigger system fires area progs with a curated ctx."""
from rom24 import instance, object_creator, merc, prog_triggers


def _spawn(vnum, room):
    mob = object_creator.create_mobile(instance.npc_templates[vnum])
    mob.position = merc.POS_STANDING
    room.put(mob)
    return mob


def test_speech_prog_fires_on_keyword(booted_world):
    # The Midgaard wizard (3000) has a speech prog registered from
    # areas/midgaard/progs.py, loaded during boot.
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    wizard = _spawn(3000, room)

    said = []
    wizard.do_say = lambda text: said.append(text)

    speaker = _spawn(3001, room)  # any other mob acting as the speaker
    prog_triggers.fire_speech(wizard, speaker, "hello there", room)

    assert said, "speech prog did not fire"
    assert "arcane" in said[0].lower()


def test_speech_prog_ignores_other_keywords(booted_world):
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    wizard = _spawn(3000, room)
    said = []
    wizard.do_say = lambda text: said.append(text)

    prog_triggers.fire_speech(wizard, wizard, "goodbye", room)
    assert not said, "speech prog fired on a non-matching keyword"


def test_greet_prog_registered(booted_world):
    # The wizard also has a greet prog; firing it should not raise.
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    wizard = _spawn(3000, room)
    enterer = _spawn(3001, room)
    prog_triggers.fire_greet(wizard, enterer, room)  # must not raise


def test_give_prog_fires(booted_world):
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    wizard = _spawn(3000, room)
    said = []
    wizard.do_say = lambda text: said.append(text)
    giver = _spawn(3001, room)
    prog_triggers.fire_give(wizard, giver, None, room)
    assert said and "gift" in said[0].lower()


def test_death_prog_fires(booted_world):
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    wizard = _spawn(3000, room)
    killer = _spawn(3001, room)
    prog_triggers.fire_death(wizard, killer, room)  # must not raise


def test_random_prog_only_fires_for_registered_vnum(booted_world):
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    # A mob with no random prog registered: fire_random is a no-op, no raise.
    plain = _spawn(3001, room)
    prog_triggers.fire_random(plain)
    # The wizard has one; firing must not raise.
    wizard = _spawn(3000, room)
    prog_triggers.fire_random(wizard)
