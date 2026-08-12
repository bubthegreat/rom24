import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp


def do_noloot(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if ch.act.is_set(merc.PLR_CANLOOT):
        ch.send("Your corpse is now safe from thieves.\n")
        ch.act.rem_bit(merc.PLR_CANLOOT)
    else:
        ch.send("Your corpse may now be looted.\n")
        ch.act.set_bit(merc.PLR_CANLOOT)


api.register("noloot", do_noloot, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
