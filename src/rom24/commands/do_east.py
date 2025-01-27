import logging

logger = logging.getLogger(__name__)

from rom24 import handler_ch
from rom24 import interp
from rom24 import merc


def do_east(ch, argument):
    handler_ch.move_char(ch, merc.DIR_EAST, False)
    return


interp.register_command(
    interp.cmd_type("east", do_east, merc.POS_STANDING, 0, merc.LOG_NEVER, 0)
)
