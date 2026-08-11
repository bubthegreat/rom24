"""Regression test for do_gain skill training.

The bug: the skill-grant branch guarded with ``if sn.spell_fun is not None``.
Non-spell skills store ``spell_fun == magic.spell_null`` (a real function, never
``None``), so the guard was always true and every skill-gain was refused with
"You must learn the full group." The fix compares against ``magic.spell_null``.
"""
import pytest


def _find_gainable_skill(guild_name):
    """A non-spell skill this guild can train and a fresh PC does not know."""
    from rom24 import const, magic

    for name, skill in const.skill_table.items():
        is_skill = skill.spell_fun is None or skill.spell_fun == magic.spell_null
        if is_skill and skill.rating[guild_name] > 0:
            return name
    return None


def test_do_gain_grants_skill(booted_world, command):
    from rom24 import const, instance, merc, object_creator
    from rom24 import handler_pc

    # A real warrior PC with training sessions to spend.
    pc = handler_pc.Pc("Zgaintest")
    pc.is_pc = True
    pc.guild = const.guild_table["warrior"]
    pc.trust = 0
    pc.train = 100
    pc.learned = {}
    pc.group_known = []
    captured = []
    pc.send = lambda text: captured.append(text)

    skill_name = _find_gainable_skill(pc.guild.name)
    assert skill_name is not None, "no trainable warrior skill found in skill_table"

    # A trainer mob (ACT_GAIN) in the same room.
    room_id = instance.instances_by_room[merc.ROOM_VNUM_SCHOOL][0]
    room = instance.global_instances[room_id]
    trainer = object_creator.create_mobile(next(iter(instance.npc_templates.values())))
    trainer.act.set_bit(merc.ACT_GAIN)
    room.put(trainer)
    room.put(pc)

    assert skill_name not in pc.learned
    command('gain')(pc, skill_name)

    assert skill_name in pc.learned, (
        "do_gain refused to grant a valid skill; output was: %r" % captured
    )
    assert pc.train < 100, "training sessions were not spent"
