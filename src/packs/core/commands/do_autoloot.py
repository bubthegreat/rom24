import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_autoloot(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if ch.act.is_set(merc.PLR_AUTOLOOT):
        ch.send("Autolooting removed.\n")
        ch.act.rem_bit(merc.PLR_AUTOLOOT)
    else:
        ch.send("Automatic corpse looting set.\n")
        ch.act.set_bit(merc.PLR_AUTOLOOT)

api.register("autoloot", do_autoloot, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
