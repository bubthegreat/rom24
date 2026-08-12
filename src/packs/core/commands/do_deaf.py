import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


# RT deaf blocks out all shouts
def do_deaf(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_DEAF):
        ch.send("You can now hear tells again.\n")
        ch.comm.rem_bit(merc.COMM_DEAF)
    else:
        ch.send("From now on, you won't hear tells.\n")
        ch.comm.set_bit(merc.COMM_DEAF)


api.register("deaf", do_deaf, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
