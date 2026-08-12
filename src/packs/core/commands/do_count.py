import logging

logger = logging.getLogger(__name__)

from rom24 import handler_ch
from rom24 import merc
from rom24 import interp
from rom24 import nanny
from rom24 import api

# for  keeping track of the player count
max_on = 0


def do_count(ctx):
    ch = ctx.ch
    argument = ctx.arg
    global max_on
    count = len(
        [
            d
            for d in merc.descriptor_list
            if d.is_connected(nanny.con_playing) and ch.can_see(handler_ch.CH(d))
        ]
    )
    max_on = max(count, max_on)

    if max_on == count:
        ch.send("There are %d characters on, the most so far today.\n" % count)
    else:
        ch.send(
            "There are %d characters on, the most on today was %d.\n" % (count, max_on)
        )


api.register("count", do_count, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
