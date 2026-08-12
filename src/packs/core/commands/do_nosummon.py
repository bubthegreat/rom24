import logging

logger = logging.getLogger(__name__)

from rom24 import api
from rom24 import merc
from rom24 import interp
from rom24 import state_checks


def do_nosummon(ctx):
    ch = ctx.ch
    argument = ctx.arg
    if ch.is_npc():
        if state_checks.IS_SET(ch.imm_flags, merc.IMM_SUMMON):
            ch.send("You are no longer immune to summon.\n")
            ch.imm_flags = state_checks.REMOVE_BIT(ch.imm_flags, merc.IMM_SUMMON)
        else:
            ch.send("You are now immune to summoning.\n")
            ch.imm_flags = state_checks.SET_BIT(ch.imm_flags, merc.IMM_SUMMON)
    else:
        if ch.act.is_set(merc.PLR_NOSUMMON):
            ch.send("You are no longer immune to summon.\n")
            ch.act.rem_bit(merc.PLR_NOSUMMON)
        else:
            ch.send("You are now immune to summoning.\n")
            ch.act.set_bit(merc.PLR_NOSUMMON)


api.register("nosummon", do_nosummon, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
