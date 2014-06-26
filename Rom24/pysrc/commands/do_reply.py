import merc
import interp


def do_reply(ch, argument):
    if merc.IS_SET(ch.comm, merc.COMM_NOTELL):
        ch.send("Your message didn't get through.\n")
        return
    if not ch.reply:
        ch.send("They aren't here.\n")
        return
    victim = ch
    if not victim.desc and not merc.IS_NPC(victim):
        merc.act("$N seems to have misplaced $S link...try again later.", ch, None, victim, merc.TO_CHAR)
        buf = "%s tells you '%s'\n" % (merc.PERS(ch, victim), argument)
        victim.pcdata.buffer.append(buf)
        return
    if not merc.IS_IMMORTAL(ch) and not merc.IS_AWAKE(victim):
        merc.act( "$E can't hear you.", ch, 0, victim, merc.TO_CHAR )
        return

    if (merc.IS_SET(victim.comm, merc.COMM_QUIET) or merc.IS_SET(victim.comm, merc.COMM_DEAF)) \
    and not merc.IS_IMMORTAL(ch) and not merc.IS_IMMORTAL(victim):
        merc.act( "$E is not receiving tells.", ch, None, victim, merc.TO_CHAR, merc.POS_DEAD)
        return
    if not merc.IS_IMMORTAL(victim) and not merc.IS_AWAKE(ch):
        ch.send("In your dreams, or what?\n")
        return
    if merc.IS_SET(victim.comm, merc.COMM_AFK):
        if merc.IS_NPC(victim):
            merc.act("$E is AFK, and not receiving tells.", ch, None, victim, merc.TO_CHAR, merc.POS_DEAD)
            return
        merc.act("$E is AFK, but your tell will go through when $E returns.", ch, None, victim, merc.TO_CHAR, merc.POS_DEAD)
        buf = "%s tells you '%s'\n" % (PERS(ch, victim), argument)
        victim.pcdata.buffer.append(buf)
        return
    merc.act("You tell $N '$t'", ch, argument, victim, merc.TO_CHAR, merc.POS_DEAD)
    merc.act("$n tells you '$t'", ch, argument, victim, merc.TO_VICT, merc.POS_DEAD)
    victim.reply = ch
    return

interp.cmd_table['reply'] = interp.cmd_type('reply', do_reply, merc.POS_SLEEPING, 0, merc.LOG_NORMAL, 1)