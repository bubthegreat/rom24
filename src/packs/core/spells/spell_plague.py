from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "plague",
    skill_level={"mage": 23, "cleric": 17, "thief": 36, "warrior": 26},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(503),
    min_mana=20,
    beats=12,
    noun_damage="sickness",
    msg_off="Your sores vanish.",
    msg_obj="",
)
def spell_plague(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT plague spell, very nasty */
    if handler_magic.saves_spell(level, victim, merc.DAM_DISEASE) or (
        victim.is_npc() and victim.act.is_set(merc.ACT_UNDEAD)
    ):
        if ch == victim:
            ch.send("You feel momentarily ill, but it passes.\n")
        else:
            handler_game.act(
                "$N seems to be unaffected.", ch, None, victim, merc.TO_CHAR
            )
        return

    af = handler_game.AFFECT_DATA()
    af.where = merc.TO_AFFECTS
    af.type = sn
    af.level = level * 3 // 4
    af.duration = level
    af.location = merc.APPLY_STR
    af.modifier = -5
    af.bitvector = merc.AFF_PLAGUE
    victim.affect_join(af)

    victim.send("You scream in agony as plague sores erupt from your skin.\n")
    handler_game.act(
        "$n screams in agony as plague sores erupt from $s skin.",
        victim,
        None,
        None,
        merc.TO_ROOM,
    )
