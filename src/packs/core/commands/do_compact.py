import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_compact(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_COMPACT):
        ch.send("Compact mode removed.\n")
        ch.comm.rem_bit(merc.COMM_COMPACT)
    else:
        ch.send("Compact mode set.\n")
        ch.comm.set_bit(merc.COMM_COMPACT)


api.register("compact", do_compact, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
