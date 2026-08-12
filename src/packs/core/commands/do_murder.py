import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import state_checks


def do_murder(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Murder whom?\n")
        return

    if ch.is_affected(merc.AFF_CHARM) or (ch.is_npc() and ch.act.is_set(merc.ACT_PET)):
        return
    victim = ch.get_char_room(arg)
    if victim is None:
        ch.send("They aren't here.\n")
        return
    if victim == ch:
        ch.send("Suicide is a mortal sin.\n")
        return
    if fight.is_safe(ch, victim):
        return
    if victim.is_npc() and victim.fighting and not ch.is_same_group(victim.fighting):
        ch.send("Kill stealing is not permitted.\n")
        return
    if ch.is_affected(merc.AFF_CHARM) and ch.master == victim:
        handler_game.act("$N is your beloved master.", ch, None, victim, merc.TO_CHAR)
        return
    if ch.position == merc.POS_FIGHTING:
        ch.send("You do the best you can!\n")
        return

    state_checks.WAIT_STATE(ch, 1 * merc.PULSE_VIOLENCE)
    if ch.is_npc():
        buf = "Help! I am being attacked by %s!" % ch.short_descr
    else:
        buf = "Help!  I am being attacked by %s!" % ch.name
    victim.do_yell(buf)
    fight.check_killer(ch, victim)
    fight.multi_hit(ch, victim, merc.TYPE_UNDEFINED)
    return


def do_murde(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("If you want to MURDER, spell it out.\n")
    return


api.register("murder", do_murder, pos=merc.POS_FIGHTING, level=5, log=merc.LOG_ALWAYS, show=1)
api.register("murde", do_murde, pos=merc.POS_FIGHTING, level=0, log=merc.LOG_NORMAL, show=0)
