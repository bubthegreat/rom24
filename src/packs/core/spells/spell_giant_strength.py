from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "giant strength",
    skill_level={"mage": 11, "cleric": 53, "thief": 22, "warrior": 20},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(39),
    min_mana=20,
    beats=12,
    noun_damage="",
    msg_off="You feel weaker.",
    msg_obj="",
)
def spell_giant_strength(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(victim, sn):
        if victim == ch:
            ch.send("You are already as strong as you can get! \n")
        else:
            handler_game.act(
                "$N can't get any stronger.", ch, None, victim, merc.TO_CHAR
            )
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level
    af.location = merc.APPLY_STR
    af.modifier = 1 + (level >= 18) + (level >= 25) + (level >= 32)
    af.bitvector = 0
    victim.affect_add(af)
    victim.send("Your muscles surge with heightened power! \n")
    handler_game.act(
        "$n's muscles surge with heightened power.", victim, None, None, merc.TO_ROOM
    )
