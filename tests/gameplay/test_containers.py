"""Tier 2: container mechanics — close/open, and put blocked while closed.

A closed container must refuse 'put' instead of swallowing the item, and 'open'
must let it back in. The bag (vnum 3032) is made closeable for the test.
"""
from helpers import make_pc, spawn_item, run
from rom24 import merc, state_checks


def _closeable_bag(pc):
    bag = spawn_item(3032, pc)
    bag.value[1] = merc.CONT_CLOSEABLE
    return bag


def test_close_then_open(booted_world):
    """'close' sets the closed flag; 'open' clears it."""
    pc = make_pc(name="Closer", room_vnum=3001)
    bag = _closeable_bag(pc)
    run(pc, "close bag")
    assert state_checks.IS_SET(bag.value[1], merc.CONT_CLOSED), "close did not close the bag"
    run(pc, "open bag")
    assert not state_checks.IS_SET(bag.value[1], merc.CONT_CLOSED), "open did not open the bag"


def test_put_into_closed_fails(booted_world):
    """Putting into a closed container is refused and drops nothing in."""
    pc = make_pc(name="Stuffer", room_vnum=3001)
    bag = _closeable_bag(pc)
    run(pc, "close bag")
    sword = spawn_item(3022, pc)
    out = run(pc, "put sword bag")
    assert "closed" in out.lower(), "closed container did not refuse put: %r" % out
    assert sword.instance_id not in bag.inventory, "item went into a closed container"


def test_put_into_open_succeeds(booted_world):
    """Putting into an open container moves the item inside."""
    pc = make_pc(name="Filler", room_vnum=3001)
    bag = _closeable_bag(pc)
    sword = spawn_item(3022, pc)
    run(pc, "put sword bag")
    assert sword.instance_id in bag.inventory, "item did not go into the open container"
