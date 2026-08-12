import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import state_checks
from rom24 import api


def do_deny(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Deny whom?\n")
        return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if victim.is_npc():
        ch.send("Not on NPC's.\n")
        return
    if victim.trust >= ch.trust:
        ch.send("You failed.\n")
        return
    victim.act = state_checks.SET_BIT(victim.act, merc.PLR_DENY)
    victim.send("You are denied access!\n")
    handler_game.wiznet(
        "$N denies access to %s" % victim.name,
        ch,
        None,
        merc.WIZ_PENALTIES,
        merc.WIZ_SECURE,
        0,
    )
    ch.send("OK.\n")
    victim.save(logout=True, force=True)
    fight.stop_fighting(victim, True)
    victim.do_quit("")
    return


api.register("deny", do_deny, pos=merc.POS_DEAD, level=merc.L1, log=merc.LOG_ALWAYS, show=1)
