import merc
import const
import interp


def do_groups(self, argument):
    ch = self
    if merc.IS_NPC(ch):
        return
    col = 0

    if not argument:
        # show all groups */
        for gn, group in const.group_table.items():
            if gn in ch.pcdata.group_known:
                ch.send("%-20s " % group.name)
                col += 1
                if col % 3 == 0:
                    ch.send("\n")
        if col % 3 != 0:
            ch.send( "\n" )
        ch.send("Creation points: %d\n" % ch.pcdata.points)
        return

    if "all" == argument.lower():
        for gn, group in const.group_table.items():
            ch.send("%-20s " % group.name)
            col += 1
            if col % 3 == 0:
                ch.send("\n")
        if col % 3 != 0:
            ch.send( "\n" )
        return

    # show the sub-members of a group */
    if argument.lower() not in const.group_table:
        ch.send("No group of that name exist.\n")
        ch.send("Type 'groups all' or 'info all' for a full listing.\n")
        return

    gn = const.group_table[argument.lower()]
    for sn in group.spells:
        if not sn:
            break
        ch.send("%-20s " % sn)
        col += 1
        if col % 3 == 0:
            ch.send("\n")
    if col % 3 != 0:
        ch.send( "\n" )


interp.cmd_table['info'] = interp.cmd_type('info', do_groups, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)
interp.cmd_table['groups'] = interp.cmd_type('groups', do_groups, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)