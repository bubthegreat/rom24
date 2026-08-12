import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import handler_ch


def do_nofollow(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    if ch.act.is_set(merc.PLR_NOFOLLOW):
        ch.send("You now accept followers.\n")
        ch.act.rem_bit(merc.PLR_NOFOLLOW)
    else:
        ch.send("You no longer accept followers.\n")
        ch.act.set_bit(merc.PLR_NOFOLLOW)
        handler_ch.die_follower(ch)


api.register("nofollow", do_nofollow, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
