import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import const
from rom24 import interp
from rom24 import api


def do_groups(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    col = 0

    if not argument:
        # show all groups
        for gn, group in const.group_table.items():
            if gn in ch.group_known:
                ch.send("%-20s " % group.name)
                col += 1
                if col % 3 == 0:
                    ch.send("\n")
        if col % 3 != 0:
            ch.send("\n")
        ch.send("Creation points: %d\n" % ch.points)
        return

    if "all" == argument.lower():
        for gn, group in const.group_table.items():
            ch.send("%-20s " % group.name)
            col += 1
            if col % 3 == 0:
                ch.send("\n")
        if col % 3 != 0:
            ch.send("\n")
        return

    # show the sub-members of a group
    if argument.lower() not in const.group_table:
        ch.send("No group of that name exist.\n")
        ch.send("Type 'groups all' or 'info all' for a full listing.\n")
        return

    gn = const.group_table[argument.lower()]
    for sn in gn.spells:  # TODO:  This might be incorrect.
        if not sn:
            break
        ch.send("%-20s " % sn)
        col += 1
        if col % 3 == 0:
            ch.send("\n")
    if col % 3 != 0:
        ch.send("\n")


api.register("info", do_groups, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
api.register("groups", do_groups, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
