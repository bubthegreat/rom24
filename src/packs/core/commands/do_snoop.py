import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import game_utils
from rom24 import handler_game
from rom24 import state_checks


def do_snoop(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Snoop whom?\n")
        return
    victim = ch.get_char_world(arg)
    if not victim:
        ch.send("They aren't here.\n")
        return
    if not victim.desc:
        ch.send("No descriptor to snoop.\n")
        return
    if victim == ch:
        ch.send("Cancelling all snoops.\n")
        handler_game.wiznet(
            "$N stops being such a snoop.",
            ch,
            None,
            merc.WIZ_SNOOPS,
            merc.WIZ_SECURE,
            ch.trust,
        )
        for d in merc.descriptor_list:
            if d.snoop_by == ch.desc:
                d.snoop_by = None
        return
    if victim.desc.snoop_by:
        ch.send("Busy already.\n")
        return
    if (
        not ch.is_room_owner(victim.in_room)
        and ch.in_room != victim.in_room
        and victim.in_room.is_private()
        and not state_checks.IS_TRUSTED(ch, merc.MAX_LEVEL)
    ):
        ch.send("That character is in a private room.\n")
        return
    if victim.trust >= ch.trust or victim.comm.is_set(merc.COMM_SNOOP_PROOF):
        ch.send("You failed.\n")
        return
    if ch.desc:
        d = ch.desc.snoop_by
        while d:
            if d.character == victim or d.original == victim:
                ch.send("No snoop loops.\n")
                return
            d = d.snoop_by
    victim.desc.snoop_by = ch.desc
    buf = "$N starts snooping on %s" % (
        victim.short_descr if ch.is_npc() else victim.name
    )
    handler_game.wiznet(buf, ch, None, merc.WIZ_SNOOPS, merc.WIZ_SECURE, ch.trust)
    ch.send("Ok.\n")
    return


api.register("snoop", do_snoop, pos=merc.POS_DEAD, level=merc.L5, log=merc.LOG_ALWAYS, show=1)
