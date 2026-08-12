from rom24 import api
from rom24 import const
from rom24 import merc


@api.spell(
    "detect poison",
    skill_level={"mage": 15, "cleric": 7, "thief": 9, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_OBJ_INV,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(21),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Detect Poison!",
    msg_obj="",
)
def spell_detect_poison(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    obj = victim  # TAR_OBJ_INV: the target is the object
    if obj.item_type == merc.ITEM_DRINK_CON or obj.item_type == merc.ITEM_FOOD:
        if obj.value[3] != 0:
            ch.send("You smell poisonous fumes.\n")
        else:
            ch.send("It looks delicious.\n")
    else:
        ch.send("It doesn't look poisoned.\n")
    return
