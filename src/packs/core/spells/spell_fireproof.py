from rom24 import api
from rom24 import const
from rom24 import game_utils
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "fireproof",
    skill_level={"mage": 13, "cleric": 12, "thief": 19, "warrior": 18},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_OBJ_INV,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(523),
    min_mana=10,
    beats=12,
    noun_damage="",
    msg_off="",
    msg_obj="$p's protective aura fades.",
)
def spell_fireproof(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    obj = victim
    if obj.flags.burn_proof:
        handler_game.act(
            "$p is already protected from burning.", ch, obj, None, merc.TO_CHAR
        )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_OBJECT
    af.type = sn
    af.level = level
    af.duration = game_utils.number_fuzzy(level // 4)
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.ITEM_BURN_PROOF

    obj.affect_add(af)

    handler_game.act("You protect $p from fire.", ch, obj, None, merc.TO_CHAR)
    handler_game.act(
        "$p is surrounded by a protective aura.", ch, obj, None, merc.TO_ROOM
    )
