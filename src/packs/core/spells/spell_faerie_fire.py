from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "faerie fire",
    skill_level={"mage": 6, "cleric": 3, "thief": 5, "warrior": 8},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(72),
    min_mana=5,
    beats=12,
    noun_damage="faerie fire",
    msg_off="The pink aura around you fades away.",
    msg_obj="",
)
def spell_faerie_fire(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_FAERIE_FIRE):
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.location = merc.APPLY_AC
    af.modifier = 2 * level
    af.bitvector = merc.AFF_FAERIE_FIRE
    victim.affect_add(af)
    victim.send("You are surrounded by a pink outline.\n")
    handler_game.act(
        "$n is surrounded by a pink outline.", victim, None, None, merc.TO_ROOM
    )
