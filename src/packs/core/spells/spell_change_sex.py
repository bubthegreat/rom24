import random

from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "change sex",
    skill_level={"mage": 53, "cleric": 53, "thief": 53, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(82),
    min_mana=15,
    beats=12,
    noun_damage="",
    msg_off="Your body feels familiar again.",
    msg_obj="",
)
def spell_change_sex(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(victim, sn):
        if victim == ch:
            ch.send("You've already been changed.\n")
        else:
            handler_game.act(
                "$N has already had $s(?) sex changed.", ch, None, victim, merc.TO_CHAR
            )
        return

    if handler_magic.saves_spell(level, victim, merc.DAM_OTHER):
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 2 * level
    af.location = merc.APPLY_SEX

    while af.modifier == 0:
        af.modifier = random.randint(0, 2) - victim.sex

    af.bitvector = 0
    victim.affect_add(af)
    victim.send("You feel different.\n")
    handler_game.act(
        "$n doesn't look like $mself anymore...", victim, None, None, merc.TO_ROOM
    )
