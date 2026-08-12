import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_combine(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_COMBINE):
        ch.send("Long inventory selected.\n")
        ch.comm.rem_bit(merc.COMM_COMBINE)
    else:
        ch.send("Combined inventory selected.\n")
        ch.comm.set_bit(merc.COMM_COMBINE)

api.register("combine", do_combine, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
