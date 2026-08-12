from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "stone skin",
    skill_level={"mage": 25, "cleric": 40, "thief": 40, "warrior": 45},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(66),
    min_mana=12,
    beats=18,
    noun_damage="",
    msg_off="Your skin feels soft again.",
    msg_obj="",
)
def spell_stone_skin(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(ch, sn):
        if victim == ch:
            ch.send("Your skin is already as hard as a rock.\n")
        else:
            handler_game.act(
                "$N is already as hard as can be.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.location = merc.APPLY_AC
    af.modifier = -40
    af.bitvector = 0
    victim.affect_add(af)
    handler_game.act("$n's skin turns to stone.", victim, None, None, merc.TO_ROOM)
    victim.send("Your skin turns to stone.\n")
