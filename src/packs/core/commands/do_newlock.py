import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import settings
from rom24 import handler_game

# RT anti-newbie code
def do_newlock(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not settings.NEWLOCK:
        handler_game.wiznet("$N locks out new characters.", ch, None, 0, 0, 0)
        ch.send("New characters have been locked out.\n")
        settings.NEWLOCK = True
    else:
        handler_game.wiznet("$N allows new characters back in.", ch, None, 0, 0, 0)
        ch.send("Newlock removed.\n")
        settings.NEWLOCK = False
    return


api.register("newlock", do_newlock, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
