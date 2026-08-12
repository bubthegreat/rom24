import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import handler_ch
from rom24 import interp
from rom24 import merc


def do_north(ctx):
    ch = ctx.ch
    argument = ctx.arg
    handler_ch.move_char(ch, merc.DIR_NORTH, False)
    return


api.register("north", do_north, pos=merc.POS_STANDING, level=0, log=merc.LOG_NEVER, show=0)
