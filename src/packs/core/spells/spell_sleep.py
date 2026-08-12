from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "sleep",
    skill_level={"mage": 10, "cleric": 53, "thief": 11, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(38),
    min_mana=15,
    beats=12,
    noun_damage="",
    msg_off="You feel less tired.",
    msg_obj="",
)
def spell_sleep(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if (
        victim.is_affected(merc.AFF_SLEEP)
        or (victim.is_npc() and victim.act.is_set(merc.ACT_UNDEAD))
        or (level + 2) < victim.level
        or handler_magic.saves_spell(level - 4, victim, merc.DAM_CHARM)
    ):
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = 4 + level
    af.location = merc.APPLY_NONE
    af.modifier = 0
    af.bitvector = merc.AFF_SLEEP
    victim.affect_join(af)

    if state_checks.IS_AWAKE(victim):
        victim.send("You feel very sleepy ..... zzzzzz.\n")
        handler_game.act("$n goes to sleep.", victim, None, None, merc.TO_ROOM)
        victim.position = merc.POS_SLEEPING
