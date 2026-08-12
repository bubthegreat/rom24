import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "magic missile",
    skill_level={"mage": 1, "cleric": 53, "thief": 2, "warrior": 2},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(32),
    min_mana=15,
    beats=12,
    noun_damage="magic missile",
    msg_off="!Magic Missile!",
    msg_obj="",
)
def spell_magic_missile(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam_each = [
        0,
        3,
        3,
        4,
        4,
        5,
        6,
        6,
        6,
        6,
        6,
        7,
        7,
        7,
        7,
        7,
        8,
        8,
        8,
        8,
        8,
        9,
        9,
        9,
        9,
        9,
        10,
        10,
        10,
        10,
        10,
        11,
        11,
        11,
        11,
        11,
        12,
        12,
        12,
        12,
        12,
        13,
        13,
        13,
        13,
        13,
        14,
        14,
        14,
        14,
        14,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if handler_magic.saves_spell(level, victim, merc.DAM_ENERGY):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_ENERGY, True)
