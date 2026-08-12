from rom24 import api
from rom24 import const
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "mass healing",
    skill_level={"mage": 53, "cleric": 38, "thief": 53, "warrior": 46},
    rating={"mage": 2, "cleric": 2, "thief": 4, "warrior": 4},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(508),
    min_mana=100,
    beats=36,
    noun_damage="",
    msg_off="!Mass Healing!",
    msg_obj="",
)
def spell_mass_healing(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    for gch_id in ch.in_room.people:
        gch = instance.characters[gch_id]
        if (ch.is_npc() and gch.is_npc()) or (not ch.is_npc() and not gch.is_npc()):
            const.skill_table["heal"].spell_fun(
                "heal", level, ch, gch, merc.TARGET_CHAR
            )
            const.skill_table["refresh"].spell_fun(
                "refresh", level, ch, gch, merc.TARGET_CHAR
            )
