import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import game_utils


def do_remove(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Remove what?\n")
        return
    if arg == "all":
        for loc, item_id in ch.equipped.items():
            if item_id:
                ch.unequip(loc, True)
        return
    else:
        item = ch.get_item_wear(arg)
        if not item:
            ch.send("You are not wearing %s.\n" % arg)
            return
        ch.unequip(item.equipped_to, True)
        return


api.register("remove", do_remove, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
