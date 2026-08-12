from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "invisibility",
    skill_level={"mage": 5, "cleric": 53, "thief": 9, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_OBJ_CHAR_DEF,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(29),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You are no longer invisible.",
    msg_obj="$p fades into view.",
)
def spell_invis(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # object invisibility */
    if target == merc.TARGET_ITEM:
        obj = victim
        if obj.flags.invis:
            handler_game.act("$p is already invisible.", ch, obj, None, merc.TO_CHAR)
            return

        af = handler_game.AFFECT_DATA()
        af.where = merc.TO_OBJECT
        af.type = sn
        af.level = level
        af.duration = level + 12
        af.location = merc.APPLY_NONE
        af.modifier = 0
        af.bitvector = merc.ITEM_INVIS
        obj.affect_add(af)
        handler_game.act("$p fades out of sight.", ch, obj, None, merc.TO_ALL)
        return
    # character invisibility */
    if victim.is_affected(merc.AFF_INVISIBLE):
        return

    handler_game.act("$n fades out of existence.", victim, None, None, merc.TO_ROOM)
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level + 12
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_INVISIBLE
    victim.affect_add(af)
    victim.send("You fade out of existence.\n")
    return
