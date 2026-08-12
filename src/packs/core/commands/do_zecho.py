import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import nanny
from rom24 import api


def do_zecho(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Zone echo what?\n")
        return
    for d in merc.descriptor_list:
        if (
            d.is_connected(nanny.con_playing)
            and d.character.in_room
            and ch.in_room
            and d.character.in_room.area == ch.in_room.area
        ):
            if d.character.trust >= ch.trust:
                d.send("zone> ")
            d.send(argument + "\n")


api.register("zecho", do_zecho, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
