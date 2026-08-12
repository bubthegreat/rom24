import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


# afk command
def do_afk(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_AFK):
        ch.send("AFK mode removed. Type 'replay' to see tells.\n")
        ch.comm.rem_bit(merc.COMM_AFK)
    else:
        ch.send("You are now in AFK mode.\n")
        ch.comm.set_bit(merc.COMM_AFK)

api.register("afk", do_afk, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
