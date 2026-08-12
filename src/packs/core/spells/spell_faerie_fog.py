from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import handler_magic
from rom24 import merc
from rom24 import state_checks
from rom24 import instance


@api.spell(
    "faerie fog",
    skill_level={"mage": 14, "cleric": 21, "thief": 16, "warrior": 24},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_IGNORE,
    min_pos=merc.POS_STANDING,
    slot=const.SLOT(73),
    min_mana=12,
    beats=12,
    noun_damage="faerie fog",
    msg_off="!Faerie Fog!",
    msg_obj="",
)
def spell_faerie_fog(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    handler_game.act(
        "$n conjures a cloud of purple smoke.", ch, None, None, merc.TO_ROOM
    )
    ch.send("You conjure a cloud of purple smoke.\n")

    for ich_id in ch.in_room.people:

        ich = instance.characters[ich_id]
        if ich.invis_level > 0:
            continue

        if ich == ch or handler_magic.saves_spell(level, ich, merc.DAM_OTHER):
            continue

        ich.affect_strip("invis")
        ich.affect_strip("mass_invis")
        ich.affect_strip("sneak")
        ich.affected_by.rem_bit(merc.AFF_HIDE)
        ich.affected_by.rem_bit(merc.AFF_INVISIBLE)
        ich.affected_by.rem_bit(merc.AFF_SNEAK)
        handler_game.act("$n is revealed! ", ich, None, None, merc.TO_ROOM)
        ich.send("You are revealed! \n")
