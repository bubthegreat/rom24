import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import comm
from rom24 import handler_ch


def do_reboot(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.invis_level < merc.LEVEL_HERO:
        ch.do_echo("Reboot by %s." % ch.name)
    comm.done = True
    for d in merc.descriptor_list[:]:
        vch = handler_ch.CH(d)
        if vch:
            vch.save(logout=True, force=True)
            comm.close_socket(d)


def do_reboo(ctx):
    ch = ctx.ch
    argument = ctx.arg
    ch.send("If you want to REBOOT, spell it out.\n")
    return


api.register("reboot", do_reboot, pos=merc.POS_DEAD, level=merc.L1, log=merc.LOG_ALWAYS, show=1)
api.register("reboo", do_reboo, pos=merc.POS_DEAD, level=merc.L1, log=merc.LOG_NORMAL, show=0)
