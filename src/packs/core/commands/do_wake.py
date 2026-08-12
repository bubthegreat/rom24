import logging

logger = logging.getLogger(__name__)

from rom24 import game_utils
from rom24 import merc
from rom24 import interp
from rom24 import handler_game
from rom24 import state_checks
from rom24 import api


def do_wake(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.do_stand("")
        return

    if not ch.is_awake():
        ch.send("You are asleep yourself!\n")
        return
    victim = ch.get_char_room(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if state_checks.IS_AWAKE(victim):
        handler_game.act("$N is already awake.", ch, None, victim, merc.TO_CHAR)
        return
    if victim.is_affected(merc.AFF_SLEEP):
        handler_game.act("You can't wake $M!", ch, None, victim, merc.TO_CHAR)
        return
    handler_game.act("$n wakes you.", ch, None, victim, merc.TO_VICT, merc.POS_SLEEPING)
    victim.do_stand("")
    return


api.register("wake", do_wake, pos=merc.POS_SLEEPING, level=0, log=merc.LOG_NORMAL, show=1)
