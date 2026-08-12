import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import instance


def do_areas(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if argument:
        ch.send("No argument is used with this command.\n")
        return
    col = 0
    for iArea in instance.areas.values():
        ch.send("%-39s" % iArea.credits)
        col += 1
        if col % 2 == 0:
            ch.send("\n")

api.register("areas", do_areas, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
