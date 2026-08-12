import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import game_utils


def do_sockets(ctx):
    ch = ctx.ch
    argument = ctx.arg
    count = 0
    argument, arg = game_utils.read_word(argument)
    for d in merc.descriptor_list:
        if (
            d.character
            and ch.can_see(d.character)
            and (not arg or arg not in d.character.name)
            or (d.original and game_utils.is_name(arg, d.original.name))
        ):
            count += 1
            ch.send(
                "%s@%s\n"
                % (
                    d.original.name
                    if d.original
                    else d.character.name
                    if d.character
                    else "(none)",
                    d.address,
                )
            )
    if count == 0:
        ch.send("No one by that name is connected.\n")
        return
    ch.send("%d user%s\n" % (count, "" if count == 1 else "s"))
    return


api.register("sockets", do_sockets, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_NORMAL, show=1)
