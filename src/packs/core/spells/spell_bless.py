from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "bless",
    skill_level={"mage": 53, "cleric": 7, "thief": 53, "warrior": 8},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_OBJ_CHAR_DEF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(3),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You feel less righteous.",
    msg_obj="$p's holy aura fades.",
)
def spell_bless(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # deal with the object case first */
    if target == merc.TARGET_ITEM:
        obj = victim
        if obj.flags.bless:
            handler_game.act("$p is already blessed.", ch, obj, send_to=merc.TO_CHAR)
            return
        if obj.flags.evil:
            paf = state_checks.affect_find(obj.affected, "curse")
            level = obj.level
            if paf:
                level = paf.level
            if not handler_magic.saves_dispel(level, level, 0):
                if paf:
                    obj.affect_remove(paf)
                    handler_game.act(
                        "$p glows a pale blue.", ch, obj, None, merc.TO_ALL
                    )
                    obj.extra_bits = state_checks.REMOVE_BIT(
                        obj.extra_flags, merc.ITEM_EVIL
                    )
                    return
                else:
                    handler_game.act(
                        "The evil of $p is too powerful for you to overcome.",
                        ch,
                        obj,
                        send_to=merc.TO_CHAR,
                    )
                    return
        af = handler_game.AFFECT_DATA()
        af.where = merc.TO_OBJECT
        af.type = sn
        af.level = level
        af.duration = 6 + level
        af.location = merc.APPLY_SAVES
        af.modifier = -1
        af.bitvector = merc.ITEM_BLESS
        obj.affect_add(af)
        handler_game.act("$p glows with a holy aura.", ch, obj, send_to=merc.TO_ALL)
        if obj.wear_loc != merc.WEAR_NONE:
            ch.saving_throw = ch.saving_throw - 1
        return

    # character target */
    if victim.position == merc.POS_FIGHTING or state_checks.is_affected(victim, sn):
        if victim == ch:
            ch.send("You are already blessed.\n")
        else:
            handler_game.act(
                "$N already has divine favor.", ch, None, victim, merc.TO_CHAR
            )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 6 + level
    af.location = merc.APPLY_HITROLL
    af.modifier = level // 8
    af.bitvector = 0
    victim.affect_add(af)

    af.location = merc.APPLY_SAVING_SPELL
    af.modifier = 0 - level // 8
    victim.affect_add(af)
    victim.send("You feel righteous.\n")
    if ch is not victim:
        handler_game.act(
            "You grant $N the favor of your god.", ch, None, victim, merc.TO_CHAR
        )
