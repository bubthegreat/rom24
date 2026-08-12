from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "sanctuary",
    skill_level={"mage": 36, "cleric": 20, "thief": 42, "warrior": 30},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(36),
    min_mana=75,
    beats=12,
    noun_damage="",
    msg_off="The white aura around your body fades.",
    msg_obj="",
)
def spell_sanctuary(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_SANCTUARY):
        if victim == ch:
            ch.send("You are already in sanctuary.\n")
        else:
            handler_game.act(
                "$N is already in sanctuary.", ch, None, victim, merc.TO_CHAR
            )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level // 6
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_SANCTUARY
    victim.affect_add(af)
    handler_game.act(
        "$n is surrounded by a white aura.", victim, None, None, merc.TO_ROOM
    )
    victim.send("You are surrounded by a white aura.\n")
