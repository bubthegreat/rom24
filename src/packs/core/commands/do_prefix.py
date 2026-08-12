import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_prefix(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        if not ch.prefix:
            ch.send("You have no prefix to clear.\n")
            return
        ch.send("Prefix removed.\n")
        ch.prefix = ""
        return
    if ch.prefix:
        ch.send("Prefix changed to %s.\n" % argument)
        ch.prefix = ""
    else:
        ch.send("Prefix set to %s.\n" % argument)
    ch.prefix = argument


def do_prefi(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("You cannot abbreviate the prefix command.\n")
    return


api.register("prefix", do_prefix, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
api.register("prefi", do_prefi, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=0)
