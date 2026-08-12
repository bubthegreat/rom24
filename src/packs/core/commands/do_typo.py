import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import settings
from rom24 import game_utils
from rom24 import api


def do_typo(ctx):
    ch = ctx.ch
    argument = ctx.arg
    game_utils.append_file(ch, settings.TYPO_FILE, argument)
    ch.send("Typo logged.\n")
    return


api.register("typo", do_typo, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
