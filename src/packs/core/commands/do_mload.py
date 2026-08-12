import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import game_utils
from rom24 import handler_game
from rom24 import object_creator
from rom24 import instance


def do_mload(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg or not arg.isdigit():
        ch.send("Syntax: load mob <vnum>.\n")
        return
    vnum = int(arg)
    if vnum not in instance.npc_templates:
        ch.send("No mob has that vnum.\n")
        return
    template = instance.npc_templates[vnum]
    victim = object_creator.create_mobile(template)
    ch.in_room.put(victim)
    handler_game.act("$n has created $N!", ch, None, victim, merc.TO_ROOM)
    handler_game.wiznet(
        "$N loads %s." % victim.short_descr,
        ch,
        None,
        merc.WIZ_LOAD,
        merc.WIZ_SECURE,
        ch.trust,
    )
    ch.send("Ok.\n")
    return


api.register("mload", do_mload, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
