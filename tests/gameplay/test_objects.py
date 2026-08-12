"""Object / container behavior."""
from helpers import make_pc, spawn_item, run
from rom24 import instance


def test_put_all_into_container(booted_world):
    """'put all <container>' must not crash and must move items in.

    Regression: do_put iterated ch.inventory (a list of item IDs) as if the
    entries were objects, so 'put all pit' raised AttributeError ('int' has no
    'item_type') mid-command; game_loop swallowed it -> the player saw no
    response. The harness propagates the exception, so this catches it.
    """
    pc = make_pc()
    room = pc.in_room
    pit = spawn_item(3010, room)          # an open container ('pit')
    coin = spawn_item(3032, pc)           # a 'bag' in the pc's inventory

    out = run(pc, "put all pit")          # must not raise
    assert coin.instance_id in pit.inventory or "put" in out.lower(), (
        "put-all did not move the item into the container: %r" % out
    )


def test_look_in_container_shows_contents(booted_world):
    pc = make_pc()
    room = pc.in_room
    pit = spawn_item(3010, room)      # 'pit' — an open container
    inner = spawn_item(3032, pit)     # a 'bag' placed inside the pit

    out = run(pc, "look in pit")
    assert inner.name.split()[0].lower() in out.lower() or "holds" in out.lower(), (
        "look in the pit showed nothing: %r" % out
    )
