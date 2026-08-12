import random
from rom24 import api
from rom24 import const
from rom24 import game_utils
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "locate object",
    skill_level={"mage": 9, "cleric": 15, "thief": 11, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(31),
    min_mana=20,
    beats=18,
    noun_damage="",
    msg_off="!Locate Object!",
    msg_obj="",
)
def spell_locate_object(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    found = False
    number = 0
    max_found = 200 if ch.is_immortal() else 2 * level

    for item in instance.items.values():
        if (
            not ch.can_see_item(item)
            or not game_utils.is_name(handler_magic.target_name, item.name)
            or item.flags.no_locate
            or random.randint(1, 99) > 2 * level
            or ch.level < item.level
        ):
            continue

        found = True
        number += 1
        in_item = item
        while in_item.in_item:
            in_item = in_item.in_item

        if in_item.in_living and ch.can_see(in_item.in_living):
            ch.send("one is carried by %s\n" % state_checks.PERS(in_item.in_living, ch))
        else:
            if ch.is_immortal() and in_item.in_room is not None:
                ch.send(
                    "one is in %s [[Room %d]]\n"
                    % (in_item.in_room.name, in_item.in_room.instance_id)
                )
            else:
                ch.send(
                    "one is in %s\n"
                    % ("somewhere" if not in_item.in_room else in_item.in_room.name)
                )

        if number >= max_found:
            break

    if not found:
        ch.send("Nothing like that in heaven or earth.\n")
