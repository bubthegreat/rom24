from rom24 import api
from rom24 import const
from rom24 import game_utils
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "control weather",
    skill_level={"mage": 15, "cleric": 19, "thief": 28, "warrior": 22},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(11),
    min_mana=25,
    beats=12,
    noun_damage="",
    msg_off="!Control Weather!",
    msg_obj="",
)
def spell_control_weather(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim.lower() == "better":
        handler_game.weather_info.change += game_utils.dice(level // 3, 4)
    elif victim.lower() == "worse":
        handler_game.weather_info.change -= game_utils.dice(level // 3, 4)
    else:
        ch.send("Do you want it to get better or worse?\n")

    ch.send("Ok.\n")
    return
