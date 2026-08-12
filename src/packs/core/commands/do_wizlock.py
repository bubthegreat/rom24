import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import settings
from rom24 import handler_game
from rom24 import api


def do_wizlock(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not settings.WIZLOCK:
        handler_game.wiznet("$N has wizlocked the game.", ch, None, 0, 0, 0)
        ch.send("Game wizlocked.\n")
        settings.WIZLOCK = True
    else:
        handler_game.wiznet("$N removes wizlock.", ch, None, 0, 0, 0)
        ch.send("Game un-wizlocked.\n")
        settings.WIZLOCK = False
    return


api.register("wizlock", do_wizlock, pos=merc.POS_DEAD, level=merc.L2, log=merc.LOG_ALWAYS, show=1)
