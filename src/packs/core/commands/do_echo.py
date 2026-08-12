import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import nanny
from rom24 import api


def do_echo(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Global echo what?\n")
        return
    for d in merc.descriptor_list:
        if d.is_connected(nanny.con_playing):
            if d.character.trust >= ch.trust:
                d.send("global> ")
            d.send(argument + "\n")
    return


api.register("gecho", do_echo, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
