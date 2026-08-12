import logging

logger = logging.getLogger(__name__)

from rom24 import game_utils
from rom24 import merc
from rom24 import interp
from rom24 import api

# 'Wimpy' originally by Dionysos.
def do_wimpy(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        wimpy = ch.max_hit // 5
    else:
        wimpy = int(arg)
    if wimpy < 0:
        ch.send("Your courage exceeds your wisdom.\n")
        return
    if wimpy > ch.max_hit // 2:
        ch.send("Such cowardice ill becomes you.\n")
        return
    ch.wimpy = wimpy
    ch.send("Wimpy set to %d hit points.\n" % wimpy)
    return


api.register("wimpy", do_wimpy, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
