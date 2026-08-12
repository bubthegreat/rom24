from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "acid blast",
    skill_level={"mage": 28, "cleric": 53, "thief": 35, "warrior": 32},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(70),
    min_mana=20,
    beats=12,
    noun_damage="acid blast",
    msg_off="!Acid Blast!",
    msg_obj="",
)
def spell_acid_blast(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    dam = game_utils.dice(level, 12)
    if handler_magic.saves_spell(level, victim, merc.DAM_ACID):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_ACID, True)
