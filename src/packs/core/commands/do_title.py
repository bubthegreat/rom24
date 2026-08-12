import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import game_utils
from rom24 import api


def do_title(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if not argument:
        ch.send("Change your title to what?\n")
        return
    if len(argument) > 45:
        argument = argument[:45]
    argument = argument.strip()
    game_utils.set_title(ch, argument)
    ch.send("Ok.\n")


api.register("title", do_title, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
