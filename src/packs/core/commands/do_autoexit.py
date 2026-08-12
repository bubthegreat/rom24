import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_autoexit(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if ch.act.is_set(merc.PLR_AUTOEXIT):
        ch.send("Exits will no longer be displayed.\n")
        ch.act.rem_bit(merc.PLR_AUTOEXIT)
    else:
        ch.send("Exits will now be displayed.\n")
        ch.act.set_bit(merc.PLR_AUTOEXIT)

api.register("autoexit", do_autoexit, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
