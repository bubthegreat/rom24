import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_holylight(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if ch.act.is_set(merc.PLR_HOLYLIGHT):
        ch.act.rem_bit(merc.PLR_HOLYLIGHT)
        ch.send("Holy light mode off.\n")
    else:
        ch.act.set_bit(merc.PLR_HOLYLIGHT)
        ch.send("Holy light mode on.\n")
    return


api.register("holylight", do_holylight, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
