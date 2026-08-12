from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "cure poison",
    skill_level={"mage": 53, "cleric": 14, "thief": 53, "warrior": 16},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(43),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Cure Poison!",
    msg_obj="",
)
def spell_cure_poison(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if not state_checks.is_affected(victim, const.skill_table["poison"]):
        if victim == ch:
            ch.send("You aren't poisoned.\n")
        else:
            handler_game.act(
                "$N doesn't appear to be poisoned.", ch, None, victim, merc.TO_CHAR
            )
        return

    if handler_magic.check_dispel(level, victim, const.skill_table["poison"]):
        victim.send("A warm feeling runs through your body.\n")
        handler_game.act("$n looks much better.", victim, None, None, merc.TO_ROOM)
        return

    ch.send("Spell failed.\n")
