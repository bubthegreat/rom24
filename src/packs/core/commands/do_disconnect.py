import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import comm
from rom24 import game_utils
from rom24 import handler_game
from rom24 import api


def do_disconnect(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Disconnect whom?\n")
        return
    if arg.isdigit():
        desc = int(arg)
        for d in merc.descriptor_list:
            if d.descriptor == desc:
                comm.close_socket(d)
                ch.send("Ok.\n")
                return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if victim.desc is None:
        handler_game.act(
            "$N doesn't have a descriptor.", ch, None, victim, merc.TO_CHAR
        )
        return
    for d in merc.descriptor_list:
        if d == victim.desc:
            comm.close_socket(d)
            ch.send("Ok.\n")
            return
    logger.warn("BUG: Do_disconnect: desc not found.")
    ch.send("Descriptor not found!\n")
    return


api.register("disconnect", do_disconnect, pos=merc.POS_DEAD, level=merc.L3, log=merc.LOG_ALWAYS, show=1)
