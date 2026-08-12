"""Tier 2: spellcasting — mana cost, damage, healing, mana gate.

98 spells, previously zero behavior tests. Casting is subject to a random skill
roll, so the effect-based checks retry a few times; the mana-cost and mana-gate
checks are deterministic (they hold whether or not the roll succeeds).
"""
from helpers import make_pc, spawn_mob, run
from rom24 import merc


def test_cast_deducts_mana(booted_world):
    """Casting a known spell spends mana (success or failure both cost)."""
    pc = make_pc(name="Manaburner", level=30, room_vnum=3001)
    pc.learned["armor"] = 100
    pc.mana = 100
    before = pc.mana
    run(pc, "cast armor")
    assert pc.mana < before, "cast spent no mana (%d -> %d)" % (before, pc.mana)


def test_cast_without_mana_refused(booted_world):
    """Casting with no mana is refused, not silently dropped."""
    pc = make_pc(name="Drained", level=30, room_vnum=3001)
    pc.learned["armor"] = 100
    pc.mana = 0
    out = run(pc, "cast armor")
    assert "enough mana" in out.lower(), "no-mana cast not refused: %r" % out


def test_offensive_spell_damages(booted_world):
    """An attack spell lowers the target's hit points."""
    pc = make_pc(name="Missiler", level=40, room_vnum=3005)
    room = pc.in_room
    victim = spawn_mob(3068, room)
    # Combat tests share room 3005; give this victim a unique keyword so the
    # cast resolves to it and not a leftover cityguard from another test.
    victim.name = "spelltarget"
    victim.hit = victim.max_hit = 300
    pc.learned["magic missile"] = 100
    for _ in range(6):
        pc.mana = 100
        run(pc, "cast 'magic missile' spelltarget")
        if victim.hit < 300:
            break
    assert victim.hit < 300, "magic missile never damaged the target"


def test_heal_restores_hp(booted_world):
    """The heal spell raises the caster's hit points."""
    pc = make_pc(name="Mender", level=40, room_vnum=3001)
    pc.learned["heal"] = 100
    pc.max_hit = 200
    for _ in range(6):
        pc.hit = 1
        pc.mana = 100
        run(pc, "cast heal")
        if pc.hit > 1:
            break
    assert pc.hit > 1, "heal never restored any hit points"
