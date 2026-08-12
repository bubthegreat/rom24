import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_autosplit(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if ch.act.is_set(merc.PLR_AUTOSPLIT):
        ch.send("Autosplitting removed.\n")
        ch.act.rem_bit(merc.PLR_AUTOSPLIT)
    else:
        ch.send("Automatic gold splitting set.\n")
        ch.act.set_bit(merc.PLR_AUTOSPLIT)

api.register("autosplit", do_autosplit, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
