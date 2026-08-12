import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp


def do_show(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_SHOW_AFFECTS):
        ch.send("Affects will no longer be shown in score.\n")
        ch.comm.rem_bit(merc.COMM_SHOW_AFFECTS)
    else:
        ch.send("Affects will now be shown in score.\n")
        ch.comm.set_bit(merc.COMM_SHOW_AFFECTS)


api.register("show", do_show, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
