import logging

logger = logging.getLogger(__name__)

from rom24 import interp
from rom24 import merc
from rom24 import api


# Contributed by Alander.
def do_visible(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.affect_strip("invisibility")
    ch.affect_strip("mass invis")
    ch.affect_strip("sneak")
    ch.affected_by.rem_bit(merc.AFF_HIDE)
    ch.affected_by.rem_bit(merc.AFF_INVISIBLE)
    ch.affected_by.rem_bit(merc.AFF_SNEAK)
    ch.send("Ok.\n")


api.register("visible", do_visible, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
