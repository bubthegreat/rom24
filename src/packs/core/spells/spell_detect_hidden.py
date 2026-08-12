from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "detect hidden",
    skill_level={"mage": 15, "cleric": 11, "thief": 12, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(44),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You feel less aware of your surroundings.",
    msg_obj="",
)
def spell_detect_hidden(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_DETECT_HIDDEN):
        if victim == ch:
            ch.send("You are already as alert as you can be. \n")
        else:
            handler_game.act(
                "$N can already sense hidden lifeforms.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_DETECT_HIDDEN
    victim.affect_add(af)
    victim.send("Your awareness improves.\n")
    if ch != victim:
        ch.send("Ok.\n")
