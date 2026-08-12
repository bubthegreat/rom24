import random

from rom24 import api
from rom24 import const
from rom24 import effects
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "acid breath",
    skill_level={"mage": 31, "cleric": 32, "thief": 33, "warrior": 34},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(200),
    min_mana=100,
    beats=24,
    noun_damage="blast of acid",
    msg_off="!Acid Breath!",
    msg_obj="",
)
def spell_acid_breath(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # NPC spells.
    handler_game.act("$n spits acid at $N.", ch, None, victim, merc.TO_NOTVICT)
    handler_game.act(
        "$n spits a stream of corrosive acid at you.", ch, None, victim, merc.TO_VICT
    )
    handler_game.act("You spit acid at $N.", ch, None, victim, merc.TO_CHAR)

    hpch = max(12, ch.hit)
    hp_dam = random.randint(hpch // 11 + 1, hpch // 6)
    dice_dam = game_utils.dice(level, 16)

    dam = max(hp_dam + dice_dam // 10, dice_dam + hp_dam // 10)

    if handler_magic.saves_spell(level, victim, merc.DAM_ACID):
        effects.acid_effect(victim, level // 2, dam // 4, merc.TARGET_CHAR)
        fight.damage(ch, victim, dam // 2, sn, merc.DAM_ACID, True)
    else:
        effects.acid_effect(victim, level, dam, merc.TARGET_CHAR)
        fight.damage(ch, victim, dam, sn, merc.DAM_ACID, True)
