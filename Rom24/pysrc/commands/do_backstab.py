from Rom24.pysrc.fight import is_safe, check_killer, multi_hit, damage


def do_backstab(ch, argument):
    argument, arg = merc.read_word(argument)

    if not arg:
        ch.send("Backstab whom?\n\r")
        return
    victim = None
    if ch.fighting:
        ch.send("You're facing the wrong end.\n\r")
        return
    else:
        victim = ch.get_char_room(arg)
        if not victim:
            ch.send("They aren't here.\n\r")
            return
        if victim == ch:
            ch.send("How can you sneak up on yourself?\n\r")
            return
        if fight.is_safe(ch, victim):
            return
        if merc.IS_NPC(victim) and victim.fighting and not ch.is_same_group(victim.fighting):
            ch.send("Kill stealing is not permitted.\n\r")
            return
        obj = ch.get_eq(merc.WEAR_WIELD)
        if obj:
            ch.send("You need to wield a weapon to backstab.\n\r")
            return
        if victim.hit < victim.max_hit // 3:
            merc.act("$N is hurt and suspicious ... you can't sneak up.", ch, None, victim, merc.TO_CHAR)
            return
        fight.check_killer(ch, victim)
        merc.WAIT_STATE( ch, const.skill_table['backstab'].beats )
        if random.randint(1,99) < ch.get_skill('backstab') \
        or ( ch.get_skill('backstab') >= 2 and not merc.IS_AWAKE(victim) ):
            skills.check_improve(ch,'backstab',True,1)
            fight.multi_hit( ch, victim, 'backstab' )
        else:
            skills.check_improve(ch,'backstab',False,1)
            fight.damage( ch, victim, 0, 'backstab', merc.DAM_NONE,True)
    return

interp.cmd_table['backstab'] = interp.cmd_type('backstab', do_backstab, merc.POS_FIGHTING, 0, merc.LOG_NORMAL, 1)
interp.cmd_table['bs'] = interp.cmd_type('bs', do_backstab, merc.POS_FIGHTING, 0, merc.LOG_NORMAL, 0)