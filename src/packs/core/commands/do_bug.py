import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import game_utils
from rom24 import interp
from rom24 import api
from rom24 import settings


def do_bug(ctx):
    ch = ctx.ch
    argument = ctx.arg
    game_utils.append_file(ch, settings.BUG_FILE, argument)
    ch.send("Bug logged.\n")
    return

api.register("bug", do_bug, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
