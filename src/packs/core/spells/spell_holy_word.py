from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks
from rom24 import instance


@api.spell(
    "holy word",
    skill_level={"mage": 53, "cleric": 36, "thief": 53, "warrior": 42},
    rating={"mage": 2, "cleric": 2, "thief": 4, "warrior": 4},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(506),
    min_mana=200,
    beats=24,
    noun_damage="divine wrath",
    msg_off="!Holy Word!",
    msg_obj="",
)
def spell_holy_word(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT really nasty high-level attack spell */
    handler_game.act("$n utters a word of divine power! ", ch, None, None, merc.TO_ROOM)
    ch.send("You utter a word of divine power.\n")

    for vch_id in ch.in_room.people:

        vch = instance.characters[vch_id]
        if (
            (ch.is_good() and vch.is_good())
            or (ch.is_evil() and vch.is_evil())
            or (ch.is_neutral() and vch.is_neutral())
        ):
            vch.send("You feel full more powerful.\n")
            const.skill_table["frenzy"].spell_fun(
                "frenzy", level, ch, vch, merc.TARGET_CHAR
            )
            const.skill_table["bless"].spell_fun(
                "bless", level, ch, vch, merc.TARGET_CHAR
            )
        elif (ch.is_good() and state_checks.IS_EVIL(vch)) or (
            ch.is_evil() and state_checks.IS_GOOD(vch)
        ):
            if not fight.is_safe_spell(ch, vch, True):
                const.skill_table["curse"].spell_fun(
                    "curse", level, ch, vch, merc.TARGET_CHAR
                )
                vch.send("You are struck down! \n")
                dam = game_utils.dice(level, 6)
                fight.damage(ch, vch, dam, sn, merc.DAM_ENERGY, True)
        elif state_checks.IS_NEUTRAL(ch):
            if not fight.is_safe_spell(ch, vch, True):
                const.skill_table["curse"].spell_fun(
                    "curse", level // 2, ch, vch, merc.TARGET_CHAR
                )
                vch.send("You are struck down! \n")
                dam = game_utils.dice(level, 4)
                fight.damage(ch, vch, dam, sn, merc.DAM_ENERGY, True)
    ch.send("You feel drained.\n")
    ch.move = 0
    ch.hit = ch.hit // 2
