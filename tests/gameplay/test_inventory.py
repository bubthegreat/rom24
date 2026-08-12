"""Tier 1: inventory flow — get / drop / give / wield / wear / remove.

Every one of these iterates ``ch.inventory``/``ch.items``, which holds item
IDs (ints), not objects. The recurring bug class is treating an ID as an object
(``item.item_type`` on an int). Smoke passes those; these assert the item
actually moves between room, inventory, another character, and equip slots.
Assertions use item identity (``instance_id``) so leftover same-named items
from earlier tests in the session-scoped world cannot mask a failure.
"""
from helpers import make_pc, spawn_mob, spawn_item, run
from rom24 import merc


def test_get_from_room(booted_world):
    """'get <item>' moves a room item into inventory."""
    pc = make_pc(name="Getter", room_vnum=3001)
    room = pc.in_room
    item = spawn_item(3032, room)          # a bag on the ground
    run(pc, "get bag")
    assert item.instance_id in pc.inventory, "get did not add bag to inventory"
    assert item.instance_id not in room.items, "bag still on the ground after get"


def test_drop_to_room(booted_world):
    """'drop <item>' moves a carried item to the room floor."""
    pc = make_pc(name="Dropper", room_vnum=3005)
    room = pc.in_room
    item = spawn_item(3032, pc)            # bag in inventory
    run(pc, "drop bag")
    assert item.instance_id not in pc.inventory, "bag still carried after drop"
    assert item.instance_id in room.items, "drop did not put bag in the room"


def test_give_to_mob(booted_world):
    """'give <item> <mob>' transfers a carried item to that mob."""
    pc = make_pc(name="Giver", room_vnum=3014)
    room = pc.in_room
    mob = spawn_mob(3011, room)            # Hassan
    item = spawn_item(3032, pc)            # bag
    run(pc, "give bag hassan")
    assert item.instance_id in mob.inventory, "mob did not receive the bag"
    assert item.instance_id not in pc.inventory, "giver still carries the bag"


def test_wield_and_remove_weapon(booted_world):
    """'wield' fills the main hand; 'remove' empties it."""
    pc = make_pc(name="Wielder", room_vnum=3001)
    weapon = spawn_item(3022, pc)          # a long sword
    run(pc, "wield sword")
    assert pc.get_eq("main_hand") is not None, "wield left main hand empty"
    assert pc.get_eq("main_hand").instance_id == weapon.instance_id, "wrong weapon wielded"
    run(pc, "remove sword")
    assert pc.get_eq("main_hand") is None, "remove left the weapon equipped"
    assert weapon.instance_id in pc.inventory, "removed weapon not back in inventory"


def test_wear_armor(booted_world):
    """'wear' equips armor into its body slot."""
    pc = make_pc(name="Armorer", room_vnum=3001)
    vest = spawn_item(616, pc)             # a leather vest (ITEM_ARMOR, torso)
    run(pc, "wear vest")
    assert vest.instance_id in pc.equipped.values(), "vest was not equipped"
