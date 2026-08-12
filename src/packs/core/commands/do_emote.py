import logging

logger = logging.getLogger(__name__)

from rom24 import handler_game
from rom24 import merc
from rom24 import interp
from rom24 import api


def do_emote(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not ch.is_npc() and ch.comm.is_set(merc.COMM_NOEMOTE):
        ch.send("You can't show your emotions.\n")
        return
    if not argument:
        ch.send("Emote what?\n")
        return
    handler_game.act("$n $T", ch, None, argument, merc.TO_ROOM)
    handler_game.act("$n $T", ch, None, argument, merc.TO_CHAR)
    return


api.register("emote", do_emote, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
api.register(",", do_emote, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=0)
