from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "detect good",
    skill_level={"mage": 11, "cleric": 4, "thief": 12, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(513),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="The gold in your vision disappears.",
    msg_obj="",
)
def spell_detect_good(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_DETECT_GOOD):
        if victim == ch:
            ch.send("You can already sense good.\n")
        else:
            handler_game.act(
                "$N can already detect good.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.modifier = 0
    af.location = merc.APPLY_NONE
    af.bitvector = merc.AFF_DETECT_GOOD
    victim.affect_add(af)
    victim.send("Your eyes tingle.\n")
    if ch != victim:
        ch.send("Ok.\n")
