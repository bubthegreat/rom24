import logging

logger = logging.getLogger(__name__)

from rom24 import handler_game
from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import fight
from rom24 import game_utils
from rom24 import instance


def do_goto(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send("Goto where?\n")
        return
    location = game_utils.find_location(ch, argument)
    if not location:
        ch.send("No such location.\n")
        return
    count = len(location.people)
    if (
        not ch.is_room_owner(location)
        and location.is_private()
        and (count > 1 or ch.trust < merc.MAX_LEVEL)
    ):
        ch.send("That room is private right now.\n")
        return
    if ch.fighting:
        fight.stop_fighting(ch, True)
    for rch_id in ch.in_room.people[:]:
        rch = instance.characters[rch_id]
        if rch.trust >= ch.invis_level:
            if ch.is_npc() and ch.bamfout:
                handler_game.act("$t", ch, ch.bamfout, rch, merc.TO_VICT)
            else:
                handler_game.act(
                    "$n leaves in a swirling mist.", ch, None, rch, merc.TO_VICT
                )
    location.put(ch.in_room.get(ch))

    for rch_id in ch.in_room.people[:]:
        rch = instance.characters[rch_id]
        if rch.trust >= ch.invis_level:
            if ch.is_npc() and ch.bamfin:
                handler_game.act("$t", ch, ch.bamfin, rch, merc.TO_VICT)
            else:
                handler_game.act(
                    "$n appears in a swirling mist.", ch, None, rch, merc.TO_VICT
                )
    ch.do_look("auto")
    return


api.register("goto", do_goto, pos=merc.POS_DEAD, level=merc.L8, log=merc.LOG_NORMAL, show=1)
