from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_ch
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "charm person",
    skill_level={"mage": 20, "cleric": 53, "thief": 25, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(7),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="You feel more self-confident.",
    msg_obj="",
)
def spell_charm_person(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if fight.is_safe(ch, victim):
        return

    if victim == ch:
        ch.send("You like yourself even better! \n")
        return

    if (
        victim.is_affected(merc.AFF_CHARM)
        or ch.is_affected(merc.AFF_CHARM)
        or level < victim.level
        or state_checks.IS_SET(victim.imm_flags, merc.IMM_CHARM)
        or handler_magic.saves_spell(level, victim, merc.DAM_CHARM)
    ):
        return

    if state_checks.IS_SET(victim.in_room.room_flags, merc.ROOM_LAW):
        ch.send("The mayor does not allow charming in the city limits.\n")
        return

    if victim.master:
        handler_ch.stop_follower(victim)
    handler_ch.add_follower(victim, ch)
    victim.leader = ch.instance_id
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = game_utils.number_fuzzy(level // 4)
    af.location = 0
    af.modifier = 0
    af.bitvector = merc.AFF_CHARM
    victim.affect_add(af)
    handler_game.act("Isn't $n just so nice?", ch, None, victim, merc.TO_VICT)
    if ch is not victim:
        handler_game.act(
            "$N looks at you with adoring eyes.", ch, None, victim, merc.TO_CHAR
        )
