import random

from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import object_creator
from rom24 import state_checks
from rom24 import instance


@api.spell(
    "floating disc",
    skill_level={"mage": 4, "cleric": 10, "thief": 7, "warrior": 16},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(522),
    min_mana=40,
    beats=24,
    noun_damage="",
    msg_off="!Floating disc!",
    msg_obj="",
)
def spell_floating_disc(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    floating = ch.slots.float
    if floating and floating.flags.no_remove:
        handler_game.act("You can't remove $p.", ch, floating, None, merc.TO_CHAR)
        return

    disc = object_creator.create_item(instance.item_templates[merc.OBJ_VNUM_DISC], 0)
    disc.value[0] = ch.level * 10  # 10 pounds per level capacity */
    disc.value[3] = ch.level * 5  # 5 pounds per level max per item */
    disc.timer = ch.level * 2 - random.randint(0, level // 2)

    handler_game.act(
        "$n has created a floating black disc.", ch, None, None, merc.TO_ROOM
    )
    ch.send("You create a floating disc.\n")
    ch.put(disc)
    ch.equip(disc, True, True)
