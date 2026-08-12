import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import game_utils


def do_pecho(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not argument or not arg:
        ch.send("Personal echo what?\n")
        return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("Target not found.\n")
        return
    if victim.trust >= ch.trust != merc.MAX_LEVEL:
        victim.send("personal> ")

    argument = argument.strip()
    victim.send(argument)
    victim.send("\n")
    ch.send("personal> ")
    ch.send(argument)
    ch.send("\n")


api.register("pecho", do_pecho, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
