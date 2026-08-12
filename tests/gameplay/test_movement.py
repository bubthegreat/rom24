"""Tier 1: movement — a direction moves you; a closed door blocks you.

Smoke only proves 'north' does not raise. These assert the player actually
changes rooms, and that a closed exit stops the move instead of silently
teleporting through it.
"""
from helpers import make_pc, run
from rom24 import merc


def test_move_changes_room(booted_world):
    """Walking a valid exit moves the player into the target room."""
    pc = make_pc(name="Walker", room_vnum=3001)   # Temple of Mota
    before = pc.in_room.instance_id
    run(pc, "south")
    assert pc.in_room.instance_id != before, "south did not change rooms"


def test_closed_door_blocks_movement(booted_world):
    """A closed exit refuses the move and leaves the player in place."""
    pc = make_pc(name="Doortester", room_vnum=3001)
    room = pc.in_room
    pexit = room.exit[merc.DIR_SOUTH]
    pexit.exit_info.set_bit(merc.EX_CLOSED)
    try:
        before = pc.in_room.instance_id
        out = run(pc, "south")
        assert pc.in_room.instance_id == before, "moved through a closed door"
        assert "closed" in out.lower(), "no 'closed' message: %r" % out
    finally:
        pexit.exit_info.rem_bit(merc.EX_CLOSED)
