import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import handler_ch


def do_inventory(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("You are carrying:\n")
    handler_ch.show_list_to_char(ch.inventory, ch, True, True)
    return


api.register("inventory", do_inventory, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
