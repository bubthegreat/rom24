import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import game_utils

# RT to replace the two load commands
def do_load(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Syntax:\n")
        ch.send("  load mob <vnum>\n")
        ch.send("  load obj <vnum> <level>\n")
        return
    if arg == "mob" or arg == "char":
        ch.do_mload(argument)
        return
    if arg == "obj":
        ch.do_oload(argument)
        return
    # echo syntax
    ch.do_load("")


api.register("load", do_load, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_ALWAYS, show=1)
