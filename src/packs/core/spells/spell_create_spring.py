from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import object_creator


@api.spell(
    "create spring",
    skill_level={"mage": 14, "cleric": 17, "thief": 23, "warrior": 20},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(80),
    min_mana=20,
    beats=12,
    noun_damage="",
    msg_off="!Create Spring!",
    msg_obj="",
)
def spell_create_spring(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    spring = object_creator.create_item(
        instance.item_templates[merc.OBJ_VNUM_SPRING], 0
    )
    spring.timer = level
    ch.in_room.put(spring)
    handler_game.act("$p flows from the ground.", ch, spring, None, merc.TO_ROOM)
    handler_game.act("$p flows from the ground.", ch, spring, None, merc.TO_CHAR)
