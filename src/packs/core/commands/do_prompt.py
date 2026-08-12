import logging


logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_prompt(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if not argument:
        if ch.comm.is_set(merc.COMM_PROMPT):
            ch.send("You will no longer see prompts.\n")
            ch.comm.rem_bit(merc.COMM_PROMPT)
        else:
            ch.send("You will now see prompts.\n")
            ch.comm.set_bit(merc.COMM_PROMPT)
        return
    if argument.lower() == "all":
        buf = "<%hhp %mm %vmv> "
    else:
        if len(argument) > 50:
            argument = argument[:50]
        buf = argument
        if buf.endswith("%c"):
            buf += " "
    ch.prompt = buf
    ch.send("Prompt set to %s\n" % ch.prompt)
    return


api.register("prompt", do_prompt, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
