import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import nanny


def do_recho(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Local echo what?\n")
        return
    for d in merc.descriptor_list:
        if d.is_connected(nanny.con_playing) and d.character.in_room == ch.in_room:
            if d.character.trust >= ch.trust:
                d.send("local> ")
            d.send(argument + "\n")

    return


api.register("echo", do_recho, pos=merc.POS_DEAD, level=merc.L6, log=merc.LOG_ALWAYS, show=1)
