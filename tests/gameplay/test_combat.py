"""Combat + death behavior."""
from helpers import make_pc, spawn_mob, corpse_in_room, run
from rom24 import merc, fight


def test_kill_leaves_corpse(booted_world):
    """Killing a mob in combat leaves a corpse in the room."""
    pc = make_pc(level=50)
    pc.hitroll = 300
    pc.damroll = 300
    room = pc.in_room
    mob = spawn_mob(3068, room, level=1)  # a cityguard (killable, not protected)

    fight.set_fighting(pc, mob)
    fight.set_fighting(mob, pc)
    for _ in range(300):
        fight.multi_hit(pc, mob, merc.TYPE_UNDEFINED)
        if mob.position == merc.POS_DEAD or mob.hit < 0:
            break

    assert corpse_in_room(room) is not None, "killing a mob left no corpse"


def test_slay_leaves_corpse(booted_world):
    """The immortal 'slay' command leaves a corpse (the reported case: Hassan)."""
    pc = make_pc(level=merc.MAX_LEVEL)  # immortal trust so 'slay' dispatches
    room = pc.in_room
    hassan = spawn_mob(3011, room)  # Hassan

    out = run(pc, "slay hassan")
    assert "cold blood" in out.lower(), "slay did not fire: %r" % out
    assert corpse_in_room(room) is not None, "slay left no corpse"
