import logging

logger = logging.getLogger(__name__)

from rom24 import handler_ch
from rom24 import interp
from rom24 import merc
from rom24 import api


def do_east(ctx):
    ch = ctx.ch
    argument = ctx.arg
    handler_ch.move_char(ch, merc.DIR_EAST, False)
    return


api.register("east", do_east, pos=merc.POS_STANDING, level=0, log=merc.LOG_NEVER, show=0)
