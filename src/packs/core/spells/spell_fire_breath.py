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
    "fire breath",
    skill_level={"mage": 40, "cleric": 45, "thief": 50, "warrior": 51},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(201),
    min_mana=200,
    beats=24,
    noun_damage="blast of flame",
    msg_off="The smoke leaves your eyes.",
    msg_obj="",
)
def spell_fire_breath(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    handler_game.act(
        "$n breathes forth a cone of fire.", ch, None, victim, merc.TO_NOTVICT
    )
    handler_game.act(
        "$n breathes a cone of hot fire over you! ", ch, None, victim, merc.TO_VICT
    )
    handler_game.act("You breath forth a cone of fire.", ch, None, None, merc.TO_CHAR)

    hpch = max(10, ch.hit)
    hp_dam = random.randint(hpch // 9 + 1, hpch // 5)
    dice_dam = game_utils.dice(level, 20)

    dam = max(hp_dam + dice_dam // 10, dice_dam + hp_dam // 10)
    effects.fire_effect(victim.in_room, level, dam // 2, merc.TARGET_ROOM)

    for vch in victim.in_room.people[:]:
        if fight.is_safe_spell(ch, vch, True) or (
            vch.is_npc() and ch.is_npc() and (ch.fighting != vch or vch.fighting != ch)
        ):
            continue

        if vch == victim:  # full damage */
            if handler_magic.saves_spell(level, vch, merc.DAM_FIRE):
                effects.fire_effect(vch, level // 2, dam // 4, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 2, sn, merc.DAM_FIRE, True)
            else:
                effects.fire_effect(vch, level, dam, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam, sn, merc.DAM_FIRE, True)
        else:  # partial damage */
            if handler_magic.saves_spell(level - 2, vch, merc.DAM_FIRE):
                effects.fire_effect(vch, level // 4, dam // 8, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 4, sn, merc.DAM_FIRE, True)
            else:
                effects.fire_effect(vch, level // 2, dam // 4, merc.TARGET_CHAR)
                fight.damage(ch, vch, dam // 2, sn, merc.DAM_FIRE, True)
