"""Behavior tests for Midgaard's bundled mob progs (progs.py).

These live WITH the area, so shipping Midgaard ships its own proof that the
wizard (vnum 3000) progs fire. The area contract test (tests/test_area_contract.py)
requires every area that has progs to carry tests like these.

Uses the shared gameplay harness: ``booted_world`` (repo-root conftest) and the
``helpers`` module (on sys.path via that same conftest).
"""
from helpers import make_pc, spawn_mob, run
from rom24 import instance


def test_wizard_answers_hello(booted_world):
    """Saying 'hello' near the wizard triggers his on_speech greeting."""
    pc = make_pc(name="Greeter", room_vnum=3001)
    spawn_mob(3000, pc.in_room)                 # the wizard
    out = run(pc, "say hello")
    assert "arcane arts" in out.lower(), "wizard did not answer 'hello': %r" % out


def test_wizard_greets_newcomer(booted_world):
    """Entering the wizard's room triggers his on_greet reaction."""
    pc = make_pc(name="Newcomer", room_vnum=3001)   # Temple, south -> Temple Square
    square = instance.global_instances[instance.instances_by_room[3005][0]]
    spawn_mob(3000, square)                     # wizard waiting in the square
    out = run(pc, "south")
    assert "arcane curiosity" in out.lower(), "wizard did not greet newcomer: %r" % out
