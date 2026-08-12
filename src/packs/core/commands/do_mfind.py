import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api
from rom24 import game_utils
from rom24 import instance


def do_mfind(ctx):
    ch = ctx.ch
    argument = ctx.arg
    argument, arg = game_utils.read_word(argument)
    if not arg:
        ch.send("Find whom?\n")
        return
    fAll = False  # !str_cmp( arg, "all" )
    found = False
    nMatch = 0
    # Yeah, so iterating over all vnum's takes 10,000 loops.
    # Get_mob_index is fast, and I don't feel like threading another link.
    # Do you?
    # -- Furey
    for pMobIndex in instance.npc_templates.values():
        if fAll or game_utils.is_name(arg, pMobIndex.name):
            found = True
            ch.send("[[%5d]] %s\n" % (pMobIndex.vnum, pMobIndex.short_descr))
    if not found:
        ch.send("No mobiles by that name.\n")
    return


api.register("mfind", do_mfind, pos=merc.POS_DEAD, level=merc.L4, log=merc.LOG_NORMAL, show=1)
