from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import merc


@api.spell(
    "cause serious",
    skill_level={"mage": 53, "cleric": 7, "thief": 53, "warrior": 10},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(64),
    min_mana=17,
    beats=12,
    noun_damage="spell",
    msg_off="!Cause Serious!",
    msg_obj="",
)
def spell_cause_serious(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    fight.damage(
        ch, victim, game_utils.dice(2, 8) + level // 2, sn, merc.DAM_HARM, True
    )
    return
