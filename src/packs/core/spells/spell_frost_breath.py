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
    "frost breath",
    skill_level={"mage": 34, "cleric": 36, "thief": 38, "warrior": 40},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(202),
    min_mana=125,
    beats=24,
    noun_damage="blast of frost",
    msg_off="!Frost Breath!",
    msg_obj="",
)
def spell_frost_breath(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    handler_game.act(
        "$n breathes out a freezing cone of frost! ", ch, None, victim, merc.TO_NOTVICT
    )
    handler_game.act(
        "$n breathes a freezing cone of frost over you! ",
        ch,
        None,
        victim,
        merc.TO_VICT,
    )
    handler_game.act("You breath out a cone of frost.", ch, None, None, merc.TO_CHAR)

    hpch = max(12, ch.hit)
    hp_dam = random.randint(hpch // 11 + 1, hpch // 6)
    dice_dam = game_utils.dice(level, 16)

    dam = max(hp_dam + dice_dam // 10, dice_dam + hp_dam // 10)
    effects.cold_effect(victim.in_room, level, dam // 2, merc.TARGET_ROOM)

    for vch in victim.in_room.people[:]:
        if fight.is_safe_spell(ch, vch, True) or (
            vch.is_npc() and ch.is_npc() and (ch.fighting != vch or vch.fighting != ch)
        ):
            continue

        if vch == victim:  # full damage */
            if handler_magic.saves_spell(level, vch, merc.DAM_COLD):
                effects.cold_effect(vch, level // 2, dam // 4, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 2, sn, merc.DAM_COLD, True)
            else:
                effects.cold_effect(vch, level, dam, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam, sn, merc.DAM_COLD, True)
        else:
            if handler_magic.saves_spell(level - 2, vch, merc.DAM_COLD):
                effects.cold_effect(vch, level // 4, dam // 8, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 4, sn, merc.DAM_COLD, True)
            else:
                effects.cold_effect(vch, level // 2, dam // 4, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 2, sn, merc.DAM_COLD, True)
