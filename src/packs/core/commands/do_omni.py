import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp


def do_omni(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.act.is_set(merc.PLR_OMNI):
        ch.send("Omnimode removed\n")
        ch.act.rem_bit(merc.PLR_OMNI)
    else:
        ch.send("Omnimode enabled.\n")
        ch.act.set_bit(merc.PLR_OMNI)


api.register("omni", do_omni, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
