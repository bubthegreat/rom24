import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import handler_item
from rom24 import api


def do_equipment(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("You are using:\n")
    found = False
    for slot, item_id in ch.equipped.items():
        item = ch.get_eq(slot)
        if not item:
            continue
        if (
            item.flags.two_handed
            and ch.equipped["off_hand"] == item.instance_id
            and "off_hand" in slot
        ):
            continue
        else:
            ch.send(merc.eq_slot_strings[slot])
            if ch.can_see_item(item):
                ch.send(handler_item.format_item_to_char(item, ch, True) + "\n")
            else:
                ch.send("something.\n")
            found = True
    if not found:
        ch.send("Nothing.\n")


api.register("equipment", do_equipment, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
