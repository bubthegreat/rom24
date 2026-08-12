from rom24 import api
from rom24 import const
from rom24 import game_utils
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "pass door",
    skill_level={"mage": 24, "cleric": 32, "thief": 25, "warrior": 37},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(74),
    min_mana=20,
    beats=12,
    noun_damage="",
    msg_off="You feel solid again.",
    msg_obj="",
)
def spell_pass_door(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.is_affected(merc.AFF_PASS_DOOR):
        if victim == ch:
            ch.send("You are already out of phase.\n")
        else:
            handler_game.act(
                "$N is already shifted out of phase.", ch, None, victim, merc.TO_CHAR
            )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = game_utils.number_fuzzy(level // 4)
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_PASS_DOOR
    victim.affect_add(af)
    handler_game.act("$n turns translucent.", victim, None, None, merc.TO_ROOM)
    victim.send("You turn translucent.\n")
