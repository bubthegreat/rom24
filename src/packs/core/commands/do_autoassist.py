import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_autoassist(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if ch.act.is_set(merc.PLR_AUTOASSIST):
        ch.send("Autoassist removed.\n")
        ch.act.rem_bit(merc.PLR_AUTOASSIST)
    else:
        ch.send("You will now assist when needed.\n")
        ch.act.set_bit(merc.PLR_AUTOASSIST)

api.register("autoassist", do_autoassist, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
