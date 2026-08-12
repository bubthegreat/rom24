import random

from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "chill touch",
    skill_level={"mage": 4, "cleric": 53, "thief": 6, "warrior": 6},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(8),
    min_mana=15,
    beats=12,
    noun_damage="chilling touch",
    msg_off="You feel less cold.",
    msg_obj="",
)
def spell_chill_touch(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam_each = [
        0,
        0,
        0,
        6,
        7,
        8,
        9,
        12,
        13,
        13,
        13,
        14,
        14,
        14,
        15,
        15,
        15,
        16,
        16,
        16,
        17,
        17,
        17,
        18,
        18,
        18,
        19,
        19,
        19,
        20,
        20,
        20,
        21,
        21,
        21,
        22,
        22,
        22,
        23,
        23,
        23,
        24,
        24,
        24,
        25,
        25,
        25,
        26,
        26,
        26,
        27,
    ]

    level = min(level, len(dam_each) - 1)
    level = max(0, level)
    dam = random.randint(dam_each[level] // 2, dam_each[level] * 2)
    if not handler_magic.saves_spell(level, victim, merc.DAM_COLD):
        handler_game.act("$n turns blue and shivers.", victim, None, None, merc.TO_ROOM)
        af = handler_game.AFFECT_DATA()
        af.where = merc.TO_AFFECTS
        af.type = sn
        af.level = level
        af.duration = 6
        af.location = merc.APPLY_STR
        af.modifier = -1
        af.bitvector = 0
        victim.affect_join(af)
    else:
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_COLD, True)
