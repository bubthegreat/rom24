"""Tier 3: persistence — deep save/load round-trip, and PC death/respawn.

test_e2e_smoke round-trips only name + level. This asserts the parts most
likely to break the JSON codec survive: coin, experience, permanent stats,
carried inventory, and an equipped weapon. Death/respawn checks a slain player
lands at the altar, stays alive, and leaves a corpse behind.
"""
import tempfile

from helpers import make_pc, spawn_item, corpse_in_room
from rom24 import merc, instance, handler_pc, settings, fight


def test_deep_save_load_roundtrip(booted_world):
    """Coin, xp, stats, inventory, and equipment survive a save/load."""
    orig_dir = settings.PLAYER_DIR
    settings.PLAYER_DIR = tempfile.mkdtemp()
    try:
        pc = make_pc(name="Roundtripper", room_vnum=3001, level=25)
        pc.gold = 42
        pc.silver = 7
        pc.exp = 12345
        for i in range(merc.MAX_STATS):
            pc.perm_stat[i] = 17
        spawn_item(3032, pc)                       # a bag in inventory
        sword = spawn_item(3022, pc)               # a long sword, wielded
        pc.equip(sword, True)
        inv_before = len(list(pc.inventory))

        pc.save(force=True)
        loaded = handler_pc.Pc.load("Roundtripper")

        assert loaded is not None, "load returned nothing"
        assert loaded.gold == 42 and loaded.silver == 7, "coin not preserved"
        assert loaded.exp == 12345, "experience not preserved"
        assert loaded.level == 25, "level not preserved"
        assert loaded.perm_stat[0] == 17, "permanent stats not preserved"
        assert len(list(loaded.inventory)) == inv_before, "inventory count changed"
        mh = loaded.get_eq("main_hand")
        assert mh is not None and "sword" in mh.name, "equipped weapon not preserved"
    finally:
        settings.PLAYER_DIR = orig_dir


def test_pc_death_respawns_at_altar(booted_world):
    """A slain player respawns at the altar, alive, leaving a corpse behind."""
    pc = make_pc(name="Doomed", room_vnum=3005, level=10)
    death_room = instance.global_instances[instance.instances_by_room[3005][0]]
    pc.hit = 1
    fight.raw_kill(pc)

    assert pc.in_room.vnum == merc.ROOM_VNUM_ALTAR, (
        "did not respawn at altar (in room %s)" % pc.in_room.vnum
    )
    assert pc.position > merc.POS_DEAD and pc.hit > 0, "player did not survive death"
    assert corpse_in_room(death_room) is not None, "no corpse left where the player died"
