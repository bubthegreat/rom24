from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc
from rom24 import object_creator
from rom24 import state_checks


@api.spell(
    "continual light",
    skill_level={"mage": 6, "cleric": 4, "thief": 6, "warrior": 9},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(57),
    min_mana=7,
    beats=12,
    noun_damage="",
    msg_off="!Continual Light!",
    msg_obj="",
)
def spell_continual_light(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    if victim:  # do a glow on some object */
        light = ch.get_item_carry(victim, ch)

        if not light:
            ch.send("You don't see that here.\n")
            return

        if item.flags.glow:
            handler_game.act("$p is already glowing.", ch, light, None, merc.TO_CHAR)
            return

        item.flags.glow = True
        handler_game.act("$p glows with a white light.", ch, light, None, merc.TO_ALL)
        return

    light = object_creator.create_object(
        instance.item_templates[merc.OBJ_VNUM_LIGHT_BALL], 0
    )
    ch.in_room.put(light)
    handler_game.act(
        "$n twiddles $s thumbs and $p appears.", ch, light, None, merc.TO_ROOM
    )
    handler_game.act(
        "You twiddle your thumbs and $p appears.", ch, light, None, merc.TO_CHAR
    )
