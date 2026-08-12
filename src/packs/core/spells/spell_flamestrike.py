from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "flamestrike",
    skill_level={"mage": 53, "cleric": 20, "thief": 53, "warrior": 27},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(65),
    min_mana=20,
    beats=12,
    noun_damage="flamestrike",
    msg_off="!Flamestrike!",
    msg_obj="",
)
def spell_flamestrike(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam = game_utils.dice(6 + level // 2, 8)
    if handler_magic.saves_spell(level, victim, merc.DAM_FIRE):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_FIRE, True)
