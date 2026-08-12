import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_description(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if argument:
        if argument[0] == "-":
            if not ch.description:
                ch.send("No lines left to remove.\n")
                return
            buf = ch.description.split("\n")
            buf.pop()
            ch.description = "\n".join(buf)
            if len(buf) > 1:
                ch.send("Your description is:\n")
                ch.send(ch.description if ch.description else "(None).\n")
                return
            else:
                ch.description = ""
                ch.send("Description cleared.\n")
                return
        if argument[0] == "+":
            argument = argument[1:].lstrip()

            if len(argument) + len(ch.description) >= 1024:
                ch.send("Description too long.\n")
                return
            ch.description += argument + "\n"

    ch.send("Your description is:\n")
    ch.send(ch.description if ch.description else "(None).\n")
    return


api.register("description", do_description, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
