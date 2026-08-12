from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "ray of truth",
    skill_level={"mage": 53, "cleric": 35, "thief": 53, "warrior": 47},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_OFFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(518),
    min_mana=20,
    beats=12,
    noun_damage="ray of truth",
    msg_off="!Ray of Truth!",
    msg_obj="",
)
def spell_ray_of_truth(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if ch.is_evil():
        victim = ch
        ch.send("The energy explodes inside you! \n")
    if victim != ch:
        handler_game.act(
            "$n raises $s hand, and a blinding ray of light shoots forth! ",
            ch,
            None,
            None,
            merc.TO_ROOM,
        )
        ch.send("You raise your hand and a blinding ray of light shoots forth! \n")

    if state_checks.IS_GOOD(victim):
        handler_game.act(
            "$n seems unharmed by the light.", victim, None, victim, merc.TO_ROOM
        )
        victim.send("The light seems powerless to affect you.\n")
        return

    dam = game_utils.dice(level, 10)
    if handler_magic.saves_spell(level, victim, merc.DAM_HOLY):
        dam = dam // 2

    align = victim.alignment
    align -= 350

    if align < -1000:
        align = -1000 + (align + 1000) // 3

    dam = (dam * align * align) // 1000000

    fight.damage(ch, victim, dam, sn, merc.DAM_HOLY, True)
    const.skill_table["blindness"].spell_fun(
        "blindness", 3 * level // 4, ch, victim, merc.TARGET_CHAR
    )
