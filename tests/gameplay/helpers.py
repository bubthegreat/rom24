"""Gameplay test harness: drive commands through interpret(), capture output.

Tests build a real playable Pc + mobs/items in a room, run command STRINGS via
``ch.interpret(...)`` (the full dispatch path -> ctx shim -> command logic), and
assert on captured output + world state.
"""
from rom24 import handler_pc, const, merc, instance, object_creator


class _Desc:
    """Minimal descriptor stand-in (commands like do_look bail if not ch.desc)."""

    def __init__(self):
        self.original = None
        self.snoop_by = None

    def __bool__(self):
        return True


def make_pc(name="Tester", guild="warrior", race="human",
            room_vnum=merc.ROOM_VNUM_SCHOOL, level=10):
    """A real playable Pc with a capturing send, placed in a room."""
    pc = handler_pc.Pc(name)
    pc.is_pc = True
    pc.captured = []
    pc.send = lambda text: pc.captured.append(text)
    pc.desc = _Desc()

    pc.race = const.race_table[race]
    pc._race = race
    pc.guild = const.guild_table[guild]
    for i in range(merc.MAX_STATS):
        pc.perm_stat[i] = 18
    pc.level = level
    pc.trust = level
    pc.position = merc.POS_STANDING
    pc.learned = {}
    pc.group_known = {}

    room = _room(room_vnum)
    room.put(pc)
    return pc


def _room(vnum):
    room_id = instance.instances_by_room[vnum][0]
    return instance.global_instances[room_id]


def spawn_mob(vnum, room, level=None):
    mob = object_creator.create_mobile(instance.npc_templates[vnum])
    mob.position = merc.POS_STANDING
    if level is not None:
        mob.level = level
    room.put(mob)
    return mob


def spawn_item(vnum, dest):
    """Create an item and put it in a room or a container/inventory (anything
    with .put)."""
    item = object_creator.create_item(instance.item_templates[vnum], 0)
    dest.put(item)
    return item


def run(pc, command):
    """Interpret a command string; return only the output it produced."""
    start = len(pc.captured)
    pc.interpret(command)
    return "".join(pc.captured[start:])


def room_items(room):
    return [instance.items[i] for i in room.items if i in instance.items]


def corpse_in_room(room):
    for item in room_items(room):
        it = getattr(item, "item_type", "")
        if it in (merc.ITEM_CORPSE_NPC, merc.ITEM_CORPSE_PC) or "corpse" in (item.name or "").lower():
            return item
    return None
