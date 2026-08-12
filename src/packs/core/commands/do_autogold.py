import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import state_checks


def do_autogold(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return

    if state_checks.IS_SET(ch.act, merc.PLR_AUTOGOLD):
        ch.send("Autogold removed.\n")
        ch.act.rem_bit(merc.PLR_AUTOGOLD)
    else:
        ch.send("Automatic gold looting set.\n")
        ch.act.set_bit(merc.PLR_AUTOGOLD)

api.register("autogold", do_autogold, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
