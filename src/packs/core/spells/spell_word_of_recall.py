from rom24 import api
from rom24 import const
from rom24 import fight
from rom24 import handler_game
from rom24 import handler_room
from rom24 import merc
from rom24 import state_checks


@api.spell(
    "word of recall",
    skill_level={"mage": 32, "cleric": 28, "thief": 40, "warrior": 30},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_SELF,
    min_pos=merc.POS_RESTING,
    slot=const.SLOT(42),
    min_mana=5,
    beats=12,
    noun_damage="",
    msg_off="!Word of Recall!",
    msg_obj="",
)
def spell_word_of_recall(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    # RT recall spell is back */
    if victim.is_npc():
        return

    location = handler_room.get_room_by_vnum(merc.ROOM_VNUM_TEMPLE)
    if not location:
        victim.send("You are completely lost.\n")
        return

    if state_checks.IS_SET(
        victim.in_room.room_flags, merc.ROOM_NO_RECALL
    ) or victim.is_affected(merc.AFF_CURSE):
        victim.send("Spell failed.\n")
        return

    if victim.fighting:
        fight.stop_fighting(victim, True)

    ch.move //= 2
    handler_game.act("$n disappears.", victim, None, None, merc.TO_ROOM)
    victim.in_room.get(victim)
    location.put(victim)
    handler_game.act("$n appears in the room.", victim, None, None, merc.TO_ROOM)
    victim.do_look("auto")
