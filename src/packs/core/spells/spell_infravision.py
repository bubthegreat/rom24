from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "infravision",
    skill_level={"mage": 9, "cleric": 13, "thief": 10, "warrior": 16},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(77),
    min_mana=5,
    beats=18,
    noun_damage="",
    msg_off="You no longer see in the dark.",
    msg_obj="",
)
def spell_infravision(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_INFRARED):
        if victim == ch:
            ch.send("You can already see in the dark.\n")
        else:
            handler_game.act(
                "$N already has infravision.\n", ch, None, victim, merc.TO_CHAR
            )
        return

    handler_game.act("$n's eyes glow red.\n", ch, None, None, merc.TO_ROOM)
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 2 * level
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_INFRARED
    victim.affect_add(af)
    victim.send("Your eyes glow red.\n")
    return
