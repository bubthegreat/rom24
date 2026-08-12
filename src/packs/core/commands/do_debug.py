import logging

logger = logging.getLogger(__name__)

from rom24 import handler_pc
from rom24 import game_utils
from rom24 import interp
from rom24 import merc
from rom24 import api


def do_debug(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        ch.send(
            "Syntax: debug <command> "
            "<arguments>\n\n   "
            "Safely execute commands and "
            "get valuable debugging "
            "information.\n"
        )
        return
    safety, word = game_utils.read_word(argument)
    if word.startswith("debug"):
        ch.send("Nope.\n")
        return
    handler_pc.Pc.interpret(ch, argument)
    return


api.register("debug", do_debug, pos=merc.POS_DEAD, level=merc.ML, log=merc.LOG_NORMAL, show=1)
