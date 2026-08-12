from rom24 import api
from rom24 import const
from rom24 import merc


@api.spell(
    "refresh",
    skill_level={"mage": 8, "cleric": 5, "thief": 12, "warrior": 9},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(81),
    min_mana=12,
    beats=18,
    noun_damage="refresh",
    msg_off="!Refresh!",
    msg_obj="",
)
def spell_refresh(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    victim.move = min(victim.move + level, victim.max_move)
    if victim.max_move == victim.move:
        victim.send("You feel fully refreshed! \n")
    else:
        victim.send("You feel less tired.\n")
    if ch != victim:
        ch.send("Ok.\n")
    return
