from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "protection good",
    skill_level={"mage": 12, "cleric": 9, "thief": 17, "warrior": 11},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(514),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You feel less protected.",
    msg_obj="",
)
def spell_protection_good(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_PROTECT_GOOD) or victim.is_affected(
        merc.AFF_PROTECT_EVIL
    ):
        if victim == ch:
            ch.send("You are already protected.\n")
        else:
            handler_game.act("$N is already protected.", ch, None, victim, merc.TO_CHAR)
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 24
    af.location = merc.APPLY_SAVING_SPELL
    af.modifier = -1
    af.bitvector = merc.AFF_PROTECT_GOOD
    victim.affect_add(af)
    victim.send("You feel aligned with darkness.\n")
    if ch != victim:
        handler_game.act("$N is protected from good.", ch, None, victim, merc.TO_CHAR)
