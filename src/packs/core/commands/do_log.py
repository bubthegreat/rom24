import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import game_utils
from rom24 import state_checks


def do_log(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Log whom?\n")
        return
    if arg == "all":
        # TODO: fix this by either adding it to merc, or figuring out an alternative
        if fLogAll:
            fLogAll = False
            ch.send("Log ALL off.\n")
        else:
            fLogAll = True
            ch.send("Log ALL on.\n")
        return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if victim.is_npc():
        ch.send("Not on NPC's.\n")
        return
    # No level check, gods can log anyone.
    if victim.act.is_set(merc.PLR_LOG):
        victim.act = victim.act.rem_bit(merc.PLR_LOG)
        ch.send("LOG removed.\n")
    else:
        victim.act = state_checks.SET_BIT(victim.act, merc.PLR_LOG)
        ch.send("LOG set.\n")
    return


api.register("log", do_log, pos=merc.POS_DEAD, level=merc.L1, log=merc.LOG_ALWAYS, show=1)
