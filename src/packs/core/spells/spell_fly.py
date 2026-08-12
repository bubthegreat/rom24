from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "fly",
    skill_level={"mage": 10, "cleric": 18, "thief": 20, "warrior": 22},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(56),
    min_mana=10,
    beats=18,
    noun_damage="",
    msg_off="You slowly float to the ground.",
    msg_obj="",
)
def spell_fly(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_FLYING):
        if victim == ch:
            ch.send("You are already airborne.\n")
        else:
            handler_game.act(
                "$N doesn't need your help to fly.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level + 3
    af.location = 0
    af.modifier = 0
    af.bitvector = merc.AFF_FLYING
    victim.affect_add(af)
    victim.send("Your feet rise off the ground.\n")
    handler_game.act("$n's feet rise off the ground.", victim, None, None, merc.TO_ROOM)
    return
