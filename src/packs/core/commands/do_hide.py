import random
import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_hide(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("You attempt to hide.\n")

    if ch.is_affected(merc.AFF_HIDE):
        ch.affected_by.rem_bit(merc.AFF_HIDE)

    if random.randint(1, 99) < ch.get_skill("hide"):
        ch.affected_by.set_bit(merc.AFF_HIDE)
        if ch.is_pc:
            ch.check_improve("hide", True, 3)
    else:
        if ch.is_pc:
            ch.check_improve("hide", False, 3)
    return


api.register("hide", do_hide, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
