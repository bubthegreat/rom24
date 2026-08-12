import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import handler_game


def do_report(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send(
        "You say 'I have %d/%d hp %d/%d mana %d/%d mv %d xp.'\n"
        % (ch.hit, ch.max_hit, ch.mana, ch.max_mana, ch.move, ch.max_move, ch.exp)
    )
    buf = "$n says 'I have %d/%d hp %d/%d mana %d/%d mv %d xp.'" % (
        ch.hit,
        ch.max_hit,
        ch.mana,
        ch.max_mana,
        ch.move,
        ch.max_move,
        ch.exp,
    )
    handler_game.act(buf, ch, None, None, merc.TO_ROOM)
    return


api.register("report", do_report, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
