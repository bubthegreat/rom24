import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import mem_report


def do_memory(ch, argument):
    for line in mem_report.memory_lines():
        ch.send(line + "\n")


interp.register_command(
    interp.cmd_type("memory", do_memory, merc.POS_DEAD, merc.IM, merc.LOG_NORMAL, 1)
)
