import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import nanny
from rom24 import api


def do_help(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        argument = "summary"

    found = [
        h
        for h in merc.help_list
        if h.level <= ch.trust and argument.lower() in h.keyword.lower()
    ]

    for pHelp in found:
        if ch.desc.is_connected(nanny.con_playing):
            ch.send("\n============================================================\n")
            ch.send(pHelp.keyword)
            ch.send("\n")
        text = pHelp.text
        if pHelp.text[0] == ".":
            text = pHelp.text[1:]
        ch.send(text + "\n")
        # small hack :)
        if (
            ch.desc
            and ch.desc.connected != nanny.con_playing
            and ch.desc.connected != nanny.con_gen_groups
        ):
            break

    if not found:
        ch.send("No help on that word.\n")


api.register("help", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
api.register("motd", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1, default_arg="motd")
api.register("imotd", do_help, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1, default_arg="imotd")
api.register("rules", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1, default_arg="rules")
api.register("story", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1, default_arg="story")
api.register("wizlist", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1, default_arg="wizlist")
api.register("credits", do_help, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1, default_arg="credits")
