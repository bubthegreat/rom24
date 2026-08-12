import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_bamfout(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not ch.is_npc():
        if not argument:
            ch.send("Your poofout is %s\n" % ch.bamfout)
            return
        if ch.name not in argument:
            ch.send("You must include your name.\n")
            return
        ch.bamfout = argument
        ch.send("Your poofout is now %s\n" % ch.bamfout)
    return

api.register("poofout", do_bamfout, pos=merc.POS_DEAD, level=merc.L8, log=merc.LOG_NORMAL, show=1)
