import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import nanny
from rom24 import handler_game
from rom24 import state_checks
from rom24 import api


def do_yell(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.comm.is_set(merc.COMM_NOSHOUT):
        ch.send("You can't yell.\n")
        return
    if not argument:
        ch.send("Yell what?\n")
        return
    handler_game.act("You yell '$t'", ch, argument, None, merc.TO_CHAR)
    for d in merc.descriptor_list:
        if (
            d.is_connected(nanny.con_playing)
            and d.character != ch
            and d.character.in_room is not None
            and d.character.in_room.area == ch.in_room.area
            and not state_checks.IS_SET(d.character.comm, merc.COMM_QUIET)
        ):
            handler_game.act("$n yells '$t'", ch, argument, d.character, merc.TO_VICT)


api.register("yell", do_yell, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
