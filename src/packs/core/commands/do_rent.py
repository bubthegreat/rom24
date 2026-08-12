import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_rent(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("There is no rent here.  Just save and quit.\n")
    return


api.register("rent", do_rent, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=0)
