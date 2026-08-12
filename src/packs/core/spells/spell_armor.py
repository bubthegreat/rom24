"""ctx-style pilot: the armor spell (defensive buff)."""
from rom24 import api


@api.spell(
    "armor",
    skill_level={"mage": 7, "cleric": 2, "thief": 10, "warrior": 5},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=api.TAR_CHAR_DEFENSIVE,
    min_pos=api.POS_STANDING,
    slot=api.SLOT(1),
    min_mana=5,
    beats=12,
    msg_off="You feel less armored.",
)
def spell_armor(ctx):
    victim = ctx.target
    if ctx.engine.state_checks.is_affected(victim, ctx.sn):
        if victim == ctx.ch:
            ctx.send("You are already armored.")
        else:
            ctx.act("$N is already armored.", None, victim, to=api.TO_CHAR)
        return

    af = ctx.engine.handler_game.AFFECT_DATA()
    af.where = api.TO_AFFECTS
    af.type = ctx.sn
    af.level = ctx.level
    af.duration = 24
    af.modifier = -20
    af.location = api.APPLY_AC
    af.bitvector = 0
    victim.affect_add(af)
    victim.send("You feel someone protecting you.\n")
    if ctx.ch is not victim:
        ctx.act("$N is protected by your magic.", None, victim, to=api.TO_CHAR)
