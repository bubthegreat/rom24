import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import db


def do_freset(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not ch.in_area:
        ch.send("You are not in an area. And that's really weird.\n")
        return
    db.reset_area(ch.in_area)
    ch.send("Area reset.\n")


api.register("freset", do_freset, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
