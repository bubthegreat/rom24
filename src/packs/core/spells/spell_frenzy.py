from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "frenzy",
    skill_level={"mage": 53, "cleric": 24, "thief": 53, "warrior": 26},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(504),
    min_mana=30,
    beats=24,
    noun_damage="",
    msg_off="Your rage ebbs.",
    msg_obj="",
)
def spell_frenzy(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT clerical berserking spell */
    if state_checks.is_affected(victim, sn) or victim.is_affected(merc.AFF_BERSERK):
        if victim == ch:
            ch.send("You are already in a frenzy.\n")
        else:
            handler_game.act(
                "$N is already in a frenzy.", ch, None, victim, merc.TO_CHAR
            )
        return

    if state_checks.is_affected(victim, const.skill_table["calm"]):
        if victim == ch:
            ch.send("Why don't you just relax for a while?\n")
        else:
            handler_game.act(
                "$N doesn't look like $e wants to fight anymore.",
                ch,
                None,
                victim,
                merc.TO_CHAR,
            )
        return
    if (
        (ch.is_good() and not state_checks.IS_GOOD(victim))
        or (state_checks.IS_NEUTRAL(ch) and not state_checks.IS_NEUTRAL(victim))
        or (ch.is_evil() and not state_checks.IS_EVIL(victim))
    ):
        handler_game.act(
            "Your god doesn't seem to like $N", ch, None, victim, merc.TO_CHAR
        )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level // 3
    af.modifier = level // 6
    af.bitvector = 0

    af.location = merc.APPLY_HITROLL
    victim.affect_add(af)

    af.location = merc.APPLY_DAMROLL
    victim.affect_add(af)

    af.modifier = 10 * (level // 12)
    af.location = merc.APPLY_AC
    victim.affect_add(af)

    victim.send("You are filled with holy wrath! \n")
    handler_game.act(
        "$n gets a wild look in $s eyes! ", victim, None, None, merc.TO_ROOM
    )
