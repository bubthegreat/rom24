import logging

logger = logging.getLogger(__name__)

from rom24 import game_utils
from rom24 import merc
from rom24 import interp
from rom24 import instance
from rom24 import api


def do_wear(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Wear, wield, or hold what?\n")
        return
    if arg == "all":
        for item_id in ch.items:
            item = instance.items.get(item_id, None)
            if ch.can_see_item(item):
                ch.equip(item, False, verbose_all=True)
        return
    else:
        item = ch.get_item_carry(arg, ch)
        if not item:
            ch.send("You do not have that item.\n")
            return
        ch.equip(item, True, verbose=True, verbose_all=True)
    return


api.register("wield", do_wear, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
api.register("hold", do_wear, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
api.register("wear", do_wear, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
