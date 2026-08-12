import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_bamfin(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not ch.is_npc():
        if not argument:
            ch.send("Your poofin is %s\n" % ch.bamfin)
            return
        if ch.name not in argument:
            ch.send("You must include your name.\n")
            return
        ch.bamfin = argument
        ch.send("Your poofin is now %s\n" % ch.bamfin)
    return

api.register("poofin", do_bamfin, pos=merc.POS_DEAD, level=merc.L8, log=merc.LOG_NORMAL, show=1)
