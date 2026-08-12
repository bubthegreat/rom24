import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_wizhelp(ctx):
    ch = ctx.ch
    argument = ctx.arg
    col = 0
    for key, cmd in interp.cmd_table.items():
        try:
            if merc.LEVEL_HERO <= cmd.level <= ch.trust and cmd.show:
                ch.send("%-12s" % key)
                col += 1
                if col % 6 == 0:
                    ch.send("\n")
        except:
            logger.exception("Error parsing %s: %s", key, cmd)
    if col % 6 != 0:
        ch.send("\n")
    return


api.register("wizhelp", do_wizhelp, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
