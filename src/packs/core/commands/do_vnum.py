import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import game_utils
from rom24 import api


# ofind and mfind replaced with vnum, vnum skill also added */
def do_vnum(ctx):
    ch = ctx.ch
    argument = ctx.arg
    string, arg = game_utils.read_word(argument)

    if not arg:
        ch.send("Syntax:\n")
        ch.send("  vnum obj <name>\n")
        ch.send("  vnum mob <name>\n")
        ch.send("  vnum skill <skill or spell>\n")
        return
    if arg == "obj":
        ch.do_ofind(string)
        return

    if arg == "mob" or arg == "char":
        ch.do_mfind(string)
        return

    if arg == "skill" or arg == "spell":
        ch.do_slookup(string)
        return
    # do both */
    ch.do_mfind(argument)
    ch.do_ofind(argument)


api.register("vnum", do_vnum, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_NORMAL, show=1)
