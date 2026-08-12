from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "detect invis",
    skill_level={"mage": 3, "cleric": 8, "thief": 6, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(19),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You no longer see invisible objects.",
    msg_obj="",
)
def spell_detect_invis(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_DETECT_INVIS):
        if victim == ch:
            ch.send("You can already see invisible.\n")
        else:
            handler_game.act(
                "$N can already see invisible things.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.modifier = 0
    af.location = merc.APPLY_NONE
    af.bitvector = merc.AFF_DETECT_INVIS
    victim.affect_add(af)
    victim.send("Your eyes tingle.\n")
    if ch != victim:
        ch.send("Ok.\n")
