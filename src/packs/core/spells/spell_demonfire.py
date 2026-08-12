from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc


@api.spell(
    "demonfire",
    skill_level={"mage": 53, "cleric": 34, "thief": 53, "warrior": 45},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(505),
    min_mana=20,
    beats=12,
    noun_damage="torments",
    msg_off="!Demonfire!",
    msg_obj="",
)
def spell_demonfire(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT replacement demonfire spell */
    if not ch.is_npc() and not ch.is_evil():
        victim = ch
        ch.send("The demons turn upon you! \n")

    ch.alignment = max(-1000, ch.alignment - 50)

    if victim != ch:
        handler_game.act(
            "$n calls forth the demons of Hell upon $N! ",
            ch,
            None,
            victim,
            merc.TO_ROOM,
        )
        handler_game.act(
            "$n has assailed you with the demons of Hell! ",
            ch,
            None,
            victim,
            merc.TO_VICT,
        )
        ch.send("You conjure forth the demons of hell! \n")
    dam = game_utils.dice(level, 10)
    if handler_magic.saves_spell(level, victim, merc.DAM_NEGATIVE):
        dam = dam // 2
    fight.damage(ch, victim, dam, sn, merc.DAM_NEGATIVE, True)
    const.skill_table["curse"].spell_fun(
        "curse", 3 * level // 4, ch, victim, merc.TARGET_CHAR
    )
