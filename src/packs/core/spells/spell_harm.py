from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "harm",
    skill_level={"mage": 53, "cleric": 23, "thief": 53, "warrior": 28},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(27),
    min_mana=35,
    beats=12,
    noun_damage="harm spell",
    msg_off="!Harm!",
    msg_obj="",
)
def spell_harm(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam = max(20, victim.hit - game_utils.dice(1, 4))
    if handler_magic.saves_spell(level, victim, merc.DAM_HARM):
        dam = min(50, dam // 2)
    dam = min(100, dam)
    fight.damage(ch, victim, dam, sn, merc.DAM_HARM, True)
