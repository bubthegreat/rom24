import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_commands(ctx):
    ch = ctx.ch
    argument = ctx.arg
    col = 0
    for key, cmd in interp.cmd_table.items():
        if cmd.level < merc.LEVEL_HERO and cmd.level <= ch.trust and cmd.show:
            ch.send("%-12s" % key)
            col += 1
            if col % 6 == 0:
                ch.send("\n")
    if col % 6 != 0:
        ch.send("\n")
    return


api.register("commands", do_commands, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
