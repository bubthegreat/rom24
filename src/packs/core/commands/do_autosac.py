import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_autosac(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if ch.act.is_set(merc.PLR_AUTOSAC):
        ch.send("Autosacrificing removed.\n")
        ch.act.rem_bit(merc.PLR_AUTOSAC)
    else:
        ch.send("Automatic corpse sacrificing set.\n")
        ch.act.set_bit(merc.PLR_AUTOSAC)

api.register("autosac", do_autosac, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
