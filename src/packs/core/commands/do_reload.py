import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import nanny
from rom24 import hotfix
from rom24 import interp
from rom24 import api


def do_reload(ctx):
    ch = ctx.ch
    argument = ctx.arg
    hotfix.reload_files(ch)
    for d in merc.descriptor_list:
        if d.is_connected(nanny.con_playing):
            if d.character.trust <= ch.trust:
                d.send(f"imp> {ch.name} reloaded files.")


api.register("reload", do_reload, pos=merc.POS_DEAD, level=merc.ML, log=merc.LOG_NORMAL, show=1)
