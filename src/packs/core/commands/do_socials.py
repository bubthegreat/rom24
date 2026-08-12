import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp


# RT does socials
def do_socials(ctx):
    ch = ctx.ch
    argument = ctx.arg
    for col, social in enumerate(merc.social_list):
        ch.send("%-12s" % social.name)
        if col % 6 == 0:
            ch.send("\n")
    if len(merc.social_list) % 6 != 0:
        ch.send("\n")
    return


api.register("socials", do_socials, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
