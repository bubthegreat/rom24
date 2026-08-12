import logging

logger = logging.getLogger(__name__)

from rom24 import merc
from rom24 import interp
from rom24 import api


def do_affects(ctx):
    ch = ctx.ch
    argument = ctx.arg
    paf_last = None
    if ch.affected:
        ch.send("You are affected by the following spells:\n")
        for paf in ch.affected:
            if paf_last and paf.type == paf_last.type:
                if ch.level >= 20:
                    ch.send("                      ")
                else:
                    continue
            else:
                ch.send("Spell: %-15s" % paf.type.name)
            if ch.level >= 20:
                ch.send(
                    ": modifies %s by %d "
                    % (merc.affect_loc_name(paf.location), paf.modifier)
                )
            if paf.duration == -1:
                ch.send("permanently")
            else:
                ch.send("for %d hours" % paf.duration)
            ch.send("\n")
            paf_last = paf
    else:
        ch.send("You are not affected by any spells.\n")

api.register("affects", do_affects, pos=merc.POS_DEAD, level=0, log=merc.LOG_NORMAL, show=1)
