from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "detect magic",
    skill_level={"mage": 2, "cleric": 6, "thief": 5, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(20),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="The detect magic wears off.",
    msg_obj="",
)
def spell_detect_magic(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_DETECT_MAGIC):
        if victim == ch:
            ch.send("You can already sense magical auras.\n")
        else:
            handler_game.act(
                "$N can already detect magic.", ch, None, victim, merc.TO_CHAR
            )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.modifier = 0
    af.location = merc.APPLY_NONE
    af.bitvector = merc.AFF_DETECT_MAGIC
    victim.affect_add(af)
    victim.send("Your eyes tingle.\n")
    if ch != victim:
        ch.send("Ok.\n")
