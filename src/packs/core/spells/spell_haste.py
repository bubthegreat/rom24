from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "haste",
    skill_level={"mage": 21, "cleric": 53, "thief": 26, "warrior": 29},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(502),
    min_mana=30,
    beats=12,
    noun_damage="",
    msg_off="You feel yourself slow down.",
    msg_obj="",
)
def spell_haste(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT haste spell */
    if (
        state_checks.is_affected(victim, sn)
        or victim.is_affected(merc.AFF_HASTE)
        or (victim.is_npc() and state_checks.IS_SET(victim.off_flags, merc.OFF_FAST))
    ):
        if victim == ch:
            ch.send("You can't move any faster! \n")
        else:
            handler_game.act(
                "$N is already moving as fast as $E can.",
                ch,
                None,
                victim,
                merc.TO_CHAR,
            )
        return
    if victim.is_affected(merc.AFF_SLOW):
        if not handler_magic.check_dispel(level, victim, const.skill_table["slow"]):
            if victim != ch:
                ch.send("Spell failed.\n")
            victim.send("You feel momentarily faster.\n")
            return
        handler_game.act("$n is moving less slowly.", victim, None, None, merc.TO_ROOM)
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    if victim == ch:
        af.duration = level // 2
    else:
        af.duration = level // 4
    af.location = merc.APPLY_DEX
    af.modifier = 1 + (level >= 18) + (level >= 25) + (level >= 32)
    af.bitvector = merc.AFF_HASTE
    victim.affect_add(af)
    victim.send("You feel yourself moving more quickly.\n")
    handler_game.act("$n is moving more quickly.", victim, None, None, merc.TO_ROOM)
    if ch != victim:
        ch.send("Ok.\n")
