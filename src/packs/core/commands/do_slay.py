import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game


def do_slay(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Slay whom?\n")
        return
    victim = ch.get_char_room(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if ch == victim:
        ch.send("Suicide is a mortal sin.\n")
        return
    if not victim.is_npc() and victim.level >= ch.trust:
        ch.send("You failed.\n")
        return
    handler_game.act("You slay $M in cold blood!", ch, None, victim, merc.TO_CHAR)
    handler_game.act("$n slays you in cold blood!", ch, None, victim, merc.TO_VICT)
    handler_game.act("$n slays $N in cold blood!", ch, None, victim, merc.TO_NOTVICT)
    fight.raw_kill(victim)
    return


def do_sla(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("If you want to SLAY, spell it out.\n")
    return


api.register("slay", do_slay, pos=merc.POS_DEAD, level=merc.L3, log=merc.LOG_ALWAYS, show=1)
api.register("sla", do_sla, pos=merc.POS_DEAD, level=merc.L3, log=merc.LOG_NORMAL, show=0)
