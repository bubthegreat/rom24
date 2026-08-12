from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "slow",
    skill_level={"mage": 23, "cleric": 30, "thief": 29, "warrior": 32},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(515),
    min_mana=30,
    beats=12,
    noun_damage="",
    msg_off="You feel yourself speed up.",
    msg_obj="",
)
def spell_slow(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(victim, sn) or victim.is_affected(merc.AFF_SLOW):
        if victim == ch:
            ch.send("You can't move any slower! \n")
        else:
            handler_game.act(
                "$N can't get any slower than that.", ch, None, victim, merc.TO_CHAR
            )
        return

    if handler_magic.saves_spell(level, victim, merc.DAM_OTHER) or state_checks.IS_SET(
        victim.imm_flags, merc.IMM_MAGIC
    ):
        if victim != ch:
            ch.send("Nothing seemed to happen.\n")
        victim.send("You feel momentarily lethargic.\n")
        return

    if victim.is_affected(merc.AFF_HASTE):
        if not handler_magic.check_dispel(level, victim, const.skill_table["haste"]):
            if victim != ch:
                ch.send("Spell failed.\n")
            victim.send("You feel momentarily slower.\n")
            return
        handler_game.act("$n is moving less quickly.", victim, None, None, merc.TO_ROOM)
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level // 2
    af.location = merc.APPLY_DEX
    af.modifier = -1 - (level >= 18) - (level >= 25) - (level >= 32)
    af.bitvector = merc.AFF_SLOW
    victim.affect_add(af)
    victim.send("You feel yourself slowing d o w n...\n")
    handler_game.act(
        "$n starts to move in slow motion.", victim, None, None, merc.TO_ROOM
    )
