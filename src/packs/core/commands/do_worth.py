import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_worth(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        ch.send("You have %ld gold and %ld silver.\n" % (ch.gold, ch.silver))
        return
    ch.send(
        "You have %ld gold, %ld silver, and %d experience (%d exp to level).\n"
        % (
            ch.gold,
            ch.silver,
            ch.exp,
            (ch.level + 1) * ch.exp_per_level(ch.points) - ch.exp,
        )
    )


api.register("worth", do_worth, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
