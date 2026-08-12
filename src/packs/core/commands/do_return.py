import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import handler_game

def do_return(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not ch.desc:
        return
    if not ch.desc.original:
        ch.send("You aren't switched.\n")
        return
    ch.send("You return to your original body. Type replay to see any missed tells.\n")
    if ch.prompt:
        ch.prompt = ""
    handler_game.wiznet(
        "$N returns from %s." % ch.short_descr,
        ch.desc.original,
        0,
        merc.WIZ_SWITCHES,
        merc.WIZ_SECURE,
        ch.trust,
    )
    ch.desc.character = ch.desc.original
    ch.desc.original = None
    ch.desc.character.desc = ch.desc
    ch.desc = None
    return


api.register("return", do_return, pos=merc.POS_DEAD, level=merc.L6, log=merc.LOG_NORMAL, show=1)
