from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "cure blindness",
    skill_level={"mage": 53, "cleric": 6, "thief": 53, "warrior": 8},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(14),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Cure Blindness!",
    msg_obj="",
)
def spell_cure_blindness(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if not state_checks.is_affected(victim, const.skill_table["blindness"]):
        if victim == ch:
            ch.send("You aren't blind.\n")
        else:
            handler_game.act(
                "$N doesn't appear to be blinded.", ch, None, victim, merc.TO_CHAR
            )
        return

    if handler_magic.check_dispel(level, victim, const.skill_table["blindness"]):
        victim.send("Your vision returns!\n")
        handler_game.act("$n is no longer blinded.", victim, None, None, merc.TO_ROOM)
    else:
        ch.send("Spell failed.\n")
