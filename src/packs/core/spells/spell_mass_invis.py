from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "mass invis",
    skill_level={"mage": 22, "cleric": 25, "thief": 31, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(69),
    min_mana=20,
    beats=24,
    noun_damage="",
    msg_off="You are no longer invisible.",
    msg_obj="",
)
def spell_mass_invis(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    for gch_id in ch.in_room.people:
        gch = instance.characters[gch_id]
        if not gch.is_same_group(ch) or gch.is_affected(merc.AFF_INVISIBLE):
            continue
        handler_game.act(
            "$n slowly fades out of existence.", gch, None, None, merc.TO_ROOM
        )
        gch.send("You slowly fade out of existence.\n")
        af = handler_game.AFFECT_DATA()
        af.where = merc.TO_AFFECTS
        af.type = sn
        af.level = level // 2
        af.duration = 24
        af.location = merc.APPLY_NONE
        af.modifier = 0
        af.bitvector = merc.AFF_INVISIBLE
        gch.affect_add(af)
    ch.send("Ok.\n")
