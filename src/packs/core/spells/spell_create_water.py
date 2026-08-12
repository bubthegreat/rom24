from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "create water",
    skill_level={"mage": 8, "cleric": 3, "thief": 12, "warrior": 11},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_OBJ_INV,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(13),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Create Water!",
    msg_obj="",
)
def spell_create_water(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    obj = victim
    if obj.item_type != merc.ITEM_DRINK_CON:
        ch.send("It is unable to hold water.\n")
        return

    if obj.value[2] != 0 and obj.value[1] != 0:
        ch.send("It contains some other liquid.\n")
        return

    water = min(
        level * (4 if handler_game.weather_info.sky >= merc.SKY_RAINING else 2),
        obj.value[0] - obj.value[1],
    )

    if water > 0:
        obj.value[2] = 0
        obj.value[1] += water
        if "water" in obj.name.lower():
            obj.name = "%s water" % obj.name

        handler_game.act("$p is filled.", ch, obj, None, merc.TO_CHAR)
