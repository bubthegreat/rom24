from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import object_creator
from rom24 import instance


@api.spell(
    "create rose",
    skill_level={"mage": 16, "cleric": 11, "thief": 10, "warrior": 24},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(511),
    min_mana=30,
    beats=12,
    noun_damage="",
    msg_off="!Create Rose!",
    msg_obj="",
)
def spell_create_rose(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    rose = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_ROSE], 0)
    handler_game.act(
        "$n has created a beautiful red rose.", ch, rose, None, merc.TO_ROOM
    )
    ch.send("You create a beautiful red rose.\n")
    ch.put(rose)
