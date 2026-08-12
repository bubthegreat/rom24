import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_brief(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_BRIEF):
        ch.send("Full descriptions activated.\n")
        ch.comm.rem_bit(merc.COMM_BRIEF)
    else:
        ch.send("Short descriptions activated.\n")
        ch.comm.set_bit(merc.COMM_BRIEF)

api.register("brief", do_brief, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
