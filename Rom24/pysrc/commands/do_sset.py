import merc
import interp
import const


def do_sset(ch, argument):
    argument, arg1 = merc.read_word(argument)
    argument, arg2 = merc.read_word(argument)
    argument, arg3 = merc.read_word(argument)

    if not arg1 or not arg2 or not arg3:
        ch.send("Syntax:\n")
        ch.send("  set skill <name> <spell or skill> <value>\n")
        ch.send("  set skill <name> all <value>\n")
        ch.send("   (use the name of the skill, not the number)\n")
        return
    victim = ch.get_char_world(arg1)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if merc.IS_NPC(victim):
        ch.send("Not on NPC's.\n")
        return
    fAll = arg2 == "all"
    sn = merc.prefix_lookup(const.skill_table,arg2)
    if not fAll and not sn:
        ch.send("No such skill or spell.\n")
        return

    # Snarf the value.
    if not arg3.isdigit():
        ch.send("Value must be numeric.\n")
        return
    value = int(arg3)
    if value < 0 or value > 100:
        ch.send("Value range is 0 to 100.\n")
        return

    if fAll:
        for sn in const.skill_table.keys():
            victim.pcdata.learned[sn] = value
    else:
        victim.pcdata.learned[sn.name] = value
    ch.send("Skill set.\n")

interp.cmd_table['sset'] = interp.cmd_type('sset', do_sset, merc.POS_DEAD, merc.L2, merc.LOG_ALWAYS, 1)