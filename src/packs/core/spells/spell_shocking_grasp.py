from rom24 import api
import random
from rom24 import const
from rom24 import fight
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "shocking grasp",
    skill_level={"mage": 10, "cleric": 53, "thief": 14, "warrior": 13},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(53),
    min_mana=15,
    beats=12,
    noun_damage="shocking grasp",
    msg_off="!Shocking Grasp!",
    msg_obj="",
)
def spell_shocking_grasp(ctx):
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
        20,
        25,
        29,
        33,
        36,
        39,
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
        49,
        49,
        50,
        50,
        51,
        51,
        52,
        52,
        53,
        53,
        54,
        54,
        55,
        55,
        56,
        56,
        57,
        57,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if handler_magic.saves_spell(level, victim, merc.DAM_LIGHTNING):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_LIGHTNING, True)
