"""Object / container behavior."""
from helpers import make_pc, spawn_item, run


def test_look_in_container_shows_contents(booted_world):
    pc = make_pc()
    room = pc.in_room
    pit = spawn_item(3010, room)      # 'pit' — an open container
    inner = spawn_item(3032, pit)     # a 'bag' placed inside the pit

    out = run(pc, "look in pit")
    assert inner.name.split()[0].lower() in out.lower() or "holds" in out.lower(), (
        "look in the pit showed nothing: %r" % out
    )
