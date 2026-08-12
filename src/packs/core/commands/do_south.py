import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import handler_ch
from rom24 import interp
from rom24 import merc


def do_south(ctx):
    ch = ctx.ch
    argument = ctx.arg
    handler_ch.move_char(ch, merc.DIR_SOUTH, False)
    return


api.register("south", do_south, pos=merc.POS_STANDING, level=0, log=merc.LOG_NEVER, show=0)
