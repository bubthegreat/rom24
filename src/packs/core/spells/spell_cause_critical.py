from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import merc


@api.spell(
    "cause critical",
    skill_level={"mage": 53, "cleric": 13, "thief": 53, "warrior": 19},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(63),
    min_mana=20,
    beats=12,
    noun_damage="spell",
    msg_off="!Cause Critical!",
    msg_obj="",
)
def spell_cause_critical(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    fight.damage(ch, victim, game_utils.dice(3, 8) + level - 6, sn, merc.DAM_HARM, True)
    return
