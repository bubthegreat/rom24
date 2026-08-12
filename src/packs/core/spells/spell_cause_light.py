from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import merc


@api.spell(
    "cause light",
    skill_level={"mage": 53, "cleric": 1, "thief": 53, "warrior": 3},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(62),
    min_mana=15,
    beats=12,
    noun_damage="spell",
    msg_off="!Cause Light!",
    msg_obj="",
)
def spell_cause_light(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    fight.damage(
        ch, victim, game_utils.dice(1, 8) + level // 3, sn, merc.DAM_HARM, True
    )
    fight.check_killer
    return
