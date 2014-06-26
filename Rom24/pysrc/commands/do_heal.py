import merc
import interp
import const


def do_heal(ch, argument):
    # check for healer */
    mob = [mob for mob in ch.in_room.people if merc.IS_NPC(mob) and merc.IS_SET(mob.act, merc.ACT_IS_HEALER)][:1]
    if not mob:
        ch.send("You can't do that here.\n\r")
        return
    mob = mob[0]
    argument, arg = merc.read_word(argument)
    if not arg:
        # display price list */
        merc.act("$N says 'I offer the following spells:'",ch,None,mob,merc.TO_CHAR)
        ch.send("  light: cure light wounds      10 gold\n\r")
        ch.send("  serious: cure serious wounds  15 gold\n\r")
        ch.send("  critic: cure critical wounds  25 gold\n\r")
        ch.send("  heal: healing spell       50 gold\n\r")
        ch.send("  blind: cure blindness         20 gold\n\r")
        ch.send("  disease: cure disease         15 gold\n\r")
        ch.send("  poison:  cure poison          25 gold\n\r")
        ch.send("  uncurse: remove curse         50 gold\n\r")
        ch.send("  refresh: restore movement      5 gold\n\r")
        ch.send("  mana:  restore mana       10 gold\n\r")
        ch.send(" Type heal <type> to be healed.\n\r")
        return
    spell = None
    sn = None
    words = None
    cost = 0
    if "light".startswith(arg):
        sn = const.skill_table["cure light"]
        spell = sn.spell_fun
        words = "judicandus dies"
        cost  = 1000
    elif "serious".startswith(arg):
        sn = const.skill_table["cure serious"]
        spell = sn.spell_fun
        words = "judicandus gzfuajg"
        cost  = 1600
    elif "critical".startswith(arg):
        sn = const.skill_table["cure critical"]
        spell = sn.spell_fun
        words = "judicandus qfuhuqar"
        cost  = 2500
    elif "heal".startswith(arg):
        sn = const.skill_table["heal"]
        spell = sn.spell_fun
        words = "pzar"
        cost = 5000
    elif "blindness".startswith(arg):
        sn = const.skill_table["cure blindness"]
        spell = sn.spell_fun
        words = "judicandus noselacri"
        cost  = 2000
    elif "disease".startswith(arg):
        sn = const.skill_table["cure disease"]
        spell = sn.spell_fun
        words = "judicandus eugzagz"
        cost = 1500
    elif "poison".startswith(arg):
        sn = const.skill_table["cure poison"]
        spell = sn.spell_fun
        words = "judicandus sausabru"
        cost  = 2500
    elif "uncurse".startswith(arg) or "curse".startswith(arg):
        sn = const.skill_table["remove curse"]
        spell = sn.spell_fun
        words = "candussido judifgz"
        cost  = 5000
    elif "mana".startswith(arg) or "energize".startswith(arg):
        spell = None
        sn = None
        words = "energizer"
        cost = 1000
    elif "refresh".startswith(arg) or "moves".startswith(arg):
        sn = const.skill_table["refresh"]
        spell = sn.spell_fun
        words = "candusima"
        cost  = 500
    else:
        merc.act("$N says 'Type 'heal' for a list of spells.'",ch,None,mob, merc.TO_CHAR)
        return
    if cost > (ch.gold * 100 + ch.silver):
        merc.act("$N says 'You do not have enough gold for my services.'",ch,None,mob, merc.TO_CHAR)
        return
    merc.WAIT_STATE(ch, merc.PULSE_VIOLENCE)

    ch.deduct_cost(cost)
    mob.gold += cost // 100
    mob.silver += cost % 100
    merc.act("$n utters the words '$T'.",mob,None,words, merc.TO_ROOM)

    if spell == None: # restore mana trap...kinda hackish */ kinda?
        ch.mana += dice(2,8) + mob.level // 3
        ch.mana = min(ch.mana,ch.max_mana)
        ch.send("A warm glow passes through you.\n\r")
        return
    if sn == -1:
        return
    spell(sn,mob.level,mob,ch, merc.TARGET_CHAR)

interp.cmd_table['heal'] = interp.cmd_type('heal', do_heal, merc.POS_RESTING, 0, merc.LOG_NORMAL, 1)