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
    "gas breath",
    skill_level={"mage": 39, "cleric": 43, "thief": 47, "warrior": 50},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(203),
    min_mana=175,
    beats=24,
    noun_damage="blast of gas",
    msg_off="!Gas Breath!",
    msg_obj="",
)
def spell_gas_breath(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    handler_game.act(
        "$n breathes out a cloud of poisonous gas! ", ch, None, None, merc.TO_ROOM
    )
    handler_game.act(
        "You breath out a cloud of poisonous gas.", ch, None, None, merc.TO_CHAR
    )

    hpch = max(16, ch.hit)
    hp_dam = random.randint(hpch // 15 + 1, 8)
    dice_dam = game_utils.dice(level, 12)

    dam = max(hp_dam + dice_dam // 10, dice_dam + hp_dam // 10)
    effects.poison_effect(ch.in_room, level, dam, merc.TARGET_ROOM)

    for vch_id in ch.in_room.people:

        vch = instance.characters[vch_id]
        if fight.is_safe_spell(ch, vch, True) or (
            ch.is_npc() and vch.is_npc() and (ch.fighting == vch or vch.fighting == ch)
        ):
            continue

        if handler_magic.saves_spell(level, vch, merc.DAM_POISON):
            effects.poison_effect(vch, level // 2, dam // 4, merc.TARGET_CHAR)
            fight.damage(ch, vch, dam // 2, sn, merc.DAM_POISON, True)
        else:
            effects.poison_effect(vch, level, dam, merc.TARGET_CHAR)
            fight.damage(ch, vch, dam, sn, merc.DAM_POISON, True)
