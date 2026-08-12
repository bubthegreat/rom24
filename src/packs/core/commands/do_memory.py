import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import mem_report


def do_memory(ctx):
    ch = ctx.ch
    argument = ctx.arg
    for line in mem_report.memory_lines():
        ch.send(line + "\n")


api.register("memory", do_memory, pos=merc.POS_DEAD, level=merc.IM, log=merc.LOG_NORMAL, show=1)
