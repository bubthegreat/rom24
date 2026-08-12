import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import state_checks


def do_save(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        return
    ch.save()
    # save.legacy_save_char_obj(ch)
    ch.send("Saving. Remember that ROM has automatic saving now.\n")
    state_checks.WAIT_STATE(ch, 4 * merc.PULSE_VIOLENCE)
    return


api.register("save", do_save, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
