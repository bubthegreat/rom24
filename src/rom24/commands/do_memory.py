import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import instance


def _memory_lines():
    """Build the stock-style memory report lines.

    Stock ROM 2.4 reports counts of the loaded world data structures. This port
    tracks templates (prototypes) and live instances in ``instance``. We report
    the analogous counts, one stat per line.
    """
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


def do_memory(ch, argument):
    for line in _memory_lines():
        ch.send(line + "\n")


interp.register_command(
    interp.cmd_type("memory", do_memory, merc.POS_DEAD, merc.IM, merc.LOG_NORMAL, 1)
)
