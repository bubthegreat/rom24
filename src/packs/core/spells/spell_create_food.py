from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import object_creator
from rom24 import instance


@api.spell(
    "create food",
    skill_level={"mage": 10, "cleric": 5, "thief": 11, "warrior": 12},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(12),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Create Food!",
    msg_obj="",
)
def spell_create_food(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    mushroom = object_creator.create_item(
        instance.item_templates[merc.OBJ_VNUM_MUSHROOM], 0
    )
    mushroom.value[0] = level // 2
    mushroom.value[1] = level
    ch.in_room.put(mushroom)
    handler_game.act("$p suddenly appears.", ch, mushroom, None, merc.TO_ROOM)
    handler_game.act("$p suddenly appears.", ch, mushroom, None, merc.TO_CHAR)
    return
