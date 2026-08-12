import random
from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "lightning bolt",
    skill_level={"mage": 13, "cleric": 23, "thief": 18, "warrior": 16},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(30),
    min_mana=15,
    beats=12,
    noun_damage="lightning bolt",
    msg_off="!Lightning Bolt!",
    msg_obj="",
)
def spell_lightning_bolt(ctx):
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
        25,
        28,
        31,
        34,
        37,
        40,
        40,
        41,
        42,
        42,
        43,
        44,
        44,
        45,
        46,
        46,
        47,
        48,
        48,
        49,
        50,
        50,
        51,
        52,
        52,
        53,
        54,
        54,
        55,
        56,
        56,
        57,
        58,
        58,
        59,
        60,
        60,
        61,
        62,
        62,
        63,
        64,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if handler_magic.saves_spell(level, victim, merc.DAM_LIGHTNING):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_LIGHTNING, True)
