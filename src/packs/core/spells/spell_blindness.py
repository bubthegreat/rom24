from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "blindness",
    skill_level={"mage": 12, "cleric": 8, "thief": 17, "warrior": 15},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(4),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You can see again.",
    msg_obj="",
)
def spell_blindness(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_BLIND) or handler_magic.saves_spell(
        level, victim, merc.DAM_OTHER
    ):
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.location = merc.APPLY_HITROLL
    af.modifier = -4
    af.duration = 1 + level
    af.bitvector = merc.AFF_BLIND
    victim.affect_add(af)
    victim.send("You are blinded! \n")
    handler_game.act("$n appears to be blinded.", victim, send_to=merc.TO_ROOM)
