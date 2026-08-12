"""ctx-style pilot: the fireball spell (offensive damage)."""
from rom24 import api

DAM_EACH = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 82, 84, 86, 88,
    90, 92, 94, 96, 98, 100, 102, 104, 106, 108, 110, 112, 114, 116, 118,
    120, 122, 124, 126, 128, 130,
]


@api.spell(
    "fireball",
    skill_level={"mage": 22, "cleric": 53, "thief": 30, "warrior": 26},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=api.TAR_CHAR_OFFENSIVE,
    min_pos=api.POS_FIGHTING,
    slot=api.SLOT(26),
    min_mana=15,
    beats=12,
    noun_damage="fireball",
    msg_off="!Fireball!",
)
def spell_fireball(ctx):
    level = max(0, min(ctx.level, len(DAM_EACH) - 1))
    dam = ctx.rand(DAM_EACH[level] // 2, DAM_EACH[level] * 2)
    if ctx.engine.handler_magic.saves_spell(level, ctx.target, api.DAM_FIRE):
        dam //= 2
    ctx.damage(ctx.target, dam, ctx.sn, api.DAM_FIRE, True)
