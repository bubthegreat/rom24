"""Shared world-memory report used by the do_memory and do_dump commands.

Lives in the engine (not in a command module) so multiple commands can share it
without importing each other — command modules load by file path inside a pack
and are not importable as ``rom24.commands.<name>``.
"""
from rom24 import instance


def memory_lines():
    """Build the stock-style memory report: one world-data count per line."""
    return [
        "Areas   %5d" % len(instance.area_templates),
        "Helps   %5d" % len(instance.helps),
        "Socials %5d" % len(instance.socials),
        "Resets  %5d" % len(instance.resets),
        "Mobs    %5d" % len(instance.npc_templates),
        "(in use)%5d" % len(instance.characters),
        "Objs    %5d" % len(instance.item_templates),
        "(in use)%5d" % len(instance.items),
        "Rooms   %5d" % len(instance.room_templates),
        "Shops   %5d" % len(instance.shop_templates),
    ]
