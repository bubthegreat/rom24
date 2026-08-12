import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import handler_game
from rom24 import instance


def do_gtell(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Tell your group what?\n")
        return
    if ch.comm.is_set(merc.COMM_NOTELL):
        ch.send("Your message didn't get through!\n")
        return
    found = False
    for gch in instance.characters.values():
        if gch.is_same_group(ch):
            handler_game.act(
                "$n tells the group '$t'",
                ch,
                argument,
                gch,
                merc.TO_VICT,
                merc.POS_SLEEPING,
            )
            found = True
    if found:
        handler_game.act(
            "$n tells the group '$t'", ch, argument, ch, merc.TO_CHAR, merc.POS_SLEEPING
        )
    else:
        ch.send("You do not have a group.\n")
    return


api.register("gtell", do_gtell, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
api.register(";", do_gtell, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=0)
