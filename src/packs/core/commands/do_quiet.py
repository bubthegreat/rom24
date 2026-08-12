import logging


logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api

# RT quiet blocks out all communication
def do_quiet(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_QUIET):
        ch.send("Quiet mode removed.\n")
        ch.comm.rem_bit(merc.COMM_QUIET)
    else:
        ch.send("From now on, you will only hear says and emotes.\n")
        ch.comm.set_bit(merc.COMM_QUIET)


api.register("quiet", do_quiet, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
