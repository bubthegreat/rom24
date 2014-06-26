import merc
import interp
import nanny


# RT answer channel - uses same line as questions */
def do_answer(ch, argument):
    if not argument:
        if merc.IS_SET(ch.comm, merc.COMM_NOQUESTION):
            ch.send("Q/A channel is now ON.\n")
            ch.comm = merc.REMOVE_BIT(ch.comm, merc.COMM_NOQUESTION)
        else:
            ch.send("Q/A channel is now OFF.\n")
            ch.comm = merc.SET_BIT(ch.comm, merc.COMM_NOQUESTION)
    else:  # answer sent, turn Q/A on if it isn't already */
        if merc.IS_SET(ch.comm, merc.COMM_QUIET):
            ch.send("You must turn off quiet mode first.\n")
            return
        if merc.IS_SET(ch.comm, merc.COMM_NOCHANNELS):
            ch.send("The gods have revoked your channel priviliges.\n")
            return
        ch.comm = merc.REMOVE_BIT(ch.comm, merc.COMM_NOQUESTION)
        ch.send("You answer '%s'\n" % argument )
        for d in merc.descriptor_list:
            victim = merc.CH(d)
            if d.is_connected(nanny.con_playing) and d.character != ch \
            and not merc.IS_SET(victim.comm, merc.COMM_NOQUESTION) and not merc.IS_SET(victim.comm, merc.COMM_QUIET):
                merc.act("$n answers '$t'", ch, argument, d.character, merc.TO_VICT, merc.POS_SLEEPING)

interp.cmd_table['answer'] = interp.cmd_type('answer', do_answer, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)