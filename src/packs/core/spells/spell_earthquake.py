from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import game_utils
from rom24 import handler_game
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "earthquake",
    skill_level={"mage": 53, "cleric": 10, "thief": 53, "warrior": 14},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(23),
    min_mana=15,
    beats=12,
    noun_damage="earthquake",
    msg_off="!Earthquake!",
    msg_obj="",
)
def spell_earthquake(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    ch.send("The earth trembles beneath your feet! \n")
    handler_game.act(
        "$n makes the earth tremble and shiver.", ch, None, None, merc.TO_ROOM
    )

    for vch in instance.characters.values():
        if not vch.in_room:
            continue
        if vch.in_room == ch.in_room:
            if vch != ch and not fight.is_safe_spell(ch, vch, True):
                if state_checks.IS_AFFECTED(vch, merc.AFF_FLYING):
                    fight.damage(ch, vch, 0, sn, merc.DAM_BASH, True)
                else:
                    fight.damage(
                        ch, vch, level + game_utils.dice(2, 8), sn, merc.DAM_BASH, True
                    )
            continue

        if vch.in_room.area == ch.in_room.area:
            vch.send("The earth trembles and shivers.\n")
