import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import game_utils
from rom24 import handler_game
from rom24 import shop_utils
from rom24 import api


def do_value(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Value what?\n")
        return
    keeper = shop_utils.find_keeper(ch)
    if not keeper:
        return
    obj = ch.get_item_carry(arg, ch)
    if not obj:
        handler_game.act(
            "$n tells you 'You don't have that item'.", keeper, None, ch, merc.TO_VICT
        )
        ch.reply = keeper
        return
    if not keeper.can_see_item(obj):
        handler_game.act(
            "$n doesn't see what you are offering.", keeper, None, ch, merc.TO_VICT
        )
        return
    if not ch.can_drop_item(obj):
        ch.send("You can't let go of it.\n")
        return
    cost = shop_utils.get_cost(keeper, obj, False)
    if cost <= 0:
        handler_game.act("$n looks uninterested in $p.", keeper, obj, ch, merc.TO_VICT)
        return
    handler_game.act(
        "$n tells you 'I'll give you %d silver and %d gold coins for $p'."
        % (cost - (cost // 100) * 100, cost // 100),
        keeper,
        obj,
        ch,
        merc.TO_VICT,
    )
    ch.reply = keeper
    return


api.register("value", do_value, pos=merc.POS_RESTING, level=0, log=merc.LOG_NORMAL, show=1)
