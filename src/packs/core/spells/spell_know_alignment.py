from rom24 import api
from rom24 import const
from rom24 import handler_game
from rom24 import merc


@api.spell(
    "know alignment",
    skill_level={"mage": 12, "cleric": 9, "thief": 20, "warrior": 53},
    rating={"mage": 1, "cleric": 1, "thief": 2, "warrior": 2},
    target=merc.TAR_CHAR_DEFENSIVE,
    min_pos=merc.POS_FIGHTING,
    slot=const.SLOT(58),
    min_mana=9,
    beats=12,
    noun_damage="",
    msg_off="!Know Alignment!",
    msg_obj="",
)
def spell_know_alignment(ctx):
    sn = ctx.sn
    level = ctx.level
    ch = ctx.ch
    victim = ctx.target
    target = ctx.target_type
    ap = victim.alignment

    if ap > 700:
        msg = "$N has a pure and good aura."
    elif ap > 350:
        msg = "$N is of excellent moral character."
    elif ap > 100:
        msg = "$N is often kind and thoughtful."
    elif ap > -100:
        msg = "$N doesn't have a firm moral commitment."
    elif ap > -350:
        msg = "$N lies to $S friends."
    elif ap > -700:
        msg = "$N is a black-hearted murderer."
    else:
        msg = "$N is the embodiment of pure evil! ."

    handler_game.act(msg, ch, None, victim, merc.TO_CHAR)
    return
