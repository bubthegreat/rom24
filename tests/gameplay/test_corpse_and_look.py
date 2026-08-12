"""Corpse-on-kill for many mobs + look-<container> defaults to look-in."""
import pytest

from helpers import make_pc, spawn_mob, spawn_item, run, corpse_in_room
from rom24 import merc, instance


def _midgaard_mob_vnums(limit=40):
    return [v for v in sorted(instance.npc_templates) if 3000 <= v <= 3080][:limit]


def test_slay_always_leaves_a_corpse(booted_world):
    """Slaying any mob must leave a corpse (make_corpse must never crash)."""
    failures = []
    for vnum in _midgaard_mob_vnums():
        pc = make_pc(name="Slayer%d" % vnum, level=merc.MAX_LEVEL)
        room = pc.in_room
        mob = spawn_mob(vnum, room)
        try:
            run(pc, "slay %s" % (mob.name.split()[0]))
        except Exception as exc:  # noqa: BLE001
            failures.append("vnum %d (%s): raised %s" % (vnum, mob.short_descr, exc))
            continue
        if corpse_in_room(room) is None:
            failures.append("vnum %d (%s): no corpse" % (vnum, mob.short_descr))
    assert not failures, "slay left no corpse for:\n" + "\n".join(failures)


def test_look_container_defaults_to_look_in(booted_world):
    """'look <container>' shows its contents, like 'look in <container>'."""
    pc = make_pc()
    room = pc.in_room
    pit = spawn_item(3010, room)      # 'pit' container
    bag = spawn_item(3032, pit)       # a bag inside it

    out_in = run(pc, "look in pit")
    out_bare = run(pc, "look pit")
    assert "holds" in out_bare.lower() or bag.name.split()[0].lower() in out_bare.lower(), (
        "'look pit' did not show contents (should default to look-in): %r" % out_bare
    )


def test_look_corpse_defaults_to_look_in(booted_world):
    """'look corpse' after a kill shows the corpse contents, not flavor text."""
    pc = make_pc(name="Gravedigger", level=merc.MAX_LEVEL)
    room = pc.in_room
    spawn_mob(3011, room)                 # Hassan
    run(pc, "slay hassan")
    assert corpse_in_room(room) is not None, "slay left no corpse"
    out = run(pc, "look corpse")
    assert "holds" in out.lower(), (
        "'look corpse' did not default to look-in: %r" % out
    )
