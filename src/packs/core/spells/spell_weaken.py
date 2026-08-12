from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "weaken",
    skill_level={"mage": 11, "cleric": 14, "thief": 16, "warrior": 17},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(68),
    min_mana=20,
    beats=12,
    noun_damage="spell",
    msg_off="You feel stronger.",
    msg_obj="",
)
def spell_weaken(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if state_checks.is_affected(victim, sn) or handler_magic.saves_spell(
        level, victim, merc.DAM_OTHER
    ):
        return
    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level
    af.duration = level // 2
    af.location = merc.APPLY_STR
    af.modifier = -1 * (level // 5)
    af.bitvector = merc.AFF_WEAKEN
    victim.affect_add(af)
    victim.send("You feel your strength slip away.\n")
    handler_game.act("$n looks tired and weak.", victim, None, None, merc.TO_ROOM)
