import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import game_utils

# RT to replace the 3 stat commands
def do_stat(ctx):
    ch = ctx.ch
    argument = ctx.arg
    string, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Syntax:\n")
        ch.send("  stat <name>\n")
        ch.send("  stat obj <name>\n")
        ch.send("  stat mob <name>\n")
        ch.send("  stat room <number>\n")
        return
    if arg == "room":
        ch.do_rstat(string)
        return
    if arg == "obj":
        ch.do_ostat(string)
        return
    if arg == "char" or arg == "mob":
        ch.do_mstat(string)
        return
    # do it the old way
    obj = ch.get_item_world(argument)
    if obj:
        ch.do_ostat(argument)
        return
    victim = ch.get_char_world(argument)
    if victim:
        ch.do_mstat(argument)
        return
    location = game_utils.find_location(ch, argument)
    if location:
        ch.do_rstat(argument)
        return
    ch.send("Nothing by that name found anywhere.\n")


api.register("stat", do_stat, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
