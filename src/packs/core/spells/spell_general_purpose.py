import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "general purpose",
    skill_level={"mage": 53, "cleric": 53, "thief": 53, "warrior": 53},
    rating={"mage": 0, "cleric": 0, "thief": 0, "warrior": 0},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(401),
    min_mana=0,
    beats=12,
    noun_damage="general purpose ammo",
    msg_off="!General Purpose Ammo!",
    msg_obj="",
)
def spell_general_purpose(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam = random.randint(25, 100)
    if handler_magic.saves_spell(level, victim, merc.DAM_PIERCE):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_PIERCE, True)
    return
