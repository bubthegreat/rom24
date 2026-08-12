import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "burning hands",
    skill_level={"mage": 7, "cleric": 53, "thief": 10, "warrior": 9},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(5),
    min_mana=15,
    beats=12,
    noun_damage="burning hands",
    msg_off="!Burning Hands!",
    msg_obj="",
)
def spell_burning_hands(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam_each = [
        0,
        0,
        0,
        0,
        0,
        14,
        17,
        20,
        23,
        26,
        29,
        29,
        29,
        30,
        30,
        31,
        31,
        32,
        32,
        33,
        33,
        34,
        34,
        35,
        35,
        36,
        36,
        37,
        37,
        38,
        38,
        39,
        39,
        40,
        40,
        41,
        41,
        42,
        42,
        43,
        43,
        44,
        44,
        45,
        45,
        46,
        46,
        47,
        47,
        48,
        48,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if handler_magic.saves_spell(level, victim, merc.DAM_FIRE):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_FIRE, True)
