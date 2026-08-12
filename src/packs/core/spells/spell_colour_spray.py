import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "colour spray",
    skill_level={"mage": 16, "cleric": 53, "thief": 22, "warrior": 20},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(10),
    min_mana=15,
    beats=12,
    noun_damage="colour spray",
    msg_off="!Colour Spray!",
    msg_obj="",
)
def spell_colour_spray(ctx):
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
        0,
        0,
        0,
        0,
        0,
        0,
        30,
        35,
        40,
        45,
        50,
        55,
        55,
        55,
        56,
        57,
        58,
        58,
        59,
        60,
        61,
        61,
        62,
        63,
        64,
        64,
        65,
        66,
        67,
        67,
        68,
        69,
        70,
        70,
        71,
        72,
        73,
        73,
        74,
        75,
        76,
        76,
        77,
        78,
        79,
        79,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if handler_magic.saves_spell(level, victim, merc.DAM_LIGHT):
        dam //= 2
    else:
        const.skill_table["blindness"].spell_fun(
            "blindness", level // 2, ch, victim, merc.TARGET_CHAR
        )

    fight.damage(ch, victim, dam, sn, merc.DAM_LIGHT, True)
