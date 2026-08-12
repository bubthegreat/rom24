from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "shield",
    skill_level={"mage": 20, "cleric": 35, "thief": 35, "warrior": 40},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(67),
    min_mana=12,
    beats=18,
    noun_damage="",
    msg_off="Your force shield shimmers then fades away.",
    msg_obj="",
)
def spell_shield(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(victim, sn):
        if victim == ch:
            ch.send("You are already shielded from harm.\n")
        else:
            handler_game.act(
                "$N is already protected by a shield.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 8 + level
    af.location = merc.APPLY_AC
    af.modifier = -20
    af.bitvector = 0
    victim.affect_add(af)
    handler_game.act(
        "$n is surrounded by a force shield.", victim, None, None, merc.TO_ROOM
    )
    victim.send("You are surrounded by a force shield.\n")
    return
