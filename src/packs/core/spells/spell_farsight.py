from rom24 import api
from rom24 import const
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "farsight",
    skill_level={"mage": 14, "cleric": 16, "thief": 16, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(521),
    min_mana=36,
    beats=20,
    noun_damage="farsight",
    msg_off="!Farsight!",
    msg_obj="",
)
def spell_farsight(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if ch.is_affected(merc.AFF_BLIND):
        ch.send("Maybe it would help if you could see?\n")
        return

    ch.do_scan(handler_magic.target_name)
